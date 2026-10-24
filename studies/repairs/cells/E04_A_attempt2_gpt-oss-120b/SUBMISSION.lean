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
  Request (σ' i) ∧ ∀ j, i ≤ j → ¬ Commit (σ' j)

/-- The corrected step (shape fixed): if `σ` violates `phi` at `i`, every extension `σ'` of the inclusive
prefix of length `i + 1` that satisfies the condition also violates `phi` at `i`. -/
def CorrectedStep : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i
-- ===== END FIXED PART =====

/-- Repair statement: the corrected step holds universally. -/
theorem repair_statement :
  ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat),
    ¬SEcs156543q.PhiInfinite σ i →
    ∀ σ' : Nat → SEcs156543q.Letter,
      SEcs156543q.AgreeUpTo (i + 1) σ' σ →
      SEcs156543q.extension_condition σ' i →
      ¬SEcs156543q.PhiInfinite σ' i :=
by
  intro σ i hnot σ' hAgree hCond
  intro hPhi
  rcases hCond with ⟨hReq, hNoComm⟩
  have hExists := hPhi hReq
  rcases hExists with ⟨j, hij, hComm⟩
  exact (hNoComm j hij) hComm

/-- Non‑vacuity of the repaired statement: the hypotheses are satisfiable and the added condition is not trivial. -/
theorem repair_nonvacuous :
  (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter),
      ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ SEcs156543q.extension_condition σ' i) ∧
  (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter),
      ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ ¬SEcs156543q.extension_condition σ' i) :=
by
  let σ0 : Nat → Letter := fun _ => eeL
  have hReq0 : Request (σ0 0) := by
    dsimp [Request, σ0]; simp
  have hNoComm0 : ∀ j, (0 : Nat) ≤ j → ¬ Commit (σ0 j) := by
    intro j _
    dsimp [Commit, σ0]; simp
  have hNotPhi0 : ¬PhiInfinite σ0 0 := by
    intro hPhi
    have hExists := hPhi hReq0
    rcases hExists with ⟨j, _, hComm⟩
    exact (hNoComm0 j (Nat.zero_le _)) hComm
  have hAgree0 : AgreeUpTo (0 + 1) σ0 σ0 := by intro k hk; rfl
  have hCond0 : extension_condition σ0 0 := ⟨hReq0, hNoComm0⟩
  refine And.intro ?pos ?neg
  · exact ⟨σ0, 0, σ0, hNotPhi0, hAgree0, hCond0⟩
  -- second witness where the condition fails
  let σ1 : Nat → Letter := fun n => if n ≤ 0 then eeL else c1L
  have hAgree1 : AgreeUpTo (0 + 1) σ1 σ0 := by
    intro k hk
    have hk0 : k = 0 := Nat.lt_one_iff.mp hk
    subst hk0
    simpa [σ1, σ0]
  have hCond1_false : ¬extension_condition σ1 0 := by
    intro h
    rcases h with ⟨_, hNo⟩
    have hComm1 : Commit (σ1 1) := by
      simpa [σ1, Commit, c1L]
    exact (hNo 1 (Nat.zero_le _)) hComm1
  exact ⟨σ0, 0, σ1, hNotPhi0, hAgree1, hCond1_false⟩

/-- Final classification: `GPhi` is a liveness property and not a safety property. -/
theorem final_theorem :
  SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi :=
by
  constructor
  · -- liveness
    intro σ n
    let σ' : Nat → Letter := fun k => if h : k < n then σ k else c1L
    have hAgree : AgreeUpTo n σ' σ := by
      intro k hk
      have hkn : k < n := hk
      simp [σ', hkn]
    refine ⟨σ', hAgree, ?gp⟩
    intro i
    intro hReq
    by_cases hlt : i < n
    · -- use commit at position n
      have hle : i ≤ n := Nat.le_of_lt hlt
      have hCommit : Commit (σ' n) := by
        simp [σ', Commit, c1L]
      exact ⟨n, hle, hCommit⟩
    · -- i ≥ n, commit already at i
      have hge : n ≤ i := Nat.le_of_not_gt hlt
      have hCommit : Commit (σ' i) := by
        simp [σ', hlt, Commit, c1L]
      exact ⟨i, Nat.le_refl _, hCommit⟩
  · -- not safety
    intro hSafety
    let bad : Nat → Letter := fun _ => eeL
    have hBadNot : ¬GPhi bad := by
      intro hAll
      have h0 := hAll 0
      have hReq0 : Request (bad 0) := by
        dsimp [Request, bad]; simp
      have hExists := h0 hReq0
      rcases hExists with ⟨j, _, hComm⟩
      have : ¬ Commit (bad j) := by
        dsimp [Commit, bad]; simp
      exact this hComm
    rcases hSafety bad hBadNot with ⟨n, hProp⟩
    let good : Nat → Letter := fun k => if h : k < n then bad k else c1L
    have hAgree : AgreeUpTo n good bad := by
      intro k hk
      have hkn : k < n := hk
      simp [good, hkn]
    have hGPhi : GPhi good := by
      intro i
      intro hReq
      by_cases hlt : i < n
      · have hle : i ≤ n := Nat.le_of_lt hlt
        have hCommit : Commit (good n) := by
          simp [good, Commit, c1L]
        exact ⟨n, hle, hCommit⟩
      · have hge : n ≤ i := Nat.le_of_not_gt hlt
        have hCommit : Commit (good i) := by
          simp [good, hlt, Commit, c1L]
        exact ⟨i, Nat.le_refl _, hCommit⟩
    have hContr := hProp good hAgree
    exact hContr hGPhi

end SEcs156543q
