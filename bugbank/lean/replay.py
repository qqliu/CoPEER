#!/usr/bin/env python3
"""Check unchanged Lean sources and their selected declarations at recorded pins."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / "bugbank" / "lean"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_selection(args):
    manifest = json.loads((FORMAL / "replay_manifest.json").read_text())
    rows = manifest["sources"]
    # This is the original 312-source replay cohort. Later archival exports
    # have separate indices/receipts and are not fresh-build claims for this run.
    source_roots = ("bugbank/certificates", "mathematics/theorems", "mathematics/extensions", "mathematics/explanations")
    actual = {str(p.relative_to(ROOT)) for sub in source_roots
              for p in (ROOT / sub).rglob("*.lean") if ".lake" not in p.parts}
    # Build output belongs outside the source trees; inventory checks concern
    # the distributed files, not temporary instrumented copies.
    expected = {row["file"] for row in rows}
    if actual != expected:
        raise ValueError(f"Lean inventory differs: missing={sorted(expected-actual)}, "
                         f"unlisted={sorted(actual-expected)}")
    for row in rows:
        if sha256(ROOT / row["file"]) != row["sha256"]:
            raise ValueError(f"Source hash differs: {row['file']}")
    for filename, expected_hash in manifest["evidence_files"].items():
        if sha256(ROOT / filename) != expected_hash:
            raise ValueError(f"Evidence hash differs: {filename}")
    if args.group != "all":
        rows = [r for r in rows if r["group"] == args.group]
    if args.core_only:
        rows = [r for r in rows if r["environment"] == "core"]
    if args.select:
        rows = [r for r in rows if any(s in r["file"] for s in args.select)]
    if args.exclude:
        rows = [r for r in rows if not any(s in r["file"] for s in args.exclude)]
    if args.core_version == "4.34.0":
        if any(r["environment"] != "core" for r in rows):
            raise ValueError("4.34.0 is available only with --core-only.")
        if any("4.34.0" not in r["recorded_lean_versions"] for r in rows):
            raise ValueError("A selected file lacks a recorded Lean 4.34.0 build.")
    if not rows:
        raise ValueError("Selection contains no sources.")
    return manifest, rows


def verify_mathlib_project(project):
    expected = json.loads((FORMAL / "lake-manifest.json").read_text())
    actual = json.loads((project / "lake-manifest.json").read_text())
    pins = lambda data: {p["name"]: (p["url"], p["rev"])
                         for p in data["packages"]}
    if pins(actual) != pins(expected):
        raise ValueError("Mathlib project dependencies differ from the release lock file.")
    if (project / "lean-toolchain").read_text().strip() != "leanprover/lean4:v4.30.0":
        raise ValueError("Mathlib project must use Lean 4.30.0.")
    if not (project / ".lake/packages/mathlib/Mathlib.lean").exists():
        raise ValueError("Mathlib is not installed. Run the preparation commands in bugbank/lean/README.md.")


def replay_one(row, args, output):
    start = time.monotonic()
    key = row["file"].replace("/", "__").removesuffix(".lean")
    raw = (ROOT / row["file"]).read_bytes()
    # Append inspection commands in a disposable copy; preserve every proof byte.
    suffix = "\n\n" + "\n".join(
        f"#print axioms _root_.{name}" for name in row["selected_declarations"])
    with tempfile.TemporaryDirectory(prefix="copeer-lean-") as tmp:
        candidate = Path(tmp) / "Replay.lean"
        candidate.write_bytes(raw + suffix.encode() + b"\n")
        if row["environment"] == "core":
            version = args.core_version
            command = ["elan", "run", f"leanprover/lean4:v{version}", "lean", str(candidate)]
            cwd = FORMAL
        else:
            version = "4.30.0"
            command = ["elan", "run", "leanprover/lean4:v4.30.0", "lake", "env", "lean",
                       str(candidate)]
            cwd = args.mathlib_project
        env = dict(os.environ)
        # No caller-supplied module search path may silently supply extra imports.
        env.pop("LEAN_PATH", None)
        try:
            process = subprocess.run(command, cwd=cwd, env=env, text=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     timeout=args.timeout or row.get("timeout_seconds", 600))
            log = process.stdout
            exit_code = process.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            log = exc.stdout or b""
            if isinstance(log, bytes):
                log = log.decode(errors="replace")
            exit_code = None
            timed_out = True
        log = log.replace(str(candidate), "<replay-source>")
        log = log.replace(str(args.mathlib_project), "<mathlib-project>")
        log = log.replace(str(ROOT), "<release>")
    found = {}
    for name, axioms in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", log):
        found[name] = sorted(x.strip() for x in axioms.split(",") if x.strip())
    for name in re.findall(r"'([^']+)' does not depend on any axioms", log):
        found[name] = []
    selected = {n: found.get(n) for n in row["selected_declarations"]}
    missing = [n for n, axioms in selected.items() if axioms is None]
    disallowed = {n: sorted(set(a) - ALLOWED_AXIOMS) for n, a in selected.items()
                  if a is not None and set(a) - ALLOWED_AXIOMS}
    # A successful compilation is not enough: each selected declaration must
    # print an axiom list containing only the recorded trusted axiom classes.
    passed = exit_code == 0 and not missing and not disallowed
    (output / (key + ".log")).write_text(log)
    return {"file": row["file"], "source_sha256": row["sha256"],
            "lean_version": version, "environment": row["environment"],
            "exit_code": exit_code, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - start, 3),
            "selected_axioms": selected, "missing_axiom_prints": missing,
            "disallowed_axioms": disallowed, "passed": passed,
            "log": key + ".log"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-inventory", action="store_true",
                        help="Verify hashes and inventory without running Lean.")
    parser.add_argument("--list", action="store_true", help="List selected sources without compiling.")
    parser.add_argument("--group", choices=("all", "certificates", "mathematics"), default="all")
    parser.add_argument("--select", action="append", default=[], metavar="SUBSTRING")
    parser.add_argument("--exclude", action="append", default=[], metavar="SUBSTRING")
    parser.add_argument("--core-only", action="store_true")
    parser.add_argument("--core-version", choices=("4.30.0", "4.34.0"), default="4.30.0")
    parser.add_argument("--mathlib-project", type=Path, default=FORMAL,
                        help="Optional existing environment with exactly the release dependency pins.")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--timeout", type=int,
                        help="Override per-source timeout (600 seconds, or 7200 for Cube8Mod36).")
    parser.add_argument("--output", type=Path, default=ROOT / ".replay")
    args = parser.parse_args()
    if args.jobs < 1 or (args.timeout is not None and args.timeout < 1):
        parser.error("--jobs and --timeout must be positive.")
    args.mathlib_project = args.mathlib_project.resolve()
    try:
        manifest, rows = load_selection(args)
        print(f"Inventory and evidence hashes verified; selected {len(rows)} sources.", flush=True)
        if args.list:
            for row in rows:
                print(row["environment"], row["file"])
        if args.check_inventory or args.list:
            return 0
        if any(r["environment"] == "mathlib" for r in rows):
            verify_mathlib_project(args.mathlib_project)
        output = args.output.resolve()
        # Keeping generated .lean files outside source trees is also enforced by
        # TemporaryDirectory above; logs/summary may use the chosen output path.
        output.mkdir(parents=True, exist_ok=True)
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(replay_one, r, args, output): r for r in rows}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                detail = "" if result["passed"] else (
                    f" (exit={result['exit_code']}, timeout={result['timed_out']})")
                print(("PASS " if result["passed"] else "FAIL ") + result["file"] + detail,
                      flush=True)
        results.sort(key=lambda r: r["file"])
        report = {"schema": "copeer-lean-replay/v1", "source_count": len(results),
                  "passed": sum(r["passed"] for r in results),
                  "allowed_axioms": sorted(ALLOWED_AXIOMS),
                  "inventory_sha256": sha256(FORMAL / "replay_manifest.json"),
                  "results": results}
        (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        print(f"Passed {report['passed']}/{len(results)}; summary: {output / 'summary.json'}")
        return 0 if report["passed"] == len(results) else 1
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"Replay error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
