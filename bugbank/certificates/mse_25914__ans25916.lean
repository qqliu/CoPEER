import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.List.Prime
import Mathlib.Tactic

/-!
Source: https://math.stackexchange.com/a/25916, line 0005.
The proposed strong-induction step assumes every next integer is a product of
strictly smaller positive integers. Prime 7 refutes this for lists of every
length, including arbitrarily many factors equal to 1. Mathlib's prime-divides-
product theorem replaces bounded enumeration and its unproved search bound.
The target odd-times-power-of-two theorem is unaffected.
-/
namespace mse_25914__ans25916

theorem seven_has_no_smaller_factorisation :
    ¬ ∃ xs : List ℕ, (∀ a ∈ xs, 0 < a ∧ a < 7) ∧ xs.prod = 7 := by
  rintro ⟨xs, hsmall, hprod⟩
  have hp : Nat.Prime 7 := by decide
  have hd : 7 ∣ xs.prod := by rw [hprod]
  obtain ⟨a, ha, hd⟩ := hp.prime.dvd_prod_iff.mp hd
  have hs := hsmall a ha
  have hle := Nat.le_of_dvd hs.1 hd
  omega

theorem composite_control : ([2, 2, 3] : List ℕ).prod = 12 := by decide

end mse_25914__ans25916
