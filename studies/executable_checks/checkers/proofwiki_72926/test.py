r"""The proof's key step claims that the cited result 'Index of Intersection of Subgroups' ([G : H \cap K] \le [G : H][G : K], valid for subgroups H, K of G) may be applied with G replaced by H, yielding [H : H \cap K] \le [H : H][H : K]. This substitution requires K to be a subgroup of H, which is not a hypothesis of the problem; moreover, in the only case where it is legitimate (K \le H) the resulting inequality is vacuous and does not bound [H : H \cap K] by [G : K]."""

import json

RECORD_ID = "proofwiki_72926"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = (
    "No concrete witness was sought among groups because the supplied data "
    "specifies neither a finite group instance nor a finite bound."
)
REFUTATION_EXPLANATION = (
    "The finite program can exhaust the two syntactic cases K <= H. When false, "
    "the quoted theorem's subgroup prerequisite fails after replacing G by H; "
    "when true, H intersection K normalizes to K and [H:H] to 1, so the displayed "
    "inequality normalizes to [H:K] <= [H:K] and contains no [G:K] bound. This "
    "checks the stated case split only. Because the target also concerns theorem "
    "applicability and arbitrary groups, with no bounded class of groups supplied, "
    "it is not finitely refutable here."
)
SEARCH_SPACE = (
    "An exhaustive fixed-order sweep of the two Boolean cases (K <= H) = False, "
    "True; zero concrete groups and zero numerical index assignments, since the "
    "supplied data gives no finite bound for either."
)


def contains_symbol(term, symbol):
    if isinstance(term, tuple):
        return any(contains_symbol(part, symbol) for part in term)
    return term == symbol


def exhaustive_syntactic_search():
    counterexamples = []
    index_h_k = ("index", "H", "K")
    for k_is_subgroup_of_h in (False, True):
        if not k_is_subgroup_of_h:
            theorem_applicable_after_substitution = False
            contradicts_target = theorem_applicable_after_substitution
        else:
            normalized_inequality = ("le", index_h_k, index_h_k)
            is_tautological = normalized_inequality[1] == normalized_inequality[2]
            states_g_k_bound = contains_symbol(normalized_inequality, "G")
            contradicts_target = (not is_tautological) or states_g_k_bound
        if contradicts_target:
            counterexamples.append(k_is_subgroup_of_h)
    return tuple(counterexamples)


def main():
    syntactic_counterexamples = exhaustive_syntactic_search()
    if syntactic_counterexamples:
        raise RuntimeError("unexpected syntactic counterexample")
    payload = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
