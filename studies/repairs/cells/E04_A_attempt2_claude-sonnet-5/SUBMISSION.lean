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

/-- Helper: from `¬PhiInfinite σ i` we can extract that `Request (σ i)` holds. -/
theorem request_of_not_phi (σ : Nat → Letter) (i : Nat) (h : ¬PhiInfinite σ i) : Request (σ i) :=
  Classical.byContradiction (fun hR => h (fun hreq => absurd hreq hR))

/-- Helper: builds a word that eventually (from position `n` on) commits, hence satisfies `GPhi`. -/
theorem gphi_of_eventually_commit (σ : Nat → Letter) (n : Nat) :
    GPhi (fun k => if k < n then σ k else c1L) := by
  intro i _
  by_cases hin : i < n
  · refine ⟨n, by omega, ?_⟩
    have hn : ¬ (n < n) := by omega
    simp [hn, c1L]
  · refine ⟨i, Nat.le_refl i, ?_⟩
    simp [hin, c1L]

theorem repair_statement :
    ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i →
      ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ →
        SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
  intro σ i hσ σ' hagree hext hphi'
  have hReqσ : Request (σ i) := request_of_not_phi σ i hσ
  have heq : σ' i = σ i := hagree i (Nat.lt_succ_self i)
  have hReqσ' : Request (σ' i) := heq ▸ hReqσ
  obtain ⟨j, hij, hcommit⟩ := hphi' hReqσ'
  exact hext j hij hcommit

theorem repair_nonvacuous :
    (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter),
        ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧
          SEcs156543q.extension_condition σ' i) ∧
    (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter),
        ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧
          ¬SEcs156543q.extension_condition σ' i) := by
  constructor
  · refine ⟨fun _ => eeL, 0, fun _ => eeL, ?_, ?_, ?_⟩
    · intro hphi
      obtain ⟨j, _, hc⟩ := hphi ⟨rfl, rfl⟩
      simp [eeL] at hc
    · intro k _; rfl
    · intro j _ hc
      simp [eeL, Commit] at hc
  · refine ⟨fun _ => eeL, 0, fun k => if k = 1 then c1L else eeL, ?_, ?_, ?_⟩
    · intro hphi
      obtain ⟨j, _, hc⟩ := hphi ⟨rfl, rfl⟩
      simp [eeL] at hc
    · intro k hk
      have : k = 0 := by omega
      subst this
      simp
    · intro hext
      have := hext 1 (by omega)
      apply this
      simp [c1L, Commit]

theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := by
  constructor
  · intro σ n
    refine ⟨fun k => if k < n then σ k else c1L, ?_, ?_⟩
    · intro k hk; simp [hk]
    · exact gphi_of_eventually_commit σ n
  · intro hsafe
    have hnotG : ¬ GPhi (fun _ : Nat => eeL) := by
      intro hG
      have h0 := hG 0
      have : ∃ j : Nat, 0 ≤ j ∧ ((eeL).p1c = true ∨ (eeL).p2c = true) := h0 ⟨rfl, rfl⟩
      obtain ⟨j, _, hc⟩ := this
      simp [eeL] at hc
    obtain ⟨n, hn⟩ := hsafe (fun _ => eeL) hnotG
    have hagree : AgreeUpTo n (fun k => if k < n then eeL else c1L) (fun _ => eeL) := by
      intro k hk; simp [hk]
    exact (hn _ hagree) (gphi_of_eventually_commit (fun _ => eeL) n)

end SEcs156543q
