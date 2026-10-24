# Four replacement records: selected-witness semantics

As of 2026-09-21T00:29:17.996405+00:00. Read-only audit; no Lean compilation, model calls, live-source fetches, or manuscript changes. This is an artifact-based semantic read, not a new independent human judgment. Scope is the four requested records in the fixed 16-case replacement roster, generated **2026-09-20T19:42:55.392754+00:00**. Selection is by recorded replacement outcome, not a random sample or a stage-ablation experiment.

## Finding that changes the proposed interpretation

**Do not describe all four old certificates as proving only source-inadmissible objects.** The old arXiv and ProofWiki selected declarations already concern source-compatible alternatives to their misleading headline prose. The tournament's selected old declaration concerns an out-of-domain object, but the *same archived module* also contains an explicitly admissible second witness. Only the population case clearly exhibits the specified omitted hypothesis in the old main object's formal admissibility predicate. This does not rehabilitate every old packet: it locates the mismatch more accurately.

| Record | Old prose headline | What the archived Lean actually states | Current repair | Accurate characterization |
|---|---|---|---|---|
| arXiv 1304.1796v2 | `a=3,p₀=1` | Selected theorem uses source numerator `(k−1)^k`, denominator `k^k`, positive clearing denominator, and a family beyond every threshold | Direct real-valued theorem with the source definition of `p₀`, for every `k≥3` | Prose/selected-object mismatch and an explicit formal bridge improvement; not an old theorem setting the source probability to 1 |
| MSE 1794123 | Mixture `(n,p,w)=(2,3/4,1/2),(3,1/2,1/2)` | Main witness reverses the claimed averages, but its formal well-formedness predicate omits overall sex balance; old theorems give unequal expected counts `3/2` and `1` | New mixture has equal expected sex counts `10/7` and averages `13/16<15/16` | Genuine omitted source hypothesis for the old main object; new formal result is an expected-mass statement |
| MSE 2605396 | `n=5,k=2` | Selected witness is outside `n≥2k>4`; additional declarations in the same old file prove an admissible `n=6,k=3` witness and the same local count failure | Selects the `n=6,k=3` object with Mathlib tournament definitions | Headline/selected-declaration defect already addressed elsewhere in the archived module; replacement is not first discovery of an admissible witness |
| ProofWiki 69483 | `r=2,j=0`, without `n,s` | Selected theorem already fixes `r=s=n=3,j=1`, checks the nonzero bracket, and computes full adjacent lines `9≠36` | Keeps that object; uses `Nat.choose` and additionally checks the induction premise | Prose/selected-object mismatch and formal strengthening; not a selected old Lean theorem about `j=0` |

In every one of these four rows, the roster binds byte-identical old/current `problem`, `source_context`, and `claim_quote`. That is an **artifact identity result**, not a proof that the excerpts include all source assumptions or that the formalization is faithful.

## 1. arxiv_1304.1796v2__source_enriched_codex

Evidence: [archived dossier](../../qedbench_certificate_availability_triage/validation/dossiers/arxiv_1304.1796v2__source_enriched_codex.tex), [current packet](../../qedbench_certificate_availability_triage/validation/human_review_20260915/confirmed_release/packets/arxiv_1304.1796v2__source_enriched_codex.json), [current Lean](../../partB_feasibility/arxiv_certificates/arxiv_1304.1796v2__source_enriched_codex.lean).

**Exact source condition and target.** Dossier line 58, archived source line 0952, says `Using $p_0 = (1 - 1/k)^{k} < e^{-1}$`. Lines 69–70 (source 0963–0964) contain

```tex
& \le p_0 \left(1 + \frac{2}{k - 1}\right)^{a - 1} && \mbox{For sufficiently large $k$} \\
& \le p_0 \left(1 + \frac{2 (a - 1)}{k - 1}\right)
```

The headline at dossier line 97 sets `a=3,p₀=1`. Read literally as the source probability, that conflicts with the definition; this is the recorded release-audit reason. However, the old certificate does **not** simply formalize that literal probability choice. Its comment at dossier lines 158–166 says that `p₀=1` is a canceled normalization and describes the actual source numerator and denominator.

**Old selected declaration.** Namespace `Arxiv13041796v2SourceEnrichedCodex`; dossier line 254:

```lean
theorem refutes_sufficiently_large_displayed_inequality :
    (forall N : Nat, exists k a t d : Nat,
      sourceHypotheses N k a t d /\
      0 < pNumerator k d /\
      0 < pDenominator k /\
      0 < commonDenominatorAThree k d /\
      clearedAThreeRight k d < clearedAThreeLeft k d /\
      Not (claimedDisplayedStepAtAThree k d)) /\
    terraConcreteWitness := by
```

Its definitions select `k=N+4`, `a=t=3`, `d=k−1`, with `N<k`, `1≤a`, `t≤a`, `a<k`, and `d>0`; `pNumerator=d^k`, `pDenominator=k^k`, common denominator `k^k*d²`. The compared expressions are `d^k*(d+2)^2` and `d^k*d*(d+4)`. `square_gap` and `cleared_gap` establish the positive gap. Thus the selected formal object already uses the source probability's numerator/denominator and unbounded `k`, rather than assuming its value is 1. The conversion from real/rational division to this natural-number inequality is explained in the old comment; no formal real-division bridge is present in that old declaration.

**Current declaration and scope.** `refutes_upper_bound_with_source_probability` at current Lean line 6 defines `p₀ k : ℝ := (1−1/(k:ℝ))^k` and proves for every `k≥3` that it is positive and that the displayed comparison at `a=3` is strictly reversed. This improves representation and makes the probability bridge explicit in the formal statement. Both versions concern the displayed algebraic step. Neither selected theorem formalizes the entire conditional distribution or refutes the original lemma's ultimate conclusion.

**Classification:** misleading/incomplete prose-to-selected-certificate binding, followed by a stronger direct formal representation. The old selected theorem is a counterexample to the proposed classification “old formal object uses inadmissible `p₀=1`.”

## 2. mse_1794123__ans1794617

Evidence: [archived dossier](../../qedbench_certificate_availability_triage/validation/dossiers/mse_1794123__ans1794617.tex), [current packet](../../qedbench_certificate_availability_triage/validation/human_review_20260915/confirmed_release/packets/mse_1794123__ans1794617.json), [current Lean](../../partB_feasibility/mse_certificates/mse_1794123__ans1794617.lean).

**Exact source condition.** Dossier line 55: “There are a large number of individuals, of whom half are men and half are women.” The challenged answer says: “If the likelihood of having boys does depend on the family, men on average have more brothers, not fewer.” The complete question also describes families and independent sex draws within a family; the answer excludes stopping rules conditioned on realized sexes.

**Old selected object and declaration.** Old namespace `MSE_1794123`, `W1` mixes family types `(2,3/4)` and `(3,1/2)` with equal weights. The selected header at dossier line 153 is:

```lean
theorem W1_conclusion_fails : claimConclusion W1 = false :=
```

At dossier line 573, `claimConclusion P := qlt (womenAvg P) (menAvg P)`. The stronger `refuted_W1 : refutesClaim W1 = true` also appears at line 680. Crucially, the `wfPop` definition at lines 554–560 requires nonempty well-formed family types, normalized weights, i.i.d. sampling, positive denominators and valid averages, but **does not require `menDen P = womenDen P`**. The old declarations themselves expose the omitted assumption:

```lean
theorem W1_men_moments :
    (qeqB (menNum W1) (qmk 21 16) && qeqB (menDen W1) (qmk 3 2)) = true := by decide
theorem W1_women_moments :
    (qeqB (womenNum W1) (qmk 15 16) && qeqB (womenDen W1) (qmk 1 1)) = true := by decide
```

`W1_men_avg`, `W1_women_avg`, and `W1_inequality_reversed` certify `7/8<15/16`. Hence the defect is not an arithmetic failure to reverse the conclusion. It is that the old main object passes a weakened formal admissibility test while violating the question's balance condition, as the existing release audit reports.

**Current object and scope.** The replacement mixes `(n,p,w)=(2,3/4,5/7)` and `(5,1/4,2/7)`. It enumerates independent product-weighted sex vectors using rational arithmetic. `equal_sex_population` at line 103 gives both population counts as `10/7`; selected `certificate` at line 113 includes normalized probability masses, equality and positivity of those counts, and average brothers `13/16<15/16`.

Here `populationCount` is an **expected weighted population count**, as its definition at line 45 shows. The theorem does not assert that every realized random finite population has exactly equal sex counts. Describing the current result as an exact theorem about the encoded probability mixture is justified; interpreting that mixture as the source's population model remains a source/formalization judgment. Do not silently strengthen the certificate to a pathwise balance claim.

**Classification:** omitted source hypothesis in the old formal model; new source-balanced probability-mixture witness under its stated expected-mass interpretation. This is the clearest of these four examples of the intended hypothesis-fidelity phenomenon.

## 3. mse_2605396__ans2605536

Evidence: [archived dossier](../../qedbench_certificate_availability_triage/validation/dossiers/mse_2605396__ans2605536.tex), [current packet](../../qedbench_certificate_availability_triage/validation/human_review_20260915/confirmed_release/packets/mse_2605396__ans2605536.json), [current Lean](../../partB_feasibility/mined_certificates/mse_2605396__ans2605536.lean).

**Exact source condition and target.** Dossier line 65 (source 0005): “Here is a general proof that a total order exists for any $n$ teams which are $k$ absolute whenever $n \geq 2k > 4$.” The challenged local sentence at line 67 (source 0007) is: “This gives you that there are teams with $k+1, k+2, \dots, n$ wins.” The source defines `k`-absolute by top and bottom elements in every `k`-subset and explicitly calls out `k>2` in its auxiliary lemma.

**Old selected declaration.** `mse_2605396__ans2605536_witness5_refutes` (dossier lines 125 and 372) evaluates the transitive five-team tournament at `k=2`; its win vector is `[4,3,2,1,0]`. It falsifies the printed top-peel count `[3,4,5]`, but does not establish `2*k>4`, which is false for this object. The release audit's reason is correct **for that headline/selected witness**.

**The same old module already contains an admissible alternative.** Its own comment at lines 400–405 explicitly acknowledges the problem with `n=5,k=2` and selects `n=6,k=3`. The declaration at line 441 is:

```lean
theorem mse_2605396__ans2605536_witness6_hypotheses_hold :
    (kAbsolute 6 (transTour 6) 3 = true)
  ∧ (kAbsolute 6 (transTour 6) 4 = true)
  ∧ (kAbsolute 6 (transTour 6) 5 = true)
  ∧ (6 ≥ 2 * 3) ∧ (2 * 3 > 4)
  ∧ ((pairsLt 6).length = 15)
  ∧ (natListEq (winVec 6 (transTour 6)) [5, 4, 3, 2, 1, 0] = true) := by decide
```

`mse_2605396__ans2605536_witness6_refutes` at line 453 certifies the claimed `[4,5,6]` counts are not realized, the corrected `[3,4,5]` counts are, no team has six wins, and the actual total is 15 rather than the printed count's 21. The file therefore cannot fairly be categorized as containing only out-of-scope witnesses. The old `kAbsolute`, top/bottom and tournament representation are local Boolean/list definitions; comparison with the source remains a semantic read, not an automatic consequence of compilation.

**Current declaration and scope.** At current Lean line 26, `admissible_tournament_refutes_printed_win_count` packages the `6,3` inequalities, irreflexive complete tournament properties, top/bottom elements for every three-element subset, and the absence of a six-win team, using `Digraph`, `Fin 6` and `Finset`. This is a more direct selected admissible certificate for the local counting error. It does not refute the total-order conclusion or the particular 93-team question: the old file even has `mse_2605396__ans2605536_conclusion_of_the_answer_is_true` at line 514, verifying the relevant distinct-win-count conclusion on both old examples.

**Classification:** an out-of-domain selected headline plus an already present source-compatible alternative; the repair changes selected presentation and formal representation. Do not say the replacement was the first admissible object in the old artifact.

## 4. proofwiki_69483

Evidence: [archived dossier](../../qedbench_certificate_availability_triage/validation/dossiers/proofwiki_69483.tex), [current packet](../../qedbench_certificate_availability_triage/validation/human_review_20260915/confirmed_release/packets/proofwiki_69483.json), [current Lean](../../partB_feasibility/diverse_certificates/proofwiki_69483.lean).

**Exact archived transition.** Dossier line 67 (source 0052) is `C(r,j+1)*B`; line 70 (source 0055) is `(j+2)*(r−j+2)*C(r,j+2)*B`, where the same bracket in both archived lines is

```tex
\paren {j + 1} \paren {n - j} \dbinom s {n - j}
+ \dbinom s {n - j - 1} \paren {n r - \paren {r + s} \paren {j + 1} }
```

The existing release audit says the source induction paragraph imposes `j≥1`. **The dossier's stored source-context window only includes lines 0043–0067 and does not contain that induction paragraph.** The referenced raw `qedbench_certificate_availability_triage/data/records_proofwiki.jsonl` was not available at this path during this read. Full and blind machine-check input copies repeat the headline witness, not the missing paragraph. Accordingly `j≥1` is attributed here to the existing source audit, not presented as a freshly located verbatim source quotation. The exact adjacent expressions above are directly available.

**Old prose versus selected formal object.** The headline at dossier line 97 starts `r=2,j=0`, without `n,s`, but the same paragraph already mentions `r=3,j=1` as an alternative. The full archived Lean fixes `r=3,j=1,n=3,s=3` at lines 186–189 and uses an integer-valued bracket. Its selected declaration `ProofWiki69483.refutes_line_0052_to_0055` at line 213 includes:

```lean
1 <= j /\ j + 1 <= r /\ j + 2 <= r /\
choose r (j + 1) > 0 /\ choose r (j + 2) > 0 /\
choose r (j + 1) = 3 /\ choose r (j + 2) = 1 /\
unchangedBracket = 3 /\ line0052 = 9 /\ line0055 = 36 /\
line0052 != line0055 /\
Not assertedLocalEquality /\ Not assertedLineTransition
```

Thus the old selected theorem already checks `j≥1`, all four witness parameters, a nonzero bracket, and complete line inequality. It is not a theorem about the `r=2,j=0` headline. The old `choose` is locally defined by the ordinary Pascal recursion rather than identified by a Lean bridge with Mathlib's `Nat.choose`.

**Current declaration and scope.** The current file uses `abbrev choose := Nat.choose` with the same object and essentially the same selected transition theorem at line 63. It additionally proves `induction_hypothesis_at_witness` at line 97: both sides of the preceding finite-sum induction premise are 36. This is a useful formal strengthening and resolves the prose/certificate mismatch, but not a newly invented admissible object. The selected result attacks the local transition, not the page's summation theorem.

**Classification:** missing complete witness in the prose and a mismatch with the already stronger selected Lean object; later use of standard definitions and an explicit induction-premise theorem. A blanket “old certificate was inadmissible because `j=0`” is false about the actual selected declaration.

## Compilation and version boundary

The fixed roster has **no authenticated retained old compile receipt for any of these four** (`old_compile_bound=false`; empty `old_authenticated_receipts`). This read recovered the second `Vlean` block from each archived dossier and rechecked its byte hash against the frozen historical Lean hash; all four match exactly. It also checked current Lean and current receipt file hashes against the roster. The roster's current certificates have authenticated PASS/exit-0 receipts and selected `KERNEL_ONLY` declarations. Those are the compilation facts available in this audit, distinct from the semantic findings above.

Claude's separately requested fresh compilation can establish that the archived bytes compile under the recorded reproduction toolchain. It cannot retroactively supply an original-time receipt, and a successful file compile cannot select which prose object or theorem justifies the objection. Any new reproduction receipts should be attached as a separately dated layer rather than overwriting the frozen old receipt-availability fields.

### Verified byte bindings (no recompilation)

- `arxiv_1304.1796v2__source_enriched_codex`: old Lean 6944 bytes, SHA-256 `0d81d7c73861d8faf5874abfe1267a73454f54e9b9483bb7d662761b54f60405`; current Lean `051af047d0a85b476a9bd1892b970418a85a12232e56534a28cba07180a7bcdb`. Current receipt [`arxiv_1304_1796v2__source_enriched_codex_4d6f996d6f.json`](../../qedbench_certificate_availability_triage/validation/human_review_20260915/lean_build/final_selected/results/arxiv_1304_1796v2__source_enriched_codex_4d6f996d6f.json), SHA-256 `524dfc75c4760601396fdc319fd9d46a01c3749e3094f6e760282837720ec6dd`.
- `mse_1794123__ans1794617`: old Lean 29343 bytes, SHA-256 `931cbf518de808987c233da5ed12658e1c1364fd19306bf021abaee73c60e88f`; current Lean `f891a934834b8b2687ed40935776de65d1b623c106b8eb3ec7908a79048c3f46`. Current receipt [`mse_1794123__ans1794617_d4000538b3.json`](../../qedbench_certificate_availability_triage/validation/human_review_20260915/lean_build/resumed_20260917/results/mse_1794123__ans1794617_d4000538b3.json), SHA-256 `29371eec1835a6c3413a0b7dcdb60202f456f4e1028eb9b9e8a1fb26bd85cfc1`.
- `mse_2605396__ans2605536`: old Lean 25086 bytes, SHA-256 `a9193133301c2b9464c47975c8b8d466b9b476da440505f1f37ae994e5eda655`; current Lean `64e5953e8ac2ed8dab67e735ebe5fc8ac88920e1d54550f133b8fc006f3f0e1f`. Current receipt [`mse_2605396__ans2605536_9236914a77.json`](../../qedbench_certificate_availability_triage/validation/human_review_20260915/lean_build/resumed_20260917/results/mse_2605396__ans2605536_9236914a77.json), SHA-256 `533202151a81eccf0d8caf64cbc4301b99415524a9584c1731dcbd51be32011f`.
- `proofwiki_69483`: old Lean 3382 bytes, SHA-256 `d552699f918680244385373295173c99be83da9571cf8798a54f456d48b0ea47`; current Lean `025359ed77894637c93ac171149bf2f73d706525c31986262f64db1f6da1899a`. Current receipt [`proofwiki_69483_22402152ec.json`](../../qedbench_certificate_availability_triage/validation/human_review_20260915/lean_build/final_selected/results/proofwiki_69483_22402152ec.json), SHA-256 `d531799fe6ecf5d06aa1e91caa97e2a56a45b94d199347ceef4611e9289b7d92`.

## Manuscript-safe inference

Suggested concise claim: **“Replacement audits exposed several different binding failures: omitted source hypotheses, stale prose witnesses, and selected declarations that differed from the packet's headline object. In some archived modules, an admissible alternative was already formalized. Checking the file alone therefore does not establish which objection the record supports.”**

A stronger particular example can use the population case's omitted equal-sex condition (with its expected-mass qualification), or the separately certified endpoint-order bridge. Do not count these four as four independent cases of kernel-accepted source-inadmissible *selected formal witnesses*. Do not treat all 16 replacement labels as that homogeneous class, estimate a corpus error rate from them, or claim that this read demonstrates a causal repair yield.
