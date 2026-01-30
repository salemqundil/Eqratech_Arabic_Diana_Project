Require Import Coq.Lists.List.
Require Import Coq.Strings.String.

(** Simple proof sketch for syllable properties. *)

Definition is_vowel (c: string) : bool :=
  match c with
  | "ا" | "و" | "ي" | "ى" => true
  | _ => false
  end.

Definition syllable_ok (onset nucleus coda: list string) : bool :=
  is_vowel nucleus = true.

Theorem syllable_preserves_vowel:
  forall onset nucleus coda,
    syllable_ok onset nucleus coda = true ->
    is_vowel nucleus = true.
Proof.
  intros. assumption.
Qed.
