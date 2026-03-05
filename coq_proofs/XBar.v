(** * XBar.v - X-bar Theory Inductive Type for C1/C2/C3 Pipeline
    
    Defines the X-bar projection hierarchy as a Coq inductive type
    compatible with the FVAFK pipeline stages:
    
      C1 (Encoding)       → X°   : head / surface form
      C2 (Phon+Morph)     → X'   : bar / intermediate projection
      C3 (Syntax)         → XP   : phrase / maximal projection
    
    Dependency chain:
      C2 is linked to C1 (C2 takes C1 output as input)
      C2 is linked to C3 (C3 takes C2 output as input)
      C1 and C3 are indirectly related through C2
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Require Import Coq.Bool.Bool.
Require Import Assumptions.
Require Import CoreTypes.

Import ListNotations.

(** ** Pipeline Stage Labels *)

(** The three pipeline stages, corresponding to X-bar levels *)
Inductive PipelineStage : Type :=
  | C1 : PipelineStage   (* Encoding & Normalization → X° head *)
  | C2 : PipelineStage   (* Phonology + Morphology   → X' bar  *)
  | C3 : PipelineStage.  (* Syntax                   → XP phrase *)

(** Pipeline stage equality is decidable *)
Definition stage_eq_dec : forall (s1 s2 : PipelineStage), {s1 = s2} + {s1 <> s2}.
Proof. decide equality. Defined.

(** ** X-bar Tree Inductive Type *)

(** X-bar projection levels, mirroring C1/C2/C3 *)
Inductive XBarLevel : Type :=
  | Head  : XBarLevel   (* X°  — C1: base lexical/phonological encoding *)
  | Bar   : XBarLevel   (* X'  — C2: intermediate morpho-phonological form *)
  | Phrase: XBarLevel.  (* XP  — C3: maximal syntactic projection *)

(** An X-bar tree node carries a level, a token reference, and child nodes *)
Inductive XBarTree : Type :=
  (** X° — head node (C1 layer): carries a single token *)
  | XHead : Token -> XBarTree
  (** X' — bar node (C2 layer): head X° plus optional complement XP *)
  | XBarNode : XBarTree -> option XBarTree -> XBarTree
  (** XP — phrase (C3 layer): optional specifier XP, and an X' node *)
  | XPhrase : option XBarTree -> XBarTree -> XBarTree.

(** The level of an X-bar tree node *)
Definition xbar_level (t : XBarTree) : XBarLevel :=
  match t with
  | XHead _        => Head
  | XBarNode _ _   => Bar
  | XPhrase _ _    => Phrase
  end.

(** The pipeline stage corresponding to each X-bar level *)
Definition level_to_stage (lv : XBarLevel) : PipelineStage :=
  match lv with
  | Head   => C1
  | Bar    => C2
  | Phrase => C3
  end.

(** The X-bar level corresponding to each pipeline stage *)
Definition stage_to_level (s : PipelineStage) : XBarLevel :=
  match s with
  | C1 => Head
  | C2 => Bar
  | C3 => Phrase
  end.

(** Round-trip: stage ↔ level *)
Lemma stage_level_roundtrip : forall s,
  level_to_stage (stage_to_level s) = s.
Proof.
  intros []; reflexivity.
Qed.

Lemma level_stage_roundtrip : forall lv,
  stage_to_level (level_to_stage lv) = lv.
Proof.
  intros []; reflexivity.
Qed.

(** ** C1 / C2 / C3 Projection Relations *)

(** C1→C2: a Bar node is directly built on top of a Head node.
    This captures "C2 is linked to C1". *)
Definition c1_feeds_c2 (head : XBarTree) (bar : XBarTree) : Prop :=
  xbar_level head = Head /\
  xbar_level bar  = Bar  /\
  match bar with
  | XBarNode h _ => h = head
  | _            => False
  end.

(** C2→C3: a Phrase node directly contains a Bar node as its core.
    This captures "C2 is linked to C3". *)
Definition c2_feeds_c3 (bar : XBarTree) (phrase : XBarTree) : Prop :=
  xbar_level bar    = Bar    /\
  xbar_level phrase = Phrase /\
  match phrase with
  | XPhrase _ b => b = bar
  | _           => False
  end.

(** C1↔C3 indirect relation: C1 and C3 are related when there exists
    a C2 node that bridges them (C1→C2→C3). *)
Definition c1_related_c3 (head : XBarTree) (phrase : XBarTree) : Prop :=
  exists bar : XBarTree,
    c1_feeds_c2 head bar /\ c2_feeds_c3 bar phrase.

(** ** Well-formedness *)

(** A well-formed X-bar tree obeys:
    - XHead carries a Head-level token (C1 well-typed)
    - XBarNode has a Head child (C1→C2 well-typed)
    - XPhrase has a Bar child (C2→C3 well-typed)
    - Optional specifier of XPhrase must itself be a Phrase (recursive) *)
Fixpoint xbar_wf (t : XBarTree) : Prop :=
  match t with
  | XHead _           => True  (* any token is a valid head *)
  | XBarNode h comp   =>
      xbar_level h = Head /\
      xbar_wf h /\
      match comp with
      | None    => True
      | Some cp => xbar_level cp = Phrase /\ xbar_wf cp
      end
  | XPhrase spec bar  =>
      xbar_level bar = Bar /\
      xbar_wf bar /\
      match spec with
      | None    => True
      | Some sp => xbar_level sp = Phrase /\ xbar_wf sp
      end
  end.

(** ** Construction from X (input) *)

(** Build a minimal X-bar tree from the first token of an input X *)
Definition xbar_from_token (tok : Token) : XBarTree :=
  let head   := XHead tok in
  let bar    := XBarNode head None in
  XPhrase None bar.

(** Build a minimal X-bar tree from an input X *)
Definition xbar_from_input (x : X) : option XBarTree :=
  match tokens x with
  | []      => None
  | tok :: _ => Some (xbar_from_token tok)
  end.

(** ** Properties *)

(** xbar_from_token produces a well-formed tree *)
Lemma xbar_from_token_wf : forall tok,
  xbar_wf (xbar_from_token tok).
Proof.
  intros tok. unfold xbar_from_token. simpl. auto.
Qed.

(** The phrase built by xbar_from_token is at the Phrase level (C3) *)
Lemma xbar_from_token_phrase : forall tok,
  xbar_level (xbar_from_token tok) = Phrase.
Proof.
  intros tok. unfold xbar_from_token. reflexivity.
Qed.

(** xbar_from_token witnesses the C1↔C3 relation *)
Lemma xbar_from_token_c1_related_c3 : forall tok,
  let head   := XHead tok in
  let phrase := xbar_from_token tok in
  c1_related_c3 head phrase.
Proof.
  intros tok. unfold c1_related_c3, xbar_from_token.
  set (head := XHead tok).
  set (bar  := XBarNode head None).
  set (phrase := XPhrase None bar).
  exists bar.
  split.
  - unfold c1_feeds_c2. repeat split. reflexivity.
  - unfold c2_feeds_c3. repeat split. reflexivity.
Qed.

(** For a valid input, xbar_from_input returns Some *)
Lemma xbar_from_input_some : forall x,
  X_valid x -> exists t, xbar_from_input x = Some t.
Proof.
  intros x [Hlen _].
  unfold xbar_from_input.
  destruct (tokens x) eqn:Htok.
  - simpl in Hlen. inversion Hlen.
  - exists (xbar_from_token t). reflexivity.
Qed.

(** For a valid input, xbar_from_input produces a well-formed Phrase *)
Lemma xbar_from_input_wf : forall x t,
  xbar_from_input x = Some t -> xbar_wf t /\ xbar_level t = Phrase.
Proof.
  intros x t Heq.
  unfold xbar_from_input in Heq.
  destruct (tokens x) as [| tok _]; [discriminate |].
  injection Heq as <-.
  split.
  - apply xbar_from_token_wf.
  - apply xbar_from_token_phrase.
Qed.

(** ** C2 as Bridge: Transitivity *)

(** If C1 feeds C2 and C2 feeds C3, then C1 is related to C3 *)
Theorem c2_bridges_c1_c3 : forall head bar phrase,
  c1_feeds_c2 head bar ->
  c2_feeds_c3 bar phrase ->
  c1_related_c3 head phrase.
Proof.
  intros head bar phrase Hc1c2 Hc2c3.
  unfold c1_related_c3.
  exists bar. auto.
Qed.

(** C1→C2→C3 chain is uniquely determined by the head token *)
Theorem c1_c3_chain_from_head : forall tok,
  exists head bar phrase,
    head   = XHead tok             /\
    bar    = XBarNode head None    /\
    phrase = XPhrase None bar      /\
    c1_feeds_c2 head bar           /\
    c2_feeds_c3 bar phrase         /\
    c1_related_c3 head phrase.
Proof.
  intros tok.
  exists (XHead tok), (XBarNode (XHead tok) None), (XPhrase None (XBarNode (XHead tok) None)).
  repeat split; try reflexivity.
  - unfold c1_feeds_c2. repeat split. reflexivity.
  - unfold c2_feeds_c3. repeat split. reflexivity.
  - eapply c2_bridges_c1_c3.
    + unfold c1_feeds_c2. repeat split. reflexivity.
    + unfold c2_feeds_c3. repeat split. reflexivity.
Qed.

(** ** Integration with CoreTypes.Y *)

(** Project an X-bar tree to the CoreTypes.Y graph structure *)
Definition xbar_to_graph (t : XBarTree) : AnalysisGraph :=
  match t with
  | XPhrase spec bar =>
      match bar with
      | XBarNode head comp =>
          let n0 := mkNode 0 None [] in   (* XP / C3 node: id=0, no token ref, no features *)
          let n1 := mkNode 1 None [] in   (* X' / C2 node: id=1, no token ref, no features *)
          let n2 := mkNode 2 None [] in   (* X° / C1 node: id=2, no token ref, no features *)
          let e_c2_c3 := mkEdge 1 0 TADMN 0 in  (* C2 → C3: inclusion *)
          let e_c1_c2 := mkEdge 2 1 ISN   0 in  (* C1 → C2: predication *)
          mkGraph [n0; n1; n2] [e_c2_c3; e_c1_c2]
      | _ => mkGraph [] []
      end
  | _ => mkGraph [] []
  end.

(** The graph for a well-formed XPhrase has exactly 3 nodes and 2 edges *)
Lemma xbar_to_graph_shape : forall tok,
  let t := xbar_from_token tok in
  length (nodes (xbar_to_graph t)) = 3 /\
  length (edges (xbar_to_graph t)) = 2.
Proof.
  intros tok. unfold xbar_from_token. simpl. auto.
Qed.
