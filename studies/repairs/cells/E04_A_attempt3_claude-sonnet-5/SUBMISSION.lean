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

/-- The constant word that always issues the request from both processes but never commits. -/
def constSigma : Nat → Letter := fun _ => eeL

theorem constSigma_not_phi (i : Nat) : ¬PhiInfinite constSigma i := by
  intro h
  have hReq : Request (constSigma i) := ⟨rfl, rfl⟩
  obtain ⟨j, _, hc⟩ := h hReq
  rcases hc with hc | hc <;> simp [constSigma, eeL] at hc

/-- Extend `σ` by copying it for positions `< n`, committing exactly at `n`, and doing nothing after. -/
def extend (σ : Nat → Letter) (n : Nat) : Nat → Letter :=
  fun k => if k < n then σ k else if k = n then c1L else emptyL

theorem extend_agree (σ : Nat → Letter) (n : Nat) : AgreeUpTo n (extend σ n) σ := by
  intro k hk
  simp [extend, hk]

theorem extend_gphi (σ : Nat → Letter) (n : Nat) : GPhi (extend σ n) := by
  intro i
  intro hReq
  rcases Nat.lt_trichotomy i n with hlt | heq | hgt
  · refine ⟨n, Nat.le_of_lt hlt, Or.inl ?_⟩
    have hnn : ¬ (n < n) := Nat.lt_irrefl n
    simp [extend, hnn, c1L]
  · exfalso
    have hnn : ¬ (n < n) := Nat.lt_irrefl n
    have : (extend σ n i).p1e = c1L.p1e := by simp [extend, heq, hnn]
    have h1 : (extend σ n i).p1e = true := hReq.1
    rw [this] at h1
    exact absurd h1 (by simp [c1L])
  · exfalso
    have hin : ¬ (i < n) := Nat.not_lt.mpr (Nat.le_of_lt hgt)
    have hine : i ≠ n := Nat.ne_of_gt hgt
    have : (extend σ n i).p1e = emptyL.p1e := by simp [extend, hin, hine]
    have h1 : (extend σ n i).p1e = true := hReq.1
    rw [this] at h1
    exact absurd h1 (by simp [emptyL])

theorem repair_statement : ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i → ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ → SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
  intro σ i hnp σ' hagree hext hcontra
  have hReq : Request (σ i) := by
    by_cases hr : Request (σ i)
    · exact hr
    · exact (hnp (fun h => absurd h hr)).elim
  have heq : σ' i = σ i := hagree i (Nat.lt_succ_self i)
  have hReq' : Request (σ' i) := heq ▸ hReq
  obtain ⟨j, hij, hcommit⟩ := hcontra hReq'
  exact hext j hij hcommit

theorem repair_nonvacuous : (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ SEcs156543q.extension_condition σ' i) ∧ (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ ¬SEcs156543q.extension_condition σ' i) := by
  constructor
  · refine ⟨constSigma, 0, constSigma, constSigma_not_phi 0, ?_, ?_⟩
    · intro k _; rfl
    · intro j _
      intro hc
      rcases hc with hc | hc <;> simp [constSigma, eeL] at hc
  · refine ⟨constSigma, 0, fun k => if k = 0 then eeL else c1L, constSigma_not_phi 0, ?_, ?_⟩
    · intro k hk
      have : k = 0 := Nat.lt_one_iff.mp hk
      simp [this, constSigma]
    · intro hcond
      have := hcond 1 (by omega)
      apply this
      simp [Commit, c1L]

theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := by
  constructor
  · intro σ n
    exact ⟨extend σ n, extend_agree σ n, extend_gphi σ n⟩
  · intro hsafety
    obtain ⟨n, hn⟩ := hsafety constSigma (fun h => constSigma_not_phi 0 (h 0))
    have hEx := extend_agree constSigma n
    have hG := extend_gphi constSigma n
    exact hn (extend constSigma n) hEx hG

end SEcs156543q
