#!/usr/bin/env python3
"""Certified-claim localization v2: tool-free critic runner, Antigravity CLI lane (`gemini-3.1-pro`).

Contract-equivalent to run_critic.py (the Claude CLI lanes): same prompt, reservations, epoch authorisation, receipts,
attempt classes, technical gate, one attempt plus the single transport retry, 600 s wall, 120,000-token attempt cap,
10,000,000-token lane cap, salted run order, freeze / canary / run subcommands, PID file and HOLD/STOP checks.
The transport is the archived engine-agy branch of runs/lean_cert_repro_20260916/scripts/e2_backend.sh (lines 215-262):
a bubblewrap sandbox that hides every experiment tree and the other CLIs' state, binds the real ~/.gemini so the OAuth
refresh lands in place, mounts tmpfs over its volatile subdirectories, and runs `agy` in an empty per-call workdir
with the prompt on stdin and stream-json events on stdout. Two deviations from the archived launch, both binding
(lane_status/gemini-3.1-pro/PREFLIGHT_v2.json): no --dangerously-skip-permissions, and --sandbox --mode plan instead.

Declared lane deviations, recorded in every receipt: agy has no --system-prompt flag, so prompt_system.txt is the head of
the user turn (`system_prompt_deviation: true`); the CLI's tool set cannot be restricted by flag, so the contract is
observational: ANY tool step (typed "tool" or carrying tool fields), a second turn, a second init event, a served model
other than the requested id, an error, or an inconsistent or zero native usage is a CONTRACT_VIOLATION (fail-closed). A
dead login is flagged whether the CLI reports it as a zero-turn result or only on stderr/stdout without any result event.
The host ~/.gemini is a symlink into the repository tree since
2026-09-20 and bwrap cannot mount onto a path whose last component is a symlink; the launch therefore reconstructs a
private $HOME (the pattern lean_recovery/run_in_auth_namespace.sh proved on a compute node) and binds the RESOLVED
store as a real directory. Nothing is copied; no credential is opened, hashed or named.

  python3 -B run_agy.py freeze                       # print the freeze hash of the design files
  python3 -B run_agy.py canary                       # one call on a synthetic non-corpus text (harness check)
  python3 -B run_agy.py run --split pilot|evaluation --workers N --approved-freeze SHA
"""
import argparse, contextlib, json, os, queue, signal, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MAX_OUTPUT, FROZEN_FILES, build_prompt, freeze_hash, load_items, parse_candidates_audit, read, safe, sha  # noqa: E402
from lane_accounting import (HOLD_NAME, MAX_PHYSICAL_ATTEMPTS, LaneAccounting, LaneHeld, LaneStopped, atomic_json,  # noqa: E402
                             attempt_receipts, derived_attempt_class, exclusive_lock)
from run_critic import count, now, should_retry  # noqa: E402  the pure pieces of the Claude runner, shared byte for byte

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
EXECUTABLE = "<user-home>/.local/bin/agy"
BWRAP = "/usr/bin/bwrap"
LANE = "gemini-3.1-pro"       # lane key: directory name under EXP/runs and EXP/canary, requested_model of every receipt
MODEL = "gemini-3.1-pro"      # requested id; init.model must echo it EXACTLY (gemini-3.1-pro-high is a different served identity)
MODELS = (MODEL,)
EFFORT = "low"                # epoch 4 (2026-09-22, [coordination reference removed]): epoch 3 at "high" ended 7/20 valid and 13/20 contract failures (12 second-user-input-step kills, 1 tool-step kill); 7 of the 13 failed attempts had first-step output above the 16,000-token allowance
VERSION = "agy 1.2.8"         # `agy --version` prints "1.2.8"; main() refuses any other CLI
PER_CALL_CAP = 120000         # attributable tokens per call (largest item is about 20k input tokens)
LANE_CAP = 10000000           # cumulative attributable tokens per lane, carryover included
UNKNOWN_USAGE_CHARGE = 40000  # charged to the lane when a call ends without trustworthy native usage
WALL_CAP = 600                # seconds per call (v3 addendum: the same wall for every lane)
PRINT_TIMEOUT = "%ds" % WALL_CAP   # --print-timeout takes a Go duration ("0s" default, "55m" in the archived launch)
DRAIN_SECONDS = 5             # bounded read of already-buffered events after a controlled kill
MAX_CONSECUTIVE_TRANSPORT_FAILURES = 10
ATTEMPT_TAGS = ("a1", "a2_transport_retry")   # the call and its single transport retry; a third tag does not exist
assert len(ATTEMPT_TAGS) == MAX_PHYSICAL_ATTEMPTS
PID_NAME = "RUNNER_PID.json"  # lane/RUNNER_PID.json: the process an operator signals; SIGTERM drains like Ctrl-C
SCRATCH = os.environ.get("CCL_SCRATCH") or "<scratch-workdirs>"
SYSTEM_PROMPT_PLACEMENT = "head_of_user_turn"   # agy has no --system-prompt flag (PREFLIGHT_v2 flags_absent)
LAUNCH = {"sandbox": True, "mode": "plan", "dangerously_skip_permissions": False, "print_flag": False, "prompt_on_stdin": True}
# Epoch 4: no structured-output schema is launched (see agy_argv); structured_output is recorded as None.
USAGE_FIELDS = ("input_tokens", "output_tokens", "thinking_tokens", "cache_read_tokens", "total_tokens")
# Native usage semantics (all three archived success receipts): total_tokens == input_tokens + output_tokens; thinking_tokens is a
# SUBSET of output_tokens and cache_read_tokens a subset of input_tokens (neither is added); the result usage is the sum of the
# agent_response step usages. total_tokens is the attributable count of one call; output_tokens (thinking included) is judged
# against MAX_OUTPUT. A zero count is a default struct, never a measurement (the archived ERROR result carries all zeros): native
# usage is trusted only when input_tokens > 0 and output_tokens > 0, even when the step usage agrees.
# The archived zero-turn auth receipt: result.error "authentication failed or timed out" and, on stderr, "Error: authentication
# required. Run 'agy' to log in, then retry." Matched (lower-cased) against the result error, stderr and any non-JSON stdout.
AUTH_MARKERS = ("authentication", "unauthenticated", "unauthorized", "log in", "login")
# Sandbox (e2_backend.sh): every experiment tree and the other CLIs' state hidden; the workdir re-exposed afterwards.
HIDDEN_ROOTS = ("<workspace>", "/tmp", "/work", "/lfscratch", "/nfs")
HIDDEN_HOME_SUBDIRS = (".config/claude", ".local/share/claude", ".local/state/claude")
PRIVATE_HOME_SKIP = (".gemini", ".claude", ".codex", ".claude.json")   # handled explicitly or absent from the private $HOME
VOLATILE_GEMINI_SUBDIRS = ("history", "antigravity-cli/conversations", "antigravity-cli/brain", "antigravity-cli/knowledge",
                           "antigravity-cli/implicit", "antigravity-cli/crashes", "antigravity-cli/log")

def stdin_text(system, prompt):
    """The user turn: the frozen system text first, then the frozen user prompt (the declared system-prompt deviation)."""
    return system + "\n\n" + prompt

def environment():
    """The launching session's environment without its Claude variables; agy reads its own state from ~/.gemini only."""
    return {k: v for k, v in os.environ.items() if not (k.startswith("CLAUDE") or k.startswith("ANTHROPIC") or k == "MAX_THINKING_TOKENS")}

def provider_variables_present(env=None):
    """Names (never values) of Gemini/Google/Antigravity variables the CLI could read; recorded for the audit."""
    env = os.environ if env is None else env
    return sorted(k for k in env if k.startswith(("GEMINI", "GOOGLE", "ANTIGRAVITY")))

def sandbox_argv(workdir, home=None):
    """bwrap prefix: e2_backend.sh isolation plus the private-$HOME reconstruction for the symlinked ~/.gemini.

    Order matters to bubblewrap: hide first, re-expose afterwards. The resolved ~/.gemini store is bound as a REAL
    directory (the directory, never a file, so an atomic token refresh stays visible), then its volatile
    subdirectories are hidden, then the empty per-call workdir is re-exposed below the hidden /tmp.
    """
    home = home or os.environ.get("HOME")
    if not home or not os.path.isdir(home):   # compute nodes have no HOME unless the job is submitted with --export=ALL
        raise RuntimeError("HOME is unset or not a directory; refusing to build a sandbox around it: %r" % (home,))
    store = os.path.realpath(os.path.join(home, ".gemini"))
    if not os.path.isdir(store):
        raise RuntimeError("resolved ~/.gemini is not a directory; refusing to launch: " + store)
    argv = [BWRAP, "--die-with-parent", "--unshare-pid"]
    for name in sorted(os.listdir("/")):
        if name in ("dev", "proc", "sys", "lost+found"): continue
        path = "/" + name
        if os.path.exists(path): argv += ["--dev-bind", path, path]
    argv += ["--dev-bind", "/dev", "/dev", "--proc", "/proc", "--ro-bind", "/sys", "/sys"]
    for path in HIDDEN_ROOTS:
        if os.path.isdir(path) and not os.path.islink(path): argv += ["--tmpfs", path]
    # Private $HOME (lean_recovery/run_in_auth_namespace.sh): same path, ordinary entries rebound or recreated as symlinks,
    # ~/.claude and ~/.codex absent, ~/.claude.json empty, ~/.gemini a real directory bind of the resolved store.
    argv += ["--tmpfs", home]
    for name in sorted(os.listdir(home)):
        if name in PRIVATE_HOME_SKIP: continue
        path = os.path.join(home, name)
        if os.path.islink(path): argv += ["--symlink", os.readlink(path), path]
        else: argv += ["--bind", path, path]
    for name in HIDDEN_HOME_SUBDIRS:
        path = os.path.join(home, name)
        if os.path.isdir(path) and not os.path.islink(path): argv += ["--tmpfs", path]
    if os.path.exists(os.path.join(home, ".claude.json")): argv += ["--ro-bind", "/dev/null", os.path.join(home, ".claude.json")]
    argv += ["--bind", store, os.path.join(home, ".gemini")]
    for sub in VOLATILE_GEMINI_SUBDIRS:
        if os.path.isdir(os.path.join(store, sub)): argv += ["--tmpfs", os.path.join(home, ".gemini", sub)]
    argv += ["--bind", workdir, workdir, "--chdir", workdir]
    return argv

def agy_argv(model, workdir):
    """The archived engine-agy command line minus --dangerously-skip-permissions, plus --sandbox --mode plan.

    No --print: the archived launch engaged print mode through the stdin prompt and --output-format stream-json (its
    receipts carry init/step_update/result events), and this adapter reproduces that launch byte for byte.
    """
    # Epoch 4: no --json-schema (the CLI's structured-output path added a second user-input step in epoch 3); the scored
    # candidates come from the shared parser on the visible text, exactly as for the Claude lanes.
    return [EXECUTABLE, "--model", model, "--effort", EFFORT, "--output-format", "stream-json",
            "--sandbox", "--mode", "plan", "--disable-slash-commands", "--print-timeout", PRINT_TIMEOUT,
            "--log-file", os.path.join(workdir, "agy.log")]

def argv_for(model, workdir, home=None):
    return sandbox_argv(workdir, home) + agy_argv(model, workdir)

def cli_version():
    """`agy --version` on the host: no prompt, no stdin, no sandbox, no model call. The one pre-dispatch invocation."""
    done = subprocess.run([EXECUTABLE, "--version"], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60, env=environment())
    text = done.stdout.strip() or done.stderr.strip()
    return text.splitlines()[0].strip() if text else ""

def one_process(model, system, prompt, private_dir, tag):
    active = []
    try:
        return _one_process(model, system, prompt, private_dir, tag, active)
    finally:
        # Interruptions cannot leave a provider process alive behind a stopped lane.
        for proc in active:
            if proc.poll() is None:
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                proc.wait()


def _one_process(model, system, prompt, private_dir, tag, active):
    workdir = os.path.join(SCRATCH, safe(model) + "_" + tag + "_" + str(time.time_ns()) + "_" + str(threading.get_ident()))
    os.makedirs(workdir, exist_ok=False)
    os.makedirs(private_dir, exist_ok=True)
    stdin = stdin_text(system, prompt)
    start = time.monotonic()
    stderr_path = os.path.join(private_dir, "stderr_%s.txt" % tag)
    with open(stderr_path, "w") as stderr:
        proc = subprocess.Popen(argv_for(model, workdir), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=stderr, cwd=workdir, env=environment(), text=True, start_new_session=True)
    active.append(proc)
    def send_prompt():
        # A stuck reader must not disable the wall-clock watchdog.
        try:
            proc.stdin.write(stdin)
        except (BrokenPipeError, OSError):
            pass
        finally:
            try: proc.stdin.close()
            except (BrokenPipeError, OSError): pass
    threading.Thread(target=send_prompt, daemon=True).start()
    lines = queue.Queue()
    def pump():
        try:
            for line in proc.stdout: lines.put(line)
        except Exception as exc:
            lines.put(("reader_error", type(exc).__name__))
        else:
            lines.put(None)   # only actual iterator exhaustion is EOF; a reader failure is not complete evidence
    threading.Thread(target=pump, daemon=True).start()
    init = result = stop = None
    init_events = 0
    init_models = []          # every init event's model, verbatim and in order (a second init is itself a violation)
    stdout_tail = ""          # non-JSON stdout: a dead login may print its refusal there instead of emitting a result event
    tool_steps, user_inputs, agent_steps, usage_steps, texts = {}, [], [], [], {}
    raw = open(os.path.join(private_dir, "events_%s.private.jsonl" % tag), "w")
    def running():
        # Attributable tokens observed so far: the agent_response step usages (the result usage is their sum).
        return sum(max(count(u.get("total_tokens")), count(u.get("input_tokens")) + count(u.get("output_tokens"))) for u in usage_steps)
    def consume(line):
        nonlocal init, result, init_events, stdout_tail
        raw.write(line); raw.flush()
        try: ev = json.loads(line)
        except ValueError:
            stdout_tail = (stdout_tail + line)[-3000:]
            return
        if not isinstance(ev, dict): return
        kind = ev.get("event")
        if kind == "init" and isinstance(ev.get("init"), dict):
            init_events += 1
            init_models.append(ev["init"].get("model"))
            if init is None: init = ev["init"]
        elif kind == "step_update" and isinstance(ev.get("step_update"), dict):
            su = ev["step_update"]; step_type, state, index = su.get("step_type"), su.get("state"), su.get("step_index")
            key = index if isinstance(index, int) else "unindexed_%d" % (len(tool_steps) + len(user_inputs) + len(agent_steps))
            info = su.get("tool_info")
            if step_type == "tool" or su.get("tool_name") is not None or info is not None:
                # A tool step is any step typed "tool" OR carrying tool_name/tool_info (the archived non-tool steps carry neither key),
                # whatever its step_type says. Every state counts (ACTIVE, DONE, ERROR): the archived receipts show tool steps that
                # failed and were still tool steps.
                name = su.get("tool_name") if su.get("tool_name") is not None else (info.get("name") if isinstance(info, dict) else None)
                row = tool_steps.setdefault(key, {"step_index": index, "step_type": step_type, "tool_name": name, "states": []})
                row["states"].append(state)
            elif step_type == "user_input":
                if key not in user_inputs: user_inputs.append(key)
            elif step_type == "agent_response":
                if isinstance(su.get("text_delta"), str): texts.setdefault(key, []).append(su["text_delta"])
                if state == "DONE":
                    agent_steps.append(key)
                    if isinstance(su.get("usage"), dict): usage_steps.append(dict(su["usage"]))
        elif kind == "result" and isinstance(ev.get("result"), dict): result = ev["result"]
    drained = 0
    stream_eof = drain_required = drain_deadline_expired = False
    reader_error = None
    while True:
        try: line = lines.get(timeout=1.0)
        except queue.Empty: line = ""
        if line is None:
            stream_eof = True
            break
        if isinstance(line, tuple):
            reader_error = line[1]
            stop = {"reason": "contract_violation", "detail": "stream_reader_failure"}
        elif line: consume(line)
        elapsed = time.monotonic() - start
        # Controlled stops, in this order: a tool step or a second turn is a violation whatever was spent (the process group is
        # killed at once so an agentic loop cannot run on); then the attempt cap on observed usage; then the wall clock.
        if stop is None and tool_steps:
            stop = {"reason": "contract_violation", "detail": "tool_step_observed", "evidence": "step_update_tool",
                    "tool_names": [row["tool_name"] for row in tool_steps.values()], "running_total_at_kill": running(), "killed_process_group": True}
        elif stop is None and len(user_inputs) > 1:
            stop = {"reason": "contract_violation", "detail": "second_turn", "evidence": "second_user_input_step",
                    "running_total_at_kill": running(), "killed_process_group": True}
        elif stop is None and running() > PER_CALL_CAP: stop = {"reason": "per_call_token_cap", "running_total_at_kill": running()}
        elif stop is None and elapsed > WALL_CAP: stop = {"reason": "wall_clock_cap", "elapsed_seconds": round(elapsed, 1)}
        if stop is not None:
            try: os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            # Bounded drain: the pump may already hold later events. They are preserved and parsed, and an observed later
            # violation outranks the stop decided above. No further stop is decided here.
            drain_required = True
            deadline = time.monotonic() + DRAIN_SECONDS
            while reader_error is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    drain_deadline_expired = True
                    break
                try: line = lines.get(timeout=remaining)
                except queue.Empty:
                    drain_deadline_expired = True
                    break
                if line is None:
                    stream_eof = True
                    break
                if isinstance(line, tuple):
                    reader_error = line[1]
                    break
                if line: consume(line); drained += 1
            break
    # EOF alone is not evidence that the process exited. Bound the remaining wait
    # by the same per-attempt wall clock, then reap the entire process group.
    try:
        proc.wait(timeout=max(0.01, WALL_CAP - (time.monotonic() - start)))
    except subprocess.TimeoutExpired:
        if stop is None: stop = {"reason": "wall_clock_cap", "elapsed_seconds": round(time.monotonic() - start, 1)}
        try: os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        proc.wait()
    raw.close()
    try:
        with open(stderr_path, errors="replace") as fh: stderr_tail = fh.read()[-3000:]
    except OSError: stderr_tail = ""
    status = result.get("status") if result is not None else None
    success = status == "SUCCESS"
    error = result.get("error") if result is not None else None
    num_turns = result.get("num_turns") if result is not None else None
    u = result.get("usage") if result is not None else None
    well_formed = isinstance(u, dict) and all(isinstance(u.get(k), int) and not isinstance(u.get(k), bool) and u.get(k) >= 0 for k in USAGE_FIELDS)
    consistent = well_formed and u["total_tokens"] == u["input_tokens"] + u["output_tokens"] and u["thinking_tokens"] <= u["output_tokens"]
    # A zero input or output count is the CLI's default struct, never a measurement, even on a SUCCESS result whose step agrees.
    positive = well_formed and u["input_tokens"] > 0 and u["output_tokens"] > 0
    steps_sum = {k: sum(count(s.get(k)) for s in usage_steps) for k in USAGE_FIELDS}
    steps_agree = bool(usage_steps) and well_formed and all(steps_sum[k] == u[k] for k in USAGE_FIELDS)
    # Native usage is trusted only from a SUCCESS result whose struct is consistent, strictly positive and equal to the sum of
    # its steps; anything else is UNKNOWN usage, charged max(UNKNOWN_USAGE_CHARGE, observed), never a known zero.
    native = success and consistent and positive and steps_agree
    usage_defect = (None if native else "malformed" if not well_formed else "inconsistent" if not consistent
                    else "zero_count" if not positive else "steps_disagree")
    observed_total = max(count(u.get("total_tokens")) if isinstance(u, dict) else 0, running())
    first_key = min(texts, key=lambda k: (isinstance(k, str), k)) if texts else None
    first_text = "".join(texts[first_key]) if first_key is not None else ""
    response = result.get("response") if result is not None and isinstance(result.get("response"), str) else None
    # The result text is the answer only for a single, uncontinued turn; otherwise the first agent response is.
    answer = response if response and len(agent_steps) <= 1 and len(user_inputs) <= 1 else first_text
    structured = result.get("structured_output") if result is not None and isinstance(result.get("structured_output"), dict) else None
    output_observed = init is not None or bool(agent_steps) or bool(tool_steps) or bool(user_inputs) or bool(texts) or count(num_turns) > 0
    zero_turn_error = result is not None and not success and not output_observed
    nothing_served = result is None and not output_observed   # no result event at all (or none parsable): the other nothing-served shape
    blob = " ".join(str(x) for x in (error, result.get("message") if result is not None else None, stderr_tail, stdout_tail) if x).lower()
    auth_marker = next((marker for marker in AUTH_MARKERS if marker in blob), None)
    # A dead login shows either as the archived zero-turn ERROR result or as a refusal on stderr/stdout with no result event at all;
    # both are flagged so call_record stops the lane after the item's retry. Anything served is never an auth failure.
    auth_unavailable = (zero_turn_error or nothing_served) and auth_marker is not None
    served = init.get("model") if init is not None else None
    response_models = sorted({m for m in init_models if m})   # every init event's model, distinct, as run_critic records them
    served_as_requested = bool(init_models) and all(m == model for m in init_models)
    rec = {"tag": tag, "engine": "agy", "cli_version": VERSION, "wall_seconds": round(time.monotonic() - start, 1), "exit_code": proc.returncode,
           "hard_stop": stop, "system_prompt_deviation": True, "system_prompt_placement": SYSTEM_PROMPT_PLACEMENT, "launch": dict(LAUNCH),
           "provider_variables_present": provider_variables_present(),
           "init_events": init_events, "init_models": list(init_models), "num_turns": num_turns, "user_input_steps": len(user_inputs),
           "agent_response_steps": len(agent_steps),
           "tool_steps_observed": len(tool_steps), "tool_steps": list(tool_steps.values()), "usage_steps": usage_steps,
           "events_drained_after_kill": drained, "drain_eof_observed": stream_eof if drain_required else None, "stream_reader_error": reader_error,
           "controlled_drain_required": drain_required, "drain_deadline_expired": drain_deadline_expired,
           "controlled_drain_complete": stream_eof and reader_error is None if drain_required else None,
           "saw_init_event": init is not None, "saw_agent_response_step": bool(agent_steps),
           "saw_assistant_message": init is not None or bool(agent_steps) or bool(texts),   # anything served: never a retry
           "saw_result_event": result is not None, "served_model": served, "response_models": response_models,
           "result_status": status, "result_error": error, "conversation_id": result.get("conversation_id") if result is not None else None,
           "duration_seconds": result.get("duration_seconds") if result is not None else None,
           # The DONE step's text_delta is a trailing newline in the archived streams: compared without surrounding whitespace.
           "response_matches_stream_text": (response.strip() == first_text.strip()) if response is not None and first_text else None,
           "structured_output": structured, "stderr_tail": stderr_tail, "stdout_unparsed_tail": stdout_tail, "auth_marker": auth_marker if auth_unavailable else None,
           "init": ({"model": served, "permission_mode": init.get("permission_mode"), "cwd": init.get("cwd"),
                     "tools_count": len(init["tools"]) if isinstance(init.get("tools"), list) else None,
                     "json_schema_present": isinstance(init.get("json_schema"), dict)} if init is not None else None)}
    if native:
        rec["usage_known"] = stream_eof and reader_error is None
        rec["usage"] = {"total_attributable_tokens": u["total_tokens"] if rec["usage_known"] else None, **{k: u[k] for k in USAGE_FIELDS},
                        "stop_reason": None, "is_error": False, "num_turns": num_turns}
        if not rec["usage_known"]:
            rec["usage"].update(observed_lower_bound=observed_total, running_estimate_at_end=running())
            rec["budget_charge_tokens"] = max(UNKNOWN_USAGE_CHARGE, observed_total)
    else:
        rec["usage_known"] = False
        rec["usage"] = {"total_attributable_tokens": None, **{k: (u.get(k) if isinstance(u, dict) else None) for k in USAGE_FIELDS},
                        "observed_lower_bound": observed_total, "running_estimate_at_end": running(),
                        "stop_reason": None, "is_error": (not success or bool(error)) if result is not None else None, "num_turns": num_turns}
        rec["budget_charge_tokens"] = max(UNKNOWN_USAGE_CHARGE, observed_total)
    if native and u["total_tokens"] > PER_CALL_CAP:   # a live kill at the cap keeps its evidence; any other stop is outranked
        stop = {**(stop if stop is not None and stop["reason"] == "per_call_token_cap" else {}),
                "reason": "per_call_token_cap", "final_native_total": u["total_tokens"]}
    over_budget = native and u["output_tokens"] > MAX_OUTPUT
    checks = {
        "exit_code_zero": proc.returncode == 0, "result_status_success": success,
        "exactly_one_turn": count(num_turns) == 1 and num_turns == 1, "no_tool_steps": not tool_steps,
        "exactly_one_agent_response": len(agent_steps) == 1 and len(user_inputs) <= 1,
        "single_init_event": init_events == 1, "served_model_equals_requested": served_as_requested,
        "init_permission_mode_not_always_proceed": init is not None and init.get("permission_mode") != "always-proceed",
        "native_usage_present_and_consistent": native, "usage_steps_agree_with_result": steps_agree,
        "stream_reader_completed": stream_eof and reader_error is None,
        "final_result_event_with_native_usage": rec["usage_known"],
        "native_output_within_max_output": native and not over_budget,
        "final_text_present": bool(answer.strip()), "result_not_flagged_error": result is not None and not error}
    # Fail-closed classification (V4_SPEC.md shared definitions). The listed violations outrank everything else; whatever
    # fits no other class is a violation too, never a valid answer and never a retry.
    violations = [name for name, found in (
        ("tool_step_observed", bool(tool_steps)),
        ("second_turn", len(user_inputs) > 1 or count(num_turns) > 1),
        ("multiple_agent_responses", len(agent_steps) > 1),
        ("stream_reader_failure", reader_error is not None),
        ("controlled_drain_incomplete", drain_required and not (stream_eof and reader_error is None)),
        ("multiple_init_events", init_events > 1),
        ("wrong_served_model", init is not None and not served_as_requested),
        ("permission_mode_always_proceed", init is not None and init.get("permission_mode") == "always-proceed"),
        ("result_error_with_output_observed", result is not None and not success and output_observed),
        ("result_flagged_error", result is not None and bool(error) and not zero_turn_error),
        ("usage_inconsistent_or_zero", success and not native)) if found]
    if violations:
        attempt_class, runner_stop = "CONTRACT_VIOLATION", stop
        stop = dict(stop) if stop is not None and stop["reason"] == "contract_violation" else {"reason": "contract_violation"}
        stop.update(detail=violations[0], violations=violations)
        if runner_stop is not None and runner_stop["reason"] != "contract_violation": stop["runner_stop"] = runner_stop
        if init is not None and not served_as_requested:   # the served id verbatim: the first init that differs, and every init
            stop.update(served_model=next(m for m in init_models if m != model), served_models=list(init_models), requested_model=model)
        if success and not native: stop.update(native_usage=u, usage_steps_sum=steps_sum, usage_defect=usage_defect)
    elif stop is None and over_budget and checks["exit_code_zero"] and rec["usage_known"]:
        # No client cap exists for this CLI: a complete, clean, one-turn SUCCESS whose native output count (thinking included)
        # exceeds the budget is the legitimate intention-to-treat miss; charged, never retried.
        attempt_class = "BUDGET_EXHAUSTED"
        stop = {"reason": "output_budget_exhausted", "detail": "native_output_tokens_exceed_max_output",
                "native_output_tokens": u["output_tokens"], "thinking_tokens": u["thinking_tokens"], "max_output_tokens": MAX_OUTPUT,
                "exhaustion_evidence_source": "native_output_count", "second_request_not_excluded": False}
    elif not output_observed and result is None and (stop is None or stop["reason"] == "wall_clock_cap"):
        attempt_class = "TRANSPORT_FAILURE"   # nothing observed, including a wall-cap kill before any output
    elif zero_turn_error and (stop is None or stop["reason"] == "wall_clock_cap"):
        attempt_class = "TRANSPORT_FAILURE"   # the CLI reported an error before any turn (no init, no step): nothing was served
    elif stop is None and all(checks.values()):
        attempt_class = "VALID_ANSWER"
    else:
        attempt_class = "CONTRACT_VIOLATION"  # a per-call/wall stop after output, an incomplete stream, a non-zero exit, unknown usage, ...
        if stop is None:
            stop = {"reason": "contract_violation", "detail": "protocol_check_failed",
                    "failed_checks": sorted(name for name, passed in checks.items() if not passed)}
    checks["no_hard_stop"] = stop is None
    rec.update(hard_stop=stop, attempt_class=attempt_class, transport_failure=attempt_class == "TRANSPORT_FAILURE",
               protocol_checks=checks, valid_protocol=attempt_class == "VALID_ANSWER",
               zero_turn_error=({"status": status, "error": error, "num_turns": num_turns} if zero_turn_error else None),
               auth_unavailable=auth_unavailable,
               exhaustion_evidence_source=stop.get("exhaustion_evidence_source") if attempt_class == "BUDGET_EXHAUSTED" else None,
               native_stop_verified=False if attempt_class == "BUDGET_EXHAUSTED" else None,   # the CLI stops nothing: the count is the evidence
               second_request_not_excluded=False if attempt_class == "BUDGET_EXHAUSTED" else None)
    return rec, answer or ""


def consumed_attempts(accounting, out_dir, record_id, split):
    """A.2: {tag: receipted attempt} of an unfinished item; these tags are never dispatched again.

    The accounting layer refuses a DISPATCH without an ATTEMPT receipt (a call of unknown extent:
    LaneAccounting.reconcile_interrupted has to close it first). Receipts of another item, freeze
    or tag scheme are refused here; like the restore, the canary is not bound to the freeze.
    """
    consumed = dict(accounting.consumed_attempts(out_dir))
    for tag, dispatch, _ in attempt_receipts(out_dir):
        if (tag not in ATTEMPT_TAGS or dispatch.get("record_id") != record_id
                or (split != "canary" and dispatch.get("freeze_sha256") != accounting.freeze_sha256)):
            accounting.stop("consumed_attempt_identity_mismatch", {"path": str(out_dir), "tag": tag,
                            "recovery": "reconcile explicitly; a consumed attempt is never rerun"})
            raise LaneStopped(accounting.summary()["stopped"])
    return consumed


def call_record(model, item, system, out_dir, private_dir, accounting, split):
    prompt = build_prompt(item)
    rec = {"record_id": item["record_id"], "requested_model": model, "engine": "agy", "cli_version": VERSION, "cli_executable": EXECUTABLE, "effort": EFFORT,
           "max_output_tokens_per_request": MAX_OUTPUT, "per_call_cap": PER_CALL_CAP, "wall_cap_seconds": WALL_CAP,
           "prompt_sha256": sha(prompt), "system_prompt_sha256": sha(system), "stdin_sha256": sha(stdin_text(system, prompt)),
           "system_prompt_deviation": True, "system_prompt_placement": SYSTEM_PROMPT_PLACEMENT, "json_schema": None,
           "launch": dict(LAUNCH), "environment_overrides": {}, "started_utc": now(), "split": split,
           "freeze_sha256": accounting.freeze_sha256, "attempts": []}
    answer, dispatched_here = "", False
    consumed = consumed_attempts(accounting, out_dir, item["record_id"], split)
    for tag in ATTEMPT_TAGS:
        if tag in consumed:
            # A.2: never start a consumed tag afresh. Only a receipted TRANSPORT_FAILURE (it has no answer) leaves
            # the next tag as allowance; the answer of any other consumed attempt cannot be recovered here.
            if not should_retry(consumed[tag]):
                accounting.stop("consumed_attempt_without_record", {"record_id": item["record_id"], "tag": tag,
                                "recovery": "reconcile explicitly; a consumed attempt is never rerun"})
                raise LaneStopped(accounting.summary()["stopped"])
            rec["attempts"].append(consumed[tag])
            continue
        try:
            ticket = accounting.reserve(out_dir, item["record_id"], split, tag)
        except LaneStopped as exc:
            # Nothing dispatched in this invocation: the item stays as the restore accepted it. A removable HOLD
            # never turns an open retry into a final miss either: the receipted a1 resumes with its a2 allowance.
            if not dispatched_here or isinstance(exc, LaneHeld):
                raise
            rec["retry_suppressed_by_lane_stop"] = str(exc)
            break
        dispatched_here = True
        try:
            attempt, answer = one_process(model, system, prompt, private_dir, tag)
            rec["attempts"].append(attempt)
            accounting.complete_attempt(ticket, attempt)
        except BaseException:
            # DISPATCH remains durable: a subsequent invocation must recover or stop.
            accounting.stop("dispatch_interrupted", {"record_id": item["record_id"], "tag": tag})
            raise
        if not should_retry(attempt):
            break
    final = rec["attempts"][-1]   # both tags consumed: finalised from the receipts, without a dispatch
    parsed = parse_candidates_audit(answer, item)
    attempt_class = derived_attempt_class(final)
    structured = final.get("structured_output")
    rec.update({"finished_utc": now(), "attempt_class": attempt_class,
                "valid_protocol": final["valid_protocol"] is True and attempt_class == "VALID_ANSWER",
                "transport_failure": attempt_class == "TRANSPORT_FAILURE",
                "candidates": parsed["candidates"], "candidate_parse": parsed, "answer_sha256": sha(answer),
                # Recorded, never scored: the CLI's structured output agrees with the parser's raw candidates or it does not.
                "structured_output_consistent": (structured.get("candidates") == parsed["raw_candidates"]) if isinstance(structured, dict) else None,
                "hard_stop": final["hard_stop"], "stop_reason": (final.get("usage") or {}).get("stop_reason")})
    try:
        accounting.write_record(out_dir, rec, answer)
    except BaseException:
        accounting.stop("record_finalization_interrupted", {"record_id": item["record_id"]})
        raise
    if final.get("auth_unavailable") is True:
        # A dead login answers every item with the same zero-turn error: the item's allowance is spent (call plus retry),
        # then the lane stops durably so the next item cannot spend its own. Log in again, then remove STOP.json explicitly.
        accounting.stop("auth_unavailable", {"record_id": item["record_id"], "tag": final.get("tag"), "error": final.get("result_error"),
                        "auth_marker": final.get("auth_marker"), "saw_result_event": final.get("saw_result_event"),
                        "recovery": "log in (`agy`), verify with a canary, then retire STOP.json explicitly"})
    return rec

def refuse_if_held():
    """B.4: no start under EXP/HOLD.json, and without a trace: no lock, no PID file, no dispatch."""
    path = os.path.join(EXP, HOLD_NAME)
    if os.path.exists(path):
        raise LaneHeld("HOLD.json present: no new dispatch (%s)" % path)

def require_cli_version():
    """Refuse to dispatch against a CLI other than the frozen one; an auto-update drifts the served identity silently."""
    observed = cli_version()
    assert "agy " + observed == VERSION, "agy version drift: expected %r, `agy --version` printed %r" % (VERSION, observed)
    return observed

@contextlib.contextmanager
def pid_file(lane, details):
    """lane/RUNNER_PID.json, written by the owner of the lane lock only; marked EXITED on the way out, never deleted.

    To stop a lane, create EXP/HOLD.json (in-flight attempts finish and are charged). SIGTERM to this pid is treated
    like Ctrl-C: the lane stops, queued work is cancelled and no provider process is left behind.
    """
    path = os.path.join(lane, PID_NAME)
    state = {"pid": os.getpid(), "pgid": os.getpgid(0), "host": os.uname().nodename, "started_utc": now(), "status": "RUNNING", **details}
    atomic_json(path, state)
    try:
        yield path
    finally:
        atomic_json(path, {**state, "status": "EXITED", "exited_utc": now()})

def main():
    def terminate(signum, frame):
        raise KeyboardInterrupt("termination signal %s" % signum)
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["freeze", "canary", "run"])
    ap.add_argument("--model", default=MODEL); ap.add_argument("--split", choices=["pilot", "evaluation"]); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--approved-freeze"); ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if a.cmd == "freeze":
        h, parts = freeze_hash(); print(json.dumps({"freeze_sha256": h, "files": parts}, indent=1)); return
    assert a.model in MODELS, "unknown model"
    refuse_if_held()
    require_cli_version()
    signal.signal(signal.SIGTERM, terminate)
    system = read("prompt_system.txt").strip()
    lane = os.path.join(EXP, "runs", safe(a.model))
    if a.cmd == "canary":
        item = {"record_id": "CANARY_not_corpus",
                "lines": [["P1", "A remark about sums of odd numbers"], [1, "Let a and b be odd integers, say a = 2j + 1 and b = 2k + 1."],
                          [2, "Then a + b = 2(j + k + 1)."], [3, "Hence a + b is odd, because it is a sum of odd numbers."], [4, "In particular a + b is never zero modulo 2... "],
                          [5, "This finishes the remark."]]}
        # A synthetic harness canary may precede adjudication/final freeze. Bind its
        # actual design bytes, keep it outside outcomes, and charge it to this lane.
        try:
            h, _ = freeze_hash()
        except FileNotFoundError:
            h = sha(json.dumps({name: sha(read(name)) for name in FROZEN_FILES}, sort_keys=True))
        out_dir = os.path.join(EXP, "canary", safe(a.model))
        with exclusive_lock(os.path.join(EXP, ".cli_processes.lock")):
            # The lane cap binds active cost plus archived carryover; without CARRYOVER.json the lane refuses to run.
            with LaneAccounting(EXP, a.model, h, LANE_CAP, UNKNOWN_USAGE_CHARGE, PER_CALL_CAP,
                                MAX_CONSECUTIVE_TRANSPORT_FAILURES, require_carryover=True) as accounting:
                if os.path.exists(os.path.join(out_dir, "record.json")):
                    rec = json.load(open(os.path.join(out_dir, "record.json")))
                else:
                    with pid_file(lane, {"cmd": "canary", "model": a.model, "freeze_sha256": h}):
                        rec = call_record(a.model, item, system, out_dir,
                                          os.path.join(EXP, "private", "canary", safe(a.model)), accounting, "canary")
        final = rec["attempts"][-1]
        checks = final.get("protocol_checks") or {}   # a reconciled (interrupted) attempt has none
        print(json.dumps({k: rec.get(k) for k in ("attempt_class", "valid_protocol", "candidates", "total_attributable_tokens", "transport_failure",
                                                  "structured_output_consistent")}), checks,
              {k: final.get(k) for k in ("served_model", "num_turns", "tool_steps_observed", "agent_response_steps", "init", "result_status", "result_error")})
        assert checks.get("served_model_equals_requested") and checks.get("exactly_one_turn") and checks.get("no_tool_steps"), "canary protocol check failed"
        return
    h, _ = freeze_hash()
    assert a.approved_freeze == h, "freeze hash mismatch: design files changed after the freeze"
    assert 1 <= a.workers <= 5
    assert a.split is not None, "run requires --split"
    assert a.limit is None or a.limit > 0, "--limit must be positive"
    items = load_items(a.split)
    if a.limit: items = items[:a.limit]
    # Lock all CLI lanes as well as this model: the frozen schedule is sequential
    # lanes, each with at most five simultaneous physical processes.
    with exclusive_lock(os.path.join(EXP, ".cli_processes.lock")):
        # The lane cap binds active cost plus archived carryover; without CARRYOVER.json the lane refuses to run.
        with LaneAccounting(EXP, a.model, h, LANE_CAP, UNKNOWN_USAGE_CHARGE, PER_CALL_CAP, MAX_CONSECUTIVE_TRANSPORT_FAILURES,
                            require_carryover=True) as accounting, pid_file(lane, {"cmd": "run", "model": a.model, "split": a.split,
                                                                                   "workers": a.workers, "freeze_sha256": h}):
            if a.split == "evaluation":
                accounting.pilot_gate(load_items("pilot"))
            todo = [it for it in items if not os.path.exists(os.path.join(lane, safe(it["record_id"]), "record.json"))]
            print(now(), "lane", a.model, a.split, "todo", len(todo), "of", len(items), "accounting", accounting.summary(), flush=True)
            def work(it):
                try:
                    return call_record(a.model, it, system, os.path.join(lane, safe(it["record_id"])),
                                       os.path.join(EXP, "private", safe(a.model), safe(it["record_id"])), accounting, a.split)
                except LaneStopped:
                    return None
            with ThreadPoolExecutor(max_workers=a.workers) as ex:
                futures = []
                try:
                    for it in todo:
                        futures.append(ex.submit(work, it))
                    for future in futures:
                        future.result()
                except BaseException:
                    # Stop before executor teardown waits on in-flight work. Queued
                    # workers then cannot start calls after a main-thread interrupt.
                    accounting.stop("runner_interrupted")
                    for future in futures:
                        future.cancel()
                    raise
            accounting.hold_reason()   # refresh `held`: a lane that ran into a HOLD or a STOP is not reported as complete
            state = accounting.summary()
            missing = sum(not os.path.exists(os.path.join(lane, safe(it["record_id"]), "record.json")) for it in items)
            atomic_json(os.path.join(lane, "LANE_%s.json" % a.split),
                        {"split": a.split, "finished_utc": now(), "records_missing": missing, **state})
            print(now(), "lane stopped" if state["stopped"] else "lane held" if state["held"] else "lane finished",
                  "records missing", missing, state, flush=True)

if __name__ == "__main__": main()
