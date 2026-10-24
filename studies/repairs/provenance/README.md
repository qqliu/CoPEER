# Saved repair provenance

`native_usage.json` retains numeric native and per-request usage evidence for the 96 selected first attempts, with original source hashes. Provider request identifiers are hashed; model message bodies and service logs are excluded. `native_usage_extraction_receipt.json` records the extraction rules and source pins.

`recovery_ledger.json` links each of the 288 reported cells to its selected record and saved predecessor records. Original runtime classes, environmental cause markers, record/proof hashes and numeric attempt fields remain visible. The paper's token totals count only selected first attempts; this ledger preserves predecessor evidence separately.

`support_versions.json` identifies the 20 selected grades stamped with the older support source and the 226 stamped with the later source. The older file is preserved in `checker_reference/repair_common.py.before_r7_b13620d2`; only its workstation-specific Node path is anonymized. Saved receipt hashes and grade stamps are unchanged.

The kernel checker and the private-helper audit are separate stages. Replaying saved aggregates uses the exported audit receipts for the three composed FAIL-to-PASS corrections. Running an original checker alone preserves its private-name-query failure until the corresponding helper audit is applied. The original full-roster audit driver is retained for inspection, not represented as a portable fresh-audit command.
