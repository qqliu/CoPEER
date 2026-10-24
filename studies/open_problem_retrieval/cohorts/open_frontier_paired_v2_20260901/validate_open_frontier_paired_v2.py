#!/usr/bin/env python3
"""Independently validate the fresh 31-problem paired open-frontier run.

This program is deliberately read-only and fail-closed.  It verifies the
preregistered problem universe, structured artifacts, byte-level lineage,
BugBank treatment receipts, prompt exposure/nonexposure, claim/audit binding,
and terminal-state semantics.  It never repairs or materializes an artifact.

Exit status is 0 for VALID_COMPLETE, 1 for INCOMPLETE without structural
errors, and 2 for INVALID.  ``--allow-incomplete`` maps the second case to 0
for monitoring jobs; the report status remains INCOMPLETE.
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
SOURCE_RUN = BASE / "runs/open_frontier_fable"
DEFAULT_RUN = BASE / "runs/open_frontier_paired_v2_20260901"
INPUTS = SOURCE_RUN / "inputs"
BUGBANK_DB = REPO / "BugBank/bugbank.sqlite"
FEEDBACK_SCRIPT = SCRIPT.parent / "open_frontier_paired_v2_feedback.py"
ACTIVE_FEEDBACK_SCRIPT = (
    SCRIPT.parent / "open_frontier_paired_v2_feedback_whole_proof_v2.py"
)
STOCK_RETRIEVER = SCRIPT.parent / "bugbank_retrieve.py"

RUN_ID = "open_frontier_paired_v2_20260901"
RECEIPT_SCHEMA = "open_frontier_paired_v2_bugbank_exposure_receipt_v1"
ACTIVE_RECEIPT_SCHEMA = "open_frontier_paired_v2_bugbank_exposure_receipt_v2"
CLAIM_COVERAGE_POLICY = "WHOLE_PROOF_UNCAPPED_V2"
CUTOVER_SCHEMA = "open_frontier_paired_v2_claim_coverage_cutover_v1"
CUTOVER_FILENAME = "CLAIM_COVERAGE_CUTOVER_20260902.json"
EXPECTED_SURPLUS_COMPLETED_MODEL_TOKENS = 659_334
AUDIT_METADATA_SCHEMA = "open_frontier_paired_v2_audit_metadata_v1"
PINNED_BUGBANK_SHA256 = (
    "a2b312e1e601d0f53c6a363530d9cf89462b92869dc63b28073537ac294ec15a"
)
ARMS = ("bugbank", "plain")
MAX_ITERATION = 50
RETRIEVAL_K = 3
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
BUGBANK_WORD = re.compile(r"[a-zA-Z][a-zA-Z-]{2,}")
BUGBANK_STOP = set(
    """a an and are as at be by for from has have if in into is it its of on
    or that the their there these this to was we which will with not no nor so then
    than let all any each every some such given hence thus where when suppose assume
    proof claim show shows shown implies follows since because therefore step case
    """.split()
)
BUGBANK_RETRIEVAL_SQL = """
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

# This literal roster is intentional: editing the source manifests cannot
# silently redefine the experimental population accepted by this validator.
EXPECTED_FUN_IDS = (
    "fun2026_max_bounded_sums_integer_linear",
    "fun2026_tiles_no_teleport_general",
    "fun2026_recursive_maze_linear",
    "fun2026_torus_push_tight_bounds",
    "fun2026_level3_additive_restoration",
    "fun2026_berlin_safe_house_better_than_two",
    "fun2026_careless_coupon_tight_hitting",
    "fun2026_magazine_marking_rounds",
    "fun2026_optimized_magazine_steps",
    "fun2026_pack_a9_in_a0",
    "fun2026_pack_a10_in_a1",
    "fun2026_pack_a9_in_a1",
    "fun2026_arrival_constant_level_width",
    "fun2026_swish_29_cards",
    "fun2026_fitting_hexasort_constant_threshold",
    "fun2026_wst_log_worstcase_updates",
    "fun2026_zombie_high_dimensional_grid",
    "fun2026_unrotatable_domino_survival",
    "fun2026_token_number_half_bound",
    "fun2026_planar_nemesis_fixed_exits",
    "fun2026_batdroid_fewer_than_77_shades",
    "fun2026_fog_chess_queen_win_within_50",
    "fun2026_mms_simultaneous_l_r_enumeration",
    "fun2026_happy_vertex_cographs",
)
EXPECTED_TCS_IDS = (
    "tcs_incremental_toposort_nsqrtm",
    "tcs_karp_rabin_collision_detection",
    "tcs_count_graphs_vc_at_most_k",
    "tcs_directed_cycle_above_min_outdegree",
    "tcs_h3_free_induced_disjoint_paths",
    "tcs_p8_free_bipartite_fvs",
    "tcs_k6_minus_edge_induced_minor",
)
EXPECTED_IDS = EXPECTED_FUN_IDS + EXPECTED_TCS_IDS
EXPECTED_SET = frozenset(EXPECTED_IDS)

ENTRY_COLUMNS = (
    "id", "title", "type", "domain", "subdomain", "refutes", "statement",
    "true_theorem", "hypothesis_violated", "source_book", "source_chapter",
    "source_item", "source_pages", "difficulty", "status", "body_md", "path",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
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


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        result = datetime.fromisoformat(normalized)
        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)
        return result
    except ValueError:
        return None


def rel(path: Path, run: Path | None = None) -> str:
    for root in (run, REPO):
        if root is None:
            continue
        try:
            return str(path.resolve().relative_to(root.resolve()))
        except (OSError, ValueError):
            pass
    return str(path)


def is_int(value: Any) -> bool:
    return type(value) is int


def is_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


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
    errors: list[dict[str, str]] = field(default_factory=list)
    incomplete: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)
    _seen: set[tuple[str, str, str, str]] = field(default_factory=set)

    def _add(self, target: list[dict[str, str]], code: str, path: Path | str,
             message: str, level: str) -> None:
        path_text = rel(path, self.run) if isinstance(path, Path) else str(path)
        key = (level, code, path_text, message)
        if key not in self._seen:
            self._seen.add(key)
            target.append({"code": code, "path": path_text, "message": message})

    def invalid(self, code: str, path: Path | str, message: str) -> None:
        self._add(self.errors, code, path, message, "INVALID")

    def missing(self, code: str, path: Path | str, message: str) -> None:
        self._add(self.incomplete, code, path, message, "INCOMPLETE")

    def warn(self, code: str, path: Path | str, message: str) -> None:
        self._add(self.warnings, code, path, message, "WARNING")


def load_json_artifact(path: Path, diagnostics: Diagnostics,
                       *, missing_code: str | None = None) -> Artifact | None:
    if not path.is_file():
        if missing_code is not None:
            diagnostics.missing(missing_code, path, "required artifact is absent")
        return None
    try:
        raw = path.read_bytes()
    except OSError as error:
        diagnostics.invalid("UNREADABLE_JSON", path, str(error))
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        diagnostics.invalid("MALFORMED_JSON", path, str(error))
        return None
    if type(value) is not dict:
        diagnostics.invalid("JSON_NOT_OBJECT", path, "top-level JSON must be an object")
        return None
    return Artifact(path, raw, value, sha_bytes(raw), len(raw))


def load_json_value(path: Path, diagnostics: Diagnostics) -> Any | None:
    if not path.is_file():
        diagnostics.invalid("MISSING_PREREQUISITE", path, "required prerequisite is absent")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        diagnostics.invalid("BAD_PREREQUISITE_JSON", path, str(error))
        return None


def resolve_recorded_path(value: str, run: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    candidates = (REPO / path, run / path, Path.cwd() / path)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


def same_recorded_path(value: Any, expected: Path, run: Path) -> bool:
    return isinstance(value, str) and bool(value) and (
        resolve_recorded_path(value, run) == expected.resolve()
    )


def schema_type_matches(value: Any, type_name: str) -> bool:
    return {
        "object": type(value) is dict,
        "array": type(value) is list,
        "string": type(value) is str,
        "integer": is_int(value),
        "number": is_number(value),
        "boolean": type(value) is bool,
        "null": value is None,
    }.get(type_name, False)


def resolve_schema_ref(root: Mapping[str, Any], reference: str) -> Mapping[str, Any] | None:
    if not reference.startswith("#/"):
        return None
    value: Any = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if type(value) is not dict or part not in value:
            return None
        value = value[part]
    return value if type(value) is dict else None


def validate_schema_instance(instance: Any, schema: Mapping[str, Any],
                             root: Mapping[str, Any], at: str = "$") -> list[str]:
    """Validate the JSON-Schema subset used by this run's three contracts."""
    errors: list[str] = []
    if "$ref" in schema:
        target = resolve_schema_ref(root, schema["$ref"])
        if target is None:
            return [f"{at}: unresolved schema reference {schema['$ref']!r}"]
        return validate_schema_instance(instance, target, root, at)
    if "allOf" in schema:
        for choice in schema["allOf"]:
            errors.extend(validate_schema_instance(instance, choice, root, at))
    if "anyOf" in schema:
        choices = [validate_schema_instance(instance, choice, root, at)
                   for choice in schema["anyOf"]]
        if choices and all(choice for choice in choices):
            errors.append(f"{at}: does not satisfy anyOf")
    if "oneOf" in schema:
        choices = [validate_schema_instance(instance, choice, root, at)
                   for choice in schema["oneOf"]]
        if sum(not choice for choice in choices) != 1:
            errors.append(f"{at}: does not satisfy exactly one oneOf branch")
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not schema_type_matches(instance, expected_type):
        return [f"{at}: expected {expected_type}, got {type(instance).__name__}"]
    if isinstance(expected_type, list) and not any(
            schema_type_matches(instance, item) for item in expected_type):
        return [f"{at}: expected one of {expected_type!r}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{at}: value {instance!r} is not in enum")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{at}: value does not equal const")
    if type(instance) is dict:
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{at}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{at}: unexpected property {key!r}")
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(validate_schema_instance(
                    instance[key], subschema, root, f"{at}.{key}"
                ))
    if type(instance) is list:
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{at}: fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{at}: more than maxItems")
        if schema.get("uniqueItems") is True:
            serialized = [canonical_bytes(item) for item in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{at}: items are not unique")
        item_schema = schema.get("items")
        if type(item_schema) is dict:
            for index, item in enumerate(instance):
                errors.extend(validate_schema_instance(
                    item, item_schema, root, f"{at}[{index}]"
                ))
    if type(instance) is str:
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{at}: shorter than minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{at}: longer than maxLength")
        if "pattern" in schema:
            try:
                if re.search(schema["pattern"], instance) is None:
                    errors.append(f"{at}: does not match pattern")
            except re.error as error:
                errors.append(f"{at}: invalid schema pattern: {error}")
    if is_number(instance):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{at}: less than minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{at}: greater than maximum")
    return errors


def apply_schema(artifact: Artifact, schema: Mapping[str, Any],
                 diagnostics: Diagnostics, label: str) -> bool:
    errors = validate_schema_instance(artifact.value, schema, schema)
    for message in errors:
        diagnostics.invalid("SCHEMA_VIOLATION", artifact.path, f"{label}: {message}")
    return not errors


def unique_strings(value: Any) -> bool:
    return (type(value) is list and all(type(item) is str and bool(item) for item in value)
            and len(value) == len(set(value)))


def expected_overall(claims: Sequence[Mapping[str, Any]]) -> str:
    verdicts = [claim.get("verdict") for claim in claims]
    if "REFUTED" in verdicts:
        return "REFUTED"
    if verdicts and all(verdict == "VERIFIED" for verdict in verdicts):
        return "VERIFIED"
    return "INCONCLUSIVE"


def validate_universe(diagnostics: Diagnostics) -> dict[str, Any]:
    result: dict[str, Any] = {
        "expected": len(EXPECTED_IDS),
        "fun_expected": len(EXPECTED_FUN_IDS),
        "tcs_expected": len(EXPECTED_TCS_IDS),
        "inputs_valid": 0,
        "input_sha256": {},
    }
    if len(EXPECTED_IDS) != 31 or len(EXPECTED_SET) != 31:
        diagnostics.invalid("INTERNAL_ROSTER_ERROR", SCRIPT,
                            "embedded roster is not 31 unique IDs")

    manifests = (
        (SOURCE_RUN / "problem_ids.json", list(EXPECTED_FUN_IDS)),
        (SOURCE_RUN / "problem_ids_dagstuhl.json", list(EXPECTED_TCS_IDS)),
    )
    for path, expected in manifests:
        value = load_json_value(path, diagnostics)
        if value != expected:
            diagnostics.invalid(
                "MANIFEST_ROSTER_MISMATCH", path,
                "manifest must equal the embedded ordered preregistered roster",
            )

    actual_files = set(INPUTS.glob("*.json")) if INPUTS.is_dir() else set()
    expected_files = {INPUTS / f"{record_id}.json" for record_id in EXPECTED_IDS}
    for path in sorted(expected_files - actual_files):
        diagnostics.invalid("MISSING_INPUT", path, "preregistered source input is absent")
    for path in sorted(actual_files - expected_files):
        diagnostics.invalid("EXTRA_INPUT", path, "input is outside the 31-ID universe")
    if not INPUTS.is_dir():
        diagnostics.invalid("MISSING_INPUT_DIRECTORY", INPUTS, "input directory is absent")

    for record_id in EXPECTED_IDS:
        path = INPUTS / f"{record_id}.json"
        artifact = load_json_artifact(path, diagnostics)
        if artifact is None:
            continue
        value = artifact.value
        valid = True
        if value.get("record_id") != record_id:
            diagnostics.invalid("INPUT_IDENTITY_MISMATCH", path,
                                f"record_id must be {record_id!r}")
            valid = False
        for key in ("title", "target", "source_paper_text"):
            if type(value.get(key)) is not str or not value[key].strip():
                diagnostics.invalid("INPUT_FIELD_INVALID", path,
                                    f"{key} must be a nonempty string")
                valid = False
        if type(value.get("source")) is not dict:
            diagnostics.invalid("INPUT_FIELD_INVALID", path,
                                "source must be an object")
            valid = False
        result["input_sha256"][record_id] = artifact.sha256
        if valid:
            result["inputs_valid"] += 1
    result["exact_roster"] = result["inputs_valid"] == len(EXPECTED_IDS)
    return result


def load_schemas(run: Path, diagnostics: Diagnostics) -> dict[str, Mapping[str, Any]]:
    schemas: dict[str, Mapping[str, Any]] = {}
    schema_files = {
        "baseline": "baseline.schema.json",
        "audit": "audit.schema.json",
        "revision": "revision.schema.json",
        "baseline_whole_proof_v2": "baseline_whole_proof_v2.schema.json",
        "revision_whole_proof_v2": "revision_whole_proof_v2.schema.json",
    }
    for name, filename in schema_files.items():
        path = run / "schemas" / filename
        value = load_json_value(path, diagnostics)
        if type(value) is not dict:
            if value is not None:
                diagnostics.invalid("SCHEMA_NOT_OBJECT", path,
                                    "schema must be a JSON object")
            continue
        if value.get("type") != "object":
            diagnostics.invalid("SCHEMA_ROOT_INVALID", path,
                                "artifact schema root must have type object")
        if value.get("additionalProperties") is not False:
            diagnostics.invalid("SCHEMA_NOT_CLOSED", path,
                                "artifact schema must forbid additional properties")
        schemas[name] = value
    return schemas


def validate_baseline(artifact: Artifact, record_id: str,
                      schema: Mapping[str, Any] | None,
                      diagnostics: Diagnostics) -> bool:
    valid = schema is not None and apply_schema(
        artifact, schema, diagnostics, "baseline"
    )
    value = artifact.value
    expected = {
        "record_id": record_id,
        "stage": "ARM_NEUTRAL_BASELINE",
    }
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            diagnostics.invalid("BASELINE_IDENTITY_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False
    if value.get("claimed_resolution") not in {"FULL", "PARTIAL", "NONE"}:
        diagnostics.invalid("BASELINE_RESOLUTION_INVALID", artifact.path,
                            "claimed_resolution is invalid")
        valid = False
    results = value.get("results")
    if type(results) is not list or len(results) < 1:
        diagnostics.invalid("BASELINE_RESULTS_INVALID", artifact.path,
                            "results must be a nonempty, uncapped array of claims")
        return False
    for index, row in enumerate(results):
        if (type(row) is not dict or type(row.get("claim")) is not str
                or not row["claim"].strip()
                or type(row.get("proof_sketch")) is not str
                or not row["proof_sketch"].strip()):
            diagnostics.invalid("BASELINE_CLAIM_INVALID", artifact.path,
                                f"results[{index}] lacks a nonempty claim/proof_sketch")
            valid = False
    if value.get("claimed_resolution") in {"FULL", "PARTIAL"} and not results:
        diagnostics.invalid("EMPTY_CANDIDATE", artifact.path,
                            "FULL/PARTIAL candidate must contain at least one claim")
        valid = False
    return valid


def validate_audit(artifact: Artifact, record_id: str, parent: Artifact,
                   stage: str, arm: str, iteration: int,
                   schema: Mapping[str, Any] | None,
                   diagnostics: Diagnostics) -> bool:
    valid = schema is not None
    if schema is not None:
        schema_errors = validate_schema_instance(artifact.value, schema, schema)
        coverage_names = {
            "target_verdict", "claimed_resolution_verdict", "target_evidence"
        }
        legacy_coverage_errors = [message for message in schema_errors if any(
            f"{name!r}" in message and "missing required property" in message
            for name in coverage_names
        )]
        other_schema_errors = [message for message in schema_errors
                               if message not in legacy_coverage_errors]
        if legacy_coverage_errors:
            diagnostics.missing(
                "AUDIT_TARGET_COVERAGE_MISSING", artifact.path,
                "audit predates target-level adjudication and must be rerun",
            )
            valid = False
        for message in other_schema_errors:
            diagnostics.invalid("SCHEMA_VIOLATION", artifact.path,
                                f"audit: {message}")
            valid = False
    value = artifact.value
    identities = {
        "record_id": record_id,
        "stage": stage,
        "arm": arm,
        "iteration": iteration,
        "parent_sha256": parent.sha256,
        "complete": True,
    }
    for key, wanted in identities.items():
        if value.get(key) != wanted:
            diagnostics.invalid("AUDIT_IDENTITY_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False
    parent_results = parent.value.get("results")
    claims = value.get("claims")
    if type(parent_results) is not list or type(claims) is not list:
        diagnostics.invalid("AUDIT_CLAIMS_INVALID", artifact.path,
                            "parent results and audit claims must be arrays")
        return False
    if len(claims) != len(parent_results):
        diagnostics.invalid("AUDIT_NOT_COMPLETE", artifact.path,
                            "audit must bind every parent claim exactly once")
        valid = False
    for index, parent_result in enumerate(parent_results):
        if index >= len(claims) or type(claims[index]) is not dict:
            continue
        claim = claims[index]
        expected_claim = parent_result.get("claim")
        expected_hash = sha_text(expected_claim) if type(expected_claim) is str else None
        bindings = {
            "idx": index,
            "claim": expected_claim,
            "claim_sha256": expected_hash,
        }
        for key, wanted in bindings.items():
            if claim.get(key) != wanted:
                diagnostics.invalid("AUDIT_CLAIM_BINDING_MISMATCH", artifact.path,
                                    f"claims[{index}].{key} must exactly bind the parent")
                valid = False
        if claim.get("verdict") not in {"VERIFIED", "REFUTED", "UNRESOLVED"}:
            diagnostics.invalid("AUDIT_VERDICT_INVALID", artifact.path,
                                f"claims[{index}] has an invalid verdict")
            valid = False
        if claim.get("verdict") == "REFUTED":
            for key in ("evidence", "witness", "search_method", "checker_path"):
                field_value = claim.get(key)
                if type(field_value) is not str or not field_value.strip():
                    diagnostics.invalid("REFUTATION_EVIDENCE_MISSING", artifact.path,
                                        f"claims[{index}].{key} is required")
                    valid = False

        # Canonical audits use either literal "none" or a path under their
        # exact per-cell scratch.  The durable byte binding is checked in the
        # separate audit metadata, so cleanup of /tmp does not break lineage.
        checker = claim.get("checker_path")
        expected_scratch = Path(
            f"/tmp/open_frontier_paired_v2/{record_id}/audit-baseline"
            if stage == "BASELINE_AUDIT" else
            f"/tmp/open_frontier_paired_v2/{record_id}/audit-revision/{arm}/iter_{iteration}"
        )
        if checker == "none":
            pass
        elif isinstance(checker, str) and checker.startswith("/"):
            if " (" in checker and stage == "BASELINE_AUDIT":
                diagnostics.warn(
                    "LEGACY_CHECKER_NOT_MATERIALIZED", artifact.path,
                    f"claims[{index}] is a known pre-durable read-only audit",
                )
            else:
                try:
                    Path(checker).resolve().relative_to(expected_scratch.resolve())
                except ValueError:
                    diagnostics.invalid(
                        "AUDIT_CHECKER_OUTSIDE_SCRATCH", artifact.path,
                        f"claims[{index}] checker_path escapes exact per-cell scratch",
                    )
                    valid = False
        else:
            diagnostics.invalid(
                "AUDIT_CHECKER_PATH_INVALID", artifact.path,
                f"claims[{index}] checker_path must be absolute or literal 'none'",
            )
            valid = False

    if type(claims) is list:
        refuted = [index for index, claim in enumerate(claims)
                   if type(claim) is dict and claim.get("verdict") == "REFUTED"]
        confirmed = value.get("confirmed_refutations")
        if confirmed != refuted:
            diagnostics.invalid(
                "CONFIRMED_REFUTATIONS_MISMATCH", artifact.path,
                f"confirmed_refutations must be exactly {refuted!r}",
            )
            valid = False
        overall = expected_overall(claims)
        if value.get("overall") != overall:
            diagnostics.invalid("AUDIT_OVERALL_MISMATCH", artifact.path,
                                f"overall must be {overall!r}")
            valid = False
    target_verdict = value.get("target_verdict")
    resolution_verdict = value.get("claimed_resolution_verdict")
    target_evidence = value.get("target_evidence")
    target_values = {
        "FULLY_RESOLVES_TARGET", "VALID_PARTIAL_PROGRESS", "NO_VALID_PROGRESS",
        "OVERCLAIMED",
    }
    if target_verdict not in target_values:
        diagnostics.missing(
            "AUDIT_TARGET_COVERAGE_MISSING", artifact.path,
            "target_verdict is absent or invalid; target coverage is not adjudicated",
        )
        valid = False
    if resolution_verdict not in {"ACCURATE", "OVERSTATED", "UNDERSTATED"}:
        diagnostics.missing(
            "AUDIT_RESOLUTION_ADJUDICATION_MISSING", artifact.path,
            "claimed_resolution_verdict is absent or invalid",
        )
        valid = False
    if type(target_evidence) is not str or not target_evidence.strip():
        diagnostics.missing(
            "AUDIT_TARGET_EVIDENCE_MISSING", artifact.path,
            "nonempty target_evidence is required for final classification",
        )
        valid = False

    claimed = parent.value.get("claimed_resolution")
    claimed_rank = {"NONE": 0, "PARTIAL": 1, "FULL": 2}.get(claimed)
    target_rank = {
        "NO_VALID_PROGRESS": 0,
        "OVERCLAIMED": 0,
        "VALID_PARTIAL_PROGRESS": 1,
        "FULLY_RESOLVES_TARGET": 2,
    }.get(target_verdict)
    if claimed_rank is not None and target_rank is not None:
        expected_resolution = (
            "ACCURATE" if claimed_rank == target_rank
            else "OVERSTATED" if claimed_rank > target_rank
            else "UNDERSTATED"
        )
        if resolution_verdict != expected_resolution:
            diagnostics.invalid(
                "CLAIMED_RESOLUTION_VERDICT_MISMATCH", artifact.path,
                f"claimed_resolution_verdict must be {expected_resolution!r}",
            )
            valid = False
    if target_verdict == "FULLY_RESOLVES_TARGET" and expected_overall(claims) != "VERIFIED":
        diagnostics.invalid(
            "FULL_TARGET_NOT_CLAIM_VERIFIED", artifact.path,
            "FULLY_RESOLVES_TARGET requires every listed claim to be VERIFIED",
        )
        valid = False
    return valid


class BugBankView:
    def __init__(self, diagnostics: Diagnostics):
        self.diagnostics = diagnostics
        self.connection: sqlite3.Connection | None = None
        self.database_sha256: str | None = None
        self.database_size: int | None = None
        self.entry_count: int | None = None
        self.status_counts: dict[str, int] = {}
        self.document_frequency: Counter[str] = Counter()
        self.tables: set[str] = set()
        self._entry_cache: dict[str, dict[str, Any] | None] = {}
        if not BUGBANK_DB.is_file():
            diagnostics.invalid("BUGBANK_DATABASE_MISSING", BUGBANK_DB,
                                "pinned BugBank database is absent")
            return
        try:
            self.database_sha256 = sha_file(BUGBANK_DB)
            self.database_size = BUGBANK_DB.stat().st_size
        except OSError as error:
            diagnostics.invalid("BUGBANK_DATABASE_UNREADABLE", BUGBANK_DB, str(error))
            return
        if self.database_sha256 != PINNED_BUGBANK_SHA256:
            diagnostics.invalid(
                "BUGBANK_DATABASE_NOT_PINNED", BUGBANK_DB,
                f"expected SHA-256 {PINNED_BUGBANK_SHA256}, got {self.database_sha256}",
            )
            return
        try:
            uri = f"file:{BUGBANK_DB.resolve()}?mode=ro"
            self.connection = sqlite3.connect(uri, uri=True)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA query_only = ON")
            self.tables = {
                row[0] for row in self.connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            self.entry_count = self.connection.execute(
                "SELECT COUNT(*) FROM entries"
            ).fetchone()[0]
            self.status_counts = {
                row[0]: row[1] for row in self.connection.execute(
                    "SELECT status, COUNT(*) FROM entries GROUP BY status ORDER BY status"
                )
            }
            for row in self.connection.execute(
                    "SELECT id, refutes FROM entries ORDER BY id COLLATE BINARY"):
                words = {
                    match.lower() for match in BUGBANK_WORD.findall(row["refutes"] or "")
                    if match.lower() not in BUGBANK_STOP
                }
                self.document_frequency.update(words)
        except sqlite3.Error as error:
            diagnostics.invalid("BUGBANK_DATABASE_INVALID", BUGBANK_DB, str(error))
            if self.connection is not None:
                self.connection.close()
                self.connection = None

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()

    def entry_payload(self, entry_id: str) -> dict[str, Any] | None:
        if entry_id in self._entry_cache:
            return self._entry_cache[entry_id]
        if self.connection is None:
            return None
        columns = ", ".join(ENTRY_COLUMNS)
        row = self.connection.execute(
            f"SELECT {columns} FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()
        if row is None:
            self._entry_cache[entry_id] = None
            return None
        entry = {column: row[column] for column in ENTRY_COLUMNS}
        tags = ([item[0] for item in self.connection.execute(
            "SELECT tag FROM tags WHERE entry_id=? ORDER BY tag COLLATE BINARY",
            (entry_id,),
        )] if "tags" in self.tables else [])
        related = ([item[0] for item in self.connection.execute(
            "SELECT related_id FROM relations WHERE entry_id=? "
            "ORDER BY related_id COLLATE BINARY", (entry_id,),
        )] if "relations" in self.tables else [])
        citation = None
        if "sources" in self.tables and entry.get("source_book") is not None:
            source = self.connection.execute(
                "SELECT citation FROM sources WHERE id=?", (entry["source_book"],)
            ).fetchone()
            citation = source[0] if source is not None else None
        payload = {**entry, "tags": tags, "related_entry_ids": related,
                   "source_citation": citation}
        self._entry_cache[entry_id] = payload
        return payload

    def expected_query(self, claim: str, k: int) -> tuple[list[dict[str, Any]], str,
                                                           list[tuple[str, float]]]:
        if self.connection is None or self.entry_count is None:
            return [], "", []
        seen: dict[str, float] = {}
        for raw_word in BUGBANK_WORD.findall(claim):
            word = raw_word.lower()
            if word in BUGBANK_STOP or len(word) < 3:
                continue
            seen.setdefault(
                word,
                (self.entry_count + 1) / (self.document_frequency.get(word, 0) + 1),
            )
        ranked = sorted(seen.items(), key=lambda item: -item[1])[:12]
        terms = [
            {
                "term": term,
                "document_frequency": self.document_frequency.get(term, 0),
                "rarity_weight": weight,
            }
            for term, weight in ranked
        ]
        expression = " OR ".join(f'"{item["term"]}"' for item in terms)
        rows = (
            self.connection.execute(BUGBANK_RETRIEVAL_SQL, (expression, k)).fetchall()
            if terms else []
        )
        hits = [(row["id"], float(row["score"])) for row in rows]
        return terms, expression, hits


def validate_exact_binding(binding: Any, expected: Artifact, label: str,
                           diagnostics: Diagnostics, owner: Path,
                           run: Path) -> bool:
    if type(binding) is not dict:
        diagnostics.invalid("BINDING_INVALID", owner, f"{label} binding must be an object")
        return False
    valid = True
    if not same_recorded_path(binding.get("path"), expected.path, run):
        diagnostics.invalid("BINDING_PATH_MISMATCH", owner,
                            f"{label}.path does not resolve to {rel(expected.path, run)}")
        valid = False
    if binding.get("sha256") != expected.sha256:
        diagnostics.invalid("BINDING_HASH_MISMATCH", owner,
                            f"{label}.sha256 does not match exact file bytes")
        valid = False
    if binding.get("size_bytes") != expected.size_bytes:
        diagnostics.invalid("BINDING_SIZE_MISMATCH", owner,
                            f"{label}.size_bytes does not match exact file bytes")
        valid = False
    return valid


def validate_current_file_record(binding: Any, expected: Path, label: str,
                                 diagnostics: Diagnostics, owner: Path,
                                 run: Path) -> bool:
    if type(binding) is not dict or not expected.is_file():
        diagnostics.invalid("PROVENANCE_FILE_MISSING", owner,
                            f"{label} provenance or current file is absent")
        return False
    valid = True
    if not same_recorded_path(binding.get("path"), expected, run):
        diagnostics.invalid("PROVENANCE_PATH_MISMATCH", owner,
                            f"{label}.path does not identify the expected file")
        valid = False
    try:
        actual_size = expected.stat().st_size
        actual_hash = sha_file(expected)
    except OSError as error:
        diagnostics.invalid("PROVENANCE_FILE_UNREADABLE", owner, f"{label}: {error}")
        return False
    if binding.get("size_bytes") != actual_size:
        diagnostics.invalid("PROVENANCE_SIZE_MISMATCH", owner,
                            f"{label}.size_bytes does not match current file")
        valid = False
    if binding.get("sha256") != actual_hash:
        diagnostics.invalid("PROVENANCE_HASH_MISMATCH", owner,
                            f"{label}.sha256 does not match current file")
        valid = False
    return valid


def validate_receipt(artifact: Artifact, record_id: str, iteration: int,
                     parent: Artifact, database: BugBankView,
                     diagnostics: Diagnostics, run: Path) -> tuple[bool, list[str]]:
    value = artifact.value
    valid = True
    receipt_schema = value.get("schema")
    whole_proof = receipt_schema == ACTIVE_RECEIPT_SCHEMA
    if receipt_schema not in {RECEIPT_SCHEMA, ACTIVE_RECEIPT_SCHEMA}:
        diagnostics.invalid(
            "RECEIPT_IDENTITY_MISMATCH", artifact.path,
            f"schema must be {RECEIPT_SCHEMA!r} or {ACTIVE_RECEIPT_SCHEMA!r}",
        )
        valid = False
    identities = {
        "run_id": RUN_ID,
        "pair_id": record_id,
        "record_id": record_id,
        "arm": "bugbank",
        "iteration": iteration,
        "stage": "BUGBANK_FEEDBACK_EXPOSURE",
        "status": "COMPLETE",
    }
    for key, wanted in identities.items():
        if value.get(key) != wanted:
            diagnostics.invalid("RECEIPT_IDENTITY_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False

    recorded_self_hash = value.get("receipt_payload_sha256")
    unsigned = copy.deepcopy(value)
    unsigned.pop("receipt_payload_sha256", None)
    try:
        actual_self_hash = sha_bytes(canonical_bytes(unsigned))
    except (TypeError, ValueError) as error:
        diagnostics.invalid("RECEIPT_NONCANONICAL", artifact.path, str(error))
        actual_self_hash = None
    if recorded_self_hash != actual_self_hash:
        diagnostics.invalid("RECEIPT_SELF_HASH_MISMATCH", artifact.path,
                            "receipt_payload_sha256 is not the canonical receipt hash")
        valid = False

    parent_binding = value.get("parent")
    if type(parent_binding) is not dict:
        diagnostics.invalid("RECEIPT_PARENT_INVALID", artifact.path,
                            "parent binding must be an object")
        valid = False
    else:
        if not validate_exact_binding(parent_binding, parent, "parent", diagnostics,
                                      artifact.path, run):
            valid = False
        expected_parent_canonical = sha_bytes(canonical_bytes(parent.value))
        if parent_binding.get("canonical_payload_sha256") != expected_parent_canonical:
            diagnostics.invalid("RECEIPT_PARENT_CANONICAL_HASH_MISMATCH", artifact.path,
                                "parent canonical payload hash is wrong")
            valid = False
        expected_parent_identity = {
            "record_id": parent.value.get("record_id"),
            "arm": parent.value.get("arm"),
            "iteration": parent.value.get("iteration"),
            "stage": parent.value.get("stage"),
        }
        for key, wanted in expected_parent_identity.items():
            if parent_binding.get(key) != wanted:
                diagnostics.invalid("RECEIPT_PARENT_IDENTITY_MISMATCH", artifact.path,
                                    f"parent.{key} is not bound to the parent artifact")
                valid = False

    results = parent.value.get("results", [])
    expected_claims = []
    query_texts: list[str] = []
    for index, row in enumerate(results):
        if type(row) is not dict:
            continue
        claim = row.get("claim", "")
        expected = {
            "claim_index": index,
            "claim": claim,
            "claim_sha256": sha_text(claim),
        }
        query_text = claim
        if whole_proof:
            proof_sketch = row.get("proof_sketch", "")
            query_text = f"{claim}\n\n{proof_sketch}"
            expected.update({
                "proof_sketch_sha256": sha_text(proof_sketch),
                "query_text_sha256": sha_text(query_text),
            })
        expected_claims.append(expected)
        query_texts.append(query_text)
    if value.get("parent_claim_count") != len(expected_claims):
        diagnostics.invalid("RECEIPT_CLAIM_COUNT_MISMATCH", artifact.path,
                            "parent_claim_count is wrong")
        valid = False
    if value.get("parent_claims") != expected_claims:
        diagnostics.invalid("RECEIPT_CLAIMS_MISMATCH", artifact.path,
                            "parent_claims do not preserve exact parent claims")
        valid = False
    claim_snapshot = [
        {"claim_index": item["claim_index"], "claim": item["claim"]}
        for item in expected_claims
    ]
    if value.get("parent_claims_sha256") != sha_bytes(canonical_bytes(claim_snapshot)):
        diagnostics.invalid("RECEIPT_CLAIMS_HASH_MISMATCH", artifact.path,
                            "parent_claims_sha256 is wrong")
        valid = False

    database_binding = value.get("database")
    if type(database_binding) is not dict:
        diagnostics.invalid("RECEIPT_DATABASE_BINDING_INVALID", artifact.path,
                            "database provenance must be an object")
        valid = False
    else:
        if not same_recorded_path(database_binding.get("path"), BUGBANK_DB, run):
            diagnostics.invalid("RECEIPT_DATABASE_PATH_MISMATCH", artifact.path,
                                "receipt does not name the pinned BugBank database")
            valid = False
        if database_binding.get("sha256") != PINNED_BUGBANK_SHA256:
            diagnostics.invalid("RECEIPT_DATABASE_HASH_MISMATCH", artifact.path,
                                "receipt database hash is not the preregistered hash")
            valid = False
        if database.database_size is not None and (
                database_binding.get("size_bytes") != database.database_size):
            diagnostics.invalid("RECEIPT_DATABASE_SIZE_MISMATCH", artifact.path,
                                "receipt database size is wrong")
            valid = False
        if database.entry_count is not None and (
                database_binding.get("entry_count") != database.entry_count):
            diagnostics.invalid("RECEIPT_DATABASE_COUNT_MISMATCH", artifact.path,
                                "receipt database entry count is wrong")
            valid = False
        if database.status_counts and database_binding.get("status_counts") != database.status_counts:
            diagnostics.invalid("RECEIPT_STATUS_COUNTS_MISMATCH", artifact.path,
                                "receipt database status counts are wrong")
            valid = False
    feedback_script = ACTIVE_FEEDBACK_SCRIPT if whole_proof else FEEDBACK_SCRIPT
    if not validate_current_file_record(value.get("script"), feedback_script,
                                        "script", diagnostics, artifact.path, run):
        valid = False
    if whole_proof:
        if not validate_current_file_record(
                value.get("legacy_script"), FEEDBACK_SCRIPT, "legacy_script",
                diagnostics, artifact.path, run):
            valid = False
    elif "legacy_script" in value:
        diagnostics.invalid(
            "RECEIPT_LEGACY_PROVENANCE_UNEXPECTED", artifact.path,
            "a v1 receipt must not contain the v2 wrapper's legacy-script binding",
        )
        valid = False
    if not validate_current_file_record(value.get("stock_retriever"), STOCK_RETRIEVER,
                                        "stock_retriever", diagnostics,
                                        artifact.path, run):
        valid = False

    invocation = value.get("invocation")
    if type(invocation) is not dict:
        diagnostics.invalid("RECEIPT_INVOCATION_INVALID", artifact.path,
                            "invocation must be an object")
        valid = False
    else:
        invocation_expected = {
            "record_id": record_id,
            "iteration": iteration,
            "k": RETRIEVAL_K,
        }
        for key, wanted in invocation_expected.items():
            if invocation.get(key) != wanted:
                diagnostics.invalid("RECEIPT_INVOCATION_MISMATCH", artifact.path,
                                    f"invocation.{key} must be {wanted!r}")
                valid = False
        if not same_recorded_path(invocation.get("parent_json"), parent.path, run):
            diagnostics.invalid("RECEIPT_INVOCATION_PARENT_MISMATCH", artifact.path,
                                "invocation.parent_json is wrong")
            valid = False
        if not same_recorded_path(invocation.get("out"), artifact.path, run):
            diagnostics.invalid("RECEIPT_INVOCATION_OUTPUT_MISMATCH", artifact.path,
                                "invocation.out is wrong")
            valid = False
        if not same_recorded_path(invocation.get("db"), BUGBANK_DB, run):
            diagnostics.invalid("RECEIPT_INVOCATION_DATABASE_MISMATCH", artifact.path,
                                "invocation.db is wrong")
            valid = False

    parameters = value.get("parameters")
    required_parameters = {
        "k_per_claim": RETRIEVAL_K,
        "status_filter": "all",
        "exclude_self": False,
        "excluded_source_items": [],
        "excluded_entry_ids": [],
        "document_frequency_corpus": "all entries.refutes rows across all statuses",
        "maximum_salient_terms": 12,
        "salient_term_tie_break": (
            "first occurrence in query text" if whole_proof
            else "first occurrence in exact claim"
        ),
        "fts_bm25_weights": [2.0, 8.0, 4.0, 1.0, 1.0, 3.0],
        "ordering": ["bm25_score_ASC_unrounded", "entry_id_BINARY_ASC"],
        "truncate_stage": "after status-all query and total ordering",
    }
    if type(parameters) is not dict:
        diagnostics.invalid("RECEIPT_PARAMETERS_INVALID", artifact.path,
                            "parameters must be an object")
        valid = False
    else:
        for key, wanted in required_parameters.items():
            if parameters.get(key) != wanted:
                diagnostics.invalid("RECEIPT_PARAMETER_MISMATCH", artifact.path,
                                    f"parameters.{key} must be {wanted!r}")
                valid = False
        if whole_proof:
            if parameters.get("query_text_basis") != (
                "claim statement, two newlines, proof_sketch"
            ):
                diagnostics.invalid(
                    "RECEIPT_PARAMETER_MISMATCH", artifact.path,
                    "parameters.query_text_basis must bind claim plus proof_sketch",
                )
                valid = False
        elif "query_text_basis" in parameters:
            diagnostics.invalid(
                "RECEIPT_PARAMETER_MISMATCH", artifact.path,
                "legacy receipt must not claim the whole-proof query basis",
            )
            valid = False
        query_sql = parameters.get("query_sql")
        if (query_sql != BUGBANK_RETRIEVAL_SQL or
                parameters.get("query_sql_sha256") != sha_text(BUGBANK_RETRIEVAL_SQL)):
            diagnostics.invalid("RECEIPT_QUERY_SQL_HASH_MISMATCH", artifact.path,
                                "query SQL/hash differ from the pinned retrieval query")
            valid = False

    queries = value.get("queries")
    retrieved_ids: list[str] = []
    seen_retrieved: set[str] = set()
    if type(queries) is not list or len(queries) != len(expected_claims):
        diagnostics.invalid("RECEIPT_QUERIES_INVALID", artifact.path,
                            "queries must correspond one-for-one with parent claims")
        valid = False
        queries = [] if type(queries) is not list else queries
    for index, query in enumerate(queries):
        if type(query) is not dict:
            diagnostics.invalid("RECEIPT_QUERY_INVALID", artifact.path,
                                f"queries[{index}] must be an object")
            valid = False
            continue
        if index < len(expected_claims):
            expected_query = {
                "query_id": f"{record_id}__bugbank__iter_{iteration}__claim_{index}",
                **expected_claims[index],
            }
            for key, wanted in expected_query.items():
                if query.get(key) != wanted:
                    diagnostics.invalid("RECEIPT_QUERY_BINDING_MISMATCH", artifact.path,
                                        f"queries[{index}].{key} is wrong")
                    valid = False
            if database.connection is not None:
                expected_terms, expected_expression, expected_hits = database.expected_query(
                    query_texts[index], RETRIEVAL_K
                )
                if query.get("salient_terms") != expected_terms:
                    diagnostics.invalid(
                        "RECEIPT_SALIENT_TERMS_MISMATCH", artifact.path,
                        f"queries[{index}] terms differ from independent recomputation",
                    )
                    valid = False
                if query.get("fts_match_expression") != expected_expression:
                    diagnostics.invalid(
                        "RECEIPT_MATCH_EXPRESSION_MISMATCH", artifact.path,
                        f"queries[{index}] FTS expression differs from recomputation",
                    )
                    valid = False
            else:
                expected_hits = []
        hits = query.get("hits")
        if type(hits) is not list:
            diagnostics.invalid("RECEIPT_HITS_INVALID", artifact.path,
                                f"queries[{index}].hits must be an array")
            valid = False
            continue
        if query.get("hit_count") != len(hits) or len(hits) > RETRIEVAL_K:
            diagnostics.invalid("RECEIPT_HIT_COUNT_MISMATCH", artifact.path,
                                f"queries[{index}] hit count is invalid")
            valid = False
        if database.connection is not None:
            observed_hit_keys = [
                (hit.get("entry_id"), float(hit.get("bm25")))
                for hit in hits
                if type(hit) is dict and type(hit.get("entry_id")) is str
                and is_number(hit.get("bm25"))
            ]
            expected_hit_keys = expected_hits if index < len(expected_claims) else []
            if (len(observed_hit_keys) != len(hits)
                    or len(expected_hit_keys) != len(hits)
                    or any(observed_id != expected_id or observed_score.hex() != expected_score.hex()
                           for (observed_id, observed_score), (expected_id, expected_score)
                           in zip(observed_hit_keys, expected_hit_keys))):
                diagnostics.invalid(
                    "RECEIPT_TOP_K_MISMATCH", artifact.path,
                    f"queries[{index}] hits are not the independently recomputed top-{RETRIEVAL_K}",
                )
                valid = False
        previous_key: tuple[float, str] | None = None
        query_ids: set[str] = set()
        for rank, hit in enumerate(hits, 1):
            if type(hit) is not dict:
                diagnostics.invalid("RECEIPT_HIT_INVALID", artifact.path,
                                    f"queries[{index}].hits[{rank - 1}] is not an object")
                valid = False
                continue
            entry_id = hit.get("entry_id")
            score = hit.get("bm25")
            if (hit.get("rank") != rank or type(entry_id) is not str or not entry_id
                    or not is_number(score)):
                diagnostics.invalid("RECEIPT_HIT_IDENTITY_INVALID", artifact.path,
                                    f"queries[{index}].hits[{rank - 1}] rank/id/score invalid")
                valid = False
                continue
            if entry_id in query_ids:
                diagnostics.invalid("RECEIPT_DUPLICATE_HIT", artifact.path,
                                    f"entry {entry_id!r} repeats within query {index}")
                valid = False
            query_ids.add(entry_id)
            current_key = (float(score), entry_id)
            if previous_key is not None and previous_key > current_key:
                diagnostics.invalid("RECEIPT_HIT_ORDER_INVALID", artifact.path,
                                    f"queries[{index}] is not score/ID ordered")
                valid = False
            previous_key = current_key
            if hit.get("bm25_binary64_hex") != float(score).hex():
                diagnostics.invalid("RECEIPT_SCORE_ENCODING_MISMATCH", artifact.path,
                                    f"queries[{index}] hit {entry_id!r} score hex is wrong")
                valid = False
            unsigned_hit = copy.deepcopy(hit)
            recorded_hit_hash = unsigned_hit.pop("hit_payload_sha256", None)
            if recorded_hit_hash != sha_bytes(canonical_bytes(unsigned_hit)):
                diagnostics.invalid("RECEIPT_HIT_HASH_MISMATCH", artifact.path,
                                    f"hit payload hash is wrong for {entry_id!r}")
                valid = False
            treatment_payload = {
                "refutes": hit.get("refutes"),
                "counterexample": hit.get("counterexample"),
                "true_theorem": hit.get("true_theorem"),
            }
            if hit.get("treatment_content_sha256") != sha_bytes(
                    canonical_bytes(treatment_payload)):
                diagnostics.invalid("RECEIPT_TREATMENT_HASH_MISMATCH", artifact.path,
                                    f"treatment hash is wrong for {entry_id!r}")
                valid = False
            if hit.get("counterexample") != hit.get("statement"):
                diagnostics.invalid("RECEIPT_COUNTEREXAMPLE_MISMATCH", artifact.path,
                                    f"counterexample is not the entry statement for {entry_id!r}")
                valid = False
            expected_entry = database.entry_payload(entry_id)
            if expected_entry is None:
                diagnostics.invalid("RECEIPT_ENTRY_NOT_IN_DATABASE", artifact.path,
                                    f"entry {entry_id!r} is absent from pinned BugBank")
                valid = False
            else:
                for key, wanted in expected_entry.items():
                    # The receipt exposes the database primary key as
                    # entry_id, while entry_payload_sha256 deliberately seals
                    # the original database-shaped object with key ``id``.
                    observed = entry_id if key == "id" else hit.get(key)
                    if observed != wanted:
                        diagnostics.invalid("RECEIPT_ENTRY_PAYLOAD_MISMATCH", artifact.path,
                                            f"hit {entry_id!r} field {key!r} differs from database")
                        valid = False
                if hit.get("entry_payload_sha256") != sha_bytes(
                        canonical_bytes(expected_entry)):
                    diagnostics.invalid("RECEIPT_ENTRY_HASH_MISMATCH", artifact.path,
                                        f"entry payload hash is wrong for {entry_id!r}")
                    valid = False
            if entry_id not in seen_retrieved:
                seen_retrieved.add(entry_id)
                retrieved_ids.append(entry_id)

    summary = value.get("exposure_summary")
    if type(summary) is not dict:
        diagnostics.invalid("RECEIPT_EXPOSURE_SUMMARY_INVALID", artifact.path,
                            "exposure_summary must be an object")
        valid = False
    else:
        exposure_bytes = canonical_bytes(queries)
        expected_summary = {
            "query_count": len(queries),
            "hit_count": sum(len(query.get("hits", [])) for query in queries
                             if type(query) is dict and type(query.get("hits")) is list),
            "ordered_payload_sha256": sha_bytes(exposure_bytes),
            "ordered_payload_size_bytes": len(exposure_bytes),
        }
        for key, wanted in expected_summary.items():
            if summary.get(key) != wanted:
                diagnostics.invalid("RECEIPT_EXPOSURE_SUMMARY_MISMATCH", artifact.path,
                                    f"exposure_summary.{key} is wrong")
                valid = False
    return valid, retrieved_ids


def validate_revision(artifact: Artifact, record_id: str, arm: str,
                      iteration: int, parent: Artifact, parent_audit: Artifact,
                      receipt: Artifact | None, retrieved_ids: Sequence[str],
                      schema: Mapping[str, Any] | None,
                      diagnostics: Diagnostics, run: Path) -> bool:
    valid = schema is not None and apply_schema(
        artifact, schema, diagnostics, "revision"
    )
    value = artifact.value
    identities = {
        "record_id": record_id,
        "stage": "REVISION",
        "arm": arm,
        "iteration": iteration,
        "parent_sha256": parent.sha256,
        "audit_sha256": parent_audit.sha256,
    }
    for key, wanted in identities.items():
        if value.get(key) != wanted:
            diagnostics.invalid("REVISION_IDENTITY_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False
    if value.get("claimed_resolution") in {"FULL", "PARTIAL"} and not value.get("results"):
        diagnostics.invalid("EMPTY_CANDIDATE", artifact.path,
                            "FULL/PARTIAL revision must contain at least one claim")
        valid = False

    refutations = parent_audit.value.get("confirmed_refutations", [])
    feedback_acted = value.get("audit_feedback_acted_on")
    if refutations and (type(feedback_acted) is not list or not feedback_acted):
        diagnostics.invalid("AUDIT_FEEDBACK_NOT_ACTED_ON", artifact.path,
                            "revision after a refutation must record acted-on audit feedback")
        valid = False

    retrieved = value.get("retrieved_entry_ids")
    acted = value.get("acted_on_entry_ids")
    dismissed_rows = value.get("dismissed_hits")
    if arm == "plain":
        plain_expected = {
            "treatment_status": "PLAIN_SELF_CRITIQUE",
            "receipt_path": "",
            "receipt_sha256": "",
            "retrieved_entry_ids": [],
            "acted_on_entry_ids": [],
            "dismissed_hits": [],
        }
        for key, wanted in plain_expected.items():
            if value.get(key) != wanted:
                diagnostics.invalid("PLAIN_EXPOSURE_CONTAMINATION", artifact.path,
                                    f"plain revision {key} must be {wanted!r}")
                valid = False
    else:
        if value.get("treatment_status") != "BUGBANK_RECEIPT_EXPOSED":
            diagnostics.invalid("BUGBANK_TREATMENT_STATUS_INVALID", artifact.path,
                                "BugBank arm lacks wrapper-computed treatment status")
            valid = False
        if receipt is None:
            diagnostics.invalid("BUGBANK_RECEIPT_NOT_BOUND", artifact.path,
                                "BugBank revision has no valid exposure receipt")
            valid = False
        else:
            if not same_recorded_path(value.get("receipt_path"), receipt.path, run):
                diagnostics.invalid("BUGBANK_RECEIPT_PATH_MISMATCH", artifact.path,
                                    "revision receipt_path is wrong")
                valid = False
            if value.get("receipt_sha256") != receipt.sha256:
                diagnostics.invalid("BUGBANK_RECEIPT_HASH_MISMATCH", artifact.path,
                                    "revision receipt_sha256 does not bind exact receipt bytes")
                valid = False
        if not unique_strings(retrieved):
            diagnostics.invalid("RETRIEVED_IDS_INVALID", artifact.path,
                                "retrieved_entry_ids must be unique nonempty strings")
            valid = False
            retrieved = [] if type(retrieved) is not list else retrieved
        if list(retrieved) != list(retrieved_ids):
            diagnostics.invalid("RETRIEVED_IDS_MISMATCH", artifact.path,
                                "retrieved_entry_ids must equal receipt hits in first-exposure order")
            valid = False
        if not unique_strings(acted):
            diagnostics.invalid("ACTED_IDS_INVALID", artifact.path,
                                "acted_on_entry_ids must be unique nonempty strings")
            valid = False
            acted = [] if type(acted) is not list else acted
        if not set(acted).issubset(set(retrieved)):
            diagnostics.invalid("ACTED_NOT_RETRIEVED", artifact.path,
                                "acted-on entries must be a subset of retrieved entries")
            valid = False
        acted_set = set(acted)
        if list(acted) != [entry_id for entry_id in retrieved if entry_id in acted_set]:
            diagnostics.invalid("ACTED_IDS_ORDER_INVALID", artifact.path,
                                "acted_on_entry_ids must preserve receipt order")
            valid = False
        if type(dismissed_rows) is not list:
            diagnostics.invalid("DISMISSED_HITS_INVALID", artifact.path,
                                "dismissed_hits must be an array")
            valid = False
            dismissed_rows = []
        dismissed: list[str] = []
        for index, row in enumerate(dismissed_rows):
            if (type(row) is not dict or type(row.get("entry_id")) is not str
                    or not row["entry_id"] or type(row.get("reason")) is not str
                    or not row["reason"].strip()):
                diagnostics.invalid("DISMISSED_HIT_INVALID", artifact.path,
                                    f"dismissed_hits[{index}] is malformed")
                valid = False
                continue
            dismissed.append(row["entry_id"])
        if len(dismissed) != len(set(dismissed)):
            diagnostics.invalid("DUPLICATE_DISMISSED_HIT", artifact.path,
                                "dismissed hit IDs must be unique")
            valid = False
        if not set(dismissed).issubset(set(retrieved)):
            diagnostics.invalid("DISMISSED_NOT_RETRIEVED", artifact.path,
                                "dismissed entries must be a subset of retrieved entries")
            valid = False
        if set(dismissed) & set(acted):
            diagnostics.invalid("ACTED_AND_DISMISSED_OVERLAP", artifact.path,
                                "an entry cannot be both acted on and dismissed")
            valid = False
        if set(dismissed) | set(acted) != set(retrieved):
            diagnostics.invalid("RETRIEVAL_NOT_ACCOUNTED_FOR", artifact.path,
                                "every retrieved entry must be acted on or explicitly dismissed")
            valid = False
        if dismissed != [entry_id for entry_id in retrieved if entry_id not in acted_set]:
            diagnostics.invalid("DISMISSED_IDS_ORDER_INVALID", artifact.path,
                                "dismissed_hits must be the receipt-ordered complement")
            valid = False
    return valid


def prompt_binding(value: Mapping[str, Any], key: str) -> Any:
    # Canonical metadata uses source/parent/audit/receipt.  The *_binding
    # aliases make the independent checker readable across preflight drafts;
    # accepting an alias does not weaken any byte/hash requirement.
    return value.get(key, value.get(f"{key}_binding"))


def validate_prompt_metadata(artifact: Artifact, record_id: str, arm: str,
                             iteration: int, source: Artifact, parent: Artifact,
                             parent_audit: Artifact, receipt: Artifact | None,
                             revision: Artifact | None, diagnostics: Diagnostics,
                             run: Path) -> bool:
    value = artifact.value
    valid = True
    expected_identity = {
        "schema": "open_frontier_paired_v2_prompt_exposure_v1",
        "run_id": RUN_ID,
        "record_id": record_id,
        "stage": "REVISION_PROMPT",
        "arm": arm,
        "iteration": iteration,
        "treatment_status": (
            "PLAIN_SELF_CRITIQUE" if arm == "plain" else "BUGBANK_RECEIPT_EXPOSED"
        ),
        "bugbank_exposed": arm == "bugbank",
    }
    for key, wanted in expected_identity.items():
        if value.get(key) != wanted:
            diagnostics.invalid("PROMPT_METADATA_IDENTITY_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False
    prompt_text = value.get("prompt_text")
    if type(prompt_text) is not str or not prompt_text:
        diagnostics.invalid("PROMPT_TEXT_MISSING", artifact.path,
                            "full prompt_text must be persisted")
        return False
    whole_proof_prompt = artifact.path.parent == run / "prompts_whole_proof_v2"
    if whole_proof_prompt:
        if value.get("claim_coverage_policy") != CLAIM_COVERAGE_POLICY:
            diagnostics.invalid(
                "PROMPT_CLAIM_COVERAGE_POLICY_MISSING", artifact.path,
                f"active prompt must declare {CLAIM_COVERAGE_POLICY}",
            )
            valid = False
        if ("There is no claim-count cap." not in prompt_text
                or "Use at most six claims" in prompt_text):
            diagnostics.invalid(
                "PROMPT_CLAIM_CAP_NOT_WITHDRAWN", artifact.path,
                "active prompt must require the complete uncapped claim inventory",
            )
            valid = False
    elif "claim_coverage_policy" in value:
        diagnostics.invalid(
            "LEGACY_PROMPT_POLICY_MARKER_UNEXPECTED", artifact.path,
            "legacy prompt metadata must remain byte-faithful to its old policy",
        )
        valid = False
    prompt_bytes = prompt_text.encode("utf-8")
    if value.get("prompt_utf8_sha256") != sha_bytes(prompt_bytes):
        diagnostics.invalid("PROMPT_HASH_MISMATCH", artifact.path,
                            "prompt_utf8_sha256 is wrong")
        valid = False
    if value.get("prompt_size_bytes") != len(prompt_bytes):
        diagnostics.invalid("PROMPT_SIZE_MISMATCH", artifact.path,
                            "prompt_size_bytes is wrong")
        valid = False
    created_at = parse_timestamp(value.get("created_at"))
    if created_at is None:
        diagnostics.invalid("PROMPT_CREATED_AT_INVALID", artifact.path,
                            "created_at must be an ISO-8601 timestamp")
        valid = False
    for key, expected in (("source", source), ("parent", parent),
                          ("audit", parent_audit)):
        if not validate_exact_binding(prompt_binding(value, key), expected, key,
                                      diagnostics, artifact.path, run):
            valid = False

    receipt_binding = prompt_binding(value, "receipt")
    if arm == "plain":
        if receipt_binding is not None:
            diagnostics.invalid("PLAIN_RECEIPT_BINDING_PRESENT", artifact.path,
                                "plain prompt metadata receipt must be null")
            valid = False
        forbidden = [
            RECEIPT_SCHEMA,
            ACTIVE_RECEIPT_SCHEMA,
            "BUGBANK_FEEDBACK_EXPOSURE",
            PINNED_BUGBANK_SHA256,
            '"receipt_payload_sha256"',
        ]
        for marker in forbidden:
            if marker in prompt_text:
                diagnostics.invalid("PLAIN_PROMPT_EXPOSURE_CONTAMINATION", artifact.path,
                                    f"plain prompt contains receipt marker {marker!r}")
                valid = False
    else:
        if receipt is None:
            diagnostics.invalid("BUGBANK_PROMPT_RECEIPT_MISSING", artifact.path,
                                "BugBank prompt has no validated receipt")
            valid = False
        else:
            if not validate_exact_binding(receipt_binding, receipt, "receipt",
                                          diagnostics, artifact.path, run):
                valid = False
            if (type(receipt_binding) is not dict or
                    receipt_binding.get("receipt_payload_sha256") !=
                    receipt.value.get("receipt_payload_sha256")):
                diagnostics.invalid("PROMPT_RECEIPT_PAYLOAD_HASH_MISMATCH", artifact.path,
                                    "prompt does not bind the receipt canonical payload")
                valid = False
            receipt_text = receipt.raw.decode("utf-8")
            if receipt_text not in prompt_text and receipt_text.rstrip("\n") not in prompt_text:
                diagnostics.invalid("RECEIPT_NOT_EXPOSED_VERBATIM", artifact.path,
                                    "full exact BugBank receipt is not embedded in prompt_text")
                valid = False

    exposure = value.get("exposure")
    if type(exposure) is not dict:
        diagnostics.invalid("PROMPT_EXPOSURE_DIAGNOSTICS_MISSING", artifact.path,
                            "exposure diagnostics must be an object")
        valid = False
    else:
        occurrence_count = len(re.findall("bugbank", prompt_text, flags=re.IGNORECASE))
        if exposure.get("prompt_treatment_name_token_count") != occurrence_count:
            diagnostics.invalid("PROMPT_TREATMENT_TOKEN_COUNT_MISMATCH", artifact.path,
                                "prompt treatment-name count is not recomputed correctly")
            valid = False
        if arm == "plain":
            input_count = sum(
                len(re.findall(b"bugbank", raw, flags=re.IGNORECASE))
                for raw in (source.raw, parent.raw, parent_audit.raw)
            )
            expected_exposure = {
                "complete_receipt_payload_embedded": False,
                "receipt_verbatim_occurrences": 0,
                "receipt_start_byte": None,
                "receipt_end_byte": None,
                "plain_input_treatment_name_token_count": input_count,
                "retrieved_entry_ids": [],
            }
        else:
            receipt_text = receipt.raw.decode("utf-8") if receipt else ""
            occurrences = prompt_text.count(receipt_text) if receipt_text else 0
            character_offset = prompt_text.find(receipt_text) if receipt_text else -1
            start_byte = (len(prompt_text[:character_offset].encode("utf-8"))
                          if character_offset >= 0 else None)
            expected_exposure = {
                "complete_receipt_payload_embedded": True,
                "receipt_verbatim_occurrences": occurrences,
                "receipt_start_byte": start_byte,
                "receipt_end_byte": (
                    start_byte + receipt.size_bytes
                    if start_byte is not None and receipt is not None else None
                ),
                "plain_input_treatment_name_token_count": None,
                "retrieved_entry_ids": revision.value.get("retrieved_entry_ids", [])
                if revision else (
                    list(dict.fromkeys(
                        hit.get("entry_id")
                        for query in receipt.value.get("queries", [])
                        for hit in query.get("hits", [])
                        if type(hit) is dict and type(hit.get("entry_id")) is str
                    )) if receipt else []
                ),
            }
        for key, wanted in expected_exposure.items():
            if exposure.get(key) != wanted:
                diagnostics.invalid("PROMPT_EXPOSURE_DIAGNOSTIC_MISMATCH", artifact.path,
                                    f"exposure.{key} must be {wanted!r}")
                valid = False

    requested_execution = value.get("requested_execution")
    expected_scratch = Path(
        f"/tmp/open_frontier_paired_v2/{record_id}/revision/{arm}/iter_{iteration}"
    )
    expected_execution = {
        "model": "gpt-5.6-sol",
        "reasoning_effort": "max",
        "sandbox": "workspace-write",
        "working_directory": str(expected_scratch),
        "repository_writes_forbidden": True,
    }
    if requested_execution != expected_execution:
        diagnostics.invalid("PROMPT_EXECUTION_CONTRACT_MISMATCH", artifact.path,
                            "requested_execution differs from the paired protocol")
        valid = False

    if "metadata_payload_sha256" not in value:
        diagnostics.invalid("PROMPT_SELF_HASH_MISSING", artifact.path,
                            "metadata_payload_sha256 is required")
        valid = False
    else:
        unsigned_metadata = copy.deepcopy(value)
        recorded_metadata_hash = unsigned_metadata.pop("metadata_payload_sha256")
        if recorded_metadata_hash != sha_bytes(canonical_bytes(unsigned_metadata)):
            diagnostics.invalid("PROMPT_SELF_HASH_MISMATCH", artifact.path,
                                "metadata_payload_sha256 is wrong")
            valid = False

    # If a wrapper records matched IDs, enforce the full subset chain.  The
    # canonical revision field is acted_on_entry_ids; matched IDs are optional
    # telemetry rather than model-controlled treatment evidence.
    matched = value.get("matched_entry_ids", value.get("matched_ids"))
    if matched is not None and revision is not None:
        retrieved = revision.value.get("retrieved_entry_ids", [])
        acted = revision.value.get("acted_on_entry_ids", [])
        if not unique_strings(matched):
            diagnostics.invalid("MATCHED_IDS_INVALID", artifact.path,
                                "matched entry IDs must be unique nonempty strings")
            valid = False
        elif not set(acted).issubset(set(matched)) or not set(matched).issubset(set(retrieved)):
            diagnostics.invalid("TREATMENT_SUBSET_CHAIN_INVALID", artifact.path,
                                "required relation is acted_on subset matched subset retrieved")
            valid = False
    return valid


def validate_audit_metadata(artifact: Artifact, record_id: str, arm: str,
                            iteration: int, source: Artifact, parent: Artifact,
                            audit: Artifact, diagnostics: Diagnostics,
                            run: Path) -> bool:
    value = artifact.value
    stage = "BASELINE_AUDIT" if arm == "neutral" else "REVISION_AUDIT"
    valid = True
    for key, wanted in {
        "schema": AUDIT_METADATA_SCHEMA,
        "run_id": RUN_ID,
        "record_id": record_id,
        "stage": stage,
        "arm": arm,
        "iteration": iteration,
    }.items():
        if value.get(key) != wanted:
            diagnostics.invalid("AUDIT_METADATA_IDENTITY_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False
    if not validate_exact_binding(value.get("source"), source, "source", diagnostics,
                                  artifact.path, run):
        valid = False
    if not validate_exact_binding(value.get("parent"), parent, "parent", diagnostics,
                                  artifact.path, run):
        valid = False
    prompt = value.get("prompt_text")
    if type(prompt) is not str or not prompt:
        diagnostics.invalid("AUDIT_PROMPT_TEXT_MISSING", artifact.path,
                            "audit metadata must persist the full prompt")
        valid = False
        prompt = ""
    prompt_bytes = prompt.encode("utf-8")
    if value.get("prompt_utf8_sha256") != sha_bytes(prompt_bytes):
        diagnostics.invalid("AUDIT_PROMPT_HASH_MISMATCH", artifact.path,
                            "audit prompt hash is wrong")
        valid = False
    if value.get("prompt_size_bytes") != len(prompt_bytes):
        diagnostics.invalid("AUDIT_PROMPT_SIZE_MISMATCH", artifact.path,
                            "audit prompt size is wrong")
        valid = False
    for required_text in (parent.sha256, record_id):
        if required_text not in prompt:
            diagnostics.invalid("AUDIT_PROMPT_BINDING_TEXT_MISSING", artifact.path,
                                f"audit prompt does not contain {required_text!r}")
            valid = False
    for index, row in enumerate(parent.value.get("results", [])):
        claim = row.get("claim") if type(row) is dict else None
        # The prompt embeds the binding array as JSON.  A claim containing a
        # literal backslash is therefore present in escaped JSON form rather
        # than as the raw parsed string.  Accept the raw form (useful in prose)
        # or the exact JSON string literal, while still requiring its hash.
        claim_in_prompt = type(claim) is str and (
            claim in prompt or json.dumps(claim, ensure_ascii=False) in prompt
        )
        if type(claim) is str and (not claim_in_prompt or sha_text(claim) not in prompt):
            diagnostics.invalid("AUDIT_PROMPT_CLAIM_BINDING_MISSING", artifact.path,
                                f"claim {index} and its hash are not present in audit prompt")
            valid = False
    if (RECEIPT_SCHEMA in prompt or ACTIVE_RECEIPT_SCHEMA in prompt
            or "BUGBANK_FEEDBACK_EXPOSURE" in prompt):
        diagnostics.invalid("AUDIT_PROMPT_TREATMENT_CONTAMINATION", artifact.path,
                            "independent audit prompt contains a treatment receipt")
        valid = False

    scratch = Path(
        f"/tmp/open_frontier_paired_v2/{record_id}/audit-baseline"
        if arm == "neutral" else
        f"/tmp/open_frontier_paired_v2/{record_id}/audit-revision/{arm}/iter_{iteration}"
    )
    expected_execution = {
        "model": "gpt-5.6-sol",
        "reasoning_effort": "max",
        "sandbox": "workspace-write",
        "working_directory": str(scratch),
        "repository_writes_forbidden": True,
    }
    if value.get("requested_execution") != expected_execution:
        diagnostics.invalid("AUDIT_EXECUTION_CONTRACT_MISMATCH", artifact.path,
                            "requested_execution differs from the audit protocol")
        valid = False

    expected_checkers: dict[int, str] = {}
    for index, claim in enumerate(audit.value.get("claims", [])):
        checker = claim.get("checker_path") if type(claim) is dict else None
        if checker == "none":
            continue
        if type(checker) is not str or not checker.startswith("/"):
            diagnostics.invalid("AUDIT_CHECKER_PATH_INVALID", artifact.path,
                                f"claim {index} checker_path must be absolute or 'none'")
            valid = False
            continue
        try:
            Path(checker).resolve().relative_to(scratch.resolve())
        except ValueError:
            diagnostics.invalid("AUDIT_CHECKER_OUTSIDE_SCRATCH", artifact.path,
                                f"claim {index} checker escapes exact scratch")
            valid = False
            continue
        expected_checkers[index] = checker

    checker_rows = value.get("checker_artifacts")
    if type(checker_rows) is not list:
        diagnostics.invalid("AUDIT_CHECKER_METADATA_INVALID", artifact.path,
                            "checker_artifacts must be an array")
        valid = False
        checker_rows = []
    seen_indices: set[int] = set()
    observed_order: list[int] = []
    for row in checker_rows:
        if type(row) is not dict or not is_int(row.get("idx")):
            diagnostics.invalid("AUDIT_CHECKER_BINDING_INVALID", artifact.path,
                                "checker artifact row lacks an integer idx")
            valid = False
            continue
        index = row["idx"]
        if index in seen_indices or index not in expected_checkers:
            diagnostics.invalid("AUDIT_CHECKER_BINDING_INVALID", artifact.path,
                                f"unexpected or duplicate checker idx {index}")
            valid = False
            continue
        seen_indices.add(index)
        observed_order.append(index)
        original_path = expected_checkers[index]
        if "durable" not in row and {"path", "sha256", "size_bytes"}.issubset(row):
            # Audits already in flight when durable archiving was introduced
            # produced this claim-indexed live-scratch binding.  It is not a
            # publishable verification record, but is a recoverable missing
            # stage rather than evidence of falsified lineage.
            if row.get("path") != original_path:
                diagnostics.invalid(
                    "LEGACY_AUDIT_CHECKER_PATH_MISMATCH", artifact.path,
                    f"legacy checker idx {index} path does not bind the audit claim",
                )
            legacy_path = Path(original_path)
            if legacy_path.is_file() and not legacy_path.is_symlink():
                if (row.get("sha256") != sha_file(legacy_path)
                        or row.get("size_bytes") != legacy_path.stat().st_size):
                    diagnostics.invalid(
                        "LEGACY_AUDIT_CHECKER_HASH_MISMATCH", artifact.path,
                        f"legacy checker idx {index} does not match live scratch bytes",
                    )
            diagnostics.missing(
                "DURABLE_AUDIT_CHECKER_MISSING", artifact.path,
                f"checker idx {index} must be archived into the run before publication",
            )
            valid = False
            continue
        if row.get("original_scratch_path") != original_path:
            diagnostics.invalid("AUDIT_CHECKER_ORIGINAL_PATH_MISMATCH", artifact.path,
                                f"checker idx {index} original scratch path is wrong")
            valid = False
        original_hash = row.get("original_sha256")
        original_size = row.get("original_size_bytes")
        hash_valid = (isinstance(original_hash, str)
                      and SHA256_RE.fullmatch(original_hash) is not None)
        size_valid = is_int(original_size) and original_size >= 0
        if not hash_valid:
            diagnostics.invalid("AUDIT_CHECKER_ORIGINAL_HASH_INVALID", artifact.path,
                                f"checker idx {index} original hash is invalid")
            valid = False
        if not size_valid:
            diagnostics.invalid("AUDIT_CHECKER_ORIGINAL_SIZE_INVALID", artifact.path,
                                f"checker idx {index} original size is invalid")
            valid = False
        durable = row.get("durable")
        if type(durable) is not dict or not hash_valid or not size_valid:
            diagnostics.invalid("AUDIT_DURABLE_CHECKER_BINDING_INVALID", artifact.path,
                                f"checker idx {index} lacks durable binding")
            valid = False
            continue
        expected_directory = (
            run / f"checkers/audits/baseline/{record_id}"
            if arm == "neutral" else
            run / f"checkers/audits/iterations/{record_id}/{arm}/iter_{iteration}"
        )
        expected_durable = expected_directory / f"claim_{index}__{original_hash}.checker"
        if expected_durable.is_symlink() or not expected_durable.is_file():
            diagnostics.invalid("AUDIT_DURABLE_CHECKER_MISSING", artifact.path,
                                f"checker idx {index} durable file is absent or a symlink")
            valid = False
            continue
        if not validate_current_file_record(
                durable, expected_durable, f"checker_artifacts[{index}].durable",
                diagnostics, artifact.path, run):
            valid = False
        if durable.get("sha256") != original_hash or durable.get("size_bytes") != original_size:
            diagnostics.invalid("AUDIT_DURABLE_CHECKER_ORIGINAL_MISMATCH", artifact.path,
                                f"checker idx {index} durable bytes differ from original seal")
            valid = False
    if seen_indices != set(expected_checkers):
        diagnostics.invalid("AUDIT_CHECKER_BINDINGS_INCOMPLETE", artifact.path,
                            "checker_artifacts do not bind every cited checker")
        valid = False
    if observed_order != sorted(expected_checkers):
        diagnostics.invalid("AUDIT_CHECKER_BINDING_ORDER_INVALID", artifact.path,
                            "checker_artifacts must follow increasing non-none claim idx")
        valid = False

    unsigned = copy.deepcopy(value)
    recorded_hash = unsigned.pop("metadata_payload_sha256", None)
    if recorded_hash != sha_bytes(canonical_bytes(unsigned)):
        diagnostics.invalid("AUDIT_METADATA_SELF_HASH_MISMATCH", artifact.path,
                            "metadata_payload_sha256 is absent or wrong")
        valid = False
    return valid


def discover_iterations(directory: Path, diagnostics: Diagnostics,
                        *, layout: str) -> dict[tuple[str, str, int], Path]:
    found: dict[tuple[str, str, int], Path] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.rglob("*.json")):
        try:
            parts = path.relative_to(directory).parts
        except ValueError:
            continue
        if layout == "tree":
            match = (len(parts) == 3 and re.fullmatch(r"iter_(\d+)\.json", parts[2]))
            if not match:
                diagnostics.invalid("NONCANONICAL_ITERATION_PATH", path,
                                    "expected <record>/<arm>/iter_N.json")
                continue
            record_id, arm = parts[0], parts[1]
            iteration = int(re.fullmatch(r"iter_(\d+)\.json", parts[2]).group(1))
        else:
            if len(parts) != 1:
                diagnostics.invalid("NONCANONICAL_PROMPT_PATH", path,
                                    "prompt metadata must be directly under prompts/")
                continue
            match = re.fullmatch(r"(.+)__(plain|bugbank)__iter_(\d+)\.json", parts[0])
            if match is None:
                diagnostics.invalid("NONCANONICAL_PROMPT_PATH", path,
                                    "expected <record>__<arm>__iter_N.json")
                continue
            record_id, arm, raw_iteration = match.groups()
            iteration = int(raw_iteration)
        key = (record_id, arm, iteration)
        if record_id not in EXPECTED_SET:
            diagnostics.invalid("ARTIFACT_OUTSIDE_UNIVERSE", path,
                                f"record {record_id!r} is outside the 31-ID universe")
        if arm not in ARMS:
            diagnostics.invalid("UNKNOWN_ARM", path, f"unknown arm {arm!r}")
        if not 1 <= iteration <= MAX_ITERATION:
            diagnostics.invalid("ITERATION_OUT_OF_RANGE", path,
                                f"iteration must lie in 1..{MAX_ITERATION}")
        if key in found:
            diagnostics.invalid("DUPLICATE_ARTIFACT", path,
                                f"duplicate canonical artifact identity {key!r}")
        found[key] = path
    return found


def discover_receipts(directory: Path, diagnostics: Diagnostics) -> dict[tuple[str, int], Path]:
    found: dict[tuple[str, int], Path] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.rglob("*.json")):
        parts = path.relative_to(directory).parts
        if len(parts) != 1:
            diagnostics.invalid("NONCANONICAL_RECEIPT_PATH", path,
                                "receipt must be directly under retrievals/")
            continue
        match = re.fullmatch(r"(.+)__iter_(\d+)\.json", parts[0])
        if match is None:
            diagnostics.invalid("NONCANONICAL_RECEIPT_PATH", path,
                                "expected <record>__iter_N.json")
            continue
        record_id, raw_iteration = match.groups()
        iteration = int(raw_iteration)
        key = (record_id, iteration)
        if record_id not in EXPECTED_SET:
            diagnostics.invalid("ARTIFACT_OUTSIDE_UNIVERSE", path,
                                f"record {record_id!r} is outside the 31-ID universe")
        if not 1 <= iteration <= MAX_ITERATION:
            diagnostics.invalid("ITERATION_OUT_OF_RANGE", path,
                                f"iteration must lie in 1..{MAX_ITERATION}")
        found[key] = path
    return found


def check_simple_directory(directory: Path, diagnostics: Diagnostics,
                           allowed_ids: frozenset[str]) -> None:
    if not directory.is_dir():
        return
    for path in sorted(directory.glob("*.json")):
        if path.stem not in allowed_ids:
            diagnostics.invalid("ARTIFACT_OUTSIDE_UNIVERSE", path,
                                f"record {path.stem!r} is outside the 31-ID universe")


def recursive_numeric_fields(value: Any, prefix: str = "") -> Iterable[tuple[str, float]]:
    if type(value) is dict:
        for key, item in value.items():
            nested = f"{prefix}.{key}" if prefix else key
            yield from recursive_numeric_fields(item, nested)
    elif is_number(value):
        yield prefix, float(value)


def collect_telemetry(run: Path, diagnostics: Diagnostics) -> dict[str, Any]:
    token_pattern = re.compile(r"tokens used\s*\n\s*([0-9][0-9,]*)", re.IGNORECASE)
    log_records: list[dict[str, Any]] = []
    tokens_by_stage: Counter[str] = Counter()
    tokens_by_arm: Counter[str] = Counter()
    tokens_by_stage_arm: Counter[str] = Counter()
    log_tokens_by_record_arm: Counter[str] = Counter()
    logs_root = run / "logs"
    if logs_root.is_dir():
        for path in sorted(logs_root.rglob("*.log")):
            try:
                raw = path.read_bytes()
            except OSError as error:
                diagnostics.warn("LOG_UNREADABLE", path, str(error))
                continue
            text = raw.decode("utf-8", errors="replace")
            matches = token_pattern.findall(text)
            tokens = int(matches[-1].replace(",", "")) if matches else None
            stage = path.relative_to(logs_root).parts[0]
            filename_parts = path.stem.split("__")
            record_id = filename_parts[0]
            arm = next((part for part in filename_parts if part in ARMS), None)
            if arm is None:
                arm = "bugbank" if stage == "receipt" else "neutral"
            if tokens is not None:
                tokens_by_stage[stage] += tokens
                tokens_by_arm[arm] += tokens
                tokens_by_stage_arm[f"{stage}:{arm}"] += tokens
                log_tokens_by_record_arm[f"{record_id}:{arm}"] += tokens
            log_records.append({
                "path": rel(path, run),
                "sha256": sha_bytes(raw),
                "size_bytes": len(raw),
                "tokens_used": tokens,
                "stage": stage,
                "arm": arm,
            })

    state_records: list[dict[str, Any]] = []
    duration_by_stage: defaultdict[str, float] = defaultdict(float)
    duration_by_arm: defaultdict[str, float] = defaultdict(float)
    duration_by_stage_arm: defaultdict[str, float] = defaultdict(float)
    explicit_cost_fields: defaultdict[str, float] = defaultdict(float)
    explicit_cost_by_arm: defaultdict[str, float] = defaultdict(float)
    structured_token_fields: defaultdict[str, float] = defaultdict(float)
    structured_tokens_by_arm: defaultdict[str, float] = defaultdict(float)
    state_duration_by_record_arm: defaultdict[str, float] = defaultdict(float)
    state_tokens_by_record_arm: defaultdict[str, float] = defaultdict(float)
    states_root = run / "states"
    if states_root.is_dir():
        for path in sorted(states_root.glob("*.json")):
            artifact = load_json_artifact(path, diagnostics)
            if artifact is None:
                continue
            value = artifact.value
            start = parse_timestamp(value.get("started_at"))
            end = parse_timestamp(value.get("ended_at"))
            duration = (end - start).total_seconds() if start and end and end >= start else None
            stage = str(value.get("stage", "unknown"))
            arm_value = value.get("arm")
            arm = arm_value if arm_value in ARMS else (
                "bugbank" if stage == "receipt" else "neutral"
            )
            if duration is not None:
                duration_by_stage[stage] += duration
                duration_by_arm[arm] += duration
                duration_by_stage_arm[f"{stage}:{arm}"] += duration
                if type(value.get("record_id")) is str:
                    state_duration_by_record_arm[
                        f"{value['record_id']}:{arm}"
                    ] += duration
            for name, number in recursive_numeric_fields(value):
                leaf = name.rsplit(".", 1)[-1].lower()
                if "cost" in leaf and (leaf.endswith("usd") or leaf == "cost"):
                    explicit_cost_fields[name] += number
                    explicit_cost_by_arm[arm] += number
                if "token" in leaf:
                    structured_token_fields[name] += number
                    if leaf in {"tokens", "tokens_used", "total_tokens"}:
                        structured_tokens_by_arm[arm] += number
                        if type(value.get("record_id")) is str:
                            state_tokens_by_record_arm[
                                f"{value['record_id']}:{arm}"
                            ] += number
            state_records.append({
                "path": rel(path, run), "sha256": artifact.sha256,
                "record_id": value.get("record_id"), "stage": stage,
                "arm": arm, "status": value.get("status"),
                "duration_seconds": duration,
            })

    receipt_duration = 0.0
    receipt_duration_count = 0
    for path in sorted((run / "retrievals").glob("*.json")) if (run / "retrievals").is_dir() else []:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            duration = value.get("timing", {}).get("duration_seconds")
            if is_number(duration):
                receipt_duration += float(duration)
                receipt_duration_count += 1
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            pass

    prompt_counts: Counter[str] = Counter()
    prompt_bytes: Counter[str] = Counter()
    receipt_exposure_bytes: Counter[str] = Counter()
    prompts_root = run / "prompts"
    if prompts_root.is_dir():
        for path in sorted(prompts_root.glob("*.json")):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                continue
            arm = value.get("arm")
            if arm not in ARMS:
                continue
            prompt_counts[arm] += 1
            size = value.get("prompt_size_bytes")
            if is_number(size):
                prompt_bytes[arm] += int(size)
            exposure = value.get("exposure")
            if type(exposure) is dict:
                start = exposure.get("receipt_start_byte")
                end = exposure.get("receipt_end_byte")
                if is_int(start) and is_int(end) and end >= start:
                    receipt_exposure_bytes[arm] += end - start
    return {
        "logs": {
            "count": len(log_records),
            "with_final_token_count": sum(row["tokens_used"] is not None
                                           for row in log_records),
            "tokens_used_total": sum(tokens_by_stage.values()),
            "tokens_used_by_stage": dict(sorted(tokens_by_stage.items())),
            "tokens_used_by_arm": dict(sorted(tokens_by_arm.items())),
            "tokens_used_by_stage_arm": dict(sorted(tokens_by_stage_arm.items())),
            "tokens_used_by_record_arm": dict(sorted(log_tokens_by_record_arm.items())),
            "raw_log_bindings": log_records,
            "validity_note": "logs are telemetry only and are not required for artifact validity",
        },
        "states": {
            "count": len(state_records),
            "completed_duration_seconds_total": sum(duration_by_stage.values()),
            "completed_duration_seconds_by_stage": dict(sorted(duration_by_stage.items())),
            "completed_duration_seconds_by_arm": dict(sorted(duration_by_arm.items())),
            "completed_duration_seconds_by_stage_arm": dict(
                sorted(duration_by_stage_arm.items())
            ),
            "records": state_records,
            "duration_seconds_by_record_arm": dict(
                sorted(state_duration_by_record_arm.items())
            ),
        },
        "structured_token_fields": dict(sorted(structured_token_fields.items())),
        "structured_tokens_used_by_arm": dict(sorted(structured_tokens_by_arm.items())),
        "structured_tokens_used_by_record_arm": dict(
            sorted(state_tokens_by_record_arm.items())
        ),
        "explicit_cost_fields": dict(sorted(explicit_cost_fields.items())),
        "explicit_cost_usd_by_arm": dict(sorted(explicit_cost_by_arm.items())),
        "explicit_cost_usd_total": (
            sum(explicit_cost_fields.values()) if explicit_cost_fields else None
        ),
        "cost_note": (
            "No cost is inferred from tokens; only explicitly recorded monetary fields are summed."
        ),
        "receipt_retrieval_duration_seconds_total": receipt_duration,
        "receipt_retrieval_duration_count": receipt_duration_count,
        "prompt_exposure": {
            "prompt_count_by_arm": {arm: prompt_counts[arm] for arm in ARMS},
            "prompt_utf8_bytes_by_arm": {arm: prompt_bytes[arm] for arm in ARMS},
            "receipt_payload_bytes_exposed_by_arm": {
                arm: receipt_exposure_bytes[arm] for arm in ARMS
            },
        },
    }


def ordered_claims(artifact: Artifact) -> list[str] | None:
    results = artifact.value.get("results")
    if type(results) is not list:
        return None
    claims: list[str] = []
    for row in results:
        if type(row) is not dict or type(row.get("claim")) is not str:
            return None
        claims.append(row["claim"])
    return claims


def proof_state(artifact: Artifact) -> dict[str, Any] | None:
    results = artifact.value.get("results")
    if type(results) is not list:
        return None
    normalized_results: list[dict[str, str]] = []
    for row in results:
        if (type(row) is not dict or type(row.get("claim")) is not str
                or type(row.get("proof_sketch")) is not str):
            return None
        normalized_results.append({
            "claim": row["claim"],
            "proof_sketch": row["proof_sketch"],
        })
    claimed_resolution = artifact.value.get("claimed_resolution")
    final_writeup = artifact.value.get("final_writeup")
    if type(claimed_resolution) is not str or type(final_writeup) is not str:
        return None
    return {
        "claimed_resolution": claimed_resolution,
        "results": normalized_results,
        "final_writeup": final_writeup,
    }


def proof_state_sha256(artifact: Artifact) -> str | None:
    state = proof_state(artifact)
    return sha_bytes(canonical_bytes(state)) if state is not None else None


def auditable_arm_model_tokens(run: Path, record_id: str, arm: str,
                               through_iteration: int) -> tuple[int | None, bool]:
    total = 0
    for iteration in range(1, through_iteration + 1):
        for stage in ("revision", "audit-revision"):
            path = run / (
                f"states/{record_id}__{arm}__iter_{iteration}__{stage}.json"
            )
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                return None, False
            tokens = value.get("tokens_used")
            if (value.get("record_id") != record_id
                    or value.get("arm") != arm
                    or value.get("iteration") != iteration
                    or value.get("stage") != stage
                    or value.get("model") != "gpt-5.6-sol"
                    or value.get("reasoning_effort") != "max"
                    or value.get("status") not in {"COMPLETE", "RECOVERED_COMPLETE"}
                    or not is_int(tokens) or tokens < 0):
                return None, False
            total += tokens
    return total, True


def artifact_binding_dict(artifact: Artifact | None) -> dict[str, Any] | None:
    if artifact is None:
        return None
    return {
        "path": str(artifact.path),
        "sha256": artifact.sha256,
        "size_bytes": artifact.size_bytes,
    }


def audit_verifies_full_solution(revision: Artifact, audit: Artifact) -> bool:
    """Return whether one valid independent audit proves the exact target solved."""
    results = revision.value.get("results")
    claims = audit.value.get("claims")
    return bool(
        audit.value.get("complete") is True
        and revision.value.get("claimed_resolution") == "FULL"
        and audit.value.get("target_verdict") == "FULLY_RESOLVES_TARGET"
        and audit.value.get("claimed_resolution_verdict") == "ACCURATE"
        and audit.value.get("overall") == "VERIFIED"
        and audit.value.get("confirmed_refutations") == []
        and type(results) is list
        and type(claims) is list
        and bool(claims)
        and len(claims) == len(results)
        and all(type(row) is dict and row.get("verdict") == "VERIFIED"
                for row in claims)
    )


def whole_proof_prompt(artifact: Artifact | None, run: Path) -> bool:
    return bool(
        artifact is not None
        and artifact.path.parent.resolve()
        == (run / "prompts_whole_proof_v2").resolve()
        and artifact.value.get("claim_coverage_policy") == CLAIM_COVERAGE_POLICY
    )


def stable_plain_waits_for_bugbank(
        revision: Artifact | None, audit: Artifact | None,
        parent: Artifact | None, prompt_metadata: Artifact | None,
        audit_valid: bool, run: Path,
        bugbank_terminal: dict[str, Any] | None) -> bool:
    return bool(
        bugbank_terminal is None
        and revision is not None and revision.value.get("arm") == "plain"
        and audit is not None and parent is not None and audit_valid
        and whole_proof_prompt(prompt_metadata, run)
        and proof_state(revision) == proof_state(parent)
        and audit.value.get("complete") is True
        and audit.value.get("confirmed_refutations") == []
        and audit.value.get("claimed_resolution_verdict") == "ACCURATE"
        and audit.value.get("target_verdict") != "OVERCLAIMED"
        and not audit_verifies_full_solution(revision, audit)
    )


def derive_terminal_state(revision: Artifact | None, audit: Artifact | None,
                          parent: Artifact | None, prompt_metadata: Artifact | None,
                          receipt: Artifact | None, audit_valid: bool, run: Path,
                          record_id: str,
                          bugbank_token_target: int | None = None) -> dict[str, Any] | None:
    if revision is None or audit is None or parent is None or not audit_valid:
        return None
    iteration = revision.value.get("iteration")
    if not is_int(iteration):
        return None
    refutations = audit.value.get("confirmed_refutations")
    claim_fixed = ordered_claims(revision) == ordered_claims(parent)
    proof_fixed = proof_state(revision) == proof_state(parent)
    arm = revision.value.get("arm")
    bugbank_recheck_required = (
        arm == "bugbank"
        and type(revision.value.get("acted_on_entry_ids")) is list
        and bool(revision.value["acted_on_entry_ids"])
    )
    model_tokens, token_cost_auditable = auditable_arm_model_tokens(
        run, record_id, arm, iteration
    )
    if arm == "plain":
        token_budget_target = bugbank_token_target
        token_budget_used = model_tokens
        token_budget_auditable = (
            token_cost_auditable and is_int(token_budget_target)
            and token_budget_target >= 0
        )
        token_budget_matched = (
            token_budget_auditable and is_int(token_budget_used)
            and token_budget_used >= token_budget_target
        )
    else:
        token_budget_target = None
        token_budget_used = None
        token_budget_auditable = token_cost_auditable
        token_budget_matched = token_cost_auditable
    audit_settled = (
        audit.value.get("complete") is True
        and refutations == []
        and audit.value.get("claimed_resolution_verdict") == "ACCURATE"
        and audit.value.get("target_verdict") != "OVERCLAIMED"
    )
    solved_by_audit = audit_verifies_full_solution(revision, audit)
    fixed = bool(
        whole_proof_prompt(prompt_metadata, run)
        and audit_settled
        and proof_fixed
        and not bugbank_recheck_required
        and token_budget_matched
    )
    if solved_by_audit:
        reason = "VERIFIED_FULL_INDEPENDENT_AUDIT"
        status = "VERIFIED_FULL"
        # A correct solution needs neither another BugBank pass nor token
        # matching.  Preserve proof equality only as descriptive evidence.
        fixed_point = proof_fixed
        bugbank_recheck_required = False
    elif fixed:
        reason = "AUDITED_FIXED_POINT"
        status = "INCONCLUSIVE_FIXED_POINT"
        fixed_point = True
    else:
        return None
    all_verified = (
        type(audit.value.get("claims")) is list
        and bool(audit.value["claims"])
        and all(row.get("verdict") == "VERIFIED" for row in audit.value["claims"]
                if type(row) is dict)
        and len(audit.value["claims"]) == len(revision.value.get("results", []))
    )
    verified_full = solved_by_audit
    verified_partial = (
        audit.value.get("target_verdict") == "VALID_PARTIAL_PROGRESS"
        and all_verified
    )
    claims = audit.value.get("claims", [])
    audit_counts = {
        verdict.lower(): sum(type(row) is dict and row.get("verdict") == verdict
                             for row in claims)
        for verdict in ("VERIFIED", "REFUTED", "UNRESOLVED")
    }
    return {
        "arm": revision.value.get("arm"),
        "status": status,
        "terminal": True,
        "terminal_reason": reason,
        "iteration": iteration,
        "revision_sha256": revision.sha256,
        "audit_sha256": audit.sha256,
        "claimed_resolution": revision.value.get("claimed_resolution"),
        "target_verdict": audit.value.get("target_verdict"),
        "audit_overall": audit.value.get("overall"),
        "fixed_point": fixed_point,
        "claim_fixed": claim_fixed,
        "ordered_claim_set_unchanged": claim_fixed,
        "proof_state_unchanged": proof_fixed,
        "parent_proof_state_sha256": proof_state_sha256(parent),
        "revision_proof_state_sha256": proof_state_sha256(revision),
        "bugbank_recheck_required": bugbank_recheck_required,
        "model_tokens_used": model_tokens,
        "model_token_cost_auditable": token_cost_auditable,
        "token_budget_target": token_budget_target,
        "token_budget_used": token_budget_used,
        "token_budget_matched": token_budget_matched,
        "token_budget_auditable": token_budget_auditable,
        "token_budget_overshoot": (
            token_budget_used - token_budget_target
            if (arm == "plain" and is_int(token_budget_used)
                and is_int(token_budget_target)) else None
        ),
        "every_claim_verified": all_verified,
        "claim_count": len(revision.value.get("results", [])),
        "audit_counts": audit_counts,
        "claimed_resolution_verdict": audit.value.get("claimed_resolution_verdict"),
        "ordered_claims_sha256": sha_bytes(canonical_bytes(ordered_claims(revision))),
        "verified_full": verified_full,
        "verified_partial": verified_partial,
        "parent_binding": artifact_binding_dict(parent),
        "revision_binding": artifact_binding_dict(revision),
        "audit_binding": artifact_binding_dict(audit),
        "prompt_metadata_binding": artifact_binding_dict(prompt_metadata),
        "receipt_binding": artifact_binding_dict(receipt),
    }


def validate_pair_terminal(artifact: Artifact, record_id: str,
                           arm_states: Mapping[str, dict[str, Any] | None],
                           baseline: Artifact | None, baseline_audit: Artifact | None,
                           diagnostics: Diagnostics, run: Path) -> bool:
    value = artifact.value
    valid = True
    common_identity = {
        "schema": "open_frontier_paired_v2_pair_terminal_v3",
        "run_id": RUN_ID,
        "record_id": record_id,
        "stage": "PAIR_TERMINAL",
        "max_iterations": MAX_ITERATION,
        "retrieval_k": RETRIEVAL_K,
    }
    for key, wanted in common_identity.items():
        if value.get(key) != wanted:
            diagnostics.invalid("PAIR_TERMINAL_IDENTITY_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False

    endpoints_complete = all(arm_states.get(arm) is not None for arm in ARMS)
    endpoint_tokens: dict[str, int | None] = {}
    for arm in ARMS:
        state = arm_states.get(arm)
        tokens = state.get("model_tokens_used") if state is not None else None
        endpoint_tokens[arm] = tokens if is_int(tokens) and tokens >= 0 else None
    comparison_auditable = all(endpoint_tokens[arm] is not None for arm in ARMS)
    pair_complete = endpoints_complete and comparison_auditable
    plain_state = arm_states.get("plain")
    plain_solved = bool(
        plain_state is not None and plain_state.get("status") == "VERIFIED_FULL"
    )
    expected_pair_fields = {
        "status": "COMPLETE" if pair_complete else "INCOMPLETE",
        "pair_status": "COMPLETE" if pair_complete else "INCOMPLETE",
        "treatment_contrast_valid": pair_complete,
        "proof_endpoints_complete": endpoints_complete,
        "token_comparison_auditable": comparison_auditable,
        "solved_arms": [
            arm for arm in ARMS
            if (arm_states.get(arm) is not None
                and arm_states[arm].get("status") == "VERIFIED_FULL")
        ],
        "bugbank_model_tokens_used": endpoint_tokens["bugbank"],
        "plain_model_tokens_used": endpoint_tokens["plain"],
        "plain_minus_bugbank_tokens": (
            endpoint_tokens["plain"] - endpoint_tokens["bugbank"]
            if comparison_auditable else None
        ),
        "plain_solved_with_fewer_tokens": (
            endpoint_tokens["plain"] < endpoint_tokens["bugbank"]
            if plain_solved and comparison_auditable else None
        ),
    }
    for key, wanted in expected_pair_fields.items():
        if value.get(key) != wanted:
            diagnostics.invalid("PAIR_TERMINAL_METRIC_MISMATCH", artifact.path,
                                f"{key} must be {wanted!r}")
            valid = False

    arms = value.get("arms")
    if type(arms) is not dict or set(arms) != set(ARMS):
        diagnostics.invalid("PAIR_TERMINAL_ARMS_INVALID", artifact.path,
                            "arms must contain exactly plain and bugbank")
        valid = False
    else:
        for arm in ARMS:
            expected = arm_states.get(arm)
            row = arms.get(arm)
            if type(row) is not dict:
                diagnostics.invalid("PAIR_TERMINAL_ARM_INVALID", artifact.path,
                                    f"arms.{arm} must be an object")
                valid = False
                continue
            if expected is None:
                if (row.get("arm") != arm or row.get("terminal") is not False
                        or row.get("status") != "INCOMPLETE"
                        or row.get("terminal_reason") != "INCOMPLETE"):
                    diagnostics.invalid(
                        "INCOMPLETE_ARM_STATUS_INVALID", artifact.path,
                        f"arms.{arm} is not a coherent incomplete state",
                    )
                    valid = False
                continue
            for key in (
                "arm", "terminal_reason", "iteration", "revision_sha256",
                "audit_sha256", "claimed_resolution", "target_verdict",
                "audit_overall", "status", "terminal", "fixed_point",
                "ordered_claim_set_unchanged", "proof_state_unchanged",
                "parent_proof_state_sha256", "revision_proof_state_sha256",
                "bugbank_recheck_required", "model_tokens_used",
                "model_token_cost_auditable", "token_budget_target",
                "token_budget_used", "token_budget_matched",
                "token_budget_auditable", "token_budget_overshoot",
                "every_claim_verified", "claim_count", "audit_counts",
                "claimed_resolution_verdict", "ordered_claims_sha256",
            ):
                if row.get(key) != expected[key]:
                    diagnostics.invalid(
                        "PAIR_TERMINAL_BINDING_MISMATCH", artifact.path,
                        f"arms.{arm}.{key} must be {expected[key]!r}",
                    )
                    valid = False
            if type(row.get("reason")) is not str or not row["reason"].strip():
                diagnostics.invalid("PAIR_TERMINAL_REASON_MISSING", artifact.path,
                                    f"arms.{arm}.reason must be nonempty")
                valid = False
            binding_fields = (
                ("parent", "parent_binding"),
                ("revision", "revision_binding"),
                ("audit", "audit_binding"),
                ("prompt_metadata", "prompt_metadata_binding"),
            )
            for row_key, expected_key in binding_fields:
                expected_binding = expected.get(expected_key)
                binding = row.get(row_key)
                if expected_binding is None or type(binding) is not dict:
                    diagnostics.invalid(
                        "PAIR_TERMINAL_ARTIFACT_BINDING_MISSING", artifact.path,
                        f"arms.{arm}.{row_key} binding is absent",
                    )
                    valid = False
                    continue
                expected_artifact = Artifact(
                    Path(expected_binding["path"]), b"", {},
                    expected_binding["sha256"], expected_binding["size_bytes"],
                )
                if not validate_exact_binding(binding, expected_artifact, row_key,
                                              diagnostics, artifact.path, run):
                    valid = False
            receipt_binding = row.get("receipt")
            expected_receipt = expected.get("receipt_binding")
            if arm == "plain":
                if receipt_binding is not None:
                    diagnostics.invalid(
                        "PAIR_TERMINAL_PLAIN_RECEIPT_PRESENT", artifact.path,
                        "plain terminal receipt must be null",
                    )
                    valid = False
            elif expected_receipt is None or type(receipt_binding) is not dict:
                diagnostics.invalid(
                    "PAIR_TERMINAL_RECEIPT_MISSING", artifact.path,
                    "BugBank terminal receipt binding is absent",
                )
                valid = False
            else:
                receipt_artifact = Artifact(
                    Path(expected_receipt["path"]), b"", {},
                    expected_receipt["sha256"], expected_receipt["size_bytes"],
                )
                if not validate_exact_binding(
                        receipt_binding, receipt_artifact, "receipt",
                        diagnostics, artifact.path, run):
                    valid = False

    baseline_record = value.get("baseline")
    if baseline is None or baseline_audit is None:
        if baseline_record is not None:
            diagnostics.invalid(
                "PAIR_TERMINAL_BASELINE_BINDING_INVALID", artifact.path,
                "baseline must be null while the shared baseline lineage is incomplete",
            )
            valid = False
    elif type(baseline_record) is not dict:
        diagnostics.invalid("PAIR_TERMINAL_BASELINE_BINDING_MISSING", artifact.path,
                            "pair terminal lacks shared baseline/audit bindings")
        valid = False
    else:
        for key, expected_artifact in (("draft", baseline),
                                       ("independent_audit", baseline_audit)):
            if not validate_exact_binding(baseline_record.get(key), expected_artifact, key,
                                          diagnostics, artifact.path, run):
                valid = False

    if "terminal_payload_sha256" not in value:
        diagnostics.invalid("PAIR_TERMINAL_SELF_HASH_MISSING", artifact.path,
                            "terminal_payload_sha256 is required")
        valid = False
    else:
        unsigned = copy.deepcopy(value)
        recorded = unsigned.pop("terminal_payload_sha256")
        if recorded != sha_bytes(canonical_bytes(unsigned)):
            diagnostics.invalid("PAIR_TERMINAL_SELF_HASH_MISMATCH", artifact.path,
                                "terminal_payload_sha256 is wrong")
            valid = False
    if not pair_complete:
        diagnostics.missing(
            "PAIR_TERMINAL_DECLARED_INCOMPLETE", artifact.path,
            "pair terminal snapshot records unfinished arm work or unauditable endpoint tokens",
        )
        return False
    return valid


def classification(draft: Artifact | None, audit: Artifact | None,
                   audit_valid: bool) -> dict[str, Any]:
    claimed = draft.value.get("claimed_resolution") if draft else None
    candidate = claimed in {"FULL", "PARTIAL"}
    all_verified = False
    target_verdict = None
    if audit is not None:
        target_verdict = audit.value.get("target_verdict")
        claims = audit.value.get("claims")
        all_verified = (
            type(claims) is list and bool(claims)
            and all(type(row) is dict and row.get("verdict") == "VERIFIED" for row in claims)
        )
    verified_full = bool(
        audit_valid and draft is not None and claimed == "FULL"
        and target_verdict == "FULLY_RESOLVES_TARGET"
        and audit.value.get("claimed_resolution_verdict") == "ACCURATE"
        and all_verified
    )
    verified_partial = bool(
        audit_valid and draft is not None
        and target_verdict == "VALID_PARTIAL_PROGRESS" and all_verified
    )
    return {
        "claimed_resolution": claimed,
        "candidate": candidate,
        "target_verdict": target_verdict,
        "all_claims_verified": all_verified,
        "verified": verified_full or verified_partial,
        "verified_full": verified_full,
        "verified_partial": verified_partial,
    }


def cutover_cell_from_path(path_text: str) -> tuple[str, str, int] | None:
    patterns = (
        r"iterations/(.+)/(plain|bugbank)/iter_(\d+)\.json",
        r"audits/iterations/(.+)/(plain|bugbank)/iter_(\d+)\.json",
        r"audits/metadata/iterations/(.+)/(plain|bugbank)/iter_(\d+)\.json",
        r"checkers/audits/iterations/(.+)/(plain|bugbank)/iter_(\d+)/.+",
        r"prompts(?:_whole_proof_v2)?/(.+)__(plain|bugbank)__iter_(\d+)\.json",
        r"states/(.+)__(plain|bugbank)__iter_(\d+)__.+\.json",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, path_text)
        if match is not None:
            record_id, arm, iteration = match.groups()
            return record_id, arm, int(iteration)
    receipt = re.fullmatch(
        r"retrievals(?:_whole_proof_v2)?/(.+)__iter_(\d+)\.json", path_text
    )
    if receipt is not None:
        return receipt.group(1), "bugbank", int(receipt.group(2))
    return None


def validate_cutover_endpoint_boundary(
        run: Path, manifest_path: Path, record_id: str, arm: str,
        endpoint: int, row: Mapping[str, Any], diagnostics: Diagnostics) -> bool:
    """Check that a sealed endpoint is the first strict FULL and has exact costs."""
    valid = True
    for earlier in range(1, endpoint):
        earlier_revision = load_json_artifact(
            run / f"iterations/{record_id}/{arm}/iter_{earlier}.json",
            diagnostics,
        )
        earlier_audit = load_json_artifact(
            run / f"audits/iterations/{record_id}/{arm}/iter_{earlier}.json",
            diagnostics,
        )
        if (earlier_revision is not None and earlier_audit is not None
                and audit_verifies_full_solution(
                    earlier_revision, earlier_audit
                )):
            diagnostics.invalid(
                "CUTOVER_ENDPOINT_NOT_FIRST_STRICT_FULL", manifest_path,
                f"{record_id}/{arm} already had strict FULL at {earlier}",
            )
            valid = False
    tokens, auditable = auditable_arm_model_tokens(
        run, record_id, arm, endpoint
    )
    if (not auditable
            or row.get("first_strict_full_endpoint_model_tokens") != tokens
            or row.get("first_strict_full_endpoint_completed_model_calls")
            != 2 * endpoint):
        diagnostics.invalid(
            "CUTOVER_ENDPOINT_TOKEN_MISMATCH", manifest_path,
            f"{record_id}/{arm} endpoint token record is not auditable",
        )
        valid = False
    return valid


def validate_cutover_manifest(run: Path, diagnostics: Diagnostics) -> dict[str, Any]:
    """Validate the immutable cutover and return its exact historical allowlists."""
    path = run / CUTOVER_FILENAME
    artifact = load_json_artifact(path, diagnostics)
    empty = {
        "surplus_paths": set(), "prepared_prompt_paths": set(),
        "prepared_receipt_paths": set(), "endpoints": {},
    }
    if artifact is None:
        diagnostics.invalid(
            "CUTOVER_MANIFEST_MISSING", path,
            "the prospective whole-proof/early-solution cutover must be sealed",
        )
        return empty
    value = artifact.value
    valid = True
    if value.get("schema") != CUTOVER_SCHEMA or value.get("run_id") != RUN_ID:
        diagnostics.invalid(
            "CUTOVER_MANIFEST_IDENTITY_MISMATCH", path,
            "cutover schema or run_id is wrong",
        )
        valid = False
    policy = value.get("policy")
    required_policy = {
        "active_prompt_policy": CLAIM_COVERAGE_POLICY,
        "active_claim_count_cap": None,
        "prepared_legacy_artifacts_are_inert": True,
        "post_cutover_inconclusive_closure_requires_active_prompt_policy": True,
        "first_strict_independent_full_audit_is_terminal": True,
        "post_first_strict_full_artifacts_are_grandfathered_surplus": True,
    }
    if type(policy) is not dict:
        diagnostics.invalid("CUTOVER_POLICY_INVALID", path, "policy must be an object")
        valid = False
    else:
        for key, wanted in required_policy.items():
            if policy.get(key) != wanted:
                diagnostics.invalid(
                    "CUTOVER_POLICY_MISMATCH", path,
                    f"policy.{key} must be {wanted!r}",
                )
                valid = False

    unsigned = copy.deepcopy(value)
    recorded_manifest_hash = unsigned.pop("manifest_payload_sha256", None)
    if recorded_manifest_hash != sha_bytes(canonical_bytes(unsigned)):
        diagnostics.invalid(
            "CUTOVER_MANIFEST_SELF_HASH_MISMATCH", path,
            "manifest_payload_sha256 is absent or wrong",
        )
        valid = False

    boundaries = value.get("arm_boundaries")
    boundary_map: dict[tuple[str, str], dict[str, Any]] = {}
    endpoints: dict[tuple[str, str], int] = {}
    prepared_prompt_paths: set[Path] = set()
    prepared_receipt_paths: set[Path] = set()
    if type(boundaries) is not list or len(boundaries) != 2 * len(EXPECTED_IDS):
        diagnostics.invalid(
            "CUTOVER_BOUNDARIES_INVALID", path,
            "arm_boundaries must contain exactly one row for each record and arm",
        )
        valid = False
        boundaries = []
    for row in boundaries:
        if type(row) is not dict:
            diagnostics.invalid("CUTOVER_BOUNDARY_INVALID", path,
                                "arm boundary must be an object")
            valid = False
            continue
        record_id, arm = row.get("record_id"), row.get("arm")
        key = (record_id, arm)
        if record_id not in EXPECTED_SET or arm not in ARMS or key in boundary_map:
            diagnostics.invalid("CUTOVER_BOUNDARY_IDENTITY_INVALID", path,
                                f"invalid or duplicate boundary {key!r}")
            valid = False
            continue
        boundary_map[key] = row
        endpoint = row.get("first_strict_full_iteration")
        if endpoint is not None and (not is_int(endpoint) or endpoint < 1):
            diagnostics.invalid("CUTOVER_ENDPOINT_INVALID", path,
                                f"{record_id}/{arm} has an invalid FULL endpoint")
            valid = False
            endpoint = None
        if is_int(endpoint):
            endpoints[key] = endpoint
            revision = load_json_artifact(
                run / f"iterations/{record_id}/{arm}/iter_{endpoint}.json", diagnostics
            )
            audit = load_json_artifact(
                run / f"audits/iterations/{record_id}/{arm}/iter_{endpoint}.json",
                diagnostics,
            )
            if (revision is None or audit is None
                    or not audit_verifies_full_solution(revision, audit)):
                diagnostics.invalid(
                    "CUTOVER_ENDPOINT_NOT_STRICT_FULL", path,
                    f"{record_id}/{arm} endpoint is not a strict independent FULL audit",
                )
                valid = False
        elif (row.get("first_strict_full_endpoint_model_tokens") is not None
              or row.get("first_strict_full_endpoint_completed_model_calls") != 0):
            diagnostics.invalid(
                "CUTOVER_NONENDPOINT_TOKEN_MISMATCH", path,
                f"{record_id}/{arm} has endpoint costs without a sealed endpoint",
            )
            valid = False

        highest_revision = row.get("highest_revision_iteration")
        if highest_revision is not None and (
                not is_int(highest_revision) or highest_revision < 1):
            diagnostics.invalid(
                "CUTOVER_HIGHEST_REVISION_INVALID", path,
                f"{record_id}/{arm} highest revision is invalid",
            )
            valid = False
            highest_revision = None
        observed_surplus_tokens = 0
        observed_surplus_calls = 0
        if is_int(endpoint) and is_int(highest_revision):
            for surplus_iteration in range(endpoint + 1, highest_revision + 1):
                for stage in ("revision", "audit-revision"):
                    state_path = run / "states" / (
                        f"{record_id}__{arm}__iter_{surplus_iteration}__{stage}.json"
                    )
                    if not state_path.is_file():
                        continue
                    try:
                        state = json.loads(state_path.read_text(encoding="utf-8"))
                    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                        diagnostics.invalid(
                            "CUTOVER_SURPLUS_STATE_INVALID", state_path,
                            "historical surplus state is unreadable",
                        )
                        valid = False
                        continue
                    tokens = state.get("tokens_used") if type(state) is dict else None
                    if (type(state) is dict
                            and state.get("status") in {
                                "COMPLETE", "RECOVERED_COMPLETE"
                            }
                            and is_int(tokens) and tokens >= 0):
                        observed_surplus_tokens += tokens
                        observed_surplus_calls += 1
        if (row.get("post_endpoint_surplus_completed_model_tokens")
                != observed_surplus_tokens
                or row.get("post_endpoint_surplus_completed_model_calls")
                != observed_surplus_calls):
            diagnostics.invalid(
                "CUTOVER_BOUNDARY_SURPLUS_TOKEN_MISMATCH", path,
                f"{record_id}/{arm} surplus completed-call total is wrong",
            )
            valid = False
        if is_int(endpoint) and not validate_cutover_endpoint_boundary(
                run, path, record_id, arm, endpoint, row, diagnostics):
            valid = False
        prepared_prompts = row.get("prepared_legacy_prompt_iterations")
        if type(prepared_prompts) is not list:
            diagnostics.invalid("CUTOVER_PREPARED_ITERATIONS_INVALID", path,
                                f"prepared prompt iterations in {key!r} must be an array")
            valid = False
            prepared_prompts = []
        for iteration in prepared_prompts:
            if not is_int(iteration) or iteration < 1:
                diagnostics.invalid("CUTOVER_PREPARED_ITERATION_INVALID", path,
                                    f"bad prepared prompt iteration in {key!r}")
                valid = False
                continue
            prepared_prompt_paths.add(
                (run / f"prompts/{record_id}__{arm}__iter_{iteration}.json").resolve()
            )
        prepared_receipts = row.get("prepared_legacy_receipt_iterations")
        if type(prepared_receipts) is not list:
            diagnostics.invalid("CUTOVER_PREPARED_ITERATIONS_INVALID", path,
                                f"prepared receipt iterations in {key!r} must be an array")
            valid = False
            prepared_receipts = []
        for iteration in prepared_receipts:
            if arm != "bugbank" or not is_int(iteration) or iteration < 1:
                diagnostics.invalid("CUTOVER_PREPARED_ITERATION_INVALID", path,
                                    f"bad prepared receipt iteration in {key!r}")
                valid = False
                continue
            prepared_receipt_paths.add(
                (run / f"retrievals/{record_id}__iter_{iteration}.json").resolve()
            )

    if set(boundary_map) != {(record_id, arm) for record_id in EXPECTED_IDS
                             for arm in ARMS}:
        diagnostics.invalid("CUTOVER_BOUNDARY_COVERAGE_INVALID", path,
                            "arm boundaries do not cover the frozen universe")
        valid = False
    if len(endpoints) != 14:
        diagnostics.invalid(
            "CUTOVER_HISTORICAL_ENDPOINT_COUNT_MISMATCH", path,
            "the sealed cutover must contain the 14 pre-amendment strict-FULL arms",
        )
        valid = False

    sealed = value.get("sealed_artifacts")
    if type(sealed) is not list:
        diagnostics.invalid("CUTOVER_SEALED_ARTIFACTS_INVALID", path,
                            "sealed_artifacts must be an array")
        sealed = []
        valid = False
    if (value.get("sealed_artifact_count") != len(sealed)
            or value.get("sealed_artifacts_payload_sha256")
            != sha_bytes(canonical_bytes(sealed))):
        diagnostics.invalid("CUTOVER_SEALED_PAYLOAD_MISMATCH", path,
                            "sealed artifact count or payload hash is wrong")
        valid = False
    run_relative_rows: list[str] = []
    exact_sealed_paths: set[Path] = set()
    exact_surplus_paths: set[Path] = set()
    for row in sealed:
        if type(row) is not dict:
            diagnostics.invalid("CUTOVER_SEALED_ROW_INVALID", path,
                                "sealed artifact row must be an object")
            valid = False
            continue
        run_relative = row.get("run_relative_path")
        if (type(run_relative) is not str or not run_relative
                or Path(run_relative).is_absolute()
                or ".." in Path(run_relative).parts):
            diagnostics.invalid("CUTOVER_SEALED_PATH_INVALID", path,
                                f"unsafe run-relative path {run_relative!r}")
            valid = False
            continue
        run_relative_rows.append(run_relative)
        expected_path = (run / run_relative).resolve()
        try:
            expected_path.relative_to(run.resolve())
        except ValueError:
            diagnostics.invalid("CUTOVER_SEALED_PATH_ESCAPE", path,
                                f"sealed path escapes run: {run_relative!r}")
            valid = False
            continue
        row_valid = True
        if not same_recorded_path(row.get("path"), expected_path, run):
            diagnostics.invalid("CUTOVER_SEALED_BINDING_PATH_MISMATCH", path,
                                f"binding path is wrong for {run_relative!r}")
            row_valid = False
        if not expected_path.is_file():
            diagnostics.invalid("CUTOVER_SEALED_ARTIFACT_MISSING", expected_path,
                                "sealed historical artifact is absent")
            row_valid = False
        elif (row.get("sha256") != sha_file(expected_path)
              or row.get("size_bytes") != expected_path.stat().st_size):
            diagnostics.invalid("CUTOVER_SEALED_ARTIFACT_CHANGED", expected_path,
                                "sealed historical artifact bytes changed")
            row_valid = False
        cell = cutover_cell_from_path(run_relative)
        expected_cell = (
            {"record_id": cell[0], "arm": cell[1], "iteration": cell[2]}
            if cell is not None else None
        )
        if row.get("cell") != expected_cell:
            diagnostics.invalid("CUTOVER_SEALED_CELL_MISMATCH", path,
                                f"cell is wrong for {run_relative!r}")
            row_valid = False
        expected_surplus = bool(
            cell is not None and cell[:2] in endpoints
            and cell[2] > endpoints[cell[:2]]
        )
        if row.get("post_first_strict_full_surplus") is not expected_surplus:
            diagnostics.invalid("CUTOVER_SURPLUS_CLASSIFICATION_MISMATCH", path,
                                f"surplus flag is wrong for {run_relative!r}")
            row_valid = False
        if row_valid:
            exact_sealed_paths.add(expected_path)
            if expected_surplus:
                exact_surplus_paths.add(expected_path)
        else:
            valid = False
    if run_relative_rows != sorted(run_relative_rows) or len(run_relative_rows) != len(set(run_relative_rows)):
        diagnostics.invalid("CUTOVER_SEALED_ORDER_INVALID", path,
                            "sealed artifacts must be uniquely sorted by run-relative path")
        valid = False

    legacy_receipts = [row for row in sealed if type(row) is dict and
                       str(row.get("run_relative_path", "")).startswith("retrievals/")]
    legacy_prompts = [row for row in sealed if type(row) is dict and
                      str(row.get("run_relative_path", "")).startswith("prompts/")]
    surplus = [row for row in sealed if type(row) is dict and
               row.get("post_first_strict_full_surplus") is True]
    for count_key, payload_key, label, rows in (
        ("sealed_legacy_receipt_count", "sealed_legacy_receipts_payload_sha256",
         "legacy receipts", legacy_receipts),
        ("sealed_legacy_prompt_count", "sealed_legacy_prompts_payload_sha256",
         "legacy prompts", legacy_prompts),
        ("sealed_post_first_full_surplus_count",
         "sealed_post_first_full_surplus_payload_sha256",
         "post-first-FULL surplus", surplus),
    ):
        if (value.get(count_key) != len(rows)
                or value.get(payload_key) != sha_bytes(canonical_bytes(rows))):
            diagnostics.invalid("CUTOVER_SUBSET_PAYLOAD_MISMATCH", path,
                                f"sealed {label} count or payload hash is wrong")
            valid = False

    actual_legacy_paths = {
        item.resolve()
        for directory in (run / "retrievals", run / "prompts")
        if directory.is_dir()
        for item in directory.rglob("*") if item.is_file()
    }
    sealed_legacy_paths = {
        (run / row["run_relative_path"]).resolve()
        for row in [*legacy_receipts, *legacy_prompts]
        if type(row.get("run_relative_path")) is str
    }
    if actual_legacy_paths != sealed_legacy_paths:
        diagnostics.invalid("CUTOVER_LEGACY_FILE_SET_CHANGED", path,
                            "the closed legacy receipt/prompt file set changed")
        valid = False

    files = value.get("files")
    if type(files) is not dict:
        diagnostics.invalid("CUTOVER_FILE_BINDINGS_INVALID", path,
                            "files must be an object")
        valid = False
        files = {}
    for name, row in files.items():
        if type(row) is not dict or type(row.get("path")) is not str:
            diagnostics.invalid("CUTOVER_FILE_BINDING_INVALID", path,
                                f"files.{name} is malformed")
            valid = False
            continue
        bound_path = resolve_recorded_path(row["path"], run)
        if (not bound_path.is_file() or row.get("sha256") != sha_file(bound_path)
                or row.get("size_bytes") != bound_path.stat().st_size):
            diagnostics.invalid("CUTOVER_FILE_BINDING_CHANGED", bound_path,
                                f"cutover-bound file {name!r} changed")
            valid = False

    surplus_token_values = [
        row.get("post_endpoint_surplus_completed_model_tokens")
        for row in boundaries if type(row) is dict
    ]
    surplus_call_values = [
        row.get("post_endpoint_surplus_completed_model_calls")
        for row in boundaries if type(row) is dict
    ]
    numeric_surplus = (
        all(is_int(item) and item >= 0 for item in surplus_token_values)
        and all(is_int(item) and item >= 0 for item in surplus_call_values)
    )
    surplus_tokens = sum(surplus_token_values) if numeric_surplus else -1
    surplus_calls = sum(surplus_call_values) if numeric_surplus else -1
    if (surplus_tokens != EXPECTED_SURPLUS_COMPLETED_MODEL_TOKENS
            or value.get("post_endpoint_surplus_completed_model_tokens")
            != surplus_tokens
            or value.get("post_endpoint_surplus_completed_model_calls")
            != surplus_calls):
        diagnostics.invalid("CUTOVER_SURPLUS_TOKEN_MISMATCH", path,
                            "historical surplus completed-call tokens changed")
        valid = False

    if not valid:
        # Never grant a post-terminal exemption from a malformed manifest.
        exact_surplus_paths = set()
    return {
        "surplus_paths": exact_surplus_paths,
        "prepared_prompt_paths": prepared_prompt_paths,
        "prepared_receipt_paths": prepared_receipt_paths,
        "endpoints": endpoints,
        "sealed_paths": exact_sealed_paths,
    }


def reject_unsealed_post_terminal_artifacts(
        run: Path, endpoints: Mapping[tuple[str, str], int],
        surplus_paths: set[Path], diagnostics: Diagnostics) -> None:
    roots = (
        "iterations", "audits/iterations", "audits/metadata/iterations",
        "checkers/audits/iterations", "prompts", "prompts_whole_proof_v2",
        "retrievals", "retrievals_whole_proof_v2", "states",
    )
    for root_text in roots:
        root = run / root_text
        if not root.is_dir():
            continue
        for item in sorted(path for path in root.rglob("*") if path.is_file()):
            run_relative = item.relative_to(run).as_posix()
            cell = cutover_cell_from_path(run_relative)
            if cell is None or cell[:2] not in endpoints:
                continue
            if cell[2] <= endpoints[cell[:2]]:
                continue
            if item.resolve() not in surplus_paths:
                diagnostics.invalid(
                    "POST_TERMINAL_ARTIFACT", item,
                    f"{cell[1]} reached its first valid terminal endpoint at "
                    f"iteration {endpoints[cell[:2]]}; this later artifact is "
                    "not exact sealed pre-amendment surplus",
                )


def all_terminal_endpoints(
        sealed_endpoints: Mapping[tuple[str, str], int],
        terminal_states: Mapping[tuple[str, str], dict[str, Any] | None],
) -> dict[tuple[str, str], int]:
    """Combine historical sealed endpoints with newly derived endpoints.

    Historical post-endpoint files may be accepted only through the exact
    cutover allowlist.  Newly derived endpoints have no such exception, but
    they must still participate in the global post-terminal artifact scan.
    Keep the earliest endpoint defensively if both sources name a cell.
    """
    endpoints = dict(sealed_endpoints)
    for key, state in terminal_states.items():
        if state is None or state.get("terminal") is not True:
            continue
        iteration = state.get("iteration")
        if not is_int(iteration) or iteration < 1:
            continue
        endpoints[key] = min(iteration, endpoints.get(key, iteration))
    return endpoints


def validate_run(run: Path) -> dict[str, Any]:
    diagnostics = Diagnostics(run)
    universe = validate_universe(diagnostics)
    if not run.is_dir():
        diagnostics.invalid("RUN_DIRECTORY_MISSING", run, "run directory is absent")
    schemas = load_schemas(run, diagnostics)

    check_simple_directory(run / "baselines", diagnostics, EXPECTED_SET)
    check_simple_directory(run / "audits/baseline", diagnostics, EXPECTED_SET)
    check_simple_directory(run / "audits/metadata/baseline", diagnostics, EXPECTED_SET)
    check_simple_directory(run / "pair_terminals", diagnostics, EXPECTED_SET)
    revision_paths = discover_iterations(run / "iterations", diagnostics, layout="tree")
    audit_paths = discover_iterations(run / "audits/iterations", diagnostics, layout="tree")
    audit_metadata_paths = discover_iterations(
        run / "audits/metadata/iterations", diagnostics, layout="tree"
    )
    legacy_prompt_paths = discover_iterations(
        run / "prompts", diagnostics, layout="flat"
    )
    active_prompt_paths = discover_iterations(
        run / "prompts_whole_proof_v2", diagnostics, layout="flat"
    )
    legacy_receipt_paths = discover_receipts(run / "retrievals", diagnostics)
    active_receipt_paths = discover_receipts(
        run / "retrievals_whole_proof_v2", diagnostics
    )

    # New work always uses the whole-proof directories. A legacy prompt or
    # receipt remains operative only when its child revision was completed
    # before the cutover. Prepared-only legacy files are immutable provenance,
    # not permission to make another call under the withdrawn claim cap.
    prompt_paths: dict[tuple[str, str, int], Path] = {}
    inert_legacy_prompt_paths: dict[tuple[str, str, int], Path] = {}
    for key in set(legacy_prompt_paths) | set(active_prompt_paths):
        if key in active_prompt_paths:
            prompt_paths[key] = active_prompt_paths[key]
            if key in legacy_prompt_paths:
                inert_legacy_prompt_paths[key] = legacy_prompt_paths[key]
        elif key in revision_paths:
            prompt_paths[key] = legacy_prompt_paths[key]
        else:
            inert_legacy_prompt_paths[key] = legacy_prompt_paths[key]

    receipt_paths: dict[tuple[str, int], Path] = {}
    inert_legacy_receipt_paths: dict[tuple[str, int], Path] = {}
    for key in set(legacy_receipt_paths) | set(active_receipt_paths):
        revision_key = (key[0], "bugbank", key[1])
        if key in active_receipt_paths:
            receipt_paths[key] = active_receipt_paths[key]
            if key in legacy_receipt_paths:
                inert_legacy_receipt_paths[key] = legacy_receipt_paths[key]
        elif revision_key in revision_paths:
            receipt_paths[key] = legacy_receipt_paths[key]
        else:
            inert_legacy_receipt_paths[key] = legacy_receipt_paths[key]

    cutover = validate_cutover_manifest(run, diagnostics)
    actual_inert_prompts = {path.resolve() for path in inert_legacy_prompt_paths.values()}
    actual_inert_receipts = {path.resolve() for path in inert_legacy_receipt_paths.values()}
    if actual_inert_prompts != cutover["prepared_prompt_paths"]:
        diagnostics.invalid(
            "CUTOVER_INERT_PROMPT_SET_MISMATCH", run / CUTOVER_FILENAME,
            "operative/prepared classification of legacy prompts differs from the seal",
        )
    if actual_inert_receipts != cutover["prepared_receipt_paths"]:
        diagnostics.invalid(
            "CUTOVER_INERT_RECEIPT_SET_MISMATCH", run / CUTOVER_FILENAME,
            "operative/prepared classification of legacy receipts differs from the seal",
        )
    legacy_dir = run / "audits/baseline_claim_only_v1"
    legacy_audits = list(legacy_dir.glob("*.json")) if legacy_dir.is_dir() else []
    for path in legacy_audits:
        if path.stem not in EXPECTED_SET:
            diagnostics.warn("LEGACY_AUDIT_OUTSIDE_UNIVERSE", path,
                             "legacy claim-only audit has an unknown record ID")
    baseline_metadata_files = (
        list((run / "audits/metadata/baseline").glob("*.json"))
        if (run / "audits/metadata/baseline").is_dir() else []
    )

    stage_counts: dict[str, Any] = {
        "inputs": {"expected": 31, "valid": universe["inputs_valid"]},
        "baselines": {"expected": 31, "present": 0, "valid": 0},
        "baseline_audits": {"expected": 31, "present": 0, "valid": 0,
                            "legacy_claim_only": len(legacy_audits)},
        "retrieval_receipts": {
            "present": sum(
                path.resolve() not in cutover["surplus_paths"]
                for path in receipt_paths.values()
            ),
            "valid": 0,
            "sealed_inert_legacy": len(inert_legacy_receipt_paths),
            "sealed_historical_surplus": sum(
                path.resolve() in cutover["surplus_paths"]
                for path in receipt_paths.values()
            ),
        },
        "prompts": {
            arm: {
                "present": 0, "valid": 0,
                "sealed_inert_legacy": sum(
                    key[1] == arm for key in inert_legacy_prompt_paths
                ),
            } for arm in ARMS
        },
        "revisions": {arm: {"present": 0, "valid": 0, "targets": 0}
                      for arm in ARMS},
        "revision_audits": {arm: {"present": 0, "valid": 0}
                            for arm in ARMS},
        "audit_metadata": {
            "baseline": {"present": len(baseline_metadata_files), "valid": 0},
            "plain": {"present": sum(arm == "plain" for _, arm, _ in audit_metadata_paths),
                      "valid": 0},
            "bugbank": {"present": sum(arm == "bugbank" for _, arm, _ in audit_metadata_paths),
                        "valid": 0},
        },
        "pair_terminals": {"expected": 31, "present": 0, "valid": 0},
    }
    per_record: dict[str, Any] = {}
    baseline_artifacts: dict[str, Artifact] = {}
    baseline_valid: dict[str, bool] = {}
    baseline_audits: dict[str, Artifact] = {}
    baseline_audit_valid: dict[str, bool] = {}
    revisions: dict[tuple[str, str, int], Artifact] = {}
    revision_valid: dict[tuple[str, str, int], bool] = {}
    revision_audits: dict[tuple[str, str, int], Artifact] = {}
    revision_audit_valid: dict[tuple[str, str, int], bool] = {}
    terminal_states: dict[tuple[str, str], dict[str, Any] | None] = {}
    latest_outcomes: dict[str, list[dict[str, Any]]] = {
        "baseline": [], "plain": [], "bugbank": []
    }

    database = BugBankView(diagnostics)
    try:
        for record_id in EXPECTED_IDS:
            record_report: dict[str, Any] = {"arms": {}}
            per_record[record_id] = record_report
            source = load_json_artifact(INPUTS / f"{record_id}.json", diagnostics)
            baseline_path = run / f"baselines/{record_id}.json"
            baseline = load_json_artifact(
                baseline_path, diagnostics, missing_code="BASELINE_MISSING"
            )
            if baseline is not None:
                stage_counts["baselines"]["present"] += 1
                baseline_artifacts[record_id] = baseline
                ok = validate_baseline(
                    baseline, record_id,
                    schemas.get("baseline_whole_proof_v2"), diagnostics,
                )
                baseline_valid[record_id] = ok
                stage_counts["baselines"]["valid"] += int(ok)
            else:
                baseline_valid[record_id] = False

            baseline_audit_path = run / f"audits/baseline/{record_id}.json"
            baseline_audit = load_json_artifact(
                baseline_audit_path, diagnostics, missing_code="BASELINE_AUDIT_MISSING"
            )
            if baseline_audit is not None:
                stage_counts["baseline_audits"]["present"] += 1
                baseline_audits[record_id] = baseline_audit
                if baseline is None:
                    diagnostics.invalid("ORPHAN_BASELINE_AUDIT", baseline_audit.path,
                                        "baseline audit exists without its parent baseline")
                    audit_ok = False
                else:
                    audit_content_ok = validate_audit(
                        baseline_audit, record_id, baseline, "BASELINE_AUDIT",
                        "neutral", 0, schemas.get("audit"), diagnostics,
                    )
                    baseline_metadata_path = (
                        run / f"audits/metadata/baseline/{record_id}.json"
                    )
                    baseline_metadata = load_json_artifact(
                        baseline_metadata_path, diagnostics,
                        missing_code="BASELINE_AUDIT_METADATA_MISSING",
                    )
                    if baseline_metadata is not None and source is not None:
                        metadata_ok = validate_audit_metadata(
                            baseline_metadata, record_id, "neutral", 0, source,
                            baseline, baseline_audit, diagnostics, run,
                        )
                        stage_counts["audit_metadata"]["baseline"]["valid"] += int(metadata_ok)
                    else:
                        metadata_ok = False
                    audit_ok = audit_content_ok and metadata_ok
                baseline_audit_valid[record_id] = audit_ok
                stage_counts["baseline_audits"]["valid"] += int(audit_ok)
            else:
                baseline_audit_valid[record_id] = False
                if (run / f"audits/metadata/baseline/{record_id}.json").exists():
                    diagnostics.missing(
                        "AUDIT_METADATA_AWAITS_OUTPUT",
                        run / f"audits/metadata/baseline/{record_id}.json",
                        "audit metadata exists while its canonical audit output is absent",
                    )

            record_report["baseline"] = {
                "present": baseline is not None,
                "valid": baseline_valid[record_id],
                "sha256": baseline.sha256 if baseline else None,
                "audit_present": baseline_audit is not None,
                "audit_valid": baseline_audit_valid[record_id],
                **classification(baseline, baseline_audit,
                                 baseline_audit_valid[record_id]),
            }
            latest_outcomes["baseline"].append(record_report["baseline"])

            for arm in ARMS:
                keys = {
                    iteration for rid, artifact_arm, iteration in set(revision_paths) |
                    set(audit_paths) | set(audit_metadata_paths) | set(prompt_paths)
                    if rid == record_id and artifact_arm == arm
                }
                if arm == "bugbank":
                    keys |= {iteration for rid, iteration in receipt_paths if rid == record_id}
                maximum_seen = max(keys, default=1)
                revision_iterations_present = sorted(
                    iteration for rid, artifact_arm, iteration in revision_paths
                    if rid == record_id and artifact_arm == arm
                )
                if revision_iterations_present:
                    expected_sequence = list(range(1, max(revision_iterations_present) + 1))
                    if revision_iterations_present != expected_sequence:
                        diagnostics.invalid(
                            "REVISION_ITERATION_GAP", run / f"iterations/{record_id}/{arm}",
                            f"present iterations {revision_iterations_present!r} are not contiguous",
                        )

                latest_revision: Artifact | None = None
                latest_audit: Artifact | None = None
                latest_parent: Artifact | None = None
                latest_prompt: Artifact | None = None
                latest_receipt: Artifact | None = None
                latest_audit_ok = False
                valid_revision_target = False
                first_terminal_state: dict[str, Any] | None = None
                first_terminal_iteration: int | None = None
                chain_through_previous = (
                    baseline_valid[record_id]
                    and baseline_audit_valid[record_id]
                )

                for iteration in range(1, maximum_seen + 1):
                    key = (record_id, arm, iteration)
                    if (first_terminal_iteration is not None
                            and iteration > first_terminal_iteration):
                        # Exact historical surplus is hash-sealed by the
                        # cutover and excluded from the endpoint. It is not a
                        # live descendant and therefore cannot demand another
                        # audit (notably A10 BugBank iteration 2). Any new or
                        # changed later artifact was rejected globally above.
                        continue
                    parent = baseline if iteration == 1 else revisions.get(
                        (record_id, arm, iteration - 1)
                    )
                    parent_audit = baseline_audit if iteration == 1 else revision_audits.get(
                        (record_id, arm, iteration - 1)
                    )

                    receipt: Artifact | None = None
                    receipt_ok = False
                    revision_ok = False
                    prompt_ok = False
                    retrieved_ids: list[str] = []
                    if arm == "bugbank" and (record_id, iteration) in receipt_paths:
                        receipt = load_json_artifact(
                            receipt_paths[(record_id, iteration)], diagnostics
                        )
                        if receipt is not None:
                            if parent is None:
                                diagnostics.invalid("ORPHAN_RECEIPT", receipt.path,
                                                    "receipt has no immediate parent draft")
                            else:
                                receipt_ok, retrieved_ids = validate_receipt(
                                    receipt, record_id, iteration, parent, database,
                                    diagnostics, run,
                                )
                                stage_counts["retrieval_receipts"]["valid"] += int(receipt_ok)

                    revision = None
                    if key in revision_paths:
                        revision = load_json_artifact(revision_paths[key], diagnostics)
                        if revision is not None:
                            revisions[key] = revision
                            stage_counts["revisions"][arm]["present"] += 1
                            if parent is None or parent_audit is None:
                                diagnostics.invalid(
                                    "REVISION_LINEAGE_MISSING", revision.path,
                                    "revision lacks its immediate parent draft or audit",
                                )
                                revision_ok = False
                            else:
                                revision_schema = (
                                    schemas.get("revision_whole_proof_v2")
                                    if (key in prompt_paths and
                                        prompt_paths[key].parent ==
                                        run / "prompts_whole_proof_v2")
                                    else schemas.get("revision")
                                )
                                revision_ok = validate_revision(
                                    revision, record_id, arm, iteration, parent,
                                    parent_audit, receipt if receipt_ok else None,
                                    retrieved_ids, revision_schema, diagnostics, run,
                                )
                            revision_valid[key] = revision_ok
                            stage_counts["revisions"][arm]["valid"] += int(revision_ok)
                            valid_revision_target |= revision_ok

                    prompt = None
                    if key in prompt_paths:
                        prompt = load_json_artifact(prompt_paths[key], diagnostics)
                        if prompt is not None:
                            stage_counts["prompts"][arm]["present"] += 1
                            if source is None or parent is None or parent_audit is None:
                                diagnostics.invalid(
                                    "PROMPT_LINEAGE_MISSING", prompt.path,
                                    "prompt lacks source, immediate parent, or parent audit",
                                )
                                prompt_ok = False
                            else:
                                prompt_ok = validate_prompt_metadata(
                                    prompt, record_id, arm, iteration, source, parent,
                                    parent_audit, receipt if receipt_ok else None,
                                    revision, diagnostics, run,
                                )
                            stage_counts["prompts"][arm]["valid"] += int(prompt_ok)

                    audit = None
                    audit_ok = False
                    if key in audit_paths:
                        audit = load_json_artifact(audit_paths[key], diagnostics)
                        if audit is not None:
                            revision_audits[key] = audit
                            stage_counts["revision_audits"][arm]["present"] += 1
                            if revision is None:
                                diagnostics.invalid("ORPHAN_REVISION_AUDIT", audit.path,
                                                    "revision audit has no parent revision")
                            else:
                                audit_content_ok = validate_audit(
                                    audit, record_id, revision, "REVISION_AUDIT", arm,
                                    iteration, schemas.get("audit"), diagnostics,
                                )
                                metadata_path = run / (
                                    f"audits/metadata/iterations/{record_id}/{arm}/"
                                    f"iter_{iteration}.json"
                                )
                                audit_metadata = load_json_artifact(
                                    metadata_path, diagnostics,
                                    missing_code="REVISION_AUDIT_METADATA_MISSING",
                                )
                                if audit_metadata is not None and source is not None:
                                    metadata_ok = validate_audit_metadata(
                                        audit_metadata, record_id, arm, iteration, source,
                                        revision, audit, diagnostics, run,
                                    )
                                    stage_counts["audit_metadata"][arm]["valid"] += int(metadata_ok)
                                else:
                                    metadata_ok = False
                                audit_ok = audit_content_ok and metadata_ok
                            revision_audit_valid[key] = audit_ok
                            stage_counts["revision_audits"][arm]["valid"] += int(audit_ok)
                    elif key in audit_metadata_paths:
                        diagnostics.missing(
                            "AUDIT_METADATA_AWAITS_OUTPUT", audit_metadata_paths[key],
                            "audit metadata exists while its canonical audit output is absent",
                        )

                    parent_chain_ok = chain_through_previous
                    complete_chain_ok = (
                        parent_chain_ok and revision_ok and prompt_ok and audit_ok
                        and (arm == "plain" or receipt_ok)
                    )
                    if complete_chain_ok and first_terminal_state is None:
                        candidate_terminal = derive_terminal_state(
                            revision, audit, parent, prompt,
                            receipt if arm == "bugbank" else None,
                            audit_ok, run, record_id,
                            (
                                terminal_states[(record_id, "bugbank")][
                                    "model_tokens_used"
                                ]
                                if arm == "plain"
                                and terminal_states.get(
                                    (record_id, "bugbank")
                                ) is not None
                                else None
                            ),
                        )
                        if candidate_terminal is not None:
                            first_terminal_state = candidate_terminal
                            first_terminal_iteration = iteration

                    # A locally valid iteration cannot repair an invalid or
                    # missing ancestor. Carry validity transitively so a
                    # terminal can only derive from the complete baseline-to-
                    # terminal lineage.
                    chain_through_previous = complete_chain_ok

                    if revision is not None:
                        if prompt is None:
                            diagnostics.missing("REVISION_PROMPT_METADATA_MISSING",
                                                run / f"prompts_whole_proof_v2/{record_id}__{arm}__iter_{iteration}.json",
                                                "revision lacks authoritative prompt metadata")
                        if arm == "bugbank" and receipt is None:
                            diagnostics.missing("BUGBANK_RECEIPT_MISSING",
                                                run / f"retrievals_whole_proof_v2/{record_id}__iter_{iteration}.json",
                                                "BugBank revision lacks its treatment receipt")
                        if audit is None:
                            diagnostics.missing("REVISION_AUDIT_MISSING",
                                                run / f"audits/iterations/{record_id}/{arm}/iter_{iteration}.json",
                                                "revision has not received its independent audit")
                        latest_revision = revision
                        latest_audit = audit
                        latest_parent = parent
                        latest_prompt = prompt
                        latest_receipt = receipt if arm == "bugbank" else None
                        latest_audit_ok = audit_ok

                if not revision_iterations_present:
                    diagnostics.missing(
                        "INITIAL_REVISION_MISSING",
                        run / f"iterations/{record_id}/{arm}/iter_1.json",
                        "both paired arms require an iteration-1 revision",
                    )
                stage_counts["revisions"][arm]["targets"] += int(valid_revision_target)
                terminal_state = first_terminal_state
                terminal_states[(record_id, arm)] = terminal_state
                if (latest_revision is not None and latest_audit is not None
                        and latest_audit_ok and terminal_state is None):
                    if stable_plain_waits_for_bugbank(
                            latest_revision, latest_audit, latest_parent,
                            latest_prompt, latest_audit_ok, run,
                            terminal_states.get((record_id, "bugbank"))):
                        diagnostics.missing(
                            "WAITING_FOR_BUGBANK_TOKEN_TARGET", latest_revision.path,
                            "stable inconclusive plain proof is waiting for the "
                            "BugBank endpoint token total; do not launch another "
                            "plain call yet",
                        )
                    elif latest_revision.value.get("iteration", 0) < MAX_ITERATION:
                        next_iteration = latest_revision.value["iteration"] + 1
                        diagnostics.missing(
                            "NEXT_REVISION_REQUIRED",
                            run / f"iterations/{record_id}/{arm}/iter_{next_iteration}.json",
                            "latest audit has not reached a verified full solution or a "
                            "valid inconclusive endpoint; another complete cycle is required",
                        )
                    else:
                        diagnostics.missing(
                            "OPERATIONAL_ITERATION_LIMIT_REACHED",
                            run / f"iterations/{record_id}/{arm}/iter_{MAX_ITERATION}.json",
                            "arm remains unfinished; raise the operational ceiling and resume",
                        )
                latest_class = classification(
                    latest_revision, latest_audit, latest_audit_ok
                )
                record_report["arms"][arm] = {
                    "iterations_present": revision_iterations_present,
                    "latest_iteration": (
                        latest_revision.value.get("iteration") if latest_revision else None
                    ),
                    "latest_revision_sha256": (
                        latest_revision.sha256 if latest_revision else None
                    ),
                    "latest_audit_sha256": latest_audit.sha256 if latest_audit else None,
                    "latest_audit_valid": latest_audit_ok,
                    "terminal": terminal_state,
                    **latest_class,
                }
                latest_outcomes[arm].append(record_report["arms"][arm])

            pair_terminal_path = run / f"pair_terminals/{record_id}.json"
            pair_terminal = load_json_artifact(
                pair_terminal_path, diagnostics, missing_code="PAIR_TERMINAL_MISSING"
            )
            if pair_terminal is not None:
                stage_counts["pair_terminals"]["present"] += 1
                terminal_ok = validate_pair_terminal(
                    pair_terminal, record_id,
                    {arm: terminal_states[(record_id, arm)] for arm in ARMS},
                    baseline, baseline_audit, diagnostics, run,
                )
                stage_counts["pair_terminals"]["valid"] += int(terminal_ok)
            else:
                terminal_ok = False
            record_report["pair_terminal_present"] = pair_terminal is not None
            record_report["pair_terminal_valid"] = terminal_ok
    finally:
        database.close()

    # The cutover can enumerate only endpoints that existed when it was
    # sealed.  Scan again using every endpoint derived from the current valid
    # lineage so a new post-cutover solution/fixed point cannot acquire a
    # silently ignored descendant.  Only exact pre-amendment surplus paths
    # from the valid cutover manifest remain exempt.
    reject_unsealed_post_terminal_artifacts(
        run,
        all_terminal_endpoints(cutover["endpoints"], terminal_states),
        cutover["surplus_paths"],
        diagnostics,
    )

    outcome_counts: dict[str, Any] = {}
    for cohort, rows in latest_outcomes.items():
        outcome_counts[cohort] = {
            "records": len(rows),
            "candidates": sum(bool(row.get("candidate")) for row in rows),
            "claimed_full": sum(row.get("claimed_resolution") == "FULL" for row in rows),
            "claimed_partial": sum(row.get("claimed_resolution") == "PARTIAL" for row in rows),
            "claimed_none": sum(row.get("claimed_resolution") == "NONE" for row in rows),
            "verified": sum(bool(row.get("verified")) for row in rows),
            "verified_full": sum(bool(row.get("verified_full")) for row in rows),
            "verified_partial": sum(bool(row.get("verified_partial")) for row in rows),
            "target_overclaimed": sum(row.get("target_verdict") == "OVERCLAIMED"
                                      for row in rows),
            "target_no_valid_progress": sum(
                row.get("target_verdict") == "NO_VALID_PROGRESS" for row in rows
            ),
        }

    audit_verdict_counts: dict[str, Any] = {}
    audit_groups: dict[str, list[Artifact]] = {
        "baseline": list(baseline_audits.values()),
        "plain": [artifact for (record_id, arm, iteration), artifact
                  in revision_audits.items() if arm == "plain"],
        "bugbank": [artifact for (record_id, arm, iteration), artifact
                    in revision_audits.items() if arm == "bugbank"],
    }
    for cohort, artifacts in audit_groups.items():
        verdicts: Counter[str] = Counter()
        target_verdicts: Counter[str] = Counter()
        confirmed = 0
        for artifact in artifacts:
            for claim in artifact.value.get("claims", []):
                if type(claim) is dict and type(claim.get("verdict")) is str:
                    verdicts[claim["verdict"]] += 1
            if type(artifact.value.get("target_verdict")) is str:
                target_verdicts[artifact.value["target_verdict"]] += 1
            refs = artifact.value.get("confirmed_refutations")
            if type(refs) is list:
                confirmed += len(refs)
        audit_verdict_counts[cohort] = {
            "audit_artifacts": len(artifacts),
            "claim_verdicts": dict(sorted(verdicts.items())),
            "confirmed_refutations": confirmed,
            "target_verdicts": dict(sorted(target_verdicts.items())),
        }

    telemetry = collect_telemetry(run, diagnostics)
    status = "INVALID" if diagnostics.errors else (
        "INCOMPLETE" if diagnostics.incomplete else "VALID_COMPLETE"
    )
    report = {
        "schema": "open_frontier_paired_v2_validation_report_v1",
        "run_id": RUN_ID,
        "run_path": str(run.resolve()),
        "validator": {
            "path": str(SCRIPT),
            "sha256": sha_file(SCRIPT),
        },
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "exit_code_contract": {
            "0": "VALID_COMPLETE (or INCOMPLETE with --allow-incomplete)",
            "1": "INCOMPLETE",
            "2": "INVALID",
        },
        "universe": universe,
        "stage_counts": stage_counts,
        "outcomes": outcome_counts,
        "audit_results": audit_verdict_counts,
        "terminal_counts": {
            "arm_terminal": {
                arm: sum(terminal_states[(record_id, arm)] is not None
                         for record_id in EXPECTED_IDS)
                for arm in ARMS
            },
            "audited_fixed_point": {
                arm: sum(
                    terminal_states[(record_id, arm)] is not None
                    and terminal_states[(record_id, arm)]["terminal_reason"] ==
                    "AUDITED_FIXED_POINT"
                    for record_id in EXPECTED_IDS
                ) for arm in ARMS
            },
            "verified_full_independent_audit": {
                arm: sum(
                    terminal_states[(record_id, arm)] is not None
                    and terminal_states[(record_id, arm)]["terminal_reason"] ==
                    "VERIFIED_FULL_INDEPENDENT_AUDIT"
                    for record_id in EXPECTED_IDS
                ) for arm in ARMS
            },
            "iteration_cap": {
                arm: sum(
                    terminal_states[(record_id, arm)] is not None
                    and terminal_states[(record_id, arm)]["terminal_reason"] ==
                    "ITERATION_CAP"
                    for record_id in EXPECTED_IDS
                ) for arm in ARMS
            },
        },
        "telemetry": telemetry,
        "per_record": per_record,
        "diagnostics": {
            "invalid_count": len(diagnostics.errors),
            "incomplete_count": len(diagnostics.incomplete),
            "warning_count": len(diagnostics.warnings),
            "invalid": diagnostics.errors,
            "incomplete": diagnostics.incomplete,
            "warnings": diagnostics.warnings,
        },
    }
    # Recompute status because telemetry parsing can itself expose malformed
    # state JSON after the first status calculation.
    report["status"] = "INVALID" if diagnostics.errors else (
        "INCOMPLETE" if diagnostics.incomplete else "VALID_COMPLETE"
    )
    report["validator"]["sha256"] = sha_file(SCRIPT)
    return report


def seal_report(report: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(report)
    result.pop("report_payload_sha256", None)
    result["report_payload_sha256"] = sha_bytes(canonical_bytes(result))
    return result


def atomic_write_report(path: Path, report: Mapping[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(
        report, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2
    ).encode("utf-8") + b"\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fchmod(handle.fileno(), 0o644)
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()


def print_text_report(report: Mapping[str, Any], maximum_diagnostics: int) -> None:
    stages = report["stage_counts"]
    outcomes = report["outcomes"]
    telemetry = report["telemetry"]
    print(f"status: {report['status']}")
    print(
        "universe: "
        f"{report['universe']['inputs_valid']}/{report['universe']['expected']} valid inputs"
    )
    print(
        "stages: "
        f"baselines {stages['baselines']['valid']}/{stages['baselines']['expected']}; "
        f"baseline audits {stages['baseline_audits']['valid']}/"
        f"{stages['baseline_audits']['expected']}; "
        f"receipts {stages['retrieval_receipts']['valid']}/"
        f"{stages['retrieval_receipts']['present']}; "
        f"plain revisions {stages['revisions']['plain']['valid']}/"
        f"{stages['revisions']['plain']['present']}; "
        f"BugBank revisions {stages['revisions']['bugbank']['valid']}/"
        f"{stages['revisions']['bugbank']['present']}; "
        f"pair terminals {stages['pair_terminals']['valid']}/31"
    )
    for cohort in ("baseline", "plain", "bugbank"):
        row = outcomes[cohort]
        print(
            f"{cohort} outcomes (latest): candidates={row['candidates']}, "
            f"claimed_full={row['claimed_full']}, claimed_partial={row['claimed_partial']}, "
            f"verified_full={row['verified_full']}, "
            f"verified_partial={row['verified_partial']}"
        )
    logs = telemetry["logs"]
    cost = telemetry["explicit_cost_usd_total"]
    print(
        "telemetry: "
        f"tokens={logs['tokens_used_total']} from "
        f"{logs['with_final_token_count']}/{logs['count']} logs; "
        f"completed_duration_seconds="
        f"{telemetry['states']['completed_duration_seconds_total']:.3f}; "
        f"explicit_cost_usd={cost if cost is not None else 'not recorded'}"
    )
    state_arm_tokens = telemetry["structured_tokens_used_by_arm"]
    exposure = telemetry["prompt_exposure"]
    print(
        "paired-arm telemetry: "
        f"plain_tokens={int(state_arm_tokens.get('plain', 0))}, "
        f"bugbank_tokens={int(state_arm_tokens.get('bugbank', 0))}; "
        f"plain_prompt_bytes={exposure['prompt_utf8_bytes_by_arm']['plain']}, "
        f"bugbank_prompt_bytes={exposure['prompt_utf8_bytes_by_arm']['bugbank']}, "
        f"bugbank_receipt_exposure_bytes="
        f"{exposure['receipt_payload_bytes_exposed_by_arm']['bugbank']}"
    )
    diagnostic_block = report["diagnostics"]
    print(
        "diagnostics: "
        f"invalid={diagnostic_block['invalid_count']}, "
        f"incomplete={diagnostic_block['incomplete_count']}, "
        f"warnings={diagnostic_block['warning_count']}"
    )
    rows: list[tuple[str, Mapping[str, str]]] = []
    for level, key in (("INVALID", "invalid"), ("INCOMPLETE", "incomplete"),
                       ("WARNING", "warnings")):
        rows.extend((level, item) for item in diagnostic_block[key])
    for level, item in rows[:maximum_diagnostics]:
        print(f"{level} {item['code']} {item['path']}: {item['message']}")
    if len(rows) > maximum_diagnostics:
        print(f"... {len(rows) - maximum_diagnostics} more diagnostics (use --json or --report)")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit codes:\n"
            "  0  VALID_COMPLETE (also INCOMPLETE when --allow-incomplete is used)\n"
            "  1  INCOMPLETE: structurally unrefuted so far, but required stages remain\n"
            "  2  INVALID: at least one structural, identity, exposure, or lineage error\n\n"
            "Canonical checkpoint example:\n"
            "  validate_open_frontier_paired_v2.py --allow-incomplete \\\n+\n    --report RUN/validation_report.json"
        ).replace("\n+\n", "\n"),
    )
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN,
                        help=f"run root (default: {DEFAULT_RUN})")
    parser.add_argument("--report", type=Path,
                        help="atomically write the complete JSON report to PATH")
    parser.add_argument("--json", action="store_true",
                        help="print the complete report as JSON")
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="return 0 rather than 1 for an INCOMPLETE monitoring snapshot")
    parser.add_argument("--max-diagnostics", type=int, default=60,
                        help="maximum diagnostics in text output (default: 60)")
    arguments = parser.parse_args()
    if arguments.max_diagnostics < 0:
        parser.error("--max-diagnostics must be nonnegative")
    return arguments


def main() -> int:
    arguments = parse_arguments()
    report = seal_report(validate_run(arguments.run_root))
    if arguments.report is not None:
        try:
            atomic_write_report(arguments.report, report)
        except OSError as error:
            print(f"error: cannot write report atomically: {error}", file=sys.stderr)
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
