"""Original pure token aggregation functions, extracted without changes.
See PROVENANCE.json for original source hashes and transformation scope.
"""

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
