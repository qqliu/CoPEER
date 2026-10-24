import Mathlib
/- Review overlay for SE_cs_16821__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/



set_option maxRecDepth 10000

namespace SE_cs_16821

structure Job where
  start    : Nat
  len      : Nat
  deadline : Nat
  profit   : Nat

abbrev Inst := List Job

def lenN {α : Type} : List α → Nat := List.length

def lmap {α β : Type} (f : α → β) : List α → List β := List.map f

def lfilter {α : Type} (p : α → Bool) : List α → List α := List.filter p

def joinL {α : Type} : List (List α) → List α := List.flatten

def allB {α : Type} (p : α → Bool) : List α → Bool := fun xs => xs.all p

def anyB {α : Type} (p : α → Bool) : List α → Bool := fun xs => xs.any p

def sumOf : List Nat → Nat := List.sum

def maxOfList : List Nat → Nat
  | [] => 0
  | a :: r => let m := maxOfList r; if Nat.ble a m then m else a

def minOfList : List Nat → Nat
  | [] => 0
  | [a] => a
  | a :: r => let m := minOfList r; if Nat.ble a m then a else m

def upto : Nat → List Nat := List.range

def posUpto : Nat → List Nat
  | 0 => []
  | k + 1 => posUpto k ++ [k + 1]

def memNat (v : Nat) : List Nat → Bool
  | [] => false
  | x :: r => Nat.beq x v || memNat v r

def remNat (v : Nat) : List Nat → List Nat
  | [] => []
  | x :: r => if Nat.beq x v then remNat v r else x :: remNat v r

def noDupB : List Nat → Bool
  | [] => true
  | a :: r => !memNat a r && noDupB r

def sublists : List Nat → List (List Nat)
  | [] => [[]]
  | a :: r => let s := sublists r; lmap (fun t => a :: t) s ++ s

def inserts (x : Nat) : List Nat → List (List Nat)
  | [] => [[x]]
  | a :: r => (x :: a :: r) :: lmap (fun t => a :: t) (inserts x r)

def permsOf : List Nat → List (List Nat)
  | [] => [[]]
  | a :: r => joinL (lmap (fun p => inserts a p) (permsOf r))

def nullJob : Job := { start := 0, len := 0, deadline := 0, profit := 0 }

def getJob : Inst → Nat → Job
  | [], _ => nullJob
  | j :: _, 0 => j
  | _ :: r, i + 1 => getJob r i

def compatB (a b : Job) : Bool :=
  Nat.ble (a.start + a.len) b.start || Nat.ble (b.start + b.len) a.start

def pairwiseCompat (I : Inst) : List Nat → Bool
  | [] => true
  | i :: r => allB (fun j => compatB (getJob I i) (getJob I j)) r && pairwiseCompat I r

def feasibleB (I : Inst) (s : List Nat) : Bool :=
  allB (fun i => Nat.blt i (lenN I)) s && noDupB s && pairwiseCompat I s

def profitOf (I : Inst) (s : List Nat) : Nat :=
  sumOf (lmap (fun i => (getJob I i).profit) s)

def allSubsets (I : Inst) : List (List Nat) := sublists (upto (lenN I))

def feasSubsets (I : Inst) : List (List Nat) := lfilter (fun s => feasibleB I s) (allSubsets I)

def optValue (I : Inst) : Nat := maxOfList (lmap (fun s => profitOf I s) (feasSubsets I))

def scanTake (I : Inst) : List Nat → List Nat → List Nat
  | [], ch => ch
  | i :: r, ch => if feasibleB I (i :: ch) then scanTake I r (i :: ch) else scanTake I r ch

def nonIncrProfit (I : Inst) : List Nat → Bool
  | [] => true
  | [_] => true
  | a :: b :: r =>
      Nat.ble (getJob I b).profit (getJob I a).profit && nonIncrProfit I (b :: r)

def greedyOrders (I : Inst) : List (List Nat) :=
  lfilter (fun p => nonIncrProfit I p) (permsOf (upto (lenN I)))

def greedyBest (I : Inst) : Nat :=
  maxOfList (lmap (fun p => profitOf I (scanTake I p [])) (greedyOrders I))

def scanBestAnyOrder (I : Inst) : Nat :=
  maxOfList (lmap (fun p => profitOf I (scanTake I p [])) (permsOf (upto (lenN I))))

def maxLen (I : Inst) : Nat := maxOfList (lmap (fun j => j.len) I)
def minLen (I : Inst) : Nat := minOfList (lmap (fun j => j.len) I)

def kFrom (I : Inst) : Nat → Nat → Nat
  | 0, k => k
  | f + 1, k => if Nat.ble (maxLen I) (k * minLen I) then k else kFrom I f (k + 1)

def kOf (I : Inst) : Nat := kFrom I (maxLen I + 1) 1

def wfB (I : Inst) : Bool :=
  Nat.blt 0 (lenN I)
    && allB (fun j => Nat.blt 0 j.len && Nat.beq j.deadline (j.start + j.len)) I

def claimKBoundB (I : Inst) : Bool := Nat.ble (optValue I) (kOf I * greedyBest I)

def refutesKBound (I : Inst) : Bool := wfB I && !(claimKBoundB I)

def epsGridAllViolated (k g o Q : Nat) : Bool :=
  allB (fun q =>
    allB (fun p =>
      !(Nat.blt p (k * q)) || Nat.blt (g * (k * q - p)) (o * q)) (posUpto Q)) (posUpto Q)

def hereditaryB (I : Inst) : Bool :=
  allB (fun A => allB (fun x => feasibleB I (remNat x A)) A) (feasSubsets I)

def augmentAxiomB (I : Inst) : Bool :=
  allB (fun A =>
    allB (fun B =>
      !(Nat.blt (lenN A) (lenN B))
        || anyB (fun x => !memNat x A && feasibleB I (x :: A)) B) (feasSubsets I))
    (feasSubsets I)

def W1 : Inst :=
  [ { start := 0, len := 2, deadline := 2, profit := 2 },
    { start := 1, len := 2, deadline := 3, profit := 3 },
    { start := 2, len := 2, deadline := 4, profit := 2 } ]

def W2 : Inst :=
  [ { start := 0, len := 2, deadline := 2, profit := 10 },
    { start := 1, len := 2, deadline := 3, profit := 11 },
    { start := 2, len := 2, deadline := 4, profit := 10 } ]

def Wasker : Inst :=
  [ { start := 0, len := 2, deadline := 2, profit := 3 },
    { start := 0, len := 1, deadline := 1, profit := 2 },
    { start := 1, len := 1, deadline := 2, profit := 2 } ]

def Cfree : Inst :=
  [ { start := 0, len := 2, deadline := 2, profit := 2 },
    { start := 2, len := 2, deadline := 4, profit := 3 },
    { start := 4, len := 2, deadline := 6, profit := 2 } ]

theorem W1_wf : wfB W1 = true := by decide

theorem W1_maxlen_minlen : (Nat.beq (maxLen W1) 2 && Nat.beq (minLen W1) 2) = true := by decide

theorem W1_k_is_one : kOf W1 = 1 := by decide

theorem W1_middle_blocks :
    (feasibleB W1 [0, 1] || feasibleB W1 [1, 2]) = false := by decide

theorem W1_outer_pair_feasible : feasibleB W1 [0, 2] = true := by decide

theorem W1_opt : optValue W1 = 4 := by decide

theorem W1_opt_attained :
    (feasibleB W1 [0, 2] && Nat.beq (profitOf W1 [0, 2]) 4) = true := by decide

theorem W1_greedy : greedyBest W1 = 3 := by decide

theorem W1_greedy_orders_are_two : lenN (greedyOrders W1) = 2 := by decide

theorem W1_every_greedy_order_yields_3 :
    allB (fun p => Nat.beq (profitOf W1 (scanTake W1 p [])) 3) (greedyOrders W1) = true := by
  decide

theorem W1_claim_fails : claimKBoundB W1 = false := by decide

theorem refuted_W1 : refutesKBound W1 = true := by decide

theorem refuted_W1_arithmetic :
    Nat.blt (kOf W1 * greedyBest W1) (optValue W1) = true := by decide

theorem refuted_W1_eps_grid :
    epsGridAllViolated (kOf W1) (greedyBest W1) (optValue W1) 12 = true := by decide

theorem refuted_W1_eps_grid_literal : epsGridAllViolated 1 3 4 40 = true := by decide

theorem W1_is_independence_system : hereditaryB W1 = true := by decide

theorem W1_not_a_matroid : augmentAxiomB W1 = false := by decide

theorem W1_exchange_failure_explicit :
    (feasibleB W1 [1] && feasibleB W1 [0, 2]
      && Nat.blt (lenN ([1] : List Nat)) (lenN ([0, 2] : List Nat))
      && !(feasibleB W1 [0, 1]) && !(feasibleB W1 [2, 1])) = true := by decide

theorem W2_greedy_opt : (Nat.beq (greedyBest W2) 11 && Nat.beq (optValue W2) 20) = true := by
  decide

theorem refuted_W2 : refutesKBound W2 = true := by decide

theorem W2_half_bound_holds : Nat.ble (optValue W2) (2 * greedyBest W2) = true := by decide

theorem nc1_feasibility_discriminates :
    (!(feasibleB W1 [0, 1]) && feasibleB W1 [0, 2]
      && !(feasibleB W1 [0, 0]) && !(feasibleB W1 [3])
      && feasibleB W1 []) = true := by decide

theorem nc2_scan_can_reach_opt :
    (Nat.beq (profitOf W1 (scanTake W1 [0, 2, 1] [])) 4
      && Nat.beq (scanBestAnyOrder W1) (optValue W1)) = true := by decide

theorem nc3_greedy_orders_are_a_proper_restriction :
    (Nat.beq (lenN (greedyOrders W1)) 2
      && Nat.beq (lenN (permsOf (upto (lenN W1)))) 6
      && !(nonIncrProfit W1 [0, 2, 1])
      && nonIncrProfit W1 [1, 0, 2]) = true := by decide

theorem nc4_control_greedy_optimal :
    (Nat.beq (greedyBest Cfree) (optValue Cfree)
      && claimKBoundB Cfree
      && !(refutesKBound Cfree)) = true := by decide

theorem nc5_augmentation_holds_on_control : augmentAxiomB Cfree = true := by decide

theorem nc6_kOf_has_teeth : kOf Wasker = 2 := by decide

theorem nc7_askers_own_example_does_not_refute :
    (Nat.beq (kOf Wasker) 2
      && Nat.beq (greedyBest Wasker) 3
      && Nat.beq (optValue Wasker) 4
      && claimKBoundB Wasker
      && !(refutesKBound Wasker)) = true := by decide

theorem nc8_wf_has_teeth :
    (!(wfB [{ start := 0, len := 2, deadline := 5, profit := 1 }])
      && !(wfB [{ start := 0, len := 0, deadline := 0, profit := 1 }])
      && !(wfB [])) = true := by decide

theorem nc9_eps_grid_discriminates :
    (epsGridAllViolated 1 3 4 40 && !(epsGridAllViolated 2 3 4 40)) = true := by decide

theorem nc9b_asker_instance_survives_eps_grid :
    epsGridAllViolated (kOf Wasker) (greedyBest Wasker) (optValue Wasker) 12 = false := by decide

theorem nc10_opt_is_a_maximum :
    (allB (fun s => Nat.ble (profitOf W1 s) (optValue W1)) (feasSubsets W1)
      && anyB (fun s => Nat.beq (profitOf W1 s) (optValue W1)) (feasSubsets W1)) = true := by
  decide


theorem exact_epsilon_counterexample : wfB W1 = true ∧
    kOf W1 = 1 ∧ greedyBest W1 = 3 ∧
    feasibleB W1 [0,2] = true ∧ profitOf W1 [0,2] = 4 ∧
    (0 : ℚ) < 1/2 ∧ (1/2 : ℚ) < 1 ∧
    ¬ (greedyBest W1 : ℚ) ≥ (profitOf W1 [0,2] : ℚ)/(kOf W1 - 1/2) := by
 have hp : profitOf W1 [0,2] = 4 := by decide
 norm_num [W1_wf, W1_k_is_one, W1_greedy, W1_outer_pair_feasible, hp]

end SE_cs_16821
