import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Group.Subgroup.Defs

/-! CRT representative lifts for P=m=3,n=9 are injective as sets,
but their image in the product of Mathlib unit groups is not a subgroup.
We use actual Units, ZMod and Subgroup structures, not an arithmetic proxy. -/
namespace MSE_947973_ans948296

abbrev Y := (ZMod 3)ˣ × (ZMod 9)ˣ

def two3 : (ZMod 3)ˣ := ⟨2, 2, by decide, by decide⟩
def two9 : (ZMod 9)ˣ := ⟨2, 5, by decide, by decide⟩
def liftRep (x : (ZMod 3)ˣ) : Y := if x = 1 then 1 else (two3, two9)

theorem image_injective : Function.Injective liftRep := by decide

theorem image_not_closed :
    liftRep two3 * liftRep two3 ∉ Set.range liftRep := by decide

/-- No subgroup has exactly the source's claimed image as its carrier. -/
theorem mse_947973__ans948296_refutation :
    Function.Injective liftRep ∧
    ¬ ∃ H : Subgroup Y, (H : Set Y) = Set.range liftRep := by
  refine ⟨image_injective, ?_⟩
  rintro ⟨H, hH⟩
  have hm : liftRep two3 ∈ H := by
    change liftRep two3 ∈ (H : Set Y)
    rw [hH]
    exact ⟨two3, rfl⟩
  have hp := H.mul_mem hm hm
  change liftRep two3 * liftRep two3 ∈ (H : Set Y) at hp
  rw [hH] at hp
  exact image_not_closed hp

/-- The diagonal map at moduli 3,3 is an actual group homomorphism. -/
def diagonal : (ZMod 3)ˣ →* (ZMod 3)ˣ × (ZMod 3)ˣ where
  toFun x := (x, x)
  map_one' := rfl
  map_mul' _ _ := rfl

end MSE_947973_ans948296
