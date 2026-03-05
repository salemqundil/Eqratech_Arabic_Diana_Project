(****************************************************)
(* AGT_Discourse.v                                   *)
(* تحليل الخطاب والنص - Discourse and Text Analysis  *)
(* Arabic Discourse Analysis Framework               *)
(****************************************************)

From Coq Require Import List String Nat.
Import ListNotations.

Set Implicit Arguments.
Set Asymmetric Patterns.

Module AGT_Discourse.

(****************************************************)
(* Part 1: بنية النص - Text Structure               *)
(****************************************************)

(* وحدات النص *)
Inductive TextUnit :=
| TU_Kalima          (* كلمة *)
| TU_Jumla           (* جملة *)
| TU_Fiqra           (* فقرة *)
| TU_Maqta3          (* مقطع *)
| TU_Fasl            (* فصل *)
| TU_Nass_Kamil      (* نص كامل *).

(* أنواع النصوص *)
Inductive TextType :=
(* النصوص السردية *)
| TT_Qissa           (* قصة *)
| TT_Riwaya          (* رواية *)
| TT_Sira            (* سيرة *)
| TT_Tarikh          (* تاريخ *)
(* النصوص الوصفية *)
| TT_Wasf            (* وصف *)
| TT_Taswir          (* تصوير *)
(* النصوص الحجاجية *)
| TT_Maqala          (* مقالة *)
| TT_Khutba          (* خطبة *)
| TT_Munazara        (* مناظرة *)
(* النصوص التفسيرية *)
| TT_Sharh           (* شرح *)
| TT_Tafsir          (* تفسير *)
| TT_Ta3liq          (* تعليق *)
(* النصوص الإرشادية *)
| TT_Dalil           (* دليل *)
| TT_Wasiyya         (* وصية *)
| TT_Qanun           (* قانون *)
(* النصوص التواصلية *)
| TT_Risala          (* رسالة *)
| TT_Hiwar           (* حوار *)
| TT_Murasala        (* مراسلة *).

(* أنماط الخطاب *)
Inductive DiscourseMode :=
| DM_Sard            (* سرد - Narration *)
| DM_Wasf            (* وصف - Description *)
| DM_Hujaj           (* حجاج - Argumentation *)
| DM_Tafsir          (* تفسير - Exposition *)
| DM_Irshad          (* إرشاد - Instruction *).

(****************************************************)
(* Part 2: الاتساق النصي - Text Cohesion           *)
(****************************************************)

(* أدوات الربط النحوية *)
Inductive GrammaticalCohesion :=
(* الإحالة *)
| GC_Ihala_Damiriyya     (* إحالة ضميرية *)
| GC_Ihala_Ishariyya     (* إحالة إشارية *)
| GC_Ihala_Mawsuliyya    (* إحالة موصولية *)
| GC_Ihala_Muqarana      (* إحالة مقارنة *)
(* الاستبدال *)
| GC_Istibdal_Ismi       (* استبدال اسمي *)
| GC_Istibdal_Fi3li      (* استبدال فعلي *)
| GC_Istibdal_Jumali     (* استبدال جملي *)
(* الحذف *)
| GC_Hadhf_Ismi          (* حذف اسمي *)
| GC_Hadhf_Fi3li         (* حذف فعلي *)
| GC_Hadhf_Jumali        (* حذف جملي *)
(* الوصل *)
| GC_Wasl_Idafi          (* وصل إضافي: و *)
| GC_Wasl_3aksi          (* وصل عكسي: لكن *)
| GC_Wasl_Sababi         (* وصل سببي: لأن *)
| GC_Wasl_Zamani         (* وصل زماني: ثم *).

(* اتجاه الإحالة *)
Inductive ReferenceDirection :=
| Ref_Qabliyya       (* إحالة قبلية - Anaphora *)
| Ref_Ba3diyya       (* إحالة بعدية - Cataphora *)
| Ref_Kharijiyya     (* إحالة خارجية - Exophora *).

(* الاتساق المعجمي *)
Inductive LexicalCohesion :=
| LC_Takrar          (* تكرار - Repetition *)
| LC_Taraduf         (* ترادف - Synonymy *)
| LC_Tadad           (* تضاد - Antonymy *)
| LC_Ishtirak        (* اشتراك - Collocation *)
| LC_Tatawuq         (* تطويق - Hyponymy *)
| LC_Juz_Kull        (* جزء-كل - Meronymy *).

Record CohesiveDevice := {
  cd_type : GrammaticalCohesion;
  cd_source : nat;  (* موقع المصدر *)
  cd_target : nat;  (* موقع الهدف *)
  cd_direction : ReferenceDirection
}.

(****************************************************)
(* Part 3: الانسجام النصي - Text Coherence          *)
(****************************************************)

(* العلاقات البلاغية - Rhetorical Relations (RST) *)
Inductive RhetoricalRelation :=
(* علاقات تقديمية - Presentational *)
| RR_Khalfiyya       (* خلفية - Background *)
| RR_Tamhid          (* تمهيد - Preparation *)
| RR_Taqdim          (* تقديم - Presentation *)
| RR_Da3wa           (* دعوة - Invitation *)
(* علاقات موضوعية - Subject matter *)
| RR_Sabab           (* سبب - Cause *)
| RR_Natija          (* نتيجة - Result *)
| RR_Gharad          (* غرض - Purpose *)
| RR_Shart           (* شرط - Condition *)
| RR_Tafasir         (* تفسير - Interpretation *)
| RR_Taqyim          (* تقييم - Evaluation *)
(* علاقات متعددة النوى - Multinuclear *)
| RR_Tawali          (* توالٍ - Sequence *)
| RR_Taqabil         (* تقابل - Contrast *)
| RR_Musa3ada        (* مساواة - Joint *)
(* علاقات إضافية *)
| RR_Ishhad          (* إشهاد - Evidence *)
| RR_Talkhis         (* تلخيص - Summary *)
| RR_I3ada_Siyagha   (* إعادة صياغة - Restatement *).

(* بنية RST *)
Record RSTNode := {
  rst_relation : RhetoricalRelation;
  rst_nucleus : nat;    (* النواة *)
  rst_satellite : option nat  (* التابع *)
}.

(****************************************************)
(* Part 4: البنية الكبرى - Macrostructure          *)
(****************************************************)

(* قواعد البنية الكبرى - Van Dijk *)
Inductive MacroRule :=
| MR_Hadhf           (* حذف - Deletion *)
| MR_Ta3mim          (* تعميم - Generalization *)
| MR_Bina            (* بناء - Construction *)
| MR_Tadmin          (* تضمين - Integration *).

(* مستويات البنية الكبرى *)
Inductive MacroLevel :=
| ML_Juz'i           (* مستوى جزئي *)
| ML_Wasit           (* مستوى وسيط *)
| ML_Kulli           (* مستوى كلي *)
| ML_Mawdu3          (* مستوى الموضوع *).

Record Macroproposition := {
  mp_level : MacroLevel;
  mp_content : nat;  (* محتوى القضية *)
  mp_rule : MacroRule  (* القاعدة المستخدمة *)
}.

(****************************************************)
(* Part 5: بنية المعلومات - Information Structure  *)
(****************************************************)

(* المعطى والجديد *)
Inductive InformationStatus :=
| IS_Mu3ta           (* معطى - Given *)
| IS_Jadid           (* جديد - New *)
| IS_Muftar          (* مفترض - Inferrable *)
| IS_Muhayya         (* مهيأ - Evoked *).

(* المبتدأ والخبر المعلوماتي *)
Inductive TopicComment :=
| TC_Mawdu3          (* موضوع - Topic *)
| TC_Ta3liq          (* تعليق - Comment *)
| TC_Bu'ra           (* بؤرة - Focus *)
| TC_Khalfiyya       (* خلفية - Background *).

(* التقديم والتأخير *)
Inductive WordOrder :=
| WO_SVO             (* فاعل-فعل-مفعول *)
| WO_VSO             (* فعل-فاعل-مفعول *)
| WO_OVS             (* مفعول-فعل-فاعل *)
| WO_Topicalized     (* مقدّم للتوكيد *)
| WO_Focused         (* مبأّر *).

Record InformationStructure := {
  info_status : InformationStatus;
  info_tc : TopicComment;
  info_order : WordOrder
}.

(****************************************************)
(* Part 6: تحليل المحادثة - Conversation Analysis   *)
(****************************************************)

(* الأدوار الحوارية *)
Inductive ConversationalTurn :=
| CT_Fatih           (* فاتح - Initiator *)
| CT_Mujib           (* مجيب - Responder *)
| CT_Mu3aqqib        (* معقّب - Follow-up *)
| CT_Khatim          (* خاتم - Closer *).

(* أزواج الجوار - Adjacency Pairs *)
Inductive AdjacencyPair :=
| AP_Su'al_Jawab     (* سؤال-جواب *)
| AP_Tahiyya_Radd    (* تحية-رد *)
| AP_Da3wa_Qubul     (* دعوة-قبول/رفض *)
| AP_Talab_Istijaba  (* طلب-استجابة *)
| AP_3ard_Muwafaqa   (* عرض-موافقة *)
| AP_Ittiham_Difa3   (* اتهام-دفاع *).

(* إدارة الدور *)
Inductive TurnManagement :=
| TM_Ikhtiyar_Tali   (* اختيار المتكلم التالي *)
| TM_Ikhtiyar_Dhati  (* الاختيار الذاتي *)
| TM_Muqata3a        (* مقاطعة *)
| TM_Tarahul         (* تراحل - Overlapping *).

(* التصحيح *)
Inductive RepairType :=
| Rep_Dhati          (* تصحيح ذاتي *)
| Rep_Akhir          (* تصحيح من الآخر *)
| Rep_Mubadir        (* مبادرة تصحيح *)
| Rep_Natija         (* نتيجة تصحيح *).

(****************************************************)
(* Part 7: تحليل الخطاب النقدي - Critical Discourse Analysis *)
(****************************************************)

(* الإيديولوجيا في الخطاب *)
Inductive IdeologicalElement :=
| IE_Sulta           (* سلطة - Power *)
| IE_Haymana         (* هيمنة - Hegemony *)
| IE_Muqawama        (* مقاومة - Resistance *)
| IE_Tabrir          (* تبرير - Legitimation *)
| IE_Tahmish         (* تهميش - Marginalization *)
| IE_Tamthil         (* تمثيل - Representation *).

(* استراتيجيات الخطاب *)
Inductive DiscourseStrategy :=
| DS_Tadmin          (* تضمين *)
| DS_Istib3ad        (* استبعاد *)
| DS_Takhfif         (* تخفيف *)
| DS_Tashkik         (* تشكيك *)
| DS_Tab3id          (* تبعيد *)
| DS_Taqrib          (* تقريب *).

(* أدوات التحكم الخطابي *)
Inductive DiscourseControl :=
| DC_Ikhtiyar_Mawdu3 (* اختيار الموضوع *)
| DC_Tadwir_Kalam    (* تدوير الكلام *)
| DC_Tahwil_Mawdu3   (* تحويل الموضوع *)
| DC_Muqata3a        (* المقاطعة *)
| DC_Ta3miq          (* التعميق *).

(****************************************************)
(* Part 8: الإحالة والمرجعية - Reference           *)
(****************************************************)

(* أنواع المراجع *)
Inductive ReferentType :=
| RT_Shakhsi         (* شخصي - Personal *)
| RT_Makani          (* مكاني - Spatial *)
| RT_Zamani          (* زماني - Temporal *)
| RT_Khitabi         (* خطابي - Discourse *)
| RT_3aqli           (* عقلي - Cognitive *).

(* حالة المرجع *)
Inductive ReferentStatus :=
| RS_Mu3arraf        (* معرّف - Definite *)
| RS_Nakira          (* نكرة - Indefinite *)
| RS_Muhaddad        (* محدد - Specific *)
| RS_3aam            (* عام - Generic *).

(* سلسلة الإحالة *)
Record ReferenceChain := {
  rc_referent : nat;
  rc_mentions : list nat;  (* مواقع الذكر *)
  rc_type : ReferentType;
  rc_status : ReferentStatus
}.

(****************************************************)
(* Part 9: بنية السرد - Narrative Structure        *)
(****************************************************)

(* عناصر السرد - Labov *)
Inductive NarrativeElement :=
| NE_Tajrid          (* تجريد - Abstract *)
| NE_Tawjih          (* توجيه - Orientation *)
| NE_Hadath_Mu3aqqid (* حدث معقد - Complicating action *)
| NE_Taqyim          (* تقييم - Evaluation *)
| NE_Natija          (* نتيجة - Resolution *)
| NE_Khatima         (* خاتمة - Coda *).

(* وجهة النظر *)
Inductive PointOfView :=
| POV_Mutakallim_Awwal    (* متكلم أول *)
| POV_Mutakallim_3alim    (* متكلم عليم *)
| POV_Mutakallim_Mahdud   (* متكلم محدود *)
| POV_Gha'ib_3alim        (* غائب عليم *)
| POV_Gha'ib_Mahdud       (* غائب محدود *).

(* الزمن السردي *)
Inductive NarrativeTime :=
| NT_Tawali_Zamani   (* توالٍ زماني *)
| NT_Istiraj3        (* استرجاع - Flashback *)
| NT_Istibaq         (* استباق - Flash-forward *)
| NT_Tawqquf         (* توقف - Pause *)
| NT_Takhlis         (* تخليص - Summary *).

(****************************************************)
(* Part 10: بنية الحجاج - Argumentation Structure  *)
(****************************************************)

(* عناصر الحجاج - Toulmin *)
Inductive ArgumentElement :=
| AE_Da3wa           (* دعوى - Claim *)
| AE_Ma3tiyat        (* معطيات - Data *)
| AE_Sanad           (* سند - Warrant *)
| AE_Da3m            (* دعم - Backing *)
| AE_Tahfiz          (* تحفيز - Qualifier *)
| AE_Istithna        (* استثناء - Rebuttal *).

(* أنواع الحجج *)
Inductive ArgumentType :=
| AT_Istiqra         (* استقراء - Induction *)
| AT_Istintaj        (* استنتاج - Deduction *)
| AT_Tamthil         (* تمثيل - Analogy *)
| AT_Sulta           (* سلطة - Authority *)
| AT_Ijma3           (* إجماع - Consensus *)
| AT_Qiyas           (* قياس - Syllogism *).

(* المغالطات *)
Inductive Fallacy :=
| Fal_Muhajamat_Shakhsiyya  (* مهاجمة شخصية - Ad hominem *)
| Fal_Isti'naf_3awatif      (* استئناف عواطف - Appeal to emotion *)
| Fal_Isti'naf_Sulta        (* استئناف سلطة - Appeal to authority *)
| Fal_Ta3mim_Mutasarri3     (* تعميم متسرع - Hasty generalization *)
| Fal_Munhader_Zaliq        (* منحدر زلق - Slippery slope *)
| Fal_Rajul_Qishsh          (* رجل قش - Straw man *)
| Fal_Dawra_Mantiqiyya      (* دورة منطقية - Circular reasoning *).

(****************************************************)
(* Part 11: دوال التحليل الخطابي                    *)
(****************************************************)

(* إنشاء أداة اتساق *)
Definition create_cohesive_device (t : GrammaticalCohesion) (src tgt : nat) (dir : ReferenceDirection) : CohesiveDevice :=
  {| cd_type := t; cd_source := src; cd_target := tgt; cd_direction := dir |}.

(* إنشاء عقدة RST *)
Definition create_rst_node (rel : RhetoricalRelation) (nuc : nat) (sat : option nat) : RSTNode :=
  {| rst_relation := rel; rst_nucleus := nuc; rst_satellite := sat |}.

(* إنشاء قضية كبرى *)
Definition create_macroprop (lvl : MacroLevel) (content : nat) (rule : MacroRule) : Macroproposition :=
  {| mp_level := lvl; mp_content := content; mp_rule := rule |}.

(* إنشاء سلسلة إحالة *)
Definition create_ref_chain (ref : nat) (ments : list nat) (t : ReferentType) (s : ReferentStatus) : ReferenceChain :=
  {| rc_referent := ref; rc_mentions := ments; rc_type := t; rc_status := s |}.

(* فحص اتجاه الإحالة *)
Definition is_anaphoric (cd : CohesiveDevice) : bool :=
  match cd.(cd_direction) with
  | Ref_Qabliyya => true
  | _ => false
  end.

(* فحص كون العلاقة متعددة النوى *)
Definition is_multinuclear (rel : RhetoricalRelation) : bool :=
  match rel with
  | RR_Tawali | RR_Taqabil | RR_Musa3ada => true
  | _ => false
  end.

(****************************************************)
(* Part 12: لمّات التحقق الخطابي                    *)
(****************************************************)

(* كل أداة اتساق لها مصدر وهدف *)
Lemma cohesive_device_has_source_target :
  forall t s tg d,
  (create_cohesive_device t s tg d).(cd_source) = s /\
  (create_cohesive_device t s tg d).(cd_target) = tg.
Proof.
  intros. split; reflexivity.
Qed.

(* العلاقات متعددة النوى محددة بشكل صحيح *)
Lemma tawali_is_multinuclear :
  is_multinuclear RR_Tawali = true.
Proof.
  reflexivity.
Qed.

Lemma sabab_is_not_multinuclear :
  is_multinuclear RR_Sabab = false.
Proof.
  reflexivity.
Qed.

(* الإحالة القبلية قبلية *)
Lemma anaphora_is_anaphoric :
  forall t s tg,
  is_anaphoric (create_cohesive_device t s tg Ref_Qabliyya) = true.
Proof.
  intros. reflexivity.
Qed.

(* كل قضية كبرى لها مستوى *)
Lemma macroprop_has_level :
  forall l c r,
  (create_macroprop l c r).(mp_level) = l.
Proof.
  intros. reflexivity.
Qed.

(****************************************************)
(* Part 13: أمثلة تطبيقية                            *)
(****************************************************)

(* مثال: إحالة ضميرية *)
Definition example_pronominal_ref :=
  create_cohesive_device GC_Ihala_Damiriyya 5 2 Ref_Qabliyya.

(* مثال: عقدة RST - سبب *)
Definition example_rst_cause :=
  create_rst_node RR_Sabab 1 (Some 2).

(* مثال: عقدة RST - تتالي *)
Definition example_rst_sequence :=
  create_rst_node RR_Tawali 1 None.

(* مثال: قضية كبرى - تلخيص *)
Definition example_summary :=
  create_macroprop ML_Kulli 100 MR_Hadhf.

(* مثال: سلسلة إحالة لشخصية في قصة *)
Definition example_character_chain :=
  create_ref_chain 1 [2; 5; 8; 12; 15] RT_Shakhsi RS_Mu3arraf.

(* التحقق من الأمثلة *)
Lemma example_ref_is_anaphoric :
  is_anaphoric example_pronominal_ref = true.
Proof.
  reflexivity.
Qed.

Lemma example_sequence_is_multinuclear :
  is_multinuclear (example_rst_sequence.(rst_relation)) = true.
Proof.
  reflexivity.
Qed.

Lemma example_cause_is_not_multinuclear :
  is_multinuclear (example_rst_cause.(rst_relation)) = false.
Proof.
  reflexivity.
Qed.

(****************************************************)
(* Part 14: سلسلة التحليل الخطابي الكامل            *)
(****************************************************)

(* 
سلسلة التحليل:
نص → وحدات → اتساق → انسجام → بنية كبرى → موضوع

Text → Units → Cohesion → Coherence → Macrostructure → Theme
*)

Record DiscourseAnalysis := {
  da_text_type : TextType;
  da_mode : DiscourseMode;
  da_cohesion : list CohesiveDevice;
  da_rst : list RSTNode;
  da_macro : list Macroproposition
}.

Definition create_discourse_analysis 
  (tt : TextType) 
  (dm : DiscourseMode) 
  (coh : list CohesiveDevice)
  (rst : list RSTNode)
  (mac : list Macroproposition) : DiscourseAnalysis :=
  {| da_text_type := tt;
     da_mode := dm;
     da_cohesion := coh;
     da_rst := rst;
     da_macro := mac |}.

(* مثال تحليل خطابي كامل *)
Definition example_full_analysis :=
  create_discourse_analysis 
    TT_Maqala 
    DM_Hujaj
    [example_pronominal_ref]
    [example_rst_cause; example_rst_sequence]
    [example_summary].

Lemma example_analysis_is_argumentative :
  (example_full_analysis).(da_mode) = DM_Hujaj.
Proof.
  reflexivity.
Qed.

End AGT_Discourse.
