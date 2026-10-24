#!/usr/bin/env python3
"""Compile the eleven recovered historical certificates. Read-only w.r.t. the repository.

Astra TASK-175 conditions: record roster, exact preexisting bytes and hashes, toolchain, commands, every outcome.
NO repair of old code. A failure is reported as a result, not fixed. New compiles establish REPRODUCIBILITY NOW,
not authentication that the historical run occurred.
"""
import json, os, subprocess, hashlib, time

OUT = 'ARCHIVED_REPLAY_ROOT/oldcerts'
TOOLCHAINS = {
    '4.30.0': 'USER_HOME/.elan/toolchains/leanprover--lean4---v4.30.0/bin/lean',
    '4.34.0': 'USER_HOME/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean',
}
PER_FILE_TIMEOUT = 900

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def now():
    return subprocess.run(['date', '-u', '+%FT%TZ'], capture_output=True, text=True).stdout.strip()

def main():
    man = json.load(open(os.path.join(OUT, 'manifest.json')))
    results = {'schema': 'old-certificate-recompile/v1', 'started_utc': now(), 'model_calls': 0,
               'scope': ('Deterministic recompilation of historical certificate bytes recovered at their exact '
                         'recorded sha256. Establishes reproducibility at the stated toolchain NOW; it does NOT '
                         'authenticate that the original historical run occurred.'),
               'no_repair_policy': 'Files compiled exactly as recovered. No edit, no repair, no flag added.',
               'toolchains': {}, 'rows': []}
    for v, path in TOOLCHAINS.items():
        r = subprocess.run([path, '--version'], capture_output=True, text=True)
        results['toolchains'][v] = {'path': path, 'version_string': r.stdout.strip(), 'exists': os.path.exists(path)}

    for entry in man:
        rid = entry['record_id']
        src = entry['recovered_path']
        got = sha(src)
        row = {'record_id': rid, 'recovered_path': src, 'expected_sha256': entry['sha256'],
               'actual_sha256_before': got, 'bytes': entry['bytes'],
               'hash_matches_historical': got == entry['sha256'],
               'block_index_zero_based': entry['block_index_zero_based'], 'recipe': entry['recipe'],
               'dossier': entry['dossier'], 'dossier_sha256': entry['dossier_sha256'], 'compiles': {}}
        for v, lean in TOOLCHAINS.items():
            cmd = [lean, src]
            t0 = time.time()
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=PER_FILE_TIMEOUT, cwd=OUT)
                rc, out, err, to = p.returncode, p.stdout, p.stderr, False
            except subprocess.TimeoutExpired as e:
                rc, out, err, to = None, (e.stdout or b'').decode('utf8', 'replace'), (e.stderr or b'').decode('utf8', 'replace'), True
            dt = time.time() - t0
            row['compiles'][v] = {
                'command': cmd, 'cwd': OUT, 'seconds': round(dt, 2), 'exit_code': rc, 'timed_out': to,
                'stdout_tail': out[-3000:], 'stderr_tail': err[-3000:],
                'source_sha256_after': sha(src), 'source_unchanged': sha(src) == got,
                'status': 'PASS' if rc == 0 else ('TIMEOUT' if to else 'FAIL'),
            }
            print(f"{rid[:42]:44s} {v:8s} {row['compiles'][v]['status']:8s} rc={rc} {dt:.1f}s", flush=True)
        results['rows'].append(row)
        json.dump(results, open(os.path.join(OUT, 'RECOMPILE_RESULTS.json'), 'w'), indent=1)

    results['finished_utc'] = now()
    summary = {}
    for v in TOOLCHAINS:
        summary[v] = {s: sum(1 for r in results['rows'] if r['compiles'][v]['status'] == s)
                      for s in ('PASS', 'FAIL', 'TIMEOUT')}
    results['summary'] = {'roster': len(man), 'by_toolchain': summary,
                          'all_hashes_matched_historical': all(r['hash_matches_historical'] for r in results['rows'])}
    json.dump(results, open(os.path.join(OUT, 'RECOMPILE_RESULTS.json'), 'w'), indent=1)
    print('\nSUMMARY', json.dumps(results['summary']))

if __name__ == '__main__':
    main()
