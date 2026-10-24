r"""The asserted equality |max(f(s),g(s))| = |max(|f(s)|,|g(s)|)| is false in general."""

import json


def integer_max(first, second):
    if first >= second:
        return first
    return second


def magnitude(value):
    if value < 0:
        return -value
    return value


def main():
    f_at_s = -2
    g_at_s = -1
    left = magnitude(integer_max(f_at_s, g_at_s))
    right = magnitude(integer_max(magnitude(f_at_s), magnitude(g_at_s)))

    if left == 1 and right == 2 and left != right:
        verdict = "CONFIRMED"
        notes = "Exact integer recomputation gives 1 on the left and 2 on the right for f(s) = -2 and g(s) = -1, so the asserted equality genuinely fails. The refuted equality is substantive, not plainly a typo."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "Exact integer recomputation did not establish the reported counterexample. The purported refutation concerns a substantive statement, not plainly a typo."

    result = {
        "record_id": "proofwiki_123738__codex_expansion",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
