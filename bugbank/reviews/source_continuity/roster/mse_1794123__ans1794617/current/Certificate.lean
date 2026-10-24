import Mathlib.Data.Rat.Defs
import Mathlib.Algebra.BigOperators.Group.List.Basic
import Mathlib.Data.List.Sections
import Mathlib.Tactic.NormNum

/-! The source assumes equally many men and women. The old witness did not
satisfy that condition. This replacement uses two fixed family types:
(n,p,w)=(2,3/4,5/7) and (5,1/4,2/7). Each sex vector receives its independent
Bernoulli product weight, so family size never depends on realized sexes.
Expected male and female population sizes both equal 10/7. Brothers are counted
by summing over distinct child positions; all expectations use Mathlib ℚ and
standard List sums rather than a separate rational/list arithmetic implementation. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
namespace MSE1794123

def sexWeight (p : ℚ) (s : Bool) : ℚ := if s then p else 1-p

def sexVectors (n : ℕ) : List (List Bool) := (List.replicate n [false,true]).sections

def mass (p : ℚ) (s : List Bool) : ℚ :=
  (s.map (sexWeight p)).prod

def brothers (s : List Bool) (i : ℕ) : ℕ :=
  ((s.eraseIdx i).filter id).length

def count (sex : Bool) (s : List Bool) : ℕ :=
  (s.filter (fun b => b == sex)).length

def directBrotherTotal (sex : Bool) (s : List Bool) : ℕ :=
  ((List.range s.length).map (fun i =>
    if s[i]?.getD false = sex then brothers s i else 0)).sum

def brotherTotal (sex : Bool) (s : List Bool) : ℕ :=
  if sex then count true s * (count true s - 1) else count false s * count true s

/-- Match the closed count to the person-by-person definition on every outcome. -/
theorem direct_counts_match :
    (sexVectors 2 ++ sexVectors 5).all (fun s =>
      [false,true].all (fun sex => directBrotherTotal sex s == brotherTotal sex s)) = true := by decide

def expectation (n : ℕ) (p : ℚ) (f : List Bool → ℕ) : ℚ :=
  ((sexVectors n).map (fun s => mass p s * f s)).sum

def populationCount (sex : Bool) : ℚ :=
  (5/7 : ℚ) * expectation 2 (3/4) (count sex) +
  (2/7 : ℚ) * expectation 5 (1/4) (count sex)

def populationBrothers (sex : Bool) : ℚ :=
  (5/7 : ℚ) * expectation 2 (3/4) (brotherTotal sex) +
  (2/7 : ℚ) * expectation 5 (1/4) (brotherTotal sex)

def averageBrothers (sex : Bool) : ℚ := populationBrothers sex / populationCount sex

theorem weights_valid :
    (0 : ℚ) < 5/7 ∧ (0 : ℚ) < 2/7 ∧ (5/7 + 2/7 : ℚ) = 1 ∧
    (0 : ℚ) < 3/4 ∧ (3/4 : ℚ) < 1 ∧ (0 : ℚ) < 1/4 ∧
    (1/4 : ℚ) < 1 ∧ (3/4 : ℚ) ≠ 1/4 := by norm_num

theorem vectors_two : sexVectors 2 = [[false,false],
    [true,false],
    [false,true],
    [true,true]] := by decide

theorem vectors_five : sexVectors 5 = [[false,false,false,false,false],
    [true,false,false,false,false],
    [false,true,false,false,false],
    [true,true,false,false,false],
    [false,false,true,false,false],
    [true,false,true,false,false],
    [false,true,true,false,false],
    [true,true,true,false,false],
    [false,false,false,true,false],
    [true,false,false,true,false],
    [false,true,false,true,false],
    [true,true,false,true,false],
    [false,false,true,true,false],
    [true,false,true,true,false],
    [false,true,true,true,false],
    [true,true,true,true,false],
    [false,false,false,false,true],
    [true,false,false,false,true],
    [false,true,false,false,true],
    [true,true,false,false,true],
    [false,false,true,false,true],
    [true,false,true,false,true],
    [false,true,true,false,true],
    [true,true,true,false,true],
    [false,false,false,true,true],
    [true,false,false,true,true],
    [false,true,false,true,true],
    [true,true,false,true,true],
    [false,false,true,true,true],
    [true,false,true,true,true],
    [false,true,true,true,true],
    [true,true,true,true,true]] := by decide

theorem probability_masses_one :
    ((sexVectors 2).map (mass (3/4))).sum = 1 ∧
    ((sexVectors 5).map (mass (1/4))).sum = 1 := by
  norm_num [populationCount, populationBrothers, averageBrothers, expectation, mass, sexWeight, vectors_two, vectors_five, count, brotherTotal]

theorem equal_sex_population :
    populationCount true = 10/7 ∧ populationCount false = 10/7 := by
  norm_num [populationCount, populationBrothers, averageBrothers, expectation, mass, sexWeight, vectors_two, vectors_five, count, brotherTotal]

theorem expectations :
    populationBrothers true = 65/56 ∧ populationBrothers false = 75/56 ∧
    averageBrothers true = 13/16 ∧ averageBrothers false = 15/16 := by
  norm_num [populationCount, populationBrothers, averageBrothers, expectation, mass, sexWeight, vectors_two, vectors_five, count, brotherTotal]

/-- Includes source balance, genuine positive denominators, and strict reversal. -/
theorem certificate :
    ((sexVectors 2).map (mass (3/4))).sum = 1 ∧
    ((sexVectors 5).map (mass (1/4))).sum = 1 ∧
    populationCount true = populationCount false ∧
    0 < populationCount true ∧
    averageBrothers true = 13/16 ∧ averageBrothers false = 15/16 ∧
    averageBrothers true < averageBrothers false := by
  norm_num [populationCount, populationBrothers, averageBrothers, expectation, mass, sexWeight, vectors_two, vectors_five, count, brotherTotal]
end MSE1794123
