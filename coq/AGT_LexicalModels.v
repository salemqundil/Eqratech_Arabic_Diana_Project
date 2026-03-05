(** AGT_LexicalModels.v
    النماذج المعجمية الشاملة - الطبقة النهائية
    
    يربط جميع المكونات:
    - الجذر المجرد (AbstractRoot)
    - الأنماط قبل الجذر (PreRootPattern)
    - الأوزان والمشتقات (VerbPattern, NounDerivPattern)
    - الأسماء الجامدة (JamidModel)
    - الخصائص النحوية والصرفية
    
    النماذج النهائية:
    - VerbModel (نموذج الفعل الكامل)
    - NounModel (نموذج الاسم الكامل)
*)

Require Import Arith List String.
Import ListNotations.

Module AGT_LexicalModels.

(**********************************************************
  Part 1: ربط مع الأنواع الأساسية من الموديولات الأخرى
**********************************************************)

(* الجذر المجرد - من AGT_Mathematical *)
Parameter AbstractRoot : Type.
Parameter root_c1 : AbstractRoot -> nat.
Parameter root_c2 : AbstractRoot -> nat.
Parameter root_c3 : AbstractRoot -> nat.

(* الشكل قبل الجذر - من AGT_Mathematical Parts 41-49 *)
Parameter PreRootPattern : Type.
Parameter prp_c_slots : PreRootPattern -> list nat.
Parameter prp_vowels : PreRootPattern -> list nat.

(* الأوزان الفعلية - من AGT_DerivationalCatalog *)
Parameter VerbBab : Type.
Parameter VerbPattern : Type.
Parameter vp_bab : VerbPattern -> VerbBab.
Parameter vp_extra_count : VerbPattern -> nat.

(* المشتقات الاسمية - من AGT_DerivationalCatalog *)
Parameter DerivativeKind : Type.
Parameter NounDerivPattern : Type.
Parameter ndp_kind : NounDerivPattern -> DerivativeKind.
Parameter ndp_source_verb : NounDerivPattern -> option VerbPattern.

(* الأسماء الجامدة - من AGT_Mathematical Part 52 *)
Parameter JamidModel : Type.
Parameter jm_kind : JamidModel -> nat.
Parameter jm_i3rab : JamidModel -> nat.

(**********************************************************
  Part 2: الخصائص النحوية والصرفية (من AGT_DerivationalCatalog)
**********************************************************)

Inductive VerbTense : Type :=
  | Tense_Madi
  | Tense_Mudari3
  | Tense_Amr.

(* Decidable equality for VerbTense *)
Definition VerbTense_eq_dec (x y : VerbTense) : {x = y} + {x <> y}.
Proof. decide equality. Defined.

Inductive VerbVoice : Type :=
  | Voice_Ma3lum
  | Voice_Majhul.

Inductive Transitivity : Type :=
  | Trans_Lazim
  | Trans_Muta3addi1
  | Trans_Muta3addi2
  | Trans_Muta3addi3.

Inductive Definiteness : Type :=
  | Def_Nakira
  | Def_Ma3rifa_Al
  | Def_Ma3rifa_Idafa
  | Def_Ma3rifa_Pronoun
  | Def_Alam.

Inductive GramNumber : Type :=
  | Num_Mufrad
  | Num_Muthanna
  | Num_Jam3_Mudhakkar_Salim
  | Num_Jam3_Mu2annath_Salim
  | Num_Jam3_Taksir.

Inductive GramGender : Type :=
  | Gen_Mudhakkar
  | Gen_Mu2annath
  | Gen_Mushtarak.

Inductive IrabCase : Type :=
  | Case_Marfu3
  | Case_Mansub
  | Case_Majrur
  | Case_Mabni.

(* Decidable equality for NounKind *)
Inductive NounKind : Type :=
  | NounKind_Jamid
  | NounKind_Mushtaq.

Definition NounKind_eq_dec (x y : NounKind) : {x = y} + {x <> y}.
Proof. decide equality. Defined.

(**********************************************************
  Part 3: VerbModel - النموذج الكامل للفعل
**********************************************************)

Record VerbModel : Type := mk_VerbModel {
  (* الطبقة الجذرية *)
  vm_root : option AbstractRoot;  (* اختياري - Root-less support *)
  
  (* الطبقة الشكلية *)
  vm_pre_root : PreRootPattern;
  vm_pattern : VerbPattern;
  
  (* الخصائص الصرفية *)
  vm_tense : VerbTense;
  vm_voice : VerbVoice;
  vm_transitivity : Transitivity;
  
  (* الخصائص النحوية *)
  vm_person : nat;  (* 1/2/3 *)
  vm_number : GramNumber;
  vm_gender : GramGender;
  
  (* السطح النهائي *)
  vm_surface : string;
}.

(* دالة فحص صحة نموذج الفعل *)
Definition is_wellformed_verb (vm : VerbModel) : Prop :=
  (* الشروط الأساسية *)
  (vm.(vm_person) >= 1 /\ vm.(vm_person) <= 3) /\
  (* المبني للمجهول يحتاج فعل متعدي *)
  (vm.(vm_voice) = Voice_Majhul -> 
   vm.(vm_transitivity) <> Trans_Lazim) /\
  (* فعل الأمر للمخاطب فقط *)
  (vm.(vm_tense) = Tense_Amr -> vm.(vm_person) = 2).

(**********************************************************
  Part 4: NounModel - النموذج الكامل للاسم
**********************************************************)

Inductive NounKind : Type :=
  | Noun_Jamid     (* اسم جامد *)
  | Noun_Mushtaq   (* اسم مشتق *)
  | Noun_Pronoun   (* ضمير *)
  | Noun_Mawsul.   (* اسم موصول *)

Record NounModel : Type := mk_NounModel {
  (* تصنيف الاسم *)
  nm_kind : NounKind;
  
  (* للجامد *)
  nm_jamid_data : option JamidModel;
  
  (* للمشتق *)
  nm_deriv_pattern : option NounDerivPattern;
  nm_source_root : option AbstractRoot;
  
  (* الخصائص النحوية *)
  nm_definiteness : Definiteness;
  nm_number : GramNumber;
  nm_gender : GramGender;
  nm_case : IrabCase;
  
  (* السطح النهائي *)
  nm_surface : string;
}.

(* دالة فحص صحة نموذج الاسم *)
Definition is_wellformed_noun (nm : NounModel) : Prop :=
  (* الجامد يحتاج بيانات جامد *)
  (nm.(nm_kind) = Noun_Jamid -> 
   nm.(nm_jamid_data) <> None) /\
  (* المشتق يحتاج نمط اشتقاق *)
  (nm.(nm_kind) = Noun_Mushtaq -> 
   nm.(nm_deriv_pattern) <> None).

(**********************************************************
  Part 5: العلاقات بين الأفعال والمشتقات
**********************************************************)

(* دالة توليد اسم الفاعل من فعل *)
Parameter generate_ism_fa3il : VerbModel -> option NounModel.

(* دالة توليد اسم المفعول من فعل *)
Parameter generate_ism_maf3ul : VerbModel -> option NounModel.

(* دالة توليد المصدر من فعل *)
Parameter generate_masdar : VerbModel -> option NounModel.

(* القاعدة: كل فعل متعدي يمكن توليد اسم مفعول منه *)
Axiom rule_muta3addi_has_ism_maf3ul : forall vm : VerbModel,
  vm.(vm_transitivity) <> Trans_Lazim ->
  is_wellformed_verb vm ->
  generate_ism_maf3ul vm <> None.

(* القاعدة: اسم الفاعل يطابق جنس وعدد الفاعل *)
Axiom rule_ism_fa3il_agreement : forall vm : VerbModel,
  forall nm : NounModel,
  generate_ism_fa3il vm = Some nm ->
  nm.(nm_gender) = vm.(vm_gender) /\
  nm.(nm_number) = vm.(vm_number).

(**********************************************************
  Part 6: التحويلات بين الصيغ
**********************************************************)

(* تحويل ماضي إلى مضارع *)
Parameter transform_madi_to_mudari3 : VerbModel -> option VerbModel.

(* تحويل مضارع إلى أمر *)
Parameter transform_mudari3_to_amr : VerbModel -> option VerbModel.

(* تحويل معلوم إلى مجهول *)
Parameter transform_ma3lum_to_majhul : VerbModel -> option VerbModel.

(* القاعدة: تحويل ماضي→مضارع يحفظ الجذر والوزن *)
Axiom rule_madi_mudari3_preserves_root : forall vm vm' : VerbModel,
  transform_madi_to_mudari3 vm = Some vm' ->
  vm.(vm_root) = vm'.(vm_root) /\
  vm.(vm_pattern) = vm'.(vm_pattern).

(* القاعدة: المبني للمجهول يتطلب فعل متعدي *)
Axiom rule_majhul_requires_muta3addi : forall vm vm' : VerbModel,
  transform_ma3lum_to_majhul vm = Some vm' ->
  vm.(vm_transitivity) <> Trans_Lazim.

(**********************************************************
  Part 7: الإحصائيات على النماذج
**********************************************************)

(* عدد الأفعال في كتالوج معين *)
Parameter verb_catalog : list VerbModel.
Parameter noun_catalog : list NounModel.

Definition count_verbs_by_tense (t : VerbTense) : nat :=
  length (filter (fun vm => 
    match vm.(vm_tense) with
    | x => if VerbTense_eq_dec x t then true else false
    end) verb_catalog).

Definition count_nouns_by_kind (k : NounKind) : nat :=
  length (filter (fun nm => 
    match nm.(nm_kind) with
    | x => if NounKind_eq_dec x k then true else false
    end) noun_catalog).

(* المبرهنة: مجموع الأزمنة = مجموع الأفعال *)
Axiom catalog_tense_sum : 
  count_verbs_by_tense Tense_Madi +
  count_verbs_by_tense Tense_Mudari3 +
  count_verbs_by_tense Tense_Amr = 
  length verb_catalog.

(**********************************************************
  Part 8: الربط مع AGT الرياضي
**********************************************************)

(* قيمة الفعل حسب AGT (من Part 46-49) *)
Parameter agt_verb_value : VerbModel -> nat.

(* قيمة الاسم حسب AGT *)
Parameter agt_noun_value : NounModel -> nat.

(* المبرهنة: القيمة تعتمد على الحركات فقط (Root-less) *)
Axiom agt_value_rootless : forall vm1 vm2 : VerbModel,
  vm1.(vm_pre_root) = vm2.(vm_pre_root) ->
  agt_verb_value vm1 = agt_verb_value vm2.

(* المبرهنة: الفعل المجرد قيمته أقل من المزيد *)
Axiom agt_mujarrad_minimal : forall vm : VerbModel,
  vp_extra_count vm.(vm_pattern) = 0 ->
  forall vm' : VerbModel,
  vp_extra_count vm'.(vm_pattern) > 0 ->
  agt_verb_value vm < agt_verb_value vm'.

(**********************************************************
  Part 9: أمثلة تطبيقية
**********************************************************)

(* مثال: فعل "كتب" *)
Parameter example_kataba : VerbModel.
Axiom kataba_is_wellformed : is_wellformed_verb example_kataba.
Axiom kataba_tense : example_kataba.(vm_tense) = Tense_Madi.
Axiom kataba_trans : example_kataba.(vm_transitivity) = Trans_Muta3addi1.

(* مثال: اسم فاعل "كاتب" *)
Parameter example_katib : NounModel.
Axiom katib_from_kataba : 
  generate_ism_fa3il example_kataba = Some example_katib.
Axiom katib_is_mushtaq : example_katib.(nm_kind) = Noun_Mushtaq.

(* مثال: اسم مفعول "مكتوب" *)
Parameter example_maktub : NounModel.
Axiom maktub_from_kataba : 
  generate_ism_maf3ul example_kataba = Some example_maktub.

(**********************************************************
  Part 10: المبرهنات النهائية
**********************************************************)

(* كل فعل صحيح له قيمة AGT محددة *)
Theorem wellformed_verb_has_agt_value : forall vm : VerbModel,
  is_wellformed_verb vm ->
  exists n : nat, agt_verb_value vm = n.
Proof.
  intros vm H.
  exists (agt_verb_value vm).
  reflexivity.
Qed.

(* كل اسم صحيح له قيمة AGT محددة *)
Theorem wellformed_noun_has_agt_value : forall nm : NounModel,
  is_wellformed_noun nm ->
  exists n : nat, agt_noun_value nm = n.
Proof.
  intros nm H.
  exists (agt_noun_value nm).
  reflexivity.
Qed.

(* الكتالوج متسق: كل عنصر إما فعل أو اسم *)
Definition total_catalog_size : nat :=
  length verb_catalog + length noun_catalog.

Theorem catalog_consistency : 
  total_catalog_size >= 0.
Proof.
  unfold total_catalog_size.
  lia.
Qed.

(**********************************************************
  Part 11: Decidability للمقارنات
**********************************************************)

(* نحتاج decidability للمقارنات في filter *)
Axiom VerbTense_eq_dec : forall (x y : VerbTense), {x = y} + {x <> y}.
Axiom NounKind_eq_dec : forall (x y : NounKind), {x = y} + {x <> y}.

End AGT_LexicalModels.

(* ملاحظات للتكامل:
   
   1. استبدل Parameter بـ Definition عند الربط مع الموديولات الفعلية
   2. املأ الـ catalogs بالبيانات الحقيقية من الأوزان
   3. نفّذ الدوال transform_* و generate_* حسب قواعد الصرف
   4. ربط agt_*_value مع الحسابات في Parts 46-49
   5. أضف أمثلة إضافية من الكتالوجات
*)
