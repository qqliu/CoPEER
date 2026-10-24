import Mathlib

/- P28: the witness supplied by the critic's response, u = 2, m = 3, n = 2,
   against the located assertion "If u ∣ m*n and gcd(u,m) = 1, then m = ±1"
   for integers u, m, n (source line 1). -/
theorem P28_witness_refutes :
    ∃ u m n : ℤ, u ∣ m * n ∧ Int.gcd u m = 1 ∧ m ≠ 1 ∧ m ≠ -1 :=
  ⟨2, 3, 2, by norm_num, by norm_num, by norm_num, by norm_num⟩
