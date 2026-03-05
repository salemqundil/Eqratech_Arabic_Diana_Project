(** * CoreTypes.v - Core Type Definitions
    
    Defines X (input), Y (candidate output), feature space F,
    and fundamental structures without any axioms.
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.Bool.Bool.
Require Import Assumptions.

Import ListNotations.

(** ** Feature Space *)

(** Feature space is the assumed finite type *)
Definition F := FeatureSpaceFinite.

(** Distance metric from assumptions *)
Definition d := distance.

(** ** Token Representation *)

(** A token has consonant and vowel features *)
Record Token : Type := mkToken {
  consonant_features : option F;  (* None if vowel-only *)
  vowel_features : option F;      (* None if consonant-only *)
  diacritics : list F;            (* Additional diacritical marks *)
}.

(** ** Maqam Features (Style/Mode) *)

(** Maqam style markers *)
Record MaqamFeatures : Type := mkMaqam {
  Q_polar : bool;          (* Polar interrogative *)
  Q_wh : option F;         (* Wh-word if present *)
  focus : option nat;      (* Focus position *)
  imperative : bool;       (* Imperative mood *)
  prohibitive : bool;      (* Prohibitive mood *)
  exclamative : bool;      (* Exclamative mood *)
  vocative : option nat;   (* Vocative particle position *)
  assertive : bool;        (* Declarative/assertive *)
}.

(** Default (neutral) maqam *)
Definition neutral_maqam : MaqamFeatures := {|
  Q_polar := false;
  Q_wh := None;
  focus := None;
  imperative := false;
  prohibitive := false;
  exclamative := false;
  vocative := None;
  assertive := true;
|}.

(** ** Input Structure (X) *)

(** Input representation *)
Record X : Type := mkInput {
  tokens : list Token;
  maqam : MaqamFeatures;
  structure_hint : option nat;  (* Optional parse hint *)
}.

(** Valid input predicate *)
Definition X_valid (x : X) : Prop :=
  length (tokens x) > 0 /\
  length (tokens x) <= MaxInputLength /\
  (* At least one token must have features *)
  exists t, In t (tokens x) /\ 
    (consonant_features t <> None \/ vowel_features t <> None).

(** ** Syntactic Relations *)

(** Three core syntactic relations *)
Inductive Relation : Type :=
  | ISN    (* إسناد - Predication *)
  | TADMN  (* تضمين - Inclusion/Embedding *)
  | TAQYID (* تقييد - Restriction/Modification *).

(** Relation equality is decidable *)
Definition rel_eq_dec : forall (r1 r2 : Relation), {r1 = r2} + {r1 <> r2}.
Proof.
  decide equality.
Defined.

(** ** Analysis Graph (Y) *)

(** Node in analysis graph *)
Record Node : Type := mkNode {
  node_id : nat;
  token_ref : option nat;  (* Reference to token in input *)
  node_features : list F;
}.

(** Edge in analysis graph *)
Record Edge : Type := mkEdge {
  source : nat;
  target : nat;
  relation : Relation;
  weight : nat;  (* Cost/strength *)
}.

(** Analysis graph structure *)
Record AnalysisGraph : Type := mkGraph {
  nodes : list Node;
  edges : list Edge;
}.

(** Phonological segments *)
Record Segment : Type := mkSegment {
  segment_features : F;
  is_consonant : bool;
}.

(** Candidate output structure *)
Record Y : Type := mkCandidate {
  graph : AnalysisGraph;
  phonology : list Segment;
  case_marking : list nat;  (* Case markers per nominal *)
}.

(** ** Equivalence Relation *)

(** Two candidates are equivalent if they have same structural properties *)
Definition graph_equiv (g1 g2 : AnalysisGraph) : Prop :=
  length (nodes g1) = length (nodes g2) /\
  length (edges g1) = length (edges g2) /\
  (* Edges have same relations (bidirectional) *)
  (forall e1, In e1 (edges g1) -> 
    exists e2, In e2 (edges g2) /\ relation e1 = relation e2) /\
  (forall e2, In e2 (edges g2) -> 
    exists e1, In e1 (edges g1) /\ relation e1 = relation e2).

Definition eqv (y1 y2 : Y) : Prop :=
  graph_equiv (graph y1) (graph y2) /\
  length (phonology y1) = length (phonology y2).

(** Equivalence is reflexive, symmetric, transitive *)
Lemma eqv_refl : forall y, eqv y y.
Proof.
  intros y. unfold eqv, graph_equiv. 
  split.
  - repeat split; try reflexivity.
    + intros e1 He1. exists e1. auto.
    + intros e2 He2. exists e2. auto.
  - reflexivity.
Qed.

Lemma eqv_symm : forall y1 y2, eqv y1 y2 -> eqv y2 y1.
Proof.
  intros y1 y2 [H1 H2]. unfold eqv, graph_equiv in *.
  destruct H1 as [Hn [He [Hrel12 Hrel21]]]. split.
  - repeat split.
    + symmetry. exact Hn.
    + symmetry. exact He.
    + (* e1 in g2 -> e2 in g1 - this is Hrel21 *)
      intros e1 He1. 
      destruct (Hrel21 e1 He1) as [e2 [He2 Heq]].
      exists e2. split; [exact He2 | symmetry; exact Heq].
    + (* e2 in g1 -> e1 in g2 - this is Hrel12 *)
      intros e2 He2.
      destruct (Hrel12 e2 He2) as [e1 [He1 Heq]].
      exists e1. split; [exact He1 | symmetry; exact Heq].
  - symmetry. exact H2.
Qed.

Lemma eqv_trans : forall y1 y2 y3, eqv y1 y2 -> eqv y2 y3 -> eqv y1 y3.
Proof.
  intros y1 y2 y3 [H12g H12p] [H23g H23p].
  unfold graph_equiv in *.
  destruct H12g as [Hn12 [He12 [Hrel12_fwd Hrel12_bwd]]].
  destruct H23g as [Hn23 [He23 [Hrel23_fwd Hrel23_bwd]]].
  split.
  - repeat split.
    + (* Length nodes *)
      rewrite Hn12. exact Hn23.
    + (* Length edges *)
      rewrite He12. exact He23.
    + (* Forward: e1 in g1 -> e3 in g3 *)
      intros e1 He1. 
      destruct (Hrel12_fwd e1 He1) as [e2 [He2 Heq12]].
      destruct (Hrel23_fwd e2 He2) as [e3 [He3 Heq23]].
      exists e3. split. exact He3.
      rewrite Heq12. exact Heq23.
    + (* Backward: e3 in g3 -> e1 in g1 *)
      intros e3 He3.
      destruct (Hrel23_bwd e3 He3) as [e2 [He2 Heq23]].
      destruct (Hrel12_bwd e2 He2) as [e1 [He1 Heq12]].
      exists e1. split. exact He1.
      rewrite Heq12. exact Heq23.
  - rewrite H12p. exact H23p.
Qed.
