#!/usr/bin/env python3
"""Synchronize the research-source counterexamples into BugBank.

The bridge has four deliberately separate stages:

* ``export`` turns the source checkout's authoritative dossiers into a
  deterministic, versioned bundle with certificate checksums;
* ``bootstrap`` captures BugBank-owned editorial metadata and the state of the
  already-imported records;
* ``check`` plans an incremental sync without writing; and
* ``apply`` stages approved changes, rejects conflicts, and updates sync state.

Source records are never published merely because they exist.  A record needs
an explicit metadata row with ``publish: true``.  Existing hand-maintained
entries can use ``management: preserve``; generated entries use optimistic
hash checks so upstream updates never overwrite later local edits silently.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterable, Mapping

import yaml

try:
    from . import active_release
except ImportError:  # direct script invocation
    import active_release


ROOT = Path(__file__).resolve().parent.parent
QQ_SOURCE_BOOKS = ("qedbench-pipeline", "qedbench-canonical-600")
BUNDLE_SCHEMA_VERSION = 1
METADATA_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 1
SOURCE_REPOSITORY = "example/research-source"
IMPORT_DIR = ROOT / "imports" / "qq-research-source"
DEFAULT_METADATA = IMPORT_DIR / "metadata.json"
DEFAULT_STATE = IMPORT_DIR / "state.json"

ENTRY_TYPES = {"counterexample", "example", "pathology", "sharpness"}
ENTRY_STATUSES = {"seeded", "verified", "draft"}
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", re.DOTALL)
IMPORT_RE = re.compile(r"^import ([A-Za-z][\w.]*)", re.MULTILINE)
PRIVATE_PATH_RE = re.compile(
    r"/(?:nfs|home|Users|private)/[^\s,;)\]}>\"']+"
)


class BundleError(RuntimeError):
    """The source export is malformed, incomplete, or has been tampered with."""


class SyncError(RuntimeError):
    """The requested sync cannot be applied safely."""


@dataclass(frozen=True)
class Coverage:
    missing: tuple[str, ...]
    removed: tuple[str, ...]

    @property
    def in_sync(self) -> bool:
        return not self.missing and not self.removed


def compare_coverage(*, source_ids: Iterable[str], imported_ids: Iterable[str]) -> Coverage:
    source = set(source_ids)
    imported = set(imported_ids)
    return Coverage(
        missing=tuple(sorted(source - imported)),
        removed=tuple(sorted(imported - source)),
    )


@dataclass(frozen=True)
class Bundle:
    root: Path
    manifest: dict
    records: dict[str, dict]


@dataclass(frozen=True)
class PlannedChange:
    record_id: str
    action: str
    entry_path: str
    entry_text: str
    certificate_bundle_path: str | None
    certificate_destination: str | None


@dataclass(frozen=True)
class SyncPlan:
    changes: tuple[PlannedChange, ...] = ()
    pending_metadata: tuple[str, ...] = ()
    unreleased: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def has_blockers(self) -> bool:
        return bool(self.pending_metadata or self.removed or self.conflicts or self.errors)

    @property
    def clean(self) -> bool:
        return not self.changes and not self.has_blockers

    def report(self) -> dict:
        return {
            "changes": [
                {"record_id": c.record_id, "action": c.action, "entry_path": c.entry_path}
                for c in self.changes
            ],
            "pending_metadata": list(self.pending_metadata),
            "unreleased": list(self.unreleased),
            "removed": list(self.removed),
            "conflicts": list(self.conflicts),
            "errors": list(self.errors),
            "has_blockers": self.has_blockers,
            "clean": self.clean,
        }


def _json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SyncError(f"{path} must contain a JSON object")
    return value


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _safe_relative(raw: str, *, context: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise BundleError(f"{context}: unsafe relative path {raw!r}")
    return path


def _source_relative(path: Path, source_root: Path, *, record_id: str) -> Path:
    candidate = path if path.is_absolute() else source_root / path
    try:
        return candidate.resolve().relative_to(source_root.resolve())
    except ValueError as exc:
        raise BundleError(
            f"{record_id}: certificate lies outside source checkout: {candidate}"
        ) from exc


def _record_digest(record: Mapping) -> str:
    payload = dict(record)
    payload.pop("record_sha256", None)
    return _sha256_bytes(_json_bytes(payload))


def _public_text(value) -> str:
    return PRIVATE_PATH_RE.sub("[private path omitted]", str(value or "")).strip()


def _normalized_record(row: dict, source_root: Path, out_dir: Path) -> dict:
    record_id = row.get("record_id")
    if not isinstance(record_id, str) or not record_id:
        raise BundleError("source dossier has no stable record_id")
    for key in ("corpus", "flaw", "witness", "explanation"):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise BundleError(f"{record_id}: missing required dossier field {key}")

    compiled = bool(row.get("lean_compiled"))
    lean_path = row.get("lean_path")
    certificate = None
    if compiled:
        if not lean_path:
            raise BundleError(f"{record_id}: compiled record has no certificate path")
        relative = _source_relative(Path(lean_path), source_root, record_id=record_id)
        source_path = source_root / relative
        if not source_path.is_file():
            raise BundleError(f"{record_id}: certificate not found: {source_path}")
        data = source_path.read_bytes()
        bundle_rel = Path("certificates") / relative
        destination = out_dir / bundle_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != data:
            raise BundleError(f"{record_id}: certificate bundle-path collision: {bundle_rel}")
        destination.write_bytes(data)
        text = data.decode("utf-8")
        certificate = {
            "source_path": relative.as_posix(),
            "bundle_path": bundle_rel.as_posix(),
            "sha256": _sha256_bytes(data),
            "imports": IMPORT_RE.findall(text),
        }
    elif lean_path:
        raise BundleError(f"{record_id}: uncompiled record unexpectedly has a certificate")

    route = row.get("certificate_route")
    if not route:
        route = "LEGACY_COMPILED" if compiled else "DESCOPE"
    if not compiled and route != "DESCOPE":
        raise BundleError(f"{record_id}: noncompiled record must use DESCOPE, got {route}")

    normalized = {
        "record_id": record_id,
        "corpus": _public_text(row["corpus"]),
        "problem": _public_text(row.get("problem")),
        "quote": _public_text(row.get("quote")),
        "flaw": _public_text(row["flaw"]),
        "witness": _public_text(row["witness"]),
        "explanation": _public_text(row["explanation"]),
        "verification_notes": _public_text(row.get("verification_notes")),
        "link": _public_text(row.get("link")),
        "attribution": _public_text(row.get("attribution")),
        "full_ref": _public_text(row.get("full_ref")),
        "novelty_note": _public_text(row.get("novelty_note")),
        "lean_note": _public_text(row.get("lean_note")),
        "certificate_route": route,
        "lean_compiled": compiled,
        "certificate": certificate,
    }
    normalized["record_sha256"] = _record_digest(normalized)
    return normalized


def export_bundle(
    dossiers: Iterable[dict],
    source_root: Path,
    source_commit: str,
    out_dir: Path,
) -> Bundle:
    """Emit a deterministic, portable export from source dossier dictionaries."""
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise BundleError(f"source checkout does not exist: {source_root}")
    if not source_commit or any(c.isspace() for c in source_commit):
        raise BundleError("source commit must be a nonempty token")
    if out_dir.exists() and any(out_dir.iterdir()):
        raise BundleError(f"bundle output is not empty: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    records: dict[str, dict] = {}
    for row in dossiers:
        record = _normalized_record(row, source_root, out_dir)
        record_id = record["record_id"]
        if record_id in records:
            raise BundleError(f"duplicate source record ID: {record_id}")
        records[record_id] = record

    records_bytes = b"".join(_json_bytes(records[key]) for key in sorted(records))
    (out_dir / "records.jsonl").write_bytes(records_bytes)
    certificate_paths = {
        row["certificate"]["bundle_path"]
        for row in records.values() if row["certificate"]
    }
    manifest = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": source_commit,
        "record_count": len(records),
        "certificate_count": len(certificate_paths),
        "records_sha256": _sha256_bytes(records_bytes),
    }
    (out_dir / "manifest.json").write_bytes(_json_bytes(manifest))
    return load_bundle(out_dir)


def load_bundle(bundle_dir: Path) -> Bundle:
    try:
        manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
        records_bytes = (bundle_dir / "records.jsonl").read_bytes()
    except (OSError, json.JSONDecodeError) as exc:
        raise BundleError(f"cannot read bundle {bundle_dir}: {exc}") from exc
    if manifest.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        raise BundleError(f"unsupported bundle schema {manifest.get('schema_version')!r}")
    if manifest.get("source_repository") != SOURCE_REPOSITORY:
        raise BundleError("bundle source repository is not approved")
    if _sha256_bytes(records_bytes) != manifest.get("records_sha256"):
        raise BundleError("records.jsonl checksum mismatch")

    records: dict[str, dict] = {}
    try:
        lines = records_bytes.decode("utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            if not line:
                continue
            row = json.loads(line)
            record_id = row.get("record_id")
            if not isinstance(record_id, str) or not record_id:
                raise BundleError(f"records.jsonl:{number}: missing record_id")
            if record_id in records:
                raise BundleError(f"duplicate source record ID: {record_id}")
            if row.get("record_sha256") != _record_digest(row):
                raise BundleError(f"{record_id}: record checksum mismatch")
            cert = row.get("certificate")
            if cert:
                relative = _safe_relative(cert.get("bundle_path", ""), context=record_id)
                path = bundle_dir / relative
                if not path.is_file():
                    raise BundleError(f"{record_id}: bundled certificate is missing")
                if _sha256_file(path) != cert.get("sha256"):
                    raise BundleError(f"{record_id}: certificate checksum mismatch")
            records[record_id] = row
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"invalid records.jsonl: {exc}") from exc

    if len(records) != manifest.get("record_count"):
        raise BundleError("bundle record count mismatch")
    cert_paths = {
        row["certificate"]["bundle_path"]
        for row in records.values() if row.get("certificate")
    }
    if len(cert_paths) != manifest.get("certificate_count"):
        raise BundleError("bundle certificate count mismatch")
    return Bundle(bundle_dir, manifest, records)


def _parse_entry(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise SyncError(f"{path}: missing YAML frontmatter")
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise SyncError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(meta, dict):
        raise SyncError(f"{path}: frontmatter must be a mapping")
    return meta, text


def bootstrap_crosswalk(bugbank_root: Path, bundle: Bundle) -> tuple[dict, dict]:
    """Capture current BugBank curation and imported-state hashes.

    This is intentionally a one-time migration helper.  New records are added
    to metadata by review rather than silently bootstrapped from source prose.
    """
    authority = active_release.load(bugbank_root)
    by_source: dict[str, tuple[Path, dict, str]] = {}
    for path in sorted((bugbank_root / "entries").glob("*/*.md")):
        if path.name.startswith("_"):
            continue
        meta, text = _parse_entry(path)
        source = meta.get("source") or {}
        if source.get("book") not in QQ_SOURCE_BOOKS or source.get("item") is None:
            continue
        record_id = str(source["item"])
        if record_id in by_source:
            raise SyncError(f"duplicate BugBank source item: {record_id}")
        by_source[record_id] = (path, meta, text)

    for record_id in bundle.records:
        review = active_release.protected(authority, record_id)
        if review and record_id not in by_source:
            path = bugbank_root / review["archive_path"]
            meta, text = _parse_entry(path)
            by_source[record_id] = (path, meta, text)
    missing = sorted(set(bundle.records) - set(by_source))
    if missing:
        raise SyncError(
            f"cannot bootstrap: {len(missing)} source records are not in BugBank; "
            f"first examples: {missing[:5]}"
        )

    metadata = {"schema_version": METADATA_SCHEMA_VERSION, "records": {}}
    state = {"schema_version": STATE_SCHEMA_VERSION, "records": {}}
    for record_id in sorted(bundle.records):
        path, entry, text = by_source[record_id]
        review = active_release.protected(authority, record_id, entry["id"])
        relative = review["entry_path"] if review else path.relative_to(bugbank_root).as_posix()
        source_book = (entry.get("source") or {}).get("book")
        management = "generated" if source_book == "qedbench-canonical-600" else "preserve"
        if review:
            management = "preserve"
        formalized = [
            item for item in (entry.get("formalized") or [])
            if isinstance(item, str) and not Path(item).is_absolute()
        ]
        row = {
            "entry_id": entry["id"],
            "entry_path": relative,
            "title": entry["title"],
            "domain": entry["domain"],
            "subdomain": entry["subdomain"],
            "tags": entry.get("tags") or [],
            "difficulty": entry["difficulty"],
            "related": entry.get("related") or [],
            "publish": not bool(review),
            "management": management,
            "source_book": source_book,
            "formalized": formalized,
        }
        if entry.get("true_theorem"):
            row["true_theorem"] = entry["true_theorem"]
        if entry.get("hypothesis_violated"):
            row["hypothesis_violated"] = entry["hypothesis_violated"]
        record = bundle.records[record_id]
        local_certificate = None
        certificate_sha = None
        if record.get("certificate") and management == "generated":
            local = [item for item in formalized if item.startswith("lean/")]
            if len(local) != 1:
                raise SyncError(
                    f"{record_id}: generated compiled entry needs one local formalized path"
                )
            local_certificate = local[0]
            local_path = bugbank_root / _safe_relative(
                local_certificate, context=f"{record_id} formalized"
            )
            if not local_path.is_file():
                raise SyncError(f"{record_id}: missing vendored certificate {local_certificate}")
            certificate_sha = _sha256_file(local_path)
            if certificate_sha != record["certificate"]["sha256"]:
                raise SyncError(f"{record_id}: vendored certificate differs from source bundle")
            row["certificate_destination"] = local_certificate

        metadata["records"][record_id] = row
        state_row = {
            "record_sha256": record["record_sha256"],
            "entry_path": relative,
            "entry_sha256": _sha256_bytes(text.encode("utf-8")),
            "source_commit": bundle.manifest["source_commit"],
            "management": management,
        }
        if local_certificate:
            state_row["certificate_destination"] = local_certificate
            state_row["certificate_sha256"] = certificate_sha
        state["records"][record_id] = state_row
    return metadata, state


def _validate_metadata(metadata: dict) -> list[str]:
    errors: list[str] = []
    if metadata.get("schema_version") != METADATA_SCHEMA_VERSION:
        return [f"unsupported metadata schema {metadata.get('schema_version')!r}"]
    records = metadata.get("records")
    if not isinstance(records, dict):
        return ["metadata records must be an object"]
    seen_entries: dict[str, str] = {}
    for record_id, row in records.items():
        if not isinstance(row, dict):
            errors.append(f"{record_id}: metadata row must be an object")
            continue
        for field in ("entry_id", "title", "domain", "subdomain", "tags",
                      "difficulty", "publish", "management"):
            if field not in row:
                errors.append(f"{record_id}: metadata missing {field}")
        entry_id = row.get("entry_id")
        if not isinstance(entry_id, str) or not SLUG_RE.match(entry_id):
            errors.append(f"{record_id}: invalid entry_id {entry_id!r}")
        elif entry_id in seen_entries:
            errors.append(
                f"{record_id}: entry_id {entry_id!r} also belongs to {seen_entries[entry_id]}"
            )
        else:
            seen_entries[entry_id] = record_id
        for field in ("domain", "subdomain"):
            value = row.get(field)
            if not isinstance(value, str) or not SLUG_RE.match(value):
                errors.append(f"{record_id}: invalid {field} {value!r}")
        if not isinstance(row.get("tags"), list) or not all(
            isinstance(tag, str) and SLUG_RE.match(tag) for tag in row.get("tags", [])
        ):
            errors.append(f"{record_id}: tags must be slug strings")
        if not isinstance(row.get("difficulty"), int) or not 1 <= row.get("difficulty", 0) <= 5:
            errors.append(f"{record_id}: difficulty must be an integer from 1 to 5")
        if not isinstance(row.get("publish"), bool):
            errors.append(f"{record_id}: publish must be boolean")
        if row.get("management") not in {"generated", "preserve"}:
            errors.append(f"{record_id}: management must be generated or preserve")
    return errors


def _corpus_tags(corpus: str) -> list[str]:
    mapping = (
        ("Reddit", "reddit-corpus"),
        ("Stack Exchange", "stack-exchange-corpus"),
        ("math.StackExchange", "stack-exchange-corpus"),
        ("ProofWiki", "proofwiki-corpus"),
        ("arXiv", "arxiv-corpus"),
        ("QEDBench", "qedbench"),
        ("Quarantined", "previously-published"),
    )
    return [tag for needle, tag in mapping if needle in corpus]


def _blockquote(text: str, max_lines: int) -> str:
    lines = text.strip().splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["[...]"]
    return "\n".join(f"> {line}" for line in lines)


def render_entry(
    record: dict,
    editorial: dict,
    source_commit: str,
    certificate_destination: str | None,
) -> str:
    tags = list(dict.fromkeys(
        list(editorial["tags"])
        + _corpus_tags(record["corpus"])
        + (["machine-checked"] if record["lean_compiled"] else [])
    ))
    statement = record["witness"]
    if record["certificate"]:
        imports = record["certificate"]["imports"]
        qualifier = (
            f"a vendored Lean 4 certificate importing {', '.join(imports)}"
            if imports else "a self-contained zero-import Lean 4 kernel certificate"
        )
        statement += f" The negation of the claim on this witness is checked by {qualifier}."

    front = {
        "id": editorial["entry_id"],
        "title": editorial["title"],
        "type": "counterexample",
        "domain": editorial["domain"],
        "subdomain": editorial["subdomain"],
        "tags": tags,
        "refutes": record["flaw"],
        "statement": statement,
        "source": {
            "book": editorial.get("source_book", "qedbench-canonical-600"),
            "chapter": record["corpus"],
            "item": record["record_id"],
            "pages": None,
        },
        "difficulty": editorial["difficulty"],
        "status": "verified" if record["lean_compiled"] else "draft",
        "related": editorial.get("related") or [],
        "imported_from": {
            "repository": SOURCE_REPOSITORY,
            "commit": source_commit,
            "record_id": record["record_id"],
            "record_sha256": record["record_sha256"],
        },
    }
    for field in ("true_theorem", "hypothesis_violated"):
        if editorial.get(field):
            front[field] = editorial[field]
    if certificate_destination:
        front["formalized"] = [certificate_destination]
        front["imported_from"]["certificate_sha256"] = record["certificate"]["sha256"]

    body = [
        "## Object\n",
        "The verified witness recorded by the research-source pipeline:\n",
        record["witness"] + "\n",
        "## What it kills\n",
        f"The flagged claim: **{record['flaw']}**\n",
    ]
    if record["quote"]:
        body += ["The flawed source step reads:\n", _blockquote(record["quote"], 14) + "\n"]
    if record["problem"]:
        body += ["Context of the original problem:\n", _blockquote(record["problem"], 10) + "\n"]
    body += [
        "The witness satisfies the stated hypotheses and falsifies the conclusion, "
        "refuting the step as written.\n",
        "## Why it works\n",
        record["explanation"] + "\n",
    ]
    if record["verification_notes"]:
        body += ["Independent verification notes:\n",
                 _blockquote(record["verification_notes"], 18) + "\n"]
    remarks = [
        f"- Provenance: `{record['record_id']}` from `{SOURCE_REPOSITORY}` at "
        f"commit `{source_commit}`; normalized record SHA-256 "
        f"`{record['record_sha256']}`.",
        f"- Certificate route: `{record['certificate_route']}`.",
    ]
    if record["certificate"]:
        remarks.append(
            f"- Vendored certificate: `{certificate_destination}`; SHA-256 "
            f"`{record['certificate']['sha256']}`."
        )
    elif record["lean_note"]:
        remarks.append(f"- {record['lean_note']}")
    if "Quarantined" in record["corpus"]:
        remarks.append(
            "- Publication status: the equivalent counterexample was previously "
            "published; this independently verified refutation is retained and tagged."
        )
    if record["novelty_note"]:
        remarks.append(f"- {record['novelty_note']}")
    body += ["## Remarks\n", "\n".join(remarks) + "\n", "## References\n"]
    references = []
    if record["link"]:
        references.append(f"- Original source: {record['link']}")
    if record["attribution"]:
        references.append(f"- Attribution: {record['attribution']}")
    if record["full_ref"]:
        references.append(f"- Pipeline record: `{record['full_ref']}`.")
    body.append("\n".join(references) + "\n")

    yaml_text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True,
                               width=88, default_flow_style=False)
    return "---\n" + yaml_text + "---\n\n" + "\n".join(body)


def _entry_path(editorial: dict) -> str:
    return editorial.get("entry_path") or (
        f"entries/{editorial['domain']}/{editorial['entry_id']}.md"
    )


def _certificate_destination(record: dict, editorial: dict) -> str | None:
    if not record.get("certificate"):
        return None
    explicit = editorial.get("certificate_destination")
    if explicit:
        return explicit
    basename = Path(record["certificate"]["source_path"]).name
    return f"lean/canonical600/{basename}"


def plan_sync(bundle: Bundle, metadata: dict, state: dict, bugbank_root: Path) -> SyncPlan:
    errors = _validate_metadata(metadata)
    if state.get("schema_version") != STATE_SCHEMA_VERSION:
        errors.append(f"unsupported state schema {state.get('schema_version')!r}")
    state_records = state.get("records")
    if not isinstance(state_records, dict):
        errors.append("state records must be an object")
        state_records = {}
    if errors:
        return SyncPlan(errors=tuple(sorted(errors)))

    authority = active_release.load(bugbank_root)
    metadata_records = metadata["records"]
    pending: list[str] = []
    unreleased: list[str] = []
    conflicts: list[str] = []
    validation_errors: list[str] = []
    changes: list[PlannedChange] = []
    removed = sorted(set(state_records) - set(bundle.records))
    certificate_owners: dict[str, tuple[str, str]] = {}

    for record_id in sorted(bundle.records):
        record = bundle.records[record_id]
        editorial = metadata_records.get(record_id)
        if active_release.protected(authority, record_id, (editorial or {}).get("entry_id")):
            unreleased.append(record_id)
            continue
        if editorial is None:
            pending.append(record_id)
            continue
        if not editorial["publish"]:
            unreleased.append(record_id)
            continue

        entry_rel = _entry_path(editorial)
        try:
            entry_path = bugbank_root / _safe_relative(entry_rel, context=record_id)
        except BundleError as exc:
            validation_errors.append(str(exc))
            continue
        if entry_path.stem != editorial["entry_id"]:
            validation_errors.append(
                f"{record_id}: entry path filename does not match entry_id"
            )
            continue

        management = editorial["management"]
        old = state_records.get(record_id)
        if management == "preserve":
            if old is None:
                conflicts.append(f"{record_id}: preserved entry has no adopted sync state")
                continue
            if not entry_path.is_file():
                conflicts.append(f"{record_id}: preserved entry is missing")
            for formalized in editorial.get("formalized") or []:
                try:
                    local = bugbank_root / _safe_relative(
                        formalized, context=f"{record_id} formalized"
                    )
                except BundleError as exc:
                    validation_errors.append(str(exc))
                    continue
                if formalized.startswith("lean/") and not local.exists():
                    conflicts.append(f"{record_id}: formalized path is missing: {formalized}")
            if old.get("record_sha256") != record["record_sha256"]:
                conflicts.append(
                    f"{record_id}: preserved entry requires manual upstream reconciliation"
                )
            continue

        certificate_destination = _certificate_destination(record, editorial)
        if certificate_destination:
            try:
                _safe_relative(certificate_destination, context=f"{record_id} certificate")
            except BundleError as exc:
                validation_errors.append(str(exc))
                continue
            certificate_sha = record["certificate"]["sha256"]
            owner = certificate_owners.get(certificate_destination)
            if owner and owner[1] != certificate_sha:
                conflicts.append(
                    f"{record_id}: certificate destination {certificate_destination} "
                    f"collides with {owner[0]}"
                )
                continue
            certificate_owners[certificate_destination] = (record_id, certificate_sha)

        rendered = render_entry(
            record,
            editorial,
            bundle.manifest["source_commit"],
            certificate_destination,
        )
        if old is None:
            if entry_path.exists():
                conflicts.append(f"{record_id}: unmanaged entry path already exists")
                continue
            if certificate_destination and (bugbank_root / certificate_destination).exists():
                conflicts.append(f"{record_id}: unmanaged certificate destination already exists")
                continue
            changes.append(PlannedChange(
                record_id=record_id,
                action="create",
                entry_path=entry_rel,
                entry_text=rendered,
                certificate_bundle_path=(
                    record["certificate"]["bundle_path"] if record["certificate"] else None
                ),
                certificate_destination=certificate_destination,
            ))
            continue

        if old.get("management") != "generated":
            conflicts.append(f"{record_id}: state ownership differs from metadata")
            continue
        if not entry_path.is_file():
            conflicts.append(f"{record_id}: managed entry is missing")
            continue
        if _sha256_file(entry_path) != old.get("entry_sha256"):
            conflicts.append(f"{record_id}: local entry changed since last sync")
            continue
        old_certificate = old.get("certificate_destination")
        if old_certificate and not certificate_destination:
            conflicts.append(
                f"{record_id}: certificate removal requires manual reconciliation"
            )
            continue
        if certificate_destination:
            local_cert = bugbank_root / certificate_destination
            if old_certificate:
                if old_certificate != certificate_destination:
                    conflicts.append(
                        f"{record_id}: certificate destination changed; reconcile manually"
                    )
                    continue
                if not local_cert.is_file():
                    conflicts.append(f"{record_id}: managed certificate is missing")
                    continue
                if _sha256_file(local_cert) != old.get("certificate_sha256"):
                    conflicts.append(f"{record_id}: local certificate changed since last sync")
                    continue
            elif local_cert.exists():
                conflicts.append(f"{record_id}: unmanaged certificate destination already exists")
                continue
        if old.get("record_sha256") == record["record_sha256"]:
            continue
        changes.append(PlannedChange(
            record_id=record_id,
            action="update",
            entry_path=entry_rel,
            entry_text=rendered,
            certificate_bundle_path=(
                record["certificate"]["bundle_path"] if record["certificate"] else None
            ),
            certificate_destination=certificate_destination,
        ))

    return SyncPlan(
        changes=tuple(changes),
        pending_metadata=tuple(pending),
        unreleased=tuple(unreleased),
        removed=tuple(removed),
        conflicts=tuple(sorted(set(conflicts))),
        errors=tuple(sorted(set(validation_errors))),
    )


def _validate_entry_text(text: str, path: Path) -> None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise SyncError(f"{path}: rendered entry has no frontmatter")
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise SyncError(f"{path}: rendered YAML is invalid: {exc}") from exc
    required = ("id", "title", "type", "domain", "subdomain", "tags",
                "statement", "difficulty", "status")
    for field in required:
        if meta.get(field) in (None, "", []):
            raise SyncError(f"{path}: rendered entry is missing {field}")
    if meta["id"] != path.stem or not SLUG_RE.match(meta["id"]):
        raise SyncError(f"{path}: rendered entry ID/path mismatch")
    if meta["type"] not in ENTRY_TYPES or meta["status"] not in ENTRY_STATUSES:
        raise SyncError(f"{path}: rendered entry enum is invalid")
    if meta["type"] in {"counterexample", "sharpness"} and not meta.get("refutes"):
        raise SyncError(f"{path}: rendered counterexample has no refutes field")
    if not match.group(2).strip():
        raise SyncError(f"{path}: rendered body is empty")


def apply_plan(
    plan: SyncPlan,
    bundle: Bundle,
    metadata: dict,
    state: dict,
    bugbank_root: Path,
) -> dict:
    """Stage and apply a blocker-free plan; return the updated state document."""
    if plan.has_blockers:
        raise SyncError("sync plan has blockers; refusing to write")
    authority = active_release.load(bugbank_root)
    for change in plan.changes:
        if active_release.protected(authority, change.record_id, Path(change.entry_path).stem):
            raise SyncError("source-review authority forbids stale planned write: " + change.record_id)
    new_state = json.loads(json.dumps(state))
    new_state.setdefault("schema_version", STATE_SCHEMA_VERSION)
    new_state.setdefault("records", {})
    if not plan.changes:
        return new_state

    stage = Path(tempfile.mkdtemp(prefix=".qq-sync-stage-", dir=bugbank_root))
    try:
        staged: list[tuple[Path, Path]] = []
        state_updates: dict[str, dict] = {}
        for change in plan.changes:
            record = bundle.records[change.record_id]
            entry_rel = _safe_relative(change.entry_path, context=change.record_id)
            entry_stage = stage / entry_rel
            entry_stage.parent.mkdir(parents=True, exist_ok=True)
            _validate_entry_text(change.entry_text, entry_stage)
            entry_data = change.entry_text.encode("utf-8")
            entry_stage.write_bytes(entry_data)
            staged.append((entry_stage, bugbank_root / entry_rel))

            state_row = {
                "record_sha256": record["record_sha256"],
                "entry_path": change.entry_path,
                "entry_sha256": _sha256_bytes(entry_data),
                "source_commit": bundle.manifest["source_commit"],
                "management": "generated",
            }
            if change.certificate_bundle_path and change.certificate_destination:
                cert_source = bundle.root / _safe_relative(
                    change.certificate_bundle_path,
                    context=f"{change.record_id} bundled certificate",
                )
                cert_rel = _safe_relative(
                    change.certificate_destination,
                    context=f"{change.record_id} certificate destination",
                )
                cert_stage = stage / cert_rel
                cert_stage.parent.mkdir(parents=True, exist_ok=True)
                cert_stage.write_bytes(cert_source.read_bytes())
                staged.append((cert_stage, bugbank_root / cert_rel))
                state_row["certificate_destination"] = change.certificate_destination
                state_row["certificate_sha256"] = record["certificate"]["sha256"]
            state_updates[change.record_id] = state_row

        # Nothing in the repository is touched until every staged entry has
        # passed the schema checks above and every certificate has been read.
        for source, destination in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)
        new_state["records"].update(state_updates)
        return new_state
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def _load_dossier_module(source_root: Path) -> ModuleType:
    script_dir = (
        source_root
        / "qedbench_certificate_availability_triage"
        / "scripts"
    )
    module_path = script_dir / "make_dossiers.py"
    if not module_path.exists():
        raise RuntimeError(f"{source_root} is not a research-source checkout")

    # make_dossiers.py supports direct execution by importing
    # integration_common from its own directory.
    sys.path.insert(0, str(script_dir))
    try:
        spec = importlib.util.spec_from_file_location("qq_make_dossiers", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(script_dir))


def load_source_dossiers(source_root: Path) -> list[dict]:
    module = _load_dossier_module(source_root.resolve())
    dossiers = module.build_dossiers()
    module.assert_final_dossier_ready(dossiers)
    return dossiers


def imported_source_ids(db_path: Path) -> set[str]:
    placeholders = ",".join("?" for _ in QQ_SOURCE_BOOKS)
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            f"SELECT source_item FROM entries "
            f"WHERE source_book IN ({placeholders}) AND source_item IS NOT NULL",
            QQ_SOURCE_BOOKS,
        )
    # The four QEDBugBank family summaries are deliberately not dossier IDs.
    return {row[0] for row in rows if not row[0].startswith("family ")
            and not row[0].startswith("refused equivalence:")}


def coverage_command(source_root: Path, db_path: Path) -> int:
    dossiers = load_source_dossiers(source_root)
    source_ids = {row["record_id"] for row in dossiers}
    result = compare_coverage(
        source_ids=source_ids,
        imported_ids=imported_source_ids(db_path),
    )
    print(
        f"source={len(source_ids)} imported={len(source_ids) - len(result.missing)} "
        f"missing={len(result.missing)} removed={len(result.removed)}"
    )
    for record_id in result.missing:
        print(f"MISSING {record_id}")
    for record_id in result.removed:
        print(f"REMOVED {record_id}")
    return 0 if result.in_sync else 1


def source_commit(source_root: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    if proc.returncode or not proc.stdout.strip():
        raise SyncError(f"cannot resolve source commit: {proc.stderr.strip()}")
    return proc.stdout.strip()


def export_source_checkout(source_root: Path, out_dir: Path, commit: str | None = None) -> Bundle:
    dossiers = load_source_dossiers(source_root)
    return export_bundle(dossiers, source_root, commit or source_commit(source_root), out_dir)


def verify_zero_import_changes(plan: SyncPlan, bundle: Bundle, lean: str = "lean") -> None:
    """Recompile changed self-contained certificates when explicitly requested."""
    failures = []
    for change in plan.changes:
        record = bundle.records[change.record_id]
        cert = record.get("certificate")
        if not cert or cert.get("imports"):
            continue
        proc = subprocess.run(
            [lean, str(bundle.root / cert["bundle_path"])],
            capture_output=True,
            text=True,
        )
        if proc.returncode:
            failures.append(
                f"{change.record_id}: Lean exit {proc.returncode}: "
                f"{(proc.stderr or proc.stdout).strip()}"
            )
    if failures:
        raise SyncError("zero-import certificate verification failed:\n" + "\n".join(failures))


def _write_report(path: Path | None, report: dict) -> None:
    if path:
        _atomic_write(path, json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _print_plan(plan: SyncPlan, *, source_count: int) -> None:
    print(
        f"source={source_count} changes={len(plan.changes)} "
        f"pending_metadata={len(plan.pending_metadata)} "
        f"unreleased={len(plan.unreleased)} removed={len(plan.removed)} "
        f"conflicts={len(plan.conflicts)} errors={len(plan.errors)}"
    )
    for change in plan.changes:
        print(f"{change.action.upper()} {change.record_id} -> {change.entry_path}")
    for label, values in (
        ("PENDING_METADATA", plan.pending_metadata),
        ("UNRELEASED", plan.unreleased),
        ("REMOVED", plan.removed),
        ("CONFLICT", plan.conflicts),
        ("ERROR", plan.errors),
    ):
        for value in values:
            print(f"{label} {value}")


def _load_bridge_inputs(metadata_path: Path, state_path: Path) -> tuple[dict, dict]:
    return load_json(metadata_path), load_json(state_path)


def _run_sync(args, *, apply: bool) -> int:
    metadata, state = _load_bridge_inputs(args.metadata, args.state)
    with tempfile.TemporaryDirectory(prefix="qq-bundle-") as tmp:
        bundle = export_source_checkout(args.source, Path(tmp), args.source_commit)
        plan = plan_sync(bundle, metadata, state, args.root)
        report = {
            "bundle": bundle.manifest,
            "plan": plan.report(),
            "pending_records": {
                record_id: {
                    "corpus": bundle.records[record_id]["corpus"],
                    "flaw": bundle.records[record_id]["flaw"],
                    "witness": bundle.records[record_id]["witness"],
                    "lean_compiled": bundle.records[record_id]["lean_compiled"],
                }
                for record_id in plan.pending_metadata
            },
        }
        _write_report(args.report, report)
        _print_plan(plan, source_count=len(bundle.records))
        if plan.has_blockers:
            return 2
        if not apply:
            return 1 if plan.changes else 0
        if args.verify_zero_import:
            verify_zero_import_changes(plan, bundle, args.lean)
        new_state = apply_plan(plan, bundle, metadata, state, args.root)
        _atomic_write(args.state, json.dumps(new_state, indent=2, sort_keys=True,
                                             ensure_ascii=False).encode("utf-8") + b"\n")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    coverage = sub.add_parser("coverage", help="compare source dossier IDs with BugBank")
    coverage.add_argument("--source", type=Path, required=True)
    coverage.add_argument("--db", type=Path, default=active_release.database_path(ROOT))

    export = sub.add_parser("export", help="write a versioned source bundle")
    export.add_argument("--source", type=Path, required=True)
    export.add_argument("--out", type=Path, required=True)
    export.add_argument("--source-commit")

    bootstrap = sub.add_parser(
        "bootstrap", help="capture current editorial metadata and adopted sync state"
    )
    bootstrap.add_argument("--source", type=Path, required=True)
    bootstrap.add_argument("--root", type=Path, default=ROOT)
    bootstrap.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    bootstrap.add_argument("--state", type=Path, default=DEFAULT_STATE)
    bootstrap.add_argument("--source-commit")

    for name in ("check", "apply"):
        command = sub.add_parser(name, help=f"{name} the incremental QQ sync")
        command.add_argument("--source", type=Path, required=True)
        command.add_argument("--root", type=Path, default=ROOT)
        command.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
        command.add_argument("--state", type=Path, default=DEFAULT_STATE)
        command.add_argument("--source-commit")
        command.add_argument("--report", type=Path)
        command.add_argument("--verify-zero-import", action="store_true")
        command.add_argument("--lean", default="lean")
    args = parser.parse_args()

    if args.command == "coverage":
        return coverage_command(args.source, args.db)
    if args.command == "export":
        bundle = export_source_checkout(args.source, args.out, args.source_commit)
        print(
            f"wrote bundle schema={bundle.manifest['schema_version']} "
            f"records={len(bundle.records)} certificates="
            f"{bundle.manifest['certificate_count']} commit="
            f"{bundle.manifest['source_commit']} -> {args.out}"
        )
        return 0
    if args.command == "bootstrap":
        with tempfile.TemporaryDirectory(prefix="qq-bundle-") as tmp:
            bundle = export_source_checkout(args.source, Path(tmp), args.source_commit)
            metadata, state = bootstrap_crosswalk(args.root, bundle)
        _atomic_write(args.metadata, json.dumps(metadata, indent=2, sort_keys=True,
                                                ensure_ascii=False).encode("utf-8") + b"\n")
        _atomic_write(args.state, json.dumps(state, indent=2, sort_keys=True,
                                             ensure_ascii=False).encode("utf-8") + b"\n")
        print(
            f"bootstrapped {len(metadata['records'])} records -> "
            f"{args.metadata}, {args.state}"
        )
        return 0
    if args.command == "check":
        return _run_sync(args, apply=False)
    if args.command == "apply":
        return _run_sync(args, apply=True)
    raise AssertionError(args.command)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BundleError, SyncError, RuntimeError) as exc:
        print(f"QQ SYNC ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
