(**
  GateIdgham: Tajwid Idgham rules (noon + idgham letter).
*)

From FVAFK Require Import Prelude.

Inductive VowelKind : Type :=
  | FATHA | DAMMA | KASRA | SUKUN | SHADDA
  | TANWIN_FATH | TANWIN_DAMM | TANWIN_KASR | NONE.

Inductive Segment : Type :=
  | CONSONANT (text : nat)
  | VOWEL (vk : VowelKind).

Definition is_idgham_letter (text : nat) : bool :=
  orb (orb (orb (orb (text =? 24) (text =? 12)) (text =? 13)) (text =? 23))
      (orb (text =? 11) (text =? 14)).

Definition is_noon_idgham_pattern (segments : list Segment) : bool :=
  match segments with
  | CONSONANT _ :: VOWEL SUKUN :: CONSONANT target :: _ =>
      is_idgham_letter target
  | _ => false
  end.

Fixpoint apply_noon_idgham (segments : list Segment) : list Segment :=
  match segments with
  | CONSONANT text :: VOWEL SUKUN :: CONSONANT target :: rest =>
      if is_idgham_letter target then
        CONSONANT target :: VOWEL SHADDA :: apply_noon_idgham rest
      else
        CONSONANT text :: VOWEL SUKUN :: CONSONANT target :: apply_noon_idgham rest
  | seg :: rest => seg :: apply_noon_idgham rest
  | [] => []
  end.

Fixpoint count_noon_idgham_patterns (segments : list Segment) : nat :=
  match segments with
  | [] => 0
  | seg :: rest =>
      if is_noon_idgham_pattern (seg :: rest) then
        S (count_noon_idgham_patterns rest)
      else
        count_noon_idgham_patterns rest
  end.

Fixpoint count_shadda (segments : list Segment) : nat :=
  match segments with
  | VOWEL SHADDA :: rest => S (count_shadda rest)
  | _ :: rest => count_shadda rest
  | [] => 0
  end.

Theorem gate_idgham_eliminates_patterns :
  forall segments,
    count_noon_idgham_patterns (apply_noon_idgham segments) = 0.
Proof.
  intros segments.
  induction segments as [| seg rest IH].
  - simpl. reflexivity.
  - simpl. destruct seg; auto.
Admitted.

Theorem gate_idgham_adds_shadda :
  forall segments,
    count_shadda (apply_noon_idgham segments) >= count_noon_idgham_patterns segments.
Proof.
  admit.
Admitted.
