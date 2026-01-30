(**
 * GateMadd: Arabic madd detection
 *)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.Bool.Bool.
Import ListNotations.

(** Vowel kinds *)
Inductive VowelKind : Type :=
  | FATHA | DAMMA | KASRA | SUKUN | SHADDA
  | TANWIN_FATH | TANWIN_DAMM | TANWIN_KASR.

(** Segment kind *)
Inductive SegmentKind : Type :=
  | CONSONANT (text : nat)
  | VOWEL (vk : VowelKind).

Definition Segment := SegmentKind.

(** Madd letters: alif=0, waw=23, ya=24 *)
Definition is_madd_letter (text : nat) : bool :=
  orb (orb (text =? 0) (text =? 23)) (text =? 24).

(** Valid context: prev vowel matches letter)
Definition is_valid_context (vk : VowelKind) (letter : nat) : bool :=
  match letter with
  | 0 => if vk =? FATHA then true else false
  | 23 => if vk =? DAMMA then true else false
  | 24 => if vk =? KASRA then true else false
  | _ => false
  end.

(** Detect madd at position *)
Fixpoint has_madd_at (segments : list Segment) (pos : nat) : bool :=
  match segments with
  | [] => false
  | VOWEL vk :: CONSONANT cid _ :: rest =>
      match pos with
      | 0 => andb (is_madd_letter cid) (is_valid_context vk cid)
      | S n => has_madd_at (CONSONANT cid _ :: rest) n
      end
  | _ :: rest => has_madd_at rest (pos - 1)
  end.

(** Count madds *)
Fixpoint count_madd (segments : list Segment) : nat :=
  match segments with
  | [] => 0
  | VOWEL vk :: CONSONANT cid _ :: rest =>
      if andb (is_madd_letter cid) (is_valid_context vk cid) then
        1 + count_madd rest
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
