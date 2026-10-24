# SE_math_4219732__q

The stored problem, source_context and claim_quote text is identical across this pair. This is not a fresh comparison against the live external source or an independent semantic adjudication.

Both complete certificate files below are copied byte-for-byte from authenticated successful build snapshots. No new compilation was performed. The semantic conclusions are quoted from the existing audit.

## Unchanged source context

```text
0001 | In [this](https://www.cs.cmu.edu/~dga/papers/cuckoo-conext2014.pdf) paper (page 7 Eq. 3) the author derives the following: $$\binom{n}{2b+1}\left( \frac{2}{cn\cdot 2^f}\right)^{2b}=\Omega\left( \frac{n}{4^{bf}}\right)$$
0002 | I have tried to do the same below, but first some preliminaries. This is an analysis for algorithms and therefore constants can be erased. In this example, $b$ is a constant while $f$ is some $f$-bit fingerprint. I assume that $f$ is not treated as a constant here. $n$ is the number of elements and $c$ is just some constant. My take is the following, and note that the binomial coefficients is converted into its lower bound:
0003 | $$\binom{n}{2b+1}\left( \frac{2}{cn\cdot 2^f}\right)^{2b}= \frac{n^{2b+1}}{(2b+1)^{2b+1}} \frac{(2b+1)^{2b+1}}{2^f\cdot cn} = \frac{n}{1}\cdot\frac{1}{4^{f}\cdot n}=\frac{1}{4f}$$ Note that $n^{2b+1}=n^{2b}\cdot n = 2n = n$ because its algorithms and their analysis.. My result above is not the same as the one at the top of this question. How does the author derive that? How is $n$ kept in his result?
```

## Unchanged challenged quote

```text
$$\binom{n}{2b+1}\left( \frac{2}{cn\cdot 2^f}\right)^{2b}= \frac{n^{2b+1}}{(2b+1)^{2b+1}} \frac{(2b+1)^{2b+1}}{2^f\cdot cn} = \frac{n}{1}\cdot\frac{1}{4^{f}\cdot n}=\frac{1}{4f}$$ Note that $n^{2b+1}=n^{2b}\cdot n = 2n = n$
```

## Original witness (raw recorded text)

Take n = 5, b = 1, c = 1, f = 2 (admissible: n >= 2b+1 = 3, b,f >= 1, c > 0). The four quantities the proof chains together with equals signs are, in exact rational arithmetic:
  binom(5,3)*(2/(c*n*2^f))^(2b) = 10*(2/20)^2 = 1/10                        (true LHS)
  (5/3)^3*(2/20)^2 = 5/108                                                  (LHS after the author's own substitution of the binomial lower bound)
  5^3/3^3 * 3^3/(2^2*1*5) = 25/4                                            (first RHS)
  (5/1)*1/(4^2*5) = 1/16                                                    (second RHS)
  1/(4*2) = 1/8                                                             (final RHS)
Claim says 1/10 = 25/4 = 1/16 = 1/8; in fact these are pairwise distinct, with left/right ratios 2/125, 100 and 1/2. The side remark also fails here: n^(2b+1) = 125, 2n = 10, n = 5, so 125 != 10 != 5.
Smallest witness in enumeration order: n = 3, b = 1, c = 1/8, f = 1, where LHS = 64/9 but the first RHS = 36 (ratio 16/81) and the second RHS = 1/4 (ratio 144).
Exhaustively, across all 96720 enumerated assignments the whole chain holds at ZERO points, exactly or even within a factor 10. Moreover the refutation is quantified over every positive real constant c and every constant factor K: for two assignments sharing (b,f), c enters both sides of a link with the same exponent and cancels from the quotient of the two discrepancy ratios, so that quotient is c-free. At (n,b,f) = (9,4,1) vs (160,4,1) the c-free quotient is 1152921504606846976000000000000000/1744146729569927314733951421 ~ 6.6e5 for link 1, 2684354560000000/4782969 ~ 5.6e8 for the lower-bound variant, and 429496729600000000/43046721 ~ 1.0e10 for link 2 (exactly (n/9)^(2b), hence unbounded in n); for the last link, f = 1 vs f = 12 gives 1048576/3 ~ 3.5e5. Since the link can hold within factor K at both points only if K^2 >= that quotient, no c and no constant K repairs any of them.

## Why the existing audit rejected that witness

The source explicitly discards constant factors. A discrepancy at the single finite value n=5 does not refute an eventual asymptotic assertion.

## Replacement witness (raw recorded text)

Keep b=1,c=1,f=2 and let n range over the natural numbers. The same quoted source simplification n^(2b+1) to n would require n^3=O(n). For every real constant C and natural threshold N, choose m>C and n=max(N,m)+2; then n>=N and n^3>C*n. Hence no eventual constant-factor bound exists, refuting the simplification under the source stated asymptotic convention.

## Exact selected Lean declarations

Historical: `SE_math_4219732_q.SE_math_4219732__q_refuted`

```lean
theorem SE_math_4219732__q_refuted :
    decide (5 ≥ 2 * 1 + 1 ∧ 1 ≥ 1 ∧ 2 ≥ 1) = true
    ∧ fracEq trueLhs ⟨1, 10⟩ = true
    ∧ fracEq substitutedLhs ⟨5, 108⟩ = true
    ∧ fracEq firstRhs ⟨25, 4⟩ = true
    ∧ fracEq secondRhs ⟨1, 16⟩ = true
    ∧ fracEq finalRhs ⟨1, 8⟩ = true
    ∧ printedChain = false :=
```

Current: `SE_math_4219732_q.source_asymptotic_refutation`

```lean
theorem source_asymptotic_refutation :
    ¬IsBigO atTop (fun n : ℕ => (n : ℝ)^3) (fun n : ℕ => (n : ℝ)) :=
```

Headers end at `:=`; full definitions and proofs appear in the copied files.


## Historical authenticated compilation

[Complete Lean source](old/Certificate.lean), [receipt](old/RECEIPT.json), [compiler log](old/compile.log), [axiom log](old/axioms.log).

Recorded execution: `2026-09-16T02:35:08.883116+00:00`. Result: `PASS`, exit `0`, trust tier `KERNEL_ONLY`.

Receipt SHA-256: `b0b161f31c84d437b832356862b22372292c81940733705cfde13262537cb84d`.

- compiled_source: `8f83789beaec56d4a7bbbd193ad184504e007f7543043e68ced05d9d3c036b86`

- compile_log: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

- axiom_log: `f54552bc1ea46b96fa66468fe878081b7ff27a88fb6fd5dcd74d9ca0966024c9`


## Current authenticated compilation

[Complete Lean source](current/Certificate.lean), [receipt](current/RECEIPT.json), [compiler log](current/compile.log), [axiom log](current/axioms.log).

Recorded execution: `2026-09-16T04:59:11.714984+00:00`. Result: `PASS`, exit `0`, trust tier `KERNEL_ONLY`.

Receipt SHA-256: `cdef72b17b9be3f4d29a154f1183a3788d1ac48248cabaa2e7004c250faa3db5`.

- compiled_source: `7c769806b5367dee6c07dfbfccc038bb5d8b4b587f6048fa85b57df173e532d6`

- compile_log: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

- axiom_log: `72ee3d904564119523de1d623d805306917b6a70a0b70f061c17ec0c9154284a`


A successful certificate establishes its encoded proposition. The claim that a witness satisfies the source assumptions is the separately recorded audit judgment. These pairs do not establish a randomized treatment effect or independent human validation.
