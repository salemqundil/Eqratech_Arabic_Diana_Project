(* coq/Gates/GateTanwin.v - Sprint 2 Task 2.5.1 *)

From Coq Require Import List.
Import ListNotations.

Module GateTanwin.

Parameter Unit : Type.
Parameter gate_tanwin : list Unit -> list Unit.

Lemma gate_tanwin_preserves_nonempty :
  forall xs, xs <> [] -> gate_tanwin xs <> [].
Proof. Admitted.

End GateTanwin.
