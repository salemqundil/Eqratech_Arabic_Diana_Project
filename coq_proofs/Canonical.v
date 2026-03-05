(** * Canonical.v - Canonical Constructor y0
    
    Defines y0 : forall x, X_valid x -> Y
    and proves it is admissible (E x (y0 x) ≠ ∞).
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.micromega.Lia.
Require Import Assumptions.
Require Import CoreTypes.
Require Import Energy.
Require Import Generator.

Import ListNotations.

(** ** Canonical Constructor *)

(** The canonical constructor returns the base candidate *)
Definition y0 (x : X) (vx : X_valid x) : Y :=
  construct_base_candidate x.

(** ** Admissibility *)

(** Canonical candidate satisfies hard gates *)
Lemma y0_hard_gates : forall x (vx : X_valid x),
  hard_gates x (y0 x vx) = true.
Proof.
  intros x vx. unfold y0, hard_gates.
  unfold construct_base_candidate, construct_base_graph.
  unfold gate_CV, gate_Sig, gate_Join, gate_Scope, gate_Maqam.
  simpl.
  (* Show nodes non-empty (gate_CV) *)
  destruct (tokens x) as [|t ts] eqn:Etok.
  - (* Empty contradicts X_valid *)
    destruct vx as [Hlen [_ _]]. simpl in Hlen. rewrite Etok in Hlen. 
    simpl in Hlen. inversion Hlen.
  - (* Non-empty: nodes = t :: generate_nodes ts 1 *)
    simpl.
    (* Strategy: simplify the boolean expression step by step *)
    unfold generate_ISN_edges.
    (* Prove length of generate_nodes first *)
    assert (Hlen: forall ts' n, length (generate_nodes ts' n) = length ts').
    { clear. intros ts' n. generalize dependent n. induction ts'; simpl; [reflexivity | intros; f_equal; apply IHts']. }
    specialize (Hlen ts 1).
    rewrite Hlen.
    (* Now case analysis on length ts *)
    destruct (length ts) eqn:ElenTs.
    + (* length ts = 0, so ts = [] *)
      destruct ts; [|discriminate].
      simpl. destruct (Q_polar (maqam x)); reflexivity.
    + (* length ts = S n *)
      simpl.
      destruct (n <=? 0) eqn:Elen0.
      * (* n = 0, length ts = 1 *)
        simpl. destruct (Q_polar (maqam x)); reflexivity.
      * (* n >= 1, length ts >= 2 *)
        simpl. destruct (Q_polar (maqam x)); reflexivity.
Qed.

(** Canonical candidate has finite cost *)
Theorem y0_admissible : forall x (vx : X_valid x),
  exists n, E x (y0 x vx) = Finite n.
Proof.
  intros x vx.
  pose proof (y0_hard_gates x vx) as Hg.
  apply hard_satisfied_finite. exact Hg.
Qed.

(** Canonical candidate is in G(x) *)
Lemma y0_in_G : forall x (vx : X_valid x),
  In (y0 x vx) (G x).
Proof.
  intros x vx. unfold y0. apply base_in_G.
Qed.

(** ** Non-emptiness *)

(** There exists admissible candidate *)
Theorem admissible_exists : forall x,
  X_valid x -> exists y, In y (G x) /\ exists n, E x y = Finite n.
Proof.
  intros x vx.
  exists (y0 x vx). split.
  - apply y0_in_G.
  - apply y0_admissible.
Qed.
