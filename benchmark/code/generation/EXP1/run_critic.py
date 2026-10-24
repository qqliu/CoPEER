#!/usr/bin/env python3
"""Certified-claim localization v2: tool-free critic runner (Claude CLI lanes).

One critic call = one `claude -p` process in a fresh empty directory outside the repository, system prompt replaced,
no tools, no MCP servers, no settings, no slash commands, every CLAUDE*/ANTHROPIC* variable of the launching session removed.
One attempt per record. A call is repeated once only when the stream shows no assistant message and no result event
(transport failure); the repeat is recorded. Records that already have a record.json are never run again.

v4: every attempt carries attempt_class (V4_SPEC.md). The output budget is a condition on ONE provider request. The CLI
answers a request that ends at its limit with a continuation turn ("Output token limit hit. Resume directly"), i.e. a second
request, and used to report the sum as one valid answer. The runner therefore kills the process group the moment a second
request shows (CONTRACT_VIOLATION) or the live output estimate of the first request exceeds MAX_OUTPUT (BUDGET_EXHAUSTED),
and validates the native usage fail-closed afterwards. A DISPATCH receipt consumes a physical attempt: a resumed item skips
its receipted tags and keeps only the allowance it had left. EXP/HOLD.json refuses a start and every further reservation.

  python3 -B run_critic.py freeze                      # print the freeze hash of the design files
  python3 -B run_critic.py canary --model M            # one call on a synthetic non-corpus text (harness check)
  python3 -B run_critic.py run --model M --split pilot|evaluation --workers N --approved-freeze SHA
"""
import argparse, contextlib, json, os, queue, signal, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MAX_OUTPUT, FROZEN_FILES, build_prompt, freeze_hash, load_items, parse_candidates_audit, read, safe, sha  # noqa: E402
from lane_accounting import (HOLD_NAME, MAX_PHYSICAL_ATTEMPTS, LaneAccounting, LaneHeld, LaneStopped, atomic_json,  # noqa: E402
                             attempt_receipts, derived_attempt_class, exclusive_lock)

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
EXECUTABLE = "<user-home>/.nvm/versions/node/v24.16.0/bin/claude"
MODELS = ("claude-haiku-4-5-20251001", "claude-sonnet-5", "claude-opus-5")
EFFORT = "medium"           # frozen for every Claude lane
PER_CALL_CAP = 120000       # attributable tokens per call (largest item is about 20k input tokens)
LANE_CAP = 10000000         # 285 x (20k largest prompt + 8k output) x 1.25, attributable tokens per model lane
UNKNOWN_USAGE_CHARGE = 40000  # charged to the lane when a call ends without native usage
CLIENT_LIMIT_NOTICE_PREFIX = "Output token limit hit."   # exact prefix of the client notice in all four archived two-request streams
LIMIT_NOTICE_MIN_SHARE = 0.9    # the notice counts as budget exhaustion only with a live first-request estimate >= 90% of MAX_OUTPUT
DRAIN_SECONDS = 5               # bounded read of already-buffered events after a controlled kill
WALL_CAP = 600              # seconds per call (v3 addendum: doubled with the output cap, for every lane)
MAX_CONSECUTIVE_TRANSPORT_FAILURES = 10
ATTEMPT_TAGS = ("a1", "a2_transport_retry")   # the call and its single transport retry; a third tag does not exist
assert len(ATTEMPT_TAGS) == MAX_PHYSICAL_ATTEMPTS
PID_NAME = "RUNNER_PID.json"  # lane/RUNNER_PID.json: the process an operator signals; SIGTERM drains like Ctrl-C
SCRATCH =os.environ.get("CCL_SCRATCH") or "<scratch-workdirs>"

def argv_for(model):
    return [EXECUTABLE, "-p", "--model", model, "--effort", EFFORT, "--safe-mode", "--tools", "", "--disallowed-tools", "*",
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--setting-sources", "",
            "--permission-mode", "dontAsk", "--permission-prompts", "none", "--disable-slash-commands",
            "--output-format", "stream-json", "--verbose", "--no-session-persistence", "--prompt-suggestions", "false"]

# CLAUDE_CODE_MAX_OUTPUT_TOKENS is a per-request CLIENT limit, never a guaranteed hard cap on a call: the CLI may open a
# further request, each with the same limit. The budget is enforced by the stream controls and the native validation below.
CONTROLS = {"CLAUDE_CODE_MAX_OUTPUT_TOKENS": str(MAX_OUTPUT), "CLAUDE_CODE_EXTRA_BODY": "{}", "CLAUDE_CODE_EFFORT_LEVEL": EFFORT,
            "CLAUDE_CODE_DISABLE_TERMINAL_TITLE": "1", "CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION": "false",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1"}

def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def count(value):
    """A token count from the stream; anything a stream should never carry there is 0, not a crash."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < float("inf"): return 0
    return int(value)

def message_text(message):
    content = (message or {}).get("content")
    if isinstance(content, str): return content
    return "".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")

def environment():
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDE") or k.startswith("ANTHROPIC") or k == "MAX_THINKING_TOKENS")}
    env.update(CONTROLS)
    return env

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
    start = time.monotonic()
    with open(os.path.join(private_dir, "stderr_%s.txt" % tag), "w") as stderr:
        proc = subprocess.Popen(argv_for(model) + ["--system-prompt", system], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=stderr, cwd=workdir, env=environment(), text=True, start_new_session=True)
    active.append(proc)
    def send_prompt():
        # A stuck reader must not disable the wall-clock watchdog.
        try:
            proc.stdin.write(prompt)
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
    requests, order, thinking, first_thinking = {}, [], 0, 0
    init = result = stop = None
    texts, continuations = [], []
    raw = open(os.path.join(private_dir, "events_%s.private.jsonl" % tag), "w")
    def running(include_estimate=True):
        tot = 0
        for i, rid in enumerate(order):
            u = requests[rid]; out = count(u.get("output_tokens"))
            if include_estimate and i == len(order) - 1: out = max(out, thinking)
            tot += count(u.get("input_tokens")) + count(u.get("cache_creation_input_tokens")) + count(u.get("cache_read_input_tokens")) + out
        return tot if order else (thinking if include_estimate else 0)
    def first_output():
        # Live output estimate of the FIRST request: its reported output tokens or the CLI's thinking estimate, whichever is larger.
        return max(count(requests[order[0]].get("output_tokens")) if order else 0, first_thinking)
    def limit_notice():
        return bool(continuations) and all(text.startswith(CLIENT_LIMIT_NOTICE_PREFIX) for text in continuations)
    def unexpected_user_turn():
        # Exact repeated notices may be duplicate client events; retain/count every copy. A different follow-up is not a duplicate.
        return bool(continuations) and (not limit_notice() or any(text != continuations[0] for text in continuations[1:]))
    def second_request():
        # A second message id, or (earlier) the user turn the CLI injects to continue a request that ended at its limit:
        # a tool-free single-prompt call has no user event after its assistant message.
        return "second_message_id" if len(order) > 1 else "continuation_user_event" if continuations else None
    def consume(line):
        nonlocal init, result, thinking, first_thinking
        raw.write(line); raw.flush()
        try: ev = json.loads(line)
        except ValueError: return
        if not isinstance(ev, dict): return
        kind, sub = ev.get("type"), ev.get("subtype")
        if kind == "system" and sub == "init": init = ev
        elif kind == "system" and sub == "thinking_tokens":
            thinking = max(thinking, count(ev.get("estimated_tokens")))
            if not second_request(): first_thinking = max(first_thinking, thinking)
        elif kind == "assistant":
            msg = ev.get("message") or {}; rid = msg.get("id") or "unknown"
            if rid not in requests:
                order.append(rid)
                if len(order) > 1: thinking = 0
            requests[rid] = dict(msg.get("usage") or {}); requests[rid]["_model"] = msg.get("model")
            if rid == order[0]:   # the text of a second request is never the answer of this attempt
                texts.append(message_text(msg))
        elif kind == "user" and order: continuations.append(message_text(ev.get("message")))
        elif kind == "result": result = ev
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
        # Controlled stops, in this order: a second request is a violation whatever the first one spent; the budget is
        # the FIRST request's alone, so it is judged only while no second request has shown.
        if stop is None and len(order) > 1:
            stop = {"reason": "contract_violation", "detail": "second_provider_request", "evidence": "second_message_id",
                    "first_request_output_estimate_at_kill": first_output(), "killed_process_group": True}
            if continuations: stop["continuation_text"] = continuations[0][:200]
        elif stop is None and continuations:
            # The client's output-limit notice is an ADDITIONAL, pinned criterion for budget exhaustion ([coordination reference removed]): the exact
            # notice prefix AND a live first-request output estimate of at least 90% of the budget. Anything else is a violation.
            # This stop does NOT prove that no second provider request started: a message id is not a request-start receipt.
            exhausted = not unexpected_user_turn() and first_output() >= LIMIT_NOTICE_MIN_SHARE * MAX_OUTPUT
            stop = {"reason": "output_budget_exhausted" if exhausted else "contract_violation",
                    "detail": ("client_output_limit_notice_with_budget_evidence" if exhausted else
                               "limit_notice_without_budget_evidence" if limit_notice() else "unexpected_user_turn"),
                    "evidence": "continuation_user_event", "continuation_text": continuations[0][:200],
                    "first_request_output_estimate_at_kill": first_output(), "required_estimate": int(LIMIT_NOTICE_MIN_SHARE * MAX_OUTPUT),
                    "second_request_not_excluded": True, "killed_process_group": True}
            if exhausted: stop["exhaustion_evidence_source"] = "inferred_client_limit_exhaustion"
        elif stop is None and first_output() > MAX_OUTPUT:
            stop = {"reason": "output_budget_exhausted", "detail": "live_output_estimate_exceeded_max_output",
                    "live_output_estimate_at_kill": first_output(), "thinking_estimate_at_kill": first_thinking,
                    "reported_output_tokens_at_kill": count(requests[order[0]].get("output_tokens")) if order else 0,
                    "max_output_tokens": MAX_OUTPUT, "killed_process_group": True,
                    "exhaustion_evidence_source": "live_output_estimate", "second_request_not_excluded": True}
        elif stop is None and running() > PER_CALL_CAP: stop = {"reason": "per_call_token_cap", "running_total_at_kill": running()}
        elif stop is None and elapsed > WALL_CAP: stop = {"reason": "wall_clock_cap", "elapsed_seconds": round(elapsed, 1)}
        if stop is not None:
            try: os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            # Bounded drain ([coordination reference removed]): the pump may already hold later events. They are preserved and parsed, and an observed
            # second message id or native overrun outranks the stop decided above. No further stop is decided here.
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
    fields = ("inputTokens", "cacheCreationInputTokens", "cacheReadInputTokens", "outputTokens")
    rows = (result or {}).get("modelUsage")
    native = isinstance(rows, dict) and rows and all(isinstance(r, dict) and all(isinstance(r.get(k), int) and not isinstance(r.get(k), bool) and r.get(k) >= 0 for k in fields) for r in rows.values())
    rec = {"tag": tag, "wall_seconds": round(time.monotonic() - start, 1), "exit_code": proc.returncode, "hard_stop": stop,
           "provider_requests_observed": len(order), "continuation_user_events": len(continuations), "events_drained_after_kill": drained,
           "continuation_user_event_sha256": [sha(text) for text in continuations],
           "identical_limit_notice_repeats": len(continuations) - 1 if limit_notice() and not unexpected_user_turn() else 0,
           "drain_eof_observed": stream_eof if drain_required else None, "stream_reader_error": reader_error,
           "controlled_drain_required": drain_required, "drain_deadline_expired": drain_deadline_expired,
           "controlled_drain_complete": stream_eof and reader_error is None if drain_required else None,
           "first_request_output_estimate": first_output(), "saw_assistant_message": bool(order), "saw_result_event": result is not None,
           "response_models": sorted({u.get("_model") for u in requests.values() if u.get("_model")}),
           "init": ({k: init.get(k) for k in ("model", "claude_code_version", "tools", "mcp_servers", "slash_commands", "permissionMode", "apiKeySource")} if init else None)}
    if result is not None and native:
        native_total = sum(sum(r[k] for k in fields) for r in rows.values())
        rec["usage_known"] = stream_eof and reader_error is None
        rec["usage"] = {"total_attributable_tokens": native_total if rec["usage_known"] else None,
                        "per_model": {m: {k: r.get(k) for k in fields} for m, r in rows.items()},
                        "stop_reason": result.get("stop_reason"), "is_error": result.get("is_error"), "num_turns": result.get("num_turns")}
        if not rec["usage_known"]:
            rec["usage"].update(observed_lower_bound=max(native_total, running(False)), running_estimate_at_end=running())
            rec["budget_charge_tokens"] = max(UNKNOWN_USAGE_CHARGE, native_total, running())
        # The result text is the answer only for a single, uncontinued request; after a drain it may belong to a second request.
        answer = result.get("result") if isinstance(result.get("result"), str) and len(order) == 1 and not continuations else "".join(texts)
    else:
        rec["usage_known"] = False
        rec["usage"] = {"total_attributable_tokens": None, "observed_lower_bound": running(False),
                        "running_estimate_at_end": running()}
        rec["budget_charge_tokens"] = max(UNKNOWN_USAGE_CHARGE, running())
        answer = "".join(texts)
    if native and native_total > PER_CALL_CAP:
        stop = {"reason": "per_call_token_cap", "final_native_total": native_total}
    stop_reason = result.get("stop_reason") if result is not None else None
    # Judged per model row and even when another field of the row is malformed: one request may not exceed MAX_OUTPUT.
    over_budget = {m: r.get("outputTokens") for m, r in rows.items()
                   if isinstance(r, dict) and count(r.get("outputTokens")) > MAX_OUTPUT} if isinstance(rows, dict) else {}
    checks = {
        "no_tools_and_no_mcp_servers_in_init": bool(init) and not (init.get("tools") or []) and not (init.get("mcp_servers") or []),
        "response_model_equals_requested": rec["response_models"] == [model],
        "exactly_one_provider_request": len(order) == 1, "no_continuation_user_event": not continuations,
        "stream_reader_completed": stream_eof and reader_error is None,
        "exit_code_zero": proc.returncode == 0, "final_result_event_with_native_usage": rec["usage_known"],
        "native_output_within_max_output": bool(native) and not over_budget,
        "natural_stop_reason": stop_reason == "end_turn", "result_not_flagged_error": bool(result) and result.get("is_error") is not True}
    # Fail-closed classification (V4_SPEC.md shared definitions). The listed violations outrank everything else; whatever
    # fits no other class is a violation too, never a valid answer and never a retry.
    violations = [name for name, found in (
        ("second_provider_request", len(order) > 1),
        ("stream_reader_failure", reader_error is not None),
        ("controlled_drain_incomplete", drain_required and not (stream_eof and reader_error is None)),
        ("unexpected_user_turn", unexpected_user_turn()),
        ("limit_notice_without_budget_evidence", limit_notice() and first_output() < LIMIT_NOTICE_MIN_SHARE * MAX_OUTPUT),
        ("native_output_tokens_exceed_max_output", bool(over_budget)),
        ("tools_or_mcp_servers_present", bool(init) and not checks["no_tools_and_no_mcp_servers_in_init"]),
        ("wrong_response_model", bool(rec["response_models"]) and not checks["response_model_equals_requested"]),
        ("result_flagged_error", result is not None and result.get("is_error") is True)) if found]
    if violations:
        attempt_class, runner_stop = "CONTRACT_VIOLATION", stop
        stop = dict(stop) if stop is not None and stop["reason"] == "contract_violation" else {"reason": "contract_violation"}
        stop.update(detail=violations[0], violations=violations)
        if runner_stop is not None and runner_stop["reason"] != "contract_violation": stop["runner_stop"] = runner_stop
        if over_budget: stop.update(native_output_tokens=over_budget, max_output_tokens=MAX_OUTPUT)
    elif stop is not None and stop["reason"] == "output_budget_exhausted":
        attempt_class = "BUDGET_EXHAUSTED"    # no second request observed in a complete drain; unobserved starts remain possible
    elif not order and result is None and (stop is None or stop["reason"] == "wall_clock_cap"):
        attempt_class = "TRANSPORT_FAILURE"   # nothing observed, including a wall-cap kill before any output
    elif stop is None and len(order) == 1 and stop_reason == "max_tokens":
        attempt_class = "BUDGET_EXHAUSTED"    # exactly one request that ended at the budget: a legitimate intention-to-treat miss
        stop = {"reason": "output_budget_exhausted", "detail": "stop_reason_max_tokens", "stop_reason": stop_reason,
                "native_output_tokens": {m: r["outputTokens"] for m, r in rows.items()} if native else None, "max_output_tokens": MAX_OUTPUT,
                "exhaustion_evidence_source": "native_max_tokens"}
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
               exhaustion_evidence_source=stop.get("exhaustion_evidence_source") if attempt_class == "BUDGET_EXHAUSTED" else None,
               native_stop_verified=stop.get("exhaustion_evidence_source") == "native_max_tokens" if attempt_class == "BUDGET_EXHAUSTED" else None,
               second_request_not_excluded=stop.get("second_request_not_excluded", False) if attempt_class == "BUDGET_EXHAUSTED" else None)
    return rec, answer or ""

def should_retry(attempt):
    """The single transport retry: only a TRANSPORT_FAILURE, never an observed answer/result, a spent budget or a violation."""
    if "attempt_class" in attempt:
        return attempt["attempt_class"] == "TRANSPORT_FAILURE"
    # A receipt older than v4 carries no class: the original predicate.
    return (not attempt["saw_assistant_message"] and not attempt["saw_result_event"]
            and (attempt["hard_stop"] is None or attempt["hard_stop"].get("reason") == "wall_clock_cap"))


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
    rec = {"record_id": item["record_id"], "requested_model": model, "effort": EFFORT, "max_output_tokens_per_request": MAX_OUTPUT,
           "per_call_cap": PER_CALL_CAP, "wall_cap_seconds": WALL_CAP, "prompt_sha256": sha(prompt), "system_prompt_sha256": sha(system),
           "environment_overrides": CONTROLS, "started_utc": now(), "split": split,
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
    rec.update({"finished_utc": now(), "attempt_class": attempt_class,
                "valid_protocol": final["valid_protocol"] is True and attempt_class == "VALID_ANSWER",
                "transport_failure": attempt_class == "TRANSPORT_FAILURE",
                "candidates": parsed["candidates"], "candidate_parse": parsed, "answer_sha256": sha(answer),
                "hard_stop": final["hard_stop"], "stop_reason": final["usage"].get("stop_reason")})
    try:
        accounting.write_record(out_dir, rec, answer)
    except BaseException:
        accounting.stop("record_finalization_interrupted", {"record_id": item["record_id"]})
        raise
    return rec

def refuse_if_held():
    """B.4: no start under EXP/HOLD.json, and without a trace: no lock, no PID file, no dispatch."""
    path = os.path.join(EXP, HOLD_NAME)
    if os.path.exists(path):
        raise LaneHeld("HOLD.json present: no new dispatch (%s)" % path)

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
    ap.add_argument("--model"); ap.add_argument("--split", choices=["pilot", "evaluation"]); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--approved-freeze"); ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if a.cmd == "freeze":
        h, parts = freeze_hash(); print(json.dumps({"freeze_sha256": h, "files": parts}, indent=1)); return
    assert a.model in MODELS, "unknown model"
    refuse_if_held()
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
        checks = rec["attempts"][-1].get("protocol_checks") or {}   # a reconciled (interrupted) attempt has none
        print(json.dumps({k: rec.get(k) for k in ("attempt_class", "valid_protocol", "candidates", "total_attributable_tokens", "transport_failure")}), checks, rec["attempts"][-1].get("response_models"))
        assert checks.get("response_model_equals_requested") and checks.get("exactly_one_provider_request"), "canary protocol check failed"
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
