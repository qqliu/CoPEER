"""Shared, deterministic pieces of the CCL v2 harness: prompt construction, answer parsing, item loading, run order."""
import hashlib, json, os, re
from pathlib import Path
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(EXP, "..", "..", "..", ".."))
ITEMS_RELATIVE_PATH = "gold_v3_work/items_v3.candidate.json"
ITEMS = os.path.join(EXP, ITEMS_RELATIVE_PATH)
ORDER_SALT = "copeer-ccl-v2-run-order"
MAX_OUTPUT = 16000   # v3 addendum (2026-09-21): raised from 8000 for EVERY lane after the Haiku pilot failed its output-cap gate
FROZEN_FILES = ("PROTOCOL.md", "V4_SPEC.md", "build_items.py", "build_gold_check.py", "finalize_gold.py", "import_gold_check.py", "test_gold_check_import.py", "common.py", "prompt_system.txt", "prompt_user_template.txt",
                "run_critic.py", "run_local.py", "run_local.sbatch", "lane_accounting.py", "score.py", "test_scoring_contract.py", "test_cli_contract.py", "test_local_contract.py", "test_gold_finalization.py",
                # v4 candidate: bind the carryover, one-epoch policy implementation and all contract suites
                "build_carryover.py", "pilot_epoch.py", "test_pilot_epoch_helpers.py", "test_epoch_integration.py", "test_lane_accounting_contract.py", "test_archived_attempt_guard.py", "test_tokenizer_contract.py", "test_parser_array_only_contract.py",
                "build_miss_audit.py", "miss_audit_source_v2.py", "test_miss_audit_contract.py",
                # v4 adapters: the Codex CLI lane runner (gpt-5.6-luna) and its contract suite
                "run_codex.py", "test_codex_contract.py", "run_agy.py", "test_agy_contract.py",
                # campaign integration (2026-09-22): the large-memory sbatch envelope of GLM-4.7-Flash and Kimi-Linear
                "run_local_large.sbatch",
                # epoch 2 (2026-09-22): the two-GPU tensor-parallel sbatch envelope of the parallel sibling root
                "run_local_tp2.sbatch")
ORIGINAL_LOCAL_FAMILY_KEYS = ("deepseek_r1_qwen_32b", "phi4", "glm47_flash", "kimi_linear_48b_a3b_instruct")
EXPANSION_A_KEYS = ('gpt_oss_120b', 'gpt_oss_20b', 'qwen3_8_27b', 'qwen3_6_35b_a3b', 'qwen3_5_122b_a10b', 'phi4_reasoning_plus')
EXPANSION_B_KEYS = ('gemma4_31b', 'gemma4_26b_a4b', 'glm45_air_fp8', 'nemotron3_super_120b_a12b_fp8', 'nemotron35_lightning_30b_a3b', 'deepseek_v4_flash_dspark')
EXPANSION_C_KEYS = ('magistral_small_2509', 'seed_oss_36b', 'olmo3_32b_think', 'skywork_or1_32b', 'openmath_nemotron_32b')
LOCAL_EXPANSION_KEYS = EXPANSION_A_KEYS + EXPANSION_B_KEYS + EXPANSION_C_KEYS
LOCAL_FAMILY_KEYS = ORIGINAL_LOCAL_FAMILY_KEYS + LOCAL_EXPANSION_KEYS
LOCAL_FAMILY_MANIFESTS = tuple("weights_manifest_" + key + ".json" for key in LOCAL_FAMILY_KEYS)   # beside the experiment, like the qwen/gemma manifests
EXPERIMENT_FROZEN_FILES = ("items_v2.json", "gold_overrides.json", "gold_finalization_manifest.json", "gold_check_manifest_not_for_reviewers.json",
                           "copeer_gold_span_check_20260921.zip", "weights_manifest_qwen3_32b.json", "weights_manifest_gemma3_27b.json", *LOCAL_FAMILY_MANIFESTS,
                           "CARRYOVER.json", "ATTEMPT_EPOCH_POLICY.json", ITEMS_RELATIVE_PATH,
                           "gold_v3_work/GOLD_V3_FREEZE_RECEIPT.json", "gold_v3_work/FRESH40_SAMPLING_PLAN.json",
                           "gold_v3_work/GOLD_V3_CANDIDATE.json", "gold_v3_work/EXCLUDED_ORIGINAL_40.json",
                           "gold_v3_work/EXCLUDED_ORIGINAL_40.csv")   # v4: retain historical pins and bind the approved v3 gold separately
REPO_FROZEN_FILES = ("analysis/rating_goal_20260921/CCL_METADATA_JOIN.csv", "analysis/rating_goal_20260921/CCL_METADATA_AUDIT.json",
                     "analysis/rating_goal_20260921/build_ccl_metadata.py",
                     "analysis/human_returns_followup_20260921/newest_returns_20260922/FRESH40_SET2_RECEIPT_AUDIT.json",
                     "analysis/human_returns_followup_20260921/newest_returns_20260922/gold_check_set2.csv")

# Epoch-2 registration (2026-09-22): the lock-fix contention test, the accounting replay tests, the parallel launcher and its
# contract test are frozen bytes; the decision, review and handoff receipts and the launch wrappers are frozen experiment inputs.
FROZEN_FILES = FROZEN_FILES + ("test_epoch_lock_contention.py", "test_epoch2_replay.py", "launch_parallel.py", "test_parallel_launch_contract.py")
FROZEN_FILES = FROZEN_FILES + ("test_restore_race_regression.py",)   # epoch 4: the lane-start race is closed and regression-tested
FROZEN_FILES = FROZEN_FILES + ("test_epoch5_outage_resume.py",)   # epoch 5: outage exemptions, the carried pilot gate and the resume scope are regression-tested
FROZEN_FILES = FROZEN_FILES + ("test_epoch5_continuation_scoring.py",)   # epoch 5: the disclosed scorer amendment (continuation join) is regression-tested
# Epoch 5 (Haiku continuation root): this root's own decision and receipts replace the epoch-4 ones; the epoch-4 launch wrappers stay as
# inert byte copies (no local or Gemini lane is registered here; the policy refuses every unregistered lane).
EXPERIMENT_FROZEN_FILES = EXPERIMENT_FROZEN_FILES + ("EPOCH5_DECISION.md", "EPOCH5_ARCHIVE_COPY_RECEIPT.json", "EPOCH5_CANARY_ELIGIBILITY_RECEIPT.json", "launch_all_local.sh", "launch_gemini.sh")

PARSER_VERSION = "original-first-three-v3-string-aware-leading-zero-labels"   # strict decoding and the intermediate (leading-zero) fallback
ARRAY_ONLY_PARSER_VERSION = "original-first-three-v4-array-only-fallback"     # stamped ONLY on audits the array-only stage produced
NORMALISATIONS = ("leading_zero_labels_in_candidates_array", "array_only_candidates_extraction",
                  "array_only_candidates_extraction_with_leading_zero_labels")
# v3 addendum: critics copy the text's four-digit labels ("candidates": [0029]); JSON forbids leading zeros, so strict decoding fails.
# Only when strict decoding finds no candidates list, bare numerals with leading zeros INSIDE a "candidates" array are rewritten
# without them (0029 -> 29) and decoding is tried again. Nothing else in the answer is touched; the use of this fallback is recorded.
def normalise_leading_zero_labels(answer, spans=None):
    """Rewrite only unsigned integer tokens directly inside candidates arrays.

    Respect strings/escapes and balanced containers. Quoted values, nested
    invalid slots, signs, decimals, exponents and malformed separators retain
    their exact text; the existing JSON decoder still decides validity.

    v4: a caller may pass a list as `spans`; every "candidates" array this
    scanner meets is then also reported as (start, end, edits). The rewrite
    and the returned text are the same with or without it.
    """
    text = answer or ""
    edits = []
    whitespace = " \t\r\n"

    def string_end(start):
        pos = start + 1
        while pos < len(text):
            if text[pos] == "\\":
                pos += 2
            elif text[pos] == '"':
                return pos + 1
            else:
                pos += 1
        return len(text)

    def array_edits(start):
        stack, found = ["["], []
        segment, pos = start + 1, start + 1
        while pos < len(text):
            char = text[pos]
            if char == '"':
                pos = string_end(pos)
                continue
            if len(stack) == 1 and char in ",]":
                match = re.fullmatch(r"([ \t\r\n]*)(0[0-9]+)([ \t\r\n]*)", text[segment:pos])
                if match:
                    lo = segment + len(match.group(1))
                    digits = match.group(2)
                    found.append((lo, lo + len(digits), digits.lstrip("0") or "0"))
                segment = pos + 1
            if char in "[{":
                stack.append(char)
            elif char in "]}":
                if not stack or stack[-1] != ("[" if char == "]" else "{"):
                    return pos + 1, []
                stack.pop()
                if not stack:
                    return pos + 1, found
            pos += 1
        return len(text), []

    pos = 0
    while pos < len(text):
        if text[pos] != '"':
            pos += 1
            continue
        end = string_end(pos)
        try:
            key = json.loads(text[pos:end])
        except ValueError:
            pos = end
            continue
        next_pos = end
        while next_pos < len(text) and text[next_pos] in whitespace:
            next_pos += 1
        if key == "candidates" and next_pos < len(text) and text[next_pos] == ":":
            next_pos += 1
            while next_pos < len(text) and text[next_pos] in whitespace:
                next_pos += 1
            if next_pos < len(text) and text[next_pos] == "[":
                pos, found = array_edits(next_pos)
                edits.extend(found)
                if spans is not None: spans.append((next_pos, pos, found))
                continue
        pos = end
    chunks, previous = [], 0
    for lo, hi, replacement in edits:
        chunks.extend((text[previous:lo], replacement))
        previous = hi
    chunks.append(text[previous:])
    return "".join(chunks)

def _last_candidates_object(text):
    found = None
    for m in re.finditer(r"\{", text or ""):
        try: obj, _ = json.JSONDecoder().raw_decode(text[m.start():])
        except (ValueError, RecursionError): continue   # absurdly deep nesting is undecodable, not a crash
        if isinstance(obj, dict) and isinstance(obj.get("candidates"), list): found = obj
    return found

# v4 candidate: critics put unescaped LaTeX ($P_\RR$, 2 \cdot 2) in the UNSCORED free-text fields; the whole object is then invalid
# JSON although its candidates array is well formed. Only when strict decoding AND the leading-zero fallback find no candidates list,
# the LAST "candidates" array located by the scanner above is decoded ALONE, after the same leading-zero rewrite confined to that
# array. The answer is never edited, the raw array text is kept, and a garbled array or one holding a nested container fails closed.
def _last_candidates_array(answer):
    text = answer or ""; spans = []
    normalise_leading_zero_labels(text, spans)
    if not spans: return None
    lo, hi, edits = spans[-1]; chunks, previous = [], lo
    for edit_lo, edit_hi, replacement in edits:
        chunks.extend((text[previous:edit_lo], replacement)); previous = edit_hi
    chunks.append(text[previous:hi])
    found = {"raw_text": text[lo:hi], "arrays_located": len(spans), "leading_zero_labels": bool(edits), "candidates": None}
    def invalid_constant(token):
        raise ValueError("non-JSON numeric constant: " + token)
    try: value = json.loads("".join(chunks), parse_constant=invalid_constant)
    except (ValueError, RecursionError): found["reason"] = "candidates_array_not_json"; return found
    if not isinstance(value, list) or any(isinstance(slot, (list, dict)) for slot in value):
        found["reason"] = "candidates_array_nested_container"; return found
    found["candidates"] = value
    return found

def sha(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()
def read(name): return (Path(HERE) / name).read_text(encoding="utf-8")
def safe(rid): return re.sub(r"[^A-Za-z0-9._-]", "_", rid)

def freeze_hash():
    parts = {f: sha((Path(HERE) / f).read_bytes()) for f in FROZEN_FILES}
    for name in EXPERIMENT_FROZEN_FILES:
        parts[name] = sha((Path(EXP) / name).read_bytes())
    for name in REPO_FROZEN_FILES:
        parts[name] = sha((Path(ROOT) / name).read_bytes())
    return sha(json.dumps(parts, sort_keys=True)), parts

def load_items(split):
    items = [it for it in json.loads(Path(ITEMS).read_text(encoding="utf-8"))["items"] if it["split"] == split]
    items.sort(key=lambda it: sha(ORDER_SALT + "|" + it["record_id"]))     # a stopped lane leaves a random subsample
    return items

def line_id(i): return i if isinstance(i, str) else "%04d" % i

def build_prompt(item):
    prob = "\n".join("%s | %s" % (i, t) for i, t in item["lines"] if isinstance(i, str)) or "(none)"
    text = "\n".join("%04d | %s" % (i, t) for i, t in item["lines"] if not isinstance(i, str))
    return read("prompt_user_template.txt").replace("{problem}", prob).replace("{text}", text)

def parse_candidates_audit(answer, item):
    """Normalize the original first three slots without promoting later entries.

    Invalid and duplicate slots are represented by None and score as misses.
    Every raw slot, including ignored ranks after three, remains auditable.
    The last decoded JSON object containing a candidates list is authoritative.
    Stages, each used only when the previous one finds no candidates list: strict
    decoding, leading-zero rewrite, array-only extraction. An audit the third
    stage did not touch is identical to the one the v3 parser produced.
    """
    valid = {i for i, t in item["lines"] if str(t).strip()}
    found = _last_candidates_object(answer); fallback = False
    if found is None:
        found = _last_candidates_object(normalise_leading_zero_labels(answer)); fallback = found is not None
    audit = {"parser_version": PARSER_VERSION, "raw_candidates": None, "candidates": None, "slot_audit": []}
    array_only = _last_candidates_array(answer) if found is None else None
    if array_only is not None:
        audit.update(parser_version=ARRAY_ONLY_PARSER_VERSION, raw_candidates_text=array_only["raw_text"],
                     candidates_arrays_located=array_only["arrays_located"])
        if array_only["candidates"] is None:
            audit["parse_reason"] = array_only["reason"]
            return audit
        found = {"candidates": array_only["candidates"]}
    if found is None:
        audit["parse_reason"] = "no_json_candidates_list"
        return audit
    audit["raw_candidates"] = found["candidates"]
    if fallback: audit["normalisation"] = "leading_zero_labels_in_candidates_array"
    if array_only is not None:
        audit["normalisation"] = ("array_only_candidates_extraction_with_leading_zero_labels" if array_only["leading_zero_labels"]
                                  else "array_only_candidates_extraction")
    out, seen = [], set()
    for rank, raw in enumerate(found["candidates"], 1):
        c, reason = raw, None
        if isinstance(c, bool): reason = "boolean_not_line_label"
        if isinstance(c, str):
            s = c.strip()
            try:
                if re.fullmatch(r"[Pp]\d+", s): c = "P%d" % int(s[1:])
                elif re.fullmatch(r"\d+", s): c = int(s)
                else: reason = "invalid_line_label"
            except ValueError: reason = "invalid_line_label"   # oversized quoted numerals must not abort the lane
        if isinstance(c, float) and c.is_integer(): c = int(c)
        if reason is None:
            if not isinstance(c, (int, str)): reason = "invalid_line_label_type"
            elif c not in valid: reason = "unknown_or_blank_line"
            elif c in seen: reason = "duplicate_line_label"
        if reason is None: seen.add(c)
        normalized = c if reason is None else None
        audit["slot_audit"].append({"rank": rank, "raw": raw, "normalized": normalized,
                                   "reason": reason or "valid", "scored": rank <= 3,
                                   "exclusion_reason": "beyond_first_three" if rank > 3 else None})
        if rank <= 3: out.append(normalized)
    audit["candidates"] = out
    audit["parse_reason"] = "parsed" if out else "empty_candidate_list"
    return audit

def parse_candidates(answer, item):
    """Compatible list-or-None wrapper; None slots preserve invalid ranks."""
    return parse_candidates_audit(answer, item)["candidates"]

def _token_count(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None

def usage_summary(record, unknown_usage_charge=40000):
    """Account for all attempts without interpreting missing native usage as zero.

    Attempt receipts take precedence over any record-level final-attempt total.
    A legacy/local record without an attempts list is one recorded attempt.
    Conservative budget charges are reported separately from measured tokens.
    """
    if _token_count(unknown_usage_charge) is None:
        raise ValueError("unknown usage charge must be a nonnegative integer")
    preflight_zero = (record is not None and record.get("attempts") == []
                      and record.get("usage_origin") == "preflight_no_inference"
                      and record.get("usage_known") is True
                      and _token_count(record.get("total_attributable_tokens")) == 0)
    if record is None:
        attempts = []
    elif isinstance(record.get("attempts"), list):
        attempts = record["attempts"]
        if not attempts and not preflight_zero: attempts = [{**record, "usage_known": False}]
    else:
        attempts = [record]
    known = lower = unknown = charge = 0
    for attempt in attempts:
        usage = attempt.get("usage") if isinstance(attempt.get("usage"), dict) else attempt
        total = _token_count(usage.get("total_attributable_tokens"))
        if attempt.get("usage_known") is True and total is not None:
            known += total; lower += total; charge += total
        else:
            unknown += 1
            observed = _token_count(usage.get("observed_lower_bound"))
            if observed is None: observed = _token_count(attempt.get("observed_usage_lower_bound"))
            observed = observed if observed is not None else 0
            lower += observed
            override = _token_count(attempt.get("budget_charge_tokens")) or 0
            charge += max(unknown_usage_charge, observed, override)
    usage_known = (bool(attempts) and unknown == 0) or preflight_zero
    return {"usage_known": usage_known, "total_attributable_tokens": known if usage_known else None,
            "known_attributable_tokens": known, "observed_usage_lower_bound": lower,
            "unknown_usage_attempts": unknown, "attempts_count": len(attempts), "budget_charge_tokens": charge}
