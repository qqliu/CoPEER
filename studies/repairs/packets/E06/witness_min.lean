import defs_only
/- Record SE_cstheory_2312__a2318 (E06): the located claim fails at
n = 3, u = 0, v = 1, G = path 0-1-2 with unit weights (T = 2), d = 20, f = -1, a = 19. -/
set_option maxRecDepth 10000

namespace SE_cstheory_2312_a2318_Census

def G3 : List WEdge := [(0, 1, 1), (1, 2, 1)]
def T3 : Int := wsum G3            -- = 2
def d3 : Int := 20
def f3 : Int := -1
def a3 : Int := f3 + 1 * d3        -- a = f + (n-2)d, with n = 3, so (n-2) = 1;  = 19
def Gstar3 : List WEdge := gstar 3 0 1 d3 a3 G3

/-- The instance meets every hypothesis of the located claim (T > 0, f in the window). -/
theorem hypotheses_hold :
    0 < T3 ∧ (-99 : Int) * T3 ≤ 100 * f3 ∧ 100 * f3 ≤ (-49 : Int) * T3 := by decide

/-- Values at the instance: booked total `T + f = 1`; actual total `-19` (also `-19` after
additive merging of parallel edges, `-21` after overwrite merging). -/
theorem instance_values :
    T3 + f3 = 1 ∧ wsum Gstar3 = -19
    ∧ tsum (build true Gstar3 []) = -19 ∧ tsum (build false Gstar3 []) = -21 := by decide

theorem local_claim_false : ¬ LocalClaim :=
  fun h => absurd (h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)).2 (by decide)

theorem positivity_under_window_false : ¬ PositivityUnderWindow :=
  fun h => absurd (h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)]
    (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)) (by decide)

end SE_cstheory_2312_a2318_Census

#print axioms SE_cstheory_2312_a2318_Census.instance_values
#print axioms SE_cstheory_2312_a2318_Census.local_claim_false
#print axioms SE_cstheory_2312_a2318_Census.positivity_under_window_false
