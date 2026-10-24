#!/usr/bin/env python3
"""Independently validate the preregistered n=6 exploratory paired run.

This validator is read-only unless ``--report`` is explicitly supplied.  It
has no migration, cutover, or historical-artifact exceptions.  Exit 0 means a
valid complete run, 1 means a structurally valid but unfinished run, and 2
means invalid evidence.  ``--allow-incomplete`` maps only exit 1 to exit 0.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import re
import sqlite3
import stat
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
BASE = SCRIPT.parent.parent
REPO = BASE.parent
SEAL_SCRIPT = SCRIPT.with_name("paired_open_problem_exploratory_runtime_r3_seal.py")
FEEDBACK_SCRIPT = SCRIPT.with_name("paired_open_problem_feedback.py")
STOCK_RETRIEVER = SCRIPT.with_name("bugbank_retrieve.py")
ARMS = ("bugbank", "plain")
EXPECTED_RUN_ID = "open_frontier_paired_exploratory_unbiased_v2r3_20260904"
EXPECTED_RUN = BASE / "runs" / EXPECTED_RUN_ID
EXPECTED_OPS = Path("<workspace-home>/paired_exploratory_unbiased_v2r3_ops")
EXPECTED_SCRATCH = Path(
    "<workspace-home>/paired_exploratory_unbiased_v2r3_scratch"
)
EXPLORATORY_COHORT_SIZE = 6
PREREGISTRATION_FILENAMES = {
    "PREREGISTRATION.json", "CANDIDATE_POOL.json", "SELECTION_REPORT.json",
    "CONFIRMATORY_BOUNDARY_SEAL.json", "SELECTED_SOURCE_CONTEXT.md",
    "RUNTIME_CORRECTION_AMENDMENT_20260904.json",
    "RUNTIME_PREFLIGHT_CORRECTION_AMENDMENT_20260904.json",
}
EXPECTED_SELECTED_KEYS = [
    "arxiv:2511.02892v1#Problem 2.1",
    "arxiv:2603.29571v1#Conjecture 22",
    "arxiv:2603.29571v1#Conjecture 26",
    "arxiv:2603.29571v1#Conjecture 17",
    "arxiv:2511.02892v1#Problem 5.1",
    "arxiv:2603.29571v1#Conjecture 28",
]
WRITABLE_SUMMARY_STAGES = frozenset({
    "baseline", "audit-baseline", "receipt", "revision",
    "audit-revision", "terminal", "recover-revisions",
})
RUNNER_INITIAL_RUNTIME_DIRECTORIES = frozenset({
    "baselines", "audits/baseline", "audits/iterations",
    "audits/metadata/baseline", "audits/metadata/iterations", "retrievals",
    "iterations", "prompts", "pair_terminals", "logs/baseline",
    "logs/audit-baseline", "logs/receipt", "logs/revision",
    "logs/audit-revision", "states", "locks", "summaries",
})
FIXED_RUNTIME_DIRECTORIES = frozenset({
    *RUNNER_INITIAL_RUNTIME_DIRECTORIES,
    "audits", "audits/metadata", "logs", "checkers", "ops",
    "checkers/audits", "checkers/audits/baseline",
    "checkers/audits/iterations", "recoveries", "recoveries/revisions",
    "forensics",
    *(f"summaries/{stage}" for stage in WRITABLE_SUMMARY_STAGES),
})
CLAIM_COVERAGE_POLICY = "WHOLE_PROOF_UNCAPPED_V1"
RECEIPT_SCHEMA = "paired_open_problem_bugbank_exposure_receipt_v1"
PROMPT_SCHEMA = "paired_open_problem_prompt_exposure_v1"
AUDIT_METADATA_SCHEMA = "paired_open_problem_audit_metadata_v1"
TERMINAL_SCHEMA = "paired_open_problem_pair_terminal_v1"
MODEL_ISOLATION_POLICY = "BWRAP_EXACT_EVIDENCE_SEALED_PROFILE_V2"
SEALED_PERMISSION_PROFILE = {
    "name": "sealed", "extends": ":workspace",
    "filesystem": {"/run/codex-home/auth.json": "deny"},
    "network_enabled": False,
}
OUTER_SPAWN_ENVIRONMENT_KEYS = ["LANG", "LC_ALL", "PATH"]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
WORD = re.compile(r"[a-zA-Z][a-zA-Z-]{2,}")
STOP = set(
    """a an and are as at be by for from has have if in into is it its of on
    or that the their there these this to was we which will with not no nor so then
    than let all any each every some such given hence thus where when suppose assume
    proof claim show shows shown implies follows since because therefore step case
    """.split()
)
MAX_SAFE_JSON_INTEGER = (1 << 53) - 1


def reject_nonfinite_json(token: str) -> Any:
    """Reject Python's nonstandard NaN/Infinity JSON extensions."""
    raise ValueError(f"non-finite JSON number {token}")


def parse_finite_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value) or abs(value) > MAX_SAFE_JSON_INTEGER:
        reject_nonfinite_json(token)
    return value


def parse_safe_json_int(token: str) -> int:
    value = int(token)
    if abs(value) > MAX_SAFE_JSON_INTEGER:
        raise ValueError(f"unsafe JSON integer {token}")
    return value


def _load_seal_module():
    spec = importlib.util.spec_from_file_location("paired_runtime_seal", SEAL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import runtime seal checker: {SEAL_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


seal_checker = _load_seal_module()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_int(value: Any) -> bool:
    return type(value) is int


def is_number(value: Any) -> bool:
    return (type(value) in (int, float) and math.isfinite(value)
            and abs(value) <= MAX_SAFE_JSON_INTEGER)


def is_token_count(value: Any) -> bool:
    return type(value) is int and 0 <= value <= MAX_SAFE_JSON_INTEGER


def is_duration(value: Any) -> bool:
    return is_number(value) and value >= 0


def add_token_counts(*values: int) -> int:
    if any(not is_token_count(value) for value in values):
        raise ValueError("model-token count is not an exact safe JSON integer")
    total = sum(values)
    if total > MAX_SAFE_JSON_INTEGER:
        raise ValueError("model-token total exceeds exact JSON-integer accounting")
    return total


def add_durations(*values: int | float) -> int | float:
    if any(not is_duration(value) for value in values):
        raise ValueError("duration has a non-finite, negative, or unsafe operand")
    total = sum(values)
    if not is_duration(total):
        raise ValueError("duration total exceeds the safe finite JSON range")
    return total


def subtract_token_counts(left: int, right: int) -> int:
    if not is_token_count(left) or not is_token_count(right):
        raise ValueError("model-token difference has an inexact operand")
    difference = left - right
    if abs(difference) > MAX_SAFE_JSON_INTEGER:
        raise ValueError("model-token difference exceeds exact JSON-integer accounting")
    return difference


def process_identity_alive(pid: Any, expected_starttime: Any) -> bool | None:
    """Return exact PID/starttime liveness, or None when it cannot be proved."""
    if (not is_int(pid) or pid < 1 or type(expected_starttime) is not str
            or re.fullmatch(r"[0-9]+", expected_starttime) is None):
        return None
    path = Path(f"/proc/{pid}/stat")
    try:
        line = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    except OSError:
        return None
    marker = line.rfind(") ")
    if marker < 0:
        return None
    fields = line[marker + 2:].strip().split()
    if len(fields) <= 19 or re.fullmatch(r"[0-9]+", fields[19]) is None:
        return None
    return fields[19] == expected_starttime


def repo_path(path: Path) -> str:
    return Path(os.path.relpath(path.resolve(), REPO.resolve())).as_posix()


def recorded_path(value: Any, run: Path) -> Path | None:
    if type(value) is not str or not value:
        return None
    raw = Path(value)
    candidates = [raw] if raw.is_absolute() else [REPO / raw, run / raw]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


@dataclass(frozen=True)
class Artifact:
    path: Path
    raw: bytes
    value: dict[str, Any]
    sha256: str
    size_bytes: int


@dataclass
class Diagnostics:
    run: Path
    invalid: list[dict[str, str]] = field(default_factory=list)
    incomplete: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)
    _seen: set[tuple[str, str, str]] = field(default_factory=set)
    checked_state_paths: set[Path] = field(default_factory=set)

    def add(self, target: list[dict[str, str]], code: str,
            path: Path | str, message: str) -> None:
        try:
            shown = str(Path(path).resolve().relative_to(self.run.resolve()))
        except (ValueError, OSError, TypeError):
            shown = str(path)
        key = (code, shown, message)
        if key not in self._seen:
            self._seen.add(key)
            target.append({"code": code, "path": shown, "message": message})

    def bad(self, code: str, path: Path | str, message: str) -> None:
        self.add(self.invalid, code, path, message)

    def missing(self, code: str, path: Path | str, message: str) -> None:
        self.add(self.incomplete, code, path, message)

    def warn(self, code: str, path: Path | str, message: str) -> None:
        self.add(self.warnings, code, path, message)


def load_artifact(path: Path, diagnostics: Diagnostics, *, required: bool = False,
                  code: str = "MISSING_ARTIFACT") -> Artifact | None:
    if not path.is_file():
        if required:
            diagnostics.missing(code, path, "required artifact is absent")
        return None
    if path.is_symlink():
        diagnostics.bad("SYMLINK_ARTIFACT", path, "evidence artifacts may not be symlinks")
        return None
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=seal_checker.reject_duplicate_keys,
            parse_constant=reject_nonfinite_json,
            parse_int=parse_safe_json_int,
            parse_float=parse_finite_json_float,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError,
            ValueError, seal_checker.SealError) as error:
        diagnostics.bad("MALFORMED_JSON", path, str(error))
        return None
    if type(value) is not dict:
        diagnostics.bad("JSON_NOT_OBJECT", path, "top-level JSON must be an object")
        return None
    return Artifact(path.resolve(), raw, value, sha_bytes(raw), len(raw))


def binding(artifact: Artifact) -> dict[str, Any]:
    return {
        "path": repo_path(artifact.path),
        "sha256": artifact.sha256,
        "size_bytes": artifact.size_bytes,
    }


def file_binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": repo_path(path), "sha256": sha_bytes(raw),
        "size_bytes": len(raw),
    }


def execution_log_segment(path: Path, start_offset: Any) -> dict[str, Any]:
    if (not is_int(start_offset) or start_offset < 0 or not path.is_file()
            or path.is_symlink()):
        raise ValueError("execution-log path or start offset is invalid")
    raw = path.read_bytes()
    if start_offset > len(raw):
        raise ValueError("execution-log start offset exceeds canonical log")
    segment = raw[start_offset:]
    return {
        "path": repo_path(path), "start_offset": start_offset,
        "size_bytes": len(segment), "sha256": sha_bytes(segment),
    }


def execution_log_prefix_sha(path: Path, start_offset: Any) -> str:
    if (not is_int(start_offset) or start_offset < 0 or not path.is_file()
            or path.is_symlink()):
        raise ValueError("execution-log path or prefix offset is invalid")
    raw = path.read_bytes()
    if start_offset > len(raw):
        raise ValueError("execution-log prefix offset exceeds canonical log")
    return sha_bytes(raw[:start_offset])


def model_isolation_state_fields(
        seal: Mapping[str, Any], schema_path: Path,
        read_only_inputs: Sequence[Path], scratch: Path) -> dict[str, Any]:
    return {
        "isolation_contract_sha256": seal["isolation_contract_sha256"],
        "inner_permission_profile": copy.deepcopy(SEALED_PERMISSION_PROFILE),
        "auth_file_model_tool_access": "deny",
        "auth_transport_fd_model_tool_access": "closed",
        "model_shell_network_access": False,
        "ignore_user_config": True,
        "ignore_workspace_rules": True,
        "web_search": "disabled",
        "model_tool_shell_environment": model_tool_shell_environment(scratch),
        "allow_login_shell": False,
        "shell_snapshot": False,
        "strict_config": True,
        "outer_spawn_environment_keys": OUTER_SPAWN_ENVIRONMENT_KEYS,
        "scratch_retry_policy": (
            "exclusive_lock_then_empty_exact_cell_scratch_before_each_new_call"
        ),
        "host_publication_temporary_policy": (
            "private_external_scratch_same_filesystem_fsync_then_atomic_rename_or_link"
        ),
        "isolated_read_only_evidence": [
            file_binding(path) for path in (schema_path, *read_only_inputs)
        ],
        "isolated_scratch_path": str(scratch.resolve()),
    }


def model_tool_shell_environment(scratch: Path) -> dict[str, Any]:
    return {
        "inherit": "none", "exclude": ["*"],
        "set": {
            "PATH": "/runtime/vendor/codex-path:/usr/bin:/bin",
            "HOME": str(scratch.resolve()), "TMPDIR": "/tmp",
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
        },
    }


def expected_requested_execution(
        manifest: Mapping[str, Any], seal: Mapping[str, Any],
        scratch: Path) -> dict[str, Any]:
    return {
        "model": manifest["execution"]["model"],
        "reasoning_effort": manifest["execution"]["reasoning_effort"],
        "sandbox": "outer-bwrap-read-isolated",
        "inner_sandbox": "custom-sealed-workspace",
        "permission_profile": copy.deepcopy(SEALED_PERMISSION_PROFILE),
        "working_directory": str(scratch),
        "repository_writes_forbidden": True,
        "outer_isolation_policy": MODEL_ISOLATION_POLICY,
        "readable_evidence_policy": "EXACT_CALL_INPUTS_ONLY",
        "auth_file_model_tool_access": "deny",
        "auth_transport_fd_model_tool_access": "closed",
        "model_shell_network_access": False,
        "isolation_contract_sha256": seal["isolation_contract_sha256"],
        "ignore_user_config": True,
        "ignore_workspace_rules": True,
        "web_search": "disabled",
        "model_tool_shell_environment": model_tool_shell_environment(scratch),
        "allow_login_shell": False,
        "shell_snapshot": False,
        "strict_config": True,
        "outer_spawn_environment_keys": OUTER_SPAWN_ENVIRONMENT_KEYS,
        "scratch_retry_policy": (
            "exclusive_lock_then_empty_exact_cell_scratch_before_each_new_call"
        ),
        "host_publication_temporary_policy": (
            "private_external_scratch_same_filesystem_fsync_then_atomic_rename_or_link"
        ),
    }


def check_binding(value: Any, artifact: Artifact, owner: Path, label: str,
                  diagnostics: Diagnostics, run: Path) -> bool:
    valid = type(value) is dict
    if not valid:
        diagnostics.bad("BINDING_INVALID", owner, f"{label} binding is not an object")
        return False
    if (recorded_path(value.get("path"), run) != artifact.path
            or value.get("sha256") != artifact.sha256
            or value.get("size_bytes") != artifact.size_bytes):
        diagnostics.bad("BINDING_MISMATCH", owner, f"{label} does not bind exact bytes")
        valid = False
    return valid


def schema_type_matches(value: Any, expected: str) -> bool:
    return {
        "object": type(value) is dict,
        "array": type(value) is list,
        "string": type(value) is str,
        "integer": is_int(value),
        "number": is_number(value),
        "boolean": type(value) is bool,
        "null": value is None,
    }.get(expected, False)


def resolve_ref(root: Mapping[str, Any], reference: str) -> Mapping[str, Any] | None:
    if not reference.startswith("#/"):
        return None
    value: Any = root
    for raw in reference[2:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if type(value) is not dict or key not in value:
            return None
        value = value[key]
    return value if type(value) is dict else None


def validate_schema(instance: Any, schema: Mapping[str, Any],
                    root: Mapping[str, Any] | None = None,
                    at: str = "$") -> list[str]:
    root = schema if root is None else root
    errors: list[str] = []
    if "$ref" in schema:
        target = resolve_ref(root, schema["$ref"])
        return ([f"{at}: unresolved ref {schema['$ref']}"] if target is None
                else validate_schema(instance, target, root, at))
    expected = schema.get("type")
    if type(expected) is str and not schema_type_matches(instance, expected):
        return [f"{at}: expected {expected}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{at}: value is outside enum")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{at}: value differs from const")
    if type(instance) is dict:
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{at}: missing required property {key!r}")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{at}: unexpected property {key!r}")
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_schema(value, properties[key], root, f"{at}.{key}"))
    if type(instance) is list:
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{at}: fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{at}: more than maxItems")
        if schema.get("uniqueItems") is True:
            encoded = [canonical_bytes(item) for item in instance]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{at}: items are not unique")
        item_schema = schema.get("items")
        if type(item_schema) is dict:
            for index, item in enumerate(instance):
                errors.extend(validate_schema(item, item_schema, root, f"{at}[{index}]"))
    if type(instance) is str:
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{at}: shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{at}: does not match pattern")
    if is_number(instance):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{at}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{at}: above maximum")
    return errors


def apply_schema(artifact: Artifact, schema: Mapping[str, Any] | None,
                 diagnostics: Diagnostics, label: str) -> bool:
    if schema is None:
        return False
    errors = validate_schema(artifact.value, schema)
    for error in errors:
        diagnostics.bad("SCHEMA_VIOLATION", artifact.path, f"{label}: {error}")
    return not errors


def payload_valid(value: Mapping[str, Any], field: str) -> bool:
    copy_value = copy.deepcopy(value)
    recorded = copy_value.pop(field, None)
    return type(recorded) is str and recorded == sha_bytes(canonical_bytes(copy_value))


def proof_state(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "claimed_resolution": value.get("claimed_resolution"),
        "results": [
            {"claim": row.get("claim"), "proof_sketch": row.get("proof_sketch")}
            for row in value.get("results", []) if type(row) is dict
        ],
        "final_writeup": value.get("final_writeup"),
    }


def expected_audit_overall(claims: Sequence[Mapping[str, Any]]) -> str:
    verdicts = [row.get("verdict") for row in claims]
    if "REFUTED" in verdicts:
        return "REFUTED"
    if verdicts and all(item == "VERIFIED" for item in verdicts):
        return "VERIFIED"
    return "INCONCLUSIVE"


def validate_baseline(artifact: Artifact, record_id: str,
                      schema: Mapping[str, Any] | None,
                      diagnostics: Diagnostics) -> bool:
    valid = apply_schema(artifact, schema, diagnostics, "baseline")
    value = artifact.value
    if value.get("record_id") != record_id or value.get("stage") != "BASELINE":
        diagnostics.bad("BASELINE_IDENTITY", artifact.path, "baseline identity mismatch")
        valid = False
    results = value.get("results")
    if type(results) is not list or not results:
        diagnostics.bad("BASELINE_EMPTY", artifact.path, "results must be nonempty and uncapped")
        return False
    if any(type(row) is not dict or type(row.get("claim")) is not str
           or not row["claim"].strip() or type(row.get("proof_sketch")) is not str
           or not row["proof_sketch"].strip() for row in results):
        diagnostics.bad("BASELINE_RESULT", artifact.path, "every result needs claim and proof")
        valid = False
    return valid


def expected_resolution_verdict(parent: Artifact, target_verdict: Any) -> str | None:
    claimed = {"NONE": 0, "PARTIAL": 1, "FULL": 2}.get(
        parent.value.get("claimed_resolution")
    )
    target = {
        "NO_VALID_PROGRESS": 0,
        "OVERCLAIMED": 0,
        "VALID_PARTIAL_PROGRESS": 1,
        "FULLY_RESOLVES_TARGET": 2,
    }.get(target_verdict)
    if claimed is None or target is None:
        return None
    return "ACCURATE" if claimed == target else ("OVERSTATED" if claimed > target else "UNDERSTATED")


def audit_scratch(manifest: Mapping[str, Any], record_id: str, arm: str,
                  iteration: int) -> Path:
    root = Path(manifest["operations"]["scratch_root"])
    if arm == "neutral":
        return root / record_id / "audit-baseline"
    return root / record_id / "audit-revision" / arm / f"iter_{iteration}"


def validate_audit(artifact: Artifact, record_id: str, parent: Artifact,
                   arm: str, iteration: int, schema: Mapping[str, Any] | None,
                   manifest: Mapping[str, Any], diagnostics: Diagnostics) -> bool:
    valid = apply_schema(artifact, schema, diagnostics, "audit")
    stage = "BASELINE_AUDIT" if arm == "neutral" else "REVISION_AUDIT"
    identities = {
        "record_id": record_id,
        "stage": stage,
        "arm": arm,
        "iteration": iteration,
        "parent_sha256": parent.sha256,
        "complete": True,
    }
    for key, expected in identities.items():
        if artifact.value.get(key) != expected:
            diagnostics.bad("AUDIT_IDENTITY", artifact.path, f"{key} mismatch")
            valid = False
    parent_results = parent.value.get("results")
    claims = artifact.value.get("claims")
    if type(parent_results) is not list or type(claims) is not list:
        diagnostics.bad("AUDIT_CLAIMS", artifact.path, "claim arrays are malformed")
        return False
    if len(claims) != len(parent_results):
        diagnostics.bad("AUDIT_INCOMPLETE", artifact.path, "audit must cover every result row")
        valid = False
    scratch = audit_scratch(manifest, record_id, arm, iteration).resolve()
    for index, source in enumerate(parent_results):
        if index >= len(claims) or type(claims[index]) is not dict:
            continue
        row = claims[index]
        claim = source.get("claim") if type(source) is dict else None
        expected = {"idx": index, "claim": claim,
                    "claim_sha256": sha_text(claim) if type(claim) is str else None}
        if any(row.get(key) != value for key, value in expected.items()):
            diagnostics.bad("AUDIT_BINDING", artifact.path, f"claim {index} binding mismatch")
            valid = False
        checker = row.get("checker_path")
        if checker != "none":
            try:
                Path(checker).resolve().relative_to(scratch)
            except (TypeError, ValueError):
                diagnostics.bad("CHECKER_OUTSIDE_SCRATCH", artifact.path,
                                f"claim {index} checker escapes exact scratch")
                valid = False
    refuted = [index for index, row in enumerate(claims)
               if type(row) is dict and row.get("verdict") == "REFUTED"]
    if artifact.value.get("confirmed_refutations") != refuted:
        diagnostics.bad("AUDIT_REFUTATION_LIST", artifact.path,
                        "confirmed_refutations is not the exact refuted index list")
        valid = False
    if artifact.value.get("overall") != expected_audit_overall(claims):
        diagnostics.bad("AUDIT_OVERALL", artifact.path, "overall verdict is inconsistent")
        valid = False
    expected_resolution = expected_resolution_verdict(
        parent, artifact.value.get("target_verdict")
    )
    if artifact.value.get("claimed_resolution_verdict") != expected_resolution:
        diagnostics.bad("AUDIT_RESOLUTION", artifact.path,
                        "claimed-resolution verdict is inconsistent")
        valid = False
    if (artifact.value.get("target_verdict") == "FULLY_RESOLVES_TARGET"
            and expected_audit_overall(claims) != "VERIFIED"):
        diagnostics.bad("AUDIT_FALSE_FULL", artifact.path,
                        "full target verdict requires every claim verified")
        valid = False
    return valid


def validate_audit_metadata(metadata: Artifact, audit: Artifact, parent: Artifact,
                            source: Artifact, record_id: str, arm: str,
                            iteration: int, manifest: Mapping[str, Any],
                            seal: Mapping[str, Any], diagnostics: Diagnostics,
                            run: Path) -> bool:
    value = metadata.value
    valid = payload_valid(value, "metadata_payload_sha256")
    if not valid:
        diagnostics.bad("AUDIT_METADATA_HASH", metadata.path, "metadata payload hash mismatch")
    stage = "BASELINE_AUDIT" if arm == "neutral" else "REVISION_AUDIT"
    identities = {
        "schema": AUDIT_METADATA_SCHEMA,
        "run_id": manifest["run_id"], "record_id": record_id,
        "stage": stage, "arm": arm, "iteration": iteration,
    }
    if any(value.get(key) != expected for key, expected in identities.items()):
        diagnostics.bad("AUDIT_METADATA_IDENTITY", metadata.path, "metadata identity mismatch")
        valid = False
    manifest_artifact = load_artifact(run / "RUN_MANIFEST.json", diagnostics)
    seal_artifact = load_artifact(run / "RUNTIME_SEAL.json", diagnostics)
    if (not check_binding(value.get("source"), source, metadata.path, "source", diagnostics, run)
            or not check_binding(value.get("parent"), parent, metadata.path, "parent", diagnostics, run)
            or manifest_artifact is None or not check_binding(
                value.get("run_manifest"), manifest_artifact, metadata.path,
                "run manifest", diagnostics, run)
            or seal_artifact is None or not check_binding(
                value.get("runtime_seal"), seal_artifact, metadata.path,
                "runtime seal", diagnostics, run)):
        valid = False
    prompt = value.get("prompt_text")
    if (type(prompt) is not str or value.get("prompt_utf8_sha256") != sha_text(prompt)
            or value.get("prompt_size_bytes") != len(prompt.encode("utf-8"))):
        diagnostics.bad("AUDIT_PROMPT_HASH", metadata.path, "audit prompt hash/size mismatch")
        valid = False
    requested = value.get("requested_execution")
    scratch = audit_scratch(manifest, record_id, arm, iteration)
    expected_execution = expected_requested_execution(manifest, seal, scratch)
    if requested != expected_execution:
        diagnostics.bad("AUDIT_EXECUTION", metadata.path, "requested execution mismatch")
        valid = False
    marker = "--- BEGIN COMPLETE BUGBANK EXPOSURE RECEIPT ---"
    if marker in (prompt or "") or manifest["bugbank"]["database_sha256"] in (prompt or ""):
        diagnostics.bad("AUDITOR_TREATMENT_EXPOSURE", metadata.path,
                        "independent auditor prompt contains treatment evidence")
        valid = False
    checker_rows = value.get("checker_artifacts")
    expected_claims = audit.value.get("claims", [])
    expected_indexes = [index for index, row in enumerate(expected_claims)
                        if row.get("checker_path") != "none"]
    if type(checker_rows) is not list or [row.get("idx") for row in checker_rows
                                         if type(row) is dict] != expected_indexes:
        diagnostics.bad("CHECKER_INVENTORY", metadata.path, "durable checker inventory mismatch")
        return False
    for row in checker_rows:
        index = row["idx"]
        original = expected_claims[index]["checker_path"]
        durable_value = row.get("durable")
        durable_path = recorded_path(
            durable_value.get("path") if type(durable_value) is dict else None, run
        )
        durable = load_artifact_bytes(durable_path, diagnostics) if durable_path else None
        if (row.get("original_scratch_path") != original or durable is None
                or row.get("original_sha256") != durable[0]
                or row.get("original_size_bytes") != durable[1]
                or durable_value.get("sha256") != durable[0]
                or durable_value.get("size_bytes") != durable[1]
                or recorded_path(durable_value.get("path"), run) != durable_path):
            diagnostics.bad("CHECKER_BINDING", metadata.path,
                            f"checker {index} durable binding mismatch")
            valid = False
    return valid


def load_artifact_bytes(path: Path | None, diagnostics: Diagnostics) -> tuple[str, int] | None:
    if path is None or not path.is_file() or path.is_symlink():
        return None
    try:
        raw = path.read_bytes()
    except OSError as error:
        diagnostics.bad("UNREADABLE_CHECKER", path, str(error))
        return None
    return sha_bytes(raw), len(raw)


ENTRY_COLUMNS = (
    "id", "title", "type", "domain", "subdomain", "refutes", "statement",
    "true_theorem", "hypothesis_violated", "source_book", "source_chapter",
    "source_item", "source_pages", "difficulty", "status", "body_md", "path",
)
RETRIEVAL_SQL = """
SELECT bm25(entries_fts, 2.0, 8.0, 4.0, 1.0, 1.0, 3.0) AS score,
       e.id, e.title, e.type, e.domain, e.subdomain, e.refutes,
       e.statement, e.true_theorem, e.hypothesis_violated,
       e.source_book, e.source_chapter, e.source_item, e.source_pages,
       e.difficulty, e.status, e.body_md, e.path
FROM entries_fts AS f
JOIN entries AS e ON e.id = f.id
WHERE entries_fts MATCH ?
ORDER BY score ASC, e.id COLLATE BINARY ASC
LIMIT ?
""".strip()


class BugBankView:
    def __init__(self, path: Path):
        self.path = path.resolve()
        uri = f"file:{self.path.as_posix()}?mode=ro"
        self.connection = sqlite3.connect(uri, uri=True)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA query_only = ON")
        self.connection.execute("BEGIN")
        table_rows = self.connection.execute(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type='table' ORDER BY name COLLATE BINARY"
        ).fetchall()
        table_sql = {row["name"]: row["sql"] for row in table_rows}
        self.tables = set(table_sql)
        if "entries" not in self.tables or "entries_fts" not in self.tables:
            raise sqlite3.DatabaseError("BugBank lacks entries or entries_fts")
        entries_columns = [
            row["name"] for row in self.connection.execute("PRAGMA table_info(entries)")
        ]
        if any(column not in entries_columns for column in ENTRY_COLUMNS):
            raise sqlite3.DatabaseError("BugBank entries table lacks required columns")
        rows = self.connection.execute(
            "SELECT id, refutes FROM entries ORDER BY id COLLATE BINARY"
        ).fetchall()
        self.document_count = len(rows)
        self.frequency: Counter[str] = Counter()
        for row in rows:
            for word in set(match.lower() for match in WORD.findall(row["refutes"] or "")):
                if word not in STOP:
                    self.frequency[word] += 1
        status_counts = {
            row["status"]: row["count"]
            for row in self.connection.execute(
                "SELECT status, COUNT(*) AS count FROM entries "
                "GROUP BY status ORDER BY status COLLATE BINARY"
            )
        }
        self.metadata = {
            "entries_columns": entries_columns,
            "entries_schema_sha256": sha_text(table_sql["entries"] or ""),
            "entries_fts_schema_sha256": sha_text(table_sql["entries_fts"] or ""),
            "tables": sorted(table_sql),
            "sqlite_library_version": sqlite3.sqlite_version,
            "sqlite_user_version": self.connection.execute(
                "PRAGMA user_version"
            ).fetchone()[0],
            "sqlite_schema_version": self.connection.execute(
                "PRAGMA schema_version"
            ).fetchone()[0],
            "journal_mode": self.connection.execute("PRAGMA journal_mode").fetchone()[0],
            "entry_count": self.document_count,
            "status_counts": status_counts,
        }

    def close(self) -> None:
        self.connection.rollback()
        self.connection.close()

    def salient_terms(self, text: str) -> list[dict[str, Any]]:
        seen: dict[str, float] = {}
        for raw in WORD.findall(text):
            word = raw.lower()
            if word in STOP or len(word) < 3:
                continue
            seen.setdefault(
                word, (self.document_count + 1) / (self.frequency.get(word, 0) + 1)
            )
        return [
            {"term": term, "document_frequency": self.frequency.get(term, 0),
             "rarity_weight": weight}
            for term, weight in sorted(seen.items(), key=lambda item: -item[1])[:12]
        ]

    def auxiliary(self, entry: dict[str, Any]) -> tuple[list[str], list[str], str | None]:
        entry_id = entry["id"]
        tags = ([row[0] for row in self.connection.execute(
            "SELECT tag FROM tags WHERE entry_id=? ORDER BY tag COLLATE BINARY",
            (entry_id,))] if "tags" in self.tables else [])
        related = ([row[0] for row in self.connection.execute(
            "SELECT related_id FROM relations WHERE entry_id=? "
            "ORDER BY related_id COLLATE BINARY", (entry_id,))]
            if "relations" in self.tables else [])
        citation = None
        if "sources" in self.tables and entry.get("source_book") is not None:
            row = self.connection.execute(
                "SELECT citation FROM sources WHERE id=?", (entry["source_book"],)
            ).fetchone()
            citation = row[0] if row is not None else None
        return tags, related, citation

    def expected_query(self, record_id: str, iteration: int, index: int,
                       result: Mapping[str, Any], k: int) -> dict[str, Any]:
        claim = result["claim"]
        proof = result["proof_sketch"]
        query_text = f"{claim}\n\n{proof}"
        terms = self.salient_terms(query_text)
        expression = " OR ".join(f'"{item["term"]}"' for item in terms)
        rows = (self.connection.execute(RETRIEVAL_SQL, (expression, k)).fetchall()
                if terms else [])
        hits: list[dict[str, Any]] = []
        for rank, row in enumerate(rows, 1):
            score = float(row["score"])
            entry = {column: row[column] for column in ENTRY_COLUMNS}
            tags, related, citation = self.auxiliary(entry)
            hit: dict[str, Any] = {
                "rank": rank, "bm25": score, "bm25_binary64_hex": score.hex(),
                "entry_id": entry["id"], "title": entry["title"],
                "type": entry["type"], "domain": entry["domain"],
                "subdomain": entry["subdomain"], "refutes": entry["refutes"],
                "statement": entry["statement"], "counterexample": entry["statement"],
                "true_theorem": entry["true_theorem"],
                "hypothesis_violated": entry["hypothesis_violated"],
                "source_book": entry["source_book"],
                "source_chapter": entry["source_chapter"],
                "source_item": entry["source_item"], "source_pages": entry["source_pages"],
                "source_citation": citation, "difficulty": entry["difficulty"],
                "status": entry["status"], "body_md": entry["body_md"],
                "path": entry["path"], "tags": tags, "related_entry_ids": related,
            }
            hit["treatment_content_sha256"] = sha_bytes(canonical_bytes({
                "refutes": hit["refutes"], "counterexample": hit["counterexample"],
                "true_theorem": hit["true_theorem"],
            }))
            hit["entry_payload_sha256"] = sha_bytes(canonical_bytes({
                **entry, "tags": tags, "related_entry_ids": related,
                "source_citation": citation,
            }))
            hit["hit_payload_sha256"] = sha_bytes(canonical_bytes(hit))
            hits.append(hit)
        return {
            "query_id": f"{record_id}__bugbank__iter_{iteration}__claim_{index}",
            "claim_index": index, "claim": claim, "claim_sha256": sha_text(claim),
            "proof_sketch_sha256": sha_text(proof),
            "query_text_sha256": sha_text(query_text),
            "salient_terms": terms, "fts_match_expression": expression,
            "hit_count": len(hits), "hits": hits,
        }


def validate_receipt(artifact: Artifact, record_id: str, iteration: int,
                     parent: Artifact, manifest: Mapping[str, Any],
                     seal: Mapping[str, Any], database: BugBankView,
                     diagnostics: Diagnostics, run: Path) -> tuple[bool, list[str]]:
    value = artifact.value
    valid = payload_valid(value, "receipt_payload_sha256")
    if not valid:
        diagnostics.bad("RECEIPT_HASH", artifact.path, "receipt payload hash mismatch")
    receipt_keys = {
        "schema", "run_id", "pair_id", "record_id", "arm", "iteration",
        "stage", "status", "parent", "parent_claim_count", "parent_claims",
        "parent_claims_sha256", "database", "script", "stock_retriever",
        "invocation", "parameters", "queries", "exposure_summary", "timing",
        "receipt_hash_contract", "receipt_payload_sha256",
    }
    if set(value) != receipt_keys:
        diagnostics.bad("RECEIPT_ENVELOPE", artifact.path,
                        "receipt has missing or unrecognized top-level fields")
        valid = False
    identities = {
        "schema": RECEIPT_SCHEMA, "run_id": manifest["run_id"],
        "pair_id": record_id, "record_id": record_id, "arm": "bugbank",
        "iteration": iteration, "stage": "BUGBANK_FEEDBACK_EXPOSURE",
        "status": "COMPLETE",
    }
    if any(value.get(key) != expected for key, expected in identities.items()):
        diagnostics.bad("RECEIPT_IDENTITY", artifact.path, "receipt identity mismatch")
        valid = False
    parent_row = value.get("parent")
    expected_parent_arm = parent.value.get("arm")
    expected_parent_iteration = parent.value.get("iteration")
    expected_parent = {
        "requested_path": str(parent.path), "path": str(parent.path),
        "size_bytes": parent.size_bytes, "sha256": parent.sha256,
        "canonical_payload_sha256": sha_bytes(canonical_bytes(parent.value)),
        "record_id": record_id, "arm": expected_parent_arm,
        "iteration": expected_parent_iteration, "stage": parent.value.get("stage"),
    }
    if type(parent_row) is not dict:
        parent_normalized = None
    else:
        parent_normalized = dict(parent_row)
        for key in ("requested_path", "path"):
            try:
                parent_normalized[key] = str(Path(parent_normalized[key]).resolve())
            except (KeyError, TypeError):
                parent_normalized = None
                break
    if parent_normalized != expected_parent:
        diagnostics.bad("RECEIPT_PARENT", artifact.path, "receipt parent binding mismatch")
        valid = False
    parameters = value.get("parameters")
    invocation = value.get("invocation")
    expected_parameters = {
        "k_per_claim": 3,
        "status_filter": "all",
        "exclude_self": False,
        "excluded_source_items": [],
        "excluded_entry_ids": [],
        "document_frequency_corpus": "all entries.refutes rows across all statuses",
        "maximum_salient_terms": 12,
        "salient_term_tie_break": "first occurrence in query text",
        "query_text_basis": "claim statement, two newlines, proof_sketch",
        "fts_bm25_weights": [2.0, 8.0, 4.0, 1.0, 1.0, 3.0],
        "ordering": ["bm25_score_ASC_unrounded", "entry_id_BINARY_ASC"],
        "truncate_stage": "after status-all query and total ordering",
        "query_sql": RETRIEVAL_SQL,
        "query_sql_sha256": sha_text(RETRIEVAL_SQL),
    }
    expected_invocation = {
        "run_id": manifest["run_id"],
        "parent_json": str(parent.path),
        "record_id": record_id,
        "iteration": iteration,
        "out": str(receipt_path(run, record_id, iteration)),
        "k": 3,
        "db": str(database.path),
        "db_sha256": manifest["bugbank"]["database_sha256"],
    }
    invocation_ok = type(invocation) is dict
    if invocation_ok:
        invocation_normalized = dict(invocation)
        for key in ("parent_json", "out", "db"):
            try:
                invocation_normalized[key] = str(Path(invocation_normalized[key]).resolve())
            except (KeyError, TypeError):
                invocation_ok = False
    if (parameters != expected_parameters or not invocation_ok
            or invocation_normalized != expected_invocation):
        diagnostics.bad("RECEIPT_PARAMETERS", artifact.path, "retrieval parameters mismatch")
        valid = False
    expected_programs = {
        "script": {
            "path": str(FEEDBACK_SCRIPT), "size_bytes": FEEDBACK_SCRIPT.stat().st_size,
            "sha256": sha_file(FEEDBACK_SCRIPT),
        },
        "stock_retriever": {
            "path": str(STOCK_RETRIEVER),
            "size_bytes": STOCK_RETRIEVER.stat().st_size,
            "sha256": sha_file(STOCK_RETRIEVER),
            "reuse_scope": (
                "STOP, WORD, document-frequency, salient-term, and BM25 contracts"
            ),
        },
    }
    for key, wanted in expected_programs.items():
        if value.get(key) != wanted:
            diagnostics.bad("RECEIPT_PROGRAM", artifact.path, f"{key} binding mismatch")
            valid = False
    db_row = value.get("database")
    expected_database = {
        "requested_path": str(database.path), "path": str(database.path),
        "size_bytes": seal["bugbank_database"]["size_bytes"],
        "sha256": seal["bugbank_database"]["sha256"],
        "open_mode": "SQLite URI mode=ro plus PRAGMA query_only",
        **database.metadata,
    }
    if type(db_row) is dict:
        database_normalized = dict(db_row)
        for key in ("requested_path", "path"):
            try:
                database_normalized[key] = str(Path(database_normalized[key]).resolve())
            except (KeyError, TypeError):
                database_normalized = None
                break
    else:
        database_normalized = None
    if database_normalized != expected_database:
        diagnostics.bad("RECEIPT_DATABASE", artifact.path, "database binding mismatch")
        valid = False
    results = parent.value.get("results", [])
    expected_claims = [{
        "claim_index": index, "claim": row["claim"],
        "claim_sha256": sha_text(row["claim"]),
        "proof_sketch_sha256": sha_text(row["proof_sketch"]),
        "query_text_sha256": sha_text(f"{row['claim']}\n\n{row['proof_sketch']}"),
    } for index, row in enumerate(results)]
    if (value.get("parent_claim_count") != len(expected_claims)
            or value.get("parent_claims") != expected_claims
            or value.get("parent_claims_sha256") != sha_bytes(canonical_bytes(expected_claims))):
        diagnostics.bad("RECEIPT_CLAIMS", artifact.path,
                        "receipt does not query the complete ordered proof")
        valid = False
    expected_queries = [database.expected_query(record_id, iteration, index, row, 3)
                        for index, row in enumerate(results)]
    if value.get("queries") != expected_queries:
        diagnostics.bad("RECEIPT_RESULTS", artifact.path,
                        "retrieval results differ from an independent database query")
        valid = False
    retrieved: list[str] = []
    seen: set[str] = set()
    for query in expected_queries:
        for hit in query["hits"]:
            if hit["entry_id"] not in seen:
                seen.add(hit["entry_id"])
                retrieved.append(hit["entry_id"])
    exposure = value.get("exposure_summary")
    query_bytes = canonical_bytes(expected_queries)
    expected_hit_count = add_token_counts(
        *(row["hit_count"] for row in expected_queries)
    )
    if (type(exposure) is not dict or exposure.get("query_count") != len(expected_queries)
            or exposure.get("hit_count") != expected_hit_count
            or exposure.get("ordered_payload_sha256") != sha_bytes(query_bytes)
            or exposure.get("ordered_payload_size_bytes") != len(query_bytes)
            or exposure.get("payload_contract") !=
            "canonical JSON of the complete ordered queries array"):
        diagnostics.bad("RECEIPT_EXPOSURE", artifact.path, "receipt exposure summary mismatch")
        valid = False
    timing = value.get("timing")
    if (type(timing) is not dict or set(timing) != {
            "started_at", "ended_at", "duration_nanoseconds",
            "duration_seconds", "clock", "timestamps_timezone",
            } or type(timing.get("started_at")) is not str
            or type(timing.get("ended_at")) is not str
            or not is_int(timing.get("duration_nanoseconds"))
            or timing.get("duration_nanoseconds") < 0
            or not is_duration(timing.get("duration_seconds"))
            or timing.get("duration_seconds") !=
            timing.get("duration_nanoseconds") / 1_000_000_000
            or timing.get("clock") != "time.monotonic_ns"
            or timing.get("timestamps_timezone") != "UTC"
            or value.get("receipt_hash_contract") !=
            "SHA-256 of canonical JSON for this object before receipt_payload_sha256 is added"):
        diagnostics.bad("RECEIPT_TIMING", artifact.path,
                        "receipt timing/hash contract is malformed")
        valid = False
    return valid, retrieved


def validate_revision(artifact: Artifact, record_id: str, arm: str,
                      iteration: int, parent: Artifact, audit: Artifact,
                      receipt: Artifact | None, retrieved: Sequence[str],
                      schema: Mapping[str, Any] | None,
                      diagnostics: Diagnostics, run: Path) -> bool:
    valid = apply_schema(artifact, schema, diagnostics, "revision")
    value = artifact.value
    expected = {
        "record_id": record_id, "stage": "REVISION", "arm": arm,
        "iteration": iteration, "parent_sha256": parent.sha256,
        "audit_sha256": audit.sha256,
    }
    if any(value.get(key) != wanted for key, wanted in expected.items()):
        diagnostics.bad("REVISION_IDENTITY", artifact.path, "revision lineage mismatch")
        valid = False
    if arm == "plain":
        if (value.get("treatment_status") != "PLAIN_SELF_CRITIQUE"
                or value.get("receipt_path") != "" or value.get("receipt_sha256") != ""
                or value.get("retrieved_entry_ids") != []
                or value.get("acted_on_entry_ids") != []
                or value.get("dismissed_hits") != []):
            diagnostics.bad("PLAIN_TREATMENT", artifact.path,
                            "plain revision contains treatment bookkeeping")
            valid = False
    else:
        acted = value.get("acted_on_entry_ids")
        dismissed_rows = value.get("dismissed_hits")
        dismissed = ([row.get("entry_id") for row in dismissed_rows]
                     if type(dismissed_rows) is list
                     and all(type(row) is dict for row in dismissed_rows) else None)
        acted_set = set(acted) if type(acted) is list else set()
        expected_acted = [item for item in retrieved if item in acted_set]
        expected_dismissed = [item for item in retrieved if item not in acted_set]
        if (receipt is None or value.get("treatment_status") != "BUGBANK_RECEIPT_EXPOSED"
                or recorded_path(value.get("receipt_path"), run) != receipt.path
                or value.get("receipt_sha256") != receipt.sha256
                or value.get("retrieved_entry_ids") != list(retrieved)
                or acted != expected_acted or dismissed != expected_dismissed
                or len(acted_set) != len(acted or [])):
            diagnostics.bad("BUGBANK_TREATMENT", artifact.path,
                            "treated revision does not exactly partition its receipt")
            valid = False
    return valid


def validate_prompt_metadata(metadata: Artifact, record_id: str, arm: str,
                             iteration: int, source: Artifact, parent: Artifact,
                             audit: Artifact, receipt: Artifact | None,
                             retrieved: Sequence[str], manifest: Mapping[str, Any],
                             diagnostics: Diagnostics, run: Path) -> bool:
    value = metadata.value
    valid = payload_valid(value, "metadata_payload_sha256")
    if not valid:
        diagnostics.bad("PROMPT_METADATA_HASH", metadata.path, "metadata payload hash mismatch")
    expected = {
        "schema": PROMPT_SCHEMA, "run_id": manifest["run_id"],
        "record_id": record_id, "stage": "REVISION_PROMPT", "arm": arm,
        "iteration": iteration, "claim_coverage_policy": CLAIM_COVERAGE_POLICY,
        "treatment_status": ("PLAIN_SELF_CRITIQUE" if arm == "plain"
                             else "BUGBANK_RECEIPT_EXPOSED"),
        "bugbank_exposed": arm == "bugbank",
    }
    if any(value.get(key) != wanted for key, wanted in expected.items()):
        diagnostics.bad("PROMPT_METADATA_IDENTITY", metadata.path,
                        "prompt metadata identity mismatch")
        valid = False
    manifest_artifact = load_artifact(run / "RUN_MANIFEST.json", diagnostics)
    seal_artifact = load_artifact(run / "RUNTIME_SEAL.json", diagnostics)
    rows = (("source", source), ("parent", parent), ("audit", audit),
            ("run_manifest", manifest_artifact), ("runtime_seal", seal_artifact))
    for key, expected_artifact in rows:
        if expected_artifact is None or not check_binding(
                value.get(key), expected_artifact, metadata.path, key, diagnostics, run):
            valid = False
    prompt = value.get("prompt_text")
    if (type(prompt) is not str or value.get("prompt_utf8_sha256") != sha_text(prompt)
            or value.get("prompt_size_bytes") != len(prompt.encode("utf-8"))
            or prompt.count(audit.raw.decode("utf-8")) != 1
            or "There is no claim-count cap." not in prompt
            or "Use at most six claims" in prompt):
        diagnostics.bad("PROMPT_CONTENT", metadata.path,
                        "revision prompt body/hash/whole-proof contract mismatch")
        valid = False
    scratch = (Path(manifest["operations"]["scratch_root"]) / record_id /
               "revision" / arm / f"iter_{iteration}")
    execution_seal = (seal_artifact.value if seal_artifact is not None else {})
    expected_execution = expected_requested_execution(
        manifest, execution_seal, scratch
    ) if seal_artifact is not None else None
    if value.get("requested_execution") != expected_execution:
        diagnostics.bad("PROMPT_EXECUTION", metadata.path, "prompt execution mismatch")
        valid = False
    exposure = value.get("exposure")
    marker = "--- BEGIN COMPLETE BUGBANK EXPOSURE RECEIPT ---"
    if arm == "plain":
        forbidden = [manifest["bugbank"]["database_sha256"]]
        if receipt is not None:
            forbidden.extend([receipt.sha256, receipt.value.get("receipt_payload_sha256")])
        if (value.get("receipt") is not None or type(exposure) is not dict
                or exposure.get("complete_receipt_payload_embedded") is not False
                or exposure.get("receipt_verbatim_occurrences") != 0
                or exposure.get("receipt_start_byte") is not None
                or exposure.get("receipt_end_byte") is not None
                or exposure.get("complete_receipt_marker_count") != 0
                or exposure.get("exposed_forbidden_treatment_hashes") != []
                or exposure.get("retrieved_entry_ids") != []
                or marker in (prompt or "")
                or any(type(item) is str and item in (prompt or "") for item in forbidden)):
            diagnostics.bad("PLAIN_EXPOSURE", metadata.path,
                            "plain prompt exposes treatment evidence")
            valid = False
    else:
        receipt_raw = receipt.raw.decode("utf-8") if receipt is not None else ""
        character_offset = (prompt or "").find(receipt_raw)
        start = (len((prompt or "")[:character_offset].encode("utf-8"))
                 if character_offset >= 0 else -1)
        expected_receipt = binding(receipt) | {
            "receipt_payload_sha256": receipt.value["receipt_payload_sha256"]
        } if receipt is not None else None
        if (receipt is None or value.get("receipt") != expected_receipt
                or type(exposure) is not dict
                or exposure.get("complete_receipt_payload_embedded") is not True
                or exposure.get("receipt_verbatim_occurrences") != 1
                or exposure.get("receipt_start_byte") != start
                or exposure.get("receipt_end_byte") != add_token_counts(
                    start, receipt.size_bytes
                )
                or exposure.get("retrieved_entry_ids") != list(retrieved)
                or (prompt or "").count(receipt_raw) != 1):
            diagnostics.bad("BUGBANK_EXPOSURE", metadata.path,
                            "treated prompt does not expose exactly one complete receipt")
            valid = False
    return valid


def state_path(run: Path, record_id: str, stage: str, arm: str | None = None,
               iteration: int | None = None) -> Path:
    parts: list[str] = [record_id]
    if arm is not None:
        parts.append(arm)
    if iteration is not None:
        parts.append(f"iter_{iteration}")
    return run / "states" / ("__".join(parts) + f"__{stage}.json")


def validate_state(state: Artifact | None, record_id: str, stage: str,
                   arm: str | None, iteration: int | None,
                   manifest: Mapping[str, Any], seal: Mapping[str, Any],
                   diagnostics: Diagnostics, *, model_call: bool,
                   prompt_sha256: str | None = None,
                   expected_fields: Mapping[str, Any] | None = None
                   ) -> tuple[bool, int | None]:
    if state is None:
        return False, None
    diagnostics.checked_state_paths.add(state.path.resolve())
    value = state.value
    effective_fields = dict(expected_fields or {})
    if prompt_sha256 is not None:
        effective_fields["prompt_sha256"] = prompt_sha256
    expected = {"run_id": manifest["run_id"], "record_id": record_id,
                "arm": arm, "iteration": iteration,
                "stage": stage}
    valid = all(value.get(key) == wanted for key, wanted in expected.items())
    status = value.get("status")
    complete = status in {"COMPLETE", "RECOVERED_COMPLETE"}
    if status == "RECOVERED_COMPLETE" and stage != "revision":
        valid = False
    runtime_expected = {
        "run_manifest_sha256": sha_file(Path(manifest["__run_root"]) / "RUN_MANIFEST.json"),
        "runtime_seal_sha256": sha_file(Path(manifest["__run_root"]) / "RUNTIME_SEAL.json"),
        "runtime_seal_payload_sha256": seal["runtime_payload_sha256"],
        "runner_sha256": seal["runner"]["sha256"],
    }
    if any(value.get(key) != wanted for key, wanted in runtime_expected.items()):
        valid = False
    tokens = value.get("tokens_used")
    # A durable state may legitimately describe a call that failed or was
    # interrupted.  Such a state is INCOMPLETE, not valid endpoint evidence.
    # Only completed states are allowed to contribute model-token costs, and
    # their envelope is exact so a self-consistent extra field cannot smuggle
    # unvalidated provenance into the experiment.
    if complete:
        if model_call:
            if (not is_token_count(tokens)
                    or value.get("model") != manifest["execution"]["model"]
                    or value.get("reasoning_effort") != manifest["execution"]["reasoning_effort"]):
                valid = False
        else:
            if (tokens != 0 or value.get("model") is not None
                    or value.get("reasoning_effort") is not None):
                valid = False
        common_keys = {
            "run_id", "record_id", "arm", "iteration", "stage", "status",
            "started_at", "ended_at", "duration_seconds", "error",
            "tokens_used", "model", "reasoning_effort",
            "execution_log_start_offset", "execution_log_prefix_sha256",
            "execution_log_segment",
            "run_manifest_sha256", "runtime_seal_sha256",
            "runtime_seal_payload_sha256", "runner_sha256",
        }
        if status == "RECOVERED_COMPLETE":
            common_keys = {
                "run_id", "record_id", "arm", "iteration", "stage", "status",
                "recovered_at", "recovery_path", "recovery_sha256",
                "tokens_used", "model", "reasoning_effort",
                "execution_log_start_offset", "execution_log_prefix_sha256",
                "execution_log_segment",
                "run_manifest_sha256", "runtime_seal_sha256",
                "runtime_seal_payload_sha256", "runner_sha256",
            }
        allowed_keys = common_keys | set(effective_fields)
        if set(value) != allowed_keys:
            valid = False
        if status == "COMPLETE" and (
                type(value.get("started_at")) is not str
                or type(value.get("ended_at")) is not str
                or not is_duration(value.get("duration_seconds"))
                or value.get("error") is not None):
            valid = False
    else:
        prefix_fields = dict(effective_fields)
        prefix_fields.pop("finalized_output", None)
        if status == "RUNNING":
            common_keys = {
                "run_id", "record_id", "arm", "iteration", "stage", "status",
                "started_at", "execution_log_start_offset",
                "execution_log_prefix_sha256", "runner_pid",
                "runner_process_starttime", "run_manifest_sha256",
                "runtime_seal_sha256", "runtime_seal_payload_sha256",
                "runner_sha256",
            }
            if (set(value) != common_keys | set(prefix_fields)
                    or type(value.get("started_at")) is not str
                    or not value["started_at"]
                    or not is_int(value.get("execution_log_start_offset"))
                    or value["execution_log_start_offset"] < 0
                    or not is_int(value.get("runner_pid"))
                    or value["runner_pid"] < 1
                    or type(value.get("runner_process_starttime")) is not str
                    or re.fullmatch(r"[0-9]+", value["runner_process_starttime"]) is None):
                valid = False
            run = Path(manifest["__run_root"])
            lock_path = run / "locks" / (state.path.stem + ".lock")
            lock = load_artifact(lock_path, diagnostics)
            expected_lock = {
                "schema": "paired_open_problem_cell_lock_v1",
                "run_id": manifest["run_id"], "pid": value.get("runner_pid"),
                "process_starttime": value.get("runner_process_starttime"),
                "record_id": record_id, "arm": arm, "iteration": iteration,
                "stage": stage, "started_at": value.get("started_at"),
                "runtime_seal_sha256": runtime_expected["runtime_seal_sha256"],
                "runner_sha256": runtime_expected["runner_sha256"],
            }
            old_owner_alive = process_identity_alive(
                value.get("runner_pid"), value.get("runner_process_starttime")
            )
            if lock is None:
                # SIGKILL can land after a proved-stale lock is unlinked but
                # before its retry lock is published.  Admit only a fully
                # validated state whose exact old PID/starttime is dead.
                if os.path.lexists(lock_path) or old_owner_alive is not False:
                    valid = False
            elif lock.value != expected_lock:
                # A second narrow SIGKILL window exists after the new lock is
                # published but before RUNNING is atomically refreshed.  The
                # old owner must be dead and the replacement lock must itself
                # have the complete sealed canonical identity.
                replacement = lock.value
                replacement_keys = {
                    "schema", "run_id", "pid", "process_starttime",
                    "record_id", "arm", "iteration", "stage", "started_at",
                    "runtime_seal_sha256", "runner_sha256",
                }
                replacement_valid = bool(
                    set(replacement) == replacement_keys
                    and replacement.get("schema") ==
                    "paired_open_problem_cell_lock_v1"
                    and replacement.get("run_id") == manifest["run_id"]
                    and replacement.get("record_id") == record_id
                    and replacement.get("arm") == arm
                    and replacement.get("iteration") == iteration
                    and replacement.get("stage") == stage
                    and is_int(replacement.get("pid"))
                    and replacement["pid"] >= 1
                    and type(replacement.get("process_starttime")) is str
                    and re.fullmatch(
                        r"[0-9]+", replacement["process_starttime"]
                    ) is not None
                    and type(replacement.get("started_at")) is str
                    and bool(replacement["started_at"])
                    and replacement.get("runtime_seal_sha256") ==
                    runtime_expected["runtime_seal_sha256"]
                    and replacement.get("runner_sha256") ==
                    runtime_expected["runner_sha256"]
                )
                if old_owner_alive is not False or not replacement_valid:
                    valid = False
            log = expected_log_path(
                run, (record_id, arm, iteration, stage)
            )
            if (not log.is_file() or log.is_symlink()
                    or log.stat().st_size <
                    value.get("execution_log_start_offset", 0)):
                valid = False
            else:
                try:
                    valid = (value.get("execution_log_prefix_sha256") ==
                             execution_log_prefix_sha(
                                 log, value["execution_log_start_offset"]
                             )) and valid
                except (OSError, ValueError):
                    valid = False
        elif status in {"FAILED", "SPAWN_FAILED"}:
            common_keys = {
                "run_id", "record_id", "arm", "iteration", "stage", "status",
                "started_at", "ended_at", "duration_seconds", "error",
                "tokens_used", "model", "reasoning_effort",
                "execution_log_start_offset", "execution_log_prefix_sha256",
                "execution_log_segment",
                "run_manifest_sha256", "runtime_seal_sha256",
                "runtime_seal_payload_sha256", "runner_sha256",
            }
            if (set(value) != common_keys | set(prefix_fields)
                    or type(value.get("started_at")) is not str
                    or type(value.get("ended_at")) is not str
                    or not is_duration(value.get("duration_seconds"))
                    or type(value.get("error")) is not str
                    or not value["error"]):
                valid = False
            if model_call:
                if (value.get("tokens_used") is not None
                        and not is_token_count(value.get("tokens_used"))):
                    valid = False
                if value.get("model") not in {
                        None, manifest["execution"]["model"]}:
                    valid = False
                if value.get("reasoning_effort") not in {
                        None, manifest["execution"]["reasoning_effort"]}:
                    valid = False
            elif (value.get("tokens_used") != 0 or value.get("model") is not None
                  or value.get("reasoning_effort") is not None):
                valid = False
            run = Path(manifest["__run_root"])
            log = expected_log_path(run, (record_id, arm, iteration, stage))
            if not log.is_file() or log.is_symlink():
                valid = False
            else:
                valid = validate_log(log, state, diagnostics) and valid
        else:
            valid = False
    if complete:
        run = Path(manifest["__run_root"])
        log = expected_log_path(run, (record_id, arm, iteration, stage))
        valid = validate_log(log, state, diagnostics) and valid
    if prompt_sha256 is not None and value.get("prompt_sha256") != prompt_sha256:
        valid = False
    fields_to_check = dict(effective_fields)
    if not complete:
        fields_to_check.pop("finalized_output", None)
    if any(value.get(key) != wanted for key, wanted in fields_to_check.items()):
        valid = False
    if valid and not complete:
        diagnostics.missing(
            "CALL_NOT_COMPLETE", state.path,
            f"{stage} call has status {status!r}; a valid completed call is required",
        )
        return False, None
    if not valid:
        diagnostics.bad("STATE_CONTRACT", state.path,
                        "call state envelope/identity/model/effort/tokens/runtime binding mismatch")
    return valid, tokens if is_token_count(tokens) else None


def input_path(run: Path, record_id: str) -> Path:
    return run / "inputs" / f"{record_id}.json"


def baseline_path(run: Path, record_id: str) -> Path:
    return run / "baselines" / f"{record_id}.json"


def baseline_audit_path(run: Path, record_id: str) -> Path:
    return run / "audits" / "baseline" / f"{record_id}.json"


def revision_path(run: Path, record_id: str, arm: str, iteration: int) -> Path:
    return run / "iterations" / record_id / arm / f"iter_{iteration}.json"


def revision_audit_path(run: Path, record_id: str, arm: str,
                        iteration: int) -> Path:
    return run / "audits" / "iterations" / record_id / arm / f"iter_{iteration}.json"


def receipt_path(run: Path, record_id: str, iteration: int) -> Path:
    return run / "retrievals" / f"{record_id}__iter_{iteration}.json"


def prompt_path(run: Path, record_id: str, arm: str, iteration: int) -> Path:
    return run / "prompts" / f"{record_id}__{arm}__iter_{iteration}.json"


def audit_metadata_path(run: Path, record_id: str, arm: str,
                        iteration: int) -> Path:
    if arm == "neutral":
        return run / "audits" / "metadata" / "baseline" / f"{record_id}.json"
    return (run / "audits" / "metadata" / "iterations" / record_id / arm /
            f"iter_{iteration}.json")


def terminal_path(run: Path, record_id: str) -> Path:
    return run / "pair_terminals" / f"{record_id}.json"


def expected_baseline_prompt(run: Path, manifest: Mapping[str, Any],
                             record_id: str) -> str:
    source = input_path(run, record_id)
    scratch = Path(manifest["operations"]["scratch_root"]) / record_id / "baseline"
    quoted_id = json.dumps(record_id, ensure_ascii=False)
    return f'''You are solving one research problem.

Read ONLY {source}. Its "target" is the exact research problem; use "source_paper_text" only for definitions and results already proved there. Do not read any other file and do not use the web. You may create and run exact-arithmetic checks under {scratch}, but do not modify files outside that directory.

Produce your strongest rigorous progress from scratch. A FULL result requires a complete proof of the recorded target. Otherwise give precisely scoped partial results, reductions, bounds, special cases, or a concrete counterexample to a natural conjecture. Put every load-bearing claim in its own results item, in proof order. There is no claim-count cap; do not omit a claim merely to keep the list short. Prefer sound claims to speculative breadth. Check finite assertions whenever practical, persist reusable checker programs under the scratch directory, and describe the checks in checks_performed.

Hard limits: final_writeup under 3,000 words and each proof_sketch under 500 words. Return JSON matching the schema, with record_id exactly {quoted_id} and stage exactly "BASELINE".'''


def expected_audit_prompt(run: Path, manifest: Mapping[str, Any],
                          record_id: str, arm: str, iteration: int,
                          parent: Artifact) -> str:
    source = input_path(run, record_id)
    if arm == "neutral":
        parent_path = baseline_path(run, record_id)
        scratch = (Path(manifest["operations"]["scratch_root"]) / record_id /
                   "audit-baseline")
        stage = "BASELINE_AUDIT"
    else:
        parent_path = revision_path(run, record_id, arm, iteration)
        scratch = (Path(manifest["operations"]["scratch_root"]) / record_id /
                   "audit-revision" / arm / f"iter_{iteration}")
        stage = "REVISION_AUDIT"
    claims = [
        {"idx": index, "claim": row["claim"],
         "claim_sha256": sha_text(row["claim"])}
        for index, row in enumerate(parent.value["results"])
    ]
    claim_json = json.dumps(claims, ensure_ascii=False, indent=2)
    quoted_id = json.dumps(record_id, ensure_ascii=False)
    return f'''You are independently checking a proposed solution to one research problem.

Read ONLY source input {source} and draft {parent_path}. Do not read any other file and do not use the web. Do not trust claimed_resolution or self_assessment.

First judge target coverage independently. Read the exact target, not merely the draft's claim list. target_verdict is FULLY_RESOLVES_TARGET only if the draft proves the entire requested target at the requested strength; VALID_PARTIAL_PROGRESS for correct but incomplete progress; NO_VALID_PROGRESS if nothing material survives; and OVERCLAIMED when the headline/final writeup asserts coverage not established by the claims. Separately judge whether claimed_resolution is ACCURATE, OVERSTATED, or UNDERSTATED. Explain this in target_evidence. A technically true but vacuous, much coarser, or mismatched result does not fully resolve a requested matching/tight classification.

Then audit every listed claim from scratch. Hunt for missing cases, quantifier errors, model or statement mismatches, invalid reductions, and counterexamples. For finite or computational claims, write and run exact-arithmetic checks under {scratch}; never use floating point for a decision. Persist each checker program under that exact directory and return its absolute path in checker_path. Use literal "none" for witness, search_method, or checker_path only when genuinely inapplicable. A finite counterexample requires a concrete witness and persisted checker. VERIFIED requires a rigorous completed proof; REFUTED requires a concrete reproducible flaw or counterexample; otherwise use UNRESOLVED.

The parent SHA-256 is {parent.sha256}. Return record_id {quoted_id}, stage {stage}, iteration {iteration}, and parent_sha256 exactly as supplied. Exact claim bindings:
{claim_json}

Preserve every idx, claim, and claim_sha256 exactly. confirmed_refutations must be exactly the increasing idx list for REFUTED claims. overall is REFUTED if any claim is refuted, VERIFIED only if the nonempty list is entirely verified, and INCONCLUSIVE otherwise. Return schema-valid JSON. Do not modify repository files.'''


def _bugbank_count(text: str) -> int:
    return len(re.findall("bugbank", text, flags=re.IGNORECASE))


def expected_revision_prompt(run: Path, manifest: Mapping[str, Any],
                             record_id: str, arm: str, iteration: int,
                             parent: Artifact, audit: Artifact,
                             receipt: Artifact | None,
                             retrieved: Sequence[str]) -> tuple[str, dict[str, Any]]:
    source_path = input_path(run, record_id)
    parent_file = (baseline_path(run, record_id) if iteration == 1 else
                   revision_path(run, record_id, arm, iteration - 1))
    audit_file = (baseline_audit_path(run, record_id) if iteration == 1 else
                  revision_audit_path(run, record_id, arm, iteration - 1))
    scratch = (Path(manifest["operations"]["scratch_root"]) / record_id /
               "revision" / arm / f"iter_{iteration}")
    audit_raw = audit.raw.decode("utf-8")
    closure = '''
Proof-state closure is exact over claimed_resolution, every claim and proof_sketch in results, and final_writeup. If no material correction is required, copy those fields from the parent exactly; do not paraphrase or polish them. Bookkeeping fields may change independently.

'''
    common = f'''You are revising one proposed solution to a research problem.

Read only source {source_path}, exact parent {parent_file}, and its independent audit {audit_file}. The source defines the target. Parent SHA-256: {parent.sha256}. Audit SHA-256: {audit.sha256}. Do not read any other file and do not use the web. Write exact-arithmetic checks only under {scratch}; do not modify files outside that directory.

Respond to every REFUTED or UNRESOLVED item and to the target-coverage and claimed-resolution judgments. Preserve correct progress; repair, narrow, replace, or remove unsupported claims. Do not call an open target solved without a complete proof at the requested strength. Keep exact claim wording when it remains correct; gratuitous rewording prevents a reproducible fixed point. Preserve every current load-bearing claim and add a separate results item for every new load-bearing claim when the proof expands. There is no claim-count cap. Keep final_writeup under 3,000 words and each proof_sketch under 500 words.

{closure}The complete independent audit follows verbatim:
--- BEGIN INDEPENDENT AUDIT ---
{audit_raw}--- END INDEPENDENT AUDIT ---

'''
    if arm == "plain":
        prompt = common + '''Use your own adversarial self-critique and the independent audit. Return JSON matching the supplied schema. Fixed provenance fields are added by the wrapper after your response.'''
        source_raw = source_path.read_text(encoding="utf-8")
        parent_raw = parent.raw.decode("utf-8")
        input_count = add_token_counts(*(
            _bugbank_count(text) for text in (source_raw, parent_raw, audit_raw)
        ))
        exposure = {
            "complete_receipt_payload_embedded": False,
            "receipt_verbatim_occurrences": 0,
            "receipt_start_byte": None,
            "receipt_end_byte": None,
            "plain_input_treatment_name_token_count": input_count,
            "prompt_treatment_name_token_count": _bugbank_count(prompt),
            "complete_receipt_marker_count": 0,
            "exposed_forbidden_treatment_hashes": [],
            "retrieved_entry_ids": [],
        }
    else:
        if receipt is None:
            raise ValueError("treated prompt requires a receipt")
        action = (' In this closure protocol, list an ID in acted_on_entry_ids only '
                  'when this iteration materially changes the proof state because of '
                  'that record. If the parent already addresses the risk and no new '
                  'proof change is needed, put the ID in dismissed_hits and state that reason.')
        prefix = (common + 'Use the following complete BugBank exposure receipt as '
                  'diagnostic memory, not authority. Independently check every applicable '
                  'counterexample and hypothesis warning. For every unique retrieved ID, '
                  'either list it in acted_on_entry_ids or give a specific reason in '
                  f'dismissed_hits.{action} Preserve first-retrieval order; the two lists '
                  'must partition retrieved_entry_ids. The wrapper owns all lineage and '
                  'exposure fields.\n\n'
                  '--- BEGIN COMPLETE BUGBANK EXPOSURE RECEIPT ---\n')
        receipt_raw = receipt.raw.decode("utf-8")
        relative_receipt = repo_path(receipt.path)
        ids_json = json.dumps(list(retrieved), ensure_ascii=False, indent=2)
        suffix = (f'--- END COMPLETE BUGBANK EXPOSURE RECEIPT ---\n\n'
                  'Return revision-schema JSON. Use treatment_status '
                  f'BUGBANK_RECEIPT_EXPOSED and receipt_path {json.dumps(relative_receipt)}. '
                  'Exact unique retrieved_entry_ids in first-retrieval order:\n'
                  f'{ids_json}')
        prompt = prefix + receipt_raw + suffix
        character_offset = prompt.find(receipt_raw)
        start = len(prompt[:character_offset].encode("utf-8"))
        exposure = {
            "complete_receipt_payload_embedded": True,
            "receipt_verbatim_occurrences": prompt.count(receipt_raw),
            "receipt_start_byte": start,
            "receipt_end_byte": add_token_counts(start, receipt.size_bytes),
            "plain_input_treatment_name_token_count": None,
            "prompt_treatment_name_token_count": _bugbank_count(prompt),
            "retrieved_entry_ids": list(retrieved),
        }
    return prompt, exposure


@dataclass
class Inventory:
    baselines: dict[str, Path] = field(default_factory=dict)
    baseline_audits: dict[str, Path] = field(default_factory=dict)
    baseline_metadata: dict[str, Path] = field(default_factory=dict)
    revisions: dict[tuple[str, str, int], Path] = field(default_factory=dict)
    revision_audits: dict[tuple[str, str, int], Path] = field(default_factory=dict)
    revision_metadata: dict[tuple[str, str, int], Path] = field(default_factory=dict)
    receipts: dict[tuple[str, int], Path] = field(default_factory=dict)
    prompts: dict[tuple[str, str, int], Path] = field(default_factory=dict)
    terminals: dict[str, Path] = field(default_factory=dict)
    states: dict[tuple[str, str | None, int | None, str], Path] = field(
        default_factory=dict
    )
    checkers: dict[tuple[str, str, int, int], Path] = field(default_factory=dict)
    recoveries: dict[tuple[str, str, int], Path] = field(default_factory=dict)
    locks: dict[tuple[str, str | None, int | None, str], Path] = field(
        default_factory=dict
    )
    forensic_files: set[Path] = field(default_factory=set)


def _regular_files(root: Path, diagnostics: Diagnostics) -> list[Path]:
    if not root.exists():
        return []
    if root.is_symlink() or not root.is_dir():
        diagnostics.bad("EVIDENCE_ROOT_INVALID", root,
                        "evidence root must be a real directory")
        return []
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        try:
            info = path.lstat()
        except OSError as error:
            diagnostics.bad("EVIDENCE_ENTRY_UNREADABLE", path, str(error))
            continue
        if stat.S_ISLNK(info.st_mode):
            diagnostics.bad("SYMLINK_ARTIFACT", path,
                            "evidence paths may not contain symlinks")
        elif stat.S_ISREG(info.st_mode):
            files.append(path.resolve())
        elif not stat.S_ISDIR(info.st_mode):
            diagnostics.bad("SPECIAL_EVIDENCE_ENTRY", path,
                            "evidence paths may contain only directories and regular files")
    return files


def _insert_unique(mapping: dict[Any, Path], key: Any, path: Path,
                   diagnostics: Diagnostics) -> None:
    if key in mapping:
        diagnostics.bad("DUPLICATE_ARTIFACT", path,
                        f"duplicate canonical artifact identity {key!r}")
    else:
        mapping[key] = path


def discover_inventory(run: Path, roster: Sequence[str], maximum: int,
                       diagnostics: Diagnostics) -> Inventory:
    inventory = Inventory()
    roster_set = set(roster)

    def simple(directory: Path, target: dict[str, Path], label: str) -> None:
        for path in _regular_files(directory, diagnostics):
            relative = path.relative_to(directory.resolve())
            if len(relative.parts) != 1 or path.suffix != ".json":
                diagnostics.bad("NONCANONICAL_ARTIFACT_PATH", path,
                                f"{label} must be <record>.json")
                continue
            record_id = path.stem
            if record_id not in roster_set:
                diagnostics.bad("ARTIFACT_OUTSIDE_ROSTER", path,
                                f"unknown record {record_id!r}")
                continue
            _insert_unique(target, record_id, path, diagnostics)

    simple(run / "baselines", inventory.baselines, "baseline")
    simple(run / "audits" / "baseline", inventory.baseline_audits,
           "baseline audit")
    simple(run / "audits" / "metadata" / "baseline",
           inventory.baseline_metadata, "baseline audit metadata")
    simple(run / "pair_terminals", inventory.terminals, "pair terminal")

    def tree(directory: Path, target: dict[tuple[str, str, int], Path],
             label: str) -> None:
        for path in _regular_files(directory, diagnostics):
            relative = path.relative_to(directory.resolve())
            if len(relative.parts) != 3:
                diagnostics.bad("NONCANONICAL_ARTIFACT_PATH", path,
                                f"{label} must be <record>/<arm>/iter_N.json")
                continue
            record_id, arm, filename = relative.parts
            match = re.fullmatch(r"iter_(\d+)\.json", filename)
            if (record_id not in roster_set or arm not in ARMS or match is None):
                diagnostics.bad("NONCANONICAL_ARTIFACT_PATH", path,
                                f"invalid {label} identity")
                continue
            iteration = int(match.group(1))
            if not 1 <= iteration <= maximum:
                diagnostics.bad("ITERATION_OUT_OF_RANGE", path,
                                f"iteration must be in 1..{maximum}")
                continue
            _insert_unique(target, (record_id, arm, iteration), path, diagnostics)

    tree(run / "iterations", inventory.revisions, "revision")
    tree(run / "audits" / "iterations", inventory.revision_audits,
         "revision audit")
    tree(run / "audits" / "metadata" / "iterations",
         inventory.revision_metadata, "revision audit metadata")

    for path in _regular_files(run / "retrievals", diagnostics):
        relative = path.relative_to((run / "retrievals").resolve())
        match = (re.fullmatch(r"(.+)__iter_(\d+)\.json", relative.name)
                 if len(relative.parts) == 1 else None)
        if match is None or match.group(1) not in roster_set:
            diagnostics.bad("NONCANONICAL_RECEIPT_PATH", path,
                            "receipt must be <record>__iter_N.json")
            continue
        iteration = int(match.group(2))
        if not 1 <= iteration <= maximum:
            diagnostics.bad("ITERATION_OUT_OF_RANGE", path,
                            f"iteration must be in 1..{maximum}")
            continue
        _insert_unique(inventory.receipts, (match.group(1), iteration), path,
                       diagnostics)

    for path in _regular_files(run / "prompts", diagnostics):
        relative = path.relative_to((run / "prompts").resolve())
        match = (re.fullmatch(r"(.+)__(plain|bugbank)__iter_(\d+)\.json",
                              relative.name)
                 if len(relative.parts) == 1 else None)
        if match is None or match.group(1) not in roster_set:
            diagnostics.bad("NONCANONICAL_PROMPT_PATH", path,
                            "prompt must be <record>__<arm>__iter_N.json")
            continue
        iteration = int(match.group(3))
        if not 1 <= iteration <= maximum:
            diagnostics.bad("ITERATION_OUT_OF_RANGE", path,
                            f"iteration must be in 1..{maximum}")
            continue
        _insert_unique(inventory.prompts,
                       (match.group(1), match.group(2), iteration), path,
                       diagnostics)

    for path in _regular_files(run / "states", diagnostics):
        relative = path.relative_to((run / "states").resolve())
        if len(relative.parts) != 1 or path.suffix != ".json":
            diagnostics.bad("NONCANONICAL_STATE_PATH", path,
                            "state must be directly under states/")
            continue
        name = relative.name
        match = re.fullmatch(
            r"(.+)__(plain|bugbank)__iter_(\d+)__(receipt|revision|audit-revision)\.json",
            name,
        )
        if match is not None:
            record_id, arm, raw_iteration, stage = match.groups()
            iteration = int(raw_iteration)
            if record_id not in roster_set or (stage == "receipt" and arm != "bugbank"):
                diagnostics.bad("NONCANONICAL_STATE_PATH", path,
                                "state record/arm/stage identity is invalid")
                continue
            if not 1 <= iteration <= maximum:
                diagnostics.bad("ITERATION_OUT_OF_RANGE", path,
                                f"iteration must be in 1..{maximum}")
                continue
            _insert_unique(inventory.states,
                           (record_id, arm, iteration, stage), path, diagnostics)
            continue
        match = re.fullmatch(r"(.+)__(baseline|audit-baseline)\.json", name)
        if match is not None and match.group(1) in roster_set:
            _insert_unique(inventory.states,
                           (match.group(1), None, None, match.group(2)), path,
                           diagnostics)
            continue
        diagnostics.bad("NONCANONICAL_STATE_PATH", path,
                        "state filename has no canonical cell identity")

    checker_root = run / "checkers" / "audits"
    for path in _regular_files(checker_root, diagnostics):
        relative = path.relative_to(checker_root.resolve())
        identity: tuple[str, str, int, int] | None = None
        if len(relative.parts) == 3 and relative.parts[0] == "baseline":
            record_id = relative.parts[1]
            match = re.fullmatch(r"claim_(\d+)__([0-9a-f]{64})\.checker",
                                 relative.parts[2])
            if record_id in roster_set and match is not None:
                identity = (record_id, "neutral", 0, int(match.group(1)))
        elif len(relative.parts) == 5 and relative.parts[0] == "iterations":
            record_id, arm, raw_iteration, filename = (
                relative.parts[1], relative.parts[2], relative.parts[3],
                relative.parts[4]
            )
            iteration_match = re.fullmatch(r"iter_(\d+)", raw_iteration)
            checker_match = re.fullmatch(
                r"claim_(\d+)__([0-9a-f]{64})\.checker", filename
            )
            if (record_id in roster_set and arm in ARMS
                    and iteration_match is not None and checker_match is not None):
                iteration = int(iteration_match.group(1))
                if 1 <= iteration <= maximum:
                    identity = (record_id, arm, iteration,
                                int(checker_match.group(1)))
        if identity is None:
            diagnostics.bad("NONCANONICAL_CHECKER_PATH", path,
                            "durable checker path is not canonical")
            continue
        _insert_unique(inventory.checkers, identity, path, diagnostics)

    recovery_root = run / "recoveries" / "revisions"
    for path in _regular_files(recovery_root, diagnostics):
        relative = path.relative_to(recovery_root.resolve())
        match = (re.fullmatch(
            r"(.+)__(plain|bugbank)__iter_(\d+)__pid_(\d+)\.json",
            relative.name,
        ) if len(relative.parts) == 1 else None)
        if match is None or match.group(1) not in roster_set:
            diagnostics.bad("NONCANONICAL_RECOVERY_PATH", path,
                            "revision recovery path is not canonical")
            continue
        iteration = int(match.group(3))
        if not 1 <= iteration <= maximum:
            diagnostics.bad("ITERATION_OUT_OF_RANGE", path,
                            f"iteration must be in 1..{maximum}")
            continue
        _insert_unique(inventory.recoveries,
                       (match.group(1), match.group(2), iteration), path,
                       diagnostics)
    inventory.forensic_files.update(_regular_files(run / "forensics", diagnostics))

    current_seal_sha256 = (
        sha_file(run / "RUNTIME_SEAL.json")
        if (run / "RUNTIME_SEAL.json").is_file() else None
    )
    current_runner_sha256 = sha_file(
        SCRIPT.with_name("paired_open_problem_exploratory_runtime_r3_runner.mjs")
    )
    for path in _regular_files(run / "locks", diagnostics):
        name = path.name
        identity: tuple[str, str | None, int | None, str] | None = None
        match = re.fullmatch(
            r"(.+)__(plain|bugbank)__iter_(\d+)__(receipt|revision|audit-revision)\.lock",
            name,
        )
        if match is not None:
            record_id, arm, raw_iteration, stage = match.groups()
            iteration = int(raw_iteration)
            if (record_id in roster_set and 1 <= iteration <= maximum
                    and not (stage == "receipt" and arm != "bugbank")):
                identity = (record_id, arm, iteration, stage)
        else:
            match = re.fullmatch(r"(.+)__(baseline|audit-baseline)\.lock", name)
            if match is not None and match.group(1) in roster_set:
                identity = (match.group(1), None, None, match.group(2))
        lock = load_artifact(path, diagnostics)
        if identity is None or lock is None:
            diagnostics.bad("NONCANONICAL_LOCK", path,
                            "lock path/payload has no canonical cell identity")
            continue
        record_id, arm, iteration, stage = identity
        expected_lock_keys = {
            "schema", "run_id", "pid", "process_starttime", "record_id",
            "arm", "iteration", "stage", "started_at",
            "runtime_seal_sha256", "runner_sha256",
        }
        if (set(lock.value) != expected_lock_keys
                or lock.value.get("schema") != "paired_open_problem_cell_lock_v1"
                or lock.value.get("run_id") != run.name
                or lock.value.get("record_id") != record_id
                or lock.value.get("arm") != arm
                or lock.value.get("iteration") != iteration
                or lock.value.get("stage") != stage
                or not is_int(lock.value.get("pid")) or lock.value["pid"] < 1
                or type(lock.value.get("process_starttime")) is not str
                or re.fullmatch(r"[0-9]+", lock.value["process_starttime"]) is None
                or type(lock.value.get("started_at")) is not str
                or not lock.value["started_at"]
                or lock.value.get("runtime_seal_sha256") !=
                current_seal_sha256
                or lock.value.get("runner_sha256") !=
                current_runner_sha256):
            diagnostics.bad("LOCK_CONTRACT", path,
                            "lock payload differs from its canonical cell identity")
            continue
        matching_state_path = state_path(
            run, record_id, stage, arm, iteration
        )
        if matching_state_path.is_file():
            matching_state = load_artifact(matching_state_path, diagnostics)
            if matching_state is None:
                diagnostics.bad("LOCK_STATE_BINDING", path,
                                "cell lock has a malformed matching state")
                continue
            state_value = matching_state.value
            admission_matches = bool(
                state_value.get("started_at") == lock.value["started_at"]
                and (state_value.get("status") != "RUNNING" or (
                    state_value.get("runner_pid") == lock.value["pid"]
                    and state_value.get("runner_process_starttime") ==
                    lock.value["process_starttime"]))
            )
            if not admission_matches:
                running_retry_window = bool(
                    state_value.get("status") == "RUNNING"
                    and process_identity_alive(
                        state_value.get("runner_pid"),
                        state_value.get("runner_process_starttime"),
                    ) is False
                )
                failed_replacement_window = False
                if (state_value.get("status") in {"FAILED", "SPAWN_FAILED"}
                        and type(state_value.get("started_at")) is str
                        and type(lock.value.get("started_at")) is str):
                    try:
                        old_started = datetime.fromisoformat(
                            state_value["started_at"].replace("Z", "+00:00")
                        )
                        new_started = datetime.fromisoformat(
                            lock.value["started_at"].replace("Z", "+00:00")
                        )
                        failed_replacement_window = new_started > old_started
                    except ValueError:
                        failed_replacement_window = False
                if not running_retry_window and not failed_replacement_window:
                    diagnostics.bad(
                        "LOCK_STATE_BINDING", path,
                        "cell lock PID/starttime/admission does not bind its retryable state",
                    )
                    continue
        _insert_unique(inventory.locks, identity, path, diagnostics)
        diagnostics.missing("ACTIVE_LOCK", path,
                            "an active or stale cell lock remains; the run is unfinished")
    return inventory


def validate_prompt_metadata_exact(
        metadata: Artifact, record_id: str, arm: str, iteration: int,
        source: Artifact, parent: Artifact, audit: Artifact,
        receipt: Artifact | None, retrieved: Sequence[str],
        manifest: Mapping[str, Any], diagnostics: Diagnostics,
        run: Path) -> tuple[bool, str]:
    valid = validate_prompt_metadata(
        metadata, record_id, arm, iteration, source, parent, audit,
        receipt, retrieved, manifest, diagnostics, run,
    )
    try:
        expected_prompt, expected_exposure = expected_revision_prompt(
            run, manifest, record_id, arm, iteration, parent, audit,
            receipt, retrieved,
        )
    except (OSError, UnicodeDecodeError, ValueError, KeyError) as error:
        diagnostics.bad("PROMPT_RECOMPUTE_FAILED", metadata.path, str(error))
        return False, ""
    value = metadata.value
    expected_receipt = None
    if receipt is not None:
        expected_receipt = binding(receipt) | {
            "receipt_payload_sha256": receipt.value.get("receipt_payload_sha256")
        }
    exact_fields = {
        "prompt_text": expected_prompt,
        "prompt_utf8_sha256": sha_text(expected_prompt),
        "prompt_size_bytes": len(expected_prompt.encode("utf-8")),
        "exposure": expected_exposure,
        "receipt": expected_receipt,
    }
    if any(value.get(key) != wanted for key, wanted in exact_fields.items()):
        diagnostics.bad("PROMPT_NOT_EXACT", metadata.path,
                        "stored prompt/exposure differs from independent reconstruction")
        valid = False
    allowed = {
        "schema", "run_id", "record_id", "stage", "arm", "iteration",
        "claim_coverage_policy", "treatment_status", "bugbank_exposed",
        "prompt_text", "prompt_utf8_sha256", "prompt_size_bytes", "source",
        "parent", "audit", "receipt", "exposure", "run_manifest",
        "runtime_seal", "requested_execution", "created_at",
        "metadata_payload_sha256",
    }
    if set(value) != allowed or type(value.get("created_at")) is not str \
            or not value["created_at"].strip():
        diagnostics.bad("PROMPT_METADATA_SHAPE", metadata.path,
                        "prompt metadata has missing or unexpected fields")
        valid = False
    return valid, expected_prompt


def validate_audit_metadata_exact(
        metadata: Artifact, audit: Artifact, parent: Artifact,
        source: Artifact, record_id: str, arm: str, iteration: int,
        manifest: Mapping[str, Any], seal: Mapping[str, Any],
        expected_prompt: str, diagnostics: Diagnostics,
        run: Path) -> bool:
    valid = validate_audit_metadata(
        metadata, audit, parent, source, record_id, arm, iteration,
        manifest, seal, diagnostics, run,
    )
    value = metadata.value
    if (value.get("prompt_text") != expected_prompt
            or value.get("prompt_utf8_sha256") != sha_text(expected_prompt)
            or value.get("prompt_size_bytes") != len(expected_prompt.encode("utf-8"))):
        diagnostics.bad("AUDIT_PROMPT_NOT_EXACT", metadata.path,
                        "audit prompt differs from independent reconstruction")
        valid = False
    allowed = {
        "schema", "run_id", "record_id", "stage", "arm", "iteration",
        "source", "parent", "run_manifest", "runtime_seal", "prompt_text",
        "prompt_utf8_sha256", "prompt_size_bytes", "requested_execution",
        "checker_artifacts", "metadata_payload_sha256",
    }
    if set(value) != allowed:
        diagnostics.bad("AUDIT_METADATA_SHAPE", metadata.path,
                        "audit metadata has missing or unexpected fields")
        valid = False
    expected_directory = (
        run / "checkers" / "audits" / "baseline" / record_id
        if arm == "neutral" else
        run / "checkers" / "audits" / "iterations" / record_id / arm /
        f"iter_{iteration}"
    )
    for row in value.get("checker_artifacts", []):
        if type(row) is not dict or not is_int(row.get("idx")):
            continue
        durable = row.get("durable")
        expected_path = expected_directory / (
            f"claim_{row['idx']}__{row.get('original_sha256')}.checker"
        )
        if (type(durable) is not dict
                or recorded_path(durable.get("path"), run) != expected_path.resolve()):
            diagnostics.bad("CHECKER_PATH_NOT_CANONICAL", metadata.path,
                            f"checker {row['idx']} is outside its canonical durable path")
            valid = False
    return valid


def ordered_claims(value: Mapping[str, Any]) -> list[str]:
    return [row["claim"] for row in value["results"]]


def proof_state_sha256(value: Mapping[str, Any]) -> str:
    return sha_bytes(canonical_bytes(proof_state(value)))


def audit_verifies_full(revision: Artifact, audit: Artifact) -> bool:
    claims = audit.value.get("claims")
    results = revision.value.get("results")
    return bool(
        audit.value.get("complete") is True
        and revision.value.get("claimed_resolution") == "FULL"
        and type(results) is list and type(claims) is list and bool(claims)
        and len(results) == len(claims)
        and all(type(row) is dict and row.get("verdict") == "VERIFIED"
                for row in claims)
        and audit.value.get("confirmed_refutations") == []
        and audit.value.get("target_verdict") == "FULLY_RESOLVES_TARGET"
        and audit.value.get("claimed_resolution_verdict") == "ACCURATE"
        and audit.value.get("overall") == "VERIFIED"
    )


def audit_is_settled(audit: Artifact) -> bool:
    return bool(
        audit.value.get("complete") is True
        and audit.value.get("confirmed_refutations") == []
        and audit.value.get("claimed_resolution_verdict") == "ACCURATE"
        and audit.value.get("target_verdict") != "OVERCLAIMED"
    )


@dataclass
class IterationBundle:
    record_id: str
    arm: str
    iteration: int
    parent: Artifact | None = None
    parent_audit: Artifact | None = None
    receipt: Artifact | None = None
    prompt: Artifact | None = None
    revision: Artifact | None = None
    audit: Artifact | None = None
    audit_metadata: Artifact | None = None
    states: dict[str, Artifact] = field(default_factory=dict)
    retrieved: list[str] = field(default_factory=list)
    valid: bool = False
    revision_tokens: int | None = None
    audit_tokens: int | None = None


@dataclass
class BaselineBundle:
    source: Artifact | None = None
    draft: Artifact | None = None
    audit: Artifact | None = None
    audit_metadata: Artifact | None = None
    valid: bool = False


def execution_costs(run: Path, inventory: Inventory,
                    bundles: Mapping[int, IterationBundle], record_id: str,
                    arm: str, through_iteration: int,
                    diagnostics: Diagnostics) -> dict[str, Any] | None:
    entries: list[dict[str, Any]] = []
    for iteration in range(1, through_iteration + 1):
        bundle = bundles.get(iteration)
        stages = ("receipt", "revision", "audit-revision") if arm == "bugbank" \
            else ("revision", "audit-revision")
        for stage in stages:
            state = bundle.states.get(stage) if bundle is not None else None
            if state is None:
                entries.append({
                    "stage": stage,
                    "iteration": iteration,
                    "state_path": repo_path(state_path(
                        run, record_id, stage, arm, iteration
                    )),
                    "missing": True,
                })
                continue
            value = state.value
            entries.append({
                "stage": stage,
                "iteration": iteration,
                "state_path": repo_path(state.path),
                "missing": False,
                "status": value.get("status"),
                "tokens_used": value.get("tokens_used"),
                "duration_seconds": (value.get("duration_seconds")
                                     if is_duration(value.get("duration_seconds")) else 0),
                "model": value.get("model"),
                "reasoning_effort": value.get("reasoning_effort"),
                "prompt_size_bytes": value.get("prompt_size_bytes"),
                "receipt_exposure_bytes": value.get("receipt_exposure_bytes"),
            })
    try:
        tokens_used = add_token_counts(*(
            row.get("tokens_used") if row.get("tokens_used") is not None else 0
            for row in entries
        ))
        duration_seconds_sum = add_durations(*(
            row.get("duration_seconds")
            if row.get("duration_seconds") is not None else 0
            for row in entries
        ))
    except ValueError as error:
        diagnostics.bad(
            "NUMERIC_ACCOUNTING_OVERFLOW", run / "states",
            f"{record_id}/{arm} execution cost is not safely representable: {error}",
        )
        return None
    return {
        "tokens_used": tokens_used,
        "duration_seconds_sum": duration_seconds_sum,
        "missing_state_count": sum(bool(row.get("missing")) for row in entries),
        "entries": entries,
    }


def model_token_total(bundles: Mapping[int, IterationBundle],
                      through_iteration: int) -> tuple[int | None, bool]:
    total = 0
    for iteration in range(1, through_iteration + 1):
        bundle = bundles.get(iteration)
        if (bundle is None or bundle.revision_tokens is None
                or bundle.audit_tokens is None):
            return None, False
        total = add_token_counts(
            total, bundle.revision_tokens, bundle.audit_tokens
        )
    return total, True


def derive_endpoint(run: Path, inventory: Inventory,
                    bundles: Mapping[int, IterationBundle],
                    record_id: str, arm: str,
                    bugbank_token_target: int | None,
                    diagnostics: Diagnostics | None = None) -> dict[str, Any] | None:
    if diagnostics is None:
        diagnostics = Diagnostics(run)
    for iteration in range(1, max(bundles, default=0) + 1):
        bundle = bundles.get(iteration)
        if (bundle is None or not bundle.valid or bundle.parent is None
                or bundle.revision is None or bundle.audit is None
                or bundle.prompt is None):
            return None
        revision = bundle.revision
        audit = bundle.audit
        proof_unchanged = proof_state(bundle.parent.value) == proof_state(revision.value)
        claims_unchanged = ordered_claims(bundle.parent.value) == ordered_claims(
            revision.value
        )
        try:
            tokens, tokens_auditable = model_token_total(bundles, iteration)
        except ValueError as error:
            diagnostics.bad(
                "NUMERIC_ACCOUNTING_OVERFLOW", run / "states",
                f"{record_id}/{arm} model-token total is not safely representable: {error}",
            )
            return None
        if arm == "plain":
            budget_target = bugbank_token_target
            budget_used = tokens
            budget_auditable = tokens_auditable and is_token_count(budget_target)
            budget_matched = bool(
                budget_auditable and is_token_count(budget_used)
                and budget_used >= budget_target
            )
        else:
            budget_target = None
            budget_used = None
            budget_auditable = tokens_auditable
            budget_matched = tokens_auditable
        solved = audit_verifies_full(revision, audit)
        acted = revision.value.get("acted_on_entry_ids")
        bugbank_recheck = arm == "bugbank" and type(acted) is list and bool(acted)
        fixed = bool(
            proof_unchanged and not bugbank_recheck and audit_is_settled(audit)
            and budget_matched
        )
        if not solved and not fixed:
            continue
        terminal_reason = (
            "VERIFIED_FULL_INDEPENDENT_AUDIT" if solved else "AUDITED_FIXED_POINT"
        )
        status = "VERIFIED_FULL" if solved else "INCONCLUSIVE_FIXED_POINT"
        reason = (
            "The independent audit verified every claim and the full exact target; "
            "the arm stops at this first correct solution without further refinement "
            "or token matching."
            if solved else
            "Audited proof-state fixed point is sound against confirmed refutation "
            "and meets the arm budget condition, but does not fully resolve the target."
        )
        claims = audit.value["claims"]
        counts = {
            verdict.lower(): sum(row.get("verdict") == verdict for row in claims)
            for verdict in ("VERIFIED", "REFUTED", "UNRESOLVED")
        }
        costs = execution_costs(
            run, inventory, bundles, record_id, arm, iteration, diagnostics
        )
        if costs is None:
            return None
        return {
            "arm": arm,
            "status": status,
            "terminal": True,
            "terminal_reason": terminal_reason,
            "iteration": iteration,
            "reason": reason,
            "fixed_point": proof_unchanged if solved else True,
            "ordered_claim_set_unchanged": claims_unchanged,
            "proof_state_unchanged": proof_unchanged,
            "parent_proof_state_sha256": proof_state_sha256(bundle.parent.value),
            "revision_proof_state_sha256": proof_state_sha256(revision.value),
            "bugbank_recheck_required": False,
            "model_tokens_used": tokens,
            "model_token_cost_auditable": tokens_auditable,
            "token_budget_target": budget_target,
            "token_budget_used": budget_used,
            "token_budget_matched": budget_matched,
            "token_budget_auditable": budget_auditable,
            "token_budget_overshoot": (
                subtract_token_counts(budget_used, budget_target)
                if arm == "plain" and is_token_count(budget_used)
                and is_token_count(budget_target) else None
            ),
            "every_claim_verified": bool(claims) and all(
                row.get("verdict") == "VERIFIED" for row in claims
            ),
            "claim_count": len(revision.value["results"]),
            "audit_counts": counts,
            "claimed_resolution": revision.value.get("claimed_resolution"),
            "target_verdict": audit.value.get("target_verdict"),
            "claimed_resolution_verdict": audit.value.get(
                "claimed_resolution_verdict"
            ),
            "audit_overall": audit.value.get("overall"),
            "revision_sha256": revision.sha256,
            "audit_sha256": audit.sha256,
            "parent": binding(bundle.parent),
            "revision": binding(revision),
            "audit": binding(audit),
            "prompt_metadata": binding(bundle.prompt),
            "receipt": binding(bundle.receipt) if arm == "bugbank" else None,
            "execution_costs": costs,
            "ordered_claims_sha256": sha_bytes(canonical_bytes(
                ordered_claims(revision.value)
            )),
        }
    return None


def _required(path: Path, diagnostics: Diagnostics, code: str) -> Artifact | None:
    return load_artifact(path, diagnostics, required=True, code=code)


def validate_baseline_bundle(
        run: Path, record_id: str, manifest: Mapping[str, Any],
        seal: Mapping[str, Any], schemas: Mapping[str, Mapping[str, Any]],
        diagnostics: Diagnostics) -> BaselineBundle:
    bundle = BaselineBundle()
    bundle.source = _required(
        input_path(run, record_id), diagnostics, "SOURCE_INPUT_MISSING"
    )
    bundle.draft = _required(
        baseline_path(run, record_id), diagnostics, "BASELINE_MISSING"
    )
    draft_ok = False
    baseline_prompt_text = expected_baseline_prompt(run, manifest, record_id)
    baseline_expected_prefix = {
        "source_sha256": sha_file(input_path(run, record_id)),
        "prompt_size_bytes": len(baseline_prompt_text.encode("utf-8")),
    } | model_isolation_state_fields(
        seal, run / manifest["schemas"]["baseline"]["path"],
        [input_path(run, record_id)],
        Path(manifest["operations"]["scratch_root"]) / record_id / "baseline",
    )
    if bundle.draft is not None:
        draft_ok = validate_baseline(
            bundle.draft, record_id, schemas.get("baseline"), diagnostics
        )
        lowered = bundle.draft.raw.lower()
        if b"bugbank" in lowered or b"treatment receipt" in lowered:
            diagnostics.bad("NEUTRAL_BASELINE_TREATMENT_LEAK", bundle.draft.path,
                            "arm-neutral baseline mentions treatment evidence")
            draft_ok = False
        prompt = baseline_prompt_text
        state = _required(
            state_path(run, record_id, "baseline"), diagnostics,
            "BASELINE_STATE_MISSING",
        )
        state_ok, _ = validate_state(
            state, record_id, "baseline", None, None, manifest, seal,
            diagnostics, model_call=True, prompt_sha256=sha_text(prompt),
            expected_fields=baseline_expected_prefix | {
                "finalized_output": binding(bundle.draft),
            },
        )
        draft_ok = draft_ok and state_ok
    else:
        state = load_artifact(
            state_path(run, record_id, "baseline"), diagnostics
        )
        if state is not None:
            validate_state(
                state, record_id, "baseline", None, None, manifest, seal,
                diagnostics, model_call=True,
                prompt_sha256=sha_text(baseline_prompt_text),
                expected_fields=baseline_expected_prefix,
            )

    bundle.audit = _required(
        baseline_audit_path(run, record_id), diagnostics,
        "BASELINE_AUDIT_MISSING",
    )
    audit_ok = False
    if bundle.audit is not None:
        if bundle.draft is None:
            diagnostics.bad("ORPHAN_BASELINE_AUDIT", bundle.audit.path,
                            "baseline audit has no parent draft")
        else:
            audit_ok = validate_audit(
                bundle.audit, record_id, bundle.draft, "neutral", 0,
                schemas.get("audit"), manifest, diagnostics,
            )
            prompt = expected_audit_prompt(
                run, manifest, record_id, "neutral", 0, bundle.draft
            )
            bundle.audit_metadata = _required(
                audit_metadata_path(run, record_id, "neutral", 0), diagnostics,
                "BASELINE_AUDIT_METADATA_MISSING",
            )
            metadata_ok = False
            if bundle.audit_metadata is not None and bundle.source is not None:
                metadata_ok = validate_audit_metadata_exact(
                    bundle.audit_metadata, bundle.audit, bundle.draft,
                    bundle.source, record_id, "neutral", 0, manifest, seal,
                    prompt, diagnostics, run,
                )
            state = _required(
                state_path(run, record_id, "audit-baseline"), diagnostics,
                "BASELINE_AUDIT_STATE_MISSING",
            )
            state_ok, _ = validate_state(
                state, record_id, "audit-baseline", None, None,
                manifest, seal, diagnostics, model_call=True,
                prompt_sha256=sha_text(prompt),
                expected_fields={
                    "parent_sha256": bundle.draft.sha256,
                    "prompt_size_bytes": len(prompt.encode("utf-8")),
                    "audit_normalization_policy": "CLERICAL_BINDINGS_ONLY_V1",
                    "finalized_output": binding(bundle.audit),
                } | model_isolation_state_fields(
                    seal, run / manifest["schemas"]["audit_solver"]["path"],
                    [input_path(run, record_id), bundle.draft.path],
                    audit_scratch(manifest, record_id, "neutral", 0),
                ),
            )
            audit_ok = audit_ok and metadata_ok and state_ok
    elif bundle.draft is not None:
        prompt = expected_audit_prompt(
            run, manifest, record_id, "neutral", 0, bundle.draft
        )
        state = load_artifact(
            state_path(run, record_id, "audit-baseline"), diagnostics
        )
        if state is not None:
            validate_state(
                state, record_id, "audit-baseline", None, None,
                manifest, seal, diagnostics, model_call=True,
                prompt_sha256=sha_text(prompt),
                expected_fields={
                    "parent_sha256": bundle.draft.sha256,
                    "prompt_size_bytes": len(prompt.encode("utf-8")),
                    "audit_normalization_policy": "CLERICAL_BINDINGS_ONLY_V1",
                } | model_isolation_state_fields(
                    seal, run / manifest["schemas"]["audit_solver"]["path"],
                    [input_path(run, record_id), bundle.draft.path],
                    audit_scratch(manifest, record_id, "neutral", 0),
                ),
            )
    bundle.valid = bool(bundle.source is not None and draft_ok and audit_ok)
    return bundle


def validate_iteration_bundle(
        run: Path, record_id: str, arm: str, iteration: int,
        parent: Artifact | None, parent_audit: Artifact | None,
        manifest: Mapping[str, Any], seal: Mapping[str, Any],
        schemas: Mapping[str, Mapping[str, Any]], database: BugBankView,
        sibling_receipt: Artifact | None, diagnostics: Diagnostics
        ) -> IterationBundle:
    bundle = IterationBundle(record_id, arm, iteration, parent, parent_audit)
    if parent is None or parent_audit is None:
        diagnostics.bad(
            "ITERATION_LINEAGE_MISSING",
            revision_path(run, record_id, arm, iteration),
            "iteration lacks a valid immediate parent draft and audit",
        )
        return bundle

    receipt_ok = arm == "plain"
    if arm == "bugbank":
        bundle.receipt = _required(
            receipt_path(run, record_id, iteration), diagnostics,
            "BUGBANK_RECEIPT_MISSING",
        )
        if bundle.receipt is not None:
            receipt_ok, bundle.retrieved = validate_receipt(
                bundle.receipt, record_id, iteration, parent, manifest, seal,
                database, diagnostics, run,
            )
            state = _required(
                state_path(run, record_id, "receipt", arm, iteration), diagnostics,
                "RECEIPT_STATE_MISSING",
            )
            state_ok, _ = validate_state(
                state, record_id, "receipt", arm, iteration,
                manifest, seal, diagnostics, model_call=False,
                expected_fields={
                    "parent_sha256": parent.sha256,
                    "retrieval_k": manifest["bugbank"]["retrieval_k"],
                    "finalized_output": binding(bundle.receipt),
                },
            )
            if state is not None:
                bundle.states["receipt"] = state
            receipt_ok = receipt_ok and state_ok
        else:
            state = load_artifact(
                state_path(run, record_id, "receipt", arm, iteration), diagnostics
            )
            if state is not None:
                validate_state(
                    state, record_id, "receipt", arm, iteration,
                    manifest, seal, diagnostics, model_call=False,
                    expected_fields={
                        "parent_sha256": parent.sha256,
                        "retrieval_k": manifest["bugbank"]["retrieval_k"],
                    },
                )

    bundle.prompt = _required(
        prompt_path(run, record_id, arm, iteration), diagnostics,
        "REVISION_PROMPT_METADATA_MISSING",
    )
    prompt_ok = False
    expected_prompt = ""
    source = _required(
        input_path(run, record_id), diagnostics, "SOURCE_INPUT_MISSING"
    )
    if bundle.prompt is not None and source is not None:
        prompt_ok, expected_prompt = validate_prompt_metadata_exact(
            bundle.prompt, record_id, arm, iteration, source, parent,
            parent_audit, bundle.receipt if receipt_ok else None,
            bundle.retrieved, manifest, diagnostics, run,
        )

    revision_expected_prefix = {
        "parent_sha256": parent.sha256,
        "audit_sha256": parent_audit.sha256,
        "prompt_size_bytes": len(expected_prompt.encode("utf-8")),
        "prompt_metadata_sha256": (
            bundle.prompt.sha256 if bundle.prompt is not None else None
        ),
        "wrapper_computed_treatment_status": (
            "BUGBANK_RECEIPT_EXPOSED" if arm == "bugbank"
            else "PLAIN_SELF_CRITIQUE"
        ),
        "receipt_sha256": (
            bundle.receipt.sha256 if arm == "bugbank"
            and bundle.receipt is not None else None
        ),
        "receipt_exposure_bytes": (
            bundle.receipt.size_bytes if arm == "bugbank"
            and bundle.receipt is not None else 0
        ),
    } | model_isolation_state_fields(
        seal, run / manifest["schemas"][
            "revision_plain_solver" if arm == "plain" else "revision"
        ]["path"],
        [input_path(run, record_id), parent.path, parent_audit.path]
        + ([bundle.receipt.path] if arm == "bugbank"
           and bundle.receipt is not None else []),
        Path(manifest["operations"]["scratch_root"]) / record_id /
        "revision" / arm / f"iter_{iteration}",
    )

    bundle.revision = _required(
        revision_path(run, record_id, arm, iteration), diagnostics,
        "REVISION_MISSING",
    )
    revision_ok = False
    if bundle.revision is not None:
        revision_ok = validate_revision(
            bundle.revision, record_id, arm, iteration, parent,
            parent_audit, bundle.receipt if receipt_ok else None,
            bundle.retrieved, schemas.get("revision"), diagnostics, run,
        )
        if arm == "plain":
            forbidden: list[str] = [manifest["bugbank"]["database_sha256"]]
            if sibling_receipt is not None:
                forbidden.extend([
                    sibling_receipt.sha256,
                    sibling_receipt.value.get("receipt_payload_sha256", ""),
                ])
                for query in sibling_receipt.value.get("queries", []):
                    for hit in query.get("hits", []) if type(query) is dict else []:
                        if type(hit) is dict:
                            forbidden.append(hit.get("entry_id", ""))
            raw_text = bundle.revision.raw.decode("utf-8", errors="replace")
            leaked = sorted({item for item in forbidden
                             if type(item) is str and item and item in raw_text})
            if leaked:
                diagnostics.bad("PLAIN_REVISION_TREATMENT_LEAK",
                                bundle.revision.path,
                                "plain revision contains sealed treatment identifiers")
                revision_ok = False
        state = _required(
            state_path(run, record_id, "revision", arm, iteration), diagnostics,
            "REVISION_STATE_MISSING",
        )
        expected_state = revision_expected_prefix | {
            "finalized_output": binding(bundle.revision),
        }
        state_ok, bundle.revision_tokens = validate_state(
            state, record_id, "revision", arm, iteration, manifest, seal,
            diagnostics, model_call=True,
            prompt_sha256=sha_text(expected_prompt) if expected_prompt else None,
            expected_fields=expected_state,
        )
        if state is not None:
            bundle.states["revision"] = state
        revision_ok = revision_ok and state_ok
    else:
        state = load_artifact(
            state_path(run, record_id, "revision", arm, iteration), diagnostics
        )
        if state is not None:
            if not prompt_ok:
                diagnostics.bad(
                    "RETRYABLE_STATE_WITHOUT_VALID_PROMPT", state.path,
                    "revision call state lacks its exact independently reconstructed prompt",
                )
            else:
                validate_state(
                    state, record_id, "revision", arm, iteration,
                    manifest, seal, diagnostics, model_call=True,
                    prompt_sha256=sha_text(expected_prompt),
                    expected_fields=revision_expected_prefix,
                )

    bundle.audit = _required(
        revision_audit_path(run, record_id, arm, iteration), diagnostics,
        "REVISION_AUDIT_MISSING",
    )
    audit_ok = False
    if bundle.audit is not None:
        if bundle.revision is None:
            diagnostics.bad("ORPHAN_REVISION_AUDIT", bundle.audit.path,
                            "revision audit has no parent revision")
        else:
            audit_ok = validate_audit(
                bundle.audit, record_id, bundle.revision, arm, iteration,
                schemas.get("audit"), manifest, diagnostics,
            )
            audit_prompt = expected_audit_prompt(
                run, manifest, record_id, arm, iteration, bundle.revision
            )
            bundle.audit_metadata = _required(
                audit_metadata_path(run, record_id, arm, iteration), diagnostics,
                "REVISION_AUDIT_METADATA_MISSING",
            )
            metadata_ok = False
            if bundle.audit_metadata is not None and source is not None:
                metadata_ok = validate_audit_metadata_exact(
                    bundle.audit_metadata, bundle.audit, bundle.revision,
                    source, record_id, arm, iteration, manifest, seal,
                    audit_prompt, diagnostics, run,
                )
            state = _required(
                state_path(run, record_id, "audit-revision", arm, iteration),
                diagnostics, "REVISION_AUDIT_STATE_MISSING",
            )
            state_ok, bundle.audit_tokens = validate_state(
                state, record_id, "audit-revision", arm, iteration,
                manifest, seal, diagnostics, model_call=True,
                prompt_sha256=sha_text(audit_prompt),
                expected_fields={
                    "parent_sha256": bundle.revision.sha256,
                    "prompt_size_bytes": len(audit_prompt.encode("utf-8")),
                    "audit_normalization_policy": "CLERICAL_BINDINGS_ONLY_V1",
                    "finalized_output": binding(bundle.audit),
                } | model_isolation_state_fields(
                    seal, run / manifest["schemas"]["audit_solver"]["path"],
                    [input_path(run, record_id), bundle.revision.path],
                    audit_scratch(manifest, record_id, arm, iteration),
                ),
            )
            if state is not None:
                bundle.states["audit-revision"] = state
            audit_ok = audit_ok and metadata_ok and state_ok
    elif bundle.revision is not None:
        audit_prompt = expected_audit_prompt(
            run, manifest, record_id, arm, iteration, bundle.revision
        )
        state = load_artifact(
            state_path(run, record_id, "audit-revision", arm, iteration), diagnostics
        )
        if state is not None:
            validate_state(
                state, record_id, "audit-revision", arm, iteration,
                manifest, seal, diagnostics, model_call=True,
                prompt_sha256=sha_text(audit_prompt),
                expected_fields={
                    "parent_sha256": bundle.revision.sha256,
                    "prompt_size_bytes": len(audit_prompt.encode("utf-8")),
                    "audit_normalization_policy": "CLERICAL_BINDINGS_ONLY_V1",
                } | model_isolation_state_fields(
                    seal, run / manifest["schemas"]["audit_solver"]["path"],
                    [input_path(run, record_id), bundle.revision.path],
                    audit_scratch(manifest, record_id, arm, iteration),
                ),
            )
    bundle.valid = bool(receipt_ok and prompt_ok and revision_ok and audit_ok)
    return bundle


def _arm_iteration_set(inventory: Inventory, record_id: str,
                       arm: str) -> set[int]:
    result: set[int] = set()
    for mapping in (inventory.revisions, inventory.revision_audits,
                    inventory.revision_metadata, inventory.prompts,
                    inventory.recoveries):
        result.update(iteration for rid, candidate_arm, iteration in mapping
                      if rid == record_id and candidate_arm == arm)
    result.update(iteration for rid, candidate_arm, iteration, _stage
                  in inventory.states
                  if rid == record_id and candidate_arm == arm
                  and iteration is not None)
    result.update(iteration for rid, candidate_arm, iteration, _stage
                  in inventory.locks
                  if rid == record_id and candidate_arm == arm
                  and iteration is not None)
    result.update(iteration for rid, candidate_arm, iteration, _index
                  in inventory.checkers
                  if rid == record_id and candidate_arm == arm)
    if arm == "bugbank":
        result.update(iteration for rid, iteration in inventory.receipts
                      if rid == record_id)
    return result


def validate_arm_chain(
        run: Path, record_id: str, arm: str, baseline: BaselineBundle,
        manifest: Mapping[str, Any], seal: Mapping[str, Any],
        schemas: Mapping[str, Mapping[str, Any]], database: BugBankView,
        inventory: Inventory, diagnostics: Diagnostics,
        bugbank_token_target: int | None = None
        ) -> tuple[dict[int, IterationBundle], dict[str, Any] | None]:
    present = _arm_iteration_set(inventory, record_id, arm)
    maximum = manifest["execution"]["max_iterations"]
    bundles: dict[int, IterationBundle] = {}
    if not present:
        diagnostics.missing(
            "INITIAL_REVISION_MISSING",
            revision_path(run, record_id, arm, 1),
            "paired arm has not begun iteration 1",
        )
        return bundles, None
    highest = max(present)
    missing_prefix = [iteration for iteration in range(1, highest + 1)
                      if iteration not in present]
    if missing_prefix:
        diagnostics.bad(
            "ITERATION_GAP", run / "iterations" / record_id / arm,
            f"runtime artifacts skip iterations {missing_prefix!r}",
        )

    chain_ok = baseline.valid
    parent = baseline.draft
    parent_audit = baseline.audit
    endpoint: dict[str, Any] | None = None
    for iteration in range(1, highest + 1):
        if iteration not in present:
            chain_ok = False
            continue
        if endpoint is not None:
            # The detailed global boundary scan names every offending file.
            continue
        sibling_receipt = None
        if arm == "plain":
            sibling_path = inventory.receipts.get((record_id, iteration))
            if sibling_path is not None:
                sibling_receipt = load_artifact(sibling_path, diagnostics)
        bundle = validate_iteration_bundle(
            run, record_id, arm, iteration,
            parent if chain_ok else None,
            parent_audit if chain_ok else None,
            manifest, seal, schemas, database, sibling_receipt, diagnostics,
        )
        bundle.valid = bundle.valid and chain_ok
        bundles[iteration] = bundle
        if not bundle.valid:
            chain_ok = False
            continue
        parent = bundle.revision
        parent_audit = bundle.audit
        endpoint = derive_endpoint(
            run, inventory, bundles, record_id, arm, bugbank_token_target,
            diagnostics,
        )

    if endpoint is None:
        if highest >= maximum:
            diagnostics.missing(
                "OPERATIONAL_ITERATION_LIMIT_REACHED",
                revision_path(run, record_id, arm, maximum),
                "the operational ceiling is not a terminal condition; review and extend",
            )
        elif arm == "plain" and bugbank_token_target is None:
            latest = bundles.get(highest)
            stable = bool(
                latest is not None and latest.valid and latest.parent is not None
                and latest.revision is not None and latest.audit is not None
                and proof_state(latest.parent.value) == proof_state(latest.revision.value)
                and audit_is_settled(latest.audit)
                and not audit_verifies_full(latest.revision, latest.audit)
            )
            diagnostics.missing(
                "WAITING_FOR_BUGBANK_TOKEN_TARGET" if stable
                else "NEXT_REVISION_REQUIRED",
                revision_path(run, record_id, arm, highest + 1),
                ("stable plain proof must wait for the BugBank endpoint token total"
                 if stable else "another complete revision/audit cycle is required"),
            )
        else:
            diagnostics.missing(
                "NEXT_REVISION_REQUIRED",
                revision_path(run, record_id, arm, highest + 1),
                "another complete revision/audit cycle is required",
            )
    return bundles, endpoint


def reject_post_endpoint_artifacts(inventory: Inventory, record_id: str,
                                   arm: str, endpoint_iteration: int,
                                   diagnostics: Diagnostics) -> None:
    paths: set[Path] = set()
    for mapping in (inventory.revisions, inventory.revision_audits,
                    inventory.revision_metadata, inventory.prompts,
                    inventory.recoveries):
        paths.update(path for (rid, candidate_arm, iteration), path in mapping.items()
                     if rid == record_id and candidate_arm == arm
                     and iteration > endpoint_iteration)
    paths.update(path for (rid, candidate_arm, iteration, _stage), path
                 in inventory.states.items()
                 if rid == record_id and candidate_arm == arm
                 and iteration is not None and iteration > endpoint_iteration)
    paths.update(path for (rid, candidate_arm, iteration, _stage), path
                 in inventory.locks.items()
                 if rid == record_id and candidate_arm == arm
                 and iteration is not None and iteration > endpoint_iteration)
    paths.update(path for (rid, candidate_arm, iteration, _index), path
                 in inventory.checkers.items()
                 if rid == record_id and candidate_arm == arm
                 and iteration > endpoint_iteration)
    if arm == "bugbank":
        paths.update(path for (rid, iteration), path in inventory.receipts.items()
                     if rid == record_id and iteration > endpoint_iteration)
    for path in sorted(paths):
        diagnostics.bad(
            "POST_ENDPOINT_ARTIFACT", path,
            f"{arm} first became terminal at iteration {endpoint_iteration}",
        )


def expected_terminal_value(run: Path, record_id: str,
                            maximum: int, retrieval_k: int,
                            baseline: BaselineBundle,
                            endpoints: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    plain_tokens = endpoints["plain"]["model_tokens_used"]
    bugbank_tokens = endpoints["bugbank"]["model_tokens_used"]
    plain_solved = endpoints["plain"]["status"] == "VERIFIED_FULL"
    value: dict[str, Any] = {
        "schema": TERMINAL_SCHEMA,
        "run_id": run.name,
        "record_id": record_id,
        "stage": "PAIR_TERMINAL",
        "status": "COMPLETE",
        "pair_status": "COMPLETE",
        "max_iterations": maximum,
        "retrieval_k": retrieval_k,
        "treatment_contrast_valid": True,
        "proof_endpoints_complete": True,
        "token_comparison_auditable": True,
        "solved_arms": [arm for arm in ("bugbank", "plain")
                        if endpoints[arm]["status"] == "VERIFIED_FULL"],
        "bugbank_model_tokens_used": bugbank_tokens,
        "plain_model_tokens_used": plain_tokens,
        "plain_minus_bugbank_tokens": subtract_token_counts(
            plain_tokens, bugbank_tokens
        ),
        "plain_solved_with_fewer_tokens": (
            plain_tokens < bugbank_tokens if plain_solved else None
        ),
        "baseline": {
            "draft": binding(baseline.draft),
            "independent_audit": binding(baseline.audit),
        },
        "arms": {
            "plain": endpoints["plain"],
            "bugbank": endpoints["bugbank"],
        },
    }
    value["terminal_payload_sha256"] = sha_bytes(canonical_bytes(value))
    return value


def expected_incomplete_terminal_arm(arm: str) -> dict[str, Any]:
    """Return the complete deterministic non-evidence arm placeholder."""
    return {
        "arm": arm,
        "status": "INCOMPLETE",
        "terminal": False,
        "terminal_reason": "INCOMPLETE",
        "iteration": None,
        "reason": "VALID_ENDPOINT_NOT_AVAILABLE",
        "next_stage": "CONTINUE_PROTOCOL",
        "revision_sha256": None,
        "audit_sha256": None,
        "claimed_resolution": None,
        "target_verdict": None,
        "audit_overall": None,
    }


def validate_terminal_artifact(
        artifact: Artifact | None, run: Path, record_id: str,
        manifest: Mapping[str, Any], baseline: BaselineBundle,
        endpoints: Mapping[str, dict[str, Any] | None],
        diagnostics: Diagnostics) -> bool:
    if artifact is None:
        diagnostics.missing("PAIR_TERMINAL_MISSING", terminal_path(run, record_id),
                            "pair terminal snapshot is absent")
        return False
    value = artifact.value
    terminal_keys = {
        "schema", "run_id", "record_id", "stage", "status", "pair_status",
        "max_iterations", "retrieval_k", "treatment_contrast_valid",
        "proof_endpoints_complete", "token_comparison_auditable",
        "solved_arms", "bugbank_model_tokens_used", "plain_model_tokens_used",
        "plain_minus_bugbank_tokens", "plain_solved_with_fewer_tokens",
        "baseline", "arms", "terminal_payload_sha256",
    }
    if set(value) != terminal_keys:
        diagnostics.bad("TERMINAL_ENVELOPE", artifact.path,
                        "terminal has missing or unrecognized top-level fields")
        return False
    unsigned = copy.deepcopy(value)
    recorded_hash = unsigned.pop("terminal_payload_sha256", None)
    if recorded_hash != sha_bytes(canonical_bytes(unsigned)):
        diagnostics.bad("TERMINAL_HASH", artifact.path,
                        "terminal payload hash is absent or incorrect")
        return False
    complete = all(endpoints.get(arm) is not None for arm in ARMS)
    auditable = complete and all(
        is_token_count(endpoints[arm].get("model_tokens_used")) for arm in ARMS
    )
    if complete and auditable and baseline.valid:
        expected = expected_terminal_value(
            run, record_id, manifest["execution"]["max_iterations"],
            manifest["bugbank"]["retrieval_k"], baseline,
            {arm: endpoints[arm] for arm in ARMS},
        )
        if value != expected:
            diagnostics.bad("TERMINAL_NOT_EXACT", artifact.path,
                            "terminal differs from independently reconstructed value")
            return False
        return True
    identity = {
        "schema": TERMINAL_SCHEMA,
        "run_id": manifest["run_id"],
        "record_id": record_id,
        "stage": "PAIR_TERMINAL",
        "status": "INCOMPLETE",
        "pair_status": "INCOMPLETE",
        "max_iterations": manifest["execution"]["max_iterations"],
        "retrieval_k": manifest["bugbank"]["retrieval_k"],
        "treatment_contrast_valid": False,
    }
    if any(value.get(key) != wanted for key, wanted in identity.items()):
        diagnostics.bad("INCOMPLETE_TERMINAL_INVALID", artifact.path,
                        "incomplete terminal identity/status is inconsistent")
        return False
    arm_values = value.get("arms")
    if type(arm_values) is not dict or set(arm_values) != set(ARMS):
        diagnostics.bad("INCOMPLETE_TERMINAL_ARMS", artifact.path,
                        "incomplete terminal must contain exactly both arms")
        return False
    arm_ok = True
    for arm in ARMS:
        row = arm_values.get(arm)
        endpoint = endpoints.get(arm)
        if endpoint is not None:
            if row != endpoint:
                arm_ok = False
            continue
        if row != expected_incomplete_terminal_arm(arm):
            arm_ok = False
    endpoint_tokens = {
        arm: (endpoints[arm].get("model_tokens_used")
              if endpoints.get(arm) is not None else None)
        for arm in ARMS
    }
    expected_cross = {
        "proof_endpoints_complete": False,
        "token_comparison_auditable": False,
        "solved_arms": [arm for arm in ("bugbank", "plain")
                        if endpoints.get(arm) is not None
                        and endpoints[arm].get("status") == "VERIFIED_FULL"],
        "bugbank_model_tokens_used": endpoint_tokens["bugbank"],
        "plain_model_tokens_used": endpoint_tokens["plain"],
        "plain_minus_bugbank_tokens": None,
        "plain_solved_with_fewer_tokens": None,
        "baseline": ({"draft": binding(baseline.draft),
                      "independent_audit": binding(baseline.audit)}
                     if baseline.valid else None),
    }
    if (not arm_ok or any(value.get(key) != wanted
                          for key, wanted in expected_cross.items())):
        diagnostics.bad("INCOMPLETE_TERMINAL_NOT_EXACT", artifact.path,
                        "incomplete terminal fields do not match independently checked progress")
        return False
    diagnostics.missing("PAIR_TERMINAL_INCOMPLETE", artifact.path,
                        "both valid auditable arm endpoints are not yet available")
    return False


def validate_recovery(artifact: Artifact, bundle: IterationBundle,
                      state: Artifact, run: Path,
                      diagnostics: Diagnostics) -> tuple[bool, set[Path]]:
    value = artifact.value
    valid = payload_valid(value, "recovery_payload_sha256")
    referenced: set[Path] = set()
    if not valid:
        diagnostics.bad("RECOVERY_HASH", artifact.path,
                        "recovery payload hash is incorrect")
    expected_keys = {
        "schema", "run_id", "incident", "record_id", "arm", "iteration",
        "dead_runner_pid", "status", "recovered_at", "lineage",
        "original_temporary_sha256", "original_temporary_size_bytes",
        "archived_temporary", "archived_lock", "archived_state", "archived_log",
        "recovered_cost", "final", "safety_checks", "recovery_payload_sha256",
    }
    if set(value) != expected_keys:
        diagnostics.bad("RECOVERY_ENVELOPE", artifact.path,
                        "recovery has missing or unexpected fields")
        valid = False
    identities = {
        "schema": "paired_open_problem_revision_recovery_v1",
        "run_id": run.name,
        "record_id": bundle.record_id,
        "arm": bundle.arm,
        "iteration": bundle.iteration,
        "status": "RECOVERED_COMPLETE",
        "incident": "orphaned_revision_model_call",
    }
    if any(value.get(key) != wanted for key, wanted in identities.items()):
        diagnostics.bad("RECOVERY_IDENTITY", artifact.path,
                        "recovery is not an accepted completed revision recovery")
        valid = False
    if (not is_int(value.get("dead_runner_pid"))
            or value["dead_runner_pid"] < 1
            or type(value.get("recovered_at")) is not str
            or not value["recovered_at"]):
        diagnostics.bad("RECOVERY_PROCESS", artifact.path,
                        "recovery process/timestamp identity is malformed")
        valid = False
    lineage = value.get("lineage")
    expected_lineage = {
        "parent": binding(bundle.parent),
        "audit": binding(bundle.parent_audit),
        "prompt_metadata": binding(bundle.prompt),
        "receipt": binding(bundle.receipt) if bundle.arm == "bugbank" else None,
    }
    if lineage != expected_lineage or value.get("final") != binding(bundle.revision):
        diagnostics.bad("RECOVERY_LINEAGE", artifact.path,
                        "recovery lineage/final binding is incorrect")
        valid = False
    recovered_cost = value.get("recovered_cost")
    if (type(recovered_cost) is not dict
            or set(recovered_cost) != {"tokens_used", "model", "reasoning_effort"}
            or recovered_cost.get("tokens_used") != state.value.get("tokens_used")
            or recovered_cost.get("model") != state.value.get("model")
            or recovered_cost.get("reasoning_effort") !=
            state.value.get("reasoning_effort")):
        diagnostics.bad("RECOVERY_COST", artifact.path,
                        "recovered model cost differs from completion state")
        valid = False
    safety = value.get("safety_checks")
    expected_safety = {
        "runner_pid_dead": True,
        "no_process_references_exact_scratch": True,
        "valid_final_never_overwritten": True,
        "original_temporary_archived_before_normalization": True,
    }
    if safety != expected_safety:
        diagnostics.bad("RECOVERY_SAFETY", artifact.path,
                        "recovery safety checks are not all true")
        valid = False
    for key in ("archived_temporary", "archived_lock", "archived_state",
                "archived_log"):
        row = value.get(key)
        if row is None:
            continue
        if type(row) is not dict:
            diagnostics.bad("RECOVERY_ARCHIVE_BINDING", artifact.path,
                            f"{key} is malformed")
            valid = False
            continue
        path = recorded_path(row.get("path"), run)
        if path is None or not path.is_file() or path.is_symlink():
            diagnostics.bad("RECOVERY_ARCHIVE_BINDING", artifact.path,
                            f"{key} target is unavailable")
            valid = False
            continue
        referenced.add(path)
        raw = path.read_bytes()
        if row.get("sha256") != sha_bytes(raw) or row.get("size_bytes") != len(raw):
            diagnostics.bad("RECOVERY_ARCHIVE_BINDING", artifact.path,
                            f"{key} byte binding is incorrect")
            valid = False
    archived_temporary = value.get("archived_temporary")
    if (type(archived_temporary) is not dict
            or value.get("original_temporary_sha256") != archived_temporary.get("sha256")
            or value.get("original_temporary_size_bytes") !=
            archived_temporary.get("size_bytes")):
        diagnostics.bad("RECOVERY_ORIGINAL_BINDING", artifact.path,
                        "original orphan bytes do not match the archived temporary")
        valid = False
    if (state.value.get("recovery_path") != repo_path(artifact.path)
            or state.value.get("recovery_sha256") != artifact.sha256):
        diagnostics.bad("RECOVERY_STATE_BINDING", state.path,
                        "completion state does not bind its recovery record")
        valid = False
    return valid, referenced


def expected_log_path(run: Path,
                      key: tuple[str, str | None, int | None, str]) -> Path:
    record_id, arm, iteration, stage = key
    pieces = [record_id]
    if arm is not None:
        pieces.append(arm)
    if iteration is not None:
        pieces.append(f"iter_{iteration}")
    return run / "logs" / stage / ("__".join(pieces) + ".log")


def validate_log(path: Path, state: Artifact, diagnostics: Diagnostics) -> bool:
    if not path.is_file() or path.is_symlink():
        diagnostics.missing("CALL_LOG_MISSING", path,
                            "completed state lacks its append-only call log")
        return False
    try:
        raw = path.read_bytes()
        start_offset = state.value.get("execution_log_start_offset")
        expected_segment = execution_log_segment(path, start_offset)
        expected_prefix_sha256 = execution_log_prefix_sha(path, start_offset)
    except (OSError, ValueError) as error:
        diagnostics.bad("CALL_LOG_UNREADABLE", path, str(error))
        return False
    if state.value.get("execution_log_prefix_sha256") != expected_prefix_sha256:
        diagnostics.bad(
            "CALL_LOG_PREFIX_BINDING", path,
            "state does not bind the exact log bytes that preceded this call",
        )
        return False
    if state.value.get("execution_log_segment") != expected_segment:
        diagnostics.bad(
            "CALL_LOG_SEGMENT_BINDING", path,
            "state does not bind the exact canonical bytes appended by this call",
        )
        return False
    if state.value.get("stage") == "receipt":
        return True
    text = raw[start_offset:].decode("utf-8", errors="replace")
    token_matches = re.findall(
        r"tokens used\s*\r?\n\s*"
        r"([0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)\s*(?:\r?\n|$)", text,
        flags=re.IGNORECASE,
    )
    model_matches = re.findall(r"^model:\s*(\S.*?)\s*$", text,
                               flags=re.IGNORECASE | re.MULTILINE)
    effort_matches = re.findall(r"^reasoning effort:\s*(\S.*?)\s*$", text,
                                flags=re.IGNORECASE | re.MULTILINE)
    observed_tokens = None
    if token_matches:
        token_text = token_matches[-1]
        if re.fullmatch(r"[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+", token_text) is None:
            diagnostics.bad("CALL_LOG_TELEMETRY", path,
                            "token telemetry has invalid digit grouping")
            return False
        observed_tokens = int(token_text.replace(",", ""))
        if not is_token_count(observed_tokens):
            diagnostics.bad("CALL_LOG_TELEMETRY", path,
                            "token telemetry exceeds exact safe JSON-integer accounting")
            return False
    observed_model = model_matches[-1].strip() if model_matches else None
    observed_effort = effort_matches[-1].strip() if effort_matches else None
    valid = bool(
        observed_tokens == state.value.get("tokens_used")
        and observed_model == state.value.get("model")
        and observed_effort == state.value.get("reasoning_effort")
    )
    if not valid:
        diagnostics.bad("CALL_LOG_TELEMETRY", path,
                        "telemetry in this call's bound log segment differs from its state")
    return valid


def validate_summary(path: Path, run_id: str,
                     diagnostics: Diagnostics) -> bool:
    artifact = load_artifact(path, diagnostics)
    if artifact is None:
        return False
    value = artifact.value
    try:
        stage = path.parent.name
        results = value["results"]
        expected_keys = {
            "run", "stage", "iteration", "dry_run", "started_at",
            "ended_at", "selected", "complete", "failed", "tokens_used",
            "duration_seconds_sum", "results",
        }
        successes = {
            "COMPLETE", "SKIP_VALID", "PLANNED",
            "RECOVERED_COMPLETE", "RECOVERED_PUBLICATION",
            "READY_FOR_RELAUNCH", "FINAL_ALREADY_VALID",
            "SKIP_OUT_OF_SCOPE", "ALREADY_TERMINAL",
        }
        computed_complete = sum(
            type(row) is dict and row.get("status") in successes for row in results
        )
        if any(type(row) is not dict for row in results):
            raise ValueError("summary results must all be objects")
        computed_tokens = add_token_counts(*(
            row.get("tokens_used") if row.get("tokens_used") is not None else 0
            for row in results
        ))
        computed_duration = add_durations(*(
            row.get("duration_seconds")
            if row.get("duration_seconds") is not None else 0
            for row in results
        ))
        valid = bool(
            stage in WRITABLE_SUMMARY_STAGES
            and set(value) == expected_keys
            and value.get("run") == run_id and value.get("stage") == stage
            and type(value.get("dry_run")) is bool
            and type(value.get("started_at")) is str
            and type(value.get("ended_at")) is str
            and (value.get("iteration") is None
                 or (is_int(value.get("iteration"))
                     and value["iteration"] >= 1))
            and type(results) is list
            and value.get("selected") == len(results)
            and value.get("complete") == computed_complete
            and value.get("failed") == len(results) - computed_complete
            and value.get("tokens_used") == computed_tokens
            and value.get("duration_seconds_sum") == computed_duration
        )
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        diagnostics.bad("SUMMARY_CONTRACT", path,
                        "summary counters or run/stage identity are inconsistent")
    return valid


def validate_derived_report(path: Path, manifest: Mapping[str, Any],
                            diagnostics: Diagnostics) -> bool:
    """Validate the one permitted non-authoritative in-run snapshot.

    The snapshot is never used to reconstruct scientific evidence.  Its only
    authority is its self-hash and provenance; it may legitimately describe
    an earlier checkpoint of a still-mutating run.
    """
    artifact = load_artifact(path, diagnostics)
    if artifact is None:
        return False
    value = artifact.value
    full_keys = {
        "schema", "run_id", "run_path", "generated_at", "validator",
        "status", "protocol_id", "counts", "closed_world", "records",
        "diagnostics", "report_payload_sha256",
    }
    early_keys = full_keys - {"protocol_id"}
    valid = bool(
        set(value) in (full_keys, early_keys)
        and value.get("schema") == "paired_open_problem_exploratory_validation_report_v1"
        and value.get("run_id") == manifest["run_id"]
        and value.get("run_path") == str(path.parent.resolve())
        and type(value.get("generated_at")) is str
        and value.get("status") in {"VALID_COMPLETE", "INCOMPLETE", "INVALID"}
        and type(value.get("counts")) is dict
        and type(value.get("closed_world")) is dict
        and type(value.get("records")) is dict
        and payload_valid(value, "report_payload_sha256")
    )
    if "protocol_id" in value and value.get("protocol_id") != manifest["protocol"]["id"]:
        valid = False
    expected_validator = {"path": str(SCRIPT), "sha256": sha_file(SCRIPT)}
    if value.get("validator") != expected_validator:
        valid = False
    diagnostic = value.get("diagnostics")
    diagnostic_keys = {
        "invalid_count", "incomplete_count", "warning_count",
        "invalid", "incomplete", "warnings",
    }
    if type(diagnostic) is not dict or set(diagnostic) != diagnostic_keys:
        valid = False
    else:
        for count_key, rows_key in (
                ("invalid_count", "invalid"),
                ("incomplete_count", "incomplete"),
                ("warning_count", "warnings")):
            rows = diagnostic.get(rows_key)
            if type(rows) is not list or diagnostic.get(count_key) != len(rows):
                valid = False
        if diagnostic.get("invalid_count", 0) > 0 and value.get("status") != "INVALID":
            valid = False
        if value.get("status") == "VALID_COMPLETE" and (
                diagnostic.get("invalid_count") != 0
                or diagnostic.get("incomplete_count") != 0):
            valid = False
    if not valid:
        diagnostics.bad(
            "DERIVED_REPORT_INVALID", path,
            "canonical validation snapshot has an invalid envelope, provenance, or self-hash",
        )
    return valid


def _walk_run_tree(run: Path, diagnostics: Diagnostics
                   ) -> tuple[set[Path], set[Path]]:
    """Classify every directory entry without following links."""
    files: set[Path] = set()
    directories: set[Path] = {run.resolve()}
    pending = [run.resolve()]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as error:
            diagnostics.bad("RUN_TREE_UNREADABLE", directory, str(error))
            continue
        for entry in entries:
            path = Path(entry.path)
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as error:
                diagnostics.bad("RUN_TREE_UNREADABLE", path, str(error))
                continue
            if stat.S_ISLNK(info.st_mode):
                diagnostics.bad("RUN_TREE_SYMLINK", path,
                                "the sealed run tree may not contain symlinks")
            elif stat.S_ISDIR(info.st_mode):
                resolved = path.resolve()
                directories.add(resolved)
                pending.append(resolved)
            elif stat.S_ISREG(info.st_mode):
                files.add(path.resolve())
            else:
                diagnostics.bad(
                    "RUN_TREE_SPECIAL_ENTRY", path,
                    "the sealed run tree may contain only directories and regular files",
                )
    return files, directories


def runner_writable_directories(
        run: Path, manifest: Mapping[str, Any],
        observed_directories: Iterable[Path] = ()) -> set[Path]:
    """Exact directory envelope that the sealed runner can materialize.

    Dynamic output/checker parents are included even while empty because a
    SIGKILL may land after ``mkdir`` and before the atomic file publication.
    Such a directory carries no evidence, but must remain a retryable prefix.
    """
    allowed = {(run / relative).resolve() for relative in FIXED_RUNTIME_DIRECTORIES}
    roster = manifest.get("problem_ids")
    maximum = manifest.get("execution", {}).get("max_iterations")
    if type(roster) is list and all(type(item) is str and item for item in roster):
        for record_id in roster:
            allowed.add((run / "iterations" / record_id).resolve())
            allowed.add((run / "audits/iterations" / record_id).resolve())
            allowed.add((run / "audits/metadata/iterations" / record_id).resolve())
            allowed.add((run / "checkers/audits/baseline" / record_id).resolve())
            allowed.add((run / "checkers/audits/iterations" / record_id).resolve())
            for arm in ARMS:
                allowed.add((run / "iterations" / record_id / arm).resolve())
                allowed.add((run / "audits/iterations" / record_id / arm).resolve())
                allowed.add(
                    (run / "audits/metadata/iterations" / record_id / arm).resolve()
                )
                checker_arm = run / "checkers/audits/iterations" / record_id / arm
                allowed.add(checker_arm.resolve())
                if is_int(maximum) and maximum >= 1:
                    allowed.update(
                        (checker_arm / f"iter_{iteration}").resolve()
                        for iteration in range(1, maximum + 1)
                    )

    # Manual revision recovery names its forensic root from an increasing,
    # unique list of positive runner PIDs. Its four category names are fixed.
    for path in observed_directories:
        try:
            relative = path.resolve().relative_to((run / "forensics").resolve())
        except ValueError:
            continue
        if not relative.parts:
            continue
        root_name = relative.parts[0]
        match = re.fullmatch(
            r"revision_recovery_pids_([1-9][0-9]*(?:_[1-9][0-9]*)*)",
            root_name,
        )
        if match is None:
            continue
        pids = [int(item) for item in match.group(1).split("_")]
        if pids != sorted(set(pids)):
            continue
        forensic_root = (run / "forensics" / root_name).resolve()
        allowed.add(forensic_root)
        allowed.update(
            (forensic_root / category).resolve()
            for category in ("locks", "states", "logs", "revision_tmp")
        )
    return allowed


def global_closed_world(
        run: Path, manifest: Mapping[str, Any], seal_present: bool,
        inventory: Inventory, referenced_forensics: set[Path],
        diagnostics: Diagnostics,
        extra_allowed: Iterable[Path] = ()) -> dict[str, Any]:
    expected: set[Path] = {(run / "RUN_MANIFEST.json").resolve()}
    if seal_present:
        expected.add((run / "RUNTIME_SEAL.json").resolve())
    try:
        for _label, row in seal_checker.manifest_bindings(dict(manifest)):
            expected.add((run / row["path"]).resolve())
    except (KeyError, TypeError):
        pass
    for mapping in (
            inventory.baselines, inventory.baseline_audits,
            inventory.baseline_metadata, inventory.revisions,
            inventory.revision_audits, inventory.revision_metadata,
            inventory.receipts, inventory.prompts, inventory.terminals,
            inventory.states, inventory.checkers, inventory.recoveries,
            inventory.locks):
        expected.update(path.resolve() for path in mapping.values())
    expected.update(path.resolve() for path in referenced_forensics)
    # Arbitrary in-run exceptions are forbidden.  `extra_allowed` is retained
    # only for backwards-compatible callers that name paths outside this run.
    for raw in extra_allowed:
        candidate = Path(raw).resolve()
        if run.resolve() not in candidate.parents and candidate != run.resolve():
            continue
        if candidate != (run / "VALIDATION_REPORT.json").resolve():
            diagnostics.bad("UNSUPPORTED_CLOSED_WORLD_EXCEPTION", candidate,
                            "only the canonical derived validation report is permitted")

    report_path = (run / "VALIDATION_REPORT.json").resolve()
    if os.path.lexists(report_path):
        expected.add(report_path)
        validate_derived_report(report_path, manifest, diagnostics)

    validated_logs = 0
    for key, state_path_value in inventory.states.items():
        log = expected_log_path(run, key).resolve()
        state = load_artifact(state_path_value, diagnostics)
        if state is None:
            continue
        # Every durable call state binds one canonical append-only log.  A
        # missing log for COMPLETE evidence is a hard absence; logs belonging
        # to failed/in-flight states remain in the closed-world inventory but
        # cannot contribute endpoint telemetry.
        expected.add(log)
        if state.value.get("status") in {"COMPLETE", "RECOVERED_COMPLETE"}:
            validated_logs += int(validate_log(log, state, diagnostics))

    summary_root = run / "summaries"
    validated_summaries = 0
    for path in _regular_files(summary_root, diagnostics):
        relative = path.relative_to(summary_root.resolve())
        canonical = bool(
            len(relative.parts) == 2 and path.suffix == ".json"
            and relative.parts[0] in WRITABLE_SUMMARY_STAGES
            and re.fullmatch(
                r".+__pid_[0-9]+__[0-9]+\.json", relative.name
            ) is not None
        )
        if canonical and validate_summary(path, manifest["run_id"], diagnostics):
            expected.add(path)
            validated_summaries += 1
        else:
            diagnostics.bad("NONCANONICAL_SUMMARY", path,
                            "summary path or payload is not canonical")

    observed, observed_directories = _walk_run_tree(run, diagnostics)
    for path in sorted(observed - expected):
        diagnostics.bad("UNEXPECTED_RUN_FILE", path,
                        "file is not manifest-bound or independently validated runtime evidence")
    for path in sorted(expected - observed):
        # Missing scientific outputs are diagnosed by their stage.  Static
        # bindings and explicitly allowed report paths are the only useful
        # additional signal here.
        if path == (run / "RUNTIME_SEAL.json").resolve() and not seal_present:
            continue
        if not path.exists() and path.parent not in (
                (run / "baselines"), (run / "pair_terminals")):
            diagnostics.missing("EXPECTED_RUN_FILE_MISSING", path,
                                "bound or referenced run file is absent")

    required_directories: set[Path] = {run.resolve()}
    for path in expected:
        cursor = path.parent.resolve()
        while cursor != run.resolve():
            required_directories.add(cursor)
            if run.resolve() not in cursor.parents:
                break
            cursor = cursor.parent
    # Bootstrap parents are required; other exact runner-writable parents are
    # allowed to be empty only for interruption recovery.
    bootstrap_directories = {
        "baselines", "audits", "retrievals", "iterations", "prompts",
        "pair_terminals", "states", "locks", "logs", "summaries",
        "checkers", "ops",
    }
    required_directories.update(
        (run / relative).resolve() for relative in bootstrap_directories
    )
    allowed_directories = set(required_directories)
    allowed_directories.update(
        runner_writable_directories(run, manifest, observed_directories)
    )
    for path in sorted(observed_directories - allowed_directories):
        diagnostics.bad("UNEXPECTED_RUN_DIRECTORY", path,
                        "directory is not part of the exact sealed run-tree envelope")
    for path in sorted(required_directories - observed_directories):
        diagnostics.bad("EXPECTED_RUN_DIRECTORY_MISSING", path,
                        "required sealed run-tree directory is absent")
    return {
        "observed_files": len(observed),
        "expected_files": len(expected),
        "observed_directories": len(observed_directories),
        "allowed_directories": len(allowed_directories),
        "validated_logs": validated_logs,
        "validated_summaries": validated_summaries,
    }


def load_schemas(run: Path, manifest: Mapping[str, Any],
                 diagnostics: Diagnostics) -> dict[str, Mapping[str, Any]]:
    schemas: dict[str, Mapping[str, Any]] = {}
    for name in (
            "baseline", "audit", "revision", "audit_solver",
            "revision_plain_solver"):
        row = manifest.get("schemas", {}).get(name)
        if type(row) is not dict:
            diagnostics.bad("SCHEMA_BINDING_MISSING", run,
                            f"manifest lacks {name} schema binding")
            continue
        path = run / str(row.get("path", ""))
        artifact = _required(path, diagnostics, "SCHEMA_MISSING")
        if artifact is None:
            continue
        if (artifact.sha256 != row.get("sha256")
                or artifact.size_bytes != row.get("size_bytes")):
            diagnostics.bad("SCHEMA_BINDING_MISMATCH", path,
                            f"{name} schema bytes differ from manifest")
            continue
        schemas[name] = artifact.value
    return schemas


def _metadata_checker_paths(metadata: Artifact | None, run: Path) -> set[Path]:
    result: set[Path] = set()
    if metadata is None:
        return result
    for row in metadata.value.get("checker_artifacts", []):
        if type(row) is not dict or type(row.get("durable")) is not dict:
            continue
        path = recorded_path(row["durable"].get("path"), run)
        if path is not None:
            result.add(path)
    return result


def _runtime_json_artifacts(inventory: Inventory,
                            diagnostics: Diagnostics) -> list[Artifact]:
    artifacts: list[Artifact] = []
    for mapping in (
            inventory.baselines, inventory.baseline_audits,
            inventory.baseline_metadata, inventory.revisions,
            inventory.revision_audits, inventory.revision_metadata,
            inventory.receipts, inventory.prompts, inventory.terminals,
            inventory.states, inventory.recoveries):
        for path in mapping.values():
            artifact = load_artifact(path, diagnostics)
            if artifact is not None:
                artifacts.append(artifact)
    return artifacts


def _reject_historical_fields(value: Any, path: Path,
                              diagnostics: Diagnostics, at: str = "$") -> None:
    forbidden = ("grandfather", "cutover", "historical_compat", "legacy_receipt")
    if type(value) is dict:
        for key, item in value.items():
            lowered = key.lower()
            if any(token in lowered for token in forbidden):
                diagnostics.bad("HISTORICAL_EXCEPTION_FIELD", path,
                                f"fresh run contains forbidden field {at}.{key}")
            _reject_historical_fields(item, path, diagnostics, f"{at}.{key}")
    elif type(value) is list:
        for index, item in enumerate(value):
            _reject_historical_fields(item, path, diagnostics, f"{at}[{index}]")


def _report_without_configuration(run: Path, diagnostics: Diagnostics,
                                  run_id: str | None = None) -> dict[str, Any]:
    return {
        "schema": "paired_open_problem_exploratory_validation_report_v1",
        "run_id": run_id,
        "run_path": str(run),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "validator": {"path": str(SCRIPT), "sha256": sha_file(SCRIPT)},
        "status": "INVALID" if diagnostics.invalid else "INCOMPLETE",
        "records": {},
        "counts": {},
        "closed_world": {},
        "diagnostics": {
            "invalid_count": len(diagnostics.invalid),
            "incomplete_count": len(diagnostics.incomplete),
            "warning_count": len(diagnostics.warnings),
            "invalid": diagnostics.invalid,
            "incomplete": diagnostics.incomplete,
            "warnings": diagnostics.warnings,
        },
    }


def validate_run(run_root: Path,
                 extra_allowed: Iterable[Path] = ()) -> dict[str, Any]:
    run = run_root.resolve()
    diagnostics = Diagnostics(run)
    try:
        run = seal_checker.safe_run_root(run)
    except (seal_checker.SealError, OSError) as error:
        diagnostics.bad("RUN_ROOT_INVALID", run, str(error))
        return _report_without_configuration(run, diagnostics)
    try:
        manifest, _bound = seal_checker.validate_manifest(run)
    except (seal_checker.SealError, OSError, KeyError, TypeError) as error:
        diagnostics.bad("MANIFEST_INVALID", run / "RUN_MANIFEST.json", str(error))
        return _report_without_configuration(run, diagnostics)
    manifest = copy.deepcopy(manifest)
    manifest["__run_root"] = str(run)
    roster = manifest["problem_ids"]
    exploratory = manifest.get("exploratory_preregistration")
    operations = manifest.get("operations")
    if (run != EXPECTED_RUN.resolve(strict=False)
            or manifest.get("schema") !=
            "paired_open_problem_exploratory_run_manifest_v1"
            or manifest.get("run_id") != EXPECTED_RUN_ID
            or manifest.get("protocol", {}).get("id") !=
            "WHOLE_PROOF_FIRST_SOLUTION_V1"
            or manifest.get("execution", {}).get("model") != "gpt-5.6-sol"
            or manifest.get("execution", {}).get("reasoning_effort") != "max"
            or manifest.get("execution", {}).get("max_iterations") != 50
            or type(roster) is not list
            or len(roster) != EXPLORATORY_COHORT_SIZE
            or manifest.get("problem_count") != EXPLORATORY_COHORT_SIZE
            or type(exploratory) is not dict
            or exploratory.get("study_id") != "EXPLORATORY_UNBIASED_V2"
            or exploratory.get("cohort_size") != EXPLORATORY_COHORT_SIZE
            or exploratory.get("never_pool_with_frozen_58") is not True
            or exploratory.get("frozen_comparison_protocol_observation_count") != 58
            or exploratory.get("frozen_comparison_distinct_target_count") != 36
            or exploratory.get("frozen_comparison_continuation_observation_count") != 22
            or exploratory.get("selected_canonical_keys") != EXPECTED_SELECTED_KEYS
            or type(exploratory.get("artifacts")) is not dict
            or set(exploratory["artifacts"]) != PREREGISTRATION_FILENAMES
            or type(exploratory.get("candidate_pool_source_snapshots")) is not dict
            or set(exploratory["candidate_pool_source_snapshots"]) != {
                "cycles_colouring_33", "dagstuhl_25041",
                "problem_4_1_resolution_2026", "randomstrasse_2025"}
            or type(operations) is not dict
            or operations.get("namespaces_disjoint_from_frozen_58") is not True
            or Path(operations.get("ops_root", "")).resolve(strict=False) !=
            EXPECTED_OPS.resolve(strict=False)
            or Path(operations.get("scratch_root", "")).resolve(strict=False) !=
            EXPECTED_SCRATCH.resolve(strict=False)):
        diagnostics.bad(
            "EXPLORATORY_PREREGISTRATION_INVALID", run / "RUN_MANIFEST.json",
            "manifest is not the exact separate preregistered n=6 cohort",
        )
        return _report_without_configuration(run, diagnostics, manifest.get("run_id"))
    maximum = manifest["execution"]["max_iterations"]
    inventory = discover_inventory(run, roster, maximum, diagnostics)
    seal_path = run / "RUNTIME_SEAL.json"
    if not seal_path.is_file():
        diagnostics.missing("RUNTIME_SEAL_MISSING", seal_path,
                            "runtime execution is not authorized yet")
        runtime_count = sum(len(mapping) for mapping in (
            inventory.baselines, inventory.baseline_audits,
            inventory.baseline_metadata, inventory.revisions,
            inventory.revision_audits, inventory.revision_metadata,
            inventory.receipts, inventory.prompts, inventory.terminals,
            inventory.states, inventory.checkers, inventory.recoveries,
            inventory.locks,
        ))
        if runtime_count:
            diagnostics.bad("UNSEALED_RUNTIME_EVIDENCE", run,
                            "runtime artifacts exist before a valid runtime seal")
        closed = global_closed_world(
            run, manifest, False, Inventory(), set(), diagnostics, extra_allowed
        )
        report = _report_without_configuration(run, diagnostics, manifest["run_id"])
        report["closed_world"] = closed
        report["counts"] = {"problems": len(roster), "runtime_artifacts": runtime_count}
        return report
    try:
        seal = seal_checker.check_seal(run)
    except (seal_checker.SealError, OSError, KeyError, TypeError) as error:
        diagnostics.bad("RUNTIME_SEAL_INVALID", seal_path, str(error))
        return _report_without_configuration(run, diagnostics, manifest["run_id"])

    schemas = load_schemas(run, manifest, diagnostics)
    expected_schema_names = {
        "baseline", "audit", "revision", "audit_solver",
        "revision_plain_solver",
    }
    if set(schemas) != expected_schema_names:
        diagnostics.bad("SCHEMA_SET_INCOMPLETE", run / "schemas",
                        "all canonical and solver-facing schemas must parse and validate")

    database_path = Path(seal["bugbank_database"]["path"]).resolve()
    database_before = sha_file(database_path)
    database: BugBankView | None = None
    try:
        database = BugBankView(database_path)
    except (OSError, sqlite3.Error) as error:
        diagnostics.bad("BUGBANK_DATABASE_INVALID", database_path, str(error))

    records: dict[str, Any] = {}
    all_bundles: dict[tuple[str, str], dict[int, IterationBundle]] = {}
    all_endpoints: dict[tuple[str, str], dict[str, Any] | None] = {}
    referenced_checkers: set[Path] = set()
    referenced_forensics: set[Path] = set()
    valid_terminals = 0
    if database is not None and set(schemas) == expected_schema_names:
        try:
            for record_id in roster:
                baseline = validate_baseline_bundle(
                    run, record_id, manifest, seal, schemas, diagnostics
                )
                referenced_checkers.update(
                    _metadata_checker_paths(baseline.audit_metadata, run)
                )
                bugbank_bundles, bugbank_endpoint = validate_arm_chain(
                    run, record_id, "bugbank", baseline, manifest, seal,
                    schemas, database, inventory, diagnostics,
                )
                bugbank_target = (
                    bugbank_endpoint.get("model_tokens_used")
                    if bugbank_endpoint is not None else None
                )
                plain_bundles, plain_endpoint = validate_arm_chain(
                    run, record_id, "plain", baseline, manifest, seal,
                    schemas, database, inventory, diagnostics,
                    bugbank_target,
                )
                all_bundles[(record_id, "bugbank")] = bugbank_bundles
                all_bundles[(record_id, "plain")] = plain_bundles
                all_endpoints[(record_id, "bugbank")] = bugbank_endpoint
                all_endpoints[(record_id, "plain")] = plain_endpoint
                for bundles in (bugbank_bundles, plain_bundles):
                    for bundle in bundles.values():
                        referenced_checkers.update(
                            _metadata_checker_paths(bundle.audit_metadata, run)
                        )
                        revision_state = bundle.states.get("revision")
                        recovery = inventory.recoveries.get(
                            (record_id, bundle.arm, bundle.iteration)
                        )
                        recovered = bool(
                            revision_state is not None
                            and revision_state.value.get("status") == "RECOVERED_COMPLETE"
                        )
                        if recovered and recovery is None:
                            diagnostics.bad("RECOVERY_RECORD_MISSING",
                                            revision_state.path,
                                            "recovered completion lacks its recovery record")
                            bundle.valid = False
                        elif recovery is not None:
                            recovery_artifact = load_artifact(recovery, diagnostics)
                            if not recovered or recovery_artifact is None:
                                diagnostics.bad("ORPHAN_RECOVERY", recovery,
                                                "recovery does not bind an accepted recovered state")
                                bundle.valid = False
                            else:
                                recovery_ok, forensic = validate_recovery(
                                    recovery_artifact, bundle, revision_state,
                                    run, diagnostics,
                                )
                                bundle.valid = bundle.valid and recovery_ok
                                referenced_forensics.update(forensic)
                # Recovery validation may invalidate what initially appeared to
                # be an endpoint, so recompute from the final bundle validity.
                bugbank_endpoint = derive_endpoint(
                    run, inventory, bugbank_bundles, record_id, "bugbank", None,
                    diagnostics,
                )
                bugbank_target = (bugbank_endpoint.get("model_tokens_used")
                                  if bugbank_endpoint is not None else None)
                plain_endpoint = derive_endpoint(
                    run, inventory, plain_bundles, record_id, "plain",
                    bugbank_target, diagnostics,
                )
                all_endpoints[(record_id, "bugbank")] = bugbank_endpoint
                all_endpoints[(record_id, "plain")] = plain_endpoint
                if bugbank_endpoint is not None:
                    reject_post_endpoint_artifacts(
                        inventory, record_id, "bugbank",
                        bugbank_endpoint["iteration"], diagnostics,
                    )
                if plain_endpoint is not None:
                    reject_post_endpoint_artifacts(
                        inventory, record_id, "plain",
                        plain_endpoint["iteration"], diagnostics,
                    )
                terminal_artifact = load_artifact(
                    terminal_path(run, record_id), diagnostics
                )
                terminal_ok = validate_terminal_artifact(
                    terminal_artifact, run, record_id, manifest, baseline,
                    {"bugbank": bugbank_endpoint, "plain": plain_endpoint},
                    diagnostics,
                )
                valid_terminals += int(terminal_ok)
                records[record_id] = {
                    "baseline_valid": baseline.valid,
                    "arms": {
                        "bugbank": {
                            "iterations": sorted(bugbank_bundles),
                            "endpoint": bugbank_endpoint,
                        },
                        "plain": {
                            "iterations": sorted(plain_bundles),
                            "endpoint": plain_endpoint,
                        },
                    },
                    "pair_terminal_valid": terminal_ok,
                }
        finally:
            database.close()
    if sha_file(database_path) != database_before:
        diagnostics.bad("BUGBANK_CHANGED_DURING_VALIDATION", database_path,
                        "pinned database bytes changed during independent queries")

    for identity, path in inventory.checkers.items():
        if path.resolve() not in referenced_checkers:
            diagnostics.bad("UNBOUND_CHECKER", path,
                            f"checker {identity!r} is not bound by valid audit metadata")
    for identity, path in inventory.states.items():
        if path.resolve() not in diagnostics.checked_state_paths:
            diagnostics.bad(
                "UNCHECKED_CALL_STATE", path,
                f"state {identity!r} has no independently validated lineage",
            )
    for artifact in _runtime_json_artifacts(inventory, diagnostics):
        _reject_historical_fields(artifact.value, artifact.path, diagnostics)

    closed = global_closed_world(
        run, manifest, True, inventory, referenced_forensics,
        diagnostics, extra_allowed,
    )
    status = "INVALID" if diagnostics.invalid else (
        "INCOMPLETE" if diagnostics.incomplete or valid_terminals != len(roster)
        else "VALID_COMPLETE"
    )
    report: dict[str, Any] = {
        "schema": "paired_open_problem_exploratory_validation_report_v1",
        "run_id": manifest["run_id"],
        "run_path": str(run),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "validator": {"path": str(SCRIPT), "sha256": sha_file(SCRIPT)},
        "status": status,
        "protocol_id": manifest["protocol"]["id"],
        "counts": {
            "problems": len(roster),
            "valid_pair_terminals": valid_terminals,
            "arm_endpoints": {
                arm: sum(all_endpoints.get((record_id, arm)) is not None
                         for record_id in roster)
                for arm in ARMS
            },
            "verified_full": {
                arm: sum(
                    all_endpoints.get((record_id, arm)) is not None
                    and all_endpoints[(record_id, arm)]["status"] == "VERIFIED_FULL"
                    for record_id in roster
                ) for arm in ARMS
            },
        },
        "closed_world": closed,
        "records": records,
        "diagnostics": {
            "invalid_count": len(diagnostics.invalid),
            "incomplete_count": len(diagnostics.incomplete),
            "warning_count": len(diagnostics.warnings),
            "invalid": diagnostics.invalid,
            "incomplete": diagnostics.incomplete,
            "warnings": diagnostics.warnings,
        },
    }
    return report


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(dict(report))
    value.pop("report_payload_sha256", None)
    value["report_payload_sha256"] = sha_bytes(canonical_bytes(value))
    return value


def atomic_write_report(
        path: Path, report: Mapping[str, Any], *, staging_root: Path | None = None
        ) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path) and (path.is_symlink() or not path.is_file()):
        raise OSError("validation report target is not a plain file")
    data = (json.dumps(report, ensure_ascii=False, allow_nan=False,
                       sort_keys=True, indent=2).encode("utf-8") + b"\n")
    if staging_root is None:
        staging = path.parent
    else:
        staging_root = staging_root.resolve()
        staging_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        root_info = staging_root.lstat()
        if (staging_root.is_symlink() or not staging_root.is_dir()
                or staging_root.resolve() != staging_root):
            raise OSError("validation-report scratch root is not an exact plain directory")
        if root_info.st_mode & 0o077:
            staging_root.chmod(0o700)
            root_info = staging_root.lstat()
        staging = staging_root / ".validator-atomic"
        staging.mkdir(parents=True, exist_ok=True, mode=0o700)
        staging_info = staging.lstat()
        if (staging.is_symlink() or not staging.is_dir()
                or staging.resolve().parent != staging_root
                or staging_info.st_mode & 0o077):
            raise OSError("validation-report staging directory is not private and exact")
        if (root_info.st_dev != path.parent.stat().st_dev
                or staging_info.st_dev != root_info.st_dev):
            raise OSError(
                "validation-report external staging and target are on different filesystems"
            )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f"{path.name}__", dir=staging
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fchmod(handle.fileno(), 0o644)
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Exit codes: 0 VALID_COMPLETE; 1 INCOMPLETE; 2 INVALID. "
            "--allow-incomplete maps only INCOMPLETE to zero."
        ),
    )
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--max-diagnostics", type=int, default=60)
    arguments = parser.parse_args()
    if arguments.max_diagnostics < 0:
        parser.error("--max-diagnostics must be nonnegative")
    return arguments


def print_text_report(report: Mapping[str, Any], maximum: int) -> None:
    print(f"status: {report['status']}")
    counts = report.get("counts", {})
    if counts:
        print(
            f"pair terminals: {counts.get('valid_pair_terminals', 0)}/"
            f"{counts.get('problems', 0)} valid"
        )
        if "arm_endpoints" in counts:
            print(
                "arm endpoints: "
                f"bugbank={counts['arm_endpoints']['bugbank']}, "
                f"plain={counts['arm_endpoints']['plain']}"
            )
    rows: list[tuple[str, Mapping[str, str]]] = []
    diagnostic = report["diagnostics"]
    for label, key in (("INVALID", "invalid"), ("INCOMPLETE", "incomplete"),
                       ("WARNING", "warnings")):
        rows.extend((label, row) for row in diagnostic[key])
    print(
        "diagnostics: "
        f"invalid={diagnostic['invalid_count']}, "
        f"incomplete={diagnostic['incomplete_count']}, "
        f"warnings={diagnostic['warning_count']}"
    )
    for label, row in rows[:maximum]:
        print(f"{label} {row['code']} {row['path']}: {row['message']}")
    if len(rows) > maximum:
        print(f"... {len(rows) - maximum} more diagnostics")


def main() -> int:
    arguments = parse_arguments()
    if arguments.report is not None:
        run = arguments.run_root.resolve()
        destination = arguments.report.resolve()
        canonical = (run / "VALIDATION_REPORT.json").resolve()
        if (destination == run or run in destination.parents) and destination != canonical:
            print(
                "error: the only permitted in-run report is exactly "
                f"{canonical}", file=sys.stderr,
            )
            return 2
    report = seal_report(validate_run(arguments.run_root))
    if arguments.report is not None:
        try:
            destination = arguments.report.resolve()
            canonical = (arguments.run_root.resolve() / "VALIDATION_REPORT.json").resolve()
            staging_root = None
            if destination == canonical:
                manifest, _bound = seal_checker.validate_manifest(
                    arguments.run_root.resolve()
                )
                staging_root = Path(manifest["operations"]["scratch_root"])
            atomic_write_report(
                destination, report, staging_root=staging_root,
            )
        except (OSError, KeyError, TypeError, seal_checker.SealError) as error:
            print(f"error: cannot write report: {error}", file=sys.stderr)
            return 2
    if arguments.json:
        print(json.dumps(report, ensure_ascii=False, allow_nan=False,
                         sort_keys=True, indent=2))
    else:
        print_text_report(report, arguments.max_diagnostics)
    if report["status"] == "INVALID":
        return 2
    if report["status"] == "INCOMPLETE" and not arguments.allow_incomplete:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
