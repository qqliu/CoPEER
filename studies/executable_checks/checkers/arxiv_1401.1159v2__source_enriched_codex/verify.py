r"""The product of any two unimodal polynomials is unimodal."""

import json

RECORD_ID = "arxiv_1401.1159v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = "Exact integer convolution gives (1, 8, 26, 62, 113, 110, 121). Both factors have strictly increasing positive coefficients and are unimodal, while the product falls from 113 to 110 and then rises to 121, so it is not unimodal. The refuted statement is substantive, not plainly a typo."


def unimodal(sequence):
    descending = False
    for previous, current in zip(sequence, sequence[1:]):
        if current < previous:
            descending = True
        elif current > previous and descending:
            return False
    return True


def convolution(first, second):
    result = []
    for degree in range(len(first) + len(second) - 1):
        coefficient = 0
        for first_degree in range(len(first)):
            second_degree = degree - first_degree
            if 0 <= second_degree < len(second):
                coefficient += first[first_degree] * second[second_degree]
        result.append(coefficient)
    return tuple(result)


def main():
    first = (1, 4, 5, 11)
    second = tuple(first)
    calculated = convolution(first, second)
    expected = (1, 8, 26, 62, 113, 110, 121)
    established = (
        all(value > 0 for value in first)
        and all(first[index] < first[index + 1] for index in range(len(first) - 1))
        and unimodal(first)
        and unimodal(second)
        and calculated == expected
        and not unimodal(calculated)
        and calculated[4] > calculated[5] < calculated[6]
    )
    if not established:
        raise AssertionError("independent exact verification failed")
    print(json.dumps({"record_id": RECORD_ID, "verdict": VERDICT, "notes": NOTES}, separators=(",", ":")))


if __name__ == "__main__":
    main()
