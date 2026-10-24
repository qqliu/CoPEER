#!/bin/bash
# Repair-track sandbox: run one command inside a bubblewrap namespace with a PRIVATE HOME.
#
#   sandbox_exec.sh <sandbox_dir> <mode> -- <command> [args...]
#   mode = lean       : Lean only, no network, no ~/.claude, sandbox root READ-WRITE (the harness's own setup compiles,
#                       before any solver exists)
#          cli        : Claude CLI, network shared, ~/.claude bound (the solver attempt); sandbox root READ-ONLY,
#                       only <sandbox>/work read-write; the gatekeeper directory REPAIR_GATE_DIR bound read-write at
#                       /opt/repair_gate (outside the sandbox root: unreachable by the file tools and the command grammar)
#          cli-nonet  : as cli but the network namespace is unshared (listing / dry run; no API call can leave)
#
# Visible inside the namespace, and nothing else:
#   /usr /etc (read-only), /proc /dev, tmpfs /tmp /run, tmpfs at $HOME, the node install (read-only),
#   $HOME/.elan (read-only toolchains), the sandbox dir (bound at its own absolute path: read-write in lean mode,
#   READ-ONLY in cli modes with <sandbox>/work read-write on top), the common Lean project's .lake/packages
#   (read-only, bound at <sandbox>/.lake/packages), the gatekeeper directory at /opt/repair_bin (read-only, first on
#   PATH), in cli modes the host directory REPAIR_GATE_DIR at /opt/repair_gate (read-write; the gatekeeper appends its
#   kernel-check log there; the solver's Write/Read/Edit are confined to the working directory by --restricted and its
#   Bash to `lake env lean <file>.lean`, so no solver tool can reach it),
#   and in cli modes: the live ~/.claude directory (resolved through the symlink; a REAL directory bind so a
#   token refresh by atomic replacement stays visible; never a bind of the token file), with every
#   subdirectory except cache/statsig/state hidden under a tmpfs and history.jsonl replaced by an empty file,
#   plus $HOME/.claude.json as a plain tmpfs file (never a bind of the host file: the host CLI renames over it).
# Everything under /scratch, /home (other than the entries above) and the harness (evaluator, packets,
# mutants, synthetic) is absent. The environment is cleared (env -i); only an allowlist plus SBX_* variables pass.
# Lean compiles requested by the solver go through /opt/repair_bin/lake, which runs them in a NESTED bubblewrap
# (no network, tmpfs HOME with only ~/.elan, sandbox root read-only): the Lean worker never sees ~/.claude.
set -uo pipefail
die() { echo "sandbox_exec: $*" >&2; exit 2; }
[ "$#" -ge 4 ] || die "usage: sandbox_exec.sh <sandbox_dir> <lean|cli|cli-nonet> -- <command...>"
SANDBOX=$1; MODE=$2; shift 2
[ "$1" = "--" ] || die "expected -- before the command"; shift
[ -d "$SANDBOX" ] || die "sandbox dir missing: $SANDBOX"
case "$SANDBOX" in /*) ;; *) die "sandbox dir must be absolute" ;; esac
[ -n "${HOME:-}" ] && [ -d "$HOME" ] || die "HOME is unset or not a directory; refusing to build a namespace around it"
COMMON=${REPAIR_COMMON_PROJECT:?REPAIR_COMMON_PROJECT must be set}
NODE_DIR=${REPAIR_NODE_DIR:-/usr}
HBIN=${REPAIR_HARNESS_BIN:?REPAIR_HARNESS_BIN must be set}
MAXK=${REPAIR_MAX_KERNEL_CHECKS:-20}
[ -d "$COMMON/.lake/packages" ] || die "common project packages missing: $COMMON/.lake/packages"
[ -x "$NODE_DIR/bin/node" ] || die "node not found under $NODE_DIR"
[ -x "$HBIN/lake" ] || die "gatekeeper missing: $HBIN/lake"
[ -d "$HOME/.elan" ] || die "\$HOME/.elan missing"
mkdir -p "$SANDBOX/.lake/packages" "$SANDBOX/.lake/build/lib/lean" || die "cannot prepare $SANDBOX/.lake"

B=(/usr/bin/bwrap --die-with-parent --unshare-user --unshare-pid --unshare-ipc --unshare-uts --unshare-cgroup-try)
case "$MODE" in
  lean|cli-nonet) B+=(--unshare-net) ;;
  cli) ;;
  *) die "unknown mode $MODE" ;;
esac
B+=(--ro-bind /usr /usr --symlink usr/lib /lib --symlink usr/lib64 /lib64 --symlink usr/bin /bin --symlink usr/sbin /sbin
    --ro-bind /etc /etc --proc /proc --dev /dev --tmpfs /tmp --tmpfs /run
    --tmpfs "$HOME" --ro-bind "$NODE_DIR" "$NODE_DIR" --ro-bind "$HOME/.elan" "$HOME/.elan")
# Optional extra read-only bind for a second Claude Code install (e.g. 2.1.280 for claude-opus-5-5); recorded by the caller.
if [ -n "${REPAIR_EXTRA_RO_BIND:-}" ]; then [ -d "$REPAIR_EXTRA_RO_BIND" ] || die "REPAIR_EXTRA_RO_BIND not a directory"; B+=(--ro-bind "$REPAIR_EXTRA_RO_BIND" "$REPAIR_EXTRA_RO_BIND"); fi
CLAUDE_LIVE=""
GATE_DIR=""
if [ "$MODE" != "lean" ]; then
  CLAUDE_LIVE=$(readlink -f "$HOME/.claude") || die "cannot resolve \$HOME/.claude"
  [ -d "$CLAUDE_LIVE" ] || die "resolved \$HOME/.claude is not a directory"
  B+=(--bind "$CLAUDE_LIVE" "$HOME/.claude")
  shopt -s nullglob dotglob
  for e in "$CLAUDE_LIVE"/*; do
    n=${e##*/}
    if [ -d "$e" ] && [ ! -L "$e" ]; then
      case "$n" in cache|statsig|state) ;; *) B+=(--tmpfs "$HOME/.claude/$n") ;; esac
    elif [ "$n" = "history.jsonl" ]; then
      B+=(--file 8 "$HOME/.claude/$n")
    fi
  done
  shopt -u nullglob dotglob
  exec 8</dev/null
  exec 9<<<'{"hasCompletedOnboarding": true}'
  B+=(--file 9 "$HOME/.claude.json")
  GATE_DIR=${REPAIR_GATE_DIR:?REPAIR_GATE_DIR must be set in cli modes (host directory for the gatekeeper log)}
  case "$GATE_DIR" in /*) ;; *) die "REPAIR_GATE_DIR must be absolute" ;; esac
  [ -d "$GATE_DIR" ] || die "REPAIR_GATE_DIR missing: $GATE_DIR"
  case "$GATE_DIR" in "$SANDBOX"|"$SANDBOX"/*) die "REPAIR_GATE_DIR must lie outside the sandbox root" ;; esac
  [ -d "$SANDBOX/work" ] || die "writable subdirectory missing: $SANDBOX/work"
  # Solver-facing layout: the whole sandbox READ-ONLY (skeleton, packet files, compiled oleans, Lake's config cache),
  # then work/ READ-WRITE on top (the deliverable work/SUBMISSION.lean and scratch files), then the read-only packages.
  B+=(--ro-bind "$SANDBOX" "$SANDBOX" --bind "$SANDBOX/work" "$SANDBOX/work"
      --ro-bind "$COMMON/.lake/packages" "$SANDBOX/.lake/packages" --bind "$GATE_DIR" /opt/repair_gate)
else
  B+=(--bind "$SANDBOX" "$SANDBOX" --ro-bind "$COMMON/.lake/packages" "$SANDBOX/.lake/packages")
fi
B+=(--ro-bind "$HBIN" /opt/repair_bin)
# Test fixtures only (offline rehearsal with tests/fake_claude): the harness's own tests/ directory, and NOTHING else, may be
# bound read-only at /opt/repair_test, so a receipt saying rehearsal_with_fake_cli always refers to that directory's fixture.
if [ -n "${REPAIR_EXTRA_BIN:-}" ]; then
  TESTS_DIR=$(readlink -f "$(dirname "$HBIN")/tests") || die "cannot resolve the harness tests directory"
  [ "$(readlink -f "$REPAIR_EXTRA_BIN")" = "$TESTS_DIR" ] || die "REPAIR_EXTRA_BIN must be the harness tests directory $TESTS_DIR (got $REPAIR_EXTRA_BIN)"
  B+=(--ro-bind "$REPAIR_EXTRA_BIN" /opt/repair_test)
fi
B+=(--chdir "$SANDBOX")
# bubblewrap 0.4.1 has no --clearenv/--setenv: the environment is cleared by `env -i` inside the namespace and
# rebuilt from this allowlist plus every SBX_* variable of the caller (prefix stripped).
E=(/usr/bin/env -i "HOME=$HOME" "PATH=/opt/repair_bin:$NODE_DIR/bin:/usr/bin:/bin" LANG=C.UTF-8 LC_ALL=C.UTF-8
   TERM=dumb SHELL=/bin/bash "USER=${USER:-$(id -un)}" "LOGNAME=${LOGNAME:-$(id -un)}" DISABLE_AUTOUPDATER=1
   "REPAIR_SANDBOX_ROOT=$SANDBOX" "REPAIR_MAX_KERNEL_CHECKS=$MAXK" "REPAIR_WORKER_ISOLATION=${REPAIR_WORKER_ISOLATION:-1}")
if [ "$MODE" != "lean" ]; then E+=("REPAIR_KERNEL_LOG=/opt/repair_gate/kernel_checks.log"); fi
for v in "${!SBX_@}"; do E+=("${v#SBX_}=${!v}"); done
exec "${B[@]}" -- "${E[@]}" "$@"
