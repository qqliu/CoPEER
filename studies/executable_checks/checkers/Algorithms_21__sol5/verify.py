#!/usr/bin/env python3
"""Base case (n = 1): G1 has no edges, R(1) = 0 = 21 −1"""

import json

record_id = "Algorithms_21__sol5"
notes = ("Exact integer recomputation confirms the witness: as written, "
         "21 − 1 = 20, and under the reported intended superscript reading, "
         "2^1 − 1 = 1; neither equals the asserted 0. The refuted statement "
         "is plainly an arithmetic/formatting typo, not a substantive "
         "counterexample to an otherwise defined result.")

asserted_value = 0
literal_value = 21 - 1
superscript_value = 2 ** 1 - 1
verified = (literal_value != asserted_value and
            superscript_value != asserted_value)
verdict = "CONFIRMED" if verified else "REFUTED_WITNESS_INVALID"

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
