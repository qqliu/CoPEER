#!/usr/bin/env python3
"""Logged retrieval wrapper for the proof-development replication.

The arm prompts (see ../prompts.json) invoke exactly
    python3 ${BASE}/scripts/bugbank_retrieve.py --claims-json ... -k 3 --out ...
with ${BASE} pointing at this run directory, so the three retrieval-using arms
(bugbank_orig, bugbank_parity, placebo_parity) see byte-identical command text.
What the command DOES is selected by environment variables set per cell by the
driver (bwrap --setenv), never by the model:

  PC_RETRIEVAL_MODE   real_noexclude | real_exclude_own | placebo
  PC_EXCLUDE_ITEMS    JSON list of source_item ids to drop (real_exclude_own only)
  PC_PLACEBO_SEED     integer seed for the placebo record substitution
  PC_CALL_LOG         path of a JSONL file; one line is appended per invocation
                      (this is the mechanical iteration count for retrieval arms)

Every mode runs the frozen original retriever
    qedbench_certificate_availability_triage/scripts/bugbank_retrieve.py
(pinned by sha256 in the run manifest) with the caller's arguments; the placebo
mode then replaces every returned record with a length-matched record from an
unrelated BugBank entry (see pc_placebo.py), keeping the output shape identical.
"""
import json, os, subprocess, sys, time, hashlib, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TRIAGE = HERE.parents[2]                       # .../qedbench_certificate_availability_triage
REAL = TRIAGE / "scripts" / "bugbank_retrieve.py"
PLACEBO = HERE / "pc_placebo.py"


def main() -> int:
    argv = sys.argv[1:]
    mode = os.environ.get("PC_RETRIEVAL_MODE", "real_noexclude")
    log = os.environ.get("PC_CALL_LOG")
    out = None
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    cmd = [sys.executable, str(REAL), *argv]
    excl_path = None
    if mode == "real_exclude_own" and os.environ.get("PC_EXCLUDE_ITEMS"):
        excl_path = pathlib.Path(out or "/tmp/pc_exclude.json").with_suffix(".exclude_items.json")
        excl_path.write_text(os.environ["PC_EXCLUDE_ITEMS"])
        cmd += ["--exclude-items-json", str(excl_path)]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    rc = r.returncode
    substituted = None
    if rc == 0 and mode == "placebo" and out and os.path.exists(out):
        p = subprocess.run([sys.executable, str(PLACEBO), "--hits", out, "--seed", os.environ.get("PC_PLACEBO_SEED", "0"),
                            "--exclude-items", os.environ.get("PC_EXCLUDE_ITEMS", "[]")], capture_output=True, text=True)
        sys.stderr.write(p.stderr)
        rc = p.returncode if p.returncode else rc
        substituted = p.stdout.strip()
    if log:
        rec = {"t": round(time.time(), 3), "seconds": round(time.time() - t0, 2), "mode": mode, "argv": argv, "rc": rc,
               "out": out, "out_sha256": (hashlib.sha256(open(out, "rb").read()).hexdigest() if out and os.path.exists(out) else None),
               "placebo_note": substituted}
        with open(log, "a") as f:
            f.write(json.dumps(rec) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
