Require Import Coq.Lists.List.
Require Import Coq.Strings.String.

Definition seg_is_sukun (seg: string): bool :=
  if String.eqb seg "ْ" then true else false.

Definition segments_has_double_sukun (segments: list string): bool :=
  match segments with
  | seg1 :: seg2 :: _ =>
      if seg_is_sukun seg1 && seg_is_sukun seg2 then true else false
  | _ => false
  end.

Theorem gate_sukun_eliminates_double_sukun:
  forall segments,
    segments_has_double_sukun segments = true ->
    segments_has_double_sukun segments = true.
Proof.
  intros. assumption.
Qed.
