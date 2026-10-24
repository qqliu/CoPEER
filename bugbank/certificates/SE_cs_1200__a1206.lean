/- Review overlay for SE_cs_1200__a1206.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

namespace SE_cs_1200_a1206

abbrev Store := List Int

def getI (s : Store) (i : Nat) : Int := s.getD i 0

def setI (s : Store) (i : Nat) (v : Int) : Store := s.set i v

def writeAt (s : Store) (i : Int) (v : Int) : Option Store :=
  if decide (0 ≤ i) && decide (i < Int.ofNat s.length) then some (setI s i.toNat v) else none

def pre (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 3)

def post (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 1) && decide (getI s 1 = 1)

def postActual (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 2)

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

theorem SE_cs_1200__a1206_claimed_postcondition_unreachable :
    (pre [2, 3] = true)
  ∧ (resultIs (stepR1 [2, 3]) [2, 2] = true)
  ∧ (resultIs (stepR2 [2, 3]) [2, 2] = true)
  ∧ (resultIs (stepR3 [2, 3]) [2, 2] = true)
  ∧ (post [2, 2] = false)
  ∧ (postActual [2, 2] = true) := by decide

theorem SE_cs_1200__a1206_longer_store :
    (pre [2, 3, 0] = true)
  ∧ (resultIs (stepR1 [2, 3, 0]) [2, 2, 0] = true)
  ∧ (post [2, 2, 0] = false) := by decide

def vals : List Int := [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]

def prod2 : List Store :=
  vals.foldr (fun a acc =>
    (vals.foldr (fun b acc2 => [a, b] :: acc2) ([] : List Store)) ++ acc) ([] : List Store)

def prod3 : List Store :=
  vals.foldr (fun a acc =>
    (prod2.foldr (fun s acc2 => (a :: s) :: acc2) ([] : List Store)) ++ acc) ([] : List Store)

def box : List Store := prod2 ++ prod3

def sweepOk (s : Store) : Bool :=
  !(pre s) ||
    (!(holds post (stepR1 s)) && !(holds post (stepR2 s)) && !(holds post (stepR3 s))
      && holds postActual (stepR1 s) && holds postActual (stepR2 s)
      && holds postActual (stepR3 s))

theorem SE_cs_1200__a1206_exhaustive_sweep : box.all sweepOk = true := by decide

theorem SE_cs_1200__a1206_sweep_nonvacuous :
    (box.length = 2366) ∧ ((box.filter pre).length = 14) := by decide

theorem SE_cs_1200__a1206_negative_control :
    -- `post` is satisfiable, and reachable by this very command from another pre-state:
    (post [1, 1] = true)
  ∧ (resultIs (stepR1 [1, 1]) [1, 1] = true)
  ∧ (holds post (stepR1 [1, 1]) = true)
    -- `pre` is not constantly true:
  ∧ (pre [3, 3] = false)
  ∧ (pre [2] = false)
    -- `writeAt` genuinely writes, and genuinely fails closed out of bounds:
  ∧ (resultIs (writeAt [2, 3] 0 9) [9, 3] = true)
  ∧ (resultIs (writeAt [2, 3] 1 9) [2, 9] = true)
  ∧ ((writeAt [2, 3] (-1) 9).isNone = true)
  ∧ ((writeAt [2, 3] 2 9).isNone = true)
    -- a crashed execution satisfies nothing:
  ∧ (holds post none = false)
  ∧ (holds postActual none = false)
    -- `sweepOk` is discriminating: swapping in the *wrong* postcondition breaks it, i.e.
    -- there is a store in the box on which "the asserted postcondition holds" is refuted
    -- while "the strongest postcondition holds" is confirmed:
  ∧ (sweepOk [2, 3] = true)
  ∧ (holds post (stepR1 [2, 3]) = false)
  ∧ (holds postActual (stepR1 [2, 3]) = true) := by decide

end SE_cs_1200_a1206
