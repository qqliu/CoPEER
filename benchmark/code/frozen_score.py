"""Frozen scientific functions: verbatim source statements; see provenance.json."""
import collections, hashlib, json, math, random, re
from frozen_common import MAX_OUTPUT, NORMALISATIONS, usage_summary
RESAMPLES = 10000

ATTEMPT_CLASS_CAUSE = {"VALID_ANSWER": None, "BUDGET_EXHAUSTED": "budget_exhausted", "CONTRACT_VIOLATION": "contract_violation",
                       "TRANSPORT_FAILURE": "transport_failure", "SETUP_FAILURE": "setup_failure"}

STOP_REASON_CLASS = {"output_budget_exhausted": "BUDGET_EXHAUSTED", "output_token_cap": "BUDGET_EXHAUSTED", "contract_violation": "CONTRACT_VIOLATION",
                     "setup_failure": "SETUP_FAILURE", "prompt_exceeds_context_with_output_cap": "SETUP_FAILURE",
                     "call_token_cap_prevents_attempt": "SETUP_FAILURE"}

BUDGET_EVIDENCE_SOURCES = ("inferred_client_limit_exhaustion", "native_max_tokens", "native_local_length", "live_output_estimate",
                           "native_output_tokens_over_budget", "unknown")

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
    return "unknown"

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
