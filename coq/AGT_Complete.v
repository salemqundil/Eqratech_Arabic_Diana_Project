(** AGT_Complete.v - Arabic Generative Theorem Complete Implementation **)
(** المبرهنة العربية المولِّدة - التنفيذ الكامل **)

From Coq Require Import String List Nat Arith Bool.
Import ListNotations.

Set Implicit Arguments.
Set Asymmetric Patterns.

Module AGT_Complete.

(************************************************************)
(*           الجزء الأول: الأساس الصوتي                      *)
(*           Part 1: Phonological Foundation                 *)
(************************************************************)

(** ========== 1.1 الحروف العربية الـ 29 ========== *)

Inductive ArabicLetter :=
| L_Hamza    (* ء *)  | L_Alif     (* ا *)  | L_Ba       (* ب *)
| L_Ta       (* ت *)  | L_Tha      (* ث *)  | L_Jim      (* ج *)
| L_Ha       (* ح *)  | L_Kha      (* خ *)  | L_Dal      (* د *)
| L_Dhal     (* ذ *)  | L_Ra       (* ر *)  | L_Zay      (* ز *)
| L_Sin      (* س *)  | L_Shin     (* ش *)  | L_Sad      (* ص *)
| L_Dad      (* ض *)  | L_Tah      (* ط *)  | L_Dhah     (* ظ *)
| L_Ayn      (* ع *)  | L_Ghayn    (* غ *)  | L_Fa       (* ف *)
| L_Qaf      (* ق *)  | L_Kaf      (* ك *)  | L_Lam      (* ل *)
| L_Mim      (* م *)  | L_Nun      (* ن *)  | L_Ha2      (* ه *)
| L_Waw      (* و *)  | L_Ya.      (* ي *)

(* تصنيف الحروف حسب المخرج *)
Inductive Makhraj :=
| MK_Halqi       (* حلقي: ء ه ع ح غ خ *)
| MK_Lahawi      (* لهوي: ق ك *)
| MK_Shajariy    (* شجري: ج ش ي *)
| MK_Asali       (* أسلي: س ص ز *)
| MK_Nit3i       (* نطعي: ت د ط *)
| MK_Lithawi     (* لثوي: ث ذ ظ *)
| MK_Asnaniy     (* أسناني: ف *)
| MK_Shafawi     (* شفوي: ب م و *)
| MK_Khayshumi   (* خيشومي: ن *)
| MK_Janibiy     (* جانبي: ل *)
| MK_Takarruri.  (* تكراري: ر *)

Definition letter_makhraj (l : ArabicLetter) : Makhraj :=
  match l with
  | L_Hamza | L_Ha2 | L_Ayn | L_Ha | L_Ghayn | L_Kha => MK_Halqi
  | L_Qaf | L_Kaf => MK_Lahawi
  | L_Jim | L_Shin | L_Ya => MK_Shajariy
  | L_Sin | L_Sad | L_Zay => MK_Asali
  | L_Ta | L_Dal | L_Tah => MK_Nit3i
  | L_Tha | L_Dhal | L_Dhah => MK_Lithawi
  | L_Fa => MK_Asnaniy
  | L_Ba | L_Mim | L_Waw => MK_Shafawi
  | L_Nun => MK_Khayshumi
  | L_Lam => MK_Janibiy
  | L_Ra => MK_Takarruri
  | L_Alif => MK_Halqi  (* الألف من الحلق *)
  | L_Sad => MK_Asali   (* الصاد من الأسلي *)
  | L_Dad => MK_Asali   (* الضاد من الأسلي *)
  end.

(* صفات الحروف *)
Inductive LetterSifa :=
| SF_Jahr       (* جهر *)
| SF_Hams       (* همس *)
| SF_Shidda     (* شدة *)
| SF_Rakhawa    (* رخاوة *)
| SF_Tawassut   (* توسط *)
| SF_Isti3la    (* استعلاء *)
| SF_Istifal    (* استفال *)
| SF_Itbaq      (* إطباق *)
| SF_Infitah    (* انفتاح *)
| SF_Idhlaq     (* إذلاق *)
| SF_Ismat.     (* إصمات *)

(** ========== 1.2 الحركات (Vowels) ========== *)

Inductive Haraka :=
| H_Fatha       (* فتحة *)
| H_Damma       (* ضمة *)
| H_Kasra       (* كسرة *)
| H_Sukun       (* سكون *)
| H_Shadda      (* شدة *)
| H_FathaLong   (* ألف مد *)
| H_DammaLong   (* واو مد *)
| H_KasraLong   (* ياء مد *)
| H_TanweenFath (* تنوين فتح *)
| H_TanweenDamm (* تنوين ضم *)
| H_TanweenKasr.(* تنوين كسر *)

(* القيمة الرياضية للحركة *)
Definition haraka_value (h : Haraka) : nat :=
  match h with
  | H_Fatha       => 1
  | H_Damma       => 1
  | H_Kasra       => 1
  | H_Sukun       => 0
  | H_Shadda      => 2
  | H_FathaLong   => 2
  | H_DammaLong   => 2
  | H_KasraLong   => 2
  | H_TanweenFath => 1
  | H_TanweenDamm => 1
  | H_TanweenKasr => 1
  end.

(** ========== 1.3 الحروف الزائدة العشرة ========== *)

Inductive FunctionalLetter :=
| FL_Sin     (* س *)  | FL_Hamza   (* ء *)  | FL_Lam     (* ل *)
| FL_Ta      (* ت *)  | FL_Mim     (* م *)  | FL_Waw     (* و *)
| FL_Nun     (* ن *)  | FL_Ya      (* ي *)  | FL_Ha      (* ه *)
| FL_Alif.   (* ا *)

Inductive FunctionalRole :=
| FR_Tense       | FR_Gender      | FR_Number      | FR_Person
| FR_Agreement   | FR_CaseMood    | FR_Valency     | FR_LogicalMode
| FR_Derivation  | FR_Linking     | FR_Emphasis    | FR_Phonological.

Record FunctionalElement := {
  fe_letter   : FunctionalLetter;
  fe_role     : FunctionalRole;
  fe_position : nat
}.

(************************************************************)
(*           الجزء الثاني: الجذر ومركزية C2                  *)
(*           Part 2: Root and C2 Centrality                  *)
(************************************************************)

(** ========== 2.1 دور C2 الدلالي ========== *)

Inductive C2Role :=
| C2_Agentive       (* فاعلية *)
| C2_Patientive     (* مفعولية *)
| C2_Eventive       (* حدثية *)
| C2_Stative        (* حالية *)
| C2_Locative       (* مكانية *)
| C2_Temporal       (* زمانية *)
| C2_Instrumental   (* آلية *)
| C2_Causative      (* سببية *)
| C2_Reciprocal     (* تبادلية *)
| C2_Reflexive      (* انعكاسية *)
| C2_Intensive      (* تكثيرية *)
| C2_Attributive    (* وصفية *)
| C2_Other.

(** ========== 2.2 الجذر ========== *)

Inductive RootClass :=
| RC_Thulathi       (* ثلاثي *)
| RC_Rubai          (* رباعي *)
| RC_Khumasi        (* خماسي *)
| RC_Sudasi.        (* سداسي *)

Record RootC2Layer := {
  root_c1     : option ArabicLetter;
  root_c2     : ArabicLetter;
  root_c3     : option ArabicLetter;
  root_c4     : option ArabicLetter;
  root_c5     : option ArabicLetter;
  root_class  : RootClass;
  root_c2role : C2Role
}.

(* حروف العلة *)
Definition is_weak_letter (l : ArabicLetter) : bool :=
  match l with
  | L_Alif | L_Waw | L_Ya => true
  | _ => false
  end.

(* نوع الجذر من حيث الصحة والاعتلال *)
Inductive RootHealth :=
| RH_Sahih_Salim     (* صحيح سالم *)
| RH_Sahih_Mudaaf    (* صحيح مضعّف *)
| RH_Sahih_Mahmouz   (* صحيح مهموز *)
| RH_Mu3tall_Mithal  (* معتل مثال: و/ي في أوله *)
| RH_Mu3tall_Ajwaf   (* معتل أجوف: و/ي في وسطه *)
| RH_Mu3tall_Naqis   (* معتل ناقص: و/ي في آخره *)
| RH_Mu3tall_Lafif   (* معتل لفيف: حرفا علة *)
| RH_Other.

(************************************************************)
(*           الجزء الثالث: الأوزان الصرفية                   *)
(*           Part 3: Morphological Patterns                  *)
(************************************************************)

(** ========== 3.1 أبواب الفعل الثلاثي المجرد (6 أبواب) ========== *)

Inductive ThulathiBab :=
| Bab_fa3ala_yaf3ulu    (* فَعَلَ يَفْعُلُ: نَصَرَ يَنْصُرُ *)
| Bab_fa3ala_yaf3ilu    (* فَعَلَ يَفْعِلُ: ضَرَبَ يَضْرِبُ *)
| Bab_fa3ala_yaf3alu    (* فَعَلَ يَفْعَلُ: فَتَحَ يَفْتَحُ *)
| Bab_fa3ila_yaf3alu    (* فَعِلَ يَفْعَلُ: عَلِمَ يَعْلَمُ *)
| Bab_fa3ila_yaf3ilu    (* فَعِلَ يَفْعِلُ: حَسِبَ يَحْسِبُ *)
| Bab_fa3ula_yaf3ulu.   (* فَعُلَ يَفْعُلُ: كَرُمَ يَكْرُمُ *)

(** ========== 3.2 أوزان الفعل الثلاثي المزيد (12 وزناً) ========== *)

Inductive ThulathiMazeed :=
(* مزيد بحرف *)
| TM_af3ala             (* أَفْعَلَ: أَكْرَمَ *)
| TM_fa33ala            (* فَعَّلَ: كَرَّمَ *)
| TM_faa3ala            (* فَاعَلَ: قَاتَلَ *)
(* مزيد بحرفين *)
| TM_infa3ala           (* انْفَعَلَ: انْكَسَرَ *)
| TM_ifta3ala           (* افْتَعَلَ: اجْتَمَعَ *)
| TM_if3alla            (* افْعَلَّ: احْمَرَّ *)
| TM_tafa33ala          (* تَفَعَّلَ: تَكَلَّمَ *)
| TM_tafaa3ala          (* تَفَاعَلَ: تَقَاتَلَ *)
(* مزيد بثلاثة أحرف *)
| TM_istaf3ala          (* اسْتَفْعَلَ: اسْتَغْفَرَ *)
| TM_if3aw3ala          (* افْعَوْعَلَ: اعْشَوْشَبَ *)
| TM_if3awwala          (* افْعَوَّلَ: اجْلَوَّذَ *)
| TM_if3aalla.          (* افْعَالَّ: اصْفَارَّ *)

(** ========== 3.3 أوزان الفعل الرباعي (7 أوزان) ========== *)

Inductive RubaiWazn :=
| RW_fa3lala            (* فَعْلَلَ: دَحْرَجَ *)
| RW_tafa3lala          (* تَفَعْلَلَ: تَدَحْرَجَ *)
| RW_if3anlala          (* افْعَنْلَلَ: احْرَنْجَمَ *)
| RW_if3alalla          (* افْعَلَلَّ: اطْمَأَنَّ *)
| RW_fa3wala            (* فَعْوَلَ: جَهْوَرَ *)
| RW_fa3yala            (* فَعْيَلَ: بَيْطَرَ *)
| RW_faw3ala.           (* فَوْعَلَ: حَوْقَلَ *)

(** ========== 3.4 المشتقات (Derivations) ========== *)

Inductive Mushtaq :=
(* المشتقات الأساسية *)
| MS_Masdar             (* المصدر *)
| MS_IsmFa3il           (* اسم الفاعل *)
| MS_IsmMaf3ul          (* اسم المفعول *)
| MS_SifaMushabbaha     (* الصفة المشبهة *)
| MS_IsmTafdil          (* اسم التفضيل: أَفْعَل *)
| MS_IsmMakan           (* اسم المكان: مَفْعَل *)
| MS_IsmZaman           (* اسم الزمان: مَفْعَل *)
| MS_IsmAla             (* اسم الآلة: مِفْعَل/مِفْعَلة/مِفْعَال *)
| MS_IsmHay2a           (* اسم الهيئة: فِعْلة *)
| MS_IsmMarra           (* اسم المرة: فَعْلة *)
| MS_Masdar_Mimi        (* المصدر الميمي *)
| MS_Masdar_Sinai.      (* المصدر الصناعي *)

(** ========== 3.5 أوزان المصادر ========== *)

Inductive MasdarWazn :=
(* مصادر الثلاثي - سماعية *)
| MW_fa3l                (* فَعْل: ضَرْب *)
| MW_fu3l                (* فُعْل: شُغْل *)
| MW_fi3l                (* فِعْل: عِلْم *)
| MW_fa3al               (* فَعَل: طَلَب *)
| MW_fa3la               (* فَعْلة: رَحْمة *)
| MW_fi3la               (* فِعْلة: خِدْمة *)
| MW_fu3la               (* فُعْلة: غُرْبة *)
| MW_fa3aal              (* فَعَال: سَلام *)
| MW_fi3aal              (* فِعَال: كِتَاب *)
| MW_fu3aal              (* فُعَال: سُعَال *)
| MW_fu3uul              (* فُعُول: دُخُول *)
| MW_fa3iil              (* فَعِيل: صَرِيخ *)
| MW_fa3aala             (* فَعَالة: بَلاغة *)
| MW_fu3uula             (* فُعُولة: أُبُوَّة *)
(* مصادر المزيد - قياسية *)
| MW_if3aal              (* إفْعَال: إكْرَام *)
| MW_taf3iil             (* تَفْعِيل: تَكْرِيم *)
| MW_mufaa3ala           (* مُفَاعَلة: مُقَاتَلة *)
| MW_infi3aal            (* انْفِعَال: انْكِسَار *)
| MW_ifti3aal            (* افْتِعَال: اجْتِمَاع *)
| MW_if3ilaal            (* افْعِلال: احْمِرَار *)
| MW_tafa33ul            (* تَفَعُّل: تَكَلُّم *)
| MW_tafaa3ul            (* تَفَاعُل: تَقَاتُل *)
| MW_istif3aal.          (* اسْتِفْعَال: اسْتِغْفَار *)

(************************************************************)
(*           الجزء الرابع: الضمائر                           *)
(*           Part 4: Pronouns                                *)
(************************************************************)

Inductive DamirType :=
| DT_Munfasil_Raf3       (* ضمير منفصل في محل رفع *)
| DT_Munfasil_Nasb       (* ضمير منفصل في محل نصب *)
| DT_Muttasil_Raf3       (* ضمير متصل في محل رفع *)
| DT_Muttasil_Nasb       (* ضمير متصل في محل نصب *)
| DT_Muttasil_Jarr       (* ضمير متصل في محل جر *)
| DT_Mustatir.           (* ضمير مستتر *)

Inductive Person := P_First | P_Second | P_Third.
Inductive Gender := G_Masculine | G_Feminine.
Inductive Number := N_Singular | N_Dual | N_Plural.

Record Damir := {
  dam_type   : DamirType;
  dam_person : Person;
  dam_gender : Gender;
  dam_number : Number
}.

(* الضمائر المنفصلة في محل رفع *)
Definition damir_ana   := {| dam_type := DT_Munfasil_Raf3; dam_person := P_First; dam_gender := G_Masculine; dam_number := N_Singular |}.
Definition damir_nahnu := {| dam_type := DT_Munfasil_Raf3; dam_person := P_First; dam_gender := G_Masculine; dam_number := N_Plural |}.
Definition damir_anta  := {| dam_type := DT_Munfasil_Raf3; dam_person := P_Second; dam_gender := G_Masculine; dam_number := N_Singular |}.
Definition damir_anti  := {| dam_type := DT_Munfasil_Raf3; dam_person := P_Second; dam_gender := G_Feminine; dam_number := N_Singular |}.
Definition damir_huwa  := {| dam_type := DT_Munfasil_Raf3; dam_person := P_Third; dam_gender := G_Masculine; dam_number := N_Singular |}.
Definition damir_hiya  := {| dam_type := DT_Munfasil_Raf3; dam_person := P_Third; dam_gender := G_Feminine; dam_number := N_Singular |}.

(************************************************************)
(*           الجزء الخامس: الأدوات والحروف                   *)
(*           Part 5: Particles and Tools                     *)
(************************************************************)

(** ========== 5.1 حروف الجر ========== *)

Inductive HarfJarr :=
| HJ_Min       (* من *)
| HJ_Ila       (* إلى *)
| HJ_An        (* عن *)
| HJ_Ala       (* على *)
| HJ_Fi        (* في *)
| HJ_Ba        (* بـ *)
| HJ_Lam       (* لـ *)
| HJ_Kaf       (* كـ *)
| HJ_Waw       (* واو القسم *)
| HJ_Ta        (* تاء القسم *)
| HJ_Mundhu    (* منذ *)
| HJ_Rubba     (* ربّ *)
| HJ_Hatta     (* حتى *)
| HJ_Khala     (* خلا *)
| HJ_Hashaa    (* حاشا *)
| HJ_Ada.      (* عدا *)

(** ========== 5.2 حروف النصب ========== *)

Inductive HarfNasb :=
| HN_An        (* أنْ *)
| HN_Lan       (* لن *)
| HN_Idhan     (* إذن *)
| HN_Kay       (* كي *)
| HN_LamKay    (* لام كي *)
| HN_LamJuhud  (* لام الجحود *)
| HN_Hatta     (* حتى *)
| HN_Fa_Sababiyya. (* فاء السببية *)

(** ========== 5.3 حروف الجزم ========== *)

Inductive HarfJazm :=
| HJZ_Lam      (* لم *)
| HJZ_Lamma    (* لمّا *)
| HJZ_LamAmr   (* لام الأمر *)
| HJZ_La_Nahiya. (* لا الناهية *)

(** ========== 5.4 أدوات الاستفهام ========== *)

Inductive AdatIstifham :=
| AI_Hamza     (* أ *)
| AI_Hal       (* هل *)
| AI_Ma        (* ما *)
| AI_Man       (* مَن *)
| AI_Mata      (* متى *)
| AI_Ayna      (* أين *)
| AI_Kayfa     (* كيف *)
| AI_Kam       (* كم *)
| AI_Ayyu      (* أيّ *)
| AI_Anna      (* أنّى *)
| AI_Limadha   (* لماذا *)
| AI_Ayyaan.   (* أيّان *)

(** ========== 5.5 أدوات الشرط ========== *)

Inductive AdatShart :=
| AS_In        (* إن *)
| AS_Idha      (* إذا *)
| AS_Man       (* مَن *)
| AS_Ma        (* ما *)
| AS_Mahma     (* مهما *)
| AS_Mata      (* متى *)
| AS_Ayna      (* أين *)
| AS_Ayyama    (* أيّما *)
| AS_Haythuma  (* حيثما *)
| AS_Kayf      (* كيفما *)
| AS_Law       (* لو *)
| AS_Lawla.    (* لولا *)

(** ========== 5.6 حروف العطف ========== *)

Inductive HarfAtf :=
| HA_Waw       (* و *)
| HA_Fa        (* ف *)
| HA_Thumma    (* ثمّ *)
| HA_Aw        (* أو *)
| HA_Am        (* أم *)
| HA_Bal       (* بل *)
| HA_Lakin     (* لكن *)
| HA_La        (* لا *)
| HA_Hatta.    (* حتى *)

(** ========== 5.7 النواسخ ========== *)

Inductive Nasikh :=
(* كان وأخواتها *)
| NK_Kaana     (* كان *)
| NK_Asbaha    (* أصبح *)
| NK_Amsa      (* أمسى *)
| NK_Adhha     (* أضحى *)
| NK_Dhalla    (* ظلّ *)
| NK_Bata      (* بات *)
| NK_Saara     (* صار *)
| NK_Laysa     (* ليس *)
| NK_Mazala    (* ما زال *)
| NK_Mabariha  (* ما برح *)
| NK_Mainfakka (* ما انفكّ *)
| NK_Mafati2a  (* ما فتئ *)
| NK_Madaama   (* ما دام *)
(* إنّ وأخواتها *)
| NK_Inna      (* إنّ *)
| NK_Anna      (* أنّ *)
| NK_Kaanna    (* كأنّ *)
| NK_Lakinna   (* لكنّ *)
| NK_Layta     (* ليت *)
| NK_La3alla   (* لعلّ *)
(* ظنّ وأخواتها *)
| NK_Dhanna    (* ظنّ *)
| NK_Hasiba    (* حسب *)
| NK_Khala     (* خال *)
| NK_Za3ama    (* زعم *)
| NK_Ra2a      (* رأى *)
| NK_3alima    (* علم *)
| NK_Wajada.   (* وجد *)

(************************************************************)
(*           الجزء السادس: الإعراب                           *)
(*           Part 6: I3rab (Case System)                     *)
(************************************************************)

Inductive I3rabCase :=
| I3_Raf3      (* رفع *)
| I3_Nasb      (* نصب *)
| I3_Jarr      (* جر *)
| I3_Jazm.     (* جزم *)

Inductive I3rabSign :=
| IS_Damma     (* ضمة *)
| IS_Fatha     (* فتحة *)
| IS_Kasra     (* كسرة *)
| IS_Sukun     (* سكون *)
| IS_Waw       (* واو *)
| IS_Alif      (* ألف *)
| IS_Ya        (* ياء *)
| IS_Nun       (* ثبوت النون *)
| IS_HadhfNun. (* حذف النون *)

Inductive I3rabType :=
| IT_Lafdhiy   (* إعراب لفظي: ظاهر *)
| IT_Taqdiri   (* إعراب تقديري *)
| IT_Mahalli.  (* إعراب محلي *)

Record I3rabProfile := {
  i3_case : I3rabCase;
  i3_sign : I3rabSign;
  i3_type : I3rabType
}.

(************************************************************)
(*           الجزء السابع: البناء اللغوي الكامل              *)
(*           Part 7: Complete Linguistic Structure           *)
(************************************************************)

(** ========== 7.1 المفردة ========== *)

Inductive WordClass :=
| WC_Ism       (* اسم *)
| WC_Fi3l      (* فعل *)
| WC_Harf.     (* حرف *)

Inductive Tense :=
| T_Madi       (* ماضي *)
| T_Mudari3    (* مضارع *)
| T_Amr.       (* أمر *)

Inductive Voice :=
| V_Ma3lum     (* معلوم *)
| V_Majhul.    (* مجهول *)

Record Mufrada := {
  muf_root     : RootC2Layer;
  muf_class    : WordClass;
  muf_mushtaq  : option Mushtaq;
  muf_tense    : option Tense;
  muf_voice    : option Voice;
  muf_gender   : Gender;
  muf_number   : Number;
  muf_person   : option Person;
  muf_i3rab    : option I3rabProfile;
  muf_extras   : list FunctionalElement
}.

(** ========== 7.2 الوظائف النحوية ========== *)

Inductive NahwRole :=
(* مرفوعات *)
| NR_Fa3il          (* فاعل *)
| NR_Na2ibFa3il     (* نائب فاعل *)
| NR_Mubtada        (* مبتدأ *)
| NR_Khabar         (* خبر *)
| NR_IsmKana        (* اسم كان *)
| NR_KhabarInna     (* خبر إنّ *)
| NR_Tabi3Marfu3    (* تابع مرفوع *)
(* منصوبات *)
| NR_Maf3ulBih      (* مفعول به *)
| NR_Maf3ulMutlaq   (* مفعول مطلق *)
| NR_Maf3ulLah      (* مفعول لأجله *)
| NR_Maf3ulFih      (* مفعول فيه: ظرف *)
| NR_Maf3ulMa3ah    (* مفعول معه *)
| NR_Hal            (* حال *)
| NR_Tamyeez        (* تمييز *)
| NR_Istithna       (* مستثنى *)
| NR_Munada         (* منادى *)
| NR_KhabarKana     (* خبر كان *)
| NR_IsmInna        (* اسم إنّ *)
| NR_Tabi3Mansub    (* تابع منصوب *)
(* مجرورات *)
| NR_MajrurHarf     (* مجرور بحرف *)
| NR_MudafIlayh     (* مضاف إليه *)
| NR_Tabi3Majrur    (* تابع مجرور *)
(* التوابع *)
| NR_Na3t           (* نعت/صفة *)
| NR_Tawkid         (* توكيد *)
| NR_Atf            (* عطف *)
| NR_Badal          (* بدل *)
| NR_Other.

(** ========== 7.3 الجملة ========== *)

Inductive JumlaType :=
| JT_Ismiyya       (* جملة اسمية *)
| JT_Fi3liyya      (* جملة فعلية *)
| JT_Shibh.        (* شبه جملة *)

Record JumlaElement := {
  je_word  : Mufrada;
  je_role  : NahwRole
}.

Record Jumla := {
  jum_type     : JumlaType;
  jum_elements : list JumlaElement;
  jum_nasikhh  : option Nasikh
}.

(** ========== 7.4 الأسلوب ========== *)

Inductive UslubCategory :=
(* الخبر *)
| US_Khabar_Ibtida2i   (* خبر ابتدائي *)
| US_Khabar_Talabi     (* خبر طلبي *)
| US_Khabar_Inkari     (* خبر إنكاري *)
(* الإنشاء الطلبي *)
| US_Amr               (* أمر *)
| US_Nahy              (* نهي *)
| US_Istifham          (* استفهام *)
| US_Tamanni           (* تمنّي *)
| US_Nida              (* نداء *)
(* الإنشاء غير الطلبي *)
| US_Ta3ajjub          (* تعجب *)
| US_Madh              (* مدح *)
| US_Dhamm             (* ذم *)
| US_Qasam             (* قسم *)
| US_Rajaa             (* رجاء *)
| US_3aqd              (* عقد *)
(* أساليب أخرى *)
| US_Shart             (* شرط *)
| US_Istithna          (* استثناء *)
| US_Takhsis           (* تخصيص *)
| US_Hasr              (* حصر *)
| US_Ikhtiṣaṣ.         (* اختصاص *)

Definition is_truth_bearing (u : UslubCategory) : bool :=
  match u with
  | US_Khabar_Ibtida2i | US_Khabar_Talabi | US_Khabar_Inkari => true
  | _ => false
  end.

Record Muraqqab := {
  mur_jumla  : Jumla;
  mur_uslub  : UslubCategory
}.

(************************************************************)
(*           الجزء الثامن: دوال التوليد AGT                  *)
(*           Part 8: AGT Generation Functions                *)
(************************************************************)

(* توليد جذر ثلاثي *)
Definition make_root_3 (c1 c2 c3 : ArabicLetter) (role : C2Role) : RootC2Layer := {|
  root_c1 := Some c1;
  root_c2 := c2;
  root_c3 := Some c3;
  root_c4 := None;
  root_c5 := None;
  root_class := RC_Thulathi;
  root_c2role := role
|}.

(* توليد جذر رباعي *)
Definition make_root_4 (c1 c2 c3 c4 : ArabicLetter) (role : C2Role) : RootC2Layer := {|
  root_c1 := Some c1;
  root_c2 := c2;
  root_c3 := Some c3;
  root_c4 := Some c4;
  root_c5 := None;
  root_class := RC_Rubai;
  root_c2role := role
|}.

(* توليد فعل *)
Definition AGT_generate_fi3l
           (root : RootC2Layer)
           (tense : Tense)
           (voice : Voice)
           (gen : Gender)
           (num : Number)
           (pers : Person) : Mufrada := {|
  muf_root := root;
  muf_class := WC_Fi3l;
  muf_mushtaq := None;
  muf_tense := Some tense;
  muf_voice := Some voice;
  muf_gender := gen;
  muf_number := num;
  muf_person := Some pers;
  muf_i3rab := None;
  muf_extras := []
|}.

(* توليد اسم فاعل *)
Definition AGT_generate_ism_fa3il
           (root : RootC2Layer)
           (gen : Gender)
           (num : Number)
           (i3rab : I3rabProfile) : Mufrada := {|
  muf_root := root;
  muf_class := WC_Ism;
  muf_mushtaq := Some MS_IsmFa3il;
  muf_tense := None;
  muf_voice := None;
  muf_gender := gen;
  muf_number := num;
  muf_person := None;
  muf_i3rab := Some i3rab;
  muf_extras := []
|}.

(* توليد مصدر *)
Definition AGT_generate_masdar
           (root : RootC2Layer)
           (i3rab : I3rabProfile) : Mufrada := {|
  muf_root := root;
  muf_class := WC_Ism;
  muf_mushtaq := Some MS_Masdar;
  muf_tense := None;
  muf_voice := None;
  muf_gender := G_Masculine;
  muf_number := N_Singular;
  muf_person := None;
  muf_i3rab := Some i3rab;
  muf_extras := []
|}.

(* توليد جملة فعلية *)
Definition AGT_generate_jumla_fi3liyya
           (fi3l : Mufrada)
           (fa3il : Mufrada) : Jumla := {|
  jum_type := JT_Fi3liyya;
  jum_elements := [
    {| je_word := fi3l; je_role := NR_Other |};
    {| je_word := fa3il; je_role := NR_Fa3il |}
  ];
  jum_nasikhh := None
|}.

(* توليد جملة اسمية *)
Definition AGT_generate_jumla_ismiyya
           (mubtada : Mufrada)
           (khabar : Mufrada) : Jumla := {|
  jum_type := JT_Ismiyya;
  jum_elements := [
    {| je_word := mubtada; je_role := NR_Mubtada |};
    {| je_word := khabar; je_role := NR_Khabar |}
  ];
  jum_nasikhh := None
|}.

(* توليد مركب *)
Definition AGT_generate_muraqqab
           (j : Jumla)
           (u : UslubCategory) : Muraqqab := {|
  mur_jumla := j;
  mur_uslub := u
|}.

(************************************************************)
(*           الجزء التاسع: اللمّات والإثباتات                 *)
(*           Part 9: Lemmas and Proofs                       *)
(************************************************************)

(* لمّا 1: كل مفردة لها جذر *)
Lemma AGT_word_has_root : forall (m : Mufrada),
  exists (r : RootC2Layer), m.(muf_root) = r.
Proof.
  intros m. exists (muf_root m). reflexivity.
Qed.

(* لمّا 2: C2 هو المركز الدلالي *)
Lemma AGT_c2_is_semantic_center : forall (m : Mufrada),
  exists (c2 : ArabicLetter) (role : C2Role),
    m.(muf_root).(root_c2) = c2 /\ m.(muf_root).(root_c2role) = role.
Proof.
  intros m.
  exists (root_c2 (muf_root m)).
  exists (root_c2role (muf_root m)).
  split; reflexivity.
Qed.

(* لمّا 3: سلسلة التوليد الكاملة *)
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

(* لمّا 4: الخبر يحتمل الصدق والكذب *)
Lemma khabar_is_truth_apt : forall (j : Jumla),
  is_truth_bearing (mur_uslub (AGT_generate_muraqqab j US_Khabar_Ibtida2i)) = true.
Proof.
  intros j. simpl. reflexivity.
Qed.

(* لمّا 5: الإنشاء لا يحتمل الصدق والكذب *)
Lemma insha_is_not_truth_apt : forall (j : Jumla),
  is_truth_bearing (mur_uslub (AGT_generate_muraqqab j US_Amr)) = false.
Proof.
  intros j. simpl. reflexivity.
Qed.

(************************************************************)
(*           الجزء العاشر: أمثلة تطبيقية                      *)
(*           Part 10: Practical Examples                     *)
(************************************************************)

(* جذر ك-ت-ب *)
Definition root_ktb := make_root_3 L_Kaf L_Ta L_Ba C2_Eventive.

(* جذر ق-ر-أ *)
Definition root_qr2 := make_root_3 L_Qaf L_Ra L_Hamza C2_Eventive.

(* جذر ع-ل-م *)
Definition root_3lm := make_root_3 L_Ayn L_Lam L_Mim C2_Stative.

(* جذر د-ح-ر-ج *)
Definition root_dhrj := make_root_4 L_Dal L_Ha L_Ra L_Jim C2_Eventive.

(* الإعراب المرفوع *)
Definition i3rab_marfu3 := {| i3_case := I3_Raf3; i3_sign := IS_Damma; i3_type := IT_Lafdhiy |}.

(* كَتَبَ - فعل ماضي *)
Definition kataba := AGT_generate_fi3l root_ktb T_Madi V_Ma3lum G_Masculine N_Singular P_Third.

(* يَكْتُبُ - فعل مضارع *)
Definition yaktubu := AGT_generate_fi3l root_ktb T_Mudari3 V_Ma3lum G_Masculine N_Singular P_Third.

(* كَاتِب - اسم فاعل *)
Definition kaatib := AGT_generate_ism_fa3il root_ktb G_Masculine N_Singular i3rab_marfu3.

(* كِتَابَة - مصدر *)
Definition kitaaba := AGT_generate_masdar root_ktb i3rab_marfu3.

(* مثال: "كَتَبَ الطَّالِبُ الدَّرْسَ" *)
Definition root_tlb := make_root_3 L_Tah L_Lam L_Ba C2_Agentive.
Definition taalib := AGT_generate_ism_fa3il root_tlb G_Masculine N_Singular i3rab_marfu3.

Definition jumla_example := AGT_generate_jumla_fi3liyya kataba taalib.
Definition muraqqab_example := AGT_generate_muraqqab jumla_example US_Khabar_Ibtida2i.

(* إثبات أن المثال خبر يحتمل الصدق والكذب *)
Lemma example_is_khabar :
  is_truth_bearing (mur_uslub muraqqab_example) = true.
Proof.
  simpl. reflexivity.
Qed.

End AGT_Complete.
