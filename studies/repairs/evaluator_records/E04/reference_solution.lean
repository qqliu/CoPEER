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
def extension_condition (σ' : Nat → Letter) (i : Nat) : Prop := ∀ j : Nat, i < j → ¬Commit (σ' j)

/-- The corrected step (shape fixed): if `σ` violates `phi` at `i`, every extension `σ'` of the inclusive
prefix of length `i + 1` that satisfies the condition also violates `phi` at `i`. -/
def CorrectedStep : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → extension_condition σ' i → ¬PhiInfinite σ' i
-- ===== END FIXED PART =====

theorem ite_pos_aux {α : Type} {c : Prop} [Decidable c] (h : c) {a b : α} :
    (if c then a else b) = a := by
  split
  · rfl
  · contradiction

theorem ite_neg_aux {α : Type} {c : Prop} [Decidable c] (h : ¬c) {a b : α} :
    (if c then a else b) = b := by
  split
  · contradiction
  · rfl

/-- Both processes request forever, nobody ever commits. -/
def allReqW : Nat → Letter := fun _ => eeL

theorem allReq_no_commit (j : Nat) : ¬Commit (allReqW j) := by
  intro h
  cases h with
  | inl h1 =>
    have h1' : eeL.p1c = true := h1
    exact absurd h1' (by decide)
  | inr h2 =>
    have h2' : eeL.p2c = true := h2
    exact absurd h2' (by decide)

theorem allReq_violates (i : Nat) : ¬PhiInfinite allReqW i := by
  intro h
  obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
  exact allReq_no_commit j hj

/-- The first letter of `allReqW`, then P1 commits forever. -/
def commitAfter : Nat → Letter := fun k => if k = 0 then eeL else c1L

/-- Keep the first `n` letters of `σ`, then `{P1C}` forever. -/
def extendC1 (σ : Nat → Letter) (n : Nat) : Nat → Letter := fun k => if k < n then σ k else c1L

theorem extendC1_agrees (σ : Nat → Letter) (n : Nat) : AgreeUpTo n (extendC1 σ n) σ := by
  intro k hk
  unfold extendC1; exact ite_pos_aux hk

theorem extendC1_tail (σ : Nat → Letter) (n k : Nat) (h : ¬k < n) : extendC1 σ n k = c1L := by
  unfold extendC1; exact ite_neg_aux h

theorem extendC1_ok (σ : Nat → Letter) (n : Nat) : AgreeUpTo n (extendC1 σ n) σ ∧ GPhi (extendC1 σ n) := by
  refine ⟨extendC1_agrees σ n, ?_⟩
  intro i hreq
  by_cases hin : i < n
  · refine ⟨n, by omega, Or.inl ?_⟩
    rw [extendC1_tail σ n n (by omega)]; rfl
  · rw [extendC1_tail σ n i hin] at hreq
    exact absurd hreq.1 (by decide)

theorem gphi_not_all : ¬GPhi allReqW := fun h => allReq_violates 0 (h 0)

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected step holds for every word, position and extension. -/
theorem repair_statement : ∀ (σ : Nat → SEcs156543q.Letter) (i : Nat), ¬SEcs156543q.PhiInfinite σ i → ∀ σ' : Nat → SEcs156543q.Letter, SEcs156543q.AgreeUpTo (i + 1) σ' σ → SEcs156543q.extension_condition σ' i → ¬SEcs156543q.PhiInfinite σ' i := by
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

/-- Non-vacuity: the hypotheses of the corrected step are jointly satisfiable, and the added condition is
not trivially true under the other hypotheses (some extension of a violating word's prefix fails it). -/
theorem repair_nonvacuous : (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ SEcs156543q.extension_condition σ' i) ∧ (∃ (σ : Nat → SEcs156543q.Letter) (i : Nat) (σ' : Nat → SEcs156543q.Letter), ¬SEcs156543q.PhiInfinite σ i ∧ SEcs156543q.AgreeUpTo (i + 1) σ' σ ∧ ¬SEcs156543q.extension_condition σ' i) := ⟨⟨allReqW, 0, allReqW, allReq_violates 0, fun _ _ => rfl, by
      unfold extension_condition
      intro j _ hc
      exact allReq_no_commit j hc⟩,
   ⟨allReqW, 0, commitAfter, allReq_violates 0, by
      intro k hk
      have hk0 : k = 0 := by omega
      subst hk0
      rfl, by
      unfold extension_condition
      intro h
      exact h 1 (by decide) (Or.inl rfl)⟩⟩

/-- The corrected classification (the endpoint of this record): `G phi` is a liveness property and not a
safety property, under the source's own definition of safety. If you cannot prove it, replace this
declaration (this doc comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : SEcs156543q.IsLiveness SEcs156543q.GPhi ∧ ¬ SEcs156543q.IsSafety SEcs156543q.GPhi := ⟨fun σ n => ⟨extendC1 σ n, (extendC1_ok σ n).1, (extendC1_ok σ n).2⟩, by
    intro hs
    obtain ⟨n, hn⟩ := hs allReqW gphi_not_all
    exact hn (extendC1 allReqW n) (extendC1_ok allReqW n).1 (extendC1_ok allReqW n).2⟩
-- ===== END OBLIGATIONS =====
end SEcs156543q
