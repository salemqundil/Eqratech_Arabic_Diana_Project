(**
  GateMadd: Arabic madd detection (normalized).
*)

From FVAFK Require Import Prelude.

Inductive VowelKind : Type :=
  | FATHA | DAMMA | KASRA | SUKUN | SHADDA
  | TANWIN_FATH | TANWIN_DAMM | TANWIN_KASR.

Definition VowelKind_beq (a b : VowelKind) : bool :=
  match a, b with
  | FATHA, FATHA => true
  | DAMMA, DAMMA => true
  | KASRA, KASRA => true
  | SUKUN, SUKUN => true
  | SHADDA, SHADDA => true
  | TANWIN_FATH, TANWIN_FATH => true
  | TANWIN_DAMM, TANWIN_DAMM => true
  | TANWIN_KASR, TANWIN_KASR => true
  | _, _ => false
  end.

Inductive Segment : Type :=
  | CONSONANT (text : nat)
  | VOWEL (vk : VowelKind).

Definition is_madd_letter (text : nat) : bool :=
  orb (orb (text =? 0) (text =? 23)) (text =? 24).

Definition is_valid_context (vk : VowelKind) (letter : nat) : bool :=
  match letter with
  | 0 => VowelKind_beq vk FATHA
  | 23 => VowelKind_beq vk DAMMA
  | 24 => VowelKind_beq vk KASRA
  | _ => false
  end.

Fixpoint has_madd_at (segments : list Segment) (pos : nat) : bool :=
  match segments with
  | [] => false
  | VOWEL vk :: CONSONANT cid :: rest =>
      match pos with
      | 0 => andb (is_madd_letter cid) (is_valid_context vk cid)
      | S n => has_madd_at (CONSONANT cid :: rest) n
      end
  | _ :: rest =>
      match pos with
      | 0 => false
      | S n => has_madd_at rest n
      end
  end.

Fixpoint count_madd (segments : list Segment) : nat :=
  match segments with
  | [] => 0
  | VOWEL vk :: CONSONANT cid :: rest =>
      if andb (is_madd_letter cid) (is_valid_context vk cid) then
        S (count_madd rest)
      else
        count_madd rest
  | _ :: rest => count_madd rest
  end.

Theorem madd_count_matches_detection :
  forall segments pos,
    has_madd_at segments pos = true ->
    count_madd segments > 0.
Proof.
  intros.
  admit.
Admitted.
