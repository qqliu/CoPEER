r"""The displayed identity claims that the pointwise maximum f ∨ g equals (f + g - |f - g|)/2."""

import json

record_id = "proofwiki_123746__codex_expansion"
f_on_singleton = (0,)
g_on_singleton = (1,)
f_value = f_on_singleton[0]
g_value = g_on_singleton[0]

left_side = f_value if f_value >= g_value else g_value
absolute_difference = abs(f_value - g_value)
right_numerator = f_value + g_value - absolute_difference
right_denominator = 2
identity_fails = left_side * right_denominator != right_numerator

if identity_fails:
    verdict = "CONFIRMED"
    notes = "Exact recomputation on the singleton witness gives max(0, 1) = 1 and (0 + 1 - |0 - 1|)/2 = 0, so the displayed identity genuinely fails. The refuted statement is plainly a sign typo: using +|f-g| gives the maximum, while the displayed minus sign gives the minimum."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The exact singleton recomputation does not refute the identity; the proposed witness is invalid. The displayed statement nevertheless resembles a plainly mistyped sign in the standard maximum formula."

result = {"record_id": record_id, "verdict": verdict, "notes": notes}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
