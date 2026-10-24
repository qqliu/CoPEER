import defs_only
/- Record proofwiki_25056 (E11): the quoted line fails at a = -1, p = X + 1:
cont(-(X+1)) = 1 while (-1) * cont(X+1) = -1. -/
namespace ProofWiki25056Census
open Polynomial

noncomputable def f : ℤ[X] := X + 1

theorem f_content : f.content = 1 :=
  IsPrimitive.content_eq_one (monic_X_add_C (1 : ℤ)).isPrimitive

theorem neg_f_content : (C (-1 : ℤ) * f).content = 1 := by
  have hf := (monic_X_add_C (1 : ℤ)).isPrimitive
  have hp : (C (-1 : ℤ) * f).IsPrimitive := by
    intro r hr
    apply hf r
    have e : C (-1 : ℤ) * f = -f := by rw [C_neg, C_1, neg_one_mul]
    rw [e, dvd_neg] at hr
    simpa [f] using hr
  simpa using hp.content_eq_one

theorem local_claim_fails_at_neg_one : (C (-1 : ℤ) * f).content ≠ (-1 : ℤ) * f.content := by
  rw [neg_f_content, f_content]
  norm_num

theorem local_claim_false : ¬ LocalClaim := fun h => local_claim_fails_at_neg_one (h (-1) f)

end ProofWiki25056Census

#print axioms ProofWiki25056Census.local_claim_fails_at_neg_one
#print axioms ProofWiki25056Census.local_claim_false
