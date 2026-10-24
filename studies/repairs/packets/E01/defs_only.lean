/- Record SE_cs_97637__a97647 (E01).  Core Lean only; no Mathlib.

Specification `R x y`: `y` is the integer square root of `x`, i.e. `y*y ≤ x < (y+1)*(y+1)`.
The program `prog` is the source's incremental square-root routine: `prog 0 = 0`, and for
input `n + 1`, with `b = prog n`, it returns `b` if `n + 1 ≤ (b+1)*(b+1)` and `b + 1` otherwise.
The located claim is that `prog` meets `R` on every input (`ProgramCorrect`). -/

set_option maxRecDepth 10000

namespace SqrtFailureBoundary

abbrev R (x y : Nat) : Prop := y * y ≤ x ∧ x < (y + 1) * (y + 1)

def prog : Nat → Nat
  | 0 => 0
  | n + 1 =>
      let b := prog n
      if n + 1 ≤ (b + 1) * (b + 1) then b else b + 1

/-- The located claim: the program meets the specification on every natural input. -/
def ProgramCorrect : Prop := ∀ x : Nat, R x (prog x)

end SqrtFailureBoundary
