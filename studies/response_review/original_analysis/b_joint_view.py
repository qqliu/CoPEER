#!/usr/bin/env python3
"""Experiment B: descriptive JOINT view requested by study coordinator (secondary joint analysis): per configuration, cross-tabulate attempt class, frozen hit1,
first-choice label membership in gold, and the first reader's J1/J2/J3/J4 together; list J3-class disagreements and flagged agreeing cases.
Reads B_RESULTS_v1.json only (no re-scoring, no solver replay). usage: b_joint_view.py <utc_from_date_u>"""
import json, sys, collections, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
ts = sys.argv[1]
res = json.load(open(HERE / "B_RESULTS_v1.json"))
rows = res["records"]
def cls(v):
    if v in ("VERIFIED_VALID_KERNEL", "VERIFIED_VALID_EXACT", "ANALYTIC_VALID"): return "VALID"
    if v == "INVALID": return "INVALID"
    return "UNRESOLVED_OR_INSUFFICIENT"
joint = collections.defaultdict(lambda: collections.Counter()); per_packet = []
disagree = []; flagged = []
for r in rows:
    r1, r2 = r["reader1"], r["reader2"]
    in_gold = r["first_choice_label"] in (r["gold"] if isinstance(r["gold"], list) else [r["gold"]])
    key = (r["attempt_class"], "hit1" if r["hit1_frozen_rule"] else "miss", "label_in_gold" if in_gold else "label_not_in_gold",
           f"J1={r1['J1']}", f"J2={r1['J2']}", f"J3class={cls(r1['J3'])}", f"J4={r1['J4']}")
    joint[r["configuration"]][" | ".join(key)] += 1
    per_packet.append({"packet_id": r["packet_id"], "configuration": r["configuration"], "attempt_class": r["attempt_class"], "hit1": r["hit1_frozen_rule"],
                       "first_choice_label": r["first_choice_label"], "label_in_gold": in_gold,
                       "reader1": {k: r1[k] for k in ("reader", "J1", "J2", "J3", "J4", "confidence")}, "reader2": {k: r2[k] for k in ("reader", "J1", "J2", "J3", "J4", "confidence")},
                       "J3_class_agree": cls(r1["J3"]) == cls(r2["J3"]), "J3_exact_agree": r1["J3"] == r2["J3"], "J1_agree": r1["J1"] == r2["J1"]})
    if cls(r1["J3"]) != cls(r2["J3"]): disagree.append(r["packet_id"])
    if cls(r1["J3"]) == "VALID" and (r1["J1"] != "YES" or r2["J1"] != "YES" or r["attempt_class"] != "VALID_ANSWER"):
        flagged.append({"packet_id": r["packet_id"], "reason": "J3 VALID but J1 not YES for a reader or protocol-invalid attempt",
                        "J1": [r1["J1"], r2["J1"]], "attempt_class": r["attempt_class"]})
strict = {}
for cfg in joint:
    rs = [p for p in per_packet if p["configuration"] == cfg]
    strict[cfg] = {
        "misses_total": sum(1 for p in rs if not p["hit1"]),
        "misses_J3_valid_first_reader": sum(1 for p in rs if not p["hit1"] and cls(p["reader1"]["J3"]) == "VALID"),
        "misses_J3_valid_AND_J1_YES_both_readers_AND_valid_attempt": sum(1 for p in rs if not p["hit1"] and cls(p["reader1"]["J3"]) == "VALID" and p["reader1"]["J1"] == "YES" and p["reader2"]["J1"] == "YES" and p["attempt_class"] == "VALID_ANSWER"),
        "hits_total": sum(1 for p in rs if p["hit1"]),
        "hits_J3_not_valid_first_reader": sum(1 for p in rs if p["hit1"] and cls(p["reader1"]["J3"]) != "VALID"),
        "protocol_invalid_attempts": sum(1 for p in rs if p["attempt_class"] != "VALID_ANSWER"),
    }
out = {"schema": "copeer-B-joint-view/v1", "utc_from_date_u": ts, "source": "B_RESULTS_v1.json", "source_sha256": hashlib.sha256((HERE / "B_RESULTS_v1.json").read_bytes()).hexdigest(),
       "note": "Descriptive secondary view (study coordinator 1577/1578). The prespecified table remains the first-reader J3 class by frozen hit1. J3 VALID means evidence assessed valid in the saved response; it is not by itself a source-applicable alternative objection (J1 and attempt class are shown alongside).",
       "joint_counts_first_reader": {cfg: dict(sorted(c.items())) for cfg, c in joint.items()}, "stricter_descriptive_view": strict,
       "J3_class_disagreements": disagree, "flagged_agreeing_cases": flagged, "per_packet": per_packet}
(HERE / "B_JOINT_VIEW_v1.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"disagreements": disagree, "flagged": [f["packet_id"] for f in flagged], "strict": strict}, indent=1))
