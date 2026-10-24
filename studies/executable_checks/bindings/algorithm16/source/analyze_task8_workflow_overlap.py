#!/usr/bin/env python3
"""Cold, model-free overlap analysis for the two completed Task-8 workflows.

The algorithm-test workflow was executed only on a positively selected
stage-2 set.  The executable-twin counterexample workflow used a much larger
population.  This script therefore reports the exact jointly observed support
and keeps "not executed" distinct from a negative result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent.parent
PART1_SEARCH = BASE / "outputs_algo_tests/test_search"
PART1_VERIFY = BASE / "outputs_algo_tests/test_verify"
PART2_SEARCH = BASE / "runs/code_twin/searches"
PART2_VERIFY = BASE / "runs/code_twin/verifies"
DEFAULT_JSON = BASE / "runs/code_twin/task8_workflow_overlap.json"
DEFAULT_MD = BASE / "runs/code_twin/TASK8_WORKFLOW_OVERLAP.md"


class AuditError(RuntimeError):
    """The frozen Task-8 evidence does not satisfy the overlap contract."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(value)
    os.replace(tmp, path)


def load_dir(path: Path, pattern: str = "*.json") -> dict[str, tuple[Path, dict[str, Any]]]:
    if path.is_symlink() or not path.is_dir():
        raise AuditError(f"required result directory absent or symlinked: {path}")
    rows: dict[str, tuple[Path, dict[str, Any]]] = {}
    for file in sorted(path.glob(pattern)):
        if file.is_symlink() or not file.is_file():
            raise AuditError(f"result is absent or symlinked: {file}")
        try:
            value = json.loads(file.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise AuditError(f"malformed JSON: {file}") from exc
        if not isinstance(value, dict) or value.get("record_id") != file.stem:
            raise AuditError(f"record identity mismatch: {file}")
        if file.stem in rows:
            raise AuditError(f"duplicate result identity: {file.stem}")
        rows[file.stem] = (file, value)
    return rows


def binding(path: Path, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(BASE.parent)),
        "sha256": sha256(path),
        "record_id": value["record_id"],
    }


def classify(code_success: bool, counterexample_success: bool) -> str:
    if code_success and counterexample_success:
        return "BOTH_CONFIRMED"
    if code_success:
        return "CODE_EXPERIMENT_ONLY"
    if counterexample_success:
        return "COUNTEREXAMPLE_WORKFLOW_ONLY"
    return "NEITHER_CONFIRMED"


def analyze() -> dict[str, Any]:
    p1_search = load_dir(PART1_SEARCH)
    p1_verify = load_dir(PART1_VERIFY)
    # Algorithms record IDs are already filename-safe.  Other Task-8 strata
    # use sanitized filenames and are deliberately outside this comparison.
    p2_search = load_dir(PART2_SEARCH, "Algorithms_*.json")
    p2_verify = load_dir(PART2_VERIFY, "Algorithms_*.json")

    if len(p1_search) != 16 or set(p1_search) != set(p1_verify):
        raise AuditError("Part 1 is not the frozen 16-search/16-verify frame")
    for rid in sorted(p1_search):
        search = p1_search[rid][1]
        verify = p1_verify[rid][1]
        if (search.get("outcome") not in {"BUG_FOUND", "BOUND_VIOLATION_FOUND"}
                or verify.get("verdict") != "CONFIRMED"):
            raise AuditError(f"Part-1 result is not a confirmed code bug: {rid}")
    if len(p2_search) != 65:
        raise AuditError(f"expected 65 Algorithms executable-twin searches, got {len(p2_search)}")
    for rid, (_, search) in p2_search.items():
        outcome = search.get("outcome")
        if outcome not in {
            "WITNESS_FOUND", "NO_WITNESS_EXHAUSTIVE",
            "NO_WITNESS_INCONCLUSIVE", "CLAIM_NOT_FINITELY_REFUTABLE",
        }:
            raise AuditError(f"invalid Part-2 search outcome: {rid}")
        verify = p2_verify.get(rid)
        if outcome == "WITNESS_FOUND":
            if verify is None or verify[1].get("verdict") not in {
                "CONFIRMED", "REFUTED_WITNESS_INVALID", "CANNOT_REPRODUCE",
            }:
                raise AuditError(f"Part-2 witness lacks a terminal verification: {rid}")
        elif verify is not None:
            raise AuditError(f"Part-2 non-witness unexpectedly has verification: {rid}")

    p1_ids = set(p1_search)
    p2_ids = set(p2_search)
    common = sorted(p1_ids & p2_ids)
    p1_only = sorted(p1_ids - p2_ids)
    p2_only = sorted(p2_ids - p1_ids)
    joint_rows: list[dict[str, Any]] = []
    for rid in common:
        s1_path, s1 = p1_search[rid]
        v1_path, v1 = p1_verify[rid]
        s2_path, s2 = p2_search[rid]
        v2_pair = p2_verify.get(rid)
        counter_success = bool(v2_pair and v2_pair[1].get("verdict") == "CONFIRMED")
        row = {
            "record_id": rid,
            "joint_category": classify(True, counter_success),
            "code_experiment": {
                "search_outcome": s1["outcome"],
                "verify_verdict": v1["verdict"],
                "search": binding(s1_path, s1),
                "verify": binding(v1_path, v1),
            },
            "counterexample_workflow": {
                "search_outcome": s2["outcome"],
                "verify_verdict": v2_pair[1]["verdict"] if v2_pair else None,
                "search": binding(s2_path, s2),
                "verify": binding(v2_pair[0], v2_pair[1]) if v2_pair else None,
            },
        }
        joint_rows.append(row)

    p2_only_confirmed = [
        rid for rid in p2_only
        if rid in p2_verify and p2_verify[rid][1].get("verdict") == "CONFIRMED"
    ]
    p2_only_invalid = [
        rid for rid in p2_only
        if rid in p2_verify
        and p2_verify[rid][1].get("verdict") == "REFUTED_WITNESS_INVALID"
    ]
    joint_counts = Counter(row["joint_category"] for row in joint_rows)
    p2_only_outcomes = Counter(p2_search[rid][1]["outcome"] for rid in p2_only)
    artifact = {
        "schema": "task8-workflow-overlap-v1",
        "status": "PASS",
        "audit_program": {
            "path": str(Path(__file__).resolve().relative_to(BASE.parent)),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "definitions": {
            "code_experiment_success": "Part-1 search found BUG_FOUND or BOUND_VIOLATION_FOUND and its independent verification is CONFIRMED.",
            "counterexample_workflow_success": "Part-2 executable-twin search found WITNESS_FOUND and its independent verification is CONFIRMED.",
            "joint_support": "Record IDs on which both workflows have an executed terminal result; absence from a workflow is never treated as failure.",
        },
        "frames": {
            "part1_confirmed_code_bug_records": len(p1_ids),
            "part2_algorithm_records": len(p2_ids),
            "jointly_observed_records": len(common),
            "part1_not_in_part2_population": len(p1_only),
            "part2_not_executed_by_part1_stage2": len(p2_only),
        },
        "joint_counts": {
            key: joint_counts.get(key, 0) for key in (
                "BOTH_CONFIRMED", "CODE_EXPERIMENT_ONLY",
                "COUNTEREXAMPLE_WORKFLOW_ONLY", "NEITHER_CONFIRMED",
            )
        },
        "joint_rows": joint_rows,
        "not_jointly_observed": {
            "part1_confirmed_bugs_outside_part2_population": p1_only,
            "part2_algorithm_records_without_part1_stage2_execution": {
                "count": len(p2_only),
                "search_outcomes": dict(sorted(p2_only_outcomes.items())),
                "confirmed_counterexamples": p2_only_confirmed,
                "invalid_witnesses": p2_only_invalid,
            },
        },
        "interpretation": [
            "On the 12-record common support, three records succeeded in both workflows and nine were confirmed only by the code experiment.",
            "There are zero measured counterexample-only cases on common support because Part 1 is a positively selected stage-2 frame: every jointly observed Part-1 record is already a confirmed code bug.",
            "Seventeen additional Algorithms records have confirmed executable-twin counterexamples but no Part-1 stage-2 execution. They are not counterexample-only failures of the code experiment; the code experiment is unobserved on them.",
            "The overlap is descriptive and selection-conditioned, not an accuracy comparison between workflows.",
        ],
    }
    return artifact


def markdown(artifact: dict[str, Any]) -> str:
    counts = artifact["joint_counts"]
    rows = artifact["joint_rows"]
    lines = [
        "# Task 8 workflow overlap",
        "",
        "Cold model-free audit: **PASS**.",
        "",
        "The only honest head-to-head frame is the 12 record IDs executed by both workflows.",
        "",
        "| Outcome on common support | Count |",
        "| --- | ---: |",
        f"| Both independently confirmed | {counts['BOTH_CONFIRMED']} |",
        f"| Code experiment only | {counts['CODE_EXPERIMENT_ONLY']} |",
        f"| Counterexample workflow only | {counts['COUNTEREXAMPLE_WORKFLOW_ONLY']} |",
        f"| Neither confirmed | {counts['NEITHER_CONFIRMED']} |",
        "",
        "| Record | Code experiment | Executable-twin workflow | Category |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        code = row["code_experiment"]["search_outcome"]
        twin = row["counterexample_workflow"]["search_outcome"]
        verdict = row["counterexample_workflow"]["verify_verdict"]
        twin_cell = twin if verdict is None else f"{twin} / {verdict}"
        lines.append(f"| `{row['record_id']}` | {code} / CONFIRMED | {twin_cell} | {row['joint_category']} |")
    extra = artifact["not_jointly_observed"]["part2_algorithm_records_without_part1_stage2_execution"]
    lines.extend([
        "",
        "## Scope limitation",
        "",
        f"Part 1 was a positively selected stage-2 frame. Another {extra['count']} Algorithms records were run only by the executable-twin workflow; {len(extra['confirmed_counterexamples'])} produced independently confirmed counterexamples. Those are not measured counterexample-only wins because the code experiment was never executed on them. Four confirmed Part-1 bugs were outside the Part-2 population.",
        "",
        "This is a descriptive, selection-conditioned overlap—not an accuracy comparison.",
    ])
    return "\n".join(lines) + "\n"


def self_test() -> None:
    expected = {
        (False, False): "NEITHER_CONFIRMED",
        (False, True): "COUNTEREXAMPLE_WORKFLOW_ONLY",
        (True, False): "CODE_EXPERIMENT_ONLY",
        (True, True): "BOTH_CONFIRMED",
    }
    for inputs, output in expected.items():
        if classify(*inputs) != output:
            raise AuditError("classification self-test failed")
    print("SELF_TEST PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    artifact = analyze()
    atomic_text(args.output_json, json.dumps(artifact, indent=1, sort_keys=True) + "\n")
    atomic_text(args.output_md, markdown(artifact))
    print(json.dumps({
        "status": artifact["status"],
        "joint_counts": artifact["joint_counts"],
        "json": str(args.output_json),
        "markdown": str(args.output_md),
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
