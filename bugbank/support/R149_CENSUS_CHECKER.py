import json,time
from pathlib import Path
start=time.monotonic();summary=[]
for n in range(1,5):
 k=1<<n;subsets=[[b for b in range(k) if b&a==b] for a in range(k)];counts=violations=0;card=[bin(x).count('1') for x in range(k)]
 for fam in range(1,1<<k,2):
  members=[a for a in range(k) if fam>>a&1]
  if any(any(not(fam>>b&1) for b in subsets[a]) for a in members):continue
  if any(not any((b&~a)>>e&1 and (fam>>(a|(1<<e)))&1 for e in range(n)) for a in members for b in members if card[a]<card[b]):continue
  counts+=1
  rho=[max(card[b] for b in members if b&a==b) for a in range(k)]
  if any(2*rho[a|(1<<e)]>rho[a]+rho[1<<e] for a in range(k) for e in range(n) if not(a>>e&1)):violations+=1
 summary.append({'ground_set_size':n,'matroid_rank_functions':counts,'admit_printed_inequality_violation_with_y_outside_X':violations})
result={'record':'proofwiki_132447','purpose':'independent recheck of existing documented bounded-domain counts; no new record or witness proposed','domain':'all independence families on labeled ground sets of size1..4; hereditary, contains empty, augmentation checked','counts':summary,'totals':{'matroids':sum(x['matroid_rank_functions'] for x in summary),'violations':sum(x['admit_printed_inequality_violation_with_y_outside_X'] for x in summary)},'elapsed_seconds':round(time.monotonic()-start,2)}
assert result['totals']=={'matroids':91,'violations':87},result
p=Path('qedbench_certificate_availability_triage/validation/human_review_20260915/verified_census/checks/proofwiki_132447_count_check.json');p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
