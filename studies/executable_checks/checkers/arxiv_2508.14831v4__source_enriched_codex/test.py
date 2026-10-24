r"""Under midpoint recursion and DFS, the potential \(\Phi_{\mathrm{path}}=\sum_i\lceil\log_2(1+\lambda_i)\rceil\) over the active intervals on the DFS stack is \(O(\log T)\) at all times."""

import json


def main():
    evaluated = 0
    checksum = 0
    for T in range(1, 4097):
        max_depth = (T - 1).bit_length()
        potential = 0
        for depth in range(max_depth + 1):
            ell = (T + (1 << depth) - 1) >> depth
            term = ell.bit_length()
            potential += term
            evaluated += 1
        checksum += potential

    if evaluated != 49153 or checksum <= 0:
        raise AssertionError("bounded sweep did not complete")

    result = {
        "record_id": "arxiv_2508.14831v4__source_enriched_codex",
        "outcome": "CLAIM_NOT_FINITELY_REFUTABLE",
        "witness_description": "No finite witness can violate an unspecified asymptotic O(log T) bound, because its multiplicative constant and threshold are not fixed.",
        "refutation_explanation": "The bounded sweep exactly evaluates the displayed upper-envelope expression, but any finite collection of values is compatible with some choice of Big-O constant and threshold. Therefore a bounded exhaustive search cannot refute or certify this asymptotic claim.",
        "search_space": "All integers T from 1 through 4096 inclusive and every depth d from 0 through ceil(log2 T), totaling 49,153 (T,d) evaluations, with ell(d)=ceil(T/2^d) and ceil(log2(1+ell(d))) computed exactly."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
