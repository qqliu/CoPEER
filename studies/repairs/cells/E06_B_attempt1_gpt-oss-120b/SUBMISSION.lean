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
def total (T a : Int) (n : Nat) (d : Int) : Int := T + a - ((n : Int) - 2) * (2 * d)

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge),
    u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = total (wsum G) a n d
-- ===== END FIXED PART =====

/- Helper lemma: the total weight contributed by the penalty edges. -/
lemma wsum_penalties (u v : Nat) (d : Int) (n : Nat)
    (h_uv : u ≠ v) (hu : u < n) (hv : v < n) :
    wsum (penaltiesBelow u v d n) = -2 * ((n : Int) - 2) * d := by
  induction' n with n ih
  · cases hu
  · have h_cases : (n = u ∨ n = v) ∨ ¬ (n = u ∨ n = v) := Classical.em _
    cases h_cases with
    | inl h_eq =>
        -- the current index coincides with u or v, so no edges are added this step
        have : (if n = u ∨ n = v then [] else [(u, n, -d), (v, n, -d)]) = [] := by
          simp [h_eq]
        have hu' : u < Nat.succ n := hu
        have hv' : v < Nat.succ n := hv
        -- the sum does not change from the previous size
        simpa [penaltiesBelow, this, ih hu' hv' h_uv, Nat.succ_eq_add_one,
               add_comm, add_left_comm, add_assoc, mul_comm, mul_left_comm, mul_assoc] using
          (by
            have : wsum (penaltiesBelow u v d (Nat.succ n)) =
                wsum (penaltiesBelow u v d n) := by
              simp [penaltiesBelow, this]
            simpa [this] )
    | inr h_ne =>
        -- the current index is distinct from u and v, so we add two edges of weight -d
        have : (if n = u ∨ n = v then [] else [(u, n, -d), (v, n, -d)]) =
                [(u, n, -d), (v, n, -d)] := by
          simp [h_ne]
        have hu' : u < Nat.succ n := hu
        have hv' : v < Nat.succ n := hv
        -- compute the sum, using the induction hypothesis for the smaller size
        have ih' := ih hu' hv' h_uv
        simpa [penaltiesBelow, this, ih', Nat.succ_eq_add_one,
               add_comm, add_left_comm, add_assoc, mul_comm, mul_left_comm, mul_assoc,
               Int.add_mul, mul_add] using
          (by
            have : wsum (penaltiesBelow u v d (Nat.succ n)) =
                (-d + -d) + wsum (penaltiesBelow u v d n) := by
              simp [penaltiesBelow, this]
            simpa [this] )

/- Main repaired statement -/
theorem repair_statement :
    ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge),
      u ≠ v → u < n → v < n →
      SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) =
        SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G hne hun hvn
  have hgs :
      SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) =
        SE_cstheory_2312_a2318_Census.wsum G +
          SE_cstheory_2312_a2318_Census.wsum (penaltiesBelow u v d n) + a := by
    simp [gstar, wsum, List.map_append, List.sum_append]
  have hpen :
      SE_cstheory_2312_a2318_Census.wsum (penaltiesBelow u v d n) =
        -2 * ((n : Int) - 2) * d :=
    wsum_penalties u v d n hne hun hvn
  simpa [total, hgs, hpen, add_comm, add_left_comm, add_assoc,
         mul_comm, mul_left_comm, mul_assoc] using hgs

/-- There exists a setting of parameters where the corrected total differs from the source's
booked total `T + (a - ((n : Int) - 2) * d)`. -/
theorem repair_nonvacuous :
    ∃ (T a : Int) (n : Nat) (d : Int),
      2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠
        T + (a - ((n : Int) - 2) * d) := by
  refine ⟨0, 0, 3, 1, ?_, ?_⟩
  · decide
  · simp [total]

/-- The positivity half of the original claim remains false after the correction. -/
theorem final_theorem :
    ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := by
  intro h
  have hpos :=
    h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
      (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)
  have hsum_eq :
    SE_cstheory_2312_a2318_Census.wsum
        (SE_cstheory_2312_a2318_Census.gstar 3 0 1 20 19
          [(0, 1, 1), (1, 2, 1)]) = -19 := by decide
  have hlt : (0 : Int) < -19 := by
    simpa [hsum_eq] using hpos
  have hlt2 : (-19 : Int) < 0 := by decide
  exact (lt_asymm hlt hlt2)

end SE_cstheory_2312_a2318_Census
