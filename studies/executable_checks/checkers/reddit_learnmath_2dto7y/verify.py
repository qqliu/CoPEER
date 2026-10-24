r"""The logarithmic argument proves the power rule for every real exponent a at every non-negative real x."""

import json

record_id = "reddit_learnmath_2dto7y"
reported_exponent = 1
reported_base = 0

exponent_is_real = isinstance(reported_exponent, int)
base_is_nonnegative = reported_base >= 0
real_natural_log_is_defined = reported_base > 0
witness_is_valid = (
    exponent_is_real
    and base_is_nonnegative
    and not real_natural_log_is_defined
)

if witness_is_valid:
    verdict = "CONFIRMED"
    notes = (
        "At the exact witness a=1, x=0, the base is non-negative and the exponent "
        "is real, but the real natural logarithm is defined only for positive inputs. "
        "Therefore a derivation that applies ln(x) cannot cover x=0. This is a "
        "substantive domain error, not a typo."
    )
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = (
        "The proposed witness does not establish the claimed logarithmic domain "
        "failure. This would be a substantive issue, not a typo."
    )

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
