r"""Since $x_{i}$ is the number of members of $j$ that satisfy $i<j$ and are before $i$ in a list based on $\text{MF}$ before the operation $s_{l}$ follows $\Phi\left(D_{l-1}\right)=x_{l}$."""

import json

RECORD_ID = "SE_cs_153448__q"
TARGET_CLAIM = r"""Since $x_{i}$ is the number of members of $j$ that satisfy $i<j$ and are before $i$ in a list based on $\text{MF}$ before the operation $s_{l}$ follows $\Phi\left(D_{l-1}\right)=x_{l}$."""
SOURCE_QUOTE = r"""Since $x_{i}$ is the number of members of $j$ that satisfy $i<j$ and are before $i$ in a list based on $\text{MF}$ before the operation $s_{l}$ follows $\Phi\left(D_{l-1}\right)=x_{l}$."""
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness can be named from the supplied data: the quote instantiates no indices, list, MF ordering, operation, diagram, or value of Phi."
REFUTATION_EXPLANATION = "The source quote merely repeats the target claim. It does not define the index domain, what the members of j are, the MF-based ordering, s_l, D_{l-1}, or Phi sufficiently to evaluate Phi(D_{l-1}) = x_l. Therefore the absence of a witness in the finite sweep is inconclusive, not evidence that the claim holds."
SEARCH_SPACE = "Exactly 1 supplied claim/quote pair was audited and exactly 0 concrete mathematical structures supplied by that pair were searched; no additional structures were invented."


def main():
    supplied_pairs = ((TARGET_CLAIM, SOURCE_QUOTE),)
    concrete_structures = ()

    audited_pairs = 0
    for claim, quote in supplied_pairs:
        audited_pairs += 1
        assert claim == quote

    searched_structures = 0
    witness = None
    for structure in concrete_structures:
        searched_structures += 1
        witness = structure
        break

    assert audited_pairs == 1
    assert searched_structures == 0
    assert witness is None

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
