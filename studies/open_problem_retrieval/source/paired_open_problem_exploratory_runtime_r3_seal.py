#!/usr/bin/env python3
"""Create or check the fail-closed seal for the preregistered exploratory run.

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
from urllib.parse import urlsplit


SCRIPT = Path(__file__).resolve()
BASE = SCRIPT.parent.parent
REPO = BASE.parent
ACTIVE_RUN = BASE / "runs/open_frontier_paired_v2_20260901"
ACTIVE_OPS = Path("<workspace-home>/paired_v2_ops")
PROTECTED_RUNS = (
    ACTIVE_RUN,
    BASE / "runs/open_frontier_paired_hard_v1_20260903",
    BASE / "runs/open_frontier_paired_v2_fixed_point_extension_v3_20260903",
)
PROTECTED_OPS = (
    ACTIVE_OPS,
    Path("<workspace-home>/paired_hard_v1_ops"),
    Path("<workspace-home>/paired_v2_fixed_point_extension_v3_ops"),
)
EXPECTED_RUN_ID = "open_frontier_paired_exploratory_unbiased_v2r3_20260904"
EXPECTED_RUN = BASE / "runs" / EXPECTED_RUN_ID
EXPLORATORY_ROOT = BASE / "paired_open_problem_exploratory_v2"
EXPECTED_SOURCE_PACKAGE = BASE / "paired_open_problem_exploratory_sources_v2"
EXPECTED_OPS = Path("<workspace-home>/paired_exploratory_unbiased_v2r3_ops")
EXPECTED_SCRATCH = Path(
    "<workspace-home>/paired_exploratory_unbiased_v2r3_scratch"
)
RUNNER = SCRIPT.with_name("paired_open_problem_exploratory_runtime_r3_runner.mjs")
VALIDATOR = SCRIPT.with_name("validate_paired_open_problem_exploratory_runtime_r3_run.py")
FEEDBACK = SCRIPT.with_name("paired_open_problem_feedback.py")
STOCK_RETRIEVER = SCRIPT.with_name("bugbank_retrieve.py")
BATCH_LAUNCHER = SCRIPT.with_name(
    "run_sealed_paired_open_problem_exploratory_runtime_r3_batch.sh"
)
CHECKPOINT_HELPER = SCRIPT.with_name("checkpoint_sealed_paired_open_problem_run.sh")
EXPLORATORY_SLURM_LAUNCHER = SCRIPT.with_name(
    "paired_open_problem_exploratory_unbiased_v2r3.sbatch"
)
BOOTSTRAP_VALIDATOR = SCRIPT.with_name(
    "bootstrap_paired_open_problem_exploratory_runtime_r3_run.py"
)

AUDIT_NORMALIZATION_POLICY = "CLERICAL_BINDINGS_ONLY_V1"
MODEL_ISOLATION_POLICY = "BWRAP_EXACT_EVIDENCE_SEALED_PROFILE_V2"
JSON_NUMBER_POLICY = "STRICT_UTF8_UNIQUE_KEYS_FINITE_SAFE_NUMBERS_V1"
NUMERIC_ACCOUNTING_POLICY = "CHECKED_SAFE_INTEGER_TOKENS_AND_FINITE_DURATIONS_V1"
ACCEPTED_COMPLETION_STATUSES = ["COMPLETE", "RECOVERED_COMPLETE"]
REQUIRED_CODEX_VERSION = "codex-cli 0.153.0"
EXPECTED_SLURM_OUTPUT = (
    "<workspace-home>/paired_exploratory_unbiased_v2r3_slurm_%j.log"
)


def reviewed_runtime_paths() -> dict[str, Path]:
    """Every repository program allowed in the exploratory unattended chain."""
    return {
        "runner": RUNNER,
        "validator": VALIDATOR,
        "feedback_generator": FEEDBACK,
        "seal_utility": SCRIPT,
        "bootstrap_validator": BOOTSTRAP_VALIDATOR,
        "stock_retriever": STOCK_RETRIEVER,
        "batch_launcher": BATCH_LAUNCHER,
        "checkpoint_helper": CHECKPOINT_HELPER,
        "exploratory_slurm_launcher": EXPLORATORY_SLURM_LAUNCHER,
    }


def unattended_launch_contract(
        run: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Return and check the exploratory launcher/wrapper environment policy."""
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
        "PAIRED_JOB_LABEL": "paired-exploratory-unbiased-v2r3",
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
        "schema": "paired_open_problem_exploratory_unattended_launch_v1",
        "scheduler_export": "NIL",
        "submission_environment_policy": "DISCARD_ALL_EXCEPT_SLURM_METADATA",
        "scheduler_launcher_path": str(EXPLORATORY_SLURM_LAUNCHER.resolve()),
        "scheduler_stdout_path": EXPECTED_SLURM_OUTPUT,
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
            "manifest_selection": "EXACTLY_ONE_PLAIN_NON_SYMLINK_PACKAGE_MANIFEST",
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

    require_plain_file(
        EXPLORATORY_SLURM_LAUNCHER, "exploratory Slurm launcher"
    )
    launcher_text = EXPLORATORY_SLURM_LAUNCHER.read_text(encoding="utf-8")
    output_directives = [
        line for line in launcher_text.splitlines()
        if line.startswith("#SBATCH --output=")
    ]
    if output_directives != [f"#SBATCH --output={EXPECTED_SLURM_OUTPUT}"]:
        raise SealError("exploratory Slurm launcher stdout path is not exact")
    if not Path(EXPECTED_SLURM_OUTPUT).parent.is_dir():
        raise SealError("exploratory Slurm stdout parent directory does not exist")
    if launcher_text.count("#SBATCH --export=NIL") != 1:
        raise SealError("exploratory Slurm launcher must use exactly --export=NIL")
    if "exec /usr/bin/env -i \\\n" not in launcher_text:
        raise SealError("exploratory Slurm launcher lacks the env -i boundary")
    for key, value in fixed_environment.items():
        if f"  {key}={value} \\\n" not in launcher_text:
            raise SealError(
                f"exploratory Slurm launcher lacks fixed binding {key}"
            )
    if "  SLURM_JOB_ID=\"$slurm_job_id\" \\\n" not in launcher_text:
        raise SealError("exploratory Slurm launcher lacks its sole dynamic field")
    if ("  /usr/bin/bash --noprofile --norc \\\n" not in launcher_text
            or f"  {BATCH_LAUNCHER.resolve()}\n" not in launcher_text):
        raise SealError("exploratory Slurm launcher invokes the wrong wrapper")
    if re.search(r"\$\{PAIRED_[A-Z_]+", launcher_text):
        raise SealError("exploratory Slurm launcher permits a PAIRED_* override")
    for name in forbidden:
        if re.search(
                rf"^\s*(?:export\s+)?{re.escape(name)}=",
                launcher_text, re.MULTILINE):
            raise SealError(f"exploratory Slurm launcher imports forbidden {name}")

    require_plain_file(BATCH_LAUNCHER, "exploratory unattended batch launcher")
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
        raise SealError("exploratory batch launcher safe environment block changed")
    python_invocations = [
        line for line in batch_text.splitlines() if '"$python_runtime"' in line
    ]
    if (len(python_invocations) != 3
            or any('"${safe_python_env[@]}"' not in line
                   for line in python_invocations)):
        raise SealError("exploratory batch launcher has a non-allowlisted Python child")
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
            "exploratory batch launcher lacks the validator/report handshake"
        )
    required_pre_namespace_authentication = (
        "expected_repo=$(realpath <workspace>)",
        '[[ "$concurrency" = 5 && "$retry_seconds" = 60 && "$wall_seconds" = 86400 && \\',
        "if (( run_manifest_present != 1 || extension_manifest_present != 0 )); then",
        "paired_open_problem_exploratory_runtime_r3_seal.py",
        "paired_open_problem_exploratory_runtime_r3_runner.mjs",
        "validate_paired_open_problem_exploratory_runtime_r3_run.py",
        "open_frontier_paired_exploratory_unbiased_v2r3_20260904",
        "paired_exploratory_unbiased_v2r3_ops",
        "paired_exploratory_unbiased_v2r3_scratch",
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
            "exploratory batch launcher does not authenticate exact runtime paths "
            "before external namespace mutation"
        )
    if ('"${safe_runtime_env[@]}" PAIRED_OPERATION_LOCK_FD=8 \\\n'
            '    "$node_runtime" "$runner"' not in batch_text):
        raise SealError("exploratory batch launcher has a non-allowlisted Node child")
    if ('"${safe_runtime_env[@]}" PAIRED_OPEN_REPO="$repo" \\\n'
            '    PAIRED_OPERATION_LOCK_FD=8 "$checkpoint"' not in batch_text):
        raise SealError("exploratory batch launcher has a non-allowlisted checkpoint child")
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

MANIFEST_SCHEMA = "paired_open_problem_exploratory_run_manifest_v1"
SEAL_SCHEMA = "paired_open_problem_exploratory_runtime_seal_v1"
PROTOCOL_ID = "WHOLE_PROOF_FIRST_SOLUTION_V1"
PROTOCOL_DOCUMENT_SHA256 = (
    "b03a16d3b689c38143a047f0554fb7c1e1b619b89887618ef59a659754e053d1"
)
EXPLORATORY_STUDY_ID = "EXPLORATORY_UNBIASED_V2"
EXPLORATORY_REPORTING_CLASS = "SEPARATE_EXPLORATORY_COHORT"
EXPLORATORY_COHORT_SIZE = 6
CONFIRMATORY_PROTOCOL_OBSERVATION_COUNT = 58
CONFIRMATORY_DISTINCT_TARGET_COUNT = 36
CONFIRMATORY_CONTINUATION_OBSERVATION_COUNT = 22
JSON_PREREGISTRATION_FILENAMES = {
    "PREREGISTRATION.json",
    "CANDIDATE_POOL.json",
    "SELECTION_REPORT.json",
    "CONFIRMATORY_BOUNDARY_SEAL.json",
    "RUNTIME_CORRECTION_AMENDMENT_20260904.json",
    "RUNTIME_PREFLIGHT_CORRECTION_AMENDMENT_20260904.json",
}
PREREGISTRATION_FILENAMES = {
    *JSON_PREREGISTRATION_FILENAMES,
    "SELECTED_SOURCE_CONTEXT.md",
}
SELECTION_SEED_PREFIX = "qedbench-exploratory-extension-v1|"
SELECTION_SALT = "qedbench-exploratory-extension-v1"
ELIGIBLE_KEY_LIST_SHA256 = (
    "7298228a7b91661bcff38ec9efd71e6015a8fb3da3be69d9c2c7bb1a7af530b9"
)
EXCLUDED_KEY_LIST_SHA256 = (
    "dcd78b631ac3c113745cd57275842682d9f550d9d23710a31d30941baf2687ba"
)
SELECTED_KEY_LIST_SHA256 = (
    "c4d8c85c00175523612e85bc477e4963803c47f685b8bad3e0afb57d818ecdde"
)
EXPECTED_SELECTED_KEYS = [
    "arxiv:2511.02892v1#Problem 2.1",
    "arxiv:2603.29571v1#Conjecture 22",
    "arxiv:2603.29571v1#Conjecture 26",
    "arxiv:2603.29571v1#Conjecture 17",
    "arxiv:2511.02892v1#Problem 5.1",
    "arxiv:2603.29571v1#Conjecture 28",
]
EXPECTED_SELECTION_HASHES = [
    "03ac6d940093025bb7cdc1d12013f3e4a6a2f8775d3aa45df92bc1fcdd5db3ea",
    "0edeba69586acf7df17b59f522cc63da3d96d4f849196eda8f5b10308f764d12",
    "1740875545b936998d9dc3a6f3ef6df3a209cf62e9a328ab71fb0fcc7ebe14ad",
    "2859b6342d30c69d9526b871cb0109a69dbb0bcd80f1ad2e8e9c641711e4ee0c",
    "354719a2559e7c071133f4b2674d9330152de5bfa62a1fb9bc872219e3de4abe",
    "3be7fe81e7ae770e2f9281db6e8b0f9b09978c5b83b96b4ff57be42ac543878f",
]
EXPECTED_BOUNDARY_COMPONENTS = (
    {
        "component_id": "original31",
        "run_id": "open_frontier_paired_v2_20260901",
        "protocol_observation_count": 31,
        "report_path": (
            "qedbench_certificate_availability_triage/runs/"
            "open_frontier_paired_v2_20260901/validation_report.json"
        ),
        "report_schema": "open_frontier_paired_v2_validation_report_v1",
        "report_sha256": (
            "17913e5e05fae9c413ed5e47b5e1aecbb34cfd566047fe9e237a747e8ec5703d"
        ),
        "checkpoint_commit": "96140455cd16e9c164fd347361991407fc2bc3c9",
    },
    {
        "component_id": "hard5",
        "run_id": "open_frontier_paired_hard_v1_20260903",
        "protocol_observation_count": 5,
        "report_path": (
            "qedbench_certificate_availability_triage/runs/"
            "open_frontier_paired_hard_v1_20260903/VALIDATION_REPORT.json"
        ),
        "report_schema": "paired_open_problem_validation_report_v1",
        "report_sha256": (
            "c38ddb26f431e15167d582094e6d331bcd5ca20c60d4c08885e94dc916d9cd06"
        ),
        "checkpoint_commit": "738f9ba01c8b38a44814a66e104339e1fe75a5f8",
    },
    {
        "component_id": "extension22",
        "run_id": "open_frontier_paired_v2_fixed_point_extension_v3_20260903",
        "protocol_observation_count": 22,
        "report_path": (
            "qedbench_certificate_availability_triage/runs/"
            "open_frontier_paired_v2_fixed_point_extension_v3_20260903/"
            "VALIDATION_REPORT.json"
        ),
        "report_schema": "paired_open_problem_extension_validation_report_v1",
    },
)
EXPECTED_POOL_SOURCE_SNAPSHOTS = {
    "randomstrasse_2025": BASE / (
        "paired_open_problem_exploratory_sources_v2/sources/"
        "arxiv_2603_29571v1/source.pdf"
    ),
    "cycles_colouring_33": BASE / (
        "paired_open_problem_exploratory_sources_v2/sources/"
        "arxiv_2511_02892v1/source.pdf"
    ),
    "dagstuhl_25041": BASE / (
        "paired_open_problem_exploratory_sources_v2/sources/"
        "dagstuhl_25041/source.pdf"
    ),
    "problem_4_1_resolution_2026": BASE / (
        "paired_open_problem_exploratory_sources_v2/sources/"
        "arxiv_2607_23462v1/source.pdf"
    ),
}
VERSIONED_CONTINUATION_POLICY = {
    "schema": "qedbench.paired_open_problem_exploratory_continuation.v1",
    "trigger": (
        "every validated nonterminal arm-problem cell at the current "
        "50-iteration block cap"
    ),
    "selection": (
        "all and only triggered cells, selected mechanically without regard to "
        "problem identity, arm, apparent progress, retrieval content, or paired outcome"
    ),
    "continuation_run_id_rule": (
        "open_frontier_paired_exploratory_unbiased_v2_continuation_v<N>_20260904, "
        "where N starts at 1 and increases by one for every required block"
    ),
    "continuation_iteration_rule": (
        "version N runs exactly the next block of at most 50 iterations: "
        "50*N+1 through 50*(N+1)"
    ),
    "iteration_cap_per_version": 50,
    "starting_state": (
        "the exact byte-bound last revision, audit, token totals, and BugBank "
        "receipt history of that cell from the preceding validated version"
    ),
    "stopping_rule": (
        "stop a continued cell immediately at its first strict independently "
        "audited full solution or its first protocol-valid INCONCLUSIVE_FIXED_POINT endpoint"
    ),
    "plain_budget_rule": (
        "retain WHOLE_PROOF_FIRST_SOLUTION_V1 incremental BugBank-token endpoint "
        "matching for every continued plain cell"
    ),
    "versioning_rule": (
        "repeat mechanically in successive separately preregistered and runtime-sealed "
        "50-iteration versions until every cell is terminal; already-terminal cells "
        "remain frozen and are never rerun"
    ),
    "finite_final_cap": None,
    "original_run_cap_and_artifacts_unchanged": True,
    "outcome_based_discretion": False,
}
CONTINUATION_REQUIREMENT = (
    "Continue every validated nonterminal arm-problem cell at each 50-iteration "
    "cap in mechanically selected, separately preregistered and runtime-sealed "
    "50-iteration versions until it reaches VERIFIED_FULL or "
    "INCONCLUSIVE_FIXED_POINT; never rerun already-terminal cells."
)
REQUIRED_RUNTIME_SEAL_FIELDS = [
    "runner", "validator", "feedback_generator", "seal_utility",
    "bootstrap_validator",
    "stock_retriever", "batch_launcher", "checkpoint_helper",
    "exploratory_slurm_launcher", "model_cli_version", "python_interpreter",
    "node_runtime", "bubblewrap", "flock_runtime", "repository_revision",
    "bugbank_database", "ops_namespace", "exploratory_preregistration",
    "candidate_pool_source_snapshots",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class SealError(RuntimeError):
    """A required runtime identity or isolation condition did not hold."""


def _load_bootstrap_validator():
    spec = importlib.util.spec_from_file_location(
        "paired_exploratory_bootstrap_validator", BOOTSTRAP_VALIDATOR
    )
    if spec is None or spec.loader is None:
        raise SealError(f"cannot import bootstrap validator: {BOOTSTRAP_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bootstrap_validator = _load_bootstrap_validator()


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
        raise SealError("runtime refuses every non-preregistered run namespace")
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


def validate_manifest_against_normalized_source_spec(
        run: Path, manifest: dict[str, Any], spec: dict[str, Any]) -> None:
    """Replay the bootstrap normalization and compare every scientific field."""
    if (spec["run_id"] != manifest["run_id"]
            or spec["model"] != {
                "name": manifest["execution"]["model"],
                "reasoning_effort": manifest["execution"]["reasoning_effort"],
            }
            or spec["max_iterations"] != manifest["execution"]["max_iterations"]
            or spec["database_sha256"] != manifest["bugbank"]["database_sha256"]
            or spec["operations"] != {
                "ops_root": manifest["operations"]["ops_root"],
                "scratch_root": manifest["operations"]["scratch_root"],
            }):
        raise SealError("manifest execution identity differs from normalized source spec")
    records = manifest["records"]
    if len(records) != len(spec["records"]):
        raise SealError("manifest record count differs from normalized source spec")
    record_keys = {
        "record_id", "canonical_key", "title", "target", "tags", "input",
        "solver_input_top_level_fields", "source_documents", "canonical_source_order",
        "canonical_text_joiner", "status_search", "semantic_audit", "causal_exposure",
    }
    internal_source_keys = {
        "snapshot_source_path", "snapshot_sha256", "snapshot_size_bytes",
        "extracted_text_source_path", "extracted_text_sha256",
        "extracted_text_size_bytes", "extracted_text_encoding", "extraction_tool",
        "extracted_text_value",
    }
    for index, (record, expected) in enumerate(zip(records, spec["records"])):
        label = f"records[{index}]"
        if type(record) is not dict or set(record) != record_keys:
            raise SealError(f"{label} envelope differs from bootstrap materialization")
        for key in ("record_id", "canonical_key", "title", "target", "tags"):
            if record[key] != expected[key]:
                raise SealError(f"{label}.{key} differs from normalized source spec")
        expected_input_path = f"inputs/{record['record_id']}.json"
        if record["input"].get("path") != expected_input_path:
            raise SealError(f"{label}.input path differs from bootstrap materialization")
        if record["solver_input_top_level_fields"] != [
                "record_id", "title", "target", "source_open_excerpt", "source",
                "source_paper_text"]:
            raise SealError(f"{label} solver input field order changed")
        sources = record["source_documents"]
        if type(sources) is not list or len(sources) != len(expected["source_documents"]):
            raise SealError(f"{label} source inventory differs from source spec")
        for source_index, (source, expected_source) in enumerate(
                zip(sources, expected["source_documents"])):
            source_label = f"{label}.source_documents[{source_index}]"
            expected_metadata = {
                key: value for key, value in expected_source.items()
                if key not in internal_source_keys
            }
            if (type(source) is not dict
                    or set(source) != set(expected_metadata) | {"snapshot", "extracted_text"}
                    or {key: source[key] for key in expected_metadata} != expected_metadata):
                raise SealError(f"{source_label} metadata/locator fields differ from source spec")
            suffix = expected_source["snapshot_source_path"].suffix.lower()
            if not suffix or len(suffix) > 12 or not suffix[1:].isalnum():
                suffix = ".bin"
            expected_snapshot = {
                "path": (
                    f"source_provenance/{record['record_id']}/"
                    f"{source['source_id']}/source{suffix}"
                ),
                "sha256": expected_source["snapshot_sha256"],
                "size_bytes": expected_source["snapshot_size_bytes"],
            }
            expected_text = {
                "artifact": {
                    "path": (
                        f"source_provenance/{record['record_id']}/"
                        f"{source['source_id']}/source.txt"
                    ),
                    "sha256": expected_source["extracted_text_sha256"],
                    "size_bytes": expected_source["extracted_text_size_bytes"],
                },
                "encoding": expected_source["extracted_text_encoding"],
                "tool": expected_source["extraction_tool"],
            }
            if source["snapshot"] != expected_snapshot:
                raise SealError(f"{source_label} snapshot differs from normalized source spec")
            if source["extracted_text"] != expected_text:
                raise SealError(
                    f"{source_label} extracted text differs from normalized source spec"
                )
        expected_canonical_order = [
            source["source_id"] for source in expected["source_documents"]
            if "canonical_statement" in source["role"]
        ]
        if (record["canonical_source_order"] != expected_canonical_order
                or record["canonical_text_joiner"] != "two newline characters"):
            raise SealError(f"{label} canonical source ordering changed")
        status = expected["status_search"]
        status_suffix = status["query_log_source_path"].suffix.lower()
        if (not status_suffix or len(status_suffix) > 12
                or not status_suffix[1:].isalnum()):
            status_suffix = ".bin"
        expected_status = {
            "searched_at": status["searched_at"],
            "cutoff": status["cutoff"],
            "outcome": status["outcome"],
            "caveats": status["caveats"],
            "log": {
                "path": f"source_provenance/{record['record_id']}/status_search{status_suffix}",
                "sha256": status["query_log_sha256"],
                "size_bytes": status["query_log_size_bytes"],
            },
        }
        if record["status_search"] != expected_status:
            raise SealError(f"{label} status-search binding differs from source spec")
        semantic = expected["semantic_audit"]
        semantic_suffix = semantic["source_path"].suffix.lower()
        if (not semantic_suffix or len(semantic_suffix) > 12
                or not semantic_suffix[1:].isalnum()):
            semantic_suffix = ".bin"
        expected_semantic = {
            "artifact": {
                "path": f"source_provenance/{record['record_id']}/semantic_audit{semantic_suffix}",
                "sha256": semantic["sha256"],
                "size_bytes": semantic["size_bytes"],
            },
            "frozen58_overlap": "none",
        }
        if record["semantic_audit"] != expected_semantic:
            raise SealError(f"{label} semantic-audit binding differs from source spec")
        if record["causal_exposure"] != {
                "solver_receives_only_bound_input": True,
                "status_search_exposed_to_solver": False,
                "semantic_audit_exposed_to_solver": False,
                "source_metadata_urls_exposed_to_solver": False,
                "embedded_urls_may_occur_in_verbatim_source_text": True,
                }:
            raise SealError(f"{label} causal-exposure contract changed")


def manifest_bindings(manifest: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for name, binding in sorted(
            manifest["exploratory_preregistration"]["artifacts"].items()):
        yield f"exploratory_preregistration.artifacts.{name}", binding
    for name, binding in sorted(
            manifest["exploratory_preregistration"][
                "candidate_pool_source_snapshots"
            ].items()):
        yield f"exploratory_preregistration.candidate_pool_source_snapshots.{name}", binding
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
    if (manifest.get("run_id") != EXPECTED_RUN_ID
            or manifest.get("run_id") != run.name
            or ID_RE.fullmatch(run.name) is None):
        raise SealError("manifest run_id must match the safe run-root basename")
    if (manifest.get("status") != "BOOTSTRAPPED_AWAITING_RUNTIME_SEAL"
            or manifest.get("launch_authorized") is not False):
        raise SealError("immutable bootstrap manifest must remain non-launchable")
    required_seal_fields = manifest.get("required_runtime_seal_fields")
    if required_seal_fields != REQUIRED_RUNTIME_SEAL_FIELDS:
        raise SealError("manifest does not require the exploratory seal binding")
    unsigned = copy.deepcopy(manifest)
    payload_hash = unsigned.pop("manifest_payload_sha256", None)
    if payload_hash != sha_bytes(canonical_bytes(unsigned)):
        raise SealError("manifest_payload_sha256 mismatch")
    protocol = manifest.get("protocol")
    execution = manifest.get("execution")
    bugbank = manifest.get("bugbank")
    operations = manifest.get("operations")
    exploratory = manifest.get("exploratory_preregistration")
    expected_exploratory_keys = {
        "study_id", "reporting_class", "never_pool_with_frozen_58",
        "frozen_comparison_protocol_observation_count",
        "frozen_comparison_distinct_target_count",
        "frozen_comparison_continuation_observation_count",
        "cohort_size", "selected_canonical_keys",
        "artifacts", "artifacts_sha256", "candidate_pool_source_snapshots",
    }
    if (type(exploratory) is not dict
            or set(exploratory) != expected_exploratory_keys
            or exploratory.get("study_id") != EXPLORATORY_STUDY_ID
            or exploratory.get("reporting_class") != EXPLORATORY_REPORTING_CLASS
            or exploratory.get("never_pool_with_frozen_58") is not True
            or exploratory.get("frozen_comparison_protocol_observation_count") !=
            CONFIRMATORY_PROTOCOL_OBSERVATION_COUNT
            or exploratory.get("frozen_comparison_distinct_target_count") !=
            CONFIRMATORY_DISTINCT_TARGET_COUNT
            or exploratory.get("frozen_comparison_continuation_observation_count") !=
            CONFIRMATORY_CONTINUATION_OBSERVATION_COUNT
            or exploratory.get("cohort_size") != EXPLORATORY_COHORT_SIZE
            or exploratory.get("selected_canonical_keys") != EXPECTED_SELECTED_KEYS
            or type(exploratory.get("artifacts")) is not dict
            or set(exploratory["artifacts"]) != PREREGISTRATION_FILENAMES
            or type(exploratory.get("candidate_pool_source_snapshots")) is not dict
            or set(exploratory["candidate_pool_source_snapshots"]) !=
            set(EXPECTED_POOL_SOURCE_SNAPSHOTS)
            or exploratory.get("artifacts_sha256") != sha_bytes(
                canonical_bytes(exploratory["artifacts"]))):
        raise SealError("exploratory preregistration contract is invalid")
    if (type(protocol) is not dict or protocol.get("id") != PROTOCOL_ID
            or type(protocol.get("document")) is not dict
            or protocol["document"].get("sha256") != PROTOCOL_DOCUMENT_SHA256):
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
    if (type(execution) is not dict or execution.get("model") != "gpt-5.6-sol"
            or execution.get("reasoning_effort") != "max"
            or execution.get("arms") != ["bugbank", "plain"]
            or execution.get("shared_neutral_baseline") is not True
            or execution.get("model_network_access") is not False
            or execution.get("runtime_seal_required") is not True
            or execution.get("max_iterations") != 50):
        raise SealError("manifest execution contract is invalid")
    if (type(bugbank) is not dict or bugbank.get("retrieval_k") != 3
            or type(bugbank.get("database_sha256")) is not str
            or SHA256_RE.fullmatch(bugbank["database_sha256"]) is None):
        raise SealError("manifest BugBank contract is invalid")
    if (type(operations) is not dict
            or operations.get("namespaces_disjoint_from_frozen_58") is not True):
        raise SealError("manifest operations contract is invalid")
    for key in ("ops_root", "scratch_root", "stop_file"):
        if type(operations.get(key)) is not str or not Path(operations[key]).is_absolute():
            raise SealError(f"manifest operations.{key} must be absolute")
    if Path(operations["stop_file"]) != Path(operations["ops_root"]) / "STOP_REQUESTED":
        raise SealError("stop_file must be the isolated ops-root STOP_REQUESTED file")
    if (Path(operations["ops_root"]).resolve(strict=False) !=
            EXPECTED_OPS.resolve(strict=False)
            or Path(operations["scratch_root"]).resolve(strict=False) !=
            EXPECTED_SCRATCH.resolve(strict=False)):
        raise SealError("operations namespaces differ from preregistration")
    protected = (run, REPO, *PROTECTED_RUNS, *PROTECTED_OPS)
    for key in ("ops_root", "scratch_root"):
        if any(path_overlaps(Path(operations[key]), item) for item in protected):
            raise SealError(f"operations.{key} overlaps protected storage")
    if path_overlaps(Path(operations["ops_root"]), Path(operations["scratch_root"])):
        raise SealError("ops and scratch namespaces overlap")

    roster = manifest.get("problem_ids")
    records = manifest.get("records")
    if (type(roster) is not list or len(roster) != EXPLORATORY_COHORT_SIZE
            or len(roster) != len(set(roster))
            or any(type(item) is not str or ID_RE.fullmatch(item) is None for item in roster)
            or type(records) is not list
            or roster != [record.get("record_id") for record in records]
            or manifest.get("problem_count") != EXPLORATORY_COHORT_SIZE):
        raise SealError("manifest roster is inconsistent")

    canonical_keys = [record.get("canonical_key") for record in records]
    if canonical_keys != exploratory["selected_canonical_keys"]:
        raise SealError("record order differs from the frozen selected roster")

    checked: list[dict[str, Any]] = []
    for label, binding in manifest_bindings(manifest):
        check_binding(run, binding, label)
        checked.append({"label": label, **binding})
    prerequisite_paths = {
        name: check_binding(
            run, exploratory["artifacts"][name],
            f"exploratory prerequisite {name}",
        )
        for name in PREREGISTRATION_FILENAMES
    }
    preregistration = load_json(prerequisite_paths["PREREGISTRATION.json"])
    candidate_pool = load_json(prerequisite_paths["CANDIDATE_POOL.json"])
    selection_report = load_json(prerequisite_paths["SELECTION_REPORT.json"])
    boundary = load_json(prerequisite_paths["CONFIRMATORY_BOUNDARY_SEAL.json"])
    try:
        bootstrap_validator.validate_preregistration(preregistration)
        candidate_selected = bootstrap_validator.validate_candidate_pool(candidate_pool)
        bootstrap_validator.validate_search_preregistration_anchor(
            candidate_pool, EXPLORATORY_ROOT / "PREREGISTRATION.json"
        )
        selected_keys = bootstrap_validator.validate_selection_report(
            selection_report,
            prerequisite_paths["CANDIDATE_POOL.json"],
            prerequisite_paths["SELECTED_SOURCE_CONTEXT.md"],
            candidate_selected,
            logical_candidate_path=(
                "qedbench_certificate_availability_triage/"
                "paired_open_problem_exploratory_v2/CANDIDATE_POOL.json"
            ),
            logical_source_context_path=(
                "qedbench_certificate_availability_triage/"
                "paired_open_problem_exploratory_v2/SELECTED_SOURCE_CONTEXT.md"
            ),
        )
        bootstrap_validator.validate_confirmatory_boundary_seal(boundary)
        bootstrap_validator.validate_runtime_correction(load_json(
            prerequisite_paths["RUNTIME_CORRECTION_AMENDMENT_20260904.json"]
        ))
        bootstrap_validator.validate_preflight_correction(load_json(
            prerequisite_paths[
                "RUNTIME_PREFLIGHT_CORRECTION_AMENDMENT_20260904.json"
            ]
        ))
    except bootstrap_validator.BootstrapError as error:
        raise SealError(f"bound exploratory prerequisite is invalid: {error}") from error
    if selected_keys != EXPECTED_SELECTED_KEYS:
        raise SealError("bound selection report differs from frozen six-item roster")

    pool_sources = {row["source_id"]: row for row in candidate_pool["sources"]}
    for source_id, binding in exploratory["candidate_pool_source_snapshots"].items():
        if binding.get("path") != f"preregistration/source_snapshots/{source_id}.pdf":
            raise SealError("candidate-pool source snapshot path is not exact")
        path = check_binding(
            run, binding, f"candidate-pool source snapshot {source_id}"
        )
        source = pool_sources[source_id]
        if (binding["sha256"] != source["pdf_sha256"]
                or binding["size_bytes"] != source["pdf_bytes"]
                or sha_file(path) != source["pdf_sha256"]):
            raise SealError(
                f"candidate-pool source snapshot {source_id} differs from ledger"
            )

    source_spec_path = EXPECTED_SOURCE_PACKAGE / "bootstrap_spec_runtime_r3.json"
    source_spec_binding = manifest["bootstrap"]["source_spec"]
    bound_source_spec_path = check_binding(
        run, source_spec_binding, "bound bootstrap source spec"
    )
    require_plain_file(source_spec_path, "canonical bootstrap source spec")
    if source_spec_path.read_bytes() != bound_source_spec_path.read_bytes():
        raise SealError("bound bootstrap source spec differs from canonical package bytes")
    try:
        normalized_spec = bootstrap_validator.validate_spec(
            source_spec_path, run, require_fresh_operations=False
        )
        bootstrap_validator.check_run(
            run, expected_run_id=EXPECTED_RUN_ID, scientific_replay_only=True
        )
    except bootstrap_validator.BootstrapError as error:
        raise SealError(f"bootstrap-equivalent scientific replay failed: {error}") from error
    validate_manifest_against_normalized_source_spec(run, manifest, normalized_spec)

    selected_pool_rows = {
        row["canonical_key"]: row for row in candidate_pool["eligible"]
        if row["selected"] is True
    }
    for record in records:
        candidate = selected_pool_rows.get(record["canonical_key"])
        if candidate is None:
            raise SealError(f"record {record['record_id']} is absent from selected pool rows")
        statement_matches = [
            (source, locator)
            for source in record["source_documents"]
            for locator in source["locators"]
            if "statement" in locator["purpose"].casefold()
            and locator["label"] == candidate["label"]
            and locator["page"] == candidate["pdf_page_1based"]
            and source["pdf_url"] == candidate["source_url"]
        ]
        if not statement_matches:
            raise SealError(
                f"record {record['record_id']} lacks its selected pool "
                "PDF/page/label/statement-locator link"
            )
    problem_ids_path = check_binding(
        run, manifest["problem_ids_artifact"], "problem_ids_artifact"
    )
    if load_json_array(problem_ids_path) != roster:
        raise SealError("problem_ids artifact differs from manifest roster")
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
    with tempfile.TemporaryDirectory(prefix="paired-hard-flock-probe-") as raw:
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
        missing_provider = "paired-hard-deliberately-missing"
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
    exploratory_preregistration = copy.deepcopy(
        manifest["exploratory_preregistration"]
    )
    exploratory_preregistration["manifest_section_sha256"] = sha_bytes(
        canonical_bytes(manifest["exploratory_preregistration"])
    )
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
        "exploratory_preregistration": exploratory_preregistration,
        "candidate_pool_source_snapshots": copy.deepcopy(
            manifest["exploratory_preregistration"]["candidate_pool_source_snapshots"]
        ),
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
    missing_required = set(REQUIRED_RUNTIME_SEAL_FIELDS) - set(seal)
    if missing_required:
        raise SealError(
            f"runtime seal lacks required fields: {sorted(missing_required)}"
        )
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
    expected_preregistration = copy.deepcopy(manifest["exploratory_preregistration"])
    expected_preregistration["manifest_section_sha256"] = sha_bytes(
        canonical_bytes(manifest["exploratory_preregistration"])
    )
    if seal.get("exploratory_preregistration") != expected_preregistration:
        raise SealError("sealed exploratory preregistration binding mismatch")
    if seal.get("candidate_pool_source_snapshots") != manifest[
            "exploratory_preregistration"]["candidate_pool_source_snapshots"]:
        raise SealError("sealed candidate-pool source-snapshot bindings mismatch")

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
