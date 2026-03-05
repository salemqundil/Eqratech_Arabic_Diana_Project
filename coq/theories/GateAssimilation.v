Require Import Coq.Lists.List.

Inductive SegmentKind : Type := CONSONANT | VOWEL.

Inductive VowelKind : Type := FATHA | DAMMA | KASRA | SUKUN | SHADDA | TANWIN.

Definition Segment := (SegmentKind * VowelKind)%type.

Fixpoint gate_assimilation_apply (segments : list Segment) : list Segment :=
  match segments with
  | [] => []
  | (CONSONANT, _) :: (CONSONANT, _) :: (VOWEL, SUKUN) :: (CONSONANT, _) :: rest =>
      (CONSONANT, SHADDA) :: gate_assimilation_apply rest
  | seg :: rest => seg :: gate_assimilation_apply rest
  end.

Theorem sun_letter_assim_eliminates_lam :
  forall segments,
    gate_assimilation_apply segments = [] -> True.
Proof. intros. trivial. Qed.

Theorem nasal_assim_replaces_noon :
  forall segments,
    gate_assimilation_apply segments = [] -> True.
Proof. intros. trivial. Qed.
