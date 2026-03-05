Require Import Coq.Lists.List.

Inductive VowelKind : Type :=
  | FATHA
  | DAMMA
  | KASRA
  | SUKUN
  | TANWIN_FATH
  | TANWIN_DAMM
  | TANWIN_KASR.

Inductive Segment : Type :=
  | CONSONANT (cid : nat)
  | VOWEL (vk : VowelKind).

Definition is_tanwin (seg : Segment) : bool :=
  match seg with
  | VOWEL TANWIN_FATH => true
  | VOWEL TANWIN_DAMM => true
  | VOWEL TANWIN_KASR => true
  | _ => false
  end.

Fixpoint count_tanwin (segments : list Segment) : nat :=
  match segments with
  | [] => 0
  | seg :: rest =>
      if is_tanwin seg then 1 + count_tanwin rest
      else count_tanwin rest
  end.

Fixpoint gate_tanwin_apply (segments : list Segment) : list Segment :=
  match segments with
  | [] => []
  | VOWEL vk :: rest =>
      if is_tanwin (VOWEL vk) then
        VOWEL (match vk with
               | TANWIN_FATH => FATHA
               | TANWIN_DAMM => DAMMA
               | TANWIN_KASR => KASRA
               | _ => vk
               end) ::
        CONSONANT 12 :: VOWEL SUKUN :: gate_tanwin_apply rest
      else
        VOWEL vk :: gate_tanwin_apply rest
  | seg :: rest => seg :: gate_tanwin_apply rest
  end.

Theorem gate_tanwin_eliminates_tanwin :
  forall segments,
    count_tanwin (gate_tanwin_apply segments) = 0.
Proof.
  intros segments.
  induction segments as [| seg rest IH].
  - simpl. reflexivity.
  - simpl. destruct seg; simpl; try apply IH.
    + destruct v; simpl; try apply IH.
Qed.
