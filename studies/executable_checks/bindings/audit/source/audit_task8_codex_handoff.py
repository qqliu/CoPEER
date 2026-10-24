#!/usr/bin/env python3
"""Independent, fail-closed cold audit and summary builder for Task 8.

This program makes no model calls and never imports either Task-8 runner.  It
reads the frozen population and the durable results, copies executable twins
to temporary directories for re-execution, and writes CODEX_HANDOFF_SUMMARY.md
only after every structural, provenance, static, dynamic, and stability check
passes.  A partial or changing tree is reported as PARTIAL and is not written.

The sixteen pre-handoff Fable searches are a documented compatibility cohort:
their result ``test_path`` is the canonical absolute path and their programs
print deterministic human-readable reports.  Every post-handoff Codex search
and every Codex verification has the new closed schema, canonical relative
path, exact JSON stdout, and a one-to-one PUBLISHED attempt manifest proving
``gpt-5.6-sol`` with ``reasoning_mode=pro``.
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent.parent
REPO = BASE.parent
RUN = BASE / "runs/code_twin"
PROGRAMS = REPO / "partB_feasibility/code_twins"
ALGO_OUT = BASE / "outputs_algo_tests"
ALGO_PROGRAMS = REPO / "partB_feasibility/algorithm_tests"
SUMMARY = RUN / "CODEX_HANDOFF_SUMMARY.md"

MODEL = "gpt-5.6-sol"
REASONING_MODE = "pro"
CODEX_ALLOWED_EFFORTS = {"high", "xhigh"}
ALGO_VERIFY_EFFORT = "xhigh"

POPULATION_SIZE = 604
PRE_AMENDMENT_POPULATION_SIZE = 566
POPULATION_SHA256 = "19fc28acac09c5c140b498c8981401795b2f16714c6db61331d35e27bd091604"
HANDOFF_GAP_SHA256 = "b1300000b821766763dd58071f6aecde8ddef9612ecd9aeb6ce90f37f17f9844"

SEARCH_KEYS = {
    "record_id",
    "outcome",
    "test_path",
    "witness_description",
    "refutation_explanation",
    "search_space",
}
SEARCH_STDOUT_KEYS = SEARCH_KEYS - {"test_path"}
VERIFY_KEYS = {"record_id", "verdict", "notes"}
SEARCH_OUTCOMES = (
    "WITNESS_FOUND",
    "NO_WITNESS_EXHAUSTIVE",
    "NO_WITNESS_INCONCLUSIVE",
    "CLAIM_NOT_FINITELY_REFUTABLE",
)
VERIFY_VERDICTS = (
    "CONFIRMED",
    "REFUTED_WITNESS_INVALID",
    "CANNOT_REPRODUCE",
)

PART1_CODEX_IDS = (
    "Algorithms_11__sol1",
    "Algorithms_11__sol4",
    "Algorithms_11__sol5",
    "Algorithms_21__sol1",
    "Algorithms_21__sol3",
    "Algorithms_21__sol4",
    "Algorithms_21__sol5",
    "Algorithms_27__sol3",
    "Algorithms_27__sol5",
    "Algorithms_28__sol5",
    "Algorithms_33__sol3",
    "Algorithms_33__sol4",
    "Algorithms_36__sol5",
    "Algorithms_43__sol5",
)
PART1_LEGACY_IDS = ("Algorithms_10__sol5", "Algorithms_11__sol3")
PART1_IDS = tuple(sorted(PART1_CODEX_IDS + PART1_LEGACY_IDS))
PART1_SEARCH_OUTCOMES = {"BUG_FOUND", "BOUND_VIOLATION_FOUND"}
PART1_VERIFY_VERDICTS = {
    "CONFIRMED",
    "REFUTED_TEST_INVALID",
    "CANNOT_REPRODUCE",
}
PART1_SEARCH_CORE_KEYS = {
    "record_id",
    "outcome",
    "claim_kind",
    "target_claim",
    "test_path",
    "failing_input",
    "observed_vs_claimed",
    "faithfulness_notes",
}
PART1_SEARCH_EXTRAS = {
    "Algorithms_11__sol3": {"notes"},
    "Algorithms_21__sol5": {"test_output_summary", "confidence"},
    "Algorithms_27__sol3": {"verdict_printed", "run_summary"},
}
PART1_LEGACY_VERIFY_KEYS = {
    "Algorithms_10__sol5": {
        "caveats",
        "claim_kind",
        "flaws_hunted_in_their_test",
        "independent_check",
        "record_id",
        "refuted_claim",
        "reported_test_path",
        "substantive_or_typo",
        "substantive_rationale",
        "verdict",
        "verified_by",
        "verifier_oracle_path",
    },
    "Algorithms_11__sol3": {
        "claim_kind",
        "flaw_hunt_on_reported_test",
        "independent_reproduction",
        "notes",
        "record_id",
        "root_cause",
        "target_claim",
        "typo_or_substantive",
        "verdict",
        "verifier_oracle_path",
    },
}

FABLE_BASELINE_IDS = (
    "Algorithms_10__sol4",
    "Algorithms_10__sol5",
    "Algorithms_11__sol3",
    "Algorithms_11__sol5",
    "Algorithms_12__sol4",
    "Algorithms_14__sol4",
    "Algorithms_17__sol2",
    "Algorithms_17__sol4",
    "Algorithms_17__sol5",
    "Algorithms_18__sol4",
    "Algorithms_18__sol5",
    "Algorithms_19__sol2",
    "Algorithms_19__sol3",
    "Algorithms_19__sol4",
    "Algorithms_19__sol5",
    "Algorithms_21__sol5",
)
FABLE_WITNESS_IDS = (
    "Algorithms_11__sol5",
    "Algorithms_14__sol4",
    "Algorithms_18__sol4",
    "Algorithms_18__sol5",
    "Algorithms_19__sol3",
    "Algorithms_19__sol5",
    "Algorithms_21__sol5",
)

# These bytes were already durable at the frozen Task-8 handoff.  Pinning both
# the result and program prevents a later Codex batch from silently rewriting
# or being credited for the legacy Fable baseline.
FABLE_BASELINE_SHA256 = {
    "Algorithms_10__sol4": ("69cd55592b1aa8de69a351067041e6feb3a40100204d4131e8c0ba5d553e93ef", "f21f2ed23e8d4db91b4ed5f5059884222d7b5c19b34313d73047d09b4fbd0994"),
    "Algorithms_10__sol5": ("2a9ece15ea98d9db0f143863790f7f6f2bd13ea27dbd7a335353912a0bdb2c04", "af35d9bb228ff5519553aa06c216b03c7bec699474b6513ab01246e189bd6ead"),
    "Algorithms_11__sol3": ("593753b53d1c683ced38b6680dfd04fe94c39402f5c3eb37e69b7d155e22c038", "af5d96dcda1b9ec4c853445e8e04cb6763a6c0265938c1f4e49d19e4127e6806"),
    "Algorithms_11__sol5": ("e2fb583f52217c80d2d4da35c2eedb1893b7a56326f1ba4efd00d39f9ad33a73", "c1c49ab81d0d911f322c0011c4d7f3404376442beb16988b33f5b439c5a40e96"),
    "Algorithms_12__sol4": ("2353abcc7bd8d0765eb00d8e4719748a6af2e810ec3714912a3cb4015c73beb0", "13480882b37e83f8b467df7799bd7c8929f9f39738d4c64661818646e83cc868"),
    "Algorithms_14__sol4": ("fa5b799aa9a7500b678bff06408bc039dab6de24f58a722003c2fae52d2ceed0", "723753135bb45cd6fafdc196e6010c9074414378693b8ed0d6717628e3076049"),
    "Algorithms_17__sol2": ("2021eaa381ea0330b89f63477de46073fc0bdf4c4c830d566d0e569bf1bd2acf", "daecbbc0e1e8c7fed0a4488ca806e2124e39cd164e451f1e959f0b992b9277a0"),
    "Algorithms_17__sol4": ("77e389f151a8d6072d1895259d22b458a72d554e704128019cc08193758a7183", "c881c1350cce0845993ea800dfb1f9d7be0bd4e4422ae185c5e32ceda00b65f6"),
    "Algorithms_17__sol5": ("ac876977e18751e7b7a21fc21705b5d0406ac4217928763c111bb5338c20c38e", "8c0f03ad8b7377ca37d29c7fdc4f28fc1a8ac8d5cc6750ac67b79c4e9b85c7f8"),
    "Algorithms_18__sol4": ("1781e97e27e49ac443944a1e41778d3f373a23f91f41dd9acb64322a014d4318", "3a90903265c465d6630fc0b2a57319fdef4cb94c0115fa8e704b21d67857dda3"),
    "Algorithms_18__sol5": ("4da7f75631d8ee60756ab91f86cb2bd5c969c3f56718bfbe1b989f7948578190", "d88d8135350c7e55e82aab4eb79c1201c54fed0653edb1118f11a9b62cfc9aeb"),
    "Algorithms_19__sol2": ("720ff47088212ea2245166f197e92d6297a8486b6300510d59b1a8ba3eb3180b", "d7bcb377037ab386baed45bc5a8004aca036d1e4f7f982dd845ffe2cbd2bf030"),
    "Algorithms_19__sol3": ("977d6c76ef5b1f5a9b16c6f3e18177ca509922052bfa42597af75de9de1b708e", "58278b8fed786176b13d01518fc3cff77c12121c006bbf5fa87248613bb05f7b"),
    "Algorithms_19__sol4": ("d30ac82be4b5b6e1b343dc6e73b0ab94b0193fdd45d659c9509215117df1429c", "b7e77f0eaf05b9d996269fec170ef3d64e74e33ab90a0625aad486433516e34a"),
    "Algorithms_19__sol5": ("def0937b633ba8c75dd659ae75dafb5a8ba5649af9e4e6248b56625adfcc55a1", "504d6541f682fe67dd4e68856e5b653380e30c2f7458935da6ad9bea7168d78c"),
    "Algorithms_21__sol5": ("1e92a88f81035393e5dbd72a3ac54ba32b8896191cfe7cf3be0fcc6786f6be2c", "446cbd109bcfe6b0f04736a0d53a31a254a7ba7f3cf75fb2f1510ba87979d38b"),
}

ATTEMPT_KEYS = {
    "record_id",
    "stage",
    "executor",
    "reasoning_mode",
    "reasoning_effort",
    "ephemeral",
    "model_tools_disabled",
    "sandbox",
    "started_at",
    "finished_at",
    "status",
    "detail",
}
FINAL_ATTEMPT_STATUSES = {"PUBLISHED", "FAILED", "SKIPPED_DISK_RACE"}
ATTEMPT_NAME = re.compile(r"attempt_[0-9]+_[0-9]+_[0-9]+\.json\Z")

EXACT_MATH_NAMES = {"comb", "factorial", "gcd", "isqrt", "lcm", "perm", "prod"}
BANNED_IMPORT_ROOTS = {
    "asyncio", "builtins", "cmath", "concurrent", "ctypes", "datetime",
    "dbm", "decimal", "ftplib", "http", "importlib", "io", "marshal",
    "multiprocessing", "os", "pathlib", "pickle", "platform", "random",
    "resource", "runpy", "secrets", "shelve", "shutil", "signal", "site",
    "smtplib", "socket", "sqlite3", "statistics", "subprocess", "tempfile",
    "threading", "time", "urllib", "uuid", "webbrowser",
}
BANNED_CALL_NAMES = {
    "__import__", "breakpoint", "compile", "complex", "eval", "exec",
    "float", "hash", "input", "open", "pow", "round",
}
MAX_OUTPUT_BYTES = 1_000_000


class AuditError(RuntimeError):
    pass


def fn_for(record_id: str) -> str:
    value = record_id.replace(" ", "_").replace("/", "_")
    if not value or value in {".", ".."} or Path(value).name != value or "\x00" in value:
        raise AuditError(f"unsafe filename mapping for {record_id!r}")
    return value


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def strict_json_loads(text: str, label: str) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise AuditError(f"{label}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    def no_constant(value: str) -> None:
        raise AuditError(f"{label}: non-standard JSON number {value}")

    try:
        return json.loads(
            text,
            object_pairs_hook=no_duplicates,
            parse_constant=no_constant,
        )
    except AuditError:
        raise
    except (json.JSONDecodeError, UnicodeError, TypeError) as exc:
        raise AuditError(f"{label}: invalid JSON: {exc}") from exc


def regular_bytes(path: Path) -> bytes:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise AuditError(f"cannot stat {path}: {exc}") from exc
    if not stat.S_ISREG(mode) or path.is_symlink():
        raise AuditError(f"not a regular non-symlink file: {path}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc}") from exc


def read_json(path: Path) -> Any:
    data = regular_bytes(path)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError(f"{path}: not UTF-8: {exc}") from exc
    return strict_json_loads(text, str(path))


def read_jsonl(path: Path) -> list[tuple[dict[str, Any], bytes]]:
    try:
        with path.open("rb") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
            try:
                data = stream.read()
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc}") from exc
    if path.is_symlink() or not path.is_file():
        raise AuditError(f"not a regular non-symlink file: {path}")
    if data and not data.endswith(b"\n"):
        raise AuditError(f"{path}: JSONL lacks final LF")
    rows: list[tuple[dict[str, Any], bytes]] = []
    for number, raw in enumerate(data.splitlines(keepends=True), 1):
        if not raw.endswith(b"\n") or raw.endswith(b"\r\n"):
            raise AuditError(f"{path}:{number}: require canonical LF line ending")
        body = raw[:-1]
        if not body:
            raise AuditError(f"{path}:{number}: blank JSONL row")
        try:
            value = strict_json_loads(body.decode("utf-8"), f"{path}:{number}")
        except UnicodeDecodeError as exc:
            raise AuditError(f"{path}:{number}: not UTF-8: {exc}") from exc
        if not isinstance(value, dict):
            raise AuditError(f"{path}:{number}: JSONL row is not an object")
        rows.append((value, raw))
    return rows


def parse_time(value: Any, label: str) -> dt.datetime:
    if not isinstance(value, str) or not value:
        raise AuditError(f"{label}: timestamp is not a nonempty string")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuditError(f"{label}: invalid ISO-8601 timestamp {value!r}") from exc
    if parsed.tzinfo is None:
        raise AuditError(f"{label}: timestamp lacks timezone")
    return parsed.astimezone(dt.timezone.utc)


def canonical_repo_path(relative: str, label: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise AuditError(f"{label}: noncanonical repository-relative path {relative!r}")
    path = REPO / candidate
    try:
        path.relative_to(REPO)
    except ValueError as exc:
        raise AuditError(f"{label}: path escapes repository") from exc
    if path.exists() and path.resolve() != path:
        raise AuditError(f"{label}: symlinked/noncanonical path component")
    return path


@dataclass
class Audit:
    issues: list[str] = field(default_factory=list)

    def issue(self, message: str) -> None:
        if message not in self.issues:
            self.issues.append(message)

    def check(self, condition: bool, message: str) -> bool:
        if not condition:
            self.issue(message)
        return condition

    def capture(self, label: str, function: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except Exception as exc:
            self.issue(f"{label}: {exc}")
            return None


def inventory_json(directory: Path) -> dict[str, Path]:
    if not directory.is_dir() or directory.is_symlink():
        raise AuditError(f"missing/noncanonical directory: {directory}")
    result: dict[str, Path] = {}
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.name.startswith("."):
            continue
        if not path.is_file() or path.is_symlink() or path.suffix != ".json":
            raise AuditError(f"unexpected artifact in {directory}: {path.name}")
        result[path.name] = path
    return result


def validate_string_object(
    payload: Any,
    keys: set[str],
    label: str,
    enum_key: str,
    enum: tuple[str, ...] | set[str],
) -> bool:
    if not isinstance(payload, dict) or set(payload) != keys:
        got = sorted(payload) if isinstance(payload, dict) else type(payload).__name__
        raise AuditError(f"{label}: closed-schema keys mismatch: {got}")
    for key in keys:
        if type(payload[key]) is not str or not payload[key].strip():
            raise AuditError(f"{label}: {key} must be a nonempty string")
    if payload[enum_key] not in enum:
        raise AuditError(f"{label}: invalid {enum_key} {payload[enum_key]!r}")
    return True


def static_exact_check(
    source: str,
    record_id: str,
    leaf: str,
    target_claim: str | None,
    *,
    codex_schema: bool,
) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        try:
            tree = ast.parse(source, filename=f"{record_id}/{leaf}")
        except SyntaxError as exc:
            raise AuditError(f"{record_id}/{leaf}: Python syntax error: {exc}") from exc
    if target_claim is not None:
        docstring = ast.get_docstring(tree, clean=False)
        if docstring is None or target_claim not in docstring:
            raise AuditError(f"{record_id}/{leaf}: module docstring lacks exact target_claim")

    math_aliases: set[str] = set()
    fractions_aliases: set[str] = set()
    sys_aliases: set[str] = set()
    stdlib = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in stdlib or root in BANNED_IMPORT_ROOTS:
                    raise AuditError(f"{record_id}/{leaf}: forbidden/non-stdlib import {alias.name!r}")
                if codex_schema and root not in {
                    "bisect", "collections", "fractions", "functools",
                    "heapq", "itertools", "json", "math",
                }:
                    raise AuditError(f"{record_id}/{leaf}: import outside Codex exact whitelist {root!r}")
                if root == "math":
                    math_aliases.add(alias.asname or "math")
                if root == "fractions":
                    fractions_aliases.add(alias.asname or "fractions")
                if root == "sys":
                    sys_aliases.add(alias.asname or "sys")
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise AuditError(f"{record_id}/{leaf}: relative import is forbidden")
            root = (node.module or "").split(".", 1)[0]
            if root not in stdlib or root in BANNED_IMPORT_ROOTS:
                raise AuditError(f"{record_id}/{leaf}: forbidden/non-stdlib from-import {node.module!r}")
            if codex_schema and root not in {
                "bisect", "collections", "fractions", "functools",
                "heapq", "itertools", "json", "math",
            }:
                raise AuditError(f"{record_id}/{leaf}: from-import outside Codex exact whitelist {root!r}")
            if root == "math" and any(
                alias.name not in EXACT_MATH_NAMES for alias in node.names
            ):
                raise AuditError(f"{record_id}/{leaf}: non-exact math from-import")
            if root == "fractions" and any(
                alias.name != "Fraction" for alias in node.names
            ):
                raise AuditError(f"{record_id}/{leaf}: only fractions.Fraction is allowed")
        elif isinstance(node, ast.Constant) and type(node.value) in (float, complex):
            raise AuditError(f"{record_id}/{leaf}: float/complex literal at line {node.lineno}")
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            raise AuditError(f"{record_id}/{leaf}: true division at line {node.lineno}")
        elif (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Pow)
            and isinstance(node.right, ast.UnaryOp)
            and isinstance(node.right.op, ast.USub)
        ):
            raise AuditError(f"{record_id}/{leaf}: explicit negative exponent")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in BANNED_CALL_NAMES:
                raise AuditError(f"{record_id}/{leaf}: forbidden call {node.func.id} at line {node.lineno}")
        elif isinstance(node, ast.Name):
            if node.id.startswith("__") and node.id != "__name__":
                raise AuditError(f"{record_id}/{leaf}: forbidden dunder name {node.id!r}")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                raise AuditError(f"{record_id}/{leaf}: forbidden dunder attribute {node.attr!r}")
            if isinstance(node.value, ast.Name) and node.value.id in math_aliases:
                if node.attr not in EXACT_MATH_NAMES:
                    raise AuditError(f"{record_id}/{leaf}: non-exact math attribute {node.attr!r}")
            if isinstance(node.value, ast.Name) and node.value.id in fractions_aliases:
                if node.attr != "Fraction":
                    raise AuditError(f"{record_id}/{leaf}: non-Fraction fractions attribute {node.attr!r}")
            if isinstance(node.value, ast.Name) and node.value.id in sys_aliases:
                if node.attr != "exit":
                    raise AuditError(f"{record_id}/{leaf}: nondeterministic sys attribute {node.attr!r}")
        elif isinstance(node, (ast.AsyncFunctionDef, ast.Await)):
            raise AuditError(f"{record_id}/{leaf}: async execution is forbidden")


def arg_value(argv: list[Any], flag: str, label: str) -> str:
    positions = [index for index, value in enumerate(argv) if value == flag]
    if len(positions) != 1 or positions[0] + 1 >= len(argv):
        raise AuditError(f"{label}: expected exactly one {flag}")
    value = argv[positions[0] + 1]
    if not isinstance(value, str):
        raise AuditError(f"{label}: non-string value after {flag}")
    return value


def validate_algo_invocation(argv: Any, record_id: str) -> Path:
    label = f"Part1 invocation {record_id}"
    if not isinstance(argv, list) or any(type(value) is not str for value in argv):
        raise AuditError(f"{label}: argv is not a string list")
    if argv[:2] != ["codex", "exec"] or argv[-1:] != ["-"]:
        raise AuditError(f"{label}: unexpected Codex command envelope")
    for flag in ("--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check"):
        if argv.count(flag) != 1:
            raise AuditError(f"{label}: missing/duplicate {flag}")
    if arg_value(argv, "--model", label) != MODEL:
        raise AuditError(f"{label}: model is not {MODEL}")
    if arg_value(argv, "--sandbox", label) != "workspace-write":
        raise AuditError(f"{label}: unexpected sandbox")
    configs = [argv[index + 1] for index, item in enumerate(argv[:-1]) if item == "-c"]
    if configs.count('reasoning.mode="pro"') != 1:
        raise AuditError(f"{label}: missing explicit reasoning.mode=pro")
    if configs.count('model_reasoning_effort="xhigh"') != 1:
        raise AuditError(f"{label}: missing explicit xhigh effort")
    expected_root = REPO / ".task8_algo_verify_stage_pro" / fn_for(record_id)
    cd_path = Path(arg_value(argv, "--cd", label))
    schema_path = Path(arg_value(argv, "--output-schema", label))
    response_path = Path(arg_value(argv, "--output-last-message", label))
    if cd_path != expected_root / "context":
        raise AuditError(f"{label}: context path is not record-isolated")
    if schema_path != expected_root / "envelope_schema.json":
        raise AuditError(f"{label}: schema path is not record-isolated")
    if response_path != expected_root / "last_message.json":
        raise AuditError(f"{label}: response path is not record-isolated")
    return cd_path


def validate_part1(audit: Audit) -> dict[str, Any]:
    result: dict[str, Any] = {"searches": {}, "verifies": {}, "log_rows": []}
    search_inventory = audit.capture("Part1 search inventory", inventory_json, ALGO_OUT / "test_search")
    verify_inventory = audit.capture("Part1 verify inventory", inventory_json, ALGO_OUT / "test_verify")
    expected_names = {f"{fn_for(record_id)}.json" for record_id in PART1_IDS}
    if search_inventory is None or verify_inventory is None:
        return result
    audit.check(set(search_inventory) == expected_names, "Part1 search file set is not exact 16/16")
    audit.check(set(verify_inventory) == expected_names, "Part1 verify file set is not exact 16/16")

    for record_id in PART1_IDS:
        fn = fn_for(record_id)
        search_path = search_inventory.get(f"{fn}.json")
        verify_path = verify_inventory.get(f"{fn}.json")
        program_dir = ALGO_PROGRAMS / fn
        test_path = program_dir / "test.py"
        oracle_path = program_dir / "verify_oracle.py"
        if not test_path.is_file() or test_path.is_symlink():
            audit.issue(f"Part1 {record_id}: missing canonical test.py")
        if not oracle_path.is_file() or oracle_path.is_symlink():
            audit.issue(f"Part1 {record_id}: missing canonical verify_oracle.py")
        else:
            source_bytes = audit.capture(f"Part1 {record_id} oracle read", regular_bytes, oracle_path)
            if source_bytes is not None:
                try:
                    source = source_bytes.decode("utf-8")
                    static_exact_check(source, record_id, "verify_oracle.py", None, codex_schema=False)
                except Exception as exc:
                    audit.issue(f"Part1 {record_id} oracle static audit: {exc}")

        if search_path is not None:
            payload = audit.capture(f"Part1 search {record_id}", read_json, search_path)
            if isinstance(payload, dict):
                expected_keys = PART1_SEARCH_CORE_KEYS | PART1_SEARCH_EXTRAS.get(record_id, set())
                if set(payload) != expected_keys:
                    audit.issue(f"Part1 search {record_id}: undocumented legacy keys {sorted(payload)}")
                elif (
                    payload.get("record_id") != record_id
                    or payload.get("outcome") not in PART1_SEARCH_OUTCOMES
                    or payload.get("test_path") != str(test_path)
                ):
                    audit.issue(f"Part1 search {record_id}: ID/outcome/canonical path mismatch")
                else:
                    for key in PART1_SEARCH_CORE_KEYS:
                        if type(payload.get(key)) is not str or not payload[key].strip():
                            audit.issue(f"Part1 search {record_id}: invalid core field {key}")
                    result["searches"][record_id] = payload

        if verify_path is not None:
            payload = audit.capture(f"Part1 verify {record_id}", read_json, verify_path)
            if isinstance(payload, dict):
                expected_keys = (
                    VERIFY_KEYS if record_id in PART1_CODEX_IDS
                    else PART1_LEGACY_VERIFY_KEYS[record_id]
                )
                if set(payload) != expected_keys:
                    audit.issue(f"Part1 verify {record_id}: schema keys mismatch {sorted(payload)}")
                elif payload.get("record_id") != record_id or payload.get("verdict") not in PART1_VERIFY_VERDICTS:
                    audit.issue(f"Part1 verify {record_id}: ID/verdict mismatch")
                else:
                    if record_id in PART1_CODEX_IDS:
                        try:
                            validate_string_object(payload, VERIFY_KEYS, f"Part1 verify {record_id}", "verdict", PART1_VERIFY_VERDICTS)
                        except Exception as exc:
                            audit.issue(str(exc))
                    else:
                        if payload.get("verifier_oracle_path") != str(oracle_path):
                            audit.issue(f"Part1 verify {record_id}: legacy oracle path is noncanonical")
                    result["verifies"][record_id] = payload

    search_counts = Counter(row["outcome"] for row in result["searches"].values())
    audit.check(search_counts == Counter({"BUG_FOUND": 12, "BOUND_VIOLATION_FOUND": 4}), f"Part1 search outcomes mismatch: {dict(search_counts)}")

    log_path = ALGO_OUT / "CODEX_COMPLETION_LOG.jsonl"
    log_rows = audit.capture("Part1 provenance", read_jsonl, log_path)
    parsed_rows: list[dict[str, Any]] = []
    if log_rows is not None:
        for number, (row, _raw) in enumerate(log_rows, 1):
            if set(row) != {"record_id", "stage", "executor", "ts"}:
                audit.issue(f"Part1 provenance line {number}: closed schema mismatch")
                continue
            if row.get("stage") != "verify" or row.get("executor") != MODEL:
                audit.issue(f"Part1 provenance line {number}: executor/stage mismatch")
            audit.capture(f"Part1 provenance line {number} timestamp", parse_time, row.get("ts"), str(log_path))
            parsed_rows.append(row)
        pairs = [(row.get("record_id"), row.get("stage")) for row in parsed_rows]
        audit.check(len(pairs) == len(set(pairs)), "Part1 provenance contains duplicate completion rows")
        audit.check(set(pairs) == {(record_id, "verify") for record_id in PART1_CODEX_IDS}, "Part1 provenance is not exact Codex 14-record completion set")
        result["log_rows"] = log_rows

    manifest_path = ALGO_OUT / "codex_invocation_provenance/task8_part1_algo_verify.json"
    manifest = audit.capture("Part1 invocation manifest", read_json, manifest_path)
    if isinstance(manifest, dict):
        expected_top = {
            "schema_version", "description", "record_count", "accepted_executor",
            "acceptance_policy", "hash_algorithm", "hash_conventions",
            "sanitization", "records",
        }
        audit.check(set(manifest) == expected_top, "Part1 invocation manifest top-level schema mismatch")
        audit.check(manifest.get("schema_version") == 1 and manifest.get("record_count") == 14, "Part1 invocation manifest count/version mismatch")
        audit.check(manifest.get("accepted_executor") == {
            "model": MODEL,
            "reasoning_mode": REASONING_MODE,
            "model_reasoning_effort": ALGO_VERIFY_EFFORT,
        }, "Part1 invocation manifest executor is not gpt-5.6-sol/pro/xhigh")
        audit.check(manifest.get("acceptance_policy") == {
            "reject_nonmatching_model": True,
            "reject_non_pro_reasoning_mode": True,
            "reject_nonmatching_reasoning_effort": True,
            "required_argv_values": [
                "--model gpt-5.6-sol",
                '-c reasoning.mode="pro"',
                '-c model_reasoning_effort="xhigh"',
            ],
        }, "Part1 invocation manifest acceptance policy does not fail closed on Pro")
        audit.check(manifest.get("hash_algorithm") == "SHA-256", "Part1 invocation manifest hash algorithm mismatch")
        records = manifest.get("records")
        if not isinstance(records, list):
            audit.issue("Part1 invocation manifest records is not a list")
        else:
            ids = [row.get("record_id") for row in records if isinstance(row, dict)]
            audit.check(len(records) == 14 and len(ids) == len(set(ids)) and set(ids) == set(PART1_CODEX_IDS), "Part1 invocation manifest is not exact unique Codex 14-record set")
            contexts: set[Path] = set()
            for row in records:
                if not isinstance(row, dict) or set(row) != {"record_id", "result", "invocation", "artifacts"}:
                    audit.issue("Part1 invocation record closed schema mismatch")
                    continue
                record_id = row.get("record_id")
                if record_id not in PART1_CODEX_IDS:
                    continue
                invocation = row.get("invocation")
                artifacts = row.get("artifacts")
                if not isinstance(invocation, dict) or set(invocation) != {
                    "model", "reasoning_mode", "model_reasoning_effort",
                    "completed_at", "codex_exec_argv",
                }:
                    audit.issue(f"Part1 {record_id}: invocation schema mismatch")
                    continue
                if (
                    invocation.get("model") != MODEL
                    or invocation.get("reasoning_mode") != REASONING_MODE
                    or invocation.get("model_reasoning_effort") != ALGO_VERIFY_EFFORT
                ):
                    audit.issue(f"Part1 {record_id}: published invocation is not gpt-5.6-sol/pro/xhigh")
                audit.capture(f"Part1 {record_id} completed_at", parse_time, invocation.get("completed_at"), record_id)
                context = audit.capture(f"Part1 {record_id} argv", validate_algo_invocation, invocation.get("codex_exec_argv"), record_id)
                if isinstance(context, Path):
                    if context in contexts:
                        audit.issue(f"Part1 {record_id}: reused Codex context {context}")
                    contexts.add(context)
                if row.get("result") != result["verifies"].get(record_id):
                    audit.issue(f"Part1 {record_id}: manifest result differs from durable verdict")
                if not isinstance(artifacts, dict) or set(artifacts) != {
                    "checker", "verdict_json", "completion_log_row",
                    "staged_invocation_metadata", "host_recheck_output",
                }:
                    audit.issue(f"Part1 {record_id}: artifact manifest schema mismatch")
                    continue
                expected_artifact_paths = {
                    "checker": f"partB_feasibility/algorithm_tests/{fn_for(record_id)}/verify_oracle.py",
                    "verdict_json": f"qedbench_certificate_availability_triage/outputs_algo_tests/test_verify/{fn_for(record_id)}.json",
                }
                for name, expected_relative in expected_artifact_paths.items():
                    item = artifacts.get(name)
                    if not isinstance(item, dict) or set(item) != {"path", "sha256_exact_file_bytes"}:
                        audit.issue(f"Part1 {record_id}: malformed {name} artifact")
                        continue
                    if not is_sha256(item.get("sha256_exact_file_bytes")):
                        audit.issue(f"Part1 {record_id}: malformed {name} SHA-256")
                        continue
                    if item.get("path") != expected_relative:
                        audit.issue(f"Part1 {record_id}: noncanonical {name} path")
                        continue
                    artifact_path = canonical_repo_path(expected_relative, f"Part1 {record_id} {name}")
                    data = audit.capture(f"Part1 {record_id} {name}", regular_bytes, artifact_path)
                    if data is not None and sha256_bytes(data) != item.get("sha256_exact_file_bytes"):
                        audit.issue(f"Part1 {record_id}: {name} hash mismatch")

                metadata_item = artifacts.get("staged_invocation_metadata")
                host_item = artifacts.get("host_recheck_output")
                for name, item, suffix in (
                    ("staged_invocation_metadata", metadata_item, "metadata.json"),
                    ("host_recheck_output", host_item, "host_run_output.txt"),
                ):
                    if not isinstance(item, dict) or set(item) != {"source_path", "sha256_exact_file_bytes"}:
                        audit.issue(f"Part1 {record_id}: malformed {name}")
                        continue
                    expected_relative = f".task8_algo_verify_stage_pro/{fn_for(record_id)}/{suffix}"
                    if item.get("source_path") != expected_relative:
                        audit.issue(f"Part1 {record_id}: noncanonical {name} source path")
                    if not is_sha256(item.get("sha256_exact_file_bytes")):
                        audit.issue(f"Part1 {record_id}: malformed {name} SHA-256")

                line_item = artifacts.get("completion_log_row")
                if not isinstance(line_item, dict) or set(line_item) != {
                    "path", "line_number", "row", "sha256_exact_utf8_line_including_lf",
                }:
                    audit.issue(f"Part1 {record_id}: malformed completion-log artifact")
                elif result["log_rows"]:
                    line_number = line_item.get("line_number")
                    if not is_sha256(line_item.get("sha256_exact_utf8_line_including_lf")):
                        audit.issue(f"Part1 {record_id}: malformed completion-log SHA-256")
                    if type(line_number) is not int or not 1 <= line_number <= len(result["log_rows"]):
                        audit.issue(f"Part1 {record_id}: invalid completion-log line number")
                    else:
                        actual_row, actual_raw = result["log_rows"][line_number - 1]
                        if line_item.get("path") != "qedbench_certificate_availability_triage/outputs_algo_tests/CODEX_COMPLETION_LOG.jsonl":
                            audit.issue(f"Part1 {record_id}: completion-log path mismatch")
                        if line_item.get("row") != actual_row or actual_row.get("record_id") != record_id:
                            audit.issue(f"Part1 {record_id}: completion-log row mismatch")
                        if line_item.get("sha256_exact_utf8_line_including_lf") != sha256_bytes(actual_raw):
                            audit.issue(f"Part1 {record_id}: completion-log line hash mismatch")

    return result


@dataclass
class Part2State:
    population: list[str]
    inputs: dict[str, dict[str, str]]
    searches: dict[str, dict[str, str]]
    verifies: dict[str, dict[str, str]]
    search_sources: dict[str, str]
    verify_sources: dict[str, str]
    search_gap: list[str]
    verify_gap: list[str]
    log_rows: dict[tuple[str, str], dict[str, Any]]


def validate_population(audit: Audit) -> tuple[list[str], dict[str, dict[str, str]]]:
    population_path = RUN / "population_ids.json"
    raw = audit.capture("population bytes", regular_bytes, population_path)
    if raw is None:
        return [], {}
    audit.check(sha256_bytes(raw) == POPULATION_SHA256, "frozen population_ids.json hash mismatch")
    population = audit.capture("population JSON", strict_json_loads, raw.decode("utf-8"), str(population_path))
    if not isinstance(population, list) or any(type(item) is not str for item in population):
        audit.issue("population_ids.json is not a string list")
        return [], {}
    audit.check(
        len(population) == POPULATION_SIZE,
        f"population size is {len(population)}, expected {POPULATION_SIZE}",
    )
    # The PI's 604-frame amendment was append-only so the already completed
    # 566-record frame retained byte/order identity.  Each frozen segment is
    # canonical; globally sorting now would rewrite the handoff artifact after
    # model calls had been attributed to it.
    audit.check(
        population[:PRE_AMENDMENT_POPULATION_SIZE]
        == sorted(population[:PRE_AMENDMENT_POPULATION_SIZE]),
        "pre-amendment population segment is not canonically sorted",
    )
    audit.check(
        population[PRE_AMENDMENT_POPULATION_SIZE:]
        == sorted(population[PRE_AMENDMENT_POPULATION_SIZE:]),
        "amended population segment is not canonically sorted",
    )
    audit.check(len(population) == len(set(population)), "population IDs are duplicated")
    mappings: list[str] = []
    for record_id in population:
        mapped = audit.capture(f"filename map {record_id}", fn_for, record_id)
        if isinstance(mapped, str):
            mappings.append(mapped)
    audit.check(len(mappings) == len(set(mappings)), "population filename mapping collides")

    input_inventory = audit.capture("input inventory", inventory_json, RUN / "inputs")
    inputs: dict[str, dict[str, str]] = {}
    if input_inventory is None:
        return population, inputs
    expected_names = {f"{fn_for(record_id)}.json" for record_id in population}
    audit.check(set(input_inventory) == expected_names, "input file set is not exact population")
    for record_id in population:
        path = input_inventory.get(f"{fn_for(record_id)}.json")
        if path is None:
            continue
        payload = audit.capture(f"input {record_id}", read_json, path)
        if not isinstance(payload, dict) or set(payload) != {
            "record_id", "target_claim", "source_quote", "domain", "stratum",
        }:
            audit.issue(f"input {record_id}: closed schema mismatch")
            continue
        if any(type(payload[key]) is not str or not payload[key].strip() for key in payload):
            audit.issue(f"input {record_id}: fields must be nonempty strings")
            continue
        if payload["record_id"] != record_id or payload["stratum"] not in {"certified", "no_lean"}:
            audit.issue(f"input {record_id}: ID/stratum mismatch")
            continue
        inputs[record_id] = payload
    strata = Counter(row["stratum"] for row in inputs.values())
    audit.check(
        strata == Counter({"certified": 514, "no_lean": 90}),
        f"population strata mismatch: {dict(strata)}",
    )
    return population, inputs


def validate_handoff_baseline(audit: Audit, population: list[str]) -> None:
    path = RUN / "handoff_gap.json"
    raw = audit.capture("handoff gap bytes", regular_bytes, path)
    if raw is None:
        return
    audit.check(sha256_bytes(raw) == HANDOFF_GAP_SHA256, "frozen handoff_gap.json hash mismatch")
    payload = audit.capture("handoff gap JSON", strict_json_loads, raw.decode("utf-8"), str(path))
    if not isinstance(payload, dict) or set(payload) != {"search_gap", "verify_gap"}:
        audit.issue("handoff_gap.json closed schema mismatch")
        return
    search_gap = payload.get("search_gap")
    verify_gap = payload.get("verify_gap")
    if not isinstance(search_gap, list) or not isinstance(verify_gap, list):
        audit.issue("handoff_gap.json gaps are not lists")
        return
    audit.check(
        len(search_gap) == POPULATION_SIZE - PRE_AMENDMENT_POPULATION_SIZE
        and search_gap == sorted(search_gap)
        and len(search_gap) == len(set(search_gap))
        and set(search_gap) <= set(population),
        "amended handoff search gap is not exact sorted unique 38",
    )
    audit.check(
        len(set(population) - set(search_gap)) == PRE_AMENDMENT_POPULATION_SIZE,
        "amended handoff does not preserve the completed 566-record frame",
    )
    audit.check(
        population[PRE_AMENDMENT_POPULATION_SIZE:] == search_gap,
        "amended handoff gap is not the exact append-only population suffix",
    )
    audit.check(
        set(FABLE_BASELINE_IDS) <= set(population) - set(search_gap),
        "frozen Fable baseline is not contained in the pre-amendment frame",
    )
    audit.check(verify_gap == [], "amended handoff verify gap is not empty")


def validate_search_result(payload: Any, record_id: str, codex: bool) -> dict[str, str]:
    validate_string_object(payload, SEARCH_KEYS, f"search {record_id}", "outcome", SEARCH_OUTCOMES)
    if payload["record_id"] != record_id:
        raise AuditError(f"search {record_id}: record_id mismatch")
    relative = f"partB_feasibility/code_twins/{fn_for(record_id)}/test.py"
    expected = relative if codex else str(REPO / relative)
    if payload["test_path"] != expected:
        raise AuditError(f"search {record_id}: noncanonical {'relative' if codex else 'legacy absolute'} test_path")
    return dict(payload)


def validate_verify_result(payload: Any, record_id: str) -> dict[str, str]:
    validate_string_object(payload, VERIFY_KEYS, f"verify {record_id}", "verdict", VERIFY_VERDICTS)
    if payload["record_id"] != record_id:
        raise AuditError(f"verify {record_id}: record_id mismatch")
    return dict(payload)


def validate_attempts_and_provenance(
    audit: Audit,
    population: list[str],
    expected_codex_pairs: set[tuple[str, str]],
) -> dict[tuple[str, str], dict[str, Any]]:
    attempt_root = RUN / "codex_attempts"
    published: dict[tuple[str, str], list[tuple[dict[str, Any], Path]]] = defaultdict(list)
    if not attempt_root.is_dir() or attempt_root.is_symlink():
        audit.issue("Codex attempt archive is missing/noncanonical")
    else:
        stage_entries = {path.name for path in attempt_root.iterdir() if not path.name.startswith(".")}
        audit.check(stage_entries <= {"search", "verify"}, f"unexpected attempt stage directories: {sorted(stage_entries - {'search', 'verify'})}")
        attempt_paths: list[Path] = []
        for stage_path in sorted(attempt_root.iterdir(), key=lambda item: item.name):
            if stage_path.name.startswith("."):
                continue
            if stage_path.name not in {"search", "verify"}:
                continue
            if not stage_path.is_dir() or stage_path.is_symlink():
                audit.issue(f"attempt stage is not a canonical directory: {stage_path}")
                continue
            for record_path in sorted(stage_path.iterdir(), key=lambda item: item.name):
                if not record_path.is_dir() or record_path.is_symlink():
                    audit.issue(f"attempt record entry is not a canonical directory: {record_path}")
                    continue
                for candidate in sorted(record_path.iterdir(), key=lambda item: item.name):
                    if candidate.is_dir():
                        audit.issue(f"unexpected nested attempt directory: {candidate}")
                    else:
                        attempt_paths.append(candidate)
        for path in attempt_paths:
            if not path.is_file() or path.is_symlink() or not ATTEMPT_NAME.fullmatch(path.name):
                audit.issue(f"unexpected attempt artifact: {path.relative_to(attempt_root)}")
                continue
            stage = path.parent.parent.name
            directory_fn = path.parent.name
            payload = audit.capture(f"attempt {path}", read_json, path)
            if not isinstance(payload, dict) or set(payload) != ATTEMPT_KEYS:
                audit.issue(f"attempt {path}: closed schema mismatch")
                continue
            record_id = payload.get("record_id")
            if record_id not in population or stage not in {"search", "verify"}:
                audit.issue(f"attempt {path}: unknown record/stage")
                continue
            if directory_fn != fn_for(record_id) or payload.get("stage") != stage:
                audit.issue(f"attempt {path}: filename/record/stage mismatch")
            # This applies to every archived use, and is an absolute gate for
            # a PUBLISHED completion below.
            if (
                payload.get("executor") != MODEL
                or payload.get("reasoning_mode") != REASONING_MODE
                or payload.get("reasoning_effort") not in CODEX_ALLOWED_EFFORTS
                or payload.get("ephemeral") is not True
                or payload.get("model_tools_disabled") is not True
                or payload.get("sandbox") != "read-only"
            ):
                audit.issue(
                    f"attempt {path}: not an isolated gpt-5.6-sol/pro "
                    "high-or-xhigh invocation"
                )
            started = audit.capture(f"attempt {path} started_at", parse_time, payload.get("started_at"), str(path))
            status_value = payload.get("status")
            if status_value == "RUNNING":
                audit.issue(f"attempt {path}: still RUNNING")
            elif status_value not in FINAL_ATTEMPT_STATUSES:
                audit.issue(f"attempt {path}: invalid final status {status_value!r}")
            if status_value in FINAL_ATTEMPT_STATUSES:
                finished = audit.capture(f"attempt {path} finished_at", parse_time, payload.get("finished_at"), str(path))
                if isinstance(started, dt.datetime) and isinstance(finished, dt.datetime) and finished < started:
                    audit.issue(f"attempt {path}: finish precedes start")
            if type(payload.get("detail")) is not str:
                audit.issue(f"attempt {path}: detail is not a string")
            if status_value == "FAILED" and not payload.get("detail"):
                audit.issue(f"attempt {path}: failed attempt lacks detail")
            if status_value == "PUBLISHED":
                published[(record_id, stage)].append((payload, path))

    actual_published = set(published)
    audit.check(actual_published == expected_codex_pairs, "PUBLISHED attempt set does not exactly equal Codex result set")
    for pair, rows in published.items():
        if len(rows) != 1:
            audit.issue(f"published attempt duplicate for {pair}: {len(rows)}")
        for payload, path in rows:
            if payload.get("executor") != MODEL or payload.get("reasoning_mode") != REASONING_MODE:
                audit.issue(f"published result {pair} backed by non-Pro/non-sol attempt {path}")

    log_rows_raw = audit.capture("Part2 provenance", read_jsonl, RUN / "CODEX_COMPLETION_LOG.jsonl")
    log_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    if log_rows_raw is not None:
        for number, (row, _raw) in enumerate(log_rows_raw, 1):
            if set(row) != {"record_id", "stage", "executor", "ts"}:
                audit.issue(f"Part2 provenance line {number}: closed schema mismatch")
                continue
            pair = (row.get("record_id"), row.get("stage"))
            if row.get("executor") != MODEL or pair[0] not in population or pair[1] not in {"search", "verify"}:
                audit.issue(f"Part2 provenance line {number}: record/stage/executor mismatch")
            audit.capture(f"Part2 provenance line {number} timestamp", parse_time, row.get("ts"), f"Part2 log:{number}")
            if pair in log_by_pair:
                audit.issue(f"Part2 provenance duplicate completion row {pair}")
            else:
                log_by_pair[pair] = row
        audit.check(set(log_by_pair) == expected_codex_pairs, "Part2 provenance is not exact Codex completion set")

    for pair in expected_codex_pairs & set(log_by_pair) & set(published):
        rows = published[pair]
        if len(rows) != 1:
            continue
        attempt, _path = rows[0]
        started = audit.capture(f"published {pair} started", parse_time, attempt.get("started_at"), str(pair))
        finished = audit.capture(f"published {pair} finished", parse_time, attempt.get("finished_at"), str(pair))
        logged = audit.capture(f"published {pair} logged", parse_time, log_by_pair[pair].get("ts"), str(pair))
        if all(isinstance(value, dt.datetime) for value in (started, finished, logged)):
            if not started <= logged <= finished:
                audit.issue(f"published {pair}: provenance timestamp is outside attempt interval")
    return log_by_pair


def validate_part2(audit: Audit) -> Part2State:
    population, inputs = validate_population(audit)
    validate_handoff_baseline(audit, population)
    population_set = set(population)
    search_inventory = audit.capture("Part2 search inventory", inventory_json, RUN / "searches") or {}
    expected_search_names = {f"{fn_for(record_id)}.json" for record_id in population}
    actual_search_ids = {
        record_id for record_id in population
        if f"{fn_for(record_id)}.json" in search_inventory
    }
    search_gap = sorted(population_set - actual_search_ids)
    extras = set(search_inventory) - expected_search_names
    if extras:
        audit.issue(f"Part2 search directory has extra files: {sorted(extras)[:20]}")
    if search_gap:
        audit.issue(f"Part2 search gap {len(search_gap)}: {search_gap[:20]}")

    searches: dict[str, dict[str, str]] = {}
    search_sources: dict[str, str] = {}
    for record_id in sorted(actual_search_ids):
        codex = record_id not in FABLE_BASELINE_IDS
        path = search_inventory[f"{fn_for(record_id)}.json"]
        payload = audit.capture(f"search result {record_id}", read_json, path)
        if payload is None:
            continue
        validated = audit.capture(f"search result {record_id}", validate_search_result, payload, record_id, codex)
        if validated is None:
            continue
        searches[record_id] = validated
        program_path = PROGRAMS / fn_for(record_id) / "test.py"
        data = audit.capture(f"search program {record_id}", regular_bytes, program_path)
        if data is None:
            continue
        try:
            source = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            audit.issue(f"search program {record_id}: not UTF-8: {exc}")
            continue
        target_claim = inputs.get(record_id, {}).get("target_claim") if codex else None
        try:
            static_exact_check(source, record_id, "test.py", target_claim, codex_schema=codex)
        except Exception as exc:
            audit.issue(f"search program {record_id}: {exc}")
        search_sources[record_id] = source
        if record_id in FABLE_BASELINE_SHA256:
            expected_result_hash, expected_program_hash = FABLE_BASELINE_SHA256[record_id]
            if sha256_bytes(regular_bytes(path)) != expected_result_hash:
                audit.issue(f"Fable baseline result changed: {record_id}")
            if sha256_bytes(data) != expected_program_hash:
                audit.issue(f"Fable baseline program changed: {record_id}")

    baseline_present = set(searches) & set(FABLE_BASELINE_IDS)
    audit.check(baseline_present == set(FABLE_BASELINE_IDS), "existing Fable baseline is not intact exact 16")
    baseline_outcomes = Counter(searches[record_id]["outcome"] for record_id in baseline_present)
    audit.check(baseline_outcomes == Counter({
        "WITNESS_FOUND": 7,
        "NO_WITNESS_EXHAUSTIVE": 3,
        "NO_WITNESS_INCONCLUSIVE": 2,
        "CLAIM_NOT_FINITELY_REFUTABLE": 4,
    }), f"Fable baseline outcome counts changed: {dict(baseline_outcomes)}")
    audit.check({record_id for record_id in baseline_present if searches[record_id]["outcome"] == "WITNESS_FOUND"} == set(FABLE_WITNESS_IDS), "Fable baseline witness set changed")

    witness_ids = {record_id for record_id, row in searches.items() if row["outcome"] == "WITNESS_FOUND"}
    verify_inventory = audit.capture("Part2 verify inventory", inventory_json, RUN / "verifies") or {}
    expected_verify_names = {f"{fn_for(record_id)}.json" for record_id in witness_ids}
    actual_verify_ids = {
        record_id for record_id in population
        if f"{fn_for(record_id)}.json" in verify_inventory
    }
    verify_gap = sorted(witness_ids - actual_verify_ids)
    extra_verify_names = set(verify_inventory) - expected_verify_names
    if extra_verify_names:
        audit.issue(f"Part2 verify directory is not exact current WITNESS_FOUND set; extras: {sorted(extra_verify_names)[:20]}")
    if verify_gap:
        audit.issue(f"Part2 verify gap {len(verify_gap)}: {verify_gap[:20]}")

    verifies: dict[str, dict[str, str]] = {}
    verify_sources: dict[str, str] = {}
    for record_id in sorted(actual_verify_ids):
        path = verify_inventory[f"{fn_for(record_id)}.json"]
        payload = audit.capture(f"verify result {record_id}", read_json, path)
        if payload is None:
            continue
        validated = audit.capture(f"verify result {record_id}", validate_verify_result, payload, record_id)
        if validated is None:
            continue
        verifies[record_id] = validated
        program_path = PROGRAMS / fn_for(record_id) / "verify.py"
        data = audit.capture(f"verify program {record_id}", regular_bytes, program_path)
        if data is None:
            continue
        try:
            source = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            audit.issue(f"verify program {record_id}: not UTF-8: {exc}")
            continue
        try:
            static_exact_check(source, record_id, "verify.py", inputs.get(record_id, {}).get("target_claim"), codex_schema=True)
        except Exception as exc:
            audit.issue(f"verify program {record_id}: {exc}")
        verify_sources[record_id] = source

    if not search_gap and len(searches) == POPULATION_SIZE:
        audit.check(set(verify_inventory) == expected_verify_names, "Part2 final verify set is not exactly final WITNESS_FOUND set")
        audit.check(set(verifies) == witness_ids, "Part2 valid verify set is not exactly final WITNESS_FOUND set")
        if PROGRAMS.is_dir() and not PROGRAMS.is_symlink():
            root_files = [path.name for path in PROGRAMS.iterdir() if not path.is_dir()]
            if root_files:
                audit.issue(f"unexpected files at code_twins root: {root_files}")
            actual_dirs = {path.name for path in PROGRAMS.iterdir() if path.is_dir() and not path.is_symlink()}
            expected_dirs = {fn_for(record_id) for record_id in population}
            audit.check(actual_dirs == expected_dirs, "code_twins directory set is not exact population")
            for record_id in population:
                directory = PROGRAMS / fn_for(record_id)
                if not directory.is_dir() or directory.is_symlink():
                    continue
                actual_leaves = {path.name for path in directory.iterdir()}
                expected_leaves = {"test.py"} | ({"verify.py"} if record_id in witness_ids else set())
                if actual_leaves != expected_leaves:
                    audit.issue(f"code_twins/{fn_for(record_id)} leaf set mismatch: {sorted(actual_leaves)}")

    expected_codex_pairs = {
        (record_id, "search") for record_id in searches if record_id not in FABLE_BASELINE_IDS
    } | {(record_id, "verify") for record_id in verifies}
    log_rows = validate_attempts_and_provenance(audit, population, expected_codex_pairs)
    return Part2State(
        population=population,
        inputs=inputs,
        searches=searches,
        verifies=verifies,
        search_sources=search_sources,
        verify_sources=verify_sources,
        search_gap=search_gap,
        verify_gap=verify_gap,
        log_rows=log_rows,
    )


def execute_copy(source: str, leaf: str, timeout: int, hash_seed: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix="task8-cold-audit-") as name:
        root = Path(name)
        script = root / leaf
        script.write_text(source, encoding="utf-8")
        stdout_path = root / "stdout.bin"
        stderr_path = root / "stderr.bin"
        env = {
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PATH": os.defpath,
            "PYTHONHASHSEED": hash_seed,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        command = [
            "/usr/bin/prlimit",
            f"--cpu={max(1, timeout)}:{max(2, timeout + 1)}",
            "--as=2147483648:2147483648",
            f"--fsize={MAX_OUTPUT_BYTES}:{MAX_OUTPUT_BYTES}",
            "--nofile=64:64",
            "--core=0:0",
            "--",
            sys.executable,
            "-B",
            "-S",
            str(script),
        ]
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(
                command,
                cwd=root,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            try:
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                raise AuditError(f"{leaf}: timed out after {timeout}s") from exc
        output = stdout_path.read_bytes()
        if len(output) > MAX_OUTPUT_BYTES:
            raise AuditError(f"{leaf}: stdout exceeds {MAX_OUTPUT_BYTES} bytes")
        if returncode != 0:
            tail = stderr_path.read_bytes()[-2000:].decode("utf-8", errors="replace")
            raise AuditError(f"{leaf}: exited {returncode}: {tail}")
        try:
            output.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AuditError(f"{leaf}: stdout is not UTF-8") from exc
        return output


def validate_dynamic_one(
    record_id: str,
    stage: str,
    source: str,
    expected: dict[str, str] | None,
    timeout: int,
) -> None:
    leaf = "test.py" if stage == "search" else "verify.py"
    first = execute_copy(source, leaf, timeout, "0")
    second = execute_copy(source, leaf, timeout, "1")
    if first != second:
        raise AuditError(f"{record_id}/{leaf}: stdout changes with PYTHONHASHSEED")
    if not first.strip():
        raise AuditError(f"{record_id}/{leaf}: empty stdout")
    if expected is None:
        return
    text = first.decode("utf-8").strip()
    if "\n" in text:
        raise AuditError(f"{record_id}/{leaf}: Codex program does not print exactly one JSON line")
    actual = strict_json_loads(text, f"{record_id}/{leaf} stdout")
    if actual != expected:
        raise AuditError(f"{record_id}/{leaf}: stdout object differs from durable result")


def validate_dynamic(audit: Audit, state: Part2State, jobs: int, timeout: int) -> None:
    tasks: list[tuple[str, str, str, dict[str, str] | None, int]] = []
    for record_id in state.population:
        source = state.search_sources.get(record_id)
        result = state.searches.get(record_id)
        if source is None or result is None:
            audit.issue(f"dynamic search input missing for {record_id}")
            continue
        expected = None if record_id in FABLE_BASELINE_IDS else {
            key: result[key] for key in SEARCH_STDOUT_KEYS
        }
        tasks.append((record_id, "search", source, expected, timeout))
    for record_id in sorted(state.verifies):
        source = state.verify_sources.get(record_id)
        if source is None:
            audit.issue(f"dynamic verify input missing for {record_id}")
            continue
        tasks.append((record_id, "verify", source, state.verifies[record_id], timeout))

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {
            pool.submit(validate_dynamic_one, *task): (task[0], task[1])
            for task in tasks
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            record_id, stage = futures[future]
            try:
                future.result()
            except Exception as exc:
                audit.issue(f"dynamic {stage} {record_id}: {exc}")
            completed += 1
            if completed % 100 == 0:
                print(f"AUDIT_EXECUTED {completed}/{len(tasks)}", flush=True)


def state_fingerprint() -> str:
    fixed = [
        RUN / "population_ids.json",
        RUN / "handoff_gap.json",
        RUN / "CODEX_COMPLETION_LOG.jsonl",
        ALGO_OUT / "CODEX_COMPLETION_LOG.jsonl",
        ALGO_OUT / "codex_invocation_provenance/task8_part1_algo_verify.json",
    ]
    patterns = [
        (RUN, "inputs/*.json"),
        (RUN, "searches/*.json"),
        (RUN, "verifies/*.json"),
        (RUN, "codex_attempts/*/*/*.json"),
        (PROGRAMS, "*/test.py"),
        (PROGRAMS, "*/verify.py"),
        (ALGO_OUT, "test_search/*.json"),
        (ALGO_OUT, "test_verify/*.json"),
        (ALGO_PROGRAMS, "*/verify_oracle.py"),
    ]
    paths = set(fixed)
    for root, pattern in patterns:
        paths.update(root.glob(pattern))
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item)):
        relative = str(path.relative_to(REPO)).encode("utf-8")
        data = regular_bytes(path)
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    rendered = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    rendered.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return rendered


def build_summary(part1: dict[str, Any], state: Part2State) -> str:
    p1_search = Counter(row["outcome"] for row in part1["searches"].values())
    p1_verify = Counter(row["verdict"] for row in part1["verifies"].values())
    outcomes = Counter(row["outcome"] for row in state.searches.values())
    verdicts = Counter(row["verdict"] for row in state.verifies.values())
    witness_ids = {record_id for record_id, row in state.searches.items() if row["outcome"] == "WITNESS_FOUND"}

    cross: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    verify_cross: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for record_id, row in state.searches.items():
        executor = "Fable (pre-handoff)" if record_id in FABLE_BASELINE_IDS else f"{MODEL} (pro)"
        stratum = state.inputs[record_id]["stratum"]
        cross[(executor, stratum)][row["outcome"]] += 1
        if record_id in state.verifies:
            verify_cross[(executor, stratum)][state.verifies[record_id]["verdict"]] += 1

    lines = [
        "# Codex Task-8 handoff summary",
        "",
        "Cold audit: **PASS**. All completion gaps and validation gaps are zero. The auditor used no model, Lean, sbatch, or web access and did not mutate any search, verify, program, or provenance artifact; every executable was run from an isolated temporary copy.",
        "",
        "## Part 1 — algorithm-test stage 2",
        "",
        f"Searches: **16/16** ({p1_search['BUG_FOUND']} `BUG_FOUND`, {p1_search['BOUND_VIOLATION_FOUND']} `BOUND_VIOLATION_FOUND`). Verifications: **16/16** ({', '.join(f'{p1_verify[name]} `{name}`' for name in sorted(p1_verify))}). The two pre-handoff Opus verdicts retain their documented legacy fields; all 14 Codex verdicts have exactly `record_id`, `verdict`, and `notes`.",
        "",
    ]
    lines += markdown_table(
        ["Stage", "Opus (pre-handoff)", f"{MODEL} (pro)", "Total"],
        [["search", 16, 0, 16], ["verify", 2, 14, 16]],
    )
    lines += [
        "",
        "## Part 2 — executable twins",
        "",
        f"Searches: **{POPULATION_SIZE}/{POPULATION_SIZE}**. Required verifications: **{len(witness_ids)}/{len(witness_ids)}**, exactly the `WITNESS_FOUND` set. Verdicts: {', '.join(f'{verdicts[name]} `{name}`' for name in sorted(verdicts))}.",
        "",
    ]
    lines += markdown_table(
        ["Outcome", "Count"],
        [[name, outcomes[name]] for name in SEARCH_OUTCOMES] + [["Total", sum(outcomes.values())]],
    )
    lines += ["", "### Outcome × stratum × search executor", ""]
    cross_rows: list[list[Any]] = []
    for executor, stratum in sorted(cross):
        counter = cross[(executor, stratum)]
        vc = verify_cross[(executor, stratum)]
        cross_rows.append([
            executor,
            stratum,
            *(counter[name] for name in SEARCH_OUTCOMES),
            sum(counter.values()),
            vc["CONFIRMED"],
            vc["REFUTED_WITNESS_INVALID"],
            vc["CANNOT_REPRODUCE"],
        ])
    lines += markdown_table(
        [
            "Search executor", "Stratum", "WITNESS_FOUND",
            "NO_WITNESS_EXHAUSTIVE", "NO_WITNESS_INCONCLUSIVE",
            "CLAIM_NOT_FINITELY_REFUTABLE", "Search total",
            "Verified CONFIRMED", "Witness invalid", "Cannot reproduce",
        ],
        cross_rows,
    )
    lines += [
        "",
        "### Provenance and executable audit",
        "",
        f"The frozen Fable baseline contributes 16 searches. The exact remaining {POPULATION_SIZE - len(FABLE_BASELINE_IDS)} searches and all {len(witness_ids)} verifications are attributed one-to-one to unique `PUBLISHED` `{MODEL}` attempt manifests with `reasoning_mode=pro`, and to unique completion-log rows. All new Codex result schemas and canonical paths are exact. Every `test.py` and `verify.py` passed the independent stdlib/exact-arithmetic AST audit and deterministic double execution under distinct hash seeds; each Codex program's JSON stdout exactly equals its durable result. The 16 frozen Fable tests passed the same arithmetic/import and double-execution checks, with their documented human-readable stdout compatibility exception.",
        "",
    ]
    return "\n".join(lines)


def atomic_write_summary(text: str) -> None:
    data = text.encode("utf-8")
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{SUMMARY.name}.", dir=SUMMARY.parent)
    temporary = Path(name)
    try:
        os.fchmod(descriptor, 0o644)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, SUMMARY)
        directory_fd = os.open(SUMMARY.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def self_test() -> None:
    try:
        strict_json_loads('{"a":1,"a":2}', "duplicate test")
    except AuditError:
        pass
    else:
        raise AssertionError("duplicate JSON key was accepted")
    record_id = "Synthetic A/1"
    assert fn_for(record_id) == "Synthetic_A_1"
    claim = "For every integer n, n = n."
    expected = {
        "record_id": record_id,
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "none",
        "refutation_explanation": "all four checked",
        "search_space": "n in {0,1,2,3}",
    }
    source = (
        repr(claim)
        + "\nimport json\nfrom fractions import Fraction\n"
        + f"result = {expected!r}\n"
        + "assert all(Fraction(n, 1) == n for n in range(4))\n"
        + "print(json.dumps(result, sort_keys=True))\n"
    )
    static_exact_check(source, record_id, "test.py", claim, codex_schema=True)
    validate_dynamic_one(record_id, "search", source, expected, 10)
    for bad in (
        repr(claim) + "\nx = 0.5\n",
        repr(claim) + "\nx = 1 / 2\n",
        repr(claim) + "\nimport random\n",
        repr(claim) + "\nimport definitely_not_stdlib\n",
    ):
        try:
            static_exact_check(bad, record_id, "test.py", claim, codex_schema=True)
        except AuditError:
            pass
        else:
            raise AssertionError("unsafe source passed static audit")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--program-timeout", type=int, default=300)
    parser.add_argument("--max-issues", type=int, default=100)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print(f"SELF_TEST PASS model={MODEL} reasoning_mode={REASONING_MODE}")
        return 0
    if args.jobs < 1 or args.program_timeout < 1 or args.max_issues < 1:
        raise AuditError("jobs, program-timeout, and max-issues must be positive")

    fingerprint_before = state_fingerprint()
    audit = Audit()
    part1 = validate_part1(audit)
    state = validate_part2(audit)
    structurally_complete = (
        len(part1["searches"]) == 16
        and len(part1["verifies"]) == 16
        and len(state.population) == POPULATION_SIZE
        and len(state.searches) == POPULATION_SIZE
        and not state.search_gap
        and set(state.verifies) == {
            record_id for record_id, row in state.searches.items()
            if row["outcome"] == "WITNESS_FOUND"
        }
        and not state.verify_gap
    )
    if structurally_complete and not audit.issues:
        validate_dynamic(audit, state, args.jobs, args.program_timeout)
    fingerprint_after = state_fingerprint()
    if fingerprint_after != fingerprint_before:
        audit.issue("audited Task-8 state changed during the cold audit; rerun after writers finish")

    if audit.issues or not structurally_complete:
        print(
            "PARTIAL "
            f"part1_search={len(part1['searches'])}/16 "
            f"part1_verify={len(part1['verifies'])}/16 "
            f"part2_search={len(state.searches)}/{POPULATION_SIZE} "
            f"part2_verify={len(state.verifies)}/"
            f"{sum(row['outcome'] == 'WITNESS_FOUND' for row in state.searches.values())} "
            f"issues={len(audit.issues)}"
        )
        for issue in audit.issues[: args.max_issues]:
            print(f"- {issue}")
        if len(audit.issues) > args.max_issues:
            print(f"- ... {len(audit.issues) - args.max_issues} additional issues omitted")
        print(f"SUMMARY_NOT_WRITTEN {SUMMARY}")
        return 1

    summary = build_summary(part1, state)
    atomic_write_summary(summary)
    print(
        f"PASS part1=16/16 part2_search={POPULATION_SIZE}/{POPULATION_SIZE} "
        f"part2_verify={len(state.verifies)}/{len(state.verifies)} "
        f"model={MODEL} reasoning_mode={REASONING_MODE} wrote={SUMMARY}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(f"PARTIAL fatal={exc}", file=sys.stderr)
        print(f"SUMMARY_NOT_WRITTEN {SUMMARY}", file=sys.stderr)
        raise SystemExit(2)
