"""The stated formulas define the induced action of the direct-product group Γ = Z/3Z × Z/2Z on π₁ ≅ F₂."""

import itertools
import json

LETTERS = (1, -1, 2, -2)
SIGMA_IMAGES = {1: (2,), 2: (-1, -2)}
TAU_IMAGES = {1: (-1,), 2: (-2,)}


def reduce_word(word):
    reduced = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


def inverse_word(word):
    return tuple(-letter for letter in reversed(word))


def apply_hom(word, images):
    expanded = []
    for letter in word:
        image = images[letter] if letter > 0 else inverse_word(images[-letter])
        expanded.extend(image)
    return reduce_word(expanded)


def sigma(word):
    return apply_hom(word, SIGMA_IMAGES)


def tau(word):
    return apply_hom(word, TAU_IMAGES)


def iterate(function, word, count):
    value = word
    for _ in range(count):
        value = function(value)
    return value


def bounded_words():
    words = []
    for length in range(3):
        for candidate in itertools.product(LETTERS, repeat=length):
            if reduce_word(candidate) == candidate:
                words.append(candidate)
    return tuple(words)


words = bounded_words()
violations = []
for word in words:
    if iterate(sigma, word, 3) != word:
        violations.append((word, "sigma^3=id"))
    if iterate(tau, word, 2) != word:
        violations.append((word, "tau^2=id"))
    if sigma(tau(word)) != tau(sigma(word)):
        violations.append((word, "sigma*tau=tau*sigma"))

assert len(words) == 17
assert violations
assert violations[0] == ((2,), "sigma*tau=tau*sigma")
assert sigma(tau((2,))) == (2, 1)
assert tau(sigma((2,))) == (1, 2)

result = {
    "record_id": "arxiv_1006.0446v2__source_enriched_codex",
    "outcome": "WITNESS_FOUND",
    "witness_description": "With γ1 represented by (1) and γ2 by (2), the word γ2 is a witness: (σ∘τ)(γ2)=γ2γ1, while (τ∘σ)(γ2)=γ1γ2; these are distinct reduced words in F2.",
    "refutation_explanation": "In Z/3Z × Z/2Z the distinguished elements σ and τ commute, so any action must give commuting automorphisms. Extending τ(γ_i)=γ_i^{-1} and the quoted σ formulas homomorphically, the exhaustive computation finds the displayed failure on γ2. Hence the formulas cannot define an action of the stated direct-product group on F2.",
    "search_space": "All 17 reduced words in F2 of length at most 2 over the fixed letter order γ1, γ1^{-1}, γ2, γ2^{-1}; for every word, the program checked σ^3(w)=w, τ^2(w)=w, and σ(τ(w))=τ(σ(w)).",
}
print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
