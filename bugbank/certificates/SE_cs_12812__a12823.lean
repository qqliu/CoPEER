/- Human-review certificate. Original witness preserved; historical certificate remains in the frozen packet. -/
namespace DnfSatFirstDisjunct
-- The original formula (x AND NOT x) OR x under an arbitrary assignment.
def firstDisjunct (x : Bool) : Prop := x = true ∧ ¬x = true
def formula (x : Bool) : Prop := firstDisjunct x ∨ x = true
theorem certificate : (∀ x : Bool, ¬firstDisjunct x) ∧ formula true := by
 exact ⟨fun x h => h.2 h.1, Or.inr rfl⟩
end DnfSatFirstDisjunct
