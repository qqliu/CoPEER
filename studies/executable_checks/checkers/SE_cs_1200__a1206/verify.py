r"""consider the assignment $A[A[0]-1] := A[0]$ under the precondition $A[0] = 2 \wedge A[1] = 3$: you cannot make a simple substitution to obtain the correct postcondition $A[0] = 1 \wedge A[1] = 1$"""

import json

record_id = "SE_cs_1200__a1206"
notes = "Exact pre-state evaluation gives index 1 and value 2, so [2, 3] becomes [2, 2], which falsifies the stated postcondition. The refuted numerical postcondition is plainly a typo or transcription error; the broader warning about naive array substitution may still be substantive."

before = [2, 3]
assert before[0] == 2 and before[1] == 3

write_index = before[0] - 1
write_value = before[0]
assert 0 <= write_index < len(before)

after = list(before)
after[write_index] = write_value

assert write_index == 1
assert write_value == 2
assert after == [2, 2]
assert not (after[0] == 1 and after[1] == 1)

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
