import Mathlib.GroupTheory.Abelianization.Defs
import Mathlib.GroupTheory.Perm.Sign
import Mathlib.Data.Fintype.Perm
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: Unchanged G=S3 now uses Equiv.Perm, Subgroup.center and Abelianization. Its center is trivial while the sign map distinguishes two elements of its abelianization, precluding an isomorphism. This establishes the same witness without rebuilding finite groups.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_bwiq68
abbrev G := Equiv.Perm (Fin 3)
theorem center_trivial : ∀ z : Subgroup.center G, (z : G) = 1 := by
  intro z
  have h := z.property
  rw [Subgroup.mem_center_iff] at h
  have hz : ∀ z : G, (∀ g : G, g*z=z*g) → z=1 := by decide
  exact hz z.val h
theorem certificate : ¬ Nonempty (Abelianization G ≃* Subgroup.center G) := by
  rintro ⟨e⟩
  have he : e (Abelianization.of (Equiv.swap (0 : Fin 3) 1)) = e 1 := by
    apply Subtype.ext
    rw [center_trivial, center_trivial]
  have h := e.injective he
  have hs := congrArg (Abelianization.lift (Equiv.Perm.sign : G →* ℤˣ)) h
  simp at hs
  have hv := congrArg Units.val hs
  norm_num at hv
end Audit_reddit_learnmath_bwiq68
