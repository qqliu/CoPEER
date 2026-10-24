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

lemma wsum_append (l1 l2 : List WEdge) : wsum (l1 ++ l2) = wsum l1 + wsum l2 := by
  simp [wsum, List.map_append, List.sum_append]

lemma penalty_wsum (u v : Nat) (d : Int) (huv : u ≠ v) :
    ∀ n : Nat, wsum (penaltiesBelow u v d n)
      = -2 * d * ((n : Int) - (if u < n then (1:Int) else 0) - (if v < n then (1:Int) else 0)) := by
  intro n
  induction n with
  | zero => simp [penaltiesBelow, wsum]
  | succ n ih =>
    have hstep : penaltiesBelow u v d (n+1)
        = (if n = u ∨ n = v then ([] : List WEdge) else [(u, n, -d), (v, n, -d)]) ++ penaltiesBelow u v d n := rfl
    rw [hstep, wsum_append, ih]
    by_cases h : n = u ∨ n = v
    · rw [if_pos h]
      simp only [wsum, List.map_nil, List.sum_nil]
      rcases h with h | h
      · have hu1 : u < n + 1 := by omega
        have hu2 : ¬ (u < n) := by omega
        have hv1 : (v < n + 1) ↔ (v < n) := by
          constructor <;> intro <;> omega
        rw [show (u < n) = False from by simp [hu2],
            show (u < n + 1) = True from by simp [hu1]]
        by_cases hvv : v < n
        · rw [show (v < n) = True from by simp [hvv],
              show (v < n + 1) = True from by simp [hv1.mpr hvv]]
          push_cast; ring
        · rw [show (v < n) = False from by simp [hvv],
              show (v < n + 1) = False from by simp [fun hc => hvv (hv1.mp hc)]]
          push_cast; ring
      · have hv1 : v < n + 1 := by omega
        have hv2 : ¬ (v < n) := by omega
        have hu1 : (u < n + 1) ↔ (u < n) := by
          constructor <;> intro <;> omega
        rw [show (v < n) = False from by simp [hv2],
            show (v < n + 1) = True from by simp [hv1]]
        by_cases huu : u < n
        · rw [show (u < n) = True from by simp [huu],
              show (u < n + 1) = True from by simp [hu1.mpr huu]]
          push_cast; ring
        · rw [show (u < n) = False from by simp [huu],
              show (u < n + 1) = False from by simp [fun hc => huu (hu1.mp hc)]]
          push_cast; ring
    · push_neg at h
      obtain ⟨hu, hv⟩ := h
      rw [if_neg (by omega : ¬ (n = u ∨ n = v))]
      simp only [wsum, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil]
      have hu1 : (u < n + 1) ↔ (u < n) := by
        constructor <;> intro <;> omega
      have hv1 : (v < n + 1) ↔ (v < n) := by
        constructor <;> intro <;> omega
      by_cases huu : u < n
      · rw [show (u < n) = True from by simp [huu],
            show (u < n + 1) = True from by simp [hu1.mpr huu]]
        by_cases hvv : v < n
        · rw [show (v < n) = True from by simp [hvv],
              show (v < n + 1) = True from by simp [hv1.mpr hvv]]
          push_cast; ring
        · rw [show (v < n) = False from by simp [hvv],
              show (v < n + 1) = False from by simp [fun hc => hvv (hv1.mp hc)]]
          push_cast; ring
      · rw [show (u < n) = False from by simp [huu],
            show (u < n + 1) = False from by simp [fun hc => huu (hu1.mp hc)]]
        by_cases hvv : v < n
        · rw [show (v < n) = True from by simp [hvv],
              show (v < n + 1) = True from by simp [hv1.mpr hvv]]
          push_cast; ring
        · rw [show (v < n) = False from by simp [hvv],
              show (v < n + 1) = False from by simp [fun hc => hvv (hv1.mp hc)]]
          push_cast; ring

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hun hvn
  have hpw := penalty_wsum u v d huv n
  rw [show (u < n) = True from by simp [hun], show (v < n) = True from by simp [hvn]] at hpw
  simp only [gstar]
  rw [wsum_append, wsum_append, hpw]
  simp only [wsum, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil]
  unfold total
  ring

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := by
  refine ⟨0, 0, 3, 1, by norm_num, ?_⟩
  unfold total
  norm_num

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := by
  intro hpos
  have h := hpos 3 0 1 1000 950 [(0, 0, 100)] (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)
  simp only [gstar, penaltiesBelow, wsum] at h
  norm_num at h

end SE_cstheory_2312_a2318_Census
