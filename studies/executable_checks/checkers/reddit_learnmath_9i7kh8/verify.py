r"""Every injective function f: X -> Y has a left inverse l: Y -> X."""

import json


def all_functions(domain, codomain):
    if len(domain) == 0:
        yield ()
        return
    for image in codomain:
        for remainder in all_functions(domain[1:], codomain):
            yield (image,) + remainder


def is_function(domain, codomain, values):
    return len(values) == len(domain) and all(value in codomain for value in values)


def is_injective(values):
    return all(
        i == j or values[i] != values[j]
        for i in range(len(values))
        for j in range(len(values))
    )


def compose_is_identity(x_set, y_set, f_values, left_values):
    for position, x in enumerate(x_set):
        y = f_values[position]
        y_position = y_set.index(y)
        if left_values[y_position] != x:
            return False
    return True


def main():
    x_set = ()
    y_set = (0,)
    f_values = ()

    valid_injection = (
        is_function(x_set, y_set, f_values)
        and is_injective(f_values)
    )
    candidates = tuple(all_functions(y_set, x_set))
    has_left_inverse = any(
        compose_is_identity(x_set, y_set, f_values, candidate)
        for candidate in candidates
    )
    counterexample_verified = valid_injection and not has_left_inverse

    if counterexample_verified:
        verdict = "CONFIRMED"
        notes = "Exact recomputation confirms the substantive empty-domain counterexample; this is a missing nonemptiness hypothesis, not plainly a typo."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "Exact recomputation did not validate the reported witness; the statement would not be refuted by it."

    print(json.dumps({
        "record_id": "reddit_learnmath_9i7kh8",
        "verdict": verdict,
        "notes": notes
    }))


if __name__ == "__main__":
    main()
