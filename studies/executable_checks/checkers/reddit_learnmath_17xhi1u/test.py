"""The stated assumptions imply x_n < 4 for every natural n."""

import json


def search():
    x1 = 1
    witness = None
    for x2 in range(5):
        initial_condition_holds = x1 == 1
        recurrence_obligations_through_n2_hold = True
        if initial_condition_holds and recurrence_obligations_through_n2_hold and not (x2 < 4):
            witness = x2
            break

    if witness != 4:
        raise AssertionError("deterministic bounded search did not find the expected witness")

    return {
        "record_id": "reddit_learnmath_17xhi1u",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take x_1=1 and x_2=4, and for every integer n>=3 define x_n=sqrt(3*x_{n-1}+1).",
        "refutation_explanation": "The recurrence is required only for n>2, so it imposes no condition on x_2. The displayed sequence satisfies x_1=1 and can be continued recursively for every n>=3, but at the natural index n=2 it has x_2=4, making x_2<4 false.",
        "search_space": "All integer choices x_2 in {0, 1, 2, 3, 4}, tested in increasing order, with x_1 fixed at 1; there are no recurrence obligations at indices at most 2 because the recurrence starts at n=3."
    }


print(json.dumps(search(), separators=(",", ":")))
