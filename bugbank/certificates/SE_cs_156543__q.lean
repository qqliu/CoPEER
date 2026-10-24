/- Review overlay for SE_cs_156543__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

import Mathlib

set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

namespace SEcs156543q

structure Letter where
  p1e : Bool
  p2e : Bool
  p1c : Bool
  p2c : Bool

def emptyL : Letter := ⟨false, false, false, false⟩

def eeL    : Letter := ⟨true,  true,  false, false⟩

def c1L    : Letter := ⟨false, false, true,  false⟩

def eqLetter (a b : Letter) : Bool :=
  (a.p1e == b.p1e) && (a.p2e == b.p2e) && (a.p1c == b.p1c) && (a.p2c == b.p2c)

def eqWord : List Letter → List Letter → Bool
  | [],      []      => true
  | a :: as, b :: bs => eqLetter a b && eqWord as bs
  | _,       _       => false

def upto : Nat → List Nat := List.range

def bindL {α β : Type} : List α → (α → List β) → List β
  | [],      _ => []
  | a :: as, f => f a ++ bindL as f

def anyOf (p : Nat → Bool) : List Nat → Bool := fun xs => xs.any p

def allOf (p : Nat → Bool) : List Nat → Bool := fun xs => xs.all p

def nthLetter : List Letter → Nat → Letter → Letter
  | [],      _,     d => d
  | a :: _,  0,     _ => a
  | _ :: as, k + 1, d => nthLetter as k d

def allLetters : List Letter :=
  bindL [false, true] (fun a =>
    bindL [false, true] (fun b =>
      bindL [false, true] (fun c =>
        [false, true].map (fun d => (⟨a, b, c, d⟩ : Letter)))))

def wordsOfLen : Nat → List (List Letter)
  | 0     => [[]]
  | n + 1 => bindL (wordsOfLen n) (fun w => allLetters.map (fun a => w ++ [a]))

structure Lasso where
  stem : List Letter
  loop : List Letter

def wfLasso (L : Lasso) : Bool :=
  match L.loop with
  | []     => false
  | _ :: _ => true

def numNodes (L : Lasso) : Nat := L.stem.length + L.loop.length

def succNode (L : Lasso) (k : Nat) : Nat :=
  if k + 1 < numNodes L then k + 1 else L.stem.length

def letterAtNode (L : Lasso) (k : Nat) : Letter :=
  nthLetter (L.stem ++ L.loop) k emptyL

def stepN (L : Lasso) : Nat → Nat → Nat
  | 0,     k => k
  | j + 1, k => stepN L j (succNode L k)

def orbit (L : Lasso) (k : Nat) : List Nat :=
  (upto (numNodes L)).map (fun j => stepN L j k)

def nodeOfPos (L : Lasso) : Nat → Nat
  | 0     => 0
  | p + 1 => succNode L (nodeOfPos L p)

def prefixWord (L : Lasso) (n : Nat) : List Letter :=
  (upto n).map (fun p => letterAtNode L (nodeOfPos L p))

def hasPrefix (L : Lasso) (w : List Letter) : Bool :=
  eqWord (prefixWord L w.length) w

inductive Atom where
  | p1e | p2e | p1c | p2c

inductive LTL where
  | atom : Atom → LTL
  | neg  : LTL → LTL
  | conj : LTL → LTL → LTL
  | disj : LTL → LTL → LTL
  | imp  : LTL → LTL → LTL
  | next : LTL → LTL
  | fin  : LTL → LTL          -- `F`
  | glob : LTL → LTL          -- `G`

def evalAtom : Atom → Letter → Bool
  | .p1e, v => v.p1e
  | .p2e, v => v.p2e
  | .p1c, v => v.p1c
  | .p2c, v => v.p2c

def satF : Nat → Lasso → LTL → Nat → Bool
  | 0,     _, _, _ => false
  | n + 1, L, f, k =>
    match f with
    | .atom a   => evalAtom a (letterAtNode L k)
    | .neg g    => !satF n L g k
    | .conj g h => satF n L g k && satF n L h k
    | .disj g h => satF n L g k || satF n L h k
    | .imp g h  => (!satF n L g k) || satF n L h k
    | .next g   => satF n L g (succNode L k)
    | .fin g    => anyOf (satF n L g) (orbit L k)
    | .glob g   => allOf (satF n L g) (orbit L k)

def fuel : Nat := 16

def satPos (L : Lasso) (f : LTL) (p : Nat) : Bool :=
  satF fuel L f (nodeOfPos L p)

def phi : LTL :=
  .imp (.conj (.atom .p1e) (.atom .p2e)) (.fin (.disj (.atom .p1c) (.atom .p2c)))

def gphi : LTL := .glob phi

def psiSafe : LTL := .glob (.neg (.atom .p1c))

def sigma : Lasso := ⟨[eeL], [emptyL]⟩

def sigmaPrime : Lasso := ⟨[eeL], [c1L]⟩

def sigmaHat : List Letter := [eeL]

theorem witnesses_wellformed :
    (wfLasso sigma && wfLasso sigmaPrime) = true := by decide

theorem sigma_violates_phi_at_0 : satPos sigma phi 0 = false := by decide

theorem sigma_not_in_P : satPos sigma gphi 0 = false := by decide

theorem sigmaHat_is_the_prefix_of_sigma :
    eqWord (prefixWord sigma 1) sigmaHat = true := by decide

theorem sigmaPrime_extends_sigmaHat :
    hasPrefix sigmaPrime sigmaHat = true := by decide

theorem sigmaPrime_satisfies_phi_at_0 : satPos sigmaPrime phi 0 = true := by decide

theorem sigmaPrime_in_P : satPos sigmaPrime gphi 0 = true := by decide

def stepInstance (f : LTL) (base : Lasso) (i : Nat) (ext : Lasso) : Bool :=
  (!((!satPos base f i) && hasPrefix ext (prefixWord base (i + 1))))
    || (!satPos ext f i)

theorem line0016_step_fails :
    stepInstance phi sigma 0 sigmaPrime = false := by decide

theorem line0016_hypotheses_hold_conclusion_fails :
    ((!satPos sigma phi 0) && hasPrefix sigmaPrime (prefixWord sigma 1)
      && satPos sigmaPrime phi 0) = true := by decide

theorem sigmaHat_is_not_a_bad_prefix :
    (hasPrefix sigmaPrime sigmaHat && satPos sigmaPrime gphi 0) = true := by decide

def smallWords : List (List Letter) := wordsOfLen 1 ++ wordsOfLen 2

def allPairs : List (List Letter × Nat) :=
  bindL smallWords (fun w => (upto w.length).map (fun i => (w, i)))

def isAdmissible (p : List Letter × Nat) : Bool :=
  !satPos ⟨p.1, [emptyL]⟩ phi p.2

def admissible : List (List Letter × Nat) := allPairs.filter isAdmissible

theorem sweep_size : (smallWords.length = 272) ∧ (allPairs.length = 528) := by
  decide

theorem admissible_count : admissible.length = 21 := by decide

theorem admissible_count_at_last_position :
    (admissible.filter (fun p => p.2 + 1 == p.1.length)).length = 17 := by decide

theorem every_admissible_pair_is_repaired :
    admissible.all (fun p =>
      hasPrefix ⟨p.1, [c1L]⟩ p.1 && satPos ⟨p.1, [c1L]⟩ phi p.2) = true := by
  decide

theorem step_fails_on_every_admissible_pair :
    admissible.all (fun p =>
      stepInstance phi ⟨p.1, [emptyL]⟩ p.2 ⟨p.1, [c1L]⟩ == false) = true := by
  decide

theorem no_bad_prefixes_of_length_le_2 :
    smallWords.all (fun w =>
      hasPrefix ⟨w, [c1L]⟩ w && satPos ⟨w, [c1L]⟩ gphi 0) = true := by
  decide

theorem nc_atoms_are_read :
    (satPos sigma (.atom .p1e) 0 && !satPos sigma (.atom .p1c) 0
      && satPos sigmaPrime (.atom .p1c) 1 && !satPos sigmaPrime (.atom .p1e) 1)
      = true := by decide

theorem nc_F_and_G_discriminate :
    ((!satPos sigma (.fin (.atom .p1c)) 0)
      && satPos sigmaPrime (.fin (.atom .p1c)) 0
      && satPos sigmaPrime (.glob (.fin (.atom .p1c))) 0
      && (!satPos ⟨[c1L], [emptyL]⟩ (.glob (.fin (.atom .p1c))) 0)) = true := by
  decide

theorem nc_lasso_wraps :
    ((nodeOfPos sigmaPrime 1 == nodeOfPos sigmaPrime 2)
      && satPos sigmaPrime (.next (.atom .p1c)) 0
      && eqWord (prefixWord sigmaPrime 3) [eeL, c1L, c1L]) = true := by decide

theorem nc_fuel_stable :
    ((satF 8 sigma phi (nodeOfPos sigma 0) == satF 16 sigma phi (nodeOfPos sigma 0))
      && (satF 8 sigmaPrime phi (nodeOfPos sigmaPrime 0)
            == satF 16 sigmaPrime phi (nodeOfPos sigmaPrime 0))
      && (satF 8 sigma gphi (nodeOfPos sigma 0) == satF 16 sigma gphi (nodeOfPos sigma 0))
      && (satF 8 sigmaPrime gphi (nodeOfPos sigmaPrime 0)
            == satF 16 sigmaPrime gphi (nodeOfPos sigmaPrime 0))) = true := by
  decide

theorem nc_step_can_hold : stepInstance phi sigma 0 sigma = true := by decide

theorem nc_real_safety_formula_has_a_bad_prefix :
    (wordsOfLen 0 ++ wordsOfLen 1).all (fun w =>
      allLetters.all (fun v =>
        !satPos ⟨[c1L] ++ w, [v]⟩ psiSafe 0)) = true := by
  decide

theorem nc_step_is_valid_for_a_real_safety_formula :
    (wordsOfLen 0 ++ wordsOfLen 1).all (fun w =>
      allLetters.all (fun v =>
        stepInstance psiSafe ⟨[c1L], [emptyL]⟩ 0 ⟨[c1L] ++ w, [v]⟩)) = true := by
  decide

theorem nc_liveness_argument_is_correct :
    smallWords.all (fun w =>
      hasPrefix ⟨w ++ [c1L], [emptyL]⟩ w
        && satPos ⟨w ++ [c1L], [emptyL]⟩ gphi 0) = true := by
  decide

theorem nc_Gphi_is_not_trivial :
    (allLetters.any (fun v => !satPos ⟨[eeL], [v]⟩ gphi 0)
      && allLetters.any (fun v => satPos ⟨[eeL], [v]⟩ gphi 0)) = true := by
  decide

theorem nc_alphabet_complete :
    (allLetters.length = 16)
      ∧ (allLetters.all (fun a =>
          (allLetters.filter (fun b => eqLetter a b)).length == 1) = true) := by
  decide

def PhiInfinite (w : Nat → Letter) (i : Nat) : Prop :=
  ((w i).p1e = true ∧ (w i).p2e = true) →
    ∃ j : Nat, i ≤ j ∧ ((w j).p1c = true ∨ (w j).p2c = true)

def sigmaInfinite (n : Nat) : Letter := if n = 0 then eeL else emptyL
def sigmaPrimeInfinite (n : Nat) : Letter := if n = 0 then eeL else c1L

theorem infinite_word_refutation :
    ¬PhiInfinite sigmaInfinite 0 ∧
    sigmaInfinite 0 = sigmaPrimeInfinite 0 ∧
    (∀ i : Nat, PhiInfinite sigmaPrimeInfinite i) := by
  constructor
  · intro h
    obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
    by_cases h0 : j = 0 <;>
      simp [sigmaInfinite, h0, eeL, emptyL] at hj
  constructor
  · rfl
  · intro i hi
    by_cases h0 : i = 0
    · subst i
      exact ⟨1, by decide, Or.inl rfl⟩
    · simp [sigmaPrimeInfinite, h0, c1L] at hi

end SEcs156543q
