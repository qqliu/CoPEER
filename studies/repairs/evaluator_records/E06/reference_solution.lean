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

theorem wsum_nil : wsum [] = 0 := rfl

theorem wsum_cons (e : WEdge) (es : List WEdge) : wsum (e :: es) = e.2.2 + wsum es := by
  simp [wsum]

theorem wsum_append (xs ys : List WEdge) : wsum (xs ++ ys) = wsum xs + wsum ys := by
  induction xs with
  | nil => simp [wsum]
  | cons e es ih => rw [List.cons_append, wsum_cons, wsum_cons, ih]; omega

def penaltyCount (u v : Nat) : Nat → Nat
  | 0 => 0
  | k + 1 => (if k = u ∨ k = v then 0 else 1) + penaltyCount u v k

theorem wsum_penaltiesBelow (u v : Nat) (d : Int) :
    ∀ k, wsum (penaltiesBelow u v d k) = -(2 * ((penaltyCount u v k : Int) * d))
  | 0 => by simp [penaltiesBelow, penaltyCount, wsum]
  | k + 1 => by
      have ih := wsum_penaltiesBelow u v d k
      by_cases h : k = u ∨ k = v
      · simp only [penaltiesBelow, penaltyCount, h, ↓reduceIte, List.nil_append, Nat.zero_add]; exact ih
      · simp only [penaltiesBelow, penaltyCount, h, ↓reduceIte, wsum_append, wsum_cons, wsum_nil, ih]
        rw [Int.natCast_add, Int.add_mul]
        simp only [Int.natCast_one, Int.one_mul]
        omega

theorem penaltyCount_eq (u v : Nat) (huv : u ≠ v) :
    ∀ k, penaltyCount u v k + min 1 (k - u) + min 1 (k - v) = k
  | 0 => by simp [penaltyCount]
  | k + 1 => by
      have ih := penaltyCount_eq u v huv k
      by_cases h : k = u ∨ k = v
      · simp only [penaltyCount, h, ↓reduceIte]; omega
      · simp only [penaltyCount, h, ↓reduceIte]; omega

theorem penaltyCount_two (n u v : Nat) (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    (penaltyCount u v n : Int) = (n : Int) - 2 := by
  have := penaltyCount_eq u v huv n
  omega

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected accounting identity holds for every `n`, distinct designated vertices `u ≠ v`
below `n`, every `d`, `a` and every edge list `G`. -/
theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  intro n u v d a G huv hu hv
  unfold gstar total
  rw [wsum_append, wsum_append, wsum_penaltiesBelow, penaltyCount_two n u v huv hu hv, wsum_cons, wsum_nil,
    Int.mul_assoc]
  show wsum G + -(2 * (((n : Int) - 2) * d)) + (a + 0) = wsum G + a - 2 * (((n : Int) - 2) * d)
  omega

/-- Non-vacuity: the corrected total differs from the source's booked total `T + (a - (n - 2) d)` at some
parameters with `n ≥ 2`. -/
theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := ⟨2, 19, 3, 20, by decide, by unfold total; decide⟩

/-- Non-entailment (the endpoint of this record): the corrected accounting does not rescue the source's
positivity claim. `PositivityUnderWindow` (from defs_only) is the positivity half of the located claim under
all of the source's hypotheses; it is false. If you cannot prove it, replace this declaration (this doc
comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := fun h => absurd (h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)) (by decide)
-- ===== END OBLIGATIONS =====
end SE_cstheory_2312_a2318_Census
