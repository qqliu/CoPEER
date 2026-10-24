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
def extension_condition (σ' : Nat → Letter) (i : Nat) : Prop := ∀ j : Nat, i ≤ j → ¬Commit (σ' j)

/-- The corrected step (shape fixed): if `σ` violates `phi` at `i`, every extension `σ'` of the inclusive
prefix of length `i + 1` that satisfies the condition also violates `phi` at `i`. -/
def CorrectedStep : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i
-- ===== END FIXED PART =====

theorem repair_statement : ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i → ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ → SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
  intro σ i hv σ' hag hc hphi
  apply hv
  intro hreq
  exfalso
  have heq : σ' i = σ i := hag i (Nat.lt_succ_self i)
  obtain ⟨j, hj, hcj⟩ := hphi (by rw [heq]; exact hreq)
  exact hc j hj hcj

theorem repair_nonvacuous : (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ SEcs156543q.extension_condition σ' i) ∧ (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ ¬SEcs156543q.extension_condition σ' i) := by
  refine ⟨⟨fun _ => eeL, 0, fun _ => eeL, ?_, ?_, ?_⟩, ⟨fun _ => eeL, 0, fun k => if k = 0 then eeL else c1L, ?_, ?_, ?_⟩⟩
  · intro h
    obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
    simp [eeL] at hj
  · intro k _; rfl
  · intro j _ h
    simp [Commit, eeL] at h
  · intro h
    obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
    simp [eeL] at hj
  · intro k hk
    have : k = 0 := by omega
    subst this; rfl
  · intro h
    apply h 1 (Nat.zero_le 1)
    simp [Commit, c1L]

theorem gphi_ext (σ : Nat → Letter) (n : Nat) :
    GPhi (fun k => if k < n then σ k else c1L) := by
  intro i _
  refine ⟨i + n, Nat.le_add_right i n, Or.inl ?_⟩
  have : ¬ (i + n < n) := by omega
  simp [this, c1L]

theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := by
  refine ⟨?_, ?_⟩
  · intro σ n
    refine ⟨fun k => if k < n then σ k else c1L, ?_, gphi_ext σ n⟩
    intro k hk
    simp [hk]
  · intro hs
    have hv : ¬ GPhi (fun _ => eeL) := by
      intro h
      obtain ⟨j, _, hj⟩ := h 0 ⟨rfl, rfl⟩
      simp [eeL] at hj
    obtain ⟨n, hn⟩ := hs _ hv
    apply hn _ _ (gphi_ext (fun _ => eeL) n)
    intro k hk
    simp [hk]

end SEcs156543q
