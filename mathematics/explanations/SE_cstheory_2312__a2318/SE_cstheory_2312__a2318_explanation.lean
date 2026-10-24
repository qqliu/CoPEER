/- Explanation census, record SE_cstheory_2312__a2318 (cstheory.stackexchange answer 2318 to question 2312).
Model-written formalisation of the dossier's documented FAMILY and REPAIR; no human review.
Core Lean only (no imports, no Mathlib). The released certificate
validation/human_review_20260915/lean/SE_cstheory_2312__a2318.lean (sha256 68a3f761...92aa42d) is NOT modified.

Section 1 restates the released definitions verbatim (WEdge, wsum, penaltiesBelow, gstar, norm, applyEdge,
build, tsum, G3, T3, d3, f3, a3, Gstar3); only the namespace name differs.
NEW definitions, not in the release: cnt (number of penalised vertices below k), cutVal (value of a cut),
GS / GstarS and GS2 / GstarS2 (slack instances), Gstar3small (the dossier's "smallest witness").

Notation of the source: T = wsum G, f = a - (n-2) d; written inline as `a - ((n : Int) - 2) * d`.
-/

set_option maxRecDepth 10000

namespace SE_cstheory_2312_a2318_Census

/-! ## 1. Released definitions, verbatim -/

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

/-! ## 2. Summation lemmas and the penalty count (NEW) -/

theorem wsum_nil : wsum [] = 0 := rfl

theorem wsum_cons (e : WEdge) (es : List WEdge) : wsum (e :: es) = e.2.2 + wsum es := by
  simp [wsum]

theorem wsum_append (xs ys : List WEdge) : wsum (xs ++ ys) = wsum xs + wsum ys := by
  induction xs with
  | nil => simp [wsum]
  | cons e es ih => rw [List.cons_append, wsum_cons, wsum_cons, ih]; omega

def cnt (u v : Nat) : Nat → Nat
  | 0 => 0
  | k + 1 => (if k = u ∨ k = v then 0 else 1) + cnt u v k

theorem wsum_penaltiesBelow (u v : Nat) (d : Int) :
    ∀ k, wsum (penaltiesBelow u v d k) = -(2 * ((cnt u v k : Int) * d))
  | 0 => by simp [penaltiesBelow, cnt, wsum]
  | k + 1 => by
      have ih := wsum_penaltiesBelow u v d k
      by_cases h : k = u ∨ k = v
      · simp only [penaltiesBelow, cnt, h, ↓reduceIte, List.nil_append, Nat.zero_add]; exact ih
      · simp only [penaltiesBelow, cnt, h, ↓reduceIte, wsum_append, wsum_cons, wsum_nil, ih]
        rw [Int.natCast_add, Int.add_mul]
        simp only [Int.natCast_one, Int.one_mul]
        omega

theorem cnt_eq (u v : Nat) (huv : u ≠ v) :
    ∀ k, cnt u v k + min 1 (k - u) + min 1 (k - v) = k
  | 0 => by simp [cnt]
  | k + 1 => by
      have ih := cnt_eq u v huv k
      by_cases h : k = u ∨ k = v
      · simp only [cnt, h, ↓reduceIte]; omega
      · simp only [cnt, h, ↓reduceIte]; omega

theorem cnt_two (n u v : Nat) (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    (cnt u v n : Int) = (n : Int) - 2 := by
  have := cnt_eq u v huv n
  omega

/-- REPAIR (universal): dossier "Correcting the arithmetic identity to T+a-2(n-2)d repairs this local equality". -/
theorem repair (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    wsum (gstar n u v d a G) = wsum G + a - 2 * ((n : Int) - 2) * d := by
  unfold gstar
  rw [wsum_append, wsum_append, wsum_penaltiesBelow, cnt_two n u v huv hu hv, wsum_cons, wsum_nil,
    Int.mul_assoc]
  show wsum G + -(2 * (((n : Int) - 2) * d)) + (a + 0) = wsum G + a - 2 * (((n : Int) - 2) * d)
  omega

/-! ## 2b. The construction adds exactly 2(n-2) edges, each of weight -d (dossier: "for each of n-2
nondesignated vertices it adds two edges of weight -d") -/

theorem length_penaltiesBelow (u v : Nat) (d : Int) :
    ∀ k, (penaltiesBelow u v d k).length = 2 * cnt u v k
  | 0 => by simp [penaltiesBelow, cnt]
  | k + 1 => by
      have ih := length_penaltiesBelow u v d k
      by_cases h : k = u ∨ k = v
      · simp only [penaltiesBelow, cnt, h, ↓reduceIte, List.nil_append, Nat.zero_add]; exact ih
      · simp only [penaltiesBelow, cnt, h, ↓reduceIte, List.length_append, List.length_cons,
          List.length_nil, ih]
        omega

theorem penalty_count (n u v : Nat) (d : Int) (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    (penaltiesBelow u v d n).length = 2 * (n - 2) := by
  have h1 := length_penaltiesBelow u v d n
  have h2 := cnt_eq u v huv n
  omega

theorem penalty_weights (u v : Nat) (d : Int) :
    ∀ k, ∀ e ∈ penaltiesBelow u v d k, e.2.2 = -d
  | 0 => by simp [penaltiesBelow]
  | k + 1 => by
      have ih := penalty_weights u v d k
      intro e he
      by_cases h : k = u ∨ k = v
      · simp only [penaltiesBelow, h, ↓reduceIte, List.nil_append] at he; exact ih e he
      · simp only [penaltiesBelow, h, ↓reduceIte, List.mem_append, List.mem_cons] at he
        rcases he with (he | he | he) | he
        · rw [he]
        · rw [he]
        · cases he
        · exact ih e he


/-- REPAIR in the source's notation f = a - (n-2)d: the new total is T + f - (n-2)d (dossier: "the actual new total T+f-(n-2)d, not T+f"). -/
theorem repair_f_form (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    wsum (gstar n u v d a G) = wsum G + (a - ((n : Int) - 2) * d) - ((n : Int) - 2) * d := by
  have h := repair n u v d a G huv hu hv
  rw [Int.mul_assoc] at h
  omega

/-- Dossier: "For every n>=3 the discrepancy is (n-2)d". Holds for every n (u ≠ v < n forces n ≥ 2). -/
theorem discrepancy (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    (wsum G + (a - ((n : Int) - 2) * d)) - wsum (gstar n u v d a G) = ((n : Int) - 2) * d := by
  have h := repair_f_form n u v d a G huv hu hv
  omega

/-- EXACT (accounting): the source's identity "new total = T + f" holds iff n = 2 or d = 0. -/
theorem exact_accounting (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    wsum (gstar n u v d a G) = wsum G + (a - ((n : Int) - 2) * d) ↔ (n = 2 ∨ d = 0) := by
  have h := repair_f_form n u v d a G huv hu hv
  have hz : ((n : Int) - 2) * d = 0 ↔ ((n : Int) - 2 = 0 ∨ d = 0) := Int.mul_eq_zero
  constructor
  · intro hc
    have : ((n : Int) - 2) * d = 0 := by omega
    rcases hz.mp this with h1 | h1
    · left; omega
    · right; exact h1
  · intro hc
    have : ((n : Int) - 2) * d = 0 := by
      apply hz.mpr
      rcases hc with h1 | h1
      · left; omega
      · right; exact h1
    omega

/-- FAMILY (universal): for every n ≥ 3, every d ≠ 0, every G, a and distinct u, v < n the source's identity fails. -/
theorem family (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) (hn : 3 ≤ n) (hd : d ≠ 0) :
    wsum (gstar n u v d a G) ≠ wsum G + (a - ((n : Int) - 2) * d) := by
  intro hc
  rcases (exact_accounting n u v d a G huv hu hv).mp hc with h1 | h1
  · omega
  · exact hd h1

theorem pos_mul (n : Nat) (d : Int) (hn : 3 ≤ n) (hd : 0 < d) : d ≤ ((n : Int) - 2) * d := by
  have h1 : (1 : Int) ≤ (n : Int) - 2 := by omega
  have h2 : 1 * d ≤ ((n : Int) - 2) * d := Int.mul_le_mul_of_nonneg_right h1 (Int.le_of_lt hd)
  omega

/-- FAMILY, source setting d > 0: the source's booked total strictly overstates the true total. -/
theorem family_overstates (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) (hn : 3 ≤ n) (hd : 0 < d) :
    wsum (gstar n u v d a G) < wsum G + (a - ((n : Int) - 2) * d) := by
  have h := repair_f_form n u v d a G huv hu hv
  have hp := pos_mul n d hn hd
  omega

/-- EXACT (sign), multiplication form of the dossier's "when d>(T+f)/(n-2), the new total is negative". -/
theorem exact_negative (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    wsum (gstar n u v d a G) < 0 ↔ wsum G + (a - ((n : Int) - 2) * d) < ((n : Int) - 2) * d := by
  have h := repair_f_form n u v d a G huv hu hv
  omega

/-- EXACT (sign), the dossier's division form; `/` is Int floor division, equivalent to the rational comparison for a positive divisor. -/
theorem exact_negative_div (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) (hn : 3 ≤ n) :
    wsum (gstar n u v d a G) < 0 ↔ (wsum G + (a - ((n : Int) - 2) * d)) / ((n : Int) - 2) < d := by
  have hpos : (0 : Int) < (n : Int) - 2 := by omega
  rw [exact_negative n u v d a G huv hu hv, Int.ediv_lt_iff_lt_mul hpos, Int.mul_comm d]

/-- EXACT (positivity premise): strict positivity of the new total fails iff T + f ≤ (n-2)d. -/
theorem exact_positivity (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    ¬ (0 < wsum (gstar n u v d a G)) ↔ wsum G + (a - ((n : Int) - 2) * d) ≤ ((n : Int) - 2) * d := by
  have h := repair_f_form n u v d a G huv hu hv
  omega

/-- FAMILY (positivity), source setting: T > 0, f ≤ -0.49T, n ≥ 3 and d ≥ T force a NEGATIVE total, for every G. -/
theorem family_negative_large_d (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) (hn : 3 ≤ n)
    (hT : 0 < wsum G)
    (hwin : 100 * (a - ((n : Int) - 2) * d) ≤ (-49 : Int) * wsum G)
    (hd : wsum G ≤ d) :
    wsum (gstar n u v d a G) < 0 := by
  have h := repair_f_form n u v d a G huv hu hv
  have hp := pos_mul n d hn (by omega)
  omega

/-- The released selected declaration `refutation`, restated verbatim over the restated definitions. -/
theorem claim_refuted_witness :
    (0 < T3 ∧ (-99 : Int) * T3 ≤ 100 * f3 ∧ 100 * f3 ≤ (-49 : Int) * T3)
    ∧ wsum Gstar3 ≠ T3 + f3
    ∧ ¬ (0 < wsum Gstar3)
    ∧ tsum (build true Gstar3 []) ≠ T3 + f3
    ∧ ¬ (0 < tsum (build true Gstar3 []))
    ∧ tsum (build false Gstar3 []) ≠ T3 + f3
    ∧ ¬ (0 < tsum (build false Gstar3 [])) := by decide

/-- CLAIM REFUTED: the source's local claim (identity and positivity under its own hypotheses) is not universally valid. -/
theorem claim_refuted :
    ¬ (∀ (n u v : Nat) (d a : Int) (G : List WEdge),
        u ≠ v → u < n → v < n → 0 < wsum G →
        (-99 : Int) * wsum G ≤ 100 * (a - ((n : Int) - 2) * d) →
        100 * (a - ((n : Int) - 2) * d) ≤ (-49 : Int) * wsum G →
        wsum (gstar n u v d a G) = wsum G + (a - ((n : Int) - 2) * d)
          ∧ 0 < wsum (gstar n u v d a G)) := by
  intro h
  have h3 := h 3 0 1 20 19 [(0, 1, 1), (1, 2, 1)] (by decide) (by decide) (by decide)
    (by decide) (by decide) (by decide)
  exact absurd h3.2 (by decide)

/-- Non-vacuity and unboundedness: for every n ≥ 3 there is an instance meeting ALL the source's hypotheses where both the identity and positivity fail. -/
theorem family_unbounded (n : Nat) (hn : 3 ≤ n) :
    ∃ (u v : Nat) (d a : Int) (G : List WEdge),
      u ≠ v ∧ u < n ∧ v < n ∧ 0 < wsum G
      ∧ (-99 : Int) * wsum G ≤ 100 * (a - ((n : Int) - 2) * d)
      ∧ 100 * (a - ((n : Int) - 2) * d) ≤ (-49 : Int) * wsum G
      ∧ wsum (gstar n u v d a G) ≠ wsum G + (a - ((n : Int) - 2) * d)
      ∧ wsum (gstar n u v d a G) < 0 := by
  have hT : wsum [((0 : Nat), (1 : Nat), (2 : Int))] = 2 := by decide
  have hf : (-1 + ((n : Int) - 2) * 20) - ((n : Int) - 2) * 20 = -1 := by omega
  refine ⟨0, 1, 20, -1 + ((n : Int) - 2) * 20, [(0, 1, 2)], by decide, by omega, by omega, ?_, ?_, ?_, ?_, ?_⟩
  · rw [hT]; decide
  · rw [hT, hf]; decide
  · rw [hT, hf]; decide
  · exact family n 0 1 20 _ _ (by decide) (by omega) (by omega) hn (by decide)
  · apply family_negative_large_d n 0 1 20 _ _ (by decide) (by omega) (by omega) hn
    · rw [hT]; decide
    · rw [hT, hf]; decide
    · rw [hT]; decide

theorem tsum_cons (p : (Nat × Nat) × Int) (m : List ((Nat × Nat) × Int)) :
    tsum (p :: m) = p.2 + tsum m := by
  simp [tsum]

theorem tsum_applyEdge_add (i j : Nat) (w : Int) :
    ∀ m, tsum (applyEdge true m (i, j, w)) = tsum m + w
  | [] => by simp [applyEdge, tsum]
  | (p, x) :: rest => by
      have ih := tsum_applyEdge_add i j w rest
      simp only [applyEdge]
      by_cases h : p = norm i j
      · simp only [h, ↓reduceIte, tsum_cons]; omega
      · simp only [h, ↓reduceIte, tsum_cons, ih]; omega

/-- Merging parallel edges additively preserves the total, for every edge list. -/
theorem tsum_build_add : ∀ (es : List WEdge) (m : List ((Nat × Nat) × Int)),
    tsum (build true es m) = tsum m + wsum es
  | [], m => by simp [build, wsum]
  | (i, j, w) :: es, m => by
      rw [build, tsum_build_add es, tsum_applyEdge_add, wsum_cons]
      show tsum m + w + wsum es = tsum m + (w + wsum es)
      omega

/-- REPAIR survives the restriction to simple weighted graphs under the ADD-merge reading. -/
theorem repair_simple_add (n u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < n) (hv : v < n) :
    tsum (build true (gstar n u v d a G) []) = wsum G + a - 2 * ((n : Int) - 2) * d := by
  rw [tsum_build_add, repair n u v d a G huv hu hv]
  show (0 : Int) + _ = _
  omega

/-- LIMIT of the repair: under the OVERWRITE reading (which the released theorem also covers) the corrected identity is false on the released witness: -21 ≠ -19. -/
theorem repair_fails_overwrite :
    tsum (build false Gstar3 []) ≠ T3 + a3 - 2 * ((3 : Int) - 2) * d3
    ∧ tsum (build false Gstar3 []) = -21
    ∧ T3 + a3 - 2 * ((3 : Int) - 2) * d3 = -19 := by decide

/-- LIMIT of the repair: the hypothesis u ≠ v is needed (u = v gives 2(n-1) penalty edges). -/
theorem repair_needs_distinct :
    wsum (gstar 3 0 0 20 19 G3) ≠ wsum G3 + 19 - 2 * ((3 : Int) - 2) * 20
    ∧ wsum (gstar 3 0 0 20 19 G3) = -59 := by decide

/-- Negative control, universal: for n = 2 the source's identity holds for every G, d, a. -/
theorem negative_control_n2 (u v : Nat) (d a : Int) (G : List WEdge)
    (huv : u ≠ v) (hu : u < 2) (hv : v < 2) :
    wsum (gstar 2 u v d a G) = wsum G + (a - (((2 : Nat) : Int) - 2) * d) :=
  (exact_accounting 2 u v d a G huv hu hv).mpr (Or.inl rfl)

/-- NEW definition (not in the release): value of the cut given by a side function. -/
def cutVal (side : Nat → Bool) (es : List WEdge) : Int :=
  (es.map (fun e => if side e.1 != side e.2.1 then e.2.2 else 0)).sum

def GS : List WEdge := [(0, 1, 34), (1, 2, 33), (0, 2, 33)]
def GstarS : List WEdge := gstar 3 0 1 50 1 GS

/-- SLACK between the two halves of the claim: an instance with nonnegative weights, T = 100 > 0, f = -49 in the window, a = 1 > 0,
d = 50 larger than every original weight and large enough in the source's own sense (every nontrivial cut keeping u, v together is
negative in G*), where the identity FAILS (true total 1, booked 51) but positivity HOLDS. So an accounting failure does not imply a
violated positive-sum precondition, and the flaw field's "negative for the required large d" is not universal. -/
theorem slack_positivity_survives :
    (0 < wsum GS ∧ (-99 : Int) * wsum GS ≤ 100 * (1 - ((3 : Int) - 2) * 50)
        ∧ 100 * (1 - ((3 : Int) - 2) * 50) ≤ (-49 : Int) * wsum GS)
    ∧ (∀ x ∈ GS, 0 ≤ x.2.2 ∧ x.2.2 < 50)
    ∧ (0 : Int) < 1
    ∧ wsum GstarS ≠ wsum GS + (1 - ((3 : Int) - 2) * 50)
    ∧ wsum GS + (1 - ((3 : Int) - 2) * 50) = 51
    ∧ wsum GstarS = 1
    ∧ 0 < wsum GstarS
    ∧ (∀ mask, mask < 8 → mask ≠ 0 → mask ≠ 7 →
        (Nat.testBit mask 0 = Nat.testBit mask 1) → cutVal (Nat.testBit mask) GstarS < 0) := by
  decide

/-- SLACK at the source's INTENDED f: G = star-like path with weights 999 and 1 (T = 1000, all weights ≥ 0), u = 0, v = 1.
The maximum cut of G is 1000 and separates u and v (all 8 side functions checked), f = -980 = -0.98·OPT lies in the window,
d = 1 already makes every nontrivial cut keeping u, v together negative in G*, a = f + (n-2)d = -979 (NOT positive, and d is
not "large": both are reported, not hidden). The identity FAILS (true total 19, booked 20) but positivity HOLDS, and the best
cut of G* is 20 = OPT + f as the source computes. -/
def GS2 : List WEdge := [(0, 1, 999), (0, 2, 1)]
def GstarS2 : List WEdge := gstar 3 0 1 1 (-979) GS2

theorem slack_at_intended_f :
    (0 < wsum GS2 ∧ (-99 : Int) * wsum GS2 ≤ 100 * (-979 - ((3 : Int) - 2) * 1)
        ∧ 100 * (-979 - ((3 : Int) - 2) * 1) ≤ (-49 : Int) * wsum GS2)
    ∧ (∀ x ∈ GS2, 0 ≤ x.2.2)
    ∧ (∀ mask, mask < 8 → cutVal (Nat.testBit mask) GS2 ≤ 1000)
    ∧ cutVal (Nat.testBit 1) GS2 = 1000
    ∧ 100 * (-979 - ((3 : Int) - 2) * 1) = -98 * 1000
    ∧ wsum GstarS2 ≠ wsum GS2 + (-979 - ((3 : Int) - 2) * 1)
    ∧ wsum GstarS2 = 19
    ∧ 0 < wsum GstarS2
    ∧ (∀ mask, mask < 8 → mask ≠ 0 → mask ≠ 7 →
        (Nat.testBit mask 0 = Nat.testBit mask 1) → cutVal (Nat.testBit mask) GstarS2 < 0)
    ∧ (∀ mask, mask < 8 → cutVal (Nat.testBit mask) GstarS2 ≤ 20)
    ∧ cutVal (Nat.testBit 1) GstarS2 = 20 := by
  decide

/-- The dossier's "smallest witness of all": n = 3, T = 2, d = 1, f = -1, a = 0. The total is 0: NOT negative,
and the dossier's condition d > (T+f)/(n-2) is NOT met (1 > 1 is false), yet strict positivity fails.
So "negative" (exact_negative) and "positivity fails" (exact_positivity) differ exactly on the boundary. -/
def Gstar3small : List WEdge := gstar 3 0 1 1 0 G3

theorem boundary_witness :
    Gstar3small = [(0, 1, 1), (1, 2, 1), (0, 2, -1), (1, 2, -1), (0, 1, 0)]
    ∧ wsum Gstar3small = 0
    ∧ ¬ (wsum Gstar3small < 0)
    ∧ ¬ (0 < wsum Gstar3small)
    ∧ wsum Gstar3small ≠ T3 + (0 - ((3 : Int) - 2) * 1)
    ∧ ¬ ((T3 + (0 - ((3 : Int) - 2) * 1)) / ((3 : Int) - 2) < 1) := by decide

end SE_cstheory_2312_a2318_Census

#print axioms SE_cstheory_2312_a2318_Census.claim_refuted
#print axioms SE_cstheory_2312_a2318_Census.claim_refuted_witness
#print axioms SE_cstheory_2312_a2318_Census.repair
#print axioms SE_cstheory_2312_a2318_Census.repair_f_form
#print axioms SE_cstheory_2312_a2318_Census.discrepancy
#print axioms SE_cstheory_2312_a2318_Census.penalty_count
#print axioms SE_cstheory_2312_a2318_Census.penalty_weights
#print axioms SE_cstheory_2312_a2318_Census.family
#print axioms SE_cstheory_2312_a2318_Census.family_overstates
#print axioms SE_cstheory_2312_a2318_Census.family_negative_large_d
#print axioms SE_cstheory_2312_a2318_Census.family_unbounded
#print axioms SE_cstheory_2312_a2318_Census.exact_accounting
#print axioms SE_cstheory_2312_a2318_Census.exact_negative
#print axioms SE_cstheory_2312_a2318_Census.exact_negative_div
#print axioms SE_cstheory_2312_a2318_Census.exact_positivity
#print axioms SE_cstheory_2312_a2318_Census.repair_simple_add
#print axioms SE_cstheory_2312_a2318_Census.tsum_build_add
#print axioms SE_cstheory_2312_a2318_Census.repair_fails_overwrite
#print axioms SE_cstheory_2312_a2318_Census.repair_needs_distinct
#print axioms SE_cstheory_2312_a2318_Census.negative_control_n2
#print axioms SE_cstheory_2312_a2318_Census.slack_positivity_survives
#print axioms SE_cstheory_2312_a2318_Census.slack_at_intended_f
#print axioms SE_cstheory_2312_a2318_Census.boundary_witness
#print axioms SE_cstheory_2312_a2318_Census.wsum_penaltiesBelow
#print axioms SE_cstheory_2312_a2318_Census.cnt_eq
