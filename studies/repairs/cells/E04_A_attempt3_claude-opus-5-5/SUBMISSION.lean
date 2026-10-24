import defs_only
/-!
Record E04: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SEcs156543q

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The condition on the extension `σ'` (and the position `i`) under which the source's step becomes
valid: an extension of the inclusive prefix `σ[..i]` that satisfies it still violates `phi` at `i`. The
hole must be a proposition in `σ'` and `i` built from `Commit`, `Request`, letters, positions and
quantifiers over `Nat`; it may not mention `PhiInfinite`, `GPhi`, `AgreeUpTo`, `LocalClaim`, `IsSafety`
or `IsLiveness`, and it may not be `True` or `False`. -/
def extension_condition (σ' : Nat → Letter) (i : Nat) : Prop := ∀ j : Nat, i < j → ¬ Commit (σ' j)

/-- The corrected step (shape fixed): if `σ` violates `phi` at `i`, every extension `σ'` of the inclusive
prefix of length `i + 1` that satisfies the condition also violates `phi` at `i`. -/
def CorrectedStep : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i
-- ===== END FIXED PART =====

theorem repair_statement : ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i → ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ → SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
  intro σ i h σ' hag hc hphi
  apply h
  intro hr
  have heq : σ' i = σ i := hag i (Nat.lt_succ_self i)
  obtain ⟨j, hij, hj⟩ := hphi (by rw [heq]; exact hr)
  rcases Nat.lt_or_eq_of_le hij with hlt | rfl
  · exact absurd hj (hc j hlt)
  · exact ⟨i, Nat.le_refl i, by rw [← heq]; exact hj⟩

theorem repair_nonvacuous : (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ SEcs156543q.extension_condition σ' i) ∧ (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ ¬SEcs156543q.extension_condition σ' i) := by
  have hv : ¬ PhiInfinite (fun _ => eeL) 0 := by
    intro h
    obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
    simp [eeL] at hj
  refine ⟨⟨fun _ => eeL, 0, fun _ => eeL, hv, fun _ _ => rfl, ?_⟩,
    ⟨fun _ => eeL, 0, fun k => if k = 0 then eeL else c1L, hv, ?_, ?_⟩⟩
  · intro j _ hj
    simp [Commit, eeL] at hj
  · intro k hk
    have : k = 0 := by omega
    subst this; rfl
  · intro hc
    exact hc 1 (by decide) (Or.inl rfl)

theorem prefix_ext_gphi (σ : Nat → Letter) (n : Nat) :
    AgreeUpTo n (fun k => if k < n then σ k else c1L) σ ∧
      GPhi (fun k => if k < n then σ k else c1L) := by
  refine ⟨fun k hk => by simp [hk], ?_⟩
  intro i _
  refine ⟨max i n, Nat.le_max_left _ _, Or.inl ?_⟩
  have : ¬ (max i n < n) := by omega
  simp only [this, if_false]
  rfl

theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := by
  refine ⟨fun σ n => ⟨_, prefix_ext_gphi σ n⟩, ?_⟩
  intro hs
  have hv : ¬ GPhi (fun _ => eeL) := by
    intro h
    obtain ⟨j, _, hj⟩ := h 0 ⟨rfl, rfl⟩
    simp [eeL] at hj
  obtain ⟨n, hn⟩ := hs _ hv
  have := prefix_ext_gphi (fun _ => eeL) n
  exact hn _ this.1 this.2

end SEcs156543q
