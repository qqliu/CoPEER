"""For an odd prime p and d_1>2 with p-1=floor((p-1)/d_1)d_1+s_1, if floor((p-1)/d_1)+s_1 >= d_1-1, then every allowed binomial X^{d_1}+bX has theta-adic exponential-sum valuation floor((p-1)/d_1)+s_1."""

import json


def is_prime(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


def main():
    antecedent_cases = []
    for p in range(3, 200):
        if not is_prime(p) or p % 2 == 0:
            continue
        for d_1 in range(3, 200):
            q = (p - 1) // d_1
            s_1 = (p - 1) - q * d_1
            if q + s_1 >= d_1 - 1:
                antecedent_cases.append((p, d_1, q, s_1))

    for p, d_1, q, s_1 in antecedent_cases:
        assert p % 2 == 1 and is_prime(p)
        assert d_1 > 2
        assert p - 1 == q * d_1 + s_1
        assert q == (p - 1) // d_1
        assert q + s_1 >= d_1 - 1

    result = {
        "record_id": "arxiv_1401.4373v3__source_enriched_codex",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No witness is asserted: the supplied data do not define “allowed”, the exponential sum S, theta, or the valuation nu_theta, so the claimed conclusion cannot be evaluated.",
        "refutation_explanation": "The arithmetic antecedent can be checked exactly, but the supplied quote provides no exact predicate for whether a binomial is allowed or whether its theta-adic exponential-sum valuation equals the stated integer. Declaring a counterexample would therefore require inventing definitions absent from the permitted data.",
        "search_space": "Exhaustively swept every pair (p,d_1) in {3,...,199}^2 for which p is an odd prime and d_1>2; for each pair set q=(p-1)//d_1 and s_1=(p-1)-q*d_1, and retained exactly those satisfying q+s_1>=d_1-1. No b-space or valuation test is defined by the supplied quote."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
