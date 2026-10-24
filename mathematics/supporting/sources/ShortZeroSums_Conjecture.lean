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
