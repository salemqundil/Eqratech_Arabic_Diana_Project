(**
  GateShadda: shadda expansion utilities.
*)

From FVAFK Require Import Prelude.

Definition is_shadda (c : string) : bool :=
  String.eqb c "ّ".

Fixpoint count_shadda (segments : list string) : nat :=
  match segments with
  | [] => 0
  | seg :: rest =>
      if is_shadda seg then S (count_shadda rest) else count_shadda rest
  end.

Fixpoint expand_shadda (segments : list string) : list string :=
  match segments with
  | [] => []
  | seg1 :: seg2 :: rest =>
      if is_shadda seg2 then
        seg1 :: "ْ" :: seg1 :: "َ" :: expand_shadda rest
      else
        seg1 :: seg2 :: expand_shadda rest
  | seg :: rest => seg :: expand_shadda rest
  end.

Theorem gate_shadda_does_not_increase_shadda :
  forall segments,
    count_shadda (expand_shadda segments) <= count_shadda segments.
Proof.
  induction segments as [| s1 rest IH].
  - simpl. lia.
  - destruct rest as [| s2 rest'].
    + simpl. destruct (is_shadda s1); simpl; lia.
    + simpl.
      destruct (is_shadda s2) eqn:Hs2.
      * simpl. lia.
      * simpl. specialize (IH). lia.
Qed.
