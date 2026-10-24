r"""while if $m$ is even then $-\varphi^{m+2}$ or $-\varphi^{m-2}$ is $1 \bmod p^2$."""

import json
import itertools

RECORD_ID = "mse_1365104__ans1369680"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No witness can be stated from the supplied data."
REFUTATION_EXPLANATION = (
    "The claim leaves \\varphi undefined and gives no domains or quantifiers "
    "for m and p, so its instances and truth conditions cannot be determined "
    "without inventing absent definitions."
)
SEARCH_SPACE = (
    "Exactly the empty Cartesian product of definitions of \\varphi, domains "
    "for m, and domains for p supplied by the quote: 0 admissible semantic "
    "instances were swept."
)

phi_definitions_supplied = ()
m_domains_supplied = ()
p_domains_supplied = ()
checked = 0
for _instance in itertools.product(
    phi_definitions_supplied, m_domains_supplied, p_domains_supplied
):
    checked += 1
assert checked == 0

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))
