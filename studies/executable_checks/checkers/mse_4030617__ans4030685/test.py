"""$$2^{n + 2} | p - 1$$"""

import json

CERTIFIED_ASSIGNMENTS = ()

for assignment in CERTIFIED_ASSIGNMENTS:
    raise AssertionError("The quote unexpectedly supplied an assignment: " + repr(assignment))

result = {
    "record_id": "mse_4030617__ans4030685",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No witness is reported because the supplied quote gives no quantified domain, admissibility conditions, or concrete values for n and p.",
    "refutation_explanation": "The bare divisibility formula does not specify which assignments to n and p the claim covers. Testing assumed integer or prime ranges would invent information absent from the quote, so no candidate can be certified as a counterexample to the intended claim.",
    "search_space": "The exact finite space swept was the empty set of assignments certified as admissible by the supplied quote (0 assignments). This exhaustive empty sweep is inconclusive, not evidence that the divisibility claim holds."
}

print(json.dumps(result, separators=(",", ":")))
