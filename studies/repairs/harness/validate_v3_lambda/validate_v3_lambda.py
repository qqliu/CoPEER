#!/usr/bin/env python3
"""validate_v3_lambda.py -- repair-study validator, version v3-lambda-E10-20260924.

  python3 validate_v3_lambda.py --record E10 --submission PATH [--out verdict.json] [--workspace DIR] [--cache-dir DIR] [--keep]
                                [--packet-dir DIR] [--evaluator-dir DIR] [--hole-grammar evaluator.json]
  (the flags of the pinned validator, unchanged)

WHAT THIS FILE IS. A WRAPPER around the pinned validator ../validate.py, sha256
    dc81a9869fa871324c3b0622ccf2ca1d004b28138b6e132448bae1bcfd30ae4c
(the wrapper refuses to run when the bytes of ../validate.py hash to anything else: exit 3, no verdict). It imports that file as a
module and calls its validate() UNCHANGED, so the imports / namespace / forbidden-token / reserved-name / template-structure /
declaration-order / anti-shadowing checks, the host-safety gate, the Lean phase (compile, no_sorry, axioms, universal, nonvacuity,
endpoint_final, hidden_instance_agreement, hole_binding), the pinned hole grammar (hole_grammar_check: regex, forbidden tokens, max_lines)
and the fix_r4/fix_r5 hole identifier rule (hole_identifier_check) execute as the very same code objects as under validate.py. Their
behaviour is therefore byte-identical by construction (test_validate_v3_lambda.py --lean-regression checks it empirically on saved
non-E10 submissions). The ONE change is a post-pass on checks["hole_syntax"], applied ONLY when --record is E10 and the record's grammar
forbids the token `fun`:

  APPROVED RULE (board TASK-999 reviewer rule, TASK-1000 reviewer approval, TASK-1002 reviewer confirmation; nothing broader is implemented).
  A lambda is permitted in the E10 hole ONLY as the summand of `Finset.sum` over an explicit `Finset.range <expr>`, i.e. the forms
      Finset.sum (Finset.range R) (fun k => BODY)          (also with the arrow spelled `↦`)
      ∑ k ∈ Finset.range R, BODY        ∑ k in Finset.range R, BODY
  where the binder is ONE bare identifier (any name: alpha-renaming is accepted; it may not shadow the template binders V / G, `ℕ`,
  a permitted identifier or a forbidden token, and `_` is not an identifier) and BODY is restricted to the task's permitted matrix
  expressions: the binder, `G.adjMatrix ℕ`, `Fintype.card V`, numerals (`1` included), the matrix operators `^` `+` `*`, parentheses,
  and the grammar's already-allowed identifiers (evaluator.json hole_syntax.allowed_identifiers) as bare atoms; inside an EXPONENT
  (the right operand of `^`) natural-index arithmetic is admitted: `+` `-` `*` `^`, numerals, the binder, `Fintype.card V`, parentheses
  (TASK-1021: the reverse-indexed power sum `(G.adjMatrix ℕ) ^ (Fintype.card V - 1 - k)` is a permitted matrix expression; the task's
  own criterion uses `Fintype.card V - 1`). Everything else in BODY is refused: `fun`/`λ`/`∑`, `Matrix.of`, `Reachable`, `Connected`,
  `Preconnected`, `Walk`, `if`, `match`, `criterion`, `sorry`, `Classical`, entrywise indexing (`A i j`: any application by
  juxtaposition other than `G.adjMatrix ℕ` / `Fintype.card V`), field access (`.entry`, `.1`), matrix subtraction (`-` outside an
  exponent) or any other operator, and any other identifier. See check_summand_body() for the exact grammar.
  The range expression R is not part of the exception: it stays under the pinned rules (identifier rule, forbidden tokens), and a `fun`
  inside it is a `fun` outside the approved position.

  EFFECT ON THE PINNED VERDICT. The pinned problem `hole_forbidden_token:fun` is removed from checks["hole_syntax"]["problems"] if and
  only if EVERY `fun` token of the extracted hole stands in the approved position with an admissible binder and BODY; a `fun` that is not
  (wrong position, several binders, BODY outside the grammar) keeps the pinned problem and ADDS `e10_summand_lambda:fun at char N: <why>`
  next to it, so the grader sees why the exception did not apply. No pinned problem other than `hole_forbidden_token:fun` is ever removed
  (a `λ` is still refused by the pinned identifier rule; identifiers outside the allowlist are still refused; the forbidden tokens other
  than `fun` are untouched), and NO new refusal is introduced: the `∑ k ∈/in Finset.range R, BODY` spellings contain no `fun`, the pinned
  grammar (which never banned `∑` for E10) already admits them, and they stay under the pinned rules unchanged. The analyser still reports
  every `∑` / `λ` site with the same shape/binder/BODY judgement, INFORMATIONALLY (site["approved"], site["problems"]), never as a problem
  (concretely: the saved Luna E10_B_attempt2 hole `∑ n : Fin (Fintype.card V), G.adjMatrix ℕ ^ (n : ℕ)` passes the pinned v2 grammar,
  because `Fin` is an identifier of the nonvacuity obligation statement and hence reserved/permitted; v3 leaves that verdict as it is and
  reports the site as not of the approved shape). checks["hole_syntax"]["pass"] and the overall verdict are recomputed with the pinned
  overall_verdict(); the pinned validator's hole_syntax pass/problems, overall and verdict BEFORE this post-pass are kept in the output
  under "pre_lambda_verdict" (top level; with the grammar file and its sha256, since that verdict is the pinned validator's verdict under
  whatever grammar file was passed: under check_record_v3.sh that is the identifier-only v2 grammar, NOT the v1 grammar) and
  checks["hole_syntax"]["pre_lambda"]. Records other than E10 get the pinned verdict with only the version fields added. Consequently
  v3 admits a superset of what the pinned validator admits under the same grammar: the only verdicts that can change are FAIL -> PASS for
  holes whose sole hole_syntax problem was the approved summand `fun`.

  OUTPUT ADDITIONS. verdict["validator_version"] = "v3-lambda-E10-20260924"; verdict["derived_from"] = {path, sha256 of validate.py};
  invocation.validator_files_sha256 gains "validate_v3_lambda.py"; verdict["pre_lambda_verdict"] = the pinned validator's verdict /
  overall / hole_syntax before the post-pass, with the grammar file used (path, sha256, version hint v1 / v2-identifiers);
  verdict["v3_lambda"] summarises whether the rule applied and whether the verdict differs from the pre-lambda one;
  checks["hole_syntax"]["e10_summand_lambda"] carries every lambda site found (kind, char span, binder, range expression, body, approved,
  problems, informational) and "fun_ban_lifted"; checks["hole_syntax"]["pre_lambda"] = the pre-lambda pass / problems.

WHY A WRAPPER AND NOT AN EDITED COPY. An edited copy of 1272 lines would have to be diffed to prove that nothing else moved; a wrapper
proves it structurally: the pinned checks are not re-implemented, re-ordered or re-typed, they are the pinned functions, and the
adjustment reads one dict of the finished verdict. The Lean phase, the workspace, the cache keys and the pinned-input hashes are the
pinned code's. The price is that the pinned validator first records `hole_forbidden_token:fun` and this pass removes it, which is why
the pre-lambda problems are preserved verbatim under "pre_lambda" / "pre_lambda_verdict".
"""
import argparse, hashlib, importlib.util, json, os, re, shutil, sys, tempfile

VALIDATOR_VERSION = "v3-lambda-E10-20260924"
RULE_RECORD = "E10"
APPROVAL = ["review protocol TASK-999 (reviewer: exact summand-lambda rule)", "review protocol TASK-1000 (reviewer: E10 exact exception accepted)",
            "review protocol TASK-1002 (reviewer: follow the approved bounded E10 extension)"]
HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
PINNED_PATH = os.path.join(HARNESS, "validate.py")
PINNED_SHA256 = "dc81a9869fa871324c3b0622ccf2ca1d004b28138b6e132448bae1bcfd30ae4c"
MATRIX_OPERATORS = ("+", "*")            # matrix level of the summand body: no subtraction, no other operator (`^` handled by matrix_pow)
NAT_OPERATORS = ("+", "-", "*")          # natural-index arithmetic admitted in exponent positions (TASK-1021), with `^`, numerals, binder, Fintype.card V
GRAPH_BINDER, TYPE_BINDER, NAT = "G", "V", "ℕ"          # the task's `G.adjMatrix ℕ` and `Fintype.card V` (E10 template binders V, G)
ADJ_MATRIX = GRAPH_BINDER + ".adjMatrix"
CARD = "Fintype.card"


def _file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_pinned():
    """Import ../validate.py as module `validate` after checking its bytes against PINNED_SHA256 (fail closed)."""
    actual = _file_sha(PINNED_PATH)
    if actual != PINNED_SHA256:
        sys.stderr.write("validate_v3_lambda: refusing to run: %s has sha256 %s, this wrapper is pinned to %s\n" % (PINNED_PATH, actual, PINNED_SHA256))
        sys.exit(3)
    spec = importlib.util.spec_from_file_location("validate", PINNED_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["validate"] = mod
    spec.loader.exec_module(mod)
    return mod


V = load_pinned()
rc = V.rc

# ------------------------------------------------------------------------------------------- E10 summand-lambda rule (text level)

# Tokens of the hole text: whitespace (dropped), the lambda arrow, decimal numerals, Lean identifiers (dotted, «»-quoted components,
# primes / ! / ? allowed; the same shape as validate.IDENT_RE), and every other single character as a symbol. `λ` is a Unicode letter and
# would lex as an identifier; Lean reserves it as the lambda keyword, so it is classified as a keyword here (never lifted: the pinned
# identifier rule refuses it as an identifier, and the approved forms are spelled `fun` / `∑`).
_TOKEN_RE = re.compile(r"(?P<ws>\s+)|(?P<arrow>=>|↦)|(?P<num>\d+(?:\.\d+)?)"
                       r"|(?P<ident>(?:«[^»\n]*»|[^\W\d][\w'!?]*)(?:\.(?:«[^»\n]*»|[^\W\d][\w'!?]*))*)|(?P<sym>.)", re.S)


def tokenize(text):
    """[(kind, text, start, end)] with kind in ident / kw / num / arrow / sym; whitespace dropped."""
    out = []
    for m in _TOKEN_RE.finditer(text):
        kind = m.lastgroup
        if kind == "ws":
            continue
        s = m.group(0)
        if kind == "ident" and (s in V.LEAN_SYNTAX_WORDS or s == "λ"):
            kind = "kw"
        out.append((kind, s, m.start(), m.end()))
    return out


def _is_sym(tok, s):
    return tok is not None and tok[0] == "sym" and tok[1] == s


def _match_parens(toks):
    """{open index: close index, close index: open index} for round parentheses; None when unbalanced."""
    match, stack = {}, []
    for i, t in enumerate(toks):
        if _is_sym(t, "("):
            stack.append(i)
        elif _is_sym(t, ")"):
            if not stack:
                return None
            j = stack.pop()
            match[j], match[i] = i, j
    return None if stack else match


def _enclosing_close(toks, match, i):
    """Index of the `)` closing the innermost `(` that encloses token i, else len(toks)."""
    stack = []
    for j in range(i):
        if _is_sym(toks[j], "("):
            stack.append(j)
        elif _is_sym(toks[j], ")") and stack:
            stack.pop()
    return match[stack[-1]] if stack else len(toks)


class _BodyError(Exception):
    pass


def check_binder(tok, template_binders, allowed_identifiers, forbidden_tokens):
    """None when tok is an admissible single bare binder, else the problem text."""
    if tok is None or tok[0] != "ident":
        return "the lambda must bind exactly one bare identifier (found `%s`)" % (tok[1] if tok else "nothing")
    name = tok[1]
    if "." in name or "«" in name:
        return "the binder must be a bare identifier (found `%s`)" % name
    if name == "_":
        return "`_` is not an identifier; the binder must be a named natural-number index"
    if name in template_binders or name == NAT or name in allowed_identifiers or name in forbidden_tokens:
        return "binder `%s` shadows a template binder, `ℕ`, a permitted identifier or a forbidden token" % name
    return None


def check_summand_body(body_toks, binder, allowed_identifiers):
    """The restricted BODY grammar (recursive descent, two sorts). Returns [] when BODY is admissible, else the problems.
        matrix_expr := matrix_pow (('+' | '*') matrix_pow)*
        matrix_pow  := matrix_atom ('^' nat_pow)?
        matrix_atom := '(' matrix_expr ')' | numeral | binder | 'G.adjMatrix' 'ℕ' | 'Fintype.card' 'V' | already-allowed identifier (bare atom)
        nat_pow     := nat_atom ('^' nat_pow)?                 -- an exponent: one atom or a parenthesised natural-number expression
        nat_atom    := '(' nat_expr ')' | numeral | binder | 'Fintype.card' 'V'
        nat_expr    := nat_pow (('+' | '-' | '*') nat_pow)*   -- natural-index arithmetic (TASK-1021): `-` is admitted ONLY here
    So `(G.adjMatrix ℕ) ^ (Fintype.card V - 1 - k)` is admissible (the exponent is index arithmetic, like the task's own
    `Fintype.card V - 1`), while `(G.adjMatrix ℕ - 1) ^ k` is not (no matrix subtraction). Everything else is refused: application by
    juxtaposition (entrywise indexing `A i j`, function calls) other than `G.adjMatrix ℕ` / `Fintype.card V`, `/`, `%`, `.entry`, `.1`,
    keywords (`fun`, `if`, `match`, ...), `∑`/`λ`, and every other identifier (`Reachable`, `Matrix.of`, `criterion`, `Classical`,
    `G.compl.adjMatrix`, ...)."""
    n, pos = len(body_toks), [0]
    allowed = set(allowed_identifiers or [])

    def peek():
        return body_toks[pos[0]] if pos[0] < n else None

    def advance():
        pos[0] += 1

    def expect_ident(name, what):
        t = peek()
        if not (t and t[0] == "ident" and t[1] == name):
            raise _BodyError("`%s` must be applied to `%s` (the task's `%s`)" % (what, name, what + " " + name))
        advance()

    def close_paren(where):
        if not _is_sym(peek(), ")"):
            raise _BodyError("unbalanced parenthesis in %s" % where)
        advance()

    def nat_atom():
        t = peek()
        if t is None:
            raise _BodyError("exponent ends where a natural-number term is expected")
        if _is_sym(t, "("):
            advance()
            nat_expr()
            close_paren("an exponent of the summand body")
            return
        if t[0] == "num":
            advance()
            return
        if t[0] == "ident":
            if t[1] == binder:
                advance()
                return
            if t[1] == CARD:
                advance()
                expect_ident(TYPE_BINDER, CARD)
                return
            raise _BodyError("identifier not permitted in an exponent of the summand body: %s" % t[1])
        if t[0] == "kw":
            raise _BodyError("keyword not permitted in summand body: %s" % t[1])
        raise _BodyError("token not permitted in an exponent of the summand body: %s" % t[1])

    def nat_pow():
        nat_atom()
        if _is_sym(peek(), "^"):
            advance()
            nat_pow()

    def nat_expr():
        nat_pow()
        while True:
            t = peek()
            if t is None or _is_sym(t, ")"):
                return
            if t[0] == "sym" and t[1] in NAT_OPERATORS:
                advance()
                nat_pow()
                continue
            if t[0] in ("ident", "num", "kw") or _is_sym(t, "("):
                raise _BodyError("application by juxtaposition in an exponent of the summand body: `... %s`" % t[1])
            raise _BodyError("operator or token not permitted in an exponent of the summand body: %s" % t[1])

    def matrix_atom():
        t = peek()
        if t is None:
            raise _BodyError("summand body ends where a matrix term is expected")
        kind, s = t[0], t[1]
        if _is_sym(t, "("):
            advance()
            matrix_expr()
            close_paren("summand body")
            return
        if kind == "num":
            advance()
            return
        if kind == "ident":
            if s == binder:
                advance()
                return
            if s == ADJ_MATRIX:
                advance()
                expect_ident(NAT, ADJ_MATRIX)
                return
            if s == CARD:
                advance()
                expect_ident(TYPE_BINDER, CARD)
                return
            if s in allowed:
                advance()
                return
            raise _BodyError("identifier not permitted in summand body: %s" % s)
        if kind == "kw":
            raise _BodyError("keyword not permitted in summand body: %s" % s)
        raise _BodyError("token not permitted in summand body: %s" % s)

    def matrix_pow():
        matrix_atom()
        if _is_sym(peek(), "^"):
            advance()
            nat_pow()

    def matrix_expr():
        matrix_pow()
        while True:
            t = peek()
            if t is None or _is_sym(t, ")"):
                return
            if t[0] == "sym" and t[1] in MATRIX_OPERATORS:
                advance()
                matrix_pow()
                continue
            if t[0] in ("ident", "num", "kw") or _is_sym(t, "("):
                raise _BodyError("application by juxtaposition in summand body (entrywise indexing or a function call): `... %s`" % t[1])
            if _is_sym(t, "-"):
                raise _BodyError("matrix subtraction is not permitted in summand body (`-` is admitted only inside an exponent)")
            raise _BodyError("operator or token not permitted in summand body: %s" % t[1])

    if n == 0:
        return ["empty summand body"]
    try:
        matrix_expr()
        if pos[0] != n:
            raise _BodyError("unbalanced parenthesis in summand body")
    except _BodyError as exc:
        return [str(exc)]
    return []


def _text(toks, a, b, hole_text):
    return hole_text[toks[a][2]:toks[b - 1][3]] if b > a else ""


def analyse_e10_hole(hole_text, rules, template_binders=(TYPE_BINDER, GRAPH_BINDER)):
    """Every lambda site of the hole (`fun` keyword, `∑` binder notation, `λ`) judged against the approved rule.
    Returns {"sites": [...], "problems": [e10_summand_lambda:... for every refused `fun` site], "fun_ban_lifted": bool, "fun_count",
    "sum_count", "lambda_symbol_count"}. fun_ban_lifted is True iff there is at least one `fun` and every `fun` is approved. `∑` and `λ`
    sites are judged and reported (approved / problems) for information only: they contain no `fun`, so the pinned grammar decides them
    unchanged and they never contribute to "problems"."""
    allowed = set(rules.get("allowed_identifiers") or [])
    forbidden = set(rules.get("forbidden_tokens") or [])
    toks = tokenize(hole_text)
    fun_idx = [i for i, t in enumerate(toks) if t[0] == "kw" and t[1] == "fun"]
    sum_idx = [i for i, t in enumerate(toks) if _is_sym(t, "∑")]
    lam_idx = [i for i, t in enumerate(toks) if t[0] == "kw" and t[1] == "λ"]
    info = {"sites": [], "problems": [], "fun_ban_lifted": False, "fun_count": len(fun_idx), "sum_count": len(sum_idx),
            "lambda_symbol_count": len(lam_idx)}
    match = _match_parens(toks)
    if match is None:
        if fun_idx:
            info["problems"].append("e10_summand_lambda:unbalanced parentheses in the hole; no summand lambda can be recognised")
        return info

    def site(kind, i):
        return {"kind": kind, "char_span": [toks[i][2], toks[i][3]], "approved": False, "binder": None, "range_expr": None, "body": None, "problems": []}

    for f in fun_idx:                                   # Finset.sum ( Finset.range R ) ( fun k => BODY )
        s = site("fun", f)
        p = s["problems"]
        L = f - 1
        if not (L >= 0 and _is_sym(toks[L], "(")):
            p.append("`fun` is not the first token of a parenthesised group `(fun k => BODY)`")
        else:
            Rp = match[L]
            binder = toks[f + 1] if f + 1 < Rp else None
            arrow = toks[f + 2] if f + 2 < Rp else None
            b_problem = check_binder(binder, template_binders, allowed, forbidden)
            if b_problem:
                p.append(b_problem)
            elif arrow is None or arrow[0] != "arrow":
                p.append("the lambda must bind exactly one bare identifier followed by `=>` (found `%s`)" % _text(toks, f + 1, min(f + 3, Rp), hole_text))
            else:
                s["binder"] = binder[1]
                s["body"] = _text(toks, f + 3, Rp, hole_text)
                p.extend(check_summand_body(toks[f + 3:Rp], binder[1], allowed))
            # the group `(fun ...)` must be the second argument of Finset.sum whose first argument is `(Finset.range R)`
            K = L - 1
            if not (K >= 0 and _is_sym(toks[K], ")")):
                p.append("the lambda group is not the second argument of `Finset.sum (Finset.range R)`")
            else:
                K0 = match[K]
                if not (K0 + 1 < K and toks[K0 + 1][0] == "ident" and toks[K0 + 1][1] == "Finset.range" and K0 + 2 < K):
                    p.append("the lambda is not summed over an explicit `(Finset.range R)`")
                elif not (K0 - 1 >= 0 and toks[K0 - 1][0] == "ident" and toks[K0 - 1][1] == "Finset.sum"):
                    p.append("the sum is not written with `Finset.sum`")
                else:
                    s["range_expr"] = _text(toks, K0 + 2, K, hole_text)
        s["approved"] = not p
        info["sites"].append(s)
    for q in sum_idx:                                   # ∑ k ∈ Finset.range R , BODY     /     ∑ k in Finset.range R , BODY
        s = site("∑", q)
        p = s["problems"]
        end = _enclosing_close(toks, match, q)
        binder = toks[q + 1] if q + 1 < end else None
        sep = toks[q + 2] if q + 2 < end else None
        b_problem = check_binder(binder, template_binders, allowed, forbidden)
        if b_problem:
            p.append(b_problem)
        elif not (_is_sym(sep, "∈") or (sep is not None and sep[0] == "kw" and sep[1] == "in")):
            p.append("`∑` must bind one bare identifier followed by `∈` or `in` (found `%s`)" % _text(toks, q + 1, min(q + 3, end), hole_text))
        elif not (q + 3 < end and toks[q + 3][0] == "ident" and toks[q + 3][1] == "Finset.range"):
            p.append("`∑` is not over an explicit `Finset.range R`")
        else:
            depth, comma = 0, None
            for j in range(q + 4, end):
                if _is_sym(toks[j], "("):
                    depth += 1
                elif _is_sym(toks[j], ")"):
                    depth -= 1
                elif depth == 0 and _is_sym(toks[j], ","):
                    comma = j
                    break
            if comma is None or comma == q + 4:
                p.append("`∑ k ∈ Finset.range R,` needs a range expression R followed by `,`")
            else:
                s["binder"] = binder[1]
                s["range_expr"] = _text(toks, q + 4, comma, hole_text)
                s["body"] = _text(toks, comma + 1, end, hole_text)
                p.extend(check_summand_body(toks[comma + 1:end], binder[1], allowed))
        s["approved"] = not p
        info["sites"].append(s)
    for l in lam_idx:
        s = site("λ", l)
        s["problems"].append("`λ` is not an approved spelling (the approved forms are `fun` inside `Finset.sum (Finset.range R) (...)` and `∑ ... ∈/in Finset.range R, ...`)")
        info["sites"].append(s)
    for s in info["sites"]:
        s["informational"] = s["kind"] != "fun"           # `∑` / `λ` sites never add a problem (pinned grammar decides them unchanged)
        if not s["approved"] and s["kind"] == "fun":
            for pr in s["problems"]:
                msg = "e10_summand_lambda:%s at char %d: %s" % (s["kind"], s["char_span"][0], pr)
                if msg not in info["problems"]:
                    info["problems"].append(msg)
    info["fun_ban_lifted"] = bool(fun_idx) and all(s["approved"] for s in info["sites"] if s["kind"] == "fun")
    return info


def adjust_hole_syntax(record_id, hole_text, hole_syntax_check, rules, template_binders=(TYPE_BINDER, GRAPH_BINDER)):
    """The v3 post-pass over the pinned checks["hole_syntax"] dict. Returns a new dict; the input is not modified.
    Applies only to record E10 with a grammar that forbids `fun`; otherwise the pinned dict is returned with the audit fields added."""
    out = dict(hole_syntax_check)
    pinned_problems = list(hole_syntax_check.get("problems") or [])
    out["pre_lambda"] = {"pass": hole_syntax_check.get("pass"), "problems": pinned_problems,
                         "description": "checks.hole_syntax of the pinned validate.py under the grammar file passed, before the v3 E10 post-pass"}
    rules = rules or {}
    if record_id != RULE_RECORD:
        out["e10_summand_lambda"] = {"applied": False, "reason": "record %s is not %s; pinned hole grammar in force" % (record_id, RULE_RECORD), "fun_ban_lifted": False}
        return out
    if hole_text is None:
        out["e10_summand_lambda"] = {"applied": False, "reason": "no hole extracted", "fun_ban_lifted": False}
        return out
    if "fun" not in (rules.get("forbidden_tokens") or []):
        out["e10_summand_lambda"] = {"applied": False, "reason": "the record's grammar does not forbid `fun`; nothing to lift", "fun_ban_lifted": False}
        return out
    info = analyse_e10_hole(hole_text, rules, template_binders)
    problems = list(pinned_problems)
    if info["fun_ban_lifted"]:
        problems = [p for p in problems if p != "hole_forbidden_token:fun"]
    for p in info["problems"]:
        if p not in problems:
            problems.append(p)
    out["problems"] = problems
    out["pass"] = not problems
    out["e10_summand_lambda"] = {"applied": True, "rule_version": VALIDATOR_VERSION, **info}
    return out


# ---------------------------------------------------------------------------------------------------------- wrapper entry points

def grammar_version_hint(grammar_path):
    """Which evaluator.json family the grammar file came from (by path): v1 (evaluator_records), v2-identifiers (evaluator_records_v2), other."""
    if not grammar_path:
        return None
    p = str(grammar_path)
    if "/evaluator_records_v2/" in p:
        return "v2-identifiers (evaluator_records_v2)"
    if "/evaluator_records/" in p:
        return "v1 (evaluator_records)"
    return "other: " + p


def validate_v3(record_id, submission_path, workspace_dir, cache_dir, packet_dir=None, evaluator_dir=None, hole_grammar_path=None, argv=None):
    verdict = V.validate(record_id, submission_path, workspace_dir, cache_dir, packet_dir, evaluator_dir, hole_grammar_path, argv)
    checks = verdict["checks"]
    pinned_verdict, pinned_overall = verdict["verdict"], dict(verdict["overall"])
    grammar_path = ((verdict.get("pinned") or {}).get("evaluator.json") or {}).get("path")
    grammar_sha = ((verdict.get("pinned") or {}).get("evaluator.json") or {}).get("sha256")
    hs = checks["hole_syntax"]
    rules = hs.get("rule") or {}
    tb = ((hs.get("identifiers") or {}).get("template_binders")) or [TYPE_BINDER, GRAPH_BINDER]
    hole_text = checks["template_structure"].get("hole_filled_with")
    new_hs = adjust_hole_syntax(record_id, hole_text, hs, rules, tuple(tb))
    applied = new_hs["e10_summand_lambda"]["applied"]
    if applied:
        checks["hole_syntax"] = new_hs
        verdict["hole_syntax"] = new_hs
        final_applicable = not verdict["overall"]["endpoint_final_not_applicable"]
        verdict["overall"] = V.overall_verdict(checks, final_applicable, new_hs)
        verdict["verdict"] = "PASS" if verdict["overall"]["all_pass"] else "FAIL"
        verdict["invocation"]["exit_code"] = 0 if verdict["overall"]["all_pass"] else 1
    else:
        checks["hole_syntax"] = new_hs                   # pinned content + the audit fields (pre_lambda, e10_summand_lambda.applied False)
        verdict["hole_syntax"] = new_hs
    verdict["validator_version"] = VALIDATOR_VERSION
    verdict["derived_from"] = {"validate.py": PINNED_PATH, "sha256": PINNED_SHA256, "repair_common.py": os.path.join(HARNESS, "repair_common.py"),
                               "repair_common_sha256": rc.file_sha(os.path.join(HARNESS, "repair_common.py"))}
    verdict["invocation"]["validator_files_sha256"]["validate_v3_lambda.py"] = rc.file_sha(os.path.abspath(__file__))
    verdict["pre_lambda_verdict"] = {"description": "verdict of the pinned validate.py (derived_from) under the grammar file below, BEFORE the v3 E10 "
                                                    "summand-lambda post-pass; under check_record_v3.sh the grammar file is the identifier-only v2 "
                                                    "evaluator.json, so this is the pre-lambda verdict under the v2 grammar, not a v1 verdict",
                                     "validator": {"validate.py": PINNED_PATH, "sha256": PINNED_SHA256},
                                     "grammar_file": grammar_path, "grammar_sha256": grammar_sha, "grammar_version_hint": grammar_version_hint(grammar_path),
                                     "verdict": pinned_verdict, "overall": pinned_overall, "hole_syntax": new_hs["pre_lambda"]}
    verdict["v3_lambda"] = {"validator_version": VALIDATOR_VERSION, "approval": APPROVAL, "record_rule_applied": applied,
                            "fun_ban_lifted": new_hs["e10_summand_lambda"].get("fun_ban_lifted", False),
                            "verdict_changed_from_pre_lambda": verdict["verdict"] != pinned_verdict, "pre_lambda_verdict": pinned_verdict,
                            "grammar_version_hint": grammar_version_hint(grammar_path)}
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--submission", required=True)
    ap.add_argument("--out")
    ap.add_argument("--workspace")
    ap.add_argument("--cache-dir", default=V.DEFAULT_CACHE)
    ap.add_argument("--packet-dir")
    ap.add_argument("--evaluator-dir")
    ap.add_argument("--hole-grammar", help="evaluator.json carrying hole_syntax (default: <evaluator-dir>/evaluator.json, then evaluator_records/<record>/evaluator.json)")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    tmp = None
    workspace = a.workspace
    if not workspace:
        os.makedirs(os.path.dirname(V.DEFAULT_CACHE), exist_ok=True)
        tmp = tempfile.mkdtemp(prefix="repair_validate_v3_", dir=os.path.dirname(V.DEFAULT_CACHE))
        workspace = tmp
    try:
        verdict = validate_v3(a.record, a.submission, workspace, a.cache_dir, a.packet_dir, a.evaluator_dir, a.hole_grammar)
    finally:
        if tmp and not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)
    if a.out:
        rc.atomic_json(a.out, verdict)
    summary = {"record_id": verdict["record_id"], "verdict": verdict["verdict"], "validator_version": VALIDATOR_VERSION,
               "derived_from_validate_py_sha256": PINNED_SHA256, "submission_sha256": verdict["submission_sha256"],
               "overall": verdict["overall"], "pre_lambda_verdict": verdict["pre_lambda_verdict"]["verdict"],
               "grammar_version_hint": verdict["pre_lambda_verdict"]["grammar_version_hint"],
               "checks": {k: v.get("pass") for k, v in verdict["checks"].items() if isinstance(v, dict) and "pass" in v},
               "hole_filled_with": verdict["hole_filled_with"], "hole_syntax": {k: verdict["hole_syntax"].get(k) for k in ("pass", "problems")},
               "e10_summand_lambda": {k: verdict["hole_syntax"].get("e10_summand_lambda", {}).get(k) for k in ("applied", "fun_ban_lifted")},
               "final_declared_cannot": verdict["final_declared_cannot"], "host_safety_gate": verdict["host_safety_gate"],
               "pinned": {k: (v.get("sha256") if isinstance(v, dict) else v) for k, v in verdict["pinned"].items() if k != "lean_version"},
               "exit_code": verdict["invocation"]["exit_code"], "out": a.out}
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return verdict["invocation"]["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
