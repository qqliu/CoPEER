---
id: permutation-grid-rook-spectrum-counterexample
title: An eight-by-eight permutation crossword grid with 155 complete rook placements
type: counterexample
domain: combinatorics
subdomain: rook-placements
tags:
  - permutation-grids
  - crossword-grids
  - perfect-matchings
  - permanents
  - modular-obstruction
  - finite-counterexample
  - exact-counting
refutes: >
  For every positive integer r, there exist n >= 1 and w in S_n such that
  |RP(Grid(w))| = r if and only if r is neither 4 nor 12 and r is not congruent
  to 3 modulo 4. Grid(w) has black cells (i,w(i)); across and down words are
  nonempty maximal contiguous white segments, including singletons, and
  RP(Grid(w)) consists of white-cell subsets meeting each word exactly once.
statement: >
  For the one-based permutation w = (2,7,4,8,1,6,3,5) in S_8, the grid with
  black cells (i,w(i)) has exactly 155 complete nonattacking rook placements.
  There are 14 across words and 14 down words. Five forced rooks reduce their
  incidence graph to a nine-by-nine graph with permanent 29 + 63 + 63 = 155.
  Since 155 is congruent to 3 modulo 4, this contradicts the proposed spectrum.
source:
  book: discovery-rook-spectrum-2026
  chapter: "Permutation grids; frozen target of Conjecture 3.10"
  item: null
  pages: null
difficulty: 3
status: draft
related: []
formalized: []
---

## Object

Use one-based coordinates and the permutation

$$w=(2,7,4,8,1,6,3,5)\in S_8.$$

Color cell $(i,w(i))$ black for each row $i$; all other cells are white. An
across word is a nonempty maximal contiguous white segment in a row, and a
down word is the corresponding segment in a column. Singleton segments are
words. A complete rook placement is a subset of white cells that meets each
across word and each down word exactly once. In particular, a black cell
separates two words on the same row or column.

Write $L_i,R_i$ for the words left and right of the black cell in row $i$,
and $U_j,D_j$ for the words above and below the black cell in column $j$.
Omit empty words. The board has 14 words in each direction.

## What it kills

The frozen form of Lewis–Won, Conjecture 3.10, claims that the positive
integers realized as $|RP(\operatorname{Grid}(w))|$, over all sizes and all
permutations, are exactly those excluding 4, 12, and the residue class
$3\pmod 4$. The witness realizes $155\equiv3\pmod4$, refuting the necessity
of that residue restriction and therefore the equivalence.

This witness alone does not settle whether 4 or 12 are realizable or classify
the complete count spectrum.

## Why it works

Each white cell belongs to a unique pair of an across word and a down word,
and two such words intersect in at most one cell. Consequently, complete
placements correspond bijectively to perfect matchings in the bipartite
word-incidence graph. Their number is the permanent of its biadjacency matrix.

Four rooks are forced by singleton words:

| Cell | Singleton word |
|---|---|
| $(1,1)$ | $L_1$ |
| $(2,8)$ | $R_2$ |
| $(8,3)$ | $D_3$ |
| $(1,7)$ | $U_7$ |

The word $U_4$ consists of $(1,4)$ and $(2,4)$. The first cell shares $R_1$
with the forced rook $(1,7)$, so $(2,4)$ is also forced. The five forced
rooks occupy distinct across and down words. Deleting their incident words
leaves the following nine-by-nine graph. Number its down words

$$
(D_1,D_2,U_3,D_4,U_5,U_6,D_6,D_7,D_8)
$$

by $1,\ldots,9$ in that order.

| Row | Across word | Available column numbers |
|---|---|---|
| $A$ | $L_3$ | 2, 3 |
| $B$ | $R_3$ | 5, 6, 8 |
| $C$ | $L_4$ | 2, 3, 4, 5, 6, 8 |
| $D$ | $R_5$ | 2, 3, 4, 5, 6, 8, 9 |
| $E$ | $L_6$ | 1, 2, 3, 4, 5 |
| $F$ | $R_6$ | 8, 9 |
| $G$ | $L_7$ | 1, 2 |
| $H$ | $R_7$ | 4, 5, 7, 8, 9 |
| $I$ | $R_8$ | 7, 8, 9 |

Adjoining the five forced edges gives a unique extension of each residual
perfect matching to a complete placement on the original board.

Rows $A,G$ occupy two columns of $\{1,2,3\}$. Each possible unused column
$p=1,2,3$ occurs once: assignments $(A,G)=(3,2),(3,1),(2,1)$, respectively.
Rows $F,I$ occupy two columns of $\{7,8,9\}$. Unused column $q=7$ occurs
twice, from $(F,I)=(8,9),(9,8)$; unused columns $q=8,9$ occur once, from
$(9,7),(8,7)$, respectively.

Let $T(p,q)$ count matchings of rows $B,C,D,E,H$ onto columns
$\{p,4,5,6,q\}$. Thus the desired count is

$$\sum_{p=1}^3\bigl(2T(p,7)+T(p,8)+T(p,9)\bigr).$$

The small minors are

| $p$ | $T(p,7)$ | $T(p,8)$ | $T(p,9)$ |
|---|---:|---:|---:|
| 1 | 4 | 14 | 7 |
| 2 | 10 | 28 | 15 |
| 3 | 10 | 28 | 15 |

Every distinct table entry has a short direct count:

- For $p=1$, column 1 forces $E\to1$. If $q=7$, also $H\to7$;
  $B$ has two choices and $C,D$ have two orders, giving 4. If $q=8$,
  the remaining four-by-four matrix has only two forbidden entries,
  $B\to4$ and $H\to6$, giving $4!-2\cdot3!+2!=14$. If $q=9$,
  assigning $H\to9$ gives 4; assigning $D\to9$ gives 1 or 2 according
  as $B\to5$ or $B\to6$, for a total of 7.
- For $p=2,q=7$, $H\to7$ is forced. Choosing $B\to5$ gives two choices
  for $E$ and two orders for $C,D$; choosing $B\to6$ gives three choices
  for $E$ and two orders for $C,D$. The total is $4+6=10$.
- For $p=2,q=8$, choose columns for $B,E,H$ first. The choices
  $B\to5,6,8$ leave respectively 3, 7, and 4 distinct-column assignments
  for $E,H$. Rows $C,D$ then have two orders, giving $2(3+7+4)=28$.
- For $p=2,q=9$, assigning $H\to9$ gives 10. Assigning $D\to9$ gives
  1 when $B\to5$, and 4 when $B\to6$, for a total of 15.
- Columns 2 and 3 have the same neighborhood among $B,C,D,E,H$, so the
  row $p=3$ equals the row $p=2$.

Therefore

$$
|RP(\operatorname{Grid}(w))|
=(2\cdot4+14+7)+(2\cdot10+28+15)+(2\cdot10+28+15)
=29+63+63=155\equiv3\pmod4.
$$

The standalone [exact checker](../../certificates/discoveries_20260910/rook_spectrum_check.py)
reconstructs maximal words directly from the board, counts the full
14-by-14 permanent by Ryser inclusion–exclusion, and independently counts
selected white-cell subsets. It then checks each forced edge, the residual
neighborhoods, their permanent, the conditioning multiplicities, and all
$5!=120$ assignments for each of the nine small minors. All three full
counts and the weighted minor sum equal 155. It uses exact integers and the
Python standard library only; no model, run directory, or solver is required.

From the repository root, run:

```sh
python3 BugBank/certificates/discoveries_20260910/rook_spectrum_check.py
```

## Debugging uses

- Test a claimed modular restriction on all permutation-grid permanents with
  this explicit witness; a size-limited search is not a universal proof.
- Preserve singleton words, remove empty segments, and let black squares
  split words. Counting ordinary nonattacking rooks on unbroken rows and
  columns computes a different object.
- Verify that forced rooks are forced by the current incidence graph before
  deleting both incident words; partial deletion can change the count.
- Distinguish selected-cell subsets from ordered rook lists: the incidence
  matching and direct cell recursion each count every subset exactly once.

## Remarks

This counterexample was discovered on 2026-09-10 by `gpt-6-astra` at maximum
reasoning in the source-only, arm-neutral baseline of
`frontier5_astra_bugbank_v2_20260910`, before any BugBank retrieval or exposure.
It is a new deposit into BugBank, not evidence that BugBank caused this
discovery. The baseline took 54,353 reported tokens and returned a full
disproof with the finite counting argument above.

The baseline's separate Astra audit completed on 2026-09-10 at 15:53:43 UTC,
verifying all 12 claims and returning `FULLY_RESOLVES_TARGET` with overall
verdict `VERIFIED`. The count was also independently reproduced by local
exact code, including the checker linked above. This entry remains `draft`:
no external human review or Lean/other proof-assistant formalization is
claimed. The model audit is recorded evidence, distinct from the baseline's
self-assessment and from formal verification.

## References

- Joel Brewster Lewis and Robert Won, *Non-attacking rook placements on
  crossword grids*, [arXiv:2609.03081v1](https://arxiv.org/abs/2609.03081v1),
  Section 2 definitions, Section 3.2 permutation grids, and
  [Conjecture 3.10](https://arxiv.org/html/2609.03081v1#S3.Thmconj10).
- [Frozen source-only target](../../../qedbench_certificate_availability_triage/runs/frontier5_astra_bugbank_v2_20260910/inputs/posthoc10_rook_permutation_grid_count_spectrum.json),
  SHA-256 `3befbb430c1ff4736ce567a9445b65398fa043f32a71e50e411ebe7856f3d679`.
  Its bounded curator restatement includes nonempty maximal words without
  minimum-length or crossword-symmetry restrictions.
- [Original Astra baseline](../../../qedbench_certificate_availability_triage/runs/frontier5_astra_bugbank_v2_20260910/baselines/posthoc10_rook_permutation_grid_count_spectrum.json),
  SHA-256 `93b1ed9c40055840aa9669a93db4011f4860b0d4077d9481c2eae44c817831ba`.
  The self-contained proof and independent replay checker are retained in
  this deposit, so reproducing the result does not require that run.
- [Independent Astra baseline audit](../../../qedbench_certificate_availability_triage/runs/frontier5_astra_bugbank_v2_20260910/audits/baseline/posthoc10_rook_permutation_grid_count_spectrum.json),
  SHA-256 `0b8bebd668779410f48f493e6eb5b27713be957c370bf89e47f8f959c93de580`.
