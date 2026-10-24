#!/usr/bin/env python3
"""Materialize one append-only whole-proof BugBank exposure receipt.

The input is a structured baseline or prior BugBank revision.  Every complete
``results[]`` row is queried independently as ``claim + "\n\n" + proof_sketch``
using the term-selection
and FTS5 weighting contract from ``bugbank_retrieve.py``.  Unlike that general
CLI, this experiment deliberately exposes all BugBank statuses, applies no
self/source exclusions, retains full-precision scores, and makes score ties
total by ordering on entry ID.

The output is evidence, not a cache: it is created with O_EXCL and an existing
path is always an error.  The receipt binds the exact parent bytes, ordered
claims, database, retrieval program, this program, parameters, and complete
ordered hit payload to SHA-256 digests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


SCRIPT = Path(__file__).resolve()
BASE = SCRIPT.parent.parent
REPO = BASE.parent
DEFAULT_DB = REPO / "BugBank/bugbank.sqlite"
STOCK_RETRIEVER = SCRIPT.parent / "bugbank_retrieve.py"

SCHEMA = "paired_open_problem_bugbank_exposure_receipt_v1"
ARM = "bugbank"
RETRIEVAL_K = 3
BM25_WEIGHTS = (2.0, 8.0, 4.0, 1.0, 1.0, 3.0)
MAX_QUERY_TERMS = 12

STOP = set(
    """a an and are as at be by for from has have if in into is it its of on
or that the their there these this to was we which will with not no nor so then
than let all any each every some such given hence thus where when suppose assume
proof claim show shows shown implies follows since because therefore step case
""".split()
)
WORD = re.compile(r"[a-zA-Z][a-zA-Z-]{2,}")
IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

ENTRY_COLUMNS = (
    "id",
    "title",
    "type",
    "domain",
    "subdomain",
    "refutes",
    "statement",
    "true_theorem",
    "hypothesis_violated",
    "source_book",
    "source_chapter",
    "source_item",
    "source_pages",
    "difficulty",
    "status",
    "body_md",
    "path",
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


class ReceiptError(RuntimeError):
    """The requested exposure receipt cannot be made auditable."""


def reject_nonfinite_json(token: str) -> Any:
    raise ReceiptError(f"non-finite JSON number {token}")


def parse_finite_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        reject_nonfinite_json(token)
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def output_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            indent=2,
        ).encode("utf-8")
        + b"\n"
    )


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def require_regular_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise ReceiptError(f"{label} is not a regular file: {path}")


def load_parent(
    path: Path, record_id: str, iteration: int
) -> tuple[dict[str, Any], bytes, list[dict[str, Any]]]:
    require_regular_file(path, "parent JSON")
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw.decode("utf-8"), parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_json_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReceiptError(f"parent JSON is not valid UTF-8 JSON: {error}") from error
    if type(value) is not dict:
        raise ReceiptError("parent JSON must be an object")
    if value.get("record_id") != record_id:
        raise ReceiptError(
            "parent record_id mismatch: "
            f"expected {record_id!r}, got {value.get('record_id')!r}"
        )

    parent_arm = value.get("arm")
    if parent_arm is not None and parent_arm != ARM:
        raise ReceiptError(
            f"parent arm must be absent or {ARM!r}, got {parent_arm!r}"
        )
    parent_iteration = value.get("iteration")
    if parent_iteration is None:
        if iteration != 1:
            raise ReceiptError(
                "only iteration 1 may use a parent without an iteration identity"
            )
    else:
        if type(parent_iteration) is not int or parent_iteration < 0:
            raise ReceiptError("parent iteration must be a non-negative integer")
        if parent_iteration != iteration - 1:
            raise ReceiptError(
                "parent iteration mismatch: "
                f"expected {iteration - 1}, got {parent_iteration}"
            )
        if iteration > 1 and parent_arm != ARM:
            raise ReceiptError("a later-iteration parent must identify the bugbank arm")
    if value.get("stage") == "ARM_NEUTRAL_BASELINE" and iteration != 1:
        raise ReceiptError("the arm-neutral baseline can only parent iteration 1")

    results = value.get("results")
    if type(results) is not list or not results:
        raise ReceiptError("parent results must be a nonempty array")
    claims: list[dict[str, Any]] = []
    for index, result in enumerate(results):
        if type(result) is not dict:
            raise ReceiptError(f"parent results[{index}] must be an object")
        claim = result.get("claim")
        proof_sketch = result.get("proof_sketch")
        if type(claim) is not str or not claim.strip():
            raise ReceiptError(f"parent results[{index}].claim must be nonempty")
        if type(proof_sketch) is not str or not proof_sketch.strip():
            raise ReceiptError(
                f"parent results[{index}].proof_sketch must be nonempty"
            )
        query_text = f"{claim}\n\n{proof_sketch}"
        claims.append({
            "claim_index": index,
            "claim": claim,
            "claim_sha256": sha_bytes(claim.encode("utf-8")),
            "proof_sketch_sha256": sha_bytes(proof_sketch.encode("utf-8")),
            "query_text": query_text,
            "query_text_sha256": sha_bytes(query_text.encode("utf-8")),
        })
    return value, raw, claims


def build_document_frequency(connection: sqlite3.Connection) -> tuple[Counter, int]:
    frequency: Counter[str] = Counter()
    rows = connection.execute(
        "SELECT id, refutes FROM entries ORDER BY id COLLATE BINARY"
    ).fetchall()
    for row in rows:
        refutes = row["refutes"] or ""
        for word in set(match.lower() for match in WORD.findall(refutes)):
            if word not in STOP:
                frequency[word] += 1
    return frequency, len(rows)


def salient_terms(
    text: str, frequency: Counter, document_count: int
) -> list[dict[str, Any]]:
    # Preserve the stock retriever's deterministic stable tie behavior: terms
    # with equal rarity remain in first-occurrence order in the exact claim.
    seen: dict[str, float] = {}
    for raw_word in WORD.findall(text):
        word = raw_word.lower()
        if word in STOP or len(word) < 3:
            continue
        seen.setdefault(
            word, (document_count + 1) / (frequency.get(word, 0) + 1)
        )
    ranked = sorted(seen.items(), key=lambda item: -item[1])[:MAX_QUERY_TERMS]
    return [
        {
            "term": term,
            "document_frequency": frequency.get(term, 0),
            "rarity_weight": weight,
        }
        for term, weight in ranked
    ]


def database_schema(connection: sqlite3.Connection) -> dict[str, Any]:
    table_rows = connection.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE type = 'table' ORDER BY name COLLATE BINARY"
    ).fetchall()
    table_sql = {row["name"]: row["sql"] for row in table_rows}
    if "entries" not in table_sql or "entries_fts" not in table_sql:
        raise ReceiptError("database lacks entries or entries_fts")
    fts_sql = table_sql["entries_fts"] or ""
    if "fts5" not in fts_sql.lower():
        raise ReceiptError("entries_fts is not an FTS5 table")
    actual_columns = tuple(
        row["name"] for row in connection.execute("PRAGMA table_info(entries)")
    )
    missing = [column for column in ENTRY_COLUMNS if column not in actual_columns]
    if missing:
        raise ReceiptError(f"database entries schema is missing columns: {missing}")
    return {
        "entries_columns": list(actual_columns),
        "entries_schema_sha256": sha_bytes((table_sql["entries"] or "").encode()),
        "entries_fts_schema_sha256": sha_bytes(fts_sql.encode()),
        "tables": sorted(table_sql),
    }


def auxiliary_provenance(
    connection: sqlite3.Connection, entry: dict[str, Any], tables: set[str]
) -> tuple[list[str], list[str], str | None]:
    entry_id = entry["id"]
    tags = (
        [
            row[0]
            for row in connection.execute(
                "SELECT tag FROM tags WHERE entry_id = ? ORDER BY tag COLLATE BINARY",
                (entry_id,),
            )
        ]
        if "tags" in tables
        else []
    )
    related = (
        [
            row[0]
            for row in connection.execute(
                "SELECT related_id FROM relations "
                "WHERE entry_id = ? ORDER BY related_id COLLATE BINARY",
                (entry_id,),
            )
        ]
        if "relations" in tables
        else []
    )
    citation = None
    if "sources" in tables and entry.get("source_book") is not None:
        source = connection.execute(
            "SELECT citation FROM sources WHERE id = ?", (entry["source_book"],)
        ).fetchone()
        citation = source[0] if source is not None else None
    return tags, related, citation


def retrieve_claim(
    connection: sqlite3.Connection,
    claim_record: dict[str, Any],
    frequency: Counter,
    document_count: int,
    tables: set[str],
    k: int,
    record_id: str,
    iteration: int,
) -> dict[str, Any]:
    terms = salient_terms(claim_record["query_text"], frequency, document_count)
    match_expression = " OR ".join(f'"{item["term"]}"' for item in terms)
    rows = (
        connection.execute(RETRIEVAL_SQL, (match_expression, k)).fetchall()
        if terms
        else []
    )
    hits = []
    for rank, row in enumerate(rows, 1):
        score = float(row["score"])
        if not score == score or score in (float("inf"), float("-inf")):
            raise ReceiptError("SQLite returned a non-finite BM25 score")
        entry = {column: row[column] for column in ENTRY_COLUMNS}
        tags, related, citation = auxiliary_provenance(connection, entry, tables)
        hit: dict[str, Any] = {
            "rank": rank,
            "bm25": score,
            "bm25_binary64_hex": score.hex(),
            "entry_id": entry["id"],
            "title": entry["title"],
            "type": entry["type"],
            "domain": entry["domain"],
            "subdomain": entry["subdomain"],
            "refutes": entry["refutes"],
            "statement": entry["statement"],
            "counterexample": entry["statement"],
            "true_theorem": entry["true_theorem"],
            "hypothesis_violated": entry["hypothesis_violated"],
            "source_book": entry["source_book"],
            "source_chapter": entry["source_chapter"],
            "source_item": entry["source_item"],
            "source_pages": entry["source_pages"],
            "source_citation": citation,
            "difficulty": entry["difficulty"],
            "status": entry["status"],
            "body_md": entry["body_md"],
            "path": entry["path"],
            "tags": tags,
            "related_entry_ids": related,
        }
        hit["treatment_content_sha256"] = sha_bytes(canonical_bytes({
            "refutes": hit["refutes"],
            "counterexample": hit["counterexample"],
            "true_theorem": hit["true_theorem"],
        }))
        hit["entry_payload_sha256"] = sha_bytes(canonical_bytes({
            **entry,
            "tags": tags,
            "related_entry_ids": related,
            "source_citation": citation,
        }))
        hit["hit_payload_sha256"] = sha_bytes(canonical_bytes(hit))
        hits.append(hit)

    # Independently assert the promised total order before it becomes evidence.
    for previous, current in zip(hits, hits[1:]):
        previous_key = (previous["bm25"], previous["entry_id"])
        current_key = (current["bm25"], current["entry_id"])
        if previous_key > current_key:
            raise ReceiptError("SQLite hits violate score/entry-ID ordering")

    index = claim_record["claim_index"]
    public_claim_record = {
        key: value for key, value in claim_record.items() if key != "query_text"
    }
    return {
        "query_id": f"{record_id}__{ARM}__iter_{iteration}__claim_{index}",
        **public_claim_record,
        "salient_terms": terms,
        "fts_match_expression": match_expression,
        "hit_count": len(hits),
        "hits": hits,
    }


def create_exclusive(path: Path, data: bytes) -> None:
    if os.path.lexists(path):
        raise ReceiptError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o644)
    except FileExistsError as error:
        raise ReceiptError(f"refusing to overwrite existing output: {path}") from error
    try:
        offset = 0
        while offset < len(data):
            written = os.write(descriptor, data[offset:])
            if written <= 0:
                raise ReceiptError(f"short write while creating receipt: {path}")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def build_receipt(arguments: argparse.Namespace) -> dict[str, Any]:
    if type(arguments.iteration) is not int or arguments.iteration < 1:
        raise ReceiptError("--iteration must be a positive integer")
    if arguments.k != RETRIEVAL_K:
        raise ReceiptError(f"--k is fixed at {RETRIEVAL_K}")
    if type(arguments.record_id) is not str or IDENTITY.fullmatch(arguments.record_id) is None:
        raise ReceiptError("--record-id contains unsafe characters")
    if type(arguments.run_id) is not str or IDENTITY.fullmatch(arguments.run_id) is None:
        raise ReceiptError("--run-id contains unsafe characters")
    if not re.fullmatch(r"[0-9a-f]{64}", arguments.db_sha256 or ""):
        raise ReceiptError("--db-sha256 must be a lowercase SHA-256 digest")

    parent_path = Path(arguments.parent_json)
    output_path = Path(arguments.out)
    canonical_output_path = Path(getattr(arguments, "canonical_out", None) or arguments.out)
    database_path = Path(arguments.db)
    if os.path.lexists(output_path):
        raise ReceiptError(f"refusing to overwrite existing output: {output_path}")
    require_regular_file(database_path, "BugBank database")
    require_regular_file(SCRIPT, "receipt script")
    require_regular_file(STOCK_RETRIEVER, "stock BugBank retriever")
    if sha_file(database_path) != arguments.db_sha256:
        raise ReceiptError("BugBank database does not match --db-sha256")

    started_at = utc_now()
    started_ns = time.monotonic_ns()
    parent, parent_raw, claims = load_parent(
        parent_path, arguments.record_id, arguments.iteration
    )
    parent_sha256 = sha_bytes(parent_raw)
    database_sha256_before = sha_file(database_path)

    database_uri = "file:" + quote(str(database_path.resolve()), safe="/") + "?mode=ro"
    connection = sqlite3.connect(database_uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("BEGIN")
        schema = database_schema(connection)
        tables = set(schema["tables"])
        frequency, document_count = build_document_frequency(connection)
        status_counts = {
            row["status"]: row["count"]
            for row in connection.execute(
                "SELECT status, COUNT(*) AS count FROM entries "
                "GROUP BY status ORDER BY status COLLATE BINARY"
            )
        }
        queries = [
            retrieve_claim(
                connection,
                claim,
                frequency,
                document_count,
                tables,
                arguments.k,
                arguments.record_id,
                arguments.iteration,
            )
            for claim in claims
        ]
        database_metadata = {
            **schema,
            "sqlite_library_version": sqlite3.sqlite_version,
            "sqlite_user_version": connection.execute(
                "PRAGMA user_version"
            ).fetchone()[0],
            "sqlite_schema_version": connection.execute(
                "PRAGMA schema_version"
            ).fetchone()[0],
            "journal_mode": connection.execute("PRAGMA journal_mode").fetchone()[0],
            "entry_count": document_count,
            "status_counts": status_counts,
        }
        # The read transaction prevents a rollback-journal writer from changing
        # the queried snapshot while its main-file hash is checked.
        database_sha256_after = sha_file(database_path)
        if database_sha256_after != database_sha256_before:
            raise ReceiptError("BugBank database changed during retrieval")
    finally:
        try:
            connection.rollback()
        finally:
            connection.close()

    # Detect parent replacement/editing during the comparatively slower query.
    if sha_file(parent_path) != parent_sha256:
        raise ReceiptError("parent JSON changed during retrieval")

    claim_snapshot = [
        {key: value for key, value in item.items() if key != "query_text"}
        for item in claims
    ]
    exposure_payload = canonical_bytes(queries)
    ended_ns = time.monotonic_ns()
    ended_at = utc_now()
    database_stat = database_path.stat()
    script_stat = SCRIPT.stat()
    retriever_stat = STOCK_RETRIEVER.stat()

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "run_id": arguments.run_id,
        "pair_id": arguments.record_id,
        "record_id": arguments.record_id,
        "arm": ARM,
        "iteration": arguments.iteration,
        "stage": "BUGBANK_FEEDBACK_EXPOSURE",
        "status": "COMPLETE",
        "parent": {
            "requested_path": str(parent_path),
            "path": str(parent_path.resolve()),
            "size_bytes": len(parent_raw),
            "sha256": parent_sha256,
            "canonical_payload_sha256": sha_bytes(canonical_bytes(parent)),
            "record_id": parent["record_id"],
            "arm": parent.get("arm"),
            "iteration": parent.get("iteration"),
            "stage": parent.get("stage"),
        },
        "parent_claim_count": len(claims),
        "parent_claims": claim_snapshot,
        "parent_claims_sha256": sha_bytes(canonical_bytes(claim_snapshot)),
        "database": {
            "requested_path": str(database_path),
            "path": str(database_path.resolve()),
            "size_bytes": database_stat.st_size,
            "sha256": database_sha256_before,
            "open_mode": "SQLite URI mode=ro plus PRAGMA query_only",
            **database_metadata,
        },
        "script": {
            "path": str(SCRIPT),
            "size_bytes": script_stat.st_size,
            "sha256": sha_file(SCRIPT),
        },
        "stock_retriever": {
            "path": str(STOCK_RETRIEVER),
            "size_bytes": retriever_stat.st_size,
            "sha256": sha_file(STOCK_RETRIEVER),
            "reuse_scope": "STOP, WORD, document-frequency, salient-term, and BM25 contracts",
        },
        "invocation": {
            "run_id": arguments.run_id,
            "parent_json": str(parent_path),
            "record_id": arguments.record_id,
            "iteration": arguments.iteration,
            "out": str(canonical_output_path),
            "k": arguments.k,
            "db": str(database_path),
            "db_sha256": arguments.db_sha256,
        },
        "parameters": {
            "k_per_claim": arguments.k,
            "status_filter": "all",
            "exclude_self": False,
            "excluded_source_items": [],
            "excluded_entry_ids": [],
            "document_frequency_corpus": "all entries.refutes rows across all statuses",
            "maximum_salient_terms": MAX_QUERY_TERMS,
            "salient_term_tie_break": "first occurrence in query text",
            "query_text_basis": "claim statement, two newlines, proof_sketch",
            "fts_bm25_weights": list(BM25_WEIGHTS),
            "ordering": ["bm25_score_ASC_unrounded", "entry_id_BINARY_ASC"],
            "truncate_stage": "after status-all query and total ordering",
            "query_sql": RETRIEVAL_SQL,
            "query_sql_sha256": sha_bytes(RETRIEVAL_SQL.encode("utf-8")),
        },
        "queries": queries,
        "exposure_summary": {
            "query_count": len(queries),
            "hit_count": sum(query["hit_count"] for query in queries),
            "ordered_payload_sha256": sha_bytes(exposure_payload),
            "ordered_payload_size_bytes": len(exposure_payload),
            "payload_contract": "canonical JSON of the complete ordered queries array",
        },
        "timing": {
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_nanoseconds": ended_ns - started_ns,
            "duration_seconds": (ended_ns - started_ns) / 1_000_000_000,
            "clock": "time.monotonic_ns",
            "timestamps_timezone": "UTC",
        },
        "receipt_hash_contract": (
            "SHA-256 of canonical JSON for this object before receipt_payload_sha256 is added"
        ),
    }
    receipt["receipt_payload_sha256"] = sha_bytes(canonical_bytes(receipt))
    return receipt


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-json", required=True, type=Path)
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--iteration", required=True, type=int)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--canonical-out", type=Path,
        help="canonical final path to bind while --out is an atomic staging path",
    )
    parser.add_argument("--k", type=int, default=RETRIEVAL_K)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--db-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        receipt = build_receipt(arguments)
        data = output_bytes(receipt)
        create_exclusive(arguments.out, data)
    except (ReceiptError, OSError, sqlite3.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "COMPLETE",
        "out": str(arguments.out),
        "record_id": arguments.record_id,
        "arm": ARM,
        "iteration": arguments.iteration,
        "claims": receipt["parent_claim_count"],
        "hits": receipt["exposure_summary"]["hit_count"],
        "receipt_payload_sha256": receipt["receipt_payload_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
