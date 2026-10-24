import Mathlib.Data.Fin.Basic
import Mathlib.Data.Bool.Basic
set_option autoImplicit false

/-!
# Algorithms_12 (sol5) — in Gale–Shapley a woman CAN prefer a man who never proposed to her

The candidate solution asserts, about the men-proposing Gale–Shapley algorithm:

> "No woman would prefer a man who did not propose to her over her current (final)
>  partner."

This is false. Women in men-proposing GS receive the *pessimal* stable matching: a
woman can end up holding a man while strictly preferring another man who simply never
got around to proposing to her (because he was accepted elsewhere first).

**Concrete witness (`n = 2`).** Men `m1 = 0`, `m2 = 1`; women `w1 = 0`, `w2 = 1`.

* Both men rank `w2` above `w1` (`menRank · w2 = 0`, `menRank · w1 = 1`; lower = better);
* both women rank `m1` above `m2` (`womenRank · m1 = 0`, `womenRank · m2 = 1`).

A valid men-proposing GS run is the three-step trace

1. `m1` proposes to `w2` (his best); `w2` is free, so she **holds** `m1`;
2. `m2` proposes to `w2` (his best); `w2` prefers her current hold `m1`, so she
   **rejects** `m2`;
3. `m2` proposes to `w1` (his best remaining); `w1` is free, so she **holds** `m2`.

No free man remains, so the algorithm terminates with the matching
`{m1–w2, m2–w1}`. Now look at `w1`: her final partner is `m2`, the man `m1` **never
proposed to her** (his only proposal went to `w2`), and yet `w1` strictly prefers `m1`
to `m2`. This refutes the claim.

## Modeling choices

* Men, women are both `Fin 2`. Preferences are rank tables
  `menRank, womenRank : Fin 2 → Fin 2 → Nat` (lower rank = more preferred); strictness
  of the lists is certified by `prefs_strict_men` / `prefs_strict_women`.
* The run is the explicit list `trace : List (Fin 2 × Fin 2 × Bool)` of steps
  `(proposer, target, accepted)`. The execution state — `holdAt k : Fin 2 → Option (Fin 2)`
  (which man each woman currently holds) and `propAt k : Fin 2 → Fin 2 → Bool`
  (which proposals have been made) — is rebuilt from the trace prefix of length `k` by
  structural recursion on `Nat` (a fuel-indexed fold; no custom inductives).
* `stepValid k : Bool` checks every men-proposing GS rule at step `k`: the proposer is
  currently free, he has never proposed to the target before, the target is his
  best-ranked woman among those he has not yet proposed to, and the accept/reject bit
  matches the woman's decision (`accepts`: a free woman holds the proposer; a matched
  woman holds the better of {current hold, proposer}). `trace_length` pins the run to
  exactly three steps, `trace_follows_gs` certifies each of them, and `gs_terminated`
  certifies no man is left free, so the run is a complete GS execution.
* The claim is modeled faithfully as `Claim`: for every woman `w` with final partner
  `m'` and every man `m` who never proposed to `w`, `w` does not prefer `m` to `m'`
  ("prefer" = strictly smaller `womenRank`). The headline `claim_fails` refutes it at
  `w = w1`, `m = m1`, `m' = m2`.

**Decidability discipline.** Everything is `Bool`- and `Nat`-valued data over `Fin 2`; the
quantified facts range over `Fin 2`/`Fin 3` only, so every theorem is proved by plain
kernel `decide` (no `native_decide`, no `Finset`, no function-type enumeration), with
the final negation unpacked GT20-style.
-/

namespace ProofCerts.Alg12

/-- Men's preference ranks (lower = better): **both** men rank `w2 = 1` first and
`w1 = 0` second. -/
def menRank : Fin 2 → Fin 2 → Nat
  | _, 0 => 1   -- w1 is every man's second choice
  | _, 1 => 0   -- w2 is every man's first choice

/-- Women's preference ranks (lower = better): **both** women rank `m1 = 0` first and
`m2 = 1` second. -/
def womenRank : Fin 2 → Fin 2 → Nat
  | _, 0 => 0   -- m1 is every woman's first choice
  | _, 1 => 1   -- m2 is every woman's second choice

/-- The men-proposing Gale–Shapley run, as an explicit list of steps
`(proposer, target, accepted)`. -/
def steps : List (Fin 2 × Fin 2 × Bool) :=
  [(0, 1, true),    -- m1 → w2 : w2 is free, holds m1
   (1, 1, false),   -- m2 → w2 : w2 prefers her hold m1, rejects m2
   (1, 0, true)]    -- m2 → w1 : w1 is free, holds m2

/-- Hold-state update for one trace step `st = (m, w, accepted)`: if the proposal was
accepted, woman `w` now holds `m`; all other holds are unchanged. (In GS the rejected
suitor — if any — simply becomes free, which the `Option`-valued hold map captures.) -/
def updHold (h : Fin 2 → Option (Fin 2)) (st : Fin 2 × Fin 2 × Bool) :
    Fin 2 → Option (Fin 2) :=
  fun w => if st.2.2 && (st.2.1 == w) then some st.1 else h w

/-- Proposal-set update for one trace step `st = (m, w, _)`: record that `m` has now
proposed to `w` (accepted or not). -/
def updProp (p : Fin 2 → Fin 2 → Bool) (st : Fin 2 × Fin 2 × Bool) :
    Fin 2 → Fin 2 → Bool :=
  fun m w => p m w || (st.1 == m && st.2.1 == w)

/-- `holdAt k w` = the man woman `w` holds after the first `k` trace steps (`none` if
she is free). Fuel-indexed structural recursion on `k`; steps beyond the trace are
no-ops. -/
def holdAt : Nat → Fin 2 → Option (Fin 2)
  | 0 => fun _ => none
  | k + 1 =>
    match steps[k]? with
    | some st => updHold (holdAt k) st
    | none => holdAt k

/-- `propAt k m w` = `true` iff man `m` has proposed to woman `w` within the first `k`
trace steps. Fuel-indexed structural recursion on `k`. -/
def propAt : Nat → Fin 2 → Fin 2 → Bool
  | 0 => fun _ _ => false
  | k + 1 =>
    match steps[k]? with
    | some st => updProp (propAt k) st
    | none => propAt k

/-- The hold map after the whole run: each woman's **final partner**. -/
def finalHold : Fin 2 → Option (Fin 2) := holdAt steps.length

/-- `proposedTo m w` = `true` iff man `m` ever proposed to woman `w` during the run. -/
def proposedTo : Fin 2 → Fin 2 → Bool := propAt steps.length

/-- Man `m` is free in hold-state `h`: no woman currently holds him. -/
def freeB (h : Fin 2 → Option (Fin 2)) (m : Fin 2) : Bool :=
  !(h 0 == some m) && !(h 1 == some m)

/-- Woman `w`'s GS decision on a proposal from `m` in hold-state `h`: a free woman
accepts (holds the proposer); a matched woman accepts iff she strictly prefers `m` to
her current hold. -/
def accepts (h : Fin 2 → Option (Fin 2)) (w m : Fin 2) : Bool :=
  match h w with
  | none => true
  | some cur => Nat.blt (womenRank w m) (womenRank w cur)

/-- `w` is `m`'s best-ranked woman among those he has not yet proposed to (given the
proposal set `p`): for every woman `w'` not yet proposed to, `menRank m w ≤ menRank m w'`.
Spelled as an explicit `Bool` conjunction over the two women. -/
def bestRemaining (p : Fin 2 → Fin 2 → Bool) (m w : Fin 2) : Bool :=
  (p m 0 || Nat.ble (menRank m w) (menRank m 0)) &&
  (p m 1 || Nat.ble (menRank m w) (menRank m 1))

/-- Step `k` of the trace obeys every men-proposing GS rule: the proposer is free, he
never proposed to the target before, the target is his best not-yet-proposed woman, and
the recorded accept/reject bit equals the woman's decision. Out-of-range `k` is
vacuously valid. -/
def stepValid (k : Nat) : Bool :=
  match steps[k]? with
  | none => true
  | some (m, w, acc) =>
      freeB (holdAt k) m &&
      !(propAt k m w) &&
      bestRemaining (propAt k) m w &&
      (acc == accepts (holdAt k) w m)

/-- The men's preference lists are strict (the two ranks differ), as GS requires. -/
theorem prefs_strict_men : ∀ m : Fin 2, menRank m 0 ≠ menRank m 1 := by decide

/-- The women's preference lists are strict (the two ranks differ), as GS requires. -/
theorem prefs_strict_women : ∀ w : Fin 2, womenRank w 0 ≠ womenRank w 1 := by decide

/-- The run consists of exactly three steps, so the `Fin 3` quantification in
`trace_follows_gs` covers the **whole** trace. -/
theorem trace_length : steps.length = 3 := by decide

/-- **The trace is a valid men-proposing Gale–Shapley run**: each of its three steps
(`trace_length`) satisfies all of the GS rules checked by `stepValid`. -/
theorem trace_follows_gs : ∀ k : Fin 3, stepValid k.val = true := by decide

/-- **The run is complete**: after the trace no man is free, so men-proposing GS has
terminated with a perfect matching. -/
theorem gs_terminated : ∀ m : Fin 2, freeB finalHold m = false := by decide

/-- The final matching: `w1`'s partner is `m2`, and `w2`'s partner is `m1`. -/
theorem final_matching : finalHold 0 = some 1 ∧ finalHold 1 = some 0 := by decide

/-- `w1`'s final partner is `m2`. -/
theorem w1_final_partner : finalHold 0 = some 1 := by decide

/-- **`m1` never proposed to `w1`** during the entire run (his single proposal went to
`w2`, where he was held until termination). -/
theorem m1_never_proposed_to_w1 : proposedTo 0 0 = false := by decide

/-- **`w1` strictly prefers `m1` to her final partner `m2`** (rank `0 < 1`). -/
theorem w1_prefers_m1 : womenRank 0 0 < womenRank 0 1 := by decide

/-- The flawed claim, faithfully modeled on this instance: *"no woman would prefer a
man who did not propose to her over her current (final) partner"* — i.e. for every
woman `w` whose final partner is `m'` and every man `m` with `proposedTo m w = false`,
`w` does not rank `m` strictly better than `m'`. -/
def Claim : Prop :=
  ∀ w m m' : Fin 2, finalHold w = some m' → proposedTo m w = false →
    ¬ womenRank w m < womenRank w m'

/-- **Refutation.** The claim fails at `w = w1`, `m = m1`, `m' = m2`: `w1`'s final
partner is `m2` (`w1_final_partner`), `m1` never proposed to `w1`
(`m1_never_proposed_to_w1`), yet `w1` strictly prefers `m1` to `m2` (`w1_prefers_m1`). -/
theorem claim_fails : ¬ Claim := fun h =>
  h 0 0 1 w1_final_partner m1_never_proposed_to_w1 w1_prefers_m1

/-- **Bundled certificate (record `Algorithms_12__sol5`).** The trace is a genuine,
complete men-proposing GS run on strict preference lists (`trace_length`,
`trace_follows_gs`, `gs_terminated`) ending in the matching `{m1–w2, m2–w1}`;
nevertheless `w1`'s final partner is `m2`, `m1` never proposed to `w1`, and `w1`
strictly prefers `m1` — so the claim "no woman prefers a non-proposer to her final
partner" is false. -/
theorem woman_prefers_nonproposer :
    steps.length = 3 ∧
    (∀ k : Fin 3, stepValid k.val = true) ∧
    (∀ m : Fin 2, freeB finalHold m = false) ∧
    finalHold 0 = some 1 ∧
    proposedTo 0 0 = false ∧
    womenRank 0 0 < womenRank 0 1 ∧
    ¬ Claim :=
  ⟨trace_length, trace_follows_gs, gs_terminated, w1_final_partner,
   m1_never_proposed_to_w1, w1_prefers_m1, claim_fails⟩

end ProofCerts.Alg12

#print axioms ProofCerts.Alg12.woman_prefers_nonproposer
