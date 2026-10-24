import Mathlib
/-! Correctly retains the source range: the n=118 calculation lists primes
between 118 and 157 (157<4*118/3). Both open and closed conventions are
checked; 139 is spurious and 149 is omitted under either convention. -/
set_option maxRecDepth 8192
set_option maxHeartbeats 800000
namespace ProofWiki56736

def qualifiesOpen (p : ℕ) : Prop := 118 < p ∧ p < 157 ∧ Nat.Prime p ∧ p % 4 = 1
def qualifiesClosed (p : ℕ) : Prop := 118 ≤ p ∧ p ≤ 157 ∧ Nat.Prime p ∧ p % 4 = 1
instance (p : ℕ) : Decidable (qualifiesOpen p) := by unfold qualifiesOpen; infer_instance
instance (p : ℕ) : Decidable (qualifiesClosed p) := by unfold qualifiesClosed; infer_instance

def claimedEnumeration : Finset ℕ := {137, 139, 157}
def openQualifying : Finset ℕ := (Finset.Icc 118 157).filter qualifiesOpen
def closedQualifying : Finset ℕ := (Finset.Icc 118 157).filter qualifiesClosed

theorem refutes_published_open_interval_enumeration :
    Nat.Prime 139 ∧ 139 % 4 = 3 ∧
    qualifiesOpen 149 ∧ 149 ∉ claimedEnumeration ∧
    139 ∈ claimedEnumeration ∧ ¬ qualifiesClosed 139 ∧
    openQualifying ≠ claimedEnumeration ∧ closedQualifying ≠ claimedEnumeration := by
  decide

theorem negative_control_corrected_enumerations_are_exact_and_nonempty :
    openQualifying = {137, 149} ∧ closedQualifying = {137, 149, 157} := by
  decide
end ProofWiki56736
