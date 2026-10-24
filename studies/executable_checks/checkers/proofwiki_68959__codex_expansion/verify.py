r'''The substitution of the integer summation index by α+k is a valid reindexing of a sum over ℤ for arbitrary complex α.'''

import json
from fractions import Fraction

record_id = "proofwiki_68959__codex_expansion"
alpha = (Fraction(1, 2), Fraction(0, 1))
k = 0
translated = (alpha[0] + k, alpha[1])
k_is_integer = isinstance(k, int) and not isinstance(k, bool)
translated_is_integer = translated[1] == Fraction(0, 1) and translated[0].denominator == 1
counterexample_holds = k_is_integer and not translated_is_integer

if counterexample_holds:
    verdict = "CONFIRMED"
    notes = "Exact Fraction arithmetic recomputes α = 1/2, k = 0, and α+k = 1/2; its denominator is 2, so the translation does not map ℤ into ℤ. The refuted statement is substantive as stated, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The exact witness computation did not refute the claim. The statement is substantive as stated, not plainly a typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
