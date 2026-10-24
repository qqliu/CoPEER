/- Record proofwiki_120506__codex_expansion (E16): Mathlib file (`import Mathlib`, as the released file).

Source: the ProofWiki page "Angle is not Invariant under Affine Transformation" (stored problem text P0001-P0003,
proof text lines 0001-0012). Line 0002 defines the map L : R^2 → R^2, (x, y) ↦ (x, x + y); `L` below is that
map as a real linear map, `XAxis` is the x-axis {(x, y) | y = 0} and `Claimed` is the line x + y = 0.
The located claim (line 0009) is that the x-axis is transformed into the line x + y = 0: `SourceImageClaim`
(the image of the x-axis under L equals Claimed). -/
import Mathlib
/-! The source shear is a genuine real linear map, hence an affine map. -/
namespace ProofWiki120506CodexExpansion

def L : (ℝ × ℝ) →ₗ[ℝ] (ℝ × ℝ) where
  toFun p := (p.1, p.1 + p.2)
  map_add' p q := by ext <;> dsimp <;> ring
  map_smul' c p := by ext <;> dsimp <;> ring

def XAxis : Set (ℝ × ℝ) := {p | p.2 = 0}
def Claimed : Set (ℝ × ℝ) := {q | q.1 + q.2 = 0}

/-- The located claim (stored line 0009): the image of the x-axis under `L` is the line `x + y = 0`. -/
def SourceImageClaim : Prop := L '' XAxis = Claimed

end ProofWiki120506CodexExpansion
