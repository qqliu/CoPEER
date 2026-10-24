#!/usr/bin/env python3
"""Proof-development replication driver (runs/proof_construction_repro_20260916).

  python3 driver.py plan
  python3 driver.py run    --model opus|sol|gemini [--arms a,b] [--ids id,id] [--limit N] [--concurrency K]
  python3 driver.py status [--model M]
  python3 driver.py grade  --model M [--grader astra|opus] [--arms ...] [--concurrency K]

One cell = (model, arm, record): ONE agentic session that receives the August
prompt (prompts.json; originals verbatim, parity arms sharing one skeleton) and
returns the August output schema. Drafting revisions happen INSIDE the session,
as in the original workflow; the driver never feeds anything back. Isolation and
token accounting come from scripts/pc_repro_backend.sh (derived from the cost
reproduction backend): every experiment tree is hidden, only the problem file,
the retrieval wrapper + frozen retriever + BugBank sqlite (read-only) and a
per-cell scratch directory are visible; usage is the engine's own record.

Resume-safe: a cell is complete when drafts/<model>/<arm>/<fn>.json exists.
Dispatch order is record-major (all arms of a record before the next record),
seeded, so a truncated run is a balanced prefix.
"""
import argparse, hashlib, json, os, random, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUN = Path(__file__).resolve().parent
TRIAGE = RUN.parents[1]
REPO = TRIAGE.parent
ORIG = TRIAGE / "runs" / "proof_construction"
IN = ORIG / "inputs"
TRUTH = ORIG / "grading_truth"
IDS = ORIG / "problem_ids.json"
OPS = Path(os.environ.get("PC_REPRO_OPS", "<workspace-home>/pc_repro_ops"))
BACKEND = RUN / "scripts" / "pc_repro_backend.sh"
WRAPPER = RUN / "scripts" / "bugbank_retrieve.py"
PLACEBO = RUN / "scripts" / "pc_placebo.py"
REAL_RETRIEVER = TRIAGE / "scripts" / "bugbank_retrieve.py"
DB = REPO / "BugBank" / "bugbank.sqlite"
PROMPTS = json.load(open(RUN / "prompts.json"))
SCHEMA = RUN / "schema.json"
SANDBOX_TMP = "/tmp/claude-24032"          # literal path in the August prompt; bound per cell

MODELS = {"opus": {"engine": "claude", "model": "opus", "effort": "high", "canonical": "claude-opus-5"},
          "sol": {"engine": "codex", "model": "gpt-5.6-sol", "effort": "high", "canonical": "gpt-5.6-sol"},
          "gemini": {"engine": "agy", "model": "gemini-3.1-pro-high", "effort": "high", "canonical": "gemini-3.1-pro-high"}}
GRADERS = {"astra": {"engine": "codex", "model": "gpt-6-astra", "effort": "max", "canonical": "gpt-6-astra"},
           "opus": {"engine": "claude", "model": "opus", "effort": "high", "canonical": "claude-opus-5"}}
ARMS = list(PROMPTS["arms"])
SEED = 20260916
LOCK = threading.Lock()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ids() -> list:
    return json.load(open(IDS))


def fn_of(rid: str) -> str:
    return rid.replace(" ", "_").replace("/", "_")


def own_items(rid: str) -> list:
    stem = rid.replace("__codex_expansion", "")
    return sorted({rid, stem, stem.replace("__", "-"), stem.replace("__ans", "-ans")})


def build_prompt(rid: str, arm: str) -> str:
    fn = fn_of(rid)
    a = PROMPTS["arms"][arm]
    label = PROMPTS["model_arm_label"][arm]
    proto = a["protocol"].replace("RECORDID", fn).replace("${BASE}", str(RUN))
    text = PROMPTS["shared_pre"] + proto + PROMPTS["shared_post"]
    text = (text.replace("${IN}", str(IN)).replace("${fn}", fn).replace("${rid_json}", json.dumps(rid))
                .replace("${arm}", label).replace("${OUTDIR}", f"{SANDBOX_TMP}/out"))
    return text


def manifest() -> dict:
    files = {str(p.relative_to(REPO)): sha(p) for p in
             [RUN / "prompts.json", SCHEMA, BACKEND, WRAPPER, PLACEBO, REAL_RETRIEVER, DB,
              TRIAGE / "runs" / "proof_construction_arms.js", TRIAGE / "runs" / "proof_construction_grading.js", IDS]}
    files["inputs"] = {rid: sha(IN / f"{rid}.json") for rid in ids()}
    files["grading_truth"] = {rid: sha(TRUTH / f"{rid}.json") for rid in ids()}
    return {"schema": "proof-construction-repro-manifest/1", "seed": SEED, "models": MODELS, "graders": GRADERS,
            "arms": {k: {kk: vv for kk, vv in v.items() if kk != "protocol"} for k, v in PROMPTS["arms"].items()},
            "files_sha256": files, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def cmd_plan(a):
    rids = ids()
    rng = random.Random(SEED); order = rids[:]; rng.shuffle(order)
    cells = [{"rid": r, "arm": arm, "cell": f"{fn_of(r)}__{arm}"} for r in order for arm in ARMS]
    (RUN / "plan.json").write_text(json.dumps({"schema": "proof-construction-repro-plan/1", "seed": SEED,
                                                "record_order": order, "arms": ARMS, "cells": cells}, indent=1))
    (RUN / "manifest.json").write_text(json.dumps(manifest(), indent=1))
    print(f"plan: {len(order)} records x {len(ARMS)} arms = {len(cells)} cells per model; manifest written")


class Runner:
    def __init__(self, model_key, concurrency):
        self.key = model_key; self.M = MODELS[model_key]; self.conc = concurrency
        self.drafts = RUN / "drafts" / model_key; self.tele = RUN / "telemetry" / f"{model_key}.jsonl"
        self.drafts.mkdir(parents=True, exist_ok=True); self.tele.parent.mkdir(parents=True, exist_ok=True)

    def done(self, rid, arm) -> bool:
        return (self.drafts / arm / f"{fn_of(rid)}.json").exists()

    def run_cell(self, rid, arm):
        fn = fn_of(rid); cell = f"{fn}__{arm}"
        cell_dir = OPS / self.key / arm / fn
        for attempt in range(1, 5):
            if self.done(rid, arm):
                return "done"
            adir = cell_dir / f"attempt_{attempt}"; adir.mkdir(parents=True, exist_ok=True)
            scratch = adir / "scratch"; scratch.mkdir(exist_ok=True); (scratch / "out").mkdir(exist_ok=True)
            prompt = build_prompt(rid, arm)
            (adir / "prompt.txt").write_text(prompt)
            mode = PROMPTS["arms"][arm]["retrieval"] or "none"
            env = [f"PC_RETRIEVAL_MODE={mode}", f"PC_CALL_LOG={SANDBOX_TMP}/retrieval_calls.jsonl",
                   f"PC_PLACEBO_SEED={int(hashlib.sha256(rid.encode()).hexdigest(), 16) % (2**31)}"]
            if mode == "real_exclude_own" or mode == "placebo":
                env.append("PC_EXCLUDE_ITEMS=" + json.dumps(own_items(rid)))
            cmd = [str(BACKEND), "--engine", self.M["engine"], "--model", self.M["model"], "--effort", self.M["effort"],
                   "--workdir", str(adir / "work"), "--schema", str(SCHEMA), "--out", str(adir / "answer.json"),
                   "--events", str(adir / "events.jsonl"), "--usage", str(adir / "usage.json"),
                   "--input", str(IN / f"{fn}.json"), "--read", str(IN / f"{fn}.json"),
                   "--read", str(WRAPPER), "--read", str(PLACEBO), "--read", str(REAL_RETRIEVER), "--read", str(DB),
                   "--rw", f"{scratch}:{SANDBOX_TMP}"]
            for kv in env: cmd += ["--setenv", kv]
            t0 = time.time()
            with open(adir / "prompt.txt") as fin, open(adir / "backend.log", "w") as flog:
                r = subprocess.run(cmd, stdin=fin, stdout=flog, stderr=subprocess.STDOUT)
            status = r.returncode
            usage = {}
            try: usage = json.load(open(adir / "usage.json"))
            except Exception: pass
            calls = 0
            log = scratch / "retrieval_calls.jsonl"
            if log.exists(): calls = sum(1 for l in open(log) if l.strip())
            drafts_saved = len(list(scratch.glob(f"pc_draft_{fn}_*.md")))
            row = {"record_id": rid, "arm": arm, "arm_label": PROMPTS["model_arm_label"][arm], "family": PROMPTS["arms"][arm]["family"],
                   "model": self.key, "canonical_model": self.M["canonical"], "effort": self.M["effort"], "attempt": attempt,
                   "status": status, "seconds": round(time.time() - t0, 1), "retrieval_calls_mechanical": calls,
                   "drafts_saved_mechanical": drafts_saved, "usage": self.normalize(usage), "attempt_dir": str(adir),
                   "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            if status == 0:
                ans = json.load(open(adir / "answer.json"))
                ans.update({"model": self.key, "canonical_model": self.M["canonical"], "arm_key": arm,
                            "iterations_self_reported": ans.get("iterations_used"), "retrieval_calls_mechanical": calls,
                            "drafts_saved_mechanical": drafts_saved, "attempt_dir": str(adir)})
                if ans.get("record_id") != rid:
                    row["status"] = 6; row["note"] = f"record_id mismatch {ans.get('record_id')!r}"
                else:
                    row["iterations_self_reported"] = ans.get("iterations_used")
                    d = self.drafts / arm; d.mkdir(parents=True, exist_ok=True)
                    (d / f"{fn}.json").write_text(json.dumps(ans, indent=1))
            with LOCK:
                with open(self.tele, "a") as f: f.write(json.dumps(row) + "\n")
            print(f"[{self.key}] {cell} attempt {attempt}: status {row['status']} ({row['seconds']}s, out={row['usage'].get('output_tokens')})", flush=True)
            if row["status"] == 0: return "ok"
            if row["status"] == 3: time.sleep(600 * attempt); continue          # rate/usage limit: back off
            if row["status"] in (4, 5, 6, 1): time.sleep(30); continue           # refusal / input unread / mismatch / other: retry
            if row["status"] == 124: time.sleep(30); continue                    # timeout: one more try
        return "failed"

    @staticmethod
    def normalize(u: dict) -> dict:
        eng = u.get("engine"); out = {"engine": eng, "status": u.get("status")}
        if eng == "claude":
            mu = (u.get("bound_model_usage") or {}); tot = {"input": 0, "cache_read": 0, "cache_write": 0, "output": 0}
            for v in mu.values():
                tot["input"] += int(v.get("inputTokens", 0)); tot["cache_read"] += int(v.get("cacheReadInputTokens", 0))
                tot["cache_write"] += int(v.get("cacheCreationInputTokens", 0)); tot["output"] += int(v.get("outputTokens", 0))
            out.update({"output_tokens": tot["output"], "input_uncached": tot["input"] + tot["cache_write"], "input_cache_read": tot["cache_read"],
                        "api_calls": u.get("api_messages"), "cost_usd": u.get("total_cost_usd"), "num_turns": u.get("num_turns")})
        elif eng == "codex":
            t = u.get("usage_total") or {}
            out.update({"output_tokens": t.get("output_tokens"), "input_uncached": (t.get("input_tokens") or 0) - (t.get("cached_input_tokens") or 0),
                        "input_cache_read": t.get("cached_input_tokens"), "reasoning_output_tokens": t.get("reasoning_output_tokens"),
                        "api_calls": len(u.get("turns") or []), "commands": u.get("command_count")})
        elif eng == "agy":
            ru = u.get("usage") or {}      # agy result.usage: input_tokens (uncached), cache_read_tokens, output_tokens (includes thinking_tokens)
            out.update({"output_tokens": u.get("output_tokens_bound_model"), "input_uncached": ru.get("input_tokens"),
                        "input_cache_read": ru.get("cache_read_tokens"), "thinking_tokens": ru.get("thinking_tokens"),
                        "api_calls": u.get("num_turns"), "raw": {k: u.get(k) for k in ("usage", "extra_exec_count", "tool_steps") if k in u}})
        return out


def cmd_run(a):
    R = Runner(a.model, a.concurrency)
    plan = json.load(open(RUN / "plan.json"))
    arms = a.arms.split(",") if a.arms else ARMS
    want = set(a.ids.split(",")) if a.ids else None
    cells = [c for c in plan["cells"] if c["arm"] in arms and (want is None or c["rid"] in want) and not R.done(c["rid"], c["arm"])]
    if a.limit: cells = cells[:a.limit]
    print(f"run {a.model}: {len(cells)} cells pending (concurrency {a.concurrency})", flush=True)
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        list(ex.map(lambda c: R.run_cell(c["rid"], c["arm"]), cells))
    cmd_status(a)


def cmd_status(a):
    plan = json.load(open(RUN / "plan.json"))
    for mk in ([a.model] if getattr(a, "model", None) else MODELS):
        R = Runner(mk, 1)
        by = {arm: sum(1 for c in plan["cells"] if c["arm"] == arm and R.done(c["rid"], c["arm"])) for arm in ARMS}
        print(mk, {k: f"{v}/{len(plan['record_order'])}" for k, v in by.items()})


GRADE_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["record_id", "pitfall_committed", "correctness", "notes"],
                "properties": {"record_id": {"type": "string"}, "pitfall_committed": {"type": "boolean"},
                               "correctness": {"type": "string", "enum": ["CORRECT", "FLAWED", "INCOMPLETE"]}, "notes": {"type": "string"}}}


def grade_prompt(rid: str, proof: str) -> str:
    """The August grader contract (proof_construction_grading.js) with the three files INLINED and every
    process field removed: the grader sees the problem, the final proof text, and the held-out pitfall only.
    It never sees the arm, the model, the iteration count or the self-assessment."""
    problem = json.load(open(IN / f"{fn_of(rid)}.json"))["problem"]
    truth = json.load(open(TRUTH / f"{fn_of(rid)}.json"))
    return f"""You are grading one drafted mathematical proof against held-out ground truth.

You are given three things:
1. THE PROBLEM STATEMENT the drafter saw.
2. THE DRAFT's final proof text; grade ONLY this text on mathematical merits.
3. THE DOCUMENTED PITFALL: a known-false claim the community's flawed proof of this problem relied on (known_pitfall_claim; if empty, the pitfall is described inside pitfall_counterexample) and the pipeline-confirmed counterexample that kills it.

Report two judgments:
- pitfall_committed: true if the final proof asserts, relies on, or reproduces the documented pitfall claim (in any phrasing) as a load-bearing step; false if it avoids it or explicitly handles the case the counterexample exposes. Anchor this ONLY to the ground truth below, not to anything the draft says about its own process.
- correctness: read the proof adversarially, hunting for the weakest step. CORRECT only if every load-bearing step is justified and no concrete counterexample you can construct breaks one. FLAWED requires you to name the failing step and the concrete reason in notes. INCOMPLETE if the proof stops short of the claim or leaves a load-bearing step unproved.

Be strict: a proof that quietly assumes the pitfall claim commits it, even if it never states it verbatim.

Set record_id exactly {json.dumps(rid)}. Answer only with the JSON object.

=== 1. PROBLEM STATEMENT ===
{problem}

=== 2. DRAFT FINAL PROOF ===
{proof}

=== 3. DOCUMENTED PITFALL (held-out ground truth) ===
{json.dumps(truth, indent=1, ensure_ascii=False)}
"""


def cmd_grade(a):
    G = GRADERS[a.grader]
    arms = a.arms.split(",") if a.arms else ARMS
    R = Runner(a.model, 1)
    jobs = []
    for arm in arms:
        for p in sorted((R.drafts / arm).glob("*.json")) if (R.drafts / arm).exists() else []:
            out = RUN / "grades" / a.grader / a.model / arm / p.name
            if not out.exists(): jobs.append((arm, p, out))
    print(f"grade {a.model} with {a.grader}: {len(jobs)} drafts pending", flush=True)
    schema_path = RUN / "grade_schema.json"; schema_path.write_text(json.dumps(GRADE_SCHEMA))

    def one(job):
        arm, p, out = job
        d = json.load(open(p)); rid = d["record_id"]
        adir = OPS / "grade" / a.grader / a.model / arm / p.stem; adir.mkdir(parents=True, exist_ok=True)
        (adir / "prompt.txt").write_text(grade_prompt(rid, d["final_proof"]))
        for attempt in range(1, 4):
            cmd = [str(BACKEND), "--engine", G["engine"], "--model", G["model"], "--effort", G["effort"], "--workdir", str(adir / f"work{attempt}"),
                   "--schema", str(schema_path), "--out", str(adir / f"answer{attempt}.json"), "--events", str(adir / f"events{attempt}.jsonl"),
                   "--usage", str(adir / f"usage{attempt}.json"), "--mode", "grade"]
            with open(adir / "prompt.txt") as fin, open(adir / f"backend{attempt}.log", "w") as flog:
                r = subprocess.run(cmd, stdin=fin, stdout=flog, stderr=subprocess.STDOUT)
            if r.returncode == 0:
                g = json.load(open(adir / f"answer{attempt}.json")); g.update({"grader": a.grader, "grader_model": G["canonical"], "model": a.model, "arm_key": arm,
                                                                               "draft_sha256": hashlib.sha256(d["final_proof"].encode()).hexdigest(), "attempt_dir": str(adir)})
                out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(g, indent=1))
                print(f"[grade {a.grader}] {a.model} {arm} {rid}: {g['correctness']} pitfall={g['pitfall_committed']}", flush=True); return
            time.sleep(600 if r.returncode == 3 else 30)
        print(f"[grade {a.grader}] {a.model} {arm} {rid}: FAILED", flush=True)

    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        list(ex.map(one, jobs))


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    r = sub.add_parser("run"); r.add_argument("--model", required=True, choices=list(MODELS)); r.add_argument("--arms"); r.add_argument("--ids")
    r.add_argument("--limit", type=int, default=0); r.add_argument("--concurrency", type=int, default=3)
    s = sub.add_parser("status"); s.add_argument("--model", choices=list(MODELS))
    g = sub.add_parser("grade"); g.add_argument("--model", required=True, choices=list(MODELS)); g.add_argument("--grader", default="astra", choices=list(GRADERS))
    g.add_argument("--arms"); g.add_argument("--concurrency", type=int, default=3)
    a = ap.parse_args()
    {"plan": cmd_plan, "run": cmd_run, "status": cmd_status, "grade": cmd_grade}[a.cmd](a)


if __name__ == "__main__":
    main()
