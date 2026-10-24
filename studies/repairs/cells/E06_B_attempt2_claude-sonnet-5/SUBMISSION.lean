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

-- ===== Helper lemmas =====

theorem wsum_append (xs ys : List WEdge) : wsum (xs ++ ys) = wsum xs + wsum ys := by
  simp [wsum, List.sum_append]

/-- Number of `k < n` with `k ≠ u` and `k ≠ v`, structurally matching `penaltiesBelow`. -/
def numNotUV (u v : Nat) : Nat → Nat
  | 0 => 0
  | k + 1 => (if k = u ∨ k = v then 0 else 1) + numNotUV u v k

theorem count_eq (u v : Nat) (huv : u ≠ v) :
    ∀ n : Nat, numNotUV u v n + (if u < n then 1 else 0) + (if v < n then 1 else 0) = n
  | 0 => by simp [numNotUV]
  | (k + 1) => by
      have IH := count_eq u v huv k
      simp only [numNotUV]
      omega

theorem pen_wsum (u v : Nat) (d : Int) :
    ∀ n : Nat, wsum (penaltiesBelow u v d n) = -2 * d * (numNotUV u v n : Int)
  | 0 => by simp [penaltiesBelow, wsum, numNotUV]
  | (k + 1) => by
      have IH := pen_wsum u v d k
      by_cases h : k = u ∨ k = v
      · simp only [penaltiesBelow, numNotUV, h, if_pos]
        simp [wsum, IH]
      · simp only [penaltiesBelow, numNotUV, h, if_neg, if_false]
        simp only [if_neg h]
        rw [wsum_append]
        simp only [wsum, IH]
        have : ((0 + numNotUV u v k + 1 : Nat) : Int) = (numNotUV u v k : Int) + 1 := by
          simp
        simp only [Nat.zero_add]
        push_cast
        simp [Int.mul_add]
        ring_nf
        sorry

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ (n u v : Nat) (d a : Int) (G : List SE_cstheory_2312_a2318_Census.WEdge), u ≠ v → u < n → v < n → SE_cstheory_2312_a2318_Census.wsum (SE_cstheory_2312_a2318_Census.gstar n u v d a G) = SE_cstheory_2312_a2318_Census.total (SE_cstheory_2312_a2318_Census.wsum G) a n d := by
  sorry

theorem repair_nonvacuous : ∃ (T a : Int) (n : Nat) (d : Int), 2 ≤ n ∧ SE_cstheory_2312_a2318_Census.total T a n d ≠ T + (a - ((n : Int) - 2) * d) := by
  sorry

theorem final_theorem : ¬ SE_cstheory_2312_a2318_Census.PositivityUnderWindow := by
  sorry

end SE_cstheory_2312_a2318_Census
