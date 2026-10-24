import defs_only
/- EVALUATOR-ONLY reference correction for E13 (original package: repair, line 118 / repair_all_odd, line 124). -/
namespace Census_reddit_learnmath_8yjpp7.Ref

/-- Reference corrected right-hand side: the odd branch returns `n + 1`. -/
def rhs (n : Nat) : Nat := n + 1

theorem universal : ∀ n : Nat, IsOdd n → IsEven (n / 2) → (n / 2 + 1) * 2 = rhs n := by
  intro n h1 _
  obtain ⟨m, hm⟩ := h1
  unfold rhs
  omega

end Census_reddit_learnmath_8yjpp7.Ref
