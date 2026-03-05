(****************************************************)
(* AGT_Semantics.v                                   *)
(* علم الدلالة العربية - Arabic Semantics            *)
(* Deep Semantic Analysis for Arabic Language        *)
(****************************************************)

From Coq Require Import List String.
Import ListNotations.

Set Implicit Arguments.
Set Asymmetric Patterns.

Module AGT_Semantics.

(****************************************************)
(* Part 1: أنواع المعاني - Types of Meaning          *)
(****************************************************)

(* المعنى المعجمي - Lexical Meaning *)
Inductive LexicalMeaningType :=
| LM_Haqiqi         (* حقيقي - Literal *)
| LM_Majazi         (* مجازي - Figurative *)
| LM_Munasaba       (* مناسبة - Contextual *)
| LM_Dalali         (* دلالي صرف - Pure semantic *).

(* المعنى النحوي - Grammatical Meaning *)
Inductive GrammaticalMeaningType :=
| GM_I3rabi         (* إعرابي - Case-related *)
| GM_Tarkibi        (* تركيبي - Structural *)
| GM_Wazifi         (* وظيفي - Functional *)
| GM_Siyaqi         (* سياقي - Contextual *).

(* المعنى الصرفي - Morphological Meaning *)
Inductive MorphMeaningType :=
| MM_Sighah         (* صيغة - Pattern meaning *)
| MM_Wazn           (* وزن - Weight meaning *)
| MM_Ziyadah        (* زيادة - Addition meaning *)
| MM_Tajrid         (* تجريد - Abstraction meaning *).

(* المعنى السياقي - Contextual Meaning *)
Inductive ContextMeaningType :=
| CM_Maqali         (* مقالي - Textual context *)
| CM_Maqami         (* مقامي - Situational context *)
| CM_Thaqafi        (* ثقافي - Cultural context *)
| CM_Tarikhi        (* تاريخي - Historical context *).

(****************************************************)
(* Part 2: العلاقات الدلالية - Semantic Relations    *)
(****************************************************)

(* الترادف - Synonymy *)
Inductive SynonymyType :=
| Syn_Tam           (* ترادف تام - Complete synonymy *)
| Syn_Qaribi        (* ترادف قريب - Near synonymy *)
| Syn_Siyaqi        (* ترادف سياقي - Contextual synonymy *)
| Syn_Uslubi        (* ترادف أسلوبي - Stylistic synonymy *).

(* التضاد - Antonymy *)
Inductive AntonymyType :=
| Ant_Hadd          (* تضاد حاد - Sharp antonymy: حي/ميت *)
| Ant_Tadarruji     (* تضاد تدرّجي - Gradable: كبير/صغير *)
| Ant_Ta3akusi      (* تضاد عكسي - Converse: باع/اشترى *)
| Ant_Ittijihi      (* تضاد اتجاهي - Directional: فوق/تحت *)
| Ant_Tadayuni      (* تضاد تدايني - Relational: أب/ابن *).

(* الاشتراك اللفظي - Homonymy *)
Inductive HomonymyType :=
| Hom_Taam          (* اشتراك تام - Full homonymy *)
| Hom_Tarikhi       (* اشتراك تاريخي - Historical *)
| Hom_Siyaqi        (* اشتراك سياقي - Contextual *).

(* المشترك الدلالي - Polysemy *)
Inductive PolysemyType :=
| Poly_Asli         (* تعدد أصلي - Original polysemy *)
| Poly_Iktisabi     (* تعدد مكتسب - Acquired polysemy *)
| Poly_Majazi       (* تعدد مجازي - Metaphorical polysemy *).

(* العلاقات الهرمية - Hierarchical Relations *)
Inductive HierarchyType :=
| Hier_Ism_Jins     (* اسم الجنس - Hypernymy: حيوان *)
| Hier_Naw3         (* نوع - Hyponymy: أسد *)
| Hier_Juz          (* جزء - Meronymy: يد *)
| Hier_Kull         (* كل - Holonymy: جسم *).

(* علاقات التضمن - Entailment *)
Inductive EntailmentType :=
| Ent_Lazim         (* لازم - Necessary entailment *)
| Ent_Iqtida        (* اقتضاء - Presupposition *)
| Ent_Tadmin        (* تضمين - Implicature *).

(****************************************************)
(* Part 3: الحقول الدلالية - Semantic Fields        *)
(****************************************************)

(* أنواع الحقول الدلالية *)
Inductive SemanticFieldType :=
| SF_Hayawan        (* حقل الحيوان *)
| SF_Nabat          (* حقل النبات *)
| SF_Insan          (* حقل الإنسان *)
| SF_Tabi3a         (* حقل الطبيعة *)
| SF_Jism           (* حقل الجسم *)
| SF_Nafs           (* حقل النفس *)
| SF_I3tiqad        (* حقل الاعتقاد *)
| SF_Haraka         (* حقل الحركة *)
| SF_Hiss           (* حقل الحس *)
| SF_Zaman          (* حقل الزمان *)
| SF_Makan          (* حقل المكان *)
| SF_Alwan          (* حقل الألوان *)
| SF_A3dad          (* حقل الأعداد *)
| SF_Qarabah        (* حقل القرابة *)
| SF_Akhlaq         (* حقل الأخلاق *)
| SF_3Ibadat        (* حقل العبادات *)
| SF_Mu3amalat      (* حقل المعاملات *).

Record SemanticField := {
  sf_type : SemanticFieldType;
  sf_core : list nat;  (* المفردات المحورية *)
  sf_peripheral : list nat  (* المفردات الطرفية *)
}.

(****************************************************)
(* Part 4: التحليل السيمي - Componential Analysis   *)
(****************************************************)

(* السمات الدلالية - Semantic Features *)
Inductive SemanticFeature :=
(* سمات الإنسان *)
| Feat_Human        (* [+إنسان] *)
| Feat_NonHuman     (* [-إنسان] *)
| Feat_Male         (* [+ذكر] *)
| Feat_Female       (* [+أنثى] *)
| Feat_Adult        (* [+بالغ] *)
| Feat_Child        (* [+صغير] *)
(* سمات الكائنات *)
| Feat_Animate      (* [+حي] *)
| Feat_Inanimate    (* [-حي] *)
| Feat_Concrete     (* [+مادي] *)
| Feat_Abstract     (* [-مادي] *)
(* سمات الأفعال *)
| Feat_Dynamic      (* [+حركي] *)
| Feat_Stative      (* [-حركي] *)
| Feat_Durative     (* [+مستمر] *)
| Feat_Punctual     (* [-مستمر] *)
| Feat_Telic        (* [+غائي] *)
| Feat_Atelic       (* [-غائي] *)
(* سمات إضافية *)
| Feat_Countable    (* [+معدود] *)
| Feat_Uncountable  (* [-معدود] *)
| Feat_Bounded      (* [+محدود] *)
| Feat_Unbounded    (* [-محدود] *).

Record ComponentialAnalysis := {
  ca_lexeme : nat;
  ca_features : list SemanticFeature
}.

(* دالة التحقق من توافق السمات *)
Definition features_compatible (f1 f2 : SemanticFeature) : bool :=
  match f1, f2 with
  | Feat_Human, Feat_NonHuman => false
  | Feat_Male, Feat_Female => false
  | Feat_Animate, Feat_Inanimate => false
  | Feat_Concrete, Feat_Abstract => false
  | Feat_Dynamic, Feat_Stative => false
  | _, _ => true
  end.

(****************************************************)
(* Part 5: نظرية الأفعال الكلامية - Speech Act Theory *)
(****************************************************)

(* أنواع الأفعال الكلامية *)
Inductive SpeechActType :=
(* الإخباريات - Assertives *)
| SA_Ikhbar         (* إخبار *)
| SA_Taqrir         (* تقرير *)
| SA_Wasf           (* وصف *)
| SA_Tanbbu         (* تنبؤ *)
(* التوجيهيات - Directives *)
| SA_Amr            (* أمر *)
| SA_Nahy           (* نهي *)
| SA_Talab          (* طلب *)
| SA_Iltimas        (* التماس *)
| SA_Nush           (* نصح *)
| SA_Tahdhir        (* تحذير *)
(* الالتزاميات - Commissives *)
| SA_Wa3d           (* وعد *)
| SA_Wa3id          (* وعيد *)
| SA_3ahd           (* عهد *)
| SA_Qasam          (* قسم *)
(* التعبيريات - Expressives *)
| SA_Shukr          (* شكر *)
| SA_I3tidhar       (* اعتذار *)
| SA_Tahni'a        (* تهنئة *)
| SA_Ta3ziya        (* تعزية *)
| SA_Madh           (* مدح *)
| SA_Dhamm          (* ذم *)
(* الإعلانيات - Declaratives *)
| SA_Talaq          (* طلاق *)
| SA_Zawaj          (* زواج *)
| SA_3itq           (* عتق *)
| SA_Ta3yin         (* تعيين *).

(* شروط الملاءمة - Felicity Conditions *)
Inductive FelicityCondition :=
| FC_Qudra          (* شرط القدرة *)
| FC_Ikhlas         (* شرط الإخلاص *)
| FC_Wudu3          (* شرط الوضوح *)
| FC_Munasaba       (* شرط المناسبة *).

Record SpeechAct := {
  sa_type : SpeechActType;
  sa_illocutionary_force : nat;  (* القوة الإنجازية *)
  sa_conditions : list FelicityCondition
}.

(****************************************************)
(* Part 6: الاستلزام الحواري - Conversational Implicature *)
(****************************************************)

(* مبادئ جرايس - Grice's Maxims *)
Inductive GriceMaxim :=
| Max_Kam            (* مبدأ الكم - Quantity *)
| Max_Kayf           (* مبدأ الكيف - Quality *)
| Max_3alaqa         (* مبدأ العلاقة - Relation *)
| Max_Uslub          (* مبدأ الأسلوب - Manner *).

(* أنواع الاستلزام *)
Inductive ImplicatureType :=
| Imp_3aam           (* استلزام عام *)
| Imp_Khass          (* استلزام خاص *)
| Imp_Qiyasi         (* استلزام قياسي *)
| Imp_3urfi          (* استلزام عرفي *).

(* انتهاك المبادئ *)
Inductive MaximViolation :=
| Viol_Khirq         (* خرق - Violation *)
| Viol_Ikhtiyar      (* اختيار - Opting out *)
| Viol_Sadm          (* صدم - Clash *)
| Viol_Istithmnar    (* استثمار - Flouting *).

(****************************************************)
(* Part 7: الافتراض المسبق - Presupposition        *)
(****************************************************)

(* أنواع الافتراض المسبق *)
Inductive PresuppositionType :=
| Pre_Wujudi         (* وجودي - Existential: أخوك يعمل → لك أخ *)
| Pre_Wasfiyy        (* وصفي - Factive: ندم على فعله → فعله *)
| Pre_Lughawi        (* لغوي - Lexical: توقف عن التدخين → كان يدخن *)
| Pre_Bunwi          (* بنوي - Structural: متى سافرت؟ → سافرت *)
| Pre_Muqarran       (* مقرّن - Counter-factual: لو جاء لأكرمته → لم يأت *).

(* محفزات الافتراض - Presupposition Triggers *)
Inductive PresuppositionTrigger :=
| Trig_Ta3rif        (* التعريف: الرجل، أخوك *)
| Trig_Wajhiyya      (* الوجهية: يعلم، يندم *)
| Trig_Taghyir_Hala  (* تغيير الحالة: بدأ، توقف *)
| Trig_Takrar        (* التكرار: مرة أخرى، أيضاً *)
| Trig_Shart_Khalfi  (* الشرط الخلفي: لو *).

(****************************************************)
(* Part 8: الإشاريات - Deixis                        *)
(****************************************************)

(* أنواع الإشاريات *)
Inductive DeixisType :=
(* الإشارة الشخصية *)
| Deix_Mutakallim    (* المتكلم: أنا، نحن *)
| Deix_Mukhatab      (* المخاطب: أنت، أنتم *)
| Deix_Gha'ib        (* الغائب: هو، هم *)
(* الإشارة المكانية *)
| Deix_Qarib_Makan   (* قريب: هنا، هذا *)
| Deix_Ba3id_Makan   (* بعيد: هناك، ذلك *)
(* الإشارة الزمانية *)
| Deix_Hadir         (* الحاضر: الآن، اليوم *)
| Deix_Madi          (* الماضي: أمس، قبل *)
| Deix_Mustaqbal     (* المستقبل: غداً، بعد *)
(* الإشارة الاجتماعية *)
| Deix_Ta3zim        (* التعظيم: حضرتك، سيادتك *)
| Deix_Tawaddu3      (* التواضع: العبد، خادمكم *)
(* الإشارة الخطابية *)
| Deix_Sabiqa        (* سابقة: ما ذكر، السابق *)
| Deix_Lahiqa        (* لاحقة: ما سيأتي، التالي *).

Record DeixisMarker := {
  dm_type : DeixisType;
  dm_reference_point : nat  (* نقطة المرجع *)
}.

(****************************************************)
(* Part 9: الحقيقة والمجاز المتقدم - Advanced Figurative Language *)
(****************************************************)

(* أنواع الاستعارة المتقدمة *)
Inductive AdvancedMetaphorType :=
| AM_Binyawiyya      (* استعارة بنيوية - Structural *)
| AM_Ittijahiyya     (* استعارة اتجاهية - Orientational *)
| AM_Wujudiyya       (* استعارة وجودية - Ontological *)
| AM_Ihya'iyya       (* استعارة إحيائية - Personification *)
| AM_Tajsidiyya      (* استعارة تجسيدية - Reification *).

(* نظرية الإطار الدلالي - Frame Semantics *)
Inductive SemanticFrame :=
| Frame_Haraka       (* إطار الحركة *)
| Frame_Idrak        (* إطار الإدراك *)
| Frame_Tabdul       (* إطار التبادل *)
| Frame_Ittisal      (* إطار الاتصال *)
| Frame_Taghyir      (* إطار التغيير *)
| Frame_Sabab        (* إطار السببية *).

Record FrameElement := {
  fe_frame : SemanticFrame;
  fe_role : nat;  (* الدور في الإطار *)
  fe_filler : nat (* المالئ *)
}.

(****************************************************)
(* Part 10: التغيّر الدلالي - Semantic Change        *)
(****************************************************)

(* أنواع التغيّر الدلالي *)
Inductive SemanticChangeType :=
(* التوسع والتضييق *)
| SC_Tawsi3          (* توسع - Broadening: سيارة من عربة إلى آلة *)
| SC_Tadyiq          (* تضييق - Narrowing: دابة من كل حيوان إلى ذوات الحوافر *)
(* الانتقال *)
| SC_Intiqal_Majazi  (* انتقال مجازي - Metaphorical transfer *)
| SC_Intiqal_Kinai   (* انتقال كنائي - Metonymic transfer *)
(* التحسن والتدهور *)
| SC_Tahsin          (* تحسن - Amelioration: وزير من خادم إلى منصب *)
| SC_Tadahwur        (* تدهور - Pejoration: ماكر من حاذق إلى مخادع *)
(* الضعف والتقوية *)
| SC_Da3f            (* ضعف - Weakening *)
| SC_Taqwiya         (* تقوية - Strengthening *).

(****************************************************)
(* Part 11: دوال التحليل الدلالي                     *)
(****************************************************)

(* توليد التحليل السيمي *)
Definition generate_componential_analysis (lex : nat) (feats : list SemanticFeature) : ComponentialAnalysis :=
  {| ca_lexeme := lex; ca_features := feats |}.

(* فحص التوافق الدلالي *)
Fixpoint check_semantic_compatibility (feats : list SemanticFeature) : bool :=
  match feats with
  | [] => true
  | f :: rest => 
      if forallb (features_compatible f) rest 
      then check_semantic_compatibility rest 
      else false
  end.

(* توليد الفعل الكلامي *)
Definition generate_speech_act (t : SpeechActType) (force : nat) (conds : list FelicityCondition) : SpeechAct :=
  {| sa_type := t; sa_illocutionary_force := force; sa_conditions := conds |}.

(* فحص شروط الملاءمة *)
Definition check_felicity (sa : SpeechAct) : bool :=
  match sa.(sa_conditions) with
  | [] => false  (* يجب أن توجد شروط *)
  | _ => true
  end.

(****************************************************)
(* Part 12: لمّات التحقق الدلالي                     *)
(****************************************************)

(* كل لفظ له سمات دلالية *)
Lemma every_lexeme_has_features : 
  forall lex feats, 
  (generate_componential_analysis lex feats).(ca_lexeme) = lex.
Proof.
  intros. simpl. reflexivity.
Qed.

(* السمات المتناقضة لا تتوافق *)
Lemma contradictory_features_incompatible :
  features_compatible Feat_Human Feat_NonHuman = false.
Proof.
  simpl. reflexivity.
Qed.

(* كل فعل كلامي له نوع *)
Lemma speech_act_has_type :
  forall t f c,
  (generate_speech_act t f c).(sa_type) = t.
Proof.
  intros. simpl. reflexivity.
Qed.

(* الفعل الكلامي بدون شروط غير ملائم *)
Lemma empty_conditions_not_felicitous :
  forall t f,
  check_felicity (generate_speech_act t f []) = false.
Proof.
  intros. simpl. reflexivity.
Qed.

(****************************************************)
(* Part 13: أمثلة تطبيقية                            *)
(****************************************************)

(* مثال: تحليل "رجل" *)
Definition example_rajul_analysis := 
  generate_componential_analysis 1 
    [Feat_Human; Feat_Male; Feat_Adult; Feat_Animate; Feat_Concrete].

(* مثال: تحليل "طفل" *)
Definition example_tifl_analysis :=
  generate_componential_analysis 2
    [Feat_Human; Feat_Child; Feat_Animate; Feat_Concrete].

(* مثال: فعل كلامي - وعد *)
Definition example_wa3d :=
  generate_speech_act SA_Wa3d 10 [FC_Qudra; FC_Ikhlas].

(* مثال: فعل كلامي - أمر *)
Definition example_amr :=
  generate_speech_act SA_Amr 8 [FC_Qudra; FC_Munasaba].

(* التحقق من صحة الأمثلة *)
Lemma example_rajul_is_human :
  In Feat_Human (example_rajul_analysis.(ca_features)).
Proof.
  simpl. left. reflexivity.
Qed.

Lemma example_wa3d_is_felicitous :
  check_felicity example_wa3d = true.
Proof.
  simpl. reflexivity.
Qed.

End AGT_Semantics.
