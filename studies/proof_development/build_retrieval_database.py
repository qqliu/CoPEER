#!/usr/bin/env python3
"""Rebuild the released 661-entry logical SQLite/FTS5 snapshot. Python standard library."""
from pathlib import Path
import argparse,json,sqlite3
HERE=Path(__file__).resolve().parent

def build(destination):
    data=json.loads((HERE/'retrieval_snapshot.json').read_text())
    cx=sqlite3.connect(destination)
    for name,t in data['tables'].items():
        cx.execute(t['sql'])
        columns=','.join('"'+c+'"' for c in t['columns'])
        marks=','.join('?' for _ in t['columns'])
        cx.executemany(f'INSERT INTO {name} ({columns}) VALUES ({marks})',t['rows'])
    cx.commit()
    assert cx.execute('SELECT COUNT(*) FROM entries').fetchone()[0]==661
    assert cx.execute('SELECT COUNT(*) FROM entries_fts').fetchone()[0]==661
    cx.close()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise SystemExit('Choose a new output path; existing databases are preserved.')
    build(a.output)
    print('Built661-entry SQLite/FTS5 snapshot:',a.output)
