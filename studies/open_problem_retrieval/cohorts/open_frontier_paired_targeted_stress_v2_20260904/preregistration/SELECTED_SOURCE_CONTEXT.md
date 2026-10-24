# Exact selected-source context and target interpretations

Freeze cutoff: 2026-09-04. This file is a reading guide; the byte-bound source
package and semantic audits are authoritative.

## 1. Barbados 2026, Problem 33, first clause

Source: `https://web.math.princeton.edu/~pds/barbados26/problems.pdf`, page 12.
The full downloaded PDF had SHA-256
`6e313aef764a3c10f6285acc2de28a76866ce414e2b81badd5b54e515f5c3769`
on 2026-09-04. No reuse license was displayed, so only the necessary excerpt is
retained locally in
`../paired_open_problem_bugbank_targeted_stress_sources_v1/sources/barbados26/selected_verbatim_excerpt.txt`.

The target is the first question only: does a finite simple graph exist that is
K6-free and odd-hole-free but is edge-Ramsey for a triangle with two colors?
“Odd hole” means an induced odd cycle of length at least five. The conditional
K4-free follow-up is not part of the target.

## 2. ESA 2026, Question 5

Source: Édouard Bonnet, *Answering Related Questions*, DOI
`10.4230/LIPIcs.ESA.2026.73`, article pages 73:7–73:8. The source asks whether
`Sidestep(Triangle Partition, dist_Δ, 1)` is in FP. Here `dist_Δ(G,H)` is the
maximum degree of the graph whose edges are the symmetric difference of the
two same-labeled-vertex-set graphs. The solver must output the nearby graph and
either an actual triangle partition or a correct `nil` answer.

## 3. ESA 2026, Question 1 subsidiary

The selected statement is the subsidiary sentence asking whether, for every
fixed positive constant, `Sidestep(Hamiltonian Cycle, dist_e, n/c)` is in FP.
The broad preceding question about the entire hardness radius is not selected.
The constant is renamed from `k` to `c`; `dist_e` counts edges in the symmetric
difference, and a positive answer must include a Hamiltonian cycle witness.

## 4. ESA 2026, Question 2

The source asks the analogous universal inverse-constant-linear question for
Dominating Set. The universal radius constant is called `c` in the normalized
target, while the instance threshold is called `q`. Finite distance requires
that threshold to remain unchanged.

The complete selected ESA passages and all needed definitions are in
`../paired_open_problem_bugbank_targeted_stress_sources_v1/sources/esa2026_73/selected_context.txt`;
the licensed final PDF is retained beside it.

## 5. Barbados 2026, Problem 31

The source asks whether every planar graph has a half-balanced separator that
is the union of two shortest paths. The normalized target uses finite simple
unweighted graphs, permits the paths to meet, and requires each path to be
shortest between its endpoints in the original graph. Every component after
deleting their union must have at most half the original vertices. The source's
known two-path result with 2/3 balance does not settle this target.

## 6. ICALP 2026, Conjecture 12

Source: Srinwanti Debgupta, Sarah Morell, and Martin Skutella,
*Unsplittable Transshipments*, DOI `10.4230/LIPIcs.ICALP.2026.74`, article page
74:16. The target preserves the finite acyclic-digraph setting stated for the
Modified DGG framework. The normalized target also requires `b` to be nonzero;
because its entries sum to zero, this makes both the source and sink sets
nonempty and makes `d_max` well-defined. Given a nonnegative
`b`-transshipment `x`, it asks for a polynomial-time unsplittable
`b`-transshipment `y` satisfying both `x_a-d_max <= y_a` and
`y_a <= x_a+d_max` on every arc.

For an executable polynomial-time experiment, the normalized target restricts
`b` and `x` to exact rational inputs and uses the standard bit model. This is a
narrower computational operationalization of the source's literal real-valued
statement, not a claim that the rational and full real-domain guarantees are
equivalent. The exact source definitions and open-status paragraph are in the
retained CC BY 4.0 source package.
