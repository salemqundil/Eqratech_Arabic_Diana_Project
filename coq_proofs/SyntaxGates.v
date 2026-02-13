(** * SyntaxGates.v - ISN/TADMN/TAQYID Separation
    
    Defines epsilon-separation between syntactic relations
    and proves argmin chooses correct structure.
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.micromega.Lia.
Require Import Assumptions.
Require Import CoreTypes.
Require Import Energy.
Require Import Generator.
Require Import Canonical.
Require Import Minimizer.

Import ListNotations.

(** ** Relation Classification *)

(** Check if graph is ISN structure (predication) *)
Definition is_ISN_structure (g : AnalysisGraph) : bool :=
  existsb (fun e => match relation e with ISN => true | _ => false end) (edges g).

(** Check if graph is TADMN structure (embedding) *)
Definition is_TADMN_structure (g : AnalysisGraph) : bool :=
  existsb (fun e => match relation e with TADMN => true | _ => false end) (edges g).

(** Check if graph is TAQYID structure (modification) *)
Definition is_TAQYID_structure (g : AnalysisGraph) : bool :=
  existsb (fun e => match relation e with TAQYID => true | _ => false end) (edges g).

(** ** Relation Energy *)

(** Additional cost based on relation type *)
Definition relation_type_cost (expected : Relation) (g : AnalysisGraph) : nat :=
  match expected with
  | ISN => if is_ISN_structure g then 0 else epsilon
  | TADMN => if is_TADMN_structure g then 0 else epsilon
  | TAQYID => if is_TAQYID_structure g then 0 else epsilon
  end.

(** Total cost with relation penalty *)
Definition E_with_relation (x : X) (expected : Relation) (y : Y) : Cost :=
  cost_add (E x y) (Finite (relation_type_cost expected (graph y))).

(** ** Epsilon Separation Lemmas *)

(** Correct relation has lower cost *)
Lemma relation_correct_minimal : forall x y expected,
  hard_gates x y = true ->
  (match expected with
   | ISN => is_ISN_structure (graph y) = true
   | TADMN => is_TADMN_structure (graph y) = true
   | TAQYID => is_TAQYID_structure (graph y) = true
   end) ->
  forall y', 
    hard_gates x y' = true ->
    (match expected with
     | ISN => is_ISN_structure (graph y') = false
     | TADMN => is_TADMN_structure (graph y') = false
     | TAQYID => is_TAQYID_structure (graph y') = false
     end) ->
    exists n m, E_with_relation x expected y = Finite n /\
                E_with_relation x expected y' = Finite m /\
                n + epsilon <= m.
Proof.
  intros x y expected Hg Hcorr y' Hg' Hwrong.
  unfold E_with_relation.
  pose proof (hard_satisfied_finite x y Hg) as [n Hn].
  pose proof (hard_satisfied_finite x y' Hg') as [m Hm].
  rewrite Hn, Hm.
  unfold relation_type_cost.
  destruct expected; simpl in Hcorr, Hwrong;
    rewrite Hcorr, Hwrong;
    exists n, (m + epsilon); 
    admit. (* TODO: prove E + penalty = Finite (n + penalty_value) *)
Admitted. (* TODO: Complete arithmetic proofs for epsilon separation *)

(** ** ISN Structure Properties *)

(** ISN requires at least two nodes *)
Definition ISN_valid (x : X) : Prop :=
  length (tokens x) >= 2.

(** ISN candidate from G *)
Definition ISN_candidate (x : X) : Y :=
  construct_base_candidate x.

(** ISN candidate is correct *)
Lemma ISN_candidate_correct : forall x,
  ISN_valid x ->
  is_ISN_structure (graph (ISN_candidate x)) = true.
Proof.
  intros x Hv. unfold ISN_candidate, construct_base_candidate, construct_base_graph.
  simpl. unfold generate_ISN_edges. unfold is_ISN_structure. simpl.
  (* Structure check for ISN *)
Admitted. (* TODO: complete structure verification *)

(** ** Argmin Chooses ISN *)

Theorem argmin_chooses_ISN : forall x,
  X_valid x -> ISN_valid x ->
  exists ystar, 
    argmin (E_with_relation x ISN) (G x) = Some ystar /\
    is_ISN_structure (graph ystar) = true.
Proof.
  intros x Hv HvISN.
  (* ISN candidate exists in G *)
  pose proof (y0_in_G x Hv) as HinG.
  (* ISN candidate is correct *)
  pose proof (ISN_candidate_correct x HvISN) as Hcorr.
  (* Proof strategy: show ISN candidate has minimal cost *)
  admit.  (* TODO: Complete using minimizer properties *)
Admitted.
