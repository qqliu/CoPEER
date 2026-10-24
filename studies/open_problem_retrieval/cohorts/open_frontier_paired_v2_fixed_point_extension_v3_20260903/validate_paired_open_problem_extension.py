#!/usr/bin/env python3
"""Independently validate a post-fixed-point paired extension run.

Exit 0 means every pair has a valid complete endpoint. Exit 1 means all present
evidence is valid but at least one pair is still operationally incomplete.
Exit 2 means the evidence or stopping contract is invalid.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
BASE = SCRIPT.parent.parent
REPO = BASE.parent
ORIGINAL_RUN = (BASE / "runs/open_frontier_paired_v2_20260901").resolve()
SEAL_UTILITY = SCRIPT.with_name("paired_open_problem_extension_runtime_seal.py")
FEEDBACK = SCRIPT.with_name("paired_open_problem_extension_feedback.py")
RETRIEVAL_CORE = SCRIPT.with_name("paired_open_problem_feedback.py")
STOCK_RETRIEVER = SCRIPT.with_name("bugbank_retrieve.py")
BATCH_LAUNCHER = SCRIPT.with_name("run_sealed_paired_open_problem_batch.sh")
CHECKPOINT_HELPER = SCRIPT.with_name("checkpoint_sealed_paired_open_problem_run.sh")
SLURM_LAUNCHER = BASE / "paired_open_problem_extension/fixed_point_v1.sbatch"
SLURM_LAUNCHERS_BY_RUN_ID = {
    "open_frontier_paired_v2_fixed_point_extension_v1_20260903": SLURM_LAUNCHER,
    "open_frontier_paired_v2_fixed_point_extension_v2_20260903": (
        BASE / "paired_open_problem_extension/fixed_point_v2.sbatch"
    ),
    "open_frontier_paired_v2_fixed_point_extension_v3_20260903": (
        BASE / "paired_open_problem_extension/fixed_point_v3.sbatch"
    ),
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z-]{2,}")
STOP_WORDS = set(
    """a an and are as at be by for from has have if in into is it its of on
    or that the their there these this to was we which will with not no nor so then
    than let all any each every some such given hence thus where when suppose assume
    proof claim show shows shown implies follows since because therefore step case
    """.split()
)
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
VALIDATED_RUNTIME_FILES: set[Path] = set()
OPERATIONAL_INCOMPLETE_FILES: set[Path] = set()
CLEAN_PYTHON_ENV = {
    "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "PATH": "/usr/bin:/bin",
    "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
    "PYTHONHASHSEED": "0",
}
MAX_SAFE_JSON_INTEGER = (1 << 53) - 1


class ValidationError(RuntimeError):
    """One or more purported evidence artifacts violates the contract."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValidationError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_nonfinite_json(value: str) -> Any:
    raise ValidationError(f"non-finite JSON number {value}")


def parse_finite_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        reject_nonfinite_json(token)
    return value


def is_token_count(value: Any) -> bool:
    return type(value) is int and 0 <= value <= MAX_SAFE_JSON_INTEGER


def add_token_counts(*values: int) -> int:
    if any(not is_token_count(value) for value in values):
        raise ValidationError("model-token count is not an exact JSON integer")
    total = sum(values)
    if total > MAX_SAFE_JSON_INTEGER:
        raise ValidationError("model-token total exceeds exact JSON-integer accounting")
    return total


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_json_float,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationError(f"invalid JSON {path}: {error}") from error
    if type(value) is not dict:
        raise ValidationError(f"expected JSON object: {path}")
    return value


def payload_hash(value: dict[str, Any], field: str) -> str:
    unsigned = copy.deepcopy(value)
    recorded = unsigned.pop(field, None)
    expected = sha_bytes(canonical_bytes(unsigned))
    if recorded != expected:
        raise ValidationError(f"{field} mismatch")
    return expected


def is_nonempty(value: Any) -> bool:
    return type(value) is str and bool(value)


def path_overlaps(left: Path, right: Path) -> bool:
    left = left.resolve(strict=False)
    right = right.resolve(strict=False)
    return left == right or left in right.parents or right in left.parents


def safe_run_root(raw: Path) -> Path:
    root = raw.resolve()
    if path_overlaps(root, ORIGINAL_RUN):
        raise ValidationError("extension validator refuses the original paired-run namespace")
    if not root.is_dir() or root.is_symlink():
        raise ValidationError("run root must be a plain directory")
    return root


def run_binding(run: Path, binding: Any, label: str) -> Path:
    if type(binding) is not dict or set(binding) != {"path", "sha256", "size_bytes"}:
        raise ValidationError(f"{label} is not an exact artifact binding")
    raw = binding["path"]
    if type(raw) is not str or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        raise ValidationError(f"unsafe path in {label}")
    path = run / raw
    if not path.is_file() or path.is_symlink():
        raise ValidationError(f"missing plain file for {label}: {path}")
    try:
        path.resolve().relative_to(run)
    except ValueError as error:
        raise ValidationError(f"{label} escapes run") from error
    if (binding["sha256"] != sha_file(path)
            or binding["size_bytes"] != path.stat().st_size):
        raise ValidationError(f"artifact mismatch for {label}")
    return path


def repo_artifact(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.resolve().relative_to(REPO.resolve()).as_posix(),
        "sha256": sha_bytes(raw), "size_bytes": len(raw),
    }


def artifact_matches(value: Any, path: Path) -> bool:
    try:
        return value == repo_artifact(path)
    except (OSError, ValueError):
        return False


def proof_state(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "claimed_resolution": value["claimed_resolution"],
        "results": [
            {"claim": row["claim"], "proof_sketch": row["proof_sketch"]}
            for row in value["results"]
        ],
        "final_writeup": value["final_writeup"],
    }


def proof_hash(value: dict[str, Any]) -> str:
    return sha_bytes(canonical_bytes(proof_state(value)))


def valid_draft_core(value: Any) -> bool:
    return (
        type(value) is dict
        and value.get("claimed_resolution") in {"FULL", "PARTIAL", "NONE"}
        and type(value.get("results")) is list and bool(value["results"])
        and all(
            type(row) is dict and is_nonempty(row.get("claim"))
            and is_nonempty(row.get("proof_sketch")) for row in value["results"]
        )
        and is_nonempty(value.get("final_writeup"))
        and type(value.get("checks_performed")) is list
        and all(is_nonempty(row) for row in value["checks_performed"])
        and value.get("self_assessment") in {"CONFIDENT", "UNSURE"}
    )


def expected_resolution(parent: dict[str, Any], target: str) -> str | None:
    claimed_rank = {"NONE": 0, "PARTIAL": 1, "FULL": 2}.get(parent.get("claimed_resolution"))
    target_rank = {
        "NO_VALID_PROGRESS": 0, "OVERCLAIMED": 0,
        "VALID_PARTIAL_PROGRESS": 1, "FULLY_RESOLVES_TARGET": 2,
    }.get(target)
    if claimed_rank is None or target_rank is None:
        return None
    if claimed_rank == target_rank:
        return "ACCURATE"
    return "OVERSTATED" if claimed_rank > target_rank else "UNDERSTATED"


def validate_audit(
    value: dict[str, Any], *, record_id: str, arm: str, attempt: int,
    parent: dict[str, Any], parent_hash: str, seed: bool = False,
) -> None:
    if set(value) != {
        "record_id", "stage", "arm", "iteration", "parent_sha256", "complete",
        "claims", "confirmed_refutations", "target_verdict",
        "claimed_resolution_verdict", "target_evidence", "overall", "checks_performed",
    }:
        raise ValidationError("independent audit key envelope mismatch")
    if (value.get("record_id") != record_id or value.get("arm") != arm
            or value.get("parent_sha256") != parent_hash or value.get("complete") is not True
            or type(value.get("claims")) is not list
            or len(value["claims"]) != len(parent["results"])
            or type(value.get("confirmed_refutations")) is not list
            or type(value.get("checks_performed")) is not list
            or not all(is_nonempty(row) for row in value["checks_performed"])
            or value.get("target_verdict") not in {
                "FULLY_RESOLVES_TARGET", "VALID_PARTIAL_PROGRESS",
                "NO_VALID_PROGRESS", "OVERCLAIMED",
            }
            or value.get("claimed_resolution_verdict") not in {
                "ACCURATE", "OVERSTATED", "UNDERSTATED",
            }
            or value.get("claimed_resolution_verdict") != expected_resolution(
                parent, value.get("target_verdict")
            )
            or not is_nonempty(value.get("target_evidence"))):
        raise ValidationError("invalid independent audit envelope")
    if seed:
        if (type(value.get("iteration")) is not int or value["iteration"] < 0
                or value.get("stage") not in {"BASELINE_AUDIT", "REVISION_AUDIT"}):
            raise ValidationError("invalid seed audit identity")
    elif value.get("iteration") != attempt or value.get("stage") != "REVISION_AUDIT":
        raise ValidationError("invalid extension audit attempt identity")
    refutations: list[int] = []
    for index, (claim, source) in enumerate(zip(value["claims"], parent["results"])):
        if (type(claim) is not dict or set(claim) != {
                "idx", "claim", "claim_sha256", "verdict", "evidence", "witness",
                "search_method", "checker_path",
            } or claim.get("idx") != index
                or claim.get("claim") != source["claim"]
                or claim.get("claim_sha256") != sha_bytes(source["claim"].encode())
                or claim.get("verdict") not in {"VERIFIED", "REFUTED", "UNRESOLVED"}
                or not all(is_nonempty(claim.get(field)) for field in (
                    "evidence", "witness", "search_method", "checker_path"
                ))):
            raise ValidationError(f"invalid audit claim {index}")
        if claim["verdict"] == "REFUTED":
            refutations.append(index)
    expected_overall = (
        "REFUTED" if refutations else
        "VERIFIED" if value["claims"] and all(
            row["verdict"] == "VERIFIED" for row in value["claims"]
        ) else "INCONCLUSIVE"
    )
    if value["confirmed_refutations"] != refutations or value.get("overall") != expected_overall:
        raise ValidationError("audit verdict aggregation mismatch")


def strict_full(revision: dict[str, Any], audit: dict[str, Any]) -> bool:
    return (
        valid_draft_core(revision)
        and revision.get("claimed_resolution") == "FULL"
        and audit.get("target_verdict") == "FULLY_RESOLVES_TARGET"
        and audit.get("claimed_resolution_verdict") == "ACCURATE"
        and audit.get("overall") == "VERIFIED"
        and audit.get("confirmed_refutations") == []
        and bool(audit.get("claims"))
        and len(audit["claims"]) == len(revision["results"])
        and all(row.get("verdict") == "VERIFIED" for row in audit["claims"])
    )


def audit_settled(audit: dict[str, Any]) -> bool:
    return (
        audit.get("confirmed_refutations") == []
        and audit.get("claimed_resolution_verdict") == "ACCURATE"
        and audit.get("target_verdict") != "OVERCLAIMED"
    )


@dataclass(frozen=True)
class AttemptEvidence:
    number: int
    parent: dict[str, Any]
    revision: dict[str, Any]
    audit: dict[str, Any]
    revision_path: Path
    audit_path: Path
    tokens: int


@dataclass(frozen=True)
class Endpoint:
    terminal: bool
    status: str
    attempt: int | None
    incremental_tokens: int | None
    reason: str


@dataclass(frozen=True)
class ArmChainEvidence:
    """Fully audited attempts plus one rigorously checked operational prefix."""

    attempts: list[AttemptEvidence]
    next_reason: str
    partial_attempt: int | None
    partial_stage: str | None


def derive_endpoint(
    arm: str, attempts: list[AttemptEvidence], bugbank_endpoint: Endpoint | None,
    forced_attempts: int = 3, max_attempts: int = 50,
) -> Endpoint:
    total = 0
    for evidence in attempts:
        total = add_token_counts(total, evidence.tokens)
        if strict_full(evidence.revision, evidence.audit):
            return Endpoint(True, "VERIFIED_FULL", evidence.number, total, "strict full audit")
        unchanged = proof_state(evidence.parent) == proof_state(evidence.revision)
        no_acted = arm == "plain" or evidence.revision.get("acted_on_entry_ids") == []
        eligible = (
            evidence.number >= forced_attempts and unchanged
            and audit_settled(evidence.audit) and no_acted
        )
        if arm == "bugbank" and eligible:
            return Endpoint(
                True, "INCONCLUSIVE_EXTENDED_FIXED_POINT", evidence.number,
                total, "post-lens audited closure",
            )
        if arm == "plain" and eligible and bugbank_endpoint is not None:
            if bugbank_endpoint.terminal and bugbank_endpoint.incremental_tokens is not None:
                if total >= bugbank_endpoint.incremental_tokens:
                    return Endpoint(
                        True, "INCONCLUSIVE_EXTENDED_FIXED_POINT", evidence.number,
                        total, "post-lens audited closure with matched incremental budget",
                    )
            elif bugbank_endpoint.status == "INCOMPLETE_MAX_ATTEMPTS":
                return Endpoint(
                    False, "INCOMPLETE_BUGBANK_NO_ENDPOINT", None, total,
                    "BugBank exhausted its attempt cap without an endpoint",
                )
    if len(attempts) == max_attempts:
        return Endpoint(
            False, "INCOMPLETE_MAX_ATTEMPTS", None, total,
            "no endpoint within maximum attempts",
        )
    if arm == "plain" and attempts and bugbank_endpoint is not None:
        last = attempts[-1]
        closed = (
            last.number >= forced_attempts
            and proof_state(last.parent) == proof_state(last.revision)
            and audit_settled(last.audit)
        )
        if closed and not bugbank_endpoint.terminal:
            return Endpoint(False, "INCOMPLETE_WAITING_FOR_BUGBANK", None, total, "waiting")
    return Endpoint(False, "INCOMPLETE", None, total if attempts else 0, "next attempt required")


def validate_manifest(run: Path) -> dict[str, Any]:
    manifest = load_json(run / "EXTENSION_MANIFEST.json")
    if (manifest.get("schema") != "paired_open_problem_extension_manifest_v1"
            or manifest.get("run_id") != run.name
            or manifest.get("status") != "BOOTSTRAPPED_AWAITING_RUNTIME_SEAL"
            or manifest.get("launch_authorized") is not False):
        raise ValidationError("extension manifest identity/status mismatch")
    payload_hash(manifest, "manifest_payload_sha256")
    protocol = manifest.get("protocol")
    execution = manifest.get("execution")
    bugbank = manifest.get("bugbank")
    if (type(protocol) is not dict
            or protocol.get("id") != "POST_FIXED_POINT_THREE_FORCED_V1"
            or protocol.get("whole_proof_claim_cap") is not None
            or protocol.get("bugbank_query_basis") != "claim + two newlines + proof_sketch"
            or protocol.get("retrieval_k_per_claim") != 3
            or protocol.get("first_strict_full_audit_stops_either_arm") is not True
            or protocol.get("inconclusive_min_valid_audited_attempts") != 3
            or protocol.get("plain_inconclusive_uses_incremental_budget_match") is not True
            or protocol.get("max_attempts") != 50):
        raise ValidationError("extension protocol fields mismatch")
    lenses = protocol.get("neutral_lenses")
    if type(lenses) is not list or len(lenses) != 3:
        raise ValidationError("exactly three neutral lenses are required")
    for number, lens in enumerate(lenses, 1):
        if (type(lens) is not dict or lens.get("attempt") != number
                or not is_nonempty(lens.get("name")) or not is_nonempty(lens.get("instruction"))
                or lens.get("instruction_sha256") != sha_bytes(lens["instruction"].encode())):
            raise ValidationError(f"neutral lens {number} is invalid")
    if (type(execution) is not dict or execution.get("model") != "gpt-5.6-sol"
            or execution.get("reasoning_effort") != "max"
            or execution.get("arms") != ["bugbank", "plain"]
            or execution.get("max_attempts") != 50
            or execution.get("runtime_seal_required") is not True):
        raise ValidationError("extension execution contract mismatch")
    if type(bugbank) is not dict or bugbank.get("retrieval_k") != 3:
        raise ValidationError("extension BugBank contract mismatch")
    operations = manifest.get("operations")
    if type(operations) is not dict:
        raise ValidationError("missing operations contract")
    for key in ("ops_root", "scratch_root", "stop_file"):
        if type(operations.get(key)) is not str or not Path(operations[key]).is_absolute():
            raise ValidationError(f"operations.{key} must be absolute")
    if Path(operations["stop_file"]) != Path(operations["ops_root"]) / "STOP_REQUESTED":
        raise ValidationError("stop file is outside isolated ops root")
    protected = [run, REPO, ORIGINAL_RUN, Path("<workspace-home>/paired_v2_ops")]
    for key in ("ops_root", "scratch_root"):
        if any(path_overlaps(Path(operations[key]), item) for item in protected):
            raise ValidationError(f"operations.{key} overlaps protected storage")
    if path_overlaps(Path(operations["ops_root"]), Path(operations["scratch_root"])):
        raise ValidationError("extension ops and scratch roots overlap")
    problem_ids = manifest.get("problem_ids")
    records = manifest.get("records")
    if (type(problem_ids) is not list or not problem_ids
            or len(problem_ids) != len(set(problem_ids))
            or any(type(item) is not str or ID_RE.fullmatch(item) is None for item in problem_ids)
            or type(records) is not list
            or [row.get("record_id") for row in records] != problem_ids
            or manifest.get("problem_count") != len(problem_ids)):
        raise ValidationError("manifest roster mismatch")
    for schema_name in ("revision", "audit"):
        run_binding(run, manifest["schemas"][schema_name], f"schema {schema_name}")
    for row in records:
        record_id = row["record_id"]
        run_binding(run, row["input"], f"input {record_id}")
        terminal_path = run_binding(run, row["seed_pair_terminal"], f"seed pair terminal {record_id}")
        terminal = load_json(terminal_path)
        for arm in ("bugbank", "plain"):
            arm_row = row.get("arms", {}).get(arm)
            if type(arm_row) is not dict:
                raise ValidationError(f"missing seed arm {record_id}:{arm}")
            revision_path = run_binding(run, arm_row["revision"], f"seed revision {record_id}:{arm}")
            audit_path = run_binding(run, arm_row["audit"], f"seed audit {record_id}:{arm}")
            run_binding(run, arm_row["prompt_metadata"], f"seed prompt metadata {record_id}:{arm}")
            if arm == "bugbank":
                run_binding(run, arm_row["receipt"], f"seed receipt {record_id}:{arm}")
            elif arm_row.get("receipt") is not None:
                raise ValidationError("plain seed receipt must be null")
            revision = load_json(revision_path)
            if (not valid_draft_core(revision) or revision.get("record_id") != record_id
                    or revision.get("arm") != arm):
                raise ValidationError(f"invalid seed revision {record_id}:{arm}")
            audit = load_json(audit_path)
            validate_audit(
                audit, record_id=record_id, arm=arm, attempt=0,
                parent=revision, parent_hash=sha_file(revision_path), seed=True,
            )
            tokens = arm_row.get("seed_lifetime_model_tokens")
            terminal_tokens = terminal.get("arms", {}).get(arm, {}).get("model_tokens_used")
            if not is_token_count(tokens) or tokens != terminal_tokens:
                raise ValidationError(f"seed token binding mismatch {record_id}:{arm}")
            if (type(arm_row.get("source_iteration")) is not int
                    or arm_row["source_iteration"] != terminal.get("arms", {}).get(arm, {}).get("iteration")):
                raise ValidationError(f"seed iteration binding mismatch {record_id}:{arm}")
    return manifest


def slurm_launcher_for_run_id(run_id: Any) -> Path:
    if type(run_id) is not str or run_id not in SLURM_LAUNCHERS_BY_RUN_ID:
        raise ValidationError(f"no independently reviewed Slurm launcher for run_id {run_id!r}")
    return SLURM_LAUNCHERS_BY_RUN_ID[run_id]


def verify_runtime_seal(run: Path) -> dict[str, Any]:
    seal_path = run / "RUNTIME_SEAL.json"
    manifest_path = run / "EXTENSION_MANIFEST.json"
    seal = load_json(seal_path)
    origin_result = subprocess.run(
        ["/usr/bin/git", "rev-parse", "origin/main^{commit}"], cwd=REPO,
        env=CLEAN_PYTHON_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    origin = origin_result.stdout.decode(errors="replace").strip()
    if origin_result.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", origin) is None:
        raise ValidationError("cannot establish validator bootstrap origin/main anchor")
    for launch_path in (manifest_path, seal_path):
        if not launch_path.is_file() or launch_path.is_symlink():
            raise ValidationError(f"launch anchor is not a plain file: {launch_path}")
        try:
            relative = launch_path.resolve().relative_to(REPO.resolve()).as_posix()
        except ValueError as error:
            raise ValidationError("launch anchor is outside repository") from error
        committed = subprocess.run(
            ["/usr/bin/git", "show", f"{origin}:{relative}"], cwd=REPO,
            env=CLEAN_PYTHON_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False,
        )
        if committed.returncode != 0 or committed.stdout != launch_path.read_bytes():
            raise ValidationError(
                f"{launch_path.name} is not byte-identical to local origin/main"
            )
    payload_hash(seal, "runtime_payload_sha256")
    slurm_launcher = slurm_launcher_for_run_id(seal.get("run_id"))
    for name, expected_path in (
        ("seal_utility", SEAL_UTILITY),
        ("validator", SCRIPT),
        ("batch_launcher", BATCH_LAUNCHER),
        ("checkpoint_helper", CHECKPOINT_HELPER),
        ("slurm_launcher", slurm_launcher),
    ):
        if not expected_path.is_file() or expected_path.is_symlink():
            raise ValidationError(f"{name} is not a plain runtime file")
        binding = seal.get(name)
        if (type(binding) is not dict or binding.get("path") != str(expected_path.resolve())
                or binding.get("sha256") != sha_file(expected_path)
                or binding.get("size_bytes") != expected_path.stat().st_size):
            raise ValidationError(
                f"{name} does not match the origin-anchored runtime seal"
            )
    python_binding = seal.get("python_runtime")
    interpreter = Path(sys.executable).resolve()
    if (type(python_binding) is not dict
            or python_binding.get("path") != str(interpreter)
            or python_binding.get("sha256") != sha_file(interpreter)
            or python_binding.get("size_bytes") != interpreter.stat().st_size):
        raise ValidationError("validator is not running under the sealed Python interpreter")
    result = subprocess.run(
        [sys.executable, str(SEAL_UTILITY), "check", "--run-root", str(run), "--quiet"],
        cwd=REPO, env=CLEAN_PYTHON_ENV, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode != 0:
        raise ValidationError(f"runtime seal check failed: {(result.stderr or result.stdout).strip()}")
    return seal


def receipt_path(run: Path, record_id: str, attempt: int) -> Path:
    return run / "retrievals" / record_id / f"attempt_{attempt}.json"


def attempt_path(run: Path, record_id: str, arm: str, attempt: int) -> Path:
    return run / "attempts" / record_id / arm / f"attempt_{attempt}.json"


def audit_path(run: Path, record_id: str, arm: str, attempt: int) -> Path:
    return run / "audits" / "attempts" / record_id / arm / f"attempt_{attempt}.json"


def prompt_path(run: Path, record_id: str, arm: str, attempt: int) -> Path:
    return run / "prompts" / f"{record_id}__{arm}__attempt_{attempt}.json"


def audit_metadata_path(run: Path, record_id: str, arm: str, attempt: int) -> Path:
    return run / "prompts" / "audits" / record_id / arm / f"attempt_{attempt}.json"


def state_path(run: Path, record_id: str, arm: str, attempt: int, stage: str) -> Path:
    return run / "states" / f"{record_id}__{arm}__attempt_{attempt}__{stage}.json"


def independent_document_frequency(connection: sqlite3.Connection) -> tuple[Counter[str], int]:
    frequency: Counter[str] = Counter()
    rows = connection.execute(
        "SELECT id, refutes FROM entries ORDER BY id COLLATE BINARY"
    ).fetchall()
    for row in rows:
        for word in set(match.lower() for match in WORD_RE.findall(row["refutes"] or "")):
            if word not in STOP_WORDS:
                frequency[word] += 1
    return frequency, len(rows)


def independent_salient_terms(
    text: str, frequency: Counter[str], document_count: int,
) -> list[dict[str, Any]]:
    seen: dict[str, float] = {}
    for raw_word in WORD_RE.findall(text):
        word = raw_word.lower()
        if word in STOP_WORDS or len(word) < 3:
            continue
        if word not in seen:
            seen[word] = (document_count + 1) / (frequency.get(word, 0) + 1)
    ranked = sorted(seen.items(), key=lambda row: -row[1])[:12]
    return [
        {
            "term": term, "document_frequency": frequency.get(term, 0),
            "rarity_weight": weight,
        }
        for term, weight in ranked
    ]


def independent_hit(
    connection: sqlite3.Connection, row: sqlite3.Row, tables: set[str], rank: int,
) -> dict[str, Any]:
    entry = {column: row[column] for column in ENTRY_COLUMNS}
    entry_id = entry["id"]
    tags = (
        [item[0] for item in connection.execute(
            "SELECT tag FROM tags WHERE entry_id = ? ORDER BY tag COLLATE BINARY",
            (entry_id,),
        )]
        if "tags" in tables else []
    )
    related = (
        [item[0] for item in connection.execute(
            "SELECT related_id FROM relations WHERE entry_id = ? "
            "ORDER BY related_id COLLATE BINARY", (entry_id,),
        )]
        if "relations" in tables else []
    )
    citation = None
    if "sources" in tables and entry["source_book"] is not None:
        source = connection.execute(
            "SELECT citation FROM sources WHERE id = ?", (entry["source_book"],)
        ).fetchone()
        citation = source[0] if source is not None else None
    score = float(row["score"])
    hit: dict[str, Any] = {
        "rank": rank, "bm25": score, "bm25_binary64_hex": score.hex(),
        "entry_id": entry_id, "title": entry["title"], "type": entry["type"],
        "domain": entry["domain"], "subdomain": entry["subdomain"],
        "refutes": entry["refutes"], "statement": entry["statement"],
        "counterexample": entry["statement"], "true_theorem": entry["true_theorem"],
        "hypothesis_violated": entry["hypothesis_violated"],
        "source_book": entry["source_book"], "source_chapter": entry["source_chapter"],
        "source_item": entry["source_item"], "source_pages": entry["source_pages"],
        "source_citation": citation, "difficulty": entry["difficulty"],
        "status": entry["status"], "body_md": entry["body_md"], "path": entry["path"],
        "tags": tags, "related_entry_ids": related,
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
    return hit


def independently_retrieve(
    database: Path, parent: dict[str, Any], record_id: str, attempt: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    hash_before = sha_file(database)
    uri = f"file:{database.resolve().as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("BEGIN")
        table_rows = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name COLLATE BINARY"
        ).fetchall()
        tables = {row["name"] for row in table_rows}
        if not {"entries", "entries_fts"}.issubset(tables):
            raise ValidationError("BugBank database lacks required tables")
        frequency, count = independent_document_frequency(connection)
        queries: list[dict[str, Any]] = []
        for index, result in enumerate(parent["results"]):
            query_text = f"{result['claim']}\n\n{result['proof_sketch']}"
            terms = independent_salient_terms(query_text, frequency, count)
            expression = " OR ".join(f'"{row["term"]}"' for row in terms)
            rows = (
                connection.execute(RETRIEVAL_SQL, (expression, 3)).fetchall()
                if terms else []
            )
            hits = [
                independent_hit(connection, row, tables, rank)
                for rank, row in enumerate(rows, 1)
            ]
            queries.append({
                "query_id": f"{record_id}__bugbank__attempt_{attempt}__claim_{index}",
                "claim_index": index, "claim": result["claim"],
                "claim_sha256": sha_bytes(result["claim"].encode()),
                "proof_sketch_sha256": sha_bytes(result["proof_sketch"].encode()),
                "query_text_sha256": sha_bytes(query_text.encode()),
                "salient_terms": terms, "fts_match_expression": expression,
                "hit_count": len(hits), "hits": hits,
            })
        table_sql = {row["name"]: row["sql"] for row in table_rows}
        actual_columns = [
            row["name"] for row in connection.execute("PRAGMA table_info(entries)")
        ]
        status_counts = {
            row["status"]: row["count"] for row in connection.execute(
                "SELECT status, COUNT(*) AS count FROM entries "
                "GROUP BY status ORDER BY status COLLATE BINARY"
            )
        }
        metadata = {
            "entries_columns": actual_columns,
            "entries_schema_sha256": sha_bytes((table_sql["entries"] or "").encode()),
            "entries_fts_schema_sha256": sha_bytes((table_sql["entries_fts"] or "").encode()),
            "tables": sorted(table_sql),
            "sqlite_library_version": sqlite3.sqlite_version,
            "sqlite_user_version": connection.execute("PRAGMA user_version").fetchone()[0],
            "sqlite_schema_version": connection.execute("PRAGMA schema_version").fetchone()[0],
            "entry_count": count, "status_counts": status_counts,
        }
        if sha_file(database) != hash_before:
            raise ValidationError("BugBank database changed during independent replay")
        return queries, metadata
    finally:
        try:
            connection.rollback()
        finally:
            connection.close()


def validate_receipt(
    value: dict[str, Any], raw: bytes, *, run_id: str, record_id: str,
    attempt: int, parent: dict[str, Any], parent_path: Path,
    database: Path,
) -> list[str]:
    payload_hash(value, "receipt_payload_sha256")
    if (value.get("schema") != "paired_open_problem_extension_bugbank_receipt_v1"
            or value.get("run_id") != run_id or value.get("record_id") != record_id
            or value.get("arm") != "bugbank" or value.get("attempt") != attempt
            or value.get("stage") != "EXTENSION_BUGBANK_EXPOSURE"
            or value.get("status") != "COMPLETE"
            or value.get("parent", {}).get("sha256") != sha_file(parent_path)
            or value.get("parent", {}).get("size_bytes") != parent_path.stat().st_size
            or value.get("parent_claim_count") != len(parent["results"])
            or value.get("database", {}).get("path") != str(database.resolve())
            or value.get("database", {}).get("sha256") != sha_file(database)
            or value.get("script", {}).get("path") != str(FEEDBACK.resolve())
            or value.get("script", {}).get("sha256") != sha_file(FEEDBACK)
            or value.get("parameters", {}).get("k_per_claim") != 3
            or value.get("parameters", {}).get("query_text_basis")
                != "claim statement, two newlines, proof_sketch"
            or type(value.get("queries")) is not list
            or len(value["queries"]) != len(parent["results"])):
        raise ValidationError("BugBank extension receipt envelope mismatch")
    independently_replayed, database_metadata = independently_retrieve(
        database, parent, record_id, attempt
    )
    if value["queries"] != independently_replayed:
        raise ValidationError(
            f"receipt differs from independent pinned-SQLite replay {record_id}:{attempt}"
        )
    expected_parent_claims = [
        {
            "claim_index": index, "claim": row["claim"],
            "claim_sha256": sha_bytes(row["claim"].encode()),
            "proof_sketch_sha256": sha_bytes(row["proof_sketch"].encode()),
            "query_text_sha256": sha_bytes(
                f"{row['claim']}\n\n{row['proof_sketch']}".encode()
            ),
        }
        for index, row in enumerate(parent["results"])
    ]
    expected_binding = lambda path: {
        "path": str(path.resolve()), "sha256": sha_file(path),
        "size_bytes": path.stat().st_size,
    }
    if set(value) != {
        "schema", "run_id", "record_id", "arm", "attempt", "stage", "status",
        "parent", "parent_claim_count", "parent_claims", "parent_claims_sha256",
        "database", "script", "retrieval_core", "stock_retriever", "parameters",
        "queries", "exposure_summary", "timing", "receipt_payload_sha256",
    }:
        raise ValidationError("BugBank receipt top-level key envelope mismatch")
    expected_parent = {
        "path": str(parent_path.resolve()), "sha256": sha_file(parent_path),
        "size_bytes": parent_path.stat().st_size, "record_id": record_id,
        "arm": parent.get("arm"), "source_iteration": parent.get("iteration"),
        "extension_attempt": parent.get("attempt"),
    }
    expected_database = {
        **expected_binding(database),
        "open_mode": "SQLite URI mode=ro plus PRAGMA query_only",
        **database_metadata,
    }
    expected_parameters = {
        "k_per_claim": 3, "status_filter": "all", "exclude_self": False,
        "query_text_basis": "claim statement, two newlines, proof_sketch",
        "maximum_salient_terms": 12,
        "fts_bm25_weights": [2.0, 8.0, 4.0, 1.0, 1.0, 3.0],
        "ordering": ["bm25_score_ASC_unrounded", "entry_id_BINARY_ASC"],
        "query_sql_sha256": sha_bytes(RETRIEVAL_SQL.encode()),
    }
    if (value.get("parent") != expected_parent
            or value.get("parent_claims") != expected_parent_claims
            or value.get("parent_claims_sha256")
                != sha_bytes(canonical_bytes(expected_parent_claims))
            or value.get("database") != expected_database
            or value.get("script") != expected_binding(FEEDBACK)
            or value.get("retrieval_core") != expected_binding(RETRIEVAL_CORE)
            or value.get("stock_retriever") != expected_binding(STOCK_RETRIEVER)
            or value.get("parameters") != expected_parameters):
        raise ValidationError("BugBank receipt provenance/content envelope mismatch")
    timing = value.get("timing")
    if type(timing) is not dict or set(timing) != {
        "started_at", "ended_at", "duration_nanoseconds",
    } or type(timing.get("duration_nanoseconds")) is not int or timing["duration_nanoseconds"] < 0:
        raise ValidationError("BugBank receipt timing envelope mismatch")
    try:
        started = datetime.fromisoformat(timing["started_at"].replace("Z", "+00:00"))
        ended = datetime.fromisoformat(timing["ended_at"].replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise ValidationError("BugBank receipt timing is not ISO-8601") from error
    if not timing["started_at"].endswith("Z") or not timing["ended_at"].endswith("Z") or ended < started:
        raise ValidationError("BugBank receipt timing order/zone mismatch")
    retrieved: list[str] = []
    seen: set[str] = set()
    hit_count = 0
    for index, (query, row) in enumerate(zip(value["queries"], parent["results"])):
        query_text = f"{row['claim']}\n\n{row['proof_sketch']}"
        if (type(query) is not dict or query.get("claim_index") != index
                or query.get("claim") != row["claim"]
                or query.get("claim_sha256") != sha_bytes(row["claim"].encode())
                or query.get("proof_sketch_sha256") != sha_bytes(row["proof_sketch"].encode())
                or query.get("query_text_sha256") != sha_bytes(query_text.encode())
                or type(query.get("hits")) is not list
                or query.get("hit_count") != len(query["hits"])
                or len(query["hits"]) > 3):
            raise ValidationError(f"receipt query {index} mismatch")
        hit_count += len(query["hits"])
        previous: tuple[float, str] | None = None
        for hit in query["hits"]:
            if (type(hit) is not dict or not is_nonempty(hit.get("entry_id"))
                    or not all(SHA_RE.fullmatch(hit.get(field, "")) for field in (
                        "hit_payload_sha256", "entry_payload_sha256", "treatment_content_sha256"
                    ))):
                raise ValidationError("invalid receipt hit")
            key = (hit.get("bm25"), hit["entry_id"])
            if type(key[0]) not in {int, float} or (previous is not None and key < previous):
                raise ValidationError("receipt hit ordering mismatch")
            previous = key
            if hit["entry_id"] not in seen:
                seen.add(hit["entry_id"])
                retrieved.append(hit["entry_id"])
    if (value.get("exposure_summary", {}).get("query_count") != len(parent["results"])
            or value.get("exposure_summary", {}).get("hit_count") != hit_count
            or value.get("exposure_summary", {}).get("ordered_payload_sha256")
                != sha_bytes(canonical_bytes(value["queries"]))):
        raise ValidationError("receipt exposure summary mismatch")
    return retrieved


def validate_payload_metadata(value: dict[str, Any]) -> None:
    payload_hash(value, "metadata_payload_sha256")


def expected_revision_prompt(
    *, manifest: dict[str, Any], record_id: str, arm: str, attempt: int,
    source_path: Path, parent_path: Path, prior_audit_path: Path,
    receipt_file: Path | None, retrieved: list[str], scratch: Path,
) -> str:
    parent_hash = sha_file(parent_path)
    audit_hash = sha_file(prior_audit_path)
    audit_raw = prior_audit_path.read_text(encoding="utf-8")
    lens = manifest["protocol"]["neutral_lenses"][attempt - 1] if attempt <= 3 else None
    if lens is None:
        schedule = (
            "This is an exact-closure attempt after the three scheduled search lenses. "
            "Concentrate on resolving the independent audit. If no material proof change "
            "is required, copy claimed_resolution, every claim and proof_sketch, and "
            "final_writeup from the parent exactly."
        )
    else:
        schedule = (
            f"This is scheduled search attempt {attempt} of 3. Apply this predeclared "
            f"arm-neutral lens:\n\n{lens['name']}: {lens['instruction']}\n\n"
            "This valid attempt is required even if the parent is already a fixed point. "
            "If the lens and audit support no material proof change, copy claimed_resolution, "
            "every claim and proof_sketch, and final_writeup from the parent exactly."
        )
    common = f"""You are extending one independently audited open-problem draft in a sealed paired experiment.

Read only source /evidence/source.json, parent /evidence/parent.json, and independent audit /evidence/audit.json. Do not use the web, any prior-run file other than those exact sealed inputs, any other solution, or any verification report. You may create exact-arithmetic checks only under /work; do not modify files outside /work.

Parent SHA-256: {parent_hash}
Audit SHA-256: {audit_hash}

{schedule}

Address every REFUTED or UNRESOLVED claim and the audit's target-coverage judgment. Preserve correct progress. Repair, narrow, replace, or remove unsupported claims. Never call the open target solved without a complete proof at the requested strength. Put every load-bearing claim in a separate results item in proof order. There is no claim-count cap. The entire ordered proof is in scope. Keep final_writeup under 3,000 words and each proof_sketch under 500 words.

Complete independent audit:
--- BEGIN AUDIT ---
{audit_raw}--- END AUDIT ---

"""
    if arm == "plain":
        return common + (
            "Use native adversarial self-critique only. Do not read or use any retrieval "
            "result, external memory, treatment receipt, or database. Return revision-schema "
            "JSON. Use treatment_status PLAIN_SELF_CRITIQUE and empty receipt_path, "
            "receipt_sha256, retrieved_entry_ids, acted_on_entry_ids, and dismissed_hits."
        )
    if receipt_file is None:
        raise ValidationError("BugBank expected-prompt construction lacks receipt")
    receipt_raw = receipt_file.read_text(encoding="utf-8")
    retrieved_json = json.dumps(retrieved, ensure_ascii=False, indent=2)
    return common + (
        "Use the following complete diagnostic-memory receipt as fallible warnings, not "
        "authority. Independently check every applicable item. Each unique retrieved ID "
        "must appear exactly once: either in acted_on_entry_ids if it materially changes "
        "this attempt's proof state, or in dismissed_hits with a specific reason. Preserve "
        "first-retrieval order. If the parent already addresses an item and no proof change "
        "is needed, dismiss it rather than calling it acted on. The wrapper owns identity "
        "and lineage fields.\n\n--- BEGIN COMPLETE TREATMENT RECEIPT ---\n"
        f"{receipt_raw}--- END COMPLETE TREATMENT RECEIPT ---\n\n"
        "Return revision-schema JSON. Use treatment_status BUGBANK_RECEIPT_EXPOSED. Exact "
        f"unique retrieved_entry_ids:\n{retrieved_json}"
    )


def expected_audit_prompt(
    *, record_id: str, arm: str, attempt: int, source_path: Path,
    revision_path: Path, revision: dict[str, Any], scratch: Path,
) -> str:
    bindings = [
        {
            "idx": index, "claim": row["claim"],
            "claim_sha256": sha_bytes(row["claim"].encode()),
        }
        for index, row in enumerate(revision["results"])
    ]
    bindings_json = json.dumps(bindings, ensure_ascii=False, indent=2)
    quoted_id = json.dumps(record_id, ensure_ascii=False, separators=(",", ":"))
    return f"""You are the independent adversarial audit agent for extension attempt {attempt} of the {arm} arm.

Read only source /evidence/source.json and draft /evidence/parent.json. Do not read the revision prompt, retrieval database, treatment receipt, other arm, prior-run material, or any other solution. Do not use the web. Do not trust claimed_resolution or self_assessment.

Judge whether the draft proves the exact source target at the requested strength. FULLY_RESOLVES_TARGET requires a complete proof of the entire target. Use VALID_PARTIAL_PROGRESS for correct incomplete progress, NO_VALID_PROGRESS if nothing material survives, and OVERCLAIMED if the writeup claims coverage the proof does not establish. Separately label claimed_resolution ACCURATE, OVERSTATED, or UNDERSTATED.

Audit every listed claim from scratch. Look for missing cases, quantifier mistakes, statement/model mismatches, invalid reductions, and counterexamples. Write exact-arithmetic checks only under /work. Persist each checker there and return its /work/... path; otherwise use literal "none" where genuinely inapplicable. VERIFIED requires a rigorous complete proof. REFUTED requires a concrete reproducible flaw or counterexample. Otherwise use UNRESOLVED.

Parent SHA-256: {sha_file(revision_path)}
Exact claim bindings:
{bindings_json}

Return record_id {quoted_id}, stage REVISION_AUDIT, arm {arm}, iteration {attempt}, and the exact parent_sha256. Preserve every idx, claim, and claim_sha256. confirmed_refutations is exactly the increasing list of REFUTED indices. overall is REFUTED if any claim is refuted, VERIFIED only if every claim is verified, and INCONCLUSIVE otherwise. Return audit-schema JSON and do not modify repository files."""


def require_exact_prompt_text(actual: Any, expected: str, label: str) -> None:
    if actual != expected:
        raise ValidationError(f"{label} prompt differs from independent exact reconstruction")


def expected_os_exposure(
    *, seal: dict[str, Any], source_path: Path, parent_path: Path,
    audit_path: Path | None, schema_path: Path, scratch: Path,
) -> dict[str, Any]:
    mounts = [
        {"role": "source", "guest_path": "/evidence/source.json", "artifact": repo_artifact(source_path)},
        {"role": "parent", "guest_path": "/evidence/parent.json", "artifact": repo_artifact(parent_path)},
    ]
    if audit_path is not None:
        mounts.append({
            "role": "prior_independent_audit", "guest_path": "/evidence/audit.json",
            "artifact": repo_artifact(audit_path),
        })
    bwrap = seal["os_isolation"]["bwrap"]
    return {
        "schema": "paired_open_problem_extension_os_exposure_v1",
        "mechanism": "bubblewrap",
        "bwrap": {key: bwrap[key] for key in ("path", "sha256", "size_bytes")},
        "bwrap_execution_profile_sha256": sha_bytes(canonical_bytes(
            seal["os_isolation"]["execution_profile"]
        )),
        "evidence_mounts": mounts,
        "output_schema_mount": {
            "guest_path": "/evidence/output.schema.json", "artifact": repo_artifact(schema_path),
        },
        "writable_mount": {
            "guest_path": "/work", "host_path": str(scratch),
            "initial_state": "EMPTY_DIRECTORY_RESET_UNDER_CANONICAL_CELL_LOCK",
        },
        "codex_home_guest_path": "/run/codex-home",
        "operational_credential_injection": (
            "/run/codex-home/auth.json (bwrap --file from inherited fd 3; host path not mounted)"
        ),
        "credential_source_fd_lifecycle": "CONSUMED_AND_CLOSED_BEFORE_CODEX_EXEC",
        "credential_visibility_to_model_tools": "DENIED_BY_CUSTOM_PERMISSION_PROFILE",
        "model_cli_guest_path": "/runtime/vendor/bin/codex",
        "model_runtime_bundle_mount": copy.deepcopy(seal["model_runtime_bundle"]),
        "repository_mounted": False, "bugbank_database_mounted": False,
        "host_home_mounted": False, "network_namespace": "HOST_SHARED_FOR_MODEL_API",
    }


def validate_prompt_metadata(
    value: dict[str, Any], *, run: Path, manifest: dict[str, Any], seal: dict[str, Any], record_id: str,
    arm: str, attempt: int, source_path: Path, parent_path: Path,
    prior_audit_path: Path, receipt_file: Path | None, database: Path,
    retrieved: list[str],
) -> tuple[str, dict[str, Any]]:
    validate_payload_metadata(value)
    expected_keys = {
        "schema", "run_id", "record_id", "stage", "arm", "attempt",
        "claim_coverage_policy", "forced_neutral_lens", "phase", "prompt_text",
        "prompt_utf8_sha256", "prompt_size_bytes", "source", "parent", "audit",
        "receipt", "treatment_exposed", "requested_execution", "os_read_isolation", "created_at",
        "metadata_payload_sha256",
    }
    if set(value) != expected_keys or not is_nonempty(value.get("created_at")):
        raise ValidationError("revision prompt metadata key envelope mismatch")
    prompt = value.get("prompt_text")
    if (value.get("schema") != "paired_open_problem_extension_prompt_v1"
            or value.get("run_id") != manifest["run_id"]
            or value.get("record_id") != record_id
            or value.get("stage") != "EXTENSION_REVISION_PROMPT"
            or value.get("arm") != arm or value.get("attempt") != attempt
            or value.get("claim_coverage_policy") != "WHOLE_PROOF_UNCAPPED_V1"
            or not is_nonempty(prompt)
            or value.get("prompt_utf8_sha256") != sha_bytes(prompt.encode())
            or value.get("prompt_size_bytes") != len(prompt.encode())
            or not artifact_matches(value.get("source"), source_path)
            or not artifact_matches(value.get("parent"), parent_path)
            or not artifact_matches(value.get("audit"), prior_audit_path)
            or prior_audit_path.read_text(encoding="utf-8") not in prompt
            or "There is no claim-count cap." not in prompt):
        raise ValidationError(f"revision prompt metadata mismatch {record_id}:{arm}:{attempt}")
    requested = value.get("requested_execution")
    if requested != {
        "model": "gpt-5.6-sol", "reasoning_effort": "max",
        "sandbox": "outer-bwrap-read-isolated", "inner_sandbox": "custom-sealed-workspace",
        "user_config": "ignored", "model_tool_network": "denied-by-inner-sandbox",
        "web_search": "disabled", "shell_environment_inheritance": "none",
        "working_directory": "/work", "repository_writes_forbidden": True,
    }:
        raise ValidationError("prompt execution identity mismatch")
    expected_lens = (
        manifest["protocol"]["neutral_lenses"][attempt - 1]
        if attempt <= 3 else None
    )
    if (value.get("forced_neutral_lens") != expected_lens
            or value.get("phase") != (
                "FORCED_NEUTRAL_LENS" if attempt <= 3 else "POST_LENS_CLOSURE"
            )):
        raise ValidationError("neutral lens schedule mismatch")
    if expected_lens is not None and expected_lens["instruction"] not in prompt:
        raise ValidationError("scheduled neutral lens missing from prompt")
    expected_prompt = expected_revision_prompt(
        manifest=manifest, record_id=record_id, arm=arm, attempt=attempt,
        source_path=source_path, parent_path=parent_path,
        prior_audit_path=prior_audit_path, receipt_file=receipt_file,
        retrieved=retrieved,
        scratch=Path(manifest["operations"]["scratch_root"])
        / record_id / "revision" / arm / f"attempt_{attempt}",
    )
    require_exact_prompt_text(prompt, expected_prompt, "revision")
    scratch = Path(manifest["operations"]["scratch_root"]) / record_id / "revision" / arm / f"attempt_{attempt}"
    schema_path = run_binding(run, manifest["schemas"]["revision"], "revision schema")
    expected_exposure = expected_os_exposure(
        seal=seal, source_path=source_path, parent_path=parent_path,
        audit_path=prior_audit_path, schema_path=schema_path, scratch=scratch,
    )
    if value.get("os_read_isolation") != expected_exposure:
        raise ValidationError("revision OS exposure manifest mismatch")
    marker = "--- BEGIN COMPLETE TREATMENT RECEIPT ---"
    if arm == "plain":
        if (value.get("treatment_exposed") is not False or value.get("receipt") is not None
                or marker in prompt or sha_file(database) in prompt):
            raise ValidationError("plain prompt contains treatment evidence")
    else:
        if receipt_file is None or not receipt_file.is_file():
            raise ValidationError("BugBank prompt lacks receipt")
        receipt_raw = receipt_file.read_text(encoding="utf-8")
        if (value.get("treatment_exposed") is not True
                or not artifact_matches(value.get("receipt"), receipt_file)
                or prompt.count(receipt_raw) != 1 or prompt.count(marker) != 1):
            raise ValidationError("BugBank prompt did not expose one complete receipt")
    return prompt, expected_exposure


def validate_revision(
    value: dict[str, Any], *, run: Path, record_id: str, arm: str, attempt: int,
    parent_hash: str, prior_audit_hash: str, retrieved: list[str],
    receipt_file: Path | None,
) -> None:
    if set(value) != {
        "record_id", "stage", "arm", "iteration", "parent_sha256", "audit_sha256",
        "treatment_status", "receipt_path", "receipt_sha256", "retrieved_entry_ids",
        "acted_on_entry_ids", "dismissed_hits", "claimed_resolution", "results",
        "final_writeup", "audit_feedback_acted_on", "checks_performed", "self_assessment",
    }:
        raise ValidationError(f"revision key envelope mismatch {record_id}:{arm}:{attempt}")
    if (not valid_draft_core(value) or value.get("record_id") != record_id
            or value.get("stage") != "REVISION" or value.get("arm") != arm
            or value.get("iteration") != attempt or value.get("parent_sha256") != parent_hash
            or value.get("audit_sha256") != prior_audit_hash
            or type(value.get("audit_feedback_acted_on")) is not list
            or not all(is_nonempty(row) for row in value["audit_feedback_acted_on"])
            or type(value.get("retrieved_entry_ids")) is not list
            or type(value.get("acted_on_entry_ids")) is not list
            or type(value.get("dismissed_hits")) is not list):
        raise ValidationError(f"revision contract mismatch {record_id}:{arm}:{attempt}")
    if (any(set(row) != {"claim", "proof_sketch"} for row in value["results"])
            or any(type(row) is not dict or set(row) != {"entry_id", "reason"}
                   for row in value["dismissed_hits"])):
        raise ValidationError("revision nested key envelope mismatch")
    if arm == "plain":
        if (value.get("treatment_status") != "PLAIN_SELF_CRITIQUE"
                or value.get("receipt_path") != "" or value.get("receipt_sha256") != ""
                or value["retrieved_entry_ids"] != [] or value["acted_on_entry_ids"] != []
                or value["dismissed_hits"] != []):
            raise ValidationError("plain revision contains treatment bookkeeping")
        return
    expected_receipt_path = receipt_file.resolve().relative_to(REPO.resolve()).as_posix()
    if (value.get("treatment_status") != "BUGBANK_RECEIPT_EXPOSED"
            or value.get("receipt_path") != expected_receipt_path
            or value.get("receipt_sha256") != sha_file(receipt_file)
            or value["retrieved_entry_ids"] != retrieved
            or len(value["acted_on_entry_ids"]) != len(set(value["acted_on_entry_ids"]))
            or not all(item in retrieved for item in value["acted_on_entry_ids"])
            or not all(
                type(row) is dict and is_nonempty(row.get("entry_id"))
                and is_nonempty(row.get("reason")) for row in value["dismissed_hits"]
            )):
        raise ValidationError("BugBank revision treatment mismatch")
    acted = set(value["acted_on_entry_ids"])
    expected_acted = [item for item in retrieved if item in acted]
    expected_dismissed = [item for item in retrieved if item not in acted]
    if (value["acted_on_entry_ids"] != expected_acted
            or [row["entry_id"] for row in value["dismissed_hits"]] != expected_dismissed):
        raise ValidationError("BugBank treatment partition mismatch")


def validate_audit_metadata(
    value: dict[str, Any], *, run: Path, manifest: dict[str, Any], seal: dict[str, Any], record_id: str,
    arm: str, attempt: int, source_path: Path, revision_path: Path,
    audit: dict[str, Any], receipt_file: Path | None,
) -> tuple[str, dict[str, Any]]:
    validate_payload_metadata(value)
    if set(value) != {
        "schema", "run_id", "record_id", "stage", "arm", "attempt", "source",
        "parent", "prompt_text", "prompt_utf8_sha256", "prompt_size_bytes",
        "checker_artifacts", "requested_execution", "os_read_isolation", "metadata_payload_sha256",
    }:
        raise ValidationError("audit metadata key envelope mismatch")
    prompt = value.get("prompt_text")
    if (value.get("schema") != "paired_open_problem_extension_audit_metadata_v1"
            or value.get("run_id") != manifest["run_id"]
            or value.get("record_id") != record_id or value.get("arm") != arm
            or value.get("attempt") != attempt or value.get("stage") != "REVISION_AUDIT"
            or not is_nonempty(prompt)
            or value.get("prompt_utf8_sha256") != sha_bytes(prompt.encode())
            or value.get("prompt_size_bytes") != len(prompt.encode())
            or not artifact_matches(value.get("source"), source_path)
            or not artifact_matches(value.get("parent"), revision_path)
            or "There is no claim-count cap." in prompt
            or "--- BEGIN COMPLETE TREATMENT RECEIPT ---" in prompt
            or (receipt_file is not None
                and receipt_file.read_text(encoding="utf-8") in prompt)):
        raise ValidationError("audit metadata or independence mismatch")
    requested = value.get("requested_execution")
    if requested != {
        "model": "gpt-5.6-sol", "reasoning_effort": "max",
        "sandbox": "outer-bwrap-read-isolated", "inner_sandbox": "custom-sealed-workspace",
        "user_config": "ignored", "model_tool_network": "denied-by-inner-sandbox",
        "web_search": "disabled", "shell_environment_inheritance": "none",
        "working_directory": "/work", "repository_writes_forbidden": True,
    }:
        raise ValidationError("audit execution identity mismatch")
    expected_prompt = expected_audit_prompt(
        record_id=record_id, arm=arm, attempt=attempt,
        source_path=source_path, revision_path=revision_path,
        revision=load_json(revision_path),
        scratch=Path(manifest["operations"]["scratch_root"])
        / record_id / "audit" / arm / f"attempt_{attempt}",
    )
    require_exact_prompt_text(prompt, expected_prompt, "audit")
    scratch = Path(manifest["operations"]["scratch_root"]) / record_id / "audit" / arm / f"attempt_{attempt}"
    schema_path = run_binding(run, manifest["schemas"]["audit"], "audit schema")
    expected_exposure = expected_os_exposure(
        seal=seal, source_path=source_path, parent_path=revision_path,
        audit_path=None, schema_path=schema_path, scratch=scratch,
    )
    if value.get("os_read_isolation") != expected_exposure:
        raise ValidationError("audit OS exposure manifest mismatch")
    rows = value.get("checker_artifacts")
    if type(rows) is not list:
        raise ValidationError("checker artifact inventory missing")
    expected_indices = [
        index for index, claim in enumerate(audit["claims"])
        if claim["checker_path"] != "none"
    ]
    if [row.get("idx") for row in rows] != expected_indices:
        raise ValidationError("checker inventory indices mismatch")
    for row in rows:
        if set(row) != {
            "idx", "original_path", "original_sha256", "original_size_bytes", "durable",
        }:
            raise ValidationError("checker inventory key envelope mismatch")
        index = row["idx"]
        original = audit["claims"][index]["checker_path"]
        expected_scratch = (
            Path(manifest["operations"]["scratch_root"])
            / record_id / "audit" / arm / f"attempt_{attempt}"
        ).resolve()
        original_path = Path(original)
        resolved_original = original_path.resolve(strict=False)
        if (not original_path.is_absolute() or str(resolved_original) != original
                or resolved_original == expected_scratch
                or expected_scratch not in resolved_original.parents
                or row.get("original_path") != original):
            raise ValidationError("normalized checker path is outside exact audit scratch")
        durable = row.get("durable")
        if type(durable) is not dict or type(durable.get("path")) is not str:
            raise ValidationError("invalid durable checker binding")
        path = REPO / durable["path"]
        try:
            path.resolve().relative_to((run / "checkers").resolve())
        except ValueError as error:
            raise ValidationError("durable checker escapes run") from error
        expected_name = f"claim_{index}__{durable.get('sha256')}.checker"
        if (path.name != expected_name
                or not path.is_file() or path.is_symlink() or not artifact_matches(durable, path)
                or row.get("original_sha256") != durable["sha256"]
                or row.get("original_size_bytes") != durable["size_bytes"]):
            raise ValidationError("durable checker bytes mismatch")
        VALIDATED_RUNTIME_FILES.add(path.resolve())
    return prompt, expected_exposure


def validate_partial_checker_artifacts(
    *, run: Path, manifest: dict[str, Any], record_id: str, arm: str,
    attempt: int, audit: dict[str, Any],
) -> None:
    """Admit only an exact prefix of derivable checker copies before metadata.

    The copy loop can be killed between individual hard publications.  These
    files are operationally incomplete and never support an audited attempt
    until the complete audit metadata binds every one of them.
    """
    scratch = (
        Path(manifest["operations"]["scratch_root"])
        / record_id / "audit" / arm / f"attempt_{attempt}"
    ).resolve()
    expected: dict[int, tuple[Path, str, int]] = {}
    for index, claim in enumerate(audit["claims"]):
        original = claim["checker_path"]
        if original == "none":
            continue
        source = Path(original)
        resolved = source.resolve(strict=False)
        if (not source.is_absolute() or str(resolved) != original
                or resolved == scratch or scratch not in resolved.parents
                or not resolved.is_file() or source.is_symlink()):
            raise ValidationError("partial checker source escapes exact audit scratch")
        expected[index] = (resolved, sha_file(resolved), resolved.stat().st_size)
    directory = run / "checkers" / record_id / arm / f"attempt_{attempt}"
    if not directory.exists():
        return
    if not directory.is_dir() or directory.is_symlink():
        raise ValidationError("partial checker destination is not a plain directory")
    seen: set[int] = set()
    pattern = re.compile(r"^claim_([0-9]+)__([0-9a-f]{64})\.checker$")
    for path in directory.iterdir():
        match = pattern.fullmatch(path.name)
        if (match is None or not path.is_file() or path.is_symlink()
                or int(match.group(1)) in seen):
            raise ValidationError("noncanonical partial checker artifact")
        index, recorded_hash = int(match.group(1)), match.group(2)
        if index not in expected:
            raise ValidationError("partial checker has no corresponding audit claim")
        source, expected_hash, expected_size = expected[index]
        if (recorded_hash != expected_hash or sha_file(path) != expected_hash
                or path.stat().st_size != expected_size
                or path.read_bytes() != source.read_bytes()):
            raise ValidationError("partial checker differs from its exact scratch source")
        seen.add(index)
        VALIDATED_RUNTIME_FILES.add(path.resolve())
        OPERATIONAL_INCOMPLETE_FILES.add(path.resolve())


def execution_log_segment(path: Path, start_offset: int) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValidationError(f"missing plain execution log: {path}")
    raw = path.read_bytes()
    if (type(start_offset) is not int or start_offset < 0
            or start_offset > len(raw)):
        raise ValidationError("execution log segment offset is outside the log")
    segment = raw[start_offset:]
    try:
        relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError as error:
        raise ValidationError("execution log is outside the repository") from error
    return {
        "path": relative, "start_offset": start_offset,
        "size_bytes": len(segment), "sha256": sha_bytes(segment),
    }


def execution_log_prefix_sha(path: Path, start_offset: int) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValidationError(f"missing plain execution log: {path}")
    raw = path.read_bytes()
    if (type(start_offset) is not int or start_offset < 0
            or start_offset > len(raw)):
        raise ValidationError("execution log prefix offset is outside the log")
    return sha_bytes(raw[:start_offset])


def parse_model_log(
    path: Path, start_offset: int = 0,
) -> tuple[int | None, str | None, str | None]:
    # Bind telemetry to this invocation's append-only slice.  Parsing the
    # entire canonical log could otherwise attribute an earlier failed call's
    # model identity or token count to a recovered later call.
    binding = execution_log_segment(path, start_offset)
    raw = path.read_bytes()
    text = raw[start_offset:start_offset + binding["size_bytes"]].decode(
        "utf-8", errors="replace",
    )
    tokens = re.findall(r"tokens used\s*\r?\n\s*([0-9][0-9,]*)", text, re.I)
    models = re.findall(r"^model:\s*(\S.*?)\s*$", text, re.I | re.M)
    efforts = re.findall(r"^reasoning effort:\s*(\S.*?)\s*$", text, re.I | re.M)
    return (
        int(tokens[-1].replace(",", "")) if tokens else None,
        models[-1].strip() if models else None,
        efforts[-1].strip() if efforts else None,
    )


def validate_model_state(
    value: dict[str, Any], *, run: Path, manifest: dict[str, Any], seal: dict[str, Any],
    record_id: str, arm: str, attempt: int, stage: str,
    prompt: str, parent_hash: str, audit_hash: str | None,
    output_path: Path, finalized_metadata_path: Path | None,
    os_exposure: dict[str, Any],
) -> int:
    common_keys = {
        "record_id", "arm", "attempt", "stage", "status", "started_at", "ended_at",
        "duration_seconds", "error", "tokens_used", "model", "reasoning_effort",
        "launcher_pid", "launcher_process_start_ticks",
        "execution_log_start_offset", "execution_log_prefix_sha256",
        "execution_log_segment",
        "extension_manifest_sha256", "runtime_seal_sha256", "runtime_payload_sha256",
        "runner_sha256", "parent_sha256", "prompt_sha256", "prompt_size_bytes",
        "os_read_isolation_sha256", "output", "finalized_metadata",
    }
    stage_keys = (
        {"audit_sha256", "prompt_metadata_sha256", "neutral_lens_attempt", "receipt_sha256"}
        if stage == "revision" else {"audit_output_normalizer"}
    )
    if set(value) != common_keys | stage_keys:
        raise ValidationError(f"model state key envelope mismatch {record_id}:{arm}:{attempt}:{stage}")
    if (value.get("record_id") != record_id or value.get("arm") != arm
            or value.get("attempt") != attempt or value.get("stage") != stage
            or value.get("status") != "COMPLETE"
            or not is_token_count(value.get("tokens_used"))
            or value.get("model") != "gpt-5.6-sol"
            or value.get("reasoning_effort") != "max"
            or type(value.get("launcher_pid")) is not int or value["launcher_pid"] < 1
            or re.fullmatch(r"[0-9]+", value.get("launcher_process_start_ticks", "")) is None
            or value.get("parent_sha256") != parent_hash
            or value.get("prompt_sha256") != sha_bytes(prompt.encode())
            or value.get("prompt_size_bytes") != len(prompt.encode())
            or value.get("extension_manifest_sha256")
                != sha_file(run / "EXTENSION_MANIFEST.json")
            or value.get("runtime_seal_sha256") != sha_file(run / "RUNTIME_SEAL.json")
            or value.get("runtime_payload_sha256") != seal["runtime_payload_sha256"]
            or value.get("runner_sha256") != seal["runner"]["sha256"]
            or not is_nonempty(value.get("started_at"))
            or not is_nonempty(value.get("ended_at"))
            or type(value.get("duration_seconds")) not in {int, float}
            or value["duration_seconds"] < 0 or value.get("error") is not None):
        raise ValidationError(f"model state mismatch {record_id}:{arm}:{attempt}:{stage}")
    start_offset = value.get("execution_log_start_offset")
    if type(start_offset) is not int or start_offset < 0:
        raise ValidationError("model state has an invalid execution-log offset")
    expected_finalized = (
        repo_artifact(finalized_metadata_path)
        if finalized_metadata_path is not None else None
    )
    if (not artifact_matches(value.get("output"), output_path)
            or value.get("finalized_metadata") != expected_finalized):
        raise ValidationError("model state does not bind finalized output/metadata bytes")
    if stage == "revision":
        prompt_metadata_file = prompt_path(run, record_id, arm, attempt)
        expected_lens = attempt if attempt <= 3 else None
        expected_receipt = (
            sha_file(receipt_path(run, record_id, attempt)) if arm == "bugbank" else None
        )
        if (value.get("audit_sha256") != audit_hash
                or value.get("prompt_metadata_sha256") != sha_file(prompt_metadata_file)
                or value.get("neutral_lens_attempt") != expected_lens
                or value.get("receipt_sha256") != expected_receipt):
            raise ValidationError("revision state lineage/prompt/treatment binding mismatch")
    if stage == "audit" and value.get("audit_output_normalizer") != "DERIVABLE_FIELDS_ONLY_V1":
        raise ValidationError("audit state lacks sealed derivable-only normalizer identity")
    if value.get("os_read_isolation_sha256") != sha_bytes(canonical_bytes(os_exposure)):
        raise ValidationError("state OS exposure hash mismatch")
    log = run / "logs" / stage / f"{record_id}__{arm}__attempt_{attempt}.log"
    if value.get("execution_log_segment") != execution_log_segment(log, start_offset):
        raise ValidationError("state does not bind its exact execution-log segment")
    if value.get("execution_log_prefix_sha256") != execution_log_prefix_sha(log, start_offset):
        raise ValidationError("state does not bind its prior execution-log bytes")
    if parse_model_log(log, start_offset) != (value["tokens_used"], "gpt-5.6-sol", "max"):
        raise ValidationError("state token/model identity differs from execution log")
    VALIDATED_RUNTIME_FILES.add(log.resolve())
    return value["tokens_used"]


def validate_receipt_state(
    value: dict[str, Any], *, run: Path, seal: dict[str, Any], record_id: str,
    attempt: int, parent_hash: str, output_path: Path,
) -> None:
    if set(value) != {
        "record_id", "arm", "attempt", "stage", "status", "started_at", "ended_at",
        "duration_seconds", "error", "parent_sha256", "retrieval_k", "tokens_used",
        "model", "reasoning_effort", "extension_manifest_sha256", "runtime_seal_sha256",
        "launcher_pid", "launcher_process_start_ticks",
        "runtime_payload_sha256", "runner_sha256", "execution_log_start_offset",
        "execution_log_prefix_sha256", "execution_log_segment", "output",
    }:
        raise ValidationError("receipt execution-state key envelope mismatch")
    if (value.get("record_id") != record_id or value.get("arm") != "bugbank"
            or value.get("attempt") != attempt or value.get("stage") != "receipt"
            or value.get("status") != "COMPLETE" or value.get("tokens_used") != 0
            or value.get("model") is not None or value.get("reasoning_effort") is not None
            or type(value.get("launcher_pid")) is not int or value["launcher_pid"] < 1
            or re.fullmatch(r"[0-9]+", value.get("launcher_process_start_ticks", "")) is None
            or value.get("parent_sha256") != parent_hash or value.get("retrieval_k") != 3
            or value.get("runtime_payload_sha256") != seal["runtime_payload_sha256"]
            or value.get("extension_manifest_sha256")
                != sha_file(run / "EXTENSION_MANIFEST.json")
            or value.get("runtime_seal_sha256") != sha_file(run / "RUNTIME_SEAL.json")
            or value.get("runner_sha256") != seal["runner"]["sha256"]
            or not is_nonempty(value.get("started_at"))
            or not is_nonempty(value.get("ended_at"))
            or type(value.get("duration_seconds")) not in {int, float}
            or value["duration_seconds"] < 0 or value.get("error") is not None):
        raise ValidationError("receipt execution state mismatch")
    if not artifact_matches(value.get("output"), output_path):
        raise ValidationError("receipt state does not bind finalized receipt bytes")
    log = run / "logs" / "receipt" / f"{record_id}__bugbank__attempt_{attempt}.log"
    if not log.is_file() or log.is_symlink():
        raise ValidationError("receipt execution log is missing")
    start_offset = value.get("execution_log_start_offset")
    if (type(start_offset) is not int or start_offset < 0
            or value.get("execution_log_segment")
            != execution_log_segment(log, start_offset)
            or value.get("execution_log_prefix_sha256")
            != execution_log_prefix_sha(log, start_offset)):
        raise ValidationError("receipt state does not bind its exact execution-log segment")
    VALIDATED_RUNTIME_FILES.add(log.resolve())


def valid_utc_timestamp(value: Any) -> bool:
    if type(value) is not str or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def process_start_ticks(pid: Any) -> str | None:
    if type(pid) is not int or pid < 1:
        return None
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        boundary = raw.rfind(") ")
        if boundary < 0:
            return None
        fields = raw[boundary + 2:].strip().split()
        return fields[19] if re.fullmatch(r"[0-9]+", fields[19]) else None
    except (OSError, IndexError):
        return None


def validate_cell_lock_file(
    path: Path, *, record_id: str, arm: str, attempt: int, stage: str,
    started_at: str | None, launcher_pid: int | None = None,
    launcher_process_start_ticks: str | None = None,
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValidationError("retryable cell lock is not a plain file")
    lock = load_json(path)
    if (set(lock) != {
            "pid", "process_start_ticks", "id", "arm", "attempt", "stage", "started_at",
        }
            or type(lock.get("pid")) is not int or lock["pid"] < 1
            or re.fullmatch(r"[0-9]+", lock.get("process_start_ticks", "")) is None
            or lock.get("id") != record_id or lock.get("arm") != arm
            or lock.get("attempt") != attempt or lock.get("stage") != stage
            or not valid_utc_timestamp(lock.get("started_at"))
            or (started_at is not None and lock.get("started_at") != started_at)
            or (launcher_pid is not None and lock.get("pid") != launcher_pid)
            or (launcher_process_start_ticks is not None
                and lock.get("process_start_ticks") != launcher_process_start_ticks)):
        raise ValidationError("retryable cell lock identity mismatch")
    VALIDATED_RUNTIME_FILES.add(path.resolve())
    OPERATIONAL_INCOMPLETE_FILES.add(path.resolve())
    return lock


def validate_retryable_cell_lock(
    *, run: Path, value: dict[str, Any], record_id: str, arm: str,
    attempt: int, stage: str,
) -> None:
    path = run / "locks" / f"{record_id}__{arm}__attempt_{attempt}__{stage}.lock"
    if not path.exists():
        # This is the narrow crash window after a dead admission lock has been
        # retired but before its replacement is published.  The exact state
        # and log are still validated and remain operationally incomplete;
        # they never contribute an attempt, endpoint, or token total.
        if (value.get("status") == "RUNNING"
                and process_start_ticks(value.get("launcher_pid"))
                == value.get("launcher_process_start_ticks")):
            raise ValidationError("live RUNNING state owner is missing its admission lock")
        return
    lock = validate_cell_lock_file(
        path, record_id=record_id, arm=arm, attempt=attempt, stage=stage,
        started_at=None,
    )
    if lock["started_at"] == value.get("started_at"):
        if (lock["pid"] != value.get("launcher_pid")
                or lock["process_start_ticks"]
                != value.get("launcher_process_start_ticks")):
            raise ValidationError("same-admission lock/state process identity mismatch")
        return
    # A process can die after publishing its replacement admission lock but
    # before overwriting the prior retryable state.  Only a strictly newer
    # lock for this exact cell, with no output publication, is that window.
    state_time = datetime.fromisoformat(value["started_at"].replace("Z", "+00:00"))
    lock_time = datetime.fromisoformat(lock["started_at"].replace("Z", "+00:00"))
    output = (
        receipt_path(run, record_id, attempt) if stage == "receipt" else
        attempt_path(run, record_id, arm, attempt) if stage == "revision" else
        audit_path(run, record_id, arm, attempt)
    )
    if (lock_time <= state_time or output.exists()
            or Path(f"{output}.finalizing").exists()):
        raise ValidationError("cell lock/state mismatch is not a replacement-admission window")
    if (process_start_ticks(value.get("launcher_pid"))
            == value.get("launcher_process_start_ticks")):
        raise ValidationError("replacement admission overlaps the exact live prior owner")


def validate_incomplete_model_state(
    value: dict[str, Any], *, run: Path, seal: dict[str, Any], record_id: str,
    arm: str, attempt: int, stage: str, prompt: str, parent_hash: str,
    audit_hash: str | None, os_exposure: dict[str, Any],
) -> None:
    """Validate a retryable RUNNING/failed call with no canonical output.

    Such a state is operational evidence only.  It contributes neither an
    audited attempt nor endpoint tokens and may be overwritten by the next
    invocation for the same canonical cell.
    """
    identity_keys = {
        "record_id", "arm", "attempt", "stage", "status", "started_at",
        "launcher_pid", "launcher_process_start_ticks",
        "execution_log_start_offset",
        "execution_log_prefix_sha256",
        "extension_manifest_sha256", "runtime_seal_sha256",
        "runtime_payload_sha256", "runner_sha256", "parent_sha256",
        "prompt_sha256", "prompt_size_bytes", "os_read_isolation_sha256",
    }
    stage_keys = (
        {"audit_sha256", "prompt_metadata_sha256", "neutral_lens_attempt", "receipt_sha256"}
        if stage == "revision" else {"audit_output_normalizer"}
    )
    final_keys = {
        "ended_at", "duration_seconds", "error", "tokens_used", "model",
        "reasoning_effort", "execution_log_segment",
    }
    status = value.get("status")
    expected_keys = identity_keys | stage_keys | (
        set() if status == "RUNNING" else final_keys
    )
    if (status not in {"RUNNING", "FAILED", "SPAWN_FAILED"}
            or set(value) != expected_keys
            or value.get("record_id") != record_id or value.get("arm") != arm
            or value.get("attempt") != attempt or value.get("stage") != stage
            or value.get("parent_sha256") != parent_hash
            or value.get("prompt_sha256") != sha_bytes(prompt.encode())
            or value.get("prompt_size_bytes") != len(prompt.encode())
            or value.get("extension_manifest_sha256")
                != sha_file(run / "EXTENSION_MANIFEST.json")
            or value.get("runtime_seal_sha256") != sha_file(run / "RUNTIME_SEAL.json")
            or value.get("runtime_payload_sha256") != seal["runtime_payload_sha256"]
            or value.get("runner_sha256") != seal["runner"]["sha256"]
            or type(value.get("launcher_pid")) is not int or value["launcher_pid"] < 1
            or re.fullmatch(r"[0-9]+", value.get("launcher_process_start_ticks", "")) is None
            or value.get("os_read_isolation_sha256")
                != sha_bytes(canonical_bytes(os_exposure))
            or not valid_utc_timestamp(value.get("started_at"))
            or type(value.get("execution_log_start_offset")) is not int
            or value["execution_log_start_offset"] < 0
            or value.get("execution_log_prefix_sha256")
                != execution_log_prefix_sha(
                    run / "logs" / stage
                    / f"{record_id}__{arm}__attempt_{attempt}.log",
                    value["execution_log_start_offset"],
                )):
        raise ValidationError(
            f"invalid retryable model state {record_id}:{arm}:{attempt}:{stage}"
        )
    if stage == "revision":
        expected_receipt = (
            sha_file(receipt_path(run, record_id, attempt)) if arm == "bugbank" else None
        )
        if (value.get("audit_sha256") != audit_hash
                or value.get("prompt_metadata_sha256")
                    != sha_file(prompt_path(run, record_id, arm, attempt))
                or value.get("neutral_lens_attempt") != (attempt if attempt <= 3 else None)
                or value.get("receipt_sha256") != expected_receipt):
            raise ValidationError("retryable revision state lineage mismatch")
    elif value.get("audit_output_normalizer") != "DERIVABLE_FIELDS_ONLY_V1":
        raise ValidationError("retryable audit state normalizer mismatch")
    log = run / "logs" / stage / f"{record_id}__{arm}__attempt_{attempt}.log"
    if not log.is_file() or log.is_symlink():
        raise ValidationError("retryable model state lacks its canonical log")
    # RUNNING has no end-of-segment commitment because the admitted process
    # may still be appending.  The offset is nevertheless exact and bounded.
    if value["execution_log_start_offset"] > log.stat().st_size:
        raise ValidationError("retryable model log offset exceeds its log")
    if status != "RUNNING":
        tokens = value.get("tokens_used")
        model = value.get("model")
        effort = value.get("reasoning_effort")
        if (not valid_utc_timestamp(value.get("ended_at"))
                or type(value.get("duration_seconds")) not in {int, float}
                or value["duration_seconds"] < 0
                or not is_nonempty(value.get("error"))
                or (tokens is not None and not is_token_count(tokens))
                or model not in (None, "gpt-5.6-sol")
                or effort not in (None, "max")):
            raise ValidationError("invalid retryable completed-failure state")
        if value.get("execution_log_segment") != execution_log_segment(
            log, value["execution_log_start_offset"],
        ):
            raise ValidationError("retryable model state log-segment binding mismatch")
        if tokens is not None and parse_model_log(
            log, value["execution_log_start_offset"],
        ) != (tokens, model, effort):
            raise ValidationError("retryable state telemetry differs from its log tail")
    validate_retryable_cell_lock(
        run=run, value=value, record_id=record_id, arm=arm,
        attempt=attempt, stage=stage,
    )
    VALIDATED_RUNTIME_FILES.update({
        state_path(run, record_id, arm, attempt, stage).resolve(), log.resolve(),
    })
    OPERATIONAL_INCOMPLETE_FILES.add(
        state_path(run, record_id, arm, attempt, stage).resolve()
    )


def validate_incomplete_receipt_state(
    value: dict[str, Any], *, run: Path, seal: dict[str, Any], record_id: str,
    attempt: int, parent_hash: str,
) -> None:
    identity_keys = {
        "record_id", "arm", "attempt", "stage", "status", "started_at",
        "launcher_pid", "launcher_process_start_ticks",
        "execution_log_start_offset",
        "execution_log_prefix_sha256",
        "parent_sha256", "retrieval_k", "extension_manifest_sha256",
        "runtime_seal_sha256", "runtime_payload_sha256", "runner_sha256",
    }
    final_keys = {
        "ended_at", "duration_seconds", "error", "tokens_used", "model",
        "reasoning_effort", "execution_log_segment", "output",
    }
    status = value.get("status")
    expected_keys = identity_keys | (set() if status == "RUNNING" else final_keys)
    if (status not in {"RUNNING", "FAILED", "SPAWN_FAILED"}
            or set(value) != expected_keys
            or value.get("record_id") != record_id or value.get("arm") != "bugbank"
            or value.get("attempt") != attempt or value.get("stage") != "receipt"
            or value.get("parent_sha256") != parent_hash
            or value.get("retrieval_k") != 3
            or value.get("extension_manifest_sha256")
                != sha_file(run / "EXTENSION_MANIFEST.json")
            or value.get("runtime_seal_sha256") != sha_file(run / "RUNTIME_SEAL.json")
            or value.get("runtime_payload_sha256") != seal["runtime_payload_sha256"]
            or value.get("runner_sha256") != seal["runner"]["sha256"]
            or type(value.get("launcher_pid")) is not int or value["launcher_pid"] < 1
            or re.fullmatch(r"[0-9]+", value.get("launcher_process_start_ticks", "")) is None
            or not valid_utc_timestamp(value.get("started_at"))
            or type(value.get("execution_log_start_offset")) is not int
            or value["execution_log_start_offset"] < 0
            or value.get("execution_log_prefix_sha256")
                != execution_log_prefix_sha(
                    run / "logs" / "receipt"
                    / f"{record_id}__bugbank__attempt_{attempt}.log",
                    value["execution_log_start_offset"],
                )):
        raise ValidationError(f"invalid retryable receipt state {record_id}:{attempt}")
    if status != "RUNNING" and (
        not valid_utc_timestamp(value.get("ended_at"))
        or type(value.get("duration_seconds")) not in {int, float}
        or value["duration_seconds"] < 0
        or not is_nonempty(value.get("error"))
        or value.get("tokens_used") != 0 or value.get("model") is not None
        or value.get("reasoning_effort") is not None or value.get("output") is not None
    ):
        raise ValidationError("invalid retryable receipt failure state")
    log = run / "logs" / "receipt" / f"{record_id}__bugbank__attempt_{attempt}.log"
    if not log.is_file() or log.is_symlink():
        raise ValidationError("retryable receipt state lacks its canonical log")
    if value["execution_log_start_offset"] > log.stat().st_size:
        raise ValidationError("retryable receipt log offset exceeds its log")
    if (status != "RUNNING" and value.get("execution_log_segment")
            != execution_log_segment(log, value["execution_log_start_offset"])):
        raise ValidationError("retryable receipt state log-segment binding mismatch")
    validate_retryable_cell_lock(
        run=run, value=value, record_id=record_id, arm="bugbank",
        attempt=attempt, stage="receipt",
    )
    VALIDATED_RUNTIME_FILES.update({
        state_path(run, record_id, "bugbank", attempt, "receipt").resolve(),
        log.resolve(),
    })
    OPERATIONAL_INCOMPLETE_FILES.add(
        state_path(run, record_id, "bugbank", attempt, "receipt").resolve()
    )


def numbered_files(
    directory: Path, prefix: str = "attempt_", *, allow_finalizing: bool = False,
) -> list[tuple[int, Path]]:
    if not directory.exists():
        return []
    if not directory.is_dir() or directory.is_symlink():
        raise ValidationError(f"artifact directory is invalid: {directory}")
    rows: list[tuple[int, Path]] = []
    pattern = re.compile(rf"^{re.escape(prefix)}([1-9][0-9]*)\.json$")
    staging_pattern = re.compile(
        rf"^{re.escape(prefix)}([1-9][0-9]*)\.json\.finalizing$"
    )
    for path in directory.iterdir():
        match = pattern.fullmatch(path.name)
        if allow_finalizing and staging_pattern.fullmatch(path.name) is not None:
            if not path.is_file() or path.is_symlink():
                raise ValidationError(f"non-plain finalization staging file: {path}")
            continue
        if match is None or not path.is_file() or path.is_symlink():
            raise ValidationError(f"unexpected artifact in {directory}: {path.name}")
        rows.append((int(match.group(1)), path))
    rows.sort()
    numbers = [number for number, _ in rows]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValidationError(f"non-contiguous attempts in {directory}: {numbers}")
    if numbers and numbers[-1] > 50:
        raise ValidationError("attempt exceeds sealed cap 50")
    return rows


def numbered_finalizing_files(
    directory: Path, prefix: str = "attempt_",
) -> list[tuple[int, Path]]:
    if not directory.exists():
        return []
    pattern = re.compile(
        rf"^{re.escape(prefix)}([1-9][0-9]*)\.json\.finalizing$"
    )
    rows: list[tuple[int, Path]] = []
    for path in directory.iterdir():
        match = pattern.fullmatch(path.name)
        if match is None:
            continue
        if not path.is_file() or path.is_symlink():
            raise ValidationError(f"non-plain finalization staging file: {path}")
        rows.append((int(match.group(1)), path))
    rows.sort()
    if any(number > 50 for number, _ in rows):
        raise ValidationError("finalization staging attempt exceeds sealed cap")
    return rows


def numbered_arm_prompts(run: Path, record_id: str, arm: str) -> list[tuple[int, Path]]:
    directory = run / "prompts"
    rows: list[tuple[int, Path]] = []
    pattern = re.compile(
        rf"^{re.escape(record_id)}__{re.escape(arm)}__attempt_([1-9][0-9]*)\.json$"
    )
    if directory.exists():
        for path in directory.iterdir():
            match = pattern.fullmatch(path.name)
            if match is None:
                continue
            if not path.is_file() or path.is_symlink():
                raise ValidationError(f"non-plain revision prompt metadata: {path}")
            rows.append((int(match.group(1)), path))
    rows.sort()
    numbers = [number for number, _ in rows]
    if numbers != list(range(1, len(numbers) + 1)) or (numbers and numbers[-1] > 50):
        raise ValidationError(f"non-contiguous prompt attempts {record_id}:{arm}: {numbers}")
    return rows


def classify_prefix_shape(
    *, arm: str, revision_numbers: list[int], audit_numbers: list[int],
    audit_metadata_numbers: list[int], receipt_numbers: list[int],
    prompt_numbers: list[int], state_attempt_numbers: list[int],
    complete_audit_numbers: list[int],
) -> tuple[int, int | None]:
    """Return complete-audit count and the optional sole trailing attempt."""
    complete = len(complete_audit_numbers)
    complete_numbers = list(range(1, complete + 1))
    if complete_audit_numbers != complete_numbers:
        raise ValidationError("COMPLETE audit states are not a contiguous prefix")
    allowed = {complete, complete + 1}
    if len(audit_numbers) not in allowed or audit_numbers[:complete] != complete_numbers:
        raise ValidationError("audit output inventory is not a single stage prefix")
    if (len(audit_metadata_numbers) not in allowed
            or audit_metadata_numbers[:complete] != complete_numbers):
        raise ValidationError("audit metadata inventory is not a single stage prefix")
    if len(revision_numbers) not in allowed or len(prompt_numbers) not in allowed:
        raise ValidationError("revision/prompt inventory is not a single stage prefix")
    if (state_attempt_numbers != list(range(1, len(state_attempt_numbers) + 1))
            or (state_attempt_numbers and state_attempt_numbers[-1] > 50)
            or state_attempt_numbers[:complete] != complete_numbers
            or len(state_attempt_numbers) not in allowed):
        raise ValidationError("execution-state inventory is not a single attempt prefix")
    if revision_numbers[:complete] != complete_numbers or prompt_numbers[:complete] != complete_numbers:
        raise ValidationError("a fully audited attempt lacks its revision prompt or output")
    if len(revision_numbers) == complete + 1 and len(prompt_numbers) != complete + 1:
        raise ValidationError("trailing revision lacks its exact prompt metadata")
    if arm == "bugbank":
        if len(receipt_numbers) not in allowed or receipt_numbers[:complete] != complete_numbers:
            raise ValidationError("BugBank receipt inventory is not a single stage prefix")
        if (len(prompt_numbers) == complete + 1 or len(revision_numbers) == complete + 1) \
                and len(receipt_numbers) != complete + 1:
            raise ValidationError("BugBank trailing prompt/revision lacks its receipt")
    elif receipt_numbers:
        raise ValidationError("plain arm unexpectedly owns receipt artifacts")
    has_partial = any(len(rows) == complete + 1 for rows in (
        revision_numbers, audit_numbers, audit_metadata_numbers,
        prompt_numbers, receipt_numbers,
        state_attempt_numbers,
    ))
    if complete == 50 and has_partial:
        raise ValidationError("runtime artifacts exceed the 50-attempt cap")
    return complete, complete + 1 if has_partial else None


def seed_paths(
    run: Path, record: dict[str, Any], arm: str,
) -> tuple[Path, Path]:
    return (
        run_binding(run, record["arms"][arm]["revision"], "seed revision"),
        run_binding(run, record["arms"][arm]["audit"], "seed audit"),
    )


def validate_arm_attempts(
    *, run: Path, manifest: dict[str, Any], seal: dict[str, Any],
    record: dict[str, Any], arm: str, database: Path,
) -> ArmChainEvidence:
    record_id = record["record_id"]
    source_path = run_binding(run, record["input"], "source input")
    load_json(source_path)
    parent_path, prior_audit_path = seed_paths(run, record, arm)
    parent = load_json(parent_path)
    prior_audit = load_json(prior_audit_path)
    revision_directory = run / "attempts" / record_id / arm
    audit_directory = run / "audits" / "attempts" / record_id / arm
    receipt_directory = run / "retrievals" / record_id
    revisions = numbered_files(revision_directory, allow_finalizing=True)
    audits = numbered_files(audit_directory, allow_finalizing=True)
    audit_metadata = numbered_files(run / "prompts" / "audits" / record_id / arm)
    receipts = (
        numbered_files(receipt_directory, allow_finalizing=True)
        if arm == "bugbank" else []
    )
    revision_staging = dict(numbered_finalizing_files(revision_directory))
    audit_staging = dict(numbered_finalizing_files(audit_directory))
    receipt_staging = (
        dict(numbered_finalizing_files(receipt_directory)) if arm == "bugbank" else {}
    )
    prompts = numbered_arm_prompts(run, record_id, arm)
    state_directory = run / "states"
    state_pattern = re.compile(
        rf"^{re.escape(record_id)}__{re.escape(arm)}__attempt_([1-9][0-9]*)__"
        r"(receipt|revision|audit)\.json$"
    )
    states: dict[tuple[int, str], Path] = {}
    if state_directory.exists():
        for path in state_directory.glob(f"{record_id}__{arm}__attempt_*__*.json"):
            match = state_pattern.fullmatch(path.name)
            if match is None or not path.is_file() or path.is_symlink():
                raise ValidationError(f"noncanonical execution state: {path}")
            key = (int(match.group(1)), match.group(2))
            if key in states:
                raise ValidationError(f"duplicate execution state: {key}")
            states[key] = path
    lock_directory = run / "locks"
    lock_pattern = re.compile(
        rf"^{re.escape(record_id)}__{re.escape(arm)}__attempt_([1-9][0-9]*)__"
        r"(receipt|revision|audit)\.lock$"
    )
    locks: dict[tuple[int, str], Path] = {}
    if lock_directory.exists():
        for path in lock_directory.glob(f"{record_id}__{arm}__attempt_*__*.lock"):
            match = lock_pattern.fullmatch(path.name)
            if match is None or not path.is_file() or path.is_symlink():
                raise ValidationError(f"noncanonical cell lock: {path}")
            key = (int(match.group(1)), match.group(2))
            if key in locks:
                raise ValidationError(f"duplicate cell lock: {key}")
            locks[key] = path
    operational_attempts = sorted(
        {attempt for attempt, _stage in states}
        | {attempt for attempt, _stage in locks}
        | set(revision_staging) | set(audit_staging) | set(receipt_staging)
    )
    complete_audit_numbers = [
        number for number, _path in audit_metadata
        if (number, "audit") in states
        and load_json(states[(number, "audit")]).get("status") == "COMPLETE"
    ]
    complete_count, partial_attempt = classify_prefix_shape(
        arm=arm,
        revision_numbers=[number for number, _ in revisions],
        audit_numbers=[number for number, _ in audits],
        audit_metadata_numbers=[number for number, _ in audit_metadata],
        receipt_numbers=[number for number, _ in receipts],
        prompt_numbers=[number for number, _ in prompts],
        state_attempt_numbers=operational_attempts,
        complete_audit_numbers=complete_audit_numbers,
    )
    for label, rows in (
        ("revision", revision_staging), ("audit", audit_staging),
        ("receipt", receipt_staging),
    ):
        unexpected = set(rows) - ({partial_attempt} if partial_attempt is not None else set())
        if unexpected:
            raise ValidationError(f"{label} finalization staging is not the sole trailing prefix")
    revision_map = dict(revisions)
    audit_map = dict(audits)
    audit_metadata_map = dict(audit_metadata)
    receipt_map = dict(receipts)
    prompt_map = dict(prompts)
    expected_states: set[Path] = set()
    evidence: list[AttemptEvidence] = []
    for attempt in range(1, complete_count + 1):
        revision_file = revision_map[attempt]
        parent_hash = sha_file(parent_path)
        prior_audit_hash = sha_file(prior_audit_path)
        receipt_file: Path | None = None
        retrieved: list[str] = []
        if arm == "bugbank":
            receipt_file = receipt_map[attempt]
            receipt_raw = receipt_file.read_bytes()
            retrieved = validate_receipt(
                load_json(receipt_file), receipt_raw, run_id=manifest["run_id"],
                record_id=record_id, attempt=attempt, parent=parent,
                parent_path=parent_path, database=database,
            )
            validate_receipt_state(
                load_json(state_path(run, record_id, arm, attempt, "receipt")),
                run=run, seal=seal, record_id=record_id, attempt=attempt,
                parent_hash=parent_hash, output_path=receipt_file,
            )
            expected_states.add(state_path(
                run, record_id, arm, attempt, "receipt"
            ).resolve())
        prompt_file = prompt_map[attempt]
        prompt, revision_exposure = validate_prompt_metadata(
            load_json(prompt_file), run=run, manifest=manifest, seal=seal,
            record_id=record_id, arm=arm, attempt=attempt,
            source_path=source_path, parent_path=parent_path,
            prior_audit_path=prior_audit_path, receipt_file=receipt_file,
            database=database, retrieved=retrieved,
        )
        revision = load_json(revision_file)
        validate_revision(
            revision, run=run, record_id=record_id, arm=arm, attempt=attempt,
            parent_hash=parent_hash, prior_audit_hash=prior_audit_hash,
            retrieved=retrieved, receipt_file=receipt_file,
        )
        revision_tokens = validate_model_state(
            load_json(state_path(run, record_id, arm, attempt, "revision")),
            run=run, manifest=manifest, seal=seal, record_id=record_id,
            arm=arm, attempt=attempt, stage="revision", prompt=prompt,
            parent_hash=parent_hash, audit_hash=prior_audit_hash,
            output_path=revision_file, finalized_metadata_path=None,
            os_exposure=revision_exposure,
        )
        revision_hash = sha_file(revision_file)
        audit_file = audit_map[attempt]
        audit = load_json(audit_file)
        validate_audit(
            audit, record_id=record_id, arm=arm, attempt=attempt,
            parent=revision, parent_hash=revision_hash,
        )
        audit_prompt, audit_exposure = validate_audit_metadata(
            load_json(audit_metadata_map[attempt]),
            run=run, manifest=manifest, seal=seal, record_id=record_id, arm=arm,
            attempt=attempt, source_path=source_path, revision_path=revision_file,
            audit=audit, receipt_file=receipt_file,
        )
        audit_tokens = validate_model_state(
            load_json(state_path(run, record_id, arm, attempt, "audit")),
            run=run, manifest=manifest, seal=seal, record_id=record_id,
            arm=arm, attempt=attempt, stage="audit", prompt=audit_prompt,
            parent_hash=revision_hash, audit_hash=None, output_path=audit_file,
            finalized_metadata_path=audit_metadata_map[attempt],
            os_exposure=audit_exposure,
        )
        evidence.append(AttemptEvidence(
            number=attempt, parent=parent, revision=revision, audit=audit,
            revision_path=revision_file, audit_path=audit_file,
            tokens=add_token_counts(revision_tokens, audit_tokens),
        ))
        VALIDATED_RUNTIME_FILES.update({
            revision_file.resolve(), audit_file.resolve(), prompt_file.resolve(),
            audit_metadata_map[attempt].resolve(),
            state_path(run, record_id, arm, attempt, "revision").resolve(),
            state_path(run, record_id, arm, attempt, "audit").resolve(),
        })
        expected_states.update({
            state_path(run, record_id, arm, attempt, "revision").resolve(),
            state_path(run, record_id, arm, attempt, "audit").resolve(),
        })
        if receipt_file is not None:
            VALIDATED_RUNTIME_FILES.update({
                receipt_file.resolve(),
                state_path(run, record_id, arm, attempt, "receipt").resolve(),
            })
        parent_path, parent = revision_file, revision
        prior_audit_path, prior_audit = audit_file, audit

    next_reason = (
        "MISSING_RECEIPT" if arm == "bugbank"
        else "MISSING_OR_INVALID_PROMPT_METADATA"
    )
    partial_stage: str | None = None
    if partial_attempt is not None:
        attempt = partial_attempt
        parent_hash = sha_file(parent_path)
        prior_audit_hash = sha_file(prior_audit_path)
        receipt_file: Path | None = None
        retrieved: list[str] = []
        receipt_state = states.get((attempt, "receipt"))
        if arm == "bugbank":
            staged_receipt = receipt_staging.get(attempt)
            if staged_receipt is not None:
                staged_retrieved = validate_receipt(
                    load_json(staged_receipt), staged_receipt.read_bytes(),
                    run_id=manifest["run_id"], record_id=record_id,
                    attempt=attempt, parent=parent, parent_path=parent_path,
                    database=database,
                )
                if receipt_state is None:
                    raise ValidationError("staged receipt lacks its retryable state")
                if attempt in receipt_map and staged_receipt.read_bytes() != receipt_map[attempt].read_bytes():
                    raise ValidationError("published and staged receipt bytes conflict")
                VALIDATED_RUNTIME_FILES.add(staged_receipt.resolve())
                OPERATIONAL_INCOMPLETE_FILES.add(staged_receipt.resolve())
                retrieved = staged_retrieved
            if attempt in receipt_map:
                receipt_file = receipt_map[attempt]
                retrieved = validate_receipt(
                    load_json(receipt_file), receipt_file.read_bytes(),
                    run_id=manifest["run_id"], record_id=record_id,
                    attempt=attempt, parent=parent, parent_path=parent_path,
                    database=database,
                )
                receipt_state_path = state_path(
                    run, record_id, arm, attempt, "receipt"
                )
                receipt_state_value = load_json(receipt_state_path)
                if receipt_state_value.get("status") == "COMPLETE":
                    validate_receipt_state(
                        receipt_state_value, run=run, seal=seal,
                        record_id=record_id, attempt=attempt,
                        parent_hash=parent_hash, output_path=receipt_file,
                    )
                else:
                    validate_incomplete_receipt_state(
                        receipt_state_value, run=run, seal=seal,
                        record_id=record_id, attempt=attempt,
                        parent_hash=parent_hash,
                    )
                expected_states.add(receipt_state_path.resolve())
                VALIDATED_RUNTIME_FILES.add(receipt_file.resolve())
                next_reason = (
                    "MISSING_OR_INVALID_PROMPT_METADATA"
                    if receipt_state_value.get("status") == "COMPLETE"
                    else "INVALID_RECEIPT_STATE"
                )
                partial_stage = "receipt"
                if (receipt_state_value.get("status") != "COMPLETE"
                        and (attempt in prompt_map or attempt in revision_map
                             or (attempt, "revision") in states
                             or attempt in revision_staging)):
                    raise ValidationError("later stage follows an incomplete receipt state")
            elif receipt_state is not None:
                validate_incomplete_receipt_state(
                    load_json(receipt_state), run=run, seal=seal,
                    record_id=record_id, attempt=attempt,
                    parent_hash=parent_hash,
                )
                expected_states.add(receipt_state.resolve())
                partial_stage = "receipt"
                if staged_receipt is not None:
                    next_reason = "MISSING_RECEIPT"
            elif (attempt, "receipt") not in locks:
                raise ValidationError("BugBank partial attempt has no receipt stage evidence")
        elif receipt_state is not None:
            raise ValidationError("plain partial attempt has a receipt state")

        prompt_file = prompt_map.get(attempt)
        prompt: str | None = None
        revision_exposure: dict[str, Any] | None = None
        if prompt_file is not None:
            if arm == "bugbank" and receipt_file is None:
                raise ValidationError("BugBank prompt exists before a complete receipt")
            prompt, revision_exposure = validate_prompt_metadata(
                load_json(prompt_file), run=run, manifest=manifest, seal=seal,
                record_id=record_id, arm=arm, attempt=attempt,
                source_path=source_path, parent_path=parent_path,
                prior_audit_path=prior_audit_path, receipt_file=receipt_file,
                database=database, retrieved=retrieved,
            )
            VALIDATED_RUNTIME_FILES.add(prompt_file.resolve())
            next_reason = "MISSING_REVISION"
            partial_stage = "revision"

        revision_file = revision_map.get(attempt)
        revision_state = states.get((attempt, "revision"))
        staged_revision = revision_staging.get(attempt)
        if staged_revision is not None:
            if prompt is None or revision_exposure is None or revision_state is None:
                raise ValidationError("staged revision lacks prompt/state lineage")
            validate_revision(
                load_json(staged_revision), run=run, record_id=record_id,
                arm=arm, attempt=attempt, parent_hash=parent_hash,
                prior_audit_hash=prior_audit_hash, retrieved=retrieved,
                receipt_file=receipt_file,
            )
            if revision_file is not None and staged_revision.read_bytes() != revision_file.read_bytes():
                raise ValidationError("published and staged revision bytes conflict")
            VALIDATED_RUNTIME_FILES.add(staged_revision.resolve())
            OPERATIONAL_INCOMPLETE_FILES.add(staged_revision.resolve())
        if revision_file is not None:
            if prompt is None or revision_exposure is None:
                raise ValidationError("trailing revision lacks validated prompt metadata")
            revision = load_json(revision_file)
            validate_revision(
                revision, run=run, record_id=record_id, arm=arm,
                attempt=attempt, parent_hash=parent_hash,
                prior_audit_hash=prior_audit_hash, retrieved=retrieved,
                receipt_file=receipt_file,
            )
            revision_state_path = state_path(
                run, record_id, arm, attempt, "revision"
            )
            revision_state_value = load_json(revision_state_path)
            if revision_state_value.get("status") == "COMPLETE":
                validate_model_state(
                    revision_state_value, run=run, manifest=manifest,
                    seal=seal, record_id=record_id, arm=arm, attempt=attempt,
                    stage="revision", prompt=prompt, parent_hash=parent_hash,
                    audit_hash=prior_audit_hash, output_path=revision_file,
                    finalized_metadata_path=None, os_exposure=revision_exposure,
                )
            else:
                validate_incomplete_model_state(
                    revision_state_value, run=run, seal=seal,
                    record_id=record_id, arm=arm, attempt=attempt,
                    stage="revision", prompt=prompt, parent_hash=parent_hash,
                    audit_hash=prior_audit_hash, os_exposure=revision_exposure,
                )
            expected_states.add(revision_state_path.resolve())
            VALIDATED_RUNTIME_FILES.add(revision_file.resolve())
            next_reason = (
                "MISSING_AUDIT"
                if revision_state_value.get("status") == "COMPLETE"
                else "INVALID_REVISION_STATE"
            )
            partial_stage = "audit"
            if (revision_state_value.get("status") != "COMPLETE"
                    and ((attempt, "audit") in states or attempt in audit_map
                         or attempt in audit_staging or attempt in audit_metadata_map)):
                raise ValidationError("audit stage follows an incomplete revision state")
        elif revision_state is not None:
            if prompt is None or revision_exposure is None:
                raise ValidationError("retryable revision state lacks validated prompt")
            validate_incomplete_model_state(
                load_json(revision_state), run=run, seal=seal,
                record_id=record_id, arm=arm, attempt=attempt,
                stage="revision", prompt=prompt, parent_hash=parent_hash,
                audit_hash=prior_audit_hash, os_exposure=revision_exposure,
            )
            expected_states.add(revision_state.resolve())
            next_reason = "MISSING_REVISION"
            partial_stage = "revision"

        audit_state = states.get((attempt, "audit"))
        published_audit = audit_map.get(attempt)
        staged_audit = audit_staging.get(attempt)
        if published_audit is not None or staged_audit is not None:
            if revision_file is None or audit_state is None:
                raise ValidationError("orphaned audit output lacks revision/state lineage")
            revision = load_json(revision_file)
            for candidate in (published_audit, staged_audit):
                if candidate is None:
                    continue
                validate_audit(
                    load_json(candidate), record_id=record_id, arm=arm,
                    attempt=attempt, parent=revision,
                    parent_hash=sha_file(revision_file),
                )
                VALIDATED_RUNTIME_FILES.add(candidate.resolve())
                if candidate == staged_audit:
                    OPERATIONAL_INCOMPLETE_FILES.add(candidate.resolve())
            if (published_audit is not None and staged_audit is not None
                    and published_audit.read_bytes() != staged_audit.read_bytes()):
                raise ValidationError("published and staged audit bytes conflict")
        if audit_state is not None:
            if revision_file is None:
                raise ValidationError("retryable audit state exists before a complete revision")
            revision = load_json(revision_file)
            audit_scratch = (
                Path(manifest["operations"]["scratch_root"])
                / record_id / "audit" / arm / f"attempt_{attempt}"
            )
            audit_prompt = expected_audit_prompt(
                record_id=record_id, arm=arm, attempt=attempt,
                source_path=source_path, revision_path=revision_file,
                revision=revision, scratch=audit_scratch,
            )
            audit_exposure = expected_os_exposure(
                seal=seal, source_path=source_path, parent_path=revision_file,
                audit_path=None,
                schema_path=run_binding(run, manifest["schemas"]["audit"], "audit schema"),
                scratch=audit_scratch,
            )
            partial_audit_metadata = audit_metadata_map.get(attempt)
            if partial_audit_metadata is not None:
                if published_audit is None:
                    raise ValidationError("audit metadata exists before canonical audit publication")
                stored_prompt, stored_exposure = validate_audit_metadata(
                    load_json(partial_audit_metadata), run=run, manifest=manifest,
                    seal=seal, record_id=record_id, arm=arm, attempt=attempt,
                    source_path=source_path, revision_path=revision_file,
                    audit=load_json(published_audit), receipt_file=receipt_file,
                )
                if stored_prompt != audit_prompt or stored_exposure != audit_exposure:
                    raise ValidationError("orphaned audit metadata reconstruction mismatch")
                VALIDATED_RUNTIME_FILES.add(partial_audit_metadata.resolve())
            elif published_audit is not None or staged_audit is not None:
                validate_partial_checker_artifacts(
                    run=run, manifest=manifest, record_id=record_id, arm=arm,
                    attempt=attempt,
                    audit=load_json(
                        published_audit if published_audit is not None else staged_audit
                    ),
                )
            validate_incomplete_model_state(
                load_json(audit_state), run=run, seal=seal,
                record_id=record_id, arm=arm, attempt=attempt,
                stage="audit", prompt=audit_prompt,
                parent_hash=sha_file(revision_file), audit_hash=None,
                os_exposure=audit_exposure,
            )
            expected_states.add(audit_state.resolve())
            next_reason = (
                "INVALID_AUDIT_STATE" if partial_audit_metadata is not None
                else "MISSING_OR_INVALID_AUDIT_METADATA"
                if published_audit is not None else "MISSING_AUDIT"
            )
            partial_stage = "audit"

    for (lock_attempt, lock_stage), lock_file in locks.items():
        linked_state = states.get((lock_attempt, lock_stage))
        if linked_state is not None:
            state_value = load_json(linked_state)
            if state_value.get("status") in {"RUNNING", "FAILED", "SPAWN_FAILED"}:
                validate_retryable_cell_lock(
                    run=run, value=state_value, record_id=record_id, arm=arm,
                    attempt=lock_attempt, stage=lock_stage,
                )
            elif state_value.get("status") == "COMPLETE":
                # A kill after COMPLETE-state publication but before lock
                # retirement is restartable, but it must not look complete to
                # checkpoint/validation while the stale lock remains.
                validate_cell_lock_file(
                    lock_file, record_id=record_id, arm=arm,
                    attempt=lock_attempt, stage=lock_stage,
                    started_at=state_value.get("started_at"),
                    launcher_pid=state_value.get("launcher_pid"),
                    launcher_process_start_ticks=state_value.get(
                        "launcher_process_start_ticks"
                    ),
                )
            else:
                raise ValidationError("cell lock is linked to a noncanonical state status")
            continue
        if lock_attempt != partial_attempt:
            raise ValidationError("cell lock without state is outside the sole trailing prefix")
        if lock_stage == "receipt":
            if arm != "bugbank" or lock_attempt in receipt_map or lock_attempt in receipt_staging:
                raise ValidationError("orphaned receipt lock has impossible stage artifacts")
            next_reason, partial_stage = "MISSING_RECEIPT", "receipt"
        elif lock_stage == "revision":
            if lock_attempt in revision_map or lock_attempt in revision_staging:
                raise ValidationError("orphaned revision lock has output without state")
            if arm == "bugbank" and lock_attempt not in receipt_map:
                raise ValidationError("orphaned BugBank revision lock precedes its receipt")
            next_reason, partial_stage = "MISSING_OR_INVALID_PROMPT_METADATA", "revision"
        else:
            if lock_attempt not in revision_map or lock_attempt in audit_map \
                    or lock_attempt in audit_staging:
                raise ValidationError("orphaned audit lock has impossible stage artifacts")
            next_reason, partial_stage = "MISSING_AUDIT", "audit"
        validate_cell_lock_file(
            lock_file, record_id=record_id, arm=arm,
            attempt=lock_attempt, stage=lock_stage, started_at=None,
        )

    actual_states = {path.resolve() for path in states.values()}
    if actual_states != expected_states:
        raise ValidationError(
            f"execution-state prefix mismatch {record_id}:{arm}; "
            f"unexpected={sorted(str(path) for path in actual_states - expected_states)}"
        )
    # Every state has now passed the exact per-arm inventory check and its
    # status-specific validation. Register the complete inventory for the
    # final whole-tree closed-world check, including a valid trailing
    # COMPLETE call whose next stage has not started yet.
    VALIDATED_RUNTIME_FILES.update(actual_states)
    return ArmChainEvidence(
        attempts=evidence, next_reason=next_reason,
        partial_attempt=partial_attempt, partial_stage=partial_stage,
    )


def independently_reconstruct_costs(
    run: Path, record_id: str, arm: str, through_attempt: int,
) -> dict[str, Any]:
    entries = []
    for attempt in range(1, through_attempt + 1):
        for stage in ("revision", "audit"):
            path = state_path(run, record_id, arm, attempt, stage)
            value = load_json(path)
            entries.append({
                "attempt": attempt, "stage": stage, "missing": False,
                "path": path.resolve().relative_to(REPO.resolve()).as_posix(),
                "status": value["status"], "tokens_used": value["tokens_used"],
                "model": value["model"], "reasoning_effort": value["reasoning_effort"],
                "duration_seconds": value.get("duration_seconds", 0),
                "identity_valid": (
                    value.get("record_id") == record_id and value.get("arm") == arm
                    and value.get("attempt") == attempt and value.get("stage") == stage
                    and value.get("model") == "gpt-5.6-sol"
                    and value.get("reasoning_effort") == "max"
                ),
            })
    return {
        "auditable": True,
        "tokens_used": add_token_counts(*(row["tokens_used"] for row in entries)),
        "entries": entries,
    }


def expected_terminal_arm(
    *, run: Path, record: dict[str, Any], arm: str,
    attempts: list[AttemptEvidence], endpoint: Endpoint,
    bugbank_endpoint: Endpoint, next_reason: str,
) -> dict[str, Any]:
    record_id = record["record_id"]
    seed_tokens = record["arms"][arm]["seed_lifetime_model_tokens"]
    through = endpoint.attempt if endpoint.terminal else len(attempts)
    costs = independently_reconstruct_costs(run, record_id, arm, through)
    incremental = costs["tokens_used"]
    if endpoint.incremental_tokens != incremental:
        raise ValidationError("independently derived endpoint/cost disagreement")
    if not endpoint.terminal:
        common = {
            "arm": arm, "status": endpoint.status, "terminal": False,
            "incremental_model_tokens_used": incremental,
            "incremental_token_cost_auditable": True,
            "seed_lifetime_model_tokens": seed_tokens,
            "lifetime_model_tokens_used": add_token_counts(seed_tokens, incremental),
        }
        if endpoint.status == "INCOMPLETE_MAX_ATTEMPTS":
            return {
                **common, "max_attempts_reached": True, "next_attempt": None,
                "reason": "No valid terminal endpoint was reached within 50 extension attempts.",
            }
        if endpoint.status == "INCOMPLETE_BUGBANK_NO_ENDPOINT":
            return {
                **common, "max_attempts_reached": False, "next_attempt": None,
                "reason": "BugBank exhausted 50 attempts without an endpoint, so the plain incremental target is undefined.",
            }
        if endpoint.status == "INCOMPLETE_WAITING_FOR_BUGBANK":
            return {
                **common, "next_attempt": None,
                "reason": (
                    "Plain is waiting for the BugBank extension endpoint."
                ),
            }
        return {
            **common, "next_attempt": len(attempts) + 1,
            "reason": next_reason,
        }
    evidence = attempts[endpoint.attempt - 1]
    unchanged = proof_state(evidence.parent) == proof_state(evidence.revision)
    claims_unchanged = [row["claim"] for row in evidence.parent["results"]] == [
        row["claim"] for row in evidence.revision["results"]
    ]
    target = (
        bugbank_endpoint.incremental_tokens
        if arm == "plain" and bugbank_endpoint.terminal else None
    )
    budget_auditable = arm == "bugbank" or bugbank_endpoint.terminal
    budget_matched = (
        True if arm == "bugbank" else
        budget_auditable and target is not None and incremental >= target
    )
    full = endpoint.status == "VERIFIED_FULL"
    row: dict[str, Any] = {
        "arm": arm, "status": endpoint.status, "terminal": True,
        "terminal_reason": (
            "FIRST_STRICT_INDEPENDENT_FULL_AUDIT" if full
            else "AUDITED_POST_LENS_FIXED_POINT"
        ),
        "attempt": endpoint.attempt,
        "reason": (
            "The first strict independent audit verified every claim and the complete exact target."
            if full else
            "After all three scheduled lenses, the exact proof state closed under an independent audit and the extension budget condition."
        ),
        "proof_state_unchanged": unchanged,
        "ordered_claim_set_unchanged": claims_unchanged,
        "audit_settled": audit_settled(evidence.audit),
        "no_acted_hits": arm == "plain" or evidence.revision["acted_on_entry_ids"] == [],
        "minimum_attempts_met": endpoint.attempt >= 3,
        "token_budget_target": target,
        "token_budget_matched": budget_matched,
        "token_budget_auditable": budget_auditable,
        "incremental_model_tokens_used": incremental,
        "incremental_token_cost_auditable": True,
        "seed_lifetime_model_tokens": seed_tokens,
        "lifetime_model_tokens_used": add_token_counts(seed_tokens, incremental),
        "claimed_resolution": evidence.revision["claimed_resolution"],
        "target_verdict": evidence.audit["target_verdict"],
        "audit_overall": evidence.audit["overall"],
        "claim_count": len(evidence.revision["results"]),
        "parent_proof_state_sha256": proof_hash(evidence.parent),
        "revision_proof_state_sha256": proof_hash(evidence.revision),
        "revision": repo_artifact(evidence.revision_path),
        "audit": repo_artifact(evidence.audit_path),
        "prompt_metadata": repo_artifact(prompt_path(
            run, record_id, arm, endpoint.attempt
        )),
        "receipt": (
            repo_artifact(receipt_path(run, record_id, endpoint.attempt))
            if arm == "bugbank" else None
        ),
        "execution_costs": costs,
    }
    return row


def validate_terminal(
    *, run: Path, manifest: dict[str, Any], record: dict[str, Any],
    bugbank: Endpoint, plain: Endpoint,
    bugbank_attempts: list[AttemptEvidence], plain_attempts: list[AttemptEvidence],
    bugbank_next_reason: str, plain_next_reason: str,
) -> str:
    record_id = record["record_id"]
    path = run / "terminals" / f"{record_id}.json"
    if not path.exists():
        return "INCOMPLETE"
    value = load_json(path)
    VALIDATED_RUNTIME_FILES.add(path.resolve())
    if (value.get("schema") != "paired_open_problem_extension_pair_terminal_v1"
            or value.get("run_id") != manifest["run_id"]
            or value.get("record_id") != record_id
            or value.get("stage") != "EXTENSION_PAIR_TERMINAL"
            or value.get("forced_audited_attempts") != 3
            or value.get("max_attempts") != 50 or value.get("retrieval_k") != 3
            or value.get("comparison_basis") != "EXTENSION_INCREMENTAL_MODEL_TOKENS"
            or SHA_RE.fullmatch(value.get("terminal_payload_sha256", "")) is None):
        raise ValidationError("pair terminal envelope mismatch")
    payload_hash(value, "terminal_payload_sha256")
    complete = bugbank.terminal and plain.terminal
    expected_arms = {
        "bugbank": expected_terminal_arm(
            run=run, record=record, arm="bugbank", attempts=bugbank_attempts,
            endpoint=bugbank, bugbank_endpoint=bugbank,
            next_reason=bugbank_next_reason,
        ),
        "plain": expected_terminal_arm(
            run=run, record=record, arm="plain", attempts=plain_attempts,
            endpoint=plain, bugbank_endpoint=bugbank,
            next_reason=plain_next_reason,
        ),
    }
    expected_difference = (
        plain.incremental_tokens - bugbank.incremental_tokens
        if plain.incremental_tokens is not None and bugbank.incremental_tokens is not None
        else None
    )
    expected_lifetime_difference = (
        expected_arms["plain"]["lifetime_model_tokens_used"]
        - expected_arms["bugbank"]["lifetime_model_tokens_used"]
        if plain.incremental_tokens is not None and bugbank.incremental_tokens is not None
        else None
    )
    expected_solved = [
        arm for arm, endpoint in (("bugbank", bugbank), ("plain", plain))
        if endpoint.status == "VERIFIED_FULL"
    ]
    expected_unsigned = {
        "schema": "paired_open_problem_extension_pair_terminal_v1",
        "run_id": manifest["run_id"], "record_id": record_id,
        "stage": "EXTENSION_PAIR_TERMINAL",
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "treatment_contrast_valid": complete,
        "forced_audited_attempts": 3, "max_attempts": 50, "retrieval_k": 3,
        "comparison_basis": "EXTENSION_INCREMENTAL_MODEL_TOKENS",
        "incremental_plain_minus_bugbank_tokens": expected_difference,
        "lifetime_plain_minus_bugbank_tokens": expected_lifetime_difference,
        "solved_arms": expected_solved,
        "seed_pair_terminal": repo_artifact(run_binding(
            run, record["seed_pair_terminal"], "seed pair terminal"
        )),
        "arms": expected_arms,
    }
    unsigned = copy.deepcopy(value)
    unsigned.pop("terminal_payload_sha256")
    if unsigned != expected_unsigned:
        raise ValidationError("pair terminal differs from complete independent reconstruction")
    if (plain.status == "INCONCLUSIVE_EXTENDED_FIXED_POINT"
            and (plain.incremental_tokens is None or bugbank.incremental_tokens is None
                 or plain.incremental_tokens < bugbank.incremental_tokens)):
        raise ValidationError("plain inconclusive endpoint does not satisfy P >= B")
    if plain.status == "INCONCLUSIVE_EXTENDED_FIXED_POINT":
        plain_row = value["arms"]["plain"]
        if (plain_row.get("token_budget_target") != bugbank.incremental_tokens
                or plain_row.get("token_budget_matched") is not True
                or plain_row.get("token_budget_auditable") is not True):
            raise ValidationError("stored plain incremental-budget parity mismatch")
    return value["status"]


def validate_record(
    run: Path, manifest: dict[str, Any], seal: dict[str, Any],
    record: dict[str, Any], database: Path,
) -> dict[str, Any]:
    record_id = record["record_id"]
    bugbank_chain = validate_arm_attempts(
        run=run, manifest=manifest, seal=seal, record=record,
        arm="bugbank", database=database,
    )
    bugbank_attempts = bugbank_chain.attempts
    bugbank = derive_endpoint("bugbank", bugbank_attempts, None)
    plain_chain = validate_arm_attempts(
        run=run, manifest=manifest, seal=seal, record=record,
        arm="plain", database=database,
    )
    plain_attempts = plain_chain.attempts
    plain = derive_endpoint("plain", plain_attempts, bugbank)
    if (bugbank.terminal and
            (len(bugbank_attempts) != bugbank.attempt
             or bugbank_chain.partial_attempt is not None)):
        raise ValidationError("BugBank continued after its first valid endpoint")
    if (plain.terminal and
            (len(plain_attempts) != plain.attempt
             or plain_chain.partial_attempt is not None)):
        raise ValidationError("plain continued after its first valid endpoint")
    if (plain.status in {"INCOMPLETE_WAITING_FOR_BUGBANK", "INCOMPLETE_BUGBANK_NO_ENDPOINT"}
            and plain_chain.partial_attempt is not None):
        raise ValidationError("plain has a partial call after its waiting boundary")
    terminal_status = validate_terminal(
        run=run, manifest=manifest, record=record, bugbank=bugbank, plain=plain,
        bugbank_attempts=bugbank_attempts, plain_attempts=plain_attempts,
        bugbank_next_reason=bugbank_chain.next_reason,
        plain_next_reason=plain_chain.next_reason,
    )
    return {
        "record_id": record_id, "status": terminal_status,
        "bugbank": bugbank.__dict__, "plain": plain.__dict__,
        "bugbank_attempts": len(bugbank_attempts), "plain_attempts": len(plain_attempts),
        "bugbank_partial_stage": bugbank_chain.partial_stage,
        "plain_partial_stage": plain_chain.partial_stage,
    }


def plain_files_below(root: Path) -> set[Path]:
    if not root.exists():
        return set()
    result: set[Path] = set()
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in directories:
            path = current_path / name
            if path.is_symlink():
                raise ValidationError(f"symlink directory in runtime evidence: {path}")
        for name in files:
            path = current_path / name
            if path.is_symlink() or not path.is_file():
                raise ValidationError(f"non-plain runtime artifact: {path}")
            result.add(path.resolve())
    return result


def plain_directories_below(root: Path) -> set[Path]:
    if not root.exists():
        return set()
    if not root.is_dir() or root.is_symlink():
        raise ValidationError(f"run root is not a plain directory: {root}")
    result: set[Path] = set()
    for current, directories, _files in os.walk(root, followlinks=False):
        current_path = Path(current)
        if current_path.is_symlink() or not current_path.is_dir():
            raise ValidationError(f"non-plain directory in runtime evidence: {current_path}")
        result.add(current_path.resolve())
        for name in directories:
            path = current_path / name
            if path.is_symlink() or not path.is_dir():
                raise ValidationError(f"symlink/non-directory in runtime evidence: {path}")
    return result


def allowed_run_directories(
    run: Path, manifest: dict[str, Any], allowed_files: set[Path],
) -> tuple[set[Path], set[Path]]:
    """Return required and possible exact directory envelopes.

    Possible directories include only names the sealed runner can create.  A
    possible-but-empty canonical directory is tolerated because SIGKILL can
    land between mkdir and the next atomic file publication.  Arbitrary empty
    directories are still closed-world violations.
    """
    run = run.resolve()
    fixed = {
        "attempts", "audits", "audits/attempts", "retrievals", "prompts",
        "states", "locks", "logs", "terminals", "summaries", "checkers",
    }
    eager = {"logs/receipt", "logs/revision", "logs/audit"}
    required = {run} | {(run / item).resolve() for item in fixed}
    possible = set(required) | {(run / item).resolve() for item in eager}
    for path in allowed_files:
        parent = path.resolve().parent
        while parent != run:
            try:
                parent.relative_to(run)
            except ValueError as error:
                raise ValidationError("allowed run file has an outside parent") from error
            required.add(parent)
            possible.add(parent)
            parent = parent.parent
    possible.add(run)
    for record in manifest["records"]:
        record_id = record["record_id"]
        possible.update({
            (run / "attempts" / record_id).resolve(),
            (run / "audits" / "attempts" / record_id).resolve(),
            (run / "retrievals" / record_id).resolve(),
            (run / "prompts" / "audits").resolve(),
            (run / "prompts" / "audits" / record_id).resolve(),
            (run / "checkers" / record_id).resolve(),
        })
        for arm in ("bugbank", "plain"):
            possible.update({
                (run / "attempts" / record_id / arm).resolve(),
                (run / "audits" / "attempts" / record_id / arm).resolve(),
                (run / "prompts" / "audits" / record_id / arm).resolve(),
                (run / "checkers" / record_id / arm).resolve(),
            })
            for attempt in range(1, 51):
                possible.add(
                    (run / "checkers" / record_id / arm / f"attempt_{attempt}").resolve()
                )
    for stage in ("receipt", "revision", "audit", "terminal"):
        possible.add((run / "summaries" / stage).resolve())
    return required, possible


def manifest_bound_files(run: Path, manifest: dict[str, Any]) -> set[Path]:
    bindings: list[dict[str, Any]] = [
        manifest["protocol"]["document"], manifest["problem_ids_artifact"],
        manifest["original"]["validation_report"], manifest["original"]["validator"],
        *manifest["schemas"].values(), *manifest["bootstrap"].values(),
    ]
    # exclusive_create is the sole non-binding bootstrap value.
    bindings = [row for row in bindings if type(row) is dict and "path" in row]
    bindings.extend(row["snapshot"] for row in manifest["original"]["artifact_lineage"])
    for record in manifest["records"]:
        bindings.extend((record["input"], record["seed_pair_terminal"]))
        for arm in ("bugbank", "plain"):
            bindings.extend((
                record["arms"][arm]["revision"], record["arms"][arm]["audit"],
                record["arms"][arm]["prompt_metadata"],
            ))
            if record["arms"][arm]["receipt"] is not None:
                bindings.append(record["arms"][arm]["receipt"])
    return {
        run_binding(run, binding, f"closed-world binding {index}").resolve()
        for index, binding in enumerate(bindings)
    }


def validate_closed_world(
    run: Path, manifest: dict[str, Any], report_path: Path | None,
) -> None:
    locks = plain_files_below(run / "locks")
    expected_locks = {
        path for path in VALIDATED_RUNTIME_FILES if (run / "locks").resolve() in path.parents
    }
    if locks != expected_locks:
        raise ValidationError(
            "closed-world retryable-lock mismatch; "
            f"unexpected={sorted(str(path) for path in locks - expected_locks)}"
        )
    actual_logs = plain_files_below(run / "logs")
    expected_logs = {
        path for path in VALIDATED_RUNTIME_FILES if (run / "logs").resolve() in path.parents
    }
    if actual_logs != expected_logs:
        raise ValidationError(
            "closed-world execution-log mismatch; "
            f"unexpected={sorted(str(path) for path in actual_logs - expected_logs)}"
        )
    for path in plain_files_below(run / "summaries"):
        value = load_json(path)
        expected_keys = {
            "schema", "run_id", "stage", "dry_run", "started_at", "ended_at",
            "selected", "complete", "failed", "tokens_used", "results",
        }
        results = value.get("results")
        stage = value.get("stage")
        try:
            relative = path.relative_to((run / "summaries").resolve())
        except ValueError as error:
            raise ValidationError(f"summary path escapes summary root: {path}") from error
        if type(results) is not list or any(type(row) is not dict for row in results):
            raise ValidationError(f"invalid runtime summary results: {path}")
        # Failed model calls legitimately report ``null`` when no complete
        # telemetry footer exists.  The runner counts those as zero in the
        # operational summary; every numeric contribution must still be an
        # exact, bounded token count and the combined total must not overflow.
        summary_token_rows = []
        for row in results:
            row_tokens = row.get("tokens_used", 0)
            if row_tokens is None:
                row_tokens = 0
            if not is_token_count(row_tokens):
                raise ValidationError(f"invalid runtime summary token row: {path}")
            summary_token_rows.append(row_tokens)
        try:
            summary_tokens = add_token_counts(*summary_token_rows)
        except ValidationError as error:
            raise ValidationError(f"invalid runtime summary token accounting: {path}") from error
        if (set(value) != expected_keys
                or value.get("schema") != "paired_open_problem_extension_stage_summary_v1"
                or value.get("run_id") != manifest["run_id"]
                or stage not in {"receipt", "revision", "audit", "terminal"}
                or len(relative.parts) != 2 or relative.parts[0] != stage
                or not relative.name.endswith(".json")
                or value.get("dry_run") is not False
                or value.get("selected") != len(results)
                or type(value.get("complete")) is not int
                or type(value.get("failed")) is not int
                or value["complete"] + value["failed"] != len(results)
                or value["complete"] != sum(
                    row.get("status") in {
                        "COMPLETE", "RECOVERED_COMPLETE", "SKIP_VALID", "PLANNED",
                        "ALREADY_TERMINAL",
                    }
                    for row in results
                )
                or not is_token_count(value.get("tokens_used"))
                or value.get("tokens_used") != summary_tokens
                or type(value.get("started_at")) is not str
                or type(value.get("ended_at")) is not str):
            raise ValidationError(f"invalid runtime summary: {path}")
        try:
            started = datetime.fromisoformat(value["started_at"].replace("Z", "+00:00"))
            ended = datetime.fromisoformat(value["ended_at"].replace("Z", "+00:00"))
        except ValueError as error:
            raise ValidationError(f"invalid runtime summary timestamp: {path}") from error
        if (not value["started_at"].endswith("Z") or not value["ended_at"].endswith("Z")
                or ended < started):
            raise ValidationError(f"invalid runtime summary timing: {path}")
        VALIDATED_RUNTIME_FILES.add(path)
    allowed = manifest_bound_files(run, manifest) | VALIDATED_RUNTIME_FILES | {
        (run / "EXTENSION_MANIFEST.json").resolve(),
        (run / "RUNTIME_SEAL.json").resolve(),
    }
    if report_path is not None and report_path.exists():
        if not report_path.is_file() or report_path.is_symlink():
            raise ValidationError("validation report path is not a plain file")
        prior_report = load_json(report_path)
        payload_hash(prior_report, "report_payload_sha256")
        if (set(prior_report) != {
                    "schema", "run_id", "status", "problem_count", "validated_count",
                    "records", "errors", "independent_validator_sha256",
                    "report_payload_sha256",
                }
                or prior_report.get("schema") != "paired_open_problem_extension_validation_report_v1"
                or prior_report.get("run_id") != manifest["run_id"]
                or prior_report.get("status") not in {
                    "INVALID", "VALID_COMPLETE", "VALID_INCOMPLETE",
                }
                or prior_report.get("problem_count") != len(manifest["records"])
                or type(prior_report.get("records")) is not list
                or prior_report.get("validated_count") != len(prior_report["records"])
                or type(prior_report.get("errors")) is not list
                or prior_report.get("independent_validator_sha256") != sha_file(SCRIPT)):
            raise ValidationError("existing validation report envelope mismatch")
        allowed.add(report_path.resolve())
    actual = plain_files_below(run)
    if actual != allowed:
        raise ValidationError(
            "whole-tree closed-world mismatch; "
            f"unexpected={sorted(str(path) for path in actual - allowed)}, "
            f"missing={sorted(str(path) for path in allowed - actual)}"
        )
    actual_directories = plain_directories_below(run)
    required_directories, possible_directories = allowed_run_directories(
        run, manifest, allowed,
    )
    if (not required_directories.issubset(actual_directories)
            or not actual_directories.issubset(possible_directories)):
        raise ValidationError(
            "whole-tree directory mismatch; "
            f"unexpected={sorted(str(path) for path in actual_directories - possible_directories)}, "
            f"missing={sorted(str(path) for path in required_directories - actual_directories)}"
        )


def atomic_report(
    path: Path, report: dict[str, Any], *, staging_root: Path,
) -> None:
    """Atomically create or replace the sole non-scientific validation report."""
    if os.path.lexists(path) and (path.is_symlink() or not path.is_file()):
        raise ValidationError("validation report target is not a plain file")
    report = copy.deepcopy(report)
    report["report_payload_sha256"] = sha_bytes(canonical_bytes(report))
    data = json.dumps(
        report, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2,
    ).encode("utf-8") + b"\n"
    staging_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    root_info = staging_root.lstat()
    if (not staging_root.is_dir() or staging_root.is_symlink()
            or root_info.st_mode & 0o077):
        raise ValidationError("private report scratch directory is unsafe")
    staging = staging_root / ".validator-atomic"
    staging.mkdir(parents=True, exist_ok=True, mode=0o700)
    for candidate, label in ((staging, "staging"),):
        info = candidate.lstat()
        if (not candidate.is_dir() or candidate.is_symlink()
                or info.st_mode & 0o077):
            raise ValidationError(f"private report {label} directory is unsafe")
    try:
        staging.resolve().relative_to(staging_root.resolve())
    except ValueError as error:
        raise ValidationError("report staging directory escapes scratch") from error
    descriptor, temporary_name = tempfile.mkstemp(
        dir=staging, prefix=f"{path.name}__", text=False,
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o644)
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short validation-report write")
            view = view[written:]
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument(
        "--report", type=Path,
        help="atomically refresh RUN_ROOT/VALIDATION_REPORT.json",
    )
    parser.add_argument(
        "--allow-incomplete", action="store_true",
        help="return success for valid but operationally incomplete evidence",
    )
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        VALIDATED_RUNTIME_FILES.clear()
        OPERATIONAL_INCOMPLETE_FILES.clear()
        run = safe_run_root(arguments.run_root)
        canonical_report = run / "VALIDATION_REPORT.json"
        report_path: Path | None = None
        if arguments.report is not None:
            requested_report = Path(os.path.abspath(arguments.report))
            if requested_report != canonical_report:
                raise ValidationError("--report must be exactly RUN_ROOT/VALIDATION_REPORT.json")
            report_path = canonical_report
        manifest = validate_manifest(run)
        seal = verify_runtime_seal(run)
        database = Path(seal["bugbank_database"]["path"])
        if not database.is_file() or sha_file(database) != manifest["bugbank"]["database_sha256"]:
            raise ValidationError("sealed BugBank database mismatch")
        records = []
        errors = []
        for record in manifest["records"]:
            try:
                records.append(validate_record(run, manifest, seal, record, database))
            except (ValidationError, OSError, KeyError, ValueError) as error:
                errors.append({"record_id": record.get("record_id"), "error": str(error)})
        if not errors:
            try:
                # A report from an earlier validation pass is the only permitted
                # mutable, derived file outside the scientific runtime roots.
                validate_closed_world(run, manifest, canonical_report)
            except (ValidationError, OSError, KeyError, ValueError) as error:
                errors.append({"record_id": None, "error": str(error)})
        complete = (
            not errors and not OPERATIONAL_INCOMPLETE_FILES
            and all(row["status"] == "COMPLETE" for row in records)
        )
        report = {
            "schema": "paired_open_problem_extension_validation_report_v1",
            "run_id": manifest["run_id"],
            "status": "INVALID" if errors else "VALID_COMPLETE" if complete else "VALID_INCOMPLETE",
            "problem_count": len(manifest["records"]),
            "validated_count": len(records), "records": records, "errors": errors,
            "independent_validator_sha256": sha_file(SCRIPT),
        }
        if report_path is not None:
            atomic_report(
                report_path, report,
                staging_root=Path(manifest["operations"]["scratch_root"]),
            )
        if not arguments.quiet:
            print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
        if errors:
            return 2
        return 0 if complete or arguments.allow_incomplete else 1
    except (ValidationError, OSError, KeyError, ValueError, subprocess.SubprocessError) as error:
        if not arguments.quiet:
            print(f"INVALID: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
