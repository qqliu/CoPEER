import Mathlib.Data.Nat.Fib.Basic
import Mathlib.Tactic

/-!
Source: https://math.stackexchange.com/a/2662794, lines 0007–0013.
The proposed base cases are all (m,0), m≥1 and (1,n), n≥0; the two rules
conclude (m+1,n) for m>1 and (m,n+1) for n>0. Neither rule can conclude
(2,1), and it is not a base case. An inductive derivability predicate proves
this over the unbounded domain, replacing finite closure-grid simulations.
We use the more permissive reading of the side conditions (each rule requires
only the side condition needed for its two premises), so the stricter reading
fails too. Nat.fib confirms the identity itself at the missing base case.
-/
namespace mse_2662707__ans2662794

inductive Derivable : ℕ → ℕ → Prop
  | axisN (m : ℕ) (hm : 1 ≤ m) : Derivable m 0
  | axisM (n : ℕ) : Derivable 1 n
  | stepM (m n : ℕ) (hm : 1 < m)
      (hprev : Derivable (m - 1) n) (hcurr : Derivable m n) : Derivable (m + 1) n
  | stepN (m n : ℕ) (hn : 0 < n)
      (hprev : Derivable m (n - 1)) (hcurr : Derivable m n) : Derivable m (n + 1)

theorem derivable_on_axes (m n : ℕ) (h : Derivable m n) : m = 1 ∨ n = 0 := by
  induction h with
  | axisN => exact Or.inr rfl
  | axisM => exact Or.inl rfl
  | stepM m n hm _ _ _ ih => omega
  | stepN m n hn _ _ _ ih => omega

theorem missing_seed_is_unreachable : ¬ Derivable 2 1 := by
  intro h
  have := derivable_on_axes 2 1 h
  omega

theorem identity_at_missing_seed :
    Nat.fib (2 + 1) = Nat.fib 2 * Nat.fib (1 + 1) + Nat.fib (2 - 1) * Nat.fib 1 := by
  decide

end mse_2662707__ans2662794
