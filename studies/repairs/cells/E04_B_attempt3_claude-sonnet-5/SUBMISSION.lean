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
def extension_condition (σ' : Nat → Letter) (i : Nat) : Prop := ∀ j : Nat, i ≤ j → ¬ Commit (σ' j)

/-- The corrected step (shape fixed): if `σ` violates `phi` at `i`, every extension `σ'` of the inclusive
prefix of length `i + 1` that satisfies the condition also violates `phi` at `i`. -/
def CorrectedStep : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i
-- ===== END FIXED PART =====

/-- Witness word: both processes request at position 0, nobody ever commits. -/
def sigmaInfinite (n : Nat) : Letter := if n = 0 then eeL else emptyL

/-- Witness word: same first letter, then P1 commits forever. -/
def sigmaPrimeInfinite (n : Nat) : Letter := if n = 0 then eeL else c1L

theorem sigma_violates_at_zero : ¬PhiInfinite sigmaInfinite 0 := by
  intro h
  obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
  by_cases h0 : j = 0 <;>
    simp [sigmaInfinite, h0, eeL, emptyL] at hj

theorem sigma_never_commits : ∀ j : Nat, 0 ≤ j → ¬ Commit (sigmaInfinite j) := by
  intro j _ hc
  by_cases h0 : j = 0 <;> simp [sigmaInfinite, h0, eeL, emptyL, Commit] at hc

theorem same_prefix_of_length_one : AgreeUpTo 1 sigmaPrimeInfinite sigmaInfinite := by
  intro k hk
  have hk0 : k = 0 := by omega
  subst hk0
  rfl

theorem sigmaPrime_commits_at_one : Commit (sigmaPrimeInfinite 1) := by
  simp [sigmaPrimeInfinite, c1L, Commit]

/-- Extend the first `n` letters of `σ` with a permanent commit afterwards. -/
def extendConst (σ : Nat → Letter) (n : Nat) : Nat → Letter :=
  fun k => if k < n then σ k else c1L

theorem extendConst_agree (σ : Nat → Letter) (n : Nat) : AgreeUpTo n (extendConst σ n) σ := by
  intro k hk
  simp [extendConst, hk]

theorem extendConst_GPhi (σ : Nat → Letter) (n : Nat) : GPhi (extendConst σ n) := by
  intro i _
  refine ⟨i + n, by omega, ?_⟩
  have hnotlt : ¬ (i + n < n) := by omega
  have : extendConst σ n (i + n) = c1L := by simp [extendConst, hnotlt]
  left
  rw [this]
  rfl

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i → ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ → SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
  intro σ i hσ σ' hagree hcond hσ'
  apply hσ
  intro hreq
  have hσi_eq : σ' i = σ i := hagree i (by omega)
  have hreq' : Request (σ' i) := by
    rw [hσi_eq]
    exact hreq
  obtain ⟨j, hij, hcommit⟩ := hσ' hreq'
  exact absurd hcommit (hcond j hij)

theorem repair_nonvacuous : (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ SEcs156543q.extension_condition σ' i) ∧ (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ ¬SEcs156543q.extension_condition σ' i) := by
  constructor
  · refine ⟨sigmaInfinite, 0, sigmaInfinite, sigma_violates_at_zero, ?_, ?_⟩
    · intro k _; rfl
    · exact sigma_never_commits
  · refine ⟨sigmaInfinite, 0, sigmaPrimeInfinite, sigma_violates_at_zero, same_prefix_of_length_one, ?_⟩
    intro hcond
    exact hcond 1 (by omega) sigmaPrime_commits_at_one

theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := by
  constructor
  · intro σ n
    exact ⟨extendConst σ n, extendConst_agree σ n, extendConst_GPhi σ n⟩
  · intro hSafety
    have hnot : ¬ GPhi sigmaInfinite := by
      intro hG
      exact sigma_violates_at_zero (hG 0)
    obtain ⟨n, hn⟩ := hSafety sigmaInfinite hnot
    exact hn (extendConst sigmaInfinite n) (extendConst_agree sigmaInfinite n) (extendConst_GPhi sigmaInfinite n)

end SEcs156543q
