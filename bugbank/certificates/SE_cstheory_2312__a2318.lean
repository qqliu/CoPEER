/- Review overlay for SE_cstheory_2312__a2318.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

set_option maxRecDepth 10000

namespace SE_cstheory_2312_a2318

abbrev WEdge := Nat × Nat × Int

def wsum (es : List WEdge) : Int := (es.map (fun e => e.2.2)).sum

def penaltiesBelow (u v : Nat) (d : Int) : Nat → List WEdge
  | 0 => []
  | k + 1 =>
      (if k = u ∨ k = v then [] else [(u, k, -d), (v, k, -d)]) ++ penaltiesBelow u v d k

def gstar (n u v : Nat) (d a : Int) (G : List WEdge) : List WEdge :=
  G ++ penaltiesBelow u v d n ++ [(u, v, a)]

def norm (i j : Nat) : Nat × Nat := if i ≤ j then (i, j) else (j, i)

def applyEdge (addMode : Bool) : List ((Nat × Nat) × Int) → WEdge → List ((Nat × Nat) × Int)
  | [], (i, j, w) => [(norm i j, w)]
  | (p, x) :: rest, (i, j, w) =>
      if p = norm i j then (p, if addMode then x + w else w) :: rest
      else (p, x) :: applyEdge addMode rest (i, j, w)

def build (addMode : Bool) : List WEdge → List ((Nat × Nat) × Int) → List ((Nat × Nat) × Int)
  | [], m => m
  | e :: es, m => build addMode es (applyEdge addMode m e)

def tsum (es : List ((Nat × Nat) × Int)) : Int := (es.map (fun e => e.2)).sum

def G3 : List WEdge := [(0, 1, 1), (1, 2, 1)]
def T3 : Int := wsum G3            -- = 2
def d3 : Int := 20
def f3 : Int := -1
def a3 : Int := f3 + 1 * d3        -- a = f + (n-2)d, with n = 3, so (n-2) = 1;  = 19
def Gstar3 : List WEdge := gstar 3 0 1 d3 a3 G3

theorem Gstar3_eq :
    Gstar3 = [(0, 1, 1), (1, 2, 1), (0, 2, -20), (1, 2, -20), (0, 1, 19)] := by decide

theorem hypotheses_hold :
    0 < T3 ∧ (-99 : Int) * T3 ≤ 100 * f3 ∧ 100 * f3 ≤ (-49 : Int) * T3 := by decide

theorem claimed_value : T3 + f3 = 1 ∧ 0 < T3 + f3 := by decide

theorem actual_value : wsum Gstar3 = -19 := by decide

theorem accounting_fails : wsum Gstar3 ≠ T3 + f3 := by decide

theorem positivity_fails : ¬ (0 < wsum Gstar3) := by decide

theorem shortfall_n3 : wsum Gstar3 = (T3 + f3) - 1 * d3 := by decide

theorem simple_add_reading :
    build true Gstar3 [] = [((0, 1), 20), ((1, 2), -19), ((0, 2), -20)]
      ∧ tsum (build true Gstar3 []) = -19
      ∧ ¬ (0 < tsum (build true Gstar3 []))
      ∧ tsum (build true Gstar3 []) ≠ T3 + f3 := by decide

theorem simple_overwrite_reading :
    build false Gstar3 [] = [((0, 1), 19), ((1, 2), -20), ((0, 2), -20)]
      ∧ tsum (build false Gstar3 []) = -21
      ∧ ¬ (0 < tsum (build false Gstar3 []))
      ∧ tsum (build false Gstar3 []) ≠ T3 + f3 := by decide

def G4 : List WEdge := [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
def T4 : Int := wsum G4            -- = 3
def d4 : Int := 20
def f4 : Int := -2
def a4 : Int := f4 + 2 * d4        -- (n-2) = 2;  = 38
def Gstar4 : List WEdge := gstar 4 0 1 d4 a4 G4

theorem hypotheses_hold_n4 :
    0 < T4 ∧ (-99 : Int) * T4 ≤ 100 * f4 ∧ 100 * f4 ≤ (-49 : Int) * T4 := by decide

theorem refutation_n4 :
    T4 + f4 = 1
      ∧ wsum Gstar4 = -39
      ∧ wsum Gstar4 ≠ T4 + f4
      ∧ ¬ (0 < wsum Gstar4) := by decide

theorem shortfall_n4 : wsum Gstar4 = (T4 + f4) - 2 * d4 := by decide

def G2 : List WEdge := [(0, 1, 2)]
def T2 : Int := wsum G2            -- = 2
def f2 : Int := -1
def a2 : Int := f2 + 0 * d3        -- (n-2) = 0, so a = f = -1
def Gstar2 : List WEdge := gstar 2 0 1 d3 a2 G2

theorem negative_control_n2 :
    penaltiesBelow 0 1 d3 2 = []
      ∧ (-99 : Int) * T2 ≤ 100 * f2 ∧ 100 * f2 ≤ (-49 : Int) * T2
      ∧ wsum Gstar2 = T2 + f2          -- the claimed identity HOLDS here
      ∧ 0 < wsum Gstar2 := by decide    -- and the positivity conclusion HOLDS here

theorem penalty_edges_n4 :
    penaltiesBelow 0 1 d4 4 = [(0, 3, -20), (1, 3, -20), (0, 2, -20), (1, 2, -20)]
      ∧ (penaltiesBelow 0 1 d4 4).length = 4 := by decide

theorem refutation :
    -- the answer's own hypotheses hold on the witness
    (0 < T3 ∧ (-99 : Int) * T3 ≤ 100 * f3 ∧ 100 * f3 ≤ (-49 : Int) * T3)
    -- (A) fails
    ∧ wsum Gstar3 ≠ T3 + f3
    -- (B) fails
    ∧ ¬ (0 < wsum Gstar3)
    -- and both still fail after collapsing to a simple graph, under the ADD reading
    ∧ tsum (build true Gstar3 []) ≠ T3 + f3
    ∧ ¬ (0 < tsum (build true Gstar3 []))
    -- ... and under the OVERWRITE reading
    ∧ tsum (build false Gstar3 []) ≠ T3 + f3
    ∧ ¬ (0 < tsum (build false Gstar3 [])) := by decide

end SE_cstheory_2312_a2318
