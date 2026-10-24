#!/usr/bin/env python3
"""Pre-registered analysis for the proof-development replication.

  python3 report.py [--model opus|sol|gemini] [--grader astra] [--json out.json]

Units: one record = one problem; every contrast is paired within (model, record)
over records that have BOTH arms' drafts (and, for correctness, both grades).
Statistics (all pre-registered, see README):
  * token ratio = sum(arm A tokens) / sum(arm B tokens) over paired records,
    with a 95% record-bootstrap interval (B = 2000, seed 20260916), for OUTPUT
    tokens (the August primary) and for ALL tokens (output + uncached input +
    cache-read input, the August 'all tokens' basis);
  * mean iterations (self-reported, as in August) and the mechanical counts
    (retrieval calls; saved drafts in parity arms);
  * pairs in which arm A used fewer output tokens;
  * correctness and pitfall counts per arm from the blind grades.
Contrasts, in pre-registered order:
  1  bugbank_parity  vs plain_parity     (primary: does the bank's content reduce cost at parity?)
  2  bugbank_parity  vs placebo_parity   (content vs presence)
  3  placebo_parity  vs plain_parity     (presence effect alone)
  4  bugbank_orig    vs plain_orig       (exact August replication; inherits the stop-rule confound)
"""
import argparse, json, random, statistics
from pathlib import Path

RUN = Path(__file__).resolve().parent
CONTRASTS = [("bugbank_parity", "plain_parity"), ("bugbank_parity", "placebo_parity"),
             ("placebo_parity", "plain_parity"), ("bugbank_orig", "plain_orig")]
B, SEED = 2000, 20260916


def load(model, grader):
    tele = {}
    p = RUN / "telemetry" / f"{model}.jsonl"
    if p.exists():
        for line in open(p):
            r = json.loads(line)
            if r.get("status") == 0:
                tele[(r["record_id"], r["arm"])] = r          # last successful attempt wins
    grades = {}
    g = RUN / "grades" / grader / model
    if g.exists():
        for arm_dir in g.iterdir():
            for f in arm_dir.glob("*.json"):
                d = json.load(open(f)); grades[(d["record_id"], arm_dir.name)] = d
    return tele, grades


def tokens(r, basis):
    u = r["usage"]
    out = u.get("output_tokens") or 0
    if basis == "output": return out
    return out + (u.get("input_uncached") or 0) + (u.get("input_cache_read") or 0)


def ratio_ci(pairs, basis):
    a = [tokens(x, basis) for x, _ in pairs]; b = [tokens(y, basis) for _, y in pairs]
    point = sum(a) / sum(b) if sum(b) else float("nan")
    rng = random.Random(SEED); n = len(pairs); boots = []
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        sa = sum(a[i] for i in idx); sb = sum(b[i] for i in idx)
        if sb: boots.append(sa / sb)
    boots.sort()
    return point, (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]) if boots else (None, None)


def contrast(tele, grades, A, Bm):
    rids = sorted({r for (r, arm) in tele if arm == A} & {r for (r, arm) in tele if arm == Bm})
    if not rids: return {"arms": [A, Bm], "n_pairs": 0}
    pairs = [(tele[(r, A)], tele[(r, Bm)]) for r in rids]
    out = {"arms": [A, Bm], "n_pairs": len(rids)}
    for basis in ("output", "all"):
        pt, (lo, hi) = ratio_ci(pairs, basis)
        out[f"{basis}_ratio"] = round(pt, 3); out[f"{basis}_ci95"] = [round(lo, 3), round(hi, 3)] if lo is not None else None
    out["pairs_A_fewer_output"] = sum(1 for x, y in pairs if tokens(x, "output") < tokens(y, "output"))
    for tag, arm in (("A", A), ("B", Bm)):
        rows = [tele[(r, arm)] for r in rids]
        it = [x.get("iterations_self_reported") for x in rows if isinstance(x.get("iterations_self_reported"), int)]
        out[f"{tag}_mean_iterations_self_reported"] = round(statistics.mean(it), 2) if it else None
        out[f"{tag}_mean_retrieval_calls"] = round(statistics.mean(x["retrieval_calls_mechanical"] for x in rows), 2)
        out[f"{tag}_mean_drafts_saved"] = round(statistics.mean(x["drafts_saved_mechanical"] for x in rows), 2)
        gs = [grades.get((r, arm)) for r in rids]; gs = [g for g in gs if g]
        out[f"{tag}_graded"] = len(gs)
        out[f"{tag}_correct"] = sum(1 for g in gs if g["correctness"] == "CORRECT")
        out[f"{tag}_flawed"] = sum(1 for g in gs if g["correctness"] == "FLAWED")
        out[f"{tag}_incomplete"] = sum(1 for g in gs if g["correctness"] == "INCOMPLETE")
        out[f"{tag}_pitfall"] = sum(1 for g in gs if g["pitfall_committed"])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model"); ap.add_argument("--grader", default="astra"); ap.add_argument("--json")
    a = ap.parse_args()
    models = [a.model] if a.model else ["opus", "sol", "gemini"]
    report = {"schema": "proof-construction-repro-report/1", "grader": a.grader, "bootstrap": {"B": B, "seed": SEED}, "models": {}}
    for m in models:
        tele, grades = load(m, a.grader)
        report["models"][m] = {"cells_ok": len(tele), "graded": len(grades),
                               "contrasts": [contrast(tele, grades, A, Bm) for A, Bm in CONTRASTS]}
        print(f"== {m}: {len(tele)} successful cells, {len(grades)} grades ({a.grader})")
        for c in report["models"][m]["contrasts"]:
            if c["n_pairs"]:
                print(f"  {c['arms'][0]:>15} vs {c['arms'][1]:<15} n={c['n_pairs']:2d} | output {c['output_ratio']} {c['output_ci95']} | all-tokens {c['all_ratio']} {c['all_ci95']} | self-rep iters {c['A_mean_iterations_self_reported']} vs {c['B_mean_iterations_self_reported']} | mech retr/drafts ({c['A_mean_retrieval_calls']},{c['A_mean_drafts_saved']}) vs ({c['B_mean_retrieval_calls']},{c['B_mean_drafts_saved']}) | A fewer output {c['pairs_A_fewer_output']}/{c['n_pairs']} | correct {c['A_correct']}/{c['A_graded']} vs {c['B_correct']}/{c['B_graded']} | pitfall {c['A_pitfall']} vs {c['B_pitfall']}")
    if a.json: Path(a.json).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
