-- P04: check exactly the witness supplied by the critic's response:
--   f(x) = x + 1,  g(x) = max(0, x - 1),  over N (Lean's Nat, 0 included).
-- Claims to check: (a) g o f is injective, (b) g is not injective.
import Mathlib

namespace P04

def f (x : ℕ) : ℕ := x + 1
def g (x : ℕ) : ℕ := max 0 (x - 1)

theorem comp_injective : Function.Injective (g ∘ f) := by
  intro a b h
  simpa [f, g, Function.comp] using h

theorem g_not_injective : ¬ Function.Injective g := by
  intro h
  have h01 : (0 : ℕ) = 1 := h (by decide)
  exact absurd h01 (by decide)

-- and the witness pair is an explicit non-injectivity witness:
theorem witness : g 0 = g 1 ∧ (0 : ℕ) ≠ 1 := by decide

end P04
