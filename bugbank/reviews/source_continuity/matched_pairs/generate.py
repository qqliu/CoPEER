#!/usr/bin/env python3
"""Recheck frozen artifact bindings and package three existing objection pairs.

No Lean execution, model calls, network access, or semantic adjudication.
Run from any directory; paths in frozen inputs are repository-relative.
"""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = HERE / "FROZEN_INPUTS.json"
IDS = [
    "Algorithms_27__sol3", "SE_cs_81391__q", "SE_math_4219732__q",
    "arxiv_1304.1796v2__source_enriched_codex", "mse_1794123__ans1794617",
    "mse_2605396__ans2605536", "mse_605342__ans609345",
    "mse_811862__ans811879", "proofwiki_69483", "reddit_askmath_1kehuzl",
    "reddit_askmath_k33fyn", "reddit_askmath_pe1euu", "reddit_learnmath_14s0k9c",
    "reddit_learnmath_egpgy9", "reddit_learnmath_t6wb5n", "reddit_mathematics_i3ob36",
]
STRICT = ["SE_cs_81391__q", "SE_math_4219732__q", "mse_811862__ans811879"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def resolve(path):
    p = Path(path)
    if not p.is_absolute():
        return ROOT / p
    if p.exists():
        return p
    # Receipts preserve their original temporary-worktree command. Relocate
    # that recorded repository path only when the retained bytes hash-match.
    marker = "/qedbench_certificate_availability_triage/"
    if marker in str(p):
        return ROOT / ("qedbench_certificate_availability_triage/" + str(p).split(marker, 1)[1])
    return p


def verify(path, expected):
    p = resolve(path)
    assert p.is_file(), f"Missing pinned artifact: {path}"
    actual = digest(p.read_bytes())
    assert actual == expected, f"Changed pinned artifact: {path}"
    return p


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def copy_pinned(source, expected, destination):
    p = verify(source, expected)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(p.read_bytes())
    return {"path": str(destination.relative_to(HERE)), "sha256": expected,
            "bytes": destination.stat().st_size, "source_path": str(source)}


def header(text, short_name):
    start = re.search(r"(?m)^(?:theorem|lemma)\s+" + re.escape(short_name) + r"\b", text)
    assert start, f"Declaration missing: {short_name}"
    end = text.index(":=", start.start()) + 2
    return {"text": text[start.start():end],
            "line_start": text.count("\n", 0, start.start()) + 1,
            "scope": "Exact declaration header through :=; proof is in the complete compiled source."}


def receipt_bundle(path, expected_hash, expected_source_hash, destination):
    p = verify(path, expected_hash)
    d = json.loads(p.read_text())
    assert d["status"] == "PASS" and d["exit_code"] == 0
    assert d["source_sha256"] == expected_source_hash
    assert d["axiom_audit"]["exit_code"] == 0
    assert d["trust_tier"] == "KERNEL_ONLY"
    receipt = copy_pinned(path, expected_hash, destination / "RECEIPT.json")
    copied = []
    for role, source, sha, filename in [
        ("compiled_source", d["snapshot"], d["snapshot_sha256"], "Certificate.lean"),
        ("compile_log", d["log"], d["log_sha256"], "compile.log"),
        ("axiom_log", d["axiom_audit"]["log"], d["axiom_audit"]["log_sha256"], "axioms.log"),
    ]:
        copied.append({"role": role, **copy_pinned(source, sha, destination / filename)})
    instrumented = d["axiom_audit"]["command"][-1]
    retained_instrumented = verify(instrumented, d["instrumented_sha256"])
    pinned = [{"role": "instrumented_source", "path": instrumented,
               "retained_path": str(retained_instrumented.relative_to(ROOT)),
               "sha256": d["instrumented_sha256"]}]
    for name in ["environment.json", "dependencies.json"]:
        dep = p.parent.parent / name
        if dep.is_file():
            pinned.append({"role": name, "path": str(dep.relative_to(ROOT)),
                           "sha256": digest(dep.read_bytes())})
    return {"receipt": receipt, "checked_at_utc": d.get("checked_at_utc"),
            "command": d["command"], "status": d["status"], "exit_code": d["exit_code"],
            "trust_tier": d["trust_tier"], "copied": copied,
            "additional_pinned_evidence": pinned}, d


def main():
    data = json.loads(FROZEN.read_text())
    assert [r["record_id"] for r in data["rows"]] == IDS
    ledger_path = verify(data["ledger"]["path"], data["ledger"]["sha256"])
    ledger = json.loads(ledger_path.read_text())
    assert [r["record_id"] for r in ledger if r["release_status"] == "RETAINED"
            and r["witness_action"] == "REPLACED_INVALID"] == IDS
    for row in data["rows"]:
        verify(row["current_packet"]["path"], row["current_packet"]["sha256"])
        verify(row["source_packet"]["path"], row["source_packet"]["expected_sha256"])
        verify(row["current_lean"]["path"], row["current_lean"]["expected_sha256"])
        packet = json.loads(resolve(row["current_packet"]["path"]).read_text())
        for field, same in row["same_fields"].items():
            a = packet["historical_source_fields"].get(field)
            b = packet["current_fields"].get(field)
            assert (a == b) == same
            for version, value in [("historical", a), ("current", b)]:
                assert digest(str(value or "").encode()) == row["field_hashes"][field][version]
        for receipt in row["old_authenticated_receipts"]:
            verify(receipt["receipt"]["path"], receipt["receipt"]["sha256"])
            for artifact in receipt["artifacts"]:
                verify(artifact["path"], artifact["expected_sha256"])
        verify(row["current_receipt"]["path"], row["current_receipt"]["sha256"])
        for artifact in row["current_log_authentication"]:
            verify(artifact["path"], artifact["expected_sha256"])
    assert sum(r["old_compile_bound"] for r in data["rows"]) == 4
    assert sum(r["current_compile_bound"] for r in data["rows"]) == 16
    assert [r["record_id"] for r in data["rows"]
            if r["strict_same_quote_both_certificates_candidate"]] == STRICT

    packages = []
    for row in data["rows"]:
        if row["record_id"] not in STRICT:
            continue
        rid = row["record_id"]
        directory = HERE / "pairs" / rid
        directory.mkdir(parents=True, exist_ok=True)
        packet = json.loads(resolve(row["current_packet"]["path"]).read_text())
        chosen_old = row["old_authenticated_receipts"][0]
        old, old_d = receipt_bundle(chosen_old["receipt"]["path"],
                                    chosen_old["receipt"]["sha256"],
                                    row["historical_lean_sha256"], directory / "old")
        current, current_d = receipt_bundle(row["current_receipt"]["path"],
                                            row["current_receipt"]["sha256"],
                                            row["current_lean"]["expected_sha256"], directory / "current")
        old_source = (directory / "old/Certificate.lean").read_text()
        current_source = (directory / "current/Certificate.lean").read_text()
        tex = resolve(row["source_packet"]["path"]).read_text()
        excerpt = re.findall(r"\\begin\{Vlean\}\n(.*?)\\end\{Vlean\}", tex, re.S)[0].strip()
        old_short = re.search(r"\btheorem\s+(\S+)", excerpt).group(1)
        old_names = [e["name"] for e in old_d["axiom_events"]
                     if e.get("kind") == "theorem" and e["name"].split(".")[-1] == old_short]
        assert len(old_names) == 1
        old_decl = {"name": old_names[0], **header(old_source, old_short)}
        assert old_decl["text"].strip() == excerpt
        new_decls = []
        for theorem in row["current_build_record"]["selected_theorems"]:
            name = theorem["name"]
            assert any(e.get("name") == name for e in current_d["axiom_events"])
            new_decls.append({"name": name, **header(current_source, name.split(".")[-1]),
                              "recorded_kernel_type": theorem["audit"]["type"]})
        evidence = {
            "record_id": rid, "main_exhibit_candidate": rid == STRICT[0],
            "selection_scope": "Replacement-defined retrospective selected sample; not an error-rate or repair-yield estimate.",
            "binding_scope": "The stored problem, source_context and claim_quote text is identical across this pair. This is not a fresh comparison against the live external source or an independent semantic adjudication.",
            "source_url": packet["historical_inventory"].get("link"),
            "source_packet": row["source_packet"],
            "problem": packet["current_fields"]["problem"],
            "unchanged_source_context": packet["current_fields"]["source_context"],
            "unchanged_claim_quote": packet["current_fields"]["claim_quote"],
            "field_hashes": row["field_hashes"],
            "original_witness_raw": row["original_witness"],
            "original_witness_failure_from_existing_audit": row["recorded_original_witness_failure"],
            "replacement_witness_raw": row["current_witness"],
            "audit_provenance": packet["audit_provenance"],
            "semantic_label_scope": row["semantic_labels_provenance"],
            "old_selected_declaration": old_decl,
            "current_selected_declarations": new_decls,
            "old_compilation": old, "current_compilation": current,
        }
        dump(directory / "PAIR.json", evidence)
        md = [f"# {rid}\n", evidence["binding_scope"],
              "\nBoth complete certificate files below are copied byte-for-byte from authenticated successful build snapshots. No new compilation was performed. The semantic conclusions are quoted from the existing audit.\n",
              "## Unchanged source context\n", "```text\n" + evidence["unchanged_source_context"] + "\n```\n",
              "## Unchanged challenged quote\n", "```text\n" + evidence["unchanged_claim_quote"] + "\n```\n",
              "## Original witness (raw recorded text)\n", evidence["original_witness_raw"],
              "\n## Why the existing audit rejected that witness\n", evidence["original_witness_failure_from_existing_audit"],
              "\n## Replacement witness (raw recorded text)\n", evidence["replacement_witness_raw"],
              "\n## Exact selected Lean declarations\n", "Historical: `" + old_decl["name"] + "`\n",
              "```lean\n" + old_decl["text"] + "\n```\n"]
        for decl in new_decls:
            md.extend(["Current: `" + decl["name"] + "`\n", "```lean\n" + decl["text"] + "\n```\n"])
        md.append("Headers end at `:=`; full definitions and proofs appear in the copied files.\n")
        for label, bundle in [("Historical", old), ("Current", current)]:
            sub = "old" if label == "Historical" else "current"
            md.extend([f"\n## {label} authenticated compilation\n",
                       f"[Complete Lean source]({sub}/Certificate.lean), [receipt]({sub}/RECEIPT.json), [compiler log]({sub}/compile.log), [axiom log]({sub}/axioms.log).\n",
                       f"Recorded execution: `{bundle['checked_at_utc']}`. Result: `PASS`, exit `0`, trust tier `KERNEL_ONLY`.\n",
                       f"Receipt SHA-256: `{bundle['receipt']['sha256']}`.\n"])
            for artifact in bundle["copied"]:
                md.append(f"- {artifact['role']}: `{artifact['sha256']}`\n")
        md.append("\nA successful certificate establishes its encoded proposition. The claim that a witness satisfies the source assumptions is the separately recorded audit judgment. These pairs do not establish a randomized treatment effect or independent human validation.\n")
        (directory / "EXHIBIT.md").write_text("\n".join(md))
        packages.append({"record_id": rid, "pair_path": str((directory / "PAIR.json").relative_to(HERE)),
                         "pair_sha256": digest((directory / "PAIR.json").read_bytes()),
                         "exhibit_path": str((directory / "EXHIBIT.md").relative_to(HERE))})
    data["reproduction"] = {"frozen_inputs_sha256": digest(FROZEN.read_bytes()),
                            "generator_sha256": digest(Path(__file__).read_bytes()),
                            "instruction": "python3 astra/final_afternoon_20260920/repair_pair_audit/generate.py",
                            "verification": "All frozen current packet/source/certificate hashes and old/current receipt/log bindings rechecked; no compilation or semantic grading."}
    data["packaged_pairs"] = packages
    bridge_receipt_path = HERE / "SourceContractBridge.RECEIPT.json"
    bridge_receipt = json.loads(bridge_receipt_path.read_text())
    assert bridge_receipt["exit_code"] == 0
    assert bridge_receipt["all_selected_declarations_axiom_free"]
    bridge = verify(bridge_receipt["source_path"], bridge_receipt["source_sha256"])
    log = verify(bridge_receipt["log_path"], bridge_receipt["log_sha256"])
    verify(bridge_receipt["compiler_path"], bridge_receipt["compiler_sha256"])
    prefix = verify(bridge_receipt["unchanged_prefix_path"], bridge_receipt["unchanged_prefix_sha256"])
    assert bridge.read_bytes().startswith(prefix.read_bytes())
    for name in bridge_receipt["selected_declarations"]:
        assert f"'{name}' does not depend on any axioms" in log.read_text()
    data["supplementary_bridge"] = {
        "receipt_path": str(bridge_receipt_path.relative_to(HERE)),
        "receipt_sha256": digest(bridge_receipt_path.read_bytes()),
        "receipt": bridge_receipt,
        "declarations": [{"name": name, **header(bridge.read_text(), name.split(".")[-1])}
                         for name in bridge_receipt["selected_declarations"]],
        "status": "New supplementary lemmas compiled successfully; original and current certificates unchanged.",
    }
    data["limitations"] = [
        "All 16 replacement-defined records remain in the roster; 4 historical compilations bound and 12 unbound within the documented search.",
        "One changed claim quote: Algorithms_27__sol3; excluded only from the strict quote-identical trio, not the 16-record roster.",
        "Three pairs keep the stored source context and claim quote identical and have old/current successful kernel-only build evidence.",
        "Identical stored excerpts are not a new live-source check. Semantic judgments are inherited from the release audit, not newly established human labels.",
        "Retrospective replacement selection cannot estimate repair success or the incidence of source-fidelity failures; no causal pipeline ablation was performed.",
        "Historical prose can contain broader enumeration or universality claims than its selected Lean declaration; raw witness text is preserved without endorsement.",
    ]
    dump(HERE / "RESULTS.json", data)
    print(json.dumps({"summary": data["summary"], "packaged_pairs": STRICT}, indent=2))


if __name__ == "__main__":
    main()
