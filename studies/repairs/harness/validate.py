#!/usr/bin/env python3
"""Repair/recovery track: deterministic validators for one SUBMISSION.lean, run in the common Lean environment.

  python3 validate.py --record SYN01 --submission PATH [--out verdict.json] [--workspace DIR] [--cache-dir DIR] [--keep]
                      [--packet-dir DIR] [--evaluator-dir DIR] [--hole-grammar evaluator.json]

ONE call produces the complete fixed-contract verdict. Checks (each reported pass/fail with the raw Lean messages):
  imports, namespace_structure, forbidden_tokens, reserved_names        text checks on the comment-stripped submission
  template_structure     the filled template matches task.json's template with the hole (structural, per declaration; diff reported)
  obligations_declared   every obligation theorem is declared (or the final theorem carries an explicit `-- CANNOT:` line)
  compile, no_sorry      `lake env lean` on SUBMISSION.lean against the packet's defs_only (compiled here, never the sandbox copy)
  axioms                 `#print axioms` on every submitted theorem: only propext / Classical.choice / Quot.sound
  universal, nonvacuity, endpoint_final
                         an evaluator-generated file states each obligation EXACTLY as task.json does and proves it by the
                         submitted constant (`theorem ob_X : <statement> := NS.X`), so the submitted theorem must have the
                         declared type; the final theorem statement is the visible one; no sorry. A record without a `final`
                         obligation (or whose evaluator.json says has_final_theorem: false) reports endpoint_final as not applicable.
  hidden_instance_agreement
                         evaluator/<record>/AGREE.lean (never copied into any sandbox) imports SUBMISSION and the hidden
                         reference and checks agreement on the record's listed finite instances by decide/norm_num
  hole_syntax            the record's hole grammar (evaluator.json -> hole_syntax: regex, forbidden tokens, max lines) applied to
                         the extracted `hole_filled_with` (folded in from evaluator_records/check_record.sh); not applicable when
                         the record has no evaluator.json
  hole_binding           fix_r3: inside CHECK.lean, `theorem «validator hole binding» BINDERS : NAME ARGS = (BODY : TYPE) := rfl` in the
                         record namespace, BODY = the template body with the hole replaced by the extracted text: the text the grammar
                         judged must be definitionally the submitted constant. Emitted for templates of the shape
                         `def NAME BINDERS : TYPE := …hole…` (every current record); not applicable otherwise.
fix_r3 (verifier round 2, B1 / TASK-552): chunks() ends a top-level command only at a column-0 line that BEGINS a Lean command
(COMMAND_KEYWORDS, `@[`, `#…`); any other column-0 line (`+ 0 / (x - 2)`, `) |> fun _ => …`, `* 2`, `∧ …`) continues the previous
declaration, as Lean's term parser does, so the extracted hole is the ENTIRE remainder Lean elaborates; a hole running onto more lines
than the grammar allows (default 1) or containing a command keyword fails template_structure with "continuation beyond the template
declaration". reserved_names now rejects every declaration whose name equals, or whose last component equals the last component of,
any identifier of the template's fixed text, the obligation statements, task.json reserved_names or the record namespace (qualified
redefinitions such as `def Real.log` / `def NS.HasDecDigits` included), every `_root_.` declaration, and every `open`/`export`/`namespace`
other than the record namespace.
Verdict: repair_valid (all checks but the endpoint), endpoint_proved, all_pass (= verdict PASS); final_declared_cannot.
Pinned in every verdict: the exact validator invocation (argv, cwd, host, python, validator file hashes, exit code), the sha256 of
task.json / defs_only.lean / witness_min.lean / contract.json / the submission / reference.lean / AGREE.lean / instances.json /
evaluator.json, the CONTRACT digests (task_contract: the verdict-relevant fields of task.json with prose removed; evaluator_contract:
hole_syntax + has_final_theorem) so a wording edit of task.json/evaluator.json is distinguishable from a change of the contract,
the Lean toolchain (file + `lean --version`), the Mathlib revision from lake-manifest.json, and every Lean run's argv, cwd and exit
code. Host safety: a submission containing a code-executing token (#eval, #guard, run_cmd, initialize, macro, elab, syntax, simproc,
extern, implemented_by, unsafe, include_str ...) anywhere in its comment-stripped text is never compiled (the stripper is
string-literal aware, so a `--` or `/-` inside a string cannot hide code from the gate); every Lean run happens inside a bubblewrap
namespace with no network, a tmpfs HOME containing only ~/.elan, and only the workspace and the read-only common packages visible.
fix_r4 (verifier round 4, B1 on P02): (1) HOLE IDENTIFIER RULE, folded into hole_syntax: `hole_filled_with` is tokenised (Lean identifiers,
dotted and «»-quoted, numerals; hex/binary/octal/scientific literals are rejected as malformed numerals) and every identifier must be a
binder of the hole-bearing template declaration (or a binder the hole itself introduces with ∀/∃/fun/∑…), a name declared in the
template's fixed part or in defs_only.lean, an identifier of the fixed text / obligation statements (un-redeclarable since fix_r3), or
listed in evaluator.json hole_syntax.allowed_identifiers; field notation on a binder head (`q.1`, `s.length`) is admitted because Lean
resolves fields through the head's type namespace, never the current namespace (probe 2026-09-23); any identifier declared in the
SUBMISSION, and any other identifier, fails with "identifier not permitted in hole: …". (2) DECLARATION ORDER: any declaration or command
other than set_option/open between `namespace NS` and the template's first fixed declaration, or between fixed declarations, fails
template_structure ("declaration before the fixed part" / "declaration inside the fixed part"). (3) `notation3`, `binder_predicate` and
every `notation*` / `*_predicate` command trip forbidden_tokens and the host-safety gate. (4) «»-quoted declaration names are read
(`def «HasDerivAt»` is the reserved name HasDerivAt).
fix_r5 (verifier round 5, B1/B2): (1) COMMAND WHITELIST: the only commands a submission may contain, at ANY position (column 0,
indented under another command, glued after `open … in`), are import / namespace / end / open / set_option / def / theorem / lemma /
abbrev / example / structure / inductive / class (+ noncomputable / private / protected, `@[…]`); every other command keyword
(`alias`, `irreducible_def`, `variable`, `universe`, `mutual`, `deriving`, `unif_hint`, `omit`, `include`, `local`, `scoped`, `nonrec`,
`partial`, …) and every `#…` command (`#check`, `#print`, …) fails forbidden_tokens ("command not admitted"); `eval%` is host-unsafe.
(2) `alias` (both forms), `irreducible_def` and `example` are declarations for the reserved-name scan, the hole identifier rule's
submission-declared set and the declaration-order rule. (3) DECLARATION ORDER: every chunk, declaration or `@[…]` attribute between
`namespace NS` and the first fixed declaration other than set_option/open, and EVERY chunk, declaration, command or attribute between
fixed declarations, fails template_structure; a stray `end` (any `end` other than the closing `end NS`) fails namespace_structure.
(4) evaluator.json hole_syntax.allowed_identifiers are reserved names (un-redeclarable) and enter the evaluator_contract digest, which
now covers every non-prose hole_syntax key. (5) Field notation on a binder head (`n.div 2`, `p.find`) is refused when the field names
a forbidden token of the record's grammar (by last component) or the operation behind a forbidden operator symbol (`/` -> div/ediv/…).
"""
import argparse, json, os, re, shutil, socket, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repair_common as rc  # noqa: E402

LEAN_TIMEOUT = 900
BWRAP = "/usr/bin/bwrap"
DECL_KINDS = ("def", "theorem", "lemma", "abbrev", "instance", "structure", "inductive", "class", "example", "axiom", "opaque")
FORBIDDEN_TOKENS = ("sorry", "admit", "axiom", "native_decide", "unsafe", "implemented_by", "extern", "opaque", "notation", "infix", "infixl",
                    "infixr", "prefix", "postfix", "macro", "macro_rules", "syntax", "elab", "elab_rules", "instance", "attribute", "export",
                    "section", "ofReduceBool", "trustCompiler", "initialize", "builtin_initialize", "run_cmd", "run_tac",
                    "#eval", "#guard", "include_str", "simproc", "dsimproc", "simproc_decl", "builtin_simproc", "builtin_dsimproc",
                    "declare_syntax_cat", "command_elab", "term_elab", "init",
                    "run_meta", "run_elab", "#exit", "MetaM", "TermElabM", "CommandElabM", "CoreM", "TacticM", "evalExpr", "evalTerm",
                    "unsafeIO", "unsafeCast", "ptrAddrUnsafe", "Lean.Elab", "Lean.Meta", "IO.Process", "IO.FS",
                    "notation3", "binder_predicate")       # fix_r4: syntax-defining commands token_present's boundary missed
# Tokens that can execute code at elaboration or import time: their presence ANYWHERE in the comment-stripped submission stops the
# validator BEFORE any Lean run (host-safety gate). `#guard` evaluates its term with the interpreter like `#eval`.
HOST_UNSAFE_TOKENS = ("#eval", "#guard", "run_cmd", "run_tac", "initialize", "builtin_initialize", "init", "macro", "macro_rules", "syntax",
                      "declare_syntax_cat", "elab", "elab_rules", "command_elab", "term_elab", "simproc", "dsimproc", "simproc_decl",
                      "builtin_simproc", "builtin_dsimproc", "extern", "implemented_by", "unsafe", "include_str", "ofReduceBool", "trustCompiler",
                      # fix_r2 (verifier finding): Lean core commands / monads that execute arbitrary MetaM/TermElabM code at elaboration time
                      "run_meta", "run_elab", "#exit", "MetaM", "TermElabM", "CommandElabM", "CoreM", "TacticM", "evalExpr", "evalTerm",
                      "unsafeIO", "unsafeCast", "ptrAddrUnsafe", "Lean.Elab", "Lean.Meta", "IO.Process", "IO.FS",
                      "notation3", "binder_predicate")     # fix_r4: both expand to syntax/macro_rules (+ a delaborator), like `syntax`/`macro`
# fix_r4: command FAMILIES a literal token list cannot enumerate (`notation3`, `notation_class`, `binder_predicate`, any future
# `*_predicate`): matched by identifier boundary, the matched text is reported as the found token
FORBIDDEN_FAMILY_RE = re.compile(r"(?<![\w'!?.«])(?:notation[\w'!?]*|[\w'!?]*_predicate|eval%)(?![\w'!?])")   # fix_r5: `eval% e` runs the interpreter at elaboration time
CHAR_LITERAL_RE = re.compile(r"'(?:\\[^\n]|[^'\\\n])'")      # 'x', '\n', '"', '\"' (a quote after an identifier is a primed name)
RAW_STRING_RE = re.compile(r'r(#*)"')                            # r"..." / r#"..."# : no escapes, closed by " + the same number of #
# The verdict-relevant content of task.json / evaluator.json (see task_contract / evaluator_contract): prose is excluded.
TASK_CONTRACT_KEYS = ("record_id", "submission_namespace", "hole_marker", "template_declaration", "allowed_imports", "reserved_names",
                      "forbidden_tokens_extra")
SET_OPTION_ALLOWED = re.compile(r"set_option\s+(maxHeartbeats|maxRecDepth|linter\.[A-Za-z0-9_.]+)\s")
MESSAGE_RE = re.compile(r"^(\S+?\.lean):(\d+):(\d+): (error|warning|info): (.*)$")
# Lean prints a primed name as 'NS.foo'' : the name group is lazy and the alternatives anchor the closing quote.
AXIOMS_RE = re.compile(r"^'(.+?)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$")
CANNOT_RE = re.compile(r"^\s*--\s*CANNOT:\s*(.*)$", re.MULTILINE)
DEFAULT_CACHE = os.path.join(os.environ.get("REPAIR_VALIDATE_CACHE") or os.path.join(tempfile.gettempdir(), "repair_validate_" + (os.environ.get("USER") or "user")),
                             "repair_validate_cache")
REPAIR_KEYS = ("imports", "namespace_structure", "forbidden_tokens", "reserved_names", "template_structure", "compile", "no_sorry",
               "axioms", "universal", "nonvacuity", "hidden_instance_agreement")
# fix_r3: column-0 lines that BEGIN a Lean command. Every other column-0 line (`+ 0 / (x - 2)`, `) |> fun _ => …`, `* 2`, `∧ …`,
# `|` alternatives, `termination_by`, `decreasing_by`) continues the previous command, exactly as Lean's term parser continues a body
# across a column-0 token that cannot start a command. These words are reserved tokens in a Mathlib-importing file, so none of them can
# be an identifier that continues a term. A column-0 command whose keyword is NOT listed is glued to the previous chunk, which is
# fail-closed (the enclosing template declaration then differs from the template; the reserved-name scan is not chunk-based).
COMMAND_KEYWORDS = ("import", "theorem", "lemma", "def", "noncomputable", "abbrev", "example", "instance", "structure", "inductive", "class",
                    "opaque", "axiom", "end", "namespace", "section", "open", "set_option", "variable", "universe", "private", "protected",
                    "partial", "unsafe", "nonrec", "scoped", "local", "mutual", "deriving", "attribute", "export", "notation", "infix",
                    "infixl", "infixr", "prefix", "postfix", "macro", "macro_rules", "syntax", "elab", "elab_rules", "declare_syntax_cat",
                    "simproc", "dsimproc", "simproc_decl", "builtin_simproc", "builtin_dsimproc", "initialize", "builtin_initialize",
                    "run_cmd", "run_meta", "run_elab", "run_tac", "omit", "include", "alias", "irreducible_def", "suppress_compilation",
                    "library_note", "assert_not_exists", "add_decl_doc", "register_simp_attr", "initialize_simps_projections", "unseal",
                    "seal", "compile_inductive", "binder_predicate", "notation3",
                    # fix_r5: further Lean core / Batteries / Mathlib commands (all refused by the command whitelist below)
                    "unif_hint", "recall", "assert_exists", "assert_not_imported", "init_quot", "register_label_attr", "register_option",
                    "declare_aesop_rule_sets", "add_aesop_rules", "erase_aesop_rules", "gen_injective_theorems", "elab_stx_quot", "print_prefix")
# fix_r5 (verifier round 5, B1): the ONLY commands a submission may contain, at ANY position (column 0, indented under another
# command, glued after `open … in` / `set_option … in`). Every other keyword of COMMAND_KEYWORDS (`alias`, `irreducible_def`, `variable`,
# `universe`, `mutual`, `deriving`, `unif_hint`, `omit`, `include`, `local`, `scoped`, `nonrec`, `partial`, …) and every `#…` command
# (`#check`, `#print`, `#reduce`, `#synth`, …) fails forbidden_tokens as a command not admitted, wherever it stands. `end` is admitted
# only as the closing `end NS` (namespace_structure), `open` only in its plain form (reserved_names), `set_option` only for the listed
# options (forbidden_tokens). Batteries `alias` and Mathlib `irreducible_def` declare constants in the current namespace and were
# invisible to every scan keyed on DECL_ANYWHERE_RE (round-5 B1); the whitelist makes the admissible command set explicit instead.
ADMITTED_COMMANDS = ("import", "namespace", "end", "open", "set_option", "def", "theorem", "lemma", "abbrev", "example", "noncomputable",
                     "private", "protected", "structure", "inductive", "class")
NON_ADMITTED_COMMANDS = tuple(k for k in COMMAND_KEYWORDS if k not in ADMITTED_COMMANDS)
_NA_ALT = "|".join(re.escape(k) for k in sorted(NON_ADMITTED_COMMANDS, key=len, reverse=True))
COMMAND_NOT_ADMITTED_RE = re.compile(r"(?<![\w'!?.«#])(?:(?:%s)(?![\w'!?»])|#[A-Za-z_][\w'!?]*)" % _NA_ALT)
END_ANYWHERE_RE = re.compile(r"(?<![\w'!?.«])end(?![\w'!?»])")
ATTR_ANYWHERE_RE = re.compile(r"@\[")
# fix_r5: the operation a forbidden operator symbol stands for, reachable by field notation on a binder head (`n.div 2` is `n / 2`)
FIELD_OPERATOR_NAMES = {"/": ("div", "ediv", "fdiv", "tdiv", "bdiv", "hdiv", "div'", "divInt", "floorDiv", "ceilDiv", "divFloor", "divCeil", "ediv'"),
                        "%": ("mod", "emod", "fmod", "tmod", "bmod", "hmod", "mod'", "modInt"), "⁻¹": ("inv",), "^": ("pow", "npow", "zpow", "rpow", "cpow"),
                        "∑": ("sum",), "∏": ("prod",), "-": ("sub", "neg"), "+": ("add",), "*": ("mul",), "∣": ("dvd",), "<": ("lt",), "≤": ("le",),
                        ">": ("gt",), "≥": ("ge",), "≠": ("ne",), "=": ("eq",), "∧": ("and",), "∨": ("or",), "¬": ("not",), "→": ("imp",), "↔": ("iff",)}
# fix_r5: hole_syntax keys that are prose (excluded from the evaluator_contract digest); every other key is contract
EVALUATOR_PROSE_KEYS = frozenset(("note", "notes", "description", "comment", "comments", "rationale", "errata", "decision", "grammar_decision", "title"))
_KW_ALT = "|".join(re.escape(k) for k in sorted(COMMAND_KEYWORDS, key=len, reverse=True))
COMMAND_START_RE = re.compile(r"^(?:@\[|#(?=[A-Za-z_])|--|/-|(?:%s)(?![\w'!?]))" % _KW_ALT)
# a command keyword (or `@[` / `#cmd`) INSIDE the extracted hole text: the text the grammar would judge is not one term
HOLE_COMMAND_RE = re.compile(r"(?<![\w'!?.«])(?:@\[|#(?=[A-Za-z_])|(?:%s)(?![\w'!?]))" % _KW_ALT)
# identifiers (dotted or bare, primes/!/? allowed, `_root_.` kept) of the template's fixed text and the obligation statements
IDENT_RE = re.compile(r"(?<![\w'!?.«])[^\W\d][\w'!?]*(?:\.[^\W\d][\w'!?]*)*")
IDENT_ONLY_RE = re.compile(r"[^\W\d][\w'!?]*")
# syntactic keywords picked up by IDENT_RE that can never be declared names (kept out of `reserved_effective` for readability)
LEAN_SYNTAX_WORDS = frozenset(("def", "theorem", "lemma", "abbrev", "instance", "structure", "inductive", "class", "opaque", "axiom", "example",
                               "noncomputable", "private", "protected", "partial", "unsafe", "namespace", "section", "end", "import", "open",
                               "export", "variable", "universe", "set_option", "fun", "by", "at", "with", "match", "if", "then", "else", "let",
                               "have", "show", "from", "do", "in", "where", "deriving", "Prop", "Type", "Sort", "calc"))
# every declaration command anywhere in the comment-stripped text (indented, glued or `set_option … in def …` on one line included);
# these words are reserved tokens, so outside a string literal each occurrence is a declaration (a literal hit fails closed)
# fix_r4: a declared name may carry «»-quoted components (`def «HasDerivAt»`, `def Real.«log»`); clean_name() removes the guillemets
DECL_NAME_PATTERN = r"((?:«[^»\n]*»|[^\s:({\[⦃«»])+)?"
# fix_r5: `alias` (Batteries; `alias NAME := target` and `alias ⟨A, B⟩ := target`), `irreducible_def` (Mathlib) and `example` are
# declaration commands too (round-5 B1: an alias of `Finset.range` in the record namespace was invisible to every scan)
DECL_ANYWHERE_RE = re.compile(r"(?<![\w'!?.«])(def|theorem|lemma|abbrev|instance|structure|inductive|class|opaque|axiom|irreducible_def|alias|example)(?![\w'!?»])"
                              r"[ \t]*" + DECL_NAME_PATTERN)
ALIAS_PAIR_RE = re.compile(r"(?<![\w'!?.«])alias(?![\w'!?»])\s*⟨([^⟩\n]*)⟩")
# fix_r4: commands admitted between `namespace NS` and the template's first fixed declaration
PRE_FIXED_ALLOWED_RE = re.compile(r"^(?:set_option|open)(?![\w'!?])")
# fix_r4: binder-introducing syntax inside a hole; the names it binds (before `:` / `∈` / `,` / `=>` / `|`) are local binders
HOLE_BINDER_KEYWORDS = ("∀", "∃!", "∃", "fun", "λ", "∑", "∏", "⨆", "⨅", "⋃", "⋂", "Π", "Σ")
HOLE_BINDER_STOP = (":", "∈", ",", "=>", "|", "↦", "⊆")
SCOPE_ANYWHERE_RE = re.compile(r"(?<![\w'!?.«])(open|export|namespace)(?![\w'!?])[ \t]*([^\n]*)")
HOLE_BINDING_NAME = "«validator hole binding»"
BINDER_CLOSE = {"(": ")", "{": "}", "[": "]", "⦃": "⦄"}


# ------------------------------------------------------------------------------------------------------------ text analysis

def _ident_char(ch):
    return ch.isalnum() or ch in "_'!?»"


def strip_comments(text):
    """Remove `-- ...` line comments and (nested) `/- ... -/` block comments, docstrings included, the way Lean's scanner sees them.
    String literals ("..." with backslash escapes, r"..."/r#"..."# raw strings), character literals ('x', '\\n', '"') and «...»
    identifiers are copied through untouched, so a `--` or `/-` inside one of them never hides the rest of the line or file from
    the text checks and the host-safety gate; a quote or `--` inside a comment is comment text. Newlines inside block comments
    are kept so line numbers stay stable. An unterminated literal runs to the end of the text (kept, never hidden)."""
    out, i, n, depth = [], 0, len(text), 0
    while i < n:
        ch = text[i]
        if depth > 0:
            if text.startswith("/-", i):
                depth += 1
                i += 2
            elif text.startswith("-/", i):
                depth -= 1
                i += 2
            else:
                if ch == "\n":
                    out.append("\n")
                i += 1
            continue
        if text.startswith("--", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if text.startswith("/-", i):
            depth = 1
            i += 2
            continue
        prev_ident = i > 0 and _ident_char(text[i - 1])
        if ch == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:min(j + 1, n)])
            i = j + 1
            continue
        if ch == "r" and not prev_ident:
            m = RAW_STRING_RE.match(text, i)
            if m:
                close = '"' + "#" * len(m.group(1))
                j = text.find(close, m.end())
                j = n if j < 0 else j + len(close)
                out.append(text[i:j])
                i = j
                continue
        if ch == "'" and not prev_ident:
            m = CHAR_LITERAL_RE.match(text, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
        if ch == "«":
            j = text.find("»", i)
            j = n if j < 0 else j + 1
            out.append(text[i:j])
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def chunks(text):
    """Top-level commands of a comment-free Lean file. A chunk starts at a column-0 line that BEGINS a Lean command (COMMAND_START_RE:
    a keyword of COMMAND_KEYWORDS, `@[…]`, `#cmd`). Every other line, indented or at column 0 (`+ 0 / (x - 2)`, `) |> fun _ => …`,
    `* 2`, `∧ …`, `|` alternatives, `termination_by`), continues the current chunk, the way Lean's term parser continues a body across a
    token that cannot start a command (fix_r3; before, every column-0 line not starting with `|` began a chunk, so a continuation line
    was silently dropped from the declaration the text checks judged while Lean elaborated it)."""
    rows, current, start_line = [], [], None
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip() == "":
            if current:
                current.append(line)
            continue
        if (not line[0].isspace() and COMMAND_START_RE.match(line)) or not current:
            if current:
                rows.append((start_line, "\n".join(current).strip()))
            current, start_line = [line], number
        else:
            current.append(line)
    if current:
        rows.append((start_line, "\n".join(current).strip()))
    return [(ln, body) for ln, body in rows if body]


def clean_name(name):
    """A declared name with «»-quoting removed (`«HasDerivAt»` -> `HasDerivAt`, `Real.«log»` -> `Real.log`); None stays None (fix_r4)."""
    return None if name is None else name.replace("«", "").replace("»", "")


def decl_of(chunk):
    m = re.match(r"^(?:@\[[^\]]*\]\s*)*(?:(?:noncomputable|private|protected|partial|unsafe|scoped|local)\s+)*"
                 r"(%s)\b\s*" % "|".join(DECL_KINDS) + DECL_NAME_PATTERN, chunk)
    if not m:
        return None
    return m.group(1), clean_name(m.group(2))


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def template_regex(template_chunk, hole):
    """Whitespace-insensitive regex of a template declaration with the hole as `(.+?)`. fix_r3: matched against the RAW comment-free
    submitted chunk (not its whitespace-normalised form), so the extracted hole keeps its line structure."""
    parts = [re.escape(normalize(p)) for p in template_chunk.split(hole)]
    pattern = r"(.+?)".join(p.replace(r"\ ", r"\s*") for p in parts)
    return re.compile(r"^\s*" + pattern + r"\s*$", re.DOTALL)


def reserved_identifiers(task, extra=()):
    """fix_r3: the effective reserved set: task.json reserved_names, every dotted or bare identifier of the template's fixed text
    (comment-stripped, hole removed, imports excluded) and of the obligation statements, and the record namespace with its components.
    Obligation names are excluded (they must be declared); syntactic keywords are dropped for readability.
    fix_r5: `extra` = evaluator.json hole_syntax.allowed_identifiers (library names the hole may use, e.g. `Finset.range`): reserved
    too, so no declaration (def, alias, …) in the record namespace can redirect an identifier the grammar admits."""
    ns, hole = task["submission_namespace"], task["hole_marker"]
    fixed = "\n".join(c for _, c in chunks(strip_comments(task["repair_template"])) if not c.startswith("import ")).replace(hole, " ")
    text = fixed + "\n" + "\n".join(ob.get("statement") or "" for ob in task.get("obligations") or [])
    names = set(IDENT_RE.findall(text)) | set(task.get("reserved_names") or []) | {ns} | set(ns.split(".")) | set(extra or [])
    names -= LEAN_SYNTAX_WORDS | {"_", "_root_"} | {ob["name"] for ob in task.get("obligations") or []}
    return names


def declarations_anywhere(stripped):
    """(line, kind, name) of every declaration command in the comment-stripped text, wherever it stands (chunk start, indented, glued
    to a previous chunk, or after `set_option … in` / `open … in` on the same line). name is None for anonymous instances."""
    out = []
    for m in DECL_ANYWHERE_RE.finditer(stripped):
        line, kind, name = stripped.count("\n", 0, m.start()) + 1, m.group(1), clean_name(m.group(2))
        if kind == "alias" and name and name.startswith("⟨"):                     # fix_r5: alias ⟨mp_name, mpr_name⟩ := iff_target
            pair = ALIAS_PAIR_RE.match(stripped, m.start())
            names = [clean_name(t.strip()) for t in (pair.group(1) if pair else name[1:]).split(",")] if pair else [name]
            out += [(line, kind, n or None) for n in names]
            continue
        if kind == "example":
            name = None
        out.append((line, kind, name))
    return out


def commands_not_admitted(stripped):
    """fix_r5: (line, token) of every command keyword outside ADMITTED_COMMANDS and every `#…` command in the comment-stripped text,
    at any position (identifier boundaries; string literals count, fail-closed)."""
    return [(stripped.count("\n", 0, m.start()) + 1, m.group(0)) for m in COMMAND_NOT_ADMITTED_RE.finditer(stripped)]


# ------------------------------------------------------------------------------------------ fix_r4: hole identifier rule

def _is_ident_start(ch):
    return ch.isalpha() or ch == "_"


def _is_ident_char(ch):
    return ch.isalnum() or ch in "_'!?"


def hole_tokens(hole_text):
    """Lexical tokens of a hole: ("ident", components) for a possibly dotted identifier (`«»`-quoted components unquoted; numeric
    projections `.1` are dropped), ("numeral", text) for a decimal literal, ("bad_numeral", text) for a literal glued to letters
    (`0x1`, `0b1`, `1e5`), ("keyword", text) for Lean syntax words (if/then/else/fun/…). Operators and brackets are skipped."""
    out, i, n = [], 0, len(hole_text)
    while i < n:
        ch = hole_text[i]
        if ch == "«" or _is_ident_start(ch):
            comps = []
            while True:
                if i < n and hole_text[i] == "«":
                    j = hole_text.find("»", i + 1)
                    j = n if j < 0 else j
                    comps.append(hole_text[i + 1:j]); i = j + 1
                elif i < n and _is_ident_start(hole_text[i]):
                    j = i
                    while j < n and _is_ident_char(hole_text[j]):
                        j += 1
                    comps.append(hole_text[i:j]); i = j
                else:
                    break
                if i < n and hole_text[i] == "." and i + 1 < n and (hole_text[i + 1] == "«" or _is_ident_start(hole_text[i + 1])):
                    i += 1
                    continue
                if i < n and hole_text[i] == "." and i + 1 < n and hole_text[i + 1].isdecimal():      # numeric projection q.1 / q.2
                    j = i + 1
                    while j < n and hole_text[j].isdecimal():
                        j += 1
                    i = j
                    if i < n and hole_text[i] == "." and i + 1 < n and (hole_text[i + 1] == "«" or _is_ident_start(hole_text[i + 1])):
                        i += 1
                        continue
                break
            if len(comps) == 1 and comps[0] in LEAN_SYNTAX_WORDS:
                out.append(("keyword", comps[0]))
            else:
                out.append(("ident", comps))
        elif ch.isdecimal():
            j = i
            while j < n and hole_text[j].isdecimal():
                j += 1
            if j + 1 < n and hole_text[j] == "." and hole_text[j + 1].isdecimal():
                j += 1
                while j < n and hole_text[j].isdecimal():
                    j += 1
            if j < n and _is_ident_char(hole_text[j]):
                k = j
                while k < n and _is_ident_char(hole_text[k]):
                    k += 1
                out.append(("bad_numeral", hole_text[i:k])); i = k
            else:
                out.append(("numeral", hole_text[i:j])); i = j
        else:
            i += 1
    return out


def binder_names(binders):
    """Every binder name of a Lean binder list, explicit, implicit, strict-implicit and named instance binders included
    (`{V : Type*} [inst : Foo V] (x y : V)` -> [V, inst, x, y]); bare names count too."""
    names, i, n = [], 0, len(binders)
    while i < n:
        ch = binders[i]
        if ch.isspace():
            i += 1
            continue
        if ch in BINDER_CLOSE:
            depth, j = 0, i
            while j < n:
                if binders[j] in BINDER_CLOSE:
                    depth += 1
                elif binders[j] in BINDER_CLOSE.values():
                    depth -= 1
                if depth == 0:
                    break
                j += 1
            inner = binders[i + 1:j]
            head = inner.split(":", 1)[0] if ":" in inner else ("" if ch == "[" else inner)
            names += [clean_name(t) for t in head.replace("«", " «").split() if t not in ("_",)]
            i = j + 1
        else:
            j = i
            while j < n and not binders[j].isspace():
                j += 1
            names.append(clean_name(binders[i:j])); i = j
    return [t for t in names if t and (t[0].isalpha() or t[0] == "_")]


def template_binders(task):
    """Binder names of the hole-bearing template declaration (its header between the declared name and `:=`)."""
    hole = task["hole_marker"]
    for _, tc in chunks(strip_comments(task["repair_template"])):
        if hole in tc and decl_of(tc):
            header = tc.split(":=", 1)[0]
            m = re.match(r"^(?:@\[[^\]]*\]\s*)*(?:(?:noncomputable|private|protected|partial)\s+)*(?:%s)\s+(?:%s)(.*)$" % ("|".join(DECL_KINDS), DECL_NAME_PATTERN[1:-2]), header, re.DOTALL)
            rest = m.group(1) if m else header
            depth, cut = 0, len(rest)
            for i, c in enumerate(rest):
                if c in BINDER_CLOSE:
                    depth += 1
                elif c in BINDER_CLOSE.values():
                    depth -= 1
                elif c == ":" and depth == 0:
                    cut = i
                    break
            return binder_names(rest[:cut])
    return []


def hole_local_binders(hole_text):
    """Names bound INSIDE the hole by ∀/∃/fun/λ/∑/… (the identifiers between the keyword and the first depth-0 `:` / `∈` / `,` / `=>` /
    `|`, bracket groups contributing the names before their `:`) and by set-builder `{x | …}`. Nothing after `:` / `∈` is ever added."""
    names = []
    for kw in HOLE_BINDER_KEYWORDS:
        pat = r"(?<![\w'!?.])%s(?![\w'!?])" % re.escape(kw) if kw.isalpha() else re.escape(kw)
        for m in re.finditer(pat, hole_text):
            rest = hole_text[m.end():]
            seg, depth = rest, 0
            for i, c in enumerate(rest):
                if c in BINDER_CLOSE:
                    depth += 1
                elif c in BINDER_CLOSE.values():
                    depth -= 1
                elif depth == 0 and any(rest.startswith(s, i) for s in HOLE_BINDER_STOP):
                    seg = rest[:i]
                    break
            names += binder_names(seg)
    for m in re.finditer(r"\{\s*((?:«[^»]*»|[^\W\d][\w'!?]*)(?:\s+(?:«[^»]*»|[^\W\d][\w'!?]*))*)\s*(?::[^|]*)?\|", hole_text):
        names += [clean_name(t) for t in m.group(1).split()]
    return sorted(set(names))


def declared_names(text):
    """Cleaned names of every declaration in a Lean text, bare and with each dotted suffix (`Foo.bar` -> {Foo.bar, bar})."""
    out = set()
    for _, _, name in declarations_anywhere(strip_comments(text)):
        if name:
            parts = name.split(".")
            out |= {".".join(parts[i:]) for i in range(len(parts))}
    return out


def field_notation_check(hole_text, tbinders, local, forbidden_tokens):
    """fix_r5 (round-5 minor): a field-notation token on a binder head (`n.div 2`, `p.find`, `G.edgeFinset.card`) reaches a library
    function the record's grammar may exclude by name or by operator symbol. Each field component is refused when it equals a forbidden
    token or the last component of a dotted forbidden token (`Nat.find` -> `find`), or names the operation behind a forbidden operator
    symbol (FIELD_OPERATOR_NAMES: `/` -> div/ediv/…, `%` -> mod/emod/…). Returns the list of problems."""
    forb = list(forbidden_tokens or [])
    by_name = {t.split(".")[-1]: t for t in forb if t and (t[0].isalpha() or t[0] == "_")}
    by_op = {n: sym for sym in forb if sym in FIELD_OPERATOR_NAMES for n in FIELD_OPERATOR_NAMES[sym]}
    heads = set(tbinders) | set(local)
    problems = []
    for kind, val in hole_tokens(hole_text):
        if kind != "ident" or len(val) < 2 or val[0] not in heads:
            continue
        for comp in val[1:]:
            if comp in by_name:
                problems.append("field notation reaches a forbidden name: %s (forbidden token `%s`)" % (".".join(val), by_name[comp]))
            elif comp in by_op:
                problems.append("field notation reaches a forbidden operation: %s (forbidden token `%s`)" % (".".join(val), by_op[comp]))
    return sorted(set(problems), key=problems.index)


def hole_identifier_check(task, defs_only_text, hole_text, submission_declared=(), allowed_identifiers=(), forbidden_tokens=()):
    """fix_r4 HOLE IDENTIFIER RULE. Returns (problems, info). An identifier token is permitted when it is a binder of the hole-bearing
    template declaration or a binder the hole introduces, a name declared in the template's fixed part or in defs_only.lean (bare, dotted
    suffix or namespace-qualified), an identifier of the fixed text / obligation statements (reserved since fix_r3, hence un-redeclarable),
    or listed in evaluator.json hole_syntax.allowed_identifiers. A dotted token whose head is a binder is field notation (`q.1`, `s.length`,
    `G.Connected`): Lean resolves the field through the head's TYPE namespace and never through the current namespace (probe 2026-09-23:
    `f.baz` with only `NS.Foo.baz` declared is "invalid field"), so it is admitted with its head. A dotted token with a non-binder head is
    resolved namespace-first by Lean (`Real.log` -> `NS.Real.log`), so it must be permitted as a whole. Every token that equals, or has a
    component equal to, a name declared in the SUBMISSION outside the template declarations is refused first. Hex/binary/octal/scientific
    literals are refused as malformed numerals."""
    ns = task["submission_namespace"]
    tbinders = template_binders(task)
    local = hole_local_binders(hole_text)
    tmpl_decls = {decl_of(c)[1] for _, c in chunks(strip_comments(task["repair_template"])) if decl_of(c) and decl_of(c)[1]}
    defs = declared_names(defs_only_text or "")
    reserved = reserved_identifiers(task)
    permitted = set(tbinders) | set(local) | tmpl_decls | defs | {ns + "." + d for d in defs} | reserved | set(allowed_identifiers or [])
    permitted |= {ns + "." + d for d in tmpl_decls}
    sub_declared = set(submission_declared or [])
    problems, tokens, refused = [], [], []
    for kind, val in hole_tokens(hole_text):
        if kind == "bad_numeral":
            problems.append("malformed numeral literal in hole: %s (hex/binary/octal/scientific literals are not numerals)" % val)
            tokens.append(val)
        elif kind == "ident":
            full = ".".join(val)
            tokens.append(full)
            suffixes = {".".join(val[i:]) for i in range(len(val))}
            if suffixes & sub_declared or set(val) & sub_declared:
                problems.append("identifier not permitted in hole: %s (declared in the submission)" % full); refused.append(full)
            elif full in permitted:
                continue
            elif len(val) > 1 and val[0] in set(tbinders) | set(local):
                continue                                              # field notation on a binder head
            else:
                problems.append("identifier not permitted in hole: %s" % full); refused.append(full)
    field_problems = field_notation_check(hole_text, tbinders, local, forbidden_tokens)          # fix_r5
    problems += [p for p in field_problems if p not in problems]
    info = {"tokens": tokens, "refused": refused, "template_binders": tbinders, "hole_local_binders": local,
            "allowed_identifiers": sorted(allowed_identifiers or []), "submission_declared_checked": sorted(sub_declared),
            "field_notation_refused": field_problems}
    return sorted(set(problems), key=problems.index), info


def scope_commands(stripped, ns):
    """fix_r3: `export`, a `namespace` other than the record namespace, and aliasing `open` forms (renaming / hiding / explicit list); plain `open X` is allowed."""
    out = []
    for m in SCOPE_ANYWHERE_RE.finditer(stripped):
        cmd, rest = m.group(1), m.group(2).strip()
        target = re.sub(r"\s+in$", "", rest).strip()
        if cmd in ("open", "namespace") and target == ns:
            continue
        # fix_r3 (narrowed, 2026-09-23): a plain `open X` / `open X in` of a library namespace is ordinary Lean (E07_B and the E08
        # reference use `open SimpleGraph`) and cannot redirect the qualified or root-elaborated obligation statements; only the
        # aliasing forms (`renaming`, `hiding`, an explicit `(…)` list), `export` and a foreign `namespace` are refused.
        if cmd == "open" and not re.search(r"\brenaming\b|\bhiding\b|\(", target):
            continue
        out.append({"command": cmd, "target": rest[:120], "line": stripped.count("\n", 0, m.start()) + 1})
    return out


def template_def_parts(template_chunk, hole):
    """(name, binders, return type, body) of a template declaration of the shape `[attrs] [modifiers] def NAME BINDERS : TYPE := BODY`
    whose BODY contains the hole; None for any other shape (pattern-matching bodies, `where`, no declared type, theorem holes)."""
    m = re.match(r"^(?:@\[[^\]]*\]\s*)*(?:(?:noncomputable|private|protected)\s+)*def\s+([^\s:({\[⦃]+)(.*?):=\s*(.*)$", template_chunk, re.DOTALL)
    if not m or hole not in m.group(3):
        return None
    name, header, body = m.group(1), m.group(2), m.group(3)
    depth, split = 0, None
    for i, ch in enumerate(header):
        if ch in BINDER_CLOSE:
            depth += 1
        elif ch in BINDER_CLOSE.values():
            depth -= 1
        elif ch == ":" and depth == 0:
            split = i
            break
    if split is None or depth != 0:
        return None
    binders, rtype = header[:split].strip(), header[split + 1:].strip()
    if not rtype or "|" in body.split(hole)[0].strip()[:1]:
        return None
    return name, normalize(binders), normalize(rtype), body


def explicit_binder_names(binders):
    """Names of the explicit binders of a binder list (`(x y : V)` -> ["x", "y"]); implicit `{}`, strict-implicit `⦃⦄` and instance `[]`
    binders are skipped (Lean supplies them at the application). None when the list has a shape this parser does not understand
    (default values, `_`, patterns), in which case the binding check is reported not applicable."""
    names, i, n = [], 0, len(binders)
    while i < n:
        ch = binders[i]
        if ch.isspace():
            i += 1
            continue
        if ch in BINDER_CLOSE:
            depth, j = 0, i
            while j < n:
                if binders[j] in BINDER_CLOSE:
                    depth += 1
                elif binders[j] in BINDER_CLOSE.values():
                    depth -= 1
                if depth == 0:
                    break
                j += 1
            if j >= n:
                return None
            inner = binders[i + 1:j]
            if ch == "(":
                if ":=" in inner:
                    return None
                toks = (inner.split(":", 1)[0] if ":" in inner else inner).split()
                if not toks or any(not IDENT_ONLY_RE.fullmatch(t) for t in toks):
                    return None
                names += toks
            i = j + 1
        else:
            j = i
            while j < n and not binders[j].isspace():
                j += 1
            tok = binders[i:j]
            if not IDENT_ONLY_RE.fullmatch(tok):
                return None
            names.append(tok)
            i = j
    return names


def hole_binding_statement(task, hole_text):
    """fix_r3: the Lean line of the binding check, placed inside `namespace NS` in CHECK.lean:
        theorem «validator hole binding» BINDERS : NAME ARGS = (BODY : TYPE) := rfl
    BODY is the template body with the hole replaced by the extracted hole text (whitespace collapsed to one line), TYPE the template's
    declared return type, ARGS the explicit binder names. It elaborates the extracted text in the declared type, inside the same
    namespace as the submission (so helper names resolve as in the submission), and requires it to be definitionally the submitted
    constant: the text the hole grammar judged is the term Lean elaborated. None when the template declaration is not of the shape
    `def NAME BINDERS : TYPE := …hole…` (reported as not applicable). It is not a grammar check: a continuation fill binds correctly
    once the hole is extracted whole; template_structure / hole_syntax reject it."""
    hole = task["hole_marker"]
    for _, tc in chunks(strip_comments(task["repair_template"])):
        if hole in tc and decl_of(tc):
            parts = template_def_parts(tc, hole)
            if not parts:
                return None
            name, binders, rtype, body = parts
            args = explicit_binder_names(binders)
            if args is None:
                return None
            filled = normalize(body.replace(hole, " " + hole_text + " "))
            return "theorem %s%s : %s = (%s : %s) := rfl" % (HOLE_BINDING_NAME, (" " + binders) if binders else "", " ".join([name] + args), filled, rtype)
    return None


def token_present(token, body):
    return re.search(r"(?<![A-Za-z0-9_.'])%s(?![A-Za-z0-9_'])" % re.escape(token), body) is not None


def host_unsafe_tokens(text):
    """Code-executing tokens present in `text` (identifier boundaries). The gate applies this to the WHOLE comment-stripped
    submission, imports region included (an indented command after `import` lands in the import chunk, not in the body)."""
    found = {t for t in HOST_UNSAFE_TOKENS if token_present(t, text)}
    found |= {m.group(0) for m in FORBIDDEN_FAMILY_RE.finditer(text)}      # fix_r4: notation3 / binder_predicate / any *_predicate
    return sorted(found)


def task_contract(task):
    """The verdict-relevant content of task.json with the prose removed: the fields the checks read, the obligations as
    (name, role, normalised statement) and the repair template as the validator compares it (comment-stripped, whitespace-normalised
    chunks). Its sha256 separates a wording edit (description, allowed_edit, docstrings, title) from a change of the contract."""
    fields = {k: task.get(k) for k in TASK_CONTRACT_KEYS}
    fields["obligations"] = [{"name": ob.get("name"), "role": ob.get("role"), "statement": normalize(ob.get("statement") or "")}
                             for ob in task.get("obligations") or []]
    fields["repair_template_chunks"] = [normalize(c) for _, c in chunks(strip_comments(task.get("repair_template") or ""))]
    return {"fields": fields, "sha256": rc.sha(json.dumps(fields, sort_keys=True, ensure_ascii=False, separators=(",", ":")))}


def evaluator_contract(evaluator_json):
    """The verdict-relevant content of evaluator.json: EVERY hole_syntax key except the prose keys (EVALUATOR_PROSE_KEYS: note, notes,
    description, errata, …), so regex, forbidden_tokens, max_lines AND allowed_identifiers (fix_r5; round-5 B2: the digest was
    byte-identical with and without allowed_identifiers, which flips verdicts) and any future grammar field enter the digest, plus
    has_final_theorem; None when the record has no evaluator.json. library_shortcut_names is informational (never flips a verdict)
    and stays out."""
    if evaluator_json is None:
        return None
    hs = evaluator_json.get("hole_syntax") or {}
    fields = {"hole_syntax": {k: hs[k] for k in sorted(hs) if k not in EVALUATOR_PROSE_KEYS},
              "has_final_theorem": evaluator_json.get("has_final_theorem", True), "contract_version": "fix_r5"}
    return {"fields": fields, "sha256": rc.sha(json.dumps(fields, sort_keys=True, ensure_ascii=False, separators=(",", ":")))}


def text_checks(task, submission_text, hole_max_lines=1, allowed_identifiers=()):
    """The text checks. hole_max_lines (fix_r3) is the number of lines the hole may occupy (evaluator.json hole_syntax.max_lines,
    default 1): a hole running onto more lines fails template_structure as a continuation beyond the template declaration.
    allowed_identifiers (fix_r5) = evaluator.json hole_syntax.allowed_identifiers, reserved names for the redeclaration scan."""
    ns, hole = task["submission_namespace"], task["hole_marker"]
    stripped = strip_comments(submission_text)
    sub_chunks = chunks(stripped)
    imports = [c.split(None, 1)[1].strip() for _, c in sub_chunks if c.startswith("import ")]
    non_import = [(ln, c) for ln, c in sub_chunks if not c.startswith("import ")]
    result = {}
    result["imports"] = {"pass": sorted(imports) == sorted(task["allowed_imports"]), "found": imports, "allowed": task["allowed_imports"]}
    ns_ok = bool(non_import) and normalize(non_import[0][1]) == "namespace " + ns and normalize(non_import[-1][1]) == "end " + ns
    others = [c for _, c in non_import[1:-1] if re.match(r"^(namespace|section|end)\b", c)]
    # fix_r5: every `end` other than the closing `end NS` chunk (indented / glued `end` closes the namespace early or a `mutual` block)
    closing_line = non_import[-1][0] if non_import else None
    stray_ends = [stripped.count("\n", 0, m.start()) + 1 for m in END_ANYWHERE_RE.finditer(stripped)]
    stray_ends = [ln for ln in stray_ends if ln != closing_line]
    result["namespace_structure"] = {"pass": ns_ok and not others and not stray_ends, "namespace": ns, "first": non_import[0][1][:80] if non_import else None,
                                     "last": non_import[-1][1][:80] if non_import else None, "nested_scope_commands": others, "stray_end_lines": stray_ends}
    body = "\n".join(c for _, c in non_import)
    tokens = sorted({t for t in FORBIDDEN_TOKENS if token_present(t, body)}
                    | set(task.get("forbidden_tokens_extra", [])) & {t for t in task.get("forbidden_tokens_extra", []) if t in body}
                    | {m.group(0) for m in FORBIDDEN_FAMILY_RE.finditer(body)})        # fix_r4: notation3, binder_predicate, *_predicate
    bad_set_options = [m.group(0) for m in re.finditer(r"set_option\s+\S+\s", body) if not SET_OPTION_ALLOWED.match(m.group(0))]
    # host-safety gate: the WHOLE comment-stripped text (not only the non-import body); the raw text is scanned for information only
    host_unsafe = host_unsafe_tokens(stripped)
    # fix_r5: command whitelist over the WHOLE comment-stripped text, at any position (indented / glued commands included)
    not_admitted = commands_not_admitted(stripped)
    tokens = sorted(set(tokens) | set(host_unsafe) | {t for _, t in not_admitted})
    result["forbidden_tokens"] = {"pass": not tokens and not bad_set_options, "found": tokens, "set_option_not_allowed": bad_set_options,
                                  "host_unsafe": host_unsafe, "host_unsafe_in_raw_text": host_unsafe_tokens(submission_text),
                                  "commands_not_admitted": [{"line": ln, "token": t} for ln, t in not_admitted],
                                  "admitted_commands": list(ADMITTED_COMMANDS)}
    decls = [(ln, decl_of(c), c) for ln, c in non_import if decl_of(c)]
    tmpl_chunks = [(ln, c) for ln, c in chunks(strip_comments(task["repair_template"])) if not c.startswith("import ")
                   and not re.match(r"^(namespace|end)\b", c)]
    # reserved names (fix_r3): every declaration anywhere in the text, against the effective reserved set; qualified redefinitions
    # (`def Real.log`, `def NS.HasDecDigits`, `def _root_.x`) and non-record `open`/`export`/`namespace` are rejected
    reserved = reserved_identifiers(task, allowed_identifiers)
    reserved_last = {r.split(".")[-1] for r in reserved}
    template_decls = {decl_of(c) for _, c in tmpl_chunks if decl_of(c)}
    obligation_names = {ob["name"] for ob in task["obligations"]}
    redefinitions = []
    for line_no, kind, name in declarations_anywhere(stripped):
        if not name or (kind, name) in template_decls or name in obligation_names:
            continue
        last = name.split(".")[-1]
        why = []
        if name in reserved:
            why.append("equals the reserved identifier `%s`" % name)
        elif last in reserved_last:
            why.append("its last component `%s` is the last component of reserved identifier(s) %s" % (last, sorted(r for r in reserved if r.split(".")[-1] == last)[:6]))
        if name.startswith("_root_."):
            why.append("declares outside the record namespace (`_root_.`)")
        if why:
            redefinitions.append({"kind": kind, "name": name, "line": line_no, "reason": "; ".join(why)})
    scope = scope_commands(stripped, ns)
    submission_declared = sorted({n for _, k, n in declarations_anywhere(stripped) if n and (k, n) not in template_decls and n not in obligation_names})
    result["reserved_names"] = {"pass": not redefinitions and not scope, "found": [r["name"] for r in redefinitions],
                                "reserved": task.get("reserved_names", []), "redefinitions": redefinitions, "scope_commands": scope,
                                "reserved_effective": sorted(reserved), "submission_declared": submission_declared,
                                "rule": "a declaration (def/theorem/lemma/abbrev/instance/structure/inductive/class/opaque/axiom/irreducible_def/alias) "
                                        "is rejected when its name equals a reserved identifier, or its last component equals the "
                                        "last component of one, or it is `_root_.`-qualified; reserved = task.json reserved_names + every identifier "
                                        "of the template's fixed text and the obligation statements + the record namespace + evaluator.json "
                                        "hole_syntax.allowed_identifiers; template declarations and obligation names are exempt; `export`, "
                                        "`namespace` other than the record namespace and aliasing `open` forms are rejected"}
    # template structure
    by_name = {}
    for _, (kind, name), c in decls:
        by_name.setdefault((kind, name), []).append(c)
    per_decl, all_ok, hole_text = [], True, None
    for _, tc in tmpl_chunks:
        d = decl_of(tc)
        if not d:
            continue
        found = by_name.get(d, [])
        row = {"declaration": d[1], "kind": d[0], "found": len(found), "pass": False}
        if len(found) != 1:
            row["detail"] = "declaration missing" if not found else "declared more than once"
        elif hole in tc:
            m = template_regex(tc, hole).match(found[0])
            if not m:
                row["detail"] = "does not match the template with the hole"
                row["template"], row["submitted"] = normalize(tc), normalize(found[0])
            else:
                # fix_r3: the hole is the ENTIRE remainder between the fixed prefix and suffix, line structure kept; anything that makes
                # it more than the grammar's line budget, or a command keyword inside it, is a continuation beyond the template declaration
                hole_text = m.group(1).strip()
                row["hole_filled_with"] = hole_text
                row["hole_lines"] = hole_text.count("\n") + 1
                cmd = HOLE_COMMAND_RE.search(hole_text)
                if row["hole_lines"] > hole_max_lines or cmd:
                    row["detail"] = "continuation beyond the template declaration"
                    row["continuation"] = ("the hole text runs onto %d lines (allowed %d)" % (row["hole_lines"], hole_max_lines)
                                           if row["hole_lines"] > hole_max_lines else "command keyword `%s` inside the hole text" % cmd.group(0))
                    row["template"], row["submitted"] = normalize(tc), found[0]
                else:
                    row["pass"] = True
        else:
            row["pass"] = normalize(found[0]) == normalize(tc)
            if not row["pass"]:
                row["detail"], row["template"], row["submitted"] = "fixed declaration differs from the template", normalize(tc), normalize(found[0])
        all_ok = all_ok and row["pass"]
        per_decl.append(row)
    # fix_r4 DECLARATION ORDER: nothing but set_option / open may stand between `namespace NS` and the template's first fixed
    # declaration, and nothing foreign between the fixed declarations (the template promises helpers between the fixed part and the
    # obligations; a helper placed before the fixed part can name what the hole then calls, verifier r4 X1-X4 / Q1)
    # fix_r5: EVERY chunk between fixed declarations (open, set_option, #…, variable, attributes, …) is foreign, not only declarations;
    # every command keyword the whitelist refuses, and every `@[…]` attribute, standing before or inside the fixed part is reported here
    # too (an indented / glued line is invisible to chunks() but not to these whole-text scans)
    before, inside = [], []
    fixed_lines = [ln for ln, (kind, name), c in decls if (kind, name) in template_decls]
    if fixed_lines and non_import:
        ns_line, first_fixed, last_fixed = non_import[0][0], min(fixed_lines), max(fixed_lines)
        seen = set()                                     # one row per line: the chunk's first line, else the declaration / command / attribute found there

        def add(row_list, ln, text):
            if ln not in seen:
                seen.add(ln)
                row_list.append({"line": ln, "text": text})
        for ln, c in non_import:
            if ns_line < ln < first_fixed and not PRE_FIXED_ALLOWED_RE.match(c):
                add(before, ln, c.splitlines()[0][:100])
            elif first_fixed < ln < last_fixed and ln not in fixed_lines:
                add(inside, ln, c.splitlines()[0][:100])
        for ln, kind, name in declarations_anywhere(stripped):
            if ns_line < ln < first_fixed:
                add(before, ln, "%s %s" % (kind, name or ""))
            elif first_fixed < ln < last_fixed and (kind, name) not in template_decls:
                add(inside, ln, "%s %s" % (kind, name or ""))
        for ln, tok in commands_not_admitted(stripped):
            if ns_line < ln < first_fixed:
                add(before, ln, "command %s" % tok)
            elif first_fixed < ln < last_fixed:
                add(inside, ln, "command %s" % tok)
        for m in ATTR_ANYWHERE_RE.finditer(stripped):
            ln = stripped.count("\n", 0, m.start()) + 1
            if ns_line < ln < first_fixed:
                add(before, ln, "attribute @[…]")
            elif first_fixed < ln <= last_fixed and ln not in fixed_lines:
                add(inside, ln, "attribute @[…]")
        for row_list, detail in ((before, "declaration before the fixed part"), (inside, "declaration inside the fixed part")):
            for b in sorted(row_list, key=lambda r: r["line"]):
                per_decl.append({"declaration": b["text"], "kind": "misplaced", "line": b["line"], "pass": False, "detail": detail})
                all_ok = False
    result["template_structure"] = {"pass": all_ok and bool(per_decl), "declarations": per_decl, "hole_filled_with": hole_text,
                                    "template_declaration": task["template_declaration"], "before_fixed_part": before, "inside_fixed_part": inside}
    # obligations declared
    theorem_names = [name for _, (kind, name), _ in decls if kind in ("theorem", "lemma") and name]
    cannot = CANNOT_RE.search(submission_text)
    ob_rows, all_declared = [], True
    for ob in task["obligations"]:
        declared = ob["name"] in theorem_names
        row = {"name": ob["name"], "role": ob["role"], "declared": declared}
        if not declared and ob["role"] == "final" and cannot:
            row["cannot"] = True
            row["cannot_reason"] = cannot.group(1).strip()[:300]
        elif not declared:
            all_declared = False
        ob_rows.append(row)
    result["obligations_declared"] = {"pass": all_declared, "obligations": ob_rows,
                                      "final_declared_cannot": any(r.get("cannot") for r in ob_rows)}
    return result, theorem_names, [r for r in ob_rows if r["declared"]]


# ------------------------------------------------------------------------------------------------------ hole grammar (evaluator)

def hole_grammar_file(record_id, evaluator_dir=None, explicit=None):
    """evaluator.json of the record: an explicit path, else <evaluator_dir>/evaluator.json, else evaluator_records/<record>/evaluator.json."""
    candidates = [Path(explicit)] if explicit else [Path(evaluator_dir or rc.EVALUATOR / record_id) / "evaluator.json",
                                                   rc.TRACK / "evaluator_records" / record_id / "evaluator.json"]
    for c in candidates:
        if c.is_file():
            return c
    return None


def hole_grammar_check(hole, rules):
    """Port of evaluator_records/check_record.sh: regex full match, forbidden tokens (`/`, `%`, `∑` by substring, `if` by word
    boundary, every other token by identifier boundary), max_lines. `hole` None means the template check extracted nothing."""
    problems = []
    if hole is None:
        problems.append("hole_not_extracted")
    else:
        if rules.get("regex") and not re.fullmatch(rules["regex"], hole.strip(), re.S):
            problems.append("hole_regex_mismatch")
        for tok in rules.get("forbidden_tokens", []):
            if tok in ("/", "%", "∑", "if"):
                hit = re.search(r"\bif\b", hole) if tok == "if" else (tok in hole)
            else:
                hit = re.search(r"(?<![A-Za-z0-9_'.])" + re.escape(tok) + r"(?![A-Za-z0-9_'])", hole)
            if hit:
                problems.append("hole_forbidden_token:" + tok)
        if hole.count("\n") + 1 > rules.get("max_lines", 1):
            problems.append("hole_too_many_lines")
    return {"pass": not problems, "problems": problems, "rule": rules}


def library_shortcuts(evaluator_json, submission_text):
    return sorted({n for n in evaluator_json.get("library_shortcut_names", [])
                   if re.search(r"(?<![A-Za-z0-9_'.])" + re.escape(n.split(".")[-1]) + r"(?![A-Za-z0-9_'])", submission_text)})


def overall_verdict(checks, final_applicable, hole):
    """repair_valid / endpoint_proved / all_pass / failed_checks. endpoint_final counts only when a final obligation applies;
    hole_syntax counts only when a grammar file exists (hole["pass"] is None otherwise); hole_binding (fix_r3) counts, inside
    repair_valid, only when it was emitted (pass None = not applicable)."""
    binding = checks.get("hole_binding") or {"pass": None}
    repair_valid = all(checks[k]["pass"] is True for k in REPAIR_KEYS) and binding["pass"] is not False
    endpoint = (checks["endpoint_final"]["pass"] is True) if final_applicable else None
    hole_ok = hole["pass"] in (True, None)
    all_pass = bool(repair_valid and endpoint is not False and hole_ok and checks["obligations_declared"]["pass"] is True)
    failed = [k for k in REPAIR_KEYS if checks[k]["pass"] is not True]
    if binding["pass"] is False:
        failed.append("hole_binding")
    if final_applicable and not endpoint:
        failed.append("endpoint_final")
    if checks["obligations_declared"]["pass"] is not True:
        failed.append("obligations_declared")
    if hole["pass"] is False:
        failed.append("hole_syntax")
    return {"repair_valid": repair_valid, "endpoint_proved": endpoint, "all_pass": all_pass, "failed_checks": failed,
            "endpoint_final_not_applicable": not final_applicable, "hole_syntax_not_applicable": hole["pass"] is None,
            "hole_binding_not_applicable": binding["pass"] is None}


# ------------------------------------------------------------------------------------------------------------- Lean phase

def parse_messages(output):
    rows, current = [], None
    for line in output.splitlines():
        m = MESSAGE_RE.match(line)
        if m:
            current = {"file": m.group(1), "line": int(m.group(2)), "col": int(m.group(3)), "severity": m.group(4), "text": m.group(5)}
            rows.append(current)
        elif current is not None and line.strip() and not AXIOMS_RE.match(line.strip()):
            current["text"] += "\n" + line
    return rows


def parse_axioms(output):
    found = {}
    for line in output.splitlines():
        m = AXIOMS_RE.match(line.strip())
        if m:
            found[m.group(1)] = sorted(a.strip() for a in (m.group(2) or "").split(",") if a.strip())
    return found


def lean_environment():
    """The pinned environment: skeleton hashes, toolchain file, Mathlib revision (and every package revision) from lake-manifest.json."""
    fp = rc.lean_env_fingerprint()
    manifest = json.loads((rc.LEAN_ENV / "lake-manifest.json").read_text(encoding="utf-8"))
    packages = {p.get("name"): p.get("rev") for p in manifest.get("packages", []) if isinstance(p, dict)}
    mathlib = next((p for p in manifest.get("packages", []) if isinstance(p, dict) and p.get("name") == "mathlib"), {})
    return {"fingerprint_sha256": fp["fingerprint_sha256"], "common_project": fp["common_project"], "skeleton_sha256": {k: v["sha256"] for k, v in fp["skeleton"].items()},
            "skeleton_matches_common_project": fp["skeleton_matches_common_project"],
            "toolchain": (rc.LEAN_ENV / "lean-toolchain").read_text(encoding="utf-8").strip(),
            "mathlib_rev": mathlib.get("rev"), "mathlib_input_rev": mathlib.get("inputRev"), "package_revs": packages,
            "mathlib_olean": fp["mathlib_olean"]}


class Workspace:
    def __init__(self, root, cache_dir):
        self.root = Path(root).resolve()
        self.lib = self.root / ".lake/build/lib/lean"
        self.lib.mkdir(parents=True, exist_ok=True)
        common = rc.common_project()
        self.common_packages = (common / ".lake/packages").resolve()
        link = self.root / ".lake/packages"
        if not link.exists():
            link.symlink_to(common / ".lake/packages")
        for name in rc.SKELETON_FILES:
            shutil.copyfile(rc.LEAN_ENV / name, self.root / name)
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.env_key = rc.lean_env_fingerprint()["fingerprint_sha256"]
        self.runs = []
        self.home = os.path.expanduser("~")
        if not os.access(BWRAP, os.X_OK):
            raise RuntimeError("validator isolation requires %s (bubblewrap); refusing to run Lean on the host without it" % BWRAP)

    def wrapper(self):
        """bubblewrap around every Lean process: no network, tmpfs HOME with only ~/.elan, the workspace read-write, the common packages
        read-only at their own path (the workspace's .lake/packages symlink resolves there), environment cleared."""
        home = self.home
        return [BWRAP, "--die-with-parent", "--unshare-user", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-net",
                "--ro-bind", "/usr", "/usr", "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64", "--symlink", "usr/bin", "/bin",
                "--symlink", "usr/sbin", "/sbin", "--ro-bind", "/etc", "/etc", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                "--tmpfs", home, "--ro-bind", home + "/.elan", home + "/.elan",
                "--ro-bind", str(self.common_packages), str(self.common_packages), "--bind", str(self.root), str(self.root),
                "--chdir", str(self.root), "--", "/usr/bin/env", "-i", "HOME=" + home, "PATH=" + home + "/.elan/bin:/usr/bin:/bin",
                "LANG=C.UTF-8", "LC_ALL=C.UTF-8", "REPAIR_VALIDATOR_WORKER=1"]

    def run(self, argv, timeout=LEAN_TIMEOUT):
        full = self.wrapper() + list(argv)
        start = time.monotonic()
        try:
            proc = subprocess.run(full, cwd=str(self.root), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, timeout=timeout)
            output, code = proc.stdout, proc.returncode
        except subprocess.TimeoutExpired as exc:
            output, code = (exc.stdout or "") + "\nvalidator: lean timed out after %d s" % timeout, -9
        return {"argv": list(argv), "full_argv": full, "cwd": str(self.root), "exit_code": code,
                "elapsed_seconds": round(time.monotonic() - start, 1), "output": output}

    def lean_version(self):
        res = self.run(["lean", "--version"], timeout=120)
        return {"output": res["output"].strip()[:300], "exit_code": res["exit_code"], "argv": res["argv"], "cwd": res["cwd"]}

    def lean(self, file_name, olean=None):
        argv = ["lake", "env", "lean"] + (["-o", str(self.lib / olean)] if olean else []) + [file_name]
        res = self.run(argv)
        output = res["output"]
        messages = parse_messages(output)
        row = {"file": file_name, "argv": argv, "full_argv": res["full_argv"], "cwd": res["cwd"], "isolation": "bubblewrap",
               "exit_code": res["exit_code"], "elapsed_seconds": res["elapsed_seconds"],
               "errors": [m for m in messages if m["severity"] == "error"], "warnings": [m for m in messages if m["severity"] == "warning"],
               "axioms": parse_axioms(output), "output_tail": output[-6000:], "output_sha256": rc.sha(output)}
        row["ok"] = row["exit_code"] == 0 and not row["errors"]
        self.runs.append(row)
        return row

    def compile_cached(self, source_path, module, key_parts):
        """Compile module (source copied into the workspace) with an olean cache keyed on source bytes + environment."""
        data = Path(source_path).read_bytes()
        key = rc.sha(data + b"|" + self.env_key.encode() + b"|" + "|".join(key_parts).encode())
        cached = self.cache / (module + "_" + key + ".olean")
        shutil.copyfile(source_path, self.root / (module + ".lean"))
        if cached.exists():
            shutil.copyfile(cached, self.lib / (module + ".olean"))
            return {"file": module + ".lean", "cached": True, "cache_key": key, "ok": True, "errors": [], "warnings": []}
        row = self.lean(module + ".lean", module + ".olean")
        if row["ok"]:
            rc.atomic_copy(self.lib / (module + ".olean"), cached)      # temp file + rename: concurrent graders never read a partial olean
        row["cached"] = False
        row["cache_key"] = key
        return row


def build_check_file(task, theorem_names, declared, binding_statement=None):
    ns = task["submission_namespace"]
    lines, line_map = ["import SUBMISSION", "set_option linter.unusedVariables false", ""], {}
    for ob in task["obligations"]:
        if ob["name"] in {d["name"] for d in declared}:
            stmt = " ".join(ob["statement"].split())
            lines.append("theorem ob_%s : %s := %s.%s" % (ob["name"], stmt, ns, ob["name"]))
            line_map[len(lines)] = ("obligation", ob["name"])
    if binding_statement:
        lines += ["", "namespace " + ns, binding_statement]
        line_map[len(lines)] = ("hole_binding", task["template_declaration"])
        lines.append("end " + ns)
    lines.append("")
    for name in theorem_names:
        lines.append("#print axioms %s.%s" % (ns, name))
        line_map[len(lines)] = ("axioms", name)
    for ob in task["obligations"]:
        if ob["name"] in {d["name"] for d in declared}:
            lines.append("#print axioms ob_%s" % ob["name"])
            line_map[len(lines)] = ("axioms_ob", ob["name"])
    return "\n".join(lines) + "\n", line_map


def pinned_inputs(packet, evaluator_dir, submission_path, submission_bytes, grammar_path):
    """sha256 of every input the verdict depends on (None where the file does not exist)."""
    pd = packet["dir"]
    ev = Path(evaluator_dir)
    files = {"task.json": pd / "task.json", "defs_only.lean": pd / "defs_only.lean", "witness_min.lean": pd / "witness_min.lean",
             "source_context": pd / packet["task"].get("source_context_file", "source_context.txt"), "contract.json": pd / "contract.json",
             "reference.lean": ev / "reference.lean", "AGREE.lean": ev / "AGREE.lean", "instances.json": ev / "instances.json",
             "evaluator.json": grammar_path}
    out = {name: {"path": str(p) if p else None, "sha256": rc.file_sha(p) if p and Path(p).is_file() else None} for name, p in files.items()}
    out["submission"] = {"path": str(submission_path), "sha256": rc.sha(submission_bytes), "bytes": len(submission_bytes)}
    return out


def validate(record_id, submission_path, workspace_dir, cache_dir, packet_dir=None, evaluator_dir=None, hole_grammar_path=None, argv=None):
    started = rc.now()
    packet = rc.load_packet(record_id, packet_dir)
    task = packet["task"]
    ns = task["submission_namespace"]
    ev = Path(evaluator_dir) if evaluator_dir else rc.EVALUATOR / record_id
    grammar_path = hole_grammar_file(record_id, ev, hole_grammar_path)
    evaluator_json = json.loads(grammar_path.read_text(encoding="utf-8")) if grammar_path else None
    submission_bytes = Path(submission_path).read_bytes()
    submission_text = submission_bytes.decode("utf-8", errors="replace")
    hole_max_lines = ((evaluator_json or {}).get("hole_syntax") or {}).get("max_lines") or 1
    checks, theorem_names, declared = text_checks(task, submission_text, hole_max_lines,
                                                  ((evaluator_json or {}).get("hole_syntax") or {}).get("allowed_identifiers") or [])
    hole_text = checks["template_structure"].get("hole_filled_with")
    binding_statement = hole_binding_statement(task, hole_text) if hole_text is not None else None
    ws = Workspace(workspace_dir, cache_dir)
    lean_version = ws.lean_version()
    host_unsafe = checks["forbidden_tokens"]["host_unsafe"]
    gate_blocked = bool(host_unsafe)
    if gate_blocked:
        comp = {"ok": False, "exit_code": None, "errors": [], "warnings": [], "elapsed_seconds": 0.0}
        checks["compile"] = {"pass": False, "exit_code": None, "errors": [], "warnings": [], "elapsed_seconds": 0.0,
                             "detail": "not compiled: host-safety gate (code-executing tokens present)", "host_unsafe_tokens": host_unsafe}
        checks["no_sorry"] = {"pass": False, "sorry_warnings": [], "detail": "not compiled: host-safety gate"}
    else:
        ws.compile_cached(packet["dir"] / "defs_only.lean", "defs_only", ["defs_only"])
        (ws.root / "SUBMISSION.lean").write_bytes(submission_bytes)
        comp = ws.lean("SUBMISSION.lean", "SUBMISSION.olean")
        sorry_msgs = [m for m in comp["warnings"] if "sorry" in m["text"]]
        checks["compile"] = {"pass": comp["ok"], "exit_code": comp["exit_code"], "errors": comp["errors"], "warnings": comp["warnings"],
                             "elapsed_seconds": comp["elapsed_seconds"], "cwd": comp["cwd"], "argv": comp["argv"]}
        checks["no_sorry"] = {"pass": comp["ok"] and not sorry_msgs, "sorry_warnings": sorry_msgs}
    role_checks = {"universal": None, "nonvacuity": None, "final": None}
    axioms_check = {"pass": False, "detail": "submission did not compile" if not gate_blocked else "not compiled: host-safety gate"}
    if hole_text is None:
        binding_check = {"pass": None, "not_applicable": True, "detail": "no hole extracted (see template_structure)"}
    elif binding_statement is None:
        binding_check = {"pass": None, "not_applicable": True, "detail": "template declaration is not of the shape `def NAME BINDERS : TYPE := …hole…`; generic binding check not emitted"}
    else:
        binding_check = {"pass": False, "statement": binding_statement, "detail": "submission did not compile" if not gate_blocked else "not compiled: host-safety gate"}
    if comp["ok"]:
        text, line_map = build_check_file(task, theorem_names, declared, binding_statement)
        (ws.root / "CHECK.lean").write_text(text, encoding="utf-8")
        chk = ws.lean("CHECK.lean")
        errors_by_target = {}
        for err in chk["errors"]:
            target = line_map.get(err["line"], ("file", None))
            errors_by_target.setdefault(target, []).append(err)
        axioms = chk["axioms"]
        bad, missing = {}, []
        for name in theorem_names:
            full = "%s.%s" % (ns, name)
            if full not in axioms:
                missing.append(full)
            elif not set(axioms[full]) <= set(rc.ALLOWED_AXIOMS):
                bad[full] = axioms[full]
        axioms_check = {"pass": not bad and not missing and bool(theorem_names),
                        "allowed": list(rc.ALLOWED_AXIOMS), "per_theorem": {k: v for k, v in axioms.items() if k.startswith(ns + ".")},
                        "disallowed": bad, "not_reported": missing, "check_file_errors_unattributed": errors_by_target.get(("file", None), [])}
        for ob in task["obligations"]:
            name, role = ob["name"], ob["role"]
            row = {"name": name, "statement": ob["statement"], "declared": name in {d["name"] for d in declared}}
            if not row["declared"]:
                cannot = next((d for d in checks["obligations_declared"]["obligations"] if d["name"] == name and d.get("cannot")), None)
                row.update(pass_=False, detail="declared CANNOT: " + cannot["cannot_reason"] if cannot else "not declared")
            else:
                errs = errors_by_target.get(("obligation", name), [])
                ax = axioms.get("ob_" + name)
                ax_ok = ax is not None and set(ax) <= set(rc.ALLOWED_AXIOMS)
                row.update(pass_=not errs and ax_ok, type_errors=errs, axioms=ax,
                           detail="type of the submitted theorem matches the declared statement" if not errs else "the submitted theorem does not have the declared type")
                if not ax_ok and not errs:
                    row["detail"] = "axioms outside the allowed set (or #print axioms failed): %s" % ax
            row["pass"] = row.pop("pass_")
            key = {"universal": "universal", "nonvacuity": "nonvacuity", "final": "final"}.get(role)
            if key:
                role_checks[key] = row
        checks["check_file"] = {"exit_code": chk["exit_code"], "elapsed_seconds": chk["elapsed_seconds"], "errors": chk["errors"],
                                "source_sha256": rc.sha(text), "cwd": chk["cwd"], "argv": chk["argv"]}
        if binding_statement is not None:
            b_errs = errors_by_target.get(("hole_binding", task["template_declaration"]), [])
            binding_check = {"pass": not b_errs, "statement": binding_statement, "errors": b_errs,
                             "detail": "the extracted hole text elaborates (in the declared type, inside the record namespace) to the submitted constant by rfl"
                                       if not b_errs else "the extracted hole text is NOT definitionally the submitted constant (or does not elaborate): the text the grammar judged is not what Lean elaborated"}
    checks["axioms"] = axioms_check
    checks["hole_binding"] = binding_check
    checks["universal"] = role_checks["universal"] or {"pass": False, "detail": "no universal obligation evaluated"}
    checks["nonvacuity"] = role_checks["nonvacuity"] or {"pass": False, "detail": "no nonvacuity obligation evaluated"}
    final_in_task = any(ob.get("role") == "final" for ob in task["obligations"])
    final_applicable = final_in_task and (evaluator_json or {}).get("has_final_theorem", True) is not False
    if final_applicable:
        checks["endpoint_final"] = role_checks["final"] or {"pass": False, "detail": "no final obligation evaluated"}
    else:
        checks["endpoint_final"] = {"pass": None, "not_applicable": True,
                                    "detail": "no final obligation in task.json" if not final_in_task else "evaluator.json: has_final_theorem is false"}
    # hidden-instance agreement (evaluator-only files; never inside any sandbox)
    agree = {"pass": False, "evaluator_dir": str(ev)}
    if not (ev / "reference.lean").exists() or not (ev / "AGREE.lean").exists():
        agree["detail"] = "evaluator files missing (reference.lean, AGREE.lean): agreement cannot be established"
    elif not comp["ok"]:
        agree["detail"] = "submission did not compile" if not gate_blocked else "not compiled: host-safety gate"
    else:
        ref = ws.compile_cached(ev / "reference.lean", "reference", ["reference", rc.file_sha(packet["dir"] / "defs_only.lean")])
        if not ref["ok"]:
            agree["detail"] = "hidden reference failed to compile (evaluator defect)"
            agree["reference_errors"] = ref["errors"]
        else:
            shutil.copyfile(ev / "AGREE.lean", ws.root / "AGREE.lean")
            ag = ws.lean("AGREE.lean")
            ag_sorry = [m for m in ag["warnings"] if "sorry" in m["text"]]
            bad = {k: v for k, v in ag["axioms"].items() if not set(v) <= set(rc.ALLOWED_AXIOMS)}
            agree.update({"pass": ag["ok"] and not ag_sorry and not bad, "exit_code": ag["exit_code"], "errors": ag["errors"],
                          "sorry_warnings": ag_sorry, "axioms": ag["axioms"], "disallowed_axioms": bad, "elapsed_seconds": ag["elapsed_seconds"],
                          "instances": json.loads((ev / "instances.json").read_text()) if (ev / "instances.json").exists() else None,
                          "agree_file_sha256": rc.file_sha(ev / "AGREE.lean"), "reference_sha256": rc.file_sha(ev / "reference.lean")})
            if ag["errors"]:
                agree["detail"] = "at least one listed instance could not be shown to agree with the reference (fail-closed)"
    checks["hidden_instance_agreement"] = agree
    # hole grammar (folded in from check_record.sh)
    hole = checks["template_structure"].get("hole_filled_with")
    hs_rules = (evaluator_json or {}).get("hole_syntax") or {}
    ident_problems, ident_info = ([], None) if hole is None else hole_identifier_check(
        task, packet.get("defs_only") or "", hole, checks["reserved_names"].get("submission_declared", []), hs_rules.get("allowed_identifiers") or [],
        hs_rules.get("forbidden_tokens") or [])
    if evaluator_json is not None:
        hs = hole_grammar_check(hole, hs_rules)
        hs["problems"] = hs["problems"] + [p for p in ident_problems if p not in hs["problems"]]
        hs["pass"] = not hs["problems"]
        checks["hole_syntax"] = {**hs, "source": str(grammar_path), "identifiers": ident_info}
    elif ident_problems:
        checks["hole_syntax"] = {"pass": False, "problems": ident_problems, "rule": {}, "identifiers": ident_info,
                                 "detail": "no evaluator.json for this record (no hole grammar); the fix_r4 hole identifier rule applies alone"}
    else:
        checks["hole_syntax"] = {"pass": None, "not_applicable": True, "detail": "no evaluator.json for this record (no hole grammar); hole identifier rule satisfied",
                                 "problems": [], "identifiers": ident_info}
    overall = overall_verdict(checks, final_applicable, checks["hole_syntax"])
    finished = rc.now()
    verdict = {"record_id": record_id, "verdict": "PASS" if overall["all_pass"] else "FAIL",
               "submission_path": str(submission_path), "submission_sha256": rc.sha(submission_bytes),
               "submission_bytes": len(submission_bytes), "started_utc": started, "finished_utc": finished,
               "invocation": {"argv": list(argv if argv is not None else sys.argv), "cwd": os.getcwd(), "hostname": socket.gethostname(),
                              "pid": os.getpid(), "python": sys.executable, "python_version": sys.version.split()[0],
                              "validator_files_sha256": {"validate.py": rc.file_sha(rc.HERE / "validate.py"),
                                                         "repair_common.py": rc.file_sha(rc.HERE / "repair_common.py")},
                              "exit_code": 0 if overall["all_pass"] else 1, "started_utc": started, "finished_utc": finished},
               "pinned": {**pinned_inputs(packet, ev, submission_path, submission_bytes, grammar_path),
                          "task_contract": task_contract(task), "evaluator_contract": evaluator_contract(evaluator_json),
                          "lean_toolchain": (rc.LEAN_ENV / "lean-toolchain").read_text(encoding="utf-8").strip(),
                          "lean_toolchain_sha256": rc.file_sha(rc.LEAN_ENV / "lean-toolchain"), "lean_version": lean_version,
                          "mathlib_rev": lean_environment()["mathlib_rev"]},
               "packet_sha256": packet["sha256"],
               "environment": {**lean_environment(), "lean_version": lean_version, "isolation": "bubblewrap (no network, tmpfs HOME + ~/.elan, workspace + read-only common packages)"},
               "hole_filled_with": hole, "hole_syntax": checks["hole_syntax"],
               "library_shortcuts_used": library_shortcuts(evaluator_json, submission_text) if evaluator_json else None,
               "host_safety_gate": {"blocked": gate_blocked, "tokens": host_unsafe},
               "checks": checks, "final_declared_cannot": checks["obligations_declared"]["final_declared_cannot"],
               "overall": overall,
               "lean_runs": [{k: v for k, v in r.items() if k != "output_tail"} for r in ws.runs],
               "lean_outputs": {r["file"]: r["output_tail"] for r in ws.runs}, "workspace": str(ws.root)}
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--submission", required=True)
    ap.add_argument("--out")
    ap.add_argument("--workspace")
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE)
    ap.add_argument("--packet-dir")
    ap.add_argument("--evaluator-dir")
    ap.add_argument("--hole-grammar", help="evaluator.json carrying hole_syntax (default: <evaluator-dir>/evaluator.json, then evaluator_records/<record>/evaluator.json)")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    tmp = None
    workspace = a.workspace
    if not workspace:
        os.makedirs(os.path.dirname(DEFAULT_CACHE), exist_ok=True)
        tmp = tempfile.mkdtemp(prefix="repair_validate_", dir=os.path.dirname(DEFAULT_CACHE))
        workspace = tmp
    try:
        verdict = validate(a.record, a.submission, workspace, a.cache_dir, a.packet_dir, a.evaluator_dir, a.hole_grammar)
    finally:
        if tmp and not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)
    if a.out:
        rc.atomic_json(a.out, verdict)
    summary = {"record_id": verdict["record_id"], "verdict": verdict["verdict"], "submission_sha256": verdict["submission_sha256"],
               "overall": verdict["overall"],
               "checks": {k: v.get("pass") for k, v in verdict["checks"].items() if isinstance(v, dict) and "pass" in v},
               "hole_filled_with": verdict["hole_filled_with"], "hole_syntax": {k: verdict["hole_syntax"].get(k) for k in ("pass", "problems")},
               "final_declared_cannot": verdict["final_declared_cannot"], "host_safety_gate": verdict["host_safety_gate"],
               "pinned": {k: (v.get("sha256") if isinstance(v, dict) else v) for k, v in verdict["pinned"].items() if k != "lean_version"},
               "exit_code": verdict["invocation"]["exit_code"], "out": a.out}
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return verdict["invocation"]["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
