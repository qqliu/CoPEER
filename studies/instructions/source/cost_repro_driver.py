#!/usr/bin/env python3
"""Driver for the Task-1 cost-experiment reproduction (runs/cost_experiment_repro_20260915).

  python3 scripts/cost_repro_driver.py plan   --set proofs100|claims60|proofs100_task1 --model opus|sol|opus_task1
  python3 scripts/cost_repro_driver.py run    --set ... --model ... [--arms a,b] [--ids id,id] [--limit N] [--concurrency K]
  python3 scripts/cost_repro_driver.py grade  --set ... --model ... [--absent-as-missed] [--concurrency K]
  python3 scripts/cost_repro_driver.py status --set ... --model ...

Every cell = one record x one arm = one call of scripts/cost_repro_backend.sh
(isolated, schema-enforced, input-read verified).  Resume-safe: a cell whose
answer file exists and validates (and has a usage record) is skipped; every
attempt is appended to the ledger with its usage; the accepted attempt's usage is
copied to usage/.  Rate/usage limits (structured signals only) pause the whole
driver until the reported reset and do NOT consume the attempt budget; refusals,
unread input, timeouts and transport failures retry up to --max-attempts.
Circuit breaker: 6 consecutive non-complete cells -> 20 min pause; 3 such pauses
-> drain and exit 2.  A file <ops>/STOP_REQUESTED drains the driver.  Locks carry
host/pid/job id and are reclaimed when the owner is dead or the lock is older
than the cell timeout.  Set proofs100_task1 x opus_task1 = the ORIGINAL Task-1
Opus assessments (runs/cost_experiment/assessments), grade-only, for grader
calibration under the reproduction's grader.
"""
import argparse, hashlib, json, os, re, signal, socket, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RUN = Path(os.environ["COST_REPRO_RUN"]).resolve() if os.environ.get("COST_REPRO_RUN") else BASE / "runs/cost_experiment_repro_20260915"  # override for sibling runs (e.g. runs/bugbank_earlystop_20260915)
INPUTS_RUN = Path(os.environ["COST_REPRO_INPUTS_RUN"]).resolve() if os.environ.get("COST_REPRO_INPUTS_RUN") else RUN  # where inputs_claims60 lives (sibling runs point at the reproduction so prompts stay byte-identical)
# Grading is blinded to treatment labels: these arms are graded under their control arm's name (prompt + inlined assessment),
# the grade is validated against that name and the real arm is written back into the grade file (graded_as_arm records the alias).
GRADE_ALIAS = {"verify_earlystop_bugbank": "verify_earlystop", "prove_earlystop_bugbank": "prove_earlystop",
               "verify_earlystop_placebo": "verify_earlystop", "prove_earlystop_placebo": "prove_earlystop"}
LEADS_RE = re.compile(r"\{(leads(?:_[a-z0-9]+)?)\}")
OPS = Path(os.environ.get("COST_REPRO_OPS", "<workspace-home>/cost_repro_ops"))
BACKEND = BASE / "scripts/cost_repro_backend.sh"
CELL_TIMEOUT = int(os.environ.get("COST_REPRO_CELL_TIMEOUT", "3600"))
MODELS = {"opus": {"engine": "claude", "model": "opus", "effort": "high", "canonical": "claude-opus-5"},
          "sol": {"engine": "codex", "model": "gpt-5.6-sol", "effort": "high", "canonical": "gpt-5.6-sol"},
          "gemini": {"engine": "agy", "model": "gemini-3.1-pro-high", "effort": "high", "canonical": "gemini-3.1-pro-high"},
          "opus_task1": {"engine": None, "model": "claude-opus-5 (Task 1, 2026-08-20)", "effort": "high", "canonical": "claude-opus-5", "grade_only": True}}
# Grader (operator instruction 2026-09-15: "Use Astra to do the grading"): gpt-6-astra through the Codex CLI at
# effort max, as the September experiments' Astra primary evaluator (evaluation/evaluator_config_astra_v1.json,
# astra_cli.py EFFORT="max"); the assessment and truth JSON are inlined into the grading prompt (text-only role).
GRADER = {"engine": "codex", "model": "gpt-6-astra", "effort": "max", "canonical": "gpt-6-astra", "inline_files": True}
SETS = {"proofs100": {"ids": RUN / "proofs100_ids.json", "inputs": BASE / "runs/cost_experiment/inputs",
                      "truth": BASE / "runs/cost_experiment/grading_truth", "prompts_key": "proofs100"},
        "claims60": {"ids": RUN / "claims60_ids.json", "inputs": INPUTS_RUN / "inputs_claims60",
                     "truth": RUN / "grading_truth_claims60", "prompts_key": "claims60"},
        "proofs100_task1": {"ids": RUN / "proofs100_ids.json", "inputs": BASE / "runs/cost_experiment/inputs",
                            "truth": BASE / "runs/cost_experiment/grading_truth", "prompts_key": "proofs100",
                            "assessments": BASE / "runs/cost_experiment/assessments", "schema_key": "schema_task1"}}
STATUS_BY_EXIT = {3: "RATE_LIMITED", 4: "REFUSED", 5: "NOT_READ", 124: "TIMEOUT"}

def fn_of(rid): return re.sub(r"[ /]", "_", rid)
def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fill(template, **kw):
    out = template
    for k, v in kw.items(): out = out.replace("{" + k + "}", v)
    assert not re.search(r"\{(input_path|method|record_id_json|arm|assessment_path|truth_path|leads(?:_[a-z0-9]+)?)\}", out), "unfilled placeholder"
    return out

def valid_obj(path, schema, rid, arm, allow_extra=False):
    try: a = json.load(open(path))
    except Exception: return False
    if not isinstance(a, dict): return False
    for k in schema["required"]:
        if k not in a: return False
    if not allow_extra and not set(a) <= set(schema["properties"]): return False
    for k, p in schema["properties"].items():
        if k in a and "enum" in p and a.get(k) not in p["enum"]: return False
        if k in a and p.get("type") == "string" and not isinstance(a.get(k), str): return False
    return a.get("record_id") == rid and a.get("arm") == arm

def write_once(path, text):
    if path.exists() and path.read_text() == text: return
    tmp = path.with_suffix(path.suffix + ".tmp"); tmp.write_text(text); os.replace(tmp, path)

class Driver:
    def __init__(self, a):
        self.a = a; self.set = a.set; self.model_key = a.model
        self.P = json.load(open(RUN / "prompts.json")); self.S = SETS[self.set]; self.M = MODELS[self.model_key]
        man = json.load(open(RUN / "manifest.json")); self.prompts_sha = sha(RUN / "prompts.json")
        assert man["sources"]["prompts_sha256"] == self.prompts_sha, "prompts.json changed since the manifest was frozen; rebuild first"
        self.PK = self.S["prompts_key"]
        self.ids = json.load(open(self.S["ids"]))
        if a.ids: want = set(a.ids.split(",")); self.ids = [i for i in self.ids if i in want]
        if getattr(a, "ids_file", None):  # JSON list, or {set: list}; keeps the planned order (record ids may contain spaces)
            j = json.load(open(a.ids_file)); want = set(j[self.set] if isinstance(j, dict) else j); self.ids = [i for i in self.ids if i in want]
        if a.limit: self.ids = self.ids[: a.limit]
        self.arms = a.arms.split(",") if a.arms else self.P[self.PK]["arms"]
        for arm in self.arms: assert arm in self.P[self.PK]["methods"], arm
        self.schema = self.P.get(self.S.get("schema_key", "schema"), self.P["schema"])
        self.out_dir = self.S.get("assessments") or (RUN / "assessments" / self.set / self.model_key)
        self.usage_dir = RUN / "usage" / self.set / self.model_key
        self.grade_dir = RUN / "grades" / self.set / self.model_key
        self.grade_usage_dir = RUN / "grade_usage" / self.set / self.model_key
        self.ledger = RUN / "ledger" / f"{self.set}_{self.model_key}.jsonl"
        self.grade_ledger = RUN / "ledger" / f"grade_{self.set}_{self.model_key}.jsonl"
        self.ops = OPS / self.set / self.model_key
        self.lock_dir = OPS / "locks" / f"{self.set}_{self.model_key}"
        for d in (self.usage_dir, self.grade_dir, self.grade_usage_dir, self.ledger.parent, self.ops, self.lock_dir):
            d.mkdir(parents=True, exist_ok=True)
        if not self.M.get("grade_only"): self.out_dir.mkdir(parents=True, exist_ok=True)
        self.pause_until = 0.0; self.lock = threading.RLock(); self.stop = False  # RLock: _record_result() calls pause() under the lock (deadlock found 2026-09-15)
        self.consec_fail = 0; self.breaker_pauses = 0; self.my_locks = set()
        self.schema_path = RUN / f"{self.S.get('schema_key','schema')}.json"; write_once(self.schema_path, json.dumps(self.schema))
        self.grade_schema_path = RUN / "grade_schema.json"; write_once(self.grade_schema_path, json.dumps(self.P["grade_schema"]))
        self.job_id = os.environ.get("SLURM_JOB_ID")
        signal.signal(signal.SIGTERM, self._on_term)

    def _on_term(self, *_):
        self.log("SIGTERM: draining, releasing my locks"); self.stop = True
        for p in list(self.my_locks):
            try: Path(p).unlink()
            except Exception: pass
        os._exit(143)

    def cells(self): return [(rid, arm) for rid in self.ids for arm in self.arms]
    def log(self, msg): print(f"[{now()}] {msg}", flush=True)
    def append(self, path, rec):
        with self.lock:
            with open(path, "a") as f: f.write(json.dumps(rec) + "\n")
    def stop_requested(self): return self.stop or (OPS / "STOP_REQUESTED").exists()

    def wait_if_paused(self):
        while not self.stop_requested():
            with self.lock: until = self.pause_until
            if time.time() >= until: return
            time.sleep(min(30, until - time.time()))

    def pause(self, seconds, why):
        with self.lock:
            new = time.time() + seconds
            if new > self.pause_until: self.pause_until = new; self.log(f"PAUSE {int(seconds)}s: {why}")

    def _lock_stale(self, p):
        try: info = json.load(open(p))
        except Exception: return True  # unparsable / empty lock
        try: age = time.time() - p.stat().st_mtime
        except Exception: return True
        if age > CELL_TIMEOUT + 900: return True
        jid = info.get("job")
        if jid:
            r = subprocess.run(["squeue", "-h", "-j", str(jid)], capture_output=True, text=True)
            if r.returncode == 0 and not r.stdout.strip(): return True
        if info.get("host") == socket.gethostname() and info.get("pid") and not Path(f"/proc/{info['pid']}").exists(): return True
        return False

    def acquire(self, name):
        p = self.lock_dir / f"{name}.lock"
        for _ in range(2):
            try:
                fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, json.dumps({"pid": os.getpid(), "host": socket.gethostname(), "job": self.job_id, "t": now()}).encode()); os.close(fd)
                self.my_locks.add(str(p)); return p
            except FileExistsError:
                if self._lock_stale(p):
                    try: p.unlink()
                    except Exception: pass
                    continue
                return None
        return None

    def release(self, p):
        try: p.unlink()
        except Exception: pass
        self.my_locks.discard(str(p))

    def method_text(self, rid, arm):
        """Arm method text with each {leads*} placeholder replaced by the record's packet RUN/<placeholder>/<set>/<record>.txt.
        Returns (text, sha256 of the substituted packet text, or None); the sha equals the builder's leads_manifest.json sha."""
        method = self.P[self.PK]["methods"][arm]; shas = []
        for ph in sorted(set(LEADS_RE.findall(method))):
            lp = RUN / ph / self.set / f"{fn_of(rid)}.txt"; assert lp.exists(), lp
            txt = lp.read_text().strip(); shas.append(hashlib.sha256(txt.encode()).hexdigest()); method = method.replace("{" + ph + "}", txt)
        return method, ("+".join(shas) if shas else None)

    def _attempts_of(self, ledger, cell):
        if not ledger.exists(): return []
        out = []
        for line in open(ledger):
            try: r = json.loads(line)
            except Exception: continue
            if r.get("cell") == cell: out.append(r)
        return out

    def _record_result(self, ok):
        with self.lock:
            self.consec_fail = 0 if ok else self.consec_fail + 1
            if self.consec_fail >= 6:
                self.consec_fail = 0; self.breaker_pauses += 1
                if self.breaker_pauses >= 3:
                    self.log("CIRCUIT BREAKER: three consecutive-failure pauses; draining"); self.stop = True
                else: self.pause(1200, f"circuit breaker ({self.breaker_pauses}/3)")

    # ---- assessment cells -------------------------------------------------
    def run_cell(self, rid, arm):
        fn = fn_of(rid); cell = f"{fn}__{arm}"
        out = self.out_dir / f"{cell}.json"; usage_out = self.usage_dir / f"{cell}.json"
        method, leads_sha = self.method_text(rid, arm)
        if valid_obj(out, self.schema, rid, arm):
            if usage_out.exists(): return ("SKIP_VALID", cell, None)
            # orphan answer (backend finished after a driver death): rebuild usage from the newest attempt, else re-run
            att = sorted((self.ops / cell).glob("attempt_*/usage.json"), key=lambda p: p.stat().st_mtime)
            if att:
                u = json.load(open(att[-1]))
                if u.get("status") == 0 and isinstance(u.get("output_tokens_bound_model"), int):
                    k = int(att[-1].parent.name.split("_")[1])
                    json.dump({"cell": cell, "record_id": rid, "arm": arm, "attempt": k, "usage": u, "seconds": None, "recovered": True, "prompts_sha256": self.prompts_sha, "leads_sha256": leads_sha}, open(usage_out, "w"), indent=1)
                    self.append(self.ledger, {"t": now(), "set": self.set, "model": self.model_key, "cell": cell, "record_id": rid, "arm": arm, "attempt": k, "status": "COMPLETE_RECOVERED", "output_tokens": u["output_tokens_bound_model"], "prompts_sha256": self.prompts_sha, "leads_sha256": leads_sha})
                    return ("COMPLETE_RECOVERED", cell, u["output_tokens_bound_model"])
            out.unlink(missing_ok=True)
        lock = self.acquire(cell)
        if lock is None: return ("LOCKED", cell, None)
        try:
            input_path = self.S["inputs"] / f"{fn}.json"; assert input_path.exists(), input_path
            prompt = fill(self.P[self.PK]["template"], input_path=str(input_path), method=method,
                          record_id_json=json.dumps(rid), arm=arm)
            prev = self._attempts_of(self.ledger, cell)
            k = len(prev); tries = sum(1 for r in prev if r.get("status") not in ("RATE_LIMITED", "COMPLETE", "COMPLETE_RECOVERED"))
            while tries < self.a.max_attempts:
                if self.stop_requested(): return ("STOP_REQUESTED", cell, None)
                self.wait_if_paused()
                if self.stop_requested(): return ("STOP_REQUESTED", cell, None)
                k += 1
                wd = self.ops / cell / f"attempt_{k}"
                if wd.exists(): wd = self.ops / cell / f"attempt_{k}_{int(time.time())}"
                wd.mkdir(parents=True, exist_ok=True)
                usage_path = wd / "usage.json"; t0 = time.time()
                cmd = [str(BACKEND), "--engine", self.M["engine"], "--model", self.M["model"], "--effort", self.M["effort"],
                       "--workdir", str(wd), "--schema", str(self.schema_path), "--out", str(out),
                       "--events", str(wd / "events.jsonl"), "--usage", str(usage_path), "--read", str(input_path), "--input", str(input_path)]
                r = subprocess.run(cmd, input=prompt, capture_output=True, text=True)
                usage = json.load(open(usage_path)) if usage_path.exists() else None
                ok = r.returncode == 0 and valid_obj(out, self.schema, rid, arm)
                status = "COMPLETE" if ok else STATUS_BY_EXIT.get(r.returncode, "FAILED")
                if r.returncode == 0 and not ok: status = "INVALID_ANSWER"; out.unlink(missing_ok=True)
                rec = {"t": now(), "set": self.set, "model": self.model_key, "engine": self.M["engine"], "requested_model": self.M["model"],
                       "effort": self.M["effort"], "record_id": rid, "arm": arm, "cell": cell, "attempt": k, "status": status,
                       "backend_exit": r.returncode, "seconds": round(time.time() - t0, 1),
                       "output_tokens": (usage or {}).get("output_tokens_bound_model"),
                       "extra_exec_count": (usage or {}).get("extra_exec_count"), "workdir": str(wd),
                       "prompts_sha256": self.prompts_sha, "leads_sha256": leads_sha, "stdout_tail": r.stdout[-300:], "stderr_tail": r.stderr[-300:]}
                self.append(self.ledger, rec)
                if ok:
                    json.dump({"cell": cell, "record_id": rid, "arm": arm, "attempt": k, "usage": usage, "seconds": rec["seconds"],
                               "prompts_sha256": self.prompts_sha, "leads_sha256": leads_sha}, open(usage_out, "w"), indent=1)
                    self._record_result(True)
                    return ("COMPLETE", cell, usage.get("output_tokens_bound_model") if usage else None)
                if status == "RATE_LIMITED":
                    rl = (usage or {}).get("rate_limit_info") or {}; reset = rl.get("resetsAt")
                    wait = (max(120, reset - time.time() + 120) if isinstance(reset, (int, float)) else 1200)
                    self.pause(min(wait, 6 * 3600), f"{cell}: rate/usage limit (structured)")
                    continue  # does not consume the attempt budget
                tries += 1; self._record_result(False)
                time.sleep({"REFUSED": 60, "TIMEOUT": 10, "NOT_READ": 15}.get(status, 30))
            return ("GAVE_UP", cell, None)
        finally:
            self.release(lock)

    # ---- grading cells ----------------------------------------------------
    def grade_cell(self, rid, arm):
        fn = fn_of(rid); cell = f"{fn}__{arm}"
        assessment = self.out_dir / f"{cell}.json"; truth = self.S["truth"] / f"{fn}.json"
        out = self.grade_dir / f"{cell}.json"
        if self._valid_grade(out, rid, arm): return ("SKIP_VALID", cell, None)
        if not valid_obj(assessment, self.schema, rid, arm, allow_extra=bool(self.M.get("grade_only"))):
            if self.a.absent_as_missed:
                json.dump({"record_id": rid, "arm": arm, "grade": "MISSED", "justification": "assessment absent (cell never completed; Task-1 rule: absent -> MISSED)", "absent": True}, open(out, "w"), indent=1)
                self.append(self.grade_ledger, {"t": now(), "set": self.set, "model": self.model_key, "cell": cell, "status": "ABSENT_AS_MISSED"})
                return ("ABSENT_AS_MISSED", cell, "MISSED")
            return ("NO_ASSESSMENT", cell, None)
        assert truth.exists(), truth
        lock = self.acquire("grade__" + cell)
        if lock is None: return ("LOCKED", cell, None)
        try:
            if GRADER.get("inline_files"):
                prompt = fill(self.P[self.PK]["grade_prompt"], assessment_path="the ASSESSMENT block below", truth_path="the GROUND TRUTH block below",
                              record_id_json=json.dumps(rid), arm=GRADE_ALIAS.get(arm, arm))
                prompt += ("\n\n=== ASSESSMENT (file 1) ===\n" + self._blind_assessment(assessment, arm) + "\n\n=== GROUND TRUTH (file 2) ===\n" + truth.read_text()
                           + "\n\nBoth files are given above in full; do not look for them on disk. Return only the structured grade.")
            else:
                prompt = fill(self.P[self.PK]["grade_prompt"], assessment_path=str(assessment), truth_path=str(truth),
                              record_id_json=json.dumps(rid), arm=GRADE_ALIAS.get(arm, arm))
            prev = self._attempts_of(self.grade_ledger, cell)
            k = len(prev); tries = sum(1 for r in prev if r.get("status") not in ("RATE_LIMITED", "COMPLETE"))
            while tries < self.a.max_attempts:
                if self.stop_requested(): return ("STOP_REQUESTED", cell, None)
                self.wait_if_paused()
                if self.stop_requested(): return ("STOP_REQUESTED", cell, None)
                k += 1
                wd = OPS / "grade" / self.set / self.model_key / cell / f"attempt_{k}"
                if wd.exists(): wd = OPS / "grade" / self.set / self.model_key / cell / f"attempt_{k}_{int(time.time())}"
                wd.mkdir(parents=True, exist_ok=True)
                usage_path = wd / "usage.json"; t0 = time.time()
                cmd = [str(BACKEND), "--engine", GRADER["engine"], "--model", GRADER["model"], "--effort", GRADER["effort"],
                       "--mode", "grade", "--workdir", str(wd), "--schema", str(self.grade_schema_path), "--out", str(out),
                       "--events", str(wd / "events.jsonl"), "--usage", str(usage_path)]
                if not GRADER.get("inline_files"): cmd += ["--read", str(assessment), "--read", str(truth)]
                r = subprocess.run(cmd, input=prompt, capture_output=True, text=True)
                usage = json.load(open(usage_path)) if usage_path.exists() else None
                ok = r.returncode == 0 and self._valid_grade(out, rid, arm)
                status = "COMPLETE" if ok else STATUS_BY_EXIT.get(r.returncode, "FAILED")
                if r.returncode == 0 and not ok: status = "INVALID_ANSWER"; out.unlink(missing_ok=True)
                self.append(self.grade_ledger, {"t": now(), "set": self.set, "model": self.model_key, "grader": GRADER, "record_id": rid,
                                                "arm": arm, "cell": cell, "attempt": k, "status": status, "backend_exit": r.returncode,
                                                "seconds": round(time.time() - t0, 1), "workdir": str(wd), "prompts_sha256": self.prompts_sha,
                                                "stderr_tail": r.stderr[-300:]})
                if ok:
                    json.dump({"cell": cell, "attempt": k, "usage": usage}, open(self.grade_usage_dir / f"{cell}.json", "w"), indent=1)
                    self._record_result(True)
                    return ("COMPLETE", cell, json.load(open(out)).get("grade"))
                if status == "RATE_LIMITED":
                    rl = (usage or {}).get("rate_limit_info") or {}; reset = rl.get("resetsAt")
                    self.pause(min(max(120, reset - time.time() + 120) if isinstance(reset, (int, float)) else 1200, 6 * 3600), f"grade {cell}: limit")
                    continue
                tries += 1; self._record_result(False); time.sleep(30)
            return ("GAVE_UP", cell, None)
        finally:
            self.release(lock)

    def _unblind_grade(self, g, arm):
        """Grade file was validated under the control alias: write the real arm back (and remember the alias). Returns True."""
        try:
            p = self.grade_dir / f"{fn_of(g['record_id'])}__{arm}.json"; g["graded_as_arm"] = g.get("arm"); g["arm"] = arm
            json.dump(g, open(p, "w"), indent=1)
        except Exception: pass
        return True

    def _blind_assessment(self, path, arm):
        """Inlined assessment text with the treatment arm label replaced by its control alias (grading is blind to condition)."""
        text = path.read_text(); alias = GRADE_ALIAS.get(arm, arm)
        if alias == arm: return text
        try:
            a = json.load(open(path)); a["arm"] = alias; return json.dumps(a, indent=1, ensure_ascii=False)
        except Exception: return text.replace(f'"{arm}"', f'"{alias}"')

    def _valid_grade(self, path, rid, arm):
        try: g = json.load(open(path))
        except Exception: return False
        return g.get("record_id") == rid and (g.get("arm") == arm or (g.get("arm") == GRADE_ALIAS.get(arm) and self._unblind_grade(g, arm))) and g.get("grade") in self.P["grade_schema"]["properties"]["grade"]["enum"] \
            and isinstance(g.get("justification"), str)

    # ---- orchestration ----------------------------------------------------
    def execute(self, fn, label):
        cells = self.cells(); counts = {}; locked = []
        self.log(f"{label}: set={self.set} model={self.model_key} arms={self.arms} records={len(self.ids)} cells={len(cells)} concurrency={self.a.concurrency} job={self.job_id} prompts_sha={self.prompts_sha[:12]}")
        with ThreadPoolExecutor(max_workers=self.a.concurrency) as ex:
            futs = {ex.submit(fn, rid, arm): (rid, arm) for rid, arm in cells}
            for f in as_completed(futs):
                try: status, cell, extra = f.result()
                except Exception as e: status, cell, extra = "EXC", str(futs[f]), str(e)[:200]
                counts[status] = counts.get(status, 0) + 1
                if status == "LOCKED": locked.append(cell)
                if status not in ("SKIP_VALID",): self.log(f"{status:16s} {cell} {extra if extra is not None else ''}")
        self.log(f"{label} done: {json.dumps(counts)}")
        if locked: self.log(f"LOCKED cells (not run this pass): {locked}")
        return counts

    def status(self):
        cells = self.cells(); done = 0; graded = 0; tok = []; st = {}; gst = {}
        for rid, arm in cells:
            cell = f"{fn_of(rid)}__{arm}"
            if valid_obj(self.out_dir / f"{cell}.json", self.schema, rid, arm):
                done += 1
                u = self.usage_dir / f"{cell}.json"
                if u.exists():
                    o = (json.load(open(u)).get("usage") or {}).get("output_tokens_bound_model")
                    if isinstance(o, int): tok.append(o)
            if self._valid_grade(self.grade_dir / f"{cell}.json", rid, arm):
                graded += 1; g = json.load(open(self.grade_dir / f"{cell}.json"))["grade"]; gst[g] = gst.get(g, 0) + 1
        for ledger, target in ((self.ledger, st),):
            if ledger.exists():
                for line in open(ledger):
                    try: r = json.loads(line); target[r["status"]] = target.get(r["status"], 0) + 1
                    except Exception: pass
        print(json.dumps({"set": self.set, "model": self.model_key, "cells": len(cells), "complete": done, "graded": graded, "grades": gst,
                          "attempt_statuses": st, "output_tokens_mean": (sum(tok) / len(tok)) if tok else None,
                          "stop_requested": self.stop_requested(), "locks_present": len(list(self.lock_dir.glob("*.lock")))}, indent=1))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run", "grade", "status"])
    ap.add_argument("--set", required=True, choices=list(SETS)); ap.add_argument("--model", required=True, choices=list(MODELS))
    ap.add_argument("--arms"); ap.add_argument("--ids-file"); ap.add_argument("--ids"); ap.add_argument("--limit", type=int)
    ap.add_argument("--concurrency", type=int, default=4); ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--absent-as-missed", action="store_true")
    a = ap.parse_args(); d = Driver(a)
    if a.cmd == "run" and d.M.get("grade_only"): sys.exit("this model key is grade-only")
    if a.cmd == "plan":
        print(json.dumps({"set": a.set, "model": d.M, "arms": d.arms, "records": len(d.ids), "cells": len(d.cells()), "inputs": str(d.S["inputs"]),
                          "out_dir": str(d.out_dir), "prompts_sha256": d.prompts_sha, "example_prompt": fill(d.P[d.PK]["template"],
                          input_path=str(d.S["inputs"] / f"{fn_of(d.ids[0])}.json"), method=d.method_text(d.ids[0], d.arms[0])[0],
                          record_id_json=json.dumps(d.ids[0]), arm=d.arms[0])}, indent=1))
    elif a.cmd == "run": c = d.execute(d.run_cell, "run"); sys.exit(2 if d.stop else 0)
    elif a.cmd == "grade": c = d.execute(d.grade_cell, "grade"); sys.exit(2 if d.stop else 0)
    else: d.status()

if __name__ == "__main__":
    main()
