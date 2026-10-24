import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

/-! The printed common exponent e_k gives C₂ × C₃ when n=12=2²3.
Use Mathlib's cyclic additive groups ZMod and Fintype.card directly.
This isolates an indexing typo; it does not refute the intended construction
with the separate exponents e_i. -/
namespace Arxiv190410482v2SourceEnrichedCodex
abbrev LiteralCommonEkCarrier := ZMod 2 × ZMod 3
abbrev CorrectedEiCarrier := ZMod 2 × ZMod 2 × ZMod 3

theorem refutes_literal_common_ek_order_twelve :
    Nat.Prime 2 ∧ Nat.Prime 3 ∧ 12 = 2^2 * 3^1 ∧
    Fintype.card LiteralCommonEkCarrier = 6 ∧
    Fintype.card LiteralCommonEkCarrier ≠ 12 := by
  norm_num [LiteralCommonEkCarrier]

theorem corrected_exponents_have_order_twelve :
    Fintype.card CorrectedEiCarrier = 12 := by
  norm_num [CorrectedEiCarrier]
end Arxiv190410482v2SourceEnrichedCodex
