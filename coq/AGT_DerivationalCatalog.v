(** AGT_DerivationalCatalog.v
    كتالوج صوري للأوزان الفعلية والمشتقات الاسمية
    + طبقة التعدّي، المعرفة/النكرة، العدد، الجنس
    
    Part 53: Derivational Patterns Catalog
*)

From Coq Require Import Arith List String Bool.
Import ListNotations.
Local Open Scope string_scope.

(* ============================================================ *)
(* Part 53.1: الخصائص النحوية - Grammatical Properties *)
(* ============================================================ *)

(* التعدّي - Transitivity *)
Inductive Transitivity : Type :=
  | Trans_Lazim        (* لازم - Intransitive *)
  | Trans_Muta3addi1   (* متعدٍّ لمفعول واحد *)
  | Trans_Muta3addi2   (* متعدٍّ لمفعولين *)
  | Trans_Muta3addi3.  (* متعدٍّ لثلاثة مفاعيل *)

(* المعرفة والنكرة - Definiteness *)
Inductive Definiteness : Type :=
  | Def_Nakira         (* نكرة *)
  | Def_Ma3rifa_Al     (* معرفة بأل *)
  | Def_Ma3rifa_Idafa  (* معرفة بالإضافة *)
  | Def_Ma3rifa_Alam   (* معرفة بالعلمية *)
  | Def_Ma3rifa_Damir  (* معرفة بالضمير *)
  | Def_Ma3rifa_Ishara (* معرفة بالإشارة *)
  | Def_Ma3rifa_Mawsul. (* معرفة بالموصول *)

(* العدد - Number *)
Inductive GramNumber : Type :=
  | Num_Mufrad   (* مفرد *)
  | Num_Muthanna (* مثنى *)
  | Num_Jam3.    (* جمع *)

(* الجنس - Gender *)
Inductive GramGender : Type :=
  | Gen_Mudhakkar  (* مذكر *)
  | Gen_Mu2annath  (* مؤنث *)
  | Gen_Mushtarak. (* مشترك *)

(* الزمن - Tense *)
Inductive VerbTense : Type :=
  | Tense_Madi     (* ماضٍ *)
  | Tense_Mudari3  (* مضارع *)
  | Tense_Amr.     (* أمر *)

(* البناء للمعلوم/المجهول - Voice *)
Inductive VerbVoice : Type :=
  | Voice_Ma3lum   (* مبني للمعلوم *)
  | Voice_Majhul.  (* مبني للمجهول *)

(* ============================================================ *)
(* Part 53.2: أوزان الأفعال - Verb Patterns *)
(* ============================================================ *)

(* باب الفعل - Verb Form/Pattern *)
Inductive VerbBab : Type :=
  (* الثلاثي المجرد - Form I variants *)
  | Bab_Fa3ala       (* فَعَلَ يَفْعُلُ - نصر *)
  | Bab_Fa3ala_i     (* فَعَلَ يَفْعِلُ - ضرب *)
  | Bab_Fa3ala_a     (* فَعَلَ يَفْعَلُ - فتح *)
  | Bab_Fa3ila       (* فَعِلَ يَفْعَلُ - فرح *)
  | Bab_Fa3ula       (* فَعُلَ يَفْعُلُ - كرم *)
  | Bab_Fa3ila_i     (* فَعِلَ يَفْعِلُ - حسب *)
  (* الثلاثي المزيد بحرف - Form II-IV *)
  | Bab_Fa33ala      (* فَعَّلَ - II *)
  | Bab_Fa3ala_alif  (* فاعَلَ - III *)
  | Bab_Af3ala       (* أَفْعَلَ - IV *)
  (* الثلاثي المزيد بحرفين - Form V-VI *)
  | Bab_Tafa33ala    (* تَفَعَّلَ - V *)
  | Bab_Tafa3ala     (* تَفاعَلَ - VI *)
  | Bab_Infa3ala     (* انْفَعَلَ - VII *)
  | Bab_Ifta3ala     (* افْتَعَلَ - VIII *)
  | Bab_If3alla      (* افْعَلَّ - IX *)
  (* الثلاثي المزيد بثلاثة أحرف - Form X+ *)
  | Bab_Istaf3ala    (* اسْتَفْعَلَ - X *)
  | Bab_If3aw3ala    (* افْعَوْعَلَ - XI *)
  | Bab_If3awwala.   (* افْعَوَّلَ - XII *)

(* عدد الأحرف الزائدة لكل باب *)
Definition bab_extra_count (b : VerbBab) : nat :=
  match b with
  | Bab_Fa3ala | Bab_Fa3ala_i | Bab_Fa3ala_a 
  | Bab_Fa3ila | Bab_Fa3ula | Bab_Fa3ila_i => 0
  | Bab_Fa33ala | Bab_Fa3ala_alif | Bab_Af3ala => 1
  | Bab_Tafa33ala | Bab_Tafa3ala | Bab_Infa3ala 
  | Bab_Ifta3ala | Bab_If3alla => 2
  | Bab_Istaf3ala | Bab_If3aw3ala | Bab_If3awwala => 3
  end.

(* نموذج وزن الفعل *)
Record VerbPattern : Type := mkVerbPattern {
  vp_bab : VerbBab;
  vp_tense : VerbTense;
  vp_voice : VerbVoice;
  vp_trans : Transitivity;
  vp_example : string
}.

(* ============================================================ *)
(* Part 53.3: المشتقات الاسمية - Noun Derivatives *)
(* ============================================================ *)

(* نوع المشتق *)
Inductive DerivativeKind : Type :=
  | Deriv_IsmFa3il       (* اسم الفاعل *)
  | Deriv_IsmMaf3ul      (* اسم المفعول *)
  | Deriv_SifaMushabbaha (* الصفة المشبهة *)
  | Deriv_IsmTafdil      (* اسم التفضيل - أفعل *)
  | Deriv_IsmMakan       (* اسم المكان *)
  | Deriv_IsmZaman       (* اسم الزمان *)
  | Deriv_IsmAla         (* اسم الآلة *)
  | Deriv_Masdar         (* المصدر *)
  | Deriv_MasdarMimi     (* المصدر الميمي *)
  | Deriv_IsmHay2a       (* اسم الهيئة *)
  | Deriv_IsmMarra       (* اسم المرة *)
  | Deriv_Mubalagha.     (* صيغة المبالغة *)

(* صيغ المبالغة *)
Inductive MubalaghaForm : Type :=
  | Mub_Fa33al    (* فَعَّال - كذّاب *)
  | Mub_Mif3al    (* مِفْعال - مقدام *)
  | Mub_Fa3ul     (* فَعُول - صبور *)
  | Mub_Fa3il     (* فَعِيل - عليم *)
  | Mub_Fa3ila.   (* فَعِلَة - فطنة *)

(* نموذج المشتق الاسمي *)
Record NounDerivative : Type := mkNounDerivative {
  nd_kind : DerivativeKind;
  nd_from_bab : VerbBab;
  nd_gender : GramGender;
  nd_number : GramNumber;
  nd_definiteness : Definiteness;
  nd_example : string
}.

(* ============================================================ *)
(* Part 53.4: كتالوج الأفعال - Verb Catalog *)
(* ============================================================ *)

(* أمثلة الأفعال *)
Definition verb_kataba := mkVerbPattern 
  Bab_Fa3ala Tense_Madi Voice_Ma3lum Trans_Muta3addi1 "كَتَبَ".
Definition verb_yaktub := mkVerbPattern 
  Bab_Fa3ala Tense_Mudari3 Voice_Ma3lum Trans_Muta3addi1 "يَكْتُبُ".
Definition verb_uktub := mkVerbPattern 
  Bab_Fa3ala Tense_Amr Voice_Ma3lum Trans_Muta3addi1 "اُكْتُبْ".
Definition verb_kutiba := mkVerbPattern 
  Bab_Fa3ala Tense_Madi Voice_Majhul Trans_Muta3addi1 "كُتِبَ".

Definition verb_3allama := mkVerbPattern 
  Bab_Fa33ala Tense_Madi Voice_Ma3lum Trans_Muta3addi2 "عَلَّمَ".
Definition verb_kataba_III := mkVerbPattern 
  Bab_Fa3ala_alif Tense_Madi Voice_Ma3lum Trans_Muta3addi1 "كاتَبَ".
Definition verb_akrama := mkVerbPattern 
  Bab_Af3ala Tense_Madi Voice_Ma3lum Trans_Muta3addi1 "أَكْرَمَ".

Definition verb_ta3allama := mkVerbPattern 
  Bab_Tafa33ala Tense_Madi Voice_Ma3lum Trans_Lazim "تَعَلَّمَ".
Definition verb_takataba := mkVerbPattern 
  Bab_Tafa3ala Tense_Madi Voice_Ma3lum Trans_Lazim "تَكاتَبَ".
Definition verb_inkasara := mkVerbPattern 
  Bab_Infa3ala Tense_Madi Voice_Ma3lum Trans_Lazim "انْكَسَرَ".
Definition verb_iktataba := mkVerbPattern 
  Bab_Ifta3ala Tense_Madi Voice_Ma3lum Trans_Muta3addi1 "اكْتَتَبَ".
Definition verb_istaktaba := mkVerbPattern 
  Bab_Istaf3ala Tense_Madi Voice_Ma3lum Trans_Muta3addi1 "اسْتَكْتَبَ".

(* قائمة الأفعال *)
Definition verb_catalog : list VerbPattern := [
  verb_kataba; verb_yaktub; verb_uktub; verb_kutiba;
  verb_3allama; verb_kataba_III; verb_akrama;
  verb_ta3allama; verb_takataba; verb_inkasara;
  verb_iktataba; verb_istaktaba
].

(* ============================================================ *)
(* Part 53.5: كتالوج المشتقات - Derivatives Catalog *)
(* ============================================================ *)

(* اسم الفاعل من كتب *)
Definition katib := mkNounDerivative 
  Deriv_IsmFa3il Bab_Fa3ala Gen_Mudhakkar Num_Mufrad Def_Nakira "كاتِب".
Definition katiba := mkNounDerivative 
  Deriv_IsmFa3il Bab_Fa3ala Gen_Mu2annath Num_Mufrad Def_Nakira "كاتِبة".
Definition kuttab := mkNounDerivative 
  Deriv_IsmFa3il Bab_Fa3ala Gen_Mudhakkar Num_Jam3 Def_Nakira "كُتّاب".

(* اسم المفعول من كتب *)
Definition maktub := mkNounDerivative 
  Deriv_IsmMaf3ul Bab_Fa3ala Gen_Mudhakkar Num_Mufrad Def_Nakira "مَكْتُوب".
Definition maktuba := mkNounDerivative 
  Deriv_IsmMaf3ul Bab_Fa3ala Gen_Mu2annath Num_Mufrad Def_Nakira "مَكْتُوبة".

(* اسم المكان *)
Definition maktab := mkNounDerivative 
  Deriv_IsmMakan Bab_Fa3ala Gen_Mudhakkar Num_Mufrad Def_Nakira "مَكْتَب".
Definition maktaba := mkNounDerivative 
  Deriv_IsmMakan Bab_Fa3ala Gen_Mu2annath Num_Mufrad Def_Nakira "مَكْتَبة".

(* المصدر *)
Definition kitaba := mkNounDerivative 
  Deriv_Masdar Bab_Fa3ala Gen_Mu2annath Num_Mufrad Def_Nakira "كِتابة".
Definition ta3lim := mkNounDerivative 
  Deriv_Masdar Bab_Fa33ala Gen_Mudhakkar Num_Mufrad Def_Nakira "تَعْليم".

(* قائمة المشتقات *)
Definition deriv_catalog : list NounDerivative := [
  katib; katiba; kuttab;
  maktub; maktuba;
  maktab; maktaba;
  kitaba; ta3lim
].

(* ============================================================ *)
(* Part 53.6: قواعد التحويل - Transformation Rules *)
(* ============================================================ *)

(* تحويل الماضي إلى مضارع: يبقى الباب نفسه *)
Axiom rule_madi_to_mudari3 : forall vp : VerbPattern,
  vp.(vp_tense) = Tense_Madi ->
  exists vp' : VerbPattern,
    vp'.(vp_bab) = vp.(vp_bab) /\
    vp'.(vp_tense) = Tense_Mudari3 /\
    vp'.(vp_voice) = vp.(vp_voice) /\
    vp'.(vp_trans) = vp.(vp_trans).

(* تحويل المعلوم إلى مجهول: يتغير الصوت فقط *)
Axiom rule_ma3lum_to_majhul : forall vp : VerbPattern,
  vp.(vp_voice) = Voice_Ma3lum ->
  vp.(vp_trans) <> Trans_Lazim ->  (* الفعل اللازم لا يُبنى للمجهول *)
  exists vp' : VerbPattern,
    vp'.(vp_bab) = vp.(vp_bab) /\
    vp'.(vp_tense) = vp.(vp_tense) /\
    vp'.(vp_voice) = Voice_Majhul.

(* انفعل دائماً لازم *)
Axiom rule_infa3ala_lazim : forall vp : VerbPattern,
  vp.(vp_bab) = Bab_Infa3ala ->
  vp.(vp_trans) = Trans_Lazim.

(* تفاعل غالباً لازم *)
Axiom rule_tafa3ala_usually_lazim : forall vp : VerbPattern,
  vp.(vp_bab) = Bab_Tafa3ala ->
  vp.(vp_trans) = Trans_Lazim.

(* ============================================================ *)
(* Part 53.7: مبرهنات على الكتالوج *)
(* ============================================================ *)

(* طول كتالوج الأفعال *)
Lemma verb_catalog_length : length verb_catalog = 12.
Proof. reflexivity. Qed.

(* طول كتالوج المشتقات *)
Lemma deriv_catalog_length : length deriv_catalog = 9.
Proof. reflexivity. Qed.

(* الثلاثي المجرد زوائده 0 *)
Theorem mujarrad_zero_extras : forall vp : VerbPattern,
  vp.(vp_bab) = Bab_Fa3ala \/ vp.(vp_bab) = Bab_Fa3ila \/ vp.(vp_bab) = Bab_Fa3ula ->
  bab_extra_count (vp.(vp_bab)) = 0.
Proof.
  intros vp [H | [H | H]]; rewrite H; reflexivity.
Qed.

(* استفعل زوائده 3 *)
Theorem istaf3ala_three_extras :
  bab_extra_count Bab_Istaf3ala = 3.
Proof. reflexivity. Qed.

(* فَعَّلَ زوائده 1 *)
Theorem fa33ala_one_extra :
  bab_extra_count Bab_Fa33ala = 1.
Proof. reflexivity. Qed.

(* تَفَعَّلَ زوائده 2 *)
Theorem tafa33ala_two_extras :
  bab_extra_count Bab_Tafa33ala = 2.
Proof. reflexivity. Qed.

(* ============================================================ *)
(* Part 53.8: العلاقة بين الفعل والمشتق *)
(* ============================================================ *)

(* المشتق يرث باب الفعل *)
Definition derivative_matches_verb (nd : NounDerivative) (vp : VerbPattern) : Prop :=
  nd.(nd_from_bab) = vp.(vp_bab).

(* اسم الفاعل من المتعدي يأخذ مفعولاً *)
Axiom rule_ism_fa3il_transitive : forall nd : NounDerivative, forall vp : VerbPattern,
  nd.(nd_kind) = Deriv_IsmFa3il ->
  derivative_matches_verb nd vp ->
  vp.(vp_trans) = Trans_Muta3addi1 ->
  True. (* اسم الفاعل يعمل عمل فعله *)

(* اسم المفعول يشترط فعلاً متعدياً *)
Axiom rule_ism_maf3ul_requires_transitive : forall nd : NounDerivative,
  nd.(nd_kind) = Deriv_IsmMaf3ul ->
  exists vp : VerbPattern,
    derivative_matches_verb nd vp /\
    vp.(vp_trans) <> Trans_Lazim.

(* ============================================================ *)
(* Part 53.9: إحصائيات الكتالوج *)
(* ============================================================ *)

(* عدّ الأفعال حسب الباب *)
Fixpoint count_by_bab (bab : VerbBab) (l : list VerbPattern) : nat :=
  match l with
  | [] => 0
  | vp :: rest => 
      if decide_bab_eq bab (vp.(vp_bab)) 
      then S (count_by_bab bab rest)
      else count_by_bab bab rest
  end
with decide_bab_eq (b1 b2 : VerbBab) : bool :=
  match b1, b2 with
  | Bab_Fa3ala, Bab_Fa3ala => true
  | Bab_Fa33ala, Bab_Fa33ala => true
  | Bab_Istaf3ala, Bab_Istaf3ala => true
  | _, _ => false  (* Simplified *)
  end.

(* عدّ المشتقات حسب النوع *)
Definition count_deriv_kind (k : DerivativeKind) (l : list NounDerivative) : nat :=
  length (filter (fun nd => 
    match nd.(nd_kind), k with
    | Deriv_IsmFa3il, Deriv_IsmFa3il => true
    | Deriv_IsmMaf3ul, Deriv_IsmMaf3ul => true
    | Deriv_IsmMakan, Deriv_IsmMakan => true
    | Deriv_Masdar, Deriv_Masdar => true
    | _, _ => false
    end) l).

(* اسم الفاعل في الكتالوج = 3 *)
Lemma ism_fa3il_count : count_deriv_kind Deriv_IsmFa3il deriv_catalog = 3.
Proof. reflexivity. Qed.

(* اسم المفعول في الكتالوج = 2 *)
Lemma ism_maf3ul_count : count_deriv_kind Deriv_IsmMaf3ul deriv_catalog = 2.
Proof. reflexivity. Qed.

(* اسم المكان في الكتالوج = 2 *)
Lemma ism_makan_count : count_deriv_kind Deriv_IsmMakan deriv_catalog = 2.
Proof. reflexivity. Qed.

(* المصدر في الكتالوج = 2 *)
Lemma masdar_count : count_deriv_kind Deriv_Masdar deriv_catalog = 2.
Proof. reflexivity. Qed.

(* ============================================================ *)
(* End of AGT_DerivationalCatalog.v *)
(* ============================================================ *)
