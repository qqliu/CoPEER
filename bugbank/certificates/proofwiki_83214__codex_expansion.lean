import Mathlib
/-! Uses Mathlib's elementary symmetric functions on multisets. The source
list has distinct entries, so its set and multiset interpretations agree. -/
namespace ProofWiki83214CodexExpansion

theorem refutes_equation_8_at_admissible_witness :
    (1 : ℕ) ≤ 1 ∧ 1 ≤ (2 : ℕ) ∧ ([1,2] : List ℕ).Nodup ∧
    (1 * ({2} : Multiset ℕ).esymm 1 + 2 * ({1} : Multiset ℕ).esymm 1) = 4 ∧
    (1 * ({1,2} : Multiset ℕ).esymm 1) = 3 ∧
    (1 * ({2} : Multiset ℕ).esymm 1 + 2 * ({1} : Multiset ℕ).esymm 1) ≠
      (1 * ({1,2} : Multiset ℕ).esymm 1) := by
  decide

theorem negative_control_corrected_degree :
    (1 * ({2} : Multiset ℕ).esymm 1 + 2 * ({1} : Multiset ℕ).esymm 1) =
      2 * ({1,2} : Multiset ℕ).esymm 2 := by
  decide
end ProofWiki83214CodexExpansion
