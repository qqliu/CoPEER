#!/usr/bin/env python3
"""CCL v2 deterministic scorer. No model calls. Usage: python3 -B score.py [--split evaluation]

Primary population: items with at least 10 non-blank text lines that adjudication did not exclude. All items are reported as secondary.
Intention to treat: a missing record, a protocol-invalid call or an unparseable answer is a miss; a per-protocol column is printed beside it.
Intervals: percentile bootstrap, 10,000 resamples of (near-duplicate-merged) problem clusters WITHIN source group; seed derived per quantity.
v4 candidate (reporting only; hit metrics, populations, bootstrap, baselines and V/S/D/H are unchanged): every miss is named by one cause
(budget_exhausted, contract_violation, transport_failure, setup_failure, unparseable, empty_candidate_list, invalid_candidate_slots);
cost = active lane + pinned carryover of archived attempts, four components never merged; parser fallbacks are counted per lane.
"""
import argparse, collections, csv, glob, hashlib, json, math, os, random, re, statistics, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EXP, ITEMS, MAX_OUTPUT, NORMALISATIONS, ROOT, freeze_hash, safe, usage_summary  # noqa: E402
from lane_accounting import load_carryover as validate_carryover  # noqa: E402

RESAMPLES = 10000; MIN_LINES = 10; PRIMARY_CRITIC = "claude-sonnet-5"; LADDER = ("claude-opus-5", "claude-haiku-4-5-20251001")
REFUTATION_ROLES = ("intermediate_step", "target_statement", "unclear")
# Shared v4 attempt classes (V4_SPEC.md) -> the cause a miss is reported under. Only VALID_ANSWER reaches the candidate rules.
ATTEMPT_CLASS_CAUSE = {"VALID_ANSWER": None, "BUDGET_EXHAUSTED": "budget_exhausted", "CONTRACT_VIOLATION": "contract_violation",
                       "TRANSPORT_FAILURE": "transport_failure", "SETUP_FAILURE": "setup_failure"}
# A record written without attempt_class is classified from the stop evidence it does carry.
STOP_REASON_CLASS = {"output_budget_exhausted": "BUDGET_EXHAUSTED", "output_token_cap": "BUDGET_EXHAUSTED", "contract_violation": "CONTRACT_VIOLATION",
                     "setup_failure": "SETUP_FAILURE", "prompt_exceeds_context_with_output_cap": "SETUP_FAILURE",
                     "call_token_cap_prevents_attempt": "SETUP_FAILURE"}
CARRYOVER_FIELDS = ("measured_tokens", "unknown_attempts", "observed_lower_bound_tokens", "charged_tokens")
BUDGET_EVIDENCE_SOURCES = ("inferred_client_limit_exhaustion", "native_max_tokens", "native_local_length", "live_output_estimate",
                           "native_output_tokens_over_budget", "unknown")   # campaign integration 2026-09-22: the Codex CLI lane's source
LABEL_VALIDITY_AUDIT = "astra/human_returns_followup_20260921/newest_returns_20260922/FRESH40_SET2_RECEIPT_AUDIT.json"
LABEL_VALIDITY_AUDIT_SHA256 = "b93ec598781dc168cbca67658936e58c8ec5ff8ea8c8db97392dc1f3404e6190"
CORRECTED_ITEMS_SHA256 = "ea1430b3f202b8b863ae5491fc9c8c122bf7316515af336e8bf9a1e0df31b044"
SYMBOLS = re.compile(r"[=<>≤≥≠+\-*/^_\\$∈∉⊆⊂∀∃∑∏√|]")
def seed_for(*parts): return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:12], 16)
def toks(s): return re.findall(r"\w+", s.lower())

def baselines(item):
    nb = [(i, t) for i, t in item["lines"] if str(t).strip()]; ids = [i for i, _ in nb]; gs = set(item["gold"]); n = len(ids); k = len(gs & set(ids))
    def top(score):  # highest score, earliest line on ties
        best = max(range(n), key=lambda j: (score(nb[j][1]), -j)); return float(ids[best] in gs)
    df = collections.Counter(w for _, t in nb for w in set(toks(t)))
    vecs = []
    for _, t in nb:
        tf = collections.Counter(toks(t)); vecs.append({w: c * math.log(1 + n / df[w]) for w, c in tf.items()})
    cen = collections.Counter()
    for v in vecs:
        for w, x in v.items(): cen[w] += x / n
    cn = math.sqrt(sum(x * x for x in cen.values())) or 1.0
    def cos(j):
        v = vecs[j]; vn = math.sqrt(sum(x * x for x in v.values()))
        return sum(x * cen[w] for w, x in v.items()) / (vn * cn) if vn else -1.0
    best_c = max(range(n), key=lambda j: (cos(j), -j))
    return {"random_line": k / n, "longest_line_chars": top(len), "most_word_tokens": top(lambda t: len(toks(t))),
            "most_math_symbols": top(lambda t: len(SYMBOLS.findall(t))), "tfidf_centroid_line": float(ids[best_c] in gs)}

def attempt_class_of(rec):
    """Class of the final attempt; explicit failure evidence cannot be overridden by a VALID_ANSWER label."""
    attempts = rec.get("attempts") if isinstance(rec.get("attempts"), list) else []
    final = attempts[-1] if attempts and isinstance(attempts[-1], dict) else {}
    classes = []
    for row in (rec, final):
        stated = row.get("attempt_class")
        if stated is None: continue
        if not isinstance(stated, str) or stated not in ATTEMPT_CLASS_CAUSE:
            raise ValueError("unknown attempt_class %r: %s" % (stated, rec.get("record_id")))
        classes.append(stated)
    for row in (rec, final):
        reason = (row.get("hard_stop") or {}).get("reason")
        if reason in STOP_REASON_CLASS: classes.append(STOP_REASON_CLASS[reason])
        usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
        if row.get("stop_reason") == "max_tokens" or usage.get("stop_reason") == "max_tokens" or row.get("finish_reason") == "length":
            classes.append("BUDGET_EXHAUSTED")
        if row.get("transport_failure") is True: classes.append("TRANSPORT_FAILURE")
    for failure in ("CONTRACT_VIOLATION", "BUDGET_EXHAUSTED", "SETUP_FAILURE", "TRANSPORT_FAILURE"):
        if failure in classes: return failure
    if classes: return classes[0]
    return "VALID_ANSWER" if rec.get("valid_protocol") else None

def budget_evidence_source(rec, contradictory=False):
    """Describe the final exhausted attempt without promoting missing or conflicting evidence to native verification."""
    if contradictory: return "unknown"
    attempts = rec.get("attempts")
    final = attempts[-1] if isinstance(attempts, list) and attempts and isinstance(attempts[-1], dict) else rec
    rows = (rec, final)
    stops = [row.get("hard_stop") if isinstance(row.get("hard_stop"), dict) else {} for row in rows]
    stated = [row["exhaustion_evidence_source"] for row in (*rows, *stops) if row.get("exhaustion_evidence_source") is not None]
    if any(not isinstance(source, str) or source not in BUDGET_EVIDENCE_SOURCES for source in stated): return "unknown"
    if len(set(stated)) > 1: return "unknown"
    if any(row.get("stream_reader_error") or row.get("drain_deadline_expired")
           or row.get("controlled_drain_complete") is False for row in rows): return "unknown"
    source = stated[0] if stated else None
    if source in ("inferred_client_limit_exhaustion", "live_output_estimate"):
        return "unknown" if any(row.get("native_stop_verified") is True for row in rows) else source
    usage = final.get("usage") if isinstance(final.get("usage"), dict) else {}
    if source == "native_output_tokens_over_budget":
        # Codex CLI lane (run_codex.py): no provider-side cap exists and the model was never stopped; the native turn.completed
        # output count itself, above the allowance, is the evidence. A CLI-internal second request is not excluded by that count.
        output = usage.get("output_tokens")
        return source if (final.get("usage_known") is True and not any(row.get("native_stop_verified") is True for row in rows)
                          and isinstance(output, int) and not isinstance(output, bool) and output > MAX_OUTPUT) else "unknown"
    if final.get("usage_known") is not True or any(row.get("second_request_not_excluded") is True for row in rows): return "unknown"
    if source == "native_max_tokens":
        verified = final.get("native_stop_verified") is True and not any(row.get("native_stop_verified") is False for row in rows)
        reasons = [row.get("stop_reason") for row in (*rows, *stops)] + [usage.get("stop_reason")]
        return source if verified and "max_tokens" in reasons and all(reason in (None, "max_tokens") for reason in reasons) else "unknown"
    if source in (None, "native_local_length") and final.get("finish_reason") == "length":
        output = usage.get("output_tokens")
        native_denied = any(row.get("native_stop_verified") is False for row in rows)
        return "native_local_length" if not native_denied and isinstance(output, int) and not isinstance(output, bool) and output >= 0 else "unknown"
    return "unknown"   # legacy budget labels or unrecognized attribution never imply a verified native stop


def outcome(item, rec):
    gs = set(item["gold"]); c = (rec or {}).get("candidates"); cls = attempt_class_of(rec) if rec is not None else None
    attempts = (rec or {}).get("attempts")
    final = attempts[-1] if isinstance(attempts, list) and attempts and isinstance(attempts[-1], dict) else {}
    contradictory = cls is not None and any(
        (row.get("attempt_class") is not None and row["attempt_class"] != cls)
        or ("valid_protocol" in row and bool(row["valid_protocol"]) != (cls == "VALID_ANSWER"))
        or (cls == "VALID_ANSWER" and bool(row.get("hard_stop")))
        for row in (rec or {}, final))
    if rec is None: cause = "no_record"
    elif cls != "VALID_ANSWER": cause = ATTEMPT_CLASS_CAUSE[cls] if cls else "protocol_invalid"   # every non-answer class is an ITT miss, whatever was parsed
    elif not rec.get("valid_protocol") or contradictory: cause = "protocol_invalid"                 # contradictory evidence fails closed
    elif c is None: cause = "unparseable"
    elif len(c) == 0: cause = "empty_candidate_list"
    elif all(x is None for x in c[:3]): cause = "invalid_candidate_slots"
    else: cause = None
    audit = {"attempt_class": cls, "contradictory_record": contradictory,
             "exhaustion_evidence_source": budget_evidence_source(rec, contradictory) if cause == "budget_exhausted" else None}
    if cause: return {"hit1": 0.0, "hit3": 0.0, "valid": False, "cause": cause, **audit}
    return {"hit1": float(c[0] in gs), "hit3": float(any(x in gs for x in c[:3])), "valid": True, "cause": None, **audit}

def aggregate_usage(records):
    """Totals are known only when every requested record and attempt is known."""
    summaries = [usage_summary(r) for r in records if r is not None]
    missing = sum(r is None for r in records)
    complete = missing == 0 and all(s["usage_known"] for s in summaries)
    known = sum(s["known_attributable_tokens"] for s in summaries)
    return {"records_present": len(summaries), "records_missing": missing, "usage_known": complete,
            "total_attributable_tokens": known if complete else None, "known_attributable_tokens": known,
            "observed_usage_lower_bound": sum(s["observed_usage_lower_bound"] for s in summaries),
            "unknown_usage_attempts": sum(s["unknown_usage_attempts"] for s in summaries),
            "attempts_count": sum(s["attempts_count"] for s in summaries),
            "budget_charge_tokens": sum(s["budget_charge_tokens"] for s in summaries)}

def aggregate_output_usage(records):
    """All-attempt native output counts; missing counts are not measured zeros.

    CLI per-model final usage and local worker output counts are alternative
    representations, never additive. Unknown attempts contribute only native
    counts actually retained, not attributable-token bounds or thinking estimates.
    """
    def count(value):
        return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None
    known = lower = unknown = attempts_count = present = missing = 0
    for record in records:
        if record is None:
            missing += 1
            continue
        present += 1
        if isinstance(record.get("attempts"), list):
            attempts = record["attempts"]
            if not attempts and usage_summary(record)["usage_known"]:
                continue  # Explicit preflight_no_inference: zero physical attempts.
            if not attempts: attempts = [{**record, "usage_known": False}]
        else:
            attempts = [record]
        for attempt in attempts:
            attempts_count += 1
            usage = attempt.get("usage") if isinstance(attempt.get("usage"), dict) else attempt
            models = usage.get("per_model")
            if isinstance(models, dict) and models:
                values = [count(row.get("outputTokens")) if isinstance(row, dict) else None for row in models.values()]
            else:
                values = [count(usage.get("output_tokens"))]
            observed = sum(value for value in values if value is not None)
            lower += observed
            if attempt.get("usage_known") is True and all(value is not None for value in values):
                known += observed
            else:
                unknown += 1
    complete = missing == 0 and unknown == 0
    return {"records_present": present, "records_missing": missing, "output_usage_known": complete,
            "total_output_tokens": known if complete else None, "known_output_tokens": known,
            "observed_output_tokens_lower_bound": lower, "unknown_output_usage_attempts": unknown,
            "attempts_count": attempts_count}

def cost_components(usage):
    """The four carryover components of an aggregate_usage result, under the carryover's names."""
    return {"measured_tokens": usage["known_attributable_tokens"], "unknown_attempts": usage["unknown_usage_attempts"],
            "observed_lower_bound_tokens": usage["observed_usage_lower_bound"], "charged_tokens": usage["budget_charge_tokens"]}

def load_carryover(path):
    """Archived-attempt cost per lane from the pinned CARRYOVER.json, which only build_carryover.py writes.

    A lane row carries the four components directly or under "totals"; when it
    has only per-item rows they are added up. Item rows that do not add up to
    the stated totals are flagged, never silently preferred. A missing or
    malformed file is an error: archived cost is never read as zero.
    """
    raw = Path(path).read_bytes(); data = json.loads(raw.decode("utf-8"))
    lanes = data.get("lanes") if isinstance(data, dict) else None
    if not isinstance(lanes, dict): raise ValueError("CARRYOVER.json has no lanes mapping")
    def components(row, where):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), int) or isinstance(row.get(k), bool) or row[k] < 0 for k in CARRYOVER_FIELDS):
            raise ValueError("CARRYOVER.json needs four nonnegative integer components: " + where)
        return {k: row[k] for k in CARRYOVER_FIELDS}
    out = {}
    for lane, row in lanes.items():
        if not isinstance(row, dict): raise ValueError("CARRYOVER.json lane row is not an object: " + str(lane))
        items = row.get("items"); rows = list(items.values()) if isinstance(items, dict) else items if isinstance(items, list) else None
        item_sum = None if rows is None else {k: sum(components(r, str(lane) + " item")[k] for r in rows) for k in CARRYOVER_FIELDS}
        stated = row["totals"] if isinstance(row.get("totals"), dict) else row
        totals = item_sum if item_sum is not None and not any(k in stated for k in CARRYOVER_FIELDS) else components(stated, str(lane))
        if safe(lane) in out: raise ValueError("duplicate carryover lane: " + str(lane))
        archives = row.get("by_archive") if isinstance(row.get("by_archive"), dict) else {}
        out[safe(lane)] = {**totals, "archived_items": None if rows is None else len(rows), "listed_in_carryover": True,
                           "item_rows_reconcile": None if item_sum is None else item_sum == totals,
                           "by_archive": {name: components(part, str(lane) + " " + str(name)) for name, part in sorted(archives.items())}}
    return {"sha256": hashlib.sha256(raw).hexdigest(), "schema": data.get("schema"), "content_sha256": data.get("content_sha256"), "lanes": out}

def parser_fallback_report(records):
    """Count of each parser path, read from the audit saved with every record; no answer is parsed again."""
    counts = {"records": 0, "strict_json": 0, **{name: 0 for name in NORMALISATIONS}, "no_candidates_list": {}, "no_parse_audit": 0}
    for record in records:
        counts["records"] += 1; audit = record.get("candidate_parse")
        if not isinstance(audit, dict): counts["no_parse_audit"] += 1
        elif audit.get("candidates") is None:
            reason = str(audit.get("parse_reason")); counts["no_candidates_list"][reason] = counts["no_candidates_list"].get(reason, 0) + 1
        else:
            path = audit.get("normalisation") or "strict_json"
            if path != "strict_json" and path not in NORMALISATIONS: raise ValueError("unknown parser normalisation: " + str(path))
            counts[path] += 1
    return counts

def load_role_metadata(roster):
    """Join the pinned census descriptors without importing automatic gold."""
    directory = Path(ROOT) / "astra/rating_goal_20260921"
    raw = (directory / "CCL_METADATA_JOIN.csv").read_bytes()
    audit = json.loads((directory / "CCL_METADATA_AUDIT.json").read_text(encoding="utf-8"))
    if hashlib.sha256(raw).hexdigest() != audit.get("output_csv_sha256"):
        raise ValueError("CCL metadata CSV does not match its audit hash")
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    metadata = {row["record_id"]: row for row in rows}
    ids = [item["record_id"] for item in roster]
    if len(metadata) != len(rows) or len(set(ids)) != len(ids) or set(metadata) != set(ids):
        raise ValueError("CCL metadata requires an exact unique record-ID roster join")
    if audit.get("row_join", {}).get("items") != len(roster):
        raise ValueError("CCL metadata audit roster count mismatch")
    for item in roster:
        rid = item["record_id"]; row = metadata[rid]
        line_hash = hashlib.sha256(json.dumps(item["lines"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        n_text = sum(not isinstance(label, str) and bool(str(text).strip()) for label, text in item["lines"])
        if (row["ccl_lines_sha256"] != line_hash or row["split_auto"] != item["split"]
                or row["ccl_assignment_group"] != item["group"] or row["cluster_problem_sha256"] != item["cluster"]
                or int(row["n_nonblank_text"]) != n_text or item["n_nonblank_text"] != n_text):
            raise ValueError("CCL metadata disagrees with final item identity, lines or assignment: " + rid)
        if row["refutation_role_census"] not in REFUTATION_ROLES:
            raise ValueError("unknown refutation_role_census: " + rid)
    return metadata

def refutation_role_report(items, metadata, records, cost_records):
    """Three descriptive A2 rows on final primary evaluation items; no inference."""
    if any(item["split"] != "evaluation" or item["n_nonblank_text"] < MIN_LINES
           or item.get("exclude_from_primary") or item.get("unscorable") for item in items):
        raise ValueError("refutation-role report requires final primary evaluation items")
    rows = []; score_available = any(item["record_id"] in records for item in items)
    for role in REFUTATION_ROLES:
        subset = [item for item in items if metadata[item["record_id"]]["refutation_role_census"] == role]
        outcomes = [outcome(item, records.get(item["record_id"])) for item in subset]
        chances = []
        for item in subset:
            labels = {label for label, text in item["lines"] if str(text).strip()}
            gold = set(item["gold"])
            if not gold or not gold <= labels:
                raise ValueError("role report requires final scorable gold: " + item["record_id"])
            chances.append(len(gold) / len(labels))
        n = len(subset); present = sum(item["record_id"] in records for item in subset)
        costs = [cost_records.get(item["record_id"]) for item in subset]
        hit = sum(o["hit1"] for o in outcomes) / n if n and score_available else None
        chance = statistics.mean(chances) if n else None
        rows.append({"refutation_role_census": role, "n_items": n,
                     "n_clusters": len({item["cluster_merged"] for item in subset}),
                     "median_nonblank_text_lines": statistics.median(item["n_nonblank_text"] for item in subset) if n else None,
                     "median_final_gold_fraction": statistics.median(chances) if n else None,
                     "itt_hit1": hit, "mean_random_line_hit1": chance,
                     "hit1_minus_chance": hit - chance if hit is not None else None,
                     "score_available": bool(n and score_available),
                     "records_present": present, "records_missing": n - present, "complete": present == n,
                     "status": "no_eligible_items" if not n else "complete" if present == n else "INCOMPLETE",
                     "inference_usage": aggregate_usage(costs), "output_usage": aggregate_output_usage(costs)})
    present = sum(item["record_id"] in records for item in items)
    return {"scope": "Descriptive only: primary critic A2, final primary evaluation population; no subgroup intervals, tests or success criteria.",
            "primary_critic": PRIMARY_CRITIC, "population": "primary_ge10_lines", "split": "evaluation",
            "annotation_scope": "Existing automated census labels; not new human judgments. Administrative assignment groups and bootstrap unchanged.",
            "cluster_count_scope": "Distinct final merged problem clusters within each role; clusters may span roles, so row cluster counts need not add to the overall count.",
            "gold_fraction_denominator": "All nonblank addressable lines, including P-lines; numerator is final verified gold, never CSV automatic gold.",
            "cost_scope": "All retained attempts for these items, including interrupted dispatch receipts; a subset of existing lane costs, not additional cost. Missing native output is unknown; estimates and attributable-token bounds are not output-token measurements.",
            "unknown_usage_is_zero": False, "score_available": score_available,
            "score_availability_note": "No A2 item records in this primary population means unavailable scores, not measured zero; otherwise missing assigned answers are ITT misses.",
            "n_items": len(items), "records_present": present,
            "complete": present == len(items), "status": "no_eligible_items" if not items else "complete" if present == len(items) else "INCOMPLETE",
            "rows": rows}

def check_record_freeze(record, expected, path):
    if record.get("freeze_sha256") != expected:
        raise ValueError("critic record does not match the current approved freeze: " + path)

def orphan_attempt_records(root, expected_freeze=None):
    """Recover cost-only records from dispatches interrupted before record.json.

    Retained attempt receipts supply native costs; an unresolved dispatch is
    an unknown attempt charged at least its reservation. Never fabricate an
    outcome, and never double-count receipts beside a completed record.
    """
    root = Path(root); groups = {}
    for path in sorted(root.glob("**/DISPATCH_*.json")):
        if (path.parent / "record.json").exists(): continue
        dispatch = json.loads(path.read_text(encoding="utf-8"))
        if expected_freeze is not None: check_record_freeze(dispatch, expected_freeze, str(path))
        attempt_path = path.with_name("ATTEMPT_" + path.name[len("DISPATCH_"):])
        if attempt_path.exists():
            saved = json.loads(attempt_path.read_text(encoding="utf-8"))
            if saved.get("dispatch") != dispatch: raise ValueError("attempt/dispatch identity mismatch: " + str(attempt_path))
            attempt = saved["attempt"]
        else:
            reserved = dispatch.get("reservation_tokens")
            if not isinstance(reserved, int) or isinstance(reserved, bool) or reserved < 0:
                raise ValueError("invalid dispatch reservation: " + str(path))
            attempt = {"usage_known": False, "budget_charge_tokens": reserved,
                       "usage": {"total_attributable_tokens": None, "observed_lower_bound": 0}}
        record = groups.setdefault(path.parent, {"record_id": dispatch["record_id"], "split": dispatch["split"],
                                                "freeze_sha256": dispatch.get("freeze_sha256"), "attempts": [], "orphan_dispatch_paths": []})
        if record["record_id"] != dispatch["record_id"] or record["split"] != dispatch["split"]:
            raise ValueError("inconsistent orphan dispatch group: " + str(path.parent))
        record["attempts"].append(attempt); record["orphan_dispatch_paths"].append(str(path))
    for path in root.glob("**/ATTEMPT_*.json"):
        if not (path.parent / "record.json").exists() and not path.with_name("DISPATCH_" + path.name[len("ATTEMPT_"):]).exists():
            raise ValueError("attempt receipt without dispatch: " + str(path))
    return list(groups.values())

def historical_evaluation_sources(exp, expected_freeze, carryover):
    """Load only byte-pinned historical evaluation records; never relabel their freeze.

    Validation uses the same policy, receipt census and activation rules as a
    live reservation. Pilot answers never enter this join. Bare dispatches
    supply costs and provenance only, not fabricated results.
    """
    from pilot_epoch import PilotEpoch, load_policy
    exp = Path(exp)
    policy, _ = load_policy(exp)
    if policy is None:
        return {}
    groups = collections.defaultdict(list)
    for row in policy["historical_dispatches"]:
        if row["split"] == "evaluation":
            if row["exempt_from_epoch_count"]:
                raise ValueError("historical evaluation cannot be exempt")
            groups[(row["lane"], row["record_id"])].append(row)
    result = {}
    for lane in sorted({lane for lane, _ in groups}):
        PilotEpoch(exp, lane, expected_freeze, carryover)  # validates all byte pins, including archived outcomes
        result[lane] = {"records": {}, "cost_records": {}, "provenance": {}}
    for (lane, rid), rows in sorted(groups.items()):
        directories = {str((exp / row["dispatch_path"]).parent.relative_to(exp)) for row in rows}
        costs = []
        for item in carryover.get("lanes", {}).get(lane, {}).get("items", []):
            if item["directory"] not in directories:
                continue
            if item["record_id"] != rid or item["split"] != "evaluation":
                raise ValueError("historical evaluation carryover identity differs: " + rid)
            directory = exp / item["directory"]
            if item["source"] == "record":
                costs.append(json.loads((directory / "record.json").read_text(encoding="utf-8")))
            else:
                costs.extend(orphan_attempt_records(directory, item["freeze_sha256"]))
        if len(costs) != len(directories):
            raise ValueError("historical evaluation cost census differs: " + rid)
        completed_paths = sorted({row["record_path"] for row in rows if row["record_path"]})
        if len(completed_paths) > 1:
            raise ValueError("multiple historical evaluation results need explicit reconciliation: " + rid)
        if completed_paths:
            record = json.loads((exp / completed_paths[0]).read_text(encoding="utf-8"))
            if record.get("record_id") != rid or record.get("requested_model") != lane:
                raise ValueError("historical evaluation outcome identity differs: " + rid)
            result[lane]["records"][rid] = record
        # Keep attempt costs once each even if lifetime transport retries span archives.
        attempts = [attempt for record in costs for attempt in record.get("attempts", [record])]
        result[lane]["cost_records"][rid] = {"record_id": rid, "split": "evaluation", "attempts": attempts}
        retryable = len(rows) < 2
        unresolved = []
        for row in rows:
            if row["attempt_path"] is None:
                unresolved.append(row["ticket_id"])
                retryable = False
                continue
            attempt = json.loads((exp / row["attempt_path"]).read_text(encoding="utf-8"))["attempt"]
            retryable = retryable and (attempt.get("attempt_class") == "TRANSPORT_FAILURE"
                         or ("attempt_class" not in attempt and attempt.get("transport_failure") is True))
            retryable = retryable and not (attempt.get("saw_assistant_message") is True or attempt.get("saw_result_event") is True)
        result[lane]["provenance"][rid] = {
            "source": "historical_evaluation", "record_paths": completed_paths,
            "record_sha256": sorted({row["record_sha256"] for row in rows if row["record_sha256"]}),
            "freeze_sha256": sorted({row["freeze_sha256"] for row in rows}),
            "dispatch_ticket_ids": sorted(row["ticket_id"] for row in rows),
            "unresolved_dispatch_ticket_ids": sorted(unresolved), "retry_eligible_from_history": bool(retryable)}
    return result


def lifetime_evaluation_report(populations, active_records, active_cost_records, history):
    """A separately labelled cross-freeze view; epoch-2 primary metrics stay unchanged."""
    report = {"scope": "Lifetime evaluation across explicitly listed source freezes. Historical answers retain their original freeze; "
                      "they are not epoch-2 results. Missing and unresolved answers remain ITT misses. Pilot answers are excluded. "
                      "Evaluation usage below is descriptive and is already included in active costs plus carryover; never add it again.",
              "lanes": {}}
    for lane, archived in sorted(history.items()):
        records = dict(archived["records"])
        costs = dict(archived["cost_records"])
        provenance = dict(archived["provenance"])
        for rid, record in active_records.get(lane, {}).items():
            if record.get("split") != "evaluation":
                continue
            if rid in provenance and not provenance[rid]["retry_eligible_from_history"]:
                raise ValueError("active evaluation re-ran terminal historical identity: " + rid)
            records[rid] = record
        for rid, record in active_cost_records.get(lane, {}).items():
            if record.get("split") != "evaluation":
                continue
            if rid in provenance and not provenance[rid]["retry_eligible_from_history"]:
                raise ValueError("active dispatch re-ran terminal historical identity: " + rid)
            if rid in costs:
                costs[rid] = {"attempts": costs[rid]["attempts"] + record.get("attempts", [record])}
            else:
                costs[rid] = record
        lane_report = {"historical_records_present": len(archived["records"]),
                       "historical_unresolved_dispatches": sum(len(p["unresolved_dispatch_ticket_ids"]) for p in provenance.values()),
                       "historical_provenance": provenance,
                       "active_evaluation_record_freezes": dict(sorted((rid, record.get("freeze_sha256"))
                           for rid, record in active_records.get(lane, {}).items() if record.get("split") == "evaluation")),
                       "populations": {}}
        for name, items in populations.items():
            recs = [records.get(it["record_id"]) for it in items]
            outs = [outcome(it, rec) for it, rec in zip(items, recs)]
            present = sum(rec is not None for rec in recs)
            metrics = summarise(items, outs, [baselines(it) for it in items], "lifetime" + name + lane) if items else {}
            metrics.update(records_present=present, complete=present == len(items),
                           inference_usage=aggregate_usage([costs.get(it["record_id"]) for it in items]))
            lane_report["populations"][name] = metrics
        report["lanes"][lane] = lane_report
    return report

def conditional_reading(signal, discrimination, headroom):
    if not headroom: return "headroom criterion not established"
    return "ladder" if signal and discrimination else "floor" if not signal else "flat"

def scoring_population(items):
    excluded = []
    for item in items:
        if item.get("unscorable"):
            if item.get("gold") or not item.get("exclude_from_primary"):
                raise ValueError("inconsistent unscorable designation: " + item["record_id"])
            excluded.append(item["record_id"])
        elif not item.get("gold"):
            raise ValueError("empty gold without explicit unscorable designation: " + item["record_id"])
    return [it for it in items if it["record_id"] not in set(excluded)], excluded

def boot(items, values, name):
    rng = random.Random(seed_for(name)); by = collections.defaultdict(lambda: collections.defaultdict(list))
    for it, v in zip(items, values): by[it["group"]][it["cluster_merged"]].append(v)
    groups = {g: [by[g][c] for c in sorted(by[g])] for g in sorted(by)}; stats = []
    for _ in range(RESAMPLES):
        tot = cnt = 0.0
        for cl in groups.values():
            for _k in range(len(cl)):
                vs = cl[rng.randrange(len(cl))]; tot += sum(vs); cnt += len(vs)
        stats.append(tot / cnt)
    stats.sort(); return [round(stats[int(0.025 * RESAMPLES)], 4), round(stats[int(0.975 * RESAMPLES) - 1], 4)]

def boot_minus_best(items, hits, base, name):
    """Critic hit@1 minus the BEST no-model baseline, with the best baseline re-selected inside every bootstrap replicate
    (so choosing the maximum on the evaluation items is not a free look). Point estimate uses the full-sample maximum."""
    names = [b for b in base[0] if b != "random_line"]; rng = random.Random(seed_for(name))
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, it in enumerate(items): by[it["group"]][it["cluster_merged"]].append(k)
    groups = [[by[g][c] for c in sorted(by[g])] for g in sorted(by)]; stats = []
    for _ in range(RESAMPLES):
        idx = []
        for cl in groups:
            for _k in range(len(cl)): idx += cl[rng.randrange(len(cl))]
        n = len(idx); stats.append(sum(hits[k] for k in idx) / n - max(sum(base[k][b] for k in idx) / n for b in names))
    stats.sort(); n = len(items)
    point = sum(hits) / n - max(sum(x[b] for x in base) / n for b in names)
    return {"mean": round(point, 4), "ci95": [round(stats[int(0.025 * RESAMPLES)], 4), round(stats[int(0.975 * RESAMPLES) - 1], 4)]}

def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 3), round((c + h) / d, 3)]

def summarise(items, outs, base, tag):
    n = len(items); res = {"n_items": n, "n_clusters": len({it["cluster_merged"] for it in items})}
    for m in ("hit1", "hit3"):
        v = [o[m] for o in outs]; res[m] = {"mean": round(sum(v) / n, 4), "ci95": boot(items, v, tag + m)}
    valid = [o for o in outs if o["valid"]]
    res["per_protocol_hit1"] = {"n_valid": len(valid), "mean": round(sum(o["hit1"] for o in valid) / len(valid), 4) if valid else None}
    res["rule_misses_by_cause"] = dict(collections.Counter(o["cause"] for o in outs if o["cause"]))
    exhausted = res["rule_misses_by_cause"].get("budget_exhausted", 0)   # reported, never part of the technical-integrity gate
    res["budget_exhausted"] = {"n": exhausted, "rate": round(exhausted / n, 4)}
    source_counts = collections.Counter(o.get("exhaustion_evidence_source") or "unknown" for o in outs if o["cause"] == "budget_exhausted")
    res["budget_exhaustion_by_evidence_source"] = {source: source_counts[source] for source in BUDGET_EVIDENCE_SOURCES}
    res["contradictory_records"] = sum(bool(o.get("contradictory_record")) for o in outs)
    cc =[o["hit1"] - b["random_line"] for o, b in zip(outs, base)]; res["chance_corrected_hit1"] = {"mean": round(sum(cc) / n, 4), "ci95": boot(items, cc, tag + "cc")}
    res["minus_baseline"] = {}
    for bname in base[0]:
        d = [o["hit1"] - b[bname] for o, b in zip(outs, base)]; res["minus_baseline"][bname] = {"mean": round(sum(d) / n, 4), "ci95": boot(items, d, tag + "minus" + bname)}
    res["minus_best_baseline_reselected"] = boot_minus_best(items, [o["hit1"] for o in outs], base, tag + "minusbest")
    g = collections.defaultdict(list)
    for it, o in zip(items, outs): g[it["group"]].append(o["hit1"])
    res["by_group_hit1"] = {k: {"n": len(v), "hit1": round(sum(v) / len(v), 3), "wilson95": wilson(sum(v), len(v))} for k, v in sorted(g.items())}
    res["group_macro_average_hit1"] = round(sum(x["hit1"] for x in res["by_group_hit1"].values()) / len(res["by_group_hit1"]), 4)
    return res

def load_label_validity():
    """Report only the exact completed, frozen author span-check audit for these corrected inputs."""
    raw = (Path(ROOT) / LABEL_VALIDITY_AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != LABEL_VALIDITY_AUDIT_SHA256:
        raise ValueError("fresh40 source audit does not match its approved hash")
    audit = json.loads(raw)
    def exact(row, expected):
        return isinstance(row, dict) and all(type(row.get(k)) is type(v) and row[k] == v for k, v in expected.items())
    if not exact(audit, {"schema": "ccl-fresh40-set2-return-audit/v1", "status": "COMPLETE_VALID_RETURN_CONDITION_V_PASS", "problems": []}):
        raise ValueError("fresh40 source audit is not the approved complete return")
    summary, sampling, historical = (audit.get(key) for key in ("summary", "sampling", "historical_result"))
    if not exact(summary, {"expected": 40, "rows": 40, "complete": 40, "denominator": 40, "joint_correct": 38,
                          "required_joint_correct": 38, "condition_V": "PASS", "joint_correct_triplet": "YES/NO/NO",
                          "reviewer_count": 1, "role_counts": {"AUTHOR": 40}, "prior_exposure_counts": {"NO": 40},
                          "missing": [], "extra": [], "duplicate_sheet_ids": [], "invalid_judgments": [], "all_primary_judgments": 120}):
        raise ValueError("fresh40 counts, threshold, conjunction or reviewer scope do not match the frozen result")
    if not exact(sampling, {"eligible_remaining_frame_n": 239, "fresh_n": 40, "explicit_original40_excluded": 40, "seed": 3927191731}):
        raise ValueError("fresh40 sampling frame does not match the frozen check")
    if not exact(historical, {"correct": 35, "denominator": 40, "condition_V": "FAIL", "unchanged": True}):
        raise ValueError("fresh40 report must preserve the original failed check")
    checks = audit.get("checks")
    if not isinstance(checks, dict) or not checks or not all(value is True for value in checks.values()):
        raise ValueError("fresh40 receipt checks are incomplete or failed")
    if (not exact(audit.get("bindings"), {"gold_version": "v3", "items_sha256": CORRECTED_ITEMS_SHA256})
            or hashlib.sha256(Path(ITEMS).read_bytes()).hexdigest() != CORRECTED_ITEMS_SHA256):
        raise ValueError("fresh40 result is not bound to the current corrected-v3 items")
    return {
        "original_v2_check": {"status": "FAILED", "correct": 35, "n": 40, "threshold": 38, "reviewer_scope": "author review",
                              "source_audit": historical["original40_audit"], "source_audit_sha256": historical["original40_audit_sha256"]},
        "corrected_v3_fresh_check": {"status": "PASS", "correct": 38, "n": 40, "complete": 40, "threshold": 38,
                                    "joint_correct_triplet": "YES/NO/NO", "frame_n": 239, "seed": 3927191731,
                                    "excludes_original_40": True, "reviewer_count": 1, "reviewer_role": "AUTHOR",
                                    "prior_exposure_self_report": {"NO": 40}, "items_sha256": CORRECTED_ITEMS_SHA256},
        "source_audit": {"path": LABEL_VALIDITY_AUDIT, "sha256": LABEL_VALIDITY_AUDIT_SHA256},
        "return_sha256": audit["provenance"]["return_sha256"],
        "scope": "Separate versions and samples: original-v2 35/40 FAILED; corrected-v3 fresh40 38/40 meets the predeclared criterion. "
                 "One AUTHOR reviewer self-reports no prior exposure. This is span-correspondence validation in the remaining239 frame, "
                 "not independent/external validation, a population precision estimate, mathematical falsehood or Lean correspondence. "
                 "The two checks are not pooled and the original failure is not replaced."}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--split", default="evaluation"); a = ap.parse_args()
    with open(ITEMS, encoding="utf-8") as fh: roster = json.load(fh)["items"]
    items_split = [it for it in roster if it["split"] == a.split]
    items_all, unscorable = scoring_population(items_split)
    pops = {"primary_ge10_lines": [it for it in items_all if it["n_nonblank_text"] >= MIN_LINES and not it.get("exclude_from_primary")], "all_items": items_all}
    out = {"split": a.split, "resamples": RESAMPLES, "primary_critic": PRIMARY_CRITIC, "ladder_contrast": list(LADDER), "populations": {}}
    out["label_validity"] = load_label_validity()
    out["unscorable_exclusions"] = {"n_items": len(unscorable), "record_ids": unscorable,
                                    "scope": "Excluded from both scoring denominators; retained in complete split inference accounting."}
    runs = os.path.join(EXP, "runs"); lanes = sorted(os.listdir(runs)) if os.path.isdir(runs) else []
    lanes = [lane for lane in lanes if os.path.isdir(os.path.join(runs, lane))]
    expected_freeze, _ = freeze_hash()
    out["freeze_sha256"] = expected_freeze
    role_metadata = load_role_metadata(roster) if a.split == "evaluation" else None
    lane_records = {}; lane_cost_records = {}; lane_orphans = {}
    for lane in lanes:
        lane_records[lane] = {}
        for path in sorted(glob.glob(os.path.join(runs, lane, "*", "record.json"))):
            with open(path, encoding="utf-8") as fh: record = json.load(fh)
            check_record_freeze(record, expected_freeze, path)
            rid = record["record_id"]
            if rid in lane_records[lane]: raise ValueError("duplicate lane record: " + rid)
            lane_records[lane][rid] = record
        lane_orphans[lane] = orphan_attempt_records(os.path.join(runs, lane), expected_freeze)
        lane_cost_records[lane] = dict(lane_records[lane])
        for record in lane_orphans[lane]:
            if record["record_id"] in lane_cost_records[lane]: raise ValueError("duplicate orphan record: " + record["record_id"])
            lane_cost_records[lane][record["record_id"]] = record
    canary_records = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(EXP, "canary", "**", "record.json"), recursive=True)):
        with open(path, encoding="utf-8") as fh: record = json.load(fh)
        lane = safe(record["requested_model"]) if record.get("requested_model") else os.path.basename(os.path.dirname(path))
        canary_records[lane].append(record)
    canary_orphans = {}
    for directory in sorted(Path(EXP, "canary").glob("*")):
        if directory.is_dir():
            canary_orphans[directory.name] = orphan_attempt_records(directory)
            canary_records[directory.name].extend(canary_orphans[directory.name])
    carryover_path = os.path.join(EXP, "CARRYOVER.json")
    validated_carryover = validate_carryover(EXP, carryover_path)   # shared schema, digest, component and archive-census checks
    carryover = load_carryover(carryover_path)   # reporting adapter, after shared fail-closed validation
    out["cost_accounting"] = {"scope": "Recorded item and canary inference of the active lane directories, all retained attempts, plus the pinned carryover of archived (superseded) attempts; excludes human work, preparation, and unrecorded orphan calls.",
                               "unknown_usage_is_zero": False, "budget_charges_are_measured_tokens": False,
                               "component_scope": "measured_tokens = native usage of attempts with known usage; unknown_attempts = attempts without it; "
                                                  "observed_lower_bound_tokens = measured plus what was observed of unknown attempts; charged_tokens = conservative "
                                                  "budget charge. The four are never merged into one another; active lane and carryover are added only within a component.",
                               "carryover_file": {"name": "CARRYOVER.json", **{k: carryover[k] for k in ("sha256", "schema", "content_sha256")}}, "lanes": {}}
    for lane in sorted(set(lanes) | set(canary_records) | set(carryover["lanes"])):
        records = lane_cost_records.get(lane, {})
        full = list(records.values()); canaries = canary_records[lane]
        active = cost_components(aggregate_usage(full + canaries))
        archived = carryover["lanes"].get(lane) or {**{k: 0 for k in CARRYOVER_FIELDS}, "archived_items": 0, "listed_in_carryover": False,
                                                    "item_rows_reconcile": None, "by_archive": {}}
        out["cost_accounting"]["lanes"][lane] = {
            "active_lane": active, "carryover": archived,
            "active_lane_plus_carryover": {k: active[k] + archived[k] for k in CARRYOVER_FIELDS},
            "requested_split_inference": aggregate_usage([records.get(it["record_id"]) for it in items_split]),
            "by_split": {split: aggregate_usage([records[it["record_id"]] for it in roster
                                                  if it["split"] == split and it["record_id"] in records])
                         for split in sorted({it["split"] for it in roster})},
            "all_item_inference": aggregate_usage(full), "canary_inference": aggregate_usage(canaries),
            "complete_recorded_experiment_inference": aggregate_usage(full + canaries),
            "unfinished_item_records": len(lane_orphans.get(lane, [])),
            "unfinished_canary_records": len(canary_orphans.get(lane, [])),
            "canary_freeze_hashes": sorted({r.get("freeze_sha256") or "not_final_frozen" for r in canaries})}
    split_of = {it["record_id"]: it["split"] for it in roster}
    out["parser_fallbacks"] = {"scope": "Completed item records of each active lane; strict_json means no fallback. Counts are read from the parse audit saved with each record. A fallback changes how an answer is decoded, never which slots are scored.", "lanes": {}}
    for lane in lanes:
        by_split = collections.defaultdict(list)
        for rid, record in lane_records[lane].items(): by_split[split_of.get(rid, "not_in_roster")].append(record)
        out["parser_fallbacks"]["lanes"][lane] = {"all_item_records": parser_fallback_report(lane_records[lane].values()),
                                                  "by_split": {split: parser_fallback_report(rs) for split, rs in sorted(by_split.items())}}
    if a.split == "evaluation":
        out["refutation_role_census"] = refutation_role_report(
            pops["primary_ge10_lines"], role_metadata, lane_records.get(safe(PRIMARY_CRITIC), {}),
            lane_cost_records.get(safe(PRIMARY_CRITIC), {}))
    for pname, items in pops.items():
        base = [baselines(it) for it in items]; P = {"n_items": len(items), "baselines": {}}
        if not items:
            P.update(best_baseline=None, critics={}, paired_hit1_differences={})
            out["populations"][pname] = P
            continue
        for b in base[0]:
            v = [x[b] for x in base]; P["baselines"][b] = {"mean": round(sum(v) / len(v), 4), "ci95": boot(items, v, pname + b)}
        P["best_baseline"] = max((b for b in base[0] if b != "random_line"), key=lambda b: P["baselines"][b]["mean"])
        P["critics"] = {}; outs_by = {}
        for lane in lanes:
            recs = [lane_records[lane].get(it["record_id"]) for it in items]
            present = sum(r is not None for r in recs)
            if present == 0: continue
            outs = [outcome(it, r) for it, r in zip(items, recs)]
            c = summarise(items, outs, base, pname + lane); c["records_present"] = present; c["complete"] = present == len(items)
            c["inference_usage"] = aggregate_usage([lane_cost_records[lane].get(it["record_id"]) for it in items])
            c["attributable_tokens"] = c["inference_usage"]["total_attributable_tokens"]
            if not c["complete"]:   # incomplete lane: the ITT numbers above stay (missing = miss), labelled incomplete; present-only is added; no pairs, no reading
                sub = [(it, o, b) for it, o, b, r in zip(items, outs, base, recs) if r is not None]
                c["present_only"] = summarise([s[0] for s in sub], [s[1] for s in sub], [s[2] for s in sub], pname + lane + "present")
            else: outs_by[lane] = outs
            P["critics"][lane] = c
        P["paired_hit1_differences"] = {}
        names = sorted(outs_by)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                d = [x["hit1"] - y["hit1"] for x, y in zip(outs_by[names[i]], outs_by[names[j]])]
                P["paired_hit1_differences"][names[i] + " minus " + names[j]] = {"mean": round(sum(d) / len(d), 4), "ci95": boot(items, d, pname + names[i] + names[j])}
        out["populations"][pname] = P
    P = out["populations"]["primary_ge10_lines"]; need = {PRIMARY_CRITIC, *LADDER}
    if need <= {m for m, c in P["critics"].items() if c["complete"]}:
        pc = P["critics"][PRIMARY_CRITIC]; key = LADDER[0] + " minus " + LADDER[1]
        lad = P["paired_hit1_differences"].get(key) or {k: (-v if k == "mean" else [-v[1], -v[0]]) for k, v in P["paired_hit1_differences"][LADDER[1] + " minus " + LADDER[0]].items()}
        S = pc["minus_best_baseline_reselected"]["ci95"][0] > 0; D = lad["ci95"][0] > 0; H = pc["hit1"]["ci95"][1] < 0.90
        out["preregistered_reading"] = {"V_label_validity": out["label_validity"]["corrected_v3_fresh_check"], "S_signal": S, "D_discrimination": D,
                                        "H_headroom": H, "ladder_contrast": lad, "reading_conditional_on_V": conditional_reading(S, D, H)}
    else: out["preregistered_reading"] = {"reading": "not evaluable: a primary lane is missing or incomplete"}
    if a.split == "evaluation":
        history = historical_evaluation_sources(EXP, expected_freeze, validated_carryover)
        out["lifetime_evaluation"] = lifetime_evaluation_report(pops, lane_records, lane_cost_records, history)
    with open(os.path.join(EXP, "RESULTS_%s.json" % a.split), "w", encoding="utf-8") as fh: json.dump(out, fh, indent=1)
    for pname, P in out["populations"].items():
        print("==", pname, "n", P["n_items"], "| baselines", {k: v["mean"] for k, v in P["baselines"].items()}, "| best", P["best_baseline"])
        for m, c in P["critics"].items():
            print("   %-28s present %3d hit1 %.3f %s hit3 %.3f perprot %s macro %.3f misses %s" % (m, c["records_present"], c["hit1"]["mean"], c["hit1"]["ci95"], c["hit3"]["mean"], c["per_protocol_hit1"]["mean"], c["group_macro_average_hit1"], c["rule_misses_by_cause"]))
    for lane, cost in out["cost_accounting"]["lanes"].items():
        print("== cost %-28s active %s | carryover %s | together %s" % (lane, cost["active_lane"], {k: cost["carryover"][k] for k in CARRYOVER_FIELDS}, cost["active_lane_plus_carryover"]))
    for lane, paths in out["parser_fallbacks"]["lanes"].items():
        print("== parser %-26s %s" % (lane, paths["all_item_records"]))
    print(json.dumps(out["preregistered_reading"], indent=1))

if __name__ == "__main__": main()
