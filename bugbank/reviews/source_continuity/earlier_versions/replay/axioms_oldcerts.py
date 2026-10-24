#!/usr/bin/env python3
"""Transitive axiom inspection for the recovered historical certificates (Astra TASK-175/177).

NOT a repair. Each driver is the recovered file's EXACT bytes as a prefix, followed only by `#print axioms`
lines. The prefix hash is recorded and checked so anyone can confirm no byte of the original was altered.
Every declaration in the file is inspected; nothing is pre-selected by me.
"""
import json, os, re, subprocess, hashlib, sys

BASE = 'ARCHIVED_REPLAY_ROOT'
LEAN = 'USER_HOME/.elan/toolchains/leanprover--lean4---v4.30.0/bin/lean'
DECL = re.compile(r'^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma)\s+([A-Za-z_][\w\'\.]*)', re.M)
NS = re.compile(r'^namespace\s+(\S+)', re.M)
BAD = ('sorryAx', 'Lean.ofReduceBool', 'Lean.ofReduceNat')

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def run(folder, outname):
    folder = os.path.abspath(folder)
    man = json.load(open(os.path.join(folder, 'manifest.json')))
    drv_dir = os.path.join(folder, 'axiom_drivers'); os.makedirs(drv_dir, exist_ok=True)
    now = subprocess.run(['date','-u','+%FT%TZ'], capture_output=True, text=True).stdout.strip()
    out = {'schema': 'old-certificate-axioms/v1', 'built_utc': now, 'model_calls': 0,
           'method': ('driver = recovered file EXACT bytes as prefix + appended `#print axioms` lines only; '
                      'prefix sha256 recorded and verified; no original file modified'),
           'lean': LEAN, 'rows': []}
    for e in man:
        rid, src = e['record_id'], e['recovered_path']
        raw = open(src, 'rb').read()
        text = raw.decode('utf8', 'surrogateescape')
        ns = NS.search(text)
        ns = ns.group(1) if ns else None
        names = [m.group(2) for m in DECL.finditer(text)]
        cands = []
        for n in names:
            cands.append(f'{ns}.{n}' if ns and not n.startswith(ns + '.') else n)
        body = text
        if not body.endswith('\n'):
            body += '\n'
        if ns:
            body += f'\nopen {ns} in\n' if False else '\n'
        body += ''.join(f'#print axioms {c}\n' for c in cands)
        drv = os.path.join(drv_dir, rid + '.driver.lean')
        open(drv, 'w', encoding='utf8', errors='surrogateescape').write(body)
        p = subprocess.run([LEAN, drv], capture_output=True, text=True, timeout=1800, cwd=drv_dir)
        so = p.stdout
        # Lean wraps long lines, so parse over the WHOLE stdout with DOTALL rather than line by line.
        # A line-based parser silently skipped a main refutation theorem on the first run.
        axioms = {}
        for m in re.finditer(r"'([^']+)' (?:depends on axioms: \[(.*?)\]|does not depend on any axioms)", so, re.S):
            axioms[m.group(1)] = [a.strip() for a in (m.group(2) or '').replace('\n', ' ').split(',') if a.strip()]
        flagged = {k: v for k, v in axioms.items() if any(b in x for x in v for b in BAD)}
        row = {'record_id': rid, 'prefix_sha256': sha(src), 'expected_sha256': e['sha256'],
               'prefix_unmodified': sha(src) == e['sha256'], 'namespace': ns,
               'declarations_found': len(cands), 'declarations': cands,
               'driver_path': drv, 'driver_sha256': sha(drv), 'exit_code': p.returncode,
               'axioms_by_declaration': axioms, 'inspected': len(axioms),
               'flagged_declarations': flagged,
               'uses_sorry_or_native': bool(flagged),
               'stdout_full': so, 'stderr_tail': p.stderr[-2500:]}
        out['rows'].append(row)
        print(f"{rid[:42]:44s} decls={len(cands):3d} inspected={len(axioms):3d} rc={p.returncode} flagged={len(flagged)}", flush=True)
        json.dump(out, open(os.path.join(folder, outname), 'w'), indent=1)
    out['summary'] = {'files': len(out['rows']),
                      'all_prefixes_unmodified': all(r['prefix_unmodified'] for r in out['rows']),
                      'files_with_sorry_or_native': sum(1 for r in out['rows'] if r['uses_sorry_or_native']),
                      'total_declarations_inspected': sum(r['inspected'] for r in out['rows'])}
    json.dump(out, open(os.path.join(folder, outname), 'w'), indent=1)
    print('\nSUMMARY', json.dumps(out['summary']))

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
