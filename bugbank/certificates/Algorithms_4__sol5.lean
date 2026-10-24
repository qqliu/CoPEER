import Mathlib.Data.Fintype.Fin
import Mathlib.Data.Finset.Card
import Mathlib.Tactic.NormNum
set_option autoImplicit false
namespace ProofCerts.Alg4
abbrev Trace := Fin 8 → Fin 16
def draws : Trace := fun _ => 0
/-- Mathlib image removes repeated samples, exactly as simple-neighborhood formation. -/
def neighbors (t : Trace) : Finset (Fin 16) := Finset.univ.image t
def simpleDegreeOf (t : Trace) : ℕ := (neighbors t).card
theorem sampling_with_replacement_degree_claim_refuted :
    8^4 = (16:ℕ)^3 ∧ neighbors draws = {0} ∧ simpleDegreeOf draws = 1 ∧
    ¬ ∀ t : Trace, simpleDegreeOf t = 8 := by
  have hn : neighbors draws = {0} := by decide
  have hd : simpleDegreeOf draws = 1 := by simp [simpleDegreeOf,hn]
  refine ⟨by norm_num,hn,hd,?_⟩
  intro h
  have := h draws
  omega
/-- Repetition defeats the degree guarantee at every size, so the defect persists
for arbitrarily large fourth powers; it is not just a small-n boundary case. -/
theorem constant_draw_degree (d n : ℕ) (hd : 0 < d) :
    (Finset.univ.image (fun _ : Fin d => (0 : Fin (n+1)))).card = 1 := by
  have hn : (Finset.univ : Finset (Fin d)).Nonempty := ⟨⟨0,hd⟩,Finset.mem_univ _⟩
  rw [Finset.image_const hn]
  simp
end ProofCerts.Alg4
#print axioms ProofCerts.Alg4.sampling_with_replacement_degree_claim_refuted
#print axioms ProofCerts.Alg4.constant_draw_degree
