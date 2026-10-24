/- Review overlay for SE_cs_1597__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/



set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

namespace SE_cs_1597_q

def llen {α : Type} : List α → Nat := List.length

def lmap {α β : Type} : List α → (α → β) → List β := fun xs f => xs.map f

def lapp {α : Type} : List α → List α → List α := List.append

def joinLL {α : Type} : List (List α) → List α := List.flatten

def lall {α : Type} : List α → (α → Bool) → Bool := fun xs f => xs.all f

def lany {α : Type} : List α → (α → Bool) → Bool := fun xs f => xs.any f

def lfilter {α : Type} : List α → (α → Bool) → List α := fun xs f => xs.filter f

def upto : Nat → List Nat := List.range

def eqN (a b : Nat) : Bool := Nat.beq a b

def ltN (a b : Nat) : Bool := Nat.blt a b

def ieqB (a b : Int) : Bool := decide (a = b)

def imax (a b : Int) : Int :=
  match decide (a ≤ b) with
  | true => b
  | false => a

def imaxFrom : Int → List Int → Int
  | best, [] => best
  | best, a :: as => imaxFrom (imax best a) as

def imaxNE : List Int → Int
  | [] => 0
  | a :: as => imaxFrom a as

def nthN : List Nat → Nat → Nat
  | [], _ => 0
  | a :: _, 0 => a
  | _ :: as, n + 1 => nthN as n

def hdN : List Nat → Nat
  | [] => 0
  | a :: _ => a

def tlN : List Nat → List Nat
  | [] => []
  | _ :: as => as

def lEqN : List Nat → List Nat → Bool
  | [], [] => true
  | a :: as, b :: bs => eqN a b && lEqN as bs
  | _, _ => false

def memLL : List Nat → List (List Nat) → Bool
  | _, [] => false
  | x, a :: as => lEqN a x || memLL x as

def countN : Nat → List Nat → Nat
  | _, [] => 0
  | x, a :: as => match eqN a x with
                  | true => Nat.succ (countN x as)
                  | false => countN x as

abbrev Mat := List (List Int)

def rowOf : Mat → Nat → List Int
  | [], _ => []
  | r :: _, 0 => r
  | _ :: rs, i + 1 => rowOf rs i

def nthI : List Int → Nat → Int
  | [], _ => 0
  | a :: _, 0 => a
  | _ :: as, j + 1 => nthI as j

def getE (A : Mat) (i j : Nat) : Int := nthI (rowOf A i) j

def isSquare (A : Mat) (n : Nat) : Bool :=
  eqN (llen A) n && lall A (fun r => eqN (llen r) n)

def dpS : Mat → Nat → Nat → Nat → Int
  | A, r, c, 0 => getE A r c
  | A, r, c, k + 1 =>
      imax
        (imax (getE A r c             + dpS A (r + 1) (c + 1) k)
              (getE A r (c + k + 1)   + dpS A (r + 1) c       k))
        (imax (getE A (r + k + 1) c           + dpS A r (c + 1) k)
              (getE A (r + k + 1) (c + k + 1) + dpS A r c       k))

def dpFull (A : Mat) (n : Nat) : Int := dpS A 0 0 (n - 1)

def insertsOf (x : Nat) : List Nat → List (List Nat)
  | [] => [[x]]
  | a :: as => (x :: a :: as) :: lmap (insertsOf x as) (fun t => a :: t)

def permsOf : List Nat → List (List Nat)
  | [] => [[]]
  | a :: as => joinLL (lmap (permsOf as) (fun p => insertsOf a p))

def assignSumFrom : Mat → Nat → List Nat → Int
  | _, _, [] => 0
  | A, i, c :: cs => getE A i c + assignSumFrom A (i + 1) cs

def assignSum (A : Mat) (p : List Nat) : Int := assignSumFrom A 0 p

def isPermOfB (n : Nat) (p : List Nat) : Bool :=
  eqN (llen p) n && lall (upto n) (fun j => eqN (countN j p) 1)

def optAssign (A : Mat) (n : Nat) : Int :=
  imaxNE (lmap (permsOf (upto n)) (assignSum A))

def claimHolds (A : Mat) (n : Nat) : Bool :=
  match isSquare A n && ltN 0 n with
  | false => true
  | true => ieqB (dpFull A n) (optAssign A n)

def selCells : Nat → Nat → Nat → List Nat → List (Nat × Nat)
  | r, c, 0, _ => [(r, c)]
  | r, c, k + 1, ch =>
      match hdN ch with
      | 0 => (r, c)                   :: selCells (r + 1) (c + 1) k (tlN ch)
      | 1 => (r, c + k + 1)           :: selCells (r + 1) c       k (tlN ch)
      | 2 => (r + k + 1, c)           :: selCells r       (c + 1) k (tlN ch)
      | _ => (r + k + 1, c + k + 1)   :: selCells r       c       k (tlN ch)

def choiceSeqs : Nat → List (List Nat)
  | 0 => [[]]
  | k + 1 =>
      joinLL (lmap ([0, 1, 2, 3] : List Nat) (fun b => lmap (choiceSeqs k) (fun t => b :: t)))

def cellSum : Mat → List (Nat × Nat) → Int
  | _, [] => 0
  | A, (i, j) :: rest => getE A i j + cellSum A rest

def colAt : List (Nat × Nat) → Nat → Nat
  | [], _ => 0
  | (a, b) :: rest, i => match eqN a i with
                         | true => b
                         | false => colAt rest i

def permOfCells (n : Nat) (cells : List (Nat × Nat)) : List Nat :=
  lmap (upto n) (fun i => colAt cells i)

def selections (n : Nat) : List (List (Nat × Nat)) :=
  lmap (choiceSeqs (n - 1)) (fun ch => selCells 0 0 (n - 1) ch)

def reachPermsRaw (n : Nat) : List (List Nat) :=
  lmap (selections n) (permOfCells n)

def reachPerms (n : Nat) : List (List Nat) :=
  lfilter (permsOf (upto n)) (fun p => memLL p (reachPermsRaw n))

def missingPerms (n : Nat) : List (List Nat) :=
  lfilter (permsOf (upto n)) (fun p => !(memLL p (reachPerms n)))

def avoidsCorners (n : Nat) (p : List Nat) : Bool :=
  !(eqN (nthN p 0) 0) && !(eqN (nthN p 0) (n - 1))
    && !(eqN (nthN p (n - 1)) 0) && !(eqN (nthN p (n - 1)) (n - 1))

def W : Mat := [[0, 0, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 0, 0, 0]]

def sigmaOpt : List Nat := [1, 3, 0, 2]

def sigmaOpt2 : List Nat := [2, 3, 0, 1]

def optPerms : List (List Nat) :=
  lfilter (permsOf (upto 4)) (fun p => ieqB (assignSum W p) 2)

theorem SE_cs_1597__q_four_corner_recurrence_is_not_optimal :
    (isSquare W 4 = true)
  ∧ (dpFull W 4 = 1)
  ∧ (isPermOfB 4 sigmaOpt = true)
  ∧ (assignSum W sigmaOpt = 2)
  ∧ (optAssign W 4 = 2)
  ∧ (claimHolds W 4 = false) := by decide

theorem SE_cs_1597__q_strict_undercount :
    (dpFull W 4 < optAssign W 4)
  ∧ (isPermOfB 4 sigmaOpt2 = true)
  ∧ (assignSum W sigmaOpt2 = 2)
  ∧ (getE W 1 3 = 1) ∧ (getE W 2 0 = 1)
  ∧ (getE W 0 0 = 0) ∧ (getE W 0 3 = 0) ∧ (getE W 3 0 = 0) ∧ (getE W 3 3 = 0) := by decide

theorem SE_cs_1597__q_recurrence_misses_the_corner_free_selections :
    -- every branch-choice sequence yields a legal assignment (so `S <= OPT` always)
    (llen (selections 4) = 64)
  ∧ (lall (reachPermsRaw 4) (fun p => isPermOfB 4 p) = true)
    -- and the recurrence's value is exactly the best over what it can reach
  ∧ (dpFull W 4 = imaxNE (lmap (selections 4) (cellSum W)))
  ∧ (imaxNE (lmap (selections 4) (cellSum W)) = 1)
    -- but it can reach only 20 of the 24 permutations
  ∧ (llen (permsOf (upto 4)) = 24)
  ∧ (llen (reachPerms 4) = 20)
  ∧ (llen (missingPerms 4) = 4)
    -- reachable  <=>  uses at least one corner of the whole array
  ∧ (lall (reachPerms 4) (fun p => !(avoidsCorners 4 p)) = true)
  ∧ (lall (missingPerms 4) (fun p => avoidsCorners 4 p) = true)
  ∧ (llen (lfilter (permsOf (upto 4)) (fun p => avoidsCorners 4 p)) = 4)
    -- the optima of `W` are unreachable
  ∧ (memLL sigmaOpt (reachPerms 4) = false)
  ∧ (memLL sigmaOpt2 (reachPerms 4) = false)
    -- at side 3 nothing is missed, which is why the bug first shows at side 4
  ∧ (llen (reachPerms 3) = 6)
  ∧ (llen (permsOf (upto 3)) = 6)
  ∧ (llen (missingPerms 3) = 0) := by decide

theorem SE_cs_1597__q_every_optimum_avoids_every_corner :
    (llen optPerms = 2)
  ∧ (lall optPerms (fun p => isPermOfB 4 p) = true)
  ∧ (lall optPerms (fun p => avoidsCorners 4 p) = true)
  ∧ (lany optPerms (fun p => lEqN p sigmaOpt) = true)
  ∧ (lany optPerms (fun p => lEqN p sigmaOpt2) = true)
    -- and no selection at all beats 2
  ∧ (lall (permsOf (upto 4)) (fun p => decide (assignSum W p ≤ 2)) = true) := by decide

def E5 : Mat :=
  [[5, 4, 3, 2, 1],
   [4, 3, 2, 1, 5],
   [3, 2, 1, 5, 4],
   [2, 1, 5, 4, 3],
   [1, 5, 4, 3, 2]]

def Wcorner : Mat := [[0, 0, 0, 1], [0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0]]

def I4 : Mat := [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

theorem SE_cs_1597__q_negative_control :
    -- (a) On the question's own worked example the recurrence is RIGHT, and reproduces the
    -- printed answer 25.  So `claimHolds` is not the constantly-false predicate.
    (dpFull E5 5 = 25) ∧ (optAssign E5 5 = 25) ∧ (claimHolds E5 5 = true)
  ∧ (isSquare E5 5 = true)
    -- (b) Moving one witness entry onto a corner repairs the recurrence: the failure is about
    -- WHERE the mass sits, not about the encoding of `W`.
  ∧ (dpFull Wcorner 4 = 2) ∧ (optAssign Wcorner 4 = 2) ∧ (claimHolds Wcorner 4 = true)
    -- (c) Diagonal case: both computations return 4.
  ∧ (dpFull I4 4 = 4) ∧ (optAssign I4 4 = 4) ∧ (claimHolds I4 4 = true)
    -- (d) `optAssign` is a real maximum, not a constant: it moves with the array.
  ∧ (optAssign [[0, 0], [0, 0]] 2 = 0) ∧ (optAssign [[7, 0], [0, 7]] 2 = 14)
  ∧ (optAssign [[0, 7], [7, 0]] 2 = 14)
    -- (e) `assignSum` reads the array, and `isPermOfB` rejects non-selections.
  ∧ (assignSum W [0, 1, 2, 3] = 0)
  ∧ (assignSum W sigmaOpt = 2)
  ∧ (isPermOfB 4 [0, 1, 1, 3] = false)
  ∧ (isPermOfB 4 [1, 3, 0] = false)
  ∧ (isPermOfB 4 sigmaOpt = true)
    -- (f) the guard fails closed: malformed input can never manufacture a refutation.
  ∧ (isSquare [[1, 2]] 2 = false) ∧ (claimHolds [[1, 2]] 2 = true)
  ∧ (isSquare W 3 = false) ∧ (claimHolds W 3 = true)
  ∧ (claimHolds [] 0 = true)
    -- (g) negative entries are handled (the max is not silently clamped at 0).
  ∧ (optAssign [[-3, -1], [-1, -3]] 2 = -2) ∧ (dpFull [[-3, -1], [-1, -3]] 2 = -2)
  ∧ (claimHolds [[-3, -1], [-1, -3]] 2 = true) := by decide

def vals3 : List Int := [0, 1, 2]
def bits : List Int := [0, 1]

def rows2 : List (List Int) := joinLL (lmap vals3 (fun a => lmap vals3 (fun b => [a, b])))

def allMats2 : List Mat :=
  joinLL (lmap rows2 (fun r1 => lmap rows2 (fun r2 => [r1, r2])))

def rows3 : List (List Int) :=
  joinLL (lmap bits (fun a => joinLL (lmap bits (fun b => lmap bits (fun c => [a, b, c])))))

def allMats3 : List Mat :=
  joinLL (lmap rows3 (fun r1 => joinLL (lmap rows3 (fun r2 => lmap rows3 (fun r3 => [r1, r2, r3])))))

theorem SE_cs_1597__q_agrees_on_all_small_arrays :
    (llen allMats2 = 81)
  ∧ (lall allMats2 (fun A => isSquare A 2) = true)
  ∧ (lall allMats2 (fun A => claimHolds A 2) = true)
  ∧ (llen allMats3 = 512)
  ∧ (lall allMats3 (fun A => isSquare A 3) = true)
  ∧ (lall allMats3 (fun A => claimHolds A 3) = true) := by decide

end SE_cs_1597_q
