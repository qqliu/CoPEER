#!/usr/bin/env python3
"""Independent finite certificate for the supplied B3 Toda witness.

Run: python3 audit_b3_exact.py
Uses only standard-library exact integers and fractions; reads no data files.
Polynomials are tuples of Fraction coefficients in consecutive ascending powers
of q. Rational-function equality is checked by polynomial cross multiplication.
"""

from fractions import Fraction as F
from itertools import combinations, product
import hashlib
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def poly(values):
    out = [F(v) for v in values]
    while out and out[-1] == 0:
        out.pop()
    return tuple(out)


ZERO = ()
ONE = (F(1),)


def padd(a, b):
    return poly((a[i] if i < len(a) else 0)
                + (b[i] if i < len(b) else 0)
                for i in range(max(len(a), len(b))))


def pneg(a):
    return poly(-x for x in a)


def psub(a, b):
    return padd(a, pneg(b))


def pmul(a, b):
    if not a or not b:
        return ZERO
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return poly(out)


def ppow(a, exponent):
    require(isinstance(exponent, int) and exponent >= 0, 'polynomial exponent')
    out = ONE
    for _ in range(exponent):
        out = pmul(out, a)
    return out


def monomial(exponent):
    require(isinstance(exponent, int) and exponent >= 0, 'monomial exponent')
    return poly([0] * exponent + [1])


def pdivmod(a, b):
    require(bool(b), 'nonzero polynomial divisor')
    original = a
    quotient = [F(0)] * max(0, len(a) - len(b) + 1)
    remainder = a
    while remainder and len(remainder) >= len(b):
        shift = len(remainder) - len(b)
        factor = remainder[-1] / b[-1]
        quotient[shift] += factor
        remainder = psub(remainder, poly([0] * shift + [factor * x for x in b]))
    quotient = poly(quotient)
    require(padd(pmul(quotient, b), remainder) == original,
            'polynomial division reconstruction')
    require(not remainder or len(remainder) < len(b), 'remainder degree')
    return quotient, remainder


class RF:
    def __init__(self, numerator=ZERO, denominator=ONE):
        self.numerator = poly(numerator)
        self.denominator = poly(denominator)
        require(bool(self.denominator), 'nonzero rational-function denominator')

    def __add__(self, other):
        return RF(padd(pmul(self.numerator, other.denominator),
                       pmul(other.numerator, self.denominator)),
                  pmul(self.denominator, other.denominator))

    def __mul__(self, other):
        return RF(pmul(self.numerator, other.numerator),
                  pmul(self.denominator, other.denominator))

    def __truediv__(self, other):
        require(bool(other.numerator), 'nonzero rational-function divisor')
        return RF(pmul(self.numerator, other.denominator),
                  pmul(self.denominator, other.numerator))

    def __eq__(self, other):
        return (pmul(self.numerator, other.denominator)
                == pmul(other.numerator, self.denominator))

    def as_polynomial(self):
        quotient, remainder = pdivmod(self.numerator, self.denominator)
        require(remainder == ZERO, 'exact polynomiality')
        return quotient


def exact_integer(value):
    value = F(value)
    require(value.denominator == 1, 'integrality')
    return value.numerator


def dot(x, y):
    return sum(u * v for u, v in zip(x, y))


def inner(x, y):
    return 2 * dot(x, y)


def determinant(matrix):
    if len(matrix) == 0:
        return 1
    return sum((-1) ** j * matrix[0][j]
               * determinant([row[:j] + row[j + 1:] for row in matrix[1:]])
               for j in range(len(matrix)))


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def negate(vector):
    return tuple(-x for x in vector)


def proportional(x, y):
    return all(x[i] * y[j] == x[j] * y[i]
               for i, j in combinations(range(3), 2))


def coefficient_list(polynomial):
    return [exact_integer(x) for x in polynomial]


def serialize_rf(value):
    return {'numerator': coefficient_list(value.numerator),
            'denominator': coefficient_list(value.denominator)}


def main():
    # Construct the full ambient root system, independent of the active support.
    basis = [tuple(int(i == j) for i in range(3)) for j in range(3)]
    roots = set()
    for e in basis:
        roots.update((e, negate(e)))
    for i, j in combinations(range(3), 2):
        for s, t in product((-1, 1), repeat=2):
            roots.add(tuple(s * basis[i][k] + t * basis[j][k]
                            for k in range(3)))
    roots = sorted(roots)
    root_set = set(roots)
    require(len(roots) == 18 and (0, 0, 0) not in root_set, 'finite nonzero roots')
    require(all(e in root_set for e in basis), 'spans the ambient real space')

    # The form matrix is 2I. Sylvester's criterion proves positive definiteness.
    form = [[2 * int(i == j) for j in range(3)] for i in range(3)]
    form_minors = [determinant([row[:k] for row in form[:k]])
                   for k in range(1, 4)]
    require(form_minors == [2, 4, 8], 'positive definite form')
    lengths = {inner(r, r) for r in roots}
    require(lengths == {2, 4}, 'short-root length 2 and long-root length 4')

    pair_count = 0
    reflection_isometry_checks = 0
    cartan_values = set()
    for r in roots:
        require(negate(r) in root_set, 'opposite root')
        reflection = [[F(int(i == j)) - F(2 * r[i] * r[j], dot(r, r))
                       for j in range(3)] for i in range(3)]
        images = [matvec(reflection, e) for e in basis]
        for i, j in product(range(3), repeat=2):
            require(inner(images[i], images[j]) == inner(basis[i], basis[j]),
                    'reflection invariance of the form')
            reflection_isometry_checks += 1
        reflected_roots = set()
        for beta in roots:
            pair_count += 1
            if proportional(r, beta):
                require(beta in (r, negate(r)), 'reducedness')
            cartan = F(2 * inner(beta, r), inner(r, r))
            cartan_values.add(exact_integer(cartan))
            reflected = tuple(F(beta[i]) - cartan * r[i] for i in range(3))
            require(reflected == matvec(reflection, beta), 'reflection formula')
            require(reflected in root_set, 'closure under every root reflection')
            reflected_roots.add(reflected)
        require(reflected_roots == root_set, 'reflection permutes all roots')
    require(pair_count == 324, 'exhaustive ordered-pair count')

    simple = [(1, -1, 0), (0, 1, -1), (0, 0, 1)]
    require(all(r in root_set for r in simple), 'simple roots belong to R')
    simple_columns = [[simple[j][i] for j in range(3)] for i in range(3)]
    require(determinant(simple_columns) == 1, 'simple roots are a basis')
    positive_expansions = []
    for r in roots:
        # Solving r=c1*(e1-e2)+c2*(e2-e3)+c3*e3 gives these exact coordinates.
        coefficients = (r[0], r[0] + r[1], r[0] + r[1] + r[2])
        require(matvec(simple_columns, coefficients) == r, 'basis reconstruction')
        require(all(c >= 0 for c in coefficients) or all(c <= 0 for c in coefficients),
                'all roots have sign-coherent integral simple coordinates')
        if all(c >= 0 for c in coefficients):
            positive_expansions.append({'root': r, 'simple_coordinates': coefficients})
    require(len(positive_expansions) == 9, 'nine positive roots')
    gram = [[inner(r, s) for s in simple] for r in simple]
    require(gram == [[4, -2, 0], [-2, 4, -2], [0, -2, 2]], 'claimed Gram matrix')
    gram_minors = [determinant([row[:k] for row in gram[:k]]) for k in range(1, 4)]
    require(gram_minors == [4, 12, 8], 'positive Gram minors')
    connected = {0}
    while True:
        enlarged = connected | {j for i in connected for j in range(3)
                                if i != j and gram[i][j] != 0}
        if enlarged == connected:
            break
        connected = enlarged
    require(connected == {0, 1, 2}, 'irreducible ambient component')
    d = tuple(exact_integer(F(gram[i][i], 2)) for i in range(3))
    require(d == (2, 2, 1), 'normalized d values')
    a = (1, 1, 0)
    require(all(isinstance(x, int) and x >= 0 for x in a), 'admissible vector')

    def energy(state):
        actual_root_vector = matvec(simple_columns, state)
        from_gram = F(sum(state[i] * gram[i][j] * state[j]
                          for i, j in product(range(3), repeat=2)), 2)
        require(from_gram == dot(actual_root_vector, actual_root_vector),
                'energy agrees in ambient and simple coordinates')
        return exact_integer(from_gram)

    def qfactorial(state):
        out = ONE
        for i, entry in enumerate(state):
            for j in range(1, entry + 1):
                out = pmul(out, psub(ONE, monomial(d[i] * j)))
        return out

    states = sorted(product(*(range(x + 1) for x in a)), key=lambda x: (sum(x), x))
    z, u, v = (0, 0, 0), (1, 0, 0), (0, 1, 0)
    require(set(states) == {z, u, v, a}, 'complete coordinatewise interval')
    f = poly([1, 0, -1])
    require([energy(state) for state in (z, u, v, a)] == [0, 2, 2, 2],
            'claimed energies')
    require([qfactorial(state) for state in (z, u, v, a)]
            == [ONE, f, f, ppow(f, 2)], 'claimed q-factorials')
    J = {z: RF(ONE)}
    recursion_trace = []
    summand_count = 0
    for state in states:
        if state == z:
            continue
        e = energy(state)
        require(e > 0, 'nonzero recursion energy')
        total = RF(ZERO)
        summands = []
        # Enumerate directly from the exact source inequalities 0<=b<=state, b!=state.
        for b in product(*(range(x + 1) for x in state)):
            if b == state:
                continue
            require(b in J, 'strictly lower recursive state already computed')
            difference = tuple(state[i] - b[i] for i in range(3))
            term = RF(monomial(energy(b))) * J[b] / RF(qfactorial(difference))
            total = total + term
            summand_count += 1
            summands.append({'b': b, 'energy': energy(b),
                             'difference_factorial': coefficient_list(qfactorial(difference)),
                             'term': serialize_rf(term)})
        J[state] = total / RF(psub(ONE, monomial(e)))
        recursion_trace.append({'a': state, 'energy': e,
                                'q_factorial': coefficient_list(qfactorial(state)),
                                'summands': summands, 'J': serialize_rf(J[state])})
    require(summand_count == 5, 'all five recursion summands evaluated')
    require(J[u] == RF(ONE, ppow(f, 2)), 'claimed singleton u identity')
    require(J[v] == RF(ONE, ppow(f, 2)), 'claimed singleton v identity')
    require(J[a] == RF(poly([1, 0, 1]), ppow(f, 4)), 'claimed a identity')
    H = (RF(ppow(qfactorial(a), 2)) * J[a]).as_polynomial()
    require(H == poly([1, 0, 1]), 'exact numerator polynomial')
    coefficients = coefficient_list(H)
    peak_checks = []
    for peak in range(len(coefficients)):
        failures = []
        for i in range(peak):
            if coefficients[i] > coefficients[i + 1]:
                failures.append({'required': '<=', 'left_index': i,
                                 'left': coefficients[i], 'right': coefficients[i + 1]})
        for i in range(peak, len(coefficients) - 1):
            if coefficients[i] < coefficients[i + 1]:
                failures.append({'required': '>=', 'left_index': i,
                                 'left': coefficients[i], 'right': coefficients[i + 1]})
        require(bool(failures), 'each possible peak fails')
        peak_checks.append({'peak': peak, 'failed_inequalities': failures})

    claims = [
        'The root system B3, realized as R = {±e_i} ∪ {±e_i ±e_j : i<j} in R^3 with (x,y)=2x·y, satisfies all root-system and normalization hypotheses.',
        'The simple roots α1=e1−e2, α2=e2−e3, α3=e3 have Gram matrix [[4,−2,0],[−2,4,−2],[0,−2,2]], and a=(1,1,0) is an admissible vector.',
        'The defining recursion gives J_(1,0,0)=J_(0,1,0)=(1−q²)^−2 and J_(1,1,0)=(1+q²)/(1−q²)^4.',
        'The exact numerator polynomial for this witness is H_(1,1,0)(q)=1+q².',
        'This polynomial violates the recorded unimodality conclusion, yielding a complete refutation.'
    ]
    hashes = [
        'a2aaa1f701b4c290400d17500793bb203e4239c8731e396e78df4c5dc608a875',
        '37c505c10941ac69a2a2ecc6ae43c69837967319d8776c4e7632f8f4929dc4aa',
        'b31f29948694e44069bf2093ab9ae4968e3708ca18ae193a94fb0ab0a072b5bc',
        '04666943d7b43ba579f1923441b91807405b359d959406c34fcfad7522ea1e98',
        'cecdd900955312d682540eaa1ad5957d431902e13746797dc0b4644d02b8fedd'
    ]
    require([hashlib.sha256(claim.encode('utf-8')).hexdigest() for claim in claims]
            == hashes, 'exact supplied claim bindings')
    certificate = {
        'status': 'PASS', 'arithmetic': 'integers and fractions only',
        'roots': roots, 'root_count': len(roots), 'form_matrix': form,
        'form_leading_principal_minors': form_minors,
        'squared_root_lengths': sorted(lengths),
        'root_counts_by_squared_length': {str(n): sum(inner(r, r) == n for r in roots)
                                         for n in sorted(lengths)},
        'ordered_root_pairs_checked': pair_count,
        'reflection_form_entries_checked': reflection_isometry_checks,
        'cartan_integers': sorted(cartan_values),
        'simple_roots': simple, 'simple_basis_determinant': determinant(simple_columns),
        'positive_root_expansions': positive_expansions, 'gram_matrix': gram,
        'gram_leading_principal_minors': gram_minors, 'ambient_component_connected': True,
        'd': d, 'a': a, 'recursion_state_count': len(states),
        'recursion_summand_count': summand_count, 'recursion_trace': recursion_trace,
        'claimed_J_identities_cross_multiplied': True,
        'H_coefficients': coefficients, 'H_division_remainder': [],
        'peak_checks': peak_checks, 'unimodal': False,
        'verified_claim_indices': list(range(5)), 'claim_sha256': hashes
    }
    print(json.dumps(certificate, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
