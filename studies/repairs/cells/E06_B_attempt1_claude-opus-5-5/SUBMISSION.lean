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

theorem wsum_append' (x y : List WEdge) : wsum (x ++ y) = wsum x + wsum y := by
  simp [wsum]

def cnt (u v k : Nat) : Int :=
  (k : Int) - (if u < k then 1 else 0) - (if v < k then 1 else 0)

theorem cnt_succ (u v k : Nat) (huv : u ≠ v) :
    cnt u v (k + 1) = cnt u v k + (if k = u ∨ k = v then 0 else 1) := by
  unfold cnt
  by_cases h1 : u < k <;> by_cases h2 : v < k <;> by_cases h3 : u = k <;>
    by_cases h4 : v = k <;>
    simp [h1, h2, h3, h4, Nat.lt_succ_iff, Nat.le_iff_lt_or_eq] <;> omega

theorem pen_sum (u v : Nat) (d : Int) (huv : u ≠ v) :
    ∀ k, wsum (penaltiesBelow u v d k) = -2 * d * cnt u v k
  | 0 => by simp [penaltiesBelow, wsum, cnt]
  | k + 1 => by
    rw [penaltiesBelow, wsum_append', pen_sum u v d huv k, cnt_succ u v k huv]
    by_cases h : k = u ∨ k = v
    · simp only [h, if_true]
      simp [wsum]
    · simp only [h, if_false]
      simp [wsum]
      rw [Int.mul_add, Int.mul_one]
      generalize -2 * d * cnt u v k = z
      omega

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  have hc : cnt u v n = (n : Int) - 2 := by
    unfold cnt
    simp [hu, hv]
    omega
  rw [gstar, wsum_append', wsum_append', pen_sum u v d huv, hc, total]
  have e : wsum [(u, v, a)] = a := by simp [wsum]
  have h : -2 * d * ((n : Int) - 2) = -(2 * ((n : Int) - 2) * d) := by
    rw [Int.mul_assoc, Int.mul_comm d, ← Int.mul_assoc, Int.neg_mul, Int.neg_mul]
  rw [e, h]
  generalize 2 * ((n : Int) - 2) * d = z
  omega

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) :=
  ⟨0, 0, 3, 1, by decide, by decide⟩

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow :=
  fun h => absurd (h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)) (by decide)

end SE_cstheory_2312_a2318_Census
