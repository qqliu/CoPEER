# mse_811862__ans811879

The stored problem, source_context and claim_quote text is identical across this pair. This is not a fresh comparison against the live external source or an independent semantic adjudication.

Both complete certificate files below are copied byte-for-byte from authenticated successful build snapshots. No new compilation was performed. The semantic conclusions are quoted from the existing audit.

## Unchanged source context

```text
0059 | \langle Tr(H^{4})\rangle=\langle H_{ij}H_{jk}\rangle \langle H_{kl}H_{li}\rangle + \langle H_{ij} H_{kl}\rangle \langle H_{jk}H_{li}\rangle + \langle H_{ij}H_{li}\rangle \langle H_{jk} H_{kl} \rangle 
0060 | \end{equation}
0061 | where a contraction is defined by 
0062 | \begin{equation}
0063 | \langle H_{ij}H_{kl}\rangle=\delta_{il} \delta_{jk}.
0064 | \end{equation}
0065 | Using this result and contracting indices we can write 
0066 | \begin{equation}
0067 | \langle Tr(H^{4})\rangle=\sum_{i,j,k,l} (\delta_{ik}\delta_{jj}\delta_{ki}\delta_{ll}+\delta_{il}\delta_{kj}\delta_{ji}\delta_{lk}+\delta_{ii}\delta_{jl}\delta_{lj}\delta_{kk})=2N^3+N,\qquad (\text{answer  to  c})
0068 | \end{equation}
0069 | since one of the contractions only has one free index it contributes N.  The other two contractions both contribute N$^3$.  The 6th moment of the distribution has 15 possibilities to contract so I will omit this derivation.  In general, the nth moment is written by expanding the product as
0070 | \begin{equation}
0071 | \langle Tr(H^{2k})\rangle= \sum_{i_1,i_2,...i_{2k}}H_{i_1 i_2} H_{i_2 i_3}...H_{i_{2k}i_1}=\frac{1}{k+1}\binom {2k} {k}=C_k \qquad (\text{general answer to A,B,C})
0072 | \end{equation}
0073 | where C$_{k}$ is the Catalan numbers which represents the k different ways to match the entries.  This result can be plugged into the average resolvent expression and summed to give
0074 | \begin{equation}
0075 | \langle G(z)\rangle = \frac{1}{N} \sum_{k=0}^{\infty} z^{-(2k+1)}\langle 
0076 | Tr(H^{2k})\rangle=\frac{1}{2}\big(z-\sqrt{z^2+4}\big).
0077 | \end{equation}
0078 | This equality is obtained by using contractions and expanding the average resolvent for large z as done above \begin{equation}
0079 | \langle G(z) \rangle=\bigg\langle \frac{1}{N} \big(z^{-1}+z^{-2}TrH+z^{-3}Tr H^2 +z^{-4} Tr H^3 + O(N)\big )\bigg \rangle.
0080 | \end{equation}
0081 | Since the odd moments vanish due to symmetry, the even moments are calculated as shown above.  We obtain
0082 | \begin{equation}
0083 | \langle G(z) \rangle= z^{-1}+z^{-1}\langle G(z) \rangle ^2
```

## Unchanged challenged quote

```text
\langle Tr(H^{2k})\rangle= \sum_{i_1,i_2,...i_{2k}}H_{i_1 i_2} H_{i_2 i_3}...H_{i_{2k}i_1}=\frac{1}{k+1}\binom {2k} {k}=C_k
```

## Original witness (raw recorded text)

k = 1, N = 2 (smallest witness; 29 of the 30 exhaustively tested (k,N) pairs falsify the claim). Using the proof's own evaluation rule <H_ij H_kl> = delta_il delta_jk together with Gaussian/Wick pairing, the exactly computed integer is <Tr(H^2)> = sum_{i,j} <H_ij H_ji> = sum_{i,j} delta_ii delta_jj = N^2 = 4, whereas the asserted value is C_1 = binom(2,1)/2 = 1. 4 != 1. Further exact witnesses from the same exhaustive table: (k=2, N=2): <Tr H^4> = 18 vs C_2 = 2; (k=3, N=2): <Tr H^6> = 120 vs C_3 = 5; (k=4, N=3): <Tr H^8> = 5355 vs C_4 = 14; (k=5, N=6): <Tr H^10> = 2521260 vs C_5 = 42. The only pair where the asserted equality holds is the degenerate (k=1, N=1).

## Why the existing audit rejected that witness

The original N=2,k=1 covariance model was not the real symmetric Gaussian ensemble in the source.

## Replacement witness (raw recorded text)

N=1,k=2, with the 1x1 real symmetric matrix whose only entry is a standard real Gaussian. Its second moment is 1 and its fourth trace moment is 3, different from Catalan(2)=2.

## Exact selected Lean declarations

Historical: `MSE_811862.claim_fails_1_2`

```lean
theorem claim_fails_1_2 : claimHolds 1 2 = false :=
```

Current: `MSE811862.certificate`

```lean
theorem certificate :
    (∀ x : ℝ, (scalarMatrix x).IsSymm) ∧
    (∫ x : ℝ, x ∂gaussianReal 0 1) = 0 ∧
    (∫ x : ℝ, Matrix.trace ((scalarMatrix x)^2) ∂gaussianReal 0 1) = 1 ∧
    (∫ x : ℝ, Matrix.trace ((scalarMatrix x)^4) ∂gaussianReal 0 1) = 3 ∧
    catalan 2 = 2 ∧
    (∫ x : ℝ, Matrix.trace ((scalarMatrix x)^4) ∂gaussianReal 0 1) ≠ (catalan 2 : ℝ) :=
```

Headers end at `:=`; full definitions and proofs appear in the copied files.


## Historical authenticated compilation

[Complete Lean source](old/Certificate.lean), [receipt](old/RECEIPT.json), [compiler log](old/compile.log), [axiom log](old/axioms.log).

Recorded execution: `2026-09-16T02:33:16.336620+00:00`. Result: `PASS`, exit `0`, trust tier `KERNEL_ONLY`.

Receipt SHA-256: `d8c0232379b7d589b64f30fa20f24c6a6bd44d2d2f2e15c1eab6f1d493187ac6`.

- compiled_source: `454e0803f59e364bcf3ea4b263737b37871eebda471ca0c7fb97f5bc3a6e7295`

- compile_log: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

- axiom_log: `68e0e0ac25c669e756c555f76a743f7ed56f7439e6c5c080f00926d56dcc665d`


## Current authenticated compilation

[Complete Lean source](current/Certificate.lean), [receipt](current/RECEIPT.json), [compiler log](current/compile.log), [axiom log](current/axioms.log).

Recorded execution: `2026-09-17T03:36:25.694884+00:00`. Result: `PASS`, exit `0`, trust tier `KERNEL_ONLY`.

Receipt SHA-256: `cf9a026c07518e8059eea780db9d8186e6a0ac93c12402c9f29fd8616478d8c0`.

- compiled_source: `0855e62d356ae2e7a22a3fdee7a07946b619036e1f450c05672210de9ed5f0b0`

- compile_log: `9498ff88965605bb4252d89800ccab4bce5816dbb4908ce692a5c6d3ac36bcb7`

- axiom_log: `50eda689f113926e2f7abdb2704636deb913757c338ed3c24526d7bebd371e83`


A successful certificate establishes its encoded proposition. The claim that a witness satisfies the source assumptions is the separately recorded audit judgment. These pairs do not establish a randomized treatment effect or independent human validation.
