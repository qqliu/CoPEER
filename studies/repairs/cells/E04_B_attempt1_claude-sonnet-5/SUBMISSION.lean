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

/-- Helper: extend a word `σ` by copying its first `n` letters and then committing (`c1L`) forever. -/
def extendCommit (σ : Nat → Letter) (n : Nat) : Nat → Letter :=
  fun k => if k < n then σ k else c1L

theorem extendCommit_agree (σ : Nat → Letter) (n : Nat) :
    AgreeUpTo n (extendCommit σ n) σ := by
  intro k hk
  simp [extendCommit, hk]

theorem extendCommit_GPhi (σ : Nat → Letter) (n : Nat) :
    GPhi (extendCommit σ n) := by
  intro i _
  rcases Nat.lt_or_ge i n with hlt | hle
  · refine ⟨n, by omega, ?_⟩
    have hnotlt : ¬ (n < n) := by omega
    simp [extendCommit, hnotlt, c1L]
  · refine ⟨i, Nat.le_refl i, ?_⟩
    have hnotlt : ¬ (i < n) := by omega
    simp [extendCommit, hnotlt, c1L]

theorem repair_statement :
    ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i →
      ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ →
        SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
  intro σ i hσ σ' hagree hext hPhi
  have hsi : σ' i = σ i := hagree i (by omega)
  by_cases hR : (σ i).p1e = true ∧ (σ i).p2e = true
  · have hnex : ¬ ∃ j, i ≤ j ∧ ((σ j).p1c = true ∨ (σ j).p2c = true) := by
      intro h
      exact hσ (fun _ => h)
    have hR' : (σ' i).p1e = true ∧ (σ' i).p2e = true := by rw [hsi]; exact hR
    obtain ⟨j, hij, hc⟩ := hPhi hR'
    exact hext j hij hc
  · exact hσ (fun hR' => (hR hR').elim)

theorem repair_nonvacuous :
    (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter),
        ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧
          SEcs156543q.extension_condition σ' i) ∧
    (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter),
        ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧
          ¬SEcs156543q.extension_condition σ' i) := by
  constructor
  · refine ⟨fun _ => eeL, 0, fun _ => eeL, ?_, ?_, ?_⟩
    · intro h
      obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
      simp [eeL] at hj
    · intro k _; rfl
    · intro j _; simp [Commit, eeL]
  · refine ⟨fun _ => eeL, 0, fun n => if n = 0 then eeL else c1L, ?_, ?_, ?_⟩
    · intro h
      obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
      simp [eeL] at hj
    · intro k hk
      have hk0 : k = 0 := by omega
      subst hk0; simp
    · intro hcond
      have h1 := hcond 1 (by omega)
      apply h1
      simp [Commit, c1L]

theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧
    ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := by
  constructor
  · intro σ n
    exact ⟨extendCommit σ n, extendCommit_agree σ n, extendCommit_GPhi σ n⟩
  · intro hsafe
    have hnot : ¬ GPhi (fun _ : Nat => eeL) := by
      intro h
      obtain ⟨j, _, hj⟩ := h 0 ⟨rfl, rfl⟩
      simp [eeL] at hj
    obtain ⟨n, hn⟩ := hsafe (fun _ : Nat => eeL) hnot
    exact hn (extendCommit (fun _ : Nat => eeL) n) (extendCommit_agree _ n)
      (extendCommit_GPhi _ n)

end SEcs156543q
