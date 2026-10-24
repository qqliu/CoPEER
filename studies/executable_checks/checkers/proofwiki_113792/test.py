r'''In the verification that the constructed rank candidate satisfies axiom (R2), the proof asserts for ARBITRARY X = {x_1,...,x_q} ⊆ S and ARBITRARY y ∈ S (no assumption y ∉ X) that rho(X ∪ {y}) − rho(X) = t(x_1,...,x_q,y) − t(x_1,...,x_q), and hence equals theta(x_1,...,x_q,y)_{q+1}, which is 1 whenever no C ∈ 𝒞 satisfies y ∈ C ⊆ {x_1,...,x_q,y}. The case y ∈ X is never excluded, and in that case the asserted equality (and the derived value) is false: it yields rho(X ∪ {y}) = rho(X) + 1 for X ∪ {y} = X. (Note the author does exclude this case in Lemma 2, stating "Let X ⊆ S and y ∈ S \ X", showing the omission in the (R2) argument is a real case gap, not a notational convention.)'''

import json


def powerset(items):
    return tuple(
        frozenset(items[index] for index in range(len(items)) if mask & (1 << index))
        for mask in range(1 << len(items))
    )


ground = (0,)
subsets = powerset(ground)
nonempty_x_sets = tuple(candidate for candidate in subsets if candidate)
families = tuple(
    tuple(subsets[index] for index in range(len(subsets)) if mask & (1 << index))
    for mask in range(1 << len(subsets))
)

witnesses = []
checked = 0
for x_set in nonempty_x_sets:
    for y in ground:
        for family in families:
            checked += 1
            union = x_set | frozenset((y,))
            no_relevant_c = not any(y in c_set and c_set <= union for c_set in family)
            actual_increment = 0 if union == x_set else None
            asserted_increment = 1 if no_relevant_c else None
            if y in x_set and actual_increment == 0 and asserted_increment == 1:
                witnesses.append((x_set, y, family))

if checked != 4 or not witnesses:
    raise RuntimeError("bounded exhaustive search failed")

result = {
    "record_id": "proofwiki_113792",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take S={0}, X={0}, y=0, and 𝒞=∅. Then y∈X and no C∈𝒞 satisfies y∈C⊆X∪{y}.",
    "refutation_explanation": "Since X∪{y}=X, rho(X∪{y})−rho(X)=0 for every set function rho. The asserted case rule instead gives 1, so it would require rho(X)=rho(X)+1.",
    "search_space": "All 4 configurations with S={0}, nonempty X⊆S, y∈S, and 𝒞 ranging in mask order over all 4 families of subsets of S; every configuration was checked."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
