(** * FractalHub Gates
    
    This module defines the gate mechanisms and transitions for the FractalHub system.
    Gates control the flow of data and state transitions between hubs.
*)

Require Import FractalHub.FractalHubSpec.

(** ** Gate Types *)

(** Gate operation types *)
Inductive GateOp : Type :=
  | Open : GateOp
  | Close : GateOp
  | Toggle : GateOp.

(** Gate structure connecting two hubs *)
Record Gate := {
  gate_source : HubId;
  gate_target : HubId;
  gate_op : GateOp
}.

(** ** Gate Operations *)

(** Apply a gate operation to change hub state *)
Definition apply_gate (g : Gate) (h : Hub) : Hub :=
  match gate_op g with
  | Open => 
      {| hub_id := hub_id h;
         hub_state := Active;
         hub_capacity := hub_capacity h |}
  | Close => 
      {| hub_id := hub_id h;
         hub_state := Inactive;
         hub_capacity := hub_capacity h |}
  | Toggle =>
      match hub_state h with
      | Active => {| hub_id := hub_id h;
                     hub_state := Inactive;
                     hub_capacity := hub_capacity h |}
      | Inactive => {| hub_id := hub_id h;
                       hub_state := Active;
                       hub_capacity := hub_capacity h |}
      | Suspended => h
      end
  end.

(** ** Gate Properties *)

(** Theorem: Opening a gate makes a hub active *)
Theorem open_gate_activates : forall (g : Gate) (h : Hub),
  gate_op g = Open ->
  hub_state (apply_gate g h) = Active.
Proof.
  intros g h H.
  unfold apply_gate.
  rewrite H.
  simpl.
  reflexivity.
Qed.

(** Theorem: Closing a gate makes a hub inactive *)
Theorem close_gate_deactivates : forall (g : Gate) (h : Hub),
  gate_op g = Close ->
  hub_state (apply_gate g h) = Inactive.
Proof.
  intros g h H.
  unfold apply_gate.
  rewrite H.
  simpl.
  reflexivity.
Qed.
