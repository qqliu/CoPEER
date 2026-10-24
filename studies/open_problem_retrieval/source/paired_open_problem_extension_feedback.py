#!/usr/bin/env python3
"""Create one immutable whole-proof BugBank receipt for an extension attempt.

The extension's attempt counter starts at one regardless of the iteration
number stored in the immutable seed.  Retrieval itself deliberately reuses the
audited implementation in ``paired_open_problem_feedback.py``; this wrapper
changes only parent identity and the receipt envelope.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import paired_open_problem_feedback as retrieval_core


SCRIPT = Path(__file__).resolve()
RETRIEVAL_CORE = Path(retrieval_core.__file__).resolve()
STOCK_RETRIEVER = SCRIPT.with_name("bugbank_retrieve.py")
SCHEMA = "paired_open_problem_extension_bugbank_receipt_v1"
K = 3
IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class ReceiptError(RuntimeError):
    """The requested receipt could not be created without ambiguity."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ReceiptError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_nonfinite_json(token: str) -> Any:
    raise ReceiptError(f"non-finite JSON number {token}")


def parse_finite_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        reject_nonfinite_json(token)
    return value


def strict_json_loads(text: str) -> Any:
    return json.loads(
        text, object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_nonfinite_json,
        parse_float=parse_finite_json_float,
    )


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2,
    ).encode("utf-8") + b"\n"


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise ReceiptError(f"{label} is not a plain file: {path}")


def load_parent(path: Path, record_id: str, arm: str) -> tuple[dict[str, Any], bytes, list[dict[str, Any]]]:
    require_file(path, "parent")
    raw = path.read_bytes()
    try:
        value = strict_json_loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReceiptError(f"parent is not UTF-8 JSON: {error}") from error
    if type(value) is not dict or value.get("record_id") != record_id:
        raise ReceiptError("parent record identity mismatch")
    # Seeds retain their original iteration/stage. Extension revisions have an
    # explicit attempt. Both forms are valid parents, but never cross arms.
    if value.get("arm") not in (None, arm):
        raise ReceiptError("parent arm mismatch")
    results = value.get("results")
    if type(results) is not list or not results:
        raise ReceiptError("parent results must be a nonempty array")
    claims: list[dict[str, Any]] = []
    for index, result in enumerate(results):
        if type(result) is not dict:
            raise ReceiptError(f"results[{index}] is not an object")
        claim = result.get("claim")
        proof = result.get("proof_sketch")
        if type(claim) is not str or not claim or type(proof) is not str or not proof:
            raise ReceiptError(f"results[{index}] lacks a complete claim/proof_sketch")
        query_text = f"{claim}\n\n{proof}"
        claims.append({
            "claim_index": index,
            "claim": claim,
            "claim_sha256": sha_bytes(claim.encode("utf-8")),
            "proof_sketch_sha256": sha_bytes(proof.encode("utf-8")),
            "query_text": query_text,
            "query_text_sha256": sha_bytes(query_text.encode("utf-8")),
        })
    return value, raw, claims


def external_binding(path: Path) -> dict[str, Any]:
    require_file(path, "bound implementation")
    return {
        "path": str(path.resolve()),
        "sha256": sha_file(path),
        "size_bytes": path.stat().st_size,
    }


def create_receipt(arguments: argparse.Namespace) -> dict[str, Any]:
    if arguments.attempt < 1 or arguments.k != K:
        raise ReceiptError(f"attempt must be positive and k must equal {K}")
    if IDENTITY.fullmatch(arguments.record_id or "") is None:
        raise ReceiptError("unsafe record ID")
    if IDENTITY.fullmatch(arguments.run_id or "") is None:
        raise ReceiptError("unsafe run ID")
    if arguments.arm != "bugbank":
        raise ReceiptError("this receipt is only for the bugbank arm")
    if re.fullmatch(r"[0-9a-f]{64}", arguments.db_sha256 or "") is None:
        raise ReceiptError("invalid database hash")
    if os.path.lexists(arguments.out):
        raise ReceiptError(f"refusing to overwrite {arguments.out}")
    require_file(arguments.db, "BugBank database")
    if sha_file(arguments.db) != arguments.db_sha256:
        raise ReceiptError("BugBank database hash mismatch")

    parent, parent_raw, claims = load_parent(
        arguments.parent_json, arguments.record_id, arguments.arm
    )
    parent_hash = sha_bytes(parent_raw)
    database_hash_before = sha_file(arguments.db)
    started_at = utc_now()
    started_ns = time.monotonic_ns()
    uri = "file:" + quote(str(arguments.db.resolve()), safe="/") + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("BEGIN")
        database_schema = retrieval_core.database_schema(connection)
        tables = set(database_schema["tables"])
        frequency, document_count = retrieval_core.build_document_frequency(connection)
        queries = []
        for claim in claims:
            query = retrieval_core.retrieve_claim(
                connection, claim, frequency, document_count, tables, K,
                arguments.record_id, arguments.attempt,
            )
            query["query_id"] = (
                f"{arguments.record_id}__bugbank__attempt_{arguments.attempt}"
                f"__claim_{claim['claim_index']}"
            )
            queries.append(query)
        status_counts = {
            row["status"]: row["count"]
            for row in connection.execute(
                "SELECT status, COUNT(*) AS count FROM entries "
                "GROUP BY status ORDER BY status COLLATE BINARY"
            )
        }
        database_metadata = {
            **database_schema,
            "sqlite_library_version": sqlite3.sqlite_version,
            "sqlite_user_version": connection.execute("PRAGMA user_version").fetchone()[0],
            "sqlite_schema_version": connection.execute("PRAGMA schema_version").fetchone()[0],
            "entry_count": document_count,
            "status_counts": status_counts,
        }
        if sha_file(arguments.db) != database_hash_before:
            raise ReceiptError("BugBank database changed during retrieval")
    finally:
        try:
            connection.rollback()
        finally:
            connection.close()
    if sha_file(arguments.parent_json) != parent_hash:
        raise ReceiptError("parent changed during retrieval")

    ended_ns = time.monotonic_ns()
    claim_snapshot = [
        {key: value for key, value in claim.items() if key != "query_text"}
        for claim in claims
    ]
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "run_id": arguments.run_id,
        "record_id": arguments.record_id,
        "arm": "bugbank",
        "attempt": arguments.attempt,
        "stage": "EXTENSION_BUGBANK_EXPOSURE",
        "status": "COMPLETE",
        "parent": {
            "path": str(arguments.parent_json.resolve()),
            "sha256": parent_hash,
            "size_bytes": len(parent_raw),
            "record_id": arguments.record_id,
            "arm": parent.get("arm"),
            "source_iteration": parent.get("iteration"),
            "extension_attempt": parent.get("attempt"),
        },
        "parent_claim_count": len(claim_snapshot),
        "parent_claims": claim_snapshot,
        "parent_claims_sha256": sha_bytes(canonical_bytes(claim_snapshot)),
        "database": {
            **external_binding(arguments.db),
            "open_mode": "SQLite URI mode=ro plus PRAGMA query_only",
            **database_metadata,
        },
        "script": external_binding(SCRIPT),
        "retrieval_core": external_binding(RETRIEVAL_CORE),
        "stock_retriever": external_binding(STOCK_RETRIEVER),
        "parameters": {
            "k_per_claim": K,
            "status_filter": "all",
            "exclude_self": False,
            "query_text_basis": "claim statement, two newlines, proof_sketch",
            "maximum_salient_terms": retrieval_core.MAX_QUERY_TERMS,
            "fts_bm25_weights": list(retrieval_core.BM25_WEIGHTS),
            "ordering": ["bm25_score_ASC_unrounded", "entry_id_BINARY_ASC"],
            "query_sql_sha256": sha_bytes(retrieval_core.RETRIEVAL_SQL.encode("utf-8")),
        },
        "queries": queries,
        "exposure_summary": {
            "query_count": len(queries),
            "hit_count": sum(query["hit_count"] for query in queries),
            "ordered_payload_sha256": sha_bytes(canonical_bytes(queries)),
        },
        "timing": {
            "started_at": started_at,
            "ended_at": utc_now(),
            "duration_nanoseconds": ended_ns - started_ns,
        },
    }
    receipt["receipt_payload_sha256"] = sha_bytes(canonical_bytes(receipt))
    return receipt


def write_exclusive(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o644)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise ReceiptError("short receipt write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-json", required=True, type=Path)
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--arm", default="bugbank")
    parser.add_argument("--attempt", required=True, type=int)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--k", default=K, type=int)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--db-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        receipt = create_receipt(arguments)
        write_exclusive(arguments.out, pretty_bytes(receipt))
    except (ReceiptError, OSError, sqlite3.Error) as error:
        print(f"error: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({
        "status": "COMPLETE",
        "record_id": arguments.record_id,
        "attempt": arguments.attempt,
        "claims": receipt["parent_claim_count"],
        "hits": receipt["exposure_summary"]["hit_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
