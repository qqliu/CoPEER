/- P24: Lean check of exactly the witness the response supplies for line 5,
   "Take u=6, m=5, n=6; then u|mn (6|30) and gcd(u,m)=1 but m=5 != ±1."
   Line 5 (under line 1, "Let u, m, n be three integers") asserts:
     forall u m n : ℤ, u ∣ m * n → Int.gcd u m = 1 → (m = 1 ∨ m = -1).
   The witness instantiates u = 6, m = 5, n = 6. -/
import Mathlib

-- the supplied witness satisfies both hypotheses of line 5
theorem P24_witness_hyps : (6 : ℤ) ∣ 5 * 6 ∧ Int.gcd 6 5 = 1 := by
  constructor
  · decide
  · decide

-- and fails its conclusion
theorem P24_witness_concl : ¬ ((5 : ℤ) = 1 ∨ (5 : ℤ) = -1) := by decide

-- hence line 5, as written, is false
theorem P24_line5_false :
    ¬ (∀ u m n : ℤ, u ∣ m * n → Int.gcd u m = 1 → (m = 1 ∨ m = -1)) := by
  intro h
  exact P24_witness_concl (h 6 5 6 P24_witness_hyps.1 P24_witness_hyps.2)
