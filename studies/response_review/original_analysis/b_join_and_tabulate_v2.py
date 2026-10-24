#!/usr/bin/env python3
"""Experiment B (v2: LOG parser accepts both reader log formats; otherwise byte-identical to v1): lock the readings, join the private packet key and the frozen outcome rule, and produce the pre-specified tables.

usage: b_join_and_tabulate.py <utc_from_date_u> [--allow-partial]
Refuses unless every packet has two locked readings (LOG hash equal to the file hash), unless --allow-partial (then reports coverage and
tabulates only fully read packets, labelled PARTIAL). Never modifies a reading. Public output: B_RESULTS_v1.json (no reader free text beyond
the J-values and class labels; justifications are copied into B_READINGS_PRIVATE.json)."""
import re, hashlib, importlib.util, json, os, sys, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sha = lambda b: hashlib.sha256(b).hexdigest()
def need(c, m):
    if not c: raise SystemExit("REFUSED: " + m)
ts = sys.argv[1]; partial = "--allow-partial" in sys.argv
priv = json.load(open(HERE / "private/B_SAMPLE_FREEZE_PRIVATE.json")); pairs = {p["packet_id"]: p for p in priv["pairs"]}
plan = json.load(open(HERE / "READER_ASSIGNMENT_PLAN.json"))["readers"]
commit = json.load(open(HERE / "B_COMMITMENT.json"))
# frozen outcome rule
rep_path = commit["inputs"]["accepted_report"]["path"]; report = json.loads(open(ROOT / rep_path, "rb").read())
need(sha(open(ROOT / rep_path, "rb").read()) == commit["inputs"]["accepted_report"]["sha256"], "report drift")
ref = json.load(open(ROOT / commit["inputs"]["reference_items"]["path"])); items = {i["record_id"]: i for i in ref["items"]}
RUNTIME = ROOT / "research/resource285_quality_check_20260923/benchmark_reruns/runtime_v1/resolve_and_score_corrected.py"
spec = importlib.util.spec_from_file_location("frozen_rt", RUNTIME); rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
runtimes = {ck: rt.frozen_runtime({"frozen_design_files": [rb["common"], rb["score"]]}, lambda d: (ROOT / d["path"]).read_bytes())[0] for ck, rb in report["runtime_bindings"].items() if ck in commit["configurations"]}
# readings: lock check
readings = collections.defaultdict(dict); locks = {}
for reader, v in plan.items():
    logp = HERE / "readings" / reader / "LOG.txt"; log = {}
    if logp.exists():
        for line in logp.read_text().splitlines():
            parts = line.split()
            # v2: accept both LOG formats used by the readers ("<ISO> <pid> <sha>" and "<date -u default, 6 tokens> <pid> <sha>"):
            # the packet id and hash are always the last two tokens.
            if len(parts) >= 3 and re.fullmatch(r"P\d\d", parts[-2]) and re.fullmatch(r"[0-9a-f]{64}", parts[-1]): log[parts[-2]] = parts[-1]
    for role, pids in (("first", v["first_reader_packets"]), ("second", v["second_reader_packets"])):
        for pid in pids:
            fp = HERE / "readings" / reader / f"{pid}.json"
            if not fp.exists(): continue
            raw = fp.read_bytes(); d = json.loads(raw); h = sha(raw)
            locked = log.get(pid) == h
            readings[pid][role] = {"reader": reader, "locked": locked, "sha256": h, "data": d}
            locks[(reader, pid)] = locked
complete = [pid for pid in pairs if "first" in readings[pid] and "second" in readings[pid] and readings[pid]["first"]["locked"] and readings[pid]["second"]["locked"]]
missing = [pid for pid in pairs if pid not in complete]
need(partial or not missing, "not all packets have two locked readings; missing/unlocked: %s" % missing[:10])
def cls(j3):
    v = (j3 or {}).get("value", "")
    if v in ("VERIFIED_VALID_KERNEL", "VERIFIED_VALID_EXACT", "ANALYTIC_VALID"): return "VALID"
    if v == "INVALID": return "INVALID"
    if v in ("UNRESOLVED", "NOT_APPLICABLE", ""): return "UNRESOLVED_OR_INSUFFICIENT"
    return "OTHER:" + v
rows = []; private_rows = []
for pid in complete:
    p = pairs[pid]; rec = json.load(open(ROOT / p["record"]["path"])); it = items[p["record_id"]]
    o = runtimes[p["configuration"]].outcome(it, rec); hit1 = int(o["hit1"])
    if p["attempt_class"] != "VALID_ANSWER" and not rec.get("candidates"): evidence_class = "MISSING_TECHNICAL"
    r1 = readings[pid]["first"]["data"]; r2 = readings[pid]["second"]["data"]
    j = lambda d, k: (d.get(k) or {}).get("value")
    row = {"packet_id": pid, "record_id": p["record_id"], "configuration": p["configuration"], "cluster": p["cluster"], "group": p["group"], "pilot": p["pilot"],
           "first_choice_label": p["first_choice_label"], "gold": it["gold"], "hit1_frozen_rule": hit1, "hit3_frozen_rule": int(o["hit3"]), "attempt_class": p["attempt_class"],
           "reader1": {"reader": readings[pid]["first"]["reader"], "J1": j(r1, "J1_line_asserts_challenged_proposition"), "J2": j(r1, "J2_evidence_specified"), "J3": j(r1, "J3_evidence_check"), "J4": j(r1, "J4_consequence_overreach"), "confidence": r1.get("confidence"), "minutes": r1.get("minutes"), "tooling_failure": (r1.get("J3_evidence_check") or {}).get("tooling_failure"), "lean_attempts": (r1.get("J3_evidence_check") or {}).get("lean_attempts")},
           "reader2": {"reader": readings[pid]["second"]["reader"], "J1": j(r2, "J1_line_asserts_challenged_proposition"), "J2": j(r2, "J2_evidence_specified"), "J3": j(r2, "J3_evidence_check"), "J4": j(r2, "J4_consequence_overreach"), "confidence": r2.get("confidence"), "minutes": r2.get("minutes"), "tooling_failure": (r2.get("J3_evidence_check") or {}).get("tooling_failure"), "lean_attempts": (r2.get("J3_evidence_check") or {}).get("lean_attempts")},
           "primary_evidence_class": cls(r1.get("J3_evidence_check")), "readers_agree_J3_class": cls(r1.get("J3_evidence_check")) == cls(r2.get("J3_evidence_check")), "readers_agree_J3_exact": j(r1, "J3_evidence_check") == j(r2, "J3_evidence_check")}
    rows.append(row); private_rows.append({"packet_id": pid, "reader1_full": r1, "reader2_full": r2})
def table(sub):
    t = {"hit1": collections.Counter(), "miss": collections.Counter()}
    for r in sub: t["hit1" if r["hit1_frozen_rule"] else "miss"][r["primary_evidence_class"]] += 1
    return {k: dict(v) for k, v in t.items()}
by_cfg = {ck: [r for r in rows if r["configuration"] == ck] for ck in commit["configurations"]}
results = {"schema": "copeer-B-results/v1", "utc_from_date_u": ts, "status": "COMPLETE" if not missing else "PARTIAL", "packets_tabulated": len(rows), "packets_missing_or_unlocked": missing,
 "protocol_sha256": sha(open(HERE / "B_PROTOCOL_v1.md", "rb").read()), "commitment_sha256": sha(open(HERE / "B_COMMITMENT.json", "rb").read()), "freeze_sha256": sha(open(HERE / "B_SAMPLE_FREEZE.json", "rb").read()),
 "primary_table_hit1_by_evidence_class_first_reader": {ck: table(v) for ck, v in by_cfg.items()},
 "secondary_reader_agreement": {ck: {"J3_class_agree": sum(r["readers_agree_J3_class"] for r in v), "J3_exact_agree": sum(r["readers_agree_J3_exact"] for r in v), "n": len(v)} for ck, v in by_cfg.items()},
 "J3_exact_values_first_reader": {ck: dict(collections.Counter(r["reader1"]["J3"] for r in v)) for ck, v in by_cfg.items()},
 "J1_first_reader": {ck: dict(collections.Counter(r["reader1"]["J1"] for r in v)) for ck, v in by_cfg.items()},
 "J2_first_reader": {ck: dict(collections.Counter(r["reader1"]["J2"] for r in v)) for ck, v in by_cfg.items()},
 "J4_first_reader": {ck: dict(collections.Counter(r["reader1"]["J4"] for r in v)) for ck, v in by_cfg.items()},
 "valid_objections_among_misses_first_reader": {ck: sum(1 for r in v if not r["hit1_frozen_rule"] and r["primary_evidence_class"] == "VALID") for ck, v in by_cfg.items()},
 "hits_without_valid_evidence_first_reader": {ck: sum(1 for r in v if r["hit1_frozen_rule"] and r["primary_evidence_class"] != "VALID") for ck, v in by_cfg.items()},
 "tooling_failures": sum(1 for r in rows for k in ("reader1", "reader2") if r[k]["tooling_failure"]), "reader_minutes_total": sum((r[k]["minutes"] or 0) for r in rows for k in ("reader1", "reader2") if isinstance(r[k]["minutes"], (int, float))),
 "records": rows,
 "interpretation": ["Descriptive audit of two selected strong configurations on 24 randomly drawn primary records; not a ranking of model families.",
                    "hit1 is the frozen scorer's rule applied to the chosen record; gold scores are unchanged by this analysis.",
                    "VALID pools kernel, exact and analytic classes; the exact J3 values are reported separately because analytic judgments are model-assisted.",
                    "Valid objections among misses are reported here only; they are never folded into the headline localization accuracy.",
                    "Reader disagreements are preserved; adjudication, if any, is a separate later step reported beside these first readings."]}
out = HERE / "B_RESULTS_v1.json"; need(not out.exists() or partial, "B_RESULTS_v1.json exists"); out.write_bytes((json.dumps(results, indent=1) + "\n").encode())
(HERE / "private" / "B_READINGS_PRIVATE.json").write_bytes((json.dumps(private_rows, indent=1) + "\n").encode())
print(json.dumps({k: results[k] for k in ("status", "packets_tabulated", "primary_table_hit1_by_evidence_class_first_reader", "secondary_reader_agreement", "valid_objections_among_misses_first_reader", "hits_without_valid_evidence_first_reader")}, indent=1))
