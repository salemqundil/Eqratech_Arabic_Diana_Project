(**
  GateSukun: double-sukun detection lemmas.
*)

From FVAFK Require Import Prelude.

Definition seg_is_sukun (seg: string): bool :=
  String.eqb seg "ْ".

Fixpoint segments_has_double_sukun (segments: list string): bool :=
  match segments with
  | s1 :: s2 :: rest =>
      if seg_is_sukun s1 && seg_is_sukun s2
      then true
      else segments_has_double_sukun (s2 :: rest)
  | _ => false
  end.

Theorem segments_has_double_sukun_step:
  forall s1 s2 rest,
    segments_has_double_sukun (s1 :: s2 :: rest) = true ->
    (seg_is_sukun s1 = true /\ seg_is_sukun s2 = true)
    \/ segments_has_double_sukun (s2 :: rest) = true.
Proof.
  intros s1 s2 rest H.
  simpl in H.
  destruct (seg_is_sukun s1 && seg_is_sukun s2) eqn:Hpair.
  - left.
    apply andb_true_iff in Hpair.
    exact Hpair.
  - right. exact H.
Qed.
