"""For every finite family of square-integrable one-dimensional martingale-difference sequences on a common discrete-time stochastic basis, there exists a martingale M with M_0=0 satisfying the displayed stochastic maximal inequality for every n≥1."""

from fractions import Fraction
from itertools import product
import json


SIGNS = (-1, 1)
COEFFICIENTS = tuple(product((-1, 0, 1), repeat=3))
KNOWN_WITNESS = ((1, 1, 1), (1, -1, -1))

WITNESS_DESCRIPTION = (
    "On Ω={(-1,-1),(-1,1),(1,-1),(1,1)} with the uniform law, let R and S "
    "be the coordinate signs, F_0 trivial, F_1=σ(R), and F_k=σ(R,S) for k≥2. "
    "Take ξ^1_1=R, ξ^1_2=S and ξ^2_1=R, ξ^2_2=-S "
    "(and ξ^i_k=0 for k≥3)."
)
REFUTATION_EXPLANATION = (
    "At n=1, the inequality requires M_1≥0 a.s.; since E[M_1]=M_0=0, this gives "
    "M_1=0 a.s. At n=2, each conditional energy term equals 1 while "
    "max{(R+S)^2,(R-S)^2}=4, so the inequality requires M_2≥2 a.s. But the "
    "martingale property gives E[M_2|F_1]=M_1=0, a contradiction."
)
SEARCH_SPACE = (
    "All 756 ordered families of size 1 or 2 on the uniform depth-2 binary tree "
    "whose increments have the form ξ^i_1=a_iR and ξ^i_2=b_{i,R}S with "
    "a_i,b_{i,-1},b_{i,1}∈{-1,0,1}, extended by ξ^i_k=0 for k≥3; feasibility "
    "through n=2 is decided exactly by backward martingale lower bounds."
)


def exact_mean(values):
    return Fraction(sum(values), len(values))


def lower_bounds_at_time_one(family):
    """Return the least possible M_1 at each R-node.

    A coefficient triple is (a, b_minus, b_plus), representing increments
    a*R and b_R*S.  At a time-one node, M_1 must dominate the time-one
    obstacle and the conditional mean of the two time-two obstacles.  These
    conditions are also sufficient because any excess conditional mean can
    be distributed among the two children.
    """
    energy_one = max(coefficient[0] ** 2 for coefficient in family)
    bounds = []

    for node_index, sign_one in enumerate(SIGNS):
        energy_two = max(
            coefficient[node_index + 1] ** 2 for coefficient in family
        )
        obstacle_one = (
            max((sign_one * coefficient[0]) ** 2 for coefficient in family)
            - energy_one
        )
        obstacle_two = []

        for sign_two in SIGNS:
            largest_square = max(
                (
                    sign_one * coefficient[0]
                    + sign_two * coefficient[node_index + 1]
                ) ** 2
                for coefficient in family
            )
            obstacle_two.append(largest_square - energy_one - energy_two)

        bounds.append(
            max(Fraction(obstacle_one, 1), exact_mean(obstacle_two))
        )

    return tuple(bounds)


def is_counterexample(family):
    # With M_0=0, feasible time-one values of conditional mean zero exist
    # exactly when the mean of their componentwise lower bounds is at most zero.
    return exact_mean(lower_bounds_at_time_one(family)) > 0


def main():
    tested = 0
    known_witness_verified = False

    for family_size in (1, 2):
        for family in product(COEFFICIENTS, repeat=family_size):
            tested += 1
            if is_counterexample(family) and family == KNOWN_WITNESS:
                known_witness_verified = True

    assert tested == 756
    assert known_witness_verified

    result = {
        "record_id": "arxiv_2004.13333v2__source_enriched_codex",
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
