import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Pi
import Mathlib.Data.Finset.BooleanAlgebra
import Mathlib.Tactic

/-! Keep the source packet's explicit admissible family { {1}, {1,2}, {3,4} }.
The isolated complementary pair has only two members and does not satisfy
|F|≥3; the packet already supplied this three-member extension. The offending
sets themselves remain {1,2} and {3,4}. All set operations use Mathlib Finset. -/
namespace MSE3703719
abbrev S := Finset (Fin 4)
def A : S := {0,1}
def B : S := {2,3}
def family : Finset S := {{0}, A, B}
def normalize (s : S) : S := if 4 < 2*s.card then sᶜ else s
def normalized : Finset S := (family.filter (fun s => s ≠ ∅ ∧ s ≠ Finset.univ)).image normalize

def cells (a b c : S) : Finset (Bool × Bool × Bool) :=
  Finset.univ.image (fun x : Fin 4 => (decide (x ∈ a), decide (x ∈ b), decide (x ∈ c)))

theorem source_hypotheses :
    family.card = 3 ∧
    (∀ a ∈ family, ∀ b ∈ family, ∀ c ∈ family, (cells a b c).card ≤ 3) ∧
    normalized = family := by decide

theorem certificate :
    A ∈ normalized ∧ B ∈ normalized ∧ A.card = 2 ∧ B.card = 2 ∧
    Aᶜ ∩ Bᶜ = ∅ ∧ ¬ (Aᶜ ∩ Bᶜ).Nonempty := by decide
end MSE3703719
