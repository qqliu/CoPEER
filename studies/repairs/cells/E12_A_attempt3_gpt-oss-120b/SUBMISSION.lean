import defs_only
namespace RedditAskmath1bq1jtcCensus

def factor (q : Int) : Int := 3 * q + 1

def CorrectedClaim : Prop := ∀ q : Int, 6 * q + 2 = 2 * (factor q)

theorem repair_statement : ∀ q : Int, 6 * q + 2 = 2 * (RedditAskmath1bq1jtcCensus.factor q) := by
  intro q
  dsimp [RedditAskmath1bq1jtcCensus.factor]
  calc
    6 * q + 2 = (2 * 3) * q + 2 := by simp
    _ = 2 * (3 * q) + 2 := by simp [Int.mul_comm, Int.mul_left_comm, Int.mul_assoc]
    _ = 2 * (3 * q) + 2 * 1 := by simp
    _ = 2 * (3 * q + 1) := by
      simpa [Int.mul_add] using (Int.mul_add 2 (3 * q) 1).symm

theorem repair_nonvacuous : ∃ q : Int, 6 * q + 2 = 2 * (RedditAskmath1bq1jtcCensus.factor q) ∧ RedditAskmath1bq1jtcCensus.factor q ≠ 3 * q + 2 := by
  refine ⟨0, ?_⟩
  dsimp [RedditAskmath1bq1jtcCensus.factor]
  constructor
  · simp
  · decide

-- CANNOT: proof of final theorem too involved

end RedditAskmath1bq1jtcCensus
