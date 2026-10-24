#!/bin/bash
# check_record_v2.sh E0k SUBMISSION.lean [OUT_JSON]        checker_version v2-identifiers-20260924
# Copy of evaluator_records/check_record.sh (v1, sha256 1406d9b026ccff4bbe98c17cbe36dbba723429fc0004df6f4dafc79ac01e7202) with
# exactly these changes (board TASK-998 reviewer decision, TASK-999 reviewer identifier lists; identifiers ONLY, no lambda exception):
#  (1) OUT = evaluator_records_v2: the record's evaluator.json is read from there. E05/E10/E11 carry the approved
#      hole_syntax.allowed_identifiers (E05 [Finset.range, Finset.sum]; E10 [Fintype.card, Finset.range, Finset.sum];
#      E11 [Int.natAbs, normalize, abs]); every other record's evaluator.json is byte-identical to v1. Forbidden tokens (incl. the
#      `fun` ban), regex, max_lines, has_final_theorem, obligations, hidden checks and imports/anti-shadowing are unchanged.
#  (2) validate.py receives --hole-grammar $OUT/$REC/evaluator.json, so the v2 allowed_identifiers reach text_checks (reserved
#      names, fix_r5), hole_identifier_check (fix_r4) and hole_grammar_check inside validate.py and are pinned as
#      pinned["evaluator.json"] / evaluator_contract. --evaluator-dir is deliberately NOT used: in validate.py dc81a986 it is
#      the directory of reference.lean / AGREE.lean / instances.json (hidden_instance_agreement) and its grammar is looked up at
#      <dir>/evaluator.json with a fallback to evaluator_records/<REC>/evaluator.json (v1); pointing it at evaluator_records_v2
#      would fail the hidden checks ("evaluator files missing") and leave the v1 grammar in force.
#  (3) checker_version and the sha256 of this script, validate.py, repair_common.py, the v2 evaluator.json, the v1 evaluator.json
#      and the v1 checker are stamped into the printed verdict AND into OUT_JSON (the validate.py verdict; all v1 fields kept),
#      together with two consistency flags (grammar_pin_matches_v2, v2_allowlist_reached_identifier_check).
# Everything else (the wrapper's own hole-grammar pass, harness_pass rule, output fields, exit codes) is the v1 text.
set -uo pipefail
TRACK=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT="$TRACK/evaluator_records_v2"
V1="$TRACK/evaluator_records"
HARNESS="$TRACK/harness"
export DISABLE_AUTOUPDATER=1
REC=$1; SUB=$(readlink -f "$2"); OUTJ=${3:-}
SELF=$(readlink -f "${BASH_SOURCE[0]}")
CHECKER_VERSION=v2-identifiers-20260924
CK_SHA=$(sha256sum "$SELF" | cut -d' ' -f1)
V1CK_SHA=$(sha256sum "$V1/check_record.sh" | cut -d' ' -f1)
VAL_SHA=$(sha256sum "$HARNESS/validate.py" | cut -d' ' -f1)
RC_SHA=$(sha256sum "$HARNESS/repair_common.py" | cut -d' ' -f1)
EV2_SHA=$(sha256sum "$OUT/$REC/evaluator.json" | cut -d' ' -f1)
EV1_SHA=$(sha256sum "$V1/$REC/evaluator.json" | cut -d' ' -f1)
mkdir -p "$OUT/_runs/validate_cache"
WS=$(mktemp -d "$OUT/_runs/vw_${REC}_XXXXXX")
python3 "$HARNESS/validate.py" --record "$REC" --submission "$SUB" --out "$WS/verdict.json" --workspace "$WS/ws" --cache-dir "$OUT/_runs/validate_cache" --hole-grammar "$OUT/$REC/evaluator.json" > "$WS/summary.txt" 2> "$WS/stderr.txt"
python3 - "$WS/verdict.json" "$OUT/$REC/evaluator.json" "$REC" "$SUB" "$WS/stderr.txt" "$CHECKER_VERSION" "$SELF" "$CK_SHA" "$V1/check_record.sh" "$V1CK_SHA" "$HARNESS/validate.py" "$VAL_SHA" "$HARNESS/repair_common.py" "$RC_SHA" "$EV2_SHA" "$V1/$REC/evaluator.json" "$EV1_SHA" <<'PY'
import json, re, sys, os
vpath, epath, rec, sub, err, ckver, ckpath, cksha, v1ckpath, v1cksha, valpath, valsha, rcpath, rcsha, ev2sha, ev1path, ev1sha = sys.argv[1:]
ev = json.load(open(epath))
stamp = {"checker_version": ckver,
         "checker_v2": {"path": ckpath, "sha256": cksha}, "checker_v1": {"path": v1ckpath, "sha256": v1cksha},
         "validate_py": {"path": valpath, "sha256": valsha}, "repair_common_py": {"path": rcpath, "sha256": rcsha},
         "evaluator_json_v2": {"path": epath, "sha256": ev2sha}, "evaluator_json_v1": {"path": ev1path, "sha256": ev1sha},
         "v2_allowed_identifiers": (ev.get("hole_syntax") or {}).get("allowed_identifiers")}
if not os.path.exists(vpath):
    print(json.dumps({"record_id": rec, "submission": sub, "verdict": "ERROR", "reason": "validator produced no verdict", "stderr": open(err).read()[-3000:], **stamp}, indent=1)); sys.exit(2)
v = json.load(open(vpath))
pin_ok = ((v.get("pinned") or {}).get("evaluator.json") or {}).get("sha256") == ev2sha
ident = ((v.get("checks") or {}).get("hole_syntax") or {}).get("identifiers") or {}
reached = ident.get("allowed_identifiers") == sorted((ev.get("hole_syntax") or {}).get("allowed_identifiers") or []) if ident else None
stamp.update({"grammar_pin_matches_v2": pin_ok, "v2_allowlist_reached_identifier_check": reached})
v.update(stamp)
tmp = vpath + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(v, f, indent=1, ensure_ascii=False)
os.replace(tmp, vpath)
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
       "validator_hole_syntax_problems": (v["checks"].get("hole_syntax") or {}).get("problems"),
       "endpoint_final_not_applicable": (not has_final),
       "harness_verdict_file": vpath, **stamp}
print(json.dumps(out, indent=1, ensure_ascii=False))
sys.exit(0 if allp else 1)
PY
RC=$?
[ -n "$OUTJ" ] && cp "$WS/verdict.json" "$OUTJ" 2>/dev/null
rm -rf "$WS/ws"
exit $RC
