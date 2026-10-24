r"""For 2.226<F≤2.26 and B=-24.116548F+54.692663, the displayed quadratic surrogate is at most 102.618907F^2-473.377198F-509.223573."""

import json
from fractions import Fraction

record = "arxiv_1503.00631v2__source_enriched_codex"
confirmed_notes = ("Exact rational recomputation confirms F=9/4 is admissible, "
                   "B=43043/100000, the surrogate is "
                   "-1127237140734619/2000000000000000, and the asserted bound "
                   "is -16877024829/16000000. The surrogate is therefore greater "
                   "than the bound. The enormous discrepancy indicates that the "
                   "refuted display is plainly a coefficient-sign typo, not a "
                   "subtle boundary failure.")
invalid_notes = ("Independent exact arithmetic did not reproduce every reported "
                 "witness value, so the witness is invalid. The alleged typo is "
                 "therefore not established.")

f = Fraction(9, 4)
b = Fraction(-24116548, 1000000) * f + Fraction(54692663, 1000000)

surrogate = (
    Fraction(246345, 1000000) * b * b
    + (Fraction(18810319, 1000000) * f
       - Fraction(42033351, 1000000)) * b
    + Fraction(202972148, 1000000) * f * f
    - Fraction(924926294, 1000000) * f
    + Fraction(1052803636, 1000000)
)
bound = (
    Fraction(102618907, 1000000) * f * f
    - Fraction(473377198, 1000000) * f
    - Fraction(509223573, 1000000)
)

valid = (
    Fraction(2226, 1000) < f
    and f <= Fraction(226, 100)
    and b == Fraction(43043, 100000)
    and surrogate == Fraction(-1127237140734619, 2000000000000000)
    and bound == Fraction(-16877024829, 16000000)
    and surrogate > bound
)

result = {
    "record_id": record,
    "verdict": "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if valid else invalid_notes,
}
print(json.dumps(result, separators=(",", ":")))
