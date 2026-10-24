r'''The proof claims that because S = {m, m+1, ..., m+n-1} contains a multiple of j for each j = 1..n, the product of the elements of S can be regrouped as (k_1 * 1)(k_2 * 2)...(k_n * n), i.e. the n elements of S can be matched one-to-one with the factors 1, 2, ..., n so that each element is a multiple of its assigned factor. This simultaneous/distinct-representative regrouping does not follow from the cited lemma and is false in general.'''

import json

record_id = "proofwiki_36906"
n = 3
m = 5
elements = tuple(range(m, m + n))

eligible = {}
premise = True
for factor in range(1, n + 1):
    choices = tuple(value for value in elements if value % factor == 0)
    eligible[factor] = choices
    if len(choices) == 0:
        premise = False

used = [False for _ in elements]

def find_bijection(factor):
    if factor == n + 1:
        return True
    for index in range(len(elements)):
        if not used[index] and elements[index] % factor == 0:
            used[index] = True
            if find_bijection(factor + 1):
                return True
            used[index] = False
    return False

matching_exists = find_bijection(1)
confirmed = (
    elements == (5, 6, 7)
    and premise
    and eligible[1] == (5, 6, 7)
    and eligible[2] == (6,)
    and eligible[3] == (6,)
    and not matching_exists
)

if confirmed:
    verdict = "CONFIRMED"
    notes = "Independent exact recomputation confirms the witness: S = {5, 6, 7} satisfies the separate divisibility premise, but no bijection to factors 1, 2, 3 respects divisibility because factors 2 and 3 both require the sole eligible element 6. This is a substantive logical gap, not a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Independent exact recomputation does not validate the reported witness. The alleged issue would be substantive rather than a typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
