#!/usr/bin/env python3
"""Telemetry + grade summary for runs/cost_experiment_repro_20260915.

Per (set, model): per-arm output-token statistics from the accepted attempt's
engine usage record; paired refute-vs-<arm> ratios with the SAME estimator as
Task 1 (scripts/cost_experiment_telemetry.py: ratio of summed output tokens over
records that have both arms with output > 0, record bootstrap seed 20260819,
B=2000, indices 50/1949; pairs sorted by record id) plus the geometric mean of
per-record ratios and the "refute cheaper on k/n" count; all-token ratios; grade
tallies (strict catch = CAUGHT_MATCHING+CAUGHT_DIFFERENT; lenient adds
CAUGHT_UNSUPPORTED; UNVERIFIED reported separately) over graded cells AND over
planned records (absent = MISSED, the Task-1 rule); pre-registered strata:
claims60 hint-flagged ids (with/without) and codex cells with extra shell
executions (with/without).  Output tokens: Claude = modelUsage[bound
model].outputTokens (includes thinking); Codex = turn.completed
usage.output_tokens (reasoning is a subset).  The Task-1 Opus proofs100 rows
(model key opus_task1) come from runs/cost_experiment/telemetry.jsonl, which
summed message.usage per transcript LINE; a 2026-09-15 review found Claude Code
writes one line per content block with identical usage, so those absolute
counts may be inflated by an arm-dependent factor -- they are labelled and
kept in a separate table.  Cross-model absolute tokens are never compared.

Attempt accounting (added 2026-09-15 after Astra's A26): the primary
statistics above use the ACCEPTED attempt only.  A second view, per arm, adds
every rejected attempt in ledger/<set>_<model>.jsonl (RATE_LIMITED, FAILED,
INVALID_ANSWER, NOT_READ, REFUSED, TIMEOUT, GAVE_UP): the engine-reported
tokens of those attempts where a usage record exists ("reported"), the number
of rejected attempts with no token count ("unknown cost"), and the total
observed output = accepted + reported-rejected.  Reported rejected counts are
the engine's own accounting (Claude modelUsage after an error, Gemini usage of
an ERROR result); they are shown separately, never merged into the primary
estimator, and the largest rejected attempts are listed by cell so outliers
(e.g. a Claude turn loop that hit the 64k output cap four times) are visible.
"""
import json, math, random, statistics, time
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
RUN = BASE / "runs/cost_experiment_repro_20260915"
SEED, B = 20260819, 2000
STRICT = ("CAUGHT_MATCHING", "CAUGHT_DIFFERENT"); LENIENT = STRICT + ("CAUGHT_UNSUPPORTED",)

def load_task1_opus():
    out = {}
    for line in open(BASE / "runs/cost_experiment/telemetry.jsonl"):
        r = json.loads(line)
        out[(r["record_id"], r["arm"])] = {"output": r["output"], "input_uncached": r["input_uncached"], "input_cache_read": r["input_cache_read"],
                                           "api_calls": r["api_calls"], "model": "claude-opus-5 (Task 1 transcript per-line sum)", "extra_exec": 0}
    return out

def load_usage(set_, model):
    if model == "opus_task1": return load_task1_opus()
    d = RUN / "usage" / set_ / model; out = {}
    for p in d.glob("*.json"):
        u = json.load(open(p)); us = u["usage"]
        if us["engine"] == "claude":
            bm = us.get("bound_model_usage") or {}; k = next(iter(bm), None); b = bm.get(k, {})
            rec = {"output": us.get("output_tokens_bound_model"), "input_uncached": b.get("inputTokens", 0) + b.get("cacheCreationInputTokens", 0),
                   "input_cache_read": b.get("cacheReadInputTokens", 0), "cost_usd": b.get("costUSD"), "api_calls": us.get("api_messages"),
                   "thinking": b.get("thinkingTokens"), "model": k, "extra_exec": 0}
        elif us["engine"] == "agy":
            u2 = us.get("usage") or {}
            rec = {"output": us.get("output_tokens_bound_model"), "input_uncached": int(u2.get("input_tokens", 0)) - int(u2.get("cache_read_tokens", 0)),
                   "input_cache_read": int(u2.get("cache_read_tokens", 0)), "thinking": u2.get("thinking_tokens"), "api_calls": len(us.get("usage_steps") or []),
                   "model": us.get("init_model") or us.get("requested_model"), "extra_exec": us.get("extra_exec_count", 0)}
        else:
            t = us["usage_total"]
            rec = {"output": us.get("output_tokens_bound_model"), "input_uncached": t["input_tokens"] - t.get("cached_input_tokens", 0),
                   "input_cache_read": t.get("cached_input_tokens", 0), "reasoning_output": t.get("reasoning_output_tokens"),
                   "api_calls": len(us.get("turns") or []), "model": us.get("requested_model"), "extra_exec": us.get("extra_exec_count", 0)}
        rec["seconds"] = u.get("seconds"); rec["attempt"] = u.get("attempt")
        out[(u["record_id"], u["arm"])] = rec
    return out

REJECTED = ("RATE_LIMITED", "FAILED", "INVALID_ANSWER", "NOT_READ", "REFUSED", "TIMEOUT", "GAVE_UP", "STOP_REQUESTED")

def load_attempts(set_, model):
    """Every ledger row for (set, model) with the engine-reported tokens of its attempt, if a usage record exists."""
    led = RUN / "ledger" / f"{set_}_{model}.jsonl"
    if not led.exists(): return []
    out = []
    for line in open(led):
        try: r = json.loads(line)
        except Exception: continue
        a = {"cell": r.get("cell"), "record_id": r.get("record_id"), "arm": r.get("arm"), "attempt": r.get("attempt"), "status": r.get("status"),
             "output": r.get("output_tokens") if isinstance(r.get("output_tokens"), int) else None, "input_uncached": None, "input_cache_read": None,
             "cost_usd": None, "engine_error": None}
        wd = r.get("workdir"); up = Path(wd) / "usage.json" if wd else None
        if up and up.exists():
            try:
                us = json.load(open(up)); eng = us.get("engine")
                if isinstance(us.get("output_tokens_bound_model"), int): a["output"] = us["output_tokens_bound_model"]
                if eng == "claude":
                    bm = us.get("bound_model_usage") or {}; b = bm.get(next(iter(bm), None), {}) if bm else {}
                    a["input_uncached"] = b.get("inputTokens", 0) + b.get("cacheCreationInputTokens", 0); a["input_cache_read"] = b.get("cacheReadInputTokens", 0)
                    a["cost_usd"] = b.get("costUSD"); errs = us.get("errors") or []
                    a["engine_error"] = (errs[0][:120] if errs else None) or ("synthetic model message" if us.get("synthetic_model_seen") else None) or ("is_error" if us.get("is_error") else None)
                elif eng == "agy":
                    u2 = us.get("usage") or {}
                    a["input_uncached"] = int(u2.get("input_tokens", 0)) - int(u2.get("cache_read_tokens", 0)); a["input_cache_read"] = int(u2.get("cache_read_tokens", 0))
                    a["engine_error"] = (str(us.get("error"))[:120] if us.get("error") else None) or (us.get("result_status") if us.get("result_status") not in (None, "SUCCESS") else None)
                else:
                    t = us.get("usage_total") or {}
                    if t: a["input_uncached"] = t.get("input_tokens", 0) - t.get("cached_input_tokens", 0); a["input_cache_read"] = t.get("cached_input_tokens", 0)
                    errs = us.get("errors") or []; a["engine_error"] = errs[0][:120] if errs else None
            except Exception as e:
                a["engine_error"] = f"usage record unreadable: {e}"[:120]
        elif wd and (Path(wd) / "events.jsonl").exists():
            # no usage record (e.g. the backend shell was killed after the model finished): recover the engine's own
            # usage from the event log and flag the source, so the attempt is "reported", not "unknown"
            try:
                o = i_ = c_ = 0; seen = False
                for line in open(Path(wd) / "events.jsonl", errors="ignore"):
                    try: e = json.loads(line)
                    except Exception: continue
                    if e.get("type") == "turn.completed" and isinstance(e.get("usage"), dict):  # codex
                        u = e["usage"]; o += int(u.get("output_tokens", 0)); i_ += int(u.get("input_tokens", 0)); c_ += int(u.get("cached_input_tokens", 0)); seen = True
                    elif e.get("event") == "result" and isinstance((e.get("result") or {}).get("usage"), dict):  # agy
                        u = e["result"]["usage"]; o += int(u.get("output_tokens", 0)); i_ += int(u.get("input_tokens", 0)); c_ += int(u.get("cache_read_tokens", 0)); seen = True
                    elif e.get("type") == "result" and isinstance(e.get("modelUsage"), dict):  # claude
                        for k, u in e["modelUsage"].items():
                            if "haiku" in k: continue
                            o += int(u.get("outputTokens", 0)); i_ += int(u.get("inputTokens", 0)) + int(u.get("cacheCreationInputTokens", 0)); c_ += int(u.get("cacheReadInputTokens", 0)); seen = True
                if seen:
                    a["output"] = o; a["input_uncached"] = i_ - c_ if i_ >= c_ else i_; a["input_cache_read"] = c_; a["token_source"] = "events_fallback"
                    a["engine_error"] = a.get("engine_error") or "no usage record; tokens recovered from the event log"
            except Exception as e:
                a["engine_error"] = f"event log unreadable: {e}"[:120]
        out.append(a)
    return out

def attempt_accounting(attempts, ids, arm, accepted_sum):
    rows = [a for a in attempts if a["arm"] == arm and a["record_id"] in ids]
    rej = [a for a in rows if a["status"] not in ("COMPLETE", "COMPLETE_RECOVERED")]
    by_status = {}
    for a in rej: by_status[a["status"]] = by_status.get(a["status"], 0) + 1
    reported = [a for a in rej if isinstance(a["output"], int)]
    unknown = [a for a in rej if not isinstance(a["output"], int)]
    rep_out = sum(a["output"] for a in reported)
    rep_in = sum((a["input_uncached"] or 0) + (a["input_cache_read"] or 0) for a in reported if a["input_uncached"] is not None)
    top = sorted(reported, key=lambda a: -a["output"])[:5]
    return {"attempts_total": len(rows), "attempts_rejected": len(rej), "rejected_by_status": by_status,
            "rejected_reported_from_event_log_n": sum(1 for a in reported if a.get("token_source") == "events_fallback"),
            "rejected_output_reported_sum": rep_out, "rejected_input_reported_sum": rep_in, "rejected_reported_n": len(reported),
            "rejected_unknown_cost_n": len(unknown), "rejected_unknown_cost_cells": sorted({a["cell"] for a in unknown}),
            "rejected_cost_usd_sum": (sum(a["cost_usd"] or 0 for a in reported) if any(a["cost_usd"] for a in reported) else None),
            "accepted_output_sum": accepted_sum, "total_observed_output_sum": accepted_sum + rep_out,
            "total_over_accepted": ((accepted_sum + rep_out) / accepted_sum) if accepted_sum else None,
            "largest_rejected": [{"cell": a["cell"], "attempt": a["attempt"], "status": a["status"], "output": a["output"], "engine_error": a["engine_error"]} for a in top]}

def ratio_of_sums(pairs, key):
    a = sum(p[0][key] for p in pairs); b = sum(p[1][key] for p in pairs)
    return a / b if b else None

def bootstrap(pairs, key):
    rng = random.Random(SEED); n = len(pairs); vals = []
    for _ in range(B):
        s = [pairs[rng.randrange(n)] for _ in range(n)]
        v = ratio_of_sums(s, key)
        if v is not None: vals.append(v)
    vals.sort(); return [vals[50], vals[1949]] if len(vals) == B else ([vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]] if vals else None)

def geomean(pairs, key):
    xs = [math.log(p[0][key] / p[1][key]) for p in pairs if p[0][key] and p[1][key]]
    return math.exp(sum(xs) / len(xs)) if xs else None

def paired(U, ids, arm, subset=None, cov=None):
    pairs = []; recs = []
    for r in sorted(ids):
        if subset is not None and r not in subset: continue
        a, b = U.get((r, "refute")), U.get((r, arm))
        if a and b and isinstance(a.get("output"), int) and isinstance(b.get("output"), int) and a["output"] > 0 and b["output"] > 0:
            pairs.append((a, b)); recs.append(r)
    if not pairs: return None
    allk = lambda x: x["output"] + x["input_uncached"] + x["input_cache_read"]
    pairs_all = [({"t": allk(a)}, {"t": allk(b)}) for a, b in pairs]
    res = {"n_pairs": len(pairs), "output_ratio_of_sums": ratio_of_sums(pairs, "output"), "output_ci95_record_bootstrap": bootstrap(pairs, "output"),
           "output_geomean_per_record": geomean(pairs, "output"), "refute_cheaper_on": sum(1 for a, b in pairs if a["output"] < b["output"]),
           "median_per_record_ratio": statistics.median([a["output"] / b["output"] for a, b in pairs]),
           "all_tokens_ratio_of_sums": ratio_of_sums(pairs_all, "t")}
    if cov is not None:  # secondary: same pairs, accepted + reported rejected-attempt output (A26 view); no bootstrap
        T, KN, UN = cov["T"], cov["KN"], cov["UN"]
        pairs_tot = [({"t": a["output"] + T.get((r, "refute"), 0)}, {"t": b["output"] + T.get((r, arm), 0)}) for (a, b), r in zip(pairs, recs)]
        res["total_observed_output_ratio_of_sums"] = ratio_of_sums(pairs_tot, "t")
        # A30: coverage of the observed total. Where unknown-cost attempts exist, each side's total is a lower bound and the ratio is not a bound on the true ratio.
        unk_pairs = sum(1 for r in recs if UN.get((r, "refute"), 0) or UN.get((r, arm), 0))
        res["total_observed_coverage"] = {"pairs": len(pairs), "pairs_with_unknown_cost_attempts": unk_pairs,
                                          "unknown_cost_attempts": sum(UN.get((r, "refute"), 0) + UN.get((r, arm), 0) for r in recs),
                                          "known_rejected_attempts": sum(KN.get((r, "refute"), 0) + KN.get((r, arm), 0) for r in recs),
                                          "rejected_output_included": sum(T.get((r, "refute"), 0) + T.get((r, arm), 0) for r in recs)}
    return res

def summarize(set_, model):
    P = json.load(open(RUN / "prompts.json")); man = json.load(open(RUN / "manifest.json"))
    pk = "proofs100" if set_.startswith("proofs100") else set_
    arms = P[pk]["arms"]; ids = json.load(open(RUN / f"{pk}_ids.json"))
    hint = set(man.get("claims60_hint_flagged_ids", [])) if set_ == "claims60" else set()
    U = load_usage(set_, model)
    task1 = model == "opus_task1"
    ATT = [] if task1 else load_attempts(set_, model)
    T, KN, UN = {}, {}, {}  # (record, arm) -> engine-reported output of rejected attempts / their count / count with no token count
    for a in ATT:
        if a["status"] in ("COMPLETE", "COMPLETE_RECOVERED"): continue
        k = (a["record_id"], a["arm"])
        if isinstance(a["output"], int): T[k] = T.get(k, 0) + a["output"]; KN[k] = KN.get(k, 0) + 1
        else: UN[k] = UN.get(k, 0) + 1
    COV = None if task1 else {"T": T, "KN": KN, "UN": UN}
    G = {}
    gd = (BASE / "runs/cost_experiment/grades") if task1 else (RUN / "grades" / set_ / model)
    for p in gd.glob("*.json"):
        g = json.load(open(p)); G[(g["record_id"], g["arm"])] = g["grade"]
    A = {}
    ad = (BASE / "runs/cost_experiment/assessments") if (task1 or set_ == "proofs100_task1") else (RUN / "assessments" / set_ / model)
    for p in ad.glob("*.json"):
        a = json.load(open(p)); A[(a["record_id"], a["arm"])] = a
    res = {"set": set_, "model": model, "records_planned": len(ids), "arms": {}, "paired": {}, "paired_strata": {},
           "hint_flagged_ids": sorted(hint), "attempt_accounting": {},
           "token_source": ("Task-1 transcript per-line sums (possibly inflated by content-block multiplicity; see docstring)" if task1 else "engine usage record of the accepted attempt")}
    for arm in arms:
        rows = [U[(r, arm)] for r in ids if (r, arm) in U]
        outs = [x["output"] for x in rows if isinstance(x.get("output"), int) and x["output"] > 0]
        verd, grades = {}, {}
        inv_empty = 0
        for r in ids:
            a = A.get((r, arm))
            if a:
                verd[a.get("verdict")] = verd.get(a.get("verdict"), 0) + 1
                if a.get("verdict") == "INVALID" and not (a.get("counterexample") or "").strip(): inv_empty += 1
            g = G.get((r, arm))
            if g: grades[g] = grades.get(g, 0) + 1
        ng = sum(grades.values()); strict = sum(grades.get(k, 0) for k in STRICT); lenient = sum(grades.get(k, 0) for k in LENIENT)
        res["arms"][arm] = {"n_planned": len(ids), "n_complete": len(rows), "n_usable_output": len(outs), "output_sum": sum(outs),
                            "output_mean": statistics.mean(outs) if outs else None, "output_median": statistics.median(outs) if outs else None,
                            "verdicts": verd, "invalid_with_empty_counterexample": inv_empty, "grades": grades, "n_graded": ng,
                            "catch_strict": strict, "catch_lenient": lenient, "false_catch": grades.get("FALSE_CATCH", 0), "unverified": grades.get("UNVERIFIED", 0),
                            "catch_rate_graded": (strict / ng) if ng else None, "catch_rate_planned_absent_missed": strict / len(ids),
                            "extra_exec_cells": sum(1 for x in rows if x.get("extra_exec")),
                            "cost_usd_sum": (sum(x.get("cost_usd") or 0 for x in rows) if model == "opus" else None),
                            "thinking_mean": (statistics.mean([x["thinking"] for x in rows if isinstance(x.get("thinking"), int)]) if any(isinstance(x.get("thinking"), int) for x in rows) else None),
                            "api_calls_mean": (statistics.mean([x["api_calls"] for x in rows if isinstance(x.get("api_calls"), int)]) if rows else None)}
        if not task1: res["attempt_accounting"][arm] = attempt_accounting(ATT, set(ids), arm, sum(outs))
    for arm in arms:
        if arm == "refute": continue
        p = paired(U, ids, arm, cov=COV)
        if p: res["paired"][f"refute_vs_{arm}"] = p
        strata = {}
        if hint:
            strata["without_hint_flagged"] = paired(U, ids, arm, subset=set(ids) - hint)
            strata["hint_flagged_only"] = paired(U, ids, arm, subset=hint)
        clean = {r for r in ids if not (U.get((r, "refute")) or {}).get("extra_exec") and not (U.get((r, arm)) or {}).get("extra_exec")}
        if any(x.get("extra_exec") for x in U.values()):
            strata["without_extra_exec_cells"] = paired(U, ids, arm, subset=clean)
        if strata: res["paired_strata"][f"refute_vs_{arm}"] = strata
    return res

def fmt(v, nd=3):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))

def main():
    RUN.joinpath("summary").mkdir(exist_ok=True)
    lines = ["# Task-1 cost-experiment reproduction — summary", "",
             f"Generated {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}. Output tokens = the engine's usage record for the accepted attempt (Claude modelUsage outputTokens incl. thinking; Codex turn usage output_tokens incl. reasoning). Ratios = ratio of arm sums over paired records with output > 0 (Task-1 estimator), 95% record-bootstrap CI (seed 20260819, B=2000, pairs sorted by record id); geometric mean of per-record ratios also shown. Catch (strict) = CAUGHT_MATCHING + CAUGHT_DIFFERENT; lenient adds CAUGHT_UNSUPPORTED (claims60 only); planned-denominator rate counts absent cells as MISSED (Task-1 rule).",
             "", "The `opus_task1` rows are the ORIGINAL 2026-08-20 Task-1 Opus cells, taken from `runs/cost_experiment/telemetry.jsonl` (per-transcript-line usage sums; a 2026-09-15 review found those may be inflated by content-block multiplicity, so their absolute counts are not comparable to the engine-usage rows; their within-arm ratios are the paper's published values).", ""]
    for set_ in ("proofs100", "claims60"):
        for model in ("opus_task1", "opus", "sol", "gemini"):
            if model == "opus_task1" and set_ != "proofs100": continue
            if model != "opus_task1" and not (RUN / "usage" / set_ / model).exists(): continue
            r = summarize(set_, model)
            json.dump(r, open(RUN / "summary" / f"{set_}_{model}.json", "w"), indent=1)
            lines += [f"## {set_} × {model}", "", f"token source: {r['token_source']}", "",
                      "| arm | complete/planned | output mean | output median | verdicts | INVALID w/o witness | graded | catch strict | lenient | false catch | unverified | catch rate (graded) | catch rate (planned) | extra-exec cells |",
                      "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
            for arm, s in r["arms"].items():
                lines.append(f"| {arm} | {s['n_complete']}/{s['n_planned']} | {fmt(s['output_mean'],0)} | {fmt(s['output_median'],1)} | {json.dumps(s['verdicts'])} | {s['invalid_with_empty_counterexample']} | {s['n_graded']} | {s['catch_strict']} | {s['catch_lenient']} | {s['false_catch']} | {s['unverified']} | {fmt(s['catch_rate_graded'])} | {fmt(s['catch_rate_planned_absent_missed'])} | {s['extra_exec_cells']} |")
            lines += ["", "| contrast | pairs | output ratio (sums) | 95% CI | geomean | refute cheaper on | all-token ratio | total-observed output ratio (A26, secondary; pairs with unknown-cost attempts / unknown attempts) |", "|---|---:|---:|---|---:|---:|---:|---:|"]
            for k, p in r["paired"].items():
                ci = p["output_ci95_record_bootstrap"]
                lines.append(f"| {k} | {p['n_pairs']} | {fmt(p['output_ratio_of_sums'])} | [{fmt(ci[0])}, {fmt(ci[1])}] | {fmt(p['output_geomean_per_record'])} | {p['refute_cheaper_on']}/{p['n_pairs']} | {fmt(p['all_tokens_ratio_of_sums'])} | {fmt(p.get('total_observed_output_ratio_of_sums'))}{(' (' + str(p['total_observed_coverage']['pairs_with_unknown_cost_attempts']) + ' / ' + str(p['total_observed_coverage']['unknown_cost_attempts']) + ')') if p.get('total_observed_coverage') else ''} |")
            for k, strata in r["paired_strata"].items():
                for name, p in strata.items():
                    if not p: continue
                    ci = p["output_ci95_record_bootstrap"]
                    lines.append(f"| {k} [{name}] | {p['n_pairs']} | {fmt(p['output_ratio_of_sums'])} | [{fmt(ci[0])}, {fmt(ci[1])}] | {fmt(p['output_geomean_per_record'])} | {p['refute_cheaper_on']}/{p['n_pairs']} | {fmt(p['all_tokens_ratio_of_sums'])} |")
            if r["attempt_accounting"]:
                lines += ["", "Attempt accounting (A26): accepted-attempt output vs every attempt in the ledger. 'reported' = engine-reported tokens of rejected attempts (from the usage record, or recovered from the event log when the backend shell died after the model finished; the count of the latter is in summary/*.json as rejected_reported_from_event_log_n); 'unknown' = rejected attempts with no token count (cost not observed). Total observed = accepted + reported; it is a secondary view, not the estimator.", "",
                          "| arm | attempts | rejected (by status) | rejected output reported (n) | unknown-cost attempts | accepted output sum | total observed output | total/accepted | rejected cost USD |", "|---|---:|---|---:|---:|---:|---:|---:|---:|"]
                for arm, s in r["attempt_accounting"].items():
                    lines.append(f"| {arm} | {s['attempts_total']} | {json.dumps(s['rejected_by_status'])} | {s['rejected_output_reported_sum']} ({s['rejected_reported_n']}) | {s['rejected_unknown_cost_n']} | {s['accepted_output_sum']} | {s['total_observed_output_sum']} | {fmt(s['total_over_accepted'])} | {fmt(s['rejected_cost_usd'], 2) if False else fmt(s['rejected_cost_usd_sum'], 2)} |")
                big = sorted((x for s in r["attempt_accounting"].values() for x in s["largest_rejected"]), key=lambda x: -x["output"])[:6]
                if big: lines += ["", "Largest rejected attempts: " + "; ".join(f"{x['cell']} attempt {x['attempt']} {x['status']} {x['output']} output tokens ({x['engine_error'] or 'no engine error text'})" for x in big)]
            incomplete = [a for a, s in r["arms"].items() if s["n_complete"] < s["n_planned"]]
            if incomplete: lines.append(f"\nWARNING: incomplete arms {incomplete}; paired ratios use only records complete in both arms.")
            lines.append("")
    (RUN / "REPORT.md").write_text("\n".join(lines)); print("\n".join(lines))

if __name__ == "__main__":
    main()
