import Mathlib.Data.List.Lex
import Mathlib.Tactic
namespace Arxiv230107191v3SourceEnrichedCodex
-- Increasing tuples represent the faces of the original ordered tetrahedron.
def faces : List (List ℕ) := [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
def lex (s t : List ℕ) : Prop := List.Lex (· < ·) s t
theorem refutes_printed_minimal_face_forms :
    faces.Pairwise lex ∧
    (∀ f ∈ faces, f.length = 3 ∧ f.Pairwise (· < ·)) ∧
    faces[0]? = some [0,1,2] ∧ faces[1]? = some [0,1,3] ∧
    ({0,1,2}:Finset ℕ) ∪ {0,1,3} = {0,1,2,3} ∧
    ([0,1]:List ℕ).length = 2 ∧ ([0,2]:List ℕ).length = 2 ∧
    ([0,1,2]:List ℕ) ≠ [0,1] ∧ ([0,1,3]:List ℕ) ≠ [0,2] := by
  unfold faces lex
  decide
end Arxiv230107191v3SourceEnrichedCodex
