"""The connected classification theorem can be applied directly to the arbitrary compact one-manifold M introduced in the proof."""

import itertools
import json


def main():
    profiles = list(itertools.product((False, True), repeat=3))
    gaps = []
    for compact, connected, one_dimensional in profiles:
        stated_for_m = compact and one_dimensional
        theorem_applicable = compact and connected and one_dimensional
        if stated_for_m and not theorem_applicable:
            gaps.append((compact, connected, one_dimensional))

    assert len(profiles) == 8
    assert gaps == [(True, False, True)]

    result = {
        "record_id": "proofwiki_100001__codex_expansion",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete manifold witness is supplied or constructible from the quote; the sweep finds only the formal profile compact=True, connected=False, one_dimensional=True.",
        "refutation_explanation": "The quoted theorem requires connectedness, while the target claim states only that M is an arbitrary compact one-manifold. The Boolean sweep exposes this missing hypothesis, but the quote supplies no fact deciding whether M is connected and no realizable disconnected compact one-manifold, so it cannot certify a mathematical counterexample.",
        "search_space": "All 2^3 = 8 Boolean valuations of (compact, connected, one_dimensional), in itertools.product((False, True), repeat=3) order; applicability was tested by the exact conjunction of the three quoted hypotheses."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
