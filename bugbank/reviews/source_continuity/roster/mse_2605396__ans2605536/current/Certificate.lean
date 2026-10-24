import Mathlib.Combinatorics.Digraph.Basic
import Mathlib.Data.Finset.Powerset

/-!
Source: https://math.stackexchange.com/a/2605536, line 0007.
The source's general statement assumes n≥2k>4. Use n=6,k=3 and the transitive
tournament i beats j iff i<j. Every three-team subset has a top and bottom,
yet no team has six wins. The printed top-peel set {4,5,6} is therefore false.
The earlier five-team illustration with k=2 did not meet 2k>4; this theorem
includes all source hypotheses on the six-team witness.
Mathlib Digraph and Finset replace bespoke tournament/list enumerators.
-/
namespace mse_2605396__ans2605536

abbrev tournament : Digraph (Fin 6) := Digraph.mk' (fun i j => decide (i < j))
def wins (i : Fin 6) : ℕ := (Finset.univ.filter (tournament.Adj i)).card

def topBottom (s : Finset (Fin 6)) : Prop :=
  (∃ t ∈ s, ∀ u ∈ s, u = t ∨ tournament.Adj t u) ∧
  (∃ b ∈ s, ∀ u ∈ s, u = b ∨ tournament.Adj u b)

instance (s : Finset (Fin 6)) : Decidable (topBottom s) := inferInstanceAs
  (Decidable ((∃ t ∈ s, ∀ u ∈ s, u = t ∨ tournament.Adj t u) ∧
    (∃ b ∈ s, ∀ u ∈ s, u = b ∨ tournament.Adj u b)))

theorem admissible_tournament_refutes_printed_win_count :
    6 ≥ 2 * 3 ∧ 2 * 3 > 4 ∧
    (∀ i : Fin 6, ¬ tournament.Adj i i) ∧
    (∀ i j : Fin 6, i ≠ j → (tournament.Adj i j ↔ ¬ tournament.Adj j i)) ∧
    (∀ s ∈ (Finset.univ : Finset (Fin 6)).powersetCard 3, topBottom s) ∧
    (∀ i : Fin 6, wins i < 6) ∧ ¬ ∃ i : Fin 6, wins i = 6 := by decide

end mse_2605396__ans2605536
