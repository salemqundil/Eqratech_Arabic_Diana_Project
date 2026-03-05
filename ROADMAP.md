# AGT Framework Extension Roadmap

This document outlines the concrete roadmap for extending the AGT (Arabic Grammar Theory) formal framework beyond the foundational architecture established in the initial PR.

## Current Foundation (PR #1)

The current PR establishes:
- **193+ theorems** across **11 Coq modules** (~9,540 lines)
- **8-layer architecture** from root to sentence level
- Master theorems as axioms with example proofs (كتب، كاتب، مكتوب)
- Modular design with Parameters for extensibility

## Extension 1: Full Master Theorem Proofs

**Goal**: Move from axiom-based master theorems to complete formal proofs that **any** `VerbModel`/`NounModel` satisfying well-formedness conditions satisfies AGT invariants.

### 1.1 Strengthen Mathematical Foundation

**File**: `coq/AGT_Mathematical.v`

Export clearly defined predicates:
```coq
(* Predicate: PreRootPattern respects fractal relations *)
Definition PreRoot_Respects_Fractal (pr : PreRootPattern) : Prop :=
  (* Relations sum to 2× triad total *)
  all_relations_value pr = 2 * triad_total_value pr.

(* Predicate: PreRootPattern respects vowel system *)
Definition PreRoot_Respects_Vowels (pr : PreRootPattern) : Prop :=
  (* Short vowels = H, Long = H/2, Sukun = 0 *)
  forall pos, vowel_at pos pr ->
    vowel_value_correct (get_vowel pos pr).

(* Predicate: PreRootPattern complexity follows Fibonacci *)
Definition PreRoot_Complexity_Fib (pr : PreRootPattern) : Prop :=
  exists n, complexity pr = fib n.
```

### 1.2 Catalog-Level Lemmas

**File**: `coq/AGT_DerivationalCatalog.v`

Create explicit `preroot_pattern_catalog` and prove properties for all entries:

```coq
(* Catalog of all standard PreRoot patterns *)
Definition preroot_pattern_catalog : list PreRootPattern :=
  [ pr_fa3ala    (* فَعَلَ *)
  ; pr_fa33ala   (* فَعَّلَ *)
  ; pr_faa3ala   (* فَاعَلَ *)
  ; pr_af3ala    (* أَفْعَلَ *)
  ; pr_tafa33ala (* تَفَعَّلَ *)
  ; pr_tafaa3ala (* تَفَاعَلَ *)
  ; pr_infa3ala  (* انْفَعَلَ *)
  ; pr_ifta3ala  (* افْتَعَلَ *)
  ; pr_if3alla   (* افْعَلَّ *)
  ; pr_istaf3ala (* اسْتَفْعَلَ *)
  (* ... all standard patterns *)
  ].

(* Prove all catalog entries respect fractal *)
Lemma all_preroot_patterns_respect_fractal :
  forall pr, In pr preroot_pattern_catalog ->
    PreRoot_Respects_Fractal pr.
Proof.
  intros pr H_in.
  destruct H_in as [H_eq | H_rest]; subst.
  - (* Case: pr_fa3ala *)
    unfold PreRoot_Respects_Fractal.
    (* Expand definitions and prove arithmetic *)
    ...
  - (* Inductive cases for all other patterns *)
    ...
Qed.

(* Similar lemmas for vowels and Fibonacci *)
Lemma all_preroot_patterns_respect_vowels : ...
Lemma all_preroot_patterns_complexity_fib : ...
```

Associate each `VerbPattern` with its `PreRootPattern`:
```coq
Definition verb_pattern_preroot (vp : VerbPattern) : PreRootPattern :=
  match vp with
  | VP_Fa3ala => pr_fa3ala
  | VP_Fa33ala => pr_fa33ala
  (* ... *)
  end.

Lemma verb_pattern_preroot_in_catalog :
  forall vp, In (verb_pattern_preroot vp) preroot_pattern_catalog.
```

### 1.3 Master Theorem Proofs

**File**: `coq/AGT_LexicalModels.v`

Replace Parameter axioms with proven theorems:

```coq
(* OLD: Parameter PreRoot_Respects_Fractal ... *)
(* NEW: Import from AGT_Mathematical *)

(* Strengthen well-formedness *)
Definition VerbModel_WellFormed_Strong (vm : VerbModel) : Prop :=
  VerbModel_WellFormed vm /\
  In vm.(vm_pre_root) preroot_pattern_catalog.

(* Full proof of master theorem *)
Theorem VerbModel_AGT_Master_Proof :
  forall vm : VerbModel,
    VerbModel_WellFormed_Strong vm ->
    PreRoot_Respects_Fractal vm.(vm_pre_root) /\
    PreRoot_Respects_Vowels vm.(vm_pre_root) /\
    PreRoot_Complexity_Fib vm.(vm_pre_root).
Proof.
  intros vm [H_wf H_in_cat].
  split; [| split].
  - (* Fractal property *)
    apply all_preroot_patterns_respect_fractal.
    exact H_in_cat.
  - (* Vowel property *)
    apply all_preroot_patterns_respect_vowels.
    exact H_in_cat.
  - (* Fibonacci property *)
    apply all_preroot_patterns_complexity_fib.
    exact H_in_cat.
Qed.

(* Similar for NounModel *)
Theorem NounModel_AGT_Master_Proof : ...
```

**Deliverables**:
- ✅ Catalog of all standard PreRoot patterns
- ✅ Proven invariants for each pattern
- ✅ Full Master Theorem proofs (no axioms)
- ✅ ~30-50 new lemmas

---

## Extension 2: Discourse-Compositional Integration

**Goal**: Map discourse relations (سببية، مقابلة، استطراد) to explicit syntactic edges and prove fractal/distribution properties at discourse level.

### 2.1 Discourse Relation Types

**File**: `coq/AGT_Discourse.v` (extend existing)

Add explicit edge types:
```coq
(* Current: Discourse relations as predicates *)
(* NEW: Discourse relations as graph edges *)

Inductive DiscourseEdgeType :=
  | DE_Causality      (* سببية - A causes B *)
  | DE_Contrast       (* مقابلة - A contrasts B *)
  | DE_Digression     (* استطراد - B digresses from A *)
  | DE_Elaboration    (* تفصيل - B elaborates A *)
  | DE_Condition      (* شرط - if A then B *)
  | DE_Concession     (* تنازل - although A, B *)
  | DE_Temporal       (* زمنية - A before/after B *)
  | DE_Purpose        (* غاية - A for purpose of B *).

(* Discourse edge connecting sentence nodes *)
Record DiscourseEdge := {
  de_type : DiscourseEdgeType;
  de_source : SentenceNode;
  de_target : SentenceNode;
  de_strength : nat  (* Measure of connection strength *)
}.
```

### 2.2 Integration with Compositional Syntax

**File**: `coq/AGT_Compositional.v` (extend)

Add discourse layer to composition tree:
```coq
(* Extend CompositionTree with discourse edges *)
Record DiscourseTree := {
  dt_sentences : list SentenceNode;
  dt_edges : list DiscourseEdge;
  dt_coherence : CoherenceRelation  (* Overall discourse coherence *)
}.

(* Discourse-level triad: analogous to C1-C2-C3 *)
Record DiscourseTriad := {
  dt_before : SentenceNode;   (* Previous context *)
  dt_center : SentenceNode;   (* Central sentence *)
  dt_after : SentenceNode     (* Following context *)
}.

(* Convert discourse triad to FractalTriad using strength *)
Definition discourse_triad_to_fractal (dt : DiscourseTriad) : FractalTriad :=
  {| ft_before := sentence_strength dt.(dt_before)
   ; ft_center := sentence_strength dt.(dt_center)
   ; ft_after := sentence_strength dt.(dt_after)
  |}.
```

### 2.3 Fractal Properties at Discourse Level

Prove discourse relations follow fractal pattern:
```coq
(* Discourse edge strength sums to 2× sentence strength *)
Axiom discourse_fractal_property :
  forall dt : DiscourseTriad,
    let ft := discourse_triad_to_fractal dt in
    all_relations_value ft = 2 * triad_total_value ft.

(* Distribution of discourse types follows power law *)
Axiom discourse_distribution_property :
  forall corpus : list DiscourseTree,
    exists alpha, discourse_type_distribution corpus alpha.

(* Coherence increases with fractal alignment *)
Theorem discourse_coherence_fractal_correlation :
  forall dt : DiscourseTree,
    high_coherence dt ->
    exists triads, all triads satisfy fractal_property.
```

**Deliverables**:
- ✅ Discourse edge types formalized
- ✅ Integration with sentence-level syntax
- ✅ Fractal theorems at discourse level
- ✅ ~20-30 new theorems

---

## Extension 3: Complete Sarf Pattern Coverage

**Goal**: Extend `VerbPattern` and `NounDerivPattern` to cover all standard morphological patterns with explicit complexity lemmas.

### 3.1 Extended Verb Pattern Catalog

**File**: `coq/AGT_DerivationalCatalog.v` (extend)

Current: 16 basic patterns
Target: 50+ patterns including rare forms

```coq
(* Add rare and extended patterns *)
Inductive VerbPattern :=
  (* Current 16 patterns... *)
  
  (* Additional Form II variants *)
  | VP_Fa33ala_Variant1  (* فَعَّلَ with specific vowel pattern *)
  | VP_Fa33ala_Variant2  (* فَعَّلَ with alternative pattern *)
  
  (* Quadriliteral patterns *)
  | VP_Fa3lala           (* فَعْلَلَ - quadriliteral base *)
  | VP_Tafa3lala         (* تَفَعْلَلَ - quad Form II *)
  | VP_Infa3lala         (* انْفَعْلَلَ - quad passive *)
  | VP_If3anlala         (* افْعَنْلَلَ - quad intensive *)
  
  (* Rare trilateral forms *)
  | VP_If3awwala         (* افْعَوَّلَ - Form XII *)
  | VP_If3awla           (* افْعَوْلَ - Form XIII *)
  | VP_If3anlala_Tri     (* افْعَنْلَلَ - Form XIV *)
  | VP_If3alalla         (* افْعَلَلَّ - Form XV *)
  
  (* Doubly augmented forms *)
  | VP_Istaf3ala_Variant (* اسْتَفْعَلَ variants *)
  (* ... *)
  .

(* Complexity lemma for each pattern *)
Lemma formII_complexity :
  forall vp, vp = VP_Fa33ala ->
    verb_pattern_complexity vp = fib 3.

Lemma tafa3ala_complexity :
  forall vp, vp = VP_Tafa3ala ->
    verb_pattern_complexity vp = fib 4.

Lemma quadriliteral_base_complexity :
  forall vp, vp = VP_Fa3lala ->
    verb_pattern_complexity vp = fib 5.

(* General complexity theorem *)
Theorem verb_pattern_complexity_complete :
  forall vp : VerbPattern,
    exists n, verb_pattern_complexity vp = fib n /\
    n = count_augmentations vp + 2.
```

### 3.2 Extended Noun Derivative Catalog

```coq
(* Expand from 12 to 30+ noun patterns *)
Inductive NounDerivPattern :=
  (* Current 12 patterns... *)
  
  (* Additional active participles *)
  | ND_IsmFa3il_FormII       (* مُفَعِّل *)
  | ND_IsmFa3il_FormIII      (* مُفَاعِل *)
  | ND_IsmFa3il_FormIV       (* مُفْعِل *)
  | ND_IsmFa3il_FormV        (* مُتَفَعِّل *)
  | ND_IsmFa3il_FormVI       (* مُتَفَاعِل *)
  
  (* Pattern of instance (مرة واحدة) *)
  | ND_IsmMarra_FormI        (* فَعْلَة *)
  | ND_IsmMarra_FormII       (* تَفْعِيلَة *)
  
  (* Pattern of manner variations *)
  | ND_IsmHay2a_Variant1     (* فِعْلَة *)
  | ND_IsmHay2a_Variant2     (* فُعْلَة *)
  
  (* Extended instrument patterns *)
  | ND_IsmAla_Mif3ala        (* مِفْعَلَة *)
  | ND_IsmAla_Mif3al         (* مِفْعَال *)
  | ND_IsmAla_Fi3aal         (* فِعَّال *)
  (* ... *)
  .

(* Complexity lemmas for noun patterns *)
Lemma ism_fa3il_formII_complexity :
  forall nd, nd = ND_IsmFa3il_FormII ->
    noun_pattern_complexity nd = fib 4.
```

### 3.3 Transformation Coverage

Complete transformation rules between all patterns:
```coq
(* Transformations between verb forms *)
Definition transform_formI_to_formII : VerbModel -> option VerbModel.
Definition transform_formII_to_formV : VerbModel -> option VerbModel.
(* ... all standard transformations *)

(* Prove transformation preserves complexity relationships *)
Theorem transform_preserves_fib_relation :
  forall vm1 vm2 transform,
    transform vm1 = Some vm2 ->
    exists k, 
      verb_complexity vm2 = fib (complexity_index vm1 + k).
```

**Deliverables**:
- ✅ 50+ verb patterns with complexity lemmas
- ✅ 30+ noun patterns with complexity lemmas
- ✅ Complete transformation matrix
- ✅ ~100+ new lemmas and theorems

---

## Extension 4: Corpus Interface & Empirical Validation

**Goal**: Connect to real Arabic corpus to empirically test AGT well-formedness and refine theory based on actual language data.

### 4.1 Corpus Data Layer

**New File**: `coq/AGT_Corpus.v`

```coq
(* Raw corpus token *)
Record CorpusToken := {
  ct_surface : string;           (* Surface form *)
  ct_context : list string;      (* Surrounding tokens *)
  ct_source : CorpusSource;      (* Quran, Hadith, Modern, etc. *)
  ct_frequency : nat             (* Occurrence count *)
}.

(* Corpus statistics *)
Record CorpusStats := {
  cs_total_tokens : nat;
  cs_unique_tokens : nat;
  cs_agt_wellformed : nat;       (* Tokens satisfying AGT *)
  cs_coverage_ratio : Q           (* wellformed / total *)
}.

(* Connect to existing VocabRaw *)
Definition corpus_token_to_vocab_raw (ct : CorpusToken) : VocabRaw :=
  {| vr_surface := ct.(ct_surface)
   ; vr_buckwalter := surface_to_buckwalter ct.(ct_surface)
  |}.

(* Connect to segmentation *)
Definition corpus_token_segmentation (ct : CorpusToken) : SegmentationResult :=
  segment (corpus_token_to_vocab_raw ct).

(* Full analysis pipeline *)
Definition corpus_to_wordstate (ct : CorpusToken) : option VocabWordState :=
  let vr := corpus_token_to_vocab_raw ct in
  let seg := segment vr in
  match morphological_analyze seg with
  | Some ws => if AGT_wellformed ws then Some ws else None
  | None => None
  end.
```

### 4.2 Well-Formedness Validation

```coq
(* Predicate: Token satisfies AGT framework *)
Definition AGT_wellformed (ws : VocabWordState) : Prop :=
  match ws.(vws_morphology) with
  | Verb vm => VerbModel_WellFormed_Strong vm
  | Noun nm => NounModel_WellFormed_Strong nm
  | Particle => True  (* Particles have different criteria *)
  end /\
  PreRoot_Respects_Fractal ws.(vws_preroot) /\
  vowel_pattern_valid ws.(vws_vowels).

(* Measure AGT coverage on corpus *)
Definition measure_agt_coverage (corpus : list CorpusToken) : CorpusStats :=
  let total := length corpus in
  let analyzed := filter_map corpus_to_wordstate corpus in
  let wellformed := length analyzed in
  {| cs_total_tokens := total
   ; cs_unique_tokens := length (dedup corpus)
   ; cs_agt_wellformed := wellformed
   ; cs_coverage_ratio := wellformed # total
  |}.
```

### 4.3 Theory Refinement Interface

```coq
(* Identify tokens that fail AGT well-formedness *)
Definition find_agt_failures (corpus : list CorpusToken) 
  : list (CorpusToken * FailureReason) :=
  filter_map (fun ct =>
    match corpus_to_wordstate ct with
    | None => Some (ct, diagnose_failure ct)
    | Some _ => None
    end
  ) corpus.

(* Categorize failure types *)
Inductive FailureReason :=
  | FR_UnknownRoot         (* Root not in catalog *)
  | FR_InvalidPattern      (* Pattern not in catalog *)
  | FR_VowelMismatch       (* Vowels don't match pattern *)
  | FR_ComplexityAnomaly   (* Fibonacci complexity violated *)
  | FR_FractalAnomaly      (* Fractal relations violated *)
  | FR_Other (reason : string).

(* Generate refinement suggestions *)
Definition suggest_theory_refinements 
  (failures : list (CorpusToken * FailureReason))
  : list TheoryRefinement :=
  analyze_failure_patterns failures.

Inductive TheoryRefinement :=
  | AddRootToLexicon (root : Root)
  | AddPatternToCatalog (pattern : VerbPattern)
  | RelaxConstraint (constraint_name : string)
  | ExtendVowelSystem (new_vowel_type : VowelType).
```

### 4.4 Empirical Testing Framework

**New File**: `tests/corpus_validation.v`

```coq
(* Test on Quranic corpus *)
Definition quran_corpus : list CorpusToken := (* load Quranic text *).

Theorem quran_agt_coverage :
  let stats := measure_agt_coverage quran_corpus in
  (cs_coverage_ratio stats >= 90 # 100)%Q.
Proof.
  (* This would be proven empirically after implementation *)
  ...
Admitted.

(* Test on Modern Standard Arabic corpus *)
Definition msa_corpus : list CorpusToken := (* load MSA text *).

Theorem msa_agt_coverage :
  let stats := measure_agt_coverage msa_corpus in
  (cs_coverage_ratio stats >= 85 # 100)%Q.
Proof.
  (* Empirical validation *)
  ...
Admitted.
```

**Deliverables**:
- ✅ Corpus data structures and loaders
- ✅ Analysis pipeline from tokens to WordState
- ✅ Well-formedness validation on real text
- ✅ Failure diagnosis and refinement suggestions
- ✅ Empirical coverage theorems
- ✅ ~40-60 new definitions and tests

---

## Implementation Timeline

### Phase 1: Master Theorems (2-3 weeks)
- Week 1: Catalog all PreRoot patterns
- Week 2: Prove invariants for each pattern
- Week 3: Complete Master Theorem proofs

### Phase 2: Discourse Integration (2-3 weeks)
- Week 1: Define discourse edge types
- Week 2: Integrate with compositional syntax
- Week 3: Prove discourse-level fractal properties

### Phase 3: Complete Sarf Coverage (3-4 weeks)
- Week 1: Add rare verb patterns
- Week 2: Add extended noun patterns
- Week 3: Complete transformation matrix
- Week 4: Prove all complexity lemmas

### Phase 4: Corpus Interface (4-5 weeks)
- Week 1: Design corpus data structures
- Week 2: Implement analysis pipeline
- Week 3: Integrate with existing vocab system
- Week 4: Empirical testing on Quran
- Week 5: Empirical testing on MSA, refinement

**Total Estimated Time**: 11-15 weeks

---

## Success Metrics

### Extension 1: Master Theorems
- ✅ Zero remaining axioms for core theorems
- ✅ All 50+ PreRoot patterns proven
- ✅ VerbModel_AGT_Master and NounModel_AGT_Master fully proven

### Extension 2: Discourse Integration
- ✅ 8 discourse edge types formalized
- ✅ Fractal properties proven at discourse level
- ✅ Integration with 3 levels (word → sentence → discourse)

### Extension 3: Sarf Coverage
- ✅ 50+ verb patterns cataloged
- ✅ 30+ noun patterns cataloged
- ✅ 100+ complexity lemmas proven
- ✅ Complete transformation coverage

### Extension 4: Corpus Validation
- ✅ Analysis pipeline handles 10,000+ tokens
- ✅ ≥90% coverage on Quranic corpus
- ✅ ≥85% coverage on MSA corpus
- ✅ Failure diagnosis system operational
- ✅ Theory refinement loop functional

---

## Long-Term Vision

Beyond these four extensions, future work includes:

1. **Semantic Composition**: Full integration of AGT_Semantics with compositional syntax
2. **Pragmatic Layer**: Context-dependent meaning and speech acts
3. **Diachronic Analysis**: Historical development of patterns
4. **Computational Tools**: Extract verified compiler from Coq to OCaml/Haskell
5. **Educational Applications**: Interactive tutoring system for Arabic grammar
6. **Cross-Linguistic Extensions**: Apply fractal principles to other Semitic languages

---

## Contributing

This roadmap is open for community contributions. Each extension can be developed independently:

- **Extension 1**: Requires strong Coq proof skills
- **Extension 2**: Requires linguistics + graph theory
- **Extension 3**: Requires Arabic morphology expertise
- **Extension 4**: Requires corpus linguistics + programming

See `CONTRIBUTING.md` for guidelines on how to contribute to these extensions.

---

**Last Updated**: 2025-12-02
**Status**: Foundational PR merged, extensions in planning phase
