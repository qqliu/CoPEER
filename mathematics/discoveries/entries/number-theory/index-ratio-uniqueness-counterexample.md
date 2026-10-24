# Two distinct squares with the same divisor index ratio below one

> Deposition record dated 11 September 2026. Read [later mathematical and attribution updates](../../README.md#later-updates) alongside this original record.

## Object

Use $n_1=1225=5^2 7^2$ and $n_2=3025=5^2 11^2$.
The complete increasing positive-divisor lists are

$$
\begin{aligned}
1225 &: 1,5,7,25,35,49,175,245,1225,\\
3025 &: 1,5,11,25,55,121,275,605,3025.
\end{aligned}
$$

Write $E(n)=\sum_{2\mid i}d_i$ and $O(n)=\sum_{2\nmid i}d_i$,
with positions beginning at one. These are Mittou's $\sigma_e(n)$ and
$\sigma_o(n)$, respectively. The split is by position, not divisor parity.

## What it kills

Conjecture 13 in Brahim Mittou's *A New Classification of Positive Integers
Via New Divisor Functions*, arXiv:2509.08844v2, proposes uniqueness of a
positive integer at each positive index ratio below one. Its set $G_k$
is defined in Definition 1. The witness violates that conclusion while
satisfying positivity and the strict ratio range.

## Why it works

The factorizations above make each divisor list exhaustive: each divisor
is $5^a p^b$ with $a,b\in\{0,1,2\}$ and $p=7$ or $11$.
Summing the even and odd positions gives

$$
\begin{aligned}
E(1225)&=5+25+49+245=324,& O(1225)&=1+7+35+175+1225=1443,\\
E(3025)&=5+25+121+605=756,& O(3025)&=1+11+55+275+3025=3367.
\end{aligned}
$$

Both ratios reduce to $108/481$. Since $0<108<481$ and $1225\ne3025$,
the two integers lie in the same $G_{108/481}$, so its size is at least two.
The integer cross-products independently give
$324\cdot3367=756\cdot1443=1090908$.

The [standalone exact checker](../../certificates/discoveries_20260910_v2/index_ratio_check.py)
enumerates divisibility from $1$ through each witness, checks the ordered
lists, uses one-based index sums, and compares exact rational numbers.
It uses the Python standard library and requires no model or run artifacts.

## Debugging uses

- Preserve index parity when translating divisor formulas; both witnesses
  have only odd divisors, so splitting by divisor parity gives a different object.
- Check an injectivity argument against distinct factorizations, beyond prime powers.
- Use exact fractions and exhaustive divisor lists to distinguish true
  collisions from rounded numerical ratios or incomplete enumeration.

## Remarks

This was found by the neutral Astra baseline of
`refutation30_astra_paired_v7_20260910`, record
`rf_numbers_index_ratio_square_injective`, on 2026-09-10. The separate
Astra audit verified all three claims, with `FULLY_RESOLVES_TARGET`,
`ACCURATE`, overall `VERIFIED`, and original-conjecture verdict `REFUTED`.
The baseline used 31,513 reported tokens and its audit 24,689, totaling
56,202. Both model states record `gpt-6-astra` with reasoning effort `max`.
Neither BugBank nor plain revision arm started: the pair closed at the shared
baseline. This is not evidence of a BugBank treatment benefit.

The card is `draft`, with no external novelty-priority claim, external
mathematical review, or proof-assistant certification. Model auditing and
the deterministic replay are distinct checks. The experiment's frozen
retrieval database is unchanged; this deposit appears only in a later index.

## References

- Brahim Mittou, *A New Classification of Positive Integers Via New Divisor
  Functions*, [arXiv:2509.08844v2](https://arxiv.org/html/2509.08844v2),
  Definition 1 and Conjecture 13 (14 September 2025).
- [Original baseline](../../provenance/rf_numbers_index_ratio_square_injective/baseline.json),
  SHA-256 `8b3dfe840287e324745e01c9d5444e9e5cfb1f3fbd5be6918cdb73380f30f86e`.
- [Independent audit](../../provenance/rf_numbers_index_ratio_square_injective/audit.json),
  SHA-256 `5ef4e5b86aeecb7d18fe93c69ae23fe98c31dca6e8a3c64edb8e7ff8bcee3535`.
- [Deposit evidence and source-input hashes](../../certificates/discoveries_20260910_v2/index_ratio_evidence.json).
