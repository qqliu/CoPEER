import defs_only
/- Record reddit_math_2s4u2m (E14): the 390000-digit count fails for every value fitting the
565248-bit budget, by the coarse comparison (2^3)^188416 < 10^188416 (565248 = 3 * 188416):
every fitting value is below 10^188416, while 390000 digits would need 10^389999 <= H. -/
namespace Audit_reddit_math_2s4u2m

theorem bits_value : bits = 565248 := by decide

/-- Coarse bound: `2^565248 = (2^3)^188416 = 8^188416 < 10^188416`. -/
theorem coarse_power_bound : (2 : Nat)^565248 < 10^188416 := by
  have h3 : (2 : Nat)^3 < 10 := by decide
  have h : ((2 : Nat)^3)^188416 < 10^188416 := Nat.pow_lt_pow_left h3 (by decide)
  have e : (2 : Nat)^565248 = ((2 : Nat)^3)^188416 := by
    rw [← pow_mul]
  rw [e]
  exact h

theorem coarse_threshold_le : (10 : Nat)^188416 ≤ 10^389999 :=
  Nat.pow_le_pow_right (by decide) (by decide)

theorem maximum_fits_budget : FitsBits bits maximum := by
  unfold FitsBits maximum
  have hpos : 0 < 2^bits := Nat.two_pow_pos bits
  omega

/-- Every value fitting the budget is below `10^188416`. -/
theorem fitting_value_below_coarse (H : Nat) (hH : FitsBits bits H) : H < 10^188416 := by
  unfold FitsBits at hH
  rw [bits_value] at hH
  exact Nat.lt_trans hH coarse_power_bound

/-- Hence every fitting value has at most 188416 decimal digits (a coarse bound, not claimed to be
the least such bound). -/
theorem fitting_value_at_most_coarse_digits (H : Nat) (hH : FitsBits bits H) :
    HasAtMostDecDigits H 188416 :=
  And.intro (by decide) (fitting_value_below_coarse H hH)

/-- No fitting value has 390000 decimal digits: that would need `10^389999 ≤ H`. -/
theorem fitting_value_not_390000_digits (H : Nat) (hH : FitsBits bits H) :
    ¬ HasDecDigits H 390000 := by
  intro hd
  have hu : H < 10^188416 := fitting_value_below_coarse H hH
  rcases hd with ⟨_, h1⟩ | ⟨_, hlow, _⟩
  · exact absurd h1 (by decide)
  · have h389 : (10 : Nat)^389999 ≤ H := hlow
    exact absurd (Nat.lt_of_le_of_lt (Nat.le_trans coarse_threshold_le h389) hu) (lt_irrefl _)

theorem maximum_not_390000_digits : ¬ HasDecDigits maximum 390000 :=
  fitting_value_not_390000_digits maximum maximum_fits_budget

theorem published_conversion_false_at_maximum : ¬ PublishedDecimalConversionAt maximum :=
  fun h => maximum_not_390000_digits (h maximum_fits_budget)

theorem universal_published_conversion_false : ¬ UniversalPublishedDecimalConversion :=
  fun h => published_conversion_false_at_maximum (h maximum)

end Audit_reddit_math_2s4u2m

#print axioms Audit_reddit_math_2s4u2m.coarse_power_bound
#print axioms Audit_reddit_math_2s4u2m.fitting_value_not_390000_digits
#print axioms Audit_reddit_math_2s4u2m.universal_published_conversion_false
