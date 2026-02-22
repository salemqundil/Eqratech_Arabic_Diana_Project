(* coq/Gates/GateSukun.v - Sprint 2 Task 2.5.1 *)

From Coq Require Import List.
Import ListNotations.

Module GateSukun.

Parameter Unit : Type.
Parameter gate_sukun : list Unit -> list Unit.

Lemma gate_sukun_preserves_nonempty :
  forall xs, xs <> [] -> gate_sukun xs <> [].
Proof. Admitted.

End GateSukun.
