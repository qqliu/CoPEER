/-!
# Sanity companion to `ShortZeroSums_Conjecture.lean` (2026-09-20)

Why this file exists. `Gen.not_conjecture62` refutes a universal statement by ONE instance, so it
evaluates the general definitions at one list ([2,2,2,2]), one k and one branch. The second targeted
review (`TARGETED_REVIEW_retained_general_wrapper.md`) showed that three one-line mutants of the GENERAL
definitions (exponent read as the first factor; divisibility reversed in `Chain`; addition modulo 2 in
place of modulo n_i) leave that theorem compiling, and that the lower branch of the conjecture is idle.
The binding of the general definitions therefore needs support of another kind. This file retains the
reviewer's two probes, which supply it:

* namespace of Appendix A: an independent statement of Conjecture 6.2 written from the TeX source in a
  different idiom (sub-multisets through `List.count`, least elements, a value in N with +infinity),
  proved EQUIVALENT to `Gen.Conjecture62`;
* namespace of Appendix B: the body of `Gen.Conjecture62` PROVED at groups where the source's statement
  is true: C_2 + C_2, C_2^3 (both branches) and C_2 + C_4 (a modulus other than 2, a chain whose
  direction matters, exponent = last factor). Together these reject all three surviving mutants.

Text: `ShortZeroSums_Conjecture.lean` verbatim, then Appendix A and Appendix B of the review verbatim
with their import lines removed. The probes are the reviewer's text, assembled by the certificate's
author; this assembled file has not had a review of its own. Provenance unchanged: an inconsistency
internal to the source (class (d)); no model call was involved in finding it; silent about the
conjecture with C_2^4 excluded.
-/

/-!
# Extended file: the certificate below verbatim, then Conjecture 6.2 stated over general definitions and its negation as one theorem (2026-09-20)

The namespace `ShortZeroSums` is `ShortZeroSums.lean` unchanged (sha256 29af0369fa3d..., the file both
adversarial reviews examined). The namespace `Gen` is the general statement that the targeted review of
2026-09-20 (`TARGETED_REVIEW_not_conjecture62_at_G.md`, Appendix B) wrote from the source text and asked
to be retained: `Gen.Conjecture62` quantifies over ALL invariant-factor lists 1 < n_1 | ... | n_r, and
`Gen.not_conjecture62 : ¬ Gen.Conjecture62` is derived from `ShortZeroSums.not_conjecture62_at_G`.
The text of `Gen` is the reviewer's, with the import line removed and one docstring extended as the
review's must-fix item 1 requires; the retained form has not had an independent review of its own.
-/

/-!
# Kernel certificate: printed Conjecture 6.2 of arXiv:2506.21383v1 fails at G = C_2^4, k = 2 (2026-09-19)

SOURCE-INTERNAL INCONSISTENCY, NOT A MODEL DISCOVERY. The same paper states D(C_2^4) = 5 and
s_{<=3}(C_2^4) = 9 (remark after Theorem 1.11; Lemma 1.7(iii)) and excludes C_2^4 from Theorem 1.11
and Conjecture 6.1, but not from Conjecture 6.2.

NEW dated artifact, outside the frozen 285-record release. Core Lean only: no Mathlib, no `sorry`,
no `native_decide`.

Source (K. Zhao, *On zero-sum subsequences in a finite abelian group of length not exceeding a given
number*, arXiv:2506.21383v1, read from the arXiv PDF on 2026-09-19; quotes in BINDING.md).
G = C_{n_1} + ... + C_{n_r} with 1 < n_1 | ... | n_r; r(G) = r; exp(G) = n_r;
D*(G) = 1 + sum (n_i - 1); D(G) = the smallest positive integer t such that every sequence S over G
of length |S| >= t has a nonempty zero-sum subsequence; s_{<=k}(G) = the smallest positive integer
l (or +infinity) such that each sequence of length l has a nonempty zero-sum subsequence of length
at most k. Conjecture 6.2: for r(G) >= 2, D(G) = D*(G), k a positive integer with
D(G) - k in [exp(G), D(G)]: if D(G) - k >= (D(G)+1)/2 then s_{<=D(G)-k}(G) <= D(G) + k; if
D(G) - k < (D(G)+1)/2 then s_{<=D(G)-k}(G) > D(G) + k.

Model used here. An element of G = C_2^4 is a natural number below 16 read as a vector of four
binary digits; the group sum is bitwise XOR (`group_is_C2_pow_4`: XOR is coordinatewise addition
modulo 2, and the four coordinates identify {0, ..., 15} with (Z/2)^4). A sequence is a `List Nat`
with all entries below 16 (repetitions allowed). A subsequence is a `List.Sublist` (a selection of
positions); since G is abelian the order of terms does not affect sums.

Certified:
* `group_is_C2_pow_4`     the carrier with XOR is C_2 + C_2 + C_2 + C_2;
* `dav_upper`             every sequence over G of length >= 5 has a nonempty zero-sum subsequence
                          (pruned exhaustive search over ordered tuples, evaluated by the kernel and
                          proved sound; no sorting or symmetry argument);
* `davenport_eq_five`     D(G) = 5 in the source's sense (5 has the property, no positive t < 5 has);
                          `davenport_unique`: no other value satisfies that definition;
* `short_lower`           for EVERY l <= 8 there is a sequence over G of length exactly l with no
                          nonempty zero-sum subsequence of length at most 3;
* `refutes_conjecture_6_2` the hypotheses of Conjecture 6.2 hold at G = C_2^4, k = 2 and its
                          conclusion s_{<=3}(G) <= 7 fails;
* `not_conjecture62_at_G` the negation of Conjecture 6.2 specialised to this one group.

NOT certified here: the matching upper bound s_{<=3}(C_2^4) <= 9 (the source's exact value 9 is not
needed: the refutation only uses s_{<=3}(C_2^4) > 8 >= 7), and nothing about any other group.
-/
set_option maxRecDepth 100000

namespace ShortZeroSums

/-! ## The group C_2^4 -/

/-- The i-th coordinate, in Z/2 = {0, 1}, of a group element. -/
def coord (i a : Nat) : Nat := a / 2 ^ i % 2

/-- ({0, ..., 15}, XOR) is C_2 + C_2 + C_2 + C_2: closed; XOR is coordinatewise addition modulo 2;
0 is the zero vector; the four coordinates determine the element; every coordinate vector
(c0, c1, c2, c3) occurs, as the element c0 + 2 c1 + 4 c2 + 8 c3. -/
theorem group_is_C2_pow_4 :
    (∀ a, a < 16 → ∀ b, b < 16 → (a ^^^ b) < 16 ∧
        ∀ i, i < 4 → coord i (a ^^^ b) = (coord i a + coord i b) % 2) ∧
    (∀ i, i < 4 → coord i 0 = 0) ∧
    (∀ a, a < 16 → ∀ b, b < 16 → (∀ i, i < 4 → coord i a = coord i b) → a = b) ∧
    (∀ c0, c0 < 2 → ∀ c1, c1 < 2 → ∀ c2, c2 < 2 → ∀ c3, c3 < 2 →
        c0 + 2 * c1 + 4 * c2 + 8 * c3 < 16 ∧
        coord 0 (c0 + 2 * c1 + 4 * c2 + 8 * c3) = c0 ∧ coord 1 (c0 + 2 * c1 + 4 * c2 + 8 * c3) = c1 ∧
        coord 2 (c0 + 2 * c1 + 4 * c2 + 8 * c3) = c2 ∧ coord 3 (c0 + 2 * c1 + 4 * c2 + 8 * c3) = c3) :=
  ⟨by decide +kernel, by decide +kernel, by decide +kernel, by
    intro c0 h0 c1 h1 c2 h2 c3 h3
    simp only [coord]
    omega⟩

/-- ({0, ..., 15}, XOR, 0) satisfies the abelian group axioms; every element is its own inverse. -/
theorem group_axioms :
    (∀ a, a < 16 → ∀ b, b < 16 → ∀ c, c < 16 → (a ^^^ b) ^^^ c = a ^^^ (b ^^^ c)) ∧
    (∀ a, a < 16 → ∀ b, b < 16 → a ^^^ b = b ^^^ a) ∧
    (∀ a, a < 16 → 0 ^^^ a = a ∧ a ^^^ 0 = a) ∧
    (∀ a, a < 16 → a ^^^ a = 0) :=
  ⟨fun a _ b _ c _ => Nat.xor_assoc a b c, fun a _ b _ => Nat.xor_comm a b,
    fun a _ => ⟨Nat.zero_xor a, Nat.xor_zero a⟩, fun a _ => Nat.xor_self a⟩

/-- Invariant factors 1 < n_1 | n_2 | n_3 | n_4 of C_2^4. -/
def invFactors : List Nat := [2, 2, 2, 2]

def lastOf : List Nat → Nat
  | [] => 0
  | [x] => x
  | _ :: y :: t => lastOf (y :: t)

def sumMinusOne : List Nat → Nat
  | [] => 0
  | n :: t => (n - 1) + sumMinusOne t

def prodOf : List Nat → Nat
  | [] => 1
  | n :: t => n * prodOf t

/-- r(G) = r, the number of invariant factors. -/
def rank : Nat := invFactors.length
/-- exp(G) = n_r. -/
def expo : Nat := lastOf invFactors
/-- D*(G) = 1 + sum (n_i - 1). -/
def dStar : Nat := 1 + sumMinusOne invFactors

theorem invariants :
    rank = 4 ∧ expo = 2 ∧ dStar = 5 ∧ prodOf invFactors = 16 ∧
    (∀ n, n ∈ invFactors → 1 < n ∧ n ∣ expo) := by
  refine ⟨by decide, by decide, by decide, by decide, ?_⟩
  intro n hn
  have : n = 2 := by simpa [invFactors] using hn
  subst this
  exact ⟨by decide, by decide⟩

/-- Cross-check of the exponent on the carrier: 2 g = 0 for every g, and some g is not 0. -/
theorem exponent_two : (∀ a, a < 16 → a ^^^ a = 0) ∧ (∃ a, a < 16 ∧ a ≠ 0) :=
  ⟨by decide +kernel, by decide +kernel⟩

/-! ## Sequences, subsequences, the two invariants -/

/-- The sum in G of the terms of a sequence. -/
def sigma : List Nat → Nat
  | [] => 0
  | x :: t => x ^^^ sigma t

/-- S is a sequence over G. -/
def OverG (S : List Nat) : Prop := ∀ x, x ∈ S → x < 16

/-- S has a nonempty zero-sum subsequence. -/
def HasZS (S : List Nat) : Prop :=
  ∃ T : List Nat, T.Sublist S ∧ T ≠ [] ∧ sigma T = 0

/-- S has a nonempty zero-sum subsequence of length at most h. -/
def HasShortZS (h : Nat) (S : List Nat) : Prop :=
  ∃ T : List Nat, T.Sublist S ∧ T ≠ [] ∧ T.length ≤ h ∧ sigma T = 0

/-- "every sequence S over G of length |S| >= t has a nonempty zero-sum subsequence". -/
def DavProp (t : Nat) : Prop := ∀ S : List Nat, OverG S → t ≤ S.length → HasZS S

/-- D(G) = d: d is the smallest positive integer t with `DavProp t`. -/
def IsDavenport (d : Nat) : Prop := 0 < d ∧ DavProp d ∧ ∀ t, 0 < t → DavProp t → d ≤ t

/-- "each sequence of length l has a non-empty zero-sum subsequence of length at most h". -/
def ShortProp (h l : Nat) : Prop := ∀ S : List Nat, OverG S → S.length = l → HasShortZS h S

/-- The variant with "length at least l" (recorded because D(G) is phrased that way). -/
def ShortPropGe (h l : Nat) : Prop := ∀ S : List Nat, OverG S → l ≤ S.length → HasShortZS h S

/-- "s_{<=h}(G) <= B": the smallest positive integer l with `ShortProp h l` is at most B
(in particular it is not +infinity). -/
def sShortAtMost (h B : Nat) : Prop := ∃ l, 0 < l ∧ l ≤ B ∧ ShortProp h l

/-! ## Completeness of the computed list of short sub-sums (used for the two free witnesses) -/

/-- Sums of all subsequences with at most h terms, the empty one included. -/
def sumsLe : List Nat → Nat → List Nat
  | [], _ => [0]
  | _ :: _, 0 => [0]
  | x :: t, h + 1 => sumsLe t (h + 1) ++ (sumsLe t h).map (· ^^^ x)

/-- Sums of all NONEMPTY subsequences with at most h terms. -/
def neSumsLe : List Nat → Nat → List Nat
  | [], _ => []
  | _ :: _, 0 => []
  | x :: t, h + 1 => neSumsLe t (h + 1) ++ (sumsLe t h).map (· ^^^ x)

theorem sigma_mem_sumsLe : ∀ (S : List Nat) (h : Nat) (T : List Nat),
    T.Sublist S → T.length ≤ h → sigma T ∈ sumsLe S h
  | [], h, T, hs, _ => by
    cases hs
    simp [sumsLe, sigma]
  | x :: t, 0, T, _, hl => by
    have : T = [] := List.eq_nil_of_length_eq_zero (by omega)
    subst this
    simp [sumsLe, sigma]
  | x :: t, h + 1, T, hs, hl => by
    simp only [sumsLe, List.mem_append, List.mem_map]
    cases hs
    · rename_i hs'
      exact Or.inl (sigma_mem_sumsLe t (h + 1) T hs' hl)
    · rename_i T' hs'
      refine Or.inr ⟨sigma T', sigma_mem_sumsLe t h T' hs' ?_, ?_⟩
      · simp only [List.length_cons] at hl; omega
      · simp only [sigma]; exact Nat.xor_comm _ _

theorem sigma_mem_neSumsLe : ∀ (S : List Nat) (h : Nat) (T : List Nat),
    T.Sublist S → T ≠ [] → T.length ≤ h → sigma T ∈ neSumsLe S h
  | [], h, T, hs, hne, _ => by
    cases hs
    exact absurd rfl hne
  | x :: t, 0, T, _, hne, hl => by
    have : T = [] := List.eq_nil_of_length_eq_zero (by omega)
    exact absurd this hne
  | x :: t, h + 1, T, hs, hne, hl => by
    simp only [neSumsLe, List.mem_append, List.mem_map]
    cases hs
    · rename_i hs'
      exact Or.inl (sigma_mem_neSumsLe t (h + 1) T hs' hne hl)
    · rename_i T' hs'
      refine Or.inr ⟨sigma T', sigma_mem_sumsLe t h T' hs' ?_, ?_⟩
      · simp only [List.length_cons] at hl; omega
      · simp only [sigma]; exact Nat.xor_comm _ _

/-- If 0 is not among the computed nonempty short sub-sums, S has no nonempty zero-sum
subsequence of length at most h. -/
theorem no_short_of_check (h : Nat) (S : List Nat)
    (hc : (neSumsLe S h).all (fun s => s != 0) = true) : ¬ HasShortZS h S := by
  intro ⟨T, hs, hne, hl, hz⟩
  have hm := sigma_mem_neSumsLe S h T hs hne hl
  rw [hz] at hm
  have := (List.all_eq_true.mp hc) 0 hm
  simp at this

theorem overG_of_all (S : List Nat) (hc : S.all (fun x => decide (x < 16)) = true) : OverG S := by
  intro x hx
  have := (List.all_eq_true.mp hc) x hx
  simpa using this

theorem hasShort_of_hasZS (S : List Nat) : HasZS S → HasShortZS S.length S := by
  intro ⟨T, hs, hne, hz⟩
  exact ⟨T, hs, hne, hs.length_le, hz⟩

/-! ## The Davenport constant: upper bound by a pruned exhaustive search -/

/-- The set of entries of a list of naturals as a bit mask. -/
def mask : List Nat → Nat
  | [] => 0
  | y :: t => 2 ^ y ||| mask t

theorem mem_of_mask : ∀ (s : List Nat) (x : Nat), (mask s).testBit x = true → x ∈ s
  | [], x, h => by simp [mask] at h
  | y :: t, x, h => by
    simp only [mask, Nat.testBit_or, Bool.or_eq_true, Nat.testBit_two_pow,
      decide_eq_true_eq] at h
    rcases h with h | h
    · subst h; exact List.mem_cons_self ..
    · exact List.mem_cons_of_mem _ (mem_of_mask t x h)

theorem full_mask : ∀ x, x < 16 → (65535 : Nat).testBit x = true := by decide +kernel

/-- `ok n s`: `s` lists the sums of all subsequences (the empty one included) of a prefix `p`;
every extension of `p` by `n + 1` further elements of G has a nonempty zero-sum subsequence.
A new term x that already is a sub-sum of the prefix closes the branch. At the last level the
test "every x below 16 is a sub-sum of the prefix" is done once, through the bit mask. -/
def ok : Nat → List Nat → Bool
  | 0, s => mask s == 65535
  | n + 1, s => (List.range 16).all fun x =>
      s.any (fun y => y == x) || ok n (s ++ s.map (· ^^^ x))

/-- The branch of the search whose first term is x. -/
def branch (x : Nat) : Bool :=
  [0].any (fun y => y == x) || ok 3 ([0] ++ [0].map (· ^^^ x))

/-! The finite computation, evaluated by the kernel, split by the first term only to bound the
memory of each kernel evaluation. -/
theorem br_00 : ∀ x, x < 2 → branch x = true := by decide +kernel
theorem br_02 : ∀ x, x < 4 → 2 ≤ x → branch x = true := by decide +kernel
theorem br_04 : ∀ x, x < 6 → 4 ≤ x → branch x = true := by decide +kernel
theorem br_06 : ∀ x, x < 8 → 6 ≤ x → branch x = true := by decide +kernel
theorem br_08 : ∀ x, x < 10 → 8 ≤ x → branch x = true := by decide +kernel
theorem br_10 : ∀ x, x < 12 → 10 ≤ x → branch x = true := by decide +kernel
theorem br_12 : ∀ x, x < 14 → 12 ≤ x → branch x = true := by decide +kernel
theorem br_14 : ∀ x, x < 16 → 14 ≤ x → branch x = true := by decide +kernel

theorem br_all (x : Nat) (hx : x < 16) : branch x = true :=
  if h2 : x < 2 then br_00 x h2
  else if h4 : x < 4 then br_02 x h4 (by omega)
  else if h6 : x < 6 then br_04 x h6 (by omega)
  else if h8 : x < 8 then br_06 x h8 (by omega)
  else if h10 : x < 10 then br_08 x h10 (by omega)
  else if h12 : x < 12 then br_10 x h12 (by omega)
  else if h14 : x < 14 then br_12 x h14 (by omega)
  else br_14 x hx (by omega)

/-- The whole search from the empty prefix succeeds. -/
theorem ok_four : ok 4 [0] = true := by
  rw [ok]
  exact List.all_eq_true.mpr (fun x hx => br_all x (List.mem_range.mp hx))

theorem ok_sound : ∀ (n : Nat) (s p : List Nat),
    (∀ y, y ∈ s → ∃ T : List Nat, T.Sublist p ∧ sigma T = y) → ok n s = true →
    ∀ e : List Nat, e.length = n + 1 → OverG e → HasZS (e.reverse ++ p)
  | 0, s, p, inv, h, e, he, hG => by
    match e, he with
    | [x], _ =>
      have hx : x < 16 := hG x (List.mem_cons_self ..)
      have hm : mask s = 65535 := by simpa [ok] using h
      have hmem : x ∈ s := mem_of_mask s x (by rw [hm]; exact full_mask x hx)
      obtain ⟨T, hT, hsum⟩ := inv x hmem
      have hsub : (x :: T).Sublist (x :: p) := List.cons_sublist_cons.mpr hT
      refine ⟨x :: T, ?_, by simp, ?_⟩
      · simpa using hsub
      · simp only [sigma, hsum]; exact Nat.xor_self x
  | n + 1, s, p, inv, h, e, he, hG => by
    cases e with
    | nil => simp at he
    | cons x e' =>
      have hx : x < 16 := hG x (List.mem_cons_self ..)
      have hstep := (List.all_eq_true.mp (by simpa only [ok] using h)) x (List.mem_range.mpr hx)
      have hrw : (x :: e').reverse ++ p = e'.reverse ++ (x :: p) := by
        simp [List.reverse_cons, List.append_assoc]
      rw [hrw]
      rcases (Bool.or_eq_true _ _).mp hstep with hmem | hrec
      · obtain ⟨y, hy, hyx⟩ := List.any_eq_true.mp hmem
        have hyx' : y = x := by simpa using hyx
        subst hyx'
        obtain ⟨T, hT, hsum⟩ := inv y hy
        have hsub : (y :: T).Sublist (y :: p) := List.cons_sublist_cons.mpr hT
        refine ⟨y :: T, ?_, by simp, ?_⟩
        · exact hsub.trans (List.sublist_append_right _ _)
        · simp only [sigma, hsum]; exact Nat.xor_self y
      · refine ok_sound n (s ++ s.map (· ^^^ x)) (x :: p) ?_ hrec e' (by simpa using he)
          (fun y hy => hG y (List.mem_cons_of_mem _ hy))
        intro y hy
        rcases List.mem_append.mp hy with hy | hy
        · obtain ⟨T, hT, hsum⟩ := inv y hy
          exact ⟨T, List.Sublist.cons x hT, hsum⟩
        · obtain ⟨z, hz, rfl⟩ := List.mem_map.mp hy
          obtain ⟨T, hT, hsum⟩ := inv z hz
          have hsub : (x :: T).Sublist (x :: p) := List.cons_sublist_cons.mpr hT
          refine ⟨x :: T, hsub, ?_⟩
          simp only [sigma, hsum]; exact Nat.xor_comm _ _

/-- Every sequence over G of length exactly 5 has a nonempty zero-sum subsequence. -/
theorem dav_five (S : List Nat) (hG : OverG S) (hlen : S.length = 5) : HasZS S := by
  have inv : ∀ y, y ∈ [0] → ∃ T : List Nat, T.Sublist ([] : List Nat) ∧ sigma T = y := by
    intro y hy
    have : y = 0 := by simpa using hy
    subst this
    exact ⟨[], List.Sublist.slnil, rfl⟩
  have h := ok_sound 4 [0] [] inv ok_four S.reverse (by simpa using hlen)
    (fun x hx => hG x (List.mem_reverse.mp hx))
  simpa using h

/-- Every sequence over G of length at least 5 has a nonempty zero-sum subsequence. -/
theorem dav_upper : DavProp 5 := by
  intro S hG hlen
  have h5 : (S.take 5).length = 5 := by simp [List.length_take]; omega
  obtain ⟨T, hT, hne, hz⟩ := dav_five (S.take 5)
    (fun x hx => hG x (List.mem_of_mem_take hx)) h5
  exact ⟨T, hT.trans (List.take_sublist 5 S), hne, hz⟩

/-- The four unit vectors. -/
def basis : List Nat := [1, 2, 4, 8]

theorem basis_free : OverG basis ∧ basis.length = 4 ∧ ¬ HasZS basis := by
  refine ⟨overG_of_all _ (by decide +kernel), by decide, ?_⟩
  intro h
  exact no_short_of_check 4 basis (by decide +kernel) (hasShort_of_hasZS basis h)

/-- D(C_2^4) = 5 in the source's sense. -/
theorem davenport_eq_five : IsDavenport 5 := by
  refine ⟨by decide, dav_upper, ?_⟩
  intro t _ hP
  by_cases h : 5 ≤ t
  · exact h
  · exfalso
    exact basis_free.2.2 (hP basis basis_free.1 (by rw [basis_free.2.1]; omega))

/-- The value is unique: any d satisfying the source's definition of D(G) equals 5. -/
theorem davenport_unique (d : Nat) (h : IsDavenport d) : d = 5 := by
  have h1 := h.2.2 5 (by decide) dav_upper
  have h2 := davenport_eq_five.2.2 d h.1 h.2.1
  omega

/-! ## The lower bound s_{<=3}(G) >= 9 -/

/-- The eight vectors (1, a, b, c): the complement of a hyperplane. -/
def witness : List Nat := [8, 9, 10, 11, 12, 13, 14, 15]

/-- The finite computation for the witness and all of its prefixes. -/
theorem witness_check : ∀ l, l < 9 →
    (witness.take l).length = l ∧
    (witness.take l).all (fun x => decide (x < 16)) = true ∧
    (neSumsLe (witness.take l) 3).all (fun s => s != 0) = true := by decide +kernel

/-- For every l <= 8 some sequence over G of length exactly l has no nonempty zero-sum
subsequence of length at most 3. -/
theorem short_lower (l : Nat) (hl : l ≤ 8) :
    ∃ S : List Nat, OverG S ∧ S.length = l ∧ ¬ HasShortZS 3 S := by
  obtain ⟨h1, h2, h3⟩ := witness_check l (by omega)
  exact ⟨witness.take l, overG_of_all _ h2, h1, no_short_of_check 3 _ h3⟩

theorem not_shortProp (l : Nat) (hl : l ≤ 8) : ¬ ShortProp 3 l := by
  intro hP
  obtain ⟨S, hG, hlen, hfree⟩ := short_lower l hl
  exact hfree (hP S hG hlen)

theorem not_shortPropGe (l : Nat) (hl : l ≤ 8) : ¬ ShortPropGe 3 l :=
  fun hP => not_shortProp l hl (fun S hG hlen => hP S hG (by omega))

/-- s_{<=3}(C_2^4) is not at most 8, hence is at least 9. -/
theorem s3_not_at_most_8 : ¬ sShortAtMost 3 8 := by
  intro ⟨l, _, hl, hP⟩
  exact not_shortProp l hl hP

/-! ## The definitions are not vacuous -/

/-- `HasShortZS` holds where it should and fails where it should, and `ShortProp`/`sShortAtMost`
are satisfiable: s_{<=5}(G) <= 5 = D(G), in line with the source's remark that
s_{<=k}(G) = D(G) if k >= D(G). -/
theorem sanity :
    HasShortZS 3 [1, 2, 3] ∧ HasShortZS 2 [5, 5] ∧ HasShortZS 1 [0] ∧
    ¬ HasShortZS 2 [1, 2, 3] ∧ ShortProp 5 5 ∧ sShortAtMost 5 5 := by
  have h55 : ShortProp 5 5 := by
    intro S hG hlen
    have h := hasShort_of_hasZS S (dav_five S hG hlen)
    rwa [hlen] at h
  exact ⟨⟨[1, 2, 3], List.Sublist.refl _, by simp, by decide, by decide⟩,
    ⟨[5, 5], List.Sublist.refl _, by simp, by decide, by decide⟩,
    ⟨[0], List.Sublist.refl _, by simp, by decide, by decide⟩,
    no_short_of_check 2 [1, 2, 3] (by decide +kernel), h55, ⟨5, by decide, Nat.le_refl 5, h55⟩⟩

/-! ## Headline -/

/-- The hypotheses of Conjecture 6.2 hold for G = C_2^4 and k = 2 (rank 4 >= 2, D(G) = 5 = D*(G),
k > 0, exp(G) = 2 <= D - k = 3 <= D, and D - k >= (D + 1)/2 written as 2 (D - k) >= D + 1), and the
asserted conclusion s_{<=D-k}(G) <= D + k, that is s_{<=3}(G) <= 7, is false. -/
theorem refutes_conjecture_6_2 :
    2 ≤ rank ∧ IsDavenport 5 ∧ dStar = 5 ∧
    0 < 2 ∧ expo ≤ 5 - 2 ∧ 5 - 2 ≤ 5 ∧ 2 * (5 - 2) ≥ 5 + 1 ∧
    ¬ sShortAtMost (5 - 2) (5 + 2) := by
  refine ⟨by decide, davenport_eq_five, by decide, by decide, by decide, by decide, by decide, ?_⟩
  intro ⟨l, _, hl, hP⟩
  exact not_shortProp l (by omega) hP

/-- The instance sits exactly AT the threshold: D - k = 3 = (D + 1)/2. The source prints ">=" in the
upper branch and "<" in the lower one, so equality belongs to the upper branch; this is the binding
point that carries the weight (BINDING.md, point 1). -/
theorem at_threshold : 2 * (5 - 2) = 5 + 1 ∧ ¬ (2 * (5 - 2) < 5 + 1) := by decide

/-- Conjecture 6.2 as printed, specialised to the single group G = C_2^4 (every admissible k, both
branches). `D` ranges over the values satisfying the source's definition of D(G). -/
def Conjecture62_at_G : Prop :=
  2 ≤ rank → ∀ D, IsDavenport D → D = dStar →
    ∀ k, 0 < k → k ≤ D → expo ≤ D - k → D - k ≤ D →
      (D + 1 ≤ 2 * (D - k) → sShortAtMost (D - k) (D + k)) ∧
      (2 * (D - k) < D + 1 → ¬ sShortAtMost (D - k) (D + k))

theorem not_conjecture62_at_G : ¬ Conjecture62_at_G := by
  intro hC
  have h := (hC (by decide) 5 davenport_eq_five (by decide) 2 (by decide) (by decide)
    (by decide) (by decide)).1 (by decide)
  exact refutes_conjecture_6_2.2.2.2.2.2.2.2 h

end ShortZeroSums

#print axioms ShortZeroSums.group_is_C2_pow_4
#print axioms ShortZeroSums.group_axioms
#print axioms ShortZeroSums.invariants
#print axioms ShortZeroSums.exponent_two
#print axioms ShortZeroSums.br_00
#print axioms ShortZeroSums.br_14
#print axioms ShortZeroSums.ok_four
#print axioms ShortZeroSums.witness_check
#print axioms ShortZeroSums.dav_upper
#print axioms ShortZeroSums.davenport_eq_five
#print axioms ShortZeroSums.davenport_unique
#print axioms ShortZeroSums.short_lower
#print axioms ShortZeroSums.not_shortPropGe
#print axioms ShortZeroSums.s3_not_at_most_8
#print axioms ShortZeroSums.sanity
#print axioms ShortZeroSums.refutes_conjecture_6_2
#print axioms ShortZeroSums.at_threshold
#print axioms ShortZeroSums.not_conjecture62_at_G

/-! Targeted-review scratch file B. My OWN general statement of Conjecture 6.2, written from the
source text (arXiv:2506.21383v1, pp. 1, 2, 4, 27), over ALL invariant-factor lists
1 < n_1 | ... | n_r, with G = C_{n_1} + ... + C_{n_r} as vectors with coordinatewise addition.
Then: the general statement IMPLIES the file's `Conjecture62_at_G` (transfer along the coding
(c0,c1,c2,c3) -> c0 + 2 c1 + 4 c2 + 8 c3), hence `¬ Conjecture62` for the general statement. -/
namespace Gen

/-- "G = C_{n1} + ... + C_{nr}, where 1 < n1 | n2 | ... | nr" (source p. 1). -/
def Chain : List Nat → Prop
  | [] => True
  | [n] => 1 < n
  | n :: m :: t => 1 < n ∧ n ∣ m ∧ Chain (m :: t)

/-- v is an element of C_{n1} + ... + C_{nr}: one coordinate below n_i for each i. -/
def Elem : List Nat → List Nat → Prop
  | [], [] => True
  | n :: ns, x :: v => x < n ∧ Elem ns v
  | _, _ => False

/-- coordinatewise addition modulo n_i -/
def add : List Nat → List Nat → List Nat → List Nat
  | n :: ns, x :: v, y :: w => (x + y) % n :: add ns v w
  | _, _, _ => []

def zero (ns : List Nat) : List Nat := ns.map (fun _ => 0)

/-- sigma(S), the sum of the terms of a sequence (source p. 4). -/
def sum (ns : List Nat) : List (List Nat) → List Nat
  | [] => zero ns
  | v :: t => add ns v (sum ns t)

def Over (ns : List Nat) (S : List (List Nat)) : Prop := ∀ v, v ∈ S → Elem ns v

def HasZS (ns : List Nat) (S : List (List Nat)) : Prop :=
  ∃ T : List (List Nat), T.Sublist S ∧ T ≠ [] ∧ sum ns T = zero ns

def HasShortZS (ns : List Nat) (h : Nat) (S : List (List Nat)) : Prop :=
  ∃ T : List (List Nat), T.Sublist S ∧ T ≠ [] ∧ T.length ≤ h ∧ sum ns T = zero ns

/-- D(G) = d: "the smallest positive integer t such that every sequence S over G of length
|S| >= t has a nonempty zero-sum subsequence" (source p. 1). -/
def DavProp (ns : List Nat) (t : Nat) : Prop :=
  ∀ S, Over ns S → t ≤ S.length → HasZS ns S
def IsDavenport (ns : List Nat) (d : Nat) : Prop :=
  0 < d ∧ DavProp ns d ∧ ∀ t, 0 < t → DavProp ns t → d ≤ t

/-- Definition 1.1: "each sequence of length l has a non-empty zero-sum subsequence of length
at most k". -/
def ShortProp (ns : List Nat) (h l : Nat) : Prop :=
  ∀ S, Over ns S → S.length = l → HasShortZS ns h S
/-- s_{<=h}(G) <= B (the smallest positive such l, or +infinity, is at most B). -/
def sAtMost (ns : List Nat) (h B : Nat) : Prop := ∃ l, 0 < l ∧ l ≤ B ∧ ShortProp ns h l

def expo : List Nat → Nat
  | [] => 1
  | [n] => n
  | _ :: m :: t => expo (m :: t)
def dStar : List Nat → Nat
  | [] => 1
  | n :: t => (n - 1) + dStar t

/-- Conjecture 6.2, source p. 27, over every finite abelian group in invariant-factor form.
`h` is D(G) - k, written `h + k = D` so that no truncated subtraction occurs. The threshold
D(G) - k >= (D(G)+1)/2 is cross-multiplied. -/
def Conjecture62 : Prop :=
  ∀ ns : List Nat, Chain ns → 2 ≤ ns.length →
    ∀ D, IsDavenport ns D → D = dStar ns →
      ∀ k h, 0 < k → h + k = D → expo ns ≤ h → h ≤ D →
        (D + 1 ≤ 2 * h → sAtMost ns h (D + k)) ∧
        (2 * h < D + 1 → ¬ sAtMost ns h (D + k))

/-! ## Transfer between C_2^4 as vectors and the file's model ({0..15}, XOR) -/

def ns4 : List Nat := [2, 2, 2, 2]

def enc : List Nat → Nat
  | [] => 0
  | x :: v => x + 2 * enc v

def dec (a : Nat) : List Nat := [a % 2, a / 2 % 2, a / 4 % 2, a / 8 % 2]

theorem elem_form (v : List Nat) (hv : Elem ns4 v) :
    ∃ a b c d, a < 2 ∧ b < 2 ∧ c < 2 ∧ d < 2 ∧ v = [a, b, c, d] := by
  match v, hv with
  | [a, b, c, d], hv =>
    simp only [ns4, Elem] at hv
    exact ⟨a, b, c, d, hv.1, hv.2.1, hv.2.2.1, hv.2.2.2.1, rfl⟩

theorem enc_add_tab : ∀ x, x < 16 → ∀ y, y < 16 →
    enc (add ns4 (dec x) (dec y)) = x ^^^ y := by
  decide +kernel

theorem dec_enc (v : List Nat) (hv : Elem ns4 v) : dec (enc v) = v := by
  obtain ⟨a, b, c, d, ha, hb, hc, hd, rfl⟩ := elem_form v hv
  simp only [dec, enc]
  have h1 : (a + 2 * (b + 2 * (c + 2 * (d + 2 * 0)))) % 2 = a := by omega
  have h2 : (a + 2 * (b + 2 * (c + 2 * (d + 2 * 0)))) / 2 % 2 = b := by omega
  have h3 : (a + 2 * (b + 2 * (c + 2 * (d + 2 * 0)))) / 4 % 2 = c := by omega
  have h4 : (a + 2 * (b + 2 * (c + 2 * (d + 2 * 0)))) / 8 % 2 = d := by omega
  rw [h1, h2, h3, h4]

theorem elem_mk (a b c d : Nat) (ha : a < 2) (hb : b < 2) (hc : c < 2) (hd : d < 2) :
    Elem ns4 [a, b, c, d] := by
  simp only [ns4, Elem]; exact ⟨ha, hb, hc, hd, trivial⟩

theorem enc_lt (v : List Nat) (hv : Elem ns4 v) : enc v < 16 := by
  obtain ⟨a, b, c, d, ha, hb, hc, hd, rfl⟩ := elem_form v hv
  simp only [enc]; omega

theorem add_elem (v w : List Nat) (hv : Elem ns4 v) (hw : Elem ns4 w) :
    Elem ns4 (add ns4 v w) ∧ enc (add ns4 v w) = enc v ^^^ enc w := by
  have key := enc_add_tab (enc v) (enc_lt v hv) (enc w) (enc_lt w hw)
  rw [dec_enc v hv, dec_enc w hw] at key
  refine ⟨?_, key⟩
  obtain ⟨a, b, c, d, ha, hb, hc, hd, rfl⟩ := elem_form v hv
  obtain ⟨a', b', c', d', ha', hb', hc', hd', rfl⟩ := elem_form w hw
  simp only [ns4, add]
  exact elem_mk _ _ _ _ (Nat.mod_lt _ (by decide)) (Nat.mod_lt _ (by decide))
    (Nat.mod_lt _ (by decide)) (Nat.mod_lt _ (by decide))

theorem enc_zero_iff (v : List Nat) (hv : Elem ns4 v) (h0 : enc v = 0) : v = zero ns4 := by
  obtain ⟨a, b, c, d, ha, hb, hc, hd, rfl⟩ := elem_form v hv
  simp only [enc] at h0
  have : a = 0 ∧ b = 0 ∧ c = 0 ∧ d = 0 := by omega
  obtain ⟨rfl, rfl, rfl, rfl⟩ := this
  rfl

theorem dec_elem (a : Nat) : Elem ns4 (dec a) :=
  elem_mk _ _ _ _ (Nat.mod_lt _ (by decide)) (Nat.mod_lt _ (by decide))
    (Nat.mod_lt _ (by decide)) (Nat.mod_lt _ (by decide))

theorem enc_dec (a : Nat) (ha : a < 16) : enc (dec a) = a := by
  simp only [dec, enc]; omega

theorem sum_enc : ∀ T : List (List Nat), Over ns4 T →
    Elem ns4 (sum ns4 T) ∧ enc (sum ns4 T) = ShortZeroSums.sigma (T.map enc)
  | [], _ => ⟨elem_mk 0 0 0 0 (by decide) (by decide) (by decide) (by decide), rfl⟩
  | v :: t, h => by
    have hv : Elem ns4 v := h v (List.mem_cons_self ..)
    obtain ⟨ih1, ih2⟩ := sum_enc t (fun w hw => h w (List.mem_cons_of_mem _ hw))
    obtain ⟨h1, h2⟩ := add_elem v (sum ns4 t) hv ih1
    refine ⟨h1, ?_⟩
    show enc (add ns4 v (sum ns4 t)) = enc v ^^^ ShortZeroSums.sigma (t.map enc)
    rw [h2, ih2]

theorem over_sub {S T : List (List Nat)} (hS : Over ns4 S) (hT : T.Sublist S) : Over ns4 T :=
  fun v hv => hS v (hT.subset hv)

theorem overG_map (S : List (List Nat)) (hS : Over ns4 S) : ShortZeroSums.OverG (S.map enc) := by
  intro x hx
  obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hx
  exact enc_lt v (hS v hv)

theorem over_map_dec (S : List Nat) : Over ns4 (S.map dec) := by
  intro v hv
  obtain ⟨a, _, rfl⟩ := List.mem_map.mp hv
  exact dec_elem a

theorem map_enc_dec (S : List Nat) (hS : ShortZeroSums.OverG S) : (S.map dec).map enc = S := by
  rw [List.map_map]
  have : List.map (enc ∘ dec) S = List.map id S :=
    List.map_congr_left (fun a ha => enc_dec a (hS a ha))
  rw [this, List.map_id]

/-- vectors -> XOR model -/
theorem short_fwd (h : Nat) (S : List (List Nat)) (hS : Over ns4 S) :
    HasShortZS ns4 h S → ShortZeroSums.HasShortZS h (S.map enc) := by
  intro ⟨T, hT, hne, hl, hz⟩
  refine ⟨T.map enc, hT.map enc, ?_, by simpa using hl, ?_⟩
  · intro hnil; exact hne (List.map_eq_nil_iff.mp hnil)
  · rw [← (sum_enc T (over_sub hS hT)).2, hz]; rfl

/-- XOR model -> vectors -/
theorem short_bwd (h : Nat) (S : List (List Nat)) (hS : Over ns4 S) :
    ShortZeroSums.HasShortZS h (S.map enc) → HasShortZS ns4 h S := by
  intro ⟨T', hT', hne, hl, hz⟩
  obtain ⟨T, hT, rfl⟩ := List.sublist_map_iff.mp hT'
  have hO := over_sub hS hT
  refine ⟨T, hT, ?_, by simpa using hl, ?_⟩
  · intro hnil; subst hnil; exact hne rfl
  · exact enc_zero_iff _ (sum_enc T hO).1 (by rw [(sum_enc T hO).2]; exact hz)

theorem zs_iff_short (S : List (List Nat)) : HasZS ns4 S ↔ HasShortZS ns4 S.length S :=
  ⟨fun ⟨T, a, b, c⟩ => ⟨T, a, b, a.length_le, c⟩, fun ⟨T, a, b, _, c⟩ => ⟨T, a, b, c⟩⟩

theorem zs_iff_short' (S : List Nat) :
    ShortZeroSums.HasZS S ↔ ShortZeroSums.HasShortZS S.length S :=
  ⟨fun ⟨T, a, b, c⟩ => ⟨T, a, b, a.length_le, c⟩, fun ⟨T, a, b, _, c⟩ => ⟨T, a, b, c⟩⟩

theorem shortProp_iff (h l : Nat) : ShortProp ns4 h l ↔ ShortZeroSums.ShortProp h l := by
  constructor
  · intro hP S hG hlen
    have := short_fwd h (S.map dec) (over_map_dec S)
      (hP (S.map dec) (over_map_dec S) (by simpa using hlen))
    rwa [map_enc_dec S hG] at this
  · intro hP S hS hlen
    exact short_bwd h S hS (hP (S.map enc) (overG_map S hS) (by simpa using hlen))

theorem davProp_iff (t : Nat) : DavProp ns4 t ↔ ShortZeroSums.DavProp t := by
  constructor
  · intro hP S hG hlen
    have h1 := hP (S.map dec) (over_map_dec S) (by simpa using hlen)
    have h2 := short_fwd _ (S.map dec) (over_map_dec S) ((zs_iff_short _).mp h1)
    rw [map_enc_dec S hG] at h2
    exact (zs_iff_short' S).mpr (by simpa using h2)
  · intro hP S hS hlen
    have h1 := hP (S.map enc) (overG_map S hS) (by simpa using hlen)
    have h2 := (zs_iff_short' _).mp h1
    exact (zs_iff_short S).mpr (short_bwd _ S hS (by simpa using h2))

theorem isDavenport_iff (d : Nat) : IsDavenport ns4 d ↔ ShortZeroSums.IsDavenport d := by
  unfold IsDavenport ShortZeroSums.IsDavenport
  constructor
  · intro ⟨a, b, c⟩
    exact ⟨a, (davProp_iff d).mp b, fun t ht hP => c t ht ((davProp_iff t).mpr hP)⟩
  · intro ⟨a, b, c⟩
    exact ⟨a, (davProp_iff d).mpr b, fun t ht hP => c t ht ((davProp_iff t).mp hP)⟩

theorem sAtMost_iff (h B : Nat) : sAtMost ns4 h B ↔ ShortZeroSums.sShortAtMost h B := by
  constructor
  · intro ⟨l, a, b, c⟩; exact ⟨l, a, b, (shortProp_iff h l).mp c⟩
  · intro ⟨l, a, b, c⟩; exact ⟨l, a, b, (shortProp_iff h l).mpr c⟩

/-- The general statement implies the file's specialisation. -/
theorem general_implies_at_G : Conjecture62 → ShortZeroSums.Conjecture62_at_G := by
  intro hC _ D hD hDs k hk hkD he hle
  have hchain : Chain ns4 := by
    simp only [ns4, Chain]
    exact ⟨by decide, ⟨1, rfl⟩, by decide, ⟨1, rfl⟩, by decide, ⟨1, rfl⟩, by decide⟩
  have hds : D = dStar ns4 := by rw [hDs]; decide
  have hexp : expo ns4 ≤ D - k := by
    have : expo ns4 = ShortZeroSums.expo := by decide
    rw [this]; exact he
  have := hC ns4 hchain (by decide) D ((isDavenport_iff D).mpr hD) hds k (D - k) hk (by omega)
    hexp hle
  exact ⟨fun h => (sAtMost_iff _ _).mp (this.1 h),
    fun h hs => this.2 h ((sAtMost_iff _ _).mpr hs)⟩

/-- The negation of Conjecture 6.2 over general definitions (all invariant-factor lists), as the
conjecture is PRINTED in arXiv:2506.21383v1. Obtained from the certificate above; the only new kernel
computation is the 256-case table `enc_add_tab`. Provenance: this is an inconsistency internal to the
source (class (d)): the source's own results give the value at C_2^4 that contradicts the printed
statement. It is not a model discovery of a new counterexample, and it says nothing about the
conjecture with C_2^4 excluded. -/
theorem not_conjecture62 : ¬ Conjecture62 :=
  fun hC => ShortZeroSums.not_conjecture62_at_G (general_implies_at_G hC)

end Gen

#print axioms Gen.general_implies_at_G
#print axioms Gen.not_conjecture62

/-! Second targeted review, scratch file M (a review probe, not a certificate).
My OWN statement of Conjecture 6.2 of arXiv:2506.21383v1, written from the TeX source of v1
(lines 74-88, 104-108, 272-289, 1346-1351 of the author's .tex), deliberately NOT in the file's
idiom:
* a subsequence is a SUB-MULTISET, literally "v_g(S) >= v_g(T) for all g" (List.count), not a
  List.Sublist;
* D(G) and s_{<=k}(G) are least elements in the form "no smaller positive value works", and
  s_{<=k}(G) is a genuine value in N u {+infinity}: "s <= B" and "s > B" are two separate
  definitions, not a proposition and its negation;
* "D(G) - k in [exp(G), D(G)]" and the threshold are stated over the integers;
* invariant factors, elements, addition, zero, D*, exp are written with zip / zipWith /
  replicate / List.sum / getLast?.
Then `Mine.Conjecture62 ↔ Gen.Conjecture62` is PROVED. On the way: `Gen.add` is commutative and
associative with no side condition, so `Gen.sum` is invariant under permutation, which is what
makes sublists and sub-multisets interchangeable. -/
namespace Mine

/-- "1 < n_1 | n_2 | ... | n_r". -/
def InvFactors (ns : List Nat) : Prop :=
  (∀ n, n ∈ ns → 1 < n) ∧ (∀ p, p ∈ ns.zip ns.tail → p.1 ∣ p.2)

/-- an element of C_{n_1} + ... + C_{n_r}: a vector of residues. -/
def IsElt (ns v : List Nat) : Prop := v.length = ns.length ∧ ∀ p, p ∈ v.zip ns → p.1 < p.2

def plus (ns v w : List Nat) : List Nat :=
  List.zipWith (fun n s => s % n) ns (List.zipWith (fun x y => x + y) v w)

def zeroV (ns : List Nat) : List Nat := List.replicate ns.length 0

/-- g_1 + ... + g_l -/
def total (ns : List Nat) : List (List Nat) → List Nat
  | [] => zeroV ns
  | g :: t => plus ns g (total ns t)

def OverG (ns : List Nat) (S : List (List Nat)) : Prop := ∀ g, g ∈ S → IsElt ns g

/-- "T is a subsequence of S if v_g(S) >= v_g(T) for all g in G". -/
def SubSeq (T S : List (List Nat)) : Prop := ∀ g, T.count g ≤ S.count g

def ZeroSum (ns : List Nat) (S : List (List Nat)) : Prop :=
  ∃ T, SubSeq T S ∧ T ≠ [] ∧ total ns T = zeroV ns

def ZeroSumShort (ns : List Nat) (h : Nat) (S : List (List Nat)) : Prop :=
  ∃ T, SubSeq T S ∧ T ≠ [] ∧ T.length ≤ h ∧ total ns T = zeroV ns

def DavHolds (ns : List Nat) (t : Nat) : Prop :=
  ∀ S, OverG ns S → t ≤ S.length → ZeroSum ns S

/-- D(G) = d: d is positive, works, and no smaller positive t works. -/
def IsD (ns : List Nat) (d : Nat) : Prop :=
  0 < d ∧ DavHolds ns d ∧ ∀ t, 0 < t → t < d → ¬ DavHolds ns t

def Works (ns : List Nat) (h l : Nat) : Prop :=
  ∀ S, OverG ns S → S.length = l → ZeroSumShort ns h S

/-- s_{<=h}(G) = s, a positive integer. -/
def sIs (ns : List Nat) (h s : Nat) : Prop :=
  0 < s ∧ Works ns h s ∧ ∀ l, 0 < l → l < s → ¬ Works ns h l
/-- s_{<=h}(G) = +infinity. -/
def sInfinite (ns : List Nat) (h : Nat) : Prop := ∀ l, 0 < l → ¬ Works ns h l
/-- s_{<=h}(G) <= B. -/
def sLe (ns : List Nat) (h B : Nat) : Prop := ∃ s, sIs ns h s ∧ s ≤ B
/-- s_{<=h}(G) > B. -/
def sGt (ns : List Nat) (h B : Nat) : Prop := sInfinite ns h ∨ ∃ s, sIs ns h s ∧ B < s

def Dstar (ns : List Nat) : Nat := 1 + (ns.map (fun n => n - 1)).sum
def expG (ns : List Nat) : Nat := ns.getLast?.getD 0

/-- Conjecture 6.2 as printed. -/
def Conjecture62 : Prop :=
  ∀ ns : List Nat, InvFactors ns → 2 ≤ ns.length →
    ∀ D, IsD ns D → D = Dstar ns →
      ∀ k : Nat, 0 < k → (expG ns : Int) ≤ (D : Int) - k → (D : Int) - k ≤ D →
        ((D : Int) + 1 ≤ 2 * ((D : Int) - k) → sLe ns (D - k) (D + k)) ∧
        (2 * ((D : Int) - k) < (D : Int) + 1 → sGt ns (D - k) (D + k))

/-! ## Relation to `Gen` -/

theorem inv_iff : ∀ ns : List Nat, InvFactors ns ↔ Gen.Chain ns
  | [] => by simp [InvFactors, Gen.Chain]
  | [n] => by simp [InvFactors, Gen.Chain]
  | n :: m :: t => by
    have ih := inv_iff (m :: t)
    constructor
    · intro ⟨h1, h2⟩
      refine ⟨h1 n (List.mem_cons_self ..), h2 (n, m) ?_, ih.mp ⟨?_, ?_⟩⟩
      · show (n, m) ∈ (n, m) :: (m :: t).zip t
        exact List.mem_cons_self ..
      · exact fun x hx => h1 x (List.mem_cons_of_mem _ hx)
      · intro p hp
        refine h2 p ?_
        show p ∈ (n, m) :: (m :: t).zip t
        exact List.mem_cons_of_mem _ hp
    · intro ⟨hn, hd, hc⟩
      obtain ⟨g1, g2⟩ := ih.mpr hc
      refine ⟨?_, ?_⟩
      · intro x hx
        rcases List.mem_cons.mp hx with rfl | hx
        · exact hn
        · exact g1 x hx
      · intro p hp
        have hp' : p ∈ (n, m) :: (m :: t).zip t := hp
        rcases List.mem_cons.mp hp' with rfl | hp'
        · exact hd
        · exact g2 p hp'

theorem elt_iff : ∀ ns v : List Nat, IsElt ns v ↔ Gen.Elem ns v
  | [], [] => by simp [IsElt, Gen.Elem]
  | [], _ :: _ => by simp [IsElt, Gen.Elem]
  | _ :: _, [] => by simp [IsElt, Gen.Elem]
  | n :: ns, x :: v => by
    have ih := elt_iff ns v
    simp only [Gen.Elem]
    rw [← ih]
    simp only [IsElt, List.length_cons, List.zip_cons_cons, List.mem_cons]
    constructor
    · intro ⟨hl, hp⟩
      exact ⟨hp (x, n) (Or.inl rfl), by omega, fun p hp' => hp p (Or.inr hp')⟩
    · intro ⟨hx, hl, hp⟩
      refine ⟨by omega, ?_⟩
      intro p hp'
      rcases hp' with rfl | hp'
      · exact hx
      · exact hp p hp'

theorem plus_eq : ∀ ns v w : List Nat, plus ns v w = Gen.add ns v w
  | [], _, _ => by simp [plus, Gen.add]
  | _ :: _, [], _ => by simp [plus, Gen.add]
  | _ :: _, _ :: _, [] => by simp [plus, Gen.add]
  | n :: ns, x :: v, y :: w => by
    have ih := plus_eq ns v w
    simp only [plus, Gen.add, List.zipWith_cons_cons] at ih ⊢
    rw [ih]

theorem zeroV_eq : ∀ ns : List Nat, zeroV ns = Gen.zero ns
  | [] => rfl
  | _ :: ns => by
    have ih := zeroV_eq ns
    simp only [zeroV, Gen.zero, List.length_cons, List.replicate_succ, List.map_cons] at ih ⊢
    rw [ih]

theorem total_eq (ns : List Nat) : ∀ S : List (List Nat), total ns S = Gen.sum ns S
  | [] => zeroV_eq ns
  | g :: t => by
    simp only [total, Gen.sum]
    rw [plus_eq, total_eq ns t]

/-! ### `Gen.add` is commutative and associative, unconditionally -/

theorem add_comm : ∀ ns v w : List Nat, Gen.add ns v w = Gen.add ns w v
  | [], _, _ => by simp [Gen.add]
  | _ :: _, [], [] => by simp [Gen.add]
  | _ :: _, [], _ :: _ => by simp [Gen.add]
  | _ :: _, _ :: _, [] => by simp [Gen.add]
  | n :: ns, x :: v, y :: w => by
    simp only [Gen.add]
    rw [add_comm ns v w, Nat.add_comm x y]

theorem add_nil_left (ns w : List Nat) : Gen.add ns [] w = [] := by
  cases ns <;> simp [Gen.add]
theorem add_nil_right (ns v : List Nat) : Gen.add ns v [] = [] := by
  cases ns <;> cases v <;> simp [Gen.add]

theorem add_assoc : ∀ ns u v w : List Nat,
    Gen.add ns (Gen.add ns u v) w = Gen.add ns u (Gen.add ns v w)
  | [], _, _, _ => by simp [Gen.add]
  | n :: ns, [], v, w => by simp [add_nil_left]
  | n :: ns, x :: u, [], w => by simp [add_nil_left, add_nil_right]
  | n :: ns, x :: u, y :: v, [] => by simp [add_nil_right]
  | n :: ns, x :: u, y :: v, z :: w => by
    simp only [Gen.add]
    rw [add_assoc ns u v w, Nat.mod_add_mod, Nat.add_mod_mod, Nat.add_assoc]

theorem add_left_comm (ns u v w : List Nat) :
    Gen.add ns u (Gen.add ns v w) = Gen.add ns v (Gen.add ns u w) := by
  rw [← add_assoc, add_comm ns u v, add_assoc]

theorem sum_perm (ns : List Nat) {T T' : List (List Nat)} (hp : T.Perm T') :
    Gen.sum ns T = Gen.sum ns T' := by
  induction hp with
  | nil => rfl
  | cons x _ ih => simp only [Gen.sum]; rw [ih]
  | swap x y l => simp only [Gen.sum]; exact add_left_comm ns y x _
  | trans _ _ ih1 ih2 => exact ih1.trans ih2

/-! ### a sub-multiset of a list is a permutation of one of its sublists -/

theorem exists_sublist_perm : ∀ (S T : List (List Nat)), (∀ g, T.count g ≤ S.count g) →
    ∃ T' : List (List Nat), T'.Sublist S ∧ T'.Perm T
  | [], T, h => by
    have : T = [] := by
      cases T with
      | nil => rfl
      | cons g t =>
        have := h g
        rw [List.count_cons_self, List.count_nil] at this
        omega
    subst this
    exact ⟨[], List.Sublist.slnil, List.Perm.refl _⟩
  | x :: S', T, h => by
    by_cases hx : x ∈ T
    · have h' : ∀ g, (T.erase x).count g ≤ S'.count g := by
        intro g
        have hg := h g
        by_cases hgx : g = x
        · subst hgx
          rw [List.count_erase_self]
          rw [List.count_cons_self] at hg
          omega
        · rw [List.count_erase_of_ne hgx]
          rw [List.count_cons_of_ne (fun e => hgx e.symm)] at hg
          exact hg
      obtain ⟨T'', hs, hp⟩ := exists_sublist_perm S' (T.erase x) h'
      exact ⟨x :: T'', List.cons_sublist_cons.mpr hs,
        (List.Perm.cons x hp).trans (List.perm_cons_erase hx).symm⟩
    · have h' : ∀ g, T.count g ≤ S'.count g := by
        intro g
        have hg := h g
        by_cases hgx : g = x
        · subst hgx
          rw [List.count_eq_zero_of_not_mem hx]
          exact Nat.zero_le _
        · rw [List.count_cons_of_ne (fun e => hgx e.symm)] at hg
          exact hg
      obtain ⟨T', hs, hp⟩ := exists_sublist_perm S' T h'
      exact ⟨T', hs.cons x, hp⟩

theorem short_iff (ns : List Nat) (h : Nat) (S : List (List Nat)) :
    ZeroSumShort ns h S ↔ Gen.HasShortZS ns h S := by
  constructor
  · intro ⟨T, hsub, hne, hl, hz⟩
    obtain ⟨T', hs, hp⟩ := exists_sublist_perm S T hsub
    refine ⟨T', hs, ?_, ?_, ?_⟩
    · intro hnil
      subst hnil
      exact hne hp.nil_eq.symm
    · rw [hp.length_eq]; exact hl
    · rw [sum_perm ns hp, ← total_eq, hz, zeroV_eq]
  · intro ⟨T, hs, hne, hl, hz⟩
    exact ⟨T, fun g => hs.count_le g, hne, hl, by rw [total_eq, hz, zeroV_eq]⟩

theorem zs_iff (ns : List Nat) (S : List (List Nat)) : ZeroSum ns S ↔ Gen.HasZS ns S := by
  constructor
  · intro ⟨T, hsub, hne, hz⟩
    obtain ⟨T', hs, hne', _, hz'⟩ := (short_iff ns T.length S).mp ⟨T, hsub, hne, Nat.le_refl _, hz⟩
    exact ⟨T', hs, hne', hz'⟩
  · intro ⟨T, hs, hne, hz⟩
    obtain ⟨T', hsub, hne', _, hz'⟩ := (short_iff ns T.length S).mpr ⟨T, hs, hne, Nat.le_refl _, hz⟩
    exact ⟨T', hsub, hne', hz'⟩

theorem over_iff (ns : List Nat) (S : List (List Nat)) : OverG ns S ↔ Gen.Over ns S :=
  ⟨fun h v hv => (elt_iff ns v).mp (h v hv), fun h v hv => (elt_iff ns v).mpr (h v hv)⟩

theorem dav_iff (ns : List Nat) (t : Nat) : DavHolds ns t ↔ Gen.DavProp ns t :=
  ⟨fun h S hS hl => (zs_iff ns S).mp (h S ((over_iff ns S).mpr hS) hl),
   fun h S hS hl => (zs_iff ns S).mpr (h S ((over_iff ns S).mp hS) hl)⟩

theorem works_iff (ns : List Nat) (h l : Nat) : Works ns h l ↔ Gen.ShortProp ns h l :=
  ⟨fun hw S hS hl => (short_iff ns h S).mp (hw S ((over_iff ns S).mpr hS) hl),
   fun hw S hS hl => (short_iff ns h S).mpr (hw S ((over_iff ns S).mp hS) hl)⟩

theorem isD_iff (ns : List Nat) (d : Nat) : IsD ns d ↔ Gen.IsDavenport ns d := by
  constructor
  · intro ⟨a, b, c⟩
    refine ⟨a, (dav_iff ns d).mp b, ?_⟩
    intro t ht hP
    by_cases hlt : t < d
    · exact absurd ((dav_iff ns t).mpr hP) (c t ht hlt)
    · omega
  · intro ⟨a, b, c⟩
    refine ⟨a, (dav_iff ns d).mpr b, ?_⟩
    intro t ht hlt hP
    have := c t ht ((dav_iff ns t).mp hP)
    omega

/-- a bounded nonempty set of positive integers has a least element -/
theorem least (P : Nat → Prop) : ∀ B, (∃ l, 0 < l ∧ l ≤ B ∧ P l) →
    ∃ s, 0 < s ∧ s ≤ B ∧ P s ∧ ∀ l, 0 < l → l < s → ¬ P l
  | 0, ⟨l, h0, hB, _⟩ => by omega
  | B + 1, ⟨l, h0, hB, hP⟩ => by
    by_cases hex : ∃ l, 0 < l ∧ l ≤ B ∧ P l
    · obtain ⟨s, a, b, c, d⟩ := least P B hex
      exact ⟨s, a, by omega, c, d⟩
    · have hl : l = B + 1 := by
        by_cases hle : l ≤ B
        · exact absurd ⟨l, h0, hle, hP⟩ hex
        · omega
      subst hl
      exact ⟨B + 1, h0, Nat.le_refl _, hP, fun l' h0' hlt hP' => hex ⟨l', h0', by omega, hP'⟩⟩

theorem sLe_iff (ns : List Nat) (h B : Nat) : sLe ns h B ↔ Gen.sAtMost ns h B := by
  constructor
  · intro ⟨s, ⟨a, b, _⟩, hB⟩
    exact ⟨s, a, hB, (works_iff ns h s).mp b⟩
  · intro ⟨l, a, b, c⟩
    obtain ⟨s, s0, sB, sP, smin⟩ := least (Works ns h) B ⟨l, a, b, (works_iff ns h l).mpr c⟩
    exact ⟨s, ⟨s0, sP, smin⟩, sB⟩

theorem sGt_iff (ns : List Nat) (h B : Nat) : sGt ns h B ↔ ¬ Gen.sAtMost ns h B := by
  constructor
  · intro hgt ⟨l, a, b, c⟩
    have hw := (works_iff ns h l).mpr c
    rcases hgt with hinf | ⟨s, ⟨_, _, smin⟩, hBs⟩
    · exact hinf l a hw
    · exact smin l a (by omega) hw
  · intro hn
    by_cases hex : ∃ l, 0 < l ∧ Works ns h l
    · obtain ⟨l, a, hw⟩ := hex
      obtain ⟨s, s0, _, sP, smin⟩ := least (Works ns h) l ⟨l, a, Nat.le_refl _, hw⟩
      refine Or.inr ⟨s, ⟨s0, sP, smin⟩, ?_⟩
      by_cases hBs : B < s
      · exact hBs
      · exact absurd ⟨s, s0, by omega, (works_iff ns h s).mp sP⟩ hn
    · exact Or.inl (fun l a hw => hex ⟨l, a, hw⟩)

theorem dstar_eq : ∀ ns : List Nat, Dstar ns = Gen.dStar ns
  | [] => rfl
  | n :: t => by
    have ih := dstar_eq t
    simp only [Dstar, Gen.dStar, List.map_cons, List.sum_cons] at ih ⊢
    omega

theorem exp_eq : ∀ ns : List Nat, ns ≠ [] → expG ns = Gen.expo ns
  | [], h => absurd rfl h
  | [n], _ => by simp [expG, Gen.expo]
  | n :: m :: t, _ => by
    have ih := exp_eq (m :: t) (by simp)
    simp only [expG, Gen.expo, List.getLast?_cons_cons] at ih ⊢
    exact ih

/-- My statement and the file's statement are equivalent. -/
theorem mine_iff_gen : Conjecture62 ↔ Gen.Conjecture62 := by
  constructor
  · intro hM ns hch hr D hD hDs k h hk hhk he hle
    have hne : ns ≠ [] := by intro h0; subst h0; simp at hr
    have hexp := exp_eq ns hne
    have hkD : D - k = h := by omega
    have := hM ns ((inv_iff ns).mpr hch) hr D ((isD_iff ns D).mpr hD) (by rw [hDs, dstar_eq]) k hk
      (by rw [hexp]; omega) (by omega)
    rw [hkD] at this
    exact ⟨fun h1 => (sLe_iff ns h _).mp (this.1 (by omega)),
      fun h2 => (sGt_iff ns h _).mp (this.2 (by omega))⟩
  · intro hG ns hinv hr D hD hDs k hk he hle
    have hne : ns ≠ [] := by intro h0; subst h0; simp at hr
    have hexp := exp_eq ns hne
    have := hG ns ((inv_iff ns).mp hinv) hr D ((isD_iff ns D).mp hD) (by rw [hDs, dstar_eq]) k
      (D - k) hk (by omega) (by rw [← hexp]; omega) (by omega)
    exact ⟨fun h1 => (sLe_iff ns _ _).mpr (this.1 (by omega)),
      fun h2 => (sGt_iff ns _ _).mpr (this.2 (by omega))⟩

/-- Hence my statement is refuted too, by the file's theorem. -/
theorem not_mine : ¬ Conjecture62 := fun h => Gen.not_conjecture62 (mine_iff_gen.mp h)

/-! ## Side results of the statement audit -/

/-- The hypothesis r(G) >= 2 (`2 ≤ ns.length`) carries no weight in `Gen.Conjecture62`: for a
cyclic group D* = exp, so "D - k in [exp, D]" forces k = 0; the same at the trivial group with the
file's conventions `expo [] = 1`, `dStar [] = 1`. -/
def GenNoRank : Prop :=
  ∀ ns : List Nat, Gen.Chain ns →
    ∀ D, Gen.IsDavenport ns D → D = Gen.dStar ns →
      ∀ k h, 0 < k → h + k = D → Gen.expo ns ≤ h → h ≤ D →
        (D + 1 ≤ 2 * h → Gen.sAtMost ns h (D + k)) ∧
        (2 * h < D + 1 → ¬ Gen.sAtMost ns h (D + k))

theorem rank_hypothesis_idle : Gen.Conjecture62 ↔ GenNoRank := by
  constructor
  · intro hC ns hch D hD hDs k h hk hhk he hle
    match ns, hch, hD, hDs, he with
    | [], _, _, hDs, he =>
      simp only [Gen.dStar] at hDs
      simp only [Gen.expo] at he
      omega
    | [n], hch, _, hDs, he =>
      simp only [Gen.dStar] at hDs
      simp only [Gen.expo] at he
      simp only [Gen.Chain] at hch
      omega
    | n :: m :: t, hch, hD, hDs, he =>
      exact hC (n :: m :: t) hch (by simp) D hD hDs k h hk hhk he hle
  · intro hC ns hch _ D hD hDs k h hk hhk he hle
    exact hC ns hch D hD hDs k h hk hhk he hle

/-- (Elem ns, add ns, zero ns) is an abelian group when every factor is positive: closure,
identity and inverses (commutativity and associativity are above, unconditional). -/
theorem add_closed : ∀ ns v w : List Nat, Gen.Elem ns v → Gen.Elem ns w →
    Gen.Elem ns (Gen.add ns v w)
  | [], [], [], _, _ => by simp [Gen.add, Gen.Elem]
  | n :: ns, x :: v, y :: w, hv, hw => by
    simp only [Gen.Elem] at hv hw
    simp only [Gen.add, Gen.Elem]
    exact ⟨Nat.mod_lt _ (by omega), add_closed ns v w hv.2 hw.2⟩
  | [], _ :: _, _, hv, _ => by simp [Gen.Elem] at hv
  | [], [], _ :: _, _, hw => by simp [Gen.Elem] at hw
  | _ :: _, [], _, hv, _ => by simp [Gen.Elem] at hv
  | _ :: _, _ :: _, [], _, hw => by simp [Gen.Elem] at hw

theorem add_zero : ∀ ns v : List Nat, Gen.Elem ns v → Gen.add ns v (Gen.zero ns) = v
  | [], [], _ => by simp [Gen.add]
  | n :: ns, x :: v, hv => by
    simp only [Gen.Elem] at hv
    simp only [Gen.zero, List.map_cons, Gen.add, Nat.add_zero]
    rw [Nat.mod_eq_of_lt hv.1]
    have := add_zero ns v hv.2
    simp only [Gen.zero] at this
    rw [this]
  | [], _ :: _, hv => by simp [Gen.Elem] at hv
  | _ :: _, [], hv => by simp [Gen.Elem] at hv

theorem exists_neg : ∀ ns v : List Nat, Gen.Elem ns v →
    ∃ w, Gen.Elem ns w ∧ Gen.add ns v w = Gen.zero ns
  | [], [], _ => ⟨[], trivial, by simp [Gen.add, Gen.zero]⟩
  | n :: ns, x :: v, hv => by
    simp only [Gen.Elem] at hv
    obtain ⟨w, hw, hz⟩ := exists_neg ns v hv.2
    refine ⟨(n - x) % n :: w, ?_, ?_⟩
    · simp only [Gen.Elem]
      exact ⟨Nat.mod_lt _ (by omega), hw⟩
    · simp only [Gen.add, Gen.zero, List.map_cons]
      simp only [Gen.zero] at hz
      rw [hz, Nat.add_mod_mod]
      have : x + (n - x) = n := by omega
      rw [this, Nat.mod_self]
  | [], _ :: _, hv => by simp [Gen.Elem] at hv
  | _ :: _, [], hv => by simp [Gen.Elem] at hv

/-- D(G) is unique when it exists, for every list: `∀ D, IsDavenport ns D → D = dStar ns → ...`
reads "if D(G) = D*(G) then ...". -/
theorem dav_unique (ns : List Nat) (D D' : Nat) (h : Gen.IsDavenport ns D)
    (h' : Gen.IsDavenport ns D') : D = D' := by
  have h1 := h.2.2 D' h'.1 h'.2.1
  have h2 := h'.2.2 D h.1 h.2.1
  omega

/-- "each sequence of length l" and "each sequence of length at least l" agree for every list:
`Gen.ShortProp` is upward closed in l. -/
theorem shortProp_mono (ns : List Nat) (h l l' : Nat) (hl : l ≤ l')
    (hP : Gen.ShortProp ns h l) : Gen.ShortProp ns h l' := by
  intro S hS hlen
  have h1 : (S.take l).length = l := by simp [List.length_take]; omega
  obtain ⟨T, hT, hne, hle, hz⟩ := hP (S.take l) (fun v hv => hS v (List.mem_of_mem_take hv)) h1
  exact ⟨T, hT.trans (List.take_sublist l S), hne, hle, hz⟩

end Mine

#print axioms Mine.mine_iff_gen
#print axioms Mine.not_mine
#print axioms Mine.rank_hypothesis_idle
#print axioms Mine.sum_perm
#print axioms Mine.exists_sublist_perm
#print axioms Mine.add_closed
#print axioms Mine.add_zero
#print axioms Mine.exists_neg
#print axioms Mine.dav_unique
#print axioms Mine.shortProp_mono

/-! Second targeted review, scratch file T (a review probe, not a certificate).
The body of `Gen.Conjecture62` is PROVED at groups where the source's statement is true, with a
generic pruned search over ordered tuples that is proved sound against `Gen.HasShortZS`:
* C_2^3 = [2,2,2]: both branches are exercised (k = 1 upper, k = 2 lower);
* C_2 + C_4 = [2,4]: a modulus other than 2, a chain whose direction matters, exp = last factor. -/
set_option maxRecDepth 100000
namespace Rev
open Gen

/-- The body of `Gen.Conjecture62` at one invariant-factor list. -/
def Conj62At (ns : List Nat) : Prop :=
  Chain ns → 2 ≤ ns.length →
    ∀ D, IsDavenport ns D → D = dStar ns →
      ∀ k h, 0 < k → h + k = D → expo ns ≤ h → h ≤ D →
        (D + 1 ≤ 2 * h → sAtMost ns h (D + k)) ∧
        (2 * h < D + 1 → ¬ sAtMost ns h (D + k))

theorem conj_iff : Conjecture62 ↔ ∀ ns, Conj62At ns := Iff.rfl

/-! ### all sublists, a decision procedure for `HasShortZS` -/

def subl : List (List Nat) → List (List (List Nat))
  | [] => [[]]
  | x :: t => (subl t).map (fun T => x :: T) ++ subl t

theorem subl_sound : ∀ (S T : List (List Nat)), T ∈ subl S → T.Sublist S
  | [], T, h => by
    have : T = [] := by simpa [subl] using h
    subst this; exact List.Sublist.slnil
  | x :: t, T, h => by
    simp only [subl, List.mem_append, List.mem_map] at h
    rcases h with ⟨T', h, rfl⟩ | h
    · exact List.cons_sublist_cons.mpr (subl_sound t T' h)
    · exact (subl_sound t T h).cons x

theorem subl_complete : ∀ (S T : List (List Nat)), T.Sublist S → T ∈ subl S
  | [], T, h => by cases h; simp [subl]
  | x :: t, T, h => by
    simp only [subl, List.mem_append, List.mem_map]
    cases h
    · rename_i h'; exact Or.inr (subl_complete t T h')
    · rename_i T' h'; exact Or.inl ⟨T', subl_complete t T' h', rfl⟩

def good (ns : List Nat) (h : Nat) (T : List (List Nat)) : Bool :=
  !T.isEmpty && decide (T.length ≤ h) && decide (sum ns T = zero ns)

def chk (ns : List Nat) (h : Nat) (S : List (List Nat)) : Bool := (subl S).any (good ns h)

theorem chk_iff (ns : List Nat) (h : Nat) (S : List (List Nat)) :
    chk ns h S = true ↔ HasShortZS ns h S := by
  constructor
  · intro hc
    obtain ⟨T, hT, hp⟩ := List.any_eq_true.mp hc
    simp only [good, Bool.and_eq_true, Bool.not_eq_true', decide_eq_true_eq] at hp
    refine ⟨T, subl_sound S T hT, ?_, hp.1.2, hp.2⟩
    intro hnil; subst hnil; simp at hp
  · intro ⟨T, hT, hne, hl, hz⟩
    refine List.any_eq_true.mpr ⟨T, subl_complete S T hT, ?_⟩
    simp only [good, Bool.and_eq_true, Bool.not_eq_true', decide_eq_true_eq]
    refine ⟨⟨?_, hl⟩, hz⟩
    cases T with
    | nil => exact absurd rfl hne
    | cons _ _ => rfl

/-! ### every element of the group, generically -/

def allEls : List Nat → List (List Nat)
  | [] => [[]]
  | n :: ns => (List.range n).flatMap (fun x => (allEls ns).map (fun v => x :: v))

theorem mem_allEls : ∀ (ns v : List Nat), Elem ns v → v ∈ allEls ns
  | [], [], _ => by simp [allEls]
  | n :: ns, x :: v, h => by
    simp only [Elem] at h
    simp only [allEls, List.mem_flatMap, List.mem_range, List.mem_map]
    exact ⟨x, h.1, v, mem_allEls ns v h.2, rfl⟩
  | [], _ :: _, h => by simp [Elem] at h
  | _ :: _, [], h => by simp [Elem] at h

def elemB : List Nat → List Nat → Bool
  | [], [] => true
  | n :: ns, x :: v => decide (x < n) && elemB ns v
  | _, _ => false

theorem elemB_sound : ∀ (ns v : List Nat), elemB ns v = true → Elem ns v
  | [], [], _ => trivial
  | n :: ns, x :: v, h => by
    simp only [elemB, Bool.and_eq_true, decide_eq_true_eq] at h
    exact ⟨h.1, elemB_sound ns v h.2⟩
  | [], _ :: _, h => by simp [elemB] at h
  | _ :: _, [], h => by simp [elemB] at h

theorem over_of_all (ns : List Nat) (S : List (List Nat)) (h : S.all (elemB ns) = true) :
    Over ns S := fun v hv => elemB_sound ns v ((List.all_eq_true.mp h) v hv)

/-! ### pruned search over ordered tuples, sound for `ShortProp` -/

def srch (ns : List Nat) (els : List (List Nat)) (h : Nat) : Nat → List (List Nat) → Bool
  | 0, p => chk ns h p
  | n + 1, p => chk ns h p || els.all (fun g => srch ns els h n (g :: p))

theorem hasShort_mono {ns : List Nat} {h : Nat} {P S : List (List Nat)} (hsub : P.Sublist S) :
    HasShortZS ns h P → HasShortZS ns h S :=
  fun ⟨T, hT, a, b, c⟩ => ⟨T, hT.trans hsub, a, b, c⟩

theorem srch_sound (ns : List Nat) (els : List (List Nat)) (h : Nat)
    (hels : ∀ v, Elem ns v → v ∈ els) :
    ∀ (n : Nat) (p : List (List Nat)), srch ns els h n p = true →
      ∀ e : List (List Nat), e.length = n → Over ns e → HasShortZS ns h (e.reverse ++ p)
  | 0, p, hs, e, he, _ => by
    have : e = [] := List.eq_nil_of_length_eq_zero he
    subst this
    have hc : chk ns h p = true := by simpa [srch] using hs
    simpa using (chk_iff ns h p).mp hc
  | n + 1, p, hs, e, he, hO => by
    cases e with
    | nil => simp at he
    | cons g e' =>
      simp only [srch, Bool.or_eq_true] at hs
      have hrw : (g :: e').reverse ++ p = e'.reverse ++ (g :: p) := by
        simp [List.reverse_cons, List.append_assoc]
      rcases hs with hc | ha
      · exact hasShort_mono (List.sublist_append_right _ _) ((chk_iff ns h p).mp hc)
      · have hg : g ∈ els := hels g (hO g (List.mem_cons_self ..))
        have h1 := (List.all_eq_true.mp ha) g hg
        rw [hrw]
        exact srch_sound ns els h hels n (g :: p) h1 e' (by simpa using he)
          (fun v hv => hO v (List.mem_cons_of_mem _ hv))

theorem shortProp_of_srch (ns : List Nat) (h l : Nat)
    (hs : srch ns (allEls ns) h l [] = true) : ShortProp ns h l := by
  intro S hS hlen
  have := srch_sound ns (allEls ns) h (mem_allEls ns) l [] hs S.reverse (by simpa using hlen)
    (fun v hv => hS v (List.mem_reverse.mp hv))
  simpa using this

theorem davProp_of_shortProp (ns : List Nat) (t : Nat) (hP : ShortProp ns t t) : DavProp ns t := by
  intro S hS hlen
  have h1 : (S.take t).length = t := by simp [List.length_take]; omega
  obtain ⟨T, hT, hne, _, hz⟩ := hP (S.take t) (fun v hv => hS v (List.mem_of_mem_take hv)) h1
  exact ⟨T, hT.trans (List.take_sublist t S), hne, hz⟩

theorem free_of_chk (ns : List Nat) (h : Nat) (S : List (List Nat)) (hc : chk ns h S = false) :
    ¬ HasShortZS ns h S := fun hs => by
  have := (chk_iff ns h S).mpr hs
  rw [hc] at this
  exact Bool.noConfusion this

/-- The prefixes of one sequence show s_{<=h}(G) > B. -/
theorem not_sAtMost_of_prefixes (ns : List Nat) (h B : Nat) (W : List (List Nat))
    (hW : ∀ l, l < B + 1 → (W.take l).length = l ∧ (W.take l).all (elemB ns) = true ∧
      chk ns h (W.take l) = false) : ¬ sAtMost ns h B := by
  intro ⟨l, _, hl, hP⟩
  obtain ⟨h1, h2, h3⟩ := hW l (by omega)
  exact free_of_chk ns h _ h3 (hP _ (over_of_all ns _ h2) h1)

/-- D(G) = d0 from `DavProp d0` and one zero-sum free sequence of length d0 - 1. -/
theorem dav_char (ns : List Nat) (d0 : Nat) (W : List (List Nat)) (hP : DavProp ns d0)
    (hW : W.all (elemB ns) = true) (hlen : W.length + 1 = d0)
    (hfree : chk ns W.length W = false) :
    IsDavenport ns d0 ∧ ∀ D, IsDavenport ns D → D = d0 := by
  have hnz : ¬ HasZS ns W := fun ⟨T, a, b, c⟩ =>
    free_of_chk ns _ W hfree ⟨T, a, b, a.length_le, c⟩
  have low : ∀ t, 0 < t → DavProp ns t → d0 ≤ t := by
    intro t _ hPt
    by_cases hle : d0 ≤ t
    · exact hle
    · exact absurd (hPt W (over_of_all ns W hW) (by omega)) hnz
  refine ⟨⟨by omega, hP, low⟩, ?_⟩
  intro D hD
  have h1 := hD.2.2 d0 (by omega) hP
  have h2 := low D hD.1 hD.2.1
  omega

/-! ## C_2^3: D = 4 = D*, exp = 2. k = 1: upper branch, s_{<=3} <= 5 (source Lemma 1.7(iii):
s_{<=3}(C_2^3) = 2^2 + 1 = 5). k = 2: LOWER branch (2 * 2 < 5), s_{<=2} > 6 (source: s_{<=2}(C_2^3) = 8). -/

def ns3 : List Nat := [2, 2, 2]

theorem s3_dav : srch ns3 (allEls ns3) 4 4 [] = true := by decide +kernel
theorem s3_35 : srch ns3 (allEls ns3) 3 5 [] = true := by decide +kernel

def basis3 : List (List Nat) := [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
def nonzero3 : List (List Nat) :=
  [[1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]]

theorem dav3 : IsDavenport ns3 4 ∧ ∀ D, IsDavenport ns3 D → D = 4 :=
  dav_char ns3 4 basis3 (davProp_of_shortProp ns3 4 (shortProp_of_srch ns3 4 4 s3_dav))
    (by decide +kernel) (by decide) (by decide +kernel)

theorem s3_lower : ¬ sAtMost ns3 2 6 :=
  not_sAtMost_of_prefixes ns3 2 6 nonzero3 (by decide +kernel)

/-- the hypotheses are met: the instance is not vacuous -/
theorem hyp3 : Chain ns3 ∧ 2 ≤ ns3.length ∧ IsDavenport ns3 4 ∧ 4 = dStar ns3 ∧ expo ns3 = 2 :=
  ⟨by simp only [ns3, Chain]; exact ⟨by decide, ⟨1, rfl⟩, by decide, ⟨1, rfl⟩, by decide⟩,
    by decide, dav3.1, by decide, by decide⟩

theorem conj62_true_at_C2_cubed : Conj62At ns3 := by
  intro _ _ D hD _ k h hk hhk he hle
  have hD4 := dav3.2 D hD
  subst hD4
  have hexp : expo ns3 = 2 := by decide
  rw [hexp] at he
  have : (k = 1 ∧ h = 3) ∨ (k = 2 ∧ h = 2) := by omega
  rcases this with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
  · exact ⟨fun _ => ⟨5, by decide, by decide, shortProp_of_srch ns3 3 5 s3_35⟩,
      fun hlt => absurd hlt (by decide)⟩
  · exact ⟨fun hge => absurd hge (by decide), fun _ => s3_lower⟩

/-! ## C_2 + C_4: D = 5 = D*, exp = 4, the only admissible k is 1: s_{<=4} <= 6
(source Lemma 1.7(iv): s_{<=D-k}(G) = D + k for r(G) = 2). -/

def ns24 : List Nat := [2, 4]

theorem s24_dav : srch ns24 (allEls ns24) 5 5 [] = true := by decide +kernel
theorem s24_46 : srch ns24 (allEls ns24) 4 6 [] = true := by decide +kernel

def free24 : List (List Nat) := [[1, 0], [0, 1], [0, 1], [0, 1]]

theorem dav24 : IsDavenport ns24 5 ∧ ∀ D, IsDavenport ns24 D → D = 5 :=
  dav_char ns24 5 free24 (davProp_of_shortProp ns24 5 (shortProp_of_srch ns24 5 5 s24_dav))
    (by decide +kernel) (by decide) (by decide +kernel)

theorem hyp24 : Chain ns24 ∧ 2 ≤ ns24.length ∧ IsDavenport ns24 5 ∧ 5 = dStar ns24 ∧
    expo ns24 = 4 :=
  ⟨by simp only [ns24, Chain]; exact ⟨by decide, ⟨2, rfl⟩, by decide⟩,
    by decide, dav24.1, by decide, by decide⟩

theorem conj62_true_at_C2_C4 : Conj62At ns24 := by
  intro _ _ D hD _ k h hk hhk he hle
  have hD5 := dav24.2 D hD
  subst hD5
  have hexp : expo ns24 = 4 := by decide
  rw [hexp] at he
  have : k = 1 ∧ h = 4 := by omega
  obtain ⟨rfl, rfl⟩ := this
  exact ⟨fun _ => ⟨6, by decide, by decide, shortProp_of_srch ns24 4 6 s24_46⟩,
    fun hlt => absurd hlt (by decide)⟩

/-- With exp read as the FIRST factor (surviving mutant S1) the statement at C_2 + C_4 would also ask
for s_{<=3}(G) <= 7 (k = 2, 2 * 3 >= 6). That is false: six copies of an element of order 4 ... the
source says s_{<=k}(G) = infinity for k < exp(G). Recorded as a fact about `Gen`'s own definitions:
no positive l at all works for h = 3. -/
theorem s24_h3_infinite : ∀ B, ¬ sAtMost ns24 3 B := by
  intro B ⟨l, hl0, _, hP⟩
  have hO : Over ns24 (List.replicate l [0, 1]) := by
    intro v hv
    have := List.eq_of_mem_replicate hv
    subst this
    simp [ns24, Elem]
  obtain ⟨T, hT, hne, hlen, hz⟩ := hP (List.replicate l [0, 1]) hO (by simp)
  -- T is a sublist of a constant list, hence constant, of length 1, 2 or 3; its sum is [0, |T|]
  have hT' : T = List.replicate T.length [0, 1] :=
    List.eq_replicate_iff.mpr ⟨rfl, fun v hv => List.eq_of_mem_replicate (hT.subset hv)⟩
  have : T.length = 1 ∨ T.length = 2 ∨ T.length = 3 := by
    have : T.length ≠ 0 := fun h0 => hne (List.eq_nil_of_length_eq_zero h0)
    omega
  rcases this with h1 | h1 | h1 <;> rw [hT', h1] at hz <;> revert hz <;> decide

/-! ## C_2 + C_2: D = 3 = D*, exp = 2, the only admissible k is 1, h = 2, and 2 * 2 = 3 + 1:
EQUALITY AT THE THRESHOLD in the upper branch, the position of the witness (C_2^4, k = 2); here the
printed statement is true (s_{<=2}(C_2^2) = 4 = D + k). Re-done with this review's own checker. -/

def ns22 : List Nat := [2, 2]

theorem s22_dav : srch ns22 (allEls ns22) 3 3 [] = true := by decide +kernel
theorem s22_24 : srch ns22 (allEls ns22) 2 4 [] = true := by decide +kernel

theorem dav22 : IsDavenport ns22 3 ∧ ∀ D, IsDavenport ns22 D → D = 3 :=
  dav_char ns22 3 [[1, 0], [0, 1]] (davProp_of_shortProp ns22 3 (shortProp_of_srch ns22 3 3 s22_dav))
    (by decide +kernel) (by decide) (by decide +kernel)

theorem conj62_true_at_C2_C2 : Conj62At ns22 := by
  intro _ _ D hD _ k h hk hhk he hle
  have hD3 := dav22.2 D hD
  subst hD3
  have hexp : expo ns22 = 2 := by decide
  rw [hexp] at he
  have : k = 1 ∧ h = 2 := by omega
  obtain ⟨rfl, rfl⟩ := this
  exact ⟨fun _ => ⟨4, by decide, by decide, shortProp_of_srch ns22 2 4 s22_24⟩,
    fun hlt => absurd hlt (by decide)⟩

theorem at_threshold22 : 2 * 2 = 3 + 1 := by decide

end Rev

#print axioms Rev.conj62_true_at_C2_cubed
#print axioms Rev.hyp3
#print axioms Rev.conj62_true_at_C2_C4
#print axioms Rev.hyp24
#print axioms Rev.s24_h3_infinite
#print axioms Rev.conj62_true_at_C2_C2
