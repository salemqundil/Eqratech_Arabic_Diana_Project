(** * Energy.v - Energy Function Definition
    
    Defines the cost function E : X -> Y -> Cost
    with hard constraints (infinite cost) and soft penalties.
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.micromega.Lia.
Require Import Coq.Bool.Bool.
Require Import Assumptions.
Require Import CoreTypes.

Import ListNotations.

(** ** Cost Type *)

(** Cost with infinity *)
Inductive Cost : Type :=
  | Finite : nat -> Cost
  | Infinite : Cost.

(** Cost comparison *)
Definition cost_le (c1 c2 : Cost) : Prop :=
  match c1, c2 with
  | Finite n1, Finite n2 => n1 <= n2
  | Finite _, Infinite => True
  | Infinite, Finite _ => False
  | Infinite, Infinite => True
  end.

(** Cost addition *)
Definition cost_add (c1 c2 : Cost) : Cost :=
  match c1, c2 with
  | Finite n1, Finite n2 => Finite (n1 + n2)
  | _, Infinite => Infinite
  | Infinite, _ => Infinite
  end.

(** Cost minimum *)
Definition cost_min (c1 c2 : Cost) : Cost :=
  match c1, c2 with
  | Finite n1, Finite n2 => Finite (min n1 n2)
  | Finite n, Infinite => Finite n
  | Infinite, c => c
  end.

Notation "c1 <=c c2" := (cost_le c1 c2) (at level 70).
Notation "c1 +c c2" := (cost_add c1 c2) (at level 50, left associativity).

(** ** Gate Conditions *)

(** CV Structure: Consonant-Vowel alternation *)
Definition gate_CV (y : Y) : bool :=
  (* Check that graph has nodes (not phonology, which may be abstract) *)
  match nodes (graph y) with
  | [] => false
  | _ => true
  end.

(** Sig (Signature): Every functional element must be anchored *)
Definition gate_Sig (y : Y) : bool :=
  (* Check that all edges have valid source/target *)
  forallb (fun e => (source e <? length (nodes (graph y))) &&
                    (target e <? length (nodes (graph y))))
          (edges (graph y)).

(** Join: Dependencies must form tree structure (simplified) *)
Definition gate_Join (y : Y) : bool :=
  (* Simplified: no node has multiple incoming ISN edges *)
  true.  (* TODO: implement proper tree check *)

(** Scope: Quantifier scope must be well-nested *)
Definition gate_Scope (y : Y) : bool :=
  true.  (* TODO: implement scope checking *)

(** Maqam gate: Style features must match structure *)
Definition gate_Maqam (x : X) (y : Y) : bool :=
  let m := maqam x in
  (* If interrogative, must have question structure *)
  if Q_polar m then
    (* Check for interrogative particle in graph *)
    true  (* TODO: check question marker presence *)
  else
    true.

(** ** Hard Gates *)

(** All hard gates must pass *)
Definition hard_gates (x : X) (y : Y) : bool :=
  gate_CV y && gate_Sig y && gate_Join y && 
  gate_Scope y && gate_Maqam x y.

(** Hard gate cost: infinite if violated *)
Definition hard_cost (x : X) (y : Y) : Cost :=
  if hard_gates x y then Finite 0 else Infinite.

(** ** Soft Penalties *)

(** Base complexity penalty *)
Definition complexity_penalty (y : Y) : nat :=
  length (nodes (graph y)) + length (edges (graph y)).

(** Relation penalty (prefer simpler relations) *)
Definition relation_penalty (y : Y) : nat :=
  fold_left (fun acc e => 
    acc + match relation e with
          | ISN => 0      (* Predication is basic *)
          | TADMN => 1    (* Embedding adds complexity *)
          | TAQYID => 1   (* Modification adds complexity *)
          end)
    (edges (graph y)) 0.

(** Maqam penalty (deviation from default) *)
Definition maqam_penalty (x : X) : nat :=
  let m := maqam x in
  (if Q_polar m then 1 else 0) +
  (if imperative m then 1 else 0) +
  (if prohibitive m then 1 else 0) +
  (if exclamative m then 1 else 0).

(** ** Total Energy *)

(** Total cost function *)
Definition E (x : X) (y : Y) : Cost :=
  cost_add (hard_cost x y)
    (Finite (complexity_penalty y + 
             relation_penalty y + 
             maqam_penalty x)).

(** ** Properties *)

(** Hard gates violated implies infinite cost *)
Lemma hard_violation_inf : forall x y,
  hard_gates x y = false -> E x y = Infinite.
Proof.
  intros x y H. unfold E, hard_cost. rewrite H. 
  simpl. reflexivity.
Qed.

(** Hard gates satisfied implies finite cost *)
Lemma hard_satisfied_finite : forall x y,
  hard_gates x y = true -> exists n, E x y = Finite n.
Proof.
  intros x y H. unfold E, hard_cost. rewrite H.
  simpl. eexists. reflexivity.
Qed.

(** Cost addition is associative *)
Lemma cost_add_assoc : forall c1 c2 c3,
  (c1 +c c2) +c c3 = c1 +c (c2 +c c3).
Proof.
  intros. destruct c1, c2, c3; simpl; auto.
  f_equal. ring.
Qed.

(** Cost ordering is transitive *)
Lemma cost_le_trans : forall c1 c2 c3,
  c1 <=c c2 -> c2 <=c c3 -> c1 <=c c3.
Proof.
  intros. destruct c1, c2, c3; simpl in *; auto.
  - apply Nat.le_trans with n0; assumption.
  - contradiction.
Qed.
