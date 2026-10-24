/- Record reddit_math_2s4u2m (E14): Mathlib file (Nat.digits available; narrow imports as in the released file).

The source (stored post lines 0028-0030) fixes a 69 KiB compressed object, counts its bits as
69 x 8 x 1024 = 565248 (line 0028), and converts that bit count into a decimal digit count (line 0030).
The definitions below are the released formal model of that budget and of the stored digit convention:
`FitsBits b n` says `n` is representable in `b` bits; `HasDecDigits n d` says `n` has exactly `d`
ordinary decimal digits (zero has one digit); `HasAtMostDecDigits n d` says `n` has at most `d`
digits; `maximum` is the largest value fitting the budget.  The located claim is the source's digit
count for the object: `PublishedDecimalConversionAt H` (a value `H` fitting the budget has 390000
decimal digits), read universally over every fitting value as `UniversalPublishedDecimalConversion`. -/
import Mathlib.Data.Nat.Digits.Lemmas
import Mathlib.Algebra.Order.Ring.Nat
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

namespace Audit_reddit_math_2s4u2m
def payloadKiB : Nat := 69
def bytesPerKiB : Nat := 1024
def bitsPerByte : Nat := 8
def bits : Nat := payloadKiB * bytesPerKiB * bitsPerByte

def FitsBits (b n : Nat) : Prop := n < 2^b

/- The disjunction is definitionally small even when `n` is a named enormous
power. Its two branches are exactly the stipulated convention: zero has one
digit, and the usual two power thresholds characterize every positive value.
The lower threshold makes the second branch false for zero. -/
def HasDecDigits (n d : Nat) : Prop :=
  (n = 0 /\ d = 1) \/
  (0 < d /\ 10^(d - 1) <= n /\ n < 10^d)

/- For positive `d`, this is precisely the upper-threshold meaning of at most
`d` ordinary decimal digits. It includes zero. -/
def HasAtMostDecDigits (n d : Nat) : Prop := 0 < d /\ n < 10^d

def maximum : Nat := 2^bits - 1

/-- The located claim at a value `H` (stored line 0030): if `H` fits the bit budget then it has
390000 decimal digits. -/
abbrev PublishedDecimalConversionAt (H : Nat) : Prop :=
  FitsBits bits H -> HasDecDigits H 390000

/-- The located claim read universally over every value fitting the source's bit budget. -/
def UniversalPublishedDecimalConversion : Prop := ∀ H : Nat, PublishedDecimalConversionAt H

end Audit_reddit_math_2s4u2m
