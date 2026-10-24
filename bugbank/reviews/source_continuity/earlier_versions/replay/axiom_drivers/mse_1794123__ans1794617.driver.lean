/-!
# mse_1794123__ans1794617 — self-contained refutation certificate

* Record id : `mse_1794123__ans1794617`
* Question  : https://math.stackexchange.com/questions/1794123  (inferred from the record id)
* Answer    : https://math.stackexchange.com/a/1794617            (inferred from the record id)
* Route     : SELF_CONTAINED_LEAN (no `import`, no Mathlib; kernel `decide` only)
* Text licence: CC BY-SA (Stack Exchange).

## The claim being refuted

The refuted sentence asserts a general implication about a population of families.
Its logical content, as transcribed in the confirmed refutation record, is:

> If the per-family probability of having a boy is NOT the same for every family
> (heterogeneous boy-propensity), and family size is fixed in advance rather than
> adjusted in reaction to the sexes of the children already born (no "family planning"
> / gender-responsive stopping rule), then a uniformly random MAN has on average MORE
> brothers than a uniformly random WOMAN.

(The certificate formalises exactly that implication.  The literal wording of the
answer is in the record's `solution_text`; it is not reproduced here — see caveat C1.)

This is a finitely refutable statement: a witness is a finite mixture of family types
with rational sizes, boy-probabilities and population weights, and both conditional
expectations are then rational and exactly computable.

## Witness

A two-type population, all data rational, family size a static attribute of the type:

    Type A : n = 2 children, boy-probability p_A = 3/4, population weight 1/2
    Type B : n = 3 children, boy-probability p_B = 1/2, population weight 1/2

Every hypothesis of the claim holds: the boy-probability is heterogeneous (3/4 ≠ 1/2),
both probabilities are strictly interior (0 < p < 1), and the number of children is a
constant of the type — the children's sexes are i.i.d. Bernoulli(p) given the type, so
no stopping rule can react to a realised sex.

Exact values (recomputed below by kernel evaluation, both by brute-force enumeration of
all 2^n sex sequences and by the closed form; the two are proved equal):

    E[K(K-1)] = 21/16 ,  E[K]   = 3/2 ,  brothers | random MAN   = 7/8  = 14/16
    E[K(N-K)] = 15/16 ,  E[N-K] = 1   ,  brothers | random WOMAN = 15/16

So the man's average is STRICTLY SMALLER than the woman's, by exactly 1/16 — the
opposite of the asserted inequality.

Two supplementary witnesses (both with a degenerate p = 1 type, hence certified under
the weaker predicate `refutesClaimBasic`, which does not demand interior p):

    W2 : {n=1, p=1, w=1/2} + {n=2, p=1/2, w=1/2}   → men 1/4  < women 1/2
    W3 : {n=1, p=1, w=7/8} + {n=6, p=7/8, w=1/8}   → men 15/8 < women 35/8

## Mechanism (why the claim's reasoning breaks)

Inside one family type BOTH a boy and a girl expect (n-1)p brothers.  The two population
averages are the SAME numbers (n_i - 1) p_i, only reweighted: by n_i p_i w_i for men and
by n_i (1 - p_i) w_i for women.  Heterogeneity in p only guarantees that the male
reweighting tilts toward high-p families; that helps men only if (n-1)p is increasing in
p, which requires family SIZE to carry no information about propensity.  In the witness
the low-p type is the LARGER one, so (n-1)p is decreasing in p (3/4 at p = 3/4 versus 1
at p = 1/2), and the male size-bias points at the families with fewer brothers.

## Modelling judgments (the kernel checks the arithmetic, not the faithfulness of these)

1. **Population model.** A population is a finite list of family *types*; each type
   carries a fixed number of children `kids`, a rational boy-probability `pn/pd`, and a
   rational population weight `wn/wd` (weights are required to sum to exactly 1).
   This is the standard finite-mixture reading of "the probability of a boy varies from
   family to family".
2. **No stopping rule — and it is CHECKED, not merely asserted.**  `iidB` is conjoined
   into well-formedness and verifies three things per type: every enumerated sex sequence
   has length exactly `kids` (family size is a constant, not a function of the realised
   sexes); the sequence probabilities sum to exactly 1 (a genuine probability measure on
   the full sex space, so no sequence is truncated away by a stopping rule); and every
   sequence's probability equals the canonical `p^k (1-p)^(n-k)`, so the measure is
   EXCHANGEABLE (two sequences with the same number of boys are equiprobable) — precisely
   what a gender-responsive rule would destroy.
3. **"Average number of brothers of a uniformly random man"** is read as
   (expected total number of brother-relationships seen by men) / (expected number of
   men) = E[K(K-1)]/E[K] — the size-biased average over men, which is what "pick a man
   uniformly at random from the population" means.  Symmetrically for women:
   E[K(N-K)]/E[N-K].  Both denominators are required to be strictly positive by `wfPop`,
   so no conditional expectation is ever formed 0/0.
4. **Brothers are counted person-by-person, not by a formula.**  The primary averages
   `menAvg`/`womenAvg` are defined by enumerating all 2^n sex sequences of each type with
   their exact rational probabilities and, for each individual position in each sequence,
   counting the boys at the OTHER positions (`boysExcept`).  The closed form
   E[K(K-1)]/E[K] appears only as a separate definition, and the file proves the two
   agree on every witness (`*_enum_eq_closed`).  A slip in the closed form therefore
   cannot produce the refutation.
5. **Exact rational arithmetic, no floats.**  `Q` is a non-negative rational as a pair of
   `Nat`s, normalised by an explicitly fuelled Euclid (`gcdFuel`, structurally recursive,
   kernel-reducible — core `Nat.gcd` is deliberately avoided).  Comparison and equality
   are by cross-multiplication and are only used on `qvalid` (positive-denominator)
   values; a zero denominator anywhere propagates to the invalid value `⟨0,0⟩`, which
   fails `qvalid` and makes every refutation predicate FALSE.  Fail-closed throughout.
6. **Only 1 - p uses truncated `Nat` subtraction**, and `wfType` requires `pn ≤ pd`, so
   the truncation is never reached on a well-formed type.
7. Everything is discharged by kernel `decide`.  No `native_decide`, no `axiom`,
   no `sorry`, no well-founded recursion.
-/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace MSE_1794123

/-! ## §0. Tiny list utilities (self-contained; no core `List` API relied upon) -/

def lmap {α β : Type} (f : α → β) : List α → List β
  | [] => []
  | a :: r => f a :: lmap f r

def lapp {α : Type} : List α → List α → List α
  | [], m => m
  | a :: r, m => a :: lapp r m

def joinL {α : Type} : List (List α) → List α
  | [] => []
  | l :: ls => lapp l (joinL ls)

def llen {α : Type} : List α → Nat
  | [] => 0
  | _ :: r => 1 + llen r

def allB {α : Type} (p : α → Bool) : List α → Bool
  | [] => true
  | a :: r => p a && allB p r

def anyB {α : Type} (p : α → Bool) : List α → Bool
  | [] => false
  | a :: r => p a || anyB p r

def sumN : List Nat → Nat
  | [] => 0
  | a :: r => a + sumN r

def upto : Nat → List Nat
  | 0 => []
  | k + 1 => lapp (upto k) [k]

/-- All ordered pairs from a list (used for "some two types differ" and for the
exchangeability check). -/
def pairsOf {α : Type} (l : List α) : List (α × α) :=
  joinL (lmap (fun a => lmap (fun b => (a, b)) l) l)

/-- `i`-th entry of a `Bool` list; out of range = `false`.  Indices always come from
`upto (llen s)`, so the default is never reached. -/
def getBool : List Bool → Nat → Bool
  | [], _ => false
  | b :: _, 0 => b
  | _ :: r, k + 1 => getBool r k

/-! ## §1. Exact non-negative rationals

`Q` is `nm / dn` with `nm dn : Nat`.  A value is VALID iff `dn > 0`; `⟨0,0⟩` is the
distinguished invalid value produced by any division by zero, and it propagates through
every operation.  No float is created anywhere in this file. -/

structure Q where
  nm : Nat
  dn : Nat

/-- Euclid's algorithm with explicit fuel — structurally recursive, hence kernel
reducible (core `Nat.gcd` is defined by well-founded recursion and is avoided). -/
def gcdFuel : Nat → Nat → Nat → Nat
  | 0, a, _ => a
  | f + 1, a, b =>
      match b with
      | 0 => a
      | _ => gcdFuel f b (a % b)

/-- Division by the computed gcd (`g = 0` only if the input was invalid). -/
def qmkAux (g a b : Nat) : Q :=
  match g with
  | 0 => ⟨0, 0⟩
  | _ => ⟨a / g, b / g⟩

/-- Smart constructor: reduces `a/b` to lowest terms; `b = 0` yields the invalid `⟨0,0⟩`. -/
def qmk (a b : Nat) : Q :=
  match b with
  | 0 => ⟨0, 0⟩
  | _ => qmkAux (gcdFuel (a + b + 1) a b) a b

def qzero : Q := ⟨0, 1⟩
def qone  : Q := ⟨1, 1⟩
def qNat (k : Nat) : Q := ⟨k, 1⟩

/-- `dn > 0`: the value denotes an actual rational number. -/
def qvalid (a : Q) : Bool := Nat.blt 0 a.dn
/-- Valid and strictly positive. -/
def qpos (a : Q) : Bool := Nat.blt 0 a.dn && Nat.blt 0 a.nm

def qadd (a b : Q) : Q := qmk (a.nm * b.dn + b.nm * a.dn) (a.dn * b.dn)
def qmul (a b : Q) : Q := qmk (a.nm * b.nm) (a.dn * b.dn)
/-- Truncated difference; only used after a strict `qlt` has established `b < a`. -/
def qsub (a b : Q) : Q := qmk (a.nm * b.dn - b.nm * a.dn) (a.dn * b.dn)
/-- Division; a zero numerator in `b` gives the invalid `⟨0,0⟩` (fail-closed). -/
def qdiv (a b : Q) : Q := qmk (a.nm * b.dn) (a.dn * b.nm)

/-- Strict order by cross-multiplication; `false` unless both sides are valid. -/
def qlt (a b : Q) : Bool :=
  qvalid a && qvalid b && Nat.blt (a.nm * b.dn) (b.nm * a.dn)
/-- Equality by cross-multiplication; `false` unless both sides are valid. -/
def qeqB (a b : Q) : Bool :=
  qvalid a && qvalid b && Nat.beq (a.nm * b.dn) (b.nm * a.dn)
/-- Provably different rationals (both sides must be valid). -/
def qneB (a b : Q) : Bool :=
  qvalid a && qvalid b && !(Nat.beq (a.nm * b.dn) (b.nm * a.dn))

def qsum : List Q → Q
  | [] => qzero
  | a :: r => qadd a (qsum r)

/-! ## §2. Populations

A family TYPE has a number of children fixed in advance, a rational boy-probability and
a rational population weight.  A POPULATION is a finite list of types. -/

structure FamilyType where
  /-- number of children — a static attribute of the type, fixed before any birth -/
  kids : Nat
  /-- boy-probability numerator / denominator -/
  pn : Nat
  pd : Nat
  /-- population weight numerator / denominator -/
  wn : Nat
  wd : Nat

abbrev Pop := List FamilyType

/-- P(boy) for this type. -/
def pOf (t : FamilyType) : Q := qmk t.pn t.pd
/-- P(girl) = 1 - p for this type (`wfType` guarantees `pn ≤ pd`). -/
def gOf (t : FamilyType) : Q := qmk (t.pd - t.pn) t.pd
/-- Population weight of this type. -/
def wOf (t : FamilyType) : Q := qmk t.wn t.wd

/-! ## §3. Brute-force enumeration of sex sequences

`true` = boy, `false` = girl.  `seqsOf n` lists all `2^n` sequences of length `n`; the
length does not depend on the sexes drawn, which is exactly "family size is fixed in
advance". -/

def seqsOf : Nat → List (List Bool)
  | 0 => [[]]
  | k + 1 => joinL (lmap (fun s => [true :: s, false :: s]) (seqsOf k))

/-- Probability of one sex sequence under the i.i.d. Bernoulli(p) product measure:
a product of per-child factors, each depending only on that child's own sex. -/
def seqProb (t : FamilyType) : List Bool → Q
  | [] => qone
  | b :: r =>
      qmul (match b with | true => pOf t | false => gOf t) (seqProb t r)

def boyCount : List Bool → Nat
  | [] => 0
  | b :: r => (match b with | true => 1 | false => 0) + boyCount r

def qpow (a : Q) : Nat → Q
  | 0 => qone
  | k + 1 => qmul a (qpow a k)

/-- The i.i.d. Bernoulli(p) probability that a family of this type produces exactly `k`
boys in a PRESCRIBED order: `p^k (1-p)^(n-k)`.  It depends on the sex sequence only
through its boy-count — that is exchangeability, and it is what `iidTypeB` verifies
`seqProb` actually equals. -/
def canonProb (t : FamilyType) (k : Nat) : Q :=
  qmul (qpow (pOf t) k) (qpow (gOf t) (t.kids - k))

/-- Number of boys among the positions OTHER than `i` — i.e. the number of brothers of
the individual sitting at position `i`, counted person by person. -/
def boysExcept (s : List Bool) (i : Nat) : Nat :=
  sumN (lmap (fun j =>
      match Nat.beq j i with
      | true => 0
      | false => match getBool s j with | true => 1 | false => 0)
    (upto (llen s)))

/-- Total brothers summed over the MEN of this family. -/
def menBrothersSeq (s : List Bool) : Nat :=
  sumN (lmap (fun i =>
      match getBool s i with
      | true => boysExcept s i
      | false => 0)
    (upto (llen s)))

/-- Number of men in this family. -/
def menCountSeq (s : List Bool) : Nat :=
  sumN (lmap (fun i =>
      match getBool s i with | true => 1 | false => 0) (upto (llen s)))

/-- Total brothers summed over the WOMEN of this family. -/
def womenBrothersSeq (s : List Bool) : Nat :=
  sumN (lmap (fun i =>
      match getBool s i with
      | true => 0
      | false => boysExcept s i)
    (upto (llen s)))

/-- Number of women in this family. -/
def womenCountSeq (s : List Bool) : Nat :=
  sumN (lmap (fun i =>
      match getBool s i with | true => 0 | false => 1) (upto (llen s)))

/-- Expectation over one type of a per-sequence `Nat` statistic. -/
def typeExp (t : FamilyType) (f : List Bool → Nat) : Q :=
  qsum (lmap (fun s => qmul (seqProb t s) (qNat (f s))) (seqsOf t.kids))

/-- Population expectation of a per-sequence statistic (weighted by `wOf`). -/
def popExp (P : Pop) (f : List Bool → Nat) : Q :=
  qsum (lmap (fun t => qmul (wOf t) (typeExp t f)) P)

/-- Expected total brother-relationships seen by men (enumerated). -/
def menNum (P : Pop) : Q := popExp P menBrothersSeq
/-- Expected number of men (enumerated). -/
def menDen (P : Pop) : Q := popExp P menCountSeq
/-- Expected total brothers seen by women (enumerated). -/
def womenNum (P : Pop) : Q := popExp P womenBrothersSeq
/-- Expected number of women (enumerated). -/
def womenDen (P : Pop) : Q := popExp P womenCountSeq

/-- **Average number of brothers of a uniformly random MAN** (primary definition:
brute-force enumeration, person-by-person counting). -/
def menAvg (P : Pop) : Q := qdiv (menNum P) (menDen P)
/-- **Average number of brothers of a uniformly random WOMAN** (same, for women). -/
def womenAvg (P : Pop) : Q := qdiv (womenNum P) (womenDen P)

/-! ## §4. Closed form (independent recomputation)

E[K(K-1)] = Σ w n(n-1)p² , E[K] = Σ w n p ,
E[K(N-K)] = Σ w n(n-1)p(1-p) , E[N-K] = Σ w n (1-p).
Used only as a CHECK against §3; the refutation itself never depends on it. -/

def cfMenNum (P : Pop) : Q :=
  qsum (lmap (fun t =>
    qmul (wOf t) (qmul (qNat (t.kids * (t.kids - 1))) (qmul (pOf t) (pOf t)))) P)

def cfMenDen (P : Pop) : Q :=
  qsum (lmap (fun t => qmul (wOf t) (qmul (qNat t.kids) (pOf t))) P)

def cfWomenNum (P : Pop) : Q :=
  qsum (lmap (fun t =>
    qmul (wOf t) (qmul (qNat (t.kids * (t.kids - 1))) (qmul (pOf t) (gOf t)))) P)

def cfWomenDen (P : Pop) : Q :=
  qsum (lmap (fun t => qmul (wOf t) (qmul (qNat t.kids) (gOf t))) P)

def cfMenAvg (P : Pop) : Q := qdiv (cfMenNum P) (cfMenDen P)
def cfWomenAvg (P : Pop) : Q := qdiv (cfWomenNum P) (cfWomenDen P)

/-- The enumeration and the closed form agree on this population. -/
def enumMatchesClosedB (P : Pop) : Bool :=
  qeqB (menNum P) (cfMenNum P)
    && qeqB (menDen P) (cfMenDen P)
    && qeqB (womenNum P) (cfWomenNum P)
    && qeqB (womenDen P) (cfWomenDen P)
    && qeqB (menAvg P) (cfMenAvg P)
    && qeqB (womenAvg P) (cfWomenAvg P)

/-! ## §5. Hypotheses of the claim, as decidable predicates -/

/-- The sex process of a type is a genuine i.i.d. product measure with a family size
fixed in advance.  This is the formal content of "no family planning / no stopping rule
reacting to the realised sexes":
  * every sequence has length exactly `kids` (size is not a function of the sexes);
  * the sequence probabilities sum to exactly 1 (nothing is truncated away);
  * the measure is EXCHANGEABLE — every sequence's probability equals the canonical
    `p^k (1-p)^(n-k)`, so any two sequences with the same boy-count are equiprobable,
    which a gender-responsive stopping rule would violate. -/
def iidTypeB (t : FamilyType) : Bool :=
  allB (fun s => Nat.beq (llen s) t.kids) (seqsOf t.kids)
    && qeqB (qsum (lmap (seqProb t) (seqsOf t.kids))) qone
    && allB (fun s => qeqB (seqProb t s) (canonProb t (boyCount s))) (seqsOf t.kids)

def iidB (P : Pop) : Bool := allB iidTypeB P

/-- A type is well formed: at least one child, genuine rational data, `p ∈ [0,1]`,
strictly positive weight. -/
def wfType (t : FamilyType) : Bool :=
  Nat.blt 0 t.kids
    && Nat.blt 0 t.pd && Nat.ble t.pn t.pd
    && Nat.blt 0 t.wn && Nat.blt 0 t.wd

/-- Well-formed population: non-empty, well-formed types, weights summing to exactly 1,
an i.i.d. static-size sex process, and both conditional expectations defined (strictly
positive expected numbers of men and of women, and valid averages). -/
def wfPop (P : Pop) : Bool :=
  Nat.blt 0 (llen P)
    && allB wfType P
    && qeqB (qsum (lmap wOf P)) qone
    && iidB P
    && qpos (menDen P) && qpos (womenDen P)
    && qvalid (menAvg P) && qvalid (womenAvg P)

/-- HYPOTHESIS: the boy-probability is heterogeneous — some two types differ in `p`. -/
def heteroPB (P : Pop) : Bool :=
  anyB (fun (pr : FamilyType × FamilyType) => qneB (pOf pr.1) (pOf pr.2)) (pairsOf P)

/-- Optional strengthening: every boy-probability is strictly interior, `0 < p < 1`
(so the witness cannot be dismissed as a degenerate all-boy / all-girl family). -/
def interiorPB (P : Pop) : Bool :=
  allB (fun t => Nat.blt 0 t.pn && Nat.blt t.pn t.pd) P

/-- CONCLUSION asserted by the claim: a random man has strictly more brothers than a
random woman. -/
def claimConclusion (P : Pop) : Bool := qlt (womenAvg P) (menAvg P)

/-- **Refutation predicate (strict form).**  True exactly when the population satisfies
every hypothesis of the claim — well formed, no stopping rule, heterogeneous and strictly
interior boy-probability — the asserted conclusion FAILS, and in fact the inequality is
strictly REVERSED. -/
def refutesClaim (P : Pop) : Bool :=
  wfPop P
    && heteroPB P
    && interiorPB P
    && !(claimConclusion P)
    && qlt (menAvg P) (womenAvg P)

/-- Same, without the interiority strengthening (used for the two supplementary
witnesses, which contain a degenerate `p = 1` type). -/
def refutesClaimBasic (P : Pop) : Bool :=
  wfPop P
    && heteroPB P
    && !(claimConclusion P)
    && qlt (menAvg P) (womenAvg P)

/-! ## §6. Witnesses -/

/-- **Primary witness.**  Type A: 2 children, p = 3/4, weight 1/2.
Type B: 3 children, p = 1/2, weight 1/2. -/
def W1 : Pop :=
  [ { kids := 2, pn := 3, pd := 4, wn := 1, wd := 2 },
    { kids := 3, pn := 1, pd := 2, wn := 1, wd := 2 } ]

/-- Supplementary witness (simplest): {n=1, p=1, w=1/2} + {n=2, p=1/2, w=1/2}. -/
def W2 : Pop :=
  [ { kids := 1, pn := 1, pd := 1, wn := 1, wd := 2 },
    { kids := 2, pn := 1, pd := 2, wn := 1, wd := 2 } ]

/-- Supplementary witness (largest gap found): {n=1, p=1, w=7/8} + {n=6, p=7/8, w=1/8}. -/
def W3 : Pop :=
  [ { kids := 1, pn := 1, pd := 1, wn := 7, wd := 8 },
    { kids := 6, pn := 7, pd := 8, wn := 1, wd := 8 } ]

/-- CONTROL C1a: a homogeneous population (3 children, p = 1/2).  The claim's
hypothesis of heterogeneity FAILS here; this is the classical "no difference" case. -/
def H1 : Pop := [ { kids := 3, pn := 1, pd := 2, wn := 1, wd := 1 } ]

/-- CONTROL C1b: another homogeneous population (4 children, p = 2/3). -/
def H2 : Pop := [ { kids := 4, pn := 2, pd := 3, wn := 1, wd := 1 } ]

/-- CONTROL C2: an EQUAL-SIZE heterogeneous mixture (both types have 3 children, so
family size carries no information about propensity).  Here the answer's conclusion is
CORRECT: men 13/10 > women 7/6. -/
def E1 : Pop :=
  [ { kids := 3, pn := 3, pd := 4, wn := 1, wd := 2 },
    { kids := 3, pn := 1, pd := 2, wn := 1, wd := 2 } ]

/-- CONTROL C3: a malformed population whose weights sum to 3/4, not 1. -/
def BAD : Pop :=
  [ { kids := 2, pn := 3, pd := 4, wn := 1, wd := 2 },
    { kids := 3, pn := 1, pd := 2, wn := 1, wd := 4 } ]

/-! ## §7. The witness really satisfies every hypothesis -/

theorem W1_wf : wfPop W1 = true := by decide

/-- The boy-probability is heterogeneous (3/4 ≠ 1/2) — the claim's stated hypothesis. -/
theorem W1_heterogeneous : heteroPB W1 = true := by decide

/-- Both boy-probabilities are strictly interior: no degenerate all-boy family. -/
theorem W1_interior : interiorPB W1 = true := by decide

/-- Family size is static and the sex process is an exchangeable i.i.d. product measure
of total mass 1 — i.e. there is NO gender-responsive stopping rule, which is exactly the
mechanism the claim explicitly excludes. -/
theorem W1_no_stopping_rule : iidB W1 = true := by decide

/-! ## §8. The exact numbers -/

/-- E[K(K-1)] = 21/16 and E[K] = 3/2, computed by enumeration. -/
theorem W1_men_moments :
    (qeqB (menNum W1) (qmk 21 16) && qeqB (menDen W1) (qmk 3 2)) = true := by decide

/-- E[K(N-K)] = 15/16 and E[N-K] = 1, computed by enumeration. -/
theorem W1_women_moments :
    (qeqB (womenNum W1) (qmk 15 16) && qeqB (womenDen W1) (qmk 1 1)) = true := by decide

/-- A uniformly random MAN has on average 7/8 = 14/16 brothers. -/
theorem W1_men_avg : qeqB (menAvg W1) (qmk 7 8) = true := by decide

/-- A uniformly random WOMAN has on average 15/16 brothers. -/
theorem W1_women_avg : qeqB (womenAvg W1) (qmk 15 16) = true := by decide

/-- The deficit is exactly 1/16. -/
theorem W1_gap : qeqB (qsub (womenAvg W1) (menAvg W1)) (qmk 1 16) = true := by decide

/-- The person-by-person enumeration and the closed form E[K(K-1)]/E[K],
E[K(N-K)]/E[N-K] agree EXACTLY on the witness, so the refutation does not rest on
either derivation alone. -/
theorem W1_enum_eq_closed : enumMatchesClosedB W1 = true := by decide

/-! ## §9. MAIN RESULT

Every hypothesis of the claim holds on `W1`, yet a random man has FEWER brothers than a
random woman.  The asserted implication is therefore false. -/

theorem W1_conclusion_fails : claimConclusion W1 = false := by decide

theorem W1_inequality_reversed : qlt (menAvg W1) (womenAvg W1) = true := by decide

/-- **THE REFUTATION.** -/
theorem refuted_W1 : refutesClaim W1 = true := by decide

/-! ## §10. Supplementary witnesses

Both contain a degenerate `p = 1` type, so they are certified under the weaker predicate
`refutesClaimBasic`; nothing in §9 depends on them. -/

theorem W2_values :
    (qeqB (menAvg W2) (qmk 1 4) && qeqB (womenAvg W2) (qmk 1 2)) = true := by decide

theorem refuted_W2 : refutesClaimBasic W2 = true := by decide

theorem W2_enum_eq_closed : enumMatchesClosedB W2 = true := by decide

theorem W3_values :
    (qeqB (menAvg W3) (qmk 15 8) && qeqB (womenAvg W3) (qmk 35 8)) = true := by decide

theorem refuted_W3 : refutesClaimBasic W3 = true := by decide

theorem W3_enum_eq_closed : enumMatchesClosedB W3 = true := by decide

/-- `W3` is not interior (its first type has p = 1), which is why it is only claimed
under the basic predicate.  Stating this keeps the scope of each witness explicit. -/
theorem W3_not_interior : interiorPB W3 = false := by decide

/-! ## §11. NEGATIVE CONTROLS

If the modelling were vacuous — a brother-counter that always returned 0, a `qlt` that
fired on everything, an `iidB`/`wfPop` that accepted anything, or a population model in
which the two averages could never be equal — these would fail and the file would not
compile. -/

/-- NC1. HOMOGENEOUS BASELINE.  With a single family type the two averages are EXACTLY
equal (the classical "no difference" result the answer is arguing against), and both
equal (n-1)p: 1 for `H1` (n=3, p=1/2) and 2 for `H2` (n=4, p=2/3).  So the machinery is
not manufacturing a difference out of thin air. -/
theorem nc1_homogeneous_H1 :
    (wfPop H1 && iidB H1
      && qeqB (menAvg H1) (womenAvg H1)
      && qeqB (menAvg H1) (qmk 1 1)) = true := by decide

theorem nc1_homogeneous_H2 :
    (wfPop H2 && iidB H2
      && qeqB (menAvg H2) (womenAvg H2)
      && qeqB (menAvg H2) (qmk 2 1)) = true := by decide

/-- NC2. The refutation predicate REFUSES the homogeneous populations — both because the
heterogeneity hypothesis fails and because there is no reversal.  If it fired on
everything, this would fail. -/
theorem nc2_no_refutation_homogeneous :
    (refutesClaim H1 || refutesClaimBasic H1
      || refutesClaim H2 || refutesClaimBasic H2) = false := by decide

theorem nc2_hetero_has_teeth : (heteroPB H1 || heteroPB H2) = false := by decide

/-- NC3. EQUAL-SIZE CONTROL — the diagnosis, not a modelling slip.  On a heterogeneous
mixture in which family size carries no information about propensity (both types have 3
children), the answer's conclusion is CORRECT: men 13/10 > women 7/6.  The gap flagged by
this certificate is therefore precisely the missing hypothesis "family size uncorrelated
with boy-propensity", not an error in the model. -/
theorem nc3_equal_size_claim_holds :
    (wfPop E1 && heteroPB E1 && interiorPB E1
      && claimConclusion E1
      && qeqB (menAvg E1) (qmk 13 10)
      && qeqB (womenAvg E1) (qmk 7 6)) = true := by decide

/-- NC4. Consequently the refutation predicate also refuses the equal-size mixture, even
though it is heterogeneous and interior.  Heterogeneity alone is not what the certificate
is exploiting. -/
theorem nc4_equal_size_not_certified :
    (refutesClaim E1 || refutesClaimBasic E1) = false := by decide

/-- NC5. Well-formedness has teeth: a population whose weights sum to 3/4 is rejected,
and cannot certify anything. -/
theorem nc5_wf_has_teeth :
    (wfPop BAD || refutesClaim BAD || refutesClaimBasic BAD) = false := by decide

/-- NC6. The brother-counter is not identically zero and counts person-by-person:
in a 3-child family BBG the two boys have 1 brother each (total 2) and the girl has 2;
in BBB the total over men is 3·2 = 6 and there are no women. -/
theorem nc6_counter_nontrivial :
    (Nat.beq (menBrothersSeq [true, true, false]) 2
      && Nat.beq (menCountSeq [true, true, false]) 2
      && Nat.beq (womenBrothersSeq [true, true, false]) 2
      && Nat.beq (womenCountSeq [true, true, false]) 1
      && Nat.beq (menBrothersSeq [true, true, true]) 6
      && Nat.beq (womenCountSeq [true, true, true]) 0
      && Nat.beq (boysExcept [true, false, true] 0) 1) = true := by decide

/-- NC7. The enumeration is complete: `2^n` sequences of the right length, and their
probabilities really sum to 1 under the witness's own parameters. -/
theorem nc7_enumeration_complete :
    (Nat.beq (llen (seqsOf 3)) 8
      && Nat.beq (llen (seqsOf 6)) 64
      && allB (fun s => Nat.beq (llen s) 3) (seqsOf 3)
      && qeqB (qsum (lmap (seqProb { kids := 3, pn := 3, pd := 4, wn := 1, wd := 1 })
                (seqsOf 3))) qone) = true := by decide

/-- NC8. The rational arithmetic discriminates: `qlt` is neither constantly true nor
constantly false, `qeqB` recognises unreduced equals and rejects genuine unequals, and
`qmk` really normalises (14/16 ↦ 7/8). -/
theorem nc8_arithmetic_discriminates :
    (qlt (qmk 7 8) (qmk 15 16)
      && !(qlt (qmk 15 16) (qmk 7 8))
      && !(qlt (qmk 7 8) (qmk 14 16))
      && qeqB (qmk 7 8) (qmk 14 16)
      && !(qeqB (qmk 7 8) (qmk 15 16))
      && Nat.beq (qmk 14 16).nm 7 && Nat.beq (qmk 14 16).dn 8
      && Nat.beq (qmk 30 12).nm 5 && Nat.beq (qmk 30 12).dn 2) = true := by decide

/-- NC9. Fail-closed arithmetic: a zero denominator produces the invalid value, which is
neither valid nor comparable, so it can never certify a refutation. -/
theorem nc9_fail_closed :
    (!(qvalid (qmk 1 0))
      && !(qvalid (qdiv (qmk 1 2) qzero))
      && !(qlt (qmk 1 0) (qmk 1 1))
      && !(qeqB (qmk 1 0) qone)
      && !(qvalid (qadd (qmk 1 0) (qmk 1 2)))) = true := by decide

/-- NC10. The exchangeability test that stands in for "no gender-responsive stopping
rule" is not vacuous: under the witness's own type A (2 children, p = 3/4) the sequences
BG and GB are EQUIPROBABLE (3/4·1/4 = 1/4·3/4 = 3/16), while BB and BG — different
boy-counts — are NOT.  So `seqProb` is a genuinely non-constant measure and the check
`seqProb = canonProb ∘ boyCount` has content rather than holding by degeneracy. -/
theorem nc10_exchangeability_nonvacuous :
    (qeqB (seqProb { kids := 2, pn := 3, pd := 4, wn := 1, wd := 2 } [true, false])
          (qmk 3 16)
      && qeqB (seqProb { kids := 2, pn := 3, pd := 4, wn := 1, wd := 2 } [false, true])
              (qmk 3 16)
      && !(qeqB (seqProb { kids := 2, pn := 3, pd := 4, wn := 1, wd := 2 } [true, true])
                (seqProb { kids := 2, pn := 3, pd := 4, wn := 1, wd := 2 } [true, false]))
      && qeqB (canonProb { kids := 2, pn := 3, pd := 4, wn := 1, wd := 2 } 2) (qmk 9 16))
      = true := by decide

/-- NC11. The claim's conclusion is expressible and CAN be true in this model — it holds
on `E1` (NC3) — so `claimConclusion` is not a predicate that is false by construction.
Together with NC1 (equality) and §9 (reversal) all three orderings are realised, which
is only possible if the model has genuine resolution. -/
theorem nc11_all_three_orderings_realised :
    (claimConclusion E1
      && qeqB (menAvg H1) (womenAvg H1)
      && qlt (menAvg W1) (womenAvg W1)) = true := by decide

end MSE_1794123

#print axioms MSE_1794123.W1_wf
#print axioms MSE_1794123.W1_heterogeneous
#print axioms MSE_1794123.W1_interior
#print axioms MSE_1794123.W1_no_stopping_rule
#print axioms MSE_1794123.W1_men_moments
#print axioms MSE_1794123.W1_women_moments
#print axioms MSE_1794123.W1_men_avg
#print axioms MSE_1794123.W1_women_avg
#print axioms MSE_1794123.W1_gap
#print axioms MSE_1794123.W1_enum_eq_closed
#print axioms MSE_1794123.W1_conclusion_fails
#print axioms MSE_1794123.W1_inequality_reversed
#print axioms MSE_1794123.refuted_W1
#print axioms MSE_1794123.W2_values
#print axioms MSE_1794123.refuted_W2
#print axioms MSE_1794123.W2_enum_eq_closed
#print axioms MSE_1794123.W3_values
#print axioms MSE_1794123.refuted_W3
#print axioms MSE_1794123.W3_enum_eq_closed
#print axioms MSE_1794123.W3_not_interior
#print axioms MSE_1794123.nc1_homogeneous_H1
#print axioms MSE_1794123.nc1_homogeneous_H2
#print axioms MSE_1794123.nc2_no_refutation_homogeneous
#print axioms MSE_1794123.nc2_hetero_has_teeth
#print axioms MSE_1794123.nc3_equal_size_claim_holds
#print axioms MSE_1794123.nc4_equal_size_not_certified
#print axioms MSE_1794123.nc5_wf_has_teeth
#print axioms MSE_1794123.nc6_counter_nontrivial
#print axioms MSE_1794123.nc7_enumeration_complete
#print axioms MSE_1794123.nc8_arithmetic_discriminates
#print axioms MSE_1794123.nc9_fail_closed
#print axioms MSE_1794123.nc10_exchangeability_nonvacuous
#print axioms MSE_1794123.nc11_all_three_orderings_realised
