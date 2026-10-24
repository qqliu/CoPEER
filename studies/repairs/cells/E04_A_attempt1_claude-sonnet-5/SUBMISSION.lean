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
def extension_condition (σ' : Nat → Letter) (i : Nat) : Prop :=
  ∀ j : Nat, i ≤ j → ¬ Commit (σ' j)

/-- The corrected step (shape fixed): if `σ` violates `phi` at `i`, every extension `σ'` of the inclusive
prefix of length `i + 1` that satisfies the condition also violates `phi` at `i`. -/
def CorrectedStep : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i
-- ===== END FIXED PART =====

/-- Helper: the extension of `σ` up to position `n` (agreeing on `0..n-1`) that commits at position
`n` and never requests or commits after that. Used to show `GPhi` is liveness and not safety. -/
def extAt (σ : Nat → Letter) (n : Nat) : Nat → Letter :=
  fun k => if k < n then σ k else if k = n then c1L else emptyL

theorem extAt_agree (σ : Nat → Letter) (n : Nat) : AgreeUpTo n (extAt σ n) σ := by
  intro k hk
  simp [extAt, hk]

theorem extAt_GPhi (σ : Nat → Letter) (n : Nat) : GPhi (extAt σ n) := by
  intro i
  intro hReq
  by_cases h : i ≤ n
  · refine ⟨n, h, ?_⟩
    have : extAt σ n n = c1L := by simp [extAt]
    rw [this]
    left
    rfl
  · exfalso
    have hne : i ≠ n := by omega
    have hnlt : ¬ (i < n) := by omega
    have : extAt σ n i = emptyL := by simp [extAt, hnlt, hne]
    rw [this] at hReq
    have := hReq.1
    simp [emptyL] at this

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i → ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ → SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
  intro σ i hnP σ' hagree hcond hImp
  have hReqi : Request (σ i) := by
    by_cases hr : Request (σ i)
    · exact hr
    · exfalso
      apply hnP
      intro hr'
      exact absurd hr' hr
  have heq : σ' i = σ i := hagree i (Nat.lt_succ_self i)
  have hReqi' : Request (σ' i) := by rw [heq]; exact hReqi
  obtain ⟨j, hij, hcomm⟩ := hImp hReqi'
  exact (hcond j hij) hcomm

theorem repair_nonvacuous : (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ SEcs156543q.extension_condition σ' i) ∧ (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ ¬SEcs156543q.extension_condition σ' i) := by
  constructor
  · refine ⟨fun _ => eeL, 0, fun _ => eeL, ?_, ?_, ?_⟩
    · intro hImp
      obtain ⟨j, _, hcomm⟩ := hImp ⟨rfl, rfl⟩
      simp [Commit, eeL] at hcomm
    · intro k hk; rfl
    · intro j hj hcomm
      simp [Commit, eeL] at hcomm
  · refine ⟨fun _ => eeL, 0, fun k => if k = 0 then eeL else c1L, ?_, ?_, ?_⟩
    · intro hImp
      obtain ⟨j, _, hcomm⟩ := hImp ⟨rfl, rfl⟩
      simp [Commit, eeL] at hcomm
    · intro k hk
      have : k = 0 := by omega
      simp [this]
    · intro hcond
      have := hcond 1 (by omega)
      apply this
      left
      simp [c1L]

theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := by
  constructor
  · intro σ n
    exact ⟨extAt σ n, extAt_agree σ n, extAt_GPhi σ n⟩
  · intro hSafety
    have hnG : ¬ GPhi (fun _ => eeL) := by
      intro hG
      obtain ⟨j, _, hcomm⟩ := (hG 0) ⟨rfl, rfl⟩
      simp [Commit, eeL] at hcomm
    obtain ⟨n, h⟩ := hSafety (fun _ => eeL) hnG
    have hagree := extAt_agree (fun _ => eeL) n
    have hG := extAt_GPhi (fun _ => eeL) n
    exact (h (extAt (fun _ => eeL) n) hagree) hG

end SEcs156543q
