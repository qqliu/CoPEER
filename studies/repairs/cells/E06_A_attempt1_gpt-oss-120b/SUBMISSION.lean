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
`n` and `d` (no reference to `wsum`, `gstar`, `penaltiesBelow`, `build`, `tsum`; no `if`/`match`). -/
def total (T : Int) (a : Int) (n : Nat) (d : Int) : Int := T + a - ((n : Int) - 2) * (2 * d)

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge),
    u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (wsum G) a n d
-- ===== END FIXED PART =====

-- Helper lemma: sum of the penalty edges added by `penaltiesBelow`.
lemma wsum_penalties (u v : Nat) (d : Int) (n : Nat) :
    wsum (penaltiesBelow u v d n) = -2 * d * ((n : Int) - 2) := by
  induction n with
  | zero =>
      simp [penaltiesBelow, wsum]
  | succ n ih =>
      simp [penaltiesBelow, wsum, List.map_append, List.sum_append, ih] at *
      by_cases h : n = u ∨ n = v
      · simp [h] at *
      · simp [h] at *
        have hneg : (-d) + (-d) = (-2) * d := by
          simp [two_mul, mul_comm, mul_left_comm, mul_assoc]
        simpa [hneg, Nat.succ_eq_add_one, mul_add, add_comm, add_left_comm, add_assoc,
               mul_comm, mul_left_comm, mul_assoc]

theorem repair_statement :
    ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge),
      u ≠ v → u < n → v < n →
      SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) =
        SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d :=
by
  intro n u v d a G hne hun hvn
  unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.gstar
  unfold SE_cstheory_2312_a2318_Census.wsum
  simp [List.map_append, List.sum_append, wsum_penalties u v d n,
        add_comm, add_left_comm, add_assoc, mul_comm, mul_left_comm, mul_assoc]

theorem repair_nonvacuous :
    ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧
      SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) :=
by
  refine ⟨2, 4, 3, 5, ?_, ?_⟩
  · decide
  · simp [SE_cstheory_2312_a2318_Census.total]

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow :=
by
  intro hpos
  let G : List SE_cstheory_2312_a2318_Census.WEdge := [(0, 0, (2 : Int))]
  have hGpos : 0 < SE_cstheory_2312_a2318_Census.wsum G := by
    simp [SE_cstheory_2312_a2318_Census.wsum]
  have hpos_inst :=
    hpos 3 0 1 5 4 G (by decide) (by decide) (by decide) hGpos (by decide) (by decide)
  have hcalc :=
    (repair_statement 3 0 1 5 4 G (by decide) (by decide) (by decide))
  have hlt : (0 : Int) < SE_cstheory_2312_a2318_Census.total 2 4 3 5 := by
    simpa [hcalc] using hpos_inst
  have hlt' : (0 : Int) < -4 := by
    simpa [SE_cstheory_2312_a2318_Census.total] using hlt
  have hle : (-4 : Int) ≤ 0 := by decide
  have hzero : (0 : Int) < 0 := lt_of_lt_of_le hlt' hle
  exact lt_irrefl _ hzero

end SE_cstheory_2312_a2318_Census
