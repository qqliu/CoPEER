r"""From a | mn, it follows that a divides both m and n and that a = mnq for some integer q."""

import json

REPORT = {
    "record_id": "reddit_learnmath_jid2cv",
    "verdict": "CONFIRMED",
    "notes": "Confirmed exactly at a = 2, m = 1, n = 4: 2 divides 4, but not 1, and divmod(2, 4) has nonzero remainder, so no integer q has 2 = 4q. The refuted statement is a substantive mathematical error, not a plain typo."
}

a = 2
m = 1
n = 4
mn = m * n

premise_quotient, premise_remainder = divmod(mn, a)
assert premise_remainder == 0
assert mn == a * premise_quotient

assert divmod(m, a)[1] != 0
assert divmod(n, a)[1] == 0

candidate_quotient, equation_remainder = divmod(a, mn)
assert equation_remainder != 0
assert a != mn * candidate_quotient

assert REPORT["record_id"] == "reddit_learnmath_jid2cv"
assert REPORT["verdict"] == "CONFIRMED"
assert "substantive mathematical error" in REPORT["notes"]

print(json.dumps(REPORT, separators=(",", ":")))
