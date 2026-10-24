/-
Record SE_cs_156543__q (E04).  Core Lean 4 only (no Mathlib, no imports).

Source: two processes; letters record which of them request entry (`p1e`, `p2e`) and which
are in the critical section (`p1c`, `p2c`).  phi = (P1E & P2E) -> F (P1C | P2C), evaluated at
position i of an infinite word.
Source definition of a safety property (lines 0010-0012): `IsSafety`.
Source step (line 0016 of the question): with sigma, i |/= phi and sigma_hat = sigma[..i],
  EVERY infinite word sigma' that has sigma_hat as a prefix satisfies sigma', i |/= phi.
That step is the located statement `LocalClaim`, with the INCLUSIVE convention that
sigma_hat = sigma[..i] is the prefix of length i+1 (positions 0 .. i).
-/

namespace SEcs156543q

structure Letter where
  p1e : Bool
  p2e : Bool
  p1c : Bool
  p2c : Bool

def emptyL : Letter := ⟨false, false, false, false⟩

def eeL    : Letter := ⟨true,  true,  false, false⟩

def c1L    : Letter := ⟨false, false, true,  false⟩

def nthLetter : List Letter → Nat → Letter → Letter
  | [],      _,     d => d
  | a :: _,  0,     _ => a
  | _ :: as, k + 1, d => nthLetter as k d

def PhiInfinite (w : Nat → Letter) (i : Nat) : Prop :=
  ((w i).p1e = true ∧ (w i).p2e = true) →
    ∃ j : Nat, i ≤ j ∧ ((w j).p1c = true ∨ (w j).p2c = true)

/-- Both processes request entry. -/
def Request (a : Letter) : Prop := a.p1e = true ∧ a.p2e = true

/-- Some process is in its critical section (a "commit"). -/
def Commit (a : Letter) : Prop := a.p1c = true ∨ a.p2c = true

instance (a : Letter) : Decidable (Request a) :=
  inferInstanceAs (Decidable (a.p1e = true ∧ a.p2e = true))
instance (a : Letter) : Decidable (Commit a) :=
  inferInstanceAs (Decidable (a.p1c = true ∨ a.p2c = true))

/-- `u` and `v` have the same finite prefix of length `n` (positions `0 .. n-1`). -/
def AgreeUpTo (n : Nat) (u v : Nat → Letter) : Prop := ∀ k : Nat, k < n → u k = v k

/-- The full property `G phi`. -/
def GPhi (w : Nat → Letter) : Prop := ∀ i : Nat, PhiInfinite w i

/-- The source's step at line 0016, with `sigma_hat = sigma[..i]` the prefix of length `i+1`. -/
def LocalClaim : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → ¬PhiInfinite σ' i

/-- Source definition of a safety property (lines 0010-0012). -/
def IsSafety (P : (Nat → Letter) → Prop) : Prop :=
  ∀ σ : Nat → Letter, ¬P σ →
    ∃ n : Nat, ∀ σ' : Nat → Letter, AgreeUpTo n σ' σ → ¬P σ'

/-- Standard definition of a liveness property: every finite prefix extends into `P`. -/
def IsLiveness (P : (Nat → Letter) → Prop) : Prop :=
  ∀ (σ : Nat → Letter) (n : Nat), ∃ σ' : Nat → Letter, AgreeUpTo n σ' σ ∧ P σ'

end SEcs156543q
