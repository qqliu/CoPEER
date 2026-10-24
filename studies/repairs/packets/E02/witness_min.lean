import defs_only
/- Record SE_cs_1200__a1206 (E02): the triple fails at the store [2, 3]. -/
namespace SE_cs_1200_a1206_Census

/-- `[2, 3]` satisfies the precondition; every reading of the command yields `[2, 2]`;
the asserted postcondition is false there. -/
theorem at_two_three :
    (pre [2, 3] = true)
  ∧ (resultIs (stepR1 [2, 3]) [2, 2] = true)
  ∧ (resultIs (stepR2 [2, 3]) [2, 2] = true)
  ∧ (resultIs (stepR3 [2, 3]) [2, 2] = true)
  ∧ (post [2, 2] = false) := by decide

theorem hoare_triple_false : ¬ HoareTriple := by
  intro h
  have h1 := h [2, 3] (by decide)
  revert h1
  decide

end SE_cs_1200_a1206_Census

#print axioms SE_cs_1200_a1206_Census.at_two_three
#print axioms SE_cs_1200_a1206_Census.hoare_triple_false
