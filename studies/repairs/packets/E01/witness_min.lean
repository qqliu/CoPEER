import defs_only
/- Record SE_cs_97637__a97647 (E01): the program fails the specification at input 1. -/
namespace SqrtFailureBoundary

theorem prog_one : prog 1 = 0 := by decide

/-- `R 1 (prog 1)` is `0 ≤ 1 ∧ 1 < 1`, which is false. -/
theorem spec_fails_at_one : ¬ R 1 (prog 1) := by decide

theorem program_correct_false : ¬ ProgramCorrect := fun h => spec_fails_at_one (h 1)

end SqrtFailureBoundary

#print axioms SqrtFailureBoundary.spec_fails_at_one
#print axioms SqrtFailureBoundary.program_correct_false
