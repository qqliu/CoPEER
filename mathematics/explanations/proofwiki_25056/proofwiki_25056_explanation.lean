import Mathlib.RingTheory.Polynomial.Content
import Mathlib.RingTheory.Localization.Integral
import Mathlib.Tactic
/-!
# proofwiki_25056: the documented family and repair, formalised (explanation census)

Source (ProofWiki, "Content of Scalar Multiple"), quoted local claim, for `q = a / b`,
`a b n : ℤ`, `n f ∈ ℤ[X]`:  `cont (b n q f) = a cont (n f)`.
Since `b n q f = a (n f)` as integer polynomials (`quoted_line_bridge`, for every `b ≠ 0`),
the claim is the unsigned scalar pull-out `cont (a p) = a cont p` with `p = n f`.

Documented family: the claim fails for every `a < 0` and `p ≠ 0`.
Documented repair: `cont (a p) = |a| cont p` and `cont (q F) = |q| cont F`.

`f`, `g`, `f_content`, `g_content` are restated verbatim from the released certificate
`partB_feasibility/diverse_certificates/proofwiki_25056.lean`
(sha256 86ce16ed02c53f9152fe20d3acba28781452578e8e169d79a70f351fc2071738); the namespace is
changed to keep the two files distinct.  Integer content is Mathlib's `Polynomial.content`
(the normalised gcd of the coefficients), exactly as in the released file.  The rational content
is NOT in the released file and is defined here (`Presents`, `ratContent`) following the source's
own definition `cont F = (1/n) cont (n F)` with `n` a positive integer and `n F ∈ ℤ[X]`.
-/
namespace ProofWiki25056Census
open Polynomial

/-! ## Released definitions, verbatim -/

noncomputable def f : ℤ[X] := X + 1
noncomputable def g : ℤ[X] := C 2 * f

theorem f_content : f.content = 1 := by
  apply IsPrimitive.content_eq_one
  exact (monic_X_add_C (1 : ℤ)).isPrimitive

theorem g_content : g.content = 2 := by
  rw [g, content_C_mul, f_content]
  norm_num [← Int.abs_eq_normalize]

/-! ## Integer form (the quoted line) -/

/-- REPAIR, integer form: `cont (a p) = |a| cont p` for every integer `a` and every `p ∈ ℤ[X]`. -/
theorem repair (a : ℤ) (p : ℤ[X]) : (C a * p).content = |a| * p.content := by
  rw [content_C_mul, Int.abs_eq_normalize]

theorem content_nonneg (p : ℤ[X]) : 0 ≤ p.content := by
  have h := normalize_content (p := p)
  exact Int.nonneg_of_normalize_eq_self h

theorem content_pos {p : ℤ[X]} (hp : p ≠ 0) : 0 < p.content := by
  have h0 : p.content ≠ 0 := fun h => hp (content_eq_zero_iff.mp h)
  exact lt_of_le_of_ne (content_nonneg p) (Ne.symm h0)

/-- FAMILY, integer form: the quoted identity fails at every negative scalar and every nonzero
integer polynomial. -/
theorem family (a : ℤ) (p : ℤ[X]) (ha : a < 0) (hp : p ≠ 0) :
    (C a * p).content ≠ a * p.content := by
  intro h
  have h1 : 0 ≤ (C a * p).content := content_nonneg _
  have h2 : a * p.content < 0 := mul_neg_of_neg_of_pos ha (content_pos hp)
  omega

/-- EXACT, integer form: the quoted identity holds iff `a ≥ 0` or `p = 0`. -/
theorem exact (a : ℤ) (p : ℤ[X]) :
    (C a * p).content = a * p.content ↔ (0 ≤ a ∨ p = 0) := by
  constructor
  · intro h
    by_contra hc
    rw [not_or, not_le] at hc
    exact family a p hc.1 hc.2 h
  · rintro (ha | hp)
    · rw [repair, abs_of_nonneg ha]
    · subst hp; simp

theorem g_ne_zero : g ≠ 0 := by
  intro h
  have h2 := g_content
  rw [h] at h2
  simp at h2

/-- The refuted local claim at the released witness `a = -1`, `n f = g = 2X + 2`,
`b n q f = -g`: the same inequality as the last conjunct of the released
`refutes_unsigned_scalar_pull_out`, here obtained as an instance of `family`. -/
theorem claim_refuted : (-g).content ≠ (-1 : ℤ) * g.content := by
  have hneg : -g = C (-1 : ℤ) * g := by simp
  rw [hneg]
  exact family (-1) g (by norm_num) g_ne_zero

/-- The source's expression `b n (q f)` with `q = a / b` IS the integer polynomial `a (n f)`,
for every nonzero `b` of either sign: the sign of `b` plays no role in the quoted line. -/
theorem quoted_line_bridge (a b n : ℤ) (hb : b ≠ 0) (F : ℚ[X]) (p : ℤ[X])
    (hp : p.map (Int.castRingHom ℚ) = C (n : ℚ) * F) :
    (C a * p).map (Int.castRingHom ℚ)
      = C (b : ℚ) * (C (n : ℚ) * (C ((a : ℚ) / (b : ℚ)) * F)) := by
  rw [Polynomial.map_mul, Polynomial.map_C, hp]
  have hbq : (b : ℚ) ≠ 0 := by exact_mod_cast hb
  have ha : (a : ℚ) = (b : ℚ) * ((a : ℚ) / (b : ℚ)) := by field_simp
  simp only [eq_intCast]
  calc C (a : ℚ) * (C (n : ℚ) * F)
      = C ((b : ℚ) * ((a : ℚ) / (b : ℚ))) * (C (n : ℚ) * F) := by rw [← ha]
    _ = C (b : ℚ) * (C (n : ℚ) * (C ((a : ℚ) / (b : ℚ)) * F)) := by rw [C_mul]; ring

/-! ## Rational form (the source theorem's final line) -/

/-- `Presents F d p`: `d` is a positive integer, `p ∈ ℤ[X]`, and `d F = p` in `ℚ[X]`. -/
def Presents (F : ℚ[X]) (d : ℤ) (p : ℤ[X]) : Prop :=
  0 < d ∧ p.map (Int.castRingHom ℚ) = C (d : ℚ) * F

/-- The quotient `cont p / d` does not depend on the presentation. -/
theorem presents_wd {F : ℚ[X]} {d₁ d₂ : ℤ} {p₁ p₂ : ℤ[X]}
    (h₁ : Presents F d₁ p₁) (h₂ : Presents F d₂ p₂) :
    (p₁.content : ℚ) / d₁ = (p₂.content : ℚ) / d₂ := by
  have hinj : Function.Injective (Polynomial.map (Int.castRingHom ℚ)) :=
    Polynomial.map_injective _ Int.cast_injective
  have hpoly : C d₂ * p₁ = C d₁ * p₂ := by
    apply hinj
    rw [Polynomial.map_mul, Polynomial.map_mul, Polynomial.map_C, Polynomial.map_C, h₁.2, h₂.2]
    simp only [eq_intCast]
    ring
  have hc : |d₂| * p₁.content = |d₁| * p₂.content := by
    rw [← repair, ← repair, hpoly]
  rw [abs_of_pos h₁.1, abs_of_pos h₂.1] at hc
  have hcq : (d₂ : ℚ) * p₁.content = d₁ * p₂.content := by exact_mod_cast hc
  have hd1 : (d₁ : ℚ) ≠ 0 := by exact_mod_cast h₁.1.ne'
  have hd2 : (d₂ : ℚ) ≠ 0 := by exact_mod_cast h₂.1.ne'
  field_simp
  linarith

/-- Every rational polynomial has a presentation. -/
theorem exists_presentation (F : ℚ[X]) : ∃ d p, Presents F d p := by
  obtain ⟨b, hbM, hb⟩ := IsLocalization.integerNormalization_spec (nonZeroDivisors ℤ) F
  have hb0 : b ≠ 0 := nonZeroDivisors.ne_zero hbM
  have hmap : (IsLocalization.integerNormalization (nonZeroDivisors ℤ) F).map
      (Int.castRingHom ℚ) = C (b : ℚ) * F := by
    have hcast : algebraMap ℤ ℚ = Int.castRingHom ℚ := rfl
    rw [← hcast, hb]
    ext i
    rw [Polynomial.coeff_smul, Polynomial.coeff_C_mul, zsmul_eq_mul]
  rcases lt_or_gt_of_ne hb0 with hneg | hpos
  · refine ⟨-b, -(IsLocalization.integerNormalization (nonZeroDivisors ℤ) F),
      by omega, ?_⟩
    rw [Polynomial.map_neg, hmap]
    simp
  · exact ⟨b, _, hpos, hmap⟩

/-- Content of a rational polynomial: `cont (d F) / d` for a chosen presentation `d F = p`. -/
noncomputable def ratContent (F : ℚ[X]) : ℚ :=
  ((Classical.choose (Classical.choose_spec (exists_presentation F))).content : ℚ) /
    (Classical.choose (exists_presentation F) : ℤ)

/-- `ratContent` is computed by ANY presentation. -/
theorem ratContent_eq {F : ℚ[X]} {d : ℤ} {p : ℤ[X]} (h : Presents F d p) :
    ratContent F = (p.content : ℚ) / d :=
  presents_wd (Classical.choose_spec (Classical.choose_spec (exists_presentation F))) h

theorem presents_smul {F : ℚ[X]} {d : ℤ} {p : ℤ[X]} (h : Presents F d p) (q : ℚ) :
    Presents (C q * F) ((q.den : ℤ) * d) (C q.num * p) := by
  refine ⟨mul_pos (by exact_mod_cast q.pos) h.1, ?_⟩
  rw [Polynomial.map_mul, Polynomial.map_C, h.2]
  have hq : (q.num : ℚ) = q * q.den := (Rat.mul_den_eq_num q).symm
  simp only [eq_intCast, Int.cast_mul, Int.cast_natCast]
  rw [hq, ← mul_assoc, ← mul_assoc, ← C_mul, ← C_mul]
  have key : q * (q.den : ℚ) * (d : ℚ) = (q.den : ℚ) * (d : ℚ) * q := by ring
  rw [key]

/-- REPAIR, rational form: `cont (q F) = |q| cont F` for every rational `q` and every
`F ∈ ℚ[X]` (including `F = 0`, where both sides are `0`). -/
theorem repair_rat (q : ℚ) (F : ℚ[X]) : ratContent (C q * F) = |q| * ratContent F := by
  obtain ⟨d, p, h⟩ := exists_presentation F
  rw [ratContent_eq h, ratContent_eq (presents_smul h q), repair]
  have hd : (d : ℚ) ≠ 0 := by exact_mod_cast h.1.ne'
  have hden : (q.den : ℚ) ≠ 0 := by exact_mod_cast q.den_nz
  have habs : |q| = |(q.num : ℚ)| / q.den := by
    conv_lhs => rw [← Rat.num_div_den q]
    rw [abs_div, Nat.abs_cast]
  rw [habs]
  push_cast
  field_simp

/-- The content of a nonzero rational polynomial is a positive rational. -/
theorem ratContent_pos {F : ℚ[X]} (hF : F ≠ 0) : 0 < ratContent F := by
  obtain ⟨d, p, h⟩ := exists_presentation F
  rw [ratContent_eq h]
  have hdq : (0 : ℚ) < d := by exact_mod_cast h.1
  have hp : p ≠ 0 := by
    rintro rfl
    have h2 := h.2
    rw [Polynomial.map_zero] at h2
    have hne : C (d : ℚ) * F ≠ 0 := mul_ne_zero (C_ne_zero.mpr hdq.ne') hF
    exact hne h2.symm
  have hc : (0 : ℚ) < p.content := by exact_mod_cast content_pos hp
  exact div_pos hc hdq

/-- The zero polynomial has content `0`, which is NOT a positive rational: the dossier's
"the content of a rational polynomial is by definition a positive rational" omits this case. -/
theorem ratContent_zero : ratContent 0 = 0 := by
  have h : Presents 0 1 0 := ⟨one_pos, by simp⟩
  rw [ratContent_eq h]; simp

/-- FAMILY, rational form: the source theorem's conclusion `cont (q F) = q cont F` fails at
every negative rational `q` and every nonzero `F ∈ ℚ[X]`. -/
theorem family_rat (q : ℚ) (F : ℚ[X]) (hq : q < 0) (hF : F ≠ 0) :
    ratContent (C q * F) ≠ q * ratContent F := by
  intro h
  have hpos := ratContent_pos hF
  have h1 : 0 ≤ ratContent (C q * F) := by
    rw [repair_rat]; exact mul_nonneg (abs_nonneg q) hpos.le
  have h2 : q * ratContent F < 0 := mul_neg_of_neg_of_pos hq hpos
  linarith

/-- EXACT, rational form: `cont (q F) = q cont F` iff `q ≥ 0` or `F = 0`. -/
theorem exact_rat (q : ℚ) (F : ℚ[X]) :
    ratContent (C q * F) = q * ratContent F ↔ (0 ≤ q ∨ F = 0) := by
  constructor
  · intro h
    by_contra hc
    rw [not_or, not_le] at hc
    exact family_rat q F hc.1 hc.2 h
  · rintro (hq | hF)
    · rw [repair_rat, abs_of_nonneg hq]
    · subst hF; simp [ratContent_zero]

/-- The dossier's rational numbers at the witness `F = X + 1`, `q = -1/2`:
`cont F = 1`, `cont (q F) = 1/2`, and the source's asserted value `q cont F = -1/2` is wrong. -/
theorem rat_witness :
    ratContent (X + 1 : ℚ[X]) = 1 ∧
    ratContent (C (-1 / 2 : ℚ) * (X + 1 : ℚ[X])) = 1 / 2 ∧
    ratContent (C (-1 / 2 : ℚ) * (X + 1 : ℚ[X])) ≠ (-1 / 2 : ℚ) * ratContent (X + 1 : ℚ[X]) := by
  have hP : Presents (X + 1 : ℚ[X]) 1 f := ⟨one_pos, by simp [f]⟩
  have h1 : ratContent (X + 1 : ℚ[X]) = 1 := by
    rw [ratContent_eq hP, f_content]; norm_num
  refine ⟨h1, ?_, ?_⟩
  · rw [repair_rat, h1]; norm_num [abs_of_neg]
  · rw [repair_rat, h1]; norm_num [abs_of_neg]

/-! ## Binding to the dossier's own definition of rational content

The dossier defines the content of a rational polynomial "as the positive rational c with
f = c f* and f* primitive".  On `F ≠ 0` such a pair exists, `c` is unique, and `c = ratContent F`.
At `F = 0` no such pair exists, so the dossier's definition is silent there. -/

/-- Any decomposition `F = c P` with `c > 0` rational and `P ∈ ℤ[X]` primitive has
`c = ratContent F` (uniqueness of the dossier's `c`, and agreement with `ratContent`). -/
theorem ratContent_of_primitive (F : ℚ[X]) (c : ℚ) (hc : 0 < c) (P : ℤ[X])
    (hP : P.IsPrimitive) (hF : F = C c * P.map (Int.castRingHom ℚ)) : ratContent F = c := by
  have hpres : Presents F (c.den : ℤ) (C c.num * P) := by
    refine ⟨by exact_mod_cast c.pos, ?_⟩
    rw [hF, Polynomial.map_mul, Polynomial.map_C, ← mul_assoc, ← C_mul]
    simp only [eq_intCast, Int.cast_natCast]
    rw [mul_comm (c.den : ℚ) c, Rat.mul_den_eq_num]
  rw [ratContent_eq hpres, repair, hP.content_eq_one, mul_one]
  have hnum : 0 < c.num := Rat.num_pos.mpr hc
  rw [abs_of_pos hnum, Int.cast_natCast]
  exact Rat.num_div_den c

/-- Every nonzero rational polynomial has such a decomposition. -/
theorem exists_primitive_decomposition (F : ℚ[X]) (hF : F ≠ 0) :
    ∃ (c : ℚ) (P : ℤ[X]), 0 < c ∧ P.IsPrimitive ∧ F = C c * P.map (Int.castRingHom ℚ) := by
  obtain ⟨d, p, h⟩ := exists_presentation F
  have hdq : (0 : ℚ) < d := by exact_mod_cast h.1
  have hp : p ≠ 0 := by
    rintro rfl
    have h2 := h.2
    rw [Polynomial.map_zero] at h2
    have hne : C (d : ℚ) * F ≠ 0 := mul_ne_zero (C_ne_zero.mpr hdq.ne') hF
    exact hne h2.symm
  have hc : (0 : ℚ) < p.content := by exact_mod_cast content_pos hp
  refine ⟨(p.content : ℚ) / d, p.primPart, div_pos hc hdq, p.isPrimitive_primPart, ?_⟩
  have e1 : C (d : ℚ) * F = C (p.content : ℚ) * p.primPart.map (Int.castRingHom ℚ) := by
    rw [← h.2]
    conv_lhs => rw [p.eq_C_content_mul_primPart]
    rw [Polynomial.map_mul, Polynomial.map_C]
    simp only [eq_intCast]
  calc F = C ((d : ℚ)⁻¹) * (C (d : ℚ) * F) := by
        rw [← mul_assoc, ← C_mul, inv_mul_cancel₀ hdq.ne', C_1, one_mul]
    _ = C ((p.content : ℚ) / d) * p.primPart.map (Int.castRingHom ℚ) := by
        rw [e1, ← mul_assoc, ← C_mul, ← div_eq_inv_mul]

/-- The zero polynomial has NO decomposition `0 = c P` with `c > 0` and `P` primitive. -/
theorem no_primitive_decomposition_of_zero :
    ¬ ∃ (c : ℚ) (P : ℤ[X]), 0 < c ∧ P.IsPrimitive ∧
        (0 : ℚ[X]) = C c * P.map (Int.castRingHom ℚ) := by
  rintro ⟨c, P, hc, hP, h0⟩
  have hPne : P ≠ 0 := hP.ne_zero
  have hmap : P.map (Int.castRingHom ℚ) ≠ 0 := by
    intro hz
    apply hPne
    have hinj : Function.Injective (Polynomial.map (Int.castRingHom ℚ)) :=
      Polynomial.map_injective _ Int.cast_injective
    exact hinj (by rw [hz, Polynomial.map_zero])
  exact (mul_ne_zero (C_ne_zero.mpr hc.ne') hmap) h0.symm

/-! ## The sign of `b` and the sign of `q` are not what the quoted line depends on -/

/-- With `a = 1`, `b = -2` (so `q = -1/2 < 0`) the quoted line HOLDS for every `p = n f`:
`b n q f = 1 * p`.  The dossier's flaw field says the line is false "when a (or b) is
negative"; for the quoted line only the sign of `a` matters. -/
theorem quoted_line_holds_with_negative_b (p : ℤ[X]) :
    (C (1 : ℤ) * p).content = (1 : ℤ) * p.content :=
  (exact 1 p).mpr (Or.inl (by norm_num))

/-- With `a = -1`, `b = -2`, `n = 2`, `F = X + 1` one has `q = 1/2 > 0`, `b n q F = -g`, and the
quoted line fails although the source theorem's conclusion `cont (q F) = q cont F` holds. -/
theorem quoted_line_fails_with_positive_q :
    (-g).map (Int.castRingHom ℚ)
        = C ((-2 : ℤ) : ℚ) * (C ((2 : ℤ) : ℚ) * (C (((-1 : ℤ) : ℚ) / ((-2 : ℤ) : ℚ)) * (X + 1 : ℚ[X]))) ∧
    (-g).content ≠ (-1 : ℤ) * g.content ∧
    ratContent (C (1 / 2 : ℚ) * (X + 1 : ℚ[X])) = (1 / 2 : ℚ) * ratContent (X + 1 : ℚ[X]) := by
  refine ⟨?_, claim_refuted, (exact_rat _ _).mpr (Or.inl (by norm_num))⟩
  have hneg : -g = C (-1 : ℤ) * g := by simp
  have hg : g.map (Int.castRingHom ℚ) = C ((2 : ℤ) : ℚ) * (X + 1 : ℚ[X]) := by
    rw [g, f, Polynomial.map_mul, Polynomial.map_C, Polynomial.map_add, Polynomial.map_X,
      Polynomial.map_one]
    simp only [eq_intCast]
  rw [hneg]
  exact quoted_line_bridge (-1) (-2) 2 (by norm_num) (X + 1) g hg

end ProofWiki25056Census

#print axioms ProofWiki25056Census.claim_refuted
#print axioms ProofWiki25056Census.family
#print axioms ProofWiki25056Census.repair
#print axioms ProofWiki25056Census.exact
#print axioms ProofWiki25056Census.quoted_line_bridge
#print axioms ProofWiki25056Census.presents_wd
#print axioms ProofWiki25056Census.exists_presentation
#print axioms ProofWiki25056Census.ratContent_eq
#print axioms ProofWiki25056Census.family_rat
#print axioms ProofWiki25056Census.repair_rat
#print axioms ProofWiki25056Census.exact_rat
#print axioms ProofWiki25056Census.ratContent_zero
#print axioms ProofWiki25056Census.rat_witness
#print axioms ProofWiki25056Census.ratContent_of_primitive
#print axioms ProofWiki25056Census.exists_primitive_decomposition
#print axioms ProofWiki25056Census.no_primitive_decomposition_of_zero
#print axioms ProofWiki25056Census.quoted_line_holds_with_negative_b
#print axioms ProofWiki25056Census.quoted_line_fails_with_positive_q
