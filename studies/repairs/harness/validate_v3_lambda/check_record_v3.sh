#!/bin/bash
# check_record_v3.sh E0k SUBMISSION.lean [OUT_JSON]        checker_version v3-lambda-20260924
# Copy of evaluator_records/check_record.sh (v1, sha256 1406d9b026ccff4bbe98c17cbe36dbba723429fc0004df6f4dafc79ac01e7202) with exactly
# these changes (board TASK-999 reviewer rule, TASK-1000 reviewer approval, TASK-1002 reviewer confirmation: E10 summand-lambda exception on top of the
# identifier-only v2 lists; nothing broader):
#  (1) VALIDATOR: harness/validate_v3_lambda/validate_v3_lambda.py, a wrapper that runs the pinned harness/validate.py (sha256 dc81a986...)
#      unchanged and post-processes ONLY checks.hole_syntax for record E10 (a `fun` is admitted iff every `fun` of the hole is the summand
#      lambda of `Finset.sum (Finset.range R) (fun k => BODY)` with one bare binder and BODY inside the task's matrix grammar; the `∑ k ∈/in
#      Finset.range R, BODY` spellings are judged by the same binder/BODY rule). For every other record the verdict is the pinned one.
#  (2) GRAMMAR SOURCE: --hole-grammar evaluator_records_v2/$REC/evaluator.json (identifier-only v2: E10 [Fintype.card, Finset.range,
#      Finset.sum]; E05 [Finset.range, Finset.sum]; E11 [Int.natAbs, normalize, abs]; every other record byte-identical to v1), together with
#      --evaluator-dir harness/evaluator/$REC, the pinned DEFAULT made explicit. --evaluator-dir is NOT pointed at evaluator_records_v2: in
#      validate.py dc81a986 that flag names the hidden-evaluator directory (reference.lean / AGREE.lean / instances.json, the
#      hidden_instance_agreement check); evaluator_records_v2/<REC>/ holds only evaluator.json, so the hidden checks would fail
#      ("evaluator files missing") and the grammar lookup would still fall back to v1. The wrapper's own grammar pass below reads the same
#      v2 file.
#  (3) WRAPPER GRAMMAR PASS (kept from v1): `hole_forbidden_token:fun` is dropped iff the validator's E10 rule lifted it
#      (checks.hole_syntax.e10_summand_lambda.fun_ban_lifted == true), and the validator's `e10_summand_lambda:` problems are appended, so
#      the wrapper verdict cannot disagree with the validator on the lambda; every other forbidden token, the regex and max_lines are the
#      v1 pass.
#  (4) STAMP: checker_version v3-lambda-20260924 and the sha256 of this script, validate_v3_lambda.py, validate.py, repair_common.py, the v2
#      evaluator.json used, the v1 evaluator.json and the v1/v2 checkers are written into the printed verdict AND into OUT_JSON (the
#      validator verdict, all fields kept), with two consistency flags (grammar_pin_matches_v2, v2_allowlist_reached_identifier_check).
#      The field `pre_lambda_v2_grammar_verdict` (= the validator's `pre_lambda_verdict`) is the PINNED validate.py verdict under the v2
#      identifier-only grammar BEFORE the summand-lambda post-pass; it is not a v1 verdict (v1 grades live in study_grading_20260923 and the
#      v2 grades in evaluator_records_v2/_runs). `pre_lambda_grammar_is_v2` asserts that the grammar file used came from evaluator_records_v2.
#  (5) Work dirs and the olean cache live under harness/validate_v3_lambda/_runs (nothing under evaluator_records* is written).
# Everything else (harness_pass rule, output fields, exit codes: 0 PASS, 1 FAIL, 2 no verdict) is the v1 text.
set -uo pipefail
TRACK=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
OUT=$TRACK/harness/validate_v3_lambda
EVAL2=$TRACK/evaluator_records_v2
V1=$TRACK/evaluator_records
HARNESS=$TRACK/harness
export DISABLE_AUTOUPDATER=1
REC=$1; SUB=$(readlink -f "$2"); OUTJ=${3:-}
SELF=$(readlink -f "${BASH_SOURCE[0]}")
CHECKER_VERSION=v3-lambda-20260924
CK_SHA=$(sha256sum "$SELF" | cut -d' ' -f1)
V1CK_SHA=$(sha256sum "$V1/check_record.sh" | cut -d' ' -f1)
V2CK_SHA=$(sha256sum "$EVAL2/check_record_v2.sh" | cut -d' ' -f1)
V3VAL_SHA=$(sha256sum "$OUT/validate_v3_lambda.py" | cut -d' ' -f1)
VAL_SHA=$(sha256sum "$HARNESS/validate.py" | cut -d' ' -f1)
RC_SHA=$(sha256sum "$HARNESS/repair_common.py" | cut -d' ' -f1)
EV2_SHA=$(sha256sum "$EVAL2/$REC/evaluator.json" | cut -d' ' -f1)
EV1_SHA=$(sha256sum "$V1/$REC/evaluator.json" | cut -d' ' -f1)
mkdir -p "$OUT/_runs/validate_cache"
WS=$(mktemp -d "$OUT/_runs/vw_${REC}_XXXXXX")
python3 "$OUT/validate_v3_lambda.py" --record "$REC" --submission "$SUB" --out "$WS/verdict.json" --workspace "$WS/ws" --cache-dir "$OUT/_runs/validate_cache" \
    --evaluator-dir "$HARNESS/evaluator/$REC" --hole-grammar "$EVAL2/$REC/evaluator.json" > "$WS/summary.txt" 2> "$WS/stderr.txt"
python3 - "$WS/verdict.json" "$EVAL2/$REC/evaluator.json" "$REC" "$SUB" "$WS/stderr.txt" "$CHECKER_VERSION" "$SELF" "$CK_SHA" "$V1/check_record.sh" "$V1CK_SHA" \
    "$EVAL2/check_record_v2.sh" "$V2CK_SHA" "$OUT/validate_v3_lambda.py" "$V3VAL_SHA" "$HARNESS/validate.py" "$VAL_SHA" "$HARNESS/repair_common.py" "$RC_SHA" \
    "$EV2_SHA" "$V1/$REC/evaluator.json" "$EV1_SHA" <<'PY'
import json, re, sys, os
(vpath, epath, rec, sub, err, ckver, ckpath, cksha, v1ckpath, v1cksha, v2ckpath, v2cksha, v3valpath, v3valsha, valpath, valsha, rcpath, rcsha,
 ev2sha, ev1path, ev1sha) = sys.argv[1:]
ev = json.load(open(epath))
stamp = {"checker_version": ckver, "validator_version_expected": "v3-lambda-E10-20260924",
         "checker_v3": {"path": ckpath, "sha256": cksha}, "checker_v2": {"path": v2ckpath, "sha256": v2cksha}, "checker_v1": {"path": v1ckpath, "sha256": v1cksha},
         "validate_v3_lambda_py": {"path": v3valpath, "sha256": v3valsha}, "validate_py": {"path": valpath, "sha256": valsha},
         "repair_common_py": {"path": rcpath, "sha256": rcsha},
         "evaluator_json_v2": {"path": epath, "sha256": ev2sha}, "evaluator_json_v1": {"path": ev1path, "sha256": ev1sha},
         "v2_allowed_identifiers": (ev.get("hole_syntax") or {}).get("allowed_identifiers")}
if not os.path.exists(vpath):
    print(json.dumps({"record_id": rec, "submission": sub, "verdict": "ERROR", "reason": "validator produced no verdict", "stderr": open(err).read()[-3000:], **stamp}, indent=1)); sys.exit(2)
v = json.load(open(vpath))
pin_ok = ((v.get("pinned") or {}).get("evaluator.json") or {}).get("sha256") == ev2sha
ident = ((v.get("checks") or {}).get("hole_syntax") or {}).get("identifiers") or {}
reached = ident.get("allowed_identifiers") == sorted((ev.get("hole_syntax") or {}).get("allowed_identifiers") or []) if ident else None
e10 = ((v.get("checks") or {}).get("hole_syntax") or {}).get("e10_summand_lambda") or {}
lifted = e10.get("fun_ban_lifted") is True
stamp.update({"grammar_pin_matches_v2": pin_ok, "v2_allowlist_reached_identifier_check": reached,
              "validator_version": v.get("validator_version"), "validator_version_matches": v.get("validator_version") == stamp["validator_version_expected"],
              "derived_from_validate_py_sha256": (v.get("derived_from") or {}).get("sha256")})
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
# v3: the `fun` ban is lifted here exactly when the validator's E10 rule lifted it; the rule's own problems are carried over
validator_problems = (v["checks"].get("hole_syntax") or {}).get("problems") or []
if lifted:
    problems = [p for p in problems if p != "hole_forbidden_token:fun"]
problems += [p for p in validator_problems if p.startswith("e10_summand_lambda:") and p not in problems]
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
       "validator_hole_syntax_problems": validator_problems,
       "e10_summand_lambda": {"applied": e10.get("applied"), "fun_ban_lifted": lifted, "sites": e10.get("sites")},
       "pre_lambda_v2_grammar_verdict": v.get("pre_lambda_verdict"),
       "pre_lambda_grammar_is_v2": str(((v.get("pre_lambda_verdict") or {}).get("grammar_version_hint") or "")).startswith("v2-identifiers"),
       "endpoint_final_not_applicable": (not has_final),
       "harness_verdict_file": vpath, **stamp}
print(json.dumps(out, indent=1, ensure_ascii=False))
sys.exit(0 if allp else 1)
PY
RC=$?
[ -n "$OUTJ" ] && cp "$WS/verdict.json" "$OUTJ" 2>/dev/null
rm -rf "$WS/ws"
exit $RC
