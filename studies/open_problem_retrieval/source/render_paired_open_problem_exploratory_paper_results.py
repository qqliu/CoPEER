#!/usr/bin/env python3
"""Render the separately reported six-target exploratory paired result.

Publication is deliberately fail closed.  The renderer accepts only the exact
pre-registered six-record roster, a currently valid runtime seal, an exact
VALID_COMPLETE independent-validator report, and six mutually consistent
pair terminals.  It never reads or writes the confirmatory renderer's output
namespace, and it never combines this cohort with the frozen 58 observations.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import paired_open_problem_exploratory_runtime_r3_seal as seal_checker
import render_paired_open_problem_paper_results as common


REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "qedbench_certificate_availability_triage"
RUNS = BASE / "runs"
SCRIPTS = BASE / "scripts"
EXPLORATORY_STUDY_ID = "EXPLORATORY_UNBIASED_V2"
DEFAULT_RUN = RUNS / "open_frontier_paired_exploratory_unbiased_v2r3_20260904"
DEFAULT_VALIDATOR = (
    SCRIPTS / "validate_paired_open_problem_exploratory_runtime_r3_run.py"
)
DEFAULT_OUTPUT_DIRECTORY = REPO / "paper_v2" / "generated"
OUTPUT_NAMES = {
    "json": "paired_open_problem_exploratory_results.json",
    "macros": "paired_open_problem_exploratory_macros.tex",
    "rows": "paired_open_problem_exploratory_rows.tex",
}
CONFIRMATORY_OUTPUT_NAMES = frozenset(common.OUTPUT_NAMES.values())
REPORT_SCHEMA = "paired_open_problem_exploratory_validation_report_v1"
TERMINAL_SCHEMA = "paired_open_problem_pair_terminal_v1"
MANIFEST_SCHEMA = "paired_open_problem_exploratory_run_manifest_v1"
SEAL_SCHEMA = "paired_open_problem_exploratory_runtime_seal_v1"
REPORTING_CLASS = "SEPARATE_EXPLORATORY_COHORT"
POOL_REPORTING_CLASS = "exploratory_external_fresh"
PROTOCOL_ID = "WHOLE_PROOF_FIRST_SOLUTION_V1"
PREREGISTRATION_SCHEMA = "qedbench.paired_open_problem_exploratory_preregistration.v2"
CANDIDATE_POOL_SCHEMA = "qedbench.exploratory_curation.v2"
SELECTION_REPORT_SCHEMA = "qedbench.paired_open_problem_exploratory_selection.v2"
SELECTION_SEED_PREFIX = "qedbench-exploratory-extension-v1|"
EXPECTED_ELIGIBLE_COUNT = 18
EXPECTED_EXCLUDED_COUNT = 15
EXPECTED_ELIGIBLE_KEY_LIST_SHA256 = (
    "7298228a7b91661bcff38ec9efd71e6015a8fb3da3be69d9c2c7bb1a7af530b9"
)
EXPECTED_EXCLUDED_KEY_LIST_SHA256 = (
    "dcd78b631ac3c113745cd57275842682d9f550d9d23710a31d30941baf2687ba"
)
EXPECTED_SELECTED_KEY_LIST_SHA256 = (
    "c4d8c85c00175523612e85bc477e4963803c47f685b8bad3e0afb57d818ecdde"
)
V2_SOURCE_PACKAGE = (
    "qedbench_certificate_availability_triage/"
    "paired_open_problem_exploratory_sources_v2"
)
V2_CANDIDATE_POOL_PATH = (
    "qedbench_certificate_availability_triage/"
    "paired_open_problem_exploratory_v2/CANDIDATE_POOL.json"
)
V2_SOURCE_CONTEXT_PATH = (
    "qedbench_certificate_availability_triage/"
    "paired_open_problem_exploratory_v2/SELECTED_SOURCE_CONTEXT.md"
)
V2_RUN_ROOT = (
    "qedbench_certificate_availability_triage/runs/"
    "open_frontier_paired_exploratory_unbiased_v2_20260904"
)
V2_OPERATIONS_ROOT = "<workspace-home>/paired_exploratory_unbiased_v2_ops"
V2_SCRATCH_ROOT = "<workspace-home>/paired_exploratory_unbiased_v2_scratch"
REPLACEMENT_RUN_ROOT = (
    "qedbench_certificate_availability_triage/runs/"
    "open_frontier_paired_exploratory_unbiased_v2r3_20260904"
)
REPLACEMENT_OPERATIONS_ROOT = (
    "<workspace-home>/paired_exploratory_unbiased_v2r3_ops"
)
REPLACEMENT_SCRATCH_ROOT = (
    "<workspace-home>/paired_exploratory_unbiased_v2r3_scratch"
)
SUPERSEDED_V1_PREREGISTRATION_PATH = (
    "qedbench_certificate_availability_triage/"
    "paired_open_problem_exploratory_v1/PREREGISTRATION.json"
)
SUPERSEDED_V1_PREREGISTRATION_SHA256 = (
    "d0ffc50fe3f58acca04ca79cd93e84fcabb12875de04cdab21d6a7d837ed4360"
)
SUPERSEDED_V1_CANDIDATE_POOL_PATH = (
    "qedbench_certificate_availability_triage/"
    "paired_open_problem_exploratory_v1/CANDIDATE_POOL.json"
)
SUPERSEDED_V1_CANDIDATE_POOL_SHA256 = (
    "11012c8cf21b786fec05d6cf667b5666bec02aa6d913e1f927e3ebbf751feac3"
)
PROBLEM_4_1_KEY = "arxiv:2511.02892v1#Problem 4.1"
PROBLEM_4_1_RESOLUTION_SOURCE_ID = "problem_4_1_resolution_2026"
PROBLEM_4_1_RESOLUTION_SHA256 = (
    "dc53bc787e12e070f3ed9509bb90540c308c629fec647caae5c422e708320771"
)
EXPECTED_POOL_SOURCE_SNAPSHOTS = {
    "cycles_colouring_33": {
        "source_path": (
            f"{V2_SOURCE_PACKAGE}/sources/arxiv_2511_02892v1/source.pdf"
        ),
        "sha256": "94a74974a31f40e9f079cc8fad4b6272dd245c739fbe9e92eb72746749fdf542",
        "size_bytes": 132766,
    },
    "dagstuhl_25041": {
        "source_path": f"{V2_SOURCE_PACKAGE}/sources/dagstuhl_25041/source.pdf",
        "sha256": "71960df908ed679d720ae4ba59ea7f415c06c2982be59bc9f6bb906ff08c3e2d",
        "size_bytes": 2528849,
    },
    "problem_4_1_resolution_2026": {
        "source_path": (
            f"{V2_SOURCE_PACKAGE}/sources/arxiv_2607_23462v1/source.pdf"
        ),
        "sha256": PROBLEM_4_1_RESOLUTION_SHA256,
        "size_bytes": 450471,
    },
    "randomstrasse_2025": {
        "source_path": (
            f"{V2_SOURCE_PACKAGE}/sources/arxiv_2603_29571v1/source.pdf"
        ),
        "sha256": "cd4e929a83143f9157283d2d9de7e6a99bca40f57e16d62a9b1f3ba33070801c",
        "size_bytes": 578998,
    },
}
FROZEN_CONFIRMATORY_PROTOCOL_OBSERVATION_COUNT = 58
FROZEN_CONFIRMATORY_DISTINCT_TARGET_COUNT = 36
FROZEN_CONFIRMATORY_CONTINUATION_OBSERVATION_COUNT = 22
EXPECTED_ROSTER_RELATIONSHIPS = {
    "original31_hard5_disjoint": True,
    "extension22_exact_subset_of_original31": True,
    "extension22_hard5_disjoint": True,
}
PREREGISTRATION_FILENAMES = frozenset({
    "PREREGISTRATION.json",
    "CANDIDATE_POOL.json",
    "SELECTION_REPORT.json",
    "CONFIRMATORY_BOUNDARY_SEAL.json",
    "RUNTIME_CORRECTION_AMENDMENT_20260904.json",
    "RUNTIME_PREFLIGHT_CORRECTION_AMENDMENT_20260904.json",
    "SELECTED_SOURCE_CONTEXT.md",
})
JSON_PREREGISTRATION_FILENAMES = PREREGISTRATION_FILENAMES - {
    "SELECTED_SOURCE_CONTEXT.md"
}
EXPECTED_RECORDS = (
    (
        "explore_random_4regular_alon_tarsi",
        "arxiv:2511.02892v1#Problem 2.1",
        "03ac6d940093025bb7cdc1d12013f3e4a6a2f8775d3aa45df92bc1fcdd5db3ea",
    ),
    (
        "explore_mub6_lt7",
        "arxiv:2603.29571v1#Conjecture 22",
        "0edeba69586acf7df17b59f522cc63da3d96d4f849196eda8f5b10308f764d12",
    ),
    (
        "explore_paley_localization_theta",
        "arxiv:2603.29571v1#Conjecture 26",
        "1740875545b936998d9dc3a6f3ef6df3a209cf62e9a328ab71fb0fcc7ebe14ad",
    ),
    (
        "explore_random_graph_theta",
        "arxiv:2603.29571v1#Conjecture 17",
        "2859b6342d30c69d9526b871cb0109a69dbb0bcd80f1ad2e8e9c641711e4ee0c",
    ),
    (
        "explore_cubic_2homogeneous_four_colors",
        "arxiv:2511.02892v1#Problem 5.1",
        "354719a2559e7c071133f4b2674d9330152de5bfa62a1fb9bc872219e3de4abe",
    ),
    (
        "explore_paley_degree4_sos_improvement",
        "arxiv:2603.29571v1#Conjecture 28",
        "3be7fe81e7ae770e2f9281db6e8b0f9b09978c5b83b96b4ff57be42ac543878f",
    ),
)
EXPECTED_IDS = tuple(row[0] for row in EXPECTED_RECORDS)
EXPECTED_KEYS = tuple(row[1] for row in EXPECTED_RECORDS)
EXPECTED_SELECTION = tuple((row[1], row[2]) for row in EXPECTED_RECORDS)
CONTINUATION_NAME_RE = re.compile(
    r"^open_frontier_paired_exploratory_unbiased_v2_continuation_v"
    r"([1-9][0-9]*)_20260904$"
)


class RenderError(common.RenderError):
    """An exploratory input or output violates the publication contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RenderError(message)


def require_object(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is dict, f"{label} must be a JSON object")
    return value


def require_exact_keys(value: Mapping[str, Any], keys: set[str], label: str) -> None:
    actual = set(value)
    require(
        actual == keys,
        f"{label} field set mismatch: missing={sorted(keys - actual)}, "
        f"unexpected={sorted(actual - keys)}",
    )


def parse_payload(value: Mapping[str, Any], field: str, label: str) -> str:
    recorded = common.require_sha(value.get(field), f"{label}.{field}")
    unsigned = copy.deepcopy(dict(value))
    unsigned.pop(field, None)
    require(
        recorded == common.sha_bytes(common.canonical_bytes(unsigned)),
        f"{label} payload hash mismatch",
    )
    return recorded


def safe_relative_binding_path(run: Path, value: Any, label: str) -> Path:
    require(type(value) is str and bool(value), f"{label}.path is empty")
    relative = Path(value)
    require(not relative.is_absolute() and ".." not in relative.parts,
            f"{label}.path is unsafe")
    path = run / relative
    try:
        path.resolve().relative_to(run.resolve())
    except ValueError as error:
        raise RenderError(f"{label}.path escapes the run") from error
    return path


def validate_binding(
    run: Path, value: Any, snapshot: common.FileSnapshot, label: str,
) -> None:
    row = require_object(value, label)
    require_exact_keys(row, {"path", "sha256", "size_bytes"}, label)
    expected_path = safe_relative_binding_path(run, row["path"], label)
    require(expected_path.resolve() == snapshot.path.resolve(),
            f"{label} names the wrong file")
    require(common.require_sha(row["sha256"], f"{label}.sha256") == snapshot.sha256
            and common.require_count(row["size_bytes"], f"{label}.size_bytes")
            == snapshot.size,
            f"{label} does not bind exact bytes")


def load_strict_json(path: Path, label: str) -> tuple[dict[str, Any], common.FileSnapshot]:
    try:
        value, snapshot = common.load_json_snapshot(path)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    return require_object(value, label), snapshot


def validate_selection(
    preregistration: Mapping[str, Any],
    candidate_pool: Mapping[str, Any],
    selection_report: Mapping[str, Any],
    boundary: Mapping[str, Any],
    runtime_correction: Mapping[str, Any],
    preflight_correction: Mapping[str, Any],
    snapshots: Mapping[str, common.FileSnapshot],
) -> None:
    # Reuse the bootstrap's exact, versioned prerequisite validators.  This is
    # intentionally more restrictive than checking only the selected six: it
    # validates the corrected 18/15 pool, deterministic ranks and digests,
    # resolved-Problem-4.1 primary evidence, v1 preservation/never-launch
    # bindings, and the disjoint v2 execution namespaces.
    bootstrap = seal_checker.bootstrap_validator
    try:
        bootstrap.validate_preregistration(preregistration)
        bootstrap.validate_runtime_correction(runtime_correction)
        bootstrap.validate_preflight_correction(preflight_correction)
        candidate_selected = bootstrap.validate_candidate_pool(candidate_pool)
        selected_keys = bootstrap.validate_selection_report(
            selection_report,
            snapshots["CANDIDATE_POOL.json"].path,
            snapshots["SELECTED_SOURCE_CONTEXT.md"].path,
            candidate_selected,
            logical_candidate_path=V2_CANDIDATE_POOL_PATH,
            logical_source_context_path=V2_SOURCE_CONTEXT_PATH,
        )
    except (bootstrap.BootstrapError, OSError, ValueError, KeyError) as error:
        raise RenderError(f"invalid v2 exploratory prerequisite: {error}") from error
    require(selected_keys == list(EXPECTED_KEYS),
            "selection report differs from the frozen six-target draw")
    expected_v1 = {
        "study_id": "EXPLORATORY_UNBIASED_V1",
        "preregistration_path": SUPERSEDED_V1_PREREGISTRATION_PATH,
        "preregistration_sha256": SUPERSEDED_V1_PREREGISTRATION_SHA256,
        "candidate_pool_path": SUPERSEDED_V1_CANDIDATE_POOL_PATH,
        "candidate_pool_sha256": SUPERSEDED_V1_CANDIDATE_POOL_SHA256,
        "run_created": False,
        "solver_auditor_model_or_bugbank_calls": False,
    }
    paired_run = require_object(
        preregistration.get("paired_run"), "preregistration.paired_run"
    )
    require(
        preregistration.get("schema") == PREREGISTRATION_SCHEMA
        and preregistration.get("study_id") == EXPLORATORY_STUDY_ID
        and preregistration.get("reporting_class") == REPORTING_CLASS
        and preregistration.get("superseded_v1") == expected_v1,
        "exploratory preregistration is not the corrected v2 authority",
    )
    require(
        paired_run.get("protocol_id") == PROTOCOL_ID
        and paired_run.get("source_package") == V2_SOURCE_PACKAGE
        and paired_run.get("run_root") == V2_RUN_ROOT
        and paired_run.get("operations_root") == V2_OPERATIONS_ROOT
        and paired_run.get("scratch_root") == V2_SCRATCH_ROOT
        and paired_run.get("versioned_continuation_policy")
        == seal_checker.VERSIONED_CONTINUATION_POLICY,
        "exploratory preregistration does not bind the exact v2 namespaces",
    )
    eligible = candidate_pool.get("eligible")
    excluded = candidate_pool.get("excluded")
    digests = require_object(candidate_pool.get("digests"), "candidate pool.digests")
    require(
        candidate_pool.get("schema_version") == CANDIDATE_POOL_SCHEMA
        and candidate_pool.get("reporting_class") == POOL_REPORTING_CLASS
        and candidate_pool.get("never_pool_with_frozen_58") is True
        and candidate_pool.get("outcome_blind") is True
        and candidate_pool.get("solver_or_bugbank_access_before_freeze") is False
        and type(eligible) is list and len(eligible) == EXPECTED_ELIGIBLE_COUNT
        and type(excluded) is list and len(excluded) == EXPECTED_EXCLUDED_COUNT
        and digests.get("eligible_key_list_sha256")
        == EXPECTED_ELIGIBLE_KEY_LIST_SHA256
        and digests.get("excluded_key_list_sha256")
        == EXPECTED_EXCLUDED_KEY_LIST_SHA256
        and digests.get("selected_rank_order_key_list_sha256")
        == EXPECTED_SELECTED_KEY_LIST_SHA256,
        "candidate pool is not the corrected outcome-blind v2 18/15 pool",
    )
    resolved_rows = [
        row for row in excluded
        if type(row) is dict and row.get("canonical_key") == PROBLEM_4_1_KEY
    ]
    require(
        len(resolved_rows) == 1
        and resolved_rows[0].get("reason_code") == "RESOLVED_BEFORE_LAUNCH"
        and resolved_rows[0].get("current_status")
        == "resolved_negatively_before_v2_launch"
        and resolved_rows[0].get("later_primary_source_pdf_sha256")
        == PROBLEM_4_1_RESOLUTION_SHA256,
        "candidate pool lacks the corrected Problem 4.1 resolution evidence",
    )
    require(
        selection_report.get("schema") == SELECTION_REPORT_SCHEMA
        and selection_report.get("study_id") == EXPLORATORY_STUDY_ID
        and selection_report.get("reporting_class") == REPORTING_CLASS
        and selection_report.get("never_pool_with_frozen_58") is True
        and selection_report.get("outcome_blind") is True
        and selection_report.get(
            "solver_auditor_or_bugbank_access_before_freeze"
        ) is False
        and selection_report.get("selected_rank_order_key_list_sha256")
        == EXPECTED_SELECTED_KEY_LIST_SHA256,
        "selection report is not the corrected outcome-blind v2 draw",
    )

    require_exact_keys(
        boundary,
        {"schema", "status", "protocol_observation_count",
         "distinct_target_count", "continuation_observation_count",
         "roster_relationships", "target_rosters",
         "never_pool_with_frozen_58", "components"},
        "confirmatory boundary seal",
    )
    require(
        boundary["schema"] == "qedbench.confirmatory_boundary_seal.v2"
        and boundary["status"] == "VALID_COMPLETE"
        and boundary["protocol_observation_count"]
        == FROZEN_CONFIRMATORY_PROTOCOL_OBSERVATION_COUNT
        and boundary["distinct_target_count"]
        == FROZEN_CONFIRMATORY_DISTINCT_TARGET_COUNT
        and boundary["continuation_observation_count"]
        == FROZEN_CONFIRMATORY_CONTINUATION_OBSERVATION_COUNT
        and boundary["roster_relationships"] == EXPECTED_ROSTER_RELATIONSHIPS
        and boundary["never_pool_with_frozen_58"] is True,
        "confirmatory boundary seal is not the complete frozen 58-observation boundary",
    )
    target_rosters = require_object(
        boundary["target_rosters"], "confirmatory boundary target_rosters"
    )
    require_exact_keys(
        target_rosters,
        {"original31_target_ids", "hard5_target_ids",
         "extension22_continuation_target_ids", "distinct_target_ids"},
        "confirmatory boundary target_rosters",
    )
    original_ids = target_rosters["original31_target_ids"]
    hard_ids = target_rosters["hard5_target_ids"]
    extension_ids = target_rosters["extension22_continuation_target_ids"]
    distinct_ids = target_rosters["distinct_target_ids"]
    require(
        type(original_ids) is list
        and all(type(item) is str and item for item in original_ids)
        and original_ids == sorted(set(original_ids))
        and len(original_ids) == 31
        and type(hard_ids) is list
        and all(type(item) is str and item for item in hard_ids)
        and hard_ids == sorted(set(hard_ids))
        and len(hard_ids) == 5
        and type(extension_ids) is list
        and all(type(item) is str and item for item in extension_ids)
        and len(extension_ids) == 22
        and len(set(extension_ids)) == 22
        and type(distinct_ids) is list
        and all(type(item) is str and item for item in distinct_ids)
        and distinct_ids == sorted(set(distinct_ids))
        and len(distinct_ids) == 36
        and set(original_ids).isdisjoint(hard_ids)
        and set(extension_ids) < set(original_ids)
        and set(extension_ids).isdisjoint(hard_ids)
        and distinct_ids == sorted(set(original_ids) | set(hard_ids)),
        "confirmatory boundary target rosters are inconsistent",
    )
    components = boundary["components"]
    require(type(components) is list and len(components) == 3,
            "confirmatory boundary must contain exactly three components")
    expected_components = (
        ("original31", "open_frontier_paired_v2_20260901", 31,
         "open_frontier_paired_v2_validation_report_v1"),
        ("hard5", "open_frontier_paired_hard_v1_20260903", 5,
         "paired_open_problem_validation_report_v1"),
        ("extension22", "open_frontier_paired_v2_fixed_point_extension_v3_20260903", 22,
         "paired_open_problem_extension_validation_report_v1"),
    )
    observed_components: list[tuple[Any, ...]] = []
    for index, raw in enumerate(components):
        row = require_object(raw, f"confirmatory boundary component[{index}]")
        require_exact_keys(
            row,
            {"component_id", "run_id", "protocol_observation_count", "report_path",
             "report_schema", "report_sha256", "checkpoint_commit"},
            f"confirmatory boundary component[{index}]",
        )
        common.require_sha(row["report_sha256"], f"boundary component[{index}] hash")
        require(
            type(row["checkpoint_commit"]) is str
            and re.fullmatch(r"[0-9a-f]{40}", row["checkpoint_commit"]) is not None,
            f"boundary component[{index}] checkpoint is invalid",
        )
        observed_components.append((
            row["component_id"], row["run_id"],
            row["protocol_observation_count"],
            row["report_schema"],
        ))
    require(tuple(observed_components) == expected_components,
            "confirmatory boundary components changed")


def verify_sealed_authority(run: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the production bootstrap and runtime-seal replay without mutations."""
    try:
        manifest, _checked = seal_checker.validate_manifest(run)
        seal = seal_checker.check_seal(run)
    except (seal_checker.SealError, OSError, ValueError, KeyError) as error:
        raise RenderError(f"exploratory runtime seal is not currently valid: {error}") from error
    return manifest, seal


AuthorityVerifier = Callable[[Path], tuple[dict[str, Any], dict[str, Any]]]


def continuation_inventory(run: Path) -> tuple[str, ...]:
    """Inventory the complete preregistered continuation namespace.

    A VALID_COMPLETE base report proves that no cell met the continuation
    trigger.  Consequently the only valid lineage for this renderer is empty.
    If a future experiment needs a continuation, its separately sealed lineage
    must first receive an explicit publication adapter; silently ignoring it is
    forbidden.
    """
    try:
        entries = list(run.parent.iterdir())
    except OSError as error:
        raise RenderError(f"cannot inventory exploratory continuation lineage: {error}") from error
    names = sorted(entry.name for entry in entries if CONTINUATION_NAME_RE.fullmatch(entry.name))
    require(not names,
            "a continuation lineage exists but has no approved paper-renderer adapter")
    return tuple(names)


def validate_report(
    report: Mapping[str, Any], run: Path, validator: common.FileSnapshot,
) -> tuple[dict[str, dict[str, Any]], str]:
    require_exact_keys(
        report,
        {"schema", "run_id", "run_path", "generated_at", "validator", "status",
         "protocol_id", "counts", "closed_world", "records", "diagnostics",
         "report_payload_sha256"},
        "exploratory validation report",
    )
    require(report["schema"] == REPORT_SCHEMA,
            "exploratory validation report schema mismatch")
    require(report["status"] == "VALID_COMPLETE",
            "exploratory validation report is not VALID_COMPLETE")
    require(report["run_id"] == run.name and report["run_path"] == str(run.resolve()),
            "exploratory validation report run identity mismatch")
    require(report["protocol_id"] == PROTOCOL_ID,
            "exploratory validation report protocol mismatch")
    report_hash = parse_payload(report, "report_payload_sha256",
                                "exploratory validation report")
    validator_binding = require_object(report["validator"], "report.validator")
    require_exact_keys(validator_binding, {"path", "sha256"}, "report.validator")
    require(
        type(validator_binding["path"]) is str
        and Path(validator_binding["path"]).resolve() == validator.path.resolve()
        and common.require_sha(validator_binding["sha256"], "report validator hash")
        == validator.sha256,
        "exploratory report was not produced by the current validator bytes",
    )
    common.validate_diagnostics(report["diagnostics"], "exploratory report diagnostics")
    records = require_object(report["records"], "exploratory report.records")
    require(set(records) == set(EXPECTED_IDS),
            "exploratory report roster differs from the frozen six records")
    counts = require_object(report["counts"], "exploratory report.counts")
    require_exact_keys(
        counts, {"problems", "valid_pair_terminals", "arm_endpoints", "verified_full"},
        "exploratory report.counts",
    )
    require(
        common.require_count(counts["problems"], "report counts.problems", minimum=1)
        == len(EXPECTED_RECORDS)
        and common.require_count(
            counts["valid_pair_terminals"], "report counts.valid_pair_terminals"
        ) == len(EXPECTED_RECORDS),
        "exploratory report does not validate all six pair terminals",
    )
    endpoints = require_object(counts["arm_endpoints"], "report arm_endpoints")
    require(
        set(endpoints) == set(common.ARMS)
        and all(common.require_count(endpoints[arm], f"arm_endpoints.{arm}")
                == len(EXPECTED_RECORDS) for arm in common.ARMS),
        "exploratory report does not contain both endpoints for every record",
    )
    return dict(records), report_hash


def validate_manifest_and_seal(
    run: Path,
    manifest: Mapping[str, Any],
    seal: Mapping[str, Any],
    manifest_snapshot: common.FileSnapshot,
    seal_snapshot: common.FileSnapshot,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    require(
        manifest.get("schema") == MANIFEST_SCHEMA
        and manifest.get("run_id") == run.name
        and manifest.get("status") == "BOOTSTRAPPED_AWAITING_RUNTIME_SEAL"
        and manifest.get("launch_authorized") is False,
        "exploratory manifest identity/status changed",
    )
    parse_payload(manifest, "manifest_payload_sha256", "exploratory manifest")
    require(
        manifest.get("problem_count") == len(EXPECTED_RECORDS)
        and manifest.get("problem_ids") == list(EXPECTED_IDS),
        "exploratory manifest record roster changed",
    )
    manifest_records = manifest.get("records")
    require(type(manifest_records) is list, "exploratory manifest records are malformed")
    observed = tuple(
        (row.get("record_id"), row.get("canonical_key"))
        for row in manifest_records if type(row) is dict
    )
    require(observed == tuple((row[0], row[1]) for row in EXPECTED_RECORDS),
            "manifest record-to-selected-target mapping changed")
    operations = require_object(manifest.get("operations"), "manifest.operations")
    require(
        operations.get("ops_root") == REPLACEMENT_OPERATIONS_ROOT
        and operations.get("scratch_root") == REPLACEMENT_SCRATCH_ROOT,
        "exploratory manifest does not use the clean v2r3 namespaces",
    )
    exploratory = require_object(
        manifest.get("exploratory_preregistration"),
        "manifest.exploratory_preregistration",
    )
    require_exact_keys(
        exploratory,
        {
            "study_id", "reporting_class", "never_pool_with_frozen_58",
            "frozen_comparison_protocol_observation_count",
            "frozen_comparison_distinct_target_count",
            "frozen_comparison_continuation_observation_count",
            "cohort_size", "selected_canonical_keys", "artifacts",
            "artifacts_sha256", "candidate_pool_source_snapshots",
        },
        "manifest.exploratory_preregistration",
    )
    require(
        exploratory.get("study_id") == EXPLORATORY_STUDY_ID
        and exploratory.get("reporting_class") == REPORTING_CLASS
        and exploratory.get("never_pool_with_frozen_58") is True
        and exploratory.get("frozen_comparison_protocol_observation_count")
        == FROZEN_CONFIRMATORY_PROTOCOL_OBSERVATION_COUNT
        and exploratory.get("frozen_comparison_distinct_target_count")
        == FROZEN_CONFIRMATORY_DISTINCT_TARGET_COUNT
        and exploratory.get("frozen_comparison_continuation_observation_count")
        == FROZEN_CONFIRMATORY_CONTINUATION_OBSERVATION_COUNT
        and exploratory.get("cohort_size") == len(EXPECTED_RECORDS)
        and exploratory.get("selected_canonical_keys") == list(EXPECTED_KEYS),
        "manifest does not preserve the separate frozen six-target roster",
    )
    artifacts = require_object(exploratory.get("artifacts"),
                               "manifest exploratory artifacts")
    require(set(artifacts) == PREREGISTRATION_FILENAMES,
            "manifest preregistration artifact inventory changed")
    require(
        exploratory.get("artifacts_sha256")
        == common.sha_bytes(common.canonical_bytes(artifacts)),
        "manifest preregistration artifact-set digest changed",
    )
    source_snapshots = require_object(
        exploratory.get("candidate_pool_source_snapshots"),
        "manifest candidate-pool source snapshots",
    )
    require(
        set(source_snapshots) == set(EXPECTED_POOL_SOURCE_SNAPSHOTS),
        "manifest candidate-pool source snapshot inventory changed",
    )
    for source_id, expected in EXPECTED_POOL_SOURCE_SNAPSHOTS.items():
        binding = require_object(
            source_snapshots[source_id],
            f"manifest candidate-pool source snapshot {source_id}",
        )
        require_exact_keys(
            binding, {"path", "sha256", "size_bytes"},
            f"manifest candidate-pool source snapshot {source_id}",
        )
        require(
            binding["path"]
            == f"preregistration/source_snapshots/{source_id}.pdf"
            and binding["sha256"] == expected["sha256"]
            and binding["size_bytes"] == expected["size_bytes"],
            f"manifest candidate-pool source snapshot {source_id} changed",
        )

    require(
        seal.get("schema") == SEAL_SCHEMA and seal.get("run_id") == run.name
        and seal.get("launch_authorized") is True,
        "exploratory runtime seal identity/status changed",
    )
    parse_payload(seal, "runtime_payload_sha256", "exploratory runtime seal")
    seal_manifest = require_object(seal.get("manifest"), "runtime seal.manifest")
    require(
        type(seal_manifest.get("path")) is str
        and Path(seal_manifest["path"]).resolve() == manifest_snapshot.path.resolve()
        and seal_manifest.get("repository_path")
        == f"{REPLACEMENT_RUN_ROOT}/RUN_MANIFEST.json"
        and seal_manifest.get("sha256") == manifest_snapshot.sha256
        and seal_manifest.get("size_bytes") == manifest_snapshot.size
        and seal_manifest.get("manifest_payload_sha256")
        == manifest.get("manifest_payload_sha256"),
        "runtime seal does not bind the current manifest bytes",
    )
    expected_exploratory = copy.deepcopy(exploratory)
    expected_exploratory["manifest_section_sha256"] = common.sha_bytes(
        common.canonical_bytes(exploratory)
    )
    require(seal.get("exploratory_preregistration") == expected_exploratory,
            "runtime seal exploratory-preregistration binding changed")
    require(
        seal.get("candidate_pool_source_snapshots") == source_snapshots,
        "runtime seal candidate-pool source-snapshot binding changed",
    )
    require(seal_snapshot.sha256 == common.sha_bytes(seal_snapshot.data),
            "runtime seal snapshot digest is inconsistent")
    return artifacts, source_snapshots


def aggregate(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    counts = {name: 0 for name in
              ("BOTH_SOLVED", "BUGBANK_ONLY", "PLAIN_ONLY", "NEITHER_SOLVED")}
    lower = {name: 0 for name in ("BUGBANK", "PLAIN", "TIE")}
    for row in records:
        counts[row["outcome"]] += 1
        lower[row["lower_token_arm"]] += 1
    bugbank_tokens = common.safe_add(
        (row["arms"]["bugbank"]["model_tokens_used"] for row in records),
        "exploratory BugBank token total",
    )
    plain_tokens = common.safe_add(
        (row["arms"]["plain"]["model_tokens_used"] for row in records),
        "exploratory plain token total",
    )
    return {
        "unit": "PAIRED_PROTOCOL_INSTANCE",
        "population_size": len(records),
        "outcomes": {
            "bugbank_solved": counts["BOTH_SOLVED"] + counts["BUGBANK_ONLY"],
            "plain_solved": counts["BOTH_SOLVED"] + counts["PLAIN_ONLY"],
            "both_solved": counts["BOTH_SOLVED"],
            "bugbank_only": counts["BUGBANK_ONLY"],
            "plain_only": counts["PLAIN_ONLY"],
            "neither_solved": counts["NEITHER_SOLVED"],
        },
        "tokens": {
            "comparison_basis": "CUMULATIVE_ENDPOINT_MODEL_TOKENS",
            "bugbank_total": bugbank_tokens,
            "plain_total": plain_tokens,
            "plain_minus_bugbank_total": common.safe_subtract(
                plain_tokens, bugbank_tokens, "exploratory aggregate token difference"
            ),
            "lower_token_pairs": {
                "bugbank": lower["BUGBANK"],
                "plain": lower["PLAIN"],
                "ties": lower["TIE"],
            },
        },
        "records": list(records),
    }


def render_results(
    run_root: Path,
    *,
    validator_path: Path = DEFAULT_VALIDATOR,
    authority_verifier: AuthorityVerifier = verify_sealed_authority,
) -> tuple[dict[str, Any], str, str]:
    run = Path(os.path.abspath(run_root))
    try:
        run_info = run.lstat()
    except OSError as error:
        raise RenderError(f"cannot stat exploratory run root {run}: {error}") from error
    require(stat.S_ISDIR(run_info.st_mode),
            "exploratory run root is not a plain directory")
    require(run.name == DEFAULT_RUN.name,
            "renderer accepts only the preregistered exploratory run identity")

    report, report_snapshot = load_strict_json(
        run / "VALIDATION_REPORT.json", "exploratory validation report"
    )
    manifest_value, manifest_snapshot = load_strict_json(
        run / "RUN_MANIFEST.json", "exploratory run manifest"
    )
    seal_value, seal_snapshot = load_strict_json(
        run / "RUNTIME_SEAL.json", "exploratory runtime seal"
    )
    try:
        validator_snapshot = common.read_plain_file(validator_path)
    except common.RenderError as error:
        raise RenderError(str(error)) from error

    manifest_checked, seal_checked = authority_verifier(run)
    require(manifest_checked == manifest_value,
            "runtime-seal verifier returned different manifest bytes")
    require(seal_checked == seal_value,
            "runtime-seal verifier returned different seal bytes")
    artifact_bindings, source_snapshot_bindings = validate_manifest_and_seal(
        run, manifest_value, seal_value, manifest_snapshot, seal_snapshot
    )

    prerequisite_values: dict[str, dict[str, Any]] = {}
    prerequisite_snapshots: dict[str, common.FileSnapshot] = {}
    snapshots: list[common.FileSnapshot] = [
        report_snapshot, manifest_snapshot, seal_snapshot, validator_snapshot,
    ]
    for name in sorted(PREREGISTRATION_FILENAMES):
        binding = artifact_bindings[name]
        path = safe_relative_binding_path(run, binding.get("path"),
                                          f"preregistration artifact {name}")
        if name in JSON_PREREGISTRATION_FILENAMES:
            value, snapshot = load_strict_json(path, f"preregistration artifact {name}")
            prerequisite_values[name] = value
        else:
            try:
                snapshot = common.read_plain_file(path)
                snapshot.data.decode("utf-8")
            except (common.RenderError, UnicodeDecodeError) as error:
                raise RenderError(f"invalid source-context artifact {path}: {error}") from error
        validate_binding(run, binding, snapshot, f"preregistration artifact {name}")
        prerequisite_snapshots[name] = snapshot
        snapshots.append(snapshot)

    superseded_v1_sources: dict[str, dict[str, Any]] = {}
    for name, relative_path, expected_sha256 in (
        (
            "preregistration",
            SUPERSEDED_V1_PREREGISTRATION_PATH,
            SUPERSEDED_V1_PREREGISTRATION_SHA256,
        ),
        (
            "candidate_pool",
            SUPERSEDED_V1_CANDIDATE_POOL_PATH,
            SUPERSEDED_V1_CANDIDATE_POOL_SHA256,
        ),
    ):
        try:
            snapshot = common.read_plain_file(REPO / relative_path)
        except common.RenderError as error:
            raise RenderError(str(error)) from error
        require(snapshot.sha256 == expected_sha256,
                f"superseded v1 {name} bytes changed")
        snapshots.append(snapshot)
        superseded_v1_sources[name] = {
            "path": relative_path,
            "size_bytes": snapshot.size,
            "sha256": snapshot.sha256,
            "never_launched": True,
        }

    validate_selection(
        prerequisite_values["PREREGISTRATION.json"],
        prerequisite_values["CANDIDATE_POOL.json"],
        prerequisite_values["SELECTION_REPORT.json"],
        prerequisite_values["CONFIRMATORY_BOUNDARY_SEAL.json"],
        prerequisite_values["RUNTIME_CORRECTION_AMENDMENT_20260904.json"],
        prerequisite_values[
            "RUNTIME_PREFLIGHT_CORRECTION_AMENDMENT_20260904.json"
        ],
        prerequisite_snapshots,
    )
    candidate_sources_raw = prerequisite_values["CANDIDATE_POOL.json"].get("sources")
    require(type(candidate_sources_raw) is list,
            "candidate-pool source ledger is malformed")
    candidate_sources = {
        row.get("source_id"): row
        for row in candidate_sources_raw if type(row) is dict
    }
    require(set(candidate_sources) == set(EXPECTED_POOL_SOURCE_SNAPSHOTS),
            "candidate-pool source ledger differs from the exact v2 set")
    candidate_source_sources: dict[str, dict[str, Any]] = {}
    for source_id in sorted(EXPECTED_POOL_SOURCE_SNAPSHOTS):
        binding = source_snapshot_bindings[source_id]
        path = safe_relative_binding_path(
            run, binding.get("path"),
            f"candidate-pool source snapshot {source_id}",
        )
        try:
            snapshot = common.read_plain_file(path)
        except common.RenderError as error:
            raise RenderError(str(error)) from error
        validate_binding(
            run, binding, snapshot,
            f"candidate-pool source snapshot {source_id}",
        )
        expected = EXPECTED_POOL_SOURCE_SNAPSHOTS[source_id]
        ledger = candidate_sources[source_id]
        require(
            snapshot.sha256 == expected["sha256"]
            and snapshot.size == expected["size_bytes"]
            and ledger.get("pdf_sha256") == snapshot.sha256
            and ledger.get("pdf_bytes") == snapshot.size,
            f"candidate-pool source snapshot {source_id} differs from v2 authority",
        )
        snapshots.append(snapshot)
        candidate_source_sources[source_id] = {
            "path": binding["path"],
            "size_bytes": snapshot.size,
            "sha256": snapshot.sha256,
        }
    report_records, report_payload_hash = validate_report(
        report, run, validator_snapshot
    )
    manifest_map = {
        row["record_id"]: row for row in manifest_value["records"]
    }
    terminal_directory = run / "pair_terminals"
    expected_names = frozenset(f"{record_id}.json" for record_id in EXPECTED_IDS)
    try:
        observed_names = common.plain_directory_names(terminal_directory)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    require(observed_names == expected_names,
            "exploratory pair-terminal inventory differs from the exact six-record roster")

    spec = common.SourceSpec(
        key="exploratory", label="Exploratory fresh-source cohort",
        run_root=run, report_name="VALIDATION_REPORT.json",
        terminal_directory="pair_terminals", report_schema=REPORT_SCHEMA,
        terminal_schema=TERMINAL_SCHEMA, validator=validator_snapshot.path,
        comparison_basis="CUMULATIVE_ENDPOINT_MODEL_TOKENS",
        macro_prefix="pairedExploratory",
    )
    records: list[dict[str, Any]] = []
    terminal_sources: list[dict[str, Any]] = []
    for rank, (record_id, canonical_key, selection_hash) in enumerate(
            EXPECTED_RECORDS, start=1):
        terminal, terminal_snapshot = load_strict_json(
            terminal_directory / f"{record_id}.json",
            f"exploratory terminal {record_id}",
        )
        snapshots.append(terminal_snapshot)
        try:
            normalized = common.validate_terminal(
                spec, terminal, report, record_id, report_records[record_id]
            )
        except common.RenderError as error:
            raise RenderError(str(error)) from error
        normalized.update({
            "canonical_key": canonical_key,
            "selection_rank": rank,
            "selection_hash": selection_hash,
        })
        require(
            manifest_map[record_id].get("canonical_key") == canonical_key,
            f"manifest target mismatch for {record_id}",
        )
        records.append(normalized)
        terminal_sources.append({
            "record_id": record_id,
            "path": f"pair_terminals/{record_id}.json",
            "size_bytes": terminal_snapshot.size,
            "sha256": terminal_snapshot.sha256,
            "terminal_payload_sha256": terminal["terminal_payload_sha256"],
        })

    cohort = aggregate(records)
    verified_counts = require_object(
        require_object(report["counts"], "report counts")["verified_full"],
        "report verified_full",
    )
    require(
        set(verified_counts) == set(common.ARMS)
        and all(common.require_count(verified_counts[arm], f"verified_full.{arm}")
                == cohort["outcomes"][f"{arm}_solved"] for arm in common.ARMS),
        "report verified-full counts disagree with pair terminals",
    )

    first_lineage = continuation_inventory(run)
    require(first_lineage == continuation_inventory(run),
            "exploratory continuation inventory changed while rendering")
    require(common.plain_directory_names(terminal_directory) == expected_names,
            "exploratory terminal inventory changed while rendering")
    for snapshot in snapshots:
        try:
            snapshot.assert_unchanged()
        except common.RenderError as error:
            raise RenderError(str(error)) from error

    unsigned: dict[str, Any] = {
        "schema": "paired_open_problem_exploratory_paper_results_v2",
        "study_id": EXPLORATORY_STUDY_ID,
        "reporting_class": REPORTING_CLASS,
        "never_pool_with_frozen_58": True,
        "frozen_confirmatory_protocol_observation_count":
        FROZEN_CONFIRMATORY_PROTOCOL_OBSERVATION_COUNT,
        "frozen_confirmatory_distinct_target_count":
        FROZEN_CONFIRMATORY_DISTINCT_TARGET_COUNT,
        "frozen_confirmatory_continuation_observation_count":
        FROZEN_CONFIRMATORY_CONTINUATION_OBSERVATION_COUNT,
        "cohort": cohort,
        "continuation_lineage": {
            "policy": copy.deepcopy(seal_checker.VERSIONED_CONTINUATION_POLICY),
            "observed_continuation_runs": list(first_lineage),
            "terminal_base_report_requires_empty_lineage": True,
        },
        "sources": {
            "run_id": run.name,
            "validation_report": {
                "path": "VALIDATION_REPORT.json",
                "size_bytes": report_snapshot.size,
                "sha256": report_snapshot.sha256,
                "report_payload_sha256": report_payload_hash,
            },
            "validator": {
                "path": f"qedbench_certificate_availability_triage/scripts/{validator_snapshot.path.name}",
                "sha256": validator_snapshot.sha256,
            },
            "run_manifest": {
                "path": "RUN_MANIFEST.json",
                "size_bytes": manifest_snapshot.size,
                "sha256": manifest_snapshot.sha256,
                "manifest_payload_sha256": manifest_value["manifest_payload_sha256"],
            },
            "runtime_seal": {
                "path": "RUNTIME_SEAL.json",
                "size_bytes": seal_snapshot.size,
                "sha256": seal_snapshot.sha256,
                "runtime_payload_sha256": seal_value["runtime_payload_sha256"],
            },
            "preregistration_artifacts": {
                name: {
                    "path": artifact_bindings[name]["path"],
                    "size_bytes": prerequisite_snapshots[name].size,
                    "sha256": prerequisite_snapshots[name].sha256,
                }
                for name in sorted(PREREGISTRATION_FILENAMES)
            },
            "candidate_pool_source_snapshots": candidate_source_sources,
            "superseded_v1_audit_trail": superseded_v1_sources,
            "pair_terminals": terminal_sources,
            "pair_terminal_set_payload_sha256": common.sha_bytes(
                common.canonical_bytes(terminal_sources)
            ),
        },
    }
    result = copy.deepcopy(unsigned)
    result["results_payload_sha256"] = common.sha_bytes(common.canonical_bytes(unsigned))
    return result, render_macros(result), render_rows(result)


def macro_values(cohort: Mapping[str, Any]) -> tuple[tuple[str, int], ...]:
    outcomes = cohort["outcomes"]
    tokens = cohort["tokens"]
    lower = tokens["lower_token_pairs"]
    return (
        ("Pairs", cohort["population_size"]),
        ("BugBankSolved", outcomes["bugbank_solved"]),
        ("PlainSolved", outcomes["plain_solved"]),
        ("BothSolved", outcomes["both_solved"]),
        ("BugBankOnly", outcomes["bugbank_only"]),
        ("PlainOnly", outcomes["plain_only"]),
        ("NeitherSolved", outcomes["neither_solved"]),
        ("BugBankTokens", tokens["bugbank_total"]),
        ("PlainTokens", tokens["plain_total"]),
        ("PlainMinusBugBankTokens", tokens["plain_minus_bugbank_total"]),
        ("BugBankLowerTokens", lower["bugbank"]),
        ("PlainLowerTokens", lower["plain"]),
        ("TokenTies", lower["ties"]),
    )


def render_macros(result: Mapping[str, Any]) -> str:
    lines = [
        "% GENERATED by render_paired_open_problem_exploratory_paper_results.py; do not edit.",
        f"% results_payload_sha256={result['results_payload_sha256']}",
    ]
    for suffix, value in macro_values(result["cohort"]):
        lines.append(f"\\newcommand{{\\pairedExploratory{suffix}}}{{{value}}}")
    return "\n".join(lines) + "\n"


def render_rows(result: Mapping[str, Any]) -> str:
    cohort = result["cohort"]
    outcomes = cohort["outcomes"]
    tokens = cohort["tokens"]
    lower = tokens["lower_token_pairs"]
    return (
        "% GENERATED by render_paired_open_problem_exploratory_paper_results.py; do not edit.\n"
        f"% results_payload_sha256={result['results_payload_sha256']}\n"
        f"Exploratory fresh-source cohort & {cohort['population_size']} & "
        f"{outcomes['bugbank_solved']}/{outcomes['plain_solved']} & "
        f"{outcomes['both_solved']} & "
        f"{outcomes['bugbank_only']}/{outcomes['plain_only']} & "
        f"{outcomes['neither_solved']} & "
        f"{tokens['bugbank_total']}/{tokens['plain_total']} & "
        f"{lower['bugbank']}/{lower['plain']}/{lower['ties']} \\\\\n"
    )


def output_bytes(result: Mapping[str, Any], macros: str, rows: str) -> dict[str, bytes]:
    require(not (set(OUTPUT_NAMES.values()) & CONFIRMATORY_OUTPUT_NAMES),
            "exploratory and confirmatory generated namespaces overlap")
    return {
        OUTPUT_NAMES["json"]: json.dumps(
            result, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2
        ).encode("utf-8") + b"\n",
        OUTPUT_NAMES["macros"]: macros.encode("utf-8"),
        OUTPUT_NAMES["rows"]: rows.encode("utf-8"),
    }


def write_outputs(output_directory: Path, expected: Mapping[str, bytes]) -> None:
    require(set(expected) == set(OUTPUT_NAMES.values()),
            "publication set is not the exact three-file exploratory namespace")
    try:
        directory = common.validate_output_directory(output_directory)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    targets = {name: directory / name for name in expected}
    for target in targets.values():
        if os.path.lexists(target):
            require(stat.S_ISREG(target.lstat().st_mode),
                    f"generated target is not a plain file: {target}")
    temporary: dict[str, Path] = {}
    try:
        for name in sorted(expected):
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{name}.", suffix=".tmp", dir=directory
            )
            temporary[name] = Path(temporary_name)
            try:
                os.fchmod(descriptor, 0o644)
                view = memoryview(expected[name])
                while view:
                    written = os.write(descriptor, view)
                    if written <= 0:
                        raise OSError("short generated-output write")
                    view = view[written:]
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        marker_name = OUTPUT_NAMES["json"]
        marker_target = targets[marker_name]
        if os.path.lexists(marker_target):
            os.unlink(marker_target)
            common.fsync_directory(directory)
        for name in sorted(name for name in expected if name != marker_name):
            os.replace(temporary.pop(name), targets[name])
        common.fsync_directory(directory)
        os.replace(temporary.pop(marker_name), marker_target)
        common.fsync_directory(directory)
    except OSError as error:
        raise RenderError(f"cannot publish exploratory generated outputs: {error}") from error
    finally:
        for temporary_path in temporary.values():
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def check_outputs(output_directory: Path, expected: Mapping[str, bytes]) -> None:
    require(set(expected) == set(OUTPUT_NAMES.values()),
            "check set is not the exact three-file exploratory namespace")
    try:
        common.check_outputs(output_directory, expected)
    except common.RenderError as error:
        raise RenderError(str(error)) from error


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    parser.add_argument("--check", action="store_true",
                        help="validate authority and require byte-identical generated outputs")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        result, macros, rows = render_results(arguments.run)
        expected = output_bytes(result, macros, rows)
        if arguments.check:
            check_outputs(arguments.output_directory, expected)
        else:
            write_outputs(arguments.output_directory, expected)
    except (RenderError, common.RenderError) as error:
        print(f"ERROR: {error}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
