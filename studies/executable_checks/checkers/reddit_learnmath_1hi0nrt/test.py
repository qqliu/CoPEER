"""For every n >= 2, F_n < F_{n+1} < 2F_n."""

import json

record_id = "reddit_learnmath_1hi0nrt"
fibonacci = [0, 1]
for index in range(2, 4):
    fibonacci.append(fibonacci[index - 1] + fibonacci[index - 2])

witnesses = []
for n in range(2, 3):
    if not (fibonacci[n] < fibonacci[n + 1] < 2 * fibonacci[n]):
        witnesses.append(n)

assert witnesses == [2]
assert fibonacci[2] == 1
assert fibonacci[3] == 2

result = {
    "record_id": record_id,
    "outcome": "WITNESS_FOUND",
    "witness_description": "Using the standard Fibonacci indexing F_0 = 0, F_1 = 1, the witness is n = 2: F_2 = 1 and F_3 = 2.",
    "refutation_explanation": "At n = 2, the claimed upper inequality F_3 < 2F_2 becomes 2 < 2, which is false because equality holds.",
    "search_space": "Exhaustively checked the singleton index set {2}, computing F_0 through F_3 exactly by F_{k+2} = F_{k+1} + F_k from F_0 = 0 and F_1 = 1."
}
print(json.dumps(result, separators=(",", ":")))
