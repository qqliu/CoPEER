/- Review overlay for SE_cs_81391__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/



set_option maxRecDepth 20000
set_option maxHeartbeats 4000000

namespace QEDCert.SE_cs_81391__q

def lapp {α : Type} : List α → List α → List α := List.append

def lmap {α β : Type} : List α → (α → β) → List β := fun xs f => xs.map f

def joinLL {α : Type} : List (List α) → List α := List.flatten

def lall {α : Type} : List α → (α → Bool) → Bool := fun xs f => xs.all f

def lany {α : Type} : List α → (α → Bool) → Bool := fun xs f => xs.any f

def llen {α : Type} : List α → Nat := List.length

def upto : Nat → List Nat := List.range

def nth : List Nat → Nat → Nat
  | [],      _     => 0
  | x :: _,  0     => x
  | _ :: xs, k + 1 => nth xs k

def setAt : List Nat → Nat → Nat → List Nat
  | [],      _,     _ => []
  | _ :: xs, 0,     v => v :: xs
  | x :: xs, k + 1, v => x :: setAt xs k v

def eqL : List Nat → List Nat → Bool
  | [],      []      => true
  | x :: xs, y :: ys => Nat.beq x y && eqL xs ys
  | _,       _       => false

def isSortedB : List Nat → Bool
  | []           => true
  | [_]          => true
  | x :: y :: r  => Nat.ble x y && isSortedB (y :: r)

def insSorted (x : Nat) : List Nat → List Nat
  | []      => [x]
  | a :: as =>
      match Nat.ble x a with
      | true  => x :: a :: as
      | false => a :: insSorted x as

def sortNat : List Nat → List Nat
  | []      => []
  | a :: as => insSorted a (sortNat as)

def shiftIns (m key : Nat) : List Nat → Nat → Nat → List Nat
  | a, j, 0          => setAt a j key
  | a, j, Nat.succ f =>
      match Nat.ble m j && Nat.blt key (nth a (j - m)) with
      | true  => shiftIns m key (setAt a j (nth a (j - m))) (j - m) f
      | false => setAt a j key

def msLoop (m n : Nat) : List Nat → Nat → Nat → List Nat
  | a, _, 0          => a
  | a, i, Nat.succ f =>
      match Nat.blt i n with
      | false => a
      | true  => msLoop m n (shiftIns m (nth a i) a i (Nat.succ i)) (Nat.succ i) f

def msortIns (m : Nat) (a : List Nat) : List Nat :=
  msLoop m (llen a) a m (llen a)

def msortFirstStep (m : Nat) (a : List Nat) : List Nat :=
  msLoop m (llen a) a m 1

def chainIdx (n m : Nat) : Nat → Nat → List Nat
  | _, 0          => []
  | r, Nat.succ f =>
      match Nat.blt r n with
      | false => []
      | true  => r :: chainIdx n m (r + m) f

def gather (a : List Nat) : List Nat → List Nat
  | []      => []
  | i :: is => nth a i :: gather a is

def scatter : List Nat → List Nat → List Nat → List Nat
  | a, [],      _       => a
  | a, _ :: _,  []      => a
  | a, i :: is, v :: vs => scatter (setAt a i v) is vs

def sortChain (m n : Nat) (a : List Nat) (r : Nat) : List Nat :=
  scatter a (chainIdx n m r n) (sortNat (gather a (chainIdx n m r n)))

def chainLoop (m n : Nat) : List Nat → Nat → List Nat
  | a, 0          => a
  | a, Nat.succ r => chainLoop m n (sortChain m n a r) r

def msortChain (m : Nat) (a : List Nat) : List Nat :=
  chainLoop m (llen a) a m

def allChainsSortedB (m : Nat) (a : List Nat) : Bool :=
  lall (upto m) (fun r => isSortedB (gather a (chainIdx (llen a) m r (llen a))))

def hypExchangeB (m : Nat) (a : List Nat) : Bool :=
  Nat.blt m (llen a)
    && Nat.beq (nth (msortFirstStep m a) 0) (nth a m)
    && Nat.beq (nth (msortFirstStep m a) m) (nth a 0)
    && !(Nat.beq (nth a 0) (nth a m))

def hypLessB (m : Nat) (a : List Nat) : Bool :=
  Nat.blt m (llen a) && Nat.blt (nth a m) (nth a 0)

def conclB (m : Nat) (a : List Nat) : Bool :=
  Nat.beq (nth (msortIns m a) 0) (nth a m)

def claimAt (m : Nat) (a : List Nat) : Bool :=
  match hypExchangeB m a with
  | false => true
  | true  => conclB m a

def chainMin (m : Nat) (a : List Nat) : Nat :=
  nth (sortNat (gather a (chainIdx (llen a) m 0 (llen a)))) 0

def repairedAt (m : Nat) (a : List Nat) : Bool :=
  Nat.beq (nth (msortIns m a) 0) (chainMin m a)

def A : List Nat := [3, 4, 2, 5, 1]

def mW : Nat := 2

def B : List Nat := msortIns mW A

theorem msort_of_witness : eqL B [1, 4, 2, 5, 3] = true := by decide

theorem two_implementations_agree_on_witness :
    eqL (msortIns mW A) (msortChain mW A) = true := by decide

theorem first_step_really_exchanges :
    (eqL (msortFirstStep mW A) [2, 4, 3, 5, 1]
      && hypExchangeB mW A
      && hypLessB mW A) = true := by decide

theorem hypothesis_holds_conclusion_fails :
    (hypExchangeB mW A
      && !(conclB mW A)
      && Nat.beq (nth B 0) 1
      && Nat.beq (nth A mW) 2) = true := by decide

theorem claim_false_on_witness : claimAt mW A = false := by decide

theorem witness_diagnosis :
    (Nat.beq (nth B 0) (chainMin mW A)
      && Nat.beq (chainMin mW A) 1
      && Nat.beq (nth A 4) 1
      && eqL (gather A (chainIdx (llen A) mW 0 (llen A))) [3, 2, 1]) = true := by decide

theorem gap_sort_first_entry_claim_is_false :
    ¬ ∀ (m : Nat) (a : List Nat), claimAt m a = true := by
  intro h
  exact absurd (h mW A) (by decide)

theorem stated_implication_fails :
    ¬ ∀ (m : Nat) (a : List Nat),
        hypExchangeB m a = true → Nat.beq (nth (msortIns m a) 0) (nth a m) = true := by
  intro h
  exact absurd (h mW A (by decide)) (by decide)

theorem degenerate_witness_m_eq_1 :
    (hypExchangeB 1 [3, 2, 1]
      && eqL (msortIns 1 [3, 2, 1]) [1, 2, 3]
      && eqL (msortChain 1 [3, 2, 1]) [1, 2, 3]
      && !(conclB 1 [3, 2, 1])
      && claimAt 1 [3, 2, 1] == false) = true := by decide

def insertsOf (x : Nat) : List Nat → List (List Nat)
  | []      => [[x]]
  | a :: as => (x :: a :: as) :: lmap (insertsOf x as) (fun t => a :: t)

def permsOf : List Nat → List (List Nat)
  | []      => [[]]
  | a :: as => joinLL (lmap (permsOf as) (fun p => insertsOf a p))

def perms5 : List (List Nat) := permsOf [1, 2, 3, 4, 5]

def perms4 : List (List Nat) := permsOf [1, 2, 3, 4]

def tuples (vals : List Nat) : Nat → List (List Nat)
  | 0     => [[]]
  | k + 1 => joinLL (lmap (tuples vals k) (fun t => lmap vals (fun v => v :: t)))

def ties5 : List (List Nat) := tuples [1, 2, 3] 5

def Aties : List Nat := [3, 1, 2, 1, 1]

theorem nc_sweeps_are_populated :
    (Nat.beq (llen perms5) 120
      && Nat.beq (llen perms4) 24
      && Nat.beq (llen ties5) 243
      && lany perms5 (fun a => eqL a A)
      && lany ties5 (fun a => eqL a Aties)
      && claimAt mW Aties == false) = true := by decide

theorem nc_claim_is_not_always_false :
    (hypExchangeB 2 [2, 3, 1, 4, 5]
      && conclB 2 [2, 3, 1, 4, 5]
      && claimAt 2 [2, 3, 1, 4, 5]
      && eqL (msortIns 2 [2, 3, 1, 4, 5]) [1, 3, 2, 4, 5]) = true := by decide

theorem nc_hypothesis_discriminates :
    (hypExchangeB mW [1, 4, 2, 5, 3] == false
      && hypExchangeB mW A
      && lany perms5 (fun a => hypExchangeB mW a)
      && lany perms5 (fun a => !(hypExchangeB mW a))) = true := by decide

theorem nc_hypothesis_paraphrase_is_faithful :
    lall perms5 (fun a => hypExchangeB mW a == hypLessB mW a) = true := by decide

theorem nc_msort_is_not_degenerate :
    (eqL (msortIns mW A) A == false
      && isSortedB (msortIns mW A) == false
      && isSortedB A == false
      && eqL (msortIns 0 A) A) = true := by decide

theorem nc_msort_really_m_sorts :
    lall perms5 (fun a => allChainsSortedB mW (msortIns mW a)) = true := by decide

theorem nc_msort_is_not_a_full_sort :
    lany perms5 (fun a => !(isSortedB (msortIns mW a))) = true := by decide

theorem nc_msort_permutes_its_input :
    lall perms5 (fun a => eqL (sortNat (msortIns mW a)) (sortNat a)) = true := by decide

theorem nc_two_implementations_agree_perms5 :
    lall perms5 (fun a => eqL (msortIns mW a) (msortChain mW a)) = true := by decide

theorem nc_two_implementations_agree_perms4_all_gaps :
    lall perms4 (fun a =>
        lall ([1, 2, 3] : List Nat) (fun m => eqL (msortIns m a) (msortChain m a)))
      = true := by decide

theorem nc_two_implementations_agree_with_ties :
    lall ties5 (fun a => eqL (msortIns mW a) (msortChain mW a)) = true := by decide

theorem nc_repaired_holds_on_perms5_gap1 :
    lall perms5 (fun a => repairedAt 1 a) = true := by decide

theorem nc_repaired_holds_on_perms5_gap2 :
    lall perms5 (fun a => repairedAt 2 a) = true := by decide

theorem nc_repaired_holds_on_perms5_gap3 :
    lall perms5 (fun a => repairedAt 3 a) = true := by decide

theorem nc_repaired_holds_on_perms5_gap4 :
    lall perms5 (fun a => repairedAt 4 a) = true := by decide

theorem nc_repaired_holds_with_ties :
    lall ties5 (fun a => repairedAt mW a) = true := by decide

theorem nc_claim_fails_and_holds_within_one_sweep :
    (lany perms5 (fun a => !(claimAt mW a))
      && lany perms5 (fun a => hypExchangeB mW a && conclB mW a)
      && lany ties5 (fun a => !(claimAt mW a))) = true := by decide

theorem certificate :
    eqL (msortFirstStep mW A) [2, 4, 3, 5, 1] = true
      ∧ hypExchangeB mW A = true
      ∧ hypLessB mW A = true
      ∧ eqL B [1, 4, 2, 5, 3] = true
      ∧ eqL (msortIns mW A) (msortChain mW A) = true
      ∧ conclB mW A = false
      ∧ claimAt mW A = false
      ∧ Nat.beq (nth B 0) (chainMin mW A) = true :=
  ⟨by decide, by decide, by decide, by decide, by decide, by decide, by decide, by decide⟩

def sourceA : List Nat := [3, 5, 2, 6, 1, 7, 4]

theorem source_hypotheses_and_refutation :
    nth sourceA 0 < nth sourceA 6 ∧
    hypExchangeB 2 sourceA = true ∧
    msortIns 2 sourceA = [1, 5, 2, 6, 3, 7, 4] ∧
    conclB 2 sourceA = false := by decide

end QEDCert.SE_cs_81391__q
