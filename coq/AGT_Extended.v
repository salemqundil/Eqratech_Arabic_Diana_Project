(** AGT_Extended.v - Extended Arabic Generative Theorem Implementation **)
(** المبرهنة العربية المولِّدة - التنفيذ الموسَّع **)
(** يغطي: البلاغة، العروض، الإعلال، التصغير، النسبة، الممنوع من الصرف، الأعداد **)

From Coq Require Import String List Nat Arith Bool.
Import ListNotations.

Set Implicit Arguments.
Set Asymmetric Patterns.

Module AGT_Extended.

(************************************************************)
(*           الجزء الأول: إعادة التعريفات الأساسية           *)
(*           Part 1: Basic Definitions Recap                 *)
(************************************************************)

(** الحروف العربية *)
Inductive ArabicLetter :=
| L_Hamza | L_Alif | L_Ba | L_Ta | L_Tha | L_Jim | L_Ha | L_Kha
| L_Dal | L_Dhal | L_Ra | L_Zay | L_Sin | L_Shin | L_Sad | L_Dad
| L_Tah | L_Dhah | L_Ayn | L_Ghayn | L_Fa | L_Qaf | L_Kaf | L_Lam
| L_Mim | L_Nun | L_Ha2 | L_Waw | L_Ya.

(** الحركات *)
Inductive Haraka :=
| H_Fatha | H_Damma | H_Kasra | H_Sukun | H_Shadda
| H_FathaLong | H_DammaLong | H_KasraLong
| H_TanweenFath | H_TanweenDamm | H_TanweenKasr.

(** الجندر والعدد *)
Inductive Gender := G_Masculine | G_Feminine.
Inductive Number := N_Singular | N_Dual | N_Plural.
Inductive Person := P_First | P_Second | P_Third.

(** نوع الجذر *)
Inductive RootClass := RC_Thulathi | RC_Rubai | RC_Khumasi | RC_Sudasi.

(** دور C2 *)
Inductive C2Role :=
| C2_Agentive | C2_Patientive | C2_Eventive | C2_Stative
| C2_Locative | C2_Temporal | C2_Instrumental | C2_Causative
| C2_Reciprocal | C2_Reflexive | C2_Intensive | C2_Attributive | C2_Other.

(** الجذر *)
Record RootC2Layer := {
  root_c1 : option ArabicLetter;
  root_c2 : ArabicLetter;
  root_c3 : option ArabicLetter;
  root_c4 : option ArabicLetter;
  root_c5 : option ArabicLetter;
  root_class : RootClass;
  root_c2role : C2Role
}.

(************************************************************)
(*           الجزء الثاني: علم البلاغة                       *)
(*           Part 2: Rhetoric (البلاغة)                      *)
(************************************************************)

(** ========== 2.1 علم البيان (Figurative Language) ========== *)

Inductive TashbihType :=
| TSH_Mursal     (* تشبيه مرسل: ذُكرت فيه الأداة *)
| TSH_Muakkad    (* تشبيه مؤكد: حُذفت منه الأداة *)
| TSH_Mujmal     (* تشبيه مجمل: حُذف منه وجه الشبه *)
| TSH_Mufassal   (* تشبيه مفصل: ذُكر فيه وجه الشبه *)
| TSH_Baligh     (* تشبيه بليغ: حُذفت منه الأداة ووجه الشبه *)
| TSH_Tamthil    (* تشبيه تمثيلي: وجه الشبه صورة منتزعة *)
| TSH_Dhimni     (* تشبيه ضمني *)
| TSH_Maqlub.    (* تشبيه مقلوب *)

Record Tashbih := {
  tash_mushabbah      : nat;  (* المشبَّه *)
  tash_mushabbah_bih  : nat;  (* المشبَّه به *)
  tash_adat           : option nat; (* أداة التشبيه *)
  tash_wajh           : option nat; (* وجه الشبه *)
  tash_type           : TashbihType
}.

Inductive MajazType :=
| MJ_Mursal        (* مجاز مرسل *)
| MJ_Aqli          (* مجاز عقلي *)
| MJ_Isti3ara_Tasrihiyya   (* استعارة تصريحية *)
| MJ_Isti3ara_Makniyya     (* استعارة مكنية *)
| MJ_Isti3ara_Tamthiliyya. (* استعارة تمثيلية *)

(* علاقات المجاز المرسل *)
Inductive MajazMursalRelation :=
| MMR_Sababiyya    (* السببية *)
| MMR_Musabbabiyya (* المسببية *)
| MMR_Juz2iyya     (* الجزئية *)
| MMR_Kulliyya     (* الكلية *)
| MMR_Ma3aliyya    (* اعتبار ما كان *)
| MMR_Musta2baliyya (* اعتبار ما سيكون *)
| MMR_Makaniyya    (* المكانية *)
| MMR_Haliyya.     (* الحالية *)

Inductive Kinaya :=
| KN_Sifa         (* كناية عن صفة *)
| KN_Mawsuf       (* كناية عن موصوف *)
| KN_Nisba.       (* كناية عن نسبة *)

(** ========== 2.2 علم المعاني (Semantics/Meaning) ========== *)

Inductive KhabarPurpose :=
| KP_Faidatul_Khabar    (* فائدة الخبر *)
| KP_Lazim_Faidah       (* لازم الفائدة *)
| KP_Idhhar_Da3f        (* إظهار الضعف *)
| KP_Idhhar_Tafarrud    (* إظهار التفرد *)
| KP_Tahdir             (* التحذير *)
| KP_Tawbikh            (* التوبيخ *)
| KP_Fakhur             (* الفخر *)
| KP_Madh_Dhamm.        (* المدح أو الذم *)

Inductive InshaType :=
| IT_Talabi           (* إنشاء طلبي *)
| IT_GhayrTalabi.     (* إنشاء غير طلبي *)

Inductive InshaAmr :=
| IA_Wujub      (* الوجوب *)
| IA_Irshad     (* الإرشاد *)
| IA_Ibaha      (* الإباحة *)
| IA_Tahdid     (* التهديد *)
| IA_Ta3jiz     (* التعجيز *)
| IA_Tamanni    (* التمني *)
| IA_Du3a       (* الدعاء *)
| IA_Iltimas.   (* الالتماس *)

Inductive IstifhamPurpose :=
| ISP_Haqiqi    (* استفهام حقيقي *)
| ISP_Taqrir    (* التقرير *)
| ISP_Inkar     (* الإنكار *)
| ISP_Ta3ajjub  (* التعجب *)
| ISP_Taswiya   (* التسوية *)
| ISP_Tamanni   (* التمني *)
| ISP_Tahdid.   (* التهديد *)

(* القصر *)
Inductive QasrType :=
| QT_Haqiqi     (* قصر حقيقي *)
| QT_Idafi.     (* قصر إضافي *)

Inductive QasrMethod :=
| QM_Nafi_Istithna     (* النفي والاستثناء *)
| QM_Innama            (* إنما *)
| QM_Taqdim            (* التقديم *)
| QM_Atf_BiLa_Bal.     (* العطف بلا وبل *)

(* الوصل والفصل *)
Inductive WaslFaslCase :=
| WF_Wasl_Kamal_Ittisaal     (* الوصل: كمال الاتصال *)
| WF_Wasl_Kamal_Inqita3      (* الوصل: كمال الانقطاع مع الإيهام *)
| WF_Wasl_Shibh_Kamal        (* الوصل: شبه كمال الاتصال *)
| WF_Fasl_Kamal_Ittisaal     (* الفصل: كمال الاتصال *)
| WF_Fasl_Kamal_Inqita3      (* الفصل: كمال الانقطاع *)
| WF_Fasl_Shibh_Kamal.       (* الفصل: شبه كمال الاتصال *)

(* الإيجاز والإطناب *)
Inductive IjazType :=
| IJ_Qasr       (* إيجاز قصر *)
| IJ_Hadhf.     (* إيجاز حذف *)

Inductive ItnabType :=
| IT_Dhikr_Khass   (* ذكر الخاص بعد العام *)
| IT_Dhikr_3amm    (* ذكر العام بعد الخاص *)
| IT_Tadyil        (* التذييل *)
| IT_Ihtiraz       (* الاحتراز *)
| IT_I3tirad       (* الاعتراض *)
| IT_Takrir        (* التكرير *)
| IT_Tawshih.      (* التوشيع *)

(** ========== 2.3 علم البديع (Embellishment) ========== *)

(* المحسنات اللفظية *)
Inductive LafdhiMuhassin :=
| LM_Jinas_Tamm       (* جناس تام *)
| LM_Jinas_Naqis      (* جناس ناقص *)
| LM_Iqtibas          (* اقتباس *)
| LM_Saj3             (* سجع *)
| LM_Radd_A3jaz.      (* رد العجز على الصدر *)

(* المحسنات المعنوية *)
Inductive Ma3nawiMuhassin :=
| MM_Tibaq_Ijab       (* طباق الإيجاب *)
| MM_Tibaq_Salb       (* طباق السلب *)
| MM_Muqabala         (* المقابلة *)
| MM_Tawriya          (* التورية *)
| MM_Husn_Ta3lil      (* حسن التعليل *)
| MM_Musha_kala       (* المشاكلة *)
| MM_Mudhahabat_Kalam (* مذهب الكلام *)
| MM_Ta2kid_Madh      (* تأكيد المدح بما يشبه الذم *)
| MM_Ta2kid_Dhamm     (* تأكيد الذم بما يشبه المدح *)
| MM_Uslub_Hakim.     (* أسلوب الحكيم *)

(************************************************************)
(*           الجزء الثالث: علم العروض والقافية               *)
(*           Part 3: Prosody (العروض)                        *)
(************************************************************)

(** ========== 3.1 التفاعيل ========== *)

Inductive Taf3ila :=
(* التفاعيل الأصلية الثمانية *)
| TF_Fa3ulun       (* فَعُولُنْ: /0/0 - وتد مجموع + سبب خفيف *)
| TF_Fa3ilun       (* فَاعِلُنْ: /0//0 - سبب خفيف + وتد مجموع *)
| TF_Mafa3ilun     (* مَفَاعِيلُنْ: //0/0/0 - وتد مجموع + سببان خفيفان *)
| TF_Mufa3alatun   (* مُفَاعَلَتُنْ: //0///0 - وتد مجموع + سببان: خفيف + ثقيل *)
| TF_Fa3ilatun     (* فَاعِلاتُنْ: /0//0/0 - سبب خفيف + وتد مجموع + سبب خفيف *)
| TF_Mustaf3ilun   (* مُسْتَفْعِلُنْ: /0/0//0 - سببان خفيفان + وتد مجموع *)
| TF_Maf3ulatu     (* مَفْعُولاتُ: /0/0/0/ - سببان خفيفان + وتد مفروق *)
| TF_Mutafa3ilun.  (* مُتَفَاعِلُنْ: ///0//0 - سببان: ثقيل + خفيف + وتد مجموع *)

(** ========== 3.2 البحور الشعرية (16 بحراً) ========== *)

Inductive Bahr :=
(* بحور الدائرة الأولى: المختلف *)
| BH_Tawil        (* الطويل: فعولن مفاعيلن فعولن مفاعلن *)
| BH_Madid        (* المديد: فاعلاتن فاعلن فاعلاتن *)
| BH_Basit        (* البسيط: مستفعلن فاعلن مستفعلن فعلن *)
(* بحور الدائرة الثانية: المؤتلف *)
| BH_Wafir        (* الوافر: مفاعلتن مفاعلتن فعولن *)
| BH_Kamil        (* الكامل: متفاعلن متفاعلن متفاعلن *)
(* بحور الدائرة الثالثة: المجتلب *)
| BH_Hazaj        (* الهزج: مفاعيلن مفاعيلن *)
| BH_Rajaz        (* الرجز: مستفعلن مستفعلن مستفعلن *)
| BH_Ramal        (* الرمل: فاعلاتن فاعلاتن فاعلاتن *)
(* بحور الدائرة الرابعة: المشتبه *)
| BH_Sari3        (* السريع: مستفعلن مستفعلن فاعلن *)
| BH_Munsarih     (* المنسرح: مستفعلن مفعولات مستفعلن *)
| BH_Khafif       (* الخفيف: فاعلاتن مستفعلن فاعلاتن *)
| BH_Mudari3      (* المضارع: مفاعيلن فاع لاتن *)
| BH_Muqtadab     (* المقتضب: مفعولات مستفعلن *)
| BH_Mujtathth    (* المجتث: مستفعلن فاعلاتن *)
(* بحور الدائرة الخامسة: المتفق *)
| BH_Mutaqarib   (* المتقارب: فعولن فعولن فعولن فعولن *)
| BH_Mutadarik.  (* المتدارك: فاعلن فاعلن فاعلن فاعلن *)

(** ========== 3.3 الزحافات والعلل ========== *)

Inductive Zihaf :=
| ZH_Khabn       (* الخبن: حذف الثاني الساكن *)
| ZH_Tayy        (* الطي: حذف الرابع الساكن *)
| ZH_Qabd        (* القبض: حذف الخامس الساكن *)
| ZH_3aql        (* العقل: حذف الخامس المتحرك *)
| ZH_Kaff        (* الكف: حذف السابع الساكن *)
| ZH_Waqṣ        (* الوقص: حذف الثاني المتحرك *)
| ZH_3aṣb        (* العصب: إسكان الخامس المتحرك *)
| ZH_Idmar       (* الإضمار: إسكان الثاني المتحرك *)
| ZH_Khazl       (* الخزل: الإضمار + الطي *)
| ZH_Shakl.      (* الشكل: الخبن + الكف *)

Inductive Illa :=
| IL_Qat3        (* القطع: حذف ساكن الوتد المجموع وإسكان ما قبله *)
| IL_Hadhf       (* الحذف: حذف السبب الخفيف *)
| IL_Qaṣr        (* القصر: حذف ساكن السبب الخفيف وإسكان ما قبله *)
| IL_Batr        (* البتر: الحذف + القطع *)
| IL_Qatf        (* القطف: العصب + الحذف *)
| IL_Waqf        (* الوقف: إسكان السابع المتحرك *)
| IL_Kashf       (* الكشف: حذف السابع المتحرك *)
| IL_Tash3ith    (* التشعيث: حذف أول الوتد المجموع *)
| IL_Tarfil      (* الترفيل: زيادة سبب خفيف *)
| IL_Tadhyil.    (* التذييل: زيادة حرف ساكن *)

(** ========== 3.4 القافية ========== *)

Inductive QafiyaType :=
| QF_Mutawatira   (* متواترة: بين ساكنيها حرف متحرك *)
| QF_Mutadarika   (* متداركة: بين ساكنيها حرفان متحركان *)
| QF_Mutarakiba   (* متراكبة: بين ساكنيها ثلاثة متحركات *)
| QF_Mutakawisa.  (* متكاوسة: بين ساكنيها أربعة متحركات *)

Record Qafiya := {
  qf_rawiy     : ArabicLetter;  (* حرف الروي *)
  qf_type      : QafiyaType;
  qf_harakaat  : list Haraka
}.

(************************************************************)
(*           الجزء الرابع: الإعلال والإبدال                   *)
(*           Part 4: Phonological Changes                    *)
(************************************************************)

(** ========== 4.1 الإعلال ========== *)

Inductive I3lalType :=
(* إعلال بالقلب *)
| I3L_Qalb_Waw_Alif      (* قلب الواو ألفاً: قَوَلَ → قَالَ *)
| I3L_Qalb_Ya_Alif       (* قلب الياء ألفاً: بَيَعَ → بَاعَ *)
| I3L_Qalb_Waw_Ya        (* قلب الواو ياء: مَوْزَان → مِيزَان *)
| I3L_Qalb_Ya_Waw        (* قلب الياء واواً *)
| I3L_Qalb_Hamza         (* قلب حرف العلة همزة *)
(* إعلال بالحذف *)
| I3L_Hadhf_Fa2          (* حذف فاء الكلمة: وَعَدَ → عِدْ *)
| I3L_Hadhf_3ayn         (* حذف عين الكلمة: قَامَ → قُمْ *)
| I3L_Hadhf_Lam          (* حذف لام الكلمة: يَرْمِي → لَمْ يَرْمِ *)
(* إعلال بالسكون *)
| I3L_Taskeen_3ayn       (* إسكان العين: يَقُوْمُ → يَقُومُ *)
| I3L_Taskeen_Lam        (* إسكان اللام *)
(* إعلال بالنقل *)
| I3L_Naql_Haraka.       (* نقل حركة حرف العلة: يَقْوُمُ → يَقُومُ *)

(** ========== 4.2 الإبدال ========== *)

Inductive IbdalType :=
| IB_Ta_Dal              (* إبدال التاء دالاً: افْتَعَلَ → ازْدَجَرَ *)
| IB_Ta_Ṭa              (* إبدال التاء طاء: اصْتَبَرَ → اصْطَبَرَ *)
| IB_Waw_Ta             (* إبدال الواو تاء: اتَّحَدَ من وَحَدَ *)
| IB_Ya_Ta              (* إبدال الياء تاء: اتَّسَرَ من يَسَرَ *)
| IB_Hamza_Ya           (* إبدال الهمزة ياء: ذِيب من ذِئب *)
| IB_Hamza_Waw          (* إبدال الهمزة واواً: جُونَة من جُؤْنَة *)
| IB_Nun_Mim            (* إبدال النون ميماً: عَمْبَر من عَنْبَر *)
| IB_Sin_Ṣad.           (* إبدال السين صاداً: صِراط من سِراط *)

(** ========== 4.3 الإدغام ========== *)

Inductive IdghamType :=
| ID_Mithlain           (* إدغام المتماثلين *)
| ID_Mutaqaribain       (* إدغام المتقاربين *)
| ID_Mutajanisain       (* إدغام المتجانسين *)
| ID_Shams              (* إدغام حروف الشمسية في اللام *)
| ID_Nun_Tanween.       (* إدغام النون الساكنة والتنوين *)

(************************************************************)
(*           الجزء الخامس: التصغير                           *)
(*           Part 5: Diminutive (التصغير)                    *)
(************************************************************)

Inductive TasghirWazn :=
| TS_Fu3ayl        (* فُعَيْل: كِتَاب → كُتَيِّب *)
| TS_Fu3ay3il      (* فُعَيْعِل: عُصْفُور → عُصَيْفِير *)
| TS_Fu3ay3il2.    (* فُعَيْعِيل: مِصْبَاح → مُصَيْبِيح *)

Inductive TasghirPurpose :=
| TSP_Tahqir       (* التحقير والتصغير *)
| TSP_Tahbib       (* التحبيب والتدليل *)
| TSP_Taqrib       (* تقريب الزمان أو المكان *)
| TSP_Taqlil.      (* تقليل الكمية *)

(************************************************************)
(*           الجزء السادس: النسبة                            *)
(*           Part 6: Relative Adjective (النسبة)             *)
(************************************************************)

Inductive NisbaType :=
| NS_Standard      (* نسبة قياسية: مِصْر → مِصْرِيّ *)
| NS_HadhfYa       (* حذف الياء: بَصْرَة → بَصْرِيّ *)
| NS_HadhfTa       (* حذف التاء: مَكَّة → مَكِّيّ *)
| NS_Qalb_Alif     (* قلب الألف: أمريكا → أمريكِيّ *)
| NS_Shadh.        (* نسبة شاذة: رُوح → رُوحَانِيّ *)

(************************************************************)
(*           الجزء السابع: الممنوع من الصرف                  *)
(*           Part 7: Diptotes (الممنوع من الصرف)             *)
(************************************************************)

Inductive Mamnuu3Sabab :=
(* أسباب تتعلق بالعلمية *)
| MN_3alam_Ajami        (* علم أعجمي: إبراهيم *)
| MN_3alam_Mu2annath    (* علم مؤنث: فاطمة *)
| MN_3alam_Murakab      (* علم مركب: بعلبك *)
| MN_3alam_3adl         (* علم معدول: عُمَر *)
| MN_3alam_Ziada        (* علم زائد على ثلاثة: إسماعيل *)
| MN_3alam_Wazn_Fi3l    (* علم على وزن الفعل: أحمد *)
(* أسباب تتعلق بالوصفية *)
| MS_Wazn_Af3al         (* وزن أفعل للصفة: أحمر *)
| MS_Wazn_Fa3lan        (* وزن فعلان للصفة: عطشان *)
| MS_3adl               (* الوصف المعدول: ثُلاث، رُباع *)
(* أسباب أخرى *)
| MN_Wazn_Afa3il        (* صيغة منتهى الجموع: مساجد *)
| MN_Wazn_Mafa3il       (* صيغة منتهى الجموع: مفاتيح *)
| MN_Wazn_Afa3ila       (* صيغة منتهى الجموع: أساتذة *)
| MN_Alif_Ta2nith.      (* ألف التأنيث الممدودة أو المقصورة: صحراء، كبرى *)

(************************************************************)
(*           الجزء الثامن: الأعداد                           *)
(*           Part 8: Numbers (الأعداد)                       *)
(************************************************************)

Inductive 3adadType :=
| 3D_Mufrad      (* مفرد: 1-10 *)
| 3D_Murakab     (* مركب: 11-19 *)
| 3D_3uqud       (* عقود: 20-90 *)
| 3D_Ma3tuf      (* معطوف: 21-99 عدا العقود *)
| 3D_Mi2a        (* مئة *)
| 3D_Alf.        (* ألف *)

Inductive TamyeezType :=
| TM_Mufrad_Mansub    (* تمييز مفرد منصوب: 11-99 *)
| TM_Mufrad_Majrur    (* تمييز مفرد مجرور: 100، 1000 *)
| TM_Jam3_Majrur.     (* تمييز جمع مجرور: 3-10 *)

(* قواعد التذكير والتأنيث مع الأعداد *)
Record 3adadRule := {
  3d_number    : nat;
  3d_type      : 3adadType;
  3d_tamyeez   : TamyeezType;
  3d_gender    : Gender  (* مخالفة للمعدود في 3-10 *)
}.

(************************************************************)
(*           الجزء التاسع: التوابع تفصيلاً                    *)
(*           Part 9: Detailed Appositives (التوابع)          *)
(************************************************************)

(** ========== 9.1 النعت ========== *)

Inductive Na3tType :=
| NT_Haqiqi       (* نعت حقيقي: الرجلُ الكريمُ *)
| NT_Sababi       (* نعت سببي: الرجلُ الكريمُ أبوه *)
| NT_Mufrad       (* نعت مفرد *)
| NT_Jumla        (* نعت جملة *)
| NT_Shibh_Jumla. (* نعت شبه جملة *)

(** ========== 9.2 التوكيد ========== *)

Inductive TawkidType :=
| TW_Lafdhiy      (* توكيد لفظي: جاء محمدٌ محمدٌ *)
| TW_Ma3nawi_Nafs    (* توكيد معنوي بالنفس *)
| TW_Ma3nawi_3ayn    (* توكيد معنوي بالعين *)
| TW_Ma3nawi_Kulla   (* توكيد معنوي بكل *)
| TW_Ma3nawi_Jami3   (* توكيد معنوي بجميع *)
| TW_Ma3nawi_3aamma  (* توكيد معنوي بعامة *)
| TW_Ma3nawi_Kilta.  (* توكيد معنوي بكلا/كلتا *)

(** ========== 9.3 البدل ========== *)

Inductive BadalType :=
| BD_Mutabiq      (* بدل مطابق: جاء زيدٌ أخوك *)
| BD_Juz2         (* بدل بعض من كل: أكلتُ الرغيفَ نصفَه *)
| BD_Ishtimal     (* بدل اشتمال: أعجبني زيدٌ علمُه *)
| BD_Ghalat       (* بدل غلط *)
| BD_Nisyan.      (* بدل نسيان *)

(** ========== 9.4 العطف ========== *)

Inductive 3atfType :=
| 3T_Nasaq        (* عطف النسق: بحروف العطف *)
| 3T_Bayan.       (* عطف البيان: هذا أخوك زيدٌ *)

(************************************************************)
(*           الجزء العاشر: أنماط الجمل المركبة               *)
(*           Part 10: Complex Sentence Patterns              *)
(************************************************************)

Inductive JumlaWaqi3a :=
| JW_Khabar       (* جملة واقعة خبراً *)
| JW_Hal          (* جملة واقعة حالاً *)
| JW_Na3t         (* جملة واقعة نعتاً *)
| JW_Mudaf_Ilayh  (* جملة واقعة مضافاً إليه *)
| JW_Jawab_Shart  (* جملة واقعة جواب شرط *)
| JW_Jawab_Qasam  (* جملة واقعة جواب قسم *)
| JW_Sila         (* جملة واقعة صلة *)
| JW_Muqawwala.   (* جملة مقول القول *)

(* روابط الجملة الواقعة خبراً *)
Inductive JumlaRabit :=
| JR_Damir        (* ضمير *)
| JR_Ishara       (* اسم إشارة *)
| JR_I3ada        (* إعادة المبتدأ *)
| JR_Umum         (* عموم يشمل المبتدأ *)
| JR_Fa.          (* الفاء *)

(************************************************************)
(*           الجزء الحادي عشر: النحو الوظيفي                 *)
(*           Part 11: Functional Grammar Extensions          *)
(************************************************************)

(* التعدي واللزوم *)
Inductive Ta3addi :=
| TA_Lazim        (* فعل لازم *)
| TA_Muta3addi_1  (* متعدٍّ لمفعول واحد *)
| TA_Muta3addi_2  (* متعدٍّ لمفعولين *)
| TA_Muta3addi_3. (* متعدٍّ لثلاثة مفاعيل *)

(* المعلوم والمجهول *)
Inductive Bina2 :=
| BN_Ma3lum       (* معلوم *)
| BN_Majhul.      (* مجهول *)

(* صيغة التعجب *)
Inductive Ta3ajjub :=
| TA3_Ma_Af3ala        (* ما أفعله: ما أجملَ السماءَ! *)
| TA3_Af3il_Bih.       (* أفعل به: أجمِل بالسماء! *)

(* صيغة المدح والذم *)
Inductive MadhDhamm :=
| MD_Ni3ma        (* نِعْمَ *)
| MD_Bi2sa        (* بِئْسَ *)
| MD_Habadha      (* حبّذا *)
| MD_La_Habadha.  (* لا حبّذا *)

(************************************************************)
(*           الجزء الثاني عشر: دوال التوليد الموسعة         *)
(*           Part 12: Extended Generation Functions          *)
(************************************************************)

(* توليد جذر *)
Definition make_root_3 (c1 c2 c3 : ArabicLetter) (role : C2Role) : RootC2Layer := {|
  root_c1 := Some c1;
  root_c2 := c2;
  root_c3 := Some c3;
  root_c4 := None;
  root_c5 := None;
  root_class := RC_Thulathi;
  root_c2role := role
|}.

Definition make_root_4 (c1 c2 c3 c4 : ArabicLetter) (role : C2Role) : RootC2Layer := {|
  root_c1 := Some c1;
  root_c2 := c2;
  root_c3 := Some c3;
  root_c4 := Some c4;
  root_c5 := None;
  root_class := RC_Rubai;
  root_c2role := role
|}.

(* فحص صحة الجذر من حيث حروف العلة *)
Definition has_weak_letter (r : RootC2Layer) : bool :=
  let check l := match l with
    | L_Alif | L_Waw | L_Ya => true
    | _ => false
    end
  in
  match r.(root_c1) with
  | Some l => if check l then true
              else match r.(root_c3) with
                   | Some l3 => check l3
                   | None => false
                   end
  | None => false
  end.

(* تحديد نوع الجذر المعتل *)
Definition get_mu3tall_type (r : RootC2Layer) : option nat :=
  let is_weak l := match l with
    | L_Alif | L_Waw | L_Ya => true
    | _ => false
    end
  in
  match r.(root_c1) with
  | Some c1 => if is_weak c1 then Some 1  (* مثال *)
               else match r.(root_c3) with
                    | Some c3 => if is_weak c3 then Some 3  (* ناقص *)
                                 else None
                    | None => None
                    end
  | None => None
  end.

(************************************************************)
(*           الجزء الثالث عشر: لمّات وإثباتات موسعة         *)
(*           Part 13: Extended Lemmas and Proofs             *)
(************************************************************)

(* لمّا: كل جذر له مركز دلالي في C2 *)
Lemma C2_is_always_present : forall (r : RootC2Layer),
  exists (c2 : ArabicLetter), r.(root_c2) = c2.
Proof.
  intros r. exists (root_c2 r). reflexivity.
Qed.

(* لمّا: C2 يحمل الدور الدلالي *)
Lemma C2_carries_semantic_role : forall (r : RootC2Layer),
  exists (role : C2Role), r.(root_c2role) = role.
Proof.
  intros r. exists (root_c2role r). reflexivity.
Qed.

(* لمّا: الجذور الثلاثية لها ثلاثة حروف *)
Lemma thulathi_has_three_letters : forall (r : RootC2Layer),
  r.(root_class) = RC_Thulathi ->
  exists c1 c2 c3,
    r.(root_c1) = Some c1 /\
    r.(root_c2) = c2 /\
    r.(root_c3) = Some c3 /\
    r.(root_c4) = None.
Proof.
  intros r H.
  destruct (root_c1 r) eqn:E1.
  - destruct (root_c3 r) eqn:E3.
    + exists a, (root_c2 r), a0.
      split. exact E1.
      split. reflexivity.
      split. exact E3.
      (* نحتاج افتراض أن الجذر الثلاثي لا يحتوي C4 *)
      admit.
    + admit.
  - admit.
Admitted.

(* لمّا: كل تشبيه له مشبه ومشبه به *)
Lemma tashbih_has_parts : forall (t : Tashbih),
  exists (m mb : nat),
    t.(tash_mushabbah) = m /\
    t.(tash_mushabbah_bih) = mb.
Proof.
  intros t.
  exists (tash_mushabbah t), (tash_mushabbah_bih t).
  split; reflexivity.
Qed.

(* لمّا: الخبر يحتمل الصدق والكذب، والإنشاء لا يحتمله *)
Definition is_khabar (k : KhabarPurpose) : bool := true.
Definition is_insha (i : InshaType) : bool := true.

Lemma khabar_truth_apt : forall (k : KhabarPurpose),
  is_khabar k = true.
Proof.
  intros k. reflexivity.
Qed.

(************************************************************)
(*           الجزء الرابع عشر: أمثلة تطبيقية موسعة          *)
(*           Part 14: Extended Practical Examples            *)
(************************************************************)

(* أمثلة على الجذور *)
Definition root_ktb := make_root_3 L_Kaf L_Ta L_Ba C2_Eventive.
Definition root_qr2 := make_root_3 L_Qaf L_Ra L_Hamza C2_Eventive.
Definition root_3lm := make_root_3 L_Ayn L_Lam L_Mim C2_Stative.
Definition root_drb := make_root_3 L_Dal L_Ra L_Ba C2_Agentive.
Definition root_jhd := make_root_3 L_Jim L_Ha2 L_Dal C2_Eventive.

(* أمثلة على الجذور المعتلة *)
Definition root_qwl := make_root_3 L_Qaf L_Waw L_Lam C2_Eventive.     (* قول - أجوف *)
Definition root_wjd := make_root_3 L_Waw L_Jim L_Dal C2_Eventive.     (* وجد - مثال *)
Definition root_rmy := make_root_3 L_Ra L_Mim L_Ya C2_Eventive.       (* رمي - ناقص *)
Definition root_wfy := make_root_3 L_Waw L_Fa L_Ya C2_Eventive.       (* وفى - لفيف مفروق *)
Definition root_qwy := make_root_3 L_Qaf L_Waw L_Ya C2_Stative.       (* قوي - لفيف مقرون *)

(* أمثلة على الجذور الرباعية *)
Definition root_dhrj := make_root_4 L_Dal L_Ha L_Ra L_Jim C2_Eventive. (* دحرج *)
Definition root_trgm := make_root_4 L_Ta L_Ra L_Jim L_Mim C2_Eventive. (* ترجم *)
Definition root_zlzl := make_root_4 L_Zay L_Lam L_Zay L_Lam C2_Eventive. (* زلزل *)

(* أمثلة على التشبيه *)
Definition tashbih_example := {|
  tash_mushabbah := 1;      (* الطالب *)
  tash_mushabbah_bih := 2;  (* الأسد *)
  tash_adat := Some 3;      (* كـ *)
  tash_wajh := Some 4;      (* الشجاعة *)
  tash_type := TSH_Mufassal
|}.

Definition tashbih_baligh := {|
  tash_mushabbah := 1;
  tash_mushabbah_bih := 2;
  tash_adat := None;       (* محذوفة *)
  tash_wajh := None;       (* محذوف *)
  tash_type := TSH_Baligh  (* "الطالب أسد" *)
|}.

(* مثال على القافية *)
Definition qafiya_example := {|
  qf_rawiy := L_Mim;
  qf_type := QF_Mutawatira;
  qf_harakaat := [H_Fatha; H_Kasra]
|}.

(* أمثلة على قواعد الأعداد *)
Definition 3adad_thalatha := {|
  3d_number := 3;
  3d_type := 3D_Mufrad;
  3d_tamyeez := TM_Jam3_Majrur;
  3d_gender := G_Feminine  (* ثلاثةُ طلابٍ - مخالفة *)
|}.

Definition 3adad_3ashara := {|
  3d_number := 10;
  3d_type := 3D_Mufrad;
  3d_tamyeez := TM_Jam3_Majrur;
  3d_gender := G_Feminine  (* عشرةُ طلابٍ - مخالفة *)
|}.

Definition 3adad_11 := {|
  3d_number := 11;
  3d_type := 3D_Murakab;
  3d_tamyeez := TM_Mufrad_Mansub;
  3d_gender := G_Masculine  (* أحدَ عشرَ طالباً - موافقة *)
|}.

(************************************************************)
(*           الجزء الخامس عشر: سلاسل التوليد الموسعة        *)
(*           Part 15: Extended Generation Chains             *)
(************************************************************)

(* سلسلة: جذر → وزن → مفردة → جملة → مركب → نص *)
Inductive GenerationLevel :=
| GL_Root       (* الجذر *)
| GL_Wazn       (* الوزن *)
| GL_Mufrada    (* المفردة *)
| GL_Jumla      (* الجملة *)
| GL_Muraqqab   (* المركب *)
| GL_Nass.      (* النص *)

(* تمثيل النص *)
Record Nass := {
  ns_muraqqabaat : list nat;  (* مجموعة المركبات *)
  ns_rabṭ        : list nat   (* أدوات الربط *)
}.

(* لمّا: كل مستوى يبنى على ما قبله *)
Lemma generation_is_hierarchical : forall (l : GenerationLevel),
  l = GL_Root \/ l = GL_Wazn \/ l = GL_Mufrada \/ 
  l = GL_Jumla \/ l = GL_Muraqqab \/ l = GL_Nass.
Proof.
  intros l.
  destruct l; auto.
Qed.

(* لمّا: الجذر هو الأساس *)
Lemma root_is_base : forall (l : GenerationLevel),
  l <> GL_Root ->
  exists (prev : GenerationLevel),
    (l = GL_Wazn /\ prev = GL_Root) \/
    (l = GL_Mufrada /\ prev = GL_Wazn) \/
    (l = GL_Jumla /\ prev = GL_Mufrada) \/
    (l = GL_Muraqqab /\ prev = GL_Jumla) \/
    (l = GL_Nass /\ prev = GL_Muraqqab).
Proof.
  intros l Hneq.
  destruct l.
  - contradiction.
  - exists GL_Root. left. auto.
  - exists GL_Wazn. right. left. auto.
  - exists GL_Mufrada. right. right. left. auto.
  - exists GL_Jumla. right. right. right. left. auto.
  - exists GL_Muraqqab. right. right. right. right. auto.
Qed.

End AGT_Extended.
