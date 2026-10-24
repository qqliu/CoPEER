"""Frozen scientific functions: verbatim source statements; see provenance.json."""
import json, re
MAX_OUTPUT = 16000

PARSER_VERSION = "original-first-three-v3-string-aware-leading-zero-labels"

ARRAY_ONLY_PARSER_VERSION = "original-first-three-v4-array-only-fallback"

NORMALISATIONS = ("leading_zero_labels_in_candidates_array", "array_only_candidates_extraction",
                  "array_only_candidates_extraction_with_leading_zero_labels")

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
