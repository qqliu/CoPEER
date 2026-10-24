import Mathlib.GroupTheory.Perm.Basic

/-!
Source: https://math.stackexchange.com/a/1091441 (line 0019).
The answer explicitly composes right to left but writes (12)(23) = (321).
This is a local worked-example error; the answer's minimum count 19 is unaffected.
Mathlib permutations replace the former bespoke image-list group operations.
Points 0,1,2 represent the source's labels 1,2,3.
-/
namespace mse_1091361__ans1091441

def t12 : Equiv.Perm (Fin 3) := Equiv.swap 0 1
def t23 : Equiv.Perm (Fin 3) := Equiv.swap 1 2
/-- (321) = (132), expressed with Mathlib's right-to-left multiplication. -/
def claimedCycle : Equiv.Perm (Fin 3) := t23 * t12

theorem product_is_123_not_321 :
    (t12 * t23) 0 = 1 ∧ (t12 * t23) 1 = 2 ∧ (t12 * t23) 2 = 0 ∧
    claimedCycle 0 = 2 ∧ t12 * t23 ≠ claimedCycle := by
  refine ⟨by decide, by decide, by decide, by decide, ?_⟩
  intro h
  have hc := congrArg (fun p : Equiv.Perm (Fin 3) => p 0) h
  have hne : (t12 * t23) 0 ≠ claimedCycle 0 := by decide
  exact hne hc

theorem reverse_order_control : t23 * t12 = claimedCycle := rfl

end mse_1091361__ans1091441
