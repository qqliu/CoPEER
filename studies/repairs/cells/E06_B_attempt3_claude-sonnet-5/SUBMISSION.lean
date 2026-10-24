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
def total (T a : Int) (n : Nat) (d : Int) : Int := T + a - 2 * d * ((n : Int) - 2)

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge), u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = total (wsum G) a n d
-- ===== END FIXED PART =====

-- ===== HELPER LEMMAS =====

/-- Indicator function: 1 if `x < n`, else 0. -/
def ind (x n : Nat) : Int := if x < n then 1 else 0

theorem ind_succ_of_ne (x m : Nat) (h : x ≠ m) : ind x m = ind x (m + 1) := by
  unfold ind
  by_cases hx : x < m
  · have h1 : x < m + 1 := by omega
    simp [hx, h1]
  · have h1 : ¬ x < m + 1 := by omega
    simp [hx, h1]

theorem wsum_nil : wsum ([] : List WEdge) = 0 := by simp [wsum]

theorem wsum_append (l1 l2 : List WEdge) : wsum (l1 ++ l2) = wsum l1 + wsum l2 := by
  simp [wsum, List.map_append, List.sum_append]

theorem wsum_penalty_pair (u v k : Nat) (d : Int) :
    wsum ([(u, k, -d), (v, k, -d)] : List WEdge) = -2 * d := by
  simp [wsum]
  omega

theorem wsum_single (u v : Nat) (a : Int) : wsum ([(u, v, a)] : List WEdge) = a := by
  simp [wsum]

/-- General closed form for the weight of the penalty edges, valid for every `n` (no side
conditions on `u`, `v` needed). -/
theorem penaltiesBelow_wsum_gen (u v : Nat) (d : Int) (huv : u ≠ v) :
    ∀ n : Nat, wsum (penaltiesBelow u v d n)
      = -2 * d * (n : Int) + 2 * d * (ind u n) + 2 * d * (ind v n) := by
  intro n
  induction n with
  | zero => simp [penaltiesBelow, wsum, ind]
  | succ m ih =>
      unfold penaltiesBelow
      rw [wsum_append, ih]
      have hcast : ((m+1 : Nat) : Int) = (m:Int) + 1 := by simp
      have hdist : (-2*d) * ((m:Int)+1) = (-2*d)*(m:Int) + (-2*d) := by
        rw [Int.mul_add, Int.mul_one]
      by_cases h1 : m = u
      · have hvm : v ≠ m := by intro hc; apply huv; omega
        have hv_eq : ind v m = ind v (m + 1) := ind_succ_of_ne v m hvm
        have hu_m : ind u m = 0 := by unfold ind; simp [h1]
        have hu_m1 : ind u (m + 1) = 1 := by
          unfold ind
          have hh : u < m + 1 := by omega
          simp [hh]
        have hcond : (m = u ∨ m = v) := Or.inl h1
        simp only [hcond, if_pos, wsum_nil]
        rw [hcast, hdist, hu_m, hu_m1, ← hv_eq]
        omega
      · by_cases h2 : m = v
        · have hum : u ≠ m := by intro hc; apply huv; omega
          have hu_eq : ind u m = ind u (m + 1) := ind_succ_of_ne u m hum
          have hv_m : ind v m = 0 := by unfold ind; simp [h2]
          have hv_m1 : ind v (m + 1) = 1 := by
            unfold ind
            have hh : v < m + 1 := by omega
            simp [hh]
          have hcond : (m = u ∨ m = v) := Or.inr h2
          simp only [hcond, if_pos, wsum_nil]
          rw [hcast, hdist, hv_m, hv_m1, ← hu_eq]
          omega
        · have hcond : ¬ (m = u ∨ m = v) := by
            intro hc
            rcases hc with hc | hc
            · exact h1 hc
            · exact h2 hc
          have hu_eq : ind u m = ind u (m + 1) := ind_succ_of_ne u m (Ne.symm h1)
          have hv_eq : ind v m = ind v (m + 1) := ind_succ_of_ne v m (Ne.symm h2)
          simp only [hcond, if_neg, not_false_iff]
          rw [wsum_penalty_pair, hcast, hdist, ← hu_eq, ← hv_eq]
          omega

theorem penaltiesBelow_wsum (n u v : Nat) (d : Int) (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    wsum (penaltiesBelow u v d n) = -2 * d * ((n : Int) - 2) := by
  rw [penaltiesBelow_wsum_gen u v d huv n]
  have hiu : ind u n = 1 := by unfold ind; simp [hu]
  have hiv : ind v n = 1 := by unfold ind; simp [hv]
  rw [hiu, hiv]
  have hexp : (n:Int) - 2 = (n:Int) + (-2) := by omega
  rw [hexp, Int.mul_add]
  omega

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  unfold gstar
  rw [wsum_append, wsum_append, wsum_single, penaltiesBelow_wsum n u v d huv hu hv]
  unfold total
  rw [Int.mul_assoc, Int.mul_assoc]
  omega

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := by
  refine ⟨0, 0, 3, 1, by decide, ?_⟩
  unfold total
  decide

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow :=
  fun h => absurd (h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)) (by decide)

end SE_cstheory_2312_a2318_Census
