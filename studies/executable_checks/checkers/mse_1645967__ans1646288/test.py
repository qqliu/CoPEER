r"""$\mathcal{G}$ is called a generator if $\sigma(\mathcal{G}) = \mathcal{A}$, this also means $\Omega \in \mathcal{G}$"""

import json

RECORD_ID = "mse_1645967__ans1646288"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take Ω = {0, 1}, A = P(Ω), and G = {{0}}. "
    "Then σ(G) = A but Ω is not an element of G."
)
REFUTATION_EXPLANATION = (
    "Closing G = {{0}} under complements and finite unions produces ∅, {0}, "
    "{1}, and {0, 1}, so σ(G) = P(Ω) = A. Nevertheless, Ω = {0, 1} "
    "is not in G, refuting the assertion that being a generator also means Ω ∈ G."
)
SEARCH_SPACE = (
    "All 16 families G ⊆ P({0, 1}) were enumerated in increasing 4-bit mask "
    "order, with A fixed to P({0, 1}); for each family, σ(G) was computed to "
    "closure under ∅, Ω, complements, and binary unions."
)

POINT_COUNT = 2
OMEGA_MASK = (1 << POINT_COUNT) - 1
POWER_SET = tuple(range(1 << POINT_COUNT))


def generated_sigma_algebra(family):
    closure = set(family)
    closure.add(0)
    closure.add(OMEGA_MASK)
    while True:
        previous_size = len(closure)
        current = tuple(sorted(closure))
        closure.update(OMEGA_MASK ^ subset for subset in current)
        current = tuple(sorted(closure))
        closure.update(left | right for left in current for right in current)
        if len(closure) == previous_size:
            return frozenset(closure)


violations = []
for family_mask in range(1 << len(POWER_SET)):
    family = tuple(
        subset for subset in POWER_SET if family_mask & (1 << subset)
    )
    sigma_family = generated_sigma_algebra(family)
    if sigma_family == frozenset(POWER_SET) and OMEGA_MASK not in family:
        violations.append((family_mask, family))

assert violations
assert violations[0] == (2, (1,))

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
