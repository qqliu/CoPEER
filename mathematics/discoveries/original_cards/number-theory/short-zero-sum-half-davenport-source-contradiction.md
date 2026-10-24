---
id: short-zero-sum-half-davenport-source-contradiction
title: The elementary two-group exception to a printed half-Davenport transition
type: counterexample
domain: number-theory
subdomain: additive-combinatorics
tags:
  - zero-sum-sequences
  - finite-abelian-groups
  - davenport-constant
  - source-internal-contradiction
  - previously-published
  - exact-enumeration
refutes: >
  For a finite abelian group G of rank at least two with D(G)=D*(G), and
  positive k with exp(G) <= D(G)-k <= D(G), Conjecture 6.2 asserts that
  s_le(D(G)-k)(G) <= D(G)+k if D(G)-k >= (D(G)+1)/2, and is greater
  than D(G)+k otherwise. Sequences allow repetitions, D is the Davenport
  constant, D*=1+sum_i(n_i-1) for invariant factors n_i, and s_le(h) is
  the least length forcing a nonempty zero-sum subsequence of length <= h.
statement: >
  Take G=C_2^4 and k=2. Rank is four, exponent is two, and D=D*=5,
  so D-k=3=(D+1)/2 satisfies the upper-branch hypotheses. But s_le3(G)=9,
  whereas the conjecture requires s_le3(G)<=7. This exception is already
  stated elsewhere in Zhao's same source paper, so it is source screening,
  not a new model or BugBank discovery.
source:
  book: source-zhao-half-davenport-2025
  chapter: "Conjecture 6.2; Lemma 1.7(iii); remark after Theorem 1.11"
  item: null
  pages: null
difficulty: 2
status: draft
related: []
formalized: []
---

## Object

Let $G=C_2^4=\mathbb F_2^4$, with componentwise addition. A sequence is
a finite list of elements with repetitions permitted; a subsequence selects
positions. Its sum is zero when the selected vectors sum to the zero vector.
The Davenport constant $D(G)$ is the least length forcing a nonempty
zero-sum subsequence. For invariant factors $n_i$, put
$D^*(G)=1+\sum_i(n_i-1)$. Write $s_{\le h}(G)$ for the least length
forcing a nonempty zero-sum subsequence of length at most $h$.

Use $k=2$ and the eight distinct vectors
$A=\{(1,a,b,c):a,b,c\in\mathbb F_2\}$ as a short-zero-sum-free sequence.

## What it kills

The printed Conjecture 6.2 of Kevin Zhao's arXiv:2506.21383v1 proposes
an upper branch $s_{\le D-k}(G)\le D+k$ when $D-k\ge(D+1)/2$,
for rank at least two, $D=D^*$, positive $k$, and
$\exp(G)\le D-k\le D$; its lower branch reverses the bound strictly.
It does not exclude $C_2^4$. Here $D=D^*=5$, rank is four, exponent is
two, and $D-k=3=(D+1)/2$. Thus its upper branch asserts $s_{\le3}(G)\le7$.
In fact $s_{\le3}(G)=9$.

This is a contradiction in the source as printed. The remark after
Theorem 1.11 already records precisely this value; Lemma 1.7(iii) gives
the corresponding elementary-two-group formula. The deposit documents a
source-screening exclusion, not a fresh mathematical or model discovery.

## Why it works

Four basis vectors have no nonempty zero-sum subsequence, while any five
vectors in a four-dimensional space over $\mathbb F_2$ are linearly
dependent. A nontrivial dependence has coefficients zero or one and hence
is a nonempty zero-sum subsequence. Thus $D=5=D^*=1+4(2-1)$.

For the lower bound $s_{\le3}\ge9$, each vector of $A$ has first coordinate
one, so a sum of one or three of them cannot vanish. Two distinct vectors
cannot sum to zero in characteristic two. All eight vectors are distinct,
so $A$ has no nonempty zero-sum subsequence of length at most three.
Any seven-element subsequence already directly violates the claimed bound.

For the upper bound, consider any sequence of length nine. A zero element
gives a zero-sum singleton; repeated elements give a zero-sum pair.
Otherwise its support $S$ consists of nine distinct nonzero vectors.
Fix $a\in S$. The sets $S$ and $a+S$ each have nine elements in a
16-element group, so they intersect. Write $x=a+y\in S\cap(a+S)$
with $y\in S$. Since $0\notin S$ and $a\ne0$, the vectors $a,x,y$
are pairwise distinct. Their sum is zero, giving a subsequence of length
three. Hence $s_{\le3}=9>7=D+k$.

The [exact standalone checker](../../certificates/discoveries_20260910_v2/short_zero_sum_check.py)
uses four-bit vectors and XOR. It checks the lower witnesses, all length-five
multisets for the Davenport upper bound, and all nine-element supports for
the short-zero-sum upper bound. Repetitions in the latter case are handled
by the explicit identical-vector pair identity. The hand arguments above
also prove both upper bounds without computation.

## Debugging uses

- Test equality at a proposed threshold: this witness is exactly at
  $D-k=(D+1)/2$, not outside the conjecture's quantified range.
- Check exceptional groups consistently across a paper's theorem and later
  conjecture. Theorem 1.11 excludes the relevant group; Conjecture 6.2 does not.
- Preserve repeated elements and nonempty-subsequence conventions when
  translating zero-sum assertions into a subset search.

## Remarks

No search-controller model call was launched for this excluded candidate.
There is no model-discovery token count or independent model audit for it.
This source-screened item is reported separately from experimental discoveries.
The exact checker is a deposit replay, not a discovery experiment. The card
remains `draft`; it has no proof-assistant certificate or external review claim.
The frozen 661-entry experimental database is unchanged.

## References

- Kevin Zhao, *On zero-sum subsequences in a finite abelian group of length
  not exceeding a given number*, [arXiv:2506.21383v1](https://arxiv.org/html/2506.21383v1)
  (26 June 2025), Conjecture 6.2, Lemma 1.7(iii), and the remark after Theorem 1.11.
- [Source-screening record](../../../qedbench_certificate_availability_triage/runs/refutation30_astra_paired_v7_20260910/SELECTION.json),
  excluded candidate `rf_numbers_short_zerosum_half_threshold`.
- [Deposit evidence](../../certificates/discoveries_20260910_v2/short_zero_sum_evidence.json).
