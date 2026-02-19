(** * Assumptions.v - Mathematical and Physical Axioms
    
    This file contains ALL external axioms used in the development.
    Every axiom must be justified as physically/mathematically grounded
    and shown to be the weakest form necessary for the proofs.
    
    Justification Table:
    
    | AssumptionName            | Type                          | Justification                                    | WeakestForm                          |
    |---------------------------|-------------------------------|--------------------------------------------------|--------------------------------------|
    | FeatureSpaceFinite        | Type                          | Physical phonetic features are discrete/bounded  | Finite type (not continuous)         |
    | DistanceSemiMetric        | Prop                          | Perceptual distance satisfies triangle ineq.     | Semi-metric (not full metric)        |
    | BoundedInput              | nat                           | Physical utterances have finite length           | Natural number bound                 |
    | EpsilonSeparation         | nat                           | Non-equivalent structures distinguishable        | eps >= 1 (minimal discrimination)    |
*)

(** ** Feature Space Assumptions *)

(** Physical features are finite and discrete *)
Axiom FeatureSpaceFinite : Type.
(** Justification: Phonetic features (voicing, place, manner, etc.) 
    are finite in number and take discrete values, not continuous reals. *)

(** Feature values are bounded *)
Axiom FeatureBound : nat.
(** Justification: Each feature has a finite range (e.g., 0-7 for place of articulation). *)

(** Distance is a semi-metric on features *)
Axiom distance : FeatureSpaceFinite -> FeatureSpaceFinite -> nat.

(** Distance axioms (weakest form: semi-metric, not full metric) *)
Axiom distance_refl : forall f, distance f f = 0.
Axiom distance_symm : forall f1 f2, distance f1 f2 = distance f2 f1.
Axiom distance_triangle : forall f1 f2 f3, 
  distance f1 f3 <= distance f1 f2 + distance f2 f3.
(** Note: We do NOT assume distance_pos_definite (d(x,y)=0 => x=y),
    allowing for perceptually indistinguishable features. *)

(** ** Input Bounds *)

(** Maximum input length (physical constraint) *)
Definition MaxInputLength : nat := 100.
(** Justification: Human utterances are bounded in length; 
    100 tokens is generous upper bound for single sentences. *)

(** Maximum branching in candidate generation *)
Definition MaxBranching : nat := 10.
(** Justification: Per decision point, linguistic ambiguity is bounded;
    10 alternatives per choice point covers typical cases. *)

(** ** Separation Constants *)

(** Epsilon for structural separation *)
Definition epsilon : nat := 1.
(** Justification: Minimal discrimination unit; 
    distinct structures must differ by at least 1 in cost. *)

(** ** Decidability Assumptions *)

(** Feature equality is decidable *)
Axiom feature_eq_dec : forall (f1 f2 : FeatureSpaceFinite), {f1 = f2} + {f1 <> f2}.
(** Justification: Finite discrete features have decidable equality. *)

(** END OF ASSUMPTIONS *)
(** All other definitions and proofs must be constructive. *)
