/-
Explanation census, record SE_cs_13118__a13122 : Mathlib file (reals and arbitrary fields).

Outside the frozen 285-record release; the released certificate
`validation/human_review_20260915/lean/SE_cs_13118__a13122.lean` is untouched. Its single
theorem `real_sum_counterexample` is restated here VERBATIM (statement and proof). The released
file has no definitions; its sum has the shape `∑ k ∈ Finset.Icc 1 2, (2:ℝ)^k`, and `Sigma` below
is that shape with the upper limit `n - 1` left general, so that
`Sigma (fun k => (2:ℝ)^k) 3` is the released sum by `rfl`.

Why Mathlib: the dossier's "every c != 1" and the released certificate are about real numbers,
which core Lean does not have. The core companion `SE_cs_13118_a13122_explanation.lean` proves
the integer versions under Lean 4.34.0 and 4.30.0.

The universal theorems are proved over an arbitrary field `K` (the dossier does not name the
domain of `c`); `family_real` is the ordered reading "smaller by exactly 1" over ℝ.
-/
import Mathlib
namespace SE_cs_13118_a13122_explanation_real

/-- The source's operator `Sigma(T)(n) = ∑_{k=1}^{n-1} T(k)` in the released `Finset.Icc` shape. -/
def Sigma {K : Type*} [Field K] (T : ℕ → K) (n : ℕ) : K := ∑ k ∈ Finset.Icc 1 (n - 1), T k

theorem Sigma_succ {K : Type*} [Field K] (T : ℕ → K) (m : ℕ) :
    Sigma T (m + 2) = Sigma T (m + 1) + T (m + 1) := by
  unfold Sigma
  simp [Finset.sum_Icc_succ_top]

/-- The released selected declaration, statement and proof verbatim. -/
theorem real_sum_counterexample :
    (∑ k ∈ Finset.Icc 1 2, (2 : ℝ)^k) = 6 ∧
    ((2 : ℝ)^3 - 1)/(2 - 1) = 7 ∧
    (∑ k ∈ Finset.Icc 1 2, (2 : ℝ)^k) ≠ ((2 : ℝ)^3 - 1)/(2 - 1) := by
 rw [show Finset.Icc 1 2 = ({1,2} : Finset ℕ) from by decide]
 norm_num

/-- The released sum is `Sigma (2^·) 3`, definitionally. -/
theorem released_sum_is_Sigma :
    Sigma (fun k => (2 : ℝ) ^ k) 3 = ∑ k ∈ Finset.Icc 1 2, (2 : ℝ)^k := rfl

/-- (a) The local claim, read universally on its domain, is false (released witness reused). -/
theorem claim_refuted :
    ¬ ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n →
        Sigma (fun k => c ^ k) n = (c ^ n - 1) / (c - 1) := by
  intro h
  have h3 := h 2 3 (by norm_num) (by norm_num)
  rw [released_sum_is_Sigma] at h3
  exact real_sum_counterexample.2.2 h3

/-- (c) Repair, division-free: every `c` (including `c = 1`), every `n ≥ 1`. -/
theorem repair_divfree {K : Type*} [Field K] (c : K) (n : ℕ) (hn : 1 ≤ n) :
    (c - 1) * Sigma (fun k => c ^ k) n = c ^ n - c := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  clear hn
  induction m with
  | zero => simp [Sigma]
  | succ m ih =>
    rw [Sigma_succ, mul_add, ih]
    ring

/-- (c) Repair as the dossier writes it: `∑_{k=1}^{n-1} c^k = (c^n - c)/(c - 1)`. -/
theorem repair {K : Type*} [Field K] (c : K) (n : ℕ) (hn : 1 ≤ n) (hc : c ≠ 1) :
    Sigma (fun k => c ^ k) n = (c ^ n - c) / (c - 1) := by
  have h := repair_divfree c n hn
  have hc' : c - 1 ≠ 0 := sub_ne_zero.mpr hc
  rw [eq_div_iff hc', mul_comm]
  exact h

/-- Honesty about triviality: the repair is an instance of the library lemma `geom_sum_Ico`
(`∑ i ∈ Ico m n, x^i = (x^n - x^m)/(x - 1)`) at `m = 1`. -/
theorem repair_is_library_instance {K : Type*} [Field K] (c : K) (n : ℕ) (hn : 1 ≤ n)
    (hc : c ≠ 1) : ∑ k ∈ Finset.Icc 1 (n - 1), c ^ k = (c ^ n - c) / (c - 1) := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  have := geom_sum_Ico hc (show 1 ≤ m + 1 by omega)
  rw [pow_one] at this
  rw [← this]
  congr 1

/-- The repair at `c = 2` over ℝ: the dossier's "the correct value is 2^n - 2". -/
theorem repair_two (n : ℕ) (hn : 1 ≤ n) : Sigma (fun k => (2 : ℝ) ^ k) n = 2 ^ n - 2 := by
  rw [repair 2 n hn (by norm_num)]
  norm_num

/-- (b) Family over any field: at EVERY `c ≠ 1`, `n ≥ 1`, claimed − actual = 1, so the claim fails. -/
theorem family {K : Type*} [Field K] (c : K) (n : ℕ) (hn : 1 ≤ n) (hc : c ≠ 1) :
    (c ^ n - 1) / (c - 1) - Sigma (fun k => c ^ k) n = 1 ∧
    Sigma (fun k => c ^ k) n ≠ (c ^ n - 1) / (c - 1) := by
  have hc' : c - 1 ≠ 0 := sub_ne_zero.mpr hc
  have hd : (c ^ n - 1) / (c - 1) - Sigma (fun k => c ^ k) n = 1 := by
    rw [repair c n hn hc, ← sub_div]
    rw [div_eq_one_iff_eq hc']
    ring
  refine ⟨hd, fun heq => ?_⟩
  rw [← heq, sub_self] at hd
  exact zero_ne_one hd

/-- (b) Family over ℝ in the dossier's ordered wording: the true sum is SMALLER by exactly 1. -/
theorem family_real (c : ℝ) (n : ℕ) (hn : 1 ≤ n) (hc : c ≠ 1) :
    Sigma (fun k => c ^ k) n = (c ^ n - 1) / (c - 1) - 1 ∧
    Sigma (fun k => c ^ k) n < (c ^ n - 1) / (c - 1) := by
  have h := (family c n hn hc).1
  constructor <;> linarith

/-- (d) Exactness, division-free: for `n ≥ 1` the claimed identity holds iff `c = 1`
(the one value at which the source's quotient is undefined). -/
theorem exact {K : Type*} [Field K] (c : K) (n : ℕ) (hn : 1 ≤ n) :
    (c - 1) * Sigma (fun k => c ^ k) n = c ^ n - 1 ↔ c = 1 := by
  rw [repair_divfree c n hn]
  constructor
  · intro h
    exact sub_right_injective h
  · rintro rfl; rfl

/-- (d) The repair constant is forced: `(c^n - a)/(c - 1)` equals the sum iff `a = c`. -/
theorem offset_exact {K : Type*} [Field K] (c a : K) (n : ℕ) (hn : 1 ≤ n) (hc : c ≠ 1) :
    Sigma (fun k => c ^ k) n = (c ^ n - a) / (c - 1) ↔ a = c := by
  have hc' : c - 1 ≠ 0 := sub_ne_zero.mpr hc
  rw [repair c n hn hc, div_left_inj' hc']
  constructor
  · intro h; exact (sub_right_injective h).symm
  · rintro rfl; rfl

/-- `n ≥ 1` cannot be dropped from `family`: with truncated `n - 1` both sides are 0 at `n = 0`. -/
theorem n_zero_claim_holds {K : Type*} [Field K] (c : K) :
    Sigma (fun k => c ^ k) 0 = (c ^ 0 - 1) / (c - 1) := by
  simp [Sigma]

/-- `n ≥ 1` cannot be dropped from `repair`: at `n = 0` the repaired formula is `-1`, the sum is 0. -/
theorem n_zero_repair_fails {K : Type*} [Field K] (c : K) (hc : c ≠ 1) :
    Sigma (fun k => c ^ k) 0 ≠ (c ^ 0 - c) / (c - 1) := by
  have hc' : c - 1 ≠ 0 := sub_ne_zero.mpr hc
  have e : (c ^ 0 - c) / (c - 1) = -1 := by
    rw [div_eq_iff hc']; ring
  rw [e]
  simp [Sigma]

theorem Sigma_one (n : ℕ) : Sigma (fun k => (1 : ℝ) ^ k) n = ((n - 1 : ℕ) : ℝ) := by
  simp [Sigma]

/-- (d) Complete description over ℝ × ℕ of where the division-form claim holds in Lean's
totalised arithmetic (`x / 0 = 0`, truncated `n - 1`): only at `n = 0` (outside the source's
index range) and at `(c, n) = (1, 1)` (where the source's quotient is `0/0`). -/
theorem exact_totalised (c : ℝ) (n : ℕ) :
    Sigma (fun k => c ^ k) n = (c ^ n - 1) / (c - 1) ↔ n = 0 ∨ (c = 1 ∧ n = 1) := by
  by_cases hn : n = 0
  · subst hn
    exact ⟨fun _ => Or.inl rfl, fun _ => n_zero_claim_holds c⟩
  · have hn1 : 1 ≤ n := by omega
    by_cases hc : c = 1
    · subst hc
      rw [Sigma_one, sub_self, div_zero]
      constructor
      · intro h
        have h0 : n - 1 = 0 := by exact_mod_cast h
        exact Or.inr ⟨rfl, by omega⟩
      · rintro (h | ⟨_, h⟩)
        · exact absurd h hn
        · subst h; simp
    · have hf := (family c n hn1 hc).2
      constructor
      · intro h
        exact absurd h hf
      · rintro (h | ⟨h, _⟩)
        · exact absurd h hn
        · exact absurd h hc

/-- (d) Complete description over ℝ × ℕ of where the REPAIRED formula holds in totalised
arithmetic: on the dossier's domain (`c ≠ 1`, `n ≥ 1`), plus the `0/0` artefacts `c = 1`, `n ≤ 1`. -/
theorem repair_totalised (c : ℝ) (n : ℕ) :
    Sigma (fun k => c ^ k) n = (c ^ n - c) / (c - 1) ↔ (c ≠ 1 ∧ 1 ≤ n) ∨ (c = 1 ∧ n ≤ 1) := by
  by_cases hc : c = 1
  · subst hc
    rw [Sigma_one, sub_self, div_zero]
    constructor
    · intro h
      have h0 : n - 1 = 0 := by exact_mod_cast h
      exact Or.inr ⟨rfl, by omega⟩
    · rintro (⟨h, _⟩ | ⟨_, h⟩)
      · exact absurd rfl h
      · have h0 : n - 1 = 0 := by omega
        rw [h0]; simp
  · by_cases hn : 1 ≤ n
    · exact ⟨fun _ => Or.inl ⟨hc, hn⟩, fun _ => repair c n hn hc⟩
    · have hn0 : n = 0 := by omega
      subst hn0
      constructor
      · intro h
        exact absurd h (n_zero_repair_fails c hc)
      · rintro (⟨_, h⟩ | ⟨h, _⟩)
        · omega
        · exact absurd h hc

/-- Negative control from the dossier: the Delta half of the quoted sentence is true. -/
theorem delta_control {K : Type*} [Field K] (c : K) (n : ℕ) :
    c ^ (n + 1) - c ^ n = (c - 1) * c ^ n := by ring

/-- The dossier's closing remark: with lower limit 0 the quoted formula is true. -/
theorem alt_reading {K : Type*} [Field K] (c : K) (n : ℕ) (hc : c ≠ 1) :
    ∑ k ∈ Finset.range n, c ^ k = (c ^ n - 1) / (c - 1) := geom_sum_eq hc n

end SE_cs_13118_a13122_explanation_real

#print axioms SE_cs_13118_a13122_explanation_real.real_sum_counterexample
#print axioms SE_cs_13118_a13122_explanation_real.claim_refuted
#print axioms SE_cs_13118_a13122_explanation_real.repair_divfree
#print axioms SE_cs_13118_a13122_explanation_real.repair
#print axioms SE_cs_13118_a13122_explanation_real.repair_is_library_instance
#print axioms SE_cs_13118_a13122_explanation_real.repair_two
#print axioms SE_cs_13118_a13122_explanation_real.family
#print axioms SE_cs_13118_a13122_explanation_real.family_real
#print axioms SE_cs_13118_a13122_explanation_real.exact
#print axioms SE_cs_13118_a13122_explanation_real.offset_exact
#print axioms SE_cs_13118_a13122_explanation_real.exact_totalised
#print axioms SE_cs_13118_a13122_explanation_real.repair_totalised
#print axioms SE_cs_13118_a13122_explanation_real.n_zero_claim_holds
#print axioms SE_cs_13118_a13122_explanation_real.n_zero_repair_fails
#print axioms SE_cs_13118_a13122_explanation_real.delta_control
#print axioms SE_cs_13118_a13122_explanation_real.alt_reading
