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
def total (T a : Int) (n : Nat) (d : Int) : Int := T + a - 2 * ((n : Int) - 2) * d

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge), u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = total (wsum G) a n d
-- ===== END FIXED PART =====

theorem wsum_append' (A B : List WEdge) : wsum (A ++ B) = wsum A + wsum B := by
  simp [wsum, List.map_append, List.sum_append]

theorem pb_key (u v : Nat) (d : Int) (huv : u ≠ v) : ∀ m : Nat, ∃ c : Int,
    wsum (penaltiesBelow u v d m) = -2 * d * c ∧
    c = (m : Int) - (if u < m then 1 else 0) - (if v < m then 1 else 0) := by
  intro m
  induction m with
  | zero => exact ⟨0, by simp [penaltiesBelow, wsum], by simp⟩
  | succ k ih =>
    obtain ⟨c, h1, h2⟩ := ih
    by_cases hk : k = u ∨ k = v
    · refine ⟨c, ?_, ?_⟩
      · simp only [penaltiesBelow, if_pos hk, List.nil_append]; exact h1
      · rw [h2]; grind
    · refine ⟨c + 1, ?_, ?_⟩
      · simp only [penaltiesBelow, if_neg hk]
        rw [wsum_append', h1]; simp [wsum]; grind
      · rw [h2]; grind

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  obtain ⟨c, h1, h2⟩ := pb_key u v d huv n
  simp only [hu, hv, if_true] at h2
  unfold gstar total
  rw [wsum_append', wsum_append', h1, h2]
  simp [wsum]; grind

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := by
  refine ⟨0, 0, 3, 1, by decide, ?_⟩
  simp [total]

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := by
  intro h
  have := h 3 0 1 1000 950 [(0, 1, 100)] (by decide) (by decide) (by decide)
    (by simp [wsum]) (by simp [wsum]) (by simp [wsum])
  rw [repair_statement 3 0 1 1000 950 [(0, 1, 100)] (by decide) (by decide) (by decide)] at this
  simp [total, wsum] at this

end SE_cstheory_2312_a2318_Census
