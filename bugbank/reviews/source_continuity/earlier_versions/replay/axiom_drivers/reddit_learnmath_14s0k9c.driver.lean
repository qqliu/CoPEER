/-!
Record: reddit_learnmath_14s0k9c
Public source: https://www.reddit.com/r/learnmath/comments/14s0k9c/checking_for_error_in_group_theory_proof/

Exact target scope: the material local inference that, under an embedding into
a symmetric group, every element of exact order two must map to one single
transposition.  This certificate does not claim that the surrounding main
theorem is false: its nonabelian/two-generator context is not used by that
local inference, so it is deliberately not imposed on the concrete source
group.

Concrete independently verified witness: C2 = {e,x}, with x*x=e and x!=e,
embedded in S4 by phi(e)=id and phi(x)=(p0 p1)(p2 p3).  The image of x has
exact order two but is not one transposition.  The meaningful negative control
is the injective homomorphism psi:C2 -> S2 taking x to (q0 q1), which really is
a single transposition.

Material modelling judgments: C2 and both acted-on sets are explicit finite
inductive types.  C2 multiplication and inversion are full tables, and its
identity, associativity, and inverse laws are proved below.  `Perm` is a genuine
bijection representation containing forward and inverse maps with proofs of
both inverse composites.  `permComp p q` means p after q (q is applied first);
homomorphism preservation is stated pointwise, the extensional equality
appropriate to permutations.  Exact order two means nonidentity plus square
equal to identity.  `IsSingleTransposition` has its literal semantic meaning:
two distinct points are swapped and every other point is fixed.  No support
count or numeric cycle-type proxy is used.  The refutation states finiteness,
all C2 group laws, exact order of x, preservation, injectivity, exact order of
its image, and failure of the claimed conclusion.  The S2 control checks the
same substantive premises and the opposite conclusion.
-/

namespace RedditLearnmath14s0k9c

inductive C2 where
  | e | x
  deriving DecidableEq

inductive P4 where
  | p0 | p1 | p2 | p3
  deriving DecidableEq

inductive P2 where
  | q0 | q1
  deriving DecidableEq

def c2Mul : C2 -> C2 -> C2
  | .e, g => g
  | g, .e => g
  | .x, .x => .e

def c2Inv : C2 -> C2
  | .e => .e
  | .x => .x

def C2Exhaustive : Prop :=
  forall g : C2, g = .e \/ g = .x

def C2GroupLaws : Prop :=
  (forall g, c2Mul .e g = g /\ c2Mul g .e = g) /\
  (forall a b c, c2Mul (c2Mul a b) c = c2Mul a (c2Mul b c)) /\
  (forall g, c2Mul (c2Inv g) g = .e /\ c2Mul g (c2Inv g) = .e)

def ExactOrderTwoC2 (g : C2) : Prop :=
  g ≠ .e /\ c2Mul g g = .e

theorem c2_exhaustive : C2Exhaustive := by
  intro g
  cases g with
  | e => exact Or.inl rfl
  | x => exact Or.inr rfl

theorem c2_group_laws : C2GroupLaws := by
  refine And.intro ?_ (And.intro ?_ ?_)
  · intro g
    cases g <;> exact And.intro rfl rfl
  · intro a b c
    cases a <;> cases b <;> cases c <;> rfl
  · intro g
    cases g <;> exact And.intro rfl rfl

theorem x_has_exact_order_two : ExactOrderTwoC2 .x := by
  exact And.intro (by decide) rfl

structure Perm (alpha : Type) where
  toFun : alpha -> alpha
  invFun : alpha -> alpha
  leftInv : forall a, invFun (toFun a) = a
  rightInv : forall a, toFun (invFun a) = a

def permId {alpha : Type} : Perm alpha where
  toFun := fun a => a
  invFun := fun a => a
  leftInv := by intro a; rfl
  rightInv := by intro a; rfl

def permInv {alpha : Type} (p : Perm alpha) : Perm alpha where
  toFun := p.invFun
  invFun := p.toFun
  leftInv := p.rightInv
  rightInv := p.leftInv

/- Composition orientation: `permComp p q` applies q first, then p. -/
def permComp {alpha : Type} (p q : Perm alpha) : Perm alpha where
  toFun := fun a => p.toFun (q.toFun a)
  invFun := fun a => q.invFun (p.invFun a)
  leftInv := by
    intro a
    rw [p.leftInv, q.leftInv]
  rightInv := by
    intro a
    rw [q.rightInv, p.rightInv]

def PermEq {alpha : Type} (p q : Perm alpha) : Prop :=
  forall a, p.toFun a = q.toFun a

theorem perm_comp_assoc_pointwise {alpha : Type} (p q r : Perm alpha) :
    PermEq (permComp (permComp p q) r) (permComp p (permComp q r)) := by
  intro a
  rfl

theorem perm_id_left_pointwise {alpha : Type} (p : Perm alpha) :
    PermEq (permComp permId p) p := by
  intro a
  rfl

theorem perm_id_right_pointwise {alpha : Type} (p : Perm alpha) :
    PermEq (permComp p permId) p := by
  intro a
  rfl

theorem perm_inv_left_pointwise {alpha : Type} (p : Perm alpha) :
    PermEq (permComp (permInv p) p) permId := by
  intro a
  exact p.leftInv a

theorem perm_inv_right_pointwise {alpha : Type} (p : Perm alpha) :
    PermEq (permComp p (permInv p)) permId := by
  intro a
  exact p.rightInv a

def ExactOrderTwoPerm {alpha : Type} (p : Perm alpha) : Prop :=
  (exists a, p.toFun a ≠ a) /\ PermEq (permComp p p) permId

def IsSingleTransposition {alpha : Type} (p : Perm alpha) : Prop :=
  exists a b,
    a ≠ b /\
    p.toFun a = b /\
    p.toFun b = a /\
    forall z, z ≠ a -> z ≠ b -> p.toFun z = z

def swap4 : P4 -> P4
  | .p0 => .p1
  | .p1 => .p0
  | .p2 => .p3
  | .p3 => .p2

def doubleSwap : Perm P4 where
  toFun := swap4
  invFun := swap4
  leftInv := by intro a; cases a <;> rfl
  rightInv := by intro a; cases a <;> rfl

def phi : C2 -> Perm P4
  | .e => permId
  | .x => doubleSwap

def PreservesC2Mul {alpha : Type} (f : C2 -> Perm alpha) : Prop :=
  forall g h z,
    (f (c2Mul g h)).toFun z = (permComp (f g) (f h)).toFun z

def Injective {alpha beta : Type} (f : alpha -> beta) : Prop :=
  forall a b, f a = f b -> a = b

theorem phi_preserves_mul : PreservesC2Mul phi := by
  intro g h z
  cases g <;> cases h <;> cases z <;> rfl

theorem phi_injective : Injective phi := by
  intro a b h
  cases a <;> cases b
  · rfl
  · have bad : P4.p0 = P4.p1 :=
      congrArg (fun p : Perm P4 => p.toFun .p0) h
    cases bad
  · have bad : P4.p1 = P4.p0 :=
      congrArg (fun p : Perm P4 => p.toFun .p0) h
    cases bad
  · rfl

theorem phi_x_has_exact_order_two : ExactOrderTwoPerm (phi .x) := by
  refine And.intro ?_ ?_
  · exact Exists.intro P4.p0 (by decide)
  · intro a
    cases a <;> rfl

theorem phi_x_is_not_single_transposition :
    Not (IsSingleTransposition (phi .x)) := by
  intro h
  rcases h with ⟨a, b, hab, habForward, _hbaForward, hfix⟩
  have h0 := hfix P4.p0
  have h2 := hfix P4.p2
  cases a <;> cases b
  · exact hab rfl
  · have bad := h2 (by decide) (by decide)
    cases bad
  · cases habForward
  · cases habForward
  · have bad := h2 (by decide) (by decide)
    cases bad
  · exact hab rfl
  · cases habForward
  · cases habForward
  · cases habForward
  · cases habForward
  · exact hab rfl
  · have bad := h0 (by decide) (by decide)
    cases bad
  · cases habForward
  · cases habForward
  · have bad := h0 (by decide) (by decide)
    cases bad
  · exact hab rfl

abbrev PublishedClaimAtWitness : Prop :=
  C2Exhaustive ->
  C2GroupLaws ->
  ExactOrderTwoC2 .x ->
  PreservesC2Mul phi ->
  Injective phi ->
  ExactOrderTwoPerm (phi .x) ->
  IsSingleTransposition (phi .x)

/-! The source's local universal inference fails at the fully checked witness. -/
theorem reddit_learnmath_14s0k9c_refutation :
    C2Exhaustive /\
    C2GroupLaws /\
    ExactOrderTwoC2 .x /\
    PreservesC2Mul phi /\
    Injective phi /\
    ExactOrderTwoPerm (phi .x) /\
    Not (IsSingleTransposition (phi .x)) /\
    Not PublishedClaimAtWitness := by
  refine And.intro c2_exhaustive ?_
  refine And.intro c2_group_laws ?_
  refine And.intro x_has_exact_order_two ?_
  refine And.intro phi_preserves_mul ?_
  refine And.intro phi_injective ?_
  refine And.intro phi_x_has_exact_order_two ?_
  refine And.intro phi_x_is_not_single_transposition ?_
  intro claimed
  exact phi_x_is_not_single_transposition
    (claimed c2_exhaustive c2_group_laws x_has_exact_order_two
      phi_preserves_mul phi_injective phi_x_has_exact_order_two)

def swap2 : P2 -> P2
  | .q0 => .q1
  | .q1 => .q0

def singleSwap : Perm P2 where
  toFun := swap2
  invFun := swap2
  leftInv := by intro a; cases a <;> rfl
  rightInv := by intro a; cases a <;> rfl

def psi : C2 -> Perm P2
  | .e => permId
  | .x => singleSwap

theorem psi_preserves_mul : PreservesC2Mul psi := by
  intro g h z
  cases g <;> cases h <;> cases z <;> rfl

theorem psi_injective : Injective psi := by
  intro a b h
  cases a <;> cases b
  · rfl
  · have bad : P2.q0 = P2.q1 :=
      congrArg (fun p : Perm P2 => p.toFun .q0) h
    cases bad
  · have bad : P2.q1 = P2.q0 :=
      congrArg (fun p : Perm P2 => p.toFun .q0) h
    cases bad
  · rfl

theorem psi_x_has_exact_order_two : ExactOrderTwoPerm (psi .x) := by
  refine And.intro ?_ ?_
  · exact Exists.intro P2.q0 (by decide)
  · intro a
    cases a <;> rfl

theorem psi_x_is_single_transposition : IsSingleTransposition (psi .x) := by
  refine Exists.intro P2.q0 (Exists.intro P2.q1 ?_)
  refine And.intro (by decide) ?_
  refine And.intro rfl ?_
  refine And.intro rfl ?_
  intro z hz0 hz1
  cases z with
  | q0 => exact (hz0 rfl).elim
  | q1 => exact (hz1 rfl).elim

/-! Negative control: the same nonvacuous premises can have the claimed result. -/
theorem reddit_learnmath_14s0k9c_negative_control :
    C2Exhaustive /\
    C2GroupLaws /\
    ExactOrderTwoC2 .x /\
    PreservesC2Mul psi /\
    Injective psi /\
    ExactOrderTwoPerm (psi .x) /\
    IsSingleTransposition (psi .x) := by
  exact And.intro c2_exhaustive
    (And.intro c2_group_laws
      (And.intro x_has_exact_order_two
        (And.intro psi_preserves_mul
          (And.intro psi_injective
            (And.intro psi_x_has_exact_order_two
              psi_x_is_single_transposition)))))

end RedditLearnmath14s0k9c

#print axioms RedditLearnmath14s0k9c.is
#print axioms RedditLearnmath14s0k9c.c2_exhaustive
#print axioms RedditLearnmath14s0k9c.c2_group_laws
#print axioms RedditLearnmath14s0k9c.x_has_exact_order_two
#print axioms RedditLearnmath14s0k9c.perm_comp_assoc_pointwise
#print axioms RedditLearnmath14s0k9c.perm_id_left_pointwise
#print axioms RedditLearnmath14s0k9c.perm_id_right_pointwise
#print axioms RedditLearnmath14s0k9c.perm_inv_left_pointwise
#print axioms RedditLearnmath14s0k9c.perm_inv_right_pointwise
#print axioms RedditLearnmath14s0k9c.phi_preserves_mul
#print axioms RedditLearnmath14s0k9c.phi_injective
#print axioms RedditLearnmath14s0k9c.phi_x_has_exact_order_two
#print axioms RedditLearnmath14s0k9c.phi_x_is_not_single_transposition
#print axioms RedditLearnmath14s0k9c.reddit_learnmath_14s0k9c_refutation
#print axioms RedditLearnmath14s0k9c.psi_preserves_mul
#print axioms RedditLearnmath14s0k9c.psi_injective
#print axioms RedditLearnmath14s0k9c.psi_x_has_exact_order_two
#print axioms RedditLearnmath14s0k9c.psi_x_is_single_transposition
#print axioms RedditLearnmath14s0k9c.reddit_learnmath_14s0k9c_negative_control
