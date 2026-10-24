#!/usr/bin/env python3
"""Render only the separately reported BugBank-targeted stress-test result.

Publication is fail closed.  The renderer accepts only the exact frozen
six-record targeted roster, current targeted runtime seal, VALID_COMPLETE
independent-validator report, and exact six-file pair-terminal inventory.  Its
three output names are disjoint from both confirmatory and outcome-blind
exploratory outputs; no result is ever pooled across those reporting strata.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import paired_open_problem_targeted_stress_v2_runtime_seal as seal_checker
import render_paired_open_problem_paper_results as common


REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "qedbench_certificate_availability_triage"
RUNS = BASE / "runs"
SCRIPTS = BASE / "scripts"
DEFAULT_RUN = RUNS / "open_frontier_paired_targeted_stress_v2_20260904"
EXPECTED_RUN_REPOSITORY_PATH = (
    "qedbench_certificate_availability_triage/runs/"
    "open_frontier_paired_targeted_stress_v2_20260904"
)
DEFAULT_VALIDATOR = (
    SCRIPTS / "validate_paired_open_problem_targeted_stress_v2_run.py"
)
DEFAULT_OUTPUT_DIRECTORY = REPO / "paper_v2" / "generated"
OUTPUT_NAMES = {
    "json": "paired_open_problem_targeted_results.json",
    "macros": "paired_open_problem_targeted_macros.tex",
    "rows": "paired_open_problem_targeted_rows.tex",
}
CONFIRMATORY_OUTPUT_NAMES = frozenset(common.OUTPUT_NAMES.values())
EXPLORATORY_OUTPUT_NAMES = frozenset({
    "paired_open_problem_exploratory_results.json",
    "paired_open_problem_exploratory_macros.tex",
    "paired_open_problem_exploratory_rows.tex",
})
FORBIDDEN_OUTPUT_NAMES = CONFIRMATORY_OUTPUT_NAMES | EXPLORATORY_OUTPUT_NAMES
REPORT_SCHEMA = "paired_open_problem_validation_report_v1"
TERMINAL_SCHEMA = "paired_open_problem_pair_terminal_v1"
MANIFEST_SCHEMA = "paired_open_problem_run_manifest_v1"
SEAL_SCHEMA = "paired_open_problem_runtime_seal_v1"
PROTOCOL_ID = "WHOLE_PROOF_FIRST_SOLUTION_V1"
STUDY_ID = "BUGBANK_TARGETED_STRESS_V1"
REPORTING_CLASS = "HYPOTHESIS_GENERATING_BUGBANK_TARGETED_STRESS_TEST"
STUDY_LABEL = (
    "Hypothesis-generating BugBank-targeted stress test "
    "(never pool with confirmatory or outcome-blind cohorts)"
)
EXPECTED_OPS = "<workspace-home>/paired_targeted_stress_v2_ops"
EXPECTED_SCRATCH = "<workspace-home>/paired_targeted_stress_v2_scratch"
ORIGINAL_RUN_REPOSITORY_PATH = (
    "qedbench_certificate_availability_triage/runs/"
    "open_frontier_paired_bugbank_targeted_stress_v1_20260904"
)
ORIGINAL_OPS = "<workspace-home>/paired_bugbank_targeted_stress_v1_ops"
ORIGINAL_SCRATCH = "<workspace-home>/paired_bugbank_targeted_stress_v1_scratch"
EXPECTED_RECORDS = (
    (
        "targeted_barbados_p33_restricted_induced_ramsey",
        "barbados26:problems.pdf@6e313aef#Problem 33 first clause",
    ),
    (
        "targeted_esa_triangle_partition_radius1",
        "doi:10.4230/LIPIcs.ESA.2026.73#Question 5",
    ),
    (
        "targeted_esa_hamiltonian_cycle_linear_radius",
        "doi:10.4230/LIPIcs.ESA.2026.73#Question 1 subsidiary",
    ),
    (
        "targeted_esa_dominating_set_linear_radius",
        "doi:10.4230/LIPIcs.ESA.2026.73#Question 2",
    ),
    (
        "targeted_barbados_p31_geodesic_separator",
        "barbados26:problems.pdf@6e313aef#Problem 31",
    ),
    (
        "targeted_icalp_unsplittable_two_sided",
        "doi:10.4230/LIPIcs.ICALP.2026.74#Conjecture 12",
    ),
)
EXPECTED_IDS = tuple(row[0] for row in EXPECTED_RECORDS)
EXPECTED_KEYS = tuple(row[1] for row in EXPECTED_RECORDS)
ARTIFACT_PATHS = {
    "preregistration": BASE / "paired_open_problem_bugbank_targeted_stress_v1"
    / "PREREGISTRATION.json",
    "ranked_roster": BASE / "paired_open_problem_bugbank_targeted_stress_v1"
    / "RANKED_ROSTER.json",
    "source_context": BASE / "paired_open_problem_bugbank_targeted_stress_v1"
    / "SELECTED_SOURCE_CONTEXT.md",
    "original_source_specification":
    BASE / "paired_open_problem_bugbank_targeted_stress_sources_v1"
    / "bootstrap_spec.json",
    "runtime_source_specification":
    BASE / "paired_open_problem_bugbank_targeted_stress_sources_v1"
    / "bootstrap_spec_runtime_v2.json",
    "runtime_correction_amendment":
    BASE / "paired_open_problem_bugbank_targeted_stress_v1"
    / "RUNTIME_CORRECTION_AMENDMENT_20260904.json",
}
ARTIFACT_REPOSITORY_PATHS = {
    name: path.relative_to(REPO).as_posix() for name, path in ARTIFACT_PATHS.items()
}


class RenderError(common.RenderError):
    """A targeted result input or output violates the publication contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RenderError(message)


def require_object(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is dict, f"{label} must be a JSON object")
    return value


def exact_keys(value: Mapping[str, Any], wanted: set[str], label: str) -> None:
    actual = set(value)
    require(
        actual == wanted,
        f"{label} field set mismatch: missing={sorted(wanted - actual)}, "
        f"unexpected={sorted(actual - wanted)}",
    )


def load_json(
    path: Path, label: str,
) -> tuple[dict[str, Any], common.FileSnapshot]:
    try:
        value, snapshot = common.load_json_snapshot(path)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    return require_object(value, label), snapshot


def payload_hash(value: Mapping[str, Any], field: str, label: str) -> str:
    try:
        return common.validate_payload_hash(value, field, label)
    except common.RenderError as error:
        raise RenderError(str(error)) from error


def verify_sealed_authority(run: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay the production targeted seal checker without mutating the run."""
    try:
        manifest, _bindings = seal_checker.validate_manifest(run)
        seal = seal_checker.check_seal(run)
    except (seal_checker.SealError, OSError, KeyError, TypeError, ValueError) as error:
        raise RenderError(f"targeted runtime seal is not currently valid: {error}") from error
    return manifest, seal


AuthorityVerifier = Callable[[Path], tuple[dict[str, Any], dict[str, Any]]]


def validate_artifact_binding(
    name: str, binding: Any,
) -> common.FileSnapshot:
    row = require_object(binding, f"targeted seal artifact {name}")
    exact_keys(
        row, {"path", "sha256", "size_bytes", "repository_path"},
        f"targeted seal artifact {name}",
    )
    expected_path = ARTIFACT_PATHS[name].resolve()
    require(
        type(row["path"]) is str
        and Path(row["path"]).resolve() == expected_path
        and row["repository_path"] == ARTIFACT_REPOSITORY_PATHS[name],
        f"targeted seal artifact {name} names the wrong repository file",
    )
    try:
        snapshot = common.read_plain_file(expected_path)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    require(
        common.require_sha(row["sha256"], f"targeted artifact {name} hash")
        == snapshot.sha256
        and common.require_count(
            row["size_bytes"], f"targeted artifact {name} size"
        ) == snapshot.size,
        f"targeted seal artifact {name} does not bind current exact bytes",
    )
    return snapshot


def validate_preregistration(
    values: Mapping[str, dict[str, Any]],
    snapshots: Mapping[str, common.FileSnapshot],
) -> None:
    prereg = values["preregistration"]
    roster = values["ranked_roster"]
    source_spec = values["original_source_specification"]
    require(
        prereg.get("schema")
        == "qedbench.paired_open_problem_bugbank_targeted_stress_preregistration.v1"
        and prereg.get("study_id") == STUDY_ID
        and prereg.get("reporting_class") == REPORTING_CLASS,
        "targeted preregistration identity or reporting class changed",
    )
    attestation = require_object(
        prereg.get("outcome_access_attestation"), "targeted outcome-access attestation"
    )
    require(
        attestation.get("static_bugbank_reconnaissance_before_freeze") is True
        and attestation.get("solver_call_before_freeze") is False
        and attestation.get("model_auditor_call_before_freeze") is False
        and attestation.get(
            "experimental_per_claim_bugbank_receipt_existed_before_freeze"
        ) is False
        and attestation.get("arm_outcome_existed_before_freeze") is False,
        "targeted selection-bias disclosure or pre-outcome freeze changed",
    )
    boundary = require_object(prereg.get("reporting_boundary"), "reporting boundary")
    require(
        all(
            type(boundary.get(name)) is dict
            and boundary[name].get("pooling_allowed") is False
            for name in ("confirmatory", "outcome_blind_internet_six", "targeted_stress")
        ),
        "targeted non-pooling boundary changed",
    )
    paired = require_object(prereg.get("paired_run"), "targeted paired run")
    require(
        paired.get("run_root") == ORIGINAL_RUN_REPOSITORY_PATH
        and paired.get("operations_root") == ORIGINAL_OPS
        and paired.get("scratch_root") == ORIGINAL_SCRATCH
        and paired.get("protocol_id") == PROTOCOL_ID
        and paired.get("initial_iteration_cap") == 50
        and paired.get("arms") == ["bugbank", "plain"]
        and paired.get("retrieval_k_per_claim") == 3,
        "targeted preregistered run contract changed",
    )

    roster_binding = require_object(prereg.get("roster"), "preregistered roster binding")
    context_binding = require_object(
        prereg.get("source_context"), "preregistered source-context binding"
    )
    package_binding = require_object(
        prereg.get("source_package"), "preregistered source-package binding"
    )
    require(
        roster_binding.get("count") == 6
        and roster_binding.get("ordered_record_ids") == list(EXPECTED_IDS)
        and roster_binding.get("path") == ARTIFACT_REPOSITORY_PATHS["ranked_roster"]
        and roster_binding.get("sha256") == snapshots["ranked_roster"].sha256
        and roster_binding.get("size_bytes") == snapshots["ranked_roster"].size,
        "preregistered ranked-roster byte binding changed",
    )
    require(
        context_binding.get("path") == ARTIFACT_REPOSITORY_PATHS["source_context"]
        and context_binding.get("sha256") == snapshots["source_context"].sha256
        and context_binding.get("size_bytes") == snapshots["source_context"].size,
        "preregistered source-context byte binding changed",
    )
    require(
        package_binding.get("bootstrap_spec_path")
        == ARTIFACT_REPOSITORY_PATHS["original_source_specification"]
        and package_binding.get("bootstrap_spec_sha256")
        == snapshots["original_source_specification"].sha256
        and package_binding.get("bootstrap_spec_size_bytes")
        == snapshots["original_source_specification"].size,
        "preregistered source-specification byte binding changed",
    )

    rows = roster.get("roster")
    require(
        roster.get("schema") == "qedbench.bugbank_targeted_stress_ranked_roster.v1"
        and roster.get("reporting_class") == REPORTING_CLASS
        and type(rows) is list
        and len(rows) == 6,
        "targeted ranked-roster envelope changed",
    )
    observed: list[tuple[Any, Any, Any]] = []
    for index, raw in enumerate(rows):
        row = require_object(raw, f"targeted ranked roster row {index + 1}")
        observed.append((row.get("rank"), row.get("record_id"), row.get("canonical_key")))
        require(
            type(row.get("expected_bugbank_relevance")) is str
            and bool(row["expected_bugbank_relevance"].strip())
            and type(row.get("scope")) is str and bool(row["scope"].strip()),
            f"targeted roster row {index + 1} lacks frozen selection rationale/scope",
        )
    require(
        observed
        == [(rank, record_id, key) for rank, (record_id, key)
            in enumerate(EXPECTED_RECORDS, start=1)],
        "targeted ranked roster differs from the exact six-record order",
    )
    require(
        source_spec.get("schema") == "paired_open_problem_bootstrap_spec_v1"
        and source_spec.get("run_id")
        == Path(ORIGINAL_RUN_REPOSITORY_PATH).name
        and source_spec.get("max_iterations") == 50
        and [row.get("record_id") for row in source_spec.get("records", [])]
        == list(EXPECTED_IDS),
        "targeted source specification identity or roster changed",
    )
    try:
        context_text = snapshots["source_context"].data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RenderError("targeted source context is not UTF-8") from error
    require(bool(context_text.strip()), "targeted source context is empty")

    runtime_spec = values["runtime_source_specification"]
    require(
        runtime_spec.get("schema") == "paired_open_problem_bootstrap_spec_v1"
        and runtime_spec.get("run_id") == DEFAULT_RUN.name
        and runtime_spec.get("max_iterations") == 50
        and [row.get("record_id") for row in runtime_spec.get("records", [])]
        == list(EXPECTED_IDS),
        "targeted runtime source specification identity or roster changed",
    )
    amendment = values["runtime_correction_amendment"]
    exact_keys(
        amendment,
        {"schema", "study_id", "created_at", "reason", "original_freeze",
         "aborted_attempt", "replacement", "unchanged"},
        "targeted runtime-correction amendment",
    )
    original = require_object(
        amendment.get("original_freeze"), "targeted amendment original freeze"
    )
    aborted = require_object(
        amendment.get("aborted_attempt"), "targeted amendment aborted attempt"
    )
    replacement = require_object(
        amendment.get("replacement"), "targeted amendment replacement"
    )
    unchanged = require_object(
        amendment.get("unchanged"), "targeted amendment unchanged contract"
    )
    require(
        amendment.get("schema")
        == "qedbench.paired_open_problem_runtime_correction_amendment.v1"
        and amendment.get("study_id") == STUDY_ID
        and original.get("preregistration_path")
        == ARTIFACT_REPOSITORY_PATHS["preregistration"]
        and original.get("preregistration_sha256")
        == snapshots["preregistration"].sha256
        and original.get("selection_path")
        == ARTIFACT_REPOSITORY_PATHS["ranked_roster"]
        and original.get("selection_sha256") == snapshots["ranked_roster"].sha256
        and original.get("source_spec_path")
        == ARTIFACT_REPOSITORY_PATHS["original_source_specification"]
        and original.get("source_spec_sha256")
        == snapshots["original_source_specification"].sha256,
        "targeted amendment does not byte-bind the original freeze",
    )
    require(
        aborted.get("run_id") == Path(ORIGINAL_RUN_REPOSITORY_PATH).name
        and aborted.get("run_path") == ORIGINAL_RUN_REPOSITORY_PATH
        and aborted.get("validation_status") == "INVALID"
        and aborted.get("arm_specific_iterations") == 0
        and aborted.get("retrieval_receipts") == 0
        and aborted.get("arm_specific_prompts") == 0
        and aborted.get("canonical_run_checkers") == 0
        and aborted.get("arm_endpoints") == {"bugbank": 0, "plain": 0}
        and aborted.get("valid_pair_terminals") == 0
        and aborted.get("neutral_baseline_treatment_leak_diagnostics") == 2,
        "targeted amendment does not preserve the pre-treatment abort facts",
    )
    require(
        replacement
        == {
            "run_id": DEFAULT_RUN.name,
            "operations_root": EXPECTED_OPS,
            "scratch_root": EXPECTED_SCRATCH,
            "model_visible_namespace_contains_treatment_name": False,
            "reuse_prior_model_outputs": False,
            "reuse_prior_neutral_drafts": False,
            "reuse_prior_baselines": False,
            "reuse_prior_audits": False,
            "reuse_prior_scratch_artifacts": False,
            "selection_rule_rerun": False,
        }
        and unchanged.get("ordered_record_ids") == list(EXPECTED_IDS)
        and unchanged.get("arms") == ["bugbank", "plain"]
        and unchanged.get("model") == "gpt-5.6-sol"
        and unchanged.get("reasoning_effort") == "max"
        and unchanged.get("max_iterations") == 50
        and unchanged.get("protocol_id") == PROTOCOL_ID
        and unchanged.get("reporting_class") == REPORTING_CLASS
        and unchanged.get("pooling_allowed") is False,
        "targeted amendment changes the roster, treatment, or reporting boundary",
    )


def validate_manifest_and_seal(
    run: Path,
    manifest: Mapping[str, Any],
    seal: Mapping[str, Any],
    manifest_snapshot: common.FileSnapshot,
) -> tuple[dict[str, common.FileSnapshot], dict[str, dict[str, Any]]]:
    require(
        manifest.get("schema") == MANIFEST_SCHEMA
        and manifest.get("run_id") == DEFAULT_RUN.name
        and manifest.get("study_label") == STUDY_LABEL
        and manifest.get("status") == "BOOTSTRAPPED_AWAITING_RUNTIME_SEAL"
        and manifest.get("launch_authorized") is False,
        "targeted manifest identity or bootstrap status changed",
    )
    payload_hash(manifest, "manifest_payload_sha256", "targeted manifest")
    require(
        manifest.get("problem_count") == 6
        and manifest.get("problem_ids") == list(EXPECTED_IDS)
        and [row.get("record_id") for row in manifest.get("records", [])]
        == list(EXPECTED_IDS),
        "targeted manifest roster differs from the exact ranked six",
    )
    execution = require_object(manifest.get("execution"), "targeted execution")
    protocol = require_object(manifest.get("protocol"), "targeted protocol")
    operations = require_object(manifest.get("operations"), "targeted operations")
    require(
        execution.get("max_iterations") == 50
        and execution.get("arms") == ["bugbank", "plain"]
        and execution.get("model_network_access") is False
        and protocol.get("id") == PROTOCOL_ID
        and protocol.get("whole_proof_claim_cap") is None
        and protocol.get("retrieval_k_per_claim") == 3
        and protocol.get("first_strict_full_audit_stops_either_arm") is True
        and protocol.get("plain_full_solution_requires_budget_match") is False
        and protocol.get("plain_inconclusive_endpoint_requires_budget_match") is True
        and operations.get("ops_root") == EXPECTED_OPS
        and operations.get("scratch_root") == EXPECTED_SCRATCH,
        "targeted manifest protocol or isolated namespace changed",
    )
    require(
        seal.get("schema") == SEAL_SCHEMA
        and seal.get("run_id") == run.name
        and seal.get("launch_authorized") is True,
        "targeted runtime seal identity or authorization changed",
    )
    payload_hash(seal, "runtime_payload_sha256", "targeted runtime seal")
    manifest_binding = require_object(seal.get("manifest"), "sealed manifest binding")
    require(
        type(manifest_binding.get("path")) is str
        and Path(manifest_binding["path"]).resolve() == manifest_snapshot.path.resolve()
        and manifest_binding.get("sha256") == manifest_snapshot.sha256
        and manifest_binding.get("size_bytes") == manifest_snapshot.size
        and manifest_binding.get("manifest_payload_sha256")
        == manifest["manifest_payload_sha256"],
        "targeted runtime seal does not bind the current manifest bytes",
    )
    targeted = require_object(
        seal.get("targeted_preregistration"), "targeted runtime-seal stratum"
    )
    exact_keys(
        targeted,
        {"study_id", "reporting_class", "never_pool_with_confirmatory_36_or_58",
         "never_pool_with_outcome_blind_six", "static_bugbank_reconnaissance_disclosed",
         "no_pre_freeze_experimental_outcomes", "artifacts"},
        "targeted runtime-seal stratum",
    )
    require(
        targeted["study_id"] == STUDY_ID
        and targeted["reporting_class"] == REPORTING_CLASS
        and targeted["never_pool_with_confirmatory_36_or_58"] is True
        and targeted["never_pool_with_outcome_blind_six"] is True
        and targeted["static_bugbank_reconnaissance_disclosed"] is True
        and targeted["no_pre_freeze_experimental_outcomes"] is True,
        "targeted reporting class, bias disclosure, or non-pooling flags changed",
    )
    artifacts = require_object(targeted["artifacts"], "targeted artifact inventory")
    require(
        set(artifacts) == set(ARTIFACT_PATHS),
        "targeted runtime seal does not contain the exact correction-bound freeze",
    )
    snapshots = {
        name: validate_artifact_binding(name, artifacts[name])
        for name in sorted(ARTIFACT_PATHS)
    }
    values: dict[str, dict[str, Any]] = {}
    for name in (
        "preregistration", "ranked_roster", "original_source_specification",
        "runtime_source_specification", "runtime_correction_amendment",
    ):
        try:
            value = json.loads(
                snapshots[name].data.decode("utf-8"),
                object_pairs_hook=common.reject_duplicate_keys,
                parse_constant=common.reject_nonfinite_json,
                parse_float=common.parse_finite_json_float,
                parse_int=common.parse_safe_json_int,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RenderError(f"invalid strict targeted JSON artifact {name}: {error}") from error
        values[name] = require_object(value, f"targeted artifact {name}")
    validate_preregistration(values, snapshots)

    source_binding = require_object(
        require_object(manifest.get("bootstrap"), "manifest bootstrap").get("source_spec"),
        "manifest source-spec binding",
    )
    relative = Path(str(source_binding.get("path", "")))
    require(not relative.is_absolute() and ".." not in relative.parts,
            "manifest source-spec path is unsafe")
    try:
        run_source = common.read_plain_file(run / relative)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    require(
        run_source.data == snapshots["runtime_source_specification"].data
        and source_binding.get("sha256") == run_source.sha256
        and source_binding.get("size_bytes") == run_source.size,
        "targeted manifest does not byte-bind the frozen source specification",
    )
    snapshots["run_source_specification"] = run_source
    return snapshots, values


def validate_report(
    report: Mapping[str, Any], run: Path, validator: common.FileSnapshot,
) -> tuple[dict[str, dict[str, Any]], str]:
    exact_keys(
        report,
        {"schema", "run_id", "run_path", "generated_at", "validator", "status",
         "protocol_id", "counts", "closed_world", "records", "diagnostics",
         "report_payload_sha256"},
        "targeted validation report",
    )
    require(
        report["schema"] == REPORT_SCHEMA
        and report["run_id"] == run.name
        and report["run_path"] == str(run.resolve())
        and report["status"] == "VALID_COMPLETE"
        and report["protocol_id"] == PROTOCOL_ID,
        "targeted validation report is not the exact VALID_COMPLETE authority",
    )
    digest = payload_hash(report, "report_payload_sha256", "targeted validation report")
    validator_binding = require_object(report["validator"], "targeted report validator")
    exact_keys(validator_binding, {"path", "sha256"}, "targeted report validator")
    require(
        type(validator_binding["path"]) is str
        and Path(validator_binding["path"]).resolve() == validator.path.resolve()
        and validator_binding["sha256"] == validator.sha256,
        "targeted report was not produced by the current dedicated validator bytes",
    )
    try:
        common.validate_diagnostics(report["diagnostics"], "targeted report diagnostics")
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    records = require_object(report["records"], "targeted report records")
    require(set(records) == set(EXPECTED_IDS),
            "targeted report roster differs from the exact six records")
    counts = require_object(report["counts"], "targeted report counts")
    exact_keys(
        counts, {"problems", "valid_pair_terminals", "arm_endpoints", "verified_full"},
        "targeted report counts",
    )
    require(
        common.require_count(counts["problems"], "targeted problem count", minimum=1) == 6
        and common.require_count(
            counts["valid_pair_terminals"], "targeted terminal count"
        ) == 6,
        "targeted report does not validate all six pair terminals",
    )
    endpoints = require_object(counts["arm_endpoints"], "targeted arm endpoints")
    require(
        set(endpoints) == set(common.ARMS)
        and all(common.require_count(endpoints[arm], f"targeted {arm} endpoints") == 6
                for arm in common.ARMS),
        "targeted report does not contain both endpoints for all six records",
    )
    return dict(records), digest


def aggregate(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    counts = {name: 0 for name in
              ("BOTH_SOLVED", "BUGBANK_ONLY", "PLAIN_ONLY", "NEITHER_SOLVED")}
    lower = {name: 0 for name in ("BUGBANK", "PLAIN", "TIE")}
    for row in records:
        counts[row["outcome"]] += 1
        lower[row["lower_token_arm"]] += 1
    bugbank_tokens = common.safe_add(
        (row["arms"]["bugbank"]["model_tokens_used"] for row in records),
        "targeted BugBank token total",
    )
    plain_tokens = common.safe_add(
        (row["arms"]["plain"]["model_tokens_used"] for row in records),
        "targeted plain token total",
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
                plain_tokens, bugbank_tokens, "targeted aggregate token difference"
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
        raise RenderError(f"cannot stat targeted run root {run}: {error}") from error
    require(
        stat.S_ISDIR(run_info.st_mode) and run.resolve() == DEFAULT_RUN.resolve(),
        "renderer accepts only the exact preregistered targeted run directory",
    )
    report, report_snapshot = load_json(
        run / "VALIDATION_REPORT.json", "targeted validation report"
    )
    manifest, manifest_snapshot = load_json(
        run / "RUN_MANIFEST.json", "targeted run manifest"
    )
    seal, seal_snapshot = load_json(run / "RUNTIME_SEAL.json", "targeted runtime seal")
    try:
        validator_snapshot = common.read_plain_file(validator_path)
    except common.RenderError as error:
        raise RenderError(str(error)) from error

    checked_manifest, checked_seal = authority_verifier(run)
    require(checked_manifest == manifest,
            "targeted seal verifier returned different manifest content")
    require(checked_seal == seal,
            "targeted seal verifier returned different runtime-seal content")
    prereg_snapshots, _values = validate_manifest_and_seal(
        run, manifest, seal, manifest_snapshot
    )
    report_records, report_payload = validate_report(report, run, validator_snapshot)

    terminal_directory = run / "pair_terminals"
    expected_names = frozenset(f"{record_id}.json" for record_id in EXPECTED_IDS)
    try:
        observed_names = common.plain_directory_names(terminal_directory)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    require(observed_names == expected_names,
            "targeted terminal inventory differs from the exact six-record roster")
    spec = common.SourceSpec(
        key="targeted", label="BugBank-targeted stress test", run_root=run,
        report_name="VALIDATION_REPORT.json", terminal_directory="pair_terminals",
        report_schema=REPORT_SCHEMA, terminal_schema=TERMINAL_SCHEMA,
        validator=validator_snapshot.path,
        comparison_basis="CUMULATIVE_ENDPOINT_MODEL_TOKENS",
        macro_prefix="pairedTargeted",
    )
    snapshots: list[common.FileSnapshot] = [
        report_snapshot, manifest_snapshot, seal_snapshot, validator_snapshot,
        *prereg_snapshots.values(),
    ]
    records: list[dict[str, Any]] = []
    terminal_sources: list[dict[str, Any]] = []
    for rank, (record_id, canonical_key) in enumerate(EXPECTED_RECORDS, start=1):
        terminal, terminal_snapshot = load_json(
            terminal_directory / f"{record_id}.json", f"targeted terminal {record_id}"
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
            "targeted_rank": rank,
        })
        records.append(normalized)
        terminal_sources.append({
            "record_id": record_id,
            "path": f"pair_terminals/{record_id}.json",
            "size_bytes": terminal_snapshot.size,
            "sha256": terminal_snapshot.sha256,
            "terminal_payload_sha256": terminal["terminal_payload_sha256"],
        })
    cohort = aggregate(records)
    verified = require_object(report["counts"]["verified_full"], "verified-full counts")
    require(
        set(verified) == set(common.ARMS)
        and all(common.require_count(verified[arm], f"verified_full.{arm}")
                == cohort["outcomes"][f"{arm}_solved"] for arm in common.ARMS),
        "targeted report solve counts disagree with exact pair terminals",
    )

    require(common.plain_directory_names(terminal_directory) == expected_names,
            "targeted terminal inventory changed while rendering")
    for snapshot in snapshots:
        try:
            snapshot.assert_unchanged()
        except common.RenderError as error:
            raise RenderError(str(error)) from error

    unsigned: dict[str, Any] = {
        "schema": "paired_open_problem_targeted_paper_results_v1",
        "study_id": STUDY_ID,
        "reporting_class": REPORTING_CLASS,
        "selection": {
            "outcome_blind": False,
            "static_bugbank_reconnaissance_used": True,
            "hypothesis_generating_only": True,
        },
        "pooling": {
            "with_confirmatory_36_or_58": False,
            "with_outcome_blind_six": False,
        },
        "cohort": cohort,
        "sources": {
            "run_id": run.name,
            "validation_report": {
                "path": "VALIDATION_REPORT.json",
                "size_bytes": report_snapshot.size,
                "sha256": report_snapshot.sha256,
                "report_payload_sha256": report_payload,
            },
            "validator": {
                "path": f"qedbench_certificate_availability_triage/scripts/"
                f"{validator_snapshot.path.name}",
                "sha256": validator_snapshot.sha256,
            },
            "run_manifest": {
                "path": "RUN_MANIFEST.json",
                "size_bytes": manifest_snapshot.size,
                "sha256": manifest_snapshot.sha256,
                "manifest_payload_sha256": manifest["manifest_payload_sha256"],
            },
            "runtime_seal": {
                "path": "RUNTIME_SEAL.json",
                "size_bytes": seal_snapshot.size,
                "sha256": seal_snapshot.sha256,
                "runtime_payload_sha256": seal["runtime_payload_sha256"],
            },
            "targeted_preregistration_artifacts": {
                name: {
                    "path": ARTIFACT_REPOSITORY_PATHS[name],
                    "size_bytes": prereg_snapshots[name].size,
                    "sha256": prereg_snapshots[name].sha256,
                }
                for name in sorted(ARTIFACT_PATHS)
            },
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
        "% GENERATED by render_paired_open_problem_targeted_paper_results.py; do not edit.",
        f"% results_payload_sha256={result['results_payload_sha256']}",
    ]
    for suffix, value in macro_values(result["cohort"]):
        lines.append(f"\\newcommand{{\\pairedTargeted{suffix}}}{{{value}}}")
    return "\n".join(lines) + "\n"


def render_rows(result: Mapping[str, Any]) -> str:
    cohort = result["cohort"]
    outcomes = cohort["outcomes"]
    tokens = cohort["tokens"]
    lower = tokens["lower_token_pairs"]
    return (
        "% GENERATED by render_paired_open_problem_targeted_paper_results.py; do not edit.\n"
        f"% results_payload_sha256={result['results_payload_sha256']}\n"
        f"BugBank-targeted stress test & {cohort['population_size']} & "
        f"{outcomes['bugbank_solved']}/{outcomes['plain_solved']} & "
        f"{outcomes['both_solved']} & "
        f"{outcomes['bugbank_only']}/{outcomes['plain_only']} & "
        f"{outcomes['neither_solved']} & "
        f"{tokens['bugbank_total']}/{tokens['plain_total']} & "
        f"{lower['bugbank']}/{lower['plain']}/{lower['ties']} \\\\\n"
    )


def output_bytes(result: Mapping[str, Any], macros: str, rows: str) -> dict[str, bytes]:
    require(set(OUTPUT_NAMES.values()).isdisjoint(FORBIDDEN_OUTPUT_NAMES),
            "targeted generated namespace overlaps another reporting stratum")
    return {
        OUTPUT_NAMES["json"]: json.dumps(
            result, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2
        ).encode("utf-8") + b"\n",
        OUTPUT_NAMES["macros"]: macros.encode("utf-8"),
        OUTPUT_NAMES["rows"]: rows.encode("utf-8"),
    }


def write_outputs(output_directory: Path, expected: Mapping[str, bytes]) -> None:
    require(set(expected) == set(OUTPUT_NAMES.values()),
            "publication set is not the exact three-file targeted namespace")
    try:
        directory = common.validate_output_directory(output_directory)
    except common.RenderError as error:
        raise RenderError(str(error)) from error
    targets = {name: directory / name for name in expected}
    require(not (set(targets) & FORBIDDEN_OUTPUT_NAMES),
            "targeted publication attempted another stratum's output name")
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
                        raise OSError("short targeted generated-output write")
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
        raise RenderError(f"cannot publish targeted generated outputs: {error}") from error
    finally:
        for path in temporary.values():
            try:
                path.unlink()
            except FileNotFoundError:
                pass


def check_outputs(output_directory: Path, expected: Mapping[str, bytes]) -> None:
    require(set(expected) == set(OUTPUT_NAMES.values()),
            "check set is not the exact three-file targeted namespace")
    try:
        common.check_outputs(output_directory, expected)
    except common.RenderError as error:
        raise RenderError(str(error)) from error


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    parser.add_argument("--check", action="store_true")
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
