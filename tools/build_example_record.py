#!/usr/bin/env python3
"""Build docs/data/example_record.js for the front-page example from the released evidence:
the current membership record (bugbank/core/membership.json), the numbered source lines
(bugbank/sources/<id>.json) and the certificate path. Email patterns in displayed text are masked;
the released files themselves are not modified. Usage: build_example_record.py [record_id]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rid = sys.argv[1] if len(sys.argv) > 1 else 'reddit_learnmath_dm6itc'
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

membership = json.loads((root / 'bugbank/core/membership.json').read_text(encoding='utf-8'))
rec = [r for r in membership['records'] if r['record_id'] == rid][0]
src = json.loads((root / 'bugbank/sources' / (rid + '.json')).read_text(encoding='utf-8'))
lines = json.loads(src['lines']) if isinstance(src['lines'], str) else src['lines']
dossier_path = root / 'bugbank/dossiers' / (rid + '.json')
dossier = json.loads(dossier_path.read_text(encoding='utf-8'))
cert_path = root / 'bugbank/certificates' / (rid + '.lean')
cert_text = cert_path.read_text(encoding='utf-8')
cert_sha = hashlib.sha256(cert_path.read_bytes()).hexdigest()
assert cert_sha == rec['current_scientific_bindings']['certificate_sha256'], 'certificate hash differs from the membership binding'

def mask(t):
    return EMAIL.sub('[contact omitted in display]', t)

out = {
    'source': {'commit': None, 'label': 'release:' + rid, 'caption': 'Built from bugbank/core/membership.json, bugbank/sources/%s.json, bugbank/dossiers/%s.json and bugbank/certificates/%s.lean of the released evidence.' % (rid, rid, rid)},
    'record_id': rid,
    'membership': {
        'eligible': rec['eligible'], 'eligibility_reasons': rec.get('eligibility_reasons'), 'continuity': rec['continuity'],
        'original_primary191': rec.get('original_primary191'), 'current_gold': rec.get('current_gold'),
        'review_evidence': rec.get('review_evidence'), 'bindings': rec['current_scientific_bindings'],
        'in_primary_100': rid in membership['benchmark_clean_primary191_record_ids'],
        'in_scorable_131': rid in membership['benchmark_clean_all255_record_ids'],
    },
    'source_lines': [{'label': str(l[0]), 'text': mask(l[1])} for l in lines],
    'n_nonblank_text': src.get('n_nonblank_text'),
    'gold': json.loads(src['gold']) if isinstance(src.get('gold'), str) else src.get('gold'),
    'dossier_fields': {k: (mask(v) if isinstance(v, str) else v) for k, v in dossier.items() if k in ('problem', 'claim_quote', 'flaw', 'witness', 'explanation', 'selected_declarations', 'evidence_tier', 'human_approval_of_current_artifact', 'source_correspondence')},
    'certificate': {'path': 'bugbank/certificates/%s.lean' % rid, 'sha256': cert_sha, 'text': mask(cert_text)},
    'note': 'The dossier JSON keeps the historical automated-export fields (evidence_tier, human_approval_of_current_artifact); the current human-review verdict is the membership record above, joined by record id.'
}
js = json.dumps(out, ensure_ascii=False, indent=1)
(root / 'docs/data/example_record.json').write_bytes((js + '\n').encode('utf-8'))
(root / 'docs/data/example_record.js').write_text('window.COPEER_DATA = window.COPEER_DATA || {};\nwindow.COPEER_DATA["example_record"] = %s;\n' % js, encoding='utf-8')
print('example record written: %d source lines, gold %s, eligible %s, certificate %d bytes' % (len(lines), out['gold'], rec['eligible'], len(cert_text)))
