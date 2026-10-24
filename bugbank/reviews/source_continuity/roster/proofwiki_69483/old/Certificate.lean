/-!
Record: proofwiki_69483
Source: ProofWiki, "Summation from k to m of r Choose k by s Choose n-k by
nr-(r+s)k"
https://proofwiki.org/wiki/Summation_from_k_to_m_of_r_Choose_k_by_s_Choose_n-k_by_nr-(r%2Bs)k

Exact target: in the induction step from line 0052 to line 0055, the proof
replaces `C(r,j+1)` by `(j+2)(r-j+2)C(r,j+2)` while leaving the bracket
`(j+1)(n-j)C(s,n-j) + C(s,n-j-1)(nr-(r+s)(j+1))` unchanged.  Thus the local
claim is `C(r,j+1) = (j+2)(r-j+2)C(r,j+2)`; this certificate also evaluates
the complete adjacent expressions.

Witness: `r = 3`, `j = 1`, `n = 3`, and `s = 3`.  Both binomial indices are
in range, both coefficients are positive, and the source-context condition
`j >= 1` holds.  The unchanged bracket is 3, so the local replacement is
`3 = 12`, and the complete lines are 9 and 36.  The earlier Terra witness
`r = 2, j = 0` showed the same arithmetic defect but missed `j >= 1`; the
semantic audit's corrected in-context witness is used here.

Scope: this refutes only the material local proof step, not the page's main
summation claim.  Terra's corrected relation and negative control is
`(j+2)C(r,j+2) = (r-j-1)C(r,j+1)`, which evaluates here to `3 = 3`.

Modelling judgments: natural binomial coefficients are defined locally by
Pascal recursion.  Parameters and indices are natural numbers, while the
bracket and complete line expressions use integers so that its subtraction
has the source's signed meaning.  Natural subtraction is used only for the
nonnegative indices and factors certified in range below.  All witness facts
are closed, exactly computable propositions checked by kernel `decide`; there
are no imports.
-/

namespace ProofWiki69483

def choose : Nat -> Nat -> Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => choose n k + choose n (k + 1)

def r : Nat := 3
def j : Nat := 1
def n : Nat := 3
def s : Nat := 3

def unchangedBracket : Int :=
  ((j + 1 : Nat) : Int) * ((n - j : Nat) : Int) *
    (choose s (n - j) : Int) +
  (choose s (n - j - 1) : Int) *
    ((n : Int) * (r : Int) -
      ((r + s : Nat) : Int) * ((j + 1 : Nat) : Int))

def line0052 : Int :=
  (choose r (j + 1) : Int) * unchangedBracket

def line0055 : Int :=
  ((j + 2 : Nat) : Int) * ((r - j + 2 : Nat) : Int) *
    (choose r (j + 2) : Int) * unchangedBracket

abbrev assertedLocalEquality : Prop :=
  (choose r (j + 1) : Int) =
    ((j + 2 : Nat) : Int) * ((r - j + 2 : Nat) : Int) *
      (choose r (j + 2) : Int)

abbrev assertedLineTransition : Prop :=
  line0052 = line0055

theorem refutes_line_0052_to_0055 :
    1 <= j /\
    j + 1 <= r /\
    j + 2 <= r /\
    choose r (j + 1) > 0 /\
    choose r (j + 2) > 0 /\
    choose r (j + 1) = 3 /\
    choose r (j + 2) = 1 /\
    unchangedBracket = 3 /\
    line0052 = 9 /\
    line0055 = 36 /\
    line0052 != line0055 /\
    Not assertedLocalEquality /\
    Not assertedLineTransition := by
  decide

/- Negative control: the corrected nearby binomial identity holds at the
same non-degenerate witness, with both sides equal to 3.  This would fail if
the encoding made all relevant binomial equalities uniformly false. -/
theorem negative_control_corrected_binomial_relation_holds :
    ((j + 2 : Nat) : Int) * (choose r (j + 2) : Int) = 3 /\
    (r - j - 1 : Nat) * choose r (j + 1) = 3 /\
    (j + 2) * choose r (j + 2) =
      (r - j - 1) * choose r (j + 1) := by
  decide

end ProofWiki69483
