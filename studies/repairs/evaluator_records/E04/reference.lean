import defs_only
/- EVALUATOR-ONLY reference correction for E04 (original package: corrected_step, line 308; repair_liveness 425; repair_not_safety 433). -/
namespace SEcs156543q.Ref

/-- Reference condition: no commit strictly after position `i`. -/
def extension_condition (σ' : Nat → Letter) (i : Nat) : Prop := ∀ j : Nat, i < j → ¬Commit (σ' j)

theorem universal : ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i → ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i := by
  intro σ i hadm σ' hag hnc hphi
  unfold extension_condition at hnc
  have hi : σ' i = σ i := hag i (by omega)
  have hreq : Request (σ' i) := by
    rw [hi]
    by_cases hr : Request (σ i)
    · exact hr
    · exact absurd (fun h => absurd h hr) hadm
  obtain ⟨j, hij, hc⟩ := hphi hreq
  by_cases hji : j = i
  · rw [hji, hi] at hc
    exact hadm (fun _ => ⟨i, Nat.le_refl i, hc⟩)
  · exact hnc j (by omega) hc

end SEcs156543q.Ref
