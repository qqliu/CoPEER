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
def total (T a : Int) (n : Nat) (d : Int) : Int := T + (a - ((n : Int) - 2) * (2 * d))

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge), u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = total (wsum G) a n d
-- ===== END FIXED PART =====

theorem wsum_append (a b : List WEdge) : wsum (a ++ b) = wsum a + wsum b := by
  simp [wsum, List.map_append, List.sum_append]

theorem pen_sum (u v : Nat) (d : Int) (huv : u ≠ v) (k : Nat) :
    wsum (penaltiesBelow u v d k) =
      -((((k : Int) - (if u < k then 1 else 0)) - (if v < k then 1 else 0)) * (2 * d)) := by
  induction k with
  | zero => simp [penaltiesBelow, wsum]
  | succ k ih =>
    rw [penaltiesBelow, wsum_append, ih]
    by_cases h : k = u ∨ k = v
    · rw [if_pos h]
      have hc : (((k + 1 : Nat) : Int) - (if u < k + 1 then 1 else 0)) - (if v < k + 1 then 1 else 0)
          = ((k : Int) - (if u < k then 1 else 0)) - (if v < k then 1 else 0) := by
        by_cases a1 : u < k <;> by_cases a2 : v < k <;> by_cases a3 : u < k + 1 <;>
          by_cases a4 : v < k + 1 <;> simp [a1, a2, a3, a4] <;> omega
      rw [hc]
      simp [wsum]
    · rw [if_neg h]
      have hc : (((k + 1 : Nat) : Int) - (if u < k + 1 then 1 else 0)) - (if v < k + 1 then 1 else 0)
          = (((k : Int) - (if u < k then 1 else 0)) - (if v < k then 1 else 0)) + 1 := by
        by_cases a1 : u < k <;> by_cases a2 : v < k <;> by_cases a3 : u < k + 1 <;>
          by_cases a4 : v < k + 1 <;> simp [a1, a2, a3, a4] <;> omega
      rw [hc, Int.add_mul, Int.one_mul]
      generalize ((((k : Int) - (if u < k then 1 else 0)) - (if v < k then 1 else 0)) * (2 * d)) = Y
      simp [wsum]
      omega

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  rw [gstar, wsum_append, wsum_append, pen_sum u v d huv n, if_pos hu, if_pos hv, total]
  have hc : ((n : Int) - 1) - 1 = (n : Int) - 2 := by omega
  rw [hc]
  generalize ((n : Int) - 2) * (2 * d) = Y
  generalize wsum G = S
  simp [wsum]
  omega

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) :=
  ⟨0, 0, 3, 1, by decide⟩

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow :=
  fun h => absurd (h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)) (by decide)

end SE_cstheory_2312_a2318_Census
