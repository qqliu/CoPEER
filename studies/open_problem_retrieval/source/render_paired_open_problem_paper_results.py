#!/usr/bin/env python3
"""Render paper_v2 results from the three final paired-run authorities.

The only scientific result inputs are each run's canonical final validation
report and canonical pair-terminal directory.  The current independent
validator bytes authenticate the validator digest recorded in each report.
No output is published unless all three reports are VALID_COMPLETE and every
result-bearing report/terminal field is mutually consistent.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "qedbench_certificate_availability_triage" / "runs"
SCRIPTS = REPO / "qedbench_certificate_availability_triage" / "scripts"
DEFAULT_OUTPUT_DIRECTORY = REPO / "paper_v2" / "generated"
OUTPUT_NAMES = {
    "json": "paired_open_problem_results.json",
    "macros": "paired_open_problem_macros.tex",
    "rows": "paired_open_problem_rows.tex",
}
MAX_SAFE_JSON_INTEGER = (1 << 53) - 1
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{2,199}$")
ARMS = ("bugbank", "plain")
EXPECTED_PROTOCOL_POPULATIONS = {
    "original": 31,
    "hard": 5,
    "extension": 22,
}
EXPECTED_DISTINCT_TARGETS = 36
OUTCOME_SEMANTICS = {
    "audited_full_is_run_local": True,
    "audited_full_is_external_solution_claim": False,
    "neither_audited_full_may_include_valid_partial_progress": True,
}


class RenderError(RuntimeError):
    """An input or output violates the publication contract."""


@dataclass(frozen=True)
class SourceSpec:
    key: str
    label: str
    run_root: Path
    report_name: str
    terminal_directory: str
    report_schema: str
    terminal_schema: str
    validator: Path
    comparison_basis: str
    macro_prefix: str


@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    data: bytes
    sha256: str
    device: int
    inode: int
    size: int
    mtime_ns: int
    ctime_ns: int

    def assert_unchanged(self) -> None:
        current = read_plain_file(self.path)
        require(
            (current.device, current.inode, current.size, current.mtime_ns,
             current.ctime_ns, current.sha256)
            == (self.device, self.inode, self.size, self.mtime_ns,
                self.ctime_ns, self.sha256),
            f"input changed while rendering: {self.path}",
        )


@dataclass(frozen=True)
class ProtocolResult:
    result: dict[str, Any]
    source: dict[str, Any]
    snapshots: tuple[FileSnapshot, ...]
    terminal_directory: Path
    terminal_names: frozenset[str]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RenderError(message)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RenderError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_nonfinite_json(token: str) -> Any:
    raise RenderError(f"non-finite JSON number {token}")


def parse_finite_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value) or abs(value) > MAX_SAFE_JSON_INTEGER:
        reject_nonfinite_json(token)
    return value


def parse_safe_json_int(token: str) -> int:
    value = int(token)
    if abs(value) > MAX_SAFE_JSON_INTEGER:
        raise RenderError(f"unsafe JSON integer {token}")
    return value


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise RenderError(f"value cannot be serialized canonically: {error}") from error


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_plain_file(path: Path) -> FileSnapshot:
    path = Path(os.path.abspath(path))
    try:
        before = path.lstat()
    except OSError as error:
        raise RenderError(f"cannot stat required file {path}: {error}") from error
    require(stat.S_ISREG(before.st_mode), f"required input is not a plain file: {path}")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise RenderError(f"cannot open required plain file {path}: {error}") from error
    try:
        opened = os.fstat(descriptor)
        require(
            stat.S_ISREG(opened.st_mode)
            and (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
            f"required input changed identity while opening: {path}",
        )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        require(
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
             after.st_ctime_ns)
            == (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns,
                opened.st_ctime_ns),
            f"required input changed while reading: {path}",
        )
    finally:
        os.close(descriptor)
    try:
        final = path.lstat()
    except OSError as error:
        raise RenderError(f"required input disappeared after reading {path}: {error}") from error
    require(
        stat.S_ISREG(final.st_mode)
        and (final.st_dev, final.st_ino) == (after.st_dev, after.st_ino),
        f"required input was replaced while reading: {path}",
    )
    data = b"".join(chunks)
    require(len(data) == after.st_size, f"short read from required input: {path}")
    return FileSnapshot(
        path=path,
        data=data,
        sha256=sha_bytes(data),
        device=after.st_dev,
        inode=after.st_ino,
        size=after.st_size,
        mtime_ns=after.st_mtime_ns,
        ctime_ns=after.st_ctime_ns,
    )


def load_json_snapshot(path: Path) -> tuple[Any, FileSnapshot]:
    snapshot = read_plain_file(path)
    try:
        text = snapshot.data.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_json_float,
            parse_int=parse_safe_json_int,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RenderError(f"invalid strict UTF-8 JSON in {path}: {error}") from error
    return value, snapshot


def require_object(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is dict, f"{label} must be a JSON object")
    return value


def require_exact_keys(value: Mapping[str, Any], keys: Iterable[str], label: str) -> None:
    expected = set(keys)
    actual = set(value)
    require(
        actual == expected,
        f"{label} field set mismatch: missing={sorted(expected - actual)}, "
        f"unexpected={sorted(actual - expected)}",
    )


def require_sha(value: Any, label: str) -> str:
    require(type(value) is str and SHA256_RE.fullmatch(value) is not None,
            f"{label} must be a lowercase SHA-256")
    return value


def require_identifier(value: Any, label: str) -> str:
    require(type(value) is str and IDENTIFIER_RE.fullmatch(value) is not None,
            f"{label} is not a safe canonical identifier")
    return value


def require_token(value: Any, label: str) -> int:
    require(type(value) is int and 0 <= value <= MAX_SAFE_JSON_INTEGER,
            f"{label} is not an exact nonnegative JSON-safe token count")
    return value


def require_count(value: Any, label: str, *, minimum: int = 0) -> int:
    require(type(value) is int and minimum <= value <= MAX_SAFE_JSON_INTEGER,
            f"{label} is not an exact JSON-safe integer count")
    return value


def require_token_difference(value: Any, label: str) -> int:
    require(type(value) is int and abs(value) <= MAX_SAFE_JSON_INTEGER,
            f"{label} is not an exact JSON-safe token difference")
    return value


def safe_add(values: Iterable[int], label: str) -> int:
    total = sum(values)
    require(0 <= total <= MAX_SAFE_JSON_INTEGER,
            f"{label} exceeds exact JSON-integer accounting")
    return total


def safe_subtract(left: int, right: int, label: str) -> int:
    result = left - right
    require(abs(result) <= MAX_SAFE_JSON_INTEGER,
            f"{label} exceeds exact JSON-integer accounting")
    return result


def validate_payload_hash(value: Mapping[str, Any], field: str, label: str) -> str:
    recorded = require_sha(value.get(field), f"{label}.{field}")
    unsigned = copy.deepcopy(dict(value))
    unsigned.pop(field, None)
    require(recorded == sha_bytes(canonical_bytes(unsigned)),
            f"{label} payload hash mismatch")
    return recorded


def plain_directory_names(path: Path) -> frozenset[str]:
    try:
        info = path.lstat()
    except OSError as error:
        raise RenderError(f"cannot stat required directory {path}: {error}") from error
    require(stat.S_ISDIR(info.st_mode), f"required directory is not plain: {path}")
    try:
        entries = list(path.iterdir())
    except OSError as error:
        raise RenderError(f"cannot inventory required directory {path}: {error}") from error
    for entry in entries:
        try:
            entry_info = entry.lstat()
        except OSError as error:
            raise RenderError(f"cannot stat terminal-directory entry {entry}: {error}") from error
        require(stat.S_ISREG(entry_info.st_mode),
                f"terminal-directory entry is not a plain file: {entry}")
    return frozenset(entry.name for entry in entries)


def validate_diagnostics(value: Any, label: str) -> None:
    diagnostics = require_object(value, label)
    require_exact_keys(
        diagnostics,
        {"invalid_count", "incomplete_count", "warning_count",
         "invalid", "incomplete", "warnings"},
        label,
    )
    invalid_count = require_count(diagnostics["invalid_count"], f"{label}.invalid_count")
    incomplete_count = require_count(
        diagnostics["incomplete_count"], f"{label}.incomplete_count"
    )
    warning_count = require_count(diagnostics["warning_count"], f"{label}.warning_count")
    require(invalid_count == 0 and diagnostics["invalid"] == [],
            f"{label} contains invalid findings")
    require(incomplete_count == 0 and diagnostics["incomplete"] == [],
            f"{label} contains incomplete findings")
    warnings = diagnostics["warnings"]
    require(type(warnings) is list and warning_count == len(warnings),
            f"{label} warning accounting mismatch")


def validate_validator_binding(
    spec: SourceSpec, report: Mapping[str, Any], validator_snapshot: FileSnapshot,
) -> str:
    if spec.key == "extension":
        recorded = report.get("independent_validator_sha256")
    else:
        binding = require_object(report.get("validator"), f"{spec.key} report.validator")
        require_exact_keys(binding, {"path", "sha256"}, f"{spec.key} report.validator")
        require(type(binding["path"]) is str and Path(binding["path"]).name == spec.validator.name,
                f"{spec.key} report names the wrong validator")
        recorded = binding["sha256"]
    require_sha(recorded, f"{spec.key} validator digest")
    require(recorded == validator_snapshot.sha256,
            f"{spec.key} report was not produced by the current validator bytes")
    return recorded


def validate_original_report(spec: SourceSpec, report: dict[str, Any]) -> tuple[str, ...]:
    require_exact_keys(
        report,
        {"schema", "run_id", "run_path", "validator", "generated_at", "status",
         "exit_code_contract", "universe", "stage_counts", "outcomes",
         "audit_results", "terminal_counts", "telemetry", "per_record",
         "diagnostics", "report_payload_sha256"},
        "original validation report",
    )
    validate_diagnostics(report["diagnostics"], "original report diagnostics")
    universe = require_object(report["universe"], "original report universe")
    bindings = require_object(universe.get("input_sha256"),
                              "original report universe.input_sha256")
    roster = tuple(sorted(require_identifier(item, "original record ID") for item in bindings))
    require(len(roster) > 0 and all(require_sha(value, f"original input {key}")
                                    for key, value in bindings.items()),
            "original input roster is empty or malformed")
    expected = require_count(universe.get("expected"), "original universe.expected", minimum=1)
    inputs_valid = require_count(
        universe.get("inputs_valid"), "original universe.inputs_valid"
    )
    require(universe.get("exact_roster") is True
            and expected == len(roster)
            and inputs_valid == len(roster),
            "original report universe is not complete")
    per_record = require_object(report["per_record"], "original report per_record")
    require(set(per_record) == set(roster), "original report record roster mismatch")
    pair_counts = require_object(
        require_object(report["stage_counts"], "original stage_counts").get("pair_terminals"),
        "original pair-terminal counts",
    )
    require(all(require_count(pair_counts.get(key), f"original pair counts.{key}")
                == len(roster) for key in ("expected", "present", "valid")),
            "original report does not validate every pair terminal")
    return roster


def validate_hard_report(spec: SourceSpec, report: dict[str, Any]) -> tuple[str, ...]:
    require_exact_keys(
        report,
        {"schema", "run_id", "run_path", "generated_at", "validator", "status",
         "protocol_id", "counts", "closed_world", "records", "diagnostics",
         "report_payload_sha256"},
        "hard validation report",
    )
    validate_diagnostics(report["diagnostics"], "hard report diagnostics")
    require(type(report["protocol_id"]) is str and bool(report["protocol_id"].strip()),
            "hard report protocol_id is empty")
    records = require_object(report["records"], "hard report records")
    roster = tuple(sorted(require_identifier(item, "hard record ID") for item in records))
    require(len(roster) > 0, "hard report record roster is empty")
    counts = require_object(report["counts"], "hard report counts")
    require_exact_keys(
        counts,
        {"problems", "valid_pair_terminals", "arm_endpoints", "verified_full"},
        "hard report counts",
    )
    problems = require_count(counts.get("problems"), "hard counts.problems", minimum=1)
    valid_terminals = require_count(
        counts.get("valid_pair_terminals"), "hard counts.valid_pair_terminals"
    )
    require(problems == len(roster) and valid_terminals == len(roster),
            "hard report pair-terminal coverage is incomplete")
    endpoints = require_object(counts.get("arm_endpoints"), "hard arm endpoint counts")
    require(set(endpoints) == set(ARMS)
            and all(require_count(endpoints[arm], f"hard arm endpoints.{arm}")
                    == len(roster) for arm in ARMS),
            "hard report arm endpoints are incomplete")
    return roster


def validate_extension_report(spec: SourceSpec, report: dict[str, Any]) -> tuple[str, ...]:
    require_exact_keys(
        report,
        {"schema", "run_id", "status", "problem_count", "validated_count",
         "records", "errors", "independent_validator_sha256",
         "report_payload_sha256"},
        "extension validation report",
    )
    require(report["errors"] == [], "extension validation report contains errors")
    records = report["records"]
    require(type(records) is list and len(records) > 0,
            "extension report records must be a nonempty array")
    ids: list[str] = []
    for index, row_value in enumerate(records):
        row = require_object(row_value, f"extension report record {index}")
        require_exact_keys(
            row,
            {"record_id", "status", "bugbank", "plain", "bugbank_attempts",
             "plain_attempts", "bugbank_partial_stage", "plain_partial_stage"},
            f"extension report record {index}",
        )
        ids.append(require_identifier(row["record_id"], "extension record ID"))
        require(row["status"] == "COMPLETE",
                f"extension report record {row['record_id']} is not complete")
        for arm in ARMS:
            require_count(
                row[f"{arm}_attempts"],
                f"extension report record {row['record_id']} {arm}_attempts",
                minimum=1,
            )
        require(row["bugbank_partial_stage"] is None
                and row["plain_partial_stage"] is None,
                f"extension report record {row['record_id']} has a partial stage")
    require(len(ids) == len(set(ids)), "extension report has duplicate record IDs")
    problem_count = require_count(
        report["problem_count"], "extension report.problem_count", minimum=1
    )
    validated_count = require_count(
        report["validated_count"], "extension report.validated_count"
    )
    require(problem_count == len(ids) and validated_count == len(ids),
            "extension report record coverage is incomplete")
    return tuple(sorted(ids))


def validate_report(
    spec: SourceSpec, report_value: Any, validator_snapshot: FileSnapshot,
) -> tuple[dict[str, Any], tuple[str, ...], str]:
    report = require_object(report_value, f"{spec.key} validation report")
    require(report.get("schema") == spec.report_schema,
            f"{spec.key} validation report schema mismatch")
    require(report.get("status") == "VALID_COMPLETE",
            f"{spec.key} validation report is not VALID_COMPLETE")
    run_id = require_identifier(report.get("run_id"), f"{spec.key} run_id")
    require(run_id == spec.run_root.name,
            f"{spec.key} validation report run_id does not match its run directory")
    payload_sha = validate_payload_hash(
        report, "report_payload_sha256", f"{spec.key} validation report"
    )
    validate_validator_binding(spec, report, validator_snapshot)
    if spec.key == "original":
        roster = validate_original_report(spec, report)
    elif spec.key == "hard":
        roster = validate_hard_report(spec, report)
    elif spec.key == "extension":
        roster = validate_extension_report(spec, report)
    else:
        raise RenderError(f"unknown protocol adapter: {spec.key}")
    return report, roster, payload_sha


def report_records(spec: SourceSpec, report: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if spec.key == "original":
        return dict(report["per_record"])
    if spec.key == "hard":
        return dict(report["records"])
    return {row["record_id"]: row for row in report["records"]}


def parse_standard_terminal(
    spec: SourceSpec, terminal: dict[str, Any], report_record: dict[str, Any],
) -> dict[str, Any]:
    require_exact_keys(
        terminal,
        {"schema", "run_id", "record_id", "stage", "status", "pair_status",
         "max_iterations", "retrieval_k", "treatment_contrast_valid",
         "proof_endpoints_complete", "token_comparison_auditable", "solved_arms",
         "bugbank_model_tokens_used", "plain_model_tokens_used",
         "plain_minus_bugbank_tokens", "plain_solved_with_fewer_tokens", "baseline",
         "arms", "terminal_payload_sha256"},
        f"{spec.key} pair terminal {terminal.get('record_id')}",
    )
    maximum = require_count(
        terminal["max_iterations"], f"{spec.key} terminal max_iterations", minimum=1
    )
    retrieval_k = require_count(
        terminal["retrieval_k"], f"{spec.key} terminal retrieval_k", minimum=1
    )
    require(terminal["stage"] == "PAIR_TERMINAL"
            and maximum == 50 and retrieval_k == 3,
            f"{spec.key} pair terminal protocol constants mismatch")
    require(terminal["status"] == "COMPLETE" and terminal["pair_status"] == "COMPLETE",
            f"{spec.key} pair terminal is not complete")
    require(terminal["treatment_contrast_valid"] is True
            and terminal["proof_endpoints_complete"] is True
            and terminal["token_comparison_auditable"] is True,
            f"{spec.key} pair terminal does not authorize a treatment comparison")
    arms = require_object(terminal["arms"], f"{spec.key} terminal arms")
    require(set(arms) == set(ARMS), f"{spec.key} terminal arm set mismatch")

    parsed_arms: dict[str, dict[str, Any]] = {}
    for arm in ARMS:
        row = require_object(arms[arm], f"{spec.key} terminal {arm} arm")
        status_value = row.get("status")
        require(status_value in {"VERIFIED_FULL", "INCONCLUSIVE_FIXED_POINT"},
                f"{spec.key} terminal has an unknown {arm} endpoint status")
        require(row.get("arm") == arm and row.get("terminal") is True,
                f"{spec.key} terminal {arm} arm is not a terminal endpoint")
        endpoint = row.get("iteration")
        require(type(endpoint) is int and 1 <= endpoint <= maximum,
                f"{spec.key} terminal {arm} iteration is invalid")
        tokens = require_token(row.get("model_tokens_used"),
                               f"{spec.key} terminal {arm} tokens")
        require(row.get("model_token_cost_auditable") is True,
                f"{spec.key} terminal {arm} token cost is not auditable")
        parsed_arms[arm] = {
            "status": status_value,
            "solved": status_value == "VERIFIED_FULL",
            "endpoint": endpoint,
            "model_tokens_used": tokens,
        }

    if spec.key == "original":
        require(report_record.get("pair_terminal_present") is True
                and report_record.get("pair_terminal_valid") is True,
                f"original report does not validate {terminal['record_id']} terminal")
        report_arms = require_object(report_record.get("arms"), "original report arms")
        for arm in ARMS:
            report_arm = require_object(report_arms.get(arm), f"original report {arm} arm")
            endpoint = require_object(report_arm.get("terminal"),
                                      f"original report {arm} terminal")
            for key, terminal_key in (
                ("status", "status"), ("terminal", "terminal"),
                ("iteration", "iteration"), ("model_tokens_used", "model_tokens_used"),
                ("revision_sha256", "revision_sha256"), ("audit_sha256", "audit_sha256"),
            ):
                require(endpoint.get(key) == arms[arm].get(terminal_key),
                        f"original report/terminal mismatch for {terminal['record_id']}:{arm}:{key}")
    else:
        require(report_record.get("baseline_valid") is True
                and report_record.get("pair_terminal_valid") is True,
                f"hard report does not validate {terminal['record_id']} terminal")
        report_arms = require_object(report_record.get("arms"), "hard report arms")
        for arm in ARMS:
            report_arm = require_object(report_arms.get(arm), f"hard report {arm} arm")
            require(report_arm.get("endpoint") == arms[arm],
                    f"hard report/terminal mismatch for {terminal['record_id']}:{arm}")

    solved_arms = [arm for arm in ARMS if parsed_arms[arm]["solved"]]
    require(terminal["solved_arms"] == solved_arms,
            f"{spec.key} terminal solved-arm accounting mismatch")
    bugbank_tokens = parsed_arms["bugbank"]["model_tokens_used"]
    plain_tokens = parsed_arms["plain"]["model_tokens_used"]
    reported_bugbank_tokens = require_token(
        terminal["bugbank_model_tokens_used"],
        f"{spec.key} terminal bugbank_model_tokens_used",
    )
    reported_plain_tokens = require_token(
        terminal["plain_model_tokens_used"],
        f"{spec.key} terminal plain_model_tokens_used",
    )
    reported_difference = require_token_difference(
        terminal["plain_minus_bugbank_tokens"],
        f"{spec.key} terminal plain_minus_bugbank_tokens",
    )
    require(reported_bugbank_tokens == bugbank_tokens
            and reported_plain_tokens == plain_tokens
            and reported_difference
            == safe_subtract(plain_tokens, bugbank_tokens,
                             f"{spec.key} per-record token difference"),
            f"{spec.key} terminal token accounting mismatch")
    expected_plain_cheaper = (
        plain_tokens < bugbank_tokens if parsed_arms["plain"]["solved"] else None
    )
    require(terminal["plain_solved_with_fewer_tokens"] is expected_plain_cheaper,
            f"{spec.key} terminal plain-solved token comparison mismatch")
    return normalized_record(
        terminal["record_id"], parsed_arms, bugbank_tokens, plain_tokens
    )


def parse_extension_terminal(
    spec: SourceSpec, terminal: dict[str, Any], report_record: dict[str, Any],
) -> dict[str, Any]:
    require_exact_keys(
        terminal,
        {"schema", "run_id", "record_id", "stage", "status",
         "treatment_contrast_valid", "forced_audited_attempts", "max_attempts",
         "retrieval_k", "comparison_basis", "incremental_plain_minus_bugbank_tokens",
         "lifetime_plain_minus_bugbank_tokens", "solved_arms", "seed_pair_terminal",
         "arms", "terminal_payload_sha256"},
        f"extension pair terminal {terminal.get('record_id')}",
    )
    require(terminal["stage"] == "EXTENSION_PAIR_TERMINAL",
            "extension pair terminal stage mismatch")
    forced_attempts = require_count(
        terminal["forced_audited_attempts"],
        "extension terminal forced_audited_attempts", minimum=1,
    )
    maximum = require_count(
        terminal["max_attempts"], "extension terminal max_attempts", minimum=1
    )
    retrieval_k = require_count(
        terminal["retrieval_k"], "extension terminal retrieval_k", minimum=1
    )
    require(terminal["status"] == "COMPLETE"
            and terminal["treatment_contrast_valid"] is True,
            "extension pair terminal is not a valid complete comparison")
    require(forced_attempts == 3 and maximum == 50 and retrieval_k == 3
            and terminal["comparison_basis"] == spec.comparison_basis,
            "extension pair terminal protocol constants mismatch")
    seed_binding = require_object(
        terminal["seed_pair_terminal"], "extension seed pair-terminal binding"
    )
    require_exact_keys(
        seed_binding, {"path", "sha256", "size_bytes"},
        "extension seed pair-terminal binding",
    )
    require(type(seed_binding["path"]) is str and bool(seed_binding["path"])
            and require_sha(seed_binding["sha256"], "extension seed terminal digest")
            and type(seed_binding["size_bytes"]) is int
            and 0 <= seed_binding["size_bytes"] <= MAX_SAFE_JSON_INTEGER,
            "extension seed pair-terminal binding is malformed")
    arms = require_object(terminal["arms"], "extension terminal arms")
    require(set(arms) == set(ARMS), "extension terminal arm set mismatch")
    parsed_arms: dict[str, dict[str, Any]] = {}
    lifetime: dict[str, int] = {}
    for arm in ARMS:
        row = require_object(arms[arm], f"extension terminal {arm} arm")
        status_value = row.get("status")
        require(status_value in {"VERIFIED_FULL", "INCONCLUSIVE_EXTENDED_FIXED_POINT"},
                f"extension terminal has an unknown {arm} endpoint status")
        require(row.get("arm") == arm and row.get("terminal") is True,
                f"extension terminal {arm} arm is not a terminal endpoint")
        endpoint = row.get("attempt")
        require(type(endpoint) is int and 1 <= endpoint <= maximum,
                f"extension terminal {arm} attempt is invalid")
        incremental = require_token(
            row.get("incremental_model_tokens_used"),
            f"extension terminal {arm} incremental tokens",
        )
        seed = require_token(row.get("seed_lifetime_model_tokens"),
                             f"extension terminal {arm} seed tokens")
        lifetime_value = require_token(row.get("lifetime_model_tokens_used"),
                                       f"extension terminal {arm} lifetime tokens")
        require(row.get("incremental_token_cost_auditable") is True
                and lifetime_value == safe_add(
                    (seed, incremental), f"extension terminal {arm} lifetime tokens"
                ),
                f"extension terminal {arm} token accounting mismatch")
        report_endpoint = require_object(report_record.get(arm),
                                         f"extension report {arm} endpoint")
        require_exact_keys(
            report_endpoint,
            {"terminal", "status", "attempt", "incremental_tokens", "reason"},
            f"extension report {arm} endpoint",
        )
        report_attempt = require_count(
            report_endpoint["attempt"],
            f"extension report {arm} endpoint attempt", minimum=1,
        )
        report_incremental = require_token(
            report_endpoint["incremental_tokens"],
            f"extension report {arm} endpoint incremental_tokens",
        )
        require(report_endpoint["terminal"] is True
                and report_endpoint["status"] == status_value
                and report_attempt == endpoint
                and report_incremental == incremental,
                f"extension report/terminal mismatch for {terminal['record_id']}:{arm}")
        require(require_count(
                    report_record[f"{arm}_attempts"],
                    f"extension report {arm}_attempts", minimum=1,
                ) == endpoint,
                f"extension report attempt count mismatch for {terminal['record_id']}:{arm}")
        parsed_arms[arm] = {
            "status": status_value,
            "solved": status_value == "VERIFIED_FULL",
            "endpoint": endpoint,
            "model_tokens_used": incremental,
            "seed_lifetime_model_tokens": seed,
            "lifetime_model_tokens_used": lifetime_value,
        }
        lifetime[arm] = lifetime_value
    solved_arms = [arm for arm in ARMS if parsed_arms[arm]["solved"]]
    require(terminal["solved_arms"] == solved_arms,
            "extension terminal solved-arm accounting mismatch")
    bugbank_tokens = parsed_arms["bugbank"]["model_tokens_used"]
    plain_tokens = parsed_arms["plain"]["model_tokens_used"]
    incremental_difference = require_token_difference(
        terminal["incremental_plain_minus_bugbank_tokens"],
        "extension incremental_plain_minus_bugbank_tokens",
    )
    lifetime_difference = require_token_difference(
        terminal["lifetime_plain_minus_bugbank_tokens"],
        "extension lifetime_plain_minus_bugbank_tokens",
    )
    require(incremental_difference
            == safe_subtract(plain_tokens, bugbank_tokens,
                             "extension incremental token difference")
            and lifetime_difference
            == safe_subtract(lifetime["plain"], lifetime["bugbank"],
                             "extension lifetime token difference"),
            "extension terminal token-difference accounting mismatch")
    result = normalized_record(
        terminal["record_id"], parsed_arms, bugbank_tokens, plain_tokens
    )
    result["lifetime_plain_minus_bugbank_tokens"] = lifetime_difference
    # Retain the seed binding so the cross-protocol aggregate can prove that
    # this continuation really descends from the same original target and
    # terminal bytes that it supersedes.
    result["seed_pair_terminal"] = dict(seed_binding)
    return result


def normalized_record(
    record_id: str,
    arms: Mapping[str, Mapping[str, Any]],
    bugbank_tokens: int,
    plain_tokens: int,
) -> dict[str, Any]:
    bugbank_solved = bool(arms["bugbank"]["solved"])
    plain_solved = bool(arms["plain"]["solved"])
    if bugbank_solved and plain_solved:
        outcome = "BOTH_SOLVED"
    elif bugbank_solved:
        outcome = "BUGBANK_ONLY"
    elif plain_solved:
        outcome = "PLAIN_ONLY"
    else:
        outcome = "NEITHER_SOLVED"
    lower = "BUGBANK" if bugbank_tokens < plain_tokens else (
        "PLAIN" if plain_tokens < bugbank_tokens else "TIE"
    )
    return {
        "record_id": record_id,
        "outcome": outcome,
        "lower_token_arm": lower,
        "plain_minus_bugbank_tokens": safe_subtract(
            plain_tokens, bugbank_tokens, f"{record_id} token difference"
        ),
        "arms": {arm: dict(arms[arm]) for arm in ARMS},
    }


def validate_terminal(
    spec: SourceSpec,
    terminal_value: Any,
    report: Mapping[str, Any],
    record_id: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    terminal = require_object(terminal_value, f"{spec.key} terminal {record_id}")
    require(terminal.get("schema") == spec.terminal_schema,
            f"{spec.key} terminal {record_id} schema mismatch")
    require(terminal.get("run_id") == report["run_id"]
            and terminal.get("record_id") == record_id,
            f"{spec.key} terminal {record_id} identity mismatch")
    validate_payload_hash(terminal, "terminal_payload_sha256",
                          f"{spec.key} terminal {record_id}")
    if spec.key == "extension":
        return parse_extension_terminal(spec, terminal, record)
    return parse_standard_terminal(spec, terminal, record)


def aggregate_protocol(spec: SourceSpec, records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    counts = {name: 0 for name in
              ("BOTH_SOLVED", "BUGBANK_ONLY", "PLAIN_ONLY", "NEITHER_SOLVED")}
    lower = {name: 0 for name in ("BUGBANK", "PLAIN", "TIE")}
    for row in records:
        counts[row["outcome"]] += 1
        lower[row["lower_token_arm"]] += 1
    bugbank_solved = counts["BOTH_SOLVED"] + counts["BUGBANK_ONLY"]
    plain_solved = counts["BOTH_SOLVED"] + counts["PLAIN_ONLY"]
    bugbank_total = safe_add(
        (row["arms"]["bugbank"]["model_tokens_used"] for row in records),
        f"{spec.key} BugBank token total",
    )
    plain_total = safe_add(
        (row["arms"]["plain"]["model_tokens_used"] for row in records),
        f"{spec.key} plain token total",
    )
    return {
        "key": spec.key,
        "label": spec.label,
        "run_id": spec.run_root.name,
        "comparison_basis": spec.comparison_basis,
        "population_size": len(records),
        "outcomes": {
            "bugbank_solved": bugbank_solved,
            "plain_solved": plain_solved,
            "both_solved": counts["BOTH_SOLVED"],
            "bugbank_only": counts["BUGBANK_ONLY"],
            "plain_only": counts["PLAIN_ONLY"],
            "neither_solved": counts["NEITHER_SOLVED"],
        },
        "tokens": {
            "bugbank_total": bugbank_total,
            "plain_total": plain_total,
            "plain_minus_bugbank_total": safe_subtract(
                plain_total, bugbank_total, f"{spec.key} aggregate token difference"
            ),
            "lower_token_pairs": {
                "bugbank": lower["BUGBANK"],
                "plain": lower["PLAIN"],
                "ties": lower["TIE"],
            },
        },
        "records": list(records),
    }


def load_protocol(spec: SourceSpec) -> ProtocolResult:
    run_root = Path(os.path.abspath(spec.run_root))
    try:
        run_info = run_root.lstat()
    except OSError as error:
        raise RenderError(f"cannot stat {spec.key} run root {run_root}: {error}") from error
    require(stat.S_ISDIR(run_info.st_mode), f"{spec.key} run root is not a plain directory")
    report_value, report_snapshot = load_json_snapshot(run_root / spec.report_name)
    validator_snapshot = read_plain_file(spec.validator)
    adjusted = SourceSpec(**{**spec.__dict__, "run_root": run_root})
    report, roster, report_payload_sha = validate_report(
        adjusted, report_value, validator_snapshot
    )
    terminal_directory = run_root / spec.terminal_directory
    expected_names = frozenset(f"{record_id}.json" for record_id in roster)
    observed_names = plain_directory_names(terminal_directory)
    require(observed_names == expected_names,
            f"{spec.key} terminal inventory mismatch: "
            f"missing={sorted(expected_names - observed_names)}, "
            f"unexpected={sorted(observed_names - expected_names)}")
    records_by_id = report_records(adjusted, report)
    normalized: list[dict[str, Any]] = []
    terminal_sources: list[dict[str, Any]] = []
    snapshots: list[FileSnapshot] = [report_snapshot, validator_snapshot]
    for record_id in roster:
        terminal_value, terminal_snapshot = load_json_snapshot(
            terminal_directory / f"{record_id}.json"
        )
        snapshots.append(terminal_snapshot)
        normalized.append(validate_terminal(
            adjusted, terminal_value, report, record_id, records_by_id[record_id]
        ))
        terminal_sources.append({
            "record_id": record_id,
            "path": f"{spec.terminal_directory}/{record_id}.json",
            "size_bytes": terminal_snapshot.size,
            "sha256": terminal_snapshot.sha256,
            "terminal_payload_sha256": terminal_value["terminal_payload_sha256"],
        })

    protocol = aggregate_protocol(adjusted, normalized)
    if spec.key == "original":
        terminal_counts = require_object(
            report["terminal_counts"], "original report terminal_counts"
        )
        require_exact_keys(
            terminal_counts,
            {"arm_terminal", "audited_fixed_point",
             "verified_full_independent_audit", "iteration_cap"},
            "original report terminal_counts",
        )
        count_groups = {
            name: require_object(
                terminal_counts[name], f"original report terminal_counts.{name}"
            )
            for name in terminal_counts
        }
        for name, group in count_groups.items():
            require(set(group) == set(ARMS),
                    f"original report terminal_counts.{name} arm set mismatch")
            for arm in ARMS:
                require_count(
                    group[arm], f"original report terminal_counts.{name}.{arm}"
                )
        for arm in ARMS:
            require(count_groups["arm_terminal"][arm] == len(roster),
                    f"original report terminal count mismatch for {arm}")
            require(count_groups["verified_full_independent_audit"][arm]
                    == protocol["outcomes"][f"{arm}_solved"],
                    f"original report solved count mismatch for {arm}")
            require(count_groups["audited_fixed_point"][arm]
                    == len(roster) - protocol["outcomes"][f"{arm}_solved"],
                    f"original report fixed-point count mismatch for {arm}")
            require(count_groups["iteration_cap"][arm] == 0,
                    f"original report contains an iteration-cap endpoint for {arm}")
    elif spec.key == "hard":
        verified = require_object(report["counts"].get("verified_full"),
                                  "hard verified-full counts")
        require(set(verified) == set(ARMS)
                and all(require_count(verified[arm], f"hard verified_full.{arm}")
                        == protocol["outcomes"][f"{arm}_solved"]
                        for arm in ARMS),
                "hard report solved counts disagree with pair terminals")

    source = {
        "run_id": report["run_id"],
        "validation_report": {
            "path": spec.report_name,
            "size_bytes": report_snapshot.size,
            "sha256": report_snapshot.sha256,
            "report_payload_sha256": report_payload_sha,
        },
        "validator": {
            "path": f"qedbench_certificate_availability_triage/scripts/{spec.validator.name}",
            "sha256": validator_snapshot.sha256,
        },
        "pair_terminals": terminal_sources,
        "pair_terminal_set_payload_sha256": sha_bytes(canonical_bytes(terminal_sources)),
    }
    return ProtocolResult(
        result=protocol,
        source=source,
        snapshots=tuple(snapshots),
        terminal_directory=terminal_directory,
        terminal_names=expected_names,
    )


def default_specs(
    original_run: Path,
    hard_run: Path,
    extension_run: Path,
) -> tuple[SourceSpec, ...]:
    return (
        SourceSpec(
            key="original",
            label="Original open-problem run",
            run_root=original_run,
            report_name="validation_report.json",
            terminal_directory="pair_terminals",
            report_schema="open_frontier_paired_v2_validation_report_v1",
            terminal_schema="open_frontier_paired_v2_pair_terminal_v3",
            validator=SCRIPTS / "validate_open_frontier_paired_v2.py",
            comparison_basis="CUMULATIVE_ENDPOINT_MODEL_TOKENS",
            macro_prefix="pairedOriginal",
        ),
        SourceSpec(
            key="hard",
            label="Hard open-problem run",
            run_root=hard_run,
            report_name="VALIDATION_REPORT.json",
            terminal_directory="pair_terminals",
            report_schema="paired_open_problem_validation_report_v1",
            terminal_schema="paired_open_problem_pair_terminal_v1",
            validator=SCRIPTS / "validate_paired_open_problem_run.py",
            comparison_basis="CUMULATIVE_ENDPOINT_MODEL_TOKENS",
            macro_prefix="pairedHard",
        ),
        SourceSpec(
            key="extension",
            label="Fixed-point extension",
            run_root=extension_run,
            report_name="VALIDATION_REPORT.json",
            terminal_directory="terminals",
            report_schema="paired_open_problem_extension_validation_report_v1",
            terminal_schema="paired_open_problem_extension_pair_terminal_v1",
            validator=SCRIPTS / "validate_paired_open_problem_extension.py",
            comparison_basis="EXTENSION_INCREMENTAL_MODEL_TOKENS",
            macro_prefix="pairedExtension",
        ),
    )


def render_results(specs: Sequence[SourceSpec]) -> tuple[dict[str, Any], str, str]:
    require(tuple(spec.key for spec in specs) == ("original", "hard", "extension"),
            "renderer requires exactly original, hard, and extension sources in that order")
    try:
        loaded = [load_protocol(spec) for spec in specs]
        for item in loaded:
            require(plain_directory_names(item.terminal_directory) == item.terminal_names,
                    f"terminal inventory changed while rendering: {item.terminal_directory}")
            for snapshot in item.snapshots:
                snapshot.assert_unchanged()
    except RenderError:
        raise
    except (KeyError, TypeError, IndexError) as error:
        raise RenderError(f"malformed authoritative result input: {error}") from error
    protocols = [item.result for item in loaded]
    sources = [item.source for item in loaded]
    distinct_targets = aggregate_distinct_target_final_endpoints(protocols, sources)
    protocol_stages = aggregate_protocol_stage_observations(
        protocols, distinct_target_count=distinct_targets["target_count"]
    )
    unsigned: dict[str, Any] = {
        "schema": "paired_open_problem_paper_results_v3",
        "sources": {spec.key: item.source for spec, item in zip(specs, loaded)},
        "protocols": protocols,
        "distinct_target_final_endpoint_aggregate": distinct_targets,
        "protocol_stage_observation_aggregate": protocol_stages,
    }
    result = copy.deepcopy(unsigned)
    result["results_payload_sha256"] = sha_bytes(canonical_bytes(unsigned))
    macros = render_macros(result, specs)
    rows = render_rows(result, specs)
    return result, macros, rows


def outcome_totals(records: Iterable[Mapping[str, Any]], label: str) -> dict[str, int]:
    counts = {name: 0 for name in
              ("BOTH_SOLVED", "BUGBANK_ONLY", "PLAIN_ONLY", "NEITHER_SOLVED")}
    for record in records:
        outcome = record.get("outcome")
        require(outcome in counts, f"{label} contains an unknown outcome")
        counts[outcome] += 1
    return {
        "bugbank_solved": counts["BOTH_SOLVED"] + counts["BUGBANK_ONLY"],
        "plain_solved": counts["BOTH_SOLVED"] + counts["PLAIN_ONLY"],
        "both_solved": counts["BOTH_SOLVED"],
        "bugbank_only": counts["BUGBANK_ONLY"],
        "plain_only": counts["PLAIN_ONLY"],
        "neither_solved": counts["NEITHER_SOLVED"],
    }


def protocol_records_by_id(
    protocol: Mapping[str, Any], expected_key: str,
) -> dict[str, Mapping[str, Any]]:
    require(protocol.get("key") == expected_key,
            f"expected {expected_key} protocol in fixed protocol order")
    expected_size = EXPECTED_PROTOCOL_POPULATIONS[expected_key]
    require(protocol.get("population_size") == expected_size,
            f"{expected_key} protocol population must be exactly {expected_size}")
    records = protocol.get("records")
    require(type(records) is list and len(records) == expected_size,
            f"{expected_key} protocol record population mismatch")
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, value in enumerate(records):
        record = require_object(value, f"{expected_key} normalized record {index}")
        record_id = require_identifier(
            record.get("record_id"), f"{expected_key} normalized record ID"
        )
        require(record_id not in by_id,
                f"{expected_key} normalized records contain duplicate ID {record_id}")
        by_id[record_id] = record
    return by_id


def aggregate_distinct_target_final_endpoints(
    protocols: Sequence[Mapping[str, Any]],
    sources: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Construct the primary one-final-endpoint-per-source-target view.

    Every extension terminal replaces its corresponding original terminal;
    retaining both would double-count an outcome-selected continuation.
    """
    require(len(protocols) == 3 and len(sources) == 3,
            "distinct-target aggregate requires three protocol authorities")
    original = protocol_records_by_id(protocols[0], "original")
    hard = protocol_records_by_id(protocols[1], "hard")
    extension = protocol_records_by_id(protocols[2], "extension")
    original_ids = set(original)
    hard_ids = set(hard)
    extension_ids = set(extension)
    require(extension_ids <= original_ids,
            "extension record IDs must be a subset of original record IDs")
    eligible_original_ids = {
        record_id for record_id, record in original.items()
        if record.get("outcome") == "NEITHER_SOLVED"
    }
    require(
        extension_ids == eligible_original_ids,
        "extension roster must equal the outcome-selected original neither-"
        "audited-full roster: "
        f"missing={sorted(eligible_original_ids - extension_ids)}, "
        f"unexpected={sorted(extension_ids - eligible_original_ids)}",
    )
    require(not (original_ids & hard_ids),
            "hard record IDs overlap the original target roster")
    require(not (extension_ids & hard_ids),
            "hard record IDs overlap the extension target roster")
    unextended_ids = original_ids - extension_ids
    expected_unextended = (
        EXPECTED_PROTOCOL_POPULATIONS["original"]
        - EXPECTED_PROTOCOL_POPULATIONS["extension"]
    )
    require(len(unextended_ids) == expected_unextended,
            f"unextended original target count must be exactly {expected_unextended}")

    source_by_key = {
        protocol["key"]: source for protocol, source in zip(protocols, sources)
    }
    require(set(source_by_key) == set(EXPECTED_PROTOCOL_POPULATIONS),
            "source/protocol key set mismatch")
    extension_run_id = require_identifier(
        source_by_key["extension"].get("run_id"),
        "extension source run ID",
    )
    original_terminal_rows = source_by_key["original"].get("pair_terminals")
    require(type(original_terminal_rows) is list,
            "original pair-terminal source inventory is malformed")
    original_terminal_by_id: dict[str, Mapping[str, Any]] = {}
    for value in original_terminal_rows:
        row = require_object(value, "original pair-terminal source binding")
        record_id = require_identifier(
            row.get("record_id"), "original pair-terminal source record ID"
        )
        require(record_id not in original_terminal_by_id,
                f"duplicate original pair-terminal source binding {record_id}")
        original_terminal_by_id[record_id] = row
    require(set(original_terminal_by_id) == original_ids,
            "original pair-terminal source inventory disagrees with normalized records")

    final_records: list[dict[str, Any]] = []
    for record_id in sorted(original_ids):
        if record_id in extension:
            selected = extension[record_id]
            seed = require_object(
                selected.get("seed_pair_terminal"),
                f"extension seed binding for {record_id}",
            )
            original_binding = original_terminal_by_id[record_id]
            # EXTENSION_MANIFEST.json binds seeds with paths relative to the
            # extension run.  A validated extension pair terminal instead
            # carries validator.repo_artifact(...), whose path is relative to
            # the repository root.  This renderer consumes the latter.
            expected_seed_path = (
                Path("qedbench_certificate_availability_triage")
                / "runs"
                / extension_run_id
                / "seeds"
                / record_id
                / "pair_terminal.json"
            ).as_posix()
            require(
                seed.get("path") == expected_seed_path
                and seed.get("sha256") == original_binding.get("sha256")
                and seed.get("size_bytes") == original_binding.get("size_bytes"),
                f"extension seed does not bind the superseded original terminal for {record_id}",
            )
            source_protocol = "extension"
            supersedes_original = True
        else:
            selected = original[record_id]
            source_protocol = "original"
            supersedes_original = False
        final_records.append({
            "record_id": record_id,
            "endpoint_source_protocol": source_protocol,
            "supersedes_original_endpoint": supersedes_original,
            "outcome": selected["outcome"],
        })
    for record_id in sorted(hard_ids):
        final_records.append({
            "record_id": record_id,
            "endpoint_source_protocol": "hard",
            "supersedes_original_endpoint": False,
            "outcome": hard[record_id]["outcome"],
        })

    target_ids = {row["record_id"] for row in final_records}
    require(len(final_records) == len(target_ids) == EXPECTED_DISTINCT_TARGETS,
            f"distinct final-target population must be exactly {EXPECTED_DISTINCT_TARGETS}")
    outcomes = outcome_totals(final_records, "distinct-target aggregate")
    require(
        outcomes["both_solved"] + outcomes["bugbank_only"]
        + outcomes["plain_only"] + outcomes["neither_solved"]
        == EXPECTED_DISTINCT_TARGETS,
        "distinct-target outcome categories do not partition the target population",
    )
    return {
        "unit": "DISTINCT_SOURCE_TARGET_FINAL_ENDPOINT",
        "primary_scientific_view": True,
        "target_count": EXPECTED_DISTINCT_TARGETS,
        "outcomes": outcomes,
        "outcome_semantics": dict(OUTCOME_SEMANTICS),
        "supersession": {
            "extension_supersedes_original": True,
            "superseded_original_target_count": len(extension_ids),
            "unextended_original_target_count": len(unextended_ids),
            "hard_target_count": len(hard_ids),
        },
        "token_aggregation": "NOT_DEFINED_ACROSS_COMPONENT_ACCOUNTING_BASES",
        "records": final_records,
    }


def aggregate_protocol_stage_observations(
    protocols: Sequence[Mapping[str, Any]], *, distinct_target_count: int,
) -> dict[str, Any]:
    """Preserve the requested descriptive ledger of dependent run stages."""
    require(len(protocols) == 3,
            "protocol-stage aggregate requires three protocols")
    records_by_protocol = [
        protocol_records_by_id(protocol, key)
        for protocol, key in zip(protocols, ("original", "hard", "extension"))
    ]
    outcome_names = (
        "bugbank_solved", "plain_solved", "both_solved",
        "bugbank_only", "plain_only", "neither_solved",
    )
    observation_count = safe_add(
        (protocol["population_size"] for protocol in protocols),
        "protocol-stage observation count",
    )
    outcomes = {
        name: safe_add(
            (protocol["outcomes"][name] for protocol in protocols),
            f"confirmatory {name}",
        )
        for name in outcome_names
    }
    require(
        outcomes["both_solved"] + outcomes["bugbank_only"]
        + outcomes["plain_only"] + outcomes["neither_solved"]
        == observation_count,
        "protocol-stage outcome categories do not partition the observations",
    )
    require(
        outcomes["bugbank_solved"]
        == outcomes["both_solved"] + outcomes["bugbank_only"]
        and outcomes["plain_solved"]
        == outcomes["both_solved"] + outcomes["plain_only"],
        "protocol-stage solved counts disagree with outcome categories",
    )
    require(observation_count == sum(EXPECTED_PROTOCOL_POPULATIONS.values()),
            "protocol-stage observation count disagrees with frozen populations")
    require(distinct_target_count == EXPECTED_DISTINCT_TARGETS,
            "protocol-stage aggregate received the wrong distinct-target count")
    return {
        "unit": "PROTOCOL_STAGE_OBSERVATIONS",
        "observation_count": observation_count,
        "distinct_target_count": distinct_target_count,
        "dependent_observations": True,
        "descriptive_only": True,
        "components": {
            key: len(records)
            for key, records in zip(
                ("original", "hard", "extension"), records_by_protocol
            )
        },
        "outcomes": outcomes,
        "outcome_semantics": dict(OUTCOME_SEMANTICS),
        "dependence_reason": (
            "EXTENSION_OBSERVATIONS_CONTINUE_OUTCOME_SELECTED_ORIGINAL_TARGETS"
        ),
        "token_aggregation": "NOT_DEFINED_ACROSS_COMPONENT_ACCOUNTING_BASES",
    }


def macro_values(protocol: Mapping[str, Any]) -> tuple[tuple[str, int], ...]:
    outcomes = protocol["outcomes"]
    tokens = protocol["tokens"]
    lower = tokens["lower_token_pairs"]
    return (
        ("Pairs", protocol["population_size"]),
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


def render_macros(result: Mapping[str, Any], specs: Sequence[SourceSpec]) -> str:
    lines = [
        "% GENERATED by render_paired_open_problem_paper_results.py; do not edit.",
        f"% results_payload_sha256={result['results_payload_sha256']}",
    ]
    for spec, protocol in zip(specs, result["protocols"]):
        for suffix, value in macro_values(protocol):
            lines.append(f"\\newcommand{{\\{spec.macro_prefix}{suffix}}}{{{value}}}")
    targets = result["distinct_target_final_endpoint_aggregate"]
    target_outcomes = targets["outcomes"]
    target_values = (
        ("DistinctTargets", targets["target_count"]),
        ("TargetBugBankAuditedFull", target_outcomes["bugbank_solved"]),
        ("TargetPlainAuditedFull", target_outcomes["plain_solved"]),
        ("TargetBothAuditedFull", target_outcomes["both_solved"]),
        ("TargetBugBankOnlyAuditedFull", target_outcomes["bugbank_only"]),
        ("TargetPlainOnlyAuditedFull", target_outcomes["plain_only"]),
        ("TargetNeitherAuditedFull", target_outcomes["neither_solved"]),
        ("SupersededOriginalTargets",
         targets["supersession"]["superseded_original_target_count"]),
        ("UnextendedOriginalTargets",
         targets["supersession"]["unextended_original_target_count"]),
    )
    for suffix, value in target_values:
        lines.append(f"\\newcommand{{\\pairedConfirmatory{suffix}}}{{{value}}}")
    stages = result["protocol_stage_observation_aggregate"]
    stage_outcomes = stages["outcomes"]
    stage_values = (
        ("ProtocolStageObservations", stages["observation_count"]),
        ("ProtocolStageBugBankAuditedFull", stage_outcomes["bugbank_solved"]),
        ("ProtocolStagePlainAuditedFull", stage_outcomes["plain_solved"]),
        ("ProtocolStageBothAuditedFull", stage_outcomes["both_solved"]),
        ("ProtocolStageBugBankOnlyAuditedFull", stage_outcomes["bugbank_only"]),
        ("ProtocolStagePlainOnlyAuditedFull", stage_outcomes["plain_only"]),
        ("ProtocolStageNeitherAuditedFull", stage_outcomes["neither_solved"]),
    )
    for suffix, value in stage_values:
        lines.append(f"\\newcommand{{\\pairedConfirmatory{suffix}}}{{{value}}}")
    return "\n".join(lines) + "\n"


def render_rows(result: Mapping[str, Any], specs: Sequence[SourceSpec]) -> str:
    lines = [
        "% GENERATED by render_paired_open_problem_paper_results.py; do not edit.",
        f"% results_payload_sha256={result['results_payload_sha256']}",
    ]
    targets = result["distinct_target_final_endpoint_aggregate"]
    target_outcomes = targets["outcomes"]
    lines.append(
        f"Distinct targets (final endpoints; primary) & {targets['target_count']} & "
        f"{target_outcomes['bugbank_solved']}/{target_outcomes['plain_solved']} & "
        f"{target_outcomes['both_solved']} & "
        f"{target_outcomes['bugbank_only']}/{target_outcomes['plain_only']} & "
        f"{target_outcomes['neither_solved']} & -- & -- \\\\"
    )
    stages = result["protocol_stage_observation_aggregate"]
    stage_outcomes = stages["outcomes"]
    lines.append(
        f"Protocol-stage observations (descriptive) & {stages['observation_count']} & "
        f"{stage_outcomes['bugbank_solved']}/{stage_outcomes['plain_solved']} & "
        f"{stage_outcomes['both_solved']} & "
        f"{stage_outcomes['bugbank_only']}/{stage_outcomes['plain_only']} & "
        f"{stage_outcomes['neither_solved']} & -- & -- \\\\"
    )
    lines.append("\\addlinespace")
    for spec, protocol in zip(specs, result["protocols"]):
        outcomes = protocol["outcomes"]
        tokens = protocol["tokens"]
        lower = tokens["lower_token_pairs"]
        lines.append(
            f"{spec.label} & {protocol['population_size']} & "
            f"{outcomes['bugbank_solved']}/{outcomes['plain_solved']} & "
            f"{outcomes['both_solved']} & "
            f"{outcomes['bugbank_only']}/{outcomes['plain_only']} & "
            f"{outcomes['neither_solved']} & "
            f"{tokens['bugbank_total']}/{tokens['plain_total']} & "
            f"{lower['bugbank']}/{lower['plain']}/{lower['ties']} \\\\"
        )
    return "\n".join(lines) + "\n"


def output_bytes(result: Mapping[str, Any], macros: str, rows: str) -> dict[str, bytes]:
    return {
        OUTPUT_NAMES["json"]: json.dumps(
            result, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2
        ).encode("utf-8") + b"\n",
        OUTPUT_NAMES["macros"]: macros.encode("utf-8"),
        OUTPUT_NAMES["rows"]: rows.encode("utf-8"),
    }


def validate_output_directory(path: Path) -> Path:
    path = Path(os.path.abspath(path))
    try:
        info = path.lstat()
    except OSError as error:
        raise RenderError(f"output directory must already exist and be plain: {path}: {error}") from error
    require(stat.S_ISDIR(info.st_mode), f"output directory is not a plain directory: {path}")
    return path


def check_outputs(output_directory: Path, expected: Mapping[str, bytes]) -> None:
    directory = validate_output_directory(output_directory)
    for name, wanted in expected.items():
        snapshot = read_plain_file(directory / name)
        require(snapshot.data == wanted, f"stale generated file: {directory / name}")


def fsync_directory(directory: Path) -> None:
    descriptor = os.open(
        directory,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_outputs(output_directory: Path, expected: Mapping[str, bytes]) -> None:
    directory = validate_output_directory(output_directory)
    targets = {name: directory / name for name in expected}
    for target in targets.values():
        if os.path.lexists(target):
            info = target.lstat()
            require(stat.S_ISREG(info.st_mode), f"generated target is not a plain file: {target}")
    temporary: dict[str, Path] = {}
    try:
        for name in sorted(expected):
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{name}.", suffix=".tmp", dir=directory
            )
            temp_path = Path(temporary_name)
            temporary[name] = temp_path
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
        # The JSON file is the publication commit marker used by the LaTeX
        # all-or-none gate.  Withhold it while either TeX file can still be an
        # old/new mixture, then publish it only after both new TeX files are
        # durable.  A crash therefore leaves either the old complete set or a
        # deliberately non-renderable set without its marker.
        marker_name = OUTPUT_NAMES["json"]
        marker_target = targets[marker_name]
        if os.path.lexists(marker_target):
            os.unlink(marker_target)
            fsync_directory(directory)
        for name in sorted(name for name in expected if name != marker_name):
            os.replace(temporary.pop(name), targets[name])
        # Persist both TeX rename entries before the JSON commit marker can
        # become durable.  File-data fsync alone does not make a rename's
        # directory entry crash-durable.
        fsync_directory(directory)
        os.replace(temporary.pop(marker_name), marker_target)
        fsync_directory(directory)
    except OSError as error:
        raise RenderError(f"cannot publish generated outputs: {error}") from error
    finally:
        for temp_path in temporary.values():
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--original-run", type=Path,
        default=RUNS / "open_frontier_paired_v2_20260901",
    )
    parser.add_argument(
        "--hard-run", type=Path,
        default=RUNS / "open_frontier_paired_hard_v1_20260903",
    )
    parser.add_argument(
        "--extension-run", type=Path,
        default=RUNS / "open_frontier_paired_v2_fixed_point_extension_v3_20260903",
    )
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    parser.add_argument("--check", action="store_true",
                        help="validate sources and require byte-identical generated outputs")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        specs = default_specs(
            arguments.original_run, arguments.hard_run, arguments.extension_run
        )
        result, macros, rows = render_results(specs)
        expected = output_bytes(result, macros, rows)
        if arguments.check:
            check_outputs(arguments.output_directory, expected)
        else:
            write_outputs(arguments.output_directory, expected)
    except RenderError as error:
        print(f"ERROR: {error}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
