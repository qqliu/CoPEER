r"""Defined $h: \{0\} \to \{1\}$ as $h(1)=0$.
It follows that $h(P) =  $\{1^p : p \text{ is a primes}\}$ and therefore is irregular."""

import json


def main():
    domain = frozenset((0,))
    codomain = frozenset((1,))

    candidates = tuple({0: output} for output in codomain)
    valid_typed_functions = tuple(
        function
        for function in candidates
        if frozenset(function) == domain
        and frozenset(function.values()).issubset(codomain)
    )

    established = (
        len(valid_typed_functions) == 1
        and valid_typed_functions[0] == {0: 1}
        and 1 not in valid_typed_functions[0]
        and 0 not in codomain
        and not any(
            1 in function and function[1] == 0
            for function in valid_typed_functions
        )
    )
    if not established:
        raise RuntimeError("independent exact verification failed")

    result = {
        "record_id": "SE_cs_42947__q",
        "verdict": "CONFIRMED",
        "notes": "The refuted statement is plainly a typo: the argument and value are reversed relative to the stated domain and codomain. Read literally, no function h:{0}->{1} can satisfy h(1)=0, so the subsequent conclusion does not follow."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
