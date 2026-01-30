Require Import Coq.Lists.List.
Require Import Coq.Strings.String.

Definition is_shadda (c : string) : bool :=
  String.eqb c "ّ".

Definition expand_shadda (segments : list string) : list string :=
  match segments with
  | [] => []
  | seg1 :: seg2 :: rest =>
      if is_shadda seg2 then
        seg1 :: "ْ" :: seg1 :: "َ" :: expand_shadda rest
      else
        seg1 :: seg2 :: expand_shadda rest
  | seg :: rest => seg :: expand_shadda rest
  end.

(* Proof sketch: after expansion, no shadda markers remain. *)
Theorem gate_shadda_eliminates_shadda :
  forall segments,
    count_shadda (expand_shadda segments) = 0.
Proof.
  intros.
  simpl.
  (* TODO: formal count_shadda *)
Admitted.
