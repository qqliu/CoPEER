r"""The stated formulas define the induced action of the direct-product group Γ = Z/3Z × Z/2Z on π₁ ≅ F₂."""

import json

RECORD = "arxiv_1006.0446v2__source_enriched_codex"
NOTES = "Exact free-word recomputation confirms the witness: σ(τ(γ₂)) reduces to γ₂γ₁, whereas τ(σ(γ₂)) reduces to γ₁γ₂. These distinct reduced words show that the stated automorphisms do not commute, as the two distinguished elements of Z/3Z × Z/2Z must. The refuted statement is substantive as written, not plainly a typo, although it may reflect an intended outer action or omitted basepoint/path data."

opposite = {"a": "A", "A": "a", "b": "B", "B": "b"}


def normalize(letters):
    stack = []
    for letter in letters:
        if stack and opposite[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def word_inverse(letters):
    return tuple(opposite[letter] for letter in reversed(letters))


def evaluate(letters, images):
    result = ()
    for letter in letters:
        if letter.islower():
            replacement = images[letter]
        else:
            replacement = word_inverse(images[letter.lower()])
        result = normalize(result + replacement)
    return result


sigma_images = {"a": ("b",), "b": ("A", "B")}
tau_images = {"a": ("A",), "b": ("B",)}


def sigma(word):
    return evaluate(word, sigma_images)


def tau(word):
    return evaluate(word, tau_images)


def repeated(mapping, word, count):
    result = word
    for unused in range(count):
        result = mapping(result)
    return result


basis = (("a",), ("b",))
orders_hold = all(repeated(sigma, word, 3) == word for word in basis)
orders_hold = orders_hold and all(repeated(tau, word, 2) == word for word in basis)
witness = ("b",)
left = sigma(tau(witness))
right = tau(sigma(witness))
confirmed = orders_hold and left == ("b", "a") and right == ("a", "b") and left != right

if not confirmed:
    raise AssertionError("the reported witness was not independently reproduced")

result = {"record_id": RECORD, "verdict": "CONFIRMED", "notes": NOTES}
print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
