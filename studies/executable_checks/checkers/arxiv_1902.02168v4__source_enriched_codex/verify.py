"""For the stated values a=222 and b=224, the difference b-a equals 12."""

import json

record_id = "arxiv_1902.02168v4__source_enriched_codex"
a = 222
b = 224
asserted_difference = 12
computed_difference = b - a

if computed_difference == 2 and computed_difference != asserted_difference:
    verdict = "CONFIRMED"
    notes = (
        "Independent exact integer recomputation gives 224 - 222 = 2, not 12, "
        "so the concrete witness genuinely refutes the claim. The refuted "
        "statement is plainly an arithmetic typo."
    )
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = (
        "Independent exact integer recomputation did not validate the reported "
        "witness. The refuted statement appears to be plainly an arithmetic typo."
    )

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
