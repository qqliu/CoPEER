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

/-- For any word `σ` and any prefix length `n`, we can extend the prefix of `σ` by forcing a commit
right at position `n` and forever after; the result satisfies `GPhi`. This witnesses liveness and is
also the key tool to show `GPhi` is not safe. -/
theorem extend_to_live (σ : Nat → Letter) (n : Nat) :
    ∃ σ' : Nat → Letter, AgreeUpTo n σ' σ ∧ GPhi σ' := by
  refine ⟨fun k => if k < n then σ k else c1L, ?_, ?_⟩
  · intro k hk
    simp [hk]
  · intro i _hreq
    refine ⟨max i n, Nat.le_max_left i n, ?_⟩
    have hnotlt : ¬ (max i n < n) := by omega
    simp [c1L, hnotlt]

theorem repair_statement :
    ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
      ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i := by
  intro σ i hσ σ' hagree hext hPhi'
  have hReq : Request (σ i) := by
    by_cases hnr : Request (σ i)
    · exact hnr
    · exact (hσ (fun hr => (hnr hr).elim)).elim
  have hsame : σ' i = σ i := hagree i (by omega)
  have hReq' : Request (σ' i) := by rw [hsame]; exact hReq
  obtain ⟨j, hij, hc⟩ := hPhi' hReq'
  exact hext j hij hc

theorem repair_nonvacuous :
    (∃ (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter),
        ¬PhiInfinite σ i ∧ AgreeUpTo (i + 1) σ' σ ∧ extension_condition σ' i) ∧
    (∃ (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter),
        ¬PhiInfinite σ i ∧ AgreeUpTo (i + 1) σ' σ ∧ ¬extension_condition σ' i) := by
  constructor
  · refine ⟨fun _ => eeL, 0, fun _ => eeL, ?_, ?_, ?_⟩
    · intro h
      obtain ⟨j, hij, hc⟩ := h ⟨rfl, rfl⟩
      simp [Commit, eeL] at hc
    · intro k _hk; rfl
    · intro j _hij
      simp [Commit, eeL]
  · refine ⟨fun _ => eeL, 0, fun n => if n = 0 then eeL else c1L, ?_, ?_, ?_⟩
    · intro h
      obtain ⟨j, hij, hc⟩ := h ⟨rfl, rfl⟩
      simp [Commit, eeL] at hc
    · intro k hk
      have hk0 : k = 0 := by omega
      simp [hk0]
    · intro hext
      exact (hext 1 (by omega)) (by simp [Commit, c1L])

theorem final_theorem : IsLiveness GPhi ∧ ¬ IsSafety GPhi := by
  constructor
  · intro σ n
    exact extend_to_live σ n
  · intro hSafe
    have hnotP : ¬ GPhi (fun _ => eeL) := by
      intro h
      obtain ⟨j, _hij, hc⟩ := h 0 ⟨rfl, rfl⟩
      simp [Commit, eeL] at hc
    obtain ⟨n, hn⟩ := hSafe (fun _ => eeL) hnotP
    obtain ⟨σ', hagree, hlive⟩ := extend_to_live (fun _ => eeL) n
    exact hn σ' hagree hlive

end SEcs156543q
