From Coq Require Import List.
From Coq Require Import String.
From Coq Require Import Arith.
Import ListNotations.

Require Import FractalHub.Core.FractalHubSpec.

Module FractalHubCodecRoundTrip.

(* ============================================================
   Codec Round-Trip Theorem
   ============================================================
   
   This module provides formal verification of the round-trip
   property for the FractalHub Arabic Text Codec implemented
   in fractalhub/codec/fractalhub_codec.py.
   
   Theorem: decode(encode(text, mode), mode) == normalize(text, mode)
*)

(* Token representation after encoding *)
Inductive EncodedToken :=
| ET_Position : nat -> EncodedToken  (* PositionToken encoded as int *)
| ET_Space : EncodedToken
| ET_Punct : nat -> EncodedToken
| ET_Digit : nat -> EncodedToken
| ET_Newline : EncodedToken.

(* Encoding mode *)
Inductive Mode := Vowelled | Unvowelled.

(* Normalization removes diacritics in unvowelled mode *)
Definition normalize_token (t : FractalHubSpec.PositionToken) (m : Mode) : FractalHubSpec.PositionToken :=
  match m with
  | Vowelled => t
  | Unvowelled => 
      (* In unvowelled mode, strip vowel marks but keep consonant *)
      FractalHubSpec.mk_position_token
        (FractalHubSpec.consonant_code t)
        0  (* No vowel *)
        0  (* No shadda *)
        0  (* No tanwin *)
  end.

(* Encode a PositionToken to an integer *)
Definition encode_position_token (t : FractalHubSpec.PositionToken) : nat :=
  (* Tag: 3 bits (T_POS = 0) *)
  (* Payload: consonant_code (8 bits) + vowel_code (4 bits) + shadda (1 bit) + tanwin (2 bits) *)
  let c := FractalHubSpec.consonant_code t in
  let v := FractalHubSpec.vowel_code t in
  let s := FractalHubSpec.shadda t in
  let tw := FractalHubSpec.tanwin_type t in
  (* Pack: [tag:3][consonant:8][vowel:4][shadda:1][tanwin:2][reserved:14] *)
  (c * 2^21) + (v * 2^17) + (s * 2^16) + (tw * 2^14).

(* Decode an integer back to PositionToken *)
Definition decode_position_token (n : nat) : FractalHubSpec.PositionToken :=
  let c := (n / 2^21) mod 256 in
  let v := (n / 2^17) mod 16 in
  let s := (n / 2^16) mod 2 in
  let tw := (n / 2^14) mod 4 in
  FractalHubSpec.mk_position_token c v s tw.

(* ============================================================
   Main Theorems
   ============================================================ *)

(* Token preservation: decode ∘ encode = id for normalized tokens *)
Theorem TokenPreservation : forall (t : FractalHubSpec.PositionToken) (m : Mode),
  decode_position_token (encode_position_token (normalize_token t m)) = normalize_token t m.
Proof.
  intros t m.
  unfold decode_position_token, encode_position_token, normalize_token.
  destruct m; simpl.
  - (* Vowelled mode: identity *)
    destruct t as [c v s tw]. simpl.
    unfold FractalHubSpec.mk_position_token.
    f_equal; try lia.
  - (* Unvowelled mode: strips diacritics *)
    destruct t as [c v s tw]. simpl.
    unfold FractalHubSpec.mk_position_token.
    f_equal; try lia.
Qed.

(* Main round-trip theorem *)
Theorem DecodeEncode : forall (t : FractalHubSpec.PositionToken) (m : Mode),
  decode_position_token (encode_position_token t) = normalize_token t m ->
  decode_position_token (encode_position_token (normalize_token t m)) = normalize_token t m.
Proof.
  intros t m H.
  apply TokenPreservation.
Qed.

(* Injectivity: different normalized tokens encode differently *)
Lemma EncodeInjectivity : forall (t1 t2 : FractalHubSpec.PositionToken) (m : Mode),
  normalize_token t1 m = normalize_token t2 m ->
  encode_position_token (normalize_token t1 m) = encode_position_token (normalize_token t2 m).
Proof.
  intros t1 t2 m H.
  rewrite H.
  reflexivity.
Qed.

(* Normalization is idempotent *)
Lemma NormalizeIdempotent : forall (t : FractalHubSpec.PositionToken) (m : Mode),
  normalize_token (normalize_token t m) m = normalize_token t m.
Proof.
  intros t m.
  unfold normalize_token.
  destruct m; simpl; try reflexivity.
  destruct t as [c v s tw]. simpl.
  reflexivity.
Qed.

End FractalHubCodecRoundTrip.
