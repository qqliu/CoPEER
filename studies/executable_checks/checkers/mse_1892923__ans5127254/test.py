r"""Let $f, g \in \mathbb{Z}[x]$ be s.t. $g(n)|f(n)$ for every $n \in \mathbb{N}$. Then, $f = rg$ for some $r \in \mathbb{Z}$."""

import json


def evaluate(coefficients, n):
    value = 0
    power = 1
    for coefficient in coefficients:
        value += coefficient * power
        power *= n
    return value


def divisible_for_all_integers_by_constant(coefficients, divisor):
    modulus = abs(divisor)
    return all(evaluate(coefficients, residue) % modulus == 0
               for residue in range(modulus))


def is_integer_scalar_multiple_of_constant(coefficients, divisor):
    return (all(coefficient == 0 for coefficient in coefficients[1:])
            and coefficients[0] % divisor == 0)


def main():
    witnesses = []
    divisor = 2

    for b in range(-2, 3):
        coefficients = (0, b, 1)
        premise = divisible_for_all_integers_by_constant(coefficients, divisor)
        conclusion = is_integer_scalar_multiple_of_constant(coefficients, divisor)
        if premise and not conclusion:
            witnesses.append((b, coefficients, divisor))

    selected = next(item for item in witnesses if item[0] == -1)
    assert selected == (-1, (0, -1, 1), 2)

    result = {
        "record_id": "mse_1892923__ans5127254",
        "outcome": "WITNESS_FOUND",
        "witness_description": "f(x)=x^2-x and g(x)=2. For every n in N, n(n-1) is even, so g(n)=2 divides f(n); but f is nonconstant, whereas rg=2r is constant for every integer r.",
        "refutation_explanation": "The exact residue checks f(0) mod 2 = 0 and f(1) mod 2 = 0 prove divisibility for every integer, hence every natural number, because polynomial evaluation respects congruence. The nonzero x^2 coefficient proves that no integer r can satisfy f=rg.",
        "search_space": "All five pairs g(x)=2 and f_b(x)=x^2+b*x for b in {-2,-1,0,1,2}; each universal divisibility condition was decided exactly by testing residues 0 and 1 modulo 2."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
