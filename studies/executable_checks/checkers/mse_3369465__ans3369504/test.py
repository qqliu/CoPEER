r"""Indeed, let $m\neq n \in N(x)$. If we had $f_{x,y}(n) = f_{x,y}(m)$, then $N(n)\cap N(m)$ would have at least two distinct elements, namely $x$ and $f_{x,y}(n)$, a contradiction to our hypothesis!"""

import json
from itertools import product

RECORD_ID = "mse_3369465__ans3369504"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certified counterexample: the quote omits the hypothesis and the "
    "definitions/axioms governing N and f_{x,y}."
)
REFUTATION_EXPLANATION = (
    "The finite sweep finds surface-structure failures of the displayed inference, "
    "but none can be called a counterexample to the quoted claim because the "
    "referenced hypothesis is not supplied and may exclude them; the quote also "
    "does not specify the properties of N or f_{x,y}."
)
SEARCH_SPACE = (
    "Exhaustively swept U={0,1,2}: all 2^9=512 mappings N:U→P(U), all "
    "3^3=27 unary maps used as the selected f_{x,y}, and all 3^4=81 ordered "
    "choices (x,y,m,n), for 1,119,744 structure/tuple combinations, testing "
    "only the explicitly displayed antecedent and conclusion. This bounded "
    "diagnostic is inconclusive about the unstated hypothesis."
)


def main():
    universe = range(3)
    examined = 0
    surface_failure_found = False

    # Nine bits enumerate every mapping N: U -> P(U).
    for neighborhood_code in range(1 << 9):
        neighborhoods = tuple(
            (neighborhood_code >> (3 * vertex)) & 7
            for vertex in universe
        )
        for function_values in product(universe, repeat=3):
            for x in universe:
                for y in universe:
                    for m in universe:
                        for n in universe:
                            examined += 1
                            antecedent = (
                                m != n
                                and ((neighborhoods[x] >> m) & 1) == 1
                                and ((neighborhoods[x] >> n) & 1) == 1
                                and function_values[n] == function_values[m]
                            )
                            if antecedent:
                                z = function_values[n]
                                common = neighborhoods[n] & neighborhoods[m]
                                displayed_conclusion = (
                                    x != z
                                    and ((common >> x) & 1) == 1
                                    and ((common >> z) & 1) == 1
                                )
                                if not displayed_conclusion:
                                    surface_failure_found = True

    if examined != 512 * 27 * 81:
        raise RuntimeError("finite sweep was incomplete")
    if not surface_failure_found:
        raise RuntimeError("diagnostic sweep did not exercise a surface failure")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
