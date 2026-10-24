import Mathlib.Data.Nat.Basic
import Mathlib.Logic.Relation

/-!
Record: proofwiki_4209__codex_expansion
Source: ProofWiki, "Combination of Recursive Functions"
https://proofwiki.org/wiki/Combination_of_Recursive_Functions

Exact scope: this certificate refutes the local, load-bearing assertion that,
for the theorem's arbitrary relation `R`, a URM program computing `chi_R` is
guaranteed to exist.  It does not refute the combination theorem after adding
the missing premise that the characteristic function of `R` is recursive.

Witness: URM programs are numbered by all natural numbers through the explicit
finite-program decoder below.  Instructions are `Z`, `S`, `T`, and `J`; nested
pairs use the computable coding `2^a * (2*b+1) - 1`, and finite instruction
lists use a terminating fuelled decoder.  The operational semantics is the
exact deterministic small-step function `stepCode`; `Halts q x y` means that a
finite run from input `x` reaches a terminal configuration with register 1
equal to `y`.  Program counters and jump targets are zero-based, registers are
natural-numbered, input and output both use register 1, all other registers
start at zero, and a counter outside the decoded list is halt.  Allowing register 0 only enlarges the usual positive-register instruction
class. Program-counter numbering starts at zero and uses the corresponding
jump convention throughout; no bound is imposed on program or run length.  Define `diagonalRelation n := not Halts n n 1`.

`ComputesChar` records every load-bearing part of characteristic-function
computation: on every input the program halts, its output is 0 or 1, all its
halting outputs agree with that output (the functional/deterministic content
of "computes"), and output 1 is equivalent to membership.  At a purported
self-code `q`, output 1 contradicts the definition of the relation, while
output 0 and output uniqueness rule out halting with 1 and hence force output
1.  This is an unbounded diagonal proof over every natural program code, not a
bounded test.

Source-faithful surrounding instantiation: `k = 1`; `f`, `g`, and `h` are the
total constant-zero functions.  The encoded one-instruction program `Z(1)`
followed by halt computes all three.  Both source definedness implications,
both branch equations, and totality of `h` are certified explicitly.  Thus the
diagonal relation satisfies the only stated condition that `R` is arbitrary,
although equal branches make `h` recursive in this particular instance.  The
failure certified here is precisely the claimed existence of `P_R`.

Negative control and correction: `falseRelation` has characteristic function
computed by the independently displayed code 4 for `Z(1)` followed by halt,
for every natural input.  This detects a vacuous halting relation, a uniformly
false computation conclusion, or omission of total Boolean output.  The four
sample inputs 0, 1, 7, and 100 from the Terra audit are therefore not used as
evidence for the diagonal theorem.  `corrected_characteristic_premise` also
records the required correction: existence follows when existence of a URM
program for the characteristic function is assumed. Instruction lookup uses
Lean’s list lookup, and finite runs use Mathlib’s reflexive transitive closure. The coding roundtrip proves that every finite
URM program is represented. All proofs are checked by the Lean kernel.
-/

namespace ProofWiki4209CodexExpansion

inductive Instruction where
  | zero : Nat -> Instruction
  | succ : Nat -> Instruction
  | transfer : Nat -> Nat -> Instruction
  | jump : Nat -> Nat -> Nat -> Instruction
  deriving DecidableEq

abbrev Program := List Instruction

def pairCode (a b : Nat) : Nat :=
  2 ^ a * (2 * b + 1) - 1

def unpairAux : Nat -> Nat -> Nat × Nat
  | 0, n => (0, n)
  | fuel + 1, n =>
      if n % 2 = 0 then
        let p := unpairAux fuel (n / 2)
        (p.1 + 1, p.2)
      else
        (0, n / 2)

def unpair (n : Nat) : Nat × Nat :=
  unpairAux (n + 1) (n + 1)

theorem unpairAux_pair (a b fuel : Nat) (hfuel : a < fuel) :
    unpairAux fuel (2 ^ a * (2 * b + 1)) = (a, b) := by
  induction a generalizing fuel with
  | zero =>
      cases fuel with
      | zero => omega
      | succ fuel =>
          simp only [Nat.pow_zero, Nat.one_mul, unpairAux]
          have hodd : (2 * b + 1) % 2 ≠ 0 := by omega
          simp only [hodd, ↓reduceIte]
          congr 1
          omega
  | succ a ih =>
      cases fuel with
      | zero => omega
      | succ fuel =>
          have hpow : 2 ^ (a + 1) * (2 * b + 1) =
              2 * (2 ^ a * (2 * b + 1)) := by
            simp [Nat.pow_succ, Nat.mul_left_comm, Nat.mul_comm]
          rw [hpow, unpairAux]
          simp only [Nat.mul_mod_right, ↓reduceIte,
            Nat.mul_div_cancel_left _ (by decide : 0 < 2)]
          rw [ih fuel (by omega)]

theorem unpair_pairCode (a b : Nat) : unpair (pairCode a b) = (a, b) := by
  have hpositive : 0 < 2 ^ a * (2 * b + 1) :=
    Nat.mul_pos (Nat.pow_pos (by decide)) (by omega)
  have habound : a < 2 ^ a * (2 * b + 1) :=
    lt_of_lt_of_le Nat.lt_two_pow_self
      (Nat.le_mul_of_pos_right _ (by omega))
  unfold unpair pairCode
  rw [Nat.sub_add_cancel (by omega : 1 ≤ 2 ^ a * (2 * b + 1))]
  exact unpairAux_pair a b _ habound

def encodeInstruction : Instruction -> Nat
  | .zero r => pairCode 0 r
  | .succ r => pairCode 1 r
  | .transfer m n => pairCode 2 (pairCode m n)
  | .jump m n target => pairCode 3 (pairCode m (pairCode n target))

def decodeInstruction (n : Nat) : Instruction :=
  let tagPayload := unpair n
  match tagPayload.1 % 4 with
  | 0 => .zero tagPayload.2
  | 1 => .succ tagPayload.2
  | 2 =>
      let operands := unpair tagPayload.2
      .transfer operands.1 operands.2
  | _ =>
      let firstRest := unpair tagPayload.2
      let secondTarget := unpair firstRest.2
      .jump firstRest.1 secondTarget.1 secondTarget.2

theorem decodeInstruction_encodeInstruction (i : Instruction) :
    decodeInstruction (encodeInstruction i) = i := by
  cases i <;> simp [encodeInstruction, decodeInstruction, unpair_pairCode]

def encodeProgram : Program -> Nat
  | [] => 0
  | i :: rest => pairCode (encodeInstruction i) (encodeProgram rest) + 1

def decodeProgramAux : Nat -> Nat -> Program
  | 0, _ => []
  | _ + 1, 0 => []
  | fuel + 1, code + 1 =>
      let headTail := unpair code
      decodeInstruction headTail.1 :: decodeProgramAux fuel headTail.2

def decodeProgram (code : Nat) : Program :=
  decodeProgramAux code code

theorem length_le_encodeProgram (p : Program) : p.length ≤ encodeProgram p := by
  induction p with
  | nil => rfl
  | cons i rest ih =>
      simp only [List.length_cons, encodeProgram]
      have hpow : 0 < 2 ^ encodeInstruction i := Nat.pow_pos (by decide)
      have hlarge := Nat.le_mul_of_pos_left (2 * encodeProgram rest + 1) hpow
      unfold pairCode
      omega

theorem decodeProgramAux_encodeProgram (p : Program) (fuel : Nat)
    (hfuel : p.length ≤ fuel) : decodeProgramAux fuel (encodeProgram p) = p := by
  induction p generalizing fuel with
  | nil => cases fuel <;> rfl
  | cons i rest ih =>
      cases fuel with
      | zero => simp at hfuel
      | succ fuel =>
          simp only [encodeProgram, decodeProgramAux, unpair_pairCode,
            decodeInstruction_encodeInstruction]
          rw [ih fuel (by simpa using hfuel)]

theorem decodeProgram_encodeProgram (p : Program) :
    decodeProgram (encodeProgram p) = p :=
  decodeProgramAux_encodeProgram p _ (length_le_encodeProgram p)

theorem decodeProgram_surjective : Function.Surjective decodeProgram := by
  intro p
  exact ⟨encodeProgram p, decodeProgram_encodeProgram p⟩

def zOneProgram : Program := [.zero 1]

def zOneCode : Nat := encodeProgram zOneProgram

structure Config where
  pc : Nat
  regs : Nat -> Nat

def writeReg (regs : Nat -> Nat) (r value : Nat) : Nat -> Nat :=
  fun i => if i = r then value else regs i

def initialRegisters (input : Nat) : Nat -> Nat :=
  fun r => if r = 1 then input else 0

def initialConfig (input : Nat) : Config :=
  { pc := 0, regs := initialRegisters input }

def executeInstruction (i : Instruction) (c : Config) : Config :=
  match i with
  | .zero r =>
      { pc := c.pc + 1, regs := writeReg c.regs r 0 }
  | .succ r =>
      { pc := c.pc + 1, regs := writeReg c.regs r (c.regs r + 1) }
  | .transfer m n =>
      { pc := c.pc + 1, regs := writeReg c.regs n (c.regs m) }
  | .jump m n target =>
      if c.regs m = c.regs n then
        { pc := target, regs := c.regs }
      else
        { pc := c.pc + 1, regs := c.regs }

abbrev instructionAt (program : Program) (pc : Nat) : Option Instruction :=
  program[pc]?

def stepProgram (program : Program) (c : Config) : Option Config :=
  match instructionAt program c.pc with
  | none => none
  | some i => some (executeInstruction i c)

def stepCode (code : Nat) (c : Config) : Option Config :=
  stepProgram (decodeProgram code) c

@[simp] theorem stepCode_encodeProgram (p : Program) (c : Config) :
    stepCode (encodeProgram p) c = stepProgram p c := by
  simp only [stepCode, decodeProgram_encodeProgram]

abbrev Reaches (code : Nat) : Config -> Config -> Prop :=
  Relation.ReflTransGen (fun c d => stepCode code c = some d)

def HaltsProgram (program : Program) (input output : Nat) : Prop :=
  Exists fun c =>
    Relation.ReflTransGen (fun c d => stepProgram program c = some d)
      (initialConfig input) c /\
    stepProgram program c = none /\
    c.regs 1 = output

def Halts (code input output : Nat) : Prop :=
  HaltsProgram (decodeProgram code) input output

@[simp] theorem halts_encodeProgram (program : Program) (input output : Nat) :
    Halts (encodeProgram program) input output ↔ HaltsProgram program input output := by
  simp only [Halts, decodeProgram_encodeProgram]

theorem haltsProgram_output_unique {program : Program} {input a b : Nat}
    (ha : HaltsProgram program input a) (hb : HaltsProgram program input b) : a = b := by
  rcases ha with ⟨ca, arun, astop, aval⟩
  rcases hb with ⟨cb, brun, bstop, bval⟩
  have unique : Relator.RightUnique (fun c d => stepProgram program c = some d) := by
    intro c d e hd he
    exact Option.some.inj (hd.symm.trans he)
  have equal : ca = cb := by
    rcases Relation.ReflTransGen.total_of_right_unique unique arun brun with run | run
    · have dead : ∀ c, ¬ stepProgram program ca = some c := by
        intro c step
        rw [astop] at step
        contradiction
      exact ((Relation.reflTransGen_iff_eq dead).mp run).symm
    · have dead : ∀ c, ¬ stepProgram program cb = some c := by
        intro c step
        rw [bstop] at step
        contradiction
      exact (Relation.reflTransGen_iff_eq dead).mp run
  subst cb
  exact aval.symm.trans bval

theorem halts_output_unique {code input a b : Nat}
    (ha : Halts code input a) (hb : Halts code input b) : a = b :=
  haltsProgram_output_unique ha hb

def ComputesFunction (code : Nat) (function : Nat -> Nat) : Prop :=
  forall input,
    Halts code input (function input) /\
    forall output, Halts code input output -> output = function input

def ComputesProgramChar (program : Program) (relation : Nat -> Prop) : Prop :=
  forall input, Exists fun output =>
    (output = 0 \/ output = 1) /\
    HaltsProgram program input output /\
    (forall other, HaltsProgram program input other -> other = output) /\
    (output = 1 <-> relation input)

def ComputesChar (code : Nat) (relation : Nat -> Prop) : Prop :=
  ComputesProgramChar (decodeProgram code) relation

@[simp] theorem computesChar_encodeProgram (program : Program) (relation : Nat -> Prop) :
    ComputesChar (encodeProgram program) relation ↔ ComputesProgramChar program relation := by
  simp only [ComputesChar, decodeProgram_encodeProgram]

def diagonalRelation (n : Nat) : Prop :=
  Not (Halts n n 1)

def falseRelation (_ : Nat) : Prop := False

def constantZero (_ : Nat) : Nat := 0

def k : Nat := 1
def f : Nat -> Nat := constantZero
def g : Nat -> Nat := constantZero
def h : Nat -> Nat := constantZero

def DefinedAt (function : Nat -> Nat) (input : Nat) : Prop :=
  Exists fun output => function input = output

def SourceInstantiation : Prop :=
  k = 1 /\
  ComputesFunction zOneCode f /\
  ComputesFunction zOneCode g /\
  ComputesFunction zOneCode h /\
  (forall n, diagonalRelation n -> DefinedAt f n) /\
  (forall n, Not (diagonalRelation n) -> DefinedAt g n) /\
  (forall n, DefinedAt h n) /\
  (forall n, diagonalRelation n -> h n = f n) /\
  (forall n, Not (diagonalRelation n) -> h n = g n)

def afterZOne (input : Nat) : Config :=
  { pc := 1, regs := writeReg (initialRegisters input) 1 0 }

theorem zOne_code_is_four : zOneCode = 4 := by
  decide

theorem zOne_decoder : decodeProgram zOneCode = zOneProgram := by
  decide

theorem zOne_step (input : Nat) :
    stepCode zOneCode (initialConfig input) = some (afterZOne input) := by
  unfold stepCode
  rw [zOne_decoder]
  rfl

theorem zOne_terminal (input : Nat) :
    stepCode zOneCode (afterZOne input) = none := by
  unfold stepCode
  rw [zOne_decoder]
  rfl

theorem reaches_zOne_cases (input : Nat) {c : Config}
    (run : Reaches zOneCode (initialConfig input) c) :
    c = initialConfig input \/ c = afterZOne input := by
  induction run with
  | refl =>
      exact Or.inl rfl
  | @tail previous current earlier step ih =>
      cases ih with
      | inl atStart =>
          subst previous
          have same : some (afterZOne input) = some current :=
            (zOne_step input).symm.trans step
          cases same
          exact Or.inr rfl
      | inr atAfter =>
          subst previous
          have impossible : (none : Option Config) = some current :=
            (zOne_terminal input).symm.trans step
          cases impossible

theorem zOne_halts (input : Nat) : Halts zOneCode input 0 := by
  refine Exists.intro (afterZOne input) ?_
  refine And.intro ?_ (And.intro (zOne_terminal input) ?_)
  · exact Relation.ReflTransGen.tail Relation.ReflTransGen.refl (zOne_step input)
  · rfl

theorem zOne_halts_only_zero {input output : Nat}
    (halts : Halts zOneCode input output) : output = 0 := by
  rcases halts with ⟨c, run, terminal, value⟩
  cases reaches_zOne_cases input run with
  | inl atStart =>
      subst c
      have impossible : some (afterZOne input) = (none : Option Config) :=
        (zOne_step input).symm.trans terminal
      cases impossible
  | inr atAfter =>
      subst c
      change 0 = output at value
      exact value.symm

theorem zOne_computes_constant_zero :
    ComputesFunction zOneCode constantZero := by
  intro input
  constructor
  · exact zOne_halts input
  · intro output halts
    exact zOne_halts_only_zero halts

theorem source_instantiation_holds : SourceInstantiation := by
  refine And.intro rfl ?_
  refine And.intro zOne_computes_constant_zero ?_
  refine And.intro zOne_computes_constant_zero ?_
  refine And.intro zOne_computes_constant_zero ?_
  refine And.intro ?_ ?_
  · intro n _
    exact Exists.intro 0 rfl
  · refine And.intro ?_ ?_
    · intro n _
      exact Exists.intro 0 rfl
    · refine And.intro ?_ ?_
      · intro n
        exact Exists.intro 0 rfl
      · refine And.intro ?_ ?_
        · intro n _
          rfl
        · intro n _
          rfl

theorem no_code_computes_diagonal_characteristic (q : Nat) :
    Not (ComputesChar q diagonalRelation) := by
  intro computes
  rcases computes q with ⟨output, boolean, halts, unique, characteristic⟩
  cases boolean with
  | inl isZero =>
      subst output
      have noOne : Not (Halts q q 1) := by
        intro haltsOne
        have impossible : 1 = 0 := unique 1 haltsOne
        cases impossible
      have member : diagonalRelation q := noOne
      have impossible : 0 = 1 := characteristic.mpr member
      cases impossible
  | inr isOne =>
      subst output
      have member : diagonalRelation q := characteristic.mp rfl
      exact member halts

/- The named load-bearing refutation includes the complete constant-zero
source instantiation and rejects every unbounded natural program code. -/
theorem refutes_arbitrary_relation_program_guarantee :
    SourceInstantiation /\
    Not (Exists fun q => ComputesChar q diagonalRelation) := by
  constructor
  · exact source_instantiation_holds
  · intro purported
    rcases purported with ⟨q, computes⟩
    exact no_code_computes_diagonal_characteristic q computes

/- This version states the local refutation directly for arbitrary finite URM
instruction lists. Its independent program semantics is connected to code
semantics by the proved coding roundtrip, rather than by an assumed enumeration. -/
theorem refutes_arbitrary_relation_for_all_programs :
    SourceInstantiation /\
    Function.Surjective decodeProgram /\
    Not (Exists fun program : Program => ComputesProgramChar program diagonalRelation) := by
  refine ⟨source_instantiation_holds, decodeProgram_surjective, ?_⟩
  rintro ⟨program, computes⟩
  exact no_code_computes_diagonal_characteristic (encodeProgram program)
    ((computesChar_encodeProgram program diagonalRelation).mpr computes)

def RecursiveCharacteristic (relation : Nat -> Prop) : Prop :=
  Exists fun q => ComputesChar q relation

theorem corrected_characteristic_premise (relation : Nat -> Prop)
    (recursive : RecursiveCharacteristic relation) :
    Exists fun q => ComputesChar q relation :=
  recursive

/- Meaningful negative control: the explicit Z(1)-then-halt code really is
decoded, halts on every input with unique output zero, and computes the
characteristic function of the everywhere-false relation. -/
theorem negative_control_false_relation :
    zOneCode = 4 /\
    decodeProgram zOneCode = [.zero 1] /\
    ComputesChar zOneCode falseRelation := by
  refine And.intro zOne_code_is_four (And.intro zOne_decoder ?_)
  intro input
  refine Exists.intro 0 ?_
  refine And.intro (Or.inl rfl) ?_
  refine And.intro (zOne_halts input) ?_
  refine And.intro ?_ ?_
  · intro output halts
    exact zOne_halts_only_zero halts
  · constructor
    · intro impossible
      cases impossible
    · intro impossible
      cases impossible

end ProofWiki4209CodexExpansion
