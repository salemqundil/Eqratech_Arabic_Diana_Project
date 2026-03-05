(** Arabic Lexical Ontology - Initial Coq Encoding **)
(** Based on AGT (Arabic Generative Theorem) Framework **)

From Coq Require Import String List.
Import ListNotations.

Set Implicit Arguments.
Set Asymmetric Patterns.

Module ArabicOntology.

(** ========== 1. Atomic identifiers ========== *)

Definition LexemeID   := nat.
Definition SenseID    := nat.
Definition TokenID    := nat.
Definition DocumentID := nat.
Definition EntityID   := nat.  (* مرجع إحالي في الخطاب *)

(** ========== 2. C-slots and RootC2Layer ========== *)

Inductive CSlot := C1 | C2 | C3 | C4.

(* نُبقي التمثيل الصوتي للحرف مجرداً الآن (كود عددي أو ID) *)
Record Consonant := {
  cons_id : nat
}.

Inductive RootClass :=
| RootTriliteral      (* ثلاثي *)
| RootQuadriliteral   (* رباعي *)
| RootOther.          (* خماسي أو غيره *)

(* دور C2 الدلالي/الفعلي كما في نظرية AGT *)
Inductive C2SemanticRole :=
| C2_Agentive       (* فاعلية *)
| C2_Patientive     (* مفعولية / انفعال *)
| C2_Eventive       (* حدث *)
| C2_Stative        (* حالة *)
| C2_Instrumental   (* أداة / وسيلة *)
| C2_Other.

(* طبقة الجذر حول C2 *)
Record RootC2Layer := {
  r_c1      : option Consonant;  (* قد يكون لبعض الجذور C1 غير موجود *)
  r_c2      : Consonant;         (* C2 هو المركز الدلالي *)
  r_c3      : option Consonant;
  r_c4      : option Consonant;
  r_class   : RootClass;
  r_c2_role : C2SemanticRole
}.

(** ========== 3. Extra letters (الحروف الزائدة العشرة) ========== *)

Inductive ExtraLetter :=
| Extra_seen      (* س *)
| Extra_hamza     (* ء *)
| Extra_lam       (* ل *)
| Extra_ta        (* ت *)
| Extra_meem      (* م *)
| Extra_waw       (* و *)
| Extra_noon      (* ن *)
| Extra_ya        (* ي *)
| Extra_ha        (* ه *)
| Extra_alif.     (* ا *)

Inductive ExtraFunction :=
| ExtraFunction_Tense             (* س، سوف، نون النسوة... *)
| ExtraFunction_Gender            (* تاء التأنيث، ألف التأنيث... *)
| ExtraFunction_Number            (* مفرد/مثنى/جمع *)
| ExtraFunction_Agreement         (* الشخص والعدد مع الضمائر *)
| ExtraFunction_CaseMood          (* الرفع/النصب/الجر/الجزم *)
| ExtraFunction_Valency           (* التعدية، اللزوم، السببية، المطاوعة *)
| ExtraFunction_LogicalMode       (* نفي، استفهام، شرط، توكيد... *)
| ExtraFunction_Phonological      (* وظائف صوتية *)
| ExtraFunction_NominalDerivation (* اشتقاق الأسماء *)
| ExtraFunction_Linking.          (* الربط *)

Record ExtraLetterProfile := {
  extra_letter    : ExtraLetter;
  extra_functions : list ExtraFunction
}.

(** ========== 4. Vowels and phonology skeleton ========== *)

Inductive Vowel :=
| Fatha        (* فتحة *)
| Damma        (* ضمة *)
| Kasra        (* كسرة *)
| Sukun        (* سكون *)
| Shadda       (* شدة *)
| TanweenFath  (* تنوين فتح *)
| TanweenDamm  (* تنوين ضم *)
| TanweenKasr. (* تنوين كسر *)

(* القيمة الرياضية للصوت (نصف صائت، صفر، تضخيم...) *)
(* الفتحة/الضمة/الكسرة = 0.5 من الألف/الواو/الياء، نمثلها بـ 1 كوحدة *)
Definition vowel_value (v : Vowel) : nat :=
  match v with
  | Fatha       => 1   (* نصف قيمة الألف *)
  | Damma       => 1   (* نصف قيمة الواو *)
  | Kasra       => 1   (* نصف قيمة الياء *)
  | Sukun       => 0   (* انعدام الصائت *)
  | Shadda      => 2   (* تضاعف قيمة موقع C *)
  | TanweenFath => 1
  | TanweenDamm => 1
  | TanweenKasr => 1
  end.

(* طبقة فونولوجية *)
Record PhonologyLayer := {
  ph_pattern    : list (option Vowel);  (* نمط الحركات *)
  ph_syllables  : nat                    (* عدد المقاطع *)
}.

(** ========== 5. Morphology Layer (الطبقة الصرفية) ========== *)

Inductive MorphType :=
| MT_Verb      (* فعل *)
| MT_Noun      (* اسم *)
| MT_Particle. (* حرف *)

Inductive VerbPattern :=
| VP_Thulathi_Mujarrad    (* ثلاثي مجرد: فَعَلَ *)
| VP_Thulathi_Mazeed      (* ثلاثي مزيد: أَفْعَلَ، فَعَّلَ، فَاعَلَ... *)
| VP_Rubai_Mujarrad       (* رباعي مجرد: فَعْلَلَ *)
| VP_Rubai_Mazeed.        (* رباعي مزيد: تَفَعْلَلَ *)

Inductive NounPattern :=
| NP_Masdar               (* مصدر *)
| NP_IsmFaail             (* اسم فاعل *)
| NP_IsmMafoul            (* اسم مفعول *)
| NP_Sifa                 (* صفة مشبهة *)
| NP_IsmTafdil            (* اسم تفضيل *)
| NP_IsmMakan             (* اسم مكان *)
| NP_IsmZaman             (* اسم زمان *)
| NP_IsmAla               (* اسم آلة *)
| NP_Jamid.               (* جامد *)

Record MorphologyLayer := {
  mo_type        : MorphType;
  mo_verb_pat    : option VerbPattern;
  mo_noun_pat    : option NounPattern;
  mo_pattern_id  : nat                  (* رقم الوزن / الصيغة *)
}.

(** ========== 6. Semantics Layer (الطبقة الدلالية) ========== *)

Inductive DenotationType :=
| Den_Event     (* حدث *)
| Den_Entity    (* ذات *)
| Den_State     (* حالة *)
| Den_Quality   (* صفة *)
| Den_Relation. (* علاقة *)

Record SemanticsLayer := {
  sem_denotation : DenotationType;
  sem_sense_id   : SenseID
}.

(** ========== 7. LexicalUnit - الوحدة المعجمية الكاملة ========== *)

Record LexicalUnit := {
  lu_id         : LexemeID;
  lu_root       : RootC2Layer;
  lu_extras     : list ExtraLetterProfile;
  lu_phonology  : PhonologyLayer;
  lu_morphology : MorphologyLayer;
  lu_semantics  : SemanticsLayer
}.

(** ========== 8. AGT Generation - التوليد حسب المبرهنة ========== *)

(* دالة توليد كلمة من جذر C2 *)
Definition AGT_generate_word (root : RootC2Layer) 
                             (extras : list ExtraLetterProfile)
                             (phon : PhonologyLayer)
                             (morph : MorphologyLayer)
                             (sem : SemanticsLayer) : LexicalUnit :=
  {| lu_id         := 0;  (* يمكن توليده لاحقاً *)
     lu_root       := root;
     lu_extras     := extras;
     lu_phonology  := phon;
     lu_morphology := morph;
     lu_semantics  := sem
  |}.

(* فحص: هل الكلمة مشتقة من جذر ثلاثي؟ *)
Definition is_triliteral (lu : LexicalUnit) : bool :=
  match lu.(lu_root).(r_class) with
  | RootTriliteral => true
  | _ => false
  end.

(* فحص: هل C2 في دور فاعلية؟ *)
Definition is_c2_agentive (lu : LexicalUnit) : bool :=
  match lu.(lu_root).(r_c2_role) with
  | C2_Agentive => true
  | _ => false
  end.

(** ========== 9. Sentence Level (مستوى الجملة) ========== *)

Inductive SentenceType :=
| ST_Nominal   (* جملة اسمية *)
| ST_Verbal.   (* جملة فعلية *)

Inductive IrabCase :=
| IC_Raf       (* رفع *)
| IC_Nasb      (* نصب *)
| IC_Jarr      (* جر *)
| IC_Jazm.     (* جزم *)

Record SentenceElement := {
  se_lexeme : LexicalUnit;
  se_irab   : IrabCase;
  se_role   : string        (* مبتدأ، خبر، فاعل، مفعول... *)
}.

Record Sentence := {
  sent_type     : SentenceType;
  sent_elements : list SentenceElement
}.

(** ========== 10. Muraqqab / Style (الأسلوب المركب) ========== *)

Inductive StyleCategory :=
| Style_Khabar      (* خبر: يحتمل الصدق والكذب *)
| Style_Istifham    (* استفهام *)
| Style_Amr         (* أمر *)
| Style_Nahy        (* نهي *)
| Style_Tamanni     (* تمني *)
| Style_Tarajji     (* ترجي *)
| Style_Qasam       (* قسم *)
| Style_Nida.       (* نداء *)

Definition is_truth_apt (s : StyleCategory) : bool :=
  match s with
  | Style_Khabar => true
  | _ => false
  end.

Record Muraqqab := {
  mur_sentence : Sentence;
  mur_style    : StyleCategory
}.

(** ========== 11. AGT Chain Lemma - سلسلة التوليد ========== *)

(* لمّا: كل مركب (Muraqqab) يُشتق من جملة، والجملة من كلمات، والكلمات من جذور C2 *)
Lemma AGT_chain : forall (m : Muraqqab),
  exists (s : Sentence) (elements : list SentenceElement),
    m.(mur_sentence) = s /\
    s.(sent_elements) = elements /\
    forall e, In e elements -> exists root, e.(se_lexeme).(lu_root) = root.
Proof.
  intros m.
  exists (mur_sentence m).
  exists (sent_elements (mur_sentence m)).
  split. reflexivity.
  split. reflexivity.
  intros e Hin.
  exists (lu_root (se_lexeme e)).
  reflexivity.
Qed.

End ArabicOntology.
