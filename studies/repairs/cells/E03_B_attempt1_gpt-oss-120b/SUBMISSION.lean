import defs_only
open scoped BigOperators
namespace SE_cs_13118_a13122_explanation_real

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected closed form for `Sigma (fun k => c ^ k) n` on the source's domain `c ≠ 1`, `1 ≤ n`.
The hole must be a closed expression in `c` and `n` built from field operations and powers: no sums,
no `Sigma`, no `Finset`, no `if`/`match`. -/
noncomputable def closed_form (c : ℝ) (n : ℕ) : ℝ := (c ^ n - c) / (c - 1)

/-- The corrected located line on the source's domain (shape fixed). -/
def CorrectedClaim : Prop :=
  ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → Sigma (fun k => c ^ k) n = closed_form c n
-- ===== END FIXED PART =====

theorem repair_statement :
  ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n →
    SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n =
      SE_cs_13118_a13122_explanation_real.closed_form c n :=
by
  intro c n hcn h1n
  unfold SE_cs_13118_a13122_explanation_real.Sigma
  unfold SE_cs_13118_a13122_explanation_real.closed_form
  -- geometric series for the full range 0 … n‑1
  have hgeom :
      Finset.sum (Finset.range n) (fun i => c ^ i) = (c ^ n - 1) / (c - 1) := by
    simpa using (geom_sum_eq (x:=c) (n:=n) hcn)
  -- the required sum is the full sum minus the term for i = 0
  have hsum :
      Finset.sum (Finset.Icc 1 (n - 1)) (fun k => c ^ k) =
        Finset.sum (Finset.range n) (fun i => c ^ i) - 1 := by
    have h0 :
        Finset.sum (Finset.range n) (fun i => c ^ i) =
          Finset.sum (Finset.Icc 0 (n - 1)) (fun i => c ^ i) := by
      simpa using (Finset.sum_range_eq_sum_Icc (fun i => c ^ i) n)
    have h1 :
        Finset.sum (Finset.Icc 0 (n - 1)) (fun i => c ^ i) =
          c ^ 0 + Finset.sum (Finset.Icc 1 (n - 1)) (fun k => c ^ k) := by
      have h0not : (0 : ℕ) ∉ Finset.Icc 1 (n - 1) := by
        simp
      have h_eq :
          Finset.Icc 0 (n - 1) = Finset.insert 0 (Finset.Icc 1 (n - 1)) := by
        ext i
        constructor
        · intro hi
          rcases Finset.mem_Icc.mp hi with ⟨h0le, hle⟩
          by_cases hzero : i = 0
          · left; exact hzero
          · right
            have : 1 ≤ i := Nat.succ_le_of_lt (Nat.lt_of_le_of_ne h0le (by symm; exact hzero))
            exact Finset.mem_Icc.mpr ⟨this, hle⟩
        · intro hi
          cases hi with
          | inl hzero =>
              subst hzero
              exact Finset.mem_Icc.mpr ⟨Nat.zero_le _, Nat.sub_le_self _ _⟩
          | inr hrest =>
              exact Finset.mem_Icc.mp hrest
      simpa [h_eq, Finset.sum_insert h0not, pow_zero, add_comm] using rfl
    have : Finset.sum (Finset.Icc 1 (n - 1)) (fun k => c ^ k) =
        Finset.sum (Finset.range n) (fun i => c ^ i) - 1 := by
      have := congrArg (fun t => t - 1) (h0.trans h1)
      simpa [sub_eq_add_neg, add_comm, add_left_comm, add_assoc] using this
    exact this
  calc
    Finset.sum (Finset.Icc 1 (n - 1)) (fun k => c ^ k)
        = Finset.sum (Finset.range n) (fun i => c ^ i) - 1 := hsum
    _ = ((c ^ n - 1) / (c - 1)) - 1 := by simpa [hgeom]
    _ = (c ^ n - c) / (c - 1) := by
      field_simp
      ring

theorem repair_nonvacuous :
  ∃ (c : ℝ) (n : ℕ),
    c ≠ 1 ∧ 1 ≤ n ∧
      SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n =
        SE_cs_13118_a13122_explanation_real.closed_form c n ∧
      SE_cs_13118_a13122_explanation_real.closed_form c n ≠ (c ^ n - 1) / (c - 1) :=
by
  refine ⟨0, 1, ?_, ?_, ?_, ?_⟩
  · norm_num
  · norm_num
  · -- evaluate the sum at c = 0, n = 1
    have hsum :
        SE_cs_13118_a13122_explanation_real.Sigma (fun k => (0 : ℝ) ^ k) 1 = 0 := by
      unfold SE_cs_13118_a13122_explanation_real.Sigma
      simp
    have hclosed :
        SE_cs_13118_a13122_explanation_real.closed_form (0 : ℝ) 1 = 0 := by
      unfold SE_cs_13118_a13122_explanation_real.closed_form
      simp
    simpa [hsum, hclosed]
  · -- the closed form differs from the original at this point
    have hclosed :
        SE_cs_13118_a13122_explanation_real.closed_form (0 : ℝ) 1 = 0 := by
      unfold SE_cs_13118_a13122_explanation_real.closed_form
      simp
    have horig : ((0 : ℝ) ^ 1 - 1) / (0 - 1) = (1 : ℝ) := by norm_num
    simpa [hclosed, horig]

theorem final_theorem :
  ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n →
    SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n =
      SE_cs_13118_a13122_explanation_real.closed_form c n :=
  repair_statement

end SE_cs_13118_a13122_explanation_real
