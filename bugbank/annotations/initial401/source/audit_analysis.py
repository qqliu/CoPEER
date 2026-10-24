#!/usr/bin/env python3
"""Describe the frozen 487 -> 449 -> 401 audit population without new grading.

Run from any directory:
    python3 /path/to/audit_analysis.py

Only this script's results/audit_analysis.json is written. All source artifacts
are read by exact manifest ID; similarly named expansion/raw-output files are
not included. The output is deterministic and includes every consumed file's
SHA-256. No model calls, searches, semantic classifications, or hypothesis tests
are performed. Source-unit and duplicate-text definitions appear in the output.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re


if not __debug__:
    raise RuntimeError('Audit provenance validation requires assertions; run Python without -O.')


PASS = {"PASS_CORROBORATED", "PASS_ADJUDICATED", "PASS_UNCORROBORATED"}
STAGES = {
    "search": ("searches", "outcome", "WITNESS_FOUND"),
    "witness": ("witness_checks", "verdict", "CONFIRMED"),
    "lean": ("lean_match", "verdict", "MATCHES"),
}
SCRIPT = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT.parents[3]
OUTPUT_REL = Path(
    "qedbench_certificate_availability_triage/analysis/"
    "counterexample_structure_20260910/results/audit_analysis.json"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rate(numerator: int, denominator: int) -> dict:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "proportion": numerator / denominator if denominator else None,
    }


def fraction_value(value: Fraction | None) -> dict | None:
    if value is None:
        return None
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "value": float(value),
    }


def normalized(text: str) -> str:
    """Collapse Unicode whitespace only, preserving case/punctuation/math."""
    return re.sub(r"\s+", " ", text).strip()


def artifact_record_id(record: str) -> str:
    """The ten legacy Graph Theory records use spaces inside JSON IDs."""
    return record.replace("Graph Theory", "Graph_Theory")


def source_unit(record: str) -> tuple[str, str, str]:
    """Return family, canonical source-unit ID, and the explicit rule used."""
    m = re.fullmatch(r"(Algorithms_\d+|Graph_Theory_\d+)__.+", record)
    if m:
        return "QEDBench", "qedbench:" + m[1], "qedbench_problem_prefix"
    m = re.fullmatch(r"SE_([a-z]+)_(\d+)__(?:q|a\d+)", record)
    if m:
        return "StackExchange", f"stackexchange:{m[1]}:{m[2]}", "se_question_id"
    m = re.fullmatch(r"mse_(\d+)__ans\d+", record)
    if m:
        return "StackExchange", f"stackexchange:math:{m[1]}", "mse_question_id"
    m = re.fullmatch(r"reddit_.+_([a-z0-9]+)", record)
    if m:
        return "Reddit", "reddit:" + m[1], "reddit_global_post_id"
    m = re.fullmatch(r"proofwiki_(\d+)(?:__codex_expansion)?", record)
    if m:
        return "ProofWiki", "proofwiki:" + m[1], "proofwiki_numeric_source_id"
    m = re.fullmatch(
        r"arxiv_(\d{4}\.\d{4,5}|math_\d{7})v\d+__source_enriched(?:_codex)?",
        record,
    )
    if m:
        return "arXiv", "arxiv:" + m[1].replace("math_", "math/"), "arxiv_id_without_version"
    raise ValueError(f"No explicit source-unit rule for {record!r}")


def records_by_id(manifest: dict) -> dict:
    rows = manifest["records"]
    result = {r["record"]: r for r in rows}
    assert len(result) == len(rows), "Duplicate record IDs in manifest"
    return result


def boolean_table(ids: list[str], left: dict, right: dict, left_label: str, right_label: str) -> dict:
    """Missing is excluded from the 2x2 table and reported explicitly."""
    counts = {"true_true": 0, "true_false": 0, "false_true": 0, "false_false": 0}
    missing = []
    cells = defaultdict(list)
    for stem in ids:
        a, b = left.get(stem), right.get(stem)
        if a is None or b is None:
            missing.append(stem)
            continue
        key = f"{str(a).lower()}_{str(b).lower()}"
        counts[key] += 1
        cells[key].append(stem)
    assert sum(counts.values()) + len(missing) == len(ids)
    return {
        "left_true_definition": left_label,
        "right_true_definition": right_label,
        "frame_records": len(ids),
        "complete_pairs": sum(counts.values()),
        "counts": counts,
        "cell_record_ids": dict(sorted(cells.items())),
        "excluded_missing_record_ids": missing,
    }


def categorical_table(ids: list[str], left: dict, right: dict) -> list[dict]:
    counts = Counter((left.get(i, "MISSING"), right.get(i, "MISSING")) for i in ids)
    return [{"left": a, "right": b, "records": n} for (a, b), n in sorted(counts.items())]


def compare_reference_groups(ids: list[str], reference: dict, replication: dict) -> dict:
    """Contrast stored gate outcomes, not latent mathematical correctness."""
    groups = {}
    for status in sorted(PASS):
        members = [i for i in ids if reference[i]["status"] == status]
        held = [i for i in members if replication[i]["status"] not in PASS]
        groups[status] = {
            "replication_held_out": rate(len(held), len(members)),
            "replication_status_counts": dict(sorted(Counter(replication[i]["status"] for i in members).items())),
            "held_out_record_ids": held,
        }
    adj = groups["PASS_ADJUDICATED"]["replication_held_out"]
    cor = groups["PASS_CORROBORATED"]["replication_held_out"]
    pa = Fraction(adj["numerator"], adj["denominator"]) if adj["denominator"] else None
    pc = Fraction(cor["numerator"], cor["denominator"]) if cor["denominator"] else None
    if pa is None or pc is None:
        direction = "not_comparable_empty_group"
    elif pa == pc:
        direction = "equal"
    else:
        direction = "adjudicated_higher" if pa > pc else "adjudicated_lower"
    return {
        "records": len(ids),
        "by_reference_status": groups,
        "adjudicated_minus_corroborated_held_out_rate": fraction_value(pa - pc) if pa is not None and pc is not None else None,
        "adjudicated_over_corroborated_held_out_rate": fraction_value(pa / pc) if pa is not None and pc else None,
        "ratio_undefined_reason": "corroborated_rate_zero_or_group_empty" if pa is None or not pc else None,
        "direction": direction,
    }


def stratified_comparison(ids: list[str], labels: dict, reference: dict, replication: dict) -> dict:
    groups = defaultdict(list)
    for i in ids:
        groups[labels[i]].append(i)
    strata = {label: compare_reference_groups(sorted(group), reference, replication) for label, group in sorted(groups.items())}
    comparable = []
    for label, row in strata.items():
        by = row["by_reference_status"]
        adj, cor = [by[x]["replication_held_out"] for x in ("PASS_ADJUDICATED", "PASS_CORROBORATED")]
        if adj["denominator"] and cor["denominator"]:
            comparable.append((label, adj, cor))
    weight_n = sum(a["denominator"] + c["denominator"] for _, a, c in comparable)
    adj_standardized = Fraction(0)
    cor_standardized = Fraction(0)
    weights = []
    for label, adj, cor in comparable:
        n = adj["denominator"] + cor["denominator"]
        weight = Fraction(n, weight_n)
        adj_standardized += weight * Fraction(adj["numerator"], adj["denominator"])
        cor_standardized += weight * Fraction(cor["numerator"], cor["denominator"])
        weights.append({"stratum": label, "weight": rate(n, weight_n)})
    return {
        "strata": strata,
        "direction_counts": dict(sorted(Counter(row["direction"] for row in strata.values()).items())),
        "descriptive_common_composition_standardization": {
            "definition": "Within strata having both reference groups, use the pooled adjudicated+corroborated stratum record fractions as the same weights for each group's held-out rate. PASS_UNCORROBORATED records are excluded from these weights. This arithmetic reweighting is descriptive and is not a causal adjustment or error-rate estimate.",
            "weight_frame_records": weight_n,
            "weights": weights,
            "adjudicated_held_out_rate": fraction_value(adj_standardized) if weight_n else None,
            "corroborated_held_out_rate": fraction_value(cor_standardized) if weight_n else None,
            "rate_difference": fraction_value(adj_standardized - cor_standardized) if weight_n else None,
            "rate_ratio": fraction_value(adj_standardized / cor_standardized) if cor_standardized else None,
        },
    }


def duplicate_summary(ids: list[str], values: dict) -> dict:
    groups = defaultdict(list)
    missing = []
    for stem in ids:
        value = values.get(stem)
        if not value:
            missing.append(stem)
        else:
            groups[value].append(stem)
    duplicates = sorted((sorted(v) for v in groups.values() if len(v) > 1), key=lambda v: (-len(v), v))
    return {
        "records": len(ids),
        "nonempty_records": len(ids) - len(missing),
        "unique_values": len(groups),
        "duplicate_groups": len(duplicates),
        "records_in_duplicate_groups": sum(map(len, duplicates)),
        "excess_rows_over_unique_values": sum(len(x) - 1 for x in duplicates),
        "largest_group_records": max(map(len, groups.values()), default=0),
        "duplicate_group_record_ids": duplicates,
        "missing_record_ids": missing,
    }


def analyze(repo_root: Path) -> dict:
    consumed = {}

    def read(rel: str | Path) -> dict:
        rel = Path(rel)
        raw = (repo_root / rel).read_bytes()
        consumed[rel.as_posix()] = {"path": rel.as_posix(), "bytes": len(raw), "sha256": sha(raw)}
        return json.loads(raw)

    base = Path("qedbench_certificate_availability_triage/validation")
    ref_manifest = read(base / "validated_manifest.json")
    cod_manifest = read(base / "codex_run/validated_manifest.json")
    ref_ledger = read(base / "findings_ledger.json")
    cod_ledger = read(base / "codex_run/findings_ledger.json")
    reference = records_by_id(ref_manifest)
    replication = records_by_id(cod_manifest)
    original_ids = sorted(reference)
    replication_ids = sorted(replication)
    release_ids = sorted(i for i in replication_ids if replication[i]["status"] in PASS)
    assert (len(original_ids), len(replication_ids), len(release_ids)) == (487, 449, 401)
    assert set(replication_ids) == {i for i in original_ids if reference[i]["status"] in PASS}
    assert set(release_ids) == set(cod_manifest["validated_stems"])
    assert cod_manifest["complete"] and not any(cod_manifest["completion_blockers"].values())
    assert all(reference[i]["corpus"] == replication[i]["corpus"] for i in replication_ids)

    inputs = {}
    byte_identical = []
    for stem in original_ids:
        ref_path = base / "machine_checks/inputs_full" / (stem + ".json")
        inputs[stem] = read(ref_path)
        assert artifact_record_id(inputs[stem]["record_id"]) == stem
        assert sha(inputs[stem]["problem"].encode()) == reference[stem]["problem_sha256"]
        if stem in replication:
            cod_path = base / "codex_run/inputs_full" / (stem + ".json")
            cod_input = read(cod_path)
            assert cod_input == inputs[stem]
            assert consumed[ref_path.as_posix()]["sha256"] == consumed[cod_path.as_posix()]["sha256"]
            byte_identical.append(stem)

    stages = {}
    expected_frame = {"reference": original_ids, "replication": replication_ids}
    for campaign, ids in expected_frame.items():
        stage_root = base / ("machine_checks" if campaign == "reference" else "codex_run")
        stage_data = {stage: {} for stage in STAGES}
        for stage, (folder, field, _) in STAGES.items():
            for stem in ids:
                path = stage_root / folder / (stem + ".json")
                if not (repo_root / path).exists():
                    assert campaign == "reference" and stage == "search" and stem == "Algorithms_38__sol5"
                    continue
                obj = read(path)
                assert artifact_record_id(obj["record_id"]) == stem
                stage_data[stage][stem] = obj[field]
                if campaign == "replication":
                    manifest_field = {"search": "search_outcome", "witness": "witness_verdict", "lean": "lean_verdict"}[stage]
                    assert obj[field] == replication[stem][manifest_field]
        stages[campaign] = stage_data
        ledger = ref_ledger if campaign == "reference" else cod_ledger
        assert all(dict(Counter(stage_data[s].values())) == ledger["counts"][s] for s in STAGES)

    good = {
        campaign: {stage: {i: verdict == STAGES[stage][2] for i, verdict in outcomes.items()} for stage, outcomes in data.items()}
        for campaign, data in stages.items()
    }
    within_campaign = {}
    for campaign, ids in expected_frame.items():
        within_campaign[campaign] = {
            "frame_records": len(ids),
            "stage_outcome_counts": {s: dict(sorted(Counter(stages[campaign][s].values()).items())) for s in STAGES},
            "coverage": {s: len(stages[campaign][s]) for s in STAGES},
            "missing_record_ids": {s: sorted(set(ids) - set(stages[campaign][s])) for s in STAGES},
            "pairwise_2x2": {
                f"{left}_vs_{right}": boolean_table(ids, good[campaign][left], good[campaign][right], f"{left} == {STAGES[left][2]}", f"{right} == {STAGES[right][2]}")
                for left, right in combinations(STAGES, 2)
            },
            "all_three_strict_positive_record_ids": [i for i in ids if all(good[campaign][s].get(i) is True for s in STAGES)],
            "strict_positive_definition": "WITNESS_FOUND + CONFIRMED + MATCHES. This is a raw-primary-stage conjunction, not the ledger's clean count or a final admission rule.",
        }

    cross_campaign = {}
    for stage in STAGES:
        cross_campaign[stage] = {
            "binary_2x2": boolean_table(replication_ids, good["reference"][stage], good["replication"][stage], f"reference {stage} == {STAGES[stage][2]}", f"replication {stage} == {STAGES[stage][2]}"),
            "all_outcomes": categorical_table(replication_ids, stages["reference"][stage], stages["replication"][stage]),
        }

    held_ids = sorted(set(replication_ids) - set(release_ids))
    gate_boolean = {i: i in release_ids for i in replication_ids}
    arithmetic_gate = boolean_table(replication_ids, good["replication"]["witness"], gate_boolean, "replication witness == CONFIRMED", "replication status is one of the three PASS statuses")
    held_confirmed = [i for i in held_ids if good["replication"]["witness"][i]]

    families, units, rules = {}, {}, {}
    for stem in original_ids:
        families[stem], units[stem], rules[stem] = source_unit(stem)
    corpus_labels = {i: reference[i]["corpus"] for i in original_ids}
    frame_sets = {"original_certified_487": original_ids, "reference_admitted_449": replication_ids, "final_release_401": release_ids}
    counts_by_corpus = {}
    for corpus in sorted(set(corpus_labels.values())):
        original = [i for i in original_ids if corpus_labels[i] == corpus]
        handoff = [i for i in original if i in replication]
        release = [i for i in handoff if i in release_ids]
        counts_by_corpus[corpus] = {
            "original_certified_records": len(original),
            "reference_admitted_records": len(handoff),
            "reference_held_out": rate(len(original) - len(handoff), len(original)),
            "final_released_records": len(release),
            "replication_held_out": rate(len(handoff) - len(release), len(handoff)),
            "total_held_out": rate(len(original) - len(release), len(original)),
            "original_source_units": len({units[i] for i in original}),
            "released_source_units": len({units[i] for i in release}),
        }

    duplicate_fields = {
        "canonical_source_unit": units,
        "problem_text_exact": {i: inputs[i]["problem"] for i in original_ids},
        "problem_text_whitespace_normalized": {i: normalized(inputs[i]["problem"]) for i in original_ids},
        "claim_quote_exact": {i: inputs[i]["claim_quote"] for i in original_ids},
        "claim_quote_whitespace_normalized": {i: normalized(inputs[i]["claim_quote"]) for i in original_ids},
        "source_unit_and_claim_whitespace_normalized": {i: units[i] + "\0" + normalized(inputs[i]["claim_quote"]) for i in original_ids},
        "witness_text_exact": {i: inputs[i]["witness"] for i in original_ids},
        "witness_text_whitespace_normalized": {i: normalized(inputs[i]["witness"]) for i in original_ids},
        "manifest_certificate_sha256": {i: reference[i]["lean_sha256"] for i in original_ids},
    }
    duplicates = {frame: {field: duplicate_summary(ids, values) for field, values in duplicate_fields.items()} for frame, ids in frame_sets.items()}

    lineage = []
    for stem in original_ids:
        cod = replication.get(stem)
        lineage.append({
            "record_id": stem,
            "raw_input_record_id": inputs[stem]["record_id"],
            "corpus": corpus_labels[stem],
            "source_family": families[stem],
            "source_unit": units[stem],
            "source_unit_rule": rules[stem],
            "reference_status": reference[stem]["status"],
            "replication_status": cod["status"] if cod else "NOT_IN_REFERENCE_HANDOFF",
            "released": stem in release_ids,
            "reference_stages": {s: stages["reference"][s].get(stem, "MISSING") for s in STAGES},
            "replication_stages": {s: stages["replication"][s].get(stem, "NOT_IN_REFERENCE_HANDOFF") for s in STAGES},
            "reference_problem_sha256": reference[stem]["problem_sha256"],
            "reference_certificate_sha256": reference[stem]["lean_sha256"],
            "reference_full_input_path": (base / "machine_checks/inputs_full" / (stem + ".json")).as_posix(),
        })

    provenance = [consumed[k] for k in sorted(consumed)]
    provenance_bytes = json.dumps(provenance, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "schema_version": 1,
        "analysis": "counterexample_structure_20260910_audit_and_identity",
        "scope": "Existing frozen audit outcomes and exact artifact identities; no new mathematical or semantic adjudication.",
        "provenance": {
            "script_path": SCRIPT.relative_to(repo_root).as_posix(),
            "script_sha256": sha(SCRIPT.read_bytes()),
            "consumed_files": len(provenance),
            "consumed_file_manifest_sha256": sha(provenance_bytes),
            "consumed_file_manifest_hash_encoding": "UTF-8 JSON of files list with sort_keys=True and separators=(',', ':').",
            "files": provenance,
        },
        "population": {
            "original_certified_records": len(original_ids),
            "reference_admitted_records": len(replication_ids),
            "reference_held_out_records": len(original_ids) - len(replication_ids),
            "final_release_records": len(release_ids),
            "replication_held_out_records": len(held_ids),
            "total_held_out_records": len(original_ids) - len(release_ids),
            "reference_status_counts": dict(sorted(Counter(r["status"] for r in reference.values()).items())),
            "replication_status_counts": dict(sorted(Counter(r["status"] for r in replication.values()).items())),
            "byte_identical_reference_replication_full_inputs": len(byte_identical),
            "reference_problem_text_hashes_recomputed_and_matched": len(original_ids),
            "reference_held_out_record_ids": sorted(set(original_ids) - set(replication_ids)),
            "replication_held_out_record_ids": held_ids,
        },
        "per_corpus_population": counts_by_corpus,
        "raw_primary_stage_analysis": {"within_campaign": within_campaign, "cross_campaign_on_449": cross_campaign},
        "reference_status_vs_replication_status": categorical_table(replication_ids, {i: reference[i]["status"] for i in replication_ids}, {i: replication[i]["status"] for i in replication_ids}),
        "later_holdout_by_reference_gate": {
            "pooled": compare_reference_groups(replication_ids, reference, replication),
            "within_original_corpus": stratified_comparison(replication_ids, corpus_labels, reference, replication),
            "within_source_family": stratified_comparison(replication_ids, families, reference, replication),
        },
        "witness_confirmation_and_final_gate": {
            "table": arithmetic_gate,
            "witness_confirmed_among_replication_held_out": rate(len(held_confirmed), len(held_ids)),
            "witness_confirmed_among_release": rate(sum(good["replication"]["witness"][i] for i in release_ids), len(release_ids)),
            "confirmed_but_held_out_record_ids": held_confirmed,
            "held_out_reason_lists": {i: replication[i]["reasons"] for i in held_ids},
        },
        "source_grouping_rules": {
            "artifact_id_alias": "Within file contents only, replace the legacy literal 'Graph Theory' with 'Graph_Theory' before validating against the exact manifest/file stem. No other record-ID aliases are admitted.",
            "unit_definition": "A benchmark problem, Stack Exchange question, Reddit post, ProofWiki numeric source record, or version-stripped arXiv paper identifier. These heterogeneous source units are grouping proxies, not certified distinct mathematical problems or independent observations.",
            "qedbench_problem_prefix": "Keep Algorithms_N or Graph_Theory_N before __, merging all solution IDs including legacy suffixes.",
            "se_question_id": "SE_SITE_QUESTION__(q|aANSWER) -> stackexchange:SITE:QUESTION.",
            "mse_question_id": "mse_QUESTION__ansANSWER -> stackexchange:math:QUESTION, sharing the same namespace as SE_math.",
            "reddit_global_post_id": "reddit_SUBREDDIT_POSTID -> reddit:POSTID; subreddit is omitted because Reddit post IDs are global identifiers.",
            "proofwiki_numeric_source_id": "Remove proofwiki_ prefix and optional __codex_expansion suffix; retain the numeric ID.",
            "arxiv_id_without_version": "Strip version and import suffix; legacy math_NNNNNNN becomes math/NNNNNNN.",
            "unknown_record_rule": "Fail with an error; do not silently assign singleton IDs.",
        },
        "source_and_text_identity": {
            "interpretation": "Text equality or file reuse does not establish mathematical equivalence; text inequality does not establish mathematical novelty or independent counterexamples. Certificate hashes are the frozen manifest's stored hashes, not a fresh recompilation or on-disk certificate audit.",
            "normalization": "re.sub(r'\\s+', ' ', text).strip(); case, punctuation, Unicode math symbols and all non-whitespace characters are preserved.",
            "by_frame": duplicates,
            "source_family_counts_by_frame": {frame: {family: {"records": sum(families[i] == family for i in ids), "source_units": len({units[i] for i in ids if families[i] == family})} for family in sorted(set(families.values()))} for frame, ids in frame_sets.items()},
        },
        "record_lineage": lineage,
        "limitations": [
            "All 487 original records were already selected for certificate availability; the analysis estimates no detection recall or false-refutation prevalence in unselected proofs.",
            "The 449-record replication frame is conditional on the reference gate; the two campaigns are not independent random samples from the 487 records.",
            "Reference-adjudicated status is a prior response to disagreements, not a randomized treatment. Its association with later holdout may reflect claim difficulty, modeling choices, provenance, and different gate strictness.",
            "Replication holdout combines NEEDS_REPAIR and FAIL, including missing source provenance and incompatible adjudication labels; it is not equivalent to a mathematically false witness.",
            "Witness CONFIRMED is the existing isolated auditor's verdict. This analysis reruns no witness checker or Lean compilation and does not elevate its trust tier.",
            "PARTIAL and MISMATCH are both non-MATCHES in binary tables; all original outcome categories are retained in accompanying categorical tables.",
            "Historical 38/38 QEDBench blind rediscovery is separate from final release admission. The core source population is 38 originally, 37 in the handoff, and 31 finally released.",
            "Repeated source problems, reused certificates, related obstruction families and model-family audit errors can create dependence; no confidence intervals, p-values or causal claims are reported.",
            "The quarantined already-published-counterexample stratum remains included with its original label; neither all-401 counts nor distinct strings establish novelty.",
            "Raw and whitespace-normalized text identity are deliberately syntactic. No keyword-based semantic taxonomy, graph isomorphism, or proof-equivalence judgment is inferred.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    result = analyze(root)
    output = root / OUTPUT_REL
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    comparison = result["later_holdout_by_reference_gate"]["pooled"]
    print(json.dumps({
        "output": output.relative_to(root).as_posix(),
        "population": [487, 449, 401],
        "heldout_ratio_adjudicated_over_corroborated": comparison["adjudicated_over_corroborated_held_out_rate"],
        "within_corpus_directions": result["later_holdout_by_reference_gate"]["within_original_corpus"]["direction_counts"],
        "confirmed_among_held": result["witness_confirmation_and_final_gate"]["witness_confirmed_among_replication_held_out"],
    }, indent=2))


if __name__ == "__main__":
    main()
