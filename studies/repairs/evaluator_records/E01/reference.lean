import defs_only
/- EVALUATOR-ONLY reference correction for E01 (original package: progStrict, line 24; strict_guard_correct, line 35). -/
namespace SqrtFailureBoundary.Ref

/-- Reference corrected step: the strict guard `n + 1 < (b + 1) * (b + 1)`. -/
def step (n b : Nat) : Nat := if n + 1 < (b + 1) * (b + 1) then b else b + 1

def progC : Nat → Nat
  | 0 => 0
  | n + 1 => step n (progC n)

end SqrtFailureBoundary.Ref
