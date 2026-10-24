# SE_cs_81391__q

The stored problem, source_context and claim_quote text is identical across this pair. This is not a fresh comparison against the live external source or an independent semantic adjudication.

Both complete certificate files below are copied byte-for-byte from authenticated successful build snapshots. No new compilation was performed. The semantic conclusions are quoted from the existing audit.

## Unchanged source context

```text
0012 | > sorted list in the end.
0013 | 
0014 | [[Source](https://en.wikipedia.org/wiki/Shellsort)]
0015 | 
0016 | *What is the mathematical proof for the quoted claim (in bold)?*
0017 | 
0018 | **An attempt at the proof** (for the case when number of elements is $2n+1$):
0019 | 
0020 | 
0021 | ----------
0022 | 
0023 | 
0024 | My initial array is $A = \{x_0, \cdots, x_n\}$ and i have $x_0 < x_n$. Say that after first pass $x_0$ switches place with $x_m$, so the final array $B$ starts with the entry $x_m$ regardless of the position of $x_0$ (which can further switch place with $x_{2m}$ and so on). Thus, $x_m < x_0$. Now, in the final pass $x_n$ can switch place with $x_k$ (which, before the last pass, is in the $(n-m)$-th position in the array). We don't care about $k$, but we just know that $x_n < x_k$. So the last entry in the final $m$-sorted array $B$ is $x_k$.
0025 | Sum it up: $x_m < x_0 < x_n < x_k$.
0026 | 
0027 | That means $B$ is $n$-sorted.
0028 | If we assumed the switchings of $x_0$ and $x_n$ didn't happen during $m$-sorting, we are trivially done, because the starting and final entries of $B$ are $x_0$ and $x_n$ respectively, and since $x_0 < x_n$, $B$ is $n$-sorted.
0029 | 
0030 | Say $A = \{x_0, \cdots, x_n, \cdots, x_{2n}\}$ is $n$-sorted. We can assume the subarray $\{x_0, \cdots, x_n\}$ is $m$-sorted WLOG and because of what we proved earlier. Suppose now that while $m$-sorting, $x_n$ and $x_{n+m}$ are switched; then $x_{n+m} < x_n$. And then on the last entry, $x_k$ (in the $2n-m$ th position) and $x_{2n}$ are switched. Then $x_{2n} < x_k$.
0031 | 
0032 | After the $m$-sorting is over, the $n$-gap subarray starting at $x_0$ is $\{x_0, x_{n+m}, x_k\}$. We have $x_0 < x_m < x_{n+m} < x_n < x_{2n} < x_k$, where $x_m < x_{n+m}$ is because $A$ is $n$-sorted.
0033 | 
0034 | So, this is proof that if a $2n+1$ array is $m$-sorted after being $n$-sorted, it remains $n$ sorted.
0035 | 
0036 | 
```

## Unchanged challenged quote

```text
Say that after first pass $x_0$ switches place with $x_m$, so the final array $B$ starts with the entry $x_m$ regardless of the position of $x_0$ (which can further switch place with $x_{2m}$ and so on). Thus, $x_m < x_0$.
```

## Original witness (raw recorded text)

Non-degenerate witness (genuine gap m >= 2), smallest of its kind found by exhaustive enumeration:

  N = 5, m = 2, A = (x_0,...,x_4) = [3, 4, 2, 5, 1]

  Gap-m chain through position 0: x_0, x_2, x_4 = 3, 2, 1.
  Hypothesis of the claim holds: at the first insertion step (i = m = 2) we compare x_2 = 2 with x_0 = 3; since 2 < 3 they exchange places, i.e. "x_0 switches place with x_m during the first pass".
  After the full m-sort (gap-2 insertion sort, equivalently sorting each residue chain in place):

  B = m-sort(A) = [1, 4, 2, 5, 3]

  The claim says B[0] == x_m = 2; here B[0] = 1 != 2. In fact B[0] = 1 = x_4 = x_{2m}, the minimum of the whole gap-m chain {x_0, x_m, x_{2m}} = {3, 2, 1} — exactly the failure mode described in the target claim.

Smallest witness overall (degenerate gap m = 1, i.e. plain insertion sort): N = 3, A = [3, 2, 1]; x_1 = 2 < 3 = x_0 so they swap on the first step, but B = [1, 2, 3] and B[0] = 1 = x_2 != x_1 = 2.

The script also verified, over all 36243 counterexamples found, that B[0] always equals min{x_0, x_m, x_{2m}, ...} (0 exceptions), confirming the stated diagnosis rather than merely the negation.

## Why the existing audit rejected that witness

The original A=[3,4,2,5,1] has x_0=3>x_4=1, contrary to the full source hypothesis x_0<x_n.

## Replacement witness (raw recorded text)

Take m=2 and A=[3,5,2,6,1,7,4], indexed x_0,...,x_6. The source hypothesis x_0<x_6 holds because 3<4. At the first gap-2 insertion, x_2=2 swaps with x_0=3. The final gap-2 sorted array is [1,5,2,6,3,7,4], whose first entry is 1 rather than x_2=2. Thus the source claim about the final first entry fails while preserving its original endpoint-order hypothesis.

## Exact selected Lean declarations

Historical: `QEDCert.SE_cs_81391__q.claim_false_on_witness`

```lean
theorem claim_false_on_witness : claimAt mW A = false :=
```

Current: `QEDCert.SE_cs_81391__q.source_hypotheses_and_refutation`

```lean
theorem source_hypotheses_and_refutation :
    nth sourceA 0 < nth sourceA 6 ∧
    hypExchangeB 2 sourceA = true ∧
    msortIns 2 sourceA = [1, 5, 2, 6, 3, 7, 4] ∧
    conclB 2 sourceA = false :=
```

Headers end at `:=`; full definitions and proofs appear in the copied files.


## Historical authenticated compilation

[Complete Lean source](old/Certificate.lean), [receipt](old/RECEIPT.json), [compiler log](old/compile.log), [axiom log](old/axioms.log).

Recorded execution: `2026-09-16T02:33:12.126381+00:00`. Result: `PASS`, exit `0`, trust tier `KERNEL_ONLY`.

Receipt SHA-256: `f5ae484007c171eb889067250f5b54a21def6204dd47ca623a8101bc7b700191`.

- compiled_source: `eed1574d0a6999b23142ee8db58112d50ba46f00cb2f9fa4f3817e0ee5c16ed9`

- compile_log: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

- axiom_log: `9bdcb92cbea534c1ad186199d172c0e2361aa223cd8b891690ce306afa9fcfca`


## Current authenticated compilation

[Complete Lean source](current/Certificate.lean), [receipt](current/RECEIPT.json), [compiler log](current/compile.log), [axiom log](current/axioms.log).

Recorded execution: `2026-09-16T04:58:37.573016+00:00`. Result: `PASS`, exit `0`, trust tier `KERNEL_ONLY`.

Receipt SHA-256: `a7e033cd65e97d2cd93548e3ef738221bd5c03d001b04f41c42d06bd55448e20`.

- compiled_source: `33e7f0491d3cee824902692fa0c42976cc01d8ba3b9d6b985293261d2a29f1d3`

- compile_log: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

- axiom_log: `afb85744c57c5ecf47379f2d4243a3ae9c4e9a34ea976c98e464a3cf2b5437e1`


A successful certificate establishes its encoded proposition. The claim that a witness satisfies the source assumptions is the separately recorded audit judgment. These pairs do not establish a randomized treatment effect or independent human validation.
