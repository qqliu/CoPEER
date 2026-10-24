#!/usr/bin/env python3
"""private_audit_roster_v1 / audit_private_axioms_roster.py  (board TASK-1019, TASK-1023, TASK-1014/1015)

A copy of harness/e01_private_audit_v1/audit_private_axioms.py (sha256 6b105ed3…) whose E01-only sweep is replaced by an explicit,
sha-pinned roster and whose stages are hardened. README.md lists every delta; the WHY / method of v1 still hold:

WHY. The pinned validator (harness/validate.py sha256 dc81a986…) prints `#print axioms <NS>.<name>` in CHECK.lean for every
theorem/lemma its text scan finds, `private` stripped. A private declaration is the constant `_private.SUBMISSION.0.<NS>.<name>`; the
public name does not exist in an importing file, Lean 4.30.0 prints `error(lean.unknownIdentifier): Unknown constant …`, no axioms
line, and the validator records the name under `not_reported` (fail-closed FAIL) without ever inspecting the helper's axioms.

WHAT THIS AUDIT DOES (one Lean process at a time, in the pinned validator's bubblewrap Workspace):
  Stage 0  compile the UNMODIFIED submission as module SUBMISSION (olean written; its sha256 is bound into the result).
  Stage B  CHECK_enum.lean: `import SUBMISSION` + `import Lean`; a CommandElabM program prints `AUDIT_MODULE_CONSTANTS <count>` and one
           `AUDIT_AXIOMS {json}` line per constant of module SUBMISSION (public, private, auxiliary) with Lean.collectAxioms, kind,
           isPrivateName and privateToUserName. The audit REQUIRES the count line, count == parsed rows, unique names (else cannot resolve).
  Stage A  the submission text + `set_option pp.fullNames true` + `namespace NS` + `#print axioms NS.<name>` for every named private helper,
           every public theorem and the Stage-B-resolved anonymous private instance, appended at the end of the file. A Stage A that
           exits non-zero or prints an error is an EXPLICIT failure (disposition cannot resolve), never silently absorbed.
  Named private declarations (roster rows) must resolve to EXACTLY ONE enumerated private constant by Stage B and to the same one by Stage A.
  Anonymous `private instance` (no public name): resolved from the Stage B enumeration only — among the module's private constants, those not
  matched by a named textual private declaration and not compiler auxiliaries (`_eq_`, `match_`, `_proof_`, …; listed separately) are the
  candidates; exactly one candidate of kind definition/theorem whose user name starts with `inst` is the resolution; otherwise cannot resolve
  with the candidate list. No public name is ever fabricated for it.
  Allowed set: exactly repair_common.ALLOWED_AXIOMS = (propext, Classical.choice, Quot.sound).
  Disposition: "uses disallowed axiom" (any module constant with an axiom outside the set, or a declared `axiom`) > "cannot resolve" (any
  stage failure, incomplete enumeration, unresolved/ambiguous declaration, stage disagreement, roster/text-scan disagreement, sha mismatch)
  > "clean".
  Grades: compared by submission sha256 AND absolute submission path (run root/cell); the grade's checker profile (v1 bare key, __ckv2,
  __ckv3) is recorded; a path-only or sha-only hit is listed but never bound.

READ-ONLY with respect to every existing file: inputs are read; outputs go under this directory only (results/, scratch/).
No hidden evaluator file (reference.lean, AGREE.lean, instances.json, contract.json) is read or copied.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # …/harness/private_audit_roster_v1
HARNESS = HERE.parent                                   # …/harness
TRACK = HARNESS.parent                                  # …/repair_track_20260922
sys.path.insert(0, str(HARNESS))
import validate as v            # noqa: E402  (pinned validator, imported read-only for Workspace / text helpers / AXIOMS_RE)
import repair_common as rc      # noqa: E402

AUDIT_VERSION = "private_audit_roster_v1"
BOARD_TASKS = ["TASK-1019", "TASK-1023", "TASK-1014", "TASK-1015"]
V1_AUDIT_SCRIPT = HARNESS / "e01_private_audit_v1/audit_private_axioms.py"
ROSTER_PATH_DEFAULT = Path("[LOCAL_PATH]")
ROSTER_SHA256_EXPECTED = "6a661a2c27e8c92b2548cdbe9184450d4925d352d8d794dab3f72f842c64fce6"
ALLOWED_AXIOMS = tuple(rc.ALLOWED_AXIOMS)
if set(ALLOWED_AXIOMS) != {"propext", "Classical.choice", "Quot.sound"} or len(ALLOWED_AXIOMS) != 3:
    raise SystemExit("refusing to run: repair_common.ALLOWED_AXIOMS is not exactly {propext, Classical.choice, Quot.sound}: %r" % (ALLOWED_AXIOMS,))

MODIFIERS_RE = re.compile(r"^(?:@\[[^\]]*\]\s*)*((?:(?:noncomputable|private|protected|partial|unsafe|scoped|local|nonrec)\s+)*)")
ANON_INSTANCE_RE = re.compile(r"^(?:@\[[^\]]*\]\s*)*(?:(?:noncomputable|private|protected|partial|unsafe|scoped|local|nonrec)\s+)*"
                              r"instance(?![\w'!?.])\s*(?:\(\s*priority\s*:=[^)]*\)\s*)?(?=[(\[{⦃:])")
PRIVATE_NAME_RE = re.compile(r"^_private\.(.+?)\.(\d+)\.(.+)$")
AUDIT_LINE_RE = re.compile(r"^(?:\S+?\.lean:\d+:\d+: info: )?AUDIT_AXIOMS (\{.*\})$")
# compiler / elaborator auxiliaries hanging off a user declaration (listed separately, never candidates for an anonymous instance)
AUX_COMPONENT_RE = re.compile(r"^(?:_?eq_\d+(?:_\d+)*|eq_def|_eq_def|_unfold|match_\d+(?:_\d+)*|_?proof_\d+(?:_\d+)*|_unsafe_rec|_sunfold|_f|_unary|_mutual|"
                              r"_cstage\d*|_boxed|_closed_\d+|_lambda_\d+|_elambda_\d+|_spec_\d+|_rarg|_redArg|_override|_aux_\d+|_auxLemma|_simp_\d+|"
                              r"_cnstr_\d+|_impl|_sizeOf_\d+|_sizeOf_inst|_arg|_hyg|_check|_private|_uniq|\d+)$")
GRADING_DIR = TRACK / "study_grading_20260923"
GRADE_SUFFIX = ".GRADE_full_contract.json"
ROOT_TAGS = {"harness/runs": "v1", "harness/runs_v2_fixr7": "v2", "harness/runs_v2_fixr7b": "v2b", "harness/runs_v2_fixr7c": "v2c",
             "harness/runs_solvers45": "s45r7", "harness/runs_solvers45_fixr8": "s45r8",
             "local_solver/frame16": "frame16", "local_solver/frame16_a2env": "frame16_a2env"}
GRADE_FILENAME_PREFIX_TO_ROOT = {"v2": "harness/runs_v2_fixr7", "v2b": "harness/runs_v2_fixr7b", "v2c": "harness/runs_v2_fixr7c",
                                 "s45r7": "harness/runs_solvers45", "s45r8": "harness/runs_solvers45_fixr8"}


# --------------------------------------------------------------------------------------------------------------- utilities
def now_utc():
    """Timestamps come from the clock via `date -u`, never estimated."""
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], stdout=subprocess.PIPE, text=True, check=True).stdout.strip()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def unmangle_private(name):
    """`_private.<Module…>.<k>.<user name>` -> (True, <user name>); anything else -> (False, name)."""
    m = PRIVATE_NAME_RE.match(name)
    return (True, m.group(3)) if m else (False, name)


def name_components(user_name):
    """Components of a printed Lean name; a «…»-quoted component keeps its inner dots."""
    comps, cur, quoted = [], "", False
    for ch in user_name:
        if ch == "«":
            quoted = True
        elif ch == "»":
            quoted = False
        elif ch == "." and not quoted:
            comps.append(cur)
            cur = ""
            continue
        cur += ch
    comps.append(cur)
    return comps


def aux_split(user_name):
    """(parent user name, auxiliary component) when the name has a compiler/elaborator auxiliary component after its head; else None."""
    comps = name_components(user_name)
    for i in range(1, len(comps)):
        if AUX_COMPONENT_RE.match(comps[i]):
            return ".".join(comps[:i]), ".".join(comps[i:])
    return None


def last_component(user_name):
    return name_components(user_name)[-1]


def user_name_matches(user_name, ns, name):
    """Rule (d): the constant's privateToUserName is `NS.<name>` (or `<name>` for a declaration outside the namespace), or ends with `.NS.<name>`."""
    full = ns + "." + name if not name.startswith(ns + ".") else name
    return user_name == full or user_name == name or user_name.endswith("." + full)


# ----------------------------------------------------------------------------------------------------------- roster
def load_roster(path=ROSTER_PATH_DEFAULT, expected_sha256=ROSTER_SHA256_EXPECTED):
    """The explicit scope. Refuses any roster whose bytes do not hash to the pinned sha256."""
    data = Path(path).read_bytes()
    got = sha_bytes(data)
    if got != expected_sha256:
        raise SystemExit("refusing to run: roster %s has sha256 %s, expected %s" % (path, got, expected_sha256))
    roster = json.loads(data.decode("utf-8"))
    for key in ("expected_roster", "ambiguous_cases", "roots", "counts"):
        if key not in roster:
            raise SystemExit("refusing to run: roster lacks %s" % key)
    return roster, got


def roster_cells(roster):
    """Every expected_roster row, in roster order, with its ambiguous_cases issues attached; nothing is selected by outcome."""
    amb = {}
    for a in roster.get("ambiguous_cases", []):
        amb.setdefault((a["root"], a["cell"]), []).extend(a.get("issues", []))
    cells = []
    for r in roster["expected_roster"]:
        root_tag = ROOT_TAGS.get(r["root"])
        if root_tag is None:
            raise SystemExit("refusing to run: roster root %r has no root tag" % r["root"])
        cells.append({"root": r["root"], "root_tag": root_tag, "cell": r["cell"], "record_id": r["record_id"], "arm": r.get("arm"), "attempt": r.get("attempt"),
                      "model": r.get("model"), "submission_path": r["submission_path"], "submission_abs_path": str(TRACK / r["submission_path"]),
                      "submission_sha256": r["submission_sha256"], "submission_bytes": r.get("submission_bytes"),
                      "declarations": [{"line": d["line"], "kind": d["kind"], "name": d["name"]} for d in r["declarations"]],
                      "private_declaration_count": r.get("private_declaration_count"), "record_sha256": r.get("record_sha256"),
                      "ambiguous_issues": amb.get((r["root"], r["cell"]), [])})
    return cells


# ----------------------------------------------------------------------------------------------------------- text scan
def scan_declarations(text, ns):
    """Top-level declarations of the comment-stripped text with the pinned validator's chunking (v.chunks / v.decl_of), so the audit sees
    exactly the declarations the validator saw. Returns (named rows, anonymous instances, unnamed other, private token lines).
    decl_of returns ("instance", None) for `instance (p : ℕ) : …` (no name; v1 would have crashed on it): such a chunk is an anonymous
    instance, verified against ANON_INSTANCE_RE; any other nameless chunk (e.g. `example`) is kept under unnamed_other."""
    stripped = v.strip_comments(text)
    rows, anon, other = [], [], []
    for ln, chunk in v.chunks(stripped):
        d = v.decl_of(chunk)
        if not d:
            continue
        kind, name = d
        mods = MODIFIERS_RE.match(chunk)
        modifiers = mods.group(1).split() if mods else []
        is_private = "private" in modifiers
        if name is None:
            head = chunk.splitlines()[0].strip()
            if kind == "instance" and ANON_INSTANCE_RE.match(chunk):
                anon.append({"line": ln, "kind": kind, "private": is_private, "modifiers": modifiers, "head": head})
            else:
                other.append({"line": ln, "kind": kind, "private": is_private, "modifiers": modifiers, "head": head})
            continue
        rows.append({"line": ln, "kind": kind, "name": name, "private": is_private, "modifiers": modifiers,
                     "full_name": name if name.startswith(ns + ".") else ns + "." + name})
    private_tokens = [stripped.count("\n", 0, m.start()) + 1 for m in re.finditer(r"(?<![\w'!?.«])private(?![\w'!?»])", stripped)]
    return rows, anon, other, private_tokens


ENUM_LEAN = r'''import SUBMISSION
import Lean
-- private_audit_roster_v1 Stage B (unchanged from e01_private_audit_v1): enumerate EVERY constant of module SUBMISSION and collect its axioms (Lean 4.30.0).
open Lean Elab Command in
#eval show CommandElabM Unit from do
  let env ← getEnv
  let some idx := env.getModuleIdx? `SUBMISSION | throwError "module SUBMISSION not found"
  let names := env.header.moduleData[idx.toNat]!.constNames
  IO.println s!"AUDIT_MODULE_CONSTANTS {names.size}"
  for n in names do
    let axs ← collectAxioms n
    let kind := match env.find? n with
      | some (.thmInfo _) => "theorem" | some (.defnInfo _) => "definition" | some (.axiomInfo _) => "axiom"
      | some (.opaqueInfo _) => "opaque" | some (.quotInfo _) => "quot" | some (.inductInfo _) => "inductive"
      | some (.ctorInfo _) => "constructor" | some (.recInfo _) => "recursor" | none => "missing"
    let j := Json.mkObj [("name", Json.str n.toString), ("private", Json.bool (isPrivateName n)),
      ("user_name", Json.str (privateToUserName n).toString), ("kind", Json.str kind),
      ("axioms", Json.arr (axs.map (fun a => Json.str a.toString)))]
    IO.println s!"AUDIT_AXIOMS {j.compress}"
'''


def parse_enum_output(output):
    rows, count = [], None
    for line in output.splitlines():
        line = line.strip()
        m = AUDIT_LINE_RE.match(line)
        if m:
            row = json.loads(m.group(1))
            row["axioms"] = sorted(row.get("axioms") or [])
            rows.append(row)
        elif line.startswith("AUDIT_MODULE_CONSTANTS "):
            count = int(line.split()[1])
    return rows, count


def in_file_audit_text(text, ns, names):
    """The submission text + `#print axioms <qualified name>` for each name, inside `namespace NS … end NS`, appended at the end of the file.
    In the same file `NS.<name>` resolves to the private constant `_private.<module>.<k>.NS.<name>` (verified on 4.30.0, v1 PROBE1, for the
    bare and the qualified form; the qualified form is used here so an `open`ed namespace cannot make a bare name ambiguous).
    `set_option pp.fullNames true` first: inside the namespace Lean otherwise prints an axiom declared in NS namespace-relative."""
    lines = ["", "-- private_audit_roster_v1 Stage A (in-file resolution of private names); appended by the audit, never part of the graded text",
             "set_option pp.fullNames true", "namespace " + ns]
    lines += ["#print axioms %s" % (n if n.startswith(ns + ".") else ns + "." + n) for n in names]
    lines += ["end " + ns, ""]
    return text.rstrip("\n") + "\n" + "\n".join(lines)


AXIOMS_HEAD_RE = re.compile(r"^'(.+?)' depends on axioms: \[(.*)$")


def parse_axioms_multiline(output):
    """Like validate.parse_axioms, but Lean 4.30.0 wraps a `depends on axioms: […]` message longer than 120 characters onto continuation
    lines; the pinned single-line AXIOMS_RE misses those. Here a wrapped list is joined before matching."""
    found, lines, i = {}, output.splitlines(), 0
    while i < len(lines):
        line = lines[i].strip()
        m = v.AXIOMS_RE.match(line)
        if m:
            found[m.group(1)] = sorted(a.strip() for a in (m.group(2) or "").split(",") if a.strip())
            i += 1
            continue
        h = AXIOMS_HEAD_RE.match(line)
        if h and "]" not in h.group(2):
            joined, j = [h.group(2)], i + 1
            while j < len(lines) and "]" not in lines[j]:
                joined.append(lines[j].strip())
                j += 1
            if j < len(lines):
                joined.append(lines[j].strip())
                body = " ".join(joined)
                body = body[:body.index("]")]
                found[h.group(1)] = sorted(a.strip() for a in body.split(",") if a.strip())
                i = j + 1
                continue
        i += 1
    return found


# ---------------------------------------------------------------------------------------------------------- identities
def tool_identities():
    env = v.lean_environment()
    return {"audit_script": {"path": str(Path(__file__).resolve()), "sha256": sha_file(__file__), "audit_version": AUDIT_VERSION},
            "v1_audit_script": {"path": str(V1_AUDIT_SCRIPT), "sha256": sha_file(V1_AUDIT_SCRIPT) if V1_AUDIT_SCRIPT.is_file() else None},
            "validate_py": {"path": str(HARNESS / "validate.py"), "sha256": sha_file(HARNESS / "validate.py")},
            "repair_common_py": {"path": str(HARNESS / "repair_common.py"), "sha256": sha_file(HARNESS / "repair_common.py")},
            "lean_env": {"toolchain": env["toolchain"], "toolchain_file_sha256": sha_file(rc.LEAN_ENV / "lean-toolchain"),
                         "mathlib_rev": env["mathlib_rev"], "mathlib_input_rev": env.get("mathlib_input_rev"),
                         "lake_manifest_sha256": sha_file(rc.LEAN_ENV / "lake-manifest.json"), "lean_env_fingerprint_sha256": env["fingerprint_sha256"],
                         "common_project": env["common_project"], "skeleton_matches_common_project": env["skeleton_matches_common_project"]},
            "enum_check_file_sha256": sha_bytes(ENUM_LEAN.encode()), "allowed_axioms": list(ALLOWED_AXIOMS)}


# ---------------------------------------------------------------------------------------------------------- the audit
class Auditor:
    def __init__(self, workspace_dir, cache_dir, record_id="E01", packet_dir=None, log_root=None):
        self.record_id = record_id
        self.packet = rc.load_packet(record_id, packet_dir)      # task.json / defs_only.lean only (no hidden files are touched)
        self.packet_dir_resolved = str(self.packet["dir"])
        self.packet_identity = {"dir": self.packet_dir_resolved, "task.json_sha256": sha_file(self.packet["dir"] / "task.json"),
                                "defs_only.lean_sha256": sha_file(self.packet["dir"] / "defs_only.lean")}
        self.ns = self.packet["task"]["submission_namespace"]
        self.ws = v.Workspace(workspace_dir, cache_dir)
        self.log_root = Path(log_root) if log_root else None
        self.lean_version = self.ws.lean_version()
        self.identities = tool_identities()
        self.identities["lean_env"]["lean_version"] = self.lean_version["output"]
        self.defs_only = self.ws.compile_cached(self.packet["dir"] / "defs_only.lean", "defs_only", ["defs_only"])
        if self.log_root:
            d = self.log_root / ("record_%s" % record_id)
            d.mkdir(parents=True, exist_ok=True)
            (d / "defs_only_compile.log").write_text(json.dumps({k: val for k, val in self.defs_only.items() if k != "full_argv"}, indent=1, ensure_ascii=False), encoding="utf-8")
        if not self.defs_only["ok"]:
            raise RuntimeError("defs_only.lean of %s did not compile in the audit workspace" % record_id)
        (self.ws.root / "CHECK_enum.lean").write_text(ENUM_LEAN, encoding="utf-8")

    def lean_full(self, file_name, olean=None, log_path=None):
        """Workspace.lean keeps only the last 6000 chars of Lean's output; the audit needs every printed line, so this mirrors
        Workspace.lean (same argv, same bubblewrap wrapper, same message parsing) and keeps the full output (also written to log_path)."""
        argv = ["lake", "env", "lean"] + (["-o", str(self.ws.lib / olean)] if olean else []) + [file_name]
        res = self.ws.run(argv)
        output = res["output"]
        messages = v.parse_messages(output)
        row = {"file": file_name, "argv": argv, "exit_code": res["exit_code"], "elapsed_seconds": res["elapsed_seconds"],
               "errors": [m for m in messages if m["severity"] == "error"], "warnings": [m for m in messages if m["severity"] == "warning"],
               "axioms": v.parse_axioms(output), "output": output, "output_sha256": sha_bytes(output.encode("utf-8", errors="replace")),
               "isolation": "bubblewrap", "log_path": None}
        row["ok"] = row["exit_code"] == 0 and not row["errors"]
        if log_path is not None:
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            Path(log_path).write_text("# argv: %s\n# exit_code: %s\n# elapsed_seconds: %s\n# output_sha256: %s\n" % (json.dumps(argv), row["exit_code"], row["elapsed_seconds"], row["output_sha256"]) + output, encoding="utf-8")
            row["log_path"] = str(log_path)
        self.ws.runs.append({k: val for k, val in row.items() if k != "output"} | {"output_tail": output[-6000:]})
        return row

    def _lean_row(self, row):
        return {k: row[k] for k in ("file", "argv", "exit_code", "elapsed_seconds", "output_sha256", "ok", "log_path") if k in row} | {"errors": row.get("errors", []), "warnings": row.get("warnings", []), "output": row.get("output", "")}

    def _olean_identity(self, reason_if_missing):
        p = self.ws.lib / "SUBMISSION.olean"
        if p.is_file():
            return {"path": str(p), "sha256": sha_file(p), "bytes": p.stat().st_size}
        return {"path": str(p), "sha256": None, "reason": reason_if_missing}

    def audit(self, submission_path, expected_sha256=None, roster_row=None, cell_tag=None):
        started = now_utc()
        log_dir = (self.log_root / (cell_tag or Path(submission_path).parent.name)) if self.log_root else None
        sub_bytes = Path(submission_path).read_bytes()
        text = sub_bytes.decode("utf-8", errors="replace")
        ns = self.ns
        sub_sha = sha_bytes(sub_bytes)
        result = {"audit_version": AUDIT_VERSION, "board_tasks": BOARD_TASKS, "record_id": self.record_id, "namespace": ns,
                  "submission_path": str(submission_path), "submission_sha256": sub_sha, "submission_bytes": len(sub_bytes), "started_utc": started,
                  "allowed_axioms": list(ALLOWED_AXIOMS),
                  "identities": json.loads(json.dumps(self.identities)) | {"packet": self.packet_identity, "submission_olean": None,
                                                                          "roster_row": roster_row},
                  "sha_check": {"expected_sha256": expected_sha256, "actual_sha256": sub_sha, "verified": (expected_sha256 is None) or (expected_sha256 == sub_sha)},
                  "text_scan": {}, "roster_agreement": None, "stages": {}, "stage_failures": [], "per_declaration": {}, "problems": [], "flags": {},
                  "private_helpers": {}, "anonymous_private_instances": {}, "private_auxiliaries": {}, "public_theorems": {}, "lean_run_logs": {}}
        if expected_sha256 is not None and expected_sha256 != sub_sha:
            result["problems"].append("refused: submission sha256 %s does not equal the roster's %s; no Lean process was run" % (sub_sha, expected_sha256))
            return self._finish(result, disposition="cannot resolve")
        # ---- text scan (pinned chunking) and roster agreement
        decls, anon, other, private_tokens = scan_declarations(text, ns)
        private_helpers = [d for d in decls if d["private"]]
        anon_private = [a for a in anon if a["private"]]
        other_private = [o for o in other if o["private"]]
        public_theorems = [d for d in decls if not d["private"] and d["kind"] in ("theorem", "lemma")]
        pinned_theorem_names = [d["name"] for d in decls if d["kind"] in ("theorem", "lemma")]   # what validate.py queries as NS.name
        accounted = len(private_helpers) + len(anon_private) + len(other_private)
        result["text_scan"] = {"declarations": decls, "private_helpers": [d["name"] for d in private_helpers],
                               "anonymous_instances": anon, "anonymous_private_instances": anon_private, "unnamed_other": other,
                               "public_theorems": [d["name"] for d in public_theorems],
                               "pinned_validator_would_query": ["%s.%s" % (ns, n) for n in pinned_theorem_names],
                               "pinned_validator_would_query_private": ["%s.%s" % (ns, d["name"]) for d in private_helpers if d["kind"] in ("theorem", "lemma")],
                               "private_token_lines": private_tokens, "private_tokens_accounted": accounted,
                               "private_tokens_unaccounted": len(private_tokens) != accounted}
        result["anonymous_private_instances"] = {"textual": anon_private, "candidates": {}, "resolution": None, "resolved_by_enumeration": False, "resolved_in_file": None}
        if result["text_scan"]["private_tokens_unaccounted"]:
            result["problems"].append("`private` tokens in the text (%d) do not match top-level private declarations (%d named + %d anonymous instance + %d other)" % (len(private_tokens), len(private_helpers), len(anon_private), len(other_private)))
        if roster_row is not None:
            exp = sorted((d["line"], d["kind"], d["name"]) for d in roster_row.get("declarations", []))
            got = sorted((d["line"], d["kind"], d["name"]) for d in private_helpers)
            exp_amb = sorted(i["line"] for i in roster_row.get("ambiguous_issues", []))
            got_anon = sorted(a["line"] for a in anon_private)
            result["roster_agreement"] = {"named_declarations_equal": exp == got, "roster_named": [list(x) for x in exp], "scan_named": [list(x) for x in got],
                                          "ambiguous_lines_equal_anonymous_private_instance_lines": exp_amb == got_anon,
                                          "roster_ambiguous_lines": exp_amb, "scan_anonymous_private_instance_lines": got_anon}
            if exp != got:
                result["problems"].append("text scan disagrees with the roster row on the named private declarations: roster %s vs scan %s" % (exp, got))
            if exp_amb != got_anon:
                result["problems"].append("roster ambiguous lines %s differ from the scanned anonymous private instance lines %s" % (exp_amb, got_anon))
        # ---- Stage 0: the unmodified submission
        for stale in (self.ws.lib / "SUBMISSION.olean", self.ws.lib / "SUBMISSION.ilean"):
            if stale.exists():
                stale.unlink()
        (self.ws.root / "SUBMISSION.lean").write_bytes(sub_bytes)
        comp = self.lean_full("SUBMISSION.lean", "SUBMISSION.olean", log_path=(log_dir / "stage0_compile_original.log") if log_dir else None)
        result["stages"]["compile_original"] = self._lean_row(comp)
        result["stages"]["compile_original"]["sorry_warnings"] = [m for m in comp["warnings"] if "sorry" in m["text"]]
        result["lean_run_logs"]["stage0_compile_original"] = comp["log_path"]
        result["identities"]["submission_olean"] = self._olean_identity("Stage 0 compile did not produce SUBMISSION.olean (exit %s)" % comp["exit_code"])
        if not comp["ok"]:
            result["stage_failures"].append({"stage": "compile_original", "exit_code": comp["exit_code"], "errors": comp["errors"]})
            result["problems"].append("Stage 0 failed: submission does not compile (exit %s): nothing can be resolved" % comp["exit_code"])
            return self._finish(result, disposition="cannot resolve")
        # ---- Stage B: exhaustive enumeration of the module's constants (count line required, complete, unique)
        enum = self.lean_full("CHECK_enum.lean", log_path=(log_dir / "stageB_enumerate_module.log") if log_dir else None)
        rows, count = parse_enum_output(enum["output"])
        result["lean_run_logs"]["stageB_enumerate_module"] = enum["log_path"]
        names_seen = [r["name"] for r in rows]
        dup = sorted({n for n in names_seen if names_seen.count(n) > 1})
        enum_ok = enum["exit_code"] == 0 and not enum["errors"] and bool(rows) and count is not None and count == len(rows) and not dup and all(r["kind"] != "missing" for r in rows)
        result["stages"]["enumerate_module"] = self._lean_row(enum) | {"ok": enum_ok, "constants_declared_by_module": count, "constants_parsed": len(rows),
                                                                      "count_line_present": count is not None, "duplicate_names": dup,
                                                                      "check_file_sha256": sha_bytes(ENUM_LEAN.encode())}
        per = result["per_declaration"]
        for row in rows:
            key = row["name"]
            bad = sorted(set(row["axioms"]) - set(ALLOWED_AXIOMS))
            if row["kind"] == "axiom":
                bad = sorted(set(bad) | {row["name"]})
            per[key] = {"kind": row["kind"], "private": row["private"], "user_name": row["user_name"], "axioms_enumeration": row["axioms"],
                        "axioms_in_file": None, "disallowed": bad}
        if not enum_ok:
            why = []
            if enum["exit_code"] != 0 or enum["errors"]:
                why.append("exit %s with %d error(s)" % (enum["exit_code"], len(enum["errors"])))
            if count is None:
                why.append("AUDIT_MODULE_CONSTANTS line missing")
            elif count != len(rows):
                why.append("count %d != %d parsed rows" % (count, len(rows)))
            if dup:
                why.append("duplicate constant names %s" % dup)
            if not rows:
                why.append("no AUDIT_AXIOMS rows")
            if any(r["kind"] == "missing" for r in rows):
                why.append("constant(s) with kind missing")
            result["stage_failures"].append({"stage": "enumerate_module", "exit_code": enum["exit_code"], "errors": enum["errors"], "why": why})
            result["problems"].append("Stage B enumeration is not complete/unique: " + "; ".join(why))
        # ---- classification of the module's private constants: named / auxiliary / candidate
        named_full = {d["full_name"]: d for d in private_helpers}
        classification = {"named": {}, "auxiliary": {}, "candidates": {}}
        for k, r in per.items():
            if not r["private"]:
                continue
            split = aux_split(r["user_name"])
            if split is not None:
                classification["auxiliary"][k] = {"user_name": r["user_name"], "parent_user_name": split[0], "aux_component": split[1], "kind": r["kind"],
                                                  "axioms": r["axioms_enumeration"], "disallowed": r["disallowed"]}
            elif any(user_name_matches(r["user_name"], ns, d["name"]) for d in private_helpers):
                classification["named"][k] = {"user_name": r["user_name"], "kind": r["kind"], "axioms": r["axioms_enumeration"], "disallowed": r["disallowed"]}
            else:
                classification["candidates"][k] = {"user_name": r["user_name"], "kind": r["kind"], "axioms": r["axioms_enumeration"], "disallowed": r["disallowed"],
                                                   "is_instance_shaped": r["kind"] in ("definition", "theorem") and last_component(r["user_name"]).startswith("inst")}
        result["private_auxiliaries"] = classification["auxiliary"]
        result["private_constants_classification"] = {"named": sorted(classification["named"]), "auxiliary": sorted(classification["auxiliary"]),
                                                      "candidates": sorted(classification["candidates"])}
        # ---- rule (e): anonymous private instance(s) resolved from the enumeration only
        cands = classification["candidates"]
        anon_res = {"textual": anon_private, "candidates": cands, "resolution": None, "resolved_by_enumeration": False, "resolved_in_file": None}
        if len(anon_private) == 1:
            if len(cands) == 1 and next(iter(cands.values()))["is_instance_shaped"]:
                k, c = next(iter(cands.items()))
                anon_res["resolution"] = {"line": anon_private[0]["line"], "head": anon_private[0]["head"], "constant": k, "user_name": c["user_name"],
                                          "kind": c["kind"], "axioms": c["axioms"], "disallowed": c["disallowed"]}
                anon_res["resolved_by_enumeration"] = True
            else:
                result["problems"].append("anonymous private instance at line %d cannot be resolved: %d candidate(s) %s (need exactly one definition/theorem whose user name starts with inst)" % (
                    anon_private[0]["line"], len(cands), sorted(cands)))
        elif len(anon_private) == 0:
            if cands and enum_ok:
                result["problems"].append("private constant(s) not explained by any textual private declaration: %s" % sorted(cands))
        else:
            result["problems"].append("%d anonymous private instances (lines %s) cannot be mapped to constants without fabricating names; candidates %s" % (
                len(anon_private), [a["line"] for a in anon_private], sorted(cands)))
        result["anonymous_private_instances"] = anon_res
        # ---- Stage A: in-file #print axioms for every named private helper, every public theorem and the resolved anonymous instance
        names_a = [d["name"] for d in private_helpers] + [d["name"] for d in public_theorems]
        anon_query = None
        if anon_res["resolution"] is not None:
            u = anon_res["resolution"]["user_name"]
            anon_query = u[len(ns) + 1:] if u.startswith(ns + ".") else u
            names_a.append(anon_query)
        if names_a:
            audited = in_file_audit_text(text, ns, names_a)
            (self.ws.root / "SUBMISSION.lean").write_text(audited, encoding="utf-8")
            infile = self.lean_full("SUBMISSION.lean", log_path=(log_dir / "stageA_in_file_print_axioms.log") if log_dir else None)   # no -o: nothing of the modified text is written to any olean
            result["lean_run_logs"]["stageA_in_file_print_axioms"] = infile["log_path"]
            ax_a = parse_axioms_multiline(infile["output"])
            infile_ok = infile["exit_code"] == 0 and not infile["errors"]
            result["stages"]["in_file_print_axioms"] = self._lean_row(infile) | {"ok": infile_ok, "audited_text_sha256": sha_bytes(audited.encode()),
                                                                                 "names_queried": names_a, "printed": ax_a,
                                                                                 "printed_by_pinned_single_line_parser": infile["axioms"]}
            if not infile_ok:
                result["stage_failures"].append({"stage": "in_file_print_axioms", "exit_code": infile["exit_code"], "errors": infile["errors"]})
                result["problems"].append("Stage A (in-file #print axioms) failed: exit %s, %d error(s)%s" % (
                    infile["exit_code"], len(infile["errors"]), (": " + "; ".join(e["text"][:160] for e in infile["errors"][:5])) if infile["errors"] else ""))
            for printed, axs in ax_a.items():
                is_priv, user = unmangle_private(printed)
                if printed in per:
                    per[printed]["axioms_in_file"] = sorted(axs)
                else:
                    per[printed] = {"kind": None, "private": is_priv, "user_name": user, "axioms_enumeration": None,
                                    "axioms_in_file": sorted(axs), "disallowed": sorted(set(axs) - set(ALLOWED_AXIOMS))}
                    result["problems"].append("in-file #print axioms printed a constant the enumeration did not list: %s" % printed)
            if len(ax_a) != len(names_a):
                result["problems"].append("Stage A printed %d axiom line(s) for %d queried name(s)" % (len(ax_a), len(names_a)))
        else:
            result["stages"]["in_file_print_axioms"] = {"ok": None, "not_applicable": True, "detail": "no private helper, no public theorem and no anonymous private instance in the text scan"}
        # ---- rule (d): every named textual private helper -> exactly one private constant by Stage B, the same one by Stage A
        helpers = {}
        for d in private_helpers:
            b_hits = sorted(k for k, r in per.items() if r["private"] and r["axioms_enumeration"] is not None and user_name_matches(r["user_name"], ns, d["name"]))
            a_hits = sorted(k for k, r in per.items() if r["private"] and r["axioms_in_file"] is not None and user_name_matches(r["user_name"], ns, d["name"]))
            row = {"kind": d["kind"], "line": d["line"], "full_name": d["full_name"], "resolved_constant": sorted(set(b_hits) | set(a_hits)),
                   "enumeration_hits": b_hits, "in_file_hits": a_hits,
                   "resolved_by_enumeration": len(b_hits) == 1, "resolved_in_file": len(a_hits) == 1 and a_hits == b_hits,
                   "axioms": sorted({a for k in set(b_hits) | set(a_hits) for a in (per[k]["axioms_enumeration"] or per[k]["axioms_in_file"] or [])}),
                   "disallowed": sorted({a for k in set(b_hits) | set(a_hits) for a in per[k]["disallowed"]})}
            row["resolved"] = row["resolved_by_enumeration"] and row["resolved_in_file"]
            if len(b_hits) != 1:
                result["problems"].append("private helper %s (line %d) matched %d enumerated private constant(s) %s; exactly one required" % (d["name"], d["line"], len(b_hits), b_hits))
            if not (len(a_hits) == 1 and a_hits == b_hits):
                result["problems"].append("private helper %s (line %d) not resolved by in-file #print axioms to the enumerated constant (in-file hits %s)" % (d["name"], d["line"], a_hits))
            for k in set(b_hits) & set(a_hits):
                if per[k]["axioms_enumeration"] != per[k]["axioms_in_file"]:
                    result["problems"].append("stages disagree on %s: enumeration %s vs in-file %s" % (k, per[k]["axioms_enumeration"], per[k]["axioms_in_file"]))
            helpers[d["name"]] = row
        result["private_helpers"] = helpers
        if anon_res["resolution"] is not None:
            k = anon_res["resolution"]["constant"]
            in_file = per[k]["axioms_in_file"]
            anon_res["resolved_in_file"] = in_file is not None and in_file == per[k]["axioms_enumeration"]
            anon_res["resolution"]["axioms_in_file"] = in_file
            anon_res["resolution"]["queried_as"] = ns + "." + anon_query
            if not anon_res["resolved_in_file"]:
                result["problems"].append("anonymous private instance constant %s: in-file #print axioms %s does not confirm the enumeration %s" % (k, in_file, per[k]["axioms_enumeration"]))
        pubs = {}
        for d in public_theorems:
            k = d["full_name"]
            r = per.get(k)
            pubs[d["name"]] = {"resolved": r is not None and r["axioms_enumeration"] is not None, "axioms": (r or {}).get("axioms_enumeration") if r else None,
                               "axioms_in_file": (r or {}).get("axioms_in_file") if r else None, "disallowed": (r or {}).get("disallowed", []) if r else []}
            if r is None or r["axioms_enumeration"] is None:
                result["problems"].append("public theorem %s not found among module constants" % k)
            elif r["axioms_in_file"] is None:
                result["problems"].append("public theorem %s not printed by Stage A" % k)
            elif r["axioms_in_file"] != r["axioms_enumeration"]:
                result["problems"].append("stages disagree on %s: enumeration %s vs in-file %s" % (k, r["axioms_enumeration"], r["axioms_in_file"]))
        result["public_theorems"] = pubs
        # ---- olean identity must be unchanged by Stage A (which compiles without -o)
        after = self._olean_identity("SUBMISSION.olean missing after Stage A")
        result["identities"]["submission_olean_after_stage_A"] = after
        result["identities"]["submission_olean_unchanged_after_stage_A"] = after.get("sha256") == (result["identities"]["submission_olean"] or {}).get("sha256")
        if not result["identities"]["submission_olean_unchanged_after_stage_A"]:
            result["problems"].append("SUBMISSION.olean changed between Stage 0 and the end of Stage A")
        # ---- flags and disposition
        disallowed_all = {k: r["disallowed"] for k, r in per.items() if r["disallowed"]}
        result["flags"] = {"uses_disallowed_axiom": bool(disallowed_all), "disallowed_by_constant": disallowed_all,
                           "declares_axiom": sorted(k for k, r in per.items() if r["kind"] == "axiom"),
                           "unresolved_private_helper": [n for n, r in helpers.items() if not r["resolved"]],
                           "anonymous_private_instance_resolved": (anon_res["resolved_by_enumeration"] and bool(anon_res["resolved_in_file"])) if anon_private else None,
                           "private_constants_in_module": sorted(k for k, r in per.items() if r["private"]),
                           "axioms_union_all_constants": sorted({a for r in per.values() for a in (r["axioms_enumeration"] or r["axioms_in_file"] or [])}),
                           "private_tokens_unaccounted": result["text_scan"]["private_tokens_unaccounted"],
                           "stage_failures": [s["stage"] for s in result["stage_failures"]]}
        if disallowed_all:
            disposition = "uses disallowed axiom"
        elif result["problems"]:
            disposition = "cannot resolve"
        else:
            disposition = "clean"
        return self._finish(result, disposition)

    def _finish(self, result, disposition):
        result["disposition"] = disposition
        result["finished_utc"] = now_utc()
        result["lean_version"] = self.lean_version["output"]
        result["workspace"] = str(self.ws.root)
        return result


# ------------------------------------------------------------------------------------------------------- grades
def grade_profile(file_name):
    """(profile, filename root prefix, bare cell key) from a study grading file name: `<cell>.GRADE…` -> v1_bare, `<cell>__ckv2.…` -> ckv2,
    `<cell>__ckv3.…` -> ckv3; a leading `v2__` / `v2b__` / `v2c__` / `s45r7__` / `s45r8__` is the naming convention's root prefix (recorded,
    never trusted for binding)."""
    key = file_name[:-len(GRADE_SUFFIX)] if file_name.endswith(GRADE_SUFFIX) else file_name
    profile = "ckv3" if key.endswith("__ckv3") else "ckv2" if key.endswith("__ckv2") else "v1_bare"
    base = key[:-len("__ckv2")] if profile != "v1_bare" else key
    prefix = base.split("__", 1)[0] if "__" in base and base.split("__", 1)[0] in GRADE_FILENAME_PREFIX_TO_ROOT else None
    return profile, prefix, base


def load_all_grades(grading_dir=GRADING_DIR):
    rows = []
    for f in sorted(Path(grading_dir).glob("*" + GRADE_SUFFIX)):
        profile, prefix, base = grade_profile(f.name)
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:       # noqa: BLE001
            rows.append({"grade_file": f.name, "grade_file_sha256": sha_file(f), "profile": profile, "unreadable": "%s: %s" % (type(exc).__name__, exc)})
            continue
        ax = (d.get("checks") or {}).get("axioms") or {}
        cf = (d.get("checks") or {}).get("check_file") or {}
        check_out = (d.get("lean_outputs") or {}).get("CHECK.lean") or ""
        rows.append({"grade_file": f.name, "grade_file_sha256": sha_file(f), "profile": profile, "filename_root_prefix": prefix, "filename_cell_key": base,
                     "submission_path": d.get("submission_path"), "submission_sha256": d.get("submission_sha256"), "record_id": d.get("record_id"),
                     "verdict": d.get("verdict"), "failed_checks": (d.get("overall") or {}).get("failed_checks"),
                     "started_utc": d.get("started_utc"), "finished_utc": d.get("finished_utc"),
                     "axioms_pass": ax.get("pass"), "axioms_not_reported": ax.get("not_reported"), "axioms_disallowed": ax.get("disallowed"),
                     "axioms_per_theorem": ax.get("per_theorem"), "axioms_allowed": ax.get("allowed"),
                     "check_file_exit_code": cf.get("exit_code"), "check_file_errors_parsed": cf.get("errors"),
                     "check_file_error_lines": [ln for ln in check_out.splitlines() if "error" in ln],
                     "validator_files_sha256": (d.get("invocation") or {}).get("validator_files_sha256"),
                     "invocation_argv0": ((d.get("invocation") or {}).get("argv") or [None])[0],
                     "checker_version": d.get("checker_version"), "validator_version": d.get("validator_version"),
                     "packet_sha256": {k: (d.get("packet_sha256") or {}).get(k) for k in ("task.json", "defs_only.lean")}})
    return rows


def bind_grades(cell, res, grades):
    """Grades bound to a roster cell: submission sha256 AND absolute submission path must both match. Path-only and sha-only hits are listed
    under `not_bound` and never used. Per bound grade the pinned mechanism is read: did the axioms check fail with `not_reported` equal to the
    private theorem/lemma names the validator queried as NS.<name>?"""
    abs_path = cell["submission_abs_path"]
    sha = cell["submission_sha256"]
    expected_nr = sorted(res.get("text_scan", {}).get("pinned_validator_would_query_private") or [])
    bound, not_bound = [], []
    for g in grades:
        if g.get("unreadable"):
            continue
        p_ok, s_ok = g["submission_path"] == abs_path, g["submission_sha256"] == sha
        if p_ok and s_ok:
            nr = sorted(g["axioms_not_reported"] or [])
            row = dict(g)
            row["filename_root_prefix_implies_root"] = GRADE_FILENAME_PREFIX_TO_ROOT.get(g["filename_root_prefix"], "harness/runs" if g["filename_root_prefix"] is None else None)
            row["filename_root_consistent_with_roster_root"] = row["filename_root_prefix_implies_root"] == cell["root"]
            row["validate_py_sha256_matches_audit"] = (g["validator_files_sha256"] or {}).get("validate.py") == res["identities"]["validate_py"]["sha256"]
            row["packet_sha256_matches_audit"] = (g["packet_sha256"].get("task.json") == res["identities"]["packet"]["task.json_sha256"] and
                                                  g["packet_sha256"].get("defs_only.lean") == res["identities"]["packet"]["defs_only.lean_sha256"])
            row["mechanism"] = {"axioms_check_failed": g["axioms_pass"] is False, "not_reported": nr, "expected_private_theorem_names": expected_nr,
                                "not_reported_equals_expected_private_names": nr == expected_nr,
                                "not_reported_outside_expected": sorted(set(nr) - set(expected_nr)),
                                "expected_not_in_not_reported": sorted(set(expected_nr) - set(nr)),
                                "check_file_exit_code": g["check_file_exit_code"], "check_file_errors_parsed_by_pinned_MESSAGE_RE": g["check_file_errors_parsed"],
                                "unknown_constant_error_lines": [ln for ln in g["check_file_error_lines"] if "Unknown constant" in ln],
                                "axioms_check_failed_with_not_reported_for_private_names": (g["axioms_pass"] is False) and bool(nr) and set(nr) <= set(expected_nr) and bool(expected_nr)}
            bound.append(row)
        elif p_ok or s_ok:
            not_bound.append({"grade_file": g["grade_file"], "profile": g["profile"], "path_match": p_ok, "sha_match": s_ok, "submission_path": g["submission_path"],
                              "submission_sha256": g["submission_sha256"], "verdict": g["verdict"], "why_not_bound": "path-only hit" if p_ok else "sha-only hit"})
    return {"bound": bound, "not_bound": not_bound, "bound_profiles": sorted(b["profile"] for b in bound), "bound_count": len(bound)}


# --------------------------------------------------------------------------------------------------------- roster run
def preflight(roster_path, results_dir):
    """No Lean: roster sha, every roster submission's sha, grade binding candidates. Written to results/PREFLIGHT.json."""
    roster, roster_sha = load_roster(roster_path)
    cells = roster_cells(roster)
    grades = load_all_grades()
    out = {"audit_version": AUDIT_VERSION, "generated_utc": now_utc(), "roster": {"path": str(roster_path), "sha256": roster_sha, "expected_sha256": ROSTER_SHA256_EXPECTED},
           "identities": tool_identities(), "grades_scanned": len(grades), "cells": []}
    for c in cells:
        p = Path(c["submission_abs_path"])
        actual = sha_file(p) if p.is_file() else None
        fake_res = {"text_scan": {"pinned_validator_would_query_private": []}, "identities": {"validate_py": out["identities"]["validate_py"], "packet": {"task.json_sha256": None, "defs_only.lean_sha256": None}}}
        b = bind_grades(c, fake_res, grades)
        out["cells"].append({k: c[k] for k in ("root", "root_tag", "cell", "record_id", "submission_path", "submission_sha256")} | {
            "submission_exists": p.is_file(), "actual_sha256": actual, "sha_verified": actual == c["submission_sha256"],
            "named_private_declarations": len(c["declarations"]), "ambiguous_issues": c["ambiguous_issues"],
            "grades_bound": [{k: g[k] for k in ("grade_file", "profile", "verdict", "axioms_pass", "axioms_not_reported", "filename_root_consistent_with_roster_root")} for g in b["bound"]],
            "grades_not_bound": b["not_bound"]})
    rc.atomic_json(Path(results_dir) / "PREFLIGHT.json", out)
    return out


def run_roster(a):
    results_dir = Path(a.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    log_root = results_dir / "lean_logs"
    run_started = now_utc()
    roster, roster_sha = load_roster(a.roster)
    cells = roster_cells(roster)
    grades_snapshot_utc = now_utc()
    grades = load_all_grades()
    driver_log = results_dir / "ROSTER_RUN.log"
    def log(msg):
        line = "%s %s" % (now_utc(), msg)
        print(line, flush=True)
        with driver_log.open("a", encoding="utf-8") as h:
            h.write(line + "\n")
    log("ROSTER_AUDIT START roster_sha256=%s cells=%d grades_scanned=%d audit_script_sha256=%s" % (roster_sha, len(cells), len(grades), sha_file(__file__)))
    auditors, table, lean_logs = {}, [], []
    for c in cells:
        tag = "%s__%s" % (c["root_tag"], c["cell"])
        rid = c["record_id"]
        if rid not in auditors:
            log("record %s: building workspace (defs_only compile, one Lean process)" % rid)
            auditors[rid] = Auditor(Path(a.workspace) / rid, a.cache_dir, rid, a.packet_dir, log_root=log_root)
        auditor = auditors[rid]
        row = {k: c[k] for k in ("root", "root_tag", "cell", "record_id", "arm", "attempt", "model", "submission_path", "submission_abs_path", "submission_sha256", "record_sha256", "ambiguous_issues")}
        row["roster_declarations"] = c["declarations"]
        p = Path(c["submission_abs_path"])
        if not p.is_file():
            row.update(disposition="cannot resolve", problems=["refused: roster submission file is missing"], result_file=None, result_sha256=None, sha_verified=False)
            table.append(row)
            log("%s: MISSING submission file" % tag)
            continue
        log("%s: audit start (record %s, namespace %s)" % (tag, rid, auditor.ns))
        res = auditor.audit(p, expected_sha256=c["submission_sha256"], roster_row=c, cell_tag=tag)
        res["roster"] = {"path": str(a.roster), "sha256": roster_sha, "root": c["root"], "root_tag": c["root_tag"], "cell": c["cell"]}
        res["grades"] = bind_grades(c, res, grades) | {"grading_dir": str(GRADING_DIR), "snapshot_utc": grades_snapshot_utc, "grades_scanned": len(grades)}
        out = results_dir / ("%s.audit.json" % tag)
        rc.atomic_json(out, res)
        helpers = res.get("private_helpers") or {}
        anon = res.get("anonymous_private_instances") or {}
        row.update(namespace=res["namespace"], sha_verified=res["sha_check"]["verified"], disposition=res["disposition"], problems=res["problems"],
                   stage_failures=[s["stage"] for s in res.get("stage_failures", [])],
                   roster_agreement=res.get("roster_agreement"),
                   named_private_helpers_in_roster=len(c["declarations"]), named_private_helpers_scanned=len(helpers),
                   named_private_helpers_resolved_both_stages=sum(1 for r in helpers.values() if r["resolved"]),
                   private_helpers={n: {"kind": r["kind"], "line": r["line"], "resolved_constant": r["resolved_constant"], "resolved": r["resolved"], "axioms": r["axioms"], "disallowed": r["disallowed"]} for n, r in helpers.items()},
                   anonymous_private_instances={"textual_lines": [x["line"] for x in anon.get("textual", [])], "candidates": sorted(anon.get("candidates", {})),
                                                "resolution": anon.get("resolution"), "resolved_by_enumeration": anon.get("resolved_by_enumeration"), "resolved_in_file": anon.get("resolved_in_file")},
                   private_auxiliaries={k: {"parent": x["parent_user_name"], "kind": x["kind"], "axioms": x["axioms"]} for k, x in (res.get("private_auxiliaries") or {}).items()},
                   public_theorems={k: r["axioms"] for k, r in (res.get("public_theorems") or {}).items()},
                   axioms_union_all_constants=res["flags"].get("axioms_union_all_constants", []),
                   disallowed_by_constant=res["flags"].get("disallowed_by_constant", {}),
                   private_constants_in_module=res["flags"].get("private_constants_in_module", []),
                   module_constants=res["stages"].get("enumerate_module", {}).get("constants_declared_by_module"),
                   identities={"submission_olean_sha256": (res["identities"].get("submission_olean") or {}).get("sha256"),
                               "submission_olean_unchanged_after_stage_A": res["identities"].get("submission_olean_unchanged_after_stage_A"),
                               "packet": res["identities"]["packet"]},
                   grades_bound=[{k: g[k] for k in ("grade_file", "grade_file_sha256", "profile", "filename_root_prefix", "filename_root_consistent_with_roster_root", "verdict", "failed_checks",
                                                    "axioms_pass", "axioms_not_reported", "axioms_disallowed", "validate_py_sha256_matches_audit", "packet_sha256_matches_audit", "checker_version", "validator_version", "mechanism")} for g in res["grades"]["bound"]],
                   grades_not_bound=res["grades"]["not_bound"],
                   lean_run_logs=res["lean_run_logs"], started_utc=res["started_utc"], finished_utc=res["finished_utc"],
                   result_file=str(out), result_sha256=sha_file(out))
        lean_logs.extend(x for x in res["lean_run_logs"].values() if x)
        table.append(row)
        log("%s: %s sha=%s helpers_resolved=%d/%d anon=%s grades=%s problems=%d" % (
            tag, res["disposition"], res["submission_sha256"][:16], row["named_private_helpers_resolved_both_stages"], len(helpers),
            (anon.get("resolution") or {}).get("constant") if anon.get("textual") else "n/a", [g["profile"] + ":" + str(g["verdict"]) for g in res["grades"]["bound"]], len(res["problems"])))
    ids = tool_identities()
    ids["lean_env"]["lean_version"] = next(iter(auditors.values())).lean_version["output"] if auditors else None
    summary = {"audit_version": AUDIT_VERSION, "board_tasks": BOARD_TASKS, "run_started_utc": run_started, "generated_utc": now_utc(),
               "roster": {"path": str(a.roster), "sha256": roster_sha, "expected_sha256": ROSTER_SHA256_EXPECTED, "schema": roster.get("schema"),
                          "roster_generated_utc": roster.get("generated_utc"), "counts": roster.get("counts"), "roots": roster.get("roots"),
                          "scanner_reviewed_validator_sha256": (roster.get("scanner") or {}).get("reviewed_validator_sha256"),
                          "scanner_reviewed_audit_source_sha256": (roster.get("scanner") or {}).get("reviewed_audit_source_sha256")},
               "identities": ids, "packets": {rid: au.packet_identity | {"namespace": au.ns} for rid, au in auditors.items()},
               "grades": {"grading_dir": str(GRADING_DIR), "snapshot_utc": grades_snapshot_utc, "grades_scanned": len(grades)},
               "cells": table, "lean_run_logs": lean_logs + [str(log_root / ("record_%s" % rid) / "defs_only_compile.log") for rid in auditors],
               "driver_log": str(driver_log),
               "counts": {"cells": len(table), "sha_verified": sum(1 for r in table if r.get("sha_verified")),
                          "by_disposition": {d: sum(1 for r in table if r["disposition"] == d) for d in sorted({r["disposition"] for r in table})},
                          "by_record": {rid: sum(1 for r in table if r["record_id"] == rid) for rid in sorted({r["record_id"] for r in table})},
                          "named_private_helpers_in_roster": sum(r.get("named_private_helpers_in_roster", 0) for r in table),
                          "named_private_helpers_resolved_both_stages": sum(r.get("named_private_helpers_resolved_both_stages", 0) for r in table),
                          "cells_with_anonymous_private_instance": sum(1 for r in table if (r.get("anonymous_private_instances") or {}).get("textual_lines")),
                          "anonymous_private_instances_resolved": sum(1 for r in table if (r.get("anonymous_private_instances") or {}).get("resolved_by_enumeration") and (r.get("anonymous_private_instances") or {}).get("resolved_in_file")),
                          "cells_with_bound_grade": sum(1 for r in table if r.get("grades_bound")),
                          "bound_grades_by_profile": {p: sum(1 for r in table for g in r.get("grades_bound", []) if g["profile"] == p) for p in ("v1_bare", "ckv2", "ckv3")},
                          "bound_grades_axioms_failed_with_not_reported_for_private_names": sum(1 for r in table for g in r.get("grades_bound", []) if g["mechanism"]["axioms_check_failed_with_not_reported_for_private_names"]),
                          "cells_with_stage_failure": sum(1 for r in table if r.get("stage_failures"))}}
    summary["finished_utc"] = now_utc()
    rc.atomic_json(results_dir / "ROSTER_AUDIT_SUMMARY.json", summary)
    log("ROSTER_AUDIT DONE counts=%s summary=%s" % (json.dumps(summary["counts"]["by_disposition"]), results_dir / "ROSTER_AUDIT_SUMMARY.json"))
    print(json.dumps(summary["counts"], indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--roster", default=str(ROSTER_PATH_DEFAULT), help="the sha-pinned roster (default: the reviewer's roster)")
    ap.add_argument("--roster-run", action="store_true", help="audit every roster cell, in roster order, one Lean process at a time")
    ap.add_argument("--preflight", action="store_true", help="no Lean: verify roster + submission sha256s, list grade binding candidates")
    ap.add_argument("--record", default="E01", help="single-submission mode: record id (namespace from its packet)")
    ap.add_argument("--submission", help="single-submission mode: audit one file")
    ap.add_argument("--expected-sha256", help="single-submission mode: refuse unless the file hashes to this")
    ap.add_argument("--workspace", default=str(HERE / "scratch/ws_roster"))
    ap.add_argument("--cache-dir", default=str(HERE / "scratch/validate_cache"))
    ap.add_argument("--out", help="single-submission mode: write the result JSON here")
    ap.add_argument("--results-dir", default=str(HERE / "results"))
    ap.add_argument("--packet-dir")
    a = ap.parse_args()
    if a.preflight:
        out = preflight(Path(a.roster), a.results_dir)
        print(json.dumps({"roster_sha256": out["roster"]["sha256"], "cells": [{k: c[k] for k in ("root_tag", "cell", "sha_verified")} | {"grades_bound": [(g["profile"], g["verdict"]) for g in c["grades_bound"]]} for c in out["cells"]]}, indent=1))
        return 0 if all(c["sha_verified"] for c in out["cells"]) else 1
    if a.roster_run:
        return run_roster(a)
    if a.submission:
        auditor = Auditor(Path(a.workspace) / a.record, a.cache_dir, a.record, a.packet_dir)
        res = auditor.audit(a.submission, expected_sha256=a.expected_sha256)
        if a.out:
            rc.atomic_json(a.out, res)
        print(json.dumps({"submission_sha256": res["submission_sha256"], "disposition": res["disposition"], "private_helpers": res.get("private_helpers"),
                          "anonymous_private_instances": (res.get("anonymous_private_instances") or {}).get("resolution"),
                          "flags": res.get("flags"), "problems": res["problems"], "out": a.out}, indent=1, ensure_ascii=False))
        return 0 if res["disposition"] == "clean" else 1
    ap.error("give --roster-run, --preflight, or --submission FILE")


if __name__ == "__main__":
    sys.exit(main())
