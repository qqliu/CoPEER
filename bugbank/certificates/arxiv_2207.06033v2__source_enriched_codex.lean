import Mathlib.Algebra.Polynomial.Degree.Operations
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

/-! The source's all-primes bound is missing the premise that reduction is
nonzero. Use Mathlib Polynomial, polynomial reduction, ZMod and root counting.
The integer polynomial 2X has degree one but reduces to zero over ZMod 2. -/
namespace Arxiv220706033v2SourceEnrichedCodex
open Polynomial
noncomputable def F : Polynomial ℤ := C 2 * X
noncomputable def reduced : Polynomial (ZMod 2) := F.map (Int.castRingHom (ZMod 2))
noncomputable def rootCount : ℕ :=
  ((Finset.univ : Finset (ZMod 2)).filter (fun x => reduced.eval x = 0)).card

theorem refutes_all_primes_root_bound :
    Nat.Prime 2 ∧ F.natDegree = 1 ∧ reduced = 0 ∧ rootCount = 2 ∧
    ¬ rootCount ≤ F.natDegree * 2^(1-1) := by
  have hd : F.natDegree = 1 := by norm_num [F]
  have hr : reduced = 0 := by
    simp only [reduced,F,Polynomial.map_mul,Polynomial.map_C,Polynomial.map_X]
    have h2 : (Int.castRingHom (ZMod 2)) 2 = 0 := by decide
    rw [h2,Polynomial.C_0,zero_mul]
  have hc : rootCount = 2 := by simp [rootCount,hr]
  exact ⟨by norm_num,hd,hr,hc,by rw [hd,hc]; norm_num⟩
end Arxiv220706033v2SourceEnrichedCodex
