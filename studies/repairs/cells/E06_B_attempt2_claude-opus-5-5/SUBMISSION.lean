import defs_only
/-!
Record E06: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SE_cstheory_2312_a2318_Census

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected total weight of the constructed graph `G*`, as an expression in `T = wsum G`, `a`, `n`
and `d` (the source books `T + (a - (n - 2) d)`). The hole must be a closed integer expression in `T`, `a`,
`n`, `d` (no reference to `wsum`, `gstar`, `penaltiesBelow`, `build`, `tsum`; no `if`/`match`). -/
def total (T a : Int) (n : Nat) (d : Int) : Int := T + (a - 2 * ((n : Int) - 2) * d)

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge), u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = total (wsum G) a n d
-- ===== END FIXED PART =====

theorem wsum_append (x y : List WEdge) : wsum (x ++ y) = wsum x + wsum y := by
  simp [wsum, List.map_append, List.sum_append]

theorem wsum_pen2 (u v : Nat) (d : Int) (huv : u ≠ v) : ∀ k : Nat, ∃ c : Int,
    wsum (penaltiesBelow u v d k) = d * c ∧
      c = -2 * (k : Int) + (if u < k then 2 else 0) + (if v < k then 2 else 0) := by
  intro k
  induction k with
  | zero => exact ⟨0, by simp [penaltiesBelow, wsum]⟩
  | succ k ih =>
    obtain ⟨c, hc, hce⟩ := ih
    rw [penaltiesBelow, wsum_append, hc]
    by_cases hk : k = u ∨ k = v
    · rw [if_pos hk]
      refine ⟨c, by simp [wsum], ?_⟩
      rw [hce]
      by_cases h1 : u < k <;> by_cases h2 : v < k <;> by_cases h3 : u < k + 1 <;>
        by_cases h4 : v < k + 1 <;> simp only [h1, h2, h3, h4, if_true, if_false] <;> omega
    · rw [if_neg hk]
      refine ⟨c - 2, ?_, ?_⟩
      · have : wsum [(u, k, -d), (v, k, -d)] = -d + -d := by simp [wsum]
        rw [this, Int.mul_sub]
        generalize d * c = y
        omega
      · rw [hce]
        by_cases h1 : u < k <;> by_cases h2 : v < k <;> by_cases h3 : u < k + 1 <;>
          by_cases h4 : v < k + 1 <;> simp only [h1, h2, h3, h4, if_true, if_false] <;> omega

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  obtain ⟨c, hc, hce⟩ := wsum_pen2 u v d huv n
  rw [if_pos hu, if_pos hv] at hce
  have ha : wsum [(u, v, a)] = a := by simp [wsum]
  rw [gstar, wsum_append, wsum_append, hc, ha, total]
  have h1 : 2 * ((n : Int) - 2) * d = d * (2 * ((n : Int) - 2)) := Int.mul_comm _ _
  have h2 : c = -(2 * ((n : Int) - 2)) := by omega
  rw [h1, h2, Int.mul_neg]
  generalize d * (2 * ((n : Int) - 2)) = y
  omega

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) :=
  ⟨0, 0, 3, 1, by decide, by decide⟩

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow :=
  fun h => absurd (h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)) (by decide)

end SE_cstheory_2312_a2318_Census
