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
def total (T a : Int) (n : Nat) (d : Int) : Int := T + a - 2*((n:Int) - 2)*d

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge), u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = total (wsum G) a n d
-- ===== END FIXED PART =====

theorem wsum_append (a b : List WEdge) : wsum (a ++ b) = wsum a + wsum b := by
  simp [wsum, List.map_append, List.sum_append]

theorem penalty_sum (u v : Nat) (huv : u ≠ v) (d : Int) :
    ∀ n : Nat, wsum (penaltiesBelow u v d n)
      = -2*d*((n:Int) - (if u < n then 1 else 0) - (if v < n then 1 else 0)) := by
  intro n
  induction n with
  | zero => simp [penaltiesBelow, wsum]
  | succ k ih =>
    simp only [penaltiesBelow]
    by_cases hc : k = u ∨ k = v
    · rw [if_pos hc, wsum_append, ih]
      have hz : wsum ([] : List WEdge) = 0 := by simp [wsum]
      rw [hz, Int.zero_add]
      have hbracket :
          ((k:Int) - (if u < k then 1 else 0) - (if v < k then 1 else 0))
          = ((k+1:Nat):Int) - (if u < k+1 then 1 else 0) - (if v < k+1 then 1 else 0) := by
        rcases hc with hu | hv
        · subst hu
          have hvk : v ≠ k := fun hh => huv hh.symm
          push_cast
          omega
        · subst hv
          have huk : u ≠ k := fun hh => huv hh
          push_cast
          omega
      rw [hbracket]
    · have hku : k ≠ u := fun h => hc (Or.inl h)
      have hkv : k ≠ v := fun h => hc (Or.inr h)
      rw [if_neg hc, wsum_append, ih]
      have hz : wsum ([(u, k, -d), (v, k, -d)] : List WEdge) = -d + -d := by simp [wsum]
      rw [hz]
      have hbracket :
          ((k+1:Nat):Int) - (if u < k+1 then 1 else 0) - (if v < k+1 then 1 else 0)
          = ((k:Int) - (if u < k then 1 else 0) - (if v < k then 1 else 0)) + 1 := by
        push_cast
        omega
      rw [hbracket, Int.mul_add, Int.mul_one]
      omega

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  unfold gstar total
  rw [wsum_append, wsum_append]
  have hpen := penalty_sum u v huv d n
  rw [if_pos hu, if_pos hv] at hpen
  have heq : ((n:Int) - 1 - 1) = ((n:Int) - 2) := by omega
  rw [heq] at hpen
  rw [hpen]
  have hlast : wsum ([(u, v, a)] : List WEdge) = a := by simp [wsum]
  rw [hlast, Int.mul_comm ((n:Int) - 2) d]
  omega

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := by
  refine ⟨0, 0, 3, 1, ?_, ?_⟩
  · decide
  · unfold total
    decide

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := by
  intro h
  have := h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)
  revert this
  decide

end SE_cstheory_2312_a2318_Census
