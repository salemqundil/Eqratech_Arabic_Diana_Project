(** * Minimizer.v - Argmin Implementation
    
    Defines argmin on finite lists and proves existence
    when at least one finite-cost element exists.
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

Import ListNotations.

(** ** Argmin Definition *)

(** Find minimum cost element in list *)
Fixpoint argmin_aux (f : Y -> Cost) (candidates : list Y) (current_min : Y) (current_cost : Cost) : Y :=
  match candidates with
  | [] => current_min
  | y :: ys =>
      let c := f y in
      if match c, current_cost with
         | Finite n1, Finite n2 => n1 <? n2
         | Finite _, Infinite => true
         | _, _ => false
         end
      then argmin_aux f ys y c
      else argmin_aux f ys current_min current_cost
  end.

(** Argmin with non-empty list *)
Definition argmin (f : Y -> Cost) (candidates : list Y) : option Y :=
  match candidates with
  | [] => None
  | y :: ys => Some (argmin_aux f ys y (f y))
  end.

(** ** Properties *)

(** If list is non-empty, argmin returns Some *)
Lemma argmin_some : forall f ys,
  ys <> [] -> exists y, argmin f ys = Some y.
Proof.
  intros f ys Hne. destruct ys.
  - contradiction.
  - exists (argmin_aux f ys y (f y)). reflexivity.
Qed.

(** Argmin result is in the list *)
Lemma argmin_in : forall f ys y,
  argmin f ys = Some y -> In y ys.
Proof.
  intros f ys y Heq.
  destruct ys as [| y0 ys]; simpl in Heq.
  - discriminate.
  - injection Heq as Hsub.
    (* argmin_aux returns y0 or something from ys *)
    assert (Haux: forall init_list candidates cm cc,
      In cm init_list ->
      (forall c, In c candidates -> In c init_list) ->
      In (argmin_aux f candidates cm cc) init_list).
    { intros init_list. induction candidates as [|c cs IH]; intros cm cc Hin_cm Hall; simpl.
      - exact Hin_cm.
      - destruct (match f c, cc with
                  | Finite n1, Finite n2 => n1 <? n2
                  | Finite _, Infinite => true
                  | _, _ => false
                  end) eqn:Hcmp.
        + apply IH.
          * apply Hall. left. reflexivity.
          * intros c' Hin_c'. apply Hall. right. exact Hin_c'.
        + apply IH.
          * exact Hin_cm.
          * intros c' Hin_c'. apply Hall. right. exact Hin_c'. }
    specialize (Haux (y0 :: ys) ys y0 (f y0)).
    rewrite <- Hsub.
    apply Haux.
    + left. reflexivity.
    + intros c Hin_c. right. exact Hin_c.
Qed.

(** Helper lemma: argmin_aux maintains minimality invariant *)
(** argmin_aux always returns value with minimal cost among all candidates *)
Lemma argmin_aux_minimal : forall f candidates current_min current_cost,
  cost_le current_cost (f current_min) ->
  (forall c, In c candidates -> cost_le current_cost (f c)) ->
  forall cx, In cx (current_min :: candidates) ->
    cost_le (f (argmin_aux f candidates current_min current_cost)) (f cx).
Proof.
  intros f. induction candidates as [| c cs IH]; intros cm cc Hcm Hcs cx Hinx.
  - simpl. destruct Hinx as [->|[]]. unfold cost_le. destruct (f cx); auto.
  - simpl.
    destruct (match f c, cc with
              | Finite n1, Finite n2 => n1 <? n2
              | Finite _, Infinite => true
              | _, _ => false
              end) eqn:Hcmp.
    + apply (IH c (f c)).
      -- destruct (f c), cc; simpl in *; try discriminate; 
         try (apply Nat.ltb_lt in Hcmp; unfold cost_le; lia); unfold cost_le; trivial.
      -- intros c2 Hin2. admit. (* TODO: 3-way case analysis on Hinx *)
    + apply (IH cm cc Hcm).
      -- intros c2 Hin2.
         destruct Hin2 as [->|Hincs2]; [assumption | apply Hcs; right; exact Hincs2].
Admitted. (* TODO: Complete argmin_aux_minimal (second apply argument needs 3-way case on Hinx) *)

(* Helper removed - will be proven inline after resolving nesting issue *)

(** Argmin has minimum cost among candidates *)
Lemma argmin_minimal : forall f ys y,
  argmin f ys = Some y ->
  forall y', In y' ys -> cost_le (f y) (f y').
Proof.
  intros f ys. destruct ys as [| y0 ys]; intros y Harg; simpl in Harg; [discriminate |].
  injection Harg as Heq. intros y' Hin'.
  apply (argmin_aux_minimal f ys y0 (f y0)).
  - unfold cost_le. destruct (f y0); auto.
  - intros. unfold cost_le. destruct (f y0); auto.
  - rewrite <- Heq. right. assumption.
Qed.

(** ** Existence on Finite Lists *)

(** If there exists a finite-cost element, argmin exists *)
Theorem argmin_exists_finite : forall f ys,
  ys <> [] ->
  (exists y, In y ys /\ exists n, f y = Finite n) ->
  exists ystar, argmin f ys = Some ystar /\ exists n, f ystar = Finite n.
Proof.
  intros f ys Hne [y [Hin [n Hfin]]].
  destruct (argmin_some f ys Hne) as [ystar Harg].
  exists ystar. split; auto.
  (* ystar must have finite cost - prove by contradiction *)
  destruct (f ystar) eqn:Hfystar.
  - exists n0. reflexivity.
  - (* Impossible: ystar has infinite cost but y has finite cost *)
    pose proof (argmin_in f ys ystar Harg) as Hinystar.
    pose proof (argmin_minimal f ys ystar Harg y Hin) as Hmin.
    rewrite Hfystar in Hmin. rewrite Hfin in Hmin.
    unfold cost_le in Hmin. contradiction.
Qed.

(** ** Application to Energy Minimization *)

(** For valid input with G(x), minimizer exists *)
Theorem minimizer_exists : forall x,
  X_valid x ->
  exists ystar, argmin (E x) (G x) = Some ystar /\ exists n, E x ystar = Finite n.
Proof.
  intros x Hv.
  apply argmin_exists_finite.
  - apply G_nonempty. exact Hv.
  - apply admissible_exists. exact Hv.
Qed.
