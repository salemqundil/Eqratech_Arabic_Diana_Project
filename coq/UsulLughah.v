(***********************************************************)
(*  Usul-based Language Ontology for Arabic in Coq          *)
(*  متناسق مع تصور: C2 → Lexeme → Sentence → Style         *)
(***********************************************************)

From Coq Require Import String List.
Import ListNotations.

Set Implicit Arguments.
Set Asymmetric Patterns.

Module UsulLughah.

(****************************************************)
(* 0. Primitive "Meaning" and "Referent"            *)
(****************************************************)

(* نُبقي المعنى مجرداً: يمكن لاحقاً ربطه بأنطولوجيا أعمق *)
Parameter Meaning : Type.
Parameter Referent : Type.  (* شيء في العالم الخارجي إن أردت لاحقاً *)

(****************************************************)
(* 1. Dalālah: مطابقة / تضمّن / التزام             *)
(****************************************************)

Inductive DalalahKind :=
| Dal_Mutabaqa   (* دلالة اللفظ على تمام ما وضع له *)
| Dal_Tadammum   (* دلالته على جزء المسمّى *)
| Dal_Iltizam.   (* دلالته على لازم المعنى (اللزوم الذهني) *)

(****************************************************)
(* 2. Expression granularity: مفرد / مركّب          *)
(****************************************************)

Inductive ExprKind :=
| EK_Simple    (* مفرد: لا يدل جزءه على جزء معناه *)
| EK_Compound. (* مركب: يدل جزءه على جزء المعنى *)

(****************************************************)
(* 3. Parts of Speech: اسم / فعل / حرف             *)
(****************************************************)

Inductive POS :=
| POS_Noun
| POS_Verb
| POS_Particle.

(****************************************************)
(* 4. Noun: كلي / جزئي – متواطئ / مشكِّك          *)
(****************************************************)

Inductive NounCardinality :=
| N_Kulli   (* يقبل الشركة في مفهومه *)
| N_Juzi.   (* لا يقبل الشركة – علم، ضمير... *)

Inductive KulliKind :=
| K_Mutawati   (* متواطئ: استواء الأفراد في المعنى *)
| K_Mushakkik. (* مشكِّك: تفاوت الأفراد بالأولوية/الشدة... *)

(* نوع الاسم من حيث كلي/جزئي ومتواطئ/مشكّك *)
Record NounProfile := {
  np_cardinality : NounCardinality;
  np_kulli_kind  : option KulliKind
}.

(****************************************************)
(* 5. Denoted object kind: المدلول                  *)
(*    (معنى / لفظ مفرد مستعمل / مهمل / مركب...)    *)
(****************************************************)

Inductive DenotedKind :=
| DK_Meaning                (* مدلول اللفظ معنى (شيء ذهني) *)
| DK_WordSimple_Used        (* لفظ مفرد مستعمل (كـ "كلمة") *)
| DK_WordSimple_Unused      (* لفظ مفرد مهمل (أسماء الحروف...) *)
| DK_WordCompound_Used      (* لفظ مركب مستعمل (خبر، جملة...) *)
| DK_WordCompound_Unused.   (* مركب مهمل – هذيان *)

(****************************************************)
(* 6. Lexical relation: منفرد / متباين / ترادف ... *)
(****************************************************)

Inductive LexemeRelationKind :=
| LRK_Infirad     (* المنفرد: لفظ واحد، معنى واحد *)
| LRK_Tabayun     (* المتباين: ألفاظ متعددة، معانٍ متباينة *)
| LRK_Taraduf     (* المترادف: ألفاظ متعددة، معنى واحد *)
| LRK_Ishtirak    (* المشترك: لفظ واحد، معانٍ متعددة، وضعاً أولاً *)
| LRK_Manqul      (* المنقول: وضع لمعنى ثم نقل لآخر واشتهر فيه *)
| LRK_Haqiqa      (* الحقيقة: استعمال اللفظ في ما وضع له أولاً *)
| LRK_Majaz.      (* المجاز: استعمال اللفظ في غير ما وضع له لعلاقة *)

(* أنواع الحقيقة تفصيلاً *)
Inductive HaqiqaKind :=
| HK_Lughawiyya    (* الحقيقة اللغوية *)
| HK_Shar_iyya     (* الحقيقة الشرعية *)
| HK_Urfiyya_Aamma (* الحقيقة العرفية العامة *)
| HK_Urfiyya_Khassa. (* الحقيقة العرفية الخاصة (اصطلاحات الفنون) *)

(****************************************************)
(* 7. Simple word representation                    *)
(****************************************************)

Record SimpleWord := {
  sw_form   : string;
  sw_pos    : POS;
  sw_noun   : option NounProfile;  (* متى كان اسماً *)
  sw_meanings : list Meaning       (* معاني ممكنة: كالمشترك أو المنقول *)
}.

(****************************************************)
(* 8. Compound expressions: "المركب" الستة          *)
(****************************************************)

(* أقسام المركب الستة كما في النص: *)
Inductive CompoundCategory :=
| CC_Istifham   (* الاستفهام: طلب الماهية *)
| CC_Amr        (* الأمر: طلب تحصيل الماهية مع استعلاء *)
| CC_Iltimas    (* الالتماس: طلب تحصيل الماهية مع التساوي *)
| CC_Su_al      (* السؤال/الدعاء: طلب تحصيل الماهية مع التذلل *)
| CC_Khabar     (* الخبر: يحتمل الصدق والكذب *)
| CC_Tanbih.    (* التنبيه: لا يحتمل الصدق والكذب – يشمل الترجي والتمني والقسم والنداء *)

(* تفريع للتنبيه كما في النص *)
Inductive TanbihSubtype :=
| TB_PureTanbih
| TB_Tarajji
| TB_Tamanni
| TB_Qasam
| TB_Nida
| TB_Other.

(* ملف الأسلوب للجملة المركّبة *)
Record CompoundForce := {
  cf_category    : CompoundCategory;
  cf_tanbih_sub  : option TanbihSubtype;
  cf_truth_apt   : bool;  (* هل يحتمل الصدق/الكذب؟ *)
}.

(* جملة مركّبة على مستوى اللغة فقط *)
Record CompoundExpr := {
  ce_words  : list SimpleWord;
  ce_force  : CompoundForce
}.

(****************************************************)
(* 9. Truth-aptness helper (خبر / غير خبر)         *)
(****************************************************)

Definition is_truth_apt (cf : CompoundForce) : bool :=
  match cf.(cf_category) with
  | CC_Khabar => true
  | _         => false
  end.

(****************************************************)
(* 10. Part-of-speech subtypes: علم / ضمير / حرف... *)
(****************************************************)

Inductive NounSubtype :=
| N_ProperName   (* علم: زيد، مكة *)
| N_Pronoun      (* ضمير: هو، هي *)
| N_CommonNoun   (* اسم جنس: إنسان، فرس *)
| N_Deictic      (* اسم إشارة: هذا، تلك *)
| N_Relative     (* اسم موصول: الذي، التي *)
| N_OtherNoun.

Inductive ParticleSubtype :=
| P_Jar          (* حروف الجر: من، إلى، في، على، عن... *)
| P_Nasb         (* حروف النصب: أن، لن، كي... *)
| P_Jazm         (* حروف الجزم: لم، لما... *)
| P_Atf          (* حروف العطف: و، ف، ثم، حتى، أو، أم، بل، لكن *)
| P_Nafi         (* حروف النفي: ما، لا، لم، لن، إن (المخففة)... *)
| P_Shart        (* حروف الشرط: إن، لو، إذا... *)
| P_Tanbih       (* حروف التنبيه: ها، ألا، أما... *)
| P_Nida         (* حروف النداء: يا، أيا، هيا، أي، وا *)
| P_Jawab        (* حروف الجواب: نعم، بلى، أجل، جير، إي، إنّ *)
| P_OtherParticle.

(* توسيع SimpleWord بمزيد من المعلومات النحوية إن أردت *)
Record SimpleWordAnnotated := {
  swa_core  : SimpleWord;
  swa_nsub  : option NounSubtype;
  swa_psub  : option ParticleSubtype
}.

(****************************************************)
(* 11. Haqiqa / Majaz profile of a usage           *)
(****************************************************)

Record UsageProfile := {
  up_haqiqa_kind : option HaqiqaKind;        (* لغوية/شرعية/عرفية... *)
  up_is_majaz    : bool;
  up_relation    : option LexemeRelationKind (* ترادف/اشتراك/منقول... *)
}.

(****************************************************)
(* 12. Link to higher-level sentence models         *)
(*     (AGT / Muraqqab) – "hooks" للتكامل لاحقاً    *)
(****************************************************)

(* نفترض لاحقاً أنك ستربط CompoundExpr بـ StructuredSentence
   من نموذج AGT (الذي بنيناه في وحدات أخرى) عن طريق دوال مثل: *)

Parameter SentenceModel : Type.
(* مثال: SentenceModel يمكن أن يكون ArabicMuraqqab.StructuredSentence *)

(* رسم خريطة من نموذج الجملة المنطقي إلى الأسلوب المركّب الستّي *)
Parameter sentence_to_compound_force :
  SentenceModel -> CompoundForce.

(* تأكيد أن الخبر في نموذج الجملة يطابق CC_Khabar هنا (يمكن برهنته لاحقاً) *)
Axiom sentence_truth_apt_compat :
  forall (s : SentenceModel),
    is_truth_apt (sentence_to_compound_force s) = true ->
    (* ... هنا يمكن أن تضع خاصية "جملة خبرية" في نموذجك العالي ... *)
    True.

End UsulLughah.
