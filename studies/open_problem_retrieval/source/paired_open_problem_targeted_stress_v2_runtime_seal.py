#!/usr/bin/env python3
"""Create or check the runtime seal for the BugBank-targeted stress run.

The bootstrap manifest is immutable and intentionally non-launchable.  A
reviewed RUNTIME_SEAL.json separately authorizes execution and binds the exact
manifest, every manifest-bound scientific input, runtime programs, repository
commit, BugBank database, model CLI, and isolated operational namespaces.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


SCRIPT = Path(__file__).resolve()
BASE = SCRIPT.parent.parent
REPO = BASE.parent
ACTIVE_RUN = BASE / "runs/open_frontier_paired_v2_20260901"
ACTIVE_OPS = Path("<workspace-home>/paired_v2_ops")
EXPECTED_RUN_ID = "open_frontier_paired_targeted_stress_v2_20260904"
EXPECTED_RUN = BASE / "runs" / EXPECTED_RUN_ID
EXPECTED_OPS = Path("<workspace-home>/paired_targeted_stress_v2_ops")
EXPECTED_SCRATCH = Path(
    "<workspace-home>/paired_targeted_stress_v2_scratch"
)
ORIGINAL_RUN = (
    BASE / "runs/open_frontier_paired_bugbank_targeted_stress_v1_20260904"
)
ORIGINAL_OPS = Path("<workspace-home>/paired_bugbank_targeted_stress_v1_ops")
ORIGINAL_SCRATCH = Path(
    "<workspace-home>/paired_bugbank_targeted_stress_v1_scratch"
)
EXPECTED_STUDY_LABEL = (
    "Hypothesis-generating BugBank-targeted stress test "
    "(never pool with confirmatory or outcome-blind cohorts)"
)
EXPECTED_RECORD_IDS = [
    "targeted_barbados_p33_restricted_induced_ramsey",
    "targeted_esa_triangle_partition_radius1",
    "targeted_esa_hamiltonian_cycle_linear_radius",
    "targeted_esa_dominating_set_linear_radius",
    "targeted_barbados_p31_geodesic_separator",
    "targeted_icalp_unsplittable_two_sided",
]
TARGETED_CURATION_ROOT = BASE / "paired_open_problem_bugbank_targeted_stress_v1"
TARGETED_SOURCE_ROOT = (
    BASE / "paired_open_problem_bugbank_targeted_stress_sources_v1"
)
TARGETED_PREREGISTRATION = TARGETED_CURATION_ROOT / "PREREGISTRATION.json"
TARGETED_ROSTER = TARGETED_CURATION_ROOT / "RANKED_ROSTER.json"
TARGETED_SOURCE_CONTEXT = TARGETED_CURATION_ROOT / "SELECTED_SOURCE_CONTEXT.md"
ORIGINAL_TARGETED_SOURCE_SPEC = TARGETED_SOURCE_ROOT / "bootstrap_spec.json"
TARGETED_SOURCE_SPEC = TARGETED_SOURCE_ROOT / "bootstrap_spec_runtime_v2.json"
TARGETED_RUNTIME_CORRECTION = (
    TARGETED_CURATION_ROOT / "RUNTIME_CORRECTION_AMENDMENT_20260904.json"
)
TARGETED_BOOTSTRAP = SCRIPT.with_name(
    "bootstrap_paired_open_problem_targeted_stress_v2_run.py"
)
RUNNER = SCRIPT.with_name("paired_open_problem_targeted_stress_v2_runner.mjs")
VALIDATOR = SCRIPT.with_name("validate_paired_open_problem_targeted_stress_v2_run.py")
FEEDBACK = SCRIPT.with_name("paired_open_problem_feedback.py")
STOCK_RETRIEVER = SCRIPT.with_name("bugbank_retrieve.py")
BATCH_LAUNCHER = SCRIPT.with_name("run_sealed_paired_open_problem_targeted_stress_v2_batch.sh")
CHECKPOINT_HELPER = SCRIPT.with_name("checkpoint_sealed_paired_open_problem_run.sh")
TARGETED_STRESS_SLURM_LAUNCHER = SCRIPT.with_name("paired_open_problem_targeted_stress_v2.sbatch")

AUDIT_NORMALIZATION_POLICY = "CLERICAL_BINDINGS_ONLY_V1"
MODEL_ISOLATION_POLICY = "BWRAP_EXACT_EVIDENCE_SEALED_PROFILE_V2"
JSON_NUMBER_POLICY = "STRICT_UTF8_UNIQUE_KEYS_FINITE_SAFE_NUMBERS_V1"
NUMERIC_ACCOUNTING_POLICY = "CHECKED_SAFE_INTEGER_TOKENS_AND_FINITE_DURATIONS_V1"
ACCEPTED_COMPLETION_STATUSES = ["COMPLETE", "RECOVERED_COMPLETE"]
REQUIRED_CODEX_VERSION = "codex-cli 0.153.0"


def reviewed_runtime_paths() -> dict[str, Path]:
    """Every repository program bound to the targeted bootstrap/runtime chain."""
    return {
        "targeted_bootstrap": TARGETED_BOOTSTRAP,
        "runner": RUNNER,
        "validator": VALIDATOR,
        "feedback_generator": FEEDBACK,
        "seal_utility": SCRIPT,
        "stock_retriever": STOCK_RETRIEVER,
        "batch_launcher": BATCH_LAUNCHER,
        "checkpoint_helper": CHECKPOINT_HELPER,
        "targeted_stress_slurm_launcher": TARGETED_STRESS_SLURM_LAUNCHER,
    }


def unattended_launch_contract(
        run: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Return and independently check the BugBank-targeted-stress-v1 scheduler environment policy."""
    fixed_environment = {
        "HOME": "<workspace-home>",
        "CODEX_HOME": "<workspace-home>/.codex",
        "USER": "anonymous-user",
        "LOGNAME": "anonymous-user",
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONNOUSERSITE": "1",
        "PAIRED_OPEN_REPO": str(REPO.resolve()),
        "PAIRED_RUN_ROOT": str(run.resolve()),
        "PAIRED_OPS_ROOT": manifest["operations"]["ops_root"],
        "PAIRED_RUNNER": str(RUNNER.resolve()),
        "PAIRED_VALIDATOR": str(VALIDATOR.resolve()),
        "PAIRED_SEAL_UTILITY": str(SCRIPT.resolve()),
        "PAIRED_JOB_LABEL": "paired-targeted-stress-v2",
        "PAIRED_CONCURRENCY": "5",
        "PAIRED_RETRY_SECONDS": "60",
        "PAIRED_WALL_SECONDS": "86400",
        "PAIRED_DRAIN_BEFORE_SECONDS": "4500",
    }
    forbidden = [
        "BASH_ENV", "ENV", "LD_LIBRARY_PATH", "LD_PRELOAD", "NODE_OPTIONS",
        "NODE_PATH", "PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP",
        "PYTHONINSPECT", "PYTHONUSERBASE",
    ]
    runtime_base = {
        key: fixed_environment[key]
        for key in (
            "HOME", "CODEX_HOME", "USER", "LOGNAME", "PATH", "LANG",
            "LC_ALL", "TZ",
        )
    }
    contract = {
        "schema": "paired_open_problem_unattended_launch_v1",
        "scheduler_export": "NIL",
        "submission_environment_policy": "DISCARD_ALL_EXCEPT_SLURM_METADATA",
        "wrapper_exec": "/usr/bin/env -i /usr/bin/bash --noprofile --norc",
        "wrapper_path": str(BATCH_LAUNCHER.resolve()),
        "fixed_wrapper_environment": fixed_environment,
        "dynamic_wrapper_environment": {
            "SLURM_JOB_ID": "scheduler_value_or_literal_not-slurm",
        },
        "explicitly_excluded_submission_variables": forbidden,
        "runtime_child_environment_policy": (
            "EXACT_ENV_I_ALLOWLIST_FOR_PYTHON_NODE_AND_CHECKPOINT_V1"
        ),
        "runtime_child_environments": {
            "base": runtime_base,
            "python": {
                **runtime_base,
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONNOUSERSITE": "1",
                "PYTHONHASHSEED": "0",
            },
            "node_runner_additions": {"PAIRED_OPERATION_LOCK_FD": "8"},
            "checkpoint_additions": {
                "PAIRED_OPEN_REPO": str(REPO.resolve()),
                "PAIRED_OPERATION_LOCK_FD": "8",
            },
        },
        "pre_namespace_authentication": {
            "manifest_selection": (
                "EXACT_TARGETED_RUN_MANIFEST_ONLY_EXTENSION_MANIFEST_FORBIDDEN"
            ),
            "seal_utility_selection": "PACKAGE_SPECIFIC_REPOSITORY_PATH_BEFORE_EXECUTION",
            "authenticated_path_bindings": [
                "manifest", "runner", "validator", "seal_utility",
            ],
            "namespace_mutation_order": (
                "AFTER_SUCCESSFUL_SEAL_AND_EXACT_BINDING_MATCH"
            ),
            "canonical_path_policy": (
                "PRECREATE_REALPATH_M_THEN_POSTCREATE_REALPATH_BEFORE_CHMOD"
            ),
        },
        "validator_report_handshake": {
            "prior_report_policy": (
                "PRESERVE_FOR_VALIDATION_AND_REQUIRE_ATOMIC_NEW_INODE_PUBLICATION"
            ),
            "fresh_plain_canonical_report_required": True,
            "accepted_exit_report_pairs": [
                "0:VALID_COMPLETE", "1:INCOMPLETE", "2:INVALID",
            ],
            "mismatch_policy": "REFUSE_LAUNCH_OR_CHECKPOINT",
        },
    }

    require_plain_file(TARGETED_STRESS_SLURM_LAUNCHER, "BugBank-targeted-stress-v1 Slurm launcher")
    text = TARGETED_STRESS_SLURM_LAUNCHER.read_text(encoding="utf-8")
    if text.count("#SBATCH --export=NIL") != 1:
        raise SealError("BugBank-targeted-stress-v1 Slurm launcher must use exactly --export=NIL")
    if "exec /usr/bin/env -i \\\n" not in text:
        raise SealError("BugBank-targeted-stress-v1 Slurm launcher lacks the exact env -i boundary")
    for key, value in fixed_environment.items():
        if f"  {key}={value} \\\n" not in text:
            raise SealError(
                f"BugBank-targeted-stress-v1 Slurm launcher lacks fixed environment binding {key}"
            )
    if "  SLURM_JOB_ID=\"$slurm_job_id\" \\\n" not in text:
        raise SealError("BugBank-targeted-stress-v1 Slurm launcher lacks the sole dynamic scheduler field")
    if ("  /usr/bin/bash --noprofile --norc \\\n" not in text
            or f"  {BATCH_LAUNCHER.resolve()}\n" not in text):
        raise SealError("BugBank-targeted-stress-v1 Slurm launcher invokes the wrong batch wrapper")
    if re.search(r"\$\{PAIRED_[A-Z_]+", text):
        raise SealError("BugBank-targeted-stress-v1 Slurm launcher permits a PAIRED_* override")
    for name in forbidden:
        if re.search(rf"^\s*(?:export\s+)?{re.escape(name)}=", text, re.MULTILINE):
            raise SealError(f"BugBank-targeted-stress-v1 Slurm launcher imports forbidden {name}")

    require_plain_file(BATCH_LAUNCHER, "shared unattended batch launcher")
    batch_text = BATCH_LAUNCHER.read_text(encoding="utf-8")
    exact_runtime_block = """safe_runtime_env=(
  /usr/bin/env -i
  HOME="$runtime_home"
  CODEX_HOME="$runtime_home/.codex"
  USER=anonymous-user
  LOGNAME=anonymous-user
  PATH=/usr/bin:/bin
  LANG=C.UTF-8
  LC_ALL=C.UTF-8
  TZ=UTC
)"""
    exact_python_block = """safe_python_env=(
  "${safe_runtime_env[@]}"
  PYTHONDONTWRITEBYTECODE=1
  PYTHONNOUSERSITE=1
  PYTHONHASHSEED=0
)"""
    if ("runtime_home=<workspace-home>" not in batch_text
            or exact_runtime_block not in batch_text
            or exact_python_block not in batch_text):
        raise SealError("targeted batch launcher safe environment block changed")
    python_invocations = [
        line for line in batch_text.splitlines() if '"$python_runtime"' in line
    ]
    if (len(python_invocations) != 3
            or any('"${safe_python_env[@]}"' not in line
                   for line in python_invocations)):
        raise SealError("targeted batch launcher has a non-allowlisted Python child")
    required_report_handshake = (
        'validation_report="$run_root/VALIDATION_REPORT.json"',
        'if [[ ! -f "$validation_report" || -L "$validation_report" ]]; then',
        "fresh_report_identity=$(stat -Lc '%d:%i' \"$validation_report\")",
        '"$fresh_report_identity" = "$prior_report_identity"',
        'incomplete_report_status=INCOMPLETE',
        '1) expected_report_status=$incomplete_report_status ;;',
        'if [[ "$report_status" != "$expected_report_status" ]]; then',
    )
    if (any(fragment not in batch_text for fragment in required_report_handshake)
            or batch_text.count("if ! run_fresh_validator; then") != 2):
        raise SealError(
            "targeted batch launcher lacks the exact fresh validator/report handshake"
        )
    required_pre_namespace_authentication = (
        'expected_run_root="$repo/qedbench_certificate_availability_triage/runs/'
        'open_frontier_paired_targeted_stress_v2_20260904"',
        '[[ "$run_root" = "$expected_run_root" ]]',
        '[[ "$PAIRED_OPS_ROOT" = "$expected_ops_root" ]]',
        '[[ ! -e "$extension_manifest" && ! -L "$extension_manifest" ]]',
        "paired_open_problem_targeted_stress_v2_runtime_seal.py",
        '[[ "$seal_utility" = "$expected_seal_utility" ]]',
        '[[ "$manifest" = "$sealed_manifest" ]]',
        '[[ "$runner" = "$sealed_runner" ]]',
        '[[ "$validator" = "$sealed_validator" ]]',
        '[[ "$seal_utility" = "$sealed_seal_utility" ]]',
        'canonical_ops=$(realpath -m -- "$ops_root")',
        'canonical_scratch=$(realpath -m -- "$scratch_root")',
        'resolved_ops=$(realpath "$ops_root")',
        'resolved_scratch=$(realpath "$scratch_root")',
    )
    seal_check_at = batch_text.find(
        '"${safe_python_env[@]}" "$python_runtime" "$seal_utility" \\\n'
        '  check --run-root "$run_root" --quiet'
    )
    manifest_paths_at = batch_text.find(
        'manifest_ops=$(jq -er \'.operations.ops_root\' "$manifest")'
    )
    ops_create_at = batch_text.find('mkdir -p "$ops_root" "$ops_root/logs"')
    if (any(fragment not in batch_text
            for fragment in required_pre_namespace_authentication)
            or min(seal_check_at, manifest_paths_at, ops_create_at) < 0
            or not seal_check_at < manifest_paths_at < ops_create_at):
        raise SealError(
            "targeted batch launcher does not authenticate exact runtime paths "
            "before external namespace mutation"
        )
    if ('"${safe_runtime_env[@]}" PAIRED_OPERATION_LOCK_FD=8 \\\n'
            '    "$node_runtime" "$runner"' not in batch_text):
        raise SealError("shared batch launcher has a non-allowlisted Node child")
    if ('"${safe_runtime_env[@]}" PAIRED_OPEN_REPO="$repo" \\\n'
            '    PAIRED_OPERATION_LOCK_FD=8 "$checkpoint"' not in batch_text):
        raise SealError("shared batch launcher has a non-allowlisted checkpoint child")
    return contract


def isolation_contract() -> dict[str, Any]:
    return {
        "schema": "paired_open_problem_bwrap_contract_v2",
        "outer_namespaces": ["pid", "ipc", "uts"],
        "outer_network_namespace": "host_for_codex_transport_only",
        "inner_codex_authorization": {
            "sandbox_cli_flag": None,
            "default_permissions": "sealed",
            "permission_profile": {
                "extends": ":workspace",
                "filesystem": {"/run/codex-home/auth.json": "deny"},
                "network": {"enabled": False},
            },
        },
        "ignore_user_config": True,
        "ignore_workspace_rules": True,
        "web_search": "disabled",
        "model_tool_shell_environment": {
            "inherit": "none", "exclude": ["*"],
            "set": {
                "PATH": "/runtime/vendor/codex-path:/usr/bin:/bin",
                "HOME": "exact_cell_scratch", "TMPDIR": "/tmp",
                "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            },
        },
        "allow_login_shell": False,
        "shell_snapshot": False,
        "strict_config": True,
        "fixed_mounts": [
            {"kind": "ro-bind", "source": "/usr", "destination": "/usr"},
            {"kind": "symlink", "source": "usr/bin", "destination": "/bin"},
            {"kind": "symlink", "source": "usr/sbin", "destination": "/sbin"},
            {"kind": "symlink", "source": "usr/lib", "destination": "/lib"},
            {"kind": "symlink", "source": "usr/lib64", "destination": "/lib64"},
            {"kind": "ro-bind", "source": "/etc/pki", "destination": "/etc/pki"},
            {"kind": "ro-bind", "source": "/etc/ssl", "destination": "/etc/ssl"},
            {"kind": "ro-bind", "source": "/etc/resolv.conf", "destination": "/etc/resolv.conf"},
            {"kind": "ro-bind", "source": "/etc/hosts", "destination": "/etc/hosts"},
            {"kind": "ro-bind", "source": "/etc/nsswitch.conf", "destination": "/etc/nsswitch.conf"},
            {"kind": "proc", "destination": "/proc"},
            {"kind": "dev", "destination": "/dev"},
            {"kind": "tmpfs", "destination": "/tmp"},
        ],
        "dynamic_mounts": [
            {"kind": "ro-bind", "source": "sealed_native_bundle", "destination": "/runtime/vendor"},
            {"kind": "dir", "destination": "/isolated/home"},
            {"kind": "tmpfs", "destination": "/run/codex-home"},
            {"kind": "file-from-fd-3", "source": "runtime_auth_json_unhashed", "destination": "/run/codex-home/auth.json"},
            {"kind": "bind", "source": "exact_cell_scratch", "destination": "same_absolute_path"},
            {"kind": "ro-bind-each", "source": "exact_call_evidence", "destination": "same_absolute_path"},
        ],
        "exact_call_evidence": [
            "bound_output_schema", "bound_source_input", "immediate_parent_draft_when_applicable",
            "immediate_parent_audit_for_revision", "current_bugbank_receipt_for_treated_revision",
        ],
        "outer_spawn_environment": {
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            "PATH": "/runtime/vendor/codex-path:/usr/bin:/bin",
        },
        "sandbox_environment": {
            "HOME": "/isolated/home", "CODEX_HOME": "/run/codex-home",
            "PATH": "/runtime/vendor/codex-path:/usr/bin:/bin",
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "NO_COLOR": "1",
        },
        "forbidden_mounts": ["repository_root", "bugbank_database", "other_arm", "prior_run", "user_home"],
        "model_output_flow": "model_writes_exact_scratch_then_host_validates_and_atomically_finalizes",
        "scratch_retry_policy": "exclusive_lock_then_empty_exact_cell_scratch_before_each_new_call",
        "host_publication_temporary_policy": (
            "private_external_scratch_same_filesystem_fsync_then_atomic_rename_or_link"
        ),
        "auth_policy": (
            "bwrap_file_from_fd3_parent_cli_only_model_tools_denied_by_profile"
        ),
        "auth_transport_fd_model_tool_access": "closed",
    }


def validate_isolation_host() -> None:
    for row in isolation_contract()["fixed_mounts"]:
        source = row.get("source")
        if row["kind"] == "ro-bind":
            if type(source) is not str or not Path(source).exists():
                raise SealError(f"required isolation mount source is absent: {source}")

MANIFEST_SCHEMA = "paired_open_problem_run_manifest_v1"
SEAL_SCHEMA = "paired_open_problem_runtime_seal_v1"
PROTOCOL_ID = "WHOLE_PROOF_FIRST_SOLUTION_V1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class SealError(RuntimeError):
    """A required runtime identity or isolation condition did not hold."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SealError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_nonfinite_json(token: str) -> Any:
    raise SealError(f"non-finite JSON number {token}")


def parse_finite_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise SealError(f"non-finite JSON number {token}")
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_bytes().decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_json_float,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SealError(f"cannot read strict JSON {path}: {error}") from error
    if type(value) is not dict:
        raise SealError(f"top-level JSON must be an object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise SealError(f"not canonical JSON: {error}") from error


def pretty_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2
        ).encode("utf-8") + b"\n"
    )


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_plain_file(path: Path, label: str) -> None:
    try:
        info = path.lstat()
    except OSError as error:
        raise SealError(f"{label} is unavailable: {path}: {error}") from error
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise SealError(f"{label} must be a regular non-symlink file: {path}")


def safe_run_root(value: Path) -> Path:
    root = value.resolve()
    if root != EXPECTED_RUN.resolve(strict=False):
        raise SealError(
            "run root differs from the frozen BugBank-targeted stress namespace"
        )
    if root == ACTIVE_RUN.resolve() or ACTIVE_RUN.resolve() in root.parents:
        raise SealError("fresh runtime refuses the active/historical paired-v2 run")
    if not root.is_dir() or root.is_symlink():
        raise SealError(f"run root must be a real directory: {root}")
    return root


def path_overlaps(left: Path, right: Path) -> bool:
    left = left.resolve(strict=False)
    right = right.resolve(strict=False)
    return left == right or left in right.parents or right in left.parents


def run_relative_file(run: Path, raw: Any, label: str) -> Path:
    if type(raw) is not str or not raw:
        raise SealError(f"{label}.path must be a nonempty string")
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise SealError(f"{label}.path must be safe and run-relative")
    path = run / relative
    require_plain_file(path, label)
    try:
        path.resolve().relative_to(run.resolve())
    except ValueError as error:
        raise SealError(f"{label}.path escapes the run root") from error
    cursor = path
    while cursor != run:
        if cursor.is_symlink():
            raise SealError(f"{label}.path traverses a symlink: {cursor}")
        cursor = cursor.parent
    return path.resolve()


def check_binding(run: Path, binding: Any, label: str) -> Path:
    if type(binding) is not dict or set(binding) != {"path", "sha256", "size_bytes"}:
        raise SealError(f"{label} must be an exact path/hash/size binding")
    if type(binding["sha256"]) is not str or SHA256_RE.fullmatch(binding["sha256"]) is None:
        raise SealError(f"{label}.sha256 is invalid")
    if type(binding["size_bytes"]) is not int or binding["size_bytes"] < 0:
        raise SealError(f"{label}.size_bytes is invalid")
    path = run_relative_file(run, binding["path"], label)
    if path.stat().st_size != binding["size_bytes"] or sha_file(path) != binding["sha256"]:
        raise SealError(f"{label} does not match current bytes")
    return path


def manifest_bindings(manifest: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    yield "protocol.document", manifest["protocol"]["document"]
    yield "problem_ids_artifact", manifest["problem_ids_artifact"]
    for name, binding in sorted(manifest["schemas"].items()):
        yield f"schemas.{name}", binding
    yield "bootstrap.source_spec", manifest["bootstrap"]["source_spec"]
    yield "bootstrap.implementation", manifest["bootstrap"]["implementation"]
    for key in ("template_readme", "run_readme", "operations_readme"):
        yield f"bootstrap.{key}", manifest["bootstrap"][key]
    for index, record in enumerate(manifest["records"]):
        prefix = f"records[{index}]"
        yield f"{prefix}.input", record["input"]
        for source_index, source in enumerate(record["source_documents"]):
            yield f"{prefix}.source_documents[{source_index}].snapshot", source["snapshot"]
            yield (
                f"{prefix}.source_documents[{source_index}].extracted_text.artifact",
                source["extracted_text"]["artifact"],
            )
        yield f"{prefix}.status_search.log", record["status_search"]["log"]
        yield f"{prefix}.semantic_audit.artifact", record["semantic_audit"]["artifact"]


def validate_manifest(run: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = run / "RUN_MANIFEST.json"
    require_plain_file(manifest_path, "run manifest")
    manifest = load_json(manifest_path)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise SealError(f"manifest schema must be {MANIFEST_SCHEMA}")
    if manifest.get("run_id") != run.name or ID_RE.fullmatch(run.name) is None:
        raise SealError("manifest run_id must match the safe run-root basename")
    if (manifest.get("run_id") != EXPECTED_RUN_ID
            or manifest.get("study_label") != EXPECTED_STUDY_LABEL):
        raise SealError("manifest is not the frozen BugBank-targeted stress study")
    if (manifest.get("status") != "BOOTSTRAPPED_AWAITING_RUNTIME_SEAL"
            or manifest.get("launch_authorized") is not False):
        raise SealError("immutable bootstrap manifest must remain non-launchable")
    unsigned = copy.deepcopy(manifest)
    payload_hash = unsigned.pop("manifest_payload_sha256", None)
    if payload_hash != sha_bytes(canonical_bytes(unsigned)):
        raise SealError("manifest_payload_sha256 mismatch")
    protocol = manifest.get("protocol")
    execution = manifest.get("execution")
    bugbank = manifest.get("bugbank")
    operations = manifest.get("operations")
    if type(protocol) is not dict or protocol.get("id") != PROTOCOL_ID:
        raise SealError("unexpected protocol identity")
    required_protocol = {
        "whole_proof_claim_cap": None,
        "bugbank_query_basis": "claim + two newlines + proof_sketch",
        "retrieval_k_per_claim": 3,
        "first_strict_full_audit_stops_either_arm": True,
        "plain_full_solution_requires_budget_match": False,
        "plain_inconclusive_endpoint_requires_budget_match": True,
    }
    if any(protocol.get(key) != value for key, value in required_protocol.items()):
        raise SealError("manifest does not encode the corrected stopping/query protocol")
    if (type(execution) is not dict or type(execution.get("model")) is not str
            or not execution["model"] or type(execution.get("reasoning_effort")) is not str
            or not execution["reasoning_effort"] or execution.get("arms") != ["bugbank", "plain"]
            or execution.get("shared_neutral_baseline") is not True
            or execution.get("model_network_access") is not False
            or execution.get("runtime_seal_required") is not True
            or type(execution.get("max_iterations")) is not int
            or execution["max_iterations"] < 1):
        raise SealError("manifest execution contract is invalid")
    if (type(bugbank) is not dict or bugbank.get("retrieval_k") != 3
            or type(bugbank.get("database_sha256")) is not str
            or SHA256_RE.fullmatch(bugbank["database_sha256"]) is None):
        raise SealError("manifest BugBank contract is invalid")
    if type(operations) is not dict:
        raise SealError("manifest operations contract is invalid")
    for key in ("ops_root", "scratch_root", "stop_file"):
        if type(operations.get(key)) is not str or not Path(operations[key]).is_absolute():
            raise SealError(f"manifest operations.{key} must be absolute")
    if Path(operations["stop_file"]) != Path(operations["ops_root"]) / "STOP_REQUESTED":
        raise SealError("stop_file must be the isolated ops-root STOP_REQUESTED file")
    if (Path(operations["ops_root"]) != EXPECTED_OPS
            or Path(operations["scratch_root"]) != EXPECTED_SCRATCH):
        raise SealError("manifest operations namespaces differ from the frozen study")
    protected = (run, REPO, ACTIVE_RUN, ACTIVE_OPS)
    for key in ("ops_root", "scratch_root"):
        if any(path_overlaps(Path(operations[key]), item) for item in protected):
            raise SealError(f"operations.{key} overlaps protected storage")
    if path_overlaps(Path(operations["ops_root"]), Path(operations["scratch_root"])):
        raise SealError("ops and scratch namespaces overlap")

    roster = manifest.get("problem_ids")
    records = manifest.get("records")
    if (type(roster) is not list or not roster or len(roster) != len(set(roster))
            or any(type(item) is not str or ID_RE.fullmatch(item) is None for item in roster)
            or type(records) is not list
            or roster != [record.get("record_id") for record in records]
            or manifest.get("problem_count") != len(roster)):
        raise SealError("manifest roster is inconsistent")
    if roster != EXPECTED_RECORD_IDS or manifest.get("problem_count") != 6:
        raise SealError("manifest roster differs from the frozen targeted six")

    checked: list[dict[str, Any]] = []
    for label, binding in manifest_bindings(manifest):
        check_binding(run, binding, label)
        checked.append({"label": label, **binding})
    problem_ids_path = check_binding(
        run, manifest["problem_ids_artifact"], "problem_ids_artifact"
    )
    if load_json_array(problem_ids_path) != roster:
        raise SealError("problem_ids artifact differs from manifest roster")
    for record in records:
        input_path = check_binding(run, record["input"], f"input {record['record_id']}")
        input_value = load_json(input_path)
        expected_fields = record.get("solver_input_top_level_fields")
        if (type(expected_fields) is not list
                or set(input_value) != set(expected_fields)
                or input_value.get("record_id") != record["record_id"]
                or input_value.get("target") != record.get("target")):
            raise SealError(f"solver input contract mismatch for {record['record_id']}")
    return manifest, checked


def load_json_array(path: Path) -> list[Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_json_float,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SealError(f"cannot read JSON array {path}: {error}") from error
    if type(value) is not list:
        raise SealError(f"expected JSON array: {path}")
    return value


def external_binding(path: Path) -> dict[str, Any]:
    require_plain_file(path, "runtime file")
    return {
        "path": str(path.resolve()),
        "sha256": sha_file(path),
        "size_bytes": path.stat().st_size,
    }


def command(*arguments: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        arguments, cwd=REPO if cwd is None else cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode != 0:
        raise SealError(
            f"command failed ({' '.join(arguments)}): "
            f"{(result.stderr or result.stdout).strip()}"
        )
    return result.stdout.strip()


def origin_main_exact_binding(path: Path, label: str) -> dict[str, Any]:
    """Require exact bytes at the current local ``origin/main`` tip.

    This is deliberately checked from Git objects, not from a self-declared
    hash in the JSON being authenticated.  The seal itself is created first,
    reviewed/pushed, and becomes launchable only when its exact bytes and the
    manifest coexist at the same current remote-tracking tip.  This is honest-
    checker self-attestation, not a defense against a malicious Git server.
    """
    require_plain_file(path, label)
    try:
        relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError as error:
        raise SealError(f"{label} is outside repository: {path}") from error
    tip = command("git", "rev-parse", "origin/main^{commit}")
    result = subprocess.run(
        ["git", "show", f"{tip}:{relative}"], cwd=REPO,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode != 0 or result.stdout != path.read_bytes():
        raise SealError(
            f"{label} current bytes are not exact at current origin/main tip"
        )
    return {
        **external_binding(path), "repository_path": relative,
        "origin_main_commit": tip,
    }


def committed_runtime_binding(path: Path, revision: str) -> dict[str, Any]:
    binding = external_binding(path)
    try:
        relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError as error:
        raise SealError(f"runtime file is outside repository: {path}") from error
    try:
        committed = subprocess.run(
            ["git", "show", f"{revision}:{relative}"], cwd=REPO,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
    except OSError as error:
        raise SealError(f"cannot inspect repository revision: {error}") from error
    if committed.returncode != 0 or committed.stdout != path.read_bytes():
        raise SealError(f"runtime file does not exactly match {revision}:{relative}")
    return {**binding, "repository_path": relative}


def targeted_preregistration_inventory(
        manifest: Mapping[str, Any], revision: str) -> dict[str, Any]:
    """Validate and bind the targeted, selection-biased reporting stratum."""
    module_spec = importlib.util.spec_from_file_location(
        "targeted_runtime_v2_bootstrap", TARGETED_BOOTSTRAP
    )
    if module_spec is None or module_spec.loader is None:
        raise SealError("cannot load the runtime-v2 targeted bootstrap validator")
    bootstrap_validator = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(bootstrap_validator)
    try:
        bootstrap_validator.validate_freeze()
    except bootstrap_validator.TargetedBootstrapError as error:
        raise SealError(f"targeted runtime correction is invalid: {error}") from error
    for path, label in (
            (TARGETED_PREREGISTRATION, "targeted preregistration"),
            (TARGETED_ROSTER, "targeted ranked roster"),
            (TARGETED_SOURCE_CONTEXT, "targeted source context"),
            (ORIGINAL_TARGETED_SOURCE_SPEC, "original targeted source specification"),
            (TARGETED_SOURCE_SPEC, "runtime-corrected targeted source specification"),
            (TARGETED_RUNTIME_CORRECTION, "targeted runtime correction")):
        require_plain_file(path, label)

    preregistration = load_json(TARGETED_PREREGISTRATION)
    if (preregistration.get("schema") !=
            "qedbench.paired_open_problem_bugbank_targeted_stress_preregistration.v1"
            or preregistration.get("study_id") != "BUGBANK_TARGETED_STRESS_V1"
            or preregistration.get("reporting_class") !=
            "HYPOTHESIS_GENERATING_BUGBANK_TARGETED_STRESS_TEST"):
        raise SealError("targeted preregistration identity changed")
    attestation = preregistration.get("outcome_access_attestation")
    if (type(attestation) is not dict
            or attestation.get("solver_call_before_freeze") is not False
            or attestation.get("model_auditor_call_before_freeze") is not False
            or attestation.get(
                "experimental_per_claim_bugbank_receipt_existed_before_freeze"
            ) is not False
            or attestation.get("arm_outcome_existed_before_freeze") is not False
            or attestation.get("static_bugbank_reconnaissance_before_freeze") is not True):
        raise SealError("targeted pre-outcome selection disclosure changed")

    paired = preregistration.get("paired_run")
    if (type(paired) is not dict
            or paired.get("run_root") !=
            ORIGINAL_RUN.relative_to(REPO).as_posix()
            or paired.get("operations_root") != str(ORIGINAL_OPS)
            or paired.get("scratch_root") != str(ORIGINAL_SCRATCH)
            or paired.get("protocol_id") != PROTOCOL_ID
            or paired.get("initial_iteration_cap") != 50
            or paired.get("arms") != ["bugbank", "plain"]
            or paired.get("retrieval_k_per_claim") != 3):
        raise SealError("targeted preregistration run contract changed")

    roster_binding = preregistration.get("roster")
    source_context_binding = preregistration.get("source_context")
    source_package_binding = preregistration.get("source_package")
    expected_roster_path = TARGETED_ROSTER.relative_to(REPO).as_posix()
    expected_context_path = TARGETED_SOURCE_CONTEXT.relative_to(REPO).as_posix()
    expected_spec_path = ORIGINAL_TARGETED_SOURCE_SPEC.relative_to(REPO).as_posix()
    if (type(roster_binding) is not dict
            or roster_binding.get("count") != 6
            or roster_binding.get("ordered_record_ids") != EXPECTED_RECORD_IDS
            or roster_binding.get("path") != expected_roster_path
            or roster_binding.get("sha256") != sha_file(TARGETED_ROSTER)
            or roster_binding.get("size_bytes") != TARGETED_ROSTER.stat().st_size):
        raise SealError("targeted roster binding changed")
    if (type(source_context_binding) is not dict
            or source_context_binding.get("path") != expected_context_path
            or source_context_binding.get("sha256") != sha_file(TARGETED_SOURCE_CONTEXT)
            or source_context_binding.get("size_bytes") !=
            TARGETED_SOURCE_CONTEXT.stat().st_size):
        raise SealError("targeted source-context binding changed")
    if (type(source_package_binding) is not dict
            or source_package_binding.get("bootstrap_spec_path") != expected_spec_path
            or source_package_binding.get("bootstrap_spec_sha256") !=
            sha_file(ORIGINAL_TARGETED_SOURCE_SPEC)
            or source_package_binding.get("bootstrap_spec_size_bytes") !=
            ORIGINAL_TARGETED_SOURCE_SPEC.stat().st_size):
        raise SealError("targeted source-package binding changed")

    reporting = preregistration.get("reporting_boundary")
    if (type(reporting) is not dict
            or any(type(reporting.get(key)) is not dict
                   or reporting[key].get("pooling_allowed") is not False
                   for key in (
                       "confirmatory", "outcome_blind_internet_six",
                       "targeted_stress",
                   ))):
        raise SealError("targeted non-pooling boundary changed")

    roster = load_json(TARGETED_ROSTER)
    rows = roster.get("roster") if type(roster) is dict else None
    if (roster.get("reporting_class") !=
            "HYPOTHESIS_GENERATING_BUGBANK_TARGETED_STRESS_TEST"
            or type(rows) is not list
            or [row.get("rank") for row in rows] != list(range(1, 7))
            or [row.get("record_id") for row in rows] != EXPECTED_RECORD_IDS):
        raise SealError("targeted ranked roster content changed")

    source_spec_binding = manifest.get("bootstrap", {}).get("source_spec")
    run_source_spec = check_binding(
        EXPECTED_RUN, source_spec_binding, "manifest targeted source spec"
    )
    if (run_source_spec.read_bytes() != TARGETED_SOURCE_SPEC.read_bytes()
            or source_spec_binding.get("sha256") != sha_file(TARGETED_SOURCE_SPEC)
            or manifest.get("problem_ids") != EXPECTED_RECORD_IDS):
        raise SealError("run does not byte-bind the targeted source package")

    artifacts = {
        "preregistration": committed_runtime_binding(
            TARGETED_PREREGISTRATION, revision
        ),
        "ranked_roster": committed_runtime_binding(TARGETED_ROSTER, revision),
        "source_context": committed_runtime_binding(
            TARGETED_SOURCE_CONTEXT, revision
        ),
        "original_source_specification": committed_runtime_binding(
            ORIGINAL_TARGETED_SOURCE_SPEC, revision
        ),
        "runtime_source_specification": committed_runtime_binding(
            TARGETED_SOURCE_SPEC, revision
        ),
        "runtime_correction_amendment": committed_runtime_binding(
            TARGETED_RUNTIME_CORRECTION, revision
        ),
    }
    return {
        "study_id": "BUGBANK_TARGETED_STRESS_V1",
        "reporting_class":
        "HYPOTHESIS_GENERATING_BUGBANK_TARGETED_STRESS_TEST",
        "never_pool_with_confirmatory_36_or_58": True,
        "never_pool_with_outcome_blind_six": True,
        "static_bugbank_reconnaissance_disclosed": True,
        "no_pre_freeze_experimental_outcomes": True,
        "artifacts": artifacts,
    }


def validate_manifest_creation_anchor(
        manifest_binding: Mapping[str, Any], current_binding: Mapping[str, Any],
        manifest_path: Path) -> None:
    """Validate the pre-seal tip without making it a circular current tip."""
    if manifest_binding.get("repository_path") != current_binding["repository_path"]:
        raise SealError("sealed manifest repository path mismatch")
    creation_anchor = manifest_binding.get("origin_main_commit")
    if type(creation_anchor) is not str:
        raise SealError("sealed manifest creation anchor is missing")
    creation_anchor = command("git", "rev-parse", f"{creation_anchor}^{{commit}}")
    current_tip = current_binding["origin_main_commit"]
    if subprocess.run(
            ["git", "merge-base", "--is-ancestor", creation_anchor, current_tip],
            cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False).returncode != 0:
        raise SealError("sealed manifest creation anchor is not an ancestor of current tip")
    creation_bytes = subprocess.run(
        ["git", "show", f"{creation_anchor}:{current_binding['repository_path']}"],
        cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if (creation_bytes.returncode != 0
            or creation_bytes.stdout != manifest_path.read_bytes()):
        raise SealError("manifest bytes differ from their sealed creation anchor")


def _resolved_executable(executable: str, label: str) -> tuple[Path, Path]:
    located = shutil.which(executable)
    if located is None:
        raise SealError(f"{label} is unavailable: {executable}")
    launcher = Path(located).resolve()
    require_plain_file(launcher, label)
    return Path(located), launcher


def _bundle_inventory(root: Path) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    try:
        root_info = root.lstat()
    except OSError as error:
        raise SealError(f"model native bundle is unavailable: {root}") from error
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise SealError("model native bundle root must be a plain directory")
    paths = [root, *sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    )]
    for path in paths:
        info = path.lstat()
        relative = "." if path == root else path.relative_to(root).as_posix()
        if stat.S_ISLNK(info.st_mode):
            raise SealError(f"model native bundle contains a symlink: {relative}")
        if stat.S_ISDIR(info.st_mode):
            inventory.append({
                "path": relative, "kind": "directory",
                "mode": stat.S_IMODE(info.st_mode),
            })
        elif stat.S_ISREG(info.st_mode):
            inventory.append({
                "path": relative, "kind": "file",
                "mode": stat.S_IMODE(info.st_mode),
                "sha256": sha_file(path), "size_bytes": info.st_size,
            })
        else:
            raise SealError(
                f"model native bundle contains a non-plain entry: {relative}"
            )
    required_files = {
        "bin/codex", "bin/codex-code-mode-host", "codex-package.json",
        "codex-path/rg", "codex-resources/bwrap",
        "codex-resources/zsh/bin/zsh",
    }
    actual_files = {
        row["path"] for row in inventory if row["kind"] == "file"
    }
    if actual_files != required_files:
        raise SealError(
            "model native bundle file envelope changed; "
            f"missing={sorted(required_files - actual_files)}, "
            f"extra={sorted(actual_files - required_files)}"
        )
    return inventory


def model_cli_binding(executable: str) -> dict[str, Any]:
    located, launcher = _resolved_executable(executable, "model CLI launcher")
    native = launcher
    if launcher.read_bytes()[:4] != b"\x7fELF":
        # The npm entry point is JavaScript.  Resolve the single platform
        # package ELF and seal/execute that binary directly, so PATH cannot
        # select different code at launch time.
        roots: list[Path] = []
        if launcher.name == "codex.js" and launcher.parent.name == "bin":
            roots.append(launcher.parent.parent)
        candidates: list[Path] = []
        for root in roots:
            candidates.extend(
                path for path in root.glob(
                    "node_modules/@openai/codex-*/vendor/*/bin/codex"
                ) if path.is_file() and path.read_bytes()[:4] == b"\x7fELF"
            )
        if len(candidates) != 1:
            raise SealError(
                f"expected exactly one native Codex ELF behind {launcher}, "
                f"found {len(candidates)}"
            )
        native = candidates[0].resolve()
    require_plain_file(native, "native model CLI")
    if native.read_bytes()[:4] != b"\x7fELF":
        raise SealError("sealed model CLI is not a native ELF executable")
    bundle_root = native.parent.parent.resolve()
    if native != bundle_root / "bin/codex":
        raise SealError("native model CLI is not at bundle/bin/codex")
    inventory = _bundle_inventory(bundle_root)
    version = command(str(native), "--version", cwd=REPO)
    if version != REQUIRED_CODEX_VERSION:
        raise SealError(
            f"model CLI version must be {REQUIRED_CODEX_VERSION!r}, got {version!r}"
        )
    return {
        **external_binding(native),
        "invoked_as": executable,
        "launcher": external_binding(launcher),
        "version_stdout": version,
        "native_bundle_root": str(bundle_root),
        "native_bundle_inventory": inventory,
        "native_bundle_inventory_sha256": sha_bytes(canonical_bytes(inventory)),
    }


def python_runtime_binding(executable: str) -> dict[str, Any]:
    _located, path = _resolved_executable(executable, "Python runtime")
    probe = command(
        str(path), "-c",
        "import json,platform,sqlite3,sys;print(json.dumps({"
        "'implementation':platform.python_implementation(),"
        "'python_version':platform.python_version(),"
        "'sqlite_version':sqlite3.sqlite_version,"
        "'sqlite_module_version':getattr(sqlite3,'version',None),"
        "'executable':sys.executable},sort_keys=True,separators=(',',':')))",
    )
    try:
        runtime = json.loads(
            probe, object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_json_float,
        )
    except json.JSONDecodeError as error:
        raise SealError("Python runtime probe returned invalid JSON") from error
    return {
        **external_binding(path), "invoked_as": executable,
        "version_stdout": command(str(path), "--version"),
        "runtime": runtime,
    }


def node_runtime_binding(executable: str) -> dict[str, Any]:
    _located, path = _resolved_executable(executable, "Node runtime")
    return {
        **external_binding(path), "invoked_as": executable,
        "version_stdout": command(str(path), "--version"),
    }


def bubblewrap_binding(executable: str) -> dict[str, Any]:
    _located, path = _resolved_executable(executable, "bubblewrap runtime")
    return {
        **external_binding(path), "invoked_as": executable,
        "version_stdout": command(str(path), "--version"),
    }


def flock_binding() -> dict[str, Any]:
    """Bind the exact non-PATH executable used by the mutation gate."""
    path = Path("/usr/bin/flock")
    with tempfile.TemporaryDirectory(
            prefix="paired-bugbank-targeted-stress-flock-probe-") as raw:
        lock_path = Path(raw) / "operation.lock"
        owner = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        competitor = -1
        try:
            acquired = subprocess.run(
                [str(path), "-n", str(owner)], pass_fds=(owner,),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            if acquired.returncode != 0:
                raise SealError(
                    "flock could not acquire an inherited open-file description"
                )
            competitor = os.open(lock_path, os.O_RDONLY | os.O_NOFOLLOW)
            conflict = subprocess.run(
                [str(path), "-n", str(competitor)], pass_fds=(competitor,),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            if conflict.returncode != 1:
                raise SealError(
                    "flock did not exclude a separately opened file description"
                )
        finally:
            if competitor >= 0:
                os.close(competitor)
            os.close(owner)
    return {
        **external_binding(path), "invoked_as": str(path),
        "version_stdout": command(str(path), "--version"),
        "inherited_ofd_acquire_probe": "PASS",
        "separate_ofd_conflict_exit_code": 1,
    }


def mutation_gate_contract(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "paired_open_problem_mutation_gate_v1",
        "environment_variable": "PAIRED_OPERATION_LOCK_FD",
        "required_fd": 8,
        "lock_path": str(
            (Path(manifest["operations"]["ops_root"]) / "operation.lock").resolve()
        ),
        "required_for": "every_non_dry_run_non_validate_runner_invocation",
        "path_policy": "plain_regular_non_symlink_exact_dev_inode_and_proc_fd_target",
        "acquisition": "sealed_flock_nonblocking_on_inherited_open_description",
        "lifetime": "invoking_parent_retains_fd_for_full_mutating_operation",
    }


def _permission_profile_config_arguments(workspace: str) -> list[str]:
    shell_set = (
        '{PATH="/runtime/vendor/codex-path:/usr/bin:/bin",'
        f'HOME={json.dumps(workspace)},TMPDIR="/tmp",'
        'LANG="C.UTF-8",LC_ALL="C.UTF-8"}'
    )
    return [
        "-c", 'web_search="disabled"',
        "-c", 'shell_environment_policy.inherit="none"',
        "-c", 'shell_environment_policy.exclude=["*"]',
        "-c", f"shell_environment_policy.set={shell_set}",
        "-c", "allow_login_shell=false",
        "-c", "features.shell_snapshot=false",
        "-c", 'default_permissions="sealed"',
        "-c", 'permissions.sealed.extends=":workspace"',
        "-c", (
            'permissions.sealed.filesystem={'
            '"/run/codex-home/auth.json"="deny"}'
        ),
        "-c", "permissions.sealed.network.enabled=false",
    ]


def permission_profile_probe(
        cli: dict[str, Any], bubblewrap_binding_value: dict[str, Any]
        ) -> dict[str, Any]:
    """Run a model-free, strict-config probe of the exact inner policy.

    A dummy credential is inherited as a file descriptor by outer bubblewrap,
    consumed into the private tmpfs, and must be both path-denied and
    descriptor-inaccessible to the probed tool.  A separate deliberately
    missing-provider exec proves that every scientific override is accepted
    under ``--strict-config`` without making an API request.
    """
    native = Path(cli["path"]).resolve()
    bundle = Path(cli["native_bundle_root"]).resolve()
    try:
        native_inside = Path("/runtime/vendor") / native.relative_to(bundle)
    except ValueError as error:
        raise SealError("native model CLI escapes its sealed bundle") from error
    bwrap = Path(bubblewrap_binding_value["path"]).resolve()
    contract_hash = sha_bytes(canonical_bytes(isolation_contract()))
    with tempfile.TemporaryDirectory(prefix="paired-open-profile-probe-") as raw:
        scratch = Path(raw).resolve()
        evidence = scratch / "outside-work-evidence.txt"
        evidence.write_text("SEALED_PROFILE_EVIDENCE_V1\n", encoding="utf-8")
        work = scratch / "work"
        work.mkdir()
        output = work / "probe-write.txt"
        auth_path = scratch / "dummy-auth.json"
        auth_path.write_bytes(
            b'{"access_token":"PROFILE_PROBE_MUST_STAY_HIDDEN"}\n'
        )
        os.chmod(auth_path, 0o600)
        strict_home = scratch / "strict-config-home"
        strict_home.mkdir(mode=0o700)
        missing_provider = "paired-bugbank-targeted-stress-deliberately-missing"
        strict_arguments = [str(native), "--strict-config"]
        strict_arguments.extend(_permission_profile_config_arguments("/work"))
        strict_arguments.extend([
            "-c", f'model_provider="{missing_provider}"',
            "exec", "--ignore-user-config", "--ignore-rules",
            "--skip-git-repo-check", "--ephemeral", "config parse probe",
        ])
        strict_result = subprocess.run(
            strict_arguments, cwd=work,
            env={
                "HOME": str(strict_home), "CODEX_HOME": str(strict_home),
                "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                "PATH": "/usr/bin:/bin",
            },
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            timeout=30, check=False,
        )
        strict_diagnostic = strict_result.stderr + strict_result.stdout
        if (strict_result.returncode != 1
                or f"Model provider `{missing_provider}` not found" not in strict_diagnostic
                or "unknown configuration field" in strict_diagnostic):
            raise SealError(
                "scientific exec strict-config probe failed: "
                + strict_diagnostic.strip()[-2000:]
            )
        probe_program = "\n".join([
            "import json, os, pathlib, socket",
            "transport_fd = __TRANSPORT_FD__",
            "def permission_denied(path):",
            "    try:",
            "        pathlib.Path(path).read_bytes()",
            "        return False",
            "    except PermissionError:",
            "        return True",
            "    except OSError:",
            "        return False",
            "def unavailable(path):",
            "    try:",
            "        pathlib.Path(path).read_bytes()",
            "        return False",
            "    except OSError:",
            "        return True",
            "checks = {}",
            "checks['exact_evidence_read'] = pathlib.Path('/evidence/probe.txt').read_text() == 'SEALED_PROFILE_EVIDENCE_V1\\n'",
            "pathlib.Path('/work/probe-write.txt').write_text('SEALED_PROFILE_WRITE_V1\\n')",
            "checks['exact_scratch_write'] = pathlib.Path('/work/probe-write.txt').read_text() == 'SEALED_PROFILE_WRITE_V1\\n'",
            "checks['auth_direct_denied'] = permission_denied('/run/codex-home/auth.json')",
            "checks['auth_procroot_denied'] = permission_denied('/proc/self/root/run/codex-home/auth.json')",
            "try:",
            "    os.fstat(transport_fd)",
            "    checks['auth_transport_fd_closed'] = False",
            "except OSError:",
            "    checks['auth_transport_fd_closed'] = True",
            f"checks['host_repository_hidden'] = unavailable({str(RUNNER)!r})",
            "checks['environment_canaries_absent'] = all(os.environ.get(k) is None for k in ('PAIRED_SECRET_CANARY','PAIRED_TOKEN_CANARY','CODEX_HOME'))",
            "checks['safe_environment_exact'] = all(os.environ.get(k) == v for k, v in {'PATH':'/runtime/vendor/codex-path:/usr/bin:/bin','HOME':'/work','TMPDIR':'/tmp','LANG':'C.UTF-8','LC_ALL':'C.UTF-8'}.items())",
            "try:",
            "    sock = socket.socket()",
            "    sock.close()",
            "    checks['network_socket_denied'] = False",
            "except (OSError, PermissionError):",
            "    checks['network_socket_denied'] = True",
            "try:",
            "    parent_env = pathlib.Path('/proc/1/environ').read_bytes()",
            "except OSError:",
            "    parent_env = b''",
            "checks['outer_parent_environment_hidden'] = b'PAIRED_SECRET_CANARY' not in parent_env and b'PAIRED_TOKEN_CANARY' not in parent_env",
            "print(json.dumps(checks, sort_keys=True, separators=(',', ':')))",
        ])
        auth_fd = os.open(auth_path, os.O_RDONLY)
        try:
            probe_program = probe_program.replace(
                "__TRANSPORT_FD__", str(auth_fd)
            )
            arguments = [
                str(bwrap), "--die-with-parent", "--new-session",
                "--unshare-pid", "--unshare-ipc", "--unshare-uts",
                "--dir", "/etc",
                "--ro-bind", "/usr", "/usr",
                "--symlink", "usr/bin", "/bin",
                "--symlink", "usr/sbin", "/sbin",
                "--symlink", "usr/lib", "/lib",
                "--symlink", "usr/lib64", "/lib64",
                "--ro-bind", "/etc/pki", "/etc/pki",
                "--ro-bind", "/etc/ssl", "/etc/ssl",
                "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
                "--ro-bind", "/etc/hosts", "/etc/hosts",
                "--ro-bind", "/etc/nsswitch.conf", "/etc/nsswitch.conf",
                "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                "--dir", "/runtime", "--ro-bind", str(bundle), "/runtime/vendor",
                "--dir", "/run", "--dir", "/run/codex-home",
                "--tmpfs", "/run/codex-home", "--file", str(auth_fd),
                "/run/codex-home/auth.json",
                "--dir", "/work", "--bind", str(work), "/work",
                "--dir", "/evidence", "--ro-bind", str(evidence),
                "/evidence/probe.txt",
                "--dir", "/isolated", "--dir", "/isolated/home",
                "--setenv", "HOME", "/isolated/home",
                "--setenv", "CODEX_HOME", "/run/codex-home",
                "--setenv", "PATH", "/runtime/vendor/codex-path:/usr/bin:/bin",
                "--setenv", "LANG", "C.UTF-8", "--setenv", "LC_ALL", "C.UTF-8",
                "--setenv", "NO_COLOR", "1", "--chdir", "/work",
                str(native_inside), *_permission_profile_config_arguments("/work"),
                "sandbox", "-P", "sealed", "-C", "/work", "--",
                "/usr/bin/python3", "-c", probe_program,
            ]
            environment = {
                "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                "PATH": "/runtime/vendor/codex-path:/usr/bin:/bin",
                # These are synthetic and test exclude=["*"]; the scientific
                # runner itself supplies no canaries or host credentials.
                "PAIRED_SECRET_CANARY": "MUST_NOT_REACH_TOOL",
                "PAIRED_TOKEN_CANARY": "MUST_NOT_REACH_TOOL",
            }
            result = subprocess.run(
                arguments, cwd=REPO, env=environment, pass_fds=(auth_fd,),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                timeout=45, check=False,
            )
        finally:
            os.close(auth_fd)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()[-2000:]
            raise SealError(f"sealed permission-profile probe failed: {detail}")
        try:
            checks = json.loads(
                result.stdout.strip(), object_pairs_hook=reject_duplicate_keys,
                parse_constant=reject_nonfinite_json,
                parse_float=parse_finite_json_float,
            )
        except json.JSONDecodeError as error:
            raise SealError("sealed permission-profile probe returned invalid JSON") from error
        expected_checks = {
            "auth_direct_denied", "auth_procroot_denied",
            "auth_transport_fd_closed", "environment_canaries_absent",
            "exact_evidence_read", "exact_scratch_write",
            "host_repository_hidden", "network_socket_denied",
            "outer_parent_environment_hidden", "safe_environment_exact",
        }
        if (type(checks) is not dict or set(checks) != expected_checks
                or any(value is not True for value in checks.values())
                or output.read_text(encoding="utf-8") != "SEALED_PROFILE_WRITE_V1\n"):
            raise SealError(f"sealed permission-profile probe checks failed: {checks}")
    return {
        "schema": "paired_open_problem_permission_profile_probe_v1",
        "status": "PASS",
        "isolation_contract_sha256": contract_hash,
        "model_cli_sha256": cli["sha256"],
        "model_bundle_inventory_sha256": cli["native_bundle_inventory_sha256"],
        "bubblewrap_sha256": bubblewrap_binding_value["sha256"],
        "checks": checks,
    }


def validate_permission_profile_probe(
        value: Any, cli: dict[str, Any], bubblewrap: dict[str, Any]) -> None:
    expected_keys = {
        "schema", "status", "isolation_contract_sha256", "model_cli_sha256",
        "model_bundle_inventory_sha256", "bubblewrap_sha256", "checks",
    }
    expected_checks = {
        "auth_direct_denied", "auth_procroot_denied",
        "auth_transport_fd_closed", "environment_canaries_absent",
        "exact_evidence_read", "exact_scratch_write", "host_repository_hidden",
        "network_socket_denied", "outer_parent_environment_hidden",
        "safe_environment_exact",
    }
    if (type(value) is not dict or set(value) != expected_keys
            or value.get("schema") != "paired_open_problem_permission_profile_probe_v1"
            or value.get("status") != "PASS"
            or value.get("isolation_contract_sha256") !=
            sha_bytes(canonical_bytes(isolation_contract()))
            or value.get("model_cli_sha256") != cli.get("sha256")
            or value.get("model_bundle_inventory_sha256") !=
            cli.get("native_bundle_inventory_sha256")
            or value.get("bubblewrap_sha256") != bubblewrap.get("sha256")
            or type(value.get("checks")) is not dict
            or set(value["checks"]) != expected_checks
            or any(item is not True for item in value["checks"].values())):
        raise SealError("sealed permission-profile probe receipt is invalid")


def verify_external_binding(value: Any, expected: Path, label: str) -> None:
    if type(value) is not dict:
        raise SealError(f"{label} binding is missing")
    require_plain_file(expected, label)
    if (Path(value.get("path", "")).resolve() != expected.resolve()
            or value.get("sha256") != sha_file(expected)
            or value.get("size_bytes") != expected.stat().st_size):
        raise SealError(f"{label} binding does not match current bytes")


def verify_named_executable(value: Any, label: str) -> Path:
    if type(value) is not dict or type(value.get("invoked_as")) is not str:
        raise SealError(f"{label} executable binding is missing")
    located = shutil.which(value["invoked_as"])
    if located is None:
        raise SealError(f"{label} invoked_as is no longer resolvable")
    resolved = Path(located).resolve()
    expected = Path(value.get("path", "")).resolve()
    verify_external_binding(value, expected, label)
    if resolved != expected:
        raise SealError(
            f"{label} PATH resolution changed: {resolved} != sealed {expected}"
        )
    return expected


def verify_model_cli(value: Any) -> Path:
    if type(value) is not dict or type(value.get("invoked_as")) is not str:
        raise SealError("model CLI binding is missing")
    located = shutil.which(value["invoked_as"])
    if located is None:
        raise SealError("model CLI invoked_as is no longer resolvable")
    launcher = Path(located).resolve()
    launcher_row = value.get("launcher")
    verify_external_binding(launcher_row, launcher, "model CLI launcher")
    if Path(launcher_row.get("path", "")).resolve() != launcher:
        raise SealError("model CLI PATH resolution differs from sealed launcher")
    native = Path(value.get("path", "")).resolve()
    verify_external_binding(value, native, "native model CLI")
    if native.read_bytes()[:4] != b"\x7fELF":
        raise SealError("sealed model CLI is no longer a native ELF")
    root = Path(value.get("native_bundle_root", "")).resolve()
    if native.parent.parent.resolve() != root:
        raise SealError("native model CLI bundle root mismatch")
    inventory = _bundle_inventory(root)
    if (value.get("native_bundle_inventory") != inventory
            or value.get("native_bundle_inventory_sha256") !=
            sha_bytes(canonical_bytes(inventory))):
        raise SealError("native model CLI bundle inventory changed")
    if (value.get("version_stdout") != REQUIRED_CODEX_VERSION
            or command(str(native), "--version") != REQUIRED_CODEX_VERSION):
        raise SealError("model CLI version output changed")
    return native


def payload_hash(value: dict[str, Any], field: str) -> str:
    unsigned = copy.deepcopy(value)
    recorded = unsigned.pop(field, None)
    expected = sha_bytes(canonical_bytes(unsigned))
    if recorded != expected:
        raise SealError(f"{field} mismatch")
    return expected


def create_seal(arguments: argparse.Namespace) -> dict[str, Any]:
    run = safe_run_root(arguments.run_root)
    seal_path = run / "RUNTIME_SEAL.json"
    if os.path.lexists(seal_path):
        raise SealError(f"refusing to overwrite runtime seal: {seal_path}")
    if not arguments.reviewed_by.strip() or not arguments.authorization_note.strip():
        raise SealError("reviewer and authorization note must be nonempty")
    validate_isolation_host()
    manifest, bound = validate_manifest(run)
    revision = command("git", "rev-parse", f"{arguments.repository_revision}^{{commit}}")
    origin_tip = command("git", "rev-parse", "origin/main^{commit}")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", revision, origin_tip], cwd=REPO,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if ancestry.returncode != 0:
        raise SealError("repository revision is not reachable from local origin/main")
    manifest_origin = origin_main_exact_binding(run / "RUN_MANIFEST.json", "run manifest")
    launch_contract = unattended_launch_contract(run, manifest)
    targeted_preregistration = targeted_preregistration_inventory(
        manifest, revision
    )
    runtime_files = {
        key: committed_runtime_binding(path, revision)
        for key, path in reviewed_runtime_paths().items()
    }
    database_path = Path(manifest["bugbank"]["database_path_at_bootstrap"]).resolve()
    database = external_binding(database_path)
    if (database["sha256"] != manifest["bugbank"]["database_sha256"]
            or database["size_bytes"] != manifest["bugbank"]["database_size_bytes"]):
        raise SealError("current BugBank database differs from bootstrap binding")
    cli = model_cli_binding(arguments.model_cli)
    python_runtime = python_runtime_binding(arguments.python_runtime)
    node_runtime = node_runtime_binding(arguments.node_runtime)
    bubblewrap = bubblewrap_binding(arguments.bubblewrap)
    flock_runtime = flock_binding()
    profile_probe = permission_profile_probe(cli, bubblewrap)
    operations = {
        "ops_root": manifest["operations"]["ops_root"],
        "scratch_root": manifest["operations"]["scratch_root"],
        "stop_file": manifest["operations"]["stop_file"],
        "canonical_lock_root": str((run / "locks").resolve()),
    }
    manifest_binding = external_binding(run / "RUN_MANIFEST.json")
    manifest_binding["manifest_payload_sha256"] = manifest["manifest_payload_sha256"]
    manifest_binding["repository_path"] = manifest_origin["repository_path"]
    manifest_binding["origin_main_commit"] = manifest_origin["origin_main_commit"]
    seal: dict[str, Any] = {
        "schema": SEAL_SCHEMA,
        "run_id": manifest["run_id"],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "launch_authorized": True,
        "authorization": {
            "reviewed_by": arguments.reviewed_by,
            "note": arguments.authorization_note,
        },
        "manifest": manifest_binding,
        "manifest_bound_artifacts": bound,
        "manifest_bound_artifacts_sha256": sha_bytes(canonical_bytes(bound)),
        "targeted_preregistration": targeted_preregistration,
        **runtime_files,
        "model_cli_version": cli,
        "python_interpreter": python_runtime,
        "node_runtime": node_runtime,
        "bubblewrap": bubblewrap,
        "flock_runtime": flock_runtime,
        "permission_profile_probe": profile_probe,
        "isolation_contract": isolation_contract(),
        "isolation_contract_sha256": sha_bytes(canonical_bytes(isolation_contract())),
        "repository_revision": {
            "commit": revision,
            "reviewed_code_commit": revision,
            "runtime_files_match_commit": True,
        },
        "bugbank_database": database,
        "ops_namespace": operations,
        "mutation_gate": mutation_gate_contract(manifest),
        "unattended_launch": launch_contract,
        "execution": {
            "model": manifest["execution"]["model"],
            "reasoning_effort": manifest["execution"]["reasoning_effort"],
            "retrieval_k": 3,
            "max_iterations": manifest["execution"]["max_iterations"],
            "claim_coverage_policy": "WHOLE_PROOF_UNCAPPED_V1",
            "audit_normalization_policy": AUDIT_NORMALIZATION_POLICY,
            "model_isolation_policy": MODEL_ISOLATION_POLICY,
            "accepted_completion_statuses": ACCEPTED_COMPLETION_STATUSES,
            "model_output_staged_in_exact_scratch": True,
            "host_publication_temporaries_outside_run": True,
            "execution_log_segment_policy": (
                "EXACT_CANONICAL_PREFIX_HASH_AND_SUFFIX_FROM_ADMISSION_OFFSET_V1"
            ),
            "json_number_policy": JSON_NUMBER_POLICY,
            "numeric_accounting_policy": NUMERIC_ACCOUNTING_POLICY,
            "inner_codex_sandbox": "custom-sealed-workspace",
            "permission_profile": {
                "name": "sealed", "extends": ":workspace",
                "filesystem": {"/run/codex-home/auth.json": "deny"},
                "network_enabled": False,
            },
            "outer_bwrap_network": "host_for_codex_transport_only",
            "model_shell_network_access": False,
            "auth_mount": "bwrap_file_from_fd3_parent_cli_only",
            "auth_file_model_tool_access": "deny",
            "auth_transport_fd_model_tool_access": "closed",
            "outer_spawn_environment_keys": ["LANG", "LC_ALL", "PATH"],
            "ignore_user_config": True,
        },
    }
    seal["runtime_payload_sha256"] = sha_bytes(canonical_bytes(seal))
    data = pretty_bytes(seal)
    descriptor = os.open(seal_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written == 0:
                raise SealError("short write while creating runtime seal")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return seal


def check_seal(run_root: Path) -> dict[str, Any]:
    run = safe_run_root(run_root)
    manifest, bound = validate_manifest(run)
    seal_path = run / "RUNTIME_SEAL.json"
    require_plain_file(seal_path, "runtime seal")
    seal = load_json(seal_path)
    if seal.get("schema") != SEAL_SCHEMA or seal.get("run_id") != manifest["run_id"]:
        raise SealError("runtime seal identity mismatch")
    if seal.get("launch_authorized") is not True:
        raise SealError("runtime seal does not authorize launch")
    validate_isolation_host()
    payload_hash(seal, "runtime_payload_sha256")
    manifest_origin = origin_main_exact_binding(
        run / "RUN_MANIFEST.json", "run manifest"
    )
    seal_origin = origin_main_exact_binding(seal_path, "runtime seal")
    if manifest_origin["origin_main_commit"] != seal_origin["origin_main_commit"]:
        raise SealError(
            "run manifest and runtime seal do not share one origin/main tip anchor"
        )
    manifest_binding = seal.get("manifest")
    verify_external_binding(
        manifest_binding, run / "RUN_MANIFEST.json", "sealed run manifest"
    )
    if manifest_binding.get("manifest_payload_sha256") != manifest["manifest_payload_sha256"]:
        raise SealError("sealed manifest payload hash mismatch")
    validate_manifest_creation_anchor(
        manifest_binding, manifest_origin, run / "RUN_MANIFEST.json"
    )
    # The returned binding is intentionally not embedded in RUNTIME_SEAL.json:
    # embedding its own commit/hash would be circular.  Successful lookup of
    # the current bytes above is the independent launch-time anchor.
    if not seal_origin.get("origin_main_commit"):
        raise SealError("runtime seal lacks an origin/main byte anchor")
    if (seal.get("manifest_bound_artifacts") != bound
            or seal.get("manifest_bound_artifacts_sha256") != sha_bytes(canonical_bytes(bound))):
        raise SealError("sealed manifest-bound artifact inventory mismatch")

    runtime_paths = reviewed_runtime_paths()
    revision_row = seal.get("repository_revision")
    if (type(revision_row) is not dict
            or set(revision_row) != {
                "commit", "reviewed_code_commit", "runtime_files_match_commit",
            }
            or type(revision_row.get("commit")) is not str):
        raise SealError("repository revision binding is invalid")
    revision = command("git", "rev-parse", f"{revision_row['commit']}^{{commit}}")
    if (revision != revision_row["commit"]
            or revision_row.get("reviewed_code_commit") != revision
            or revision_row.get("runtime_files_match_commit") is not True):
        raise SealError("repository revision is not the exact reviewed code commit")
    origin_tip = command("git", "rev-parse", "origin/main^{commit}")
    if subprocess.run(
            ["git", "merge-base", "--is-ancestor", revision, origin_tip],
            cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False).returncode != 0:
        raise SealError("repository revision is not reachable from origin/main")
    for key, path in runtime_paths.items():
        verify_external_binding(seal.get(key), path, key)
        committed = committed_runtime_binding(path, revision)
        if seal[key].get("repository_path") != committed["repository_path"]:
            raise SealError(f"{key} repository path mismatch")

    expected_targeted_preregistration = targeted_preregistration_inventory(
        manifest, revision
    )
    if seal.get("targeted_preregistration") != expected_targeted_preregistration:
        raise SealError("targeted preregistration/runtime binding changed")

    database_path = Path(seal.get("bugbank_database", {}).get("path", ""))
    verify_external_binding(seal.get("bugbank_database"), database_path, "BugBank database")
    if (seal["bugbank_database"]["sha256"] != manifest["bugbank"]["database_sha256"]
            or seal["bugbank_database"]["size_bytes"] != manifest["bugbank"]["database_size_bytes"]):
        raise SealError("sealed BugBank database differs from manifest")
    verify_model_cli(seal.get("model_cli_version"))
    python_path = verify_named_executable(
        seal.get("python_interpreter"), "Python runtime"
    )
    python_expected = python_runtime_binding(
        seal["python_interpreter"]["invoked_as"]
    )
    if seal["python_interpreter"] != python_expected:
        raise SealError("Python/SQLite runtime identity changed")
    node_path = verify_named_executable(seal.get("node_runtime"), "Node runtime")
    if command(str(node_path), "--version") != seal["node_runtime"].get("version_stdout"):
        raise SealError("Node runtime version changed")
    bwrap_path = verify_named_executable(seal.get("bubblewrap"), "bubblewrap runtime")
    if command(str(bwrap_path), "--version") != seal["bubblewrap"].get("version_stdout"):
        raise SealError("bubblewrap runtime version changed")
    flock_path = Path("/usr/bin/flock")
    verify_external_binding(seal.get("flock_runtime"), flock_path, "flock runtime")
    if seal.get("flock_runtime") != flock_binding():
        raise SealError("flock runtime identity changed")
    validate_permission_profile_probe(
        seal.get("permission_profile_probe"),
        seal["model_cli_version"], seal["bubblewrap"],
    )
    current_probe = permission_profile_probe(
        seal["model_cli_version"], seal["bubblewrap"]
    )
    if current_probe != seal.get("permission_profile_probe"):
        raise SealError("live permission-profile probe differs from sealed probe")
    if seal.get("isolation_contract") != isolation_contract():
        raise SealError("OS isolation mount/environment contract mismatch")
    if seal.get("isolation_contract_sha256") != sha_bytes(
            canonical_bytes(isolation_contract())):
        raise SealError("OS isolation contract hash mismatch")

    expected_ops = {
        "ops_root": manifest["operations"]["ops_root"],
        "scratch_root": manifest["operations"]["scratch_root"],
        "stop_file": manifest["operations"]["stop_file"],
        "canonical_lock_root": str((run / "locks").resolve()),
    }
    if seal.get("ops_namespace") != expected_ops:
        raise SealError("runtime ops namespace differs from manifest")
    if seal.get("mutation_gate") != mutation_gate_contract(manifest):
        raise SealError("runtime mutation-gate contract mismatch")
    if seal.get("unattended_launch") != unattended_launch_contract(run, manifest):
        raise SealError("unattended launch environment contract mismatch")
    expected_execution = {
        "model": manifest["execution"]["model"],
        "reasoning_effort": manifest["execution"]["reasoning_effort"],
        "retrieval_k": 3,
        "max_iterations": manifest["execution"]["max_iterations"],
        "claim_coverage_policy": "WHOLE_PROOF_UNCAPPED_V1",
        "audit_normalization_policy": AUDIT_NORMALIZATION_POLICY,
        "model_isolation_policy": MODEL_ISOLATION_POLICY,
        "accepted_completion_statuses": ACCEPTED_COMPLETION_STATUSES,
        "model_output_staged_in_exact_scratch": True,
        "host_publication_temporaries_outside_run": True,
        "execution_log_segment_policy": (
            "EXACT_CANONICAL_PREFIX_HASH_AND_SUFFIX_FROM_ADMISSION_OFFSET_V1"
        ),
        "json_number_policy": JSON_NUMBER_POLICY,
        "numeric_accounting_policy": NUMERIC_ACCOUNTING_POLICY,
        "inner_codex_sandbox": "custom-sealed-workspace",
        "permission_profile": {
            "name": "sealed", "extends": ":workspace",
            "filesystem": {"/run/codex-home/auth.json": "deny"},
            "network_enabled": False,
        },
        "outer_bwrap_network": "host_for_codex_transport_only",
        "model_shell_network_access": False,
        "auth_mount": "bwrap_file_from_fd3_parent_cli_only",
        "auth_file_model_tool_access": "deny",
        "auth_transport_fd_model_tool_access": "closed",
        "outer_spawn_environment_keys": ["LANG", "LC_ALL", "PATH"],
        "ignore_user_config": True,
    }
    if seal.get("execution") != expected_execution:
        raise SealError("runtime execution contract mismatch")
    return seal


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("--run-root", required=True, type=Path)
    create.add_argument("--repository-revision", default="HEAD")
    create.add_argument("--model-cli", default="codex")
    create.add_argument("--python-runtime", default=sys.executable)
    create.add_argument("--node-runtime", default="node")
    create.add_argument("--bubblewrap", default="bwrap")
    create.add_argument("--reviewed-by", required=True)
    create.add_argument("--authorization-note", required=True)
    create.add_argument("--quiet", action="store_true")
    check = subparsers.add_parser("check")
    check.add_argument("--run-root", required=True, type=Path)
    check.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        result = (
            create_seal(arguments) if arguments.command == "create"
            else check_seal(arguments.run_root)
        )
    except (SealError, OSError, KeyError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if not arguments.quiet:
        print(json.dumps({
            "status": "RUNTIME_SEALED" if arguments.command == "create" else "VALID",
            "run_id": result["run_id"],
            "runtime_payload_sha256": result["runtime_payload_sha256"],
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
