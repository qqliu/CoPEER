#!/usr/bin/env python3
"""Extract per-assessment token counts for the cost experiment.

The experiment's claim is about TOKENS, so the evidence must come from the API
usage records in each agent's transcript — never from anything a model said
about its own effort.  For every assessment agent we sum, across all its API
calls:

  output_tokens            the dominant, cache-independent cost driver
  input_uncached           input_tokens + cache_creation_input_tokens
  input_cache_read         cache_read_input_tokens (billed ~10x cheaper)

and report per-arm totals, per-record paired differences, and a seeded
bootstrap CI on the refute-vs-verify ratio.  Pairing is by record: every
record ran every arm, so ratios are within-record and corpus mix cancels.

Usage: python3 scripts/cost_experiment_telemetry.py WF_RUN_ID [WF_RUN_ID ...]
(multiple run ids cover resumed runs; an (record, arm) seen twice keeps the
FIRST completed instance and warns, so a resume cannot double-count).
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

WF_BASE = Path.home() / (".claude/projects/-nfs-roberts-scratch-pi-anonymous-user-anonymous-user-"
                         "new-proof-verification/43185ca4-4048-4e34-acf2-b015a0c5b093/"
                         "subagents/workflows")
OUT = Path(__file__).resolve().parent.parent / "runs/cost_experiment"


def agent_usage(transcript: Path):
    out = inp = cread = calls = 0
    for line in open(transcript):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = row.get("message")
        usage = msg.get("usage") if isinstance(msg, dict) else None
        if not usage:
            continue
        calls += 1
        out += usage.get("output_tokens", 0)
        inp += usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
        cread += usage.get("cache_read_input_tokens", 0)
    return {"output": out, "input_uncached": inp, "input_cache_read": cread,
            "api_calls": calls}


def main():
    run_ids = sys.argv[1:]
    if not run_ids:
        raise SystemExit(__doc__)
    rows = {}
    for run_id in run_ids:
        d = WF_BASE / run_id
        journal = d / "journal.jsonl"
        if not journal.exists():
            raise SystemExit(f"no journal for {run_id}")
        started = {}
        for line in open(journal):
            r = json.loads(line)
            if r.get("type") == "started":
                started[r["key"]] = r.get("agentId")
            elif r.get("type") == "result" and isinstance(r.get("result"), dict):
                res = r["result"]
                rid, arm = res.get("record_id"), res.get("arm")
                if not rid or not arm:
                    continue
                agent_id = r.get("agentId") or started.get(r.get("key"))
                t = d / f"agent-{agent_id}.jsonl"
                if not t.exists():
                    print(f"WARN: transcript missing for {rid}/{arm} ({agent_id})")
                    continue
                key = (rid, arm)
                if key in rows:
                    print(f"WARN: duplicate {key}; keeping first")
                    continue
                rows[key] = {"record_id": rid, "arm": arm,
                             "verdict": res.get("verdict"),
                             **agent_usage(t)}
    if not rows:
        raise SystemExit("no completed assessments found")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "telemetry.jsonl", "w") as f:
        for row in rows.values():
            f.write(json.dumps(row) + "\n")

    by_arm = defaultdict(list)
    for row in rows.values():
        by_arm[row["arm"]].append(row)
    print(f"{'arm':18s} {'n':>4s} {'out tok (mean)':>14s} {'out (median)':>12s} "
          f"{'in-uncached':>12s} {'INVALID':>8s}")
    for arm, items in sorted(by_arm.items()):
        outs = sorted(x["output"] for x in items)
        mean = sum(outs) / len(outs)
        med = outs[len(outs) // 2]
        inm = sum(x["input_uncached"] for x in items) / len(items)
        inv = sum(1 for x in items if x["verdict"] == "INVALID")
        print(f"{arm:18s} {len(items):4d} {mean:14.0f} {med:12.0f} {inm:12.0f} "
              f"{inv:5d}/{len(items)}")

    # paired ratios: refute vs each verification arm, records present in both
    for base in ("verify_full", "verify_earlystop", "verify_earlystop_witness"):
        pairs = []
        for (rid, arm), row in rows.items():
            if arm != "refute":
                continue
            other = rows.get((rid, base))
            if other and row["output"] > 0 and other["output"] > 0:
                pairs.append((row["output"], other["output"]))
        if not pairs:
            continue
        ratios = sorted(r / v for r, v in pairs)
        rng = random.Random(20260819)
        boots = []
        for _ in range(2000):
            sample = [rng.choice(pairs) for _ in pairs]
            boots.append(sum(r for r, _ in sample) / sum(v for _, v in sample))
        boots.sort()
        lo, hi = boots[50], boots[1949]
        agg = sum(r for r, _ in pairs) / sum(v for _, v in pairs)
        print(f"\nrefute vs {base}: n={len(pairs)} paired records")
        print(f"  aggregate token ratio (refute/{base}): {agg:.3f}  "
              f"[95% bootstrap CI {lo:.3f}, {hi:.3f}]")
        print(f"  median per-record ratio: {ratios[len(ratios)//2]:.3f}")
        cheaper = sum(1 for x in ratios if x < 1)
        print(f"  records where refutation is cheaper: {cheaper}/{len(ratios)}")


if __name__ == "__main__":
    main()
