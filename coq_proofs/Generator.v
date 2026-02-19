(** * Generator.v - Candidate Generation
    
    Defines G(x) that generates finite list of candidate analyses.
    Proves finiteness and boundedness.
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.micromega.Lia.
Require Import Assumptions.
Require Import CoreTypes.

Import ListNotations.

(** ** Basic Generators *)

(** Generate nodes from tokens *)
Fixpoint generate_nodes (tokens : list Token) (offset : nat) : list Node :=
  match tokens with
  | [] => []
  | t :: ts => mkNode offset (Some offset) [] :: generate_nodes ts (S offset)
  end.

(** Generate ISN edges (predication) *)
Definition generate_ISN_edges (n : nat) : list Edge :=
  if n <=? 1 then []
  else [mkEdge 0 1 ISN 0].

(** Generate TADMN edges (embedding) *)
Definition generate_TADMN_edges (n : nat) : list Edge :=
  if n <=? 2 then []
  else [mkEdge 0 2 TADMN 1].

(** Generate TAQYID edges (modification) *)
Definition generate_TAQYID_edges (n : nat) : list Edge :=
  if n <=? 1 then []
  else [mkEdge 1 0 TAQYID 1].

(** ** Base Candidate Constructor *)

(** Construct base analysis graph *)
Definition construct_base_graph (x : X) : AnalysisGraph :=
  let nodes := generate_nodes (tokens x) 0 in
  let n := length nodes in
  mkGraph nodes (generate_ISN_edges n).

(** Construct base candidate *)
Definition construct_base_candidate (x : X) : Y :=
  mkCandidate (construct_base_graph x) [] [].

(** ** Candidate Generator *)

(** Generate alternative analyses with different relations *)
Definition G (x : X) : list Y :=
  let base := construct_base_candidate x in
  let nodes := generate_nodes (tokens x) 0 in
  let n := length nodes in
  [
    (* Base ISN structure *)
    base;
    (* TADMN alternative *)
    mkCandidate (mkGraph nodes (generate_TADMN_edges n)) [] [];
    (* TAQYID alternative *)
    mkCandidate (mkGraph nodes (generate_TAQYID_edges n)) [] []
  ].

(** ** Finiteness *)

(** G always returns finite list *)
Lemma G_finite : forall x, exists n, length (G x) = n.
Proof.
  intros x. exists 3. reflexivity.
Qed.

(** G is not empty for valid input *)
Lemma G_nonempty : forall x, X_valid x -> G x <> [].
Proof.
  intros x Hv. unfold G. discriminate.
Qed.

(** Length of G is bounded *)
Lemma G_bounded : forall x, length (G x) <= MaxBranching.
Proof.
  intros x. unfold G. simpl. unfold MaxBranching. lia.
Qed.

(** ** Membership *)

(** Base candidate is always in G *)
Lemma base_in_G : forall x,
  In (construct_base_candidate x) (G x).
Proof.
  intros x. unfold G. simpl. left. reflexivity.
Qed.

(** All candidates in G have bounded size *)
Lemma G_candidates_bounded : forall x y,
  In y (G x) -> 
  length (nodes (graph y)) <= length (tokens x).
Proof.
  intros x y Hin. unfold G in Hin. simpl in Hin.
  (* All three candidates have nodes = tokens *)
  destruct Hin as [H | [H | [H | []]]]; subst; simpl;
  unfold construct_base_candidate, construct_base_graph; simpl; auto.
Admitted. (* TODO: complete induction proof *)
