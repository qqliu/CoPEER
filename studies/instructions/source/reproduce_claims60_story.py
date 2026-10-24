#!/usr/bin/env python3
"""Offline claims60 evidence counts and corrected accepted-attempt token totals.

Reads frozen research evidence only; writes its derived JSON beside this script.
No dependencies, network, subprocesses, model calls, or regrading.

Default (fast, deterministic):
  python3 astra/story_20260921/reproduce_claims60_story.py

To reproduce the memo's new pointwise full-token bootstrap intervals:
  python3 astra/story_20260921/reproduce_claims60_story.py --bootstrap-resamples 20000

The JSON hashes every source read, the script, and all frozen claims60 inputs
and references. It verifies the latter against the original manifest.
"""

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import random


SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[2]
RUN = ROOT / "qedbench_certificate_availability_triage/runs/cost_experiment_repro_20260915"
MODELS = ("sol", "gemini", "opus")
ARMS = ("refute", "prove_full", "prove_earlystop", "prove_earlystop_witness")
STRICT = {"CAUGHT_MATCHING", "CAUGHT_DIFFERENT"}
SOURCE_HASHES = {}


def read_json(path):
    data = path.read_bytes()
    SOURCE_HASHES[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return json.loads(data)


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def bound_usage(model, outer):
    usage = outer["usage"]
    output = usage["output_tokens_bound_model"]
    require(isinstance(output, int) and output > 0, "Missing/invalid output usage")
    auxiliary = None
    if model == "sol":
        require(usage["engine"] == "codex", "Unexpected Sol engine")
        native = usage["usage_total"]
        cache = native.get("cached_input_tokens", 0)
        uncached = native["input_tokens"] - cache
        require(output == native["output_tokens"], "Sol output receipt mismatch")
        legacy_full = native["input_tokens"] + output
    elif model == "gemini":
        require(usage["engine"] == "agy", "Unexpected Gemini engine")
        native = usage["usage"]
        # Gemini reports input_tokens EXCLUDING the separately reported cache.
        # The historical summary incorrectly subtracted cache from this field.
        uncached = native["input_tokens"]
        cache = native.get("cache_read_tokens", 0)
        require(output == native["output_tokens"], "Gemini output receipt mismatch")
        legacy_full = uncached + output
    else:
        require(usage["engine"] == "claude", "Unexpected Opus engine")
        models = usage["bound_model_usage"]
        require(len(models) == 1, "Expected one bound Opus model")
        native = next(iter(models.values()))
        uncached = native.get("inputTokens", 0) + native.get("cacheCreationInputTokens", 0)
        cache = native.get("cacheReadInputTokens", 0)
        require(output == native["outputTokens"], "Opus output receipt mismatch")
        legacy_full = uncached + cache + output
        all_models = usage["modelUsage"]
        bound_name = next(iter(models))
        require(all_models[bound_name] == native, "Opus bound/all-model receipt mismatch")
        auxiliary = {
            "uncached_input_including_creation": sum(v["inputTokens"] + v["cacheCreationInputTokens"] for k, v in all_models.items() if k != bound_name),
            "cache_read_input": sum(v["cacheReadInputTokens"] for k, v in all_models.items() if k != bound_name),
            "output": sum(v["outputTokens"] for k, v in all_models.items() if k != bound_name),
        }
    require(uncached >= 0 and cache >= 0, "Negative corrected input component")
    aux = auxiliary or {"uncached_input_including_creation": 0, "cache_read_input": 0, "output": 0}
    return {
        "bound_model_output": output,
        "bound_model_uncached_input_including_creation": uncached,
        "bound_model_cache_read_input": cache,
        "bound_model_full_tokens": uncached + cache + output,
        "all_reported_models_output": output + aux["output"],
        "all_reported_models_uncached_input_including_creation": uncached + aux["uncached_input_including_creation"],
        "all_reported_models_cache_read_input": cache + aux["cache_read_input"],
        "all_reported_models_full_tokens": uncached + cache + output + sum(aux.values()),
        "auxiliary_models_reported": auxiliary is not None,
        "auxiliary_models": auxiliary,
        "historical_summary_full_tokens": legacy_full,
        "extra_exec_count": usage.get("extra_exec_count", 0),
    }


def full_bootstrap(pairs, repetitions, seed):
    if not repetitions:
        return None
    rng = random.Random(seed)
    n = len(pairs)
    values = []
    for _ in range(repetitions):
        indices = [rng.randrange(n) for _ in range(n)]
        values.append(
            sum(pairs[i][0] for i in indices) / sum(pairs[i][1] for i in indices)
        )
    values.sort()
    return [values[int(0.025 * repetitions)], values[int(0.975 * repetitions) - 1]]


def aggregate(cells, selected, arm):
    rows = [cells[record_id, arm] for record_id in selected]
    grades = collections.Counter(row["grade"] for row in rows)
    verdicts = collections.Counter(row["verdict"] for row in rows)
    sums = {
        name: sum(row["usage"][name] for row in rows)
        for name in (
            "bound_model_output", "bound_model_uncached_input_including_creation", "bound_model_cache_read_input",
            "bound_model_full_tokens", "all_reported_models_output", "all_reported_models_uncached_input_including_creation",
            "all_reported_models_cache_read_input", "all_reported_models_full_tokens", "historical_summary_full_tokens",
        )
    }
    return {
        "n": len(rows),
        "grader_supported_refutations": sum(grades.get(g, 0) for g in STRICT),
        "grade_counts": dict(sorted(grades.items())),
        "verdict_counts": dict(sorted(verdicts.items())),
        "invalid_with_empty_counterexample_field": sum(
            row["verdict"] == "INVALID" and row["counterexample_empty"] for row in rows
        ),
        "recorded_extra_execution_cells": sum(row["usage"]["extra_exec_count"] > 0 for row in rows),
        "accepted_attempt_token_sums": sums,
        "cells_with_reported_auxiliary_models": sum(row["usage"]["auxiliary_models_reported"] for row in rows),
        "accepted_attempt_auxiliary_model_token_sums": {
            name: sum(row["usage"]["auxiliary_models"][name] for row in rows)
            for name in ("uncached_input_including_creation", "cache_read_input", "output")
        } if all(row["usage"]["auxiliary_models_reported"] for row in rows) else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-resamples", type=int, default=0)
    parser.add_argument("--bootstrap-seed", type=int, default=20260921)
    parser.add_argument("--output-name", default="claims60_story_reanalysis.json")
    args = parser.parse_args()
    require(args.bootstrap_resamples == 0 or args.bootstrap_resamples >= 100, "Use zero or at least 100 bootstrap resamples")
    require(Path(args.output_name).name == args.output_name, "Output must be a filename beside this script")
    output_path = SCRIPT.parent / args.output_name
    require(output_path != SCRIPT and output_path.suffix == ".json", "Output must be a JSON file")

    manifest = read_json(RUN / "manifest.json")
    roster = read_json(RUN / "claims60_ids.json")
    ids = sorted(roster)
    hints = set(manifest["claims60_hint_flagged_ids"])
    require(len(ids) == len(set(ids)) == 60, "Unexpected claims60 roster")
    require(set(ids) == set(manifest["claims60"]), "Manifest/roster population mismatch")
    require(len(hints) == 13 and hints <= set(ids), "Unexpected hint stratum")
    for record_id in ids:
        for directory, expected_key in (
            ("inputs_claims60", "input_sha256"),
            ("grading_truth_claims60", "truth_sha256"),
        ):
            path = RUN / directory / f"{record_id}.json"
            read_json(path)
            require(
                SOURCE_HASHES[str(path.relative_to(ROOT))] == manifest["claims60"][record_id][expected_key],
                f"Frozen hash mismatch: {path}",
            )
        require(bool(manifest["claims60"][record_id]["definitions_hint_flagged"]) == (record_id in hints), "Hint flag mismatch")

    results = {}
    for model in MODELS:
        historical = read_json(RUN / "summary" / f"claims60_{model}.json")
        cells = {}
        for record_id in ids:
            for arm in ARMS:
                filename = f"{record_id}__{arm}.json"
                usage = read_json(RUN / "usage/claims60" / model / filename)
                grade = read_json(RUN / "grades/claims60" / model / filename)
                assessment = read_json(RUN / "assessments/claims60" / model / filename)
                for record in (usage, grade, assessment):
                    require(record["record_id"] == record_id and record["arm"] == arm, "Cell identity mismatch")
                cells[record_id, arm] = {
                    "usage": bound_usage(model, usage),
                    "grade": grade["grade"],
                    "verdict": assessment["verdict"],
                    "counterexample_empty": not (assessment.get("counterexample") or "").strip(),
                }

        all_arms = {arm: aggregate(cells, ids, arm) for arm in ARMS}
        for arm, result in all_arms.items():
            saved = historical["arms"][arm]
            require(result["grader_supported_refutations"] == saved["catch_strict"], "Historical strict count not reproduced")
            require(result["accepted_attempt_token_sums"]["bound_model_output"] == saved["output_sum"], "Historical output sum not reproduced")
            require(result["verdict_counts"] == saved["verdicts"], "Historical verdict count not reproduced")

        comparisons = {}
        for comparator in ARMS[1:]:
            clean = {
                record_id for record_id in ids
                if not cells[record_id, "refute"]["usage"]["extra_exec_count"]
                and not cells[record_id, comparator]["usage"]["extra_exec_count"]
            }
            strata = {
                "all": set(ids),
                "no_hint": set(ids) - hints,
                "no_tool": clean,
                "no_hint_no_tool": (set(ids) - hints) & clean,
            }
            comparison = {}
            bootstrap_cache = {}
            for name, subset in strata.items():
                selected = sorted(subset)
                search = aggregate(cells, selected, "refute")
                review = aggregate(cells, selected, comparator)
                search_sums = search["accepted_attempt_token_sums"]
                review_sums = review["accepted_attempt_token_sums"]
                pairs = [(cells[r, "refute"]["usage"]["bound_model_full_tokens"], cells[r, comparator]["usage"]["bound_model_full_tokens"]) for r in selected]
                all_model_pairs = [(cells[r, "refute"]["usage"]["all_reported_models_full_tokens"], cells[r, comparator]["usage"]["all_reported_models_full_tokens"]) for r in selected]
                key = tuple(selected)
                if key not in bootstrap_cache:
                    bound_ci = full_bootstrap(pairs, args.bootstrap_resamples, args.bootstrap_seed)
                    all_ci = bound_ci if pairs == all_model_pairs else full_bootstrap(all_model_pairs, args.bootstrap_resamples, args.bootstrap_seed)
                    bootstrap_cache[key] = (bound_ci, all_ci)
                comparison[name] = {
                    "n_pairs": len(selected),
                    "record_ids": selected,
                    "search": search,
                    "comparator": review,
                    "frozen_bound_model_output_ratio_search_over_comparator": search_sums["bound_model_output"] / review_sums["bound_model_output"],
                    "all_reported_models_output_ratio_search_over_comparator": search_sums["all_reported_models_output"] / review_sums["all_reported_models_output"],
                    "corrected_bound_model_full_ratio_search_over_comparator": search_sums["bound_model_full_tokens"] / review_sums["bound_model_full_tokens"],
                    "all_reported_models_full_ratio_search_over_comparator": search_sums["all_reported_models_full_tokens"] / review_sums["all_reported_models_full_tokens"],
                    "historical_full_ratio_search_over_comparator": search_sums["historical_summary_full_tokens"] / review_sums["historical_summary_full_tokens"],
                    "new_exploratory_bound_model_full_ratio_ci95": bootstrap_cache[key][0],
                    "new_exploratory_all_reported_models_full_ratio_ci95": bootstrap_cache[key][1],
                }
            saved = historical["paired"][f"refute_vs_{comparator}"]
            require(math.isclose(comparison["all"]["frozen_bound_model_output_ratio_search_over_comparator"], saved["output_ratio_of_sums"], abs_tol=1e-12), "Historical paired output ratio not reproduced")
            require(math.isclose(comparison["all"]["historical_full_ratio_search_over_comparator"], saved["all_tokens_ratio_of_sums"], abs_tol=1e-12), "Historical full-token interpretation not reproduced")
            comparisons[comparator] = comparison

        results[model] = {
            "all_arm_summaries": all_arms,
            "comparisons": comparisons,
            "historical_attempt_accounting": {
                arm: historical["attempt_accounting"][arm] for arm in ARMS
            },
        }

    source_list = [{"path": path, "sha256": digest} for path, digest in sorted(SOURCE_HASHES.items())]
    payload = {
        "schema_version": 2,
        "purpose": "Read-only claims60 story audit of existing model judgments and accepted native usage",
        "accounting": {
            "sol": "usage_total.input_tokens + output_tokens_bound_model; cache is already within input",
            "gemini_corrected": "usage.input_tokens + usage.cache_read_tokens + output_tokens_bound_model; input is uncached",
            "gemini_historical_error": "Historical summaries subtracted cache from uncached input and then added it back, omitting cache from full totals",
            "opus_bound_model": "bound_model_usage inputTokens + cacheCreationInputTokens + cacheReadInputTokens + outputTokens",
            "opus_all_reported_models": "Sum the same four components over EVERY modelUsage entry, including Haiku auxiliary usage; bound-model fields remain separate",
            "sol_gemini_all_reported_models": "Native aggregate only; no auxiliary-model split is available or inferred",
            "frozen_output_endpoint": "Original configured-solver/bound-model output; adding auxiliary output is a separate sensitivity and never replaces the frozen comparison",
            "reasoning": "Included once within output; never added separately",
            "endpoint": "Accepted solver attempts only; additional attempts, grading and monetary pricing excluded",
        },
        "grade_scope": "Reference-assisted Astra CAUGHT_MATCHING/CAUGHT_DIFFERENT judgments; may credit complete arguments or named reference objects; not independently executed witnesses",
        "population": {
            "claims": len(ids), "hint_flagged": len(hints),
            "hint_rule": manifest["claims60_hint_flag_rule"],
            "hint_flagged_ids": sorted(hints),
            "frozen_input_and_reference_hashes_verified": 120,
        },
        "bootstrap": {
            "resamples": args.bootstrap_resamples,
            "seed": args.bootstrap_seed,
            "algorithm": "Sorted paired IDs; Python random.Random(seed) reset per comparison/stratum; n draws with replacement; ratio of sums; sorted indices int(.025*B) and int(.975*B)-1",
            "scope": "Optional new exploratory pointwise intervals, not preregistered or multiplicity adjusted; no-tool exclusions depend on post-treatment behavior",
        },
        "historical_counts_and_output_ratios_reproduced": True,
        "results": results,
        "provenance": {
            "script": str(SCRIPT.relative_to(ROOT)),
            "script_sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
            "sources_count": len(source_list),
            "source_hash_list_sha256": hashlib.sha256(json.dumps(source_list, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "sources": source_list,
        },
    }
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    output_path.write_bytes(data)
    print(json.dumps({"output": str(output_path.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest(), "source_files": len(source_list), "bootstrap_resamples": args.bootstrap_resamples}))


if __name__ == "__main__":
    main()
