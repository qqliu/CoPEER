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
def total (T a : Int) (n : Nat) (d : Int) : Int := T + a - d * (2 * (n : Int) - 4)

/-- The corrected accounting identity for every instance of the construction (shape fixed; the source's
window hypotheses are not needed for the identity itself). -/
def CorrectedAccounting : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge), u ≠ v → u < n → v < n →
    wsum (gstar n u v d a G) = total (wsum G) a n d
-- ===== END FIXED PART =====

theorem wsum_append (x y : List WEdge) : wsum (x ++ y) = wsum x + wsum y := by
  simp [wsum, List.map_append, List.sum_append]

def cnt (u v : Nat) : Nat → Int
  | 0 => 0
  | k + 1 => (if k = u ∨ k = v then 0 else 2) + cnt u v k

theorem wsum_pen (u v : Nat) (d : Int) (k : Nat) :
    wsum (penaltiesBelow u v d k) = -(d * cnt u v k) := by
  induction k with
  | zero => simp [penaltiesBelow, wsum, cnt]
  | succ k ih =>
    rw [penaltiesBelow, wsum_append, ih, cnt]
    split
    · simp [wsum]
    · simp only [wsum, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil, Int.mul_add]
      generalize d * cnt u v k = p
      omega

theorem cnt_eq (u v : Nat) (huv : u ≠ v) (k : Nat) :
    cnt u v k = 2 * ((k : Int) - (if u < k then 1 else 0) - (if v < k then 1 else 0)) := by
  induction k with
  | zero => simp [cnt]
  | succ k ih =>
    rw [cnt, ih]
    repeat' split
    all_goals omega

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  have hc : cnt u v n = 2 * (n : Int) - 4 := by
    rw [cnt_eq u v huv n]; simp [hu, hv]; omega
  rw [gstar, wsum_append, wsum_append, wsum_pen u v d n, hc, total]
  have : wsum [(u, v, a)] = a := by simp [wsum]
  rw [this]
  generalize d * (2 * (n : Int) - 4) = p
  omega

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := by
  refine ⟨0, 0, 3, 1, by decide, ?_⟩
  simp [total]

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := by
  intro h
  have := h 3 0 1 100 50 [(0, 1, 100)] (by decide) (by decide) (by decide)
    (by decide) (by decide) (by decide)
  rw [repair_statement 3 0 1 100 50 _ (by decide) (by decide) (by decide)] at this
  simp [total, wsum] at this

end SE_cstheory_2312_a2318_Census
