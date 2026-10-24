#!/usr/bin/env python3
"""Text completions through the authenticated Codex CLI, never a model API SDK.

Each call gets a fresh, isolated CLI process.  The experiment host, rather than the model,
owns harness tools.  Only the exact messages for this role enter the call.
``complete(messages, artifact_dir=...)`` returns text and actual CLI usage.
No model-reported counts, tokenizer estimates, or missing-usage fallbacks exist.

Leading system/developer messages become the CLI model-instructions file. A
single user message is sent byte-for-byte; conversational histories are encoded
as JSON with their original roles, because ``codex exec`` accepts one prompt.
This role mapping is an explicit CLI adaptation, not native chat-API parity.
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence


MODEL = "gpt-6-astra"
EFFORT = "max"
VERSION = "codex-cli 0.153.3"
DISABLED_FEATURES = (
    "apps", "artifact", "auth_elicitation", "browser_use",
    "browser_use_external", "browser_use_full_cdp_access", "code_mode",
    "code_mode_host", "computer_use", "current_time_reminder", "goals",
    "hooks", "image_generation", "in_app_browser", "memories", "multi_agent",
    "multi_agent_v2", "plugins", "remote_plugin", "recommended_plugins",
    "request_permissions_tool", "shell_snapshot", "shell_tool", "skill_search",
    "skill_mcp_dependency_install", "sleep_tool", "tool_call_mcp_elicitation",
    "tool_suggest", "unified_exec", "view_image", "workspace_dependencies",
    "unbounded_connection_retries",
)
BASE_INSTRUCTIONS = (
    "You are a text completion engine executing one mathematical harness role. "
    "Follow the supplied instructions and return only the requested response. "
    "There are no tools or external files in this role."
)


class AstraCLIError(RuntimeError):
    """A completion is unusable; raw evidence remains in artifact_dir."""


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def _strict_json(value: str | bytes) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, item in items:
            if key in result:
                raise AstraCLIError("duplicate JSON key")
            result[key] = item
        return result

    def reject(value: str) -> Any:
        raise AstraCLIError("non-finite JSON number")

    return json.loads(value, object_pairs_hook=pairs, parse_constant=reject)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_new(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _write_json(path: Path, data: Any) -> None:
    _write_new(path, (_json(data) + "\n").encode())


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        """Total counts cached input once, not a second time."""
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class Completion:
    text: str
    usage: Usage
    report: dict[str, Any]
    artifact_dir: Path


def _decode_events(raw: bytes) -> list[dict[str, Any]]:
    try:
        events = [_strict_json(line) for line in raw.splitlines() if line.strip()]
    except (ValueError, UnicodeError) as exc:
        raise AstraCLIError("CLI event stream is not valid JSONL") from exc
    if not events or any(not isinstance(event, dict) for event in events):
        raise AstraCLIError("CLI event stream is empty or contains non-objects")
    return events


def extract_usage(raw: bytes) -> Usage:
    """Read actual billing even when the response or tool policy is invalid.

    Unknown usage remains an error. This function does not validate completion
    success: callers must charge this usage before judging response validity.
    """
    events = _decode_events(raw)
    completed = [event for event in events if event.get("type") == "turn.completed"]
    if len(completed) != 1:
        raise AstraCLIError("missing or ambiguous real CLI token usage")
    value = completed[0].get("usage")
    keys = {"input_tokens", "cached_input_tokens", "output_tokens"}
    if not isinstance(value, dict) or not keys.issubset(value):
        raise AstraCLIError("missing real CLI token usage")
    if any(type(value[k]) is not int or value[k] < 0 for k in keys):
        raise AstraCLIError("invalid CLI token usage")
    usage = Usage(**{k: value[k] for k in keys})
    if (usage.input_tokens == 0 or usage.output_tokens == 0
            or usage.cached_input_tokens > usage.input_tokens):
        raise AstraCLIError("inconsistent CLI token usage")
    return usage


def parse_events(raw: bytes, final_text: str, *,
                 allowed_item_types: frozenset[str] | None = None) -> Usage:
    """Require one successful turn; allow only explicitly authorized tools.

    Text calls leave ``allowed_item_types`` unset. Native harnesses can supply
    their reviewed CLI item allowlist; this does not broaden text transport.
    Use ``extract_usage`` first so invalid responses still consume budget.
    """
    events = _decode_events(raw)
    allowed = {"thread.started", "turn.started", "item.started", "item.updated",
               "item.completed", "turn.completed"}
    completed = []
    messages = []
    for event in events:
        if not isinstance(event, dict) or event.get("type") not in allowed:
            raise AstraCLIError("failed or unknown CLI event")
        kind = event["type"]
        if kind.startswith("item."):
            item = event.get("item")
            allowed_items = {"agent_message", "reasoning"} | set(allowed_item_types or ())
            if not isinstance(item, dict) or item.get("type") not in allowed_items:
                raise AstraCLIError("tool or unknown item in text-only completion")
            if kind == "item.completed" and item["type"] == "agent_message":
                messages.append(item.get("text"))
        if kind == "turn.completed":
            completed.append(event)
    if (len(completed) != 1 or not events or events[-1] != completed[0]
            or sum(e["type"] == "turn.started" for e in events) != 1
            or sum(e["type"] == "thread.started" for e in events) != 1):
        raise AstraCLIError("expected exactly one complete fresh CLI turn")
    usage = extract_usage(raw)
    if not final_text.strip() or not messages or messages[-1] != final_text:
        raise AstraCLIError("CLI final response does not match raw event output")
    return usage


def render_messages(messages: Sequence[Mapping[str, Any]]) -> tuple[str, str, str]:
    if not messages:
        raise AstraCLIError("messages must not be empty")
    leading = []
    history = []
    for message in messages:
        if (not isinstance(message, Mapping)
                or set(message) != {"role", "content"}
                or message["role"] not in {"system", "developer", "user", "assistant"}
                or not isinstance(message["content"], str)):
            raise AstraCLIError("only string content and standard text message roles are supported")
        if not history and message["role"] in {"system", "developer"}:
            leading.append(message["content"])
        else:
            history.append(dict(message))
    if not history or history[-1]["role"] != "user":
        raise AstraCLIError("messages must end with a user request")
    instructions = "\n\n".join(leading) if leading else BASE_INSTRUCTIONS
    if len(history) == 1:
        return instructions, history[0]["content"], "leading_instructions_then_exact_user"
    return (instructions,
            "Continue this message history. Return only the next assistant response.\n"
            + _json(history), "leading_instructions_then_role_labelled_json_history")


def find_native_cli(cli: str | Path | None = None) -> Path:
    location = Path(cli or shutil.which("codex") or "")
    if not location.is_file():
        raise AstraCLIError("Codex CLI executable is unavailable")
    location = location.resolve()
    if location.name != "codex.js":
        return location
    vendor = location.parent.parent / "node_modules/@openai/codex-linux-x64/vendor"
    candidates = list(vendor.glob("*/bin/codex"))
    if len(candidates) != 1:
        raise AstraCLIError("cannot unambiguously locate native Codex CLI")
    return candidates[0].resolve()


def project_catalog(catalog: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Keep the exact model; remove its coding-agent tool advertisements."""
    if not isinstance(catalog, dict) or not isinstance(catalog.get("models"), list):
        raise AstraCLIError("invalid bundled model catalog")
    matches = [m for m in catalog["models"] if m.get("slug") == MODEL]
    if len(matches) != 1:
        raise AstraCLIError("exact configured model missing or ambiguous")
    original = matches[0]
    if not any(x.get("effort") == EFFORT for x in original.get("supported_reasoning_levels", [])):
        raise AstraCLIError("configured catalog does not support max effort")
    projected = copy.deepcopy(original)
    edits = {"tool_mode": "direct", "shell_type": "disabled",
             "apply_patch_tool_type": None, "experimental_supported_tools": [],
             "node_repl_disabled": True}
    projected.update(edits)
    binding = {"original_entry_sha256": _sha(_json(original).encode()),
               "projected_entry_sha256": _sha(_json(projected).encode()),
               "changes": {k: {"before": original.get(k), "after": v}
                           for k, v in edits.items() if original.get(k) != v}}
    return {"models": [projected]}, binding


def config_arguments() -> list[str]:
    values = {
        "model": MODEL,
        "model_reasoning_effort": EFFORT,
        "model_catalog_json": "/input/catalog.json",
        "model_instructions_file": "/input/instructions.txt",
        "approval_policy": "never",
        "default_permissions": "text_only",
        "permissions.text_only.filesystem": {"/": "deny"},
        "permissions.text_only.network.enabled": False,
        "web_search": "disabled", "tools.web_search": False,
        "tools.update_plan.enabled": False,
        "tools.experimental_request_user_input.enabled": False,
        "agents.enabled": False, "apps._default.enabled": False,
        "project_doc_max_bytes": 0, "project_doc_fallback_filenames": [],
        "project_root_markers": [], "include_apps_instructions": False,
        "include_collaboration_mode_instructions": False,
        "include_environment_context": False,
        "include_permissions_instructions": False,
        "shell_environment_policy.inherit": "none",
        "shell_environment_policy.exclude": ["*"], "allow_login_shell": False,
        "analytics.enabled": False, "otel.exporter": "none",
        "otel.metrics_exporter": "none", "otel.trace_exporter": "none",
        "otel.log_user_prompt": False, "suppress_unstable_features_warning": True,
        "features.skip_host_skill_discovery": True,
        "skills.include_instructions": False,
    }
    args = []
    for key, value in values.items():
        if isinstance(value, dict):
            encoded = "{" + ",".join(_json(k) + "=" + _json(v) for k, v in value.items()) + "}"
        else:
            encoded = _json(value)
        args += ["-c", key + "=" + encoded]
    for feature in DISABLED_FEATURES:
        args += ["--disable", feature]
    return args


def build_launch(native: Path, inputs: Path, outputs: Path, auth_fd: int | None,
                 command: Sequence[str]) -> list[str]:
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise AstraCLIError("bubblewrap is required; no weaker isolation fallback")
    args = [bwrap, "--die-with-parent", "--new-session", "--unshare-pid",
            "--unshare-ipc", "--unshare-uts", "--ro-bind", "/usr", "/usr"]
    for name in ("bin", "sbin", "lib", "lib64"):
        args += ["--symlink", "usr/" + name, "/" + name]
    for path in ("/etc/pki", "/etc/ssl", "/etc/resolv.conf", "/etc/hosts", "/etc/nsswitch.conf"):
        if Path(path).exists():
            args += ["--ro-bind", path, path]
    args += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
             "--ro-bind", str(native.parent.parent), "/runtime/vendor",
             "--ro-bind", str(inputs), "/input", "--bind", str(outputs), "/output",
             "--dir", "/workspace", "--dir", "/isolated/home",
             "--tmpfs", "/run/codex-home"]
    if auth_fd is not None:
        args += ["--file", str(auth_fd), "/run/codex-home/auth.json"]
    environment = {"HOME": "/isolated/home", "CODEX_HOME": "/run/codex-home",
                   "PATH": "/runtime/vendor/codex-path:/usr/bin:/bin",
                   "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "NO_COLOR": "1"}
    for key, value in environment.items():
        args += ["--setenv", key, value]
    return args + ["--chdir", "/workspace", "/runtime/vendor/bin/codex", *command]


def _environment() -> dict[str, str]:
    return {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}


def _run(command: list[str], *, prompt: bytes = b"", timeout: float = 1800,
         pass_fds: tuple[int, ...] = ()) -> subprocess.CompletedProcess[bytes]:
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=_environment(), cwd="/tmp",
                             pass_fds=pass_fds, start_new_session=True)
    try:
        stdout, stderr = child.communicate(prompt, timeout=timeout)
    except BaseException as exc:
        os.killpg(child.pid, signal.SIGKILL)
        stdout, stderr = child.communicate()
        if isinstance(exc, subprocess.TimeoutExpired):
            return subprocess.CompletedProcess(command, -signal.SIGKILL, stdout, stderr)
        raise
    return subprocess.CompletedProcess(command, child.returncode, stdout, stderr)


def inspect_prompt(native, inputs, outputs, config, instructions, prompt, destination):
    """Inspect full native input without sending a model request.

    The released debug command accepts prompt only as one argv (Linux caps
    an argument near128KiB). For large inputs, capture the identical CLI exec
    stdin input at a rejecting loopback-only no-inference HTTP fixture. This
    changes only the inspection route, never the actual authenticated launch.
    No auth is mounted and the fixture cannot forward a request anywhere.
    """
    if len(prompt.encode()) < 100_000:
        result = _run(build_launch(native, inputs, outputs, None,
            [*config, 'debug', 'prompt-input', prompt]), timeout=30)
        _write_new(destination / 'prompt_input.raw.json', result.stdout)
        _write_new(destination / 'prompt_input.stderr.log', result.stderr)
        if result.returncode:
            raise AstraCLIError('model-free prompt isolation verification failed')
        _verify_visible_input(_strict_json(result.stdout), instructions, prompt)
        return 'native debug full prompt argv'
    import http.server
    import threading
    captured = []

    class RejectingInspection(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 32_000_000 or self.path != '/v1/responses':
                self.send_error(400)
                return
            captured.append((self.path, self.rfile.read(size)))
            body = b'{"error":{"message":"Local input inspection only; no inference service exists","type":"invalid_request_error"}}'
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), RejectingInspection)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        inspection_config = list(config)
        overrides = {
            'model_provider': 'input_inspection',
            'model_providers.input_inspection.name': 'Local no-inference input inspection',
            'model_providers.input_inspection.base_url': f'http://127.0.0.1:{server.server_port}/v1',
            'model_providers.input_inspection.requires_openai_auth': False,
            'model_providers.input_inspection.wire_api': 'responses',
            'model_providers.input_inspection.request_max_retries': 0,
            'model_providers.input_inspection.stream_max_retries': 0,
        }
        for key, value in overrides.items():
            inspection_config += ['-c', key + '=' + _json(value)]
        command = ['exec', '--strict-config', '--ignore-user-config', '--ignore-rules',
            '--skip-git-repo-check', '--ephemeral', '--model', MODEL, *inspection_config,
            '--json', '--color', 'never', '--cd', '/workspace', '-']
        result = _run(build_launch(native, inputs, outputs, None, command),
                      prompt=prompt.encode(), timeout=45)
        _write_new(destination / 'inspection_exec_events.jsonl', result.stdout)
        _write_new(destination / 'prompt_input.stderr.log', result.stderr)
        if len(captured) != 1 or result.returncode == 0:
            raise AstraCLIError('Rejecting local inspection did not capture exactly one failed request')
        raw = captured[0][1]
        _write_new(destination / 'prompt_input.raw.json', raw)
        value = _strict_json(raw)
        if value.get('model') != MODEL or value.get('reasoning', {}).get('effort') != EFFORT or value.get('tools'):
            raise AstraCLIError('Local input capture changed requested model/effort/tool configuration')
        _verify_visible_input(value, instructions, prompt)
        _write_json(destination / 'inspection_binding.json', {
            'model_calls': 0, 'external_requests': 0, 'authentication_mounted': False,
            'route': 'rejecting localhost fixture, no inference or forwarding implementation',
            'captured_requests': 1, 'prompt_bytes': len(prompt.encode()),
            'prompt_sha256': _sha(prompt.encode()), 'request_sha256': _sha(raw)})
        return 'native exec full prompt stdin; rejecting local no-inference input capture'
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def complete(messages: Sequence[Mapping[str, Any]], *, artifact_dir: str | Path,
             output_schema: Mapping[str, Any] | None = None,
             timeout: float = 1800, cli: str | Path | None = None,
             auth_path: str | Path | None = None) -> Completion:
    """One CLI call, no retry. Never overwrite an earlier call's evidence.

    Auth is mounted from a descriptor into a private tmpfs, never copied into
    artifacts, hashed, logged, or exposed to model tools. CLI transport uses its
    own authenticated ChatGPT connection. Outer networking is needed by the
    CLI; the model has zero tools and a deny-all file/network permission profile.
    """
    instructions, prompt, message_mapping = render_messages(messages)
    destination = Path(artifact_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    native = find_native_cli(cli)
    report: dict[str, Any] = {
        "status": "STARTED", "model": MODEL, "reasoning_effort": EFFORT,
        "model_identity_source": "pinned CLI configuration and bundled catalog",
        "token_usage_source": "raw codex exec JSONL turn.completed.usage",
        "transport": "authenticated ChatGPT Codex CLI; no model API SDK or proxy",
        "message_mapping": message_mapping, "prompt_sha256": _sha(prompt.encode()),
        "instructions_sha256": _sha(instructions.encode()), "usage": None,
        "cli_model_call_attempted": False,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "isolation": {"repository_mounted": False, "user_home_mounted": False,
                      "inherited_environment": False, "fresh_ephemeral_thread": True,
                      "model_tools": [], "model_filesystem": "deny all",
                      "model_network": "disabled", "cwd": "/workspace"},
    }
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="model-text-") as temporary:
            temp = Path(temporary)
            inputs, outputs = temp / "inputs", temp / "outputs"
            inputs.mkdir(); outputs.mkdir()
            version = _run(build_launch(native, inputs, outputs, None, ["--version"]), timeout=30)
            if version.returncode != 0 or version.stdout.decode().strip() != VERSION:
                raise AstraCLIError("native CLI version does not match tested version " + VERSION)
            report["cli_version"] = version.stdout.decode().strip()
            report["cli_sha256"] = _sha(native.read_bytes())
            catalog_result = _run(build_launch(native, inputs, outputs, None,
                                               ["debug", "models", "--bundled"]), timeout=30)
            if catalog_result.returncode:
                raise AstraCLIError("cannot read bundled model catalog")
            catalog, binding = project_catalog(_strict_json(catalog_result.stdout))
            report["catalog_projection"] = binding
            _write_json(inputs / "catalog.json", catalog)
            _write_new(inputs / "instructions.txt", instructions.encode())
            _write_json(destination / "request.messages.json", list(messages))
            _write_new(destination / "prompt.txt", prompt.encode())
            _write_json(destination / "catalog_projection.json", binding)
            config = config_arguments()
            # Full prompt inspection never truncates mathematical context.
            report['model_free_prompt_inspection_route'] = inspect_prompt(
                native, inputs, outputs, config, instructions, prompt, destination)
            report["model_free_prompt_inspection"] = "PASS"
            command = ["exec", "--strict-config", "--ignore-user-config", "--ignore-rules",
                       "--skip-git-repo-check", "--ephemeral", "--model", MODEL, *config,
                       "--json", "--color", "never", "--cd", "/workspace",
                       "--output-last-message", "/output/final.txt"]
            if output_schema is not None:
                # Schema verification after the call requires this package.
                import jsonschema
                jsonschema.Draft202012Validator.check_schema(output_schema)
                _write_json(inputs / "schema.json", output_schema)
                _write_json(destination / "output_schema.json", output_schema)
                command += ["--output-schema", "/input/schema.json"]
            command += ["-"]
            _write_json(destination / "cli_arguments.json", command)
            authentication = Path(auth_path) if auth_path else (
                Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json")
            descriptor = os.open(authentication, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise AstraCLIError("authentication file is not regular")
                # Check only the auth mode, never publish auth bytes or hashes.
                auth_mode = _strict_json(os.pread(descriptor, 128_000, 0)).get("auth_mode")
                if auth_mode != "chatgpt":
                    raise AstraCLIError("ChatGPT CLI login is required; API-key authentication refused")
                report["authentication_mode"] = "chatgpt"
                report["cli_model_call_attempted"] = True
                result = _run(build_launch(native, inputs, outputs, descriptor, command),
                              prompt=prompt.encode(), timeout=timeout, pass_fds=(descriptor,))
            finally:
                os.close(descriptor)
            _write_new(destination / "events.raw.jsonl", result.stdout)
            _write_new(destination / "stderr.raw.log", result.stderr)
            report["returncode"] = result.returncode
            report["events_sha256"] = _sha(result.stdout)
            # Usage is financially/scientifically relevant even when parsing,
            # output-schema validation, the process, or tool policy fails.
            try:
                observed_usage = extract_usage(result.stdout)
                report["usage"] = {**asdict(observed_usage), "total_tokens": observed_usage.total_tokens}
            except AstraCLIError as exc:
                report["usage_error"] = str(exc)
            if result.returncode:
                raise AstraCLIError("Codex CLI call failed; see raw artifacts")
            returned = outputs / "final.txt"
            if not returned.is_file() or returned.is_symlink():
                raise AstraCLIError("CLI did not write a regular final response")
            text = returned.read_text()
            usage = parse_events(result.stdout, text)
            report["usage"] = {**asdict(usage), "total_tokens": usage.total_tokens}
            if output_schema is not None:
                jsonschema.validate(_strict_json(text), output_schema)
            _write_new(destination / "response.txt", text.encode())
            report["status"] = "COMPLETE"
    except Exception as exc:
        report["status"] = "FAILED"
        report["error"] = str(exc)
        raise AstraCLIError(f"{exc}; artifacts: {destination}") from exc
    finally:
        report["elapsed_seconds"] = time.monotonic() - started
        report["ended_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        _write_json(destination / "report.json", report)
    return Completion(text, usage, report, destination)


def _verify_visible_input(value: Any, instructions: str, prompt: str) -> None:
    """Fail closed if the CLI advertises tools or adds hidden role context."""
    if isinstance(value, dict):
        if value.get("instructions") not in (None, instructions):
            raise AstraCLIError("unexpected model base instructions")
        value = value.get("input")
    if not isinstance(value, list):
        raise AstraCLIError("unexpected debug prompt-input shape")
    observed = []
    for item in value:
        if not isinstance(item, dict):
            raise AstraCLIError("invalid model input item")
        if item.get("type") == "additional_tools":
            if item.get("tools"):
                raise AstraCLIError("CLI advertised tools despite text-only configuration")
            continue
        if item.get("type") != "message":
            raise AstraCLIError("unexpected model input item")
        content = item.get("content")
        if not isinstance(content, list) or any(p.get("type") != "input_text" for p in content):
            raise AstraCLIError("non-text model input")
        text = "".join(p["text"] for p in content)
        if item.get("role") == "user":
            observed.append(text)
        elif text.strip() and text != instructions:
            raise AstraCLIError("CLI inserted unexpected non-user instructions")
    if observed != [prompt]:
        raise AstraCLIError("CLI inserted inherited context or changed the user prompt")


async def acomplete(messages: Sequence[Mapping[str, Any]], **kwargs: Any) -> Completion:
    return await asyncio.to_thread(complete, messages, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--messages", type=Path, help="JSON list of role/content messages")
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--output-schema", type=Path)
    parser.add_argument("--smoke", action="store_true", help="one non-scientific transport-only call")
    parser.add_argument("--timeout", type=float, default=1800)
    args = parser.parse_args()
    if bool(args.messages) == bool(args.smoke):
        parser.error("choose exactly one of --messages or --smoke")
    messages = ([{"role": "user", "content": "What is 2 + 2? Reply with the single digit only."}]
                if args.smoke else _strict_json(args.messages.read_bytes()))
    schema = _strict_json(args.output_schema.read_bytes()) if args.output_schema else None
    result = complete(messages, artifact_dir=args.artifact_dir, output_schema=schema, timeout=args.timeout)
    print(_json({"text": result.text, "usage": result.report["usage"],
                 "artifact_dir": str(result.artifact_dir)}))


if __name__ == "__main__":
    main()
