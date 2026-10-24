#!/usr/bin/env python3
"""Repair/recovery track: shared harness code (no model calls, no Lean calls in this module).

Prompt construction, event-stream accounting, attempt classification and the DISPATCH/ATTEMPT/record receipts.
fix_r6 (2026-09-23): read-only inspection commands (INSPECTION_COMMANDS / INSPECTION_RULE / inspection_command_check) are a third kind
of Bash call, audited but never a kernel check and never a violation; the kernel-check grammar ALLOWED_COMMAND_RE is unchanged.
fix_r7 (2026-09-23): the kernel check may be wrapped (KERNEL_CHECK_RULE / kernel_check_form: `timeout N`, `time`, `cd <subdir> &&`,
`&& echo <word>` around the one `lake env lean <file>.lean`; ONE kernel check, same gatekeeper argv); `xargs` is a pipeline stage between
path-emitting and consuming inspection programs (XARGS_RULE); `grep -f FILE` no longer exempts the first operand from the path rule;
the prompt's TOOLS sentence and SUBMISSION FORMAT item 2 (closing `end <Namespace>` line) are amended. ALLOWED_COMMAND_RE is unchanged.
The reservation/receipt pattern follows design_v4_candidate/lane_accounting.py (copied, not imported: that module is frozen).
"""
import contextlib, fcntl, hashlib, json, os, re, shutil, subprocess, tempfile, time, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent                  # .../repair_track_20260922/harness
TRACK = HERE.parent                                     # .../repair_track_20260922
PACKETS = TRACK / "packets"
SYNTHETIC = HERE / "synthetic"
EVALUATOR = HERE / "evaluator"
LEAN_ENV = HERE / "lean_env"
SANDBOX_BIN = HERE / "sandbox_bin"
SANDBOX_EXEC = HERE / "sandbox_exec.sh"
NODE_DIR = os.environ.get("REPAIR_NODE_DIR", "/usr")
REAL_EXECUTABLE = NODE_DIR + "/bin/claude"
# REPAIR_CLI_EXECUTABLE selects the CLI build (default: the nvm install; the claude-opus-5-5 lane uses a pinned second
# install through REPAIR_EXTRA_RO_BIND). The offline test fixture tests/fake_claude is the ONLY executable that makes a run a
# rehearsal (`rehearsal_with_fake_cli`); every other executable is treated as a real CLI and identified by cli_identity().
EXECUTABLE = os.environ.get("REPAIR_CLI_EXECUTABLE", REAL_EXECUTABLE)
FIXTURE_DIR = HERE / "tests"                            # the ONLY directory sandbox_exec.sh may bind at /opt/repair_test (REPAIR_EXTRA_BIN)
FAKE_CLI_HOST = FIXTURE_DIR / "fake_claude"             # the fixture on the host
FAKE_CLI_SANDBOX = "/opt/repair_test/fake_claude"       # where REPAIR_EXTRA_BIN=<harness>/tests binds it inside the namespace
WORK_DIR = "work"                                       # the ONLY writable subdirectory of the (read-only) sandbox root
SUBMISSION_REL = WORK_DIR + "/SUBMISSION.lean"          # the deliverable
GATE_MOUNT = "/opt/repair_gate"                         # host gate directory (kernel-check log) bound outside the sandbox root

MODELS = ("claude-opus-5-5", "claude-sonnet-5")

ARMS = ("A", "B")
ATTEMPT_TAGS = ("a1", "a2_transport_retry")            # the call and its single transport retry; nothing else exists
ATTEMPT_CLASSES = ("VALID_SUBMISSION", "NO_SUBMISSION", "BUDGET_EXHAUSTED", "CONTRACT_VIOLATION", "TRANSPORT_FAILURE")
MAX_OUTPUT_TOKENS = 60000       # total output tokens of the attempt, summed over every provider request (thinking included)
MAX_KERNEL_CHECKS = 20          # `lake env lean` invocations per attempt
MAX_TURNS = 40                  # CLI --max-turns
WALL_CAP = 1800                 # seconds per physical attempt (kill + bounded drain)
DRAIN_SECONDS = 5
EFFORT_DEFAULT = "medium"
ALLOWED_TOOLS = ("Bash", "Write", "Read", "Edit")      # deviation from "Bash only": the solver must be able to write work/SUBMISSION.lean
ALLOWED_COMMAND_RE = re.compile(r"^\s*lake\s+env\s+lean\s+(?!/)(?!.*\.\.)([A-Za-z0-9_./-]+\.lean)\s*$")
CLI_ALLOW_RULES = ("Write", "Read", "Edit", "Bash(lake env lean *)", "Bash(lake env lean:*)")
SKELETON_FILES = ("lakefile.toml", "lake-manifest.json", "lean-toolchain")
ALLOWED_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
CONTROLS = {"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "CLAUDE_CODE_DISABLE_TERMINAL_TITLE": "1",
            "CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION": "false", "CLAUDE_CODE_EXTRA_BODY": "{}", "DISABLE_AUTOUPDATER": "1"}
CHARS_PER_TOKEN = 3.5           # character-based fallback estimate of output tokens (used only for the live kill, never as a measurement)
DENIAL_MARKERS = ("denied", "not allowed", "permission", "doesn't want to proceed", "rejected", "blocked")
HIDDEN_PATH_MARKERS = ("/evaluator", "/mutants", "/synthetic", "/packets", "/smoke", "/story_20260922")
HIDDEN_FILE_NAMES = ("reference.lean", "AGREE.lean", "instances.json", "contract.json")


# ------------------------------------------------------------------------------------- read-only inspection commands (fix_r6)
# The external3 pilot (2026-09-23, 11:19-11:23Z) ended 4 of 6 claude-sonnet-5 cells as CONTRACT_VIOLATION (disallowed_command_executed):
# the CLI's own read-only auto-approval executed `ls <sandbox path>`, `grep -n "sorry\|axiom\|native_decide" work/SUBMISSION.lean`,
# `grep -rl … 2>/dev/null | head; grep -n … -r … 2>/dev/null | head -20` and `grep -rn … 2>/dev/null | head -20`, and the fix_r5 audit
# (ONE grammar, `lake env lean <file>.lean`) classified every other executed command as disallowed. Those commands read files the Read
# tool may already open and can alter neither the inputs (read-only root), the kernel-check counter (gate log outside the grammar's
# reach; `lake` is never admitted here) nor the evaluator (absent from the namespace). fix_r6 admits a CLOSED set of read-only
# inspection commands as a third kind of Bash call, `inspection_command`: never a kernel check, never a violation, never a budget item.
# Everything the fix_r5 audit admitted (the one `lake env lean` form) stays admitted unchanged; everything else stays disallowed.
INSPECTION_COMMANDS = ("ls", "cat", "head", "tail", "wc", "grep", "rg", "egrep", "fgrep", "find", "sed", "diff", "stat", "file",
                       "echo", "pwd", "tree", "sort", "uniq", "cut", "tr", "awk")
INSPECTION_RULE = ("fix_r6: simple commands whose program is one of INSPECTION_COMMANDS (exact name, no path, no builtin, no assignment), "
                   "joined only by | ; && || or newlines; no `$` expansion outside single quotes, no backticks, no process substitution, "
                   "no & background, no unquoted ( ) { } (grouping or brace expansion), no `~`, no `;;`; redirections limited to `< path`, `>/dev/null` (any fd, > or >>), "
                   "`2>&1`, `1>&2`; no `..` path component; absolute paths only under the sandbox root (or /dev/null); `lake` never "
                   "admitted here (the kernel-check form is the separate ALLOWED_COMMAND_RE, unchanged); find without -exec/-execdir/-ok/"
                   "-okdir/-delete/-fprint/-fprint0/-fprintf/-fls; sed only with -n, print-only scripts (no -i/-f, no a/i/c/e/r/R/w/W "
                   "commands, no e/w flags); awk without system/getline/single |/>/@load and without -f/-E/-i/-l/-d/-p/-D/-o/-W; sort "
                   "without -o/-T/--output/--temporary-directory/--compress-program; tree without -o/--output; uniq with at most one "
                   "operand; file without -C/--compile; tail without -f/-F/--follow/--pid; rg without --pre/--hostname-bin. fix_r7: `xargs` is "
                   "admitted only as a pipeline stage under XARGS_RULE; an unquoted `{}` (empty braces, which bash never expands) is a literal "
                   "word; with grep/rg -f FILE or --file=FILE the first operand is a file and is path-checked")


# ------------------------------------------------------------------------------------- kernel-check wrappers and xargs (fix_r7)
# The full study (claude-sonnet-5, 2026-09-23) ended attempts as CONTRACT_VIOLATION for executed Bash commands that were the one
# kernel check in harmless clothing (owner's counts over all attempts): `timeout N lake env lean <file>` 34, `lake env lean <file>
# && echo <word>` chains 15, `cd work && lake env lean SUBMISSION.lean` 4, `time lake env lean <file>` 2; and for `xargs` in read-only
# pipelines 10. fix_r7 admits the wrappers as ONE kernel check (counted in the stream exactly like the bare form; gatekept by the
# UNCHANGED /opt/repair_bin/lake, which receives the same argv `env lean <file>`) and `xargs` as a pipeline stage whose input can only be
# paths under path-checked start points and whose command is an inspection program checked like any other. Everything fix_r6 admitted
# stays admitted; heredocs, redirections to files, `~`, `..`, absolute paths outside the sandbox root, every other `lake` form stay refused.
KERNEL_CHECK_RULE = ("fix_r7: the kernel check is `lake env lean <file>.lean` (one relative .lean file, no options: ALLOWED_COMMAND_RE, unchanged), "
                     "optionally wrapped, in any combination, by a leading `cd <relative subdirectory inside the sandbox> &&` (no `..`, no absolute "
                     "path, no `~`, no `-`), a leading `time` and/or `timeout <integer>[s]` (in that order: `time` is the bash keyword, so it must "
                     "come first; each at most once), and a trailing `&& echo <literal "
                     "words or quoted string>` or `; echo ...` (no expansion, no redirection, nothing after the echo); the wrapped command is ONE "
                     "kernel check: counted in the stream like the bare form and gatekept by /opt/repair_bin/lake, which sees the same argv "
                     "`env lean <file>` (a `cd` into a subdirectory is refused by the gatekeeper's sandbox-root rule and logs nothing, like any "
                     "other gatekeeper refusal); every other `lake` form stays disallowed")
XARGS_RULE = ("fix_r7: `xargs` only as a pipeline stage preceded by `|`, whose input originates from a path-emitting inspection stage (find without "
              "-printf, ls, grep/rg/egrep/fgrep with -l/-L/--files-with-matches/--files-without-match, rg --files, or an xargs stage running one of "
              "those) passed at most through whole-line filters (head, tail, sort, uniq with no file operand; grep/rg/egrep/fgrep reading stdin "
              "without -o/-r/-R); its own options limited to -0/--null, -r/--no-run-if-empty, -t/--verbose, -n N/--max-args, -L N/--max-lines, "
              "-I R/--replace, -d C/--delimiter (never -P, -E/-e, -a/--arg-file, -p, -x, -s or any other); the program it runs must be one of "
              "INSPECTION_COMMANDS (never lake, sh, bash, python, xargs) and is checked with its arguments under INSPECTION_RULE with the sandbox "
              "root; anything after the xargs stage is checked as usual")
_KC_FILE = r"[A-Za-z0-9_./-]+\.lean"
_KC_DIR = r"[A-Za-z0-9_./-]+"
_KC_WORD = r"[A-Za-z0-9_.:=,+%@-]+"                                    # a literal echo word: nothing bash could expand or redirect
_KC_ECHO_ARG = r"(?:" + _KC_WORD + r"|'[^']*'|" + r'"[^"$`\\]*")'
KERNEL_CHECK_WRAPPED_RE = re.compile(
    r"^\s*(?:cd\s+(?P<cd>" + _KC_DIR + r"|'" + _KC_DIR + r"'|\"" + _KC_DIR + r"\")\s*&&\s*)?"
    r"(?P<pre>(?:time\s+)?(?:timeout\s+(?P<timeout>[0-9]+s?)\s+)?)"
    r"lake\s+env\s+lean\s+(?P<file>" + _KC_FILE + r")"
    r"(?:\s*(?P<sep>&&|;)\s*echo(?P<echo>(?:\s+" + _KC_ECHO_ARG + r")+))?\s*$")


def kernel_check_form(command):
    """fix_r7: is `command` the kernel check `lake env lean <file>.lean`, bare (ALLOWED_COMMAND_RE) or in one of the wrappers admitted by
    KERNEL_CHECK_RULE? {"admitted", "bare", "file", "wrappers": {cd, timeout, time, echo}, "reason"}. The gatekeeper receives argv
    `env lean <file>` in every admitted form; the wrappers add no capability (timeout/time only bound or measure the compile, echo prints a
    literal, cd moves into a subdirectory the gatekeeper then refuses)."""
    text = command or ""
    bare = ALLOWED_COMMAND_RE.match(text)
    if bare:
        return {"admitted": True, "bare": True, "file": bare.group(1), "wrappers": {}, "reason": None}

    def refuse(reason):
        return {"admitted": False, "bare": False, "file": None, "wrappers": {}, "reason": reason}
    m = KERNEL_CHECK_WRAPPED_RE.match(text)
    if not m:
        return refuse("not the kernel-check form (bare or wrapped)")
    file = m.group("file")
    if file.startswith("/") or ".." in file.split("/"):
        return refuse("kernel-check file must be relative without '..' (%s)" % file)
    wrappers = {}
    if m.group("cd") is not None:
        cd = m.group("cd").strip("'\"")
        if cd.startswith("/") or ".." in cd.split("/") or not re.search(r"[A-Za-z0-9_]", cd):
            return refuse("cd target must be a relative subdirectory inside the sandbox without '..' (%s)" % cd)
        wrappers["cd"] = cd
    pre = m.group("pre").split()                      # `time` only in the leading position: after `timeout` it would be /usr/bin/time, not the keyword
    if m.group("timeout") is not None:
        wrappers["timeout"] = m.group("timeout")
    if "time" in pre:
        wrappers["time"] = True
    if m.group("echo") is not None:
        wrappers["echo"] = {"separator": m.group("sep"), "arguments": m.group("echo").strip()}
    return {"admitted": True, "bare": False, "file": file, "wrappers": wrappers, "reason": None}


class _Refused(Exception):
    pass


def _shell_tokens(command):
    """Bash-like lexer for the inspection grammar. Returns ("word", text), ("op", text) and ("redir", spec) items; raises _Refused for
    anything that could add capability: a `$` starting an expansion outside single quotes, a backtick outside single quotes, an unquoted
    `~` at the start of a word, process substitution, subshell/grouping parentheses or braces (fix_r7: the empty pair `{}` is a literal
    word), `&` background, `|&`, heredocs/here-strings, unterminated quotes. Quotes are removed: single quotes are literal; in double
    quotes only \\ before $ ` " \\ or newline escapes."""
    out, buf, have_word, digits_only = [], [], False, True
    i, n = 0, len(command)

    def flush():
        nonlocal buf, have_word, digits_only
        if have_word or buf:
            out.append(("word", "".join(buf)))
        buf, have_word, digits_only = [], False, True

    def expansion_start(ch):
        return ch != "" and (ch.isalnum() or ch in "_{(@*#?-$!")

    while i < n:
        ch = command[i]
        nxt = command[i + 1] if i + 1 < n else ""
        if ch in " \t\r":
            flush(); i += 1
        elif ch == "\n":
            flush(); out.append(("op", "\n")); i += 1
        elif ch == "#" and not have_word and not buf:
            while i < n and command[i] != "\n":
                i += 1
        elif ch == "'":
            j = command.find("'", i + 1)
            if j < 0:
                raise _Refused("unterminated single quote")
            buf.extend(command[i + 1:j]); have_word, digits_only = True, False; i = j + 1
        elif ch == '"':
            i += 1; have_word, digits_only = True, False
            while True:
                if i >= n:
                    raise _Refused("unterminated double quote")
                c = command[i]
                if c == '"':
                    i += 1; break
                if c == "\\":
                    e = command[i + 1] if i + 1 < n else ""
                    if e in ('$', '`', '"', '\\'):
                        buf.append(e); i += 2
                    elif e == "\n":
                        i += 2
                    else:
                        buf.append("\\"); i += 1
                elif c == "$":
                    if expansion_start(command[i + 1] if i + 1 < n else ""):
                        raise _Refused("parameter/command/arithmetic expansion ($) in double quotes")
                    buf.append("$"); i += 1
                elif c == "`":
                    raise _Refused("command substitution (backtick) in double quotes")
                else:
                    buf.append(c); i += 1
        elif ch == "\\":
            if nxt == "":
                raise _Refused("trailing backslash")
            if nxt == "\n":
                i += 2
            else:
                buf.append(nxt); have_word, digits_only = True, False; i += 2
        elif ch == "$":
            if nxt == "'":                                    # $'…' ANSI-C quoting: a literal string, no expansion possible inside
                j = i + 2
                while j < n and command[j] != "'":
                    j += 2 if command[j] == "\\" else 1
                if j >= n:
                    raise _Refused("unterminated $'…' quote")
                buf.extend(command[i + 2:j]); have_word, digits_only = True, False; i = j + 1
            elif expansion_start(nxt) or nxt == '"':
                raise _Refused("parameter/command/arithmetic expansion ($)")
            else:
                buf.append("$"); have_word, digits_only = True, False; i += 1
        elif ch == "`":
            raise _Refused("command substitution (backtick)")
        elif ch == "~" and not have_word and not buf:
            raise _Refused("tilde expansion (~)")
        elif ch == "{" and nxt == "}":                        # fix_r7: `{}` (xargs -I placeholder) is never brace-expanded: a literal word
            buf.extend("{}"); have_word, digits_only = True, False; i += 2
        elif ch in "(){}":
            raise _Refused("unquoted %s (subshell, grouping, process substitution or brace expansion)" % ch)
        elif ch == "|":
            flush()
            if nxt == "|":
                out.append(("op", "||")); i += 2
            elif nxt == "&":
                raise _Refused("|& pipe")
            else:
                out.append(("op", "|")); i += 1
        elif ch == "&":
            flush()
            if nxt == "&":
                out.append(("op", "&&")); i += 2
            elif nxt == ">":
                spec = "&>>" if command[i + 2:i + 3] == ">" else "&>"
                out.append(("redir", spec)); i += len(spec)
            else:
                raise _Refused("background or fd duplication (&)")
        elif ch == ";":
            flush(); out.append(("op", ";")); i += 1
        elif ch in "<>":
            fd = ""
            if buf and have_word and digits_only:
                fd = "".join(buf); buf, have_word, digits_only = [], False, True
            else:
                flush()
            rest = command[i:i + 3]
            if ch == "<":
                if rest.startswith("<<") or rest.startswith("<(") or rest.startswith("<>"):
                    raise _Refused("heredoc, here-string, process substitution or read-write redirection")
                op = "<&" if rest.startswith("<&") else "<"
            else:
                if rest.startswith(">(") or rest.startswith(">|"):
                    raise _Refused("process substitution or clobbering redirection")
                op = ">>" if rest.startswith(">>") else (">&" if rest.startswith(">&") else ">")
            out.append(("redir", fd + op)); i += len(op)
        else:
            if not (ch.isdigit() and (digits_only or not buf)):
                digits_only = False
            buf.append(ch); have_word = True; i += 1
    flush()
    return out


def _sandbox_roots(sandbox_root):
    roots = set()
    if sandbox_root:
        root = str(sandbox_root).rstrip("/")
        roots.add(root)
        try:
            roots.add(os.path.realpath(root).rstrip("/"))
        except OSError:
            pass
    return roots


def _path_ok(token, roots):
    if token in ("-", ""):
        return None
    if ".." in token.split("/"):
        return "'..' path component (%s)" % token
    if token.startswith("/"):
        if token == "/dev/null" or any(token == r or token.startswith(r + "/") for r in roots):
            return None
        return "absolute path outside the sandbox root (%s)" % token
    return None


def _opt_value_path(token, roots):
    """`--opt=value`: the value is path-checked when it looks like a path (absolute or with `..`)."""
    if "=" in token:
        value = token.split("=", 1)[1]
        if value.startswith("/") or ".." in value.split("/"):
            return _path_ok(value, roots)
    return None


_SED_ADDR_END = re.compile(r"[0-9]+(?:~[0-9]+)?|\$")


def _sed_script_ok(script):
    """Print-only sed script: optional addresses, then a command from p P = l d D q Q n N h H g G x z F { } b t T : #, or s/y with
    print-only flags (g p i I m M digits). Anything else (a i c e r R w W v, an e/w flag, a filename) is refused."""
    i, n = 0, len(script)

    def skip_ws():
        nonlocal i
        while i < n and script[i] in " \t":
            i += 1

    def regex(delim):
        nonlocal i
        while i < n:
            c = script[i]
            if c == "\\":
                i += 2
            elif c == delim:
                i += 1
                return True
            else:
                i += 1
        return False

    def address():
        nonlocal i
        if i < n and script[i] == "/":
            i += 1
            if not regex("/"):
                return False
        elif i < n and script[i] == "\\" and i + 1 < n:
            d = script[i + 1]; i += 2
            if not regex(d):
                return False
        else:
            m = _SED_ADDR_END.match(script, i)
            if not m:
                return None
            i = m.end()
        while i < n and script[i] in "IM":
            i += 1
        return True

    while True:
        while i < n and script[i] in " \t\n;":
            i += 1
        if i >= n:
            return True
        a = address()
        if a is False:
            return False
        if a and i < n and script[i] == ",":
            i += 1
            skip_ws()
            if i < n and script[i] in "+~":
                i += 1
                m = re.compile(r"[0-9]+").match(script, i)
                if not m:
                    return False
                i = m.end()
            else:
                b = address()
                if not b:
                    return False
        skip_ws()
        while i < n and script[i] == "!":
            i += 1
            skip_ws()
        if i >= n:
            return False
        c = script[i]
        if c in "pP=ldDqQnNhHgGxzF{}":
            i += 1
            if c in "qQ":
                skip_ws()
                while i < n and script[i].isdigit():
                    i += 1
        elif c in "sy":
            if i + 1 >= n:
                return False
            d = script[i + 1]
            if d in "\\\n":
                return False
            i += 2
            if not regex(d) or not regex(d):
                return False
            if c == "s":
                while i < n and script[i] in "gpiImM0123456789":
                    i += 1
        elif c in "btT:":
            i += 1
            skip_ws()
            while i < n and (script[i].isalnum() or script[i] == "_"):
                i += 1
        elif c == "#":
            while i < n and script[i] != "\n":
                i += 1
        else:
            return False
        skip_ws()
        if c != "{" and i < n and script[i] not in ";\n}":
            return False


_AWK_REFUSED = re.compile(r"\bsystem\b|\bgetline\b|@[A-Za-z_]|(?<!\|)\|(?!\|)|>(?!=)")


def _awk_program_ok(program):
    """awk program text: no system(), no getline, no @load/@include, no single `|` (pipes to or from a command), no `>`/`>>` (output
    redirection; `>=` stays). Regex alternation `/a|b/` is therefore refused too: use grep -E for that."""
    return not _AWK_REFUSED.search(program)


_GREP_VALUE_SHORT = {"grep": "efmABCdD", "egrep": "efmABCdD", "fgrep": "efmABCdD", "rg": "efmABCdDgtTjMrE"}
_GREP_VALUE_LONG = ("--regexp", "--file", "--max-count", "--after-context", "--before-context", "--context", "--include", "--exclude",
                    "--exclude-dir", "--exclude-from", "--color", "--colour", "--binary-files", "--directories", "--devices", "--label",
                    "--group-separator", "--glob", "--iglob", "--type", "--type-not", "--type-add", "--type-clear", "--max-depth",
                    "--max-filesize", "--colors", "--context-separator", "--field-context-separator", "--field-match-separator",
                    "--path-separator", "--encoding", "--engine", "--ignore-file", "--sort", "--sortr", "--replace", "--dfa-size-limit",
                    "--regex-size-limit", "--max-columns", "--threads", "--pre", "--pre-glob", "--hostname-bin")
_GREP_PATH_LONG = ("--file", "--exclude-from", "--ignore-file")
_GREP_REFUSED_LONG = ("--pre", "--hostname-bin")
_FIND_REFUSED = ("-exec", "-execdir", "-ok", "-okdir", "-delete", "-fprint", "-fprint0", "-fprintf", "-fls")
_FIND_PATH_VALUE = ("-newer", "-anewer", "-cnewer", "-bnewer", "-samefile", "-files0-from", "-f")
_FIND_VALUE = ("-name", "-iname", "-path", "-ipath", "-wholename", "-iwholename", "-regex", "-iregex", "-lname", "-ilname", "-type", "-xtype",
               "-size", "-perm", "-user", "-group", "-uid", "-gid", "-mtime", "-mmin", "-atime", "-amin", "-ctime", "-cmin", "-btime", "-bmin",
               "-used", "-links", "-inum", "-fstype", "-maxdepth", "-mindepth", "-printf", "-regextype", "-context", "-D", "-O", "-limit",
               "-since", "-xattrname", "-S", "-j", "-flags") + _FIND_PATH_VALUE
# generic programs: (long options refused by name, short option letters refused anywhere in a cluster, max operands or None)
_GENERIC = {"ls": ((), "", None), "cat": ((), "", None), "head": ((), "", None), "wc": ((), "", None), "stat": ((), "", None),
            "diff": ((), "", None), "cut": ((), "", None), "pwd": ((), "", None),
            "tail": (("--follow", "--pid", "--retry"), "fF", None),
            "sort": (("--output", "--temporary-directory", "--compress-program"), "oT", None),
            "tree": (("--output",), "o", None),
            "uniq": ((), "", 1),
            "file": (("--compile",), "C", None)}


def _check_generic(name, args, roots):
    long_refused, short_refused, max_operands = _GENERIC[name]
    operands, opts_done, skip = 0, False, False
    for tok in args:
        if skip:
            skip = False
            continue
        if name == "uniq" and tok in ("-f", "-s", "-w"):
            skip = True
            continue
        if opts_done or not tok.startswith("-") or tok == "-":
            operands += 1
            reason = _path_ok(tok, roots)
            if reason:
                return reason
            continue
        if tok == "--":
            opts_done = True
            continue
        if tok.startswith("--"):
            base = tok.split("=", 1)[0]
            if base in long_refused:
                return "%s option %s not admitted" % (name, base)
            reason = _opt_value_path(tok, roots)
            if reason:
                return reason
        elif any(letter in tok[1:] for letter in short_refused):
            return "%s option %s not admitted" % (name, tok)
    if max_operands is not None and operands > max_operands:
        return "%s with more than %d operand(s) (the second operand is an output file)" % (name, max_operands)
    return None


def _check_grep(name, args, roots):
    pattern_seen, opts_done, positionals = False, False, []
    i = 0
    while i < len(args):
        tok = args[i]; i += 1
        if opts_done or not tok.startswith("-") or tok == "-":
            positionals.append(tok)
            continue
        if tok == "--":
            opts_done = True
            continue
        if tok.startswith("--"):
            base, eq, value = tok.partition("=")
            if base in _GREP_REFUSED_LONG:
                return "%s option %s not admitted (executes a program)" % (name, base)
            if base in _GREP_VALUE_LONG:
                if not eq:
                    if i >= len(args):
                        return "%s option %s lacks its value" % (name, base)
                    value = args[i]; i += 1
                if base == "--regexp":
                    pattern_seen = True
                elif base in _GREP_PATH_LONG or value.startswith("/") or ".." in value.split("/"):
                    if base == "--file":
                        pattern_seen = True               # fix_r7: with --file=F the first operand is a FILE, not a pattern (fix_r6 gap)
                    reason = _path_ok(value, roots)
                    if reason:
                        return reason
            else:
                reason = _opt_value_path(tok, roots)
                if reason:
                    return reason
            continue
        cluster = tok[1:]
        for k, letter in enumerate(cluster):
            if letter in _GREP_VALUE_SHORT[name]:
                value = cluster[k + 1:]
                if value == "":
                    if i >= len(args):
                        return "%s option -%s lacks its value" % (name, letter)
                    value = args[i]; i += 1
                if letter == "e":
                    pattern_seen = True
                elif letter == "f" or value.startswith("/") or ".." in value.split("/"):
                    if letter == "f":
                        pattern_seen = True               # fix_r7: with -f F the first operand is a FILE, not a pattern (fix_r6 gap)
                    reason = _path_ok(value, roots)
                    if reason:
                        return reason
                break
    if not pattern_seen and positionals:
        positionals = positionals[1:]                 # the first operand is the pattern, exempt from the path rules
    for tok in positionals:
        reason = _path_ok(tok, roots)
        if reason:
            return reason
    return None


def _check_find(args, roots):
    i = 0
    while i < len(args):
        tok = args[i]; i += 1
        if tok in _FIND_REFUSED:
            return "find action %s not admitted" % tok
        if tok.startswith("-") and tok != "-":
            if tok.startswith("-fprint") or tok.startswith("-exec") or tok.startswith("-ok"):
                return "find action %s not admitted" % tok
            if tok in _FIND_VALUE or tok.startswith("-newer"):
                if i >= len(args):
                    return "find predicate %s lacks its value" % tok
                value = args[i]; i += 1
                if tok in _FIND_PATH_VALUE or tok.startswith("-newer"):
                    reason = _path_ok(value, roots)
                    if reason:
                        return reason
            continue
        if tok in ("(", ")", "!", ","):
            continue
        reason = _path_ok(tok, roots)
        if reason:
            return reason
    return None


def _check_sed(args, roots):
    quiet, scripts, positionals, opts_done = False, [], [], False
    i = 0
    while i < len(args):
        tok = args[i]; i += 1
        if opts_done or not tok.startswith("-") or tok == "-":
            positionals.append(tok)
            continue
        if tok == "--":
            opts_done = True
            continue
        if tok.startswith("--"):
            base, eq, value = tok.partition("=")
            if base in ("--in-place", "--file"):
                return "sed option %s not admitted" % base
            if base in ("--quiet", "--silent"):
                quiet = True
            elif base == "--expression":
                if not eq:
                    if i >= len(args):
                        return "sed --expression lacks its script"
                    value = args[i]; i += 1
                scripts.append(value)
            elif base == "--line-length" and not eq:
                i += 1
            else:
                reason = _opt_value_path(tok, roots)
                if reason:
                    return reason
            continue
        cluster = tok[1:]
        k = 0
        while k < len(cluster):
            letter = cluster[k]; k += 1
            if letter == "i":
                return "sed -i (in-place edit) not admitted"
            if letter == "f":
                return "sed -f (script file) not admitted"
            if letter == "n":
                quiet = True
            elif letter in "el":
                value = cluster[k:]
                if value == "":
                    if i >= len(args):
                        return "sed -%s lacks its value" % letter
                    value = args[i]; i += 1
                if letter == "e":
                    scripts.append(value)
                break
    if not scripts:
        if not positionals:
            return "sed without a script"
        scripts.append(positionals.pop(0))
    if not quiet:
        return "sed without -n (only print-only inspection is admitted)"
    for script in scripts:
        if not _sed_script_ok(script):
            return "sed script not print-only: %r" % script[:80]
    for tok in positionals:
        reason = _path_ok(tok, roots)
        if reason:
            return reason
    return None


def _check_awk(args, roots):
    programs, positionals, opts_done = [], [], False
    i = 0
    while i < len(args):
        tok = args[i]; i += 1
        if opts_done or not tok.startswith("-") or tok == "-":
            positionals.append(tok)
            continue
        if tok == "--":
            opts_done = True
            continue
        if tok.startswith("--"):
            base, eq, value = tok.partition("=")
            if base in ("--file", "--exec", "--include", "--load", "--dump-variables", "--profile", "--debug", "--pretty-print"):
                return "awk option %s not admitted" % base
            if base == "--source":
                if not eq:
                    if i >= len(args):
                        return "awk --source lacks its program"
                    value = args[i]; i += 1
                programs.append(value)
            elif base in ("--field-separator", "--assign") and not eq:
                i += 1
            else:
                reason = _opt_value_path(tok, roots)
                if reason:
                    return reason
            continue
        letter, value = tok[1], tok[2:]
        if letter in "fEildpDoW":
            return "awk option -%s not admitted" % letter
        if letter in "eFv":
            if value == "":
                if i >= len(args):
                    return "awk option -%s lacks its value" % letter
                value = args[i]; i += 1
            if letter == "e":
                programs.append(value)
    if not programs:
        if not positionals:
            return "awk without a program"
        programs.append(positionals.pop(0))
    for program in programs:
        if not _awk_program_ok(program):
            return "awk program uses system/getline/@load, a pipe or an output redirection: %r" % program[:80]
    for tok in positionals:
        reason = _path_ok(tok, roots)
        if reason:
            return reason
    return None


def _check_redirs(redirs, roots):
    for spec, target in redirs:
        fd, op = spec.rstrip("<>&"), spec.lstrip("0123456789")
        if op == "<" and fd in ("", "0"):
            reason = _path_ok(target, roots)
            if reason:
                return "input redirection: " + reason
        elif op in (">", ">>", "&>", "&>>") and target == "/dev/null":
            pass
        elif op == ">&" and ((fd, target) in (("2", "1"), ("1", "2"), ("", "2")) or target == "/dev/null"):
            pass
        else:
            return "redirection not admitted: %s%s" % (spec, target)
    return None


def _check_program(words, roots):
    """The per-program rules of INSPECTION_RULE for one admitted program and its arguments (no redirections here)."""
    name, args = words[0], words[1:]
    if name in _GENERIC:
        return _check_generic(name, args, roots)
    if name in _GREP_VALUE_SHORT:
        return _check_grep(name, args, roots)
    if name == "find":
        return _check_find(args, roots)
    if name == "sed":
        return _check_sed(args, roots)
    if name == "awk":
        return _check_awk(args, roots)
    return None                                       # echo, tr: no file access at all


# fix_r7: xargs. Its command receives whatever lines reach it as operands, so the ordinary path rule (which reads the command text) cannot
# see them; the input side is therefore restricted to stages whose every output line is a path under a path-checked start point or text no
# program can open: find (without -printf), ls, grep/rg -l/-L (rg --files), passed at most through filters that only select or reorder
# whole lines. `echo /etc/passwd | xargs cat`, `cat work/list.txt | xargs cat`, `sed`/`awk`/`cut`/`tr` producers are refused for that reason.
_XARGS_FLAGS = ("-0", "--null", "-r", "--no-run-if-empty", "-t", "--verbose", "--replace")
_XARGS_VALUE_SHORT = "nILd"                                              # -n N, -I R, -L N, -d C (attached or in the next token)
_XARGS_VALUE_LONG = ("--max-args", "--replace", "--max-lines", "--delimiter")
_LINE_FILTERS = ("head", "tail", "sort", "uniq")
_NUMBER = re.compile(r"^[+-]?[0-9]+[kKmMgGbB]?$")


def _grep_scan(name, args):
    """(pattern given by -e/--regexp/-f/--file, file operands, short option letters, long option names) with _check_grep's option handling."""
    pattern_seen, opts_done, positionals, shorts, longs = False, False, [], set(), set()
    i = 0
    while i < len(args):
        tok = args[i]; i += 1
        if opts_done or not tok.startswith("-") or tok == "-":
            positionals.append(tok); continue
        if tok == "--":
            opts_done = True; continue
        if tok.startswith("--"):
            base, eq, _ = tok.partition("=")
            longs.add(base)
            if base in _GREP_VALUE_LONG and not eq and i < len(args):
                i += 1
            if base in ("--regexp", "--file"):
                pattern_seen = True
            continue
        cluster = tok[1:]
        for k, letter in enumerate(cluster):
            shorts.add(letter)
            if letter in _GREP_VALUE_SHORT[name]:
                if cluster[k + 1:] == "" and i < len(args):
                    i += 1
                if letter in ("e", "f"):
                    pattern_seen = True
                break
    files = positionals if pattern_seen else positionals[1:]
    return pattern_seen, [f for f in files if f != "-"], shorts, longs


def _xargs_consumer(args):
    """The words of the command an xargs stage runs, after its admitted options; None when an option is not admitted or no command follows."""
    i = 0
    while i < len(args):
        tok = args[i]
        if not tok.startswith("-") or tok == "-":
            return args[i:]
        i += 1
        if tok in _XARGS_FLAGS:
            continue
        if tok.startswith("--"):
            base, eq, _ = tok.partition("=")
            if base in _XARGS_VALUE_LONG:
                if not eq:
                    i += 1
                continue
            return None
        cluster = tok[1:]
        for k, letter in enumerate(cluster):
            if letter in "0rt":
                continue
            if letter in _XARGS_VALUE_SHORT:
                if cluster[k + 1:] == "":
                    i += 1
                break
            return None
    return None


def _emits_paths(words):
    """Every output line of this stage is a path under a path-checked start point (or text no program can open)."""
    name = words[0]
    if name == "find":
        return "-printf" not in words[1:]
    if name == "ls":
        return True
    if name in _GREP_VALUE_SHORT:
        _, _, shorts, longs = _grep_scan(name, words[1:])
        return bool({"l", "L"} & shorts) or bool({"--files-with-matches", "--files-without-match", "--files"} & longs)
    if name == "xargs":
        consumer = _xargs_consumer(words[1:])
        return consumer is not None and consumer[0] in INSPECTION_COMMANDS and _emits_paths(consumer)
    return False


def _keeps_lines(words):
    """A stdin-only filter that only selects or reorders whole input lines: head/tail/sort/uniq without a file operand (every non-option
    token numeric), or grep/rg/egrep/fgrep with no file operand and without -o/-r/-R."""
    name = words[0]
    if name in _LINE_FILTERS:
        return "--" not in words[1:] and all(tok.startswith("-") or _NUMBER.match(tok) for tok in words[1:])
    if name in _GREP_VALUE_SHORT:
        _, files, shorts, longs = _grep_scan(name, words[1:])
        return not files and not ({"o", "r", "R"} & shorts) and not ({"--only-matching", "--recursive", "--dereference-recursive", "--files"} & longs)
    return False


def _check_xargs(words, chain, roots):
    """fix_r7 (XARGS_RULE): `chain` = the stages before this xargs in the same pipeline (head first), None when xargs is not preceded by |."""
    if chain is None or not chain:
        return None, "xargs only as a pipeline stage after |"
    if not _emits_paths(chain[0]):
        return None, "xargs input must originate from find, ls or grep -l/-L (a path-emitting stage), not from %s" % chain[0][0]
    for stage in chain[1:]:
        if not (_emits_paths(stage) or _keeps_lines(stage)):
            return None, "stage %s between the path-emitting stage and xargs may only select or reorder whole lines" % stage[0]
    consumer = _xargs_consumer(words[1:])
    if consumer is None:
        return None, "xargs option not admitted or no command given (admitted: -0 -r -t -n N -L N -I R -d C and their long forms)"
    if consumer[0] not in INSPECTION_COMMANDS:
        return None, "xargs may run only an inspection program, never %s" % consumer[0]
    if "=" in consumer[0]:
        return None, "variable assignment in the xargs command"
    return consumer, _check_program(consumer, roots)


def _check_simple(words, redirs, roots, chain=None):
    if not words:
        return "empty command"
    name = words[0]
    if "=" in name:
        return "variable assignment before the command (%s)" % name.split("=", 1)[0]
    if name != "xargs" and name not in INSPECTION_COMMANDS:
        return "program not admitted: %s" % name
    reason = _check_redirs(redirs, roots)
    if reason:
        return reason
    if name == "xargs":
        return _check_xargs(words, chain, roots)[1]
    return _check_program(words, roots)


def inspection_command_check(command, sandbox_root=None):
    """fix_r6: is `command` read-only inspection under INSPECTION_RULE? {"admitted", "reason", "programs"}. Never admits the kernel-check
    form (`lake` is not an inspection program); classify_command() tests the kernel-check forms first. fix_r7: an `xargs` stage is admitted
    under XARGS_RULE (its input side must be path-emitting stages, its command an inspection program; `programs` lists `xargs` and it)."""
    roots = _sandbox_roots(sandbox_root)
    programs = []
    try:
        tokens = _shell_tokens(command or "")
        segments, words, redirs, prev_sep, before = [], [], [], None, None    # segments: (words, redirs, separator before the segment)
        i = 0
        while i <= len(tokens):
            tok = tokens[i] if i < len(tokens) else ("op", None)
            i += 1
            if tok[0] == "redir":
                if i >= len(tokens) or tokens[i][0] != "word":
                    raise _Refused("redirection without a target")
                redirs.append((tok[1], tokens[i][1])); i += 1
            elif tok[0] == "word":
                words.append(tok[1])
            else:
                sep = tok[1]
                if words or redirs:
                    segments.append((words, redirs, before)); before = sep
                elif sep in ("|", "&&", "||") or prev_sep in ("|", "&&", "||"):
                    raise _Refused("empty command next to %s" % (sep or prev_sep).strip() or "a pipe")
                elif sep == ";" and prev_sep in (";", None):
                    raise _Refused("empty command before ;")
                words, redirs, prev_sep = [], [], sep
        if not segments:
            raise _Refused("empty command")
        for k, (words, redirs, sep_before) in enumerate(segments):
            chain = None
            if words and words[0] == "xargs" and sep_before == "|":
                j = k                                                          # the stages of this pipeline before the xargs, head first
                while j > 0 and segments[j][2] == "|":
                    j -= 1
                chain = [s[0] for s in segments[j:k]]
            reason = _check_simple(words, redirs, roots, chain)
            if reason:
                raise _Refused(reason)
            programs.append(words[0])
            if words[0] == "xargs":
                programs.append(_xargs_consumer(words[1:])[0])
    except _Refused as exc:
        return {"admitted": False, "reason": str(exc), "programs": programs}
    return {"admitted": True, "reason": None, "programs": programs}


def classify_command(command, sandbox_root=None):
    """Kind of one Bash command: `kernel_check` (the one admitted `lake env lean <file>.lean` form, unchanged since fix_r1, bare or -- since
    fix_r7 -- in a wrapper admitted by KERNEL_CHECK_RULE), `inspection_command` (fix_r6: read-only inspection admitted by
    inspection_command_check) or `disallowed_command`."""
    if kernel_check_form(command)["admitted"]:
        return "kernel_check"
    if inspection_command_check(command, sandbox_root)["admitted"]:
        return "inspection_command"
    return "disallowed_command"


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def safe(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_copy(src, dst):
    """Publish a copy of src at dst through a temporary file beside dst and one rename: a concurrent reader of dst never sees a
    partially written file (the validator's shared olean cache is read by several graders at once)."""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        shutil.copyfile(src, tmp)
        with tmp.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(tmp, dst)
    finally:
        if tmp.exists():
            tmp.unlink()


@contextlib.contextmanager
def exclusive_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another process holds " + str(path)) from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def count(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < float("inf"):
        return 0
    return int(value)


# ----------------------------------------------------------------------------------------------------------------- packets

def packet_dir(record_id, override=None):
    if override:
        return Path(override)
    for base in (SYNTHETIC, PACKETS):
        if (base / record_id).is_dir():
            return base / record_id
    raise FileNotFoundError("no packet directory for record %s under %s or %s" % (record_id, SYNTHETIC, PACKETS))


def load_packet(record_id, override=None):
    """The packet interface (packets/E0k or synthetic/SYN01):

    task.json           solver-facing spec, RENDERED INTO THE PROMPT (template with hole, obligations, allowed edit, reserved names)
    source_context.txt  the original source text, solver-visible in both arms (task.json names it via source_context_file)
    defs_only.lean      definitions only, copied into the sandbox (both arms)
    witness_min.lean    minimal checked counterexample, copied into the sandbox for arm B only
    contract.json       the packet agent's metadata (hidden references, hidden endpoint statement, edit grammar prose,
                        source_exposed_repair): NEVER exposed; its sha and source_exposed_repair are recorded in receipts
    Everything else in the packet directory (leak_audit.json, compile receipts, oleans) is ignored and never copied.
    """
    pd = packet_dir(record_id, override)
    task_path = pd / "task.json"
    if not task_path.exists():
        raise FileNotFoundError("packet %s has no task.json (solver-facing template/obligations spec); refusing to build a prompt" % pd)
    task = json.loads(task_path.read_text(encoding="utf-8"))
    for key in ("record_id", "located_defect", "repair_template", "hole_marker", "submission_namespace",
                "template_declaration", "obligations", "allowed_imports"):
        if key not in task:
            raise ValueError("task.json of %s lacks %s" % (record_id, key))
    if task["record_id"] != record_id:
        raise ValueError("task.json record_id %s does not match %s" % (task["record_id"], record_id))
    src_name = task.get("source_context_file", "source_context.txt")
    src_path = pd / src_name
    if src_path.exists():
        source = src_path.read_text(encoding="utf-8")
    elif "source_context" in task:
        source = task["source_context"]
    else:
        raise FileNotFoundError("packet %s has neither %s nor task.source_context" % (pd, src_name))
    defs = (pd / "defs_only.lean").read_text(encoding="utf-8")
    witness_path = pd / "witness_min.lean"
    witness = witness_path.read_text(encoding="utf-8") if witness_path.exists() else None
    meta_path = pd / "contract.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else None
    shas = {"task.json": file_sha(task_path), "defs_only.lean": file_sha(pd / "defs_only.lean"),
            "witness_min.lean": file_sha(witness_path) if witness_path.exists() else None,
            src_name: file_sha(src_path) if src_path.exists() else None,
            "contract.json": file_sha(meta_path) if meta_path.exists() else None}
    return {"dir": pd, "contract": task, "task": task, "source_context": source, "defs_only": defs, "witness_min": witness,
            "metadata_never_exposed": {"present": meta is not None,
                                       "source_exposed_repair": (meta or {}).get("source_exposed_repair"),
                                       "endpoint_type": (meta or {}).get("endpoint_type"),
                                       "hidden_reference_count": len((meta or {}).get("hidden_references") or [])},
            "sha256": shas}


def common_project():
    return Path(os.environ.get("COPEER_LEAN_PROJECT", str(LEAN_ENV))).resolve()


def lean_env_fingerprint():
    """The immutable common environment: skeleton files (must equal the common project's), toolchain, Mathlib olean identity."""
    common = common_project()
    parts, same = {}, True
    for name in SKELETON_FILES:
        mine, theirs = LEAN_ENV / name, common / name
        parts[name] = {"sha256": file_sha(mine), "common_project_sha256": file_sha(theirs) if theirs.exists() else None}
        same = same and parts[name]["sha256"] == parts[name]["common_project_sha256"]
    olean = common / ".lake/packages/mathlib/.lake/build/lib/lean/Mathlib.olean"
    st = olean.stat() if olean.exists() else None
    fp = {"common_project": str(common), "skeleton": parts, "skeleton_matches_common_project": same,
          "toolchain": (LEAN_ENV / "lean-toolchain").read_text(encoding="utf-8").strip(),
          "mathlib_olean": {"path": str(olean), "size": st.st_size if st else None, "mtime": int(st.st_mtime) if st else None}}
    fp["fingerprint_sha256"] = sha(json.dumps({k: v for k, v in fp.items() if k != "fingerprint_sha256"}, sort_keys=True))
    return fp


# ------------------------------------------------------------------------------------------------------------ CLI identity
def extra_bin_ok(extra_bin=None):
    """True when REPAIR_EXTRA_BIN (the host directory sandbox_exec.sh binds at /opt/repair_test) is unset or resolves to the harness
    tests/ directory; any other directory is refused by the launcher and by sandbox_exec.sh. None reads the environment."""
    extra_bin = os.environ.get("REPAIR_EXTRA_BIN") if extra_bin is None else extra_bin
    if not extra_bin:
        return True
    try:
        return Path(extra_bin).resolve() == FIXTURE_DIR.resolve()
    except OSError:
        return False


def is_fake_cli(executable, extra_bin=None):
    """True only for the offline fixture tests/fake_claude: on the host by resolved path, or at its in-namespace path
    /opt/repair_test/fake_claude when the directory bound there (REPAIR_EXTRA_BIN, or `extra_bin`) IS the harness tests/ directory.
    Never by name alone: the in-namespace path with REPAIR_EXTRA_BIN unset or pointing elsewhere is not the fixture."""
    executable = str(executable)
    if executable == FAKE_CLI_SANDBOX:
        extra_bin = os.environ.get("REPAIR_EXTRA_BIN") if extra_bin is None else extra_bin
        return bool(extra_bin) and extra_bin_ok(extra_bin)
    path = Path(executable)
    try:
        return path.exists() and path.resolve() == FAKE_CLI_HOST.resolve()
    except OSError:
        return False


def cli_identity(executable=None, timeout=120, extra_bin=None):
    """Executable path, its resolved host path and sha256, and `--version` output; rehearsal_with_fake_cli only for the fixture.
    For the in-namespace fixture path the file hashed and versioned is the one actually bound there: <REPAIR_EXTRA_BIN>/fake_claude."""
    executable = str(executable or EXECUTABLE)
    extra_bin = os.environ.get("REPAIR_EXTRA_BIN") if extra_bin is None else extra_bin
    fake = is_fake_cli(executable, extra_bin)
    host_path = (Path(extra_bin) / Path(FAKE_CLI_SANDBOX).name) if fake and executable == FAKE_CLI_SANDBOX else Path(executable)
    exists = host_path.exists()
    info = {"cli_executable": executable, "rehearsal_with_fake_cli": fake, "cli_exists_on_host": exists,
            "cli_executable_resolved": str(host_path.resolve()) if exists else None,
            "cli_executable_sha256": file_sha(host_path) if exists and host_path.is_file() else None,
            "rehearsal_extra_bin": extra_bin or None, "rehearsal_extra_bin_is_fixture_dir": extra_bin_ok(extra_bin) if extra_bin else None,
            "cli_version": None, "cli_version_exit_code": None}
    if exists:
        env = {"PATH": NODE_DIR + "/bin:/usr/bin:/bin", "HOME": os.environ.get("HOME", ""), "LANG": "C.UTF-8",
               "DISABLE_AUTOUPDATER": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
        with tempfile.TemporaryDirectory(prefix="repair_cli_version_") as tmp:
            try:
                proc = subprocess.run([str(host_path), "--version"], cwd=tmp, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, timeout=timeout)
                info["cli_version"], info["cli_version_exit_code"] = proc.stdout.strip()[:200], proc.returncode
            except (subprocess.TimeoutExpired, OSError) as exc:
                info["cli_version"], info["cli_version_exit_code"] = "error: " + repr(exc)[:150], None
    return info


# ----------------------------------------------------------------------------------------------------------------- prompts

SYSTEM_PROMPT = """You are a Lean 4 proof engineer working alone and non-interactively in a sandboxed Lean project (Lean 4.30.0 with Mathlib). Nobody will answer questions; finish the task in this session.

TASK. A mathematical argument contains a defective local claim, already located for you. Fill the template's declared hole within its allowed grammar, prove the fixed repair and nonvacuity obligations, and prove the fixed record-specific final obligation; every obligation's statement is given and must not be changed. If you cannot prove the final obligation, write the single line `-- CANNOT: <one-line reason>` where it would go.

TOOLS. Exactly these exist:
  * Write, Read and Edit on files inside the working directory (your sandbox). The working directory is READ-ONLY except its subdirectory `work/`: every file you create or edit must live under `work/` (the deliverable `work/SUBMISSION.lean`, scratch files such as `work/test.lean`); a write anywhere else fails with "Read-only file system".
  * Bash. The only build/compile command is `lake env lean <file>.lean` with one relative .lean file and no options, run from the working directory root (for example `lake env lean work/SUBMISSION.lean`); it may be wrapped as `timeout <seconds> lake env lean <file>.lean` or `time lake env lean <file>.lean` and followed by `&& echo <word>`, and each such command counts as one `lake env lean` run (a leading `cd work &&` is tolerated and counted too, but the compile is then refused, so do not use it). Read-only inspection commands are permitted and do not count: `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `rg`, `find`, `sed -n`, `awk`, `diff`, `stat`, `file`, `sort`, `uniq`, `cut`, `tr`, `echo`, `pwd`, `tree`, and `xargs` between them, joined by `|`, `;`, `&&` or `||`, on paths inside the working directory only, with no redirection except to /dev/null, no heredoc, no `$(...)`, no `~`, no `..`. Any other command (any other program, any other `lake` form, a pipe, option or redirection on `lake env lean`) ends the attempt.
There is no internet, no search and no subagent. Mathlib is available (defs_only.lean imports it). A compile of a Mathlib-importing file takes about 15-30 seconds.

BUDGET. Exceeding any of these voids the attempt: at most {kernel} `lake env lean` runs; at most {tokens} output tokens in total (thinking included); at most {turns} turns; {minutes} minutes of wall clock.

SUBMISSION FORMAT. The deliverable is the single file work/SUBMISSION.lean (inside the writable subdirectory `work/` of the working directory). It must
  1. begin with exactly the import line(s) of the template (`import defs_only`; import nothing else);
  2. contain the repair template with the hole filled and every other character unchanged (docstrings included), inside the namespace the template opens, and nothing outside that namespace; the file must end with the line `end <Namespace>` that closes that namespace (the namespace named under OBLIGATIONS): a file that stops after the final theorem and omits this line fails the structure check;
  3. contain, inside that namespace, theorems with exactly the names and statements listed under OBLIGATIONS; for the final theorem you may instead write the single line `-- CANNOT: <reason>`;
  4. compile with `lake env lean work/SUBMISSION.lean` with no error and no `sorry`;
  5. use no axiom beyond propext, Classical.choice and Quot.sound: no `sorry`, `admit`, `axiom`, `native_decide`, `unsafe`, `implemented_by`, `extern`, `opaque`; and no `notation`, `macro`, `macro_rules`, `syntax`, `elab`, `instance`, `attribute`, `export`, `section`, extra `namespace`, or `set_option` other than maxHeartbeats/maxRecDepth. The only commands admitted anywhere in the file are `import`, `namespace`/`end`, plain `open X`, `set_option` (as above), `def`, `theorem`, `lemma`, `abbrev`, `example`, `structure`, `inductive`, `class` (with `noncomputable`/`private`/`protected` and `@[...]` attributes on your own helpers); every other command (`variable`, `universe`, `alias`, `irreducible_def`, `mutual`, `deriving`, `unif_hint`, `#check`, `#print`, ...) is refused. Helper lemmas inside the namespace, placed AFTER the fixed part, are fine; the hole itself may name only the template's binders, names of the fixed part / defs_only.lean and identifiers the task lists as admitted, never a helper you declare;
  6. not redefine any declaration of defs_only.lean (the reserved names are listed); the given files are read-only and must not be modified.
Make sure work/SUBMISSION.lean compiles before you stop. Your last line must be exactly `SUBMITTED` or `SUBMITTED-CANNOT-FINAL`.
""".format(kernel=MAX_KERNEL_CHECKS, tokens=MAX_OUTPUT_TOKENS, turns=MAX_TURNS, minutes=WALL_CAP // 60)


def build_prompts(packet, arm):
    """(system, user) for one arm. Arm A: source, defect, defs_only, template, obligations. Arm B: the same plus witness_min."""
    if arm not in ARMS:
        raise ValueError("arm must be A or B")
    c = packet["contract"]
    lines = ["# Record %s: %s" % (c["record_id"], c.get("title", "")), "",
             "## Source argument (full context)", "", packet["source_context"].strip(), "",
             "## Located defective declaration", "",
             "Declaration: `%s`" % c["located_defect"].get("declaration", ""), "",
             "```lean", c["located_defect"].get("lean_text", "").strip(), "```", "",
             c["located_defect"].get("description", "").strip(), "",
             "## Files in your working directory", "",
             "- `defs_only.lean`: the definitions (full text below), already compiled; `import defs_only` resolves. Read-only.",
             "- `lakefile.toml`, `lake-manifest.json`, `lean-toolchain`, `.lake/`: the fixed Lean project. Read-only.",
             "- `work/`: the ONLY writable directory. Put `work/SUBMISSION.lean` and every scratch file (e.g. `work/test.lean`) there "
             "and compile with `lake env lean work/<file>.lean`. Writes anywhere else fail."]
    if arm == "B":
        if not packet.get("witness_min"):
            raise ValueError("arm B requires witness_min.lean in the packet")
        lines.append("- `witness_min.lean`: a kernel-checked counterexample to the located claim (full text below), already compiled; "
                     "you may study it and compile scratch files that import it, but SUBMISSION.lean must import only defs_only. Read-only.")
    lines += ["", "## defs_only.lean", "", "```lean", packet["defs_only"].rstrip(), "```", ""]
    if arm == "B":
        lines += ["## witness_min.lean (checked counterexample)", "", "```lean", packet["witness_min"].rstrip(), "```", ""]
    lines += ["## Repair template (fill the hole `%s`; every other character is fixed)" % c["hole_marker"], "",
              "```lean", c["repair_template"].rstrip(), "```", "",
              "Allowed edit: " + c.get("allowed_edit", "").strip(), "",
              "Reserved names (never redefine): " + ", ".join(c.get("reserved_names", [])), "",
              "## OBLIGATIONS (exact names and statements, inside `namespace %s`)" % c["submission_namespace"], ""]
    for ob in c["obligations"]:
        lines += ["```lean", "theorem %s : %s" % (ob["name"], ob["statement"].strip()), "```",
                  "(%s: %s)" % (ob["role"], ob.get("description", "").strip()), ""]
    lines += ["## Submission", "",
              "Write work/SUBMISSION.lean as specified in the instructions, compile it with `lake env lean work/SUBMISSION.lean`, "
              "fix errors within the budget, and finish with the line `SUBMITTED` or `SUBMITTED-CANNOT-FINAL`."]
    return SYSTEM_PROMPT, "\n".join(lines) + "\n"


def argv_for(model, effort, system_prompt):
    return [EXECUTABLE, "-p", "--model", model, "--effort", effort, "--restricted", "--tools", ",".join(ALLOWED_TOOLS),
            "--allowedTools", *CLI_ALLOW_RULES, "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--setting-sources", "", "--permission-mode", "dontAsk", "--permission-prompts", "none",
            "--disable-slash-commands", "--max-turns", str(MAX_TURNS), "--output-format", "stream-json", "--verbose",
            "--include-partial-messages",
            "--no-session-persistence", "--prompt-suggestions", "false", "--system-prompt", system_prompt]


# ------------------------------------------------------------------------------------------------------ stream accounting

def message_text(message):
    content = (message or {}).get("content")
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def result_text(block):
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")
    return ""


def looks_like_denial(text):
    low = (text or "").lower()
    return any(marker in low for marker in DENIAL_MARKERS)


class StreamAccount:
    """Consumes stream-json lines; keeps per-request usage, tool calls, kernel checks and live budget estimates.

    Bash tool calls are of three kinds: `kernel_check` (ALLOWED_COMMAND_RE bare or, since fix_r7, wrapped under KERNEL_CHECK_RULE; counted
    against MAX_KERNEL_CHECKS), `inspection_command` (fix_r6: read-only inspection under INSPECTION_RULE, fix_r7: xargs stages under
    XARGS_RULE; audited but never counted and never a violation) and `disallowed_command` (a violation when its result shows execution).
    `sandbox_root` is the in-namespace sandbox path: the only root under which an absolute path in an inspection command is admitted
    (None: every absolute path other than /dev/null is refused)."""

    def __init__(self, requested_model, sandbox_root=None):
        self.requested_model = requested_model
        self.sandbox_root = str(sandbox_root) if sandbox_root else None
        self.init = None
        self.result = None
        self.requests = {}          # message id -> usage snapshot (max of seen values) + model
        self.order = []
        self.thinking_estimate = 0  # CLI estimate for the current request, if the CLI emits it
        self.stream_chars = {}      # message id -> characters seen in content_block_delta events (partial messages)
        self.block_chars = {}       # message id -> characters of the assistant event's content blocks
        self.current_stream_id = None
        self.tool_uses = {}         # tool_use id -> {name, input, kind, index}
        self.tool_order = []
        self.tool_results = {}      # tool_use id -> {is_error, text}
        self.texts = []
        self.user_events = 0
        self.events = 0
        self.unparsed_lines = 0
        self.reader_error = None

    # ---- consumption
    def consume(self, line):
        self.events += 1
        try:
            ev = json.loads(line)
        except ValueError:
            self.unparsed_lines += 1
            return
        if not isinstance(ev, dict):
            self.unparsed_lines += 1
            return
        kind, sub = ev.get("type"), ev.get("subtype")
        if kind == "system" and sub == "init":
            self.init = ev
        elif kind == "system" and sub == "thinking_tokens":
            self.thinking_estimate = max(self.thinking_estimate, count(ev.get("estimated_tokens")))
        elif kind == "stream_event":
            # --include-partial-messages: the API's own stream. message_delta carries the cumulative output_tokens of the
            # request (the `assistant` events only carry the message_start snapshot, i.e. a handful of tokens).
            e = ev.get("event") or {}
            et = e.get("type")
            if et == "message_start":
                msg = e.get("message") or {}
                rid = self.register(msg.get("id") or "unknown", msg.get("model"), msg.get("usage") or {})
                self.current_stream_id = rid
            elif et == "message_delta":
                rid = self.current_stream_id or (self.order[-1] if self.order else self.register("unknown", None, {}))
                self.merge_usage(rid, e.get("usage") or {})
            elif et == "content_block_delta":
                d = e.get("delta") or {}
                text = d.get("text") or d.get("thinking") or d.get("partial_json") or ""
                rid = self.current_stream_id or (self.order[-1] if self.order else "unknown")
                self.stream_chars[rid] = self.stream_chars.get(rid, 0) + len(text)
        elif kind == "assistant":
            msg = ev.get("message") or {}
            rid = self.register(msg.get("id") or "unknown", msg.get("model"), msg.get("usage") or {})
            chars = 0
            for block in msg.get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    self.texts.append(block.get("text", ""))
                    chars += len(block.get("text", ""))
                elif block.get("type") == "thinking":
                    chars += len(block.get("thinking", "") or "")
                elif block.get("type") == "tool_use":
                    chars += len(json.dumps(block.get("input"), ensure_ascii=False)) if block.get("input") is not None else 0
            self.block_chars[rid] = self.block_chars.get(rid, 0) + chars
            for block in msg.get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    pass
                elif block.get("type") == "tool_use":
                    bid = block.get("id") or ("tool_%d" % len(self.tool_order))
                    if bid in self.tool_uses:
                        continue
                    name, inp = block.get("name"), block.get("input") if isinstance(block.get("input"), dict) else {}
                    entry = {"id": bid, "name": name, "request_id": rid, "index": len(self.tool_order), "input": inp,
                             "kind": self.classify_tool_use(name, inp)}
                    if name == "Bash" and entry["kind"] != "kernel_check":
                        entry["command_check"] = inspection_command_check(inp.get("command", "") or "", self.sandbox_root)
                    elif name == "Bash":
                        entry["kernel_check_form"] = kernel_check_form(inp.get("command", "") or "")      # fix_r7: bare or wrapped
                    self.tool_uses[bid] = entry
                    self.tool_order.append(bid)
        elif kind == "user":
            self.user_events += 1
            for block in ((ev.get("message") or {}).get("content") or []):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    text = result_text(block)
                    self.tool_results[block.get("tool_use_id")] = {"is_error": block.get("is_error") is True, "text": text[:2000],
                                                                    "text_sha256": sha(text)}
        elif kind == "result":
            self.result = ev

    def register(self, rid, model, usage):
        if rid not in self.requests:
            self.order.append(rid)
            self.requests[rid] = {"model": model}
            self.thinking_estimate = 0
        if model:
            self.requests[rid]["model"] = model
        self.merge_usage(rid, usage)
        return rid

    def merge_usage(self, rid, usage):
        row = self.requests.setdefault(rid, {"model": None})
        for key in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
            if key in usage:
                row[key] = max(count(row.get(key)), count(usage.get(key)))

    def chars_estimate(self, rid):
        return int(max(self.stream_chars.get(rid, 0), self.block_chars.get(rid, 0)) / CHARS_PER_TOKEN + 0.999)

    def classify_tool_use(self, name, inp):
        if name == "Bash":
            cmd = inp.get("command", "") if isinstance(inp, dict) else ""
            return classify_command(cmd or "", self.sandbox_root)
        if name in ALLOWED_TOOLS:
            return "file_tool"
        return "forbidden_tool"

    # ---- derived quantities
    def output_tokens(self, include_estimate=True):
        """Live output-token estimate, summed over requests: per request the largest of the reported usage (message_delta with
        --include-partial-messages; otherwise only the message_start snapshot), the character-based estimate of its content, and
        (for the current request) the CLI's thinking estimate. The native total in the result event is the measurement."""
        total = 0
        for i, rid in enumerate(self.order):
            out = count(self.requests[rid].get("output_tokens"))
            if include_estimate:
                out = max(out, self.chars_estimate(rid))
                if i == len(self.order) - 1:
                    out = max(out, self.thinking_estimate)
            total += out
        if not self.order and include_estimate:
            total = self.thinking_estimate
        return total

    def kernel_checks(self):
        return sum(1 for bid in self.tool_order if self.tool_uses[bid]["kind"] == "kernel_check")

    def forbidden_tool_uses(self):
        return [self.tool_uses[b] for b in self.tool_order if self.tool_uses[b]["kind"] == "forbidden_tool"]

    def disallowed_commands(self):
        return [self.tool_uses[b] for b in self.tool_order if self.tool_uses[b]["kind"] == "disallowed_command"]

    def inspection_commands(self):
        """fix_r6: read-only inspection commands (kind `inspection_command`): audited, never counted, never a violation."""
        return [self.tool_uses[b] for b in self.tool_order if self.tool_uses[b]["kind"] == "inspection_command"]

    def kernel_check_summary(self):
        """fix_r7: how the kernel checks were written: bare, or wrapped (timeout / time / cd <subdir> && / && echo); the wrapped ones listed."""
        rows = [self.tool_uses[b] for b in self.tool_order if self.tool_uses[b]["kind"] == "kernel_check"]
        forms = [e.get("kernel_check_form") or kernel_check_form(e["input"].get("command", "") or "") for e in rows]
        return {"rule": "fix_r7", "total": len(rows), "bare": sum(1 for f in forms if f["bare"]), "wrapped": sum(1 for f in forms if not f["bare"]),
                "wrappers_used": {w: sum(1 for f in forms if w in f["wrappers"]) for w in ("cd", "timeout", "time", "echo")},
                "wrapped_commands": [{"index": e["index"], "id": e["id"], "command": e["input"].get("command"), "file": f["file"], "wrappers": f["wrappers"]}
                                     for e, f in zip(rows, forms) if not f["bare"]]}

    def inspection_summary(self):
        denied = self.denied_ids()
        rows = self.inspection_commands()
        return {"rule": "fix_r7", "admitted_programs": list(INSPECTION_COMMANDS), "xargs_rule": XARGS_RULE, "attempted": len(rows),
                "executed": sum(1 for e in rows if e["id"] in self.tool_results and e["id"] not in denied),
                "denied_by_cli": sum(1 for e in rows if e["id"] in denied),
                "commands": [{"index": e["index"], "id": e["id"], "command": e["input"].get("command"),
                              "programs": (e.get("command_check") or {}).get("programs"), "denied": e["id"] in denied,
                              "result_is_error": (self.tool_results.get(e["id"]) or {}).get("is_error")} for e in rows]}

    def denied_ids(self):
        ids = set()
        for row in ((self.result or {}).get("permission_denials") or []):
            if isinstance(row, dict) and row.get("tool_use_id"):
                ids.add(row["tool_use_id"])
        for bid, res in self.tool_results.items():
            if res["is_error"] and looks_like_denial(res["text"]):
                ids.add(bid)
        return ids

    def executed_disallowed_commands(self):
        """Disallowed Bash commands whose tool_result shows execution (a non-error result) rather than a denial: the restriction failed.

        An error result without a recognisable denial text is ambiguous (denied with unknown wording, or ran and failed); it is
        listed by ambiguous_disallowed_results() and never counted as executed.
        """
        denied = self.denied_ids()
        rows = []
        for entry in self.disallowed_commands():
            res = self.tool_results.get(entry["id"])
            if res is None or entry["id"] in denied or res["is_error"]:
                continue
            rows.append({**entry, "result_excerpt": res["text"][:300]})
        return rows

    def ambiguous_disallowed_results(self):
        denied = self.denied_ids()
        return [{**e, "result_excerpt": self.tool_results[e["id"]]["text"][:300]} for e in self.disallowed_commands()
                if e["id"] in self.tool_results and e["id"] not in denied and self.tool_results[e["id"]]["is_error"]]

    def gatekeeper_refusals(self):
        return [self.tool_uses[b] for b in self.tool_order
                if self.tool_uses[b]["kind"] == "kernel_check" and "repair-sandbox: refused" in self.tool_results.get(b, {}).get("text", "")]

    def response_models(self):
        return sorted({r.get("model") for r in self.requests.values() if r.get("model")})

    def native_usage(self):
        rows = (self.result or {}).get("modelUsage")
        fields = ("inputTokens", "cacheCreationInputTokens", "cacheReadInputTokens", "outputTokens")
        ok = isinstance(rows, dict) and bool(rows) and all(isinstance(r, dict) and all(isinstance(r.get(k), int) and not isinstance(r.get(k), bool)
                                                                                    and r.get(k) >= 0 for k in fields) for r in rows.values())
        if not ok:
            return None
        return {"per_model": {m: {k: r.get(k) for k in fields} for m, r in rows.items()},
                "output_tokens": sum(r["outputTokens"] for r in rows.values()),
                "total_tokens": sum(sum(r[k] for k in fields) for r in rows.values())}

    def per_request_usage(self):
        return [{"message_id": rid, **self.requests[rid]} for rid in self.order]

    def tool_call_log(self):
        rows = []
        for bid in self.tool_order:
            e = self.tool_uses[bid]
            res = self.tool_results.get(bid)
            inp = e["input"]
            summary = {"command": inp.get("command")} if e["name"] == "Bash" else {"file_path": inp.get("file_path")}
            if e["name"] == "Bash" and e.get("command_check") is not None:
                summary["command_check"] = e["command_check"]                     # fix_r6: why the command is inspection / disallowed
            if e["name"] == "Bash" and e.get("kernel_check_form") is not None:
                summary["kernel_check_form"] = {k: e["kernel_check_form"][k] for k in ("bare", "file", "wrappers")}   # fix_r7
            rows.append({"index": e["index"], "id": bid, "tool": e["name"], "kind": e["kind"], "request_id": e["request_id"], **summary,
                         "result_is_error": res["is_error"] if res else None, "result_excerpt": res["text"][:300] if res else None,
                         "denied": bid in self.denied_ids()})
        return rows

    def library_reads(self):
        return [self.tool_uses[b]["input"].get("file_path") for b in self.tool_order
                if self.tool_uses[b]["name"] == "Read" and ".lake/packages" in str(self.tool_uses[b]["input"].get("file_path", ""))]

    # ---- live stop decision
    def stop_reason(self, elapsed):
        """The first controlled stop, or None. Order: contract violations observed live, then budgets, then the wall clock."""
        if self.forbidden_tool_uses():
            return {"reason": "contract_violation", "detail": "forbidden_tool_used", "tool": self.forbidden_tool_uses()[0]["name"]}
        if self.executed_disallowed_commands():
            return {"reason": "contract_violation", "detail": "disallowed_command_executed",
                    "command": self.executed_disallowed_commands()[0]["input"].get("command")}
        if self.output_tokens() > MAX_OUTPUT_TOKENS:
            return {"reason": "output_budget", "detail": "live_output_estimate_exceeded_max", "live_output_estimate": self.output_tokens(),
                    "max_output_tokens": MAX_OUTPUT_TOKENS}
        if self.kernel_checks() > MAX_KERNEL_CHECKS:
            return {"reason": "kernel_budget", "detail": "kernel_checks_exceeded_max", "kernel_checks": self.kernel_checks(),
                    "max_kernel_checks": MAX_KERNEL_CHECKS}
        if elapsed > WALL_CAP:
            return {"reason": "wall_clock", "detail": "wall_clock_cap", "elapsed_seconds": round(elapsed, 1), "wall_cap_seconds": WALL_CAP}
        return None


def classify_attempt(acc, exit_code, stop, submission, integrity, drain):
    """Fail-closed attempt class (mutually exclusive). Violations outrank budgets, budgets outrank outcomes.

    submission: {"present": bool, "bytes": int, "regular_file": bool}
    integrity: {"packet_files_unchanged", "inputs_unchanged", "inputs_read_only_mounts": bool, "writes_outside_work": list,
                "gatekeeper_log_present": bool, "kernel_checks_logged": int|None}  (all fail-closed: a missing key is a violation)
    drain: {"required": bool, "complete": bool}.
    """
    result = acc.result or {}
    native = acc.native_usage()
    kernel_log = integrity.get("kernel_checks_logged")
    checks = {
        "init_seen": acc.init is not None,
        "init_tools_within_contract": acc.init is None or set(acc.init.get("tools") or []) <= set(ALLOWED_TOOLS),
        "no_mcp_servers": acc.init is None or not (acc.init.get("mcp_servers") or []),
        "response_model_matches": all(m == acc.requested_model or m.startswith(acc.requested_model) for m in acc.response_models()),
        "no_forbidden_tool_use": not acc.forbidden_tool_uses(),
        "no_disallowed_command_executed": not acc.executed_disallowed_commands(),
        "stream_reader_completed": acc.reader_error is None,
        "controlled_drain_complete": (not drain["required"]) or drain["complete"],
        "packet_files_unchanged": integrity.get("packet_files_unchanged") is True,
        "inputs_unchanged": integrity.get("inputs_unchanged") is True,
        "inputs_read_only_mounts": integrity.get("inputs_read_only_mounts") is True,
        "no_writes_outside_work": integrity.get("writes_outside_work") == [],
        "gatekeeper_log_present": integrity.get("gatekeeper_log_present") is True,
        "submission_regular_file": (not submission["present"]) or submission["regular_file"],
        "exit_code_zero": exit_code == 0,
        "result_event_seen": acc.result is not None,
        "result_success": result.get("subtype") == "success" and result.get("is_error") is not True,
        "native_usage_present": native is not None,
        "native_output_within_max": native is not None and native["output_tokens"] <= MAX_OUTPUT_TOKENS,
        "kernel_checks_within_max": acc.kernel_checks() <= MAX_KERNEL_CHECKS and kernel_log is not None and kernel_log <= MAX_KERNEL_CHECKS,
        "no_hard_stop": stop is None,
    }
    violations = [name for name, ok in checks.items() if not ok and name in (
        "init_tools_within_contract", "no_mcp_servers", "response_model_matches", "no_forbidden_tool_use",
        "no_disallowed_command_executed", "stream_reader_completed", "controlled_drain_complete", "packet_files_unchanged",
        "inputs_unchanged", "inputs_read_only_mounts", "no_writes_outside_work", "gatekeeper_log_present", "submission_regular_file")]
    budget = None
    if stop is not None and stop["reason"] in ("output_budget", "kernel_budget", "wall_clock") and (acc.order or acc.result):
        budget = stop
    elif result.get("subtype") == "error_max_turns":
        budget = {"reason": "turn_budget", "detail": "cli_max_turns", "num_turns": result.get("num_turns"), "max_turns": MAX_TURNS}
    elif native is not None and native["output_tokens"] > MAX_OUTPUT_TOKENS:
        budget = {"reason": "output_budget", "detail": "native_output_tokens_exceeded_max", "native_output_tokens": native["output_tokens"],
                  "max_output_tokens": MAX_OUTPUT_TOKENS}
    elif not checks["kernel_checks_within_max"]:
        budget = {"reason": "kernel_budget", "detail": "kernel_checks_exceeded_max", "kernel_checks_stream": acc.kernel_checks(),
                  "kernel_checks_logged": kernel_log, "max_kernel_checks": MAX_KERNEL_CHECKS}
    if violations:
        attempt_class, detail = "CONTRACT_VIOLATION", {"reason": "contract_violation", "violations": violations,
                                                       "stop": stop, "failed_checks": sorted(n for n, ok in checks.items() if not ok)}
    elif budget is not None:
        attempt_class, detail = "BUDGET_EXHAUSTED", budget
    elif not acc.order and (acc.result is None or result.get("is_error") is True):
        attempt_class, detail = "TRANSPORT_FAILURE", {"reason": "transport_failure", "stop": stop,
                                                      "result_subtype": result.get("subtype"), "events": acc.events}
    elif stop is None and checks["init_seen"] and checks["exit_code_zero"] and checks["result_success"] and checks["native_usage_present"]:
        if submission["present"] and submission["bytes"] > 0:
            attempt_class, detail = "VALID_SUBMISSION", {"reason": "submission_present"}
        else:
            attempt_class, detail = "NO_SUBMISSION", {"reason": "no_submission_file"}
    else:
        attempt_class, detail = "CONTRACT_VIOLATION", {"reason": "contract_violation", "detail": "protocol_check_failed", "stop": stop,
                                                       "failed_checks": sorted(n for n, ok in checks.items() if not ok)}
    return attempt_class, detail, checks


def kernel_counts(acc, integrity):
    """Both kernel-check counters side by side: the stream (Bash tool calls matching the grammar, refusals included) and the
    gatekeeper log (accepted calls, written outside the sandbox root). Expected log count = stream - refusals; a mismatch is flagged."""
    stream = acc.kernel_checks()
    refusals = len(acc.gatekeeper_refusals())
    logged = integrity.get("kernel_checks_logged")
    expected = stream - refusals
    return {"from_stream_tool_calls": stream, "gatekeeper_refusals": refusals, "from_gatekeeper_log": logged,
            "expected_gatekeeper_count": expected, "counts_agree": logged == expected, "mismatch_flagged": logged != expected,
            "max": MAX_KERNEL_CHECKS, "gatekeeper_log_path": integrity.get("gatekeeper_log_path"),
            "gatekeeper_log_sha256": integrity.get("gatekeeper_log_sha256"),
            "gatekeeper_log_outside_sandbox": integrity.get("gatekeeper_log_outside_sandbox")}


# ---------------------------------------------------------------------------------------------------------------- receipts

def attempt_receipts(workdir):
    """(tag, dispatch, saved ATTEMPT receipt or None) per DISPATCH of one attempt directory, oldest first."""
    rows = []
    for path in Path(workdir).glob("DISPATCH_*.json"):
        dispatch = json.loads(path.read_text(encoding="utf-8"))
        attempt_path = path.with_name("ATTEMPT_" + path.name[len("DISPATCH_"):])
        saved = json.loads(attempt_path.read_text(encoding="utf-8")) if attempt_path.exists() else None
        if saved is not None and (not isinstance(saved, dict) or saved.get("dispatch") != dispatch or not isinstance(saved.get("attempt"), dict)):
            raise RuntimeError("attempt/dispatch identity mismatch: " + str(attempt_path))
        rows.append((dispatch.get("dispatched_time_ns") or 0, path.name, dispatch, saved))
    return [(d.get("tag"), d, s) for _, _, d, s in sorted(rows, key=lambda r: r[:2])]


def reserve(workdir, tag, identity):
    """Write DISPATCH_<tag>.json (consumes a physical attempt). Refuses a finished record, a duplicate tag and an unreconciled dispatch."""
    workdir = Path(workdir)
    if (workdir / "record.json").exists():
        raise RuntimeError("record already completed: " + str(workdir / "record.json"))
    if tag not in ATTEMPT_TAGS:
        raise RuntimeError("unknown attempt tag " + tag)
    path = workdir / ("DISPATCH_%s.json" % safe(tag))
    if path.exists():
        raise RuntimeError("duplicate dispatch: " + str(path))
    for earlier in sorted(workdir.glob("DISPATCH_*.json")):
        if not earlier.with_name("ATTEMPT_" + earlier.name[len("DISPATCH_"):]).exists():
            raise RuntimeError("unreconciled dispatch without ATTEMPT receipt: %s (never rerun automatically)" % earlier)
    ticket = {"ticket_id": uuid.uuid4().hex, "tag": tag, "dispatched_time_ns": time.time_ns(), "dispatched_utc": now(), **identity}
    atomic_json(path, ticket)
    return ticket


def complete_attempt(workdir, ticket, attempt):
    attempt = dict(attempt)
    attempt["completed_time_ns"] = time.time_ns()
    attempt["completed_utc"] = now()
    atomic_json(Path(workdir) / ("ATTEMPT_%s.json" % safe(ticket["tag"])), {"dispatch": ticket, "attempt": attempt})
    return attempt


def write_record(workdir, record):
    path = Path(workdir) / "record.json"
    if path.exists():
        raise RuntimeError("refusing to overwrite completed record " + str(path))
    record["completed_time_ns"] = time.time_ns()
    record["finished_utc"] = now()
    atomic_json(path, record)


def should_retry(attempt):
    return attempt.get("attempt_class") == "TRANSPORT_FAILURE"


def harness_fingerprint():
    files = ["repair_common.py", "run_repair.py", "validate.py", "sandbox_exec.sh", "sandbox_bin/lake"]
    parts = {name: file_sha(HERE / name) for name in files if (HERE / name).exists()}
    return {"files": parts, "sha256": sha(json.dumps(parts, sort_keys=True))}
