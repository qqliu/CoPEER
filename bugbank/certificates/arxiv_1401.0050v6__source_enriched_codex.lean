import Mathlib.Data.Fintype.Powerset
import Mathlib.Data.Finset.Union
import Mathlib.Tactic

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
namespace Arxiv1401_0050v6Mathlib

abbrev Col := Fin 6
abbrev Row := Fin 6
abbrev Code := Col → Finset Row
/-- Original supports, with the source row labels 1,...,6 shifted to 0,...,5.
Columns 0,1,2 are A,B,C; columns 3,4,5 are D,E,F. -/
def X : Code := fun i =>
  if i = 0 then {0,1} else if i = 1 then {0,2} else if i = 2 then {1,2}
  else if i = 3 then {3} else if i = 4 then {4} else {5}

def s : ℕ := 4
def L : ℕ := 2
/-- Boolean columns are precisely the characteristic functions of the supports. -/
def bit (Y : Code) (j : Col) (r : Row) : Bool := decide (r ∈ Y j)
def coveredOutside (Y : Code) (S : Finset Col) : Finset Col :=
  Finset.univ.filter (fun j => j ∉ S ∧ Y j ⊆ S.biUnion Y)
/-- Literal source Definition 2: every s-set covers at most L-1 outside columns. -/
def LD (Y : Code) : Prop :=
  ∀ S : Finset Col, S.card = s → (coveredOutside Y S).card ≤ L - 1
instance (Y : Code) : Decidable (LD Y) := by unfold LD; infer_instance
/-- Literal source badness: exactly floor(s/L) distinct other columns cover j. -/
def Bad (Y : Code) (j : Col) : Prop :=
  ∃ S : Finset Col, S.card = s / L ∧ j ∉ S ∧ Y j ⊆ S.biUnion Y
instance (Y : Code) (j : Col) : Decidable (Bad Y j) := by unfold Bad; infer_instance
def badColumns (Y : Code) : Finset Col := Finset.univ.filter (Bad Y)

/-- The support containment used throughout is precisely coordinatewise Boolean
coverage by the disjunct union of the selected columns. -/
theorem coverage_iff_boolean (Y : Code) (j : Col) (S : Finset Col) :
    Y j ⊆ S.biUnion Y ↔
      ∀ r : Row, bit Y j r = true → ∃ k ∈ S, bit Y k r = true := by
  simp only [bit, decide_eq_true_eq, Finset.subset_iff, Finset.mem_biUnion]

theorem parameter_restrictions :
    1 ≤ s ∧ s < Fintype.card Col ∧ 1 ≤ L ∧ L ≤ Fintype.card Col - s ∧
    s > L ∧ 2 ≤ L ∧ Fintype.card Row = 6 ∧ Fintype.card Col = 6 ∧
    s / L = 2 ∧ L - 1 = 1 := by decide

theorem columns_distinct : Function.Injective X := by decide
/-- Quantification is over all Finset Col, hence all 64 subsets and all fifteen
four-element selections; no externally supplied coverage table is assumed. -/
theorem is_LD : LD X := by decide

theorem exactly_three_bad : badColumns X = {0,1,2} := by decide

theorem original_witness_refutes :
    Function.Injective X ∧ LD X ∧
    badColumns X = {0,1,2} ∧ (badColumns X).card = 3 ∧
    ¬ (badColumns X).card ≤ L - 1 := by
  exact ⟨columns_distinct,is_LD,exactly_three_bad,by decide,by decide⟩

/-- One admissible original code refutes the literal universal bound. This makes
no claim that the later extremal/rate bounds cannot have a different proof. -/
theorem refutes_universal_bad_column_bound :
    ¬ ∀ Y : Code, Function.Injective Y → LD Y → (badColumns Y).card ≤ L - 1 := by
  intro h
  exact original_witness_refutes.2.2.2.2 (h X columns_distinct is_LD)

end Arxiv1401_0050v6Mathlib
#print axioms Arxiv1401_0050v6Mathlib.original_witness_refutes
#print axioms Arxiv1401_0050v6Mathlib.refutes_universal_bad_column_bound
