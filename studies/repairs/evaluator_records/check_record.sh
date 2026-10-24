#!/bin/bash
# check_record.sh E0k SUBMISSION.lean [OUT_JSON]
# Wrapper around the harness validator (../harness/validate.py: imports, namespace, forbidden tokens, reserved names,
# template structure, obligations, compile, no sorry, axioms, universal/nonvacuity/final type checks, hidden-instance
# agreement) plus the one check the harness does not have: the record's hole grammar (evaluator.json -> hole_syntax,
# applied to the validator's `hole_filled_with`). Prints one JSON verdict; exit 0 iff PASS.
set -uo pipefail
TRACK=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT="$TRACK/evaluator_records"
HARNESS="$TRACK/harness"
export DISABLE_AUTOUPDATER=1
REC=$1; SUB=$(readlink -f "$2"); OUTJ=${3:-}
mkdir -p "$OUT/_runs/validate_cache"
WS=$(mktemp -d "$OUT/_runs/vw_${REC}_XXXXXX")
python3 "$HARNESS/validate.py" --record "$REC" --submission "$SUB" --out "$WS/verdict.json" --workspace "$WS/ws" --cache-dir "$OUT/_runs/validate_cache" > "$WS/summary.txt" 2> "$WS/stderr.txt"
python3 - "$WS/verdict.json" "$OUT/$REC/evaluator.json" "$REC" "$SUB" "$WS/stderr.txt" <<'PY'
import json, re, sys, os
vpath, epath, rec, sub, err = sys.argv[1:]
ev = json.load(open(epath))
if not os.path.exists(vpath):
    print(json.dumps({"record_id": rec, "submission": sub, "verdict": "ERROR", "reason": "validator produced no verdict", "stderr": open(err).read()[-3000:]}, indent=1)); sys.exit(2)
v = json.load(open(vpath))
hole = (v["checks"]["template_structure"] or {}).get("hole_filled_with")
hs = ev.get("hole_syntax", {})
problems = []
if hole is None:
    problems.append("hole_not_extracted")
else:
    if hs.get("regex") and not re.fullmatch(hs["regex"], hole.strip(), re.S): problems.append("hole_regex_mismatch")
    for tok in hs.get("forbidden_tokens", []):
        if (tok in ("/", "%", "∑", "if") and (tok in hole if tok != "if" else re.search(r"\bif\b", hole))) or \
           (tok not in ("/", "%", "∑", "if") and re.search(r"(?<![A-Za-z0-9_'.])" + re.escape(tok) + r"(?![A-Za-z0-9_'])", hole)):
            problems.append("hole_forbidden_token:" + tok)
    if hole.count("\n") + 1 > hs.get("max_lines", 1): problems.append("hole_too_many_lines")
hole_ok = not problems
_src = re.sub(r"--[^\n]*", "", open(sub, encoding="utf-8").read())
lib = sorted({n for n in ev.get("library_shortcut_names", []) if re.search(r"(?<![A-Za-z0-9_'])" + re.escape(n.split(".")[-1]) + r"(?![A-Za-z0-9_'])", _src)})
has_final = ev.get("has_final_theorem", True)
# harness defect (validate.py): with no `final` obligation, endpoint_final is reported as failed and all_pass is False even
# though README says the final role may be absent; for such records the verdict is repair_valid (+ hole grammar).
harness_pass = v["overall"]["all_pass"] if has_final else v["overall"]["repair_valid"]
allp = harness_pass and hole_ok
out = {"record_id": rec, "submission": sub, "submission_sha256": v["submission_sha256"], "started_utc": v["started_utc"], "finished_utc": v["finished_utc"],
       "verdict": "PASS" if allp else "FAIL",
       "harness": {"all_pass": v["overall"]["all_pass"], "repair_valid": v["overall"]["repair_valid"], "endpoint_proved": v["overall"]["endpoint_proved"],
                   "failed_checks": v["overall"]["failed_checks"], "final_declared_cannot": v["final_declared_cannot"],
                   "checks": {k: c.get("pass") for k, c in v["checks"].items() if isinstance(c, dict) and "pass" in c}},
       "hole_filled_with": hole, "hole_syntax": {"pass": hole_ok, "problems": problems, "rule": hs},
       "library_shortcuts_used": lib, "axioms": v["checks"].get("axioms", {}).get("per_theorem"),
       "failed_checks_all": [c for c in v["overall"]["failed_checks"] if has_final or c != "endpoint_final"] + (["hole_syntax"] if not hole_ok else []),
       "hole_syntax_problems": problems,
       "endpoint_final_not_applicable": (not has_final),
       "harness_verdict_file": vpath}
print(json.dumps(out, indent=1, ensure_ascii=False))
sys.exit(0 if allp else 1)
PY
RC=$?
[ -n "$OUTJ" ] && cp "$WS/verdict.json" "$OUTJ" 2>/dev/null
rm -rf "$WS/ws"
exit $RC
