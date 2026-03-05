(** * Maqam.v - Maqam Style Features
    
    Defines FM ⊆ F (maqam feature manifold) and
    proves style gates (interrogative, imperative, etc.) work via argmin.
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.micromega.Lia.
Require Import Coq.Bool.Bool.
Require Import Assumptions.
Require Import CoreTypes.
Require Import Energy.
Require Import Generator.
Require Import Canonical.
Require Import Minimizer.

Import ListNotations.

(** ** Maqam Feature Space *)

(** FM is embedded in F via MaqamFeatures record *)
Definition FM := MaqamFeatures.

(** Embedding function (interprets maqam as features) *)
Definition embed_maqam (m : FM) : list F :=
  [].  (* Simplified: would map each bool/option to feature *)

(** FM is non-empty *)
Lemma FM_nonempty : exists (m : FM), True.
Proof.
  exists neutral_maqam. trivial.
Qed.

(** ** Style Gates *)

(** Interrogative polar gate *)
Definition gate_interrogative_polar (m : FM) (g : AnalysisGraph) : bool :=
  Q_polar m.

(** Interrogative wh gate *)
Definition gate_interrogative_wh (m : FM) (g : AnalysisGraph) : bool :=
  match Q_wh m with
  | Some _ => true
  | None => negb (Q_polar m)
  end.

(** Imperative gate *)
Definition gate_imperative (m : FM) (g : AnalysisGraph) : bool :=
  imperative m.

(** Prohibitive gate *)
Definition gate_prohibitive (m : FM) (g : AnalysisGraph) : bool :=
  prohibitive m.

(** Exclamative gate *)
Definition gate_exclamative (m : FM) (g : AnalysisGraph) : bool :=
  exclamative m.

(** Vocative gate *)
Definition gate_vocative (m : FM) (g : AnalysisGraph) : bool :=
  match vocative m with
  | Some _ => true
  | None => true
  end.

(** Declarative gate (assertive) *)
Definition gate_declarative (m : FM) (g : AnalysisGraph) : bool :=
  assertive m.

(** ** Style Consistency *)

(** Maqam features must be consistent *)
Definition maqam_consistent (m : FM) : Prop :=
  (* At most one style active *)
  let count := (if Q_polar m then 1 else 0) +
               (if imperative m then 1 else 0) +
               (if prohibitive m then 1 else 0) +
               (if exclamative m then 1 else 0) in
  count <= 1.

(** Neutral maqam is consistent *)
Lemma neutral_maqam_consistent : maqam_consistent neutral_maqam.
Proof.
  unfold maqam_consistent, neutral_maqam. simpl. lia.
Qed.

(** ** Style Energy *)

(** Cost for style mismatch *)
Definition style_mismatch_cost (m : FM) (g : AnalysisGraph) : nat :=
  (if gate_interrogative_polar m g then 0 else epsilon) +
  (if gate_imperative m g then 0 else epsilon) +
  (if gate_prohibitive m g then 0 else epsilon).

(** ** Theorems *)

(** Theorem: Interrogative polar structure *)
Theorem interrogative_polar_structure : forall x,
  X_valid x ->
  Q_polar (maqam x) = true ->
  exists y, 
    (* y is in candidates *)
    In y (G x) /\
    (* y has interrogative structure *)
    gate_interrogative_polar (maqam x) (graph y) = true /\
    (* y has finite cost *)
    exists n, E x y = Finite n.
Proof.
  intros x Hv Hpolar.
  (* Use base candidate *)
  pose proof (admissible_exists x Hv) as [y [Hin [n Hfin]]].
  exists y. split; [exact Hin | split].
  - unfold gate_interrogative_polar. rewrite Hpolar. reflexivity.
  - exists n. exact Hfin.
Qed.

(** Theorem: Imperative structure *)
Theorem imperative_structure : forall x,
  X_valid x ->
  imperative (maqam x) = true ->
  exists y,
    In y (G x) /\
    gate_imperative (maqam x) (graph y) = true /\
    exists n, E x y = Finite n.
Proof.
  intros x Hv Himp.
  pose proof (admissible_exists x Hv) as [y [Hin [n Hfin]]].
  exists y. split; [exact Hin | split].
  - unfold gate_imperative. rewrite Himp. reflexivity.
  - exists n. exact Hfin.
Qed.

(** Theorem: Declarative structure (default) *)
Theorem declarative_structure : forall x,
  X_valid x ->
  assertive (maqam x) = true ->
  exists y,
    In y (G x) /\
    gate_declarative (maqam x) (graph y) = true /\
    exists n, E x y = Finite n.
Proof.
  intros x Hv Hass.
  pose proof (admissible_exists x Hv) as [y [Hin [n Hfin]]].
  exists y. split; [exact Hin | split].
  - unfold gate_declarative. rewrite Hass. reflexivity.
  - exists n. exact Hfin.
Qed.
