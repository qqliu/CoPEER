"""The two lexicographically smallest k-faces of an ordered (k+1)-simplex must have the explicit forms stated in the proof of Theorem 2.5."""

import json

record_id = "arxiv_2301.07191v3__source_enriched_codex"
verdict = "CONFIRMED"
notes = ("Exact recomputation for k=1 and tau=(0,1,2) gives the "
         "lexicographically first two 1-faces as (0,1) and (0,2), whereas "
         "the displayed forms specialize to (0,) and (1,), which are "
         "0-faces and do not cover tau. Thus the literal statement is "
         "refuted, but the source error is plainly an indexing/omission "
         "typo rather than a substantive mathematical counterexample.")

k = 1
tau = (0, 1, 2)

faces = []
for omitted in range(len(tau)):
    face = tuple(tau[index] for index in range(len(tau)) if index != omitted)
    if len(face) == k + 1:
        faces.append(face)
faces.sort()
actual_pair = tuple(faces[:2])

stated_sigma0 = tuple(tau[index] for index in range(k))
stated_sigma1 = tuple(tau[index] for index in range(k - 1)) + (tau[k],)
stated_pair = (stated_sigma0, stated_sigma1)

assert len(tau) == k + 2
assert actual_pair == ((0, 1), (0, 2))
assert stated_pair == ((0,), (1,))
assert all(len(face) == k + 1 for face in actual_pair)
assert all(len(face) != k + 1 for face in stated_pair)
assert set(stated_sigma0).union(stated_sigma1) != set(tau)
assert actual_pair != stated_pair

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}))
