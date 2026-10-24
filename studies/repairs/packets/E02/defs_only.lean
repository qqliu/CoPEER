/-!
Record SE_cs_1200__a1206 (E02).  Core Lean only, no imports.

Source (cs.stackexchange reply a1206 to question 1200), quoted local claim:
"consider the assignment `A[A[0]-1] := A[0]` under the precondition `A[0] = 2 ∧ A[1] = 3`:
you cannot make a simple substitution to obtain the correct postcondition `A[0] = 1 ∧ A[1] = 1`".
The content under test is the Hoare triple
  `{A[0]=2 ∧ A[1]=3}  A[A[0]-1] := A[0]  {A[0]=1 ∧ A[1]=1}`,
stated below as `HoareTriple` over the operational reading `stepR1` (index and right-hand
side evaluated in the pre-state).  `stepR2` and `stepR3` are two further operational readings
of the same command.  Stores are integer lists; out-of-range reads return 0; an out-of-range
write is an error (`none`).
-/

namespace SE_cs_1200_a1206_Census

abbrev Store := List Int

def getI (s : Store) (i : Nat) : Int := s.getD i 0

def setI (s : Store) (i : Nat) (v : Int) : Store := s.set i v

def writeAt (s : Store) (i : Int) (v : Int) : Option Store :=
  if decide (0 ≤ i) && decide (i < Int.ofNat s.length) then some (setI s i.toNat v) else none

def pre (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 3)

def post (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 1) && decide (getI s 1 = 1)

def stepR1 (s : Store) : Option Store :=
  writeAt s (getI s 0 - 1) (getI s 0)

def stepR2 (s : Store) : Option Store :=
  match writeAt s (getI s 0 - 1) (getI s 0) with
  | none   => none
  | some t => writeAt t (getI s 0 - 1) (getI t 0)

def stepR3 (s : Store) : Option Store :=
  let v := getI s 0
  writeAt s (getI s 0 - 1) v

def holds (p : Store → Bool) : Option Store → Bool
  | none   => false
  | some t => p t

def resultIs : Option Store → Store → Bool
  | none,   _ => false
  | some t, u => decide (t = u)

/-- The located claim: the source's Hoare triple `{pre} A[A[0]-1] := A[0] {post}`
(total correctness, reading `stepR1`). -/
def HoareTriple : Prop := ∀ s : Store, pre s = true → holds post (stepR1 s) = true

end SE_cs_1200_a1206_Census
