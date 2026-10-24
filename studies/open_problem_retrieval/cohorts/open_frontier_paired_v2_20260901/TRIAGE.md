# Preliminary candidate triage

This note records an early, read-only review of the first ten neutral drafts.
It is not an audit result and is not supplied to either experimental arm.

## Full-result claims requiring special scrutiny

- **Level-3 additive restoration.** The saturated-count upper-bound
  construction is plausible, but P-completeness under polynomial-time
  many-one reductions is a tautological classification for any nontrivial
  language in P. It is not the usual matching hardness result. The `FULL`
  label therefore requires either a standard hardness proof or a narrower
  interpretation of the target.
- **Simultaneous M&M limits.** The transfer matrix is coherent for the physical
  interpretation that applies the per-colour cap `m = ell + 1` to the relaxed
  pyramid. The source's short future-work sentence may also be read as
  intersecting two permutation-displacement restrictions. A full result must
  fix or cover this ambiguity.
- **Careless coupon collector.** The stationary product and Kac identity are
  consistent. The key proof risk is the coupling/Abel-summation argument for
  monotonicity of the passage increments, especially `(n-k)e_k`; the uniform
  asymptotic conclusion depends on it.
- **A10-in-A1 and A9-in-A1 packing.** The benchmark alternatives are crossed
  relative to the supplied source table and ISO dimensions: A1/A9 is 258--259,
  while A1/A10 is 518--519. The candidates give arithmetically coherent
  placements and marker upper bounds of 258 and 518, respectively. These must
  be reported as target-definition corruption as well as mathematical
  resolutions of the correctly identified source instances.

## Partial-result claims requiring special scrutiny

- **Berlin safe houses.** The interval example separates bidirectional greedy
  from optimum by 7 versus 6, but does not resolve the requested sub-2
  approximation question.
- **Max-Bounded-Sums.** The general linear-time word-RAM target remains open;
  the bit-length observation is not a standard fine-grained lower bound.
- **Recursive maze.** The unrestricted linear bound remains open, and the
  positive certificate needs an exact chronological/live-root check.
- **Tiles without teleport.** The frequency-two algorithm's deterministic
  linear-time wording depends on explicit radix/counting-sort assumptions.
- **Torus pushes.** The balanced-board gap remains open; the transposed
  `FillColumns` argument and parity gadgets need a full independent check.

Until the strengthened audits separately verify literal claims and exact
target coverage, none of these drafts is labeled a verified full solution.
