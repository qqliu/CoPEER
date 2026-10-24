#!/usr/bin/env python3
"""Verify the supporting formal sources and saved compiler evidence; no Lean runs."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
data = json.loads((root / "index.json").read_text())
for row in data["files"]:
    assert hashlib.sha256((root / row["file"]).read_bytes()).hexdigest() == row["sha256"], row["file"]
for row in data["entries"]:
    receipt = json.loads((root / row["receipt"]).read_text())
    assert receipt["selected_source_sha256"] == row["sha256"]
    for build in receipt["saved_builds"]:
        text = (root / build["log"]).read_text()
        for name in row["selected_declarations"]:
            assert "'" + name + "'" in text, (row["source"], name)
print(json.dumps({"sources": len(data["entries"]), "saved_build_logs": sum(
    len(json.loads((root / r["receipt"]).read_text())["saved_builds"]) for r in data["entries"]),
    "hashes_match": True, "new_lean_runs": 0}, indent=2))
