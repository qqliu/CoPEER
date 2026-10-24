r'''For n₁ > 1 with largest prime factor p, the largest prime factor of φ(n₁) is strictly less than p.'''

import json
from math import gcd


def prime_factors(number):
    factors = []
    candidate = 2
    residue = number
    while candidate * candidate <= residue:
        if residue % candidate == 0:
            factors.append(candidate)
            while residue % candidate == 0:
                residue //= candidate
        candidate += 1
    if residue > 1:
        factors.append(residue)
    return factors


def totient_by_definition(number):
    count = 0
    for candidate in range(1, number + 1):
        if gcd(candidate, number) == 1:
            count += 1
    return count


witness = 4
witness_factors = prime_factors(witness)
phi_value = totient_by_definition(witness)
phi_factors = prime_factors(phi_value)
valid = (
    witness > 1
    and witness_factors
    and phi_factors
    and witness_factors[-1] == 2
    and phi_value == 2
    and phi_factors[-1] == 2
    and not (phi_factors[-1] < witness_factors[-1])
)

if valid:
    verdict = "CONFIRMED"
    notes = "Substantive, not plainly a typo: for n₁ = 4, exact recomputation gives p = 2 and φ(4) = 2, whose largest prime factor is also 2, so the claimed strict inequality fails."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Substantive, not plainly a typo: the supplied witness did not survive exact independent recomputation."

print(json.dumps({
    "record_id": "proofwiki_130200__codex_expansion",
    "verdict": verdict,
    "notes": notes,
}, ensure_ascii=False, separators=(",", ":")))
