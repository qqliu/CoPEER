import SUBMISSION
import reference
/- EVALUATOR-ONLY hidden-instance agreement for E04: the submitted condition on (σ', i) must be equivalent to the reference
('no commit strictly after i') on the listed eventually-constant words. Boundary instances (a commit exactly at i) are not
listed because 'no commit at or after i' is also admissible. Proof-based (the condition quantifies over Nat); the cascades
cover ∀-shaped and ¬∃-shaped conditions with the binder order (position, bound). Fail-closed. -/

/-- Test words (evaluator-only). -/
def wEmpty : Nat → SEcs156543q.Letter := fun _ => SEcs156543q.emptyL
def wReq : Nat → SEcs156543q.Letter := fun _ => SEcs156543q.eeL
def wCommitAt1 : Nat → SEcs156543q.Letter := fun k => if k = 0 then SEcs156543q.eeL else SEcs156543q.c1L
def wCommitAt3 : Nat → SEcs156543q.Letter := fun k => if k = 3 then SEcs156543q.c1L else SEcs156543q.eeL
def wAllC1 : Nat → SEcs156543q.Letter := fun _ => SEcs156543q.c1L
def wC1UpTo2 : Nat → SEcs156543q.Letter := fun k => if k ≤ 2 then SEcs156543q.c1L else SEcs156543q.emptyL
def wP2At10 : Nat → SEcs156543q.Letter := fun k => if k = 10 then ⟨false, false, false, true⟩ else SEcs156543q.emptyL

theorem wEmpty_nc (j : Nat) : ¬SEcs156543q.Commit (wEmpty j) := by
  intro h; cases h with
  | inl h1 =>
    have h1' : SEcs156543q.emptyL.p1c = true := h1
    exact absurd h1' (by decide)
  | inr h2 =>
    have h2' : SEcs156543q.emptyL.p2c = true := h2
    exact absurd h2' (by decide)
theorem wReq_nc (j : Nat) : ¬SEcs156543q.Commit (wReq j) := by
  intro h; cases h with
  | inl h1 =>
    have h1' : SEcs156543q.eeL.p1c = true := h1
    exact absurd h1' (by decide)
  | inr h2 =>
    have h2' : SEcs156543q.eeL.p2c = true := h2
    exact absurd h2' (by decide)
theorem wCommitAt3_nc (j : Nat) (hj : j ≠ 3) : ¬SEcs156543q.Commit (wCommitAt3 j) := by
  intro h
  unfold wCommitAt3 at h
  rw [if_neg hj] at h
  cases h with
  | inl h1 =>
    have h1' : SEcs156543q.eeL.p1c = true := h1
    exact absurd h1' (by decide)
  | inr h2 =>
    have h2' : SEcs156543q.eeL.p2c = true := h2
    exact absurd h2' (by decide)
theorem wC1UpTo2_nc (j : Nat) (hj : ¬ j ≤ 2) : ¬SEcs156543q.Commit (wC1UpTo2 j) := by
  intro h
  unfold wC1UpTo2 at h
  rw [if_neg hj] at h
  cases h with
  | inl h1 =>
    have h1' : SEcs156543q.emptyL.p1c = true := h1
    exact absurd h1' (by decide)
  | inr h2 =>
    have h2' : SEcs156543q.emptyL.p2c = true := h2
    exact absurd h2' (by decide)

theorem agree_empty_0 : (SEcs156543q.extension_condition wEmpty 0 ↔ SEcs156543q.Ref.extension_condition wEmpty 0) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_true
  · first
    | (intro j hj hc; exact absurd hc (wEmpty_nc j))
    | (intro j hj; exact wEmpty_nc j)
    | (rintro ⟨j, hj, hc⟩; exact absurd hc (wEmpty_nc j))
    | (intro j hc hj; exact absurd hc (wEmpty_nc j))
    | (simp only [not_exists, not_and]; intro j hj hc; exact absurd hc (wEmpty_nc j))
  · intro j hj hc; exact absurd hc (wEmpty_nc j)
theorem agree_req_5 : (SEcs156543q.extension_condition wReq 5 ↔ SEcs156543q.Ref.extension_condition wReq 5) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_true
  · first
    | (intro j hj hc; exact absurd hc (wReq_nc j))
    | (intro j hj; exact wReq_nc j)
    | (rintro ⟨j, hj, hc⟩; exact absurd hc (wReq_nc j))
    | (intro j hc hj; exact absurd hc (wReq_nc j))
    | (simp only [not_exists, not_and]; intro j hj hc; exact absurd hc (wReq_nc j))
  · intro j hj hc; exact absurd hc (wReq_nc j)
theorem agree_commit3_5 : (SEcs156543q.extension_condition wCommitAt3 5 ↔ SEcs156543q.Ref.extension_condition wCommitAt3 5) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_true
  · first
    | (intro j hj hc; exact absurd hc (wCommitAt3_nc j (by omega)))
    | (intro j hj; exact wCommitAt3_nc j (by omega))
    | (rintro ⟨j, hj, hc⟩; exact absurd hc (wCommitAt3_nc j (by omega)))
    | (intro j hc hj; exact absurd hc (wCommitAt3_nc j (by omega)))
    | (simp only [not_exists, not_and]; intro j hj hc; exact absurd hc (wCommitAt3_nc j (by omega)))
  · intro j hj hc; exact absurd hc (wCommitAt3_nc j (by omega))
theorem agree_c1upto2_4 : (SEcs156543q.extension_condition wC1UpTo2 4 ↔ SEcs156543q.Ref.extension_condition wC1UpTo2 4) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_true
  · first
    | (intro j hj hc; exact absurd hc (wC1UpTo2_nc j (by omega)))
    | (intro j hj; exact wC1UpTo2_nc j (by omega))
    | (rintro ⟨j, hj, hc⟩; exact absurd hc (wC1UpTo2_nc j (by omega)))
    | (intro j hc hj; exact absurd hc (wC1UpTo2_nc j (by omega)))
    | (simp only [not_exists, not_and]; intro j hj hc; exact absurd hc (wC1UpTo2_nc j (by omega)))
  · intro j hj hc; exact absurd hc (wC1UpTo2_nc j (by omega))
theorem agree_empty_7 : (SEcs156543q.extension_condition wEmpty 7 ↔ SEcs156543q.Ref.extension_condition wEmpty 7) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_true
  · first
    | (intro j hj hc; exact absurd hc (wEmpty_nc j))
    | (intro j hj; exact wEmpty_nc j)
    | (rintro ⟨j, hj, hc⟩; exact absurd hc (wEmpty_nc j))
    | (intro j hc hj; exact absurd hc (wEmpty_nc j))
    | (simp only [not_exists, not_and]; intro j hj hc; exact absurd hc (wEmpty_nc j))
  · intro j hj hc; exact absurd hc (wEmpty_nc j)
theorem agree_commit1_0 : (SEcs156543q.extension_condition wCommitAt1 0 ↔ SEcs156543q.Ref.extension_condition wCommitAt1 0) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_false
  · first
    | (intro h; exact h 1 (by omega) (Or.inl rfl))
    | (intro h; exact h ⟨1, by omega, Or.inl rfl⟩)
    | (intro h; exact h 1 (Or.inl rfl) (by omega))
    | (intro h; exact (h 1 (by omega)) (Or.inl rfl))
  · intro h; exact h 1 (by omega) (Or.inl rfl)
theorem agree_commit3_0 : (SEcs156543q.extension_condition wCommitAt3 0 ↔ SEcs156543q.Ref.extension_condition wCommitAt3 0) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_false
  · first
    | (intro h; exact h 3 (by omega) (Or.inl rfl))
    | (intro h; exact h ⟨3, by omega, Or.inl rfl⟩)
    | (intro h; exact h 3 (Or.inl rfl) (by omega))
    | (intro h; exact (h 3 (by omega)) (Or.inl rfl))
  · intro h; exact h 3 (by omega) (Or.inl rfl)
theorem agree_allc1_2 : (SEcs156543q.extension_condition wAllC1 2 ↔ SEcs156543q.Ref.extension_condition wAllC1 2) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_false
  · first
    | (intro h; exact h 3 (by omega) (Or.inl rfl))
    | (intro h; exact h ⟨3, by omega, Or.inl rfl⟩)
    | (intro h; exact h 3 (Or.inl rfl) (by omega))
    | (intro h; exact (h 3 (by omega)) (Or.inl rfl))
  · intro h; exact h 3 (by omega) (Or.inl rfl)
theorem agree_p2at10_0 : (SEcs156543q.extension_condition wP2At10 0 ↔ SEcs156543q.Ref.extension_condition wP2At10 0) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_false
  · first
    | (intro h; exact h 10 (by omega) (Or.inr rfl))
    | (intro h; exact h ⟨10, by omega, Or.inr rfl⟩)
    | (intro h; exact h 10 (Or.inr rfl) (by omega))
    | (intro h; exact (h 10 (by omega)) (Or.inr rfl))
  · intro h; exact h 10 (by omega) (Or.inr rfl)
theorem agree_commit3_1 : (SEcs156543q.extension_condition wCommitAt3 1 ↔ SEcs156543q.Ref.extension_condition wCommitAt3 1) := by
  unfold SEcs156543q.extension_condition SEcs156543q.Ref.extension_condition
  apply iff_of_false
  · first
    | (intro h; exact h 3 (by omega) (Or.inl rfl))
    | (intro h; exact h ⟨3, by omega, Or.inl rfl⟩)
    | (intro h; exact h 3 (Or.inl rfl) (by omega))
    | (intro h; exact (h 3 (by omega)) (Or.inl rfl))
  · intro h; exact h 3 (by omega) (Or.inl rfl)
#print axioms agree_empty_0
#print axioms agree_req_5
#print axioms agree_commit3_5
#print axioms agree_c1upto2_4
#print axioms agree_empty_7
#print axioms agree_commit1_0
#print axioms agree_commit3_0
#print axioms agree_allc1_2
#print axioms agree_p2at10_0
#print axioms agree_commit3_1
