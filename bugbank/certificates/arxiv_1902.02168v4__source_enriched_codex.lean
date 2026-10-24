import Mathlib.NumberTheory.Divisors
import Mathlib.Tactic
namespace Arxiv190202168v4SourceEnrichedCodex
open Finset
def Zumkeller (n : ℕ) : Prop := ∃ s : Finset ℕ,
  s ⊆ n.divisors ∧ 2*(∑ d ∈ s,d) = ∑ d ∈ n.divisors,d
lemma z222 : Zumkeller 222 := by
  refine ⟨{222,6},?_,?_⟩ <;> decide
lemma z224 : Zumkeller 224 := by
  refine ⟨{224,28},?_,?_⟩ <;> decide
lemma not_z223 : ¬ Zumkeller 223 := by
  rintro ⟨s,hs,hsum⟩
  have hd : Nat.divisors 223 = {1,223} := by decide
  rw [hd] at hs hsum
  have hm : s ∈ ({1,223}:Finset ℕ).powerset := mem_powerset.mpr hs
  have he : ({1,223}:Finset ℕ).powerset = {∅,{1},{223},{1,223}} := by decide
  rw [he] at hm
  simp only [mem_insert,mem_singleton] at hm
  rcases hm with h|h|h|h <;> subst s <;> norm_num at hsum
theorem refutes_stated_zumkeller_gap :
    Zumkeller 222 ∧ Zumkeller 224 ∧
    (∀ n : ℕ, 222 < n → n < 224 → ¬ Zumkeller n) ∧
    (224:ℤ)-222 = 2 ∧ (224:ℤ)-222 ≠ 12 := by
  refine ⟨z222,z224,?_,by norm_num,by norm_num⟩
  intro n h1 h2
  have : n=223 := by omega
  simpa [this] using not_z223
end Arxiv190202168v4SourceEnrichedCodex
