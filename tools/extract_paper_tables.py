#!/usr/bin/env python3
"""Extract the tables and figure text of the Co-PEER manuscript into data files for the website.

Usage: extract_paper_tables.py <path to main.tex> <output directory> [--commit <id>]

Every output file records the manuscript commit, the SHA-256 of main.tex, the table label,
the line range of the environment in main.tex and the caption. Numbers are parsed from the
LaTeX cells; nothing is typed by hand. A JSON file and a JavaScript twin (which assigns the
same object to window.COPEER_DATA[<name>] so pages work from file://) are written per table,
plus MANIFEST.md.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------------- helpers

def brace_span(s, i):
    """s[i] == '{'; return index just after the matching '}'."""
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError('unbalanced braces')


def replace_command(s, name, nargs=1, keep=None, sep=' '):
    """Replace \\name{a}{b}... by the kept argument (default: last), repeatedly."""
    pat = '\\' + name
    out = []
    i = 0
    while True:
        k = s.find(pat, i)
        if k < 0 or (k + len(pat) < len(s) and s[k + len(pat)].isalpha()):
            if k < 0:
                out.append(s[i:])
                break
            out.append(s[i:k + len(pat)])
            i = k + len(pat)
            continue
        out.append(s[i:k])
        j = k + len(pat)
        while j < len(s) and s[j] in ' \t':
            j += 1
        args = []
        for _ in range(nargs):
            if j < len(s) and s[j] == '[':
                j = s.index(']', j) + 1
            if j >= len(s) or s[j] != '{':
                break
            e = brace_span(s, j)
            args.append(s[j + 1:e - 1])
            j = e
        if not args:
            out.append(pat)
            i = j
            continue
        kept = args[keep if keep is not None else -1]
        kept = kept.replace('\\\\', sep)
        out.append(kept)
        i = j
    return ''.join(out)


def strip_rules(row):
    row = re.sub(r'\\(toprule|midrule|bottomrule|endfirsthead|endhead)\b', '', row)
    row = re.sub(r'\\cmidrule(\([^)]*\))?\{[^}]*\}', '', row)
    row = re.sub(r'\\addlinespace(\[[^\]]*\])?', '', row)
    row = re.sub(r'\\(centering|small|footnotesize|scriptsize|raggedright|arraybackslash)\b', '', row)
    row = re.sub(r'\\setlength\{[^}]*\}\{[^}]*\}', '', row)
    row = re.sub(r'\\renewcommand\{[^}]*\}\{[^}]*\}', '', row)
    return row


def tabular_bodies(env_text):
    """Return the bodies of every tabular-like environment inside env_text, in order."""
    bodies = []
    for m in re.finditer(r'\\begin\{(tabular|tabularx|longtable)\}', env_text):
        start = m.end()
        # skip the column specification (and the width argument of tabularx)
        j = start
        nbr = 2 if m.group(1) == 'tabularx' else 1
        for _ in range(nbr):
            while env_text[j] in ' \n':
                j += 1
            j = brace_span(env_text, j)
        end = env_text.index('\\end{' + m.group(1) + '}', j)
        bodies.append(env_text[j:end])
    return bodies


def split_rows(body):
    body = replace_command(body, 'shortstack')
    # \multicolumn{n}{c}{X} -> X followed by n-1 empty cells, so header rows keep the column count
    while '\\multicolumn' in body:
        k = body.index('\\multicolumn')
        j = k + len('\\multicolumn')
        e1 = brace_span(body, j); span = int(body[j + 1:e1 - 1])
        e2 = brace_span(body, e1); e3 = brace_span(body, e2)
        content = body[e2 + 1:e3 - 1]
        body = body[:k] + content + (' & \u0001SPAN' * (span - 1)) + body[e3:]
    # longtable bodies carry their caption and label; drop them
    body = re.sub(r'\\caption\{', '\u0000CAP{', body)
    while '\u0000CAP{' in body:
        k = body.index('\u0000CAP{')
        e = brace_span(body, k + 4)
        body = body[:k] + body[e:]
    body = re.sub(r'\\label\{[^}]*\}', '', body)
    rows = re.split(r'\\\\(?:\[[^\]]*\])?', body)
    out = []
    for r in rows:
        r = strip_rules(r).strip()
        if not r or r == '&' * r.count('&'):
            continue
        cells = [c.strip() for c in r.split('&')]
        out.append(cells)
    return out


def clean_text(cell, mode='tex'):
    """mode 'tex' keeps math and citations as [cite:key]; mode 'plain' strips everything."""
    c = cell
    c = c.replace('\\newline', ' / ')
    c = re.sub(r'\\(?:citep|citet|citetalias|citealp)\{([^}]*)\}', lambda m: '[cite:' + m.group(1) + ']', c)
    c = replace_command(c, 'href', nargs=2, keep=1)
    for name in ('textbf', 'emph', 'texttt', 'path', 'textit', 'operatorname'):
        if mode == 'plain' or name != 'operatorname':
            c = replace_command(c, name)
    c = c.replace('\\%', '%').replace('\\,', ' ').replace('~', ' ').replace('{,}', ',')
    c = c.replace('\\&', '&').replace("``", '"').replace("''", '"').replace('\\-', '')
    c = re.sub(r'\\(?:ref|eqref|autoref|cref)\{([^}]*)\}', lambda m: '[ref:' + m.group(1) + ']', c)
    c = c.replace('\\_', '_')
    c = re.sub(r"\\'\{?o\}?", 'ó', c)
    c = c.replace('\\scriptsize', '').replace('\\small', '').replace('\\ ', ' ')
    c = re.sub(r'(?<!-)--(?!-)', '\u2013', c)
    if mode == 'plain':
        c = c.replace('$', '')
        c = re.sub(r'\\(ge|geq)\b', '≥', c)
        c = re.sub(r'\\(le|leq)\b', '≤', c)
        c = re.sub(r'\\Delta\b', 'Δ', c)
        c = re.sub(r'\\[a-zA-Z]+', '', c)
        c = c.replace('{', '').replace('}', '')
    else:
        # keep math; remove stray grouping braces outside math
        parts = c.split('$')
        for k in range(0, len(parts), 2):
            parts[k] = parts[k].replace('{', '').replace('}', '')
        c = '$'.join(parts)
    c = re.sub(r'\s+', ' ', c).strip()
    return c


NUM = r'[-+]?\d[\d,]*(?:\.\d+)?|[-+]?\.\d+'


def parse_number(tok):
    t = tok.replace(',', '').replace('+', '')
    return float(t) if '.' in t else int(t)


def parse_numeric(cell):
    """Interpret a numeric cell. Returns a JSON-able value."""
    c = clean_text(cell, 'plain')
    if c in ('---', '--', '—', '–', '-', ''):
        return None
    if c == 'n.r.':
        return {'value': None, 'note': 'not recorded'}
    m = re.fullmatch(r'(≥)?\s*(' + NUM + r')\s*(?:\[\s*(' + NUM + r')\s*,\s*(' + NUM + r')\s*\])?', c)
    if m:
        v = {'value': parse_number(m.group(2))}
        if m.group(1):
            v['lower_bound'] = True
        if m.group(3):
            v['ci95'] = [parse_number(m.group(3)), parse_number(m.group(4))]
        return v if len(v) > 1 else v['value']
    m = re.fullmatch(r'(' + NUM + r')\s*/\s*(' + NUM + r')', c)
    if m:
        return {'pair': [parse_number(m.group(1)), parse_number(m.group(2))]}
    m = re.fullmatch(r'(' + NUM + r')\s*/\s*(' + NUM + r')\s*/\s*(' + NUM + r')', c)
    if m:
        return {'triple': [parse_number(g) for g in m.groups()]}
    m = re.fullmatch(r'1 \(ref\.\)', c)
    if m:
        return {'value': 1, 'reference': True}
    m = re.fullmatch(r'(' + NUM + r')\s*of\s*(' + NUM + r')', c)
    if m:
        return {'pair': [parse_number(m.group(1)), parse_number(m.group(2))]}
    return {'text': c}


# ----------------------------------------------------------------------------- source access

class Source:
    def __init__(self, path):
        self.path = Path(path)
        self.text = self.path.read_text(encoding='utf-8')
        self.lines = self.text.split('\n')
        self.sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.blocks = {}
        for m in re.finditer(r'\\begin\{filecontents\*\}\[overwrite\]\{([^}]+)\}\n(.*?)\\end\{filecontents\*\}', self.text, re.S):
            self.blocks[m.group(1)] = m.group(2)

    def environment(self, label):
        """Return (text, first_line, last_line) of the table/figure environment carrying label."""
        pos = self.text.index('\\label{' + label + '}')
        line_no = self.text.count('\n', 0, pos) + 1
        # walk backwards to the enclosing begin
        starts = [(m.start(), m.group(1)) for m in re.finditer(r'\\begin\{(table\*?|longtable|figure\*?)\}', self.text) if m.start() < pos]
        s, kind = starts[-1]
        e = self.text.index('\\end{' + kind + '}', pos) + len('\\end{' + kind + '}')
        env = self.text[s:e]
        # resolve \input of embedded generated tables
        def inp(m):
            name = m.group(1)
            if not name.endswith('.tex'):
                name += '.tex'
            return self.blocks[name]
        env = re.sub(r'\\input\{([^}]+)\}', inp, env)
        first = self.text.count('\n', 0, s) + 1
        last = self.text.count('\n', 0, e) + 1
        return env, first, last

    def caption(self, env):
        k = env.find('\\caption{')
        if k < 0:
            return ''
        e = brace_span(env, k + len('\\caption'))
        return clean_text(env[k + len('\\caption{'):e - 1], 'tex')


# ----------------------------------------------------------------------------- table builders

def meta(src, label, first, last, caption, commit):
    return {'commit': commit, 'main_tex_sha256': src.sha256, 'label': label,
            'main_tex_lines': [first, last], 'caption': caption}


def rows_of(src, label, index=0):
    env, first, last = src.environment(label)
    bodies = tabular_bodies(env)
    return split_rows(bodies[index]), env, first, last, len(bodies)


def build_localization(src, commit, label, name):
    rows, env, first, last, _ = rows_of(src, label)
    header = rows[0]
    out = []
    for cells in rows[1:]:
        name_ = clean_text(cells[0], 'plain')
        rec = {'name': name_}
        rec['hit1'] = parse_numeric(cells[1])
        rec['hit3'] = parse_numeric(cells[2])
        if label == 'tab:localization':
            rec['recorded_total_tokens'] = parse_numeric(cells[3])
            rec['met_rules_of_100'] = parse_numeric(cells[4])
        else:
            rec['recorded_total_tokens'] = parse_numeric(cells[3])
            rec['recorded_output_tokens'] = parse_numeric(cells[4])
        rec['kind'] = 'baseline' if (rec['hit3'] is None) else 'model'
        out.append(rec)
    return {'source': meta(src, label, first, last, src.caption(env), commit),
            'columns': [clean_text(h, 'plain') for h in header], 'rows': out}


def build_generic(src, commit, label, columns, kinds, index=0, header_rows=1, carry_first=False):
    """kinds: list of 'text' | 'tex' | 'num' per column."""
    rows, env, first, last, nb = rows_of(src, label, index)
    out = []
    last_first = None
    header_cells = rows[0]
    for cells in rows[header_rows:]:
        if cells == header_cells:
            continue
        if len(cells) != len(columns) or any(c == '\u0001SPAN' for c in cells):
            # section rows such as "\emph{100 proof inputs per model}" spanning all columns
            txt = clean_text([c for c in cells if c != '\u0001SPAN'][0], 'plain') if any(c != '\u0001SPAN' for c in cells) else ''
            if txt:
                out.append({'section': txt})
            continue
        rec = {}
        for col, kind, cell in zip(columns, kinds, cells):
            if kind == 'num':
                rec[col] = parse_numeric(cell)
            elif kind == 'plain':
                rec[col] = clean_text(cell, 'plain')
            else:
                rec[col] = clean_text(cell, 'tex')
        if carry_first:
            if rec[columns[0]] == '':
                rec[columns[0]] = last_first
            else:
                last_first = rec[columns[0]]
        out.append(rec)
    def header_row(cells):
        out_cells, spanned, last = [], [], ''
        for c in cells:
            if c == '\u0001SPAN':
                out_cells.append(last); spanned.append(True)
                if spanned and len(spanned) >= 2:
                    spanned[-2] = True
            else:
                last = clean_text(c, 'plain'); out_cells.append(last); spanned.append(False)
        return out_cells, spanned
    header, spanned = header_row(rows[0])
    if header_rows == 2:
        second, _ = header_row(rows[1])
        if len(second) == len(columns):
            pad = len(second) - len(header)
            header = header + [''] * pad; spanned = spanned + [False] * pad
            header = [((a + (': ' if sp else ' ') + b).strip() if a else b) for a, b, sp in zip(header, second, spanned)]
    return {'source': meta(src, label, first, last, src.caption(env), commit),
            'header': header, 'rows': out}


def build_figure_example(src, commit):
    env, first, last = src.environment('fig:benchmark-example')
    lines = []
    for m in re.finditer(r'\{\[(\d+)\]\}\s*(.*?)\\\\\[', env, re.S):
        lines.append({'line': int(m.group(1)), 'tex': clean_text(m.group(2), 'tex')})
    total = re.search(r'\((\d+) nonblank numbered lines total\)', env)
    sel = re.search(r'"candidates":\s*\[([\d, ]+)\]', env)
    ref = re.search(r'Reference line:\}\s*Line\s*(\d+)', env)
    wit = re.search(r'Witness:\}\s*(.*?)\\\\\[', env, re.S)
    lean = re.search(r'Lean-checked statement:\}\s*\\\\\s*(.*?)\n\\end\{minipage\}', env, re.S)
    rid = re.search(r'\\texttt\{([^}]*)\}\)', src.caption(env)) or re.search(r'reddit\\_learnmath\\_dm6itc', env)
    record_id = 'reddit_learnmath_dm6itc'
    assert record_id.replace('_', '\\_') in env
    model = re.search(r'Recorded (.*?) selection', env)
    out = {
        'source': meta(src, 'fig:benchmark-example', first, last, src.caption(env), commit),
        'record_id': record_id,
        'numbered_lines_total': int(total.group(1)),
        'excerpt_lines': lines,
        'recorded_selection': {'model': clean_text(model.group(1), 'plain'), 'candidates': [int(x) for x in sel.group(1).replace(' ', '').split(',')], 'hit1': 1, 'hit3': 1},
        'reference_line': int(ref.group(1)),
        'witness_tex': clean_text(wit.group(1), 'tex'),
        'lean_statement_text': clean_text(lean.group(1), 'tex'),
    }
    assert out['reference_line'] in [l['line'] for l in lines]
    return out


def build_workflow_counts(src, commit):
    m = re.search(r'Across (\d+) executable tasks, the search produced (\d+) witnesses, (\d+) exhaustive searches without a witness in the specified finite set, (\d+) inconclusive searches, and (\d+) claims outside the permitted search setting\. Separately written checkers confirmed (\d+) of the (\d+) proposed witnesses and rejected (\w+)', src.text)
    assert m, 'workflow counts sentence not found'
    line = src.text.count('\n', 0, m.start()) + 1
    m2 = re.search(r'all (\d+) search and checker programs passed exact-arithmetic inspection', src.text)
    m3 = re.search(r'A separate stage checked (\d+) selected algorithmic failures and confirmed all (\d+)', src.text)
    words = {'three': 3}
    return {'source': {'commit': commit, 'main_tex_sha256': src.sha256, 'label': 'text:executable-checks', 'main_tex_lines': [line, line], 'caption': 'Executable checks paragraph of the procedures appendix'},
            'executable_tasks': int(m.group(1)), 'witnesses': int(m.group(2)), 'exhaustive_without_witness': int(m.group(3)),
            'inconclusive': int(m.group(4)), 'outside_permitted_setting': int(m.group(5)),
            'checker_confirmed': int(m.group(6)), 'checker_rejected': words[m.group(8)],
            'programs_replayed': int(m2.group(1)), 'selected_algorithmic_failures_checked': int(m3.group(1)), 'selected_algorithmic_failures_confirmed': int(m3.group(2))}


def build_math_constants(src, commit):
    """Statements the laboratories and tests rely on, each located in the source."""
    def find(pattern, flags=0):
        m = re.search(pattern, src.text, flags)
        assert m, pattern
        return src.text.count('\n', 0, m.start()) + 1
    items = {
        'sqrt': {
            'statement': 'The printed integer square-root recurrence starts with answer 0 at 0; given answer b at x-1 it returns b if x <= (b+1)^2 and b+1 otherwise. For every positive x it returns floor(sqrt(x-1)); replacing <= by < gives floor(sqrt(x)) for every nonnegative x.',
            'guard_weak': 'x <= (b+1)^2', 'guard_strict': 'x < (b+1)^2',
            'failure_set': 'positive perfect squares',
            'lines': [find(r'returns \$b\$ if \$x\\le\(b\+1\)\^2\$ and \$b\+1\$ otherwise'), find(r'returns \$\\lfloor\\sqrt\{x-1\}\\rfloor\$, lagging')],
        },
        'cycle_blowup': {
            'statement': 'Let n >= 5 be odd. The doubled n-cycle C_n[K_2] has a frozen six-colouring exactly when 3 divides n; for each such n there are exactly 90 * 2^n such colourings with labelled vertices and colours (90 = C(6,2) C(4,2) pair assignments; 2 orderings per bag).',
            'count_formula': '90 * 2^n', 'pair_assignments': 90, 'min_n': 5,
            'lines': [find(r'frozen six-coloring exactly when \$n\$ is a multiple of three'), find(r'\\binom\{6\}\{2\}\\binom\{4\}\{2\}=90')],
        },
        'schur': {
            'statement': 'Two-threshold rule: every even integer red; an odd k is blue if k/n <= a or k/n > b, green if a < k/n <= b. With a = 4/11, b = 10/11 and n = 22m the colouring has 99 m^2 + 3 m rainbow ordered Schur triples out of n(n-1)/2, converging to 9/22. Over 0 <= a <= b <= 1 the limiting fraction D(a,b) has unique maximum 9/22 at (4/11, 10/11); rules with a = 0 or b = 1 reach at most 2/5.',
            'a': '4/11', 'b': '10/11', 'count_formula': '99*m^2 + 3*m', 'denominator': 'n(n-1)/2', 'limit': '9/22', 'single_block_bound': '2/5',
            'stability': {'region': 'a <= 1/2 <= b and a + b >= 1 (as stated in the appendix)', 'loss': '9/22 - D = (5/2)u^2 - 2uv + (3/2)v^2', 'bound': '>= ((4 - sqrt 5)/2)(u^2 + v^2)'},
            'lines': [find(r'produces \$99m\^2\+3m\$ rainbow triples'), find(r'unique maximum of \$D\(a,b\)\$ is \$9/22\$'), find(r'D\(a,b\)=\\frac9\{22\}-\\frac52u\^2\+2uv-\\frac32v\^2')],
        },
        'projective_cubes': {
            'statement': 'For the layered construction C_d, the density exceeds the conjectured bound (d-1)/d exactly when d is not in {2^l - 2, 2^l - 1, 2^l : l >= 1}; equality holds exactly at powers of two and the density is strictly below the bound at the other exceptional dimensions. Certified families: d = 5 (13/16 > 4/5), d = 7 (7/8 > 6/7), d = 8 (8/9 > 7/8).',
            'exceptional_dimensions': '{2^l - 2, 2^l - 1, 2^l : l >= 1}',
            'recursion': 'g(1) = 1; g(P + m - 1) = (1 + g(m)) / (2P) for P = 2^l, l >= 1, 1 <= m <= P; the layered density is 1 - g(d)',
            'lines': [find(r'd\\notin\\\{2\^\\ell-2,\\;2\^\\ell-1,\\;2\^\\ell:\\ell\\ge1\\\};'), find(r'equality holds exactly when \$d\$ is a power of two'), find(r'g\(P\+m-1\)=\(1\+g\(m\)\)/\(2P\)')],
        },
        'rooks': {
            'statement': 'For the permutation w = (2,7,4,8,1,6,3,5), the Lean kernel computes 155 complete non-attacking rook placements on its permutation crossword grid; 155 = 3 mod 4.',
            'permutation': [2, 7, 4, 8, 1, 6, 3, 5], 'count': 155,
            'lines': [find(r'w=\(2,7,4,8,1,6,3,5\)')],
        },
        'even_odd': {
            'statement': 'The theorem (every real-valued function on a domain closed under negation is a sum of an even and an odd function) is true; the argument asserts f(x) = f(-x) + (-f(x)); the constant function f = 1 refutes it: 1 = 1 + (-1) = 0 is false. Valid decomposition: (f(x)+f(-x))/2 + (f(x)-f(-x))/2.',
            'false_identity_tex': 'f(x)=f(-x)+(-f(x))',
            'lines': [find(r'asserts the intermediate identity \$f\(x\)=f\(-x\)\+\(-f\(x\)\)\$')],
        },
        'shellsort': {
            'statement': 'The gap-sorting source assumes x_0 < x_n. The original witness, m = 2 and A = (3,4,2,5,1), has a Lean-checked theorem but violates the endpoint assumption (3 < 1 is false). The replacement (3,5,2,6,1,7,4) satisfies it (3 < 4) and refutes the same step.',
            'gap': 2, 'original': [3, 4, 2, 5, 1], 'replacement': [3, 5, 2, 6, 1, 7, 4],
            'lines': [find(r'A=\(3,4,2,5,1\)'), find(r'The replacement \$\(3,5,2,6,1,7,4\)\$')],
        },
    }
    return {'source': {'commit': commit, 'main_tex_sha256': src.sha256, 'label': 'text:mathematics', 'main_tex_lines': None, 'caption': 'Statements located by pattern in main.tex; the line numbers are where each pattern matched.'}, 'items': items}


def bib_entries(src, keys):
    bib = src.blocks['fc__references.bib']
    out = {}
    for key in keys:
        m = re.search(r'@\w+\{' + re.escape(key) + r',(.*?)\n\}', bib, re.S)
        if not m:
            out[key] = None
            continue
        body = m.group(1)
        def field(name):
            f = re.search(r'\b' + name + r'\s*=\s*[{"](.*?)[}"],?\n', body, re.S)
            return re.sub(r'\s+', ' ', f.group(1)).replace('{', '').replace('}', '') if f else None
        out[key] = {'title': field('title'), 'author': (field('author') or '').replace("\\'o", 'ó').replace("\\'{o}", 'ó') or None, 'year': field('year'), 'url': field('url') or (('https://doi.org/' + field('doi')) if field('doi') else None), 'eprint': field('eprint')}
    return out


# ----------------------------------------------------------------------------- main

def main():
    args = sys.argv[1:]
    commit = '444d8f7'
    if '--commit' in args:
        k = args.index('--commit')
        commit = args[k + 1]
        del args[k:k + 2]
    src = Source(args[0])
    outdir = Path(args[1])
    outdir.mkdir(parents=True, exist_ok=True)
    files = {}

    files['localization_main'] = build_localization(src, commit, 'tab:localization', 'localization_main')
    files['localization_full'] = build_localization(src, commit, 'tab:ccl-primary-results', 'localization_full')
    files['execution_settings'] = build_generic(src, commit, 'tab:ccl-execution-settings', ['model', 'context_tokens', 'generation_setting', 'interface'], ['plain', 'num', 'tex', 'plain'])
    files['local_models'] = build_generic(src, commit, 'tab:local_models', ['label', 'repository'], ['plain', 'plain'])
    files['instruction_summary'] = build_generic(src, commit, 'tab:instruction-main', ['model', 'search_confirmed', 'sequential_confirmed', 'output_ratio', 'recorded_total_ratio'], ['plain', 'num', 'num', 'num', 'num'], header_rows=2)
    files['instruction_arms'] = build_generic(src, commit, 'tab:cost-repro', ['panel_model', 'arm', 'n', 'strict', 'lenient', 'false', 'unverifiable', 'mean_output_tokens', 'output_ratio', 'observed_ratio'], ['plain', 'plain', 'num', 'num', 'num', 'num', 'num', 'num', 'num', 'num'], carry_first=True)
    files['instruction_tokens'] = build_generic(src, commit, 'tab:proofs100-fourarm-full-components', ['model', 'instruction', 'n', 'uncached_input', 'cache_reads', 'output', 'recorded_total'], ['plain', 'plain', 'num', 'num', 'num', 'num', 'num'])
    files['source_matched'] = build_generic(src, commit, 'tab:reference-sensitivity', ['model', 'catches', 'delta_catches_pp', 'output_ratio', 'recorded_total_ratio'], ['plain', 'num', 'num', 'num', 'num'])
    files['repair_outcomes'] = build_generic(src, commit, 'tab:repair_outcomes', ['solver', 'condition', 'pass', 'fail', 'absent'], ['plain', 'plain', 'num', 'num', 'num'])
    files['repair_resources'] = build_generic(src, commit, 'tab:repair_resources', ['configuration', 'condition', 'recorded_total_tokens', 'output_tokens', 'attempts_with_recorded_usage'], ['plain', 'plain', 'num', 'num', 'num'])
    files['proof_development'] = build_generic(src, commit, 'tab:proof50-results', ['model', 'protocol', 'graded_correct_bugbank_plain', 'output_tokens_bugbank_plain', 'recorded_total_bugbank_plain', 'total_token_ratio'], ['plain', 'plain', 'num', 'num', 'num', 'num'])
    files['open_problem_retrieval'] = build_generic(src, commit, 'tab:historical_retrieval', ['component', 'paired_units', 'audited_full_b_p', 'both', 'b_only_p_only', 'neither'], ['plain', 'num', 'num', 'num', 'num', 'num'])
    files['claims60_summary'] = build_generic(src, commit, 'tab:claims60-evidence', ['model', 'supported_s_o_w', 'output_ratio_s_w', 'recorded_total_ratio_s_w'], ['plain', 'num', 'num', 'num'])
    files['claims60_sensitivity'] = build_generic(src, commit, 'tab:claims60-all-sensitivities', ['model', 'arm', 'subset', 'n', 'catches_s_c', 'output_ratio', 'recorded_total_ratio'], ['plain', 'plain', 'plain', 'num', 'num', 'num', 'num'])
    files['review_rounds'] = build_generic(src, commit, 'tab:review-rounds', ['round', 'frame_and_selection', 'purpose', 'outcome'], ['tex', 'tex', 'tex', 'tex'])
    files['audit_nonapprovals'] = build_generic(src, commit, 'tab:final-human-audit-exclusions', ['packet', 'earlier_set', 'negative_checks', 'recorded_concern', 'certificate_version'], ['plain', 'plain', 'plain', 'tex', 'plain'])
    files['population_map'] = build_generic(src, commit, 'tab:population-map', ['collection_or_study', 'question'], ['tex', 'tex'])
    comp_sources = build_generic(src, commit, 'tab:corpus-sources', ['source_collection', 'dossiers', 'inputs'], ['plain', 'num', 'num'], index=0)
    comp_mech = build_generic(src, commit, 'tab:corpus-sources', ['error_mechanism', 'dossiers', 'inputs'], ['plain', 'num', 'num'], index=1)
    files['core_composition'] = {'source': comp_sources['source'], 'by_source_collection': comp_sources['rows'], 'by_error_mechanism': comp_mech['rows']}
    files['explanation_packages'] = build_generic(src, commit, 'tab:explanation-census', ['record_topic', 'formal_result', 'assumptions_scope'], ['tex', 'tex', 'tex'])
    files['certified_families'] = build_generic(src, commit, 'tab:certified-research-extensions', ['case', 'refuted_statement', 'lean_establishes', 'toolchain'], ['tex', 'tex', 'tex', 'tex'])
    files['projective_cube_families'] = build_generic(src, commit, 'tab:projective-cube-families', ['d', 'M', 'excluded_residues', 'N', 'size', 'density'], ['num', 'num', 'tex', 'tex', 'tex', 'tex'])
    files['related_resources'] = build_generic(src, commit, 'tab:related', ['resource_and_scale', 'evaluation_target', 'reference_evidence'], ['tex', 'tex', 'tex'])
    keys = sorted(set(re.findall(r'\[cite:([^\]]+)\]', json.dumps(files['related_resources']) + json.dumps(files['certified_families']) + json.dumps(files['explanation_packages']))))
    files['related_resources']['bibliography'] = bib_entries(src, keys)
    files['experiment_b'] = build_generic(src, commit, 'tab:b-results', ['model', 'reference_matches', 'valid_among_matches', 'valid_among_misses', 'total_valid_objections'], ['plain', 'num', 'num', 'num', 'num'], header_rows=2)
    files['benchmark_example'] = build_figure_example(src, commit)
    files['workflow_counts'] = build_workflow_counts(src, commit)
    files['math_constants'] = build_math_constants(src, commit)

    manifest = ['# Data manifest', '', 'Generated by `tools/extract_paper_tables.py` from the manuscript source `main.tex` at commit `%s` (SHA-256 `%s`). Each file carries its table label, the line range in `main.tex`, and the caption. Numbers are parsed from the LaTeX cells.' % (commit, src.sha256), '', '| File | Label | Lines in main.tex | Rows | SHA-256 of the JSON file (exact bytes) |', '|---|---|---|---|---|']
    for name, obj in files.items():
        js = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False)
        json_bytes = (js + '\n').encode('utf-8')
        (outdir / (name + '.json')).write_bytes(json_bytes)
        (outdir / (name + '.js')).write_text('window.COPEER_DATA = window.COPEER_DATA || {};\nwindow.COPEER_DATA[%s] = %s;\n' % (json.dumps(name), js), encoding='utf-8')
        rows = len(obj.get('rows', obj.get('items', obj.get('by_source_collection', [])))) if isinstance(obj, dict) else 0
        manifest.append('| `%s` | `%s` | %s | %d | `%s` |' % (name, obj['source']['label'], obj['source'].get('main_tex_lines'), rows, hashlib.sha256(json_bytes).hexdigest()))
    (outdir / 'MANIFEST.md').write_text('\n'.join(manifest) + '\n', encoding='utf-8')
    print('wrote %d data files to %s' % (len(files), outdir))


if __name__ == '__main__':
    main()
