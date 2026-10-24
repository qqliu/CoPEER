#!/usr/bin/env python3
"""Create post-cutover BugBank receipts from every claim and proof sketch.

This is deliberately a versioned wrapper around the frozen paired-v2 receipt
program.  Historical v1 receipts bind that program's exact path and bytes, so
it must not be edited in place.  The v2 contract keeps its database, ordering,
and provenance rules while changing the query text for each ``results`` row to
``claim + "\n\n" + proof_sketch``.  It also records hashes of both the proof
sketch and the resulting query text.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
LEGACY_SCRIPT = SCRIPT.with_name("open_frontier_paired_v2_feedback.py")
SCHEMA = "open_frontier_paired_v2_bugbank_exposure_receipt_v2"
QUERY_TEXT_BASIS = "claim statement, two newlines, proof_sketch"


def _load_legacy_module():
    spec = importlib.util.spec_from_file_location(
        "open_frontier_paired_v2_feedback_legacy", LEGACY_SCRIPT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load legacy receipt program: {LEGACY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


legacy = _load_legacy_module()
_legacy_load_parent = legacy.load_parent
_legacy_retrieve_claim = legacy.retrieve_claim
_legacy_build_receipt = legacy.build_receipt
_query_texts: dict[int, str] = {}


def query_text(claim: str, proof_sketch: str) -> str:
    return f"{claim}\n\n{proof_sketch}"


def load_parent(
    path: Path, record_id: str, iteration: int
) -> tuple[dict[str, Any], bytes, list[dict[str, Any]]]:
    parent, raw, legacy_claims = _legacy_load_parent(
        path, record_id, iteration
    )
    if not legacy_claims:
        raise legacy.ReceiptError("parent results must contain at least one claim")
    _query_texts.clear()
    claims: list[dict[str, Any]] = []
    for index, legacy_claim in enumerate(legacy_claims):
        result = parent["results"][index]
        proof_sketch = result.get("proof_sketch")
        if type(proof_sketch) is not str or not proof_sketch.strip():
            raise legacy.ReceiptError(
                f"parent results[{index}].proof_sketch must be a nonempty string"
            )
        combined = query_text(legacy_claim["claim"], proof_sketch)
        _query_texts[index] = combined
        claims.append({
            **legacy_claim,
            "proof_sketch_sha256": legacy.sha_bytes(proof_sketch.encode("utf-8")),
            "query_text_sha256": legacy.sha_bytes(combined.encode("utf-8")),
        })
    return parent, raw, claims


def retrieve_claim(
    connection,
    claim_record: dict[str, Any],
    frequency,
    document_count: int,
    tables: set[str],
    k: int,
    record_id: str,
    iteration: int,
) -> dict[str, Any]:
    index = claim_record["claim_index"]
    original_claim = claim_record["claim"]
    query_record = {**claim_record, "claim": _query_texts[index]}
    result = _legacy_retrieve_claim(
        connection, query_record, frequency, document_count, tables, k,
        record_id, iteration,
    )
    # Keep the public claim field bound verbatim to results[index].claim.  The
    # separate query-text hash binds the proof sketch used for term selection.
    result["claim"] = original_claim
    return result


def build_receipt(arguments) -> dict[str, Any]:
    receipt = _legacy_build_receipt(arguments)
    legacy_stat = LEGACY_SCRIPT.stat()
    receipt["legacy_script"] = {
        "path": str(LEGACY_SCRIPT),
        "size_bytes": legacy_stat.st_size,
        "sha256": legacy.sha_file(LEGACY_SCRIPT),
        "reuse_scope": (
            "fail-closed filesystem, SQLite, ordering, payload, and output contracts"
        ),
    }
    receipt["parameters"]["salient_term_tie_break"] = (
        "first occurrence in query text"
    )
    receipt["parameters"]["query_text_basis"] = QUERY_TEXT_BASIS
    receipt.pop("receipt_payload_sha256", None)
    receipt["receipt_payload_sha256"] = legacy.sha_bytes(
        legacy.canonical_bytes(receipt)
    )
    return receipt


# The inherited implementation continues to own all fail-closed filesystem,
# SQLite, ordering, and output behavior.  Rebind only the versioned contract.
legacy.SCRIPT = SCRIPT
legacy.SCHEMA = SCHEMA
legacy.__doc__ = __doc__
legacy.load_parent = load_parent
legacy.retrieve_claim = retrieve_claim
legacy.build_receipt = build_receipt


if __name__ == "__main__":
    raise SystemExit(legacy.main())
