(* coq/Gates/GateShadda.v - Sprint 2 Task 2.5.1 *)

From Coq Require Import List.
Import ListNotations.

Module GateShadda.

Parameter Unit : Type.
Parameter gate_shadda : list Unit -> list Unit.

Lemma gate_shadda_preserves_nonempty :
  forall xs, xs <> [] -> gate_shadda xs <> [].
Proof. Admitted.

End GateShadda.
