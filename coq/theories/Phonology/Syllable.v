(**
  Basic syllable well-formedness.
*)

From FVAFK Require Import Prelude.

Definition is_vowel (c: string) : bool :=
  match c with
  | "ا" | "و" | "ي" | "ى" => true
  | _ => false
  end.

Record Syllable : Type := {
  onset : list string;
  nucleus : string;
  coda : list string;
}.

Definition syllable_ok (s : Syllable) : bool :=
  is_vowel (nucleus s) = true.

Theorem syllable_preserves_vowel :
  forall s,
    syllable_ok s = true ->
    is_vowel (nucleus s) = true.
Proof.
  intros s H.
  exact H.
Qed.
