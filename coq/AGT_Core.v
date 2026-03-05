(** AGT_Core.v - Arabic Generative Theorem Core Implementation **)
(** المبرهنة العربية المولِّدة - النواة الأساسية **)

From Coq Require Import String List Nat Arith Bool.
Import ListNotations.

Set Implicit Arguments.
Set Asymmetric Patterns.

Module AGT_Core.

(************************************************************)
(* 1. الأساس الرياضي: Arabic Generative Theorem (AGT)        *)
(*    M = f(C1, C2, C3, C4, V1, V2, V3, Extra)              *)
(************************************************************)

(** ========== 1.1 الصوامت الجذرية (Root Consonants) ========== *)

(* تمثيل الحرف العربي - 29 حرفاً *)
Inductive ArabicLetter :=
| L_Hamza    (* ء *)
| L_Alif     (* ا *)
| L_Ba       (* ب *)
| L_Ta       (* ت *)
| L_Tha      (* ث *)
| L_Jim      (* ج *)
| L_Ha       (* ح *)
| L_Kha      (* خ *)
| L_Dal      (* د *)
| L_Dhal     (* ذ *)
| L_Ra       (* ر *)
| L_Zay      (* ز *)
| L_Sin      (* س *)
| L_Shin     (* ش *)
| L_Sad      (* ص *)
| L_Dad      (* ض *)
| L_Tah      (* ط *)
| L_Dhah     (* ظ *)
| L_Ayn      (* ع *)
| L_Ghayn    (* غ *)
| L_Fa       (* ف *)
| L_Qaf      (* ق *)
| L_Kaf      (* ك *)
| L_Lam      (* ل *)
| L_Mim      (* م *)
| L_Nun      (* ن *)
| L_Ha2      (* ه *)
| L_Waw      (* و *)
| L_Ya.      (* ي *)

(* الصامت الجذري - موقع في الجذر *)
Record RootConsonant := {
  rc_letter : ArabicLetter;
  rc_pos    : nat  (* 1=C1, 2=C2, 3=C3, 4=C4 *)
}.

(** ========== 1.2 الحركات (Vowels) ========== *)

Inductive Haraka :=
| H_Fatha       (* فتحة *)
| H_Damma       (* ضمة *)
| H_Kasra       (* كسرة *)
| H_Sukun       (* سكون *)
| H_Shadda      (* شدة *)
| H_FathaLong   (* ألف مد = فتحة + ألف *)
| H_DammaLong   (* واو مد = ضمة + واو *)
| H_KasraLong   (* ياء مد = كسرة + ياء *)
| H_TanweenFath (* تنوين فتح *)
| H_TanweenDamm (* تنوين ضم *)
| H_TanweenKasr. (* تنوين كسر *)

(* القيمة الرياضية للحركة *)
(* الفتحة = 0.5 ألف، الضمة = 0.5 واو، الكسرة = 0.5 ياء *)
(* نستخدم nat لتمثيل القيم: 1 = نصف، 2 = كاملة، 0 = صفر *)
Definition haraka_value (h : Haraka) : nat :=
  match h with
  | H_Fatha       => 1   (* نصف قيمة الألف *)
  | H_Damma       => 1   (* نصف قيمة الواو *)
  | H_Kasra       => 1   (* نصف قيمة الياء *)
  | H_Sukun       => 0   (* انعدام الصائت *)
  | H_Shadda      => 2   (* تضاعف قيمة موقع C *)
  | H_FathaLong   => 2   (* فتحة + ألف = قيمة كاملة *)
  | H_DammaLong   => 2   (* ضمة + واو = قيمة كاملة *)
  | H_KasraLong   => 2   (* كسرة + ياء = قيمة كاملة *)
  | H_TanweenFath => 1
  | H_TanweenDamm => 1
  | H_TanweenKasr => 1
  end.

(** ========== 1.3 الحروف الزائدة العشرة (Functional Ten) ========== *)
(* { س، ء، ل، ت، م، و، ن، ي، ه، ا } *)

Inductive FunctionalLetter :=
| FL_Sin     (* س *)
| FL_Hamza   (* ء *)
| FL_Lam     (* ل *)
| FL_Ta      (* ت *)
| FL_Mim     (* م *)
| FL_Waw     (* و *)
| FL_Nun     (* ن *)
| FL_Ya      (* ي *)
| FL_Ha      (* ه *)
| FL_Alif.   (* ا *)

(* وظائف الحروف الزائدة *)
Inductive FunctionalRole :=
| FR_Tense            (* صوغ الزمن: س/سوف/نون النسوة *)
| FR_Gender           (* تحويل الجنس: تاء التأنيث *)
| FR_Number           (* مفرد/مثنى/جمع *)
| FR_Person           (* الشخص: متكلم/مخاطب/غائب *)
| FR_Agreement        (* المطابقة مع الضمائر *)
| FR_CaseMood         (* الإعراب: رفع/نصب/جر/جزم *)
| FR_Valency          (* التعدية/اللزوم/السببية/المطاوعة *)
| FR_LogicalMode      (* نفي/استفهام/شرط/توكيد/تمني *)
| FR_Derivation       (* الاشتقاق الاسمي *)
| FR_Linking          (* الربط *)
| FR_Emphasis         (* التوكيد *)
| FR_Phonological.    (* وظيفة صوتية *)

Record FunctionalElement := {
  fe_letter : FunctionalLetter;
  fe_role   : FunctionalRole;
  fe_position : nat  (* موقعه في الكلمة: بداية/وسط/نهاية *)
}.

(************************************************************)
(* 2. الجذر - RootC2Layer                                    *)
(************************************************************)

(* دور C2 الدلالي - البؤرة الرياضية-الدلالية *)
Inductive C2Role :=
| C2_Agentive       (* فاعلية: الفعل المتعدي *)
| C2_Patientive     (* مفعولية: الانفعال *)
| C2_Eventive       (* حدثية: الحدث المجرد *)
| C2_Stative        (* حالية: الصفة/الحال *)
| C2_Locative       (* مكانية: المكان *)
| C2_Instrumental   (* آلية: الأداة *)
| C2_Causative      (* سببية: التسبب *)
| C2_Reciprocal     (* تبادلية: المفاعلة *)
| C2_Other.

Record RootC2Layer := {
  root_c1     : option ArabicLetter;
  root_c2     : ArabicLetter;           (* المركز الدلالي *)
  root_c3     : option ArabicLetter;
  root_c4     : option ArabicLetter;
  root_c2role : C2Role
}.

(* تحديد نوع الجذر *)
Definition root_type (r : RootC2Layer) : nat :=
  let c1 := match r.(root_c1) with Some _ => 1 | None => 0 end in
  let c3 := match r.(root_c3) with Some _ => 1 | None => 0 end in
  let c4 := match r.(root_c4) with Some _ => 1 | None => 0 end in
  c1 + 1 + c3 + c4.  (* 2=ثنائي، 3=ثلاثي، 4=رباعي *)

(************************************************************)
(* 3. الوزن - Pattern/Wazn                                   *)
(************************************************************)

Inductive WaznCategory :=
| WC_Mujarrad       (* مجرد *)
| WC_Mazeed_1       (* مزيد بحرف *)
| WC_Mazeed_2       (* مزيد بحرفين *)
| WC_Mazeed_3.      (* مزيد بثلاثة *)

Record Wazn := {
  wazn_id       : nat;
  wazn_category : WaznCategory;
  wazn_template : string;  (* مثال: "فَعَلَ"، "أَفْعَلَ" *)
  wazn_meaning  : string   (* الدلالة الصرفية *)
}.

(* أمثلة على الأوزان *)
Definition wazn_fa3ala : Wazn := {|
  wazn_id := 1;
  wazn_category := WC_Mujarrad;
  wazn_template := "فَعَلَ"%string;
  wazn_meaning := "فعل ثلاثي مجرد"%string
|}.

Definition wazn_af3ala : Wazn := {|
  wazn_id := 4;
  wazn_category := WC_Mazeed_1;
  wazn_template := "أَفْعَلَ"%string;
  wazn_meaning := "تعدية أو صيرورة"%string
|}.

Definition wazn_fa33ala : Wazn := {|
  wazn_id := 2;
  wazn_category := WC_Mazeed_1;
  wazn_template := "فَعَّلَ"%string;
  wazn_meaning := "تكثير أو تعدية"%string
|}.

(************************************************************)
(* 4. المفردة - Mufrada (Word)                               *)
(************************************************************)

Inductive WordClass :=
| WCl_Ism        (* اسم *)
| WCl_Fi3l       (* فعل *)
| WCl_Harf.      (* حرف *)

Inductive Tense :=
| T_Madi         (* ماضي *)
| T_Mudari3      (* مضارع *)
| T_Amr.         (* أمر *)

Inductive Gender :=
| G_Masculine    (* مذكر *)
| G_Feminine.    (* مؤنث *)

Inductive Number :=
| N_Singular     (* مفرد *)
| N_Dual         (* مثنى *)
| N_Plural.      (* جمع *)

Inductive Person :=
| P_First        (* متكلم *)
| P_Second       (* مخاطب *)
| P_Third.       (* غائب *)

Record Mufrada := {
  muf_root      : RootC2Layer;
  muf_wazn      : Wazn;
  muf_class     : WordClass;
  muf_tense     : option Tense;    (* للأفعال *)
  muf_gender    : Gender;
  muf_number    : Number;
  muf_person    : option Person;   (* للأفعال والضمائر *)
  muf_extras    : list FunctionalElement
}.

(************************************************************)
(* 5. AGT Generation Functions - دوال التوليد               *)
(************************************************************)

(* توليد كلمة من جذر ووزن *)
Definition AGT_generate_word 
           (root : RootC2Layer) 
           (wazn : Wazn)
           (cls : WordClass)
           (gen : Gender)
           (num : Number) : Mufrada := {|
  muf_root   := root;
  muf_wazn   := wazn;
  muf_class  := cls;
  muf_tense  := None;
  muf_gender := gen;
  muf_number := num;
  muf_person := None;
  muf_extras := []
|}.

(* توليد فعل من جذر *)
Definition AGT_generate_verb
           (root : RootC2Layer)
           (wazn : Wazn)
           (tense : Tense)
           (gen : Gender)
           (num : Number)
           (pers : Person) : Mufrada := {|
  muf_root   := root;
  muf_wazn   := wazn;
  muf_class  := WCl_Fi3l;
  muf_tense  := Some tense;
  muf_gender := gen;
  muf_number := num;
  muf_person := Some pers;
  muf_extras := []
|}.

(************************************************************)
(* 6. الجملة - Jumla (Sentence)                              *)
(************************************************************)

Inductive JumlaType :=
| JT_Ismiyya     (* جملة اسمية *)
| JT_Fi3liyya.   (* جملة فعلية *)

Inductive I3rabCase :=
| I3_Raf3        (* رفع *)
| I3_Nasb        (* نصب *)
| I3_Jarr        (* جر *)
| I3_Jazm.       (* جزم *)

Inductive NahwRole :=
| NR_Mubtada     (* مبتدأ *)
| NR_Khabar      (* خبر *)
| NR_Fa3il       (* فاعل *)
| NR_Maf3ul      (* مفعول به *)
| NR_Majrur      (* مجرور *)
| NR_Hal         (* حال *)
| NR_Tamyeez     (* تمييز *)
| NR_Sifa        (* صفة *)
| NR_Mudaf       (* مضاف *)
| NR_MudafIlayh  (* مضاف إليه *)
| NR_Other.

Record JumlaElement := {
  je_word  : Mufrada;
  je_i3rab : I3rabCase;
  je_role  : NahwRole
}.

Record Jumla := {
  jum_type     : JumlaType;
  jum_elements : list JumlaElement
}.

(* توليد جملة فعلية بسيطة: فعل + فاعل *)
Definition AGT_generate_jumla_fi3liyya 
           (fi3l : Mufrada) 
           (fa3il : Mufrada) : Jumla := {|
  jum_type := JT_Fi3liyya;
  jum_elements := [
    {| je_word := fi3l; je_i3rab := I3_Raf3; je_role := NR_Other |};
    {| je_word := fa3il; je_i3rab := I3_Raf3; je_role := NR_Fa3il |}
  ]
|}.

(* توليد جملة اسمية بسيطة: مبتدأ + خبر *)
Definition AGT_generate_jumla_ismiyya
           (mubtada : Mufrada)
           (khabar : Mufrada) : Jumla := {|
  jum_type := JT_Ismiyya;
  jum_elements := [
    {| je_word := mubtada; je_i3rab := I3_Raf3; je_role := NR_Mubtada |};
    {| je_word := khabar; je_i3rab := I3_Raf3; je_role := NR_Khabar |}
  ]
|}.

(************************************************************)
(* 7. الأسلوب - Uslub (Style/Muraqqab)                       *)
(************************************************************)

Inductive UslubCategory :=
| US_Khabar      (* خبر: يحتمل الصدق والكذب *)
| US_Insha       (* إنشاء: لا يحتمل *)
| US_Istifham    (* استفهام *)
| US_Amr         (* أمر *)
| US_Nahy        (* نهي *)
| US_Tamanni     (* تمني *)
| US_Tarajji     (* ترجي *)
| US_Nida        (* نداء *)
| US_Qasam       (* قسم *)
| US_Ta3ajjub    (* تعجب *)
| US_Madh        (* مدح *)
| US_Dhamm.      (* ذم *)

Record Muraqqab := {
  mur_jumla  : Jumla;
  mur_uslub  : UslubCategory
}.

(* هل الأسلوب يحتمل الصدق والكذب؟ *)
Definition is_truth_bearing (u : UslubCategory) : bool :=
  match u with
  | US_Khabar => true
  | _ => false
  end.

(* توليد مركب خبري *)
Definition AGT_generate_muraqqab_khabari (j : Jumla) : Muraqqab := {|
  mur_jumla := j;
  mur_uslub := US_Khabar
|}.

(* توليد مركب استفهامي *)
Definition AGT_generate_muraqqab_istifhami (j : Jumla) : Muraqqab := {|
  mur_jumla := j;
  mur_uslub := US_Istifham
|}.

(************************************************************)
(* 8. AGT Chain Lemmas - إثباتات سلسلة التوليد              *)
(************************************************************)

(* لمّا 1: كل مفردة مشتقة من جذر *)
Lemma AGT_word_has_root : forall (m : Mufrada),
  exists (r : RootC2Layer), m.(muf_root) = r.
Proof.
  intros m.
  exists (muf_root m).
  reflexivity.
Qed.

(* لمّا 2: كل جملة تتكون من مفردات *)
Lemma AGT_jumla_has_words : forall (j : Jumla),
  exists (elems : list JumlaElement), j.(jum_elements) = elems.
Proof.
  intros j.
  exists (jum_elements j).
  reflexivity.
Qed.

(* لمّا 3: كل مركب مبني على جملة *)
Lemma AGT_muraqqab_has_jumla : forall (m : Muraqqab),
  exists (j : Jumla), m.(mur_jumla) = j.
Proof.
  intros m.
  exists (mur_jumla m).
  reflexivity.
Qed.

(* لمّا 4: سلسلة التوليد الكاملة: جذر → مفردة → جملة → مركب *)
Lemma AGT_full_chain : forall (mur : Muraqqab),
  exists (j : Jumla) (elems : list JumlaElement),
    mur.(mur_jumla) = j /\
    j.(jum_elements) = elems /\
    forall e, In e elems -> exists r, e.(je_word).(muf_root) = r.
Proof.
  intros mur.
  exists (mur_jumla mur).
  exists (jum_elements (mur_jumla mur)).
  split. reflexivity.
  split. reflexivity.
  intros e Hin.
  exists (muf_root (je_word e)).
  reflexivity.
Qed.

(* لمّا 5: C2 هو المركز الدلالي لكل مفردة *)
Lemma AGT_c2_is_semantic_center : forall (m : Mufrada),
  exists (c2 : ArabicLetter) (role : C2Role),
    m.(muf_root).(root_c2) = c2 /\
    m.(muf_root).(root_c2role) = role.
Proof.
  intros m.
  exists (root_c2 (muf_root m)).
  exists (root_c2role (muf_root m)).
  split; reflexivity.
Qed.

(************************************************************)
(* 9. مثال تطبيقي: توليد "كَتَبَ زَيْدٌ"                      *)
(************************************************************)

(* جذر ك-ت-ب *)
Definition root_ktb : RootC2Layer := {|
  root_c1 := Some L_Kaf;
  root_c2 := L_Ta;
  root_c3 := Some L_Ba;
  root_c4 := None;
  root_c2role := C2_Eventive  (* حدث الكتابة *)
|}.

(* كَتَبَ - فعل ماضي *)
Definition kataba : Mufrada := 
  AGT_generate_verb root_ktb wazn_fa3ala T_Madi G_Masculine N_Singular P_Third.

(* جذر ز-ي-د *)
Definition root_zyd : RootC2Layer := {|
  root_c1 := Some L_Zay;
  root_c2 := L_Ya;
  root_c3 := Some L_Dal;
  root_c4 := None;
  root_c2role := C2_Stative  (* اسم علم *)
|}.

(* زَيْدٌ - اسم علم *)
Definition zayd : Mufrada := 
  AGT_generate_word root_zyd wazn_fa3ala WCl_Ism G_Masculine N_Singular.

(* جملة "كَتَبَ زَيْدٌ" *)
Definition jumla_kataba_zayd : Jumla :=
  AGT_generate_jumla_fi3liyya kataba zayd.

(* مركب خبري: "كَتَبَ زَيْدٌ" *)
Definition muraqqab_kataba_zayd : Muraqqab :=
  AGT_generate_muraqqab_khabari jumla_kataba_zayd.

(* إثبات أن "كتب زيد" يحتمل الصدق والكذب *)
Lemma kataba_zayd_is_truth_bearing :
  is_truth_bearing (mur_uslub muraqqab_kataba_zayd) = true.
Proof.
  simpl. reflexivity.
Qed.

End AGT_Core.
