---
id: cyclic-cube-free-density-counterexample
title: A cyclic 5-cube-free set of density 13/16
type: counterexample
domain: combinatorics
subdomain: additive-combinatorics
tags: [cyclic-groups, subset-sums, projective-cubes, multisets, density-bounds, quotient-lifting, computational-certificate, discovered-counterexample]
refutes: >
  For all positive integers d and N with d dividing N, every d-cube-free
  subset A of Z_N satisfies |A| <= ((d-1)/d)N. Here a projective d-cube
  comprises every nonempty indexed subset sum of a size-d multiset, with
  repetitions and zero entries permitted.
statement: >
  Take d=5, N=80, and A={x in Z_80 : x modulo 16 is not in {0,4,12}}.
  Then |A|=65>64=((d-1)/d)N, although A is 5-cube-free. Every five-entry
  multiset in Z_16 has a nonempty indexed subset sum in {0,4,12}; reduction
  modulo 16 lifts this obstruction to Z_80. The finite obstruction has an
  independent exhaustive exact-arithmetic certificate covering all 15,504
  five-entry multisets and all 31 nonempty indexed subsets of each.
true_theorem: >
  If Q divides N and A_0 is d-cube-free in Z_Q, then its inverse image under
  reduction Z_N -> Z_Q is d-cube-free and has size (N/Q)|A_0|. In particular,
  this example gives a 5-cube-free set of density 13/16 for every N divisible
  by 80, exceeding 4/5 by 1/80.
hypothesis_violated: null
source:
  book: discovery-cube-free-2026
  chapter: "Introduction; Definitions 1 and 2 and Conjecture 4"
  item: null
  pages: "2"
difficulty: 3
status: draft
related: []
formalized: []
---

## Object

For a multiset $S=(a_1,\ldots,a_d)$ of elements of the additive cyclic group
$\mathbb Z_N$, define its projective cube by

$$
\Sigma^*S=\left\{\sum_{i\in I}a_i:
\varnothing\ne I\subseteq\{1,\ldots,d\}\right\}.
$$

The full index set is included. Repeated generators and zero generators are
allowed, and coincident subset sums are counted only once in the resulting
set. A set $A$ is $d$-cube-free if no such cube is contained in $A$.

Take $d=5$, $N=80$, $F=\{0,4,12\}\subset\mathbb Z_{16}$, and

$$
A=\{x\in\mathbb Z_{80}:x\bmod16\notin F\}.
$$

Its complement consists of the 15 residues
$0,4,12,16,20,28,32,36,44,48,52,60,64,68,76$.

## What it kills

Conjecture 4 of Yuchen Meng's *On Cube-Free Problems* asserts that, if
$d\mid N$, every $d$-cube-free subset of $\mathbb Z_N$ has cardinality at most
$(d-1)N/d$. Here $5\mid80$, but $|A|=65>64=4\cdot80/5$.

This refutes the universal bound under its multiset definition; it is not
merely a failure of a distinct-generator variant or of the paper's separate
diagonal conjecture. The object tests attempts to extrapolate the source's
proved special cases to arbitrary composite moduli.

## Why it works

First, every five-entry multiset $S$ in $\mathbb Z_{16}$ has a nonempty
indexed subset whose sum belongs to $F$. Here is a direct proof. Suppose
otherwise. Every nonempty subset whose sum is divisible by 4 must then sum
to 8 modulo 16. Two disjoint such subsets are impossible, since their union
would sum to 0 modulo 16.

No entry is divisible by 4: it would equal 8 modulo 16, while among the
remaining four entries two of their five consecutive partial sums agree
modulo 4, giving a disjoint nonempty subset summing to 0 modulo 4. Thus
every even entry is 2 modulo 4. There cannot be three even entries: all
three pair sums would have to equal 8 modulo 16, forcing the entries equal
and $2e=8\pmod {16}$, impossible for $e=2\pmod4$.

It remains to consider zero, one, or two even entries.

- With two even entries $e,f$, their pair sums to 0 modulo 4. Hence the
  three odd entries all have the same class modulo 4, since otherwise an
  opposite-class odd pair is disjoint from the even pair. For two odd
  entries $x,y$, both $e+x+y$ and $f+x+y$ equal 8 modulo 16, so $e=f$;
  the even pair again gives the impossible equation $2e=8\pmod {16}$.
- With one even entry $e$, the four odd entries cannot split $2+2$ between
  classes 1 and 3 modulo 4, since that gives two disjoint opposite-class
  pairs. A $3+1$ split also fails: combine $e$ with two majority entries,
  and pair the remaining majority entry with the minority entry. Thus all
  four odd entries share a class. Every $e+x_i+x_j$ then equals 8 modulo
  16; comparing these equations forces all four odd entries equal to an
  odd $a$. Their sum $4a$ is 4 or 12 modulo 16, a contradiction.
- With zero even entries, if both odd classes occur at least twice, take
  two disjoint opposite-class pairs. In a $4+1$ split, each majority entry
  plus the minority entry equals 8 modulo 16, forcing the four majority
  entries equal; their sum is 4 or 12. If all five share one class, every
  four-entry sum equals 8 modulo 16. Comparing these sums forces all five
  entries equal, giving the same contradiction.

The finite assertion is also verified independently by the exact enumeration in
[cube_density_check.py](../../certificates/discoveries_20260910/cube_density_check.py).
The checker visits each weakly increasing tuple
$0\le a_1\le\cdots\le a_5<16$. There are
$\binom{20}{5}=15,504$ such tuples. For each tuple it evaluates all 31 nonzero
five-bit masks and checks that at least one indexed subset sum, reduced modulo
16, lies in $F$. It checks all $480,624$ subset sums, including the full
five-element sum; no distinctness or nonzero restriction is imposed.
Sorting permutes indices and hence preserves the set of all indexed subset
sums, so this enumeration covers every ordered tuple as well.

Next, reduction $\pi:\mathbb Z_{80}\to\mathbb Z_{16}$ is a well-defined
surjective additive homomorphism because $16\mid80$. Each fiber has five
elements, giving

$$
|A|=(16-3)\cdot5=65.
$$

For any five generators in $\mathbb Z_{80}$, apply the finite assertion to
their images under $\pi$. It supplies a nonempty index set $I$ such that

$$
\pi\!\left(\sum_{i\in I}a_i\right)
=\sum_{i\in I}\pi(a_i)\in F.
$$

The corresponding sum is outside $A$, so no projective 5-cube is contained
in $A$. The checker also verifies every projection fiber, all $80^2=6,400$
additivity identities, the cardinality, both divisibility conditions, and
the strict inequality using exact rational arithmetic.

The same inverse-image argument works for every $N$ divisible by 16. To
satisfy the conjecture's additional $5\mid N$ condition, take any multiple
of 80. Its inverse image has density $13/16>4/5$.

## Debugging uses

- Test a purported universal cube-free density bound on $(d,N)=(5,80)$ and
  this explicit 65-element set before extending arguments from prime powers
  or from dimensions equal to the smallest prime factor of $N$.
- When passing to a quotient, check that the quotient modulus divides the
  ambient modulus and that the same nonempty index set lifts through the
  additive map. The conjecture's condition $d\mid N$ need not hold in the
  smaller quotient used to construct the obstruction.
- Enumerate multisets and indexed subsets. Restricting to distinct or
  nonzero generators, dropping the full subset, or treating coincident sums
  as distinct proves a different statement.
- Keep projective subset sums separate from translated affine cubes; the
  definition above has no independently chosen translation parameter.

## Remarks

Deposited on 2026-09-10 from the Astra comparison experiment for record
`ext3_cube_free_cyclic_bound`. Both the plain arm (P3, revision `c000593`, full
audit `c000619`) and the BugBank arm (R3, revision `c000535`, full audit
`c000552`) supplied a complete disproof. Each full run audit marked every
load-bearing claim `VERIFIED`, the inventory and dependencies complete, and
the exact target `FULLY_RESOLVES_TARGET` with accurate resolution status.
The reported valid post-baseline token totals are 518,063 for plain and
2,131,034 for BugBank. This is a discovery in both arms, not evidence of a
BugBank-only success or a causal benefit from retrieval.

The entry's finite computation was independently replayed with the standalone
checker at deposit time. The run's model audits and this replay do not
constitute a Lean formalization or external publication review. The entry
therefore remains `draft`, with no formalization link. No priority claim is
made. See [the deposit evidence](../../certificates/discoveries_20260910/cube_density_evidence.json)
for exact local provenance and hashes. This deposit follows the experiment
and must not be treated as an entry available to its earlier retrievals.
The separately recorded final independent replay of the full experiment
remains pending; the standalone check here verifies the mathematical witness
without changing that experiment-wide status.

## References

- Yuchen Meng, *On Cube-Free Problems*, The Electronic Journal of Combinatorics
  33(1) (2026), P1.16, Definitions 1 and 2 and Conjecture 4, p. 2.
  [Publisher page](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v33i1p16),
  [DOI 10.37236/14052](https://doi.org/10.37236/14052).
- Repository source package:
  `qedbench_certificate_availability_triage/paired_open_problem_bugbank_targeted_extension_sources_v3/records/ext3_cube_free_cyclic_bound.json`;
  retained PDF and exact definition binding in that package's
  `sources/ejc2026_cube_free/` directory.
- Repository run audits:
  `qedbench_certificate_availability_triage/astra_simple_comparison_20260906/c000619/CANONICAL_RESPONSE.json`
  and `c000552/CANONICAL_RESPONSE.json` within the same run directory.
