import Mathlib
/-! M3 is a complete lattice in Mathlib's sense, with three incomparable atoms.
It violates the infinitary distributivity required of a frame. Thus the
source's proposed object inclusion CLat -> Frm fails. -/
namespace ProofWiki144841CodexExpansion

inductive M3 where
  | bot | a | b | c | top
  deriving DecidableEq, Fintype

def m3Le : M3 → M3 → Prop
  | .bot, _ => True
  | _, .top => True
  | x, y => x = y

instance : DecidableRel m3Le := fun x y => by cases x <;> cases y <;> unfold m3Le <;> infer_instance

instance : PartialOrder M3 where
  le := m3Le
  le_refl x := by cases x <;> simp [m3Le]
  le_trans x y z := by cases x <;> cases y <;> cases z <;> simp [m3Le]
  le_antisymm x y := by cases x <;> cases y <;> simp [m3Le]

instance : DecidableLE M3 := fun x y => inferInstanceAs (Decidable (m3Le x y))

def m3Meet : M3 → M3 → M3
  | .bot, _ => .bot
  | _, .bot => .bot
  | .top, y => y
  | x, .top => x
  | x, y => if x = y then x else .bot

def m3Join : M3 → M3 → M3
  | .top, _ => .top
  | _, .top => .top
  | .bot, y => y
  | x, .bot => x
  | x, y => if x = y then x else .top

instance : Lattice M3 where
  sup := m3Join
  le_sup_left a b := by cases a <;> cases b <;> decide
  le_sup_right a b := by cases a <;> cases b <;> decide
  sup_le a b c := by cases a <;> cases b <;> cases c <;> decide
  inf := m3Meet
  inf_le_left a b := by cases a <;> cases b <;> decide
  inf_le_right a b := by cases a <;> cases b <;> decide
  le_inf a b c := by cases a <;> cases b <;> cases c <;> decide

instance : BoundedOrder M3 where
  top := .top
  le_top a := by cases a <;> decide
  bot := .bot
  bot_le a := by cases a <;> decide

noncomputable instance : CompleteLattice M3 := Fintype.toCompleteLattice M3

theorem refutes_complete_lattice_object_inclusion :
    M3.a ⊓ sSup ({M3.b, M3.c} : Set M3) = M3.a ∧
    sSup ((fun x => M3.a ⊓ x) '' ({M3.b, M3.c} : Set M3)) = M3.bot ∧
    ¬ (∀ (a : M3) (s : Set M3), a ⊓ sSup s = sSup ((fun x => a ⊓ x) '' s)) := by
  have hl : M3.a ⊓ sSup ({M3.b, M3.c} : Set M3) = M3.a := by
    rw [sSup_pair]
    rfl
  have hr : sSup ((fun x => M3.a ⊓ x) '' ({M3.b, M3.c} : Set M3)) = M3.bot := by
    rw [Set.image_pair, sSup_pair]
    rfl
  refine ⟨hl, hr, ?_⟩
  intro h
  have hh := h M3.a {M3.b, M3.c}
  rw [hl, hr] at hh
  cases hh

/-- A genuine frame satisfies exactly the equation falsified above. -/
theorem negative_control_frame_law (a : Set Unit) (s : Set (Set Unit)) :
    a ⊓ sSup s = sSup ((fun x => a ⊓ x) '' s) := by
  rw [inf_sSup_eq, sSup_image]
end ProofWiki144841CodexExpansion
