#!/usr/bin/env python3
"""Certified-claim localization v4: tool-free critic runner for the Codex CLI lane (gpt-5.6-luna).

One critic call = one `codex exec` process through the pinned transport astra_cli.py: bubblewrap sandbox, fresh ephemeral
thread, no repository, no home, no inherited environment, a single-entry projected model catalog with every tool disabled,
deny-all filesystem and network for the model, the system prompt as the model-instructions file and the user prompt on stdin
byte-for-byte (verified model-free before every call). One attempt per record. A call is repeated once only when the process
showed nothing from the model and no completed turn (transport failure); the repeat is recorded. Records that already have a
record.json are never run again.

Contract-equivalent to run_critic.py (Claude CLI lanes): same prompts, reservations, epoch authorization, DISPATCH/ATTEMPT/
record receipts, attempt classes, technical gate, HOLD/STOP handling and PID file; should_retry, consumed_attempts,
refuse_if_held and pid_file are copied verbatim (run_critic.py is frozen, so nothing is factored out of it). What differs is
the evidence: the codex JSONL stream has no live output estimate and no per-request message ids, so nothing is killed mid-
stream; every attempt is judged fail-closed afterwards from the complete raw event stream, the transport report and the
native turn.completed usage.

OUTPUT CAP (model-free finding of 2026-09-22, re-proved by the lane preflight before every canary/run): codex-cli 0.155.1
has no client-side output cap and no configuration that bounds the provider-side output. `-c model_max_output_tokens=16000`
is refused by --strict-config ("unknown configuration field"), the string does not occur in the binary, the bundled catalog
entry carries no output limit, and the Responses request body captured by the transport's rejecting loopback route carries no
max-output field (top-level keys: client_metadata, include, input, model, parallel_tool_calls, prompt_cache_key, reasoning,
store, stream, text, tool_choice). OUTPUT_CAP_ENFORCED_BY_PROVIDER is therefore False: native output > MAX_OUTPUT is
BUDGET_EXHAUSTED (charged, intention-to-treat miss, never retried), not a violation. Were a captured request ever to carry
max_output_tokens == MAX_OUTPUT, the constant would be True and an overrun a CONTRACT_VIOLATION (the cap was requested and not
honoured); the preflight refuses to start when the captured request disagrees with the constant.

  python3 -B run_codex.py freeze                       # print the freeze hash of the design files
  python3 -B run_codex.py canary --model M             # one call on a synthetic non-corpus text (harness check)
  python3 -B run_codex.py run --model M --split pilot|evaluation --workers N --approved-freeze SHA
"""
import argparse, collections, contextlib, importlib.util, json, os, signal, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MAX_OUTPUT, FROZEN_FILES, build_prompt, freeze_hash, load_items, parse_candidates_audit, read, safe, sha  # noqa: E402
from lane_accounting import (HOLD_NAME, MAX_PHYSICAL_ATTEMPTS, LaneAccounting, LaneHeld, LaneStopped, atomic_json,  # noqa: E402
                             attempt_receipts, derived_attempt_class, exclusive_lock)

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
TRANSPORT_PATH = "<repository>/qedbench_certificate_availability_triage/cli_transport/transport.py"
TRANSPORT_SHA256 = "38e66e95f2d77849e48451c8a6ba969370cb9c7605ce370ee0d36bdf4b0cd5c2"   # the reviewed transport; other bytes refuse to load
EXECUTABLE = "<user-home>/.nvm/versions/node/v24.16.0/bin/codex"   # the transport resolves codex.js to the vendored native binary
MODELS = ("gpt-5.6-luna",)
EFFORT = "medium"           # frozen for this lane, like every Claude lane
VERSION = "codex-cli 0.155.1"   # what `codex --version` prints inside the sandbox; the transport refuses any other build
PER_CALL_CAP = 120000       # attributable tokens per call (largest item is about 20k input tokens)
LANE_CAP = 10000000         # attributable tokens per model lane, cumulative over canary, pilot, evaluation and carryover
UNKNOWN_USAGE_CHARGE = 40000  # charged to the lane when a call ends without native usage
WALL_CAP = 600              # seconds for the provider call; the transport's model-free checks keep their own 30 s / 45 s limits
MAX_CONSECUTIVE_TRANSPORT_FAILURES = 10
ATTEMPT_TAGS = ("a1", "a2_transport_retry")   # the call and its single transport retry; a third tag does not exist
assert len(ATTEMPT_TAGS) == MAX_PHYSICAL_ATTEMPTS
PID_NAME = "RUNNER_PID.json"  # lane/RUNNER_PID.json: the process an operator signals; SIGTERM drains like Ctrl-C
PREFLIGHT_NAME = "TRANSPORT_PREFLIGHT.json"   # lane/transport_preflight_<ns>/TRANSPORT_PREFLIGHT.json: the model-free proof of this invocation
OUTPUT_CAP_ENFORCED_BY_PROVIDER = False       # see the module docstring; the preflight refuses to start if the captured request disagrees
OUTPUT_CAP_REQUEST_FIELD = "max_output_tokens"   # the Responses API field the preflight looks for in the captured request body
INSPECTION_MIN_BYTES = 100000   # the transport takes its rejecting loopback route (captured request body) only from this prompt size
# The codex exec JSONL vocabulary the transport accepts for a tool-free text completion; anything else fails closed.
ALLOWED_EVENTS = frozenset({"thread.started", "turn.started", "item.started", "item.updated", "item.completed", "turn.completed"})
ALLOWED_ITEMS = frozenset({"agent_message", "reasoning"})
USAGE_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens")
EXHAUSTION_EVIDENCE_SOURCE = "native_output_tokens_over_budget"   # not a native stop; score.py lists this source (campaign integration 2026-09-22)
# What the transport does around every call (astra_cli.build_launch / config_arguments / complete); recorded on every record.
ISOLATION = {"sandbox": "bubblewrap --die-with-parent --new-session --unshare-pid --unshare-ipc --unshare-uts; /usr read-only, /proc, /dev, tmpfs /tmp; "
                        "vendored CLI read-only at /runtime/vendor, inputs read-only at /input, outputs at /output, empty /workspace and /isolated/home, tmpfs CODEX_HOME",
             "environment": "HOME=/isolated/home CODEX_HOME=/run/codex-home PATH=/runtime/vendor/codex-path:/usr/bin:/bin LANG=LC_ALL=C.UTF-8 NO_COLOR=1; "
                            "the launching session's environment is not inherited (the outer process runs the CLI with PATH, LANG and LC_ALL only)",
             "argv": "codex exec --strict-config --ignore-user-config --ignore-rules --skip-git-repo-check --ephemeral --model MODEL <-c config ...> "
                     "<--disable feature ...> --json --color never --cd /workspace --output-last-message /output/final.txt -",
             "model": "single-entry projected bundled catalog (tool_mode direct, shell disabled, apply_patch off, node repl off); approval never; "
                      "permissions text_only (filesystem deny all, network off); web search, plan, user-input, agents and apps off; no project docs, "
                      "no environment context, no skills; 32 features disabled (--disable), among them shell_tool, unified_exec, code_mode, "
                      "browser_use, computer_use, multi_agent, memories, plugins, hooks, unbounded_connection_retries",
             "auth": "ChatGPT login file mounted from a descriptor into the sandbox tmpfs; never read into a receipt, never hashed, never copied",
             "verification": "before every call: `codex --version`, `codex debug models --bundled` (catalog projection) and a model-free prompt "
                             "inspection (`debug prompt-input`, or the rejecting loopback capture for prompts of at least 100,000 bytes); "
                             "the call's native-binary hash and bundled catalog entry hash must equal the lane preflight's"}

TRANSPORT = None   # the loaded transport module; tests replace it with an in-memory fake


class TransportSetupFailure(RuntimeError):
    """The transport refused before any provider call (version, catalog, inspection, auth): a harness fault, not an outcome."""


def load_transport(path=TRANSPORT_PATH):
    """A fresh module object of the pinned transport bound to this lane's model, effort and version; never a shared import."""
    data = Path(path).read_bytes()
    if sha(data) != TRANSPORT_SHA256:
        raise RuntimeError("transport bytes differ from the reviewed transport (%s): %s" % (TRANSPORT_SHA256, path))
    spec = importlib.util.spec_from_file_location("ccl_codex_transport", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module   # dataclasses resolve string annotations through sys.modules
    spec.loader.exec_module(module)
    module.MODEL, module.EFFORT, module.VERSION = MODELS[0], EFFORT, VERSION
    # Provider retry overrides (-c model_providers.openai.request_max_retries=0 / stream_max_retries=0) are NOT appended to
    # config_arguments: codex-cli 0.155.1 --strict-config refuses them ("model_providers contains reserved built-in provider
    # IDs: `openai`. Built-in providers cannot be overridden."), proven model-free on the rejecting loopback route on
    # 2026-09-22 (LUNA_ADAPTER_NOTES.md, section 8). The CLI's own retry counts therefore apply to the one provider call.
    return module


def transport():
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = load_transport()
    return TRANSPORT


def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def count(value):
    """A token count from the stream; anything a stream should never carry there is None, not a crash."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0: return None
    return value

def preflight_prompt():
    """A synthetic non-corpus text in the frozen user template, long enough for the transport's loopback capture route."""
    lines = [["P1", "Transport preflight fixture: no response is requested from a model"]]
    lines += [[i, "filler line %04d of the preflight fixture, not corpus text" % i] for i in range(1, 2400)]
    prompt = build_prompt({"record_id": "PREFLIGHT_not_corpus", "lines": lines})
    assert len(prompt.encode("utf-8")) >= INSPECTION_MIN_BYTES
    return prompt

def catalog_statement(catalog, model):
    """Exactly what the bundled catalog says about the requested model: entries, their efforts, and every slug it lists."""
    models = catalog.get("models") if isinstance(catalog, dict) else None
    models = [m for m in models if isinstance(m, dict)] if isinstance(models, list) else []
    entries = [m for m in models if m.get("slug") == model]
    efforts = [x.get("effort") for m in entries for x in m.get("supported_reasoning_levels") or [] if isinstance(x, dict)]
    return {"requested_model": model, "entries": len(entries), "supported_efforts": efforts, "slugs": [m.get("slug") for m in models]}

def lane_preflight(destination, module=None):
    """The model-free proof of this invocation's transport, before any dispatch: version, bundled catalog, and the exact request
    body of this lane's configuration captured by the transport's rejecting loopback route (no auth mounted, no inference
    service, nothing leaves the host). Refuses on any disagreement with the pinned constants; nothing is written to the lane
    ledger, because a transport that cannot be proven is not a fault of the lane.
    """
    module = module or transport()
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    native = module.find_native_cli(EXECUTABLE)
    system = read("prompt_system.txt").strip()
    instructions, prompt, mapping = module.render_messages([{"role": "system", "content": system}, {"role": "user", "content": preflight_prompt()}])
    with tempfile.TemporaryDirectory(prefix="ccl-codex-preflight-") as temporary:
        temp = Path(temporary); inputs, outputs = temp / "inputs", temp / "outputs"; inputs.mkdir(); outputs.mkdir()
        version = module._run(module.build_launch(native, inputs, outputs, None, ["--version"]), timeout=30)
        observed_version = version.stdout.decode("utf-8", "replace").strip()
        if version.returncode != 0 or observed_version != VERSION:
            raise RuntimeError("native CLI version %r (exit %s) is not the pinned %r" % (observed_version, version.returncode, VERSION))
        catalog_result = module._run(module.build_launch(native, inputs, outputs, None, ["debug", "models", "--bundled"]), timeout=30)
        if catalog_result.returncode:
            raise RuntimeError("cannot read the bundled model catalog (exit %s)" % catalog_result.returncode)
        module._write_new(destination / "catalog_bundled.json", catalog_result.stdout)
        catalog = module._strict_json(catalog_result.stdout)
        statement = catalog_statement(catalog, module.MODEL)
        if statement["entries"] != 1 or EFFORT not in statement["supported_efforts"]:
            raise RuntimeError("bundled catalog does not list %s once with effort %s; the catalog says: %s" % (module.MODEL, EFFORT, json.dumps(statement)))
        projected, binding = module.project_catalog(catalog)
        module._write_json(inputs / "catalog.json", projected)
        module._write_new(inputs / "instructions.txt", instructions.encode("utf-8"))
        route = module.inspect_prompt(native, inputs, outputs, module.config_arguments(), instructions, prompt, destination)
    raw = (destination / "prompt_input.raw.json").read_bytes()
    body = module._strict_json(raw)
    if not isinstance(body, dict) or "input" not in body:
        raise RuntimeError("the inspection did not capture a request body (route %r); the prompt was below the loopback threshold?" % route)
    cap_value = body.get(OUTPUT_CAP_REQUEST_FIELD)
    cap_like = {k: body[k] for k in sorted(body) if any(word in k for word in ("max", "output", "token"))}
    enforced = cap_value == MAX_OUTPUT
    if enforced != OUTPUT_CAP_ENFORCED_BY_PROVIDER:
        raise RuntimeError("captured request %s=%r disagrees with OUTPUT_CAP_ENFORCED_BY_PROVIDER=%s (cap-like fields: %s)"
                           % (OUTPUT_CAP_REQUEST_FIELD, cap_value, OUTPUT_CAP_ENFORCED_BY_PROVIDER, json.dumps(cap_like)))
    if body.get("model") != module.MODEL or (body.get("reasoning") or {}).get("effort") != EFFORT or body.get("tools"):
        raise RuntimeError("captured request differs from the lane: model=%r reasoning=%r tools=%r" % (body.get("model"), body.get("reasoning"), body.get("tools")))
    receipt = {"status": "PASS", "model_calls": 0, "external_requests": 0, "authentication_mounted": False, "requested_model": module.MODEL,
               "effort": EFFORT, "cli_version": observed_version, "native_cli": str(native), "native_sha256": sha(native.read_bytes()),
               "transport_path": TRANSPORT_PATH, "transport_sha256": TRANSPORT_SHA256, "inspection_route": route, "message_mapping": mapping,
               "catalog": statement, "catalog_projection": binding, "request_body_keys": sorted(body), "request_sha256": sha(raw),
               "request_model": body.get("model"), "request_reasoning": body.get("reasoning"), "request_cap_like_fields": cap_like,
               "output_cap_request_field": OUTPUT_CAP_REQUEST_FIELD, "output_cap_request_value": cap_value,
               "output_cap_enforced_by_provider": OUTPUT_CAP_ENFORCED_BY_PROVIDER, "max_output_tokens": MAX_OUTPUT,
               "overrun_class": "CONTRACT_VIOLATION" if OUTPUT_CAP_ENFORCED_BY_PROVIDER else "BUDGET_EXHAUSTED",
               "prompt_bytes": len(prompt.encode("utf-8")), "completed_utc": now()}
    atomic_json(destination / PREFLIGHT_NAME, receipt)
    return receipt

PREFLIGHT = None   # the receipt of this invocation's lane preflight; every attempt records where its proof is

def stream_summary(raw):
    """Counts and texts of the complete raw event stream; undecodable lines are counted, never skipped silently."""
    events, undecodable = [], 0
    for line in raw.splitlines():
        if not line.strip(): continue
        try: ev = json.loads(line)
        except ValueError: undecodable += 1; continue
        if isinstance(ev, dict): events.append(ev)
        else: undecodable += 1
    kinds = collections.Counter(str(ev.get("type")) for ev in events)
    items = collections.Counter(str(ev["item"].get("type")) if isinstance(ev.get("item"), dict) else "missing"
                                for ev in events if str(ev.get("type")).startswith("item."))
    texts = [ev["item"].get("text") for ev in events if ev.get("type") == "item.completed"
             and isinstance(ev.get("item"), dict) and ev["item"].get("type") == "agent_message"]
    completed = [ev for ev in events if ev.get("type") == "turn.completed"]
    return {"events": events, "kinds": kinds, "items": items, "texts": texts, "completed": completed, "undecodable": undecodable}

def native_usage(completed):
    """The transport's rule (astra_cli.extract_usage): exactly one turn.completed whose three counts are non-negative integers,
    input and output both positive, cached input not above input. None otherwise: unknown, never zero."""
    if len(completed) != 1: return None
    value = completed[0].get("usage")
    if not isinstance(value, dict) or any(count(value.get(k)) is None for k in USAGE_KEYS): return None
    if value["input_tokens"] == 0 or value["output_tokens"] == 0 or value["cached_input_tokens"] > value["input_tokens"]: return None
    return {k: value[k] for k in USAGE_KEYS}

def one_process(model, system, prompt, private_dir, tag):
    """One sandboxed `codex exec` through the pinned transport; the receipt is judged from its artifacts afterwards.

    The transport makes at most one provider call, kills the process group at WALL_CAP, reads the pipes to EOF, and always
    writes report.json; an interruption propagates after the kill, exactly as in run_critic (DISPATCH stays for reconciliation).
    """
    module = transport()
    assert model == module.MODEL, "the pinned transport is bound to one model"
    if PREFLIGHT is None:
        raise TransportSetupFailure("no lane preflight bound to this invocation")
    os.makedirs(private_dir, exist_ok=True)
    artifact_dir = os.path.join(private_dir, "%s_%d" % (tag, time.time_ns()))   # the transport refuses to reuse a directory
    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
    start = time.monotonic(); completion = error = None
    try:
        completion = module.complete(messages, artifact_dir=artifact_dir, timeout=WALL_CAP, cli=EXECUTABLE, auth_path=None)
    except module.AstraCLIError as exc:
        error = str(exc)
    wall = round(time.monotonic() - start, 1)
    report_path = Path(artifact_dir, "report.json")
    if not report_path.exists():
        # The transport writes report.json in its `finally`; without one it raised before its call began (artifact
        # directory, message rendering): a harness fault reported with the transport's words, never a missing-file crash.
        raise TransportSetupFailure("transport raised before writing report.json: %s (artifacts: %s)" % (error, artifact_dir))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("cli_model_call_attempted") is not True:
        # Version, catalog, prompt inspection or auth refused before any provider call: a harness fault, never an outcome of
        # the item and never a retry. Like a process that could not be started, it stops the lane (dispatch_interrupted).
        raise TransportSetupFailure("transport refused before any provider call: %s (artifacts: %s)" % (report.get("error"), artifact_dir))
    events_path = Path(artifact_dir, "events.raw.jsonl")
    raw = events_path.read_bytes() if events_path.exists() else b""
    return judge_attempt(tag, report, raw, completion.text if completion is not None else None, error, wall, artifact_dir)

def judge_attempt(tag, report, raw, text, error, wall, artifact_dir):
    """Fail-closed classification of one finished attempt (V4_SPEC.md shared definitions) from complete evidence only."""
    stream = stream_summary(raw)
    kinds, items, texts, completed = stream["kinds"], stream["items"], stream["texts"], stream["completed"]
    observed = bool(items) or bool(completed)   # the model produced something, or the CLI completed a turn
    usage = native_usage(completed)
    exit_code = report.get("returncode")
    killed = exit_code == -signal.SIGKILL          # the transport's own timeout kill; any other kill is external
    stop = None
    if killed: stop = {"reason": "wall_clock_cap" if wall >= WALL_CAP else "process_killed", "elapsed_seconds": wall, "killed_process_group": True}
    rec = {"tag": tag, "wall_seconds": wall, "exit_code": exit_code, "hard_stop": stop, "artifact_dir": artifact_dir,
           "transport_status": report.get("status"), "transport_error": error, "transport_sha256": TRANSPORT_SHA256,
           "cli_version": report.get("cli_version"), "cli_sha256": report.get("cli_sha256"), "events_sha256": report.get("events_sha256"),
           "events_observed": dict(kinds), "items_observed": dict(items), "undecodable_event_lines": stream["undecodable"],
           "turns_completed": len(completed), "saw_assistant_message": bool(items), "saw_result_event": bool(completed),
           "provider_request_ids_available": False,   # the codex stream carries no message ids: a CLI-internal stream retry is unobservable
           "agent_message_sha256": [sha(t) for t in texts if isinstance(t, str)],
           "requested_model": report.get("model"), "requested_effort": report.get("reasoning_effort"),
           "model_identity_source": report.get("model_identity_source"), "catalog_projection": report.get("catalog_projection"),
           "model_free_prompt_inspection": report.get("model_free_prompt_inspection"),
           "output_cap_enforced_by_provider": OUTPUT_CAP_ENFORCED_BY_PROVIDER, "output_cap_request_field": OUTPUT_CAP_REQUEST_FIELD if OUTPUT_CAP_ENFORCED_BY_PROVIDER else None,
           "max_output_tokens_per_request": MAX_OUTPUT,
           "preflight_receipt": {**{k: PREFLIGHT.get(k) for k in ("request_sha256", "native_sha256", "cli_version")},
                                 "catalog_original_entry_sha256": (PREFLIGHT.get("catalog_projection") or {}).get("original_entry_sha256")} if PREFLIGHT else None}
    if usage is not None:
        total = usage["input_tokens"] + usage["output_tokens"]   # cached input is part of input_tokens and counted once (transport rule)
        rec["usage_known"] = True
        rec["usage"] = {"total_attributable_tokens": total, **usage, "stop_reason": None, "source": "codex exec JSONL turn.completed.usage"}
        rec["output_tokens"] = usage["output_tokens"]
    else:
        total = None
        rec["usage_known"] = False
        rec["usage"] = {"total_attributable_tokens": None, "observed_lower_bound": 0}   # the stream carries no partial counts
        rec["budget_charge_tokens"] = UNKNOWN_USAGE_CHARGE
    if total is not None and total > PER_CALL_CAP:
        stop = {"reason": "per_call_token_cap", "final_native_total": total}
    over_budget = usage is not None and usage["output_tokens"] > MAX_OUTPUT
    reported = report.get("usage") if isinstance(report.get("usage"), dict) else {}
    checks = {
        "exactly_one_completed_turn": (len(completed) == 1 and kinds.get("turn.started") == 1 and kinds.get("thread.started") == 1
                                       and stream["events"][-1] == completed[0]),
        "no_tool_or_unknown_items": all(kind in ALLOWED_ITEMS for kind in items),
        "no_unknown_event_types": all(kind in ALLOWED_EVENTS for kind in kinds) and stream["undecodable"] == 0,
        "requested_model_confirmed_by_catalog_projection": (report.get("model") == MODELS[0] and report.get("reasoning_effort") == EFFORT
                                                            and isinstance(report.get("catalog_projection"), dict)
                                                            and report.get("model_free_prompt_inspection") == "PASS"),
        "native_binary_and_catalog_match_preflight": (PREFLIGHT is not None and report.get("cli_sha256") == PREFLIGHT.get("native_sha256")
                                                      and isinstance(report.get("catalog_projection"), dict)
                                                      and report["catalog_projection"].get("original_entry_sha256")
                                                      == (PREFLIGHT.get("catalog_projection") or {}).get("original_entry_sha256")),
        "exit_code_zero": exit_code == 0, "final_result_event_with_native_usage": rec["usage_known"],
        "usage_agrees_with_transport_report": reported.get("total_tokens") == total,
        "final_text_present_and_matches_stream": isinstance(text, str) and bool(text.strip()) and bool(texts) and texts[-1] == text,
        "native_output_within_max_output": usage is not None and not over_budget,
        "transport_status_complete": report.get("status") == "COMPLETE" and error is None}
    # Fail-closed classification (V4_SPEC.md shared definitions). The listed violations outrank everything else; whatever
    # fits no other class is a violation too, never a valid answer and never a retry.
    violations = [name for name, found in (
        ("multiple_completed_turns", len(completed) > 1),
        ("tool_or_unknown_item", not checks["no_tool_or_unknown_items"]),
        ("unexpected_event_type", observed and not checks["no_unknown_event_types"]),
        ("wrong_requested_model_or_effort", not checks["requested_model_confirmed_by_catalog_projection"]),
        ("native_binary_or_catalog_differs_from_preflight", not checks["native_binary_and_catalog_match_preflight"]),
        ("native_usage_inconsistent", bool(completed) and usage is None),
        ("native_output_tokens_exceed_max_output", over_budget and OUTPUT_CAP_ENFORCED_BY_PROVIDER)) if found]
    if violations:
        attempt_class, runner_stop = "CONTRACT_VIOLATION", stop
        stop = {"reason": "contract_violation", "detail": violations[0], "violations": violations}
        if runner_stop is not None: stop["runner_stop"] = runner_stop
        if over_budget: stop.update(native_output_tokens=usage["output_tokens"], max_output_tokens=MAX_OUTPUT)
    elif over_budget and stop is None and all(passed for name, passed in checks.items() if name != "native_output_within_max_output"):
        attempt_class = "BUDGET_EXHAUSTED"    # one otherwise valid request that ran past the budget no provider-side cap bounds: an intention-to-treat miss
        stop = {"reason": "output_budget_exhausted", "detail": "native_output_tokens_exceed_max_output", "native_output_tokens": usage["output_tokens"],
                "max_output_tokens": MAX_OUTPUT, "exhaustion_evidence_source": EXHAUSTION_EVIDENCE_SOURCE,
                "output_cap_enforced_by_provider": False, "second_request_not_excluded": True}
    elif not observed:
        attempt_class = "TRANSPORT_FAILURE"   # nothing from the model and no completed turn, whatever the exit code or kill
    elif stop is None and all(checks.values()):
        attempt_class = "VALID_ANSWER"
    else:
        attempt_class = "CONTRACT_VIOLATION"  # a per-call/wall stop after output, an incomplete turn, a non-zero exit, unknown usage, ...
        if stop is None:
            stop = {"reason": "contract_violation", "detail": "protocol_check_failed",
                    "failed_checks": sorted(name for name, passed in checks.items() if not passed)}
    checks["no_hard_stop"] = stop is None
    rec.update(hard_stop=stop, attempt_class=attempt_class, transport_failure=attempt_class == "TRANSPORT_FAILURE",
               protocol_checks=checks, valid_protocol=attempt_class == "VALID_ANSWER",
               exhaustion_evidence_source=stop.get("exhaustion_evidence_source") if attempt_class == "BUDGET_EXHAUSTED" else None,
               native_stop_verified=False if attempt_class == "BUDGET_EXHAUSTED" else None,   # the model was never stopped; it ran past the budget
               second_request_not_excluded=stop.get("second_request_not_excluded", False) if attempt_class == "BUDGET_EXHAUSTED" else None)
    # The text exists only when the transport completed (one turn, no tools, final text equal to the stream); like run_critic it is
    # kept for audit whatever the class, and scored only under VALID_ANSWER.
    return rec, text if isinstance(text, str) else ""

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
           "transport": {"path": TRANSPORT_PATH, "sha256": TRANSPORT_SHA256, "cli_version": VERSION, "isolation": ISOLATION},
           "output_cap_enforced_by_provider": OUTPUT_CAP_ENFORCED_BY_PROVIDER, "started_utc": now(), "split": split,
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

def prove_transport(lane):
    """Run the lane preflight into a fresh lane/transport_preflight_<ns>/ and bind its receipt to this invocation."""
    global PREFLIGHT
    PREFLIGHT = lane_preflight(os.path.join(lane, "transport_preflight_%d" % time.time_ns()))
    return PREFLIGHT

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
                        prove_transport(lane)   # model-free; refuses before any dispatch
                        rec = call_record(a.model, item, system, out_dir,
                                          os.path.join(EXP, "private", "canary", safe(a.model)), accounting, "canary")
        checks = rec["attempts"][-1].get("protocol_checks") or {}   # a reconciled (interrupted) attempt has none
        print(json.dumps({k: rec.get(k) for k in ("attempt_class", "valid_protocol", "candidates", "total_attributable_tokens", "transport_failure")}), checks,
              rec["attempts"][-1].get("requested_model"), rec["attempts"][-1].get("cli_version"))
        assert (checks.get("requested_model_confirmed_by_catalog_projection") and checks.get("exactly_one_completed_turn")
                and checks.get("no_tool_or_unknown_items")), "canary protocol check failed"
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
            prove_transport(lane)   # model-free; refuses before the gate and before any dispatch, without a lane stop
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
