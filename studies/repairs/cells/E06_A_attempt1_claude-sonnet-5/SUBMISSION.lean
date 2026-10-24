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

theorem mul_succ_cast (c d : Int) (k : Nat) :
    c * (d * ((k + 1 : Nat) : Int)) = c * (d * (k : Int)) + c * d := by
  have h : ((k + 1 : Nat) : Int) = (k : Int) + 1 := by omega
  simp only [h, Int.mul_add, Int.mul_one]

theorem penaltiesBelow_sum (u v : Nat) (d : Int) :
    ∀ n : Nat, wsum (penaltiesBelow u v d n)
      = 2 * (d * (if u < n then (1 : Int) else 0)) + 2 * (d * (if v < n then (1 : Int) else 0))
          + (-2) * (d * (n : Int)) := by
  intro n
  induction n with
  | zero => simp [penaltiesBelow, wsum]
  | succ k ih =>
      unfold penaltiesBelow
      simp only [wsum, List.map_append, List.sum_append, List.nil_append] at *
      have hstep := mul_succ_cast (-2) d k
      by_cases hk : k = u ∨ k = v
      · simp only [if_pos hk]
        rcases hk with hk | hk
        · subst hk
          have h1 : ¬ (k < u) := by omega
          have h2 : (k < k + 1) := by omega
          by_cases hv : v < k
          · have hv1 : v < k + 1 := by omega
            rw [if_neg h1, if_pos h2, if_pos hv, if_pos hv1] at *
            simp only [List.map_nil, List.sum_nil, zero_add] at ih ⊢
            omega
          · have hv1 : ¬ v < k + 1 := by
              rcases hk : v = k with hveq
              · omega
              · omega
            rw [if_neg h1, if_pos h2, if_neg hv, if_neg hv1] at *
            simp only [List.map_nil, List.sum_nil, zero_add] at ih ⊢
            omega
        · subst hk
          have h1 : ¬ (k < v) := by omega
          have h2 : (k < k + 1) := by omega
          by_cases hu : u < k
          · have hu1 : u < k + 1 := by omega
            rw [if_neg h1, if_pos h2, if_pos hu, if_pos hu1] at *
            simp only [List.map_nil, List.sum_nil, zero_add] at ih ⊢
            omega
          · have hu1 : ¬ u < k + 1 := by
              rcases hk : u = k with hueq
              · omega
              · omega
            rw [if_neg h1, if_pos h2, if_neg hu, if_neg hu1] at *
            simp only [List.map_nil, List.sum_nil, zero_add] at ih ⊢
            omega
      · push_neg at hk
        obtain ⟨hku, hkv⟩ := hk
        simp only [if_neg (show ¬ (k = u ∨ k = v) from fun h => h.elim hku hkv)] at *
        have hu1 : (u < k + 1) ↔ (u < k ∨ u = k) := by omega
        have hv1 : (v < k + 1) ↔ (v < k ∨ v = k) := by omega
        by_cases hu : u < k
        · have huk1 : u < k + 1 := by omega
          by_cases hv : v < k
          · have hvk1 : v < k + 1 := by omega
            rw [if_pos hu, if_pos huk1, if_pos hv, if_pos hvk1] at *
            simp only [List.map_cons, List.map_nil, List.sum_cons, List.sum_nil] at *
            omega
          · have hvk1 : ¬ v < k + 1 := by omega
            rw [if_pos hu, if_pos huk1, if_neg hv, if_neg hvk1] at *
            simp only [List.map_cons, List.map_nil, List.sum_cons, List.sum_nil] at *
            omega
        · have huk1 : ¬ u < k + 1 := by omega
          by_cases hv : v < k
          · have hvk1 : v < k + 1 := by omega
            rw [if_neg hu, if_neg huk1, if_pos hv, if_pos hvk1] at *
            simp only [List.map_cons, List.map_nil, List.sum_cons, List.sum_nil] at *
            omega
          · have hvk1 : ¬ v < k + 1 := by omega
            rw [if_neg hu, if_neg huk1, if_neg hv, if_neg hvk1] at *
            simp only [List.map_cons, List.map_nil, List.sum_cons, List.sum_nil] at *
            omega

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  have hp := penaltiesBelow_sum u v d n
  rw [if_pos hu, if_pos hv] at hp
  unfold gstar total
  simp only [wsum, List.map_append, List.sum_append, List.map_cons, List.map_nil,
    List.sum_cons, List.sum_nil] at *
  rw [hp]
  have key : (2:Int) * ((n:Int) - 2) * d = 2 * (d * (n:Int)) - 2 * (2 * d) := by
    rw [Int.mul_assoc, Int.sub_mul, Int.mul_sub, Int.mul_comm (n:Int) d]
  rw [key]
  omega

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := by
  refine ⟨0, 0, 3, 1, by decide, ?_⟩
  unfold total
  omega

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := by
  intro h
  unfold PositivityUnderWindow at h
  have h1 := h 3 0 1 200 151 [(0, 1, 100)] (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)
  rw [repair_statement 3 0 1 200 151 [(0, 1, 100)] (by decide) (by decide) (by decide)] at h1
  unfold total at h1
  omega

end SE_cstheory_2312_a2318_Census
