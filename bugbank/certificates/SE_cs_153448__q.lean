/- Human-review certificate. Original witness preserved; historical certificate remains in the frozen packet. -/
import Mathlib
namespace SEcs153448
-- Source labels have been consistently renamed 0,1,2.
def mtf (L : List ℕ) (i : ℕ) : List ℕ := i :: L.erase i
def initial : List ℕ := ([2,1,0] : List ℕ).foldl mtf []
def afterFirst : List ℕ := mtf initial 1
def Phi (L : List ℕ) : ℕ :=
 ((Finset.range 3).product (Finset.range 3)).filter
  (fun p => p.1 < p.2 ∧ L.idxOf p.2 < L.idxOf p.1) |>.card
def x (L : List ℕ) (i : ℕ) : ℕ :=
 ((Finset.range 3).filter (fun j => i < j ∧ L.idxOf j < L.idxOf i)).card
-- Both lists can be initialized identically by three front insertions from the empty list.
-- A then performs no exchanges, while MF performs the requested access to 1.
theorem source_counterexample :
 initial = [0,1,2] ∧ afterFirst = [1,0,2] ∧
 Phi initial = 0 ∧ Phi afterFirst = 1 ∧ x afterFirst 2 = 0 ∧
 Phi afterFirst ≠ x afterFirst 2 ∧ Phi (mtf afterFirst 2) = 3 := by decide
end SEcs153448
