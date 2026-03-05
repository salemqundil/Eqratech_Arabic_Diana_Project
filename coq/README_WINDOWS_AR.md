# دليل تثبيت وإعداد Coq Platform على Windows

هذا الدليل يشرح كيفية تثبيت وإعداد Coq Platform على نظام Windows لتطوير البراهين الرياضية باستخدام نظرية الأنواع.

## المتطلبات

- نظام Windows (64-بت)
- اتصال بالإنترنت لتحميل المثبت

## خطوات التثبيت

### 1. تحميل Coq Platform

نزّل مثبت Coq Platform لويندوز (64‑بت) من الرابط التالي:
```
https://github.com/coq/platform/releases
```

اختر أحدث إصدار متاح وحمّل الملف `.exe` المناسب لنظام Windows 64-بت.

### 2. تشغيل المثبت

1. شغّل الملف `.exe` الذي قمت بتحميله
2. اختر نوع التثبيت:
   - **Full**: تثبيت كامل مع جميع المكتبات والأدوات (موصى به للمبتدئين)
   - **Custom**: تثبيت مخصص حيث يمكنك اختيار المكونات التي تريد تثبيتها

3. **مهم جداً**: فَعِّل خيار **"Add Coq to PATH"** أثناء التثبيت
   - هذا الخيار يضيف أدوات Coq إلى متغير PATH في النظام
   - يسمح لك باستخدام أوامر Coq من أي مكان في سطر الأوامر

### 3. موقع التثبيت الافتراضي

سيتم تثبيت Coq Platform غالباً في المسار التالي:
```
C:\Coq-Platform~8.xx~YYYY.MM\
```

حيث:
- `8.xx` هو رقم إصدار Coq (مثل 8.17، 8.18، إلخ)
- `YYYY.MM` هو تاريخ إصدار Platform

المجلد `bin\` داخل مجلد التثبيت يحتوي على الملف التنفيذي `coqc.exe` والأدوات الأخرى.

## التحقق من التثبيت

### 1. فتح PowerShell جديد

بعد اكتمال التثبيت، افتح نافذة PowerShell جديدة:
- اضغط `Win + X` واختر **Windows PowerShell** أو **Terminal**
- أو ابحث عن "PowerShell" في قائمة ابدأ

**ملاحظة**: يجب فتح نافذة جديدة بعد التثبيت لتحديث متغيرات البيئة.

### 2. اختبار الأمر coqc

في نافذة PowerShell، شغّل الأمر التالي:
```powershell
coqc --version
```

إذا ظهر رقم الإصدار (مثل `The Coq Proof Assistant, version 8.17.1`), فهذا يعني أن:
- التثبيت نجح بشكل صحيح
- الأداة `coqc` أصبحت في PATH
- يمكنك الآن استخدام Coq من أي مكان

### 3. في حالة عدم العثور على coqc

إذا ظهرت رسالة خطأ مثل:
```
coqc : The term 'coqc' is not recognized as the name of a cmdlet...
```

هذا يعني أن Coq غير موجود في PATH. يمكنك إصلاح ذلك بطريقتين:

#### الطريقة المؤقتة (للجلسة الحالية فقط)

أضف المسار يدوياً في نفس نافذة PowerShell:
```powershell
$env:PATH += ";C:\Coq-Platform~8.xx~YYYY.MM\bin"
```

**تنبيه**: عدّل المسار ليطابق موقع التثبيت الفعلي على جهازك.

ثم أعد تشغيل الأمر:
```powershell
coqc --version
```

استمر في تعديل المسار حتى يعمل الأمر بشكل صحيح.

#### الطريقة الدائمة (لجميع الجلسات)

1. افتح **إعدادات النظام** → **النظام** → **حول** → **إعدادات النظام المتقدمة**
2. اضغط على زر **Environment Variables** (متغيرات البيئة)
3. في قسم **System variables** (متغيرات النظام)، ابحث عن متغير `Path`
4. اضغط **Edit** (تحرير)
5. أضف مسار جديد: `C:\Coq-Platform~8.xx~YYYY.MM\bin`
6. اضغط **OK** لحفظ التغييرات
7. أعد فتح PowerShell للتحديث

## بناء ملفات Coq في هذا المشروع

### بنية المشروع

يحتوي مجلد `coq/` على بنية طبقية منظمة:
```
coq/
├── scripts/
│   └── build_all.ps1                 # سكريبت بناء شامل
├── theories/
│   ├── Core/                         # الطبقة الأساسية
│   │   ├── FractalHubSpec.v
│   │   ├── FractalHubGates.v
│   │   └── FractalHubDerivation.v
│   ├── Phonology/                    # طبقة الفونولوجيا
│   │   └── FractalHubPhonology.v
│   ├── Syntax/                       # طبقة النحو
│   │   └── FractalHubSyntaxDerivation.v
│   ├── Codec/                        # طبقة الترميز
│   │   └── FractalHubCodecRoundTrip.v
│   ├── FractalHubSpec.v              # واجهة (facade)
│   ├── FractalHubGates.v             # واجهة
│   ├── FractalHubDerivation.v        # واجهة
│   ├── FractalHubPhonology.v         # واجهة
│   ├── FractalHubSyntaxDerivation.v  # واجهة
│   └── FractalHubCodecRoundTrip.v    # واجهة
├── _CoqProject                       # ملف مشروع Coq
└── README_WINDOWS_AR.md              # هذا الملف
```

**ملاحظة**: ملفات الواجهة (facade files) في الجذر تحافظ على التوافق الخلفي مع الاستيرادات القديمة.

### أوامر البناء

بعد التحقق من أن `coqc` يعمل، يمكنك بناء ملفات النظريات من مجلد `coq`:

#### 1. الانتقال إلى مجلد coq

```powershell
cd coq
```

#### 2. بناء الملفات باستخدام السكريبت الشامل (الطريقة الموصى بها)

استخدم السكريبت الشامل لبناء جميع الطبقات بالترتيب الصحيح:

```powershell
# من داخل مجلد coq/
.\scripts\build_all.ps1
```

السكريبت سيبني:
1. **Core layer**: FractalHubSpec, FractalHubGates, FractalHubDerivation
2. **Phonology layer**: FractalHubPhonology
3. **Syntax layer**: FractalHubSyntaxDerivation
4. **Codec layer**: FractalHubCodecRoundTrip
5. **Facade files**: ملفات الواجهة للتوافق الخلفي

#### 3. بناء الملفات يدوياً (متقدم)

يمكنك بناء الطبقات يدوياً بالترتيب التالي:

**Core layer:**
```powershell
coqc -q -R theories FractalHub theories/Core/FractalHubSpec.v
coqc -q -R theories FractalHub theories/Core/FractalHubGates.v
coqc -q -R theories FractalHub theories/Core/FractalHubDerivation.v
```

**Phonology layer:**
```powershell
coqc -q -R theories FractalHub theories/Phonology/FractalHubPhonology.v
```

**Syntax layer:**
```powershell
coqc -q -R theories FractalHub theories/Syntax/FractalHubSyntaxDerivation.v
```

**Codec layer:**
```powershell
coqc -q -R theories FractalHub theories/Codec/FractalHubCodecRoundTrip.v
```

**Facade files:**
```powershell
coqc -q -R theories FractalHub theories/FractalHubSpec.v
coqc -q -R theories FractalHub theories/FractalHubGates.v
coqc -q -R theories FractalHub theories/FractalHubDerivation.v
coqc -q -R theories FractalHub theories/FractalHubPhonology.v
coqc -q -R theories FractalHub theories/FractalHubSyntaxDerivation.v
coqc -q -R theories FractalHub theories/FractalHubCodecRoundTrip.v
```

**شرح الخيارات:**
- `-q`: وضع هادئ (quiet mode) - يقلل من الرسائل المطبوعة
- `-R theories FractalHub`: يربط مجلد `theories` بمساحة الاسم `FractalHub`
  - هذا يسمح للملفات باستخدام `Require Import FractalHub...`
  - يجب أن يكون هذا الخيار متسقاً عبر جميع أوامر البناء

#### 4. التحقق من نجاح البناء

إذا نجح البناء، ستجد ملفات `.vo` (Verified Object) في المجلدات المختلفة:
- `theories/Core/*.vo`
- `theories/Phonology/*.vo`
- `theories/Syntax/*.vo`
- `theories/Codec/*.vo`
- `theories/*.vo` (facade files)

هذه الملفات هي نتيجة عملية التحقق والبناء.

### بناء جميع الملفات مرة واحدة (بدون السكريبت)

يمكنك بناء جميع الطبقات بأمر واحد إذا أردت:

```powershell
# Core layer
coqc -q -R theories FractalHub theories/Core/FractalHubSpec.v && `
coqc -q -R theories FractalHub theories/Core/FractalHubGates.v && `
coqc -q -R theories FractalHub theories/Core/FractalHubDerivation.v && `
# Phonology layer
coqc -q -R theories FractalHub theories/Phonology/FractalHubPhonology.v && `
# Syntax layer
coqc -q -R theories FractalHub theories/Syntax/FractalHubSyntaxDerivation.v && `
# Codec layer
coqc -q -R theories FractalHub theories/Codec/FractalHubCodecRoundTrip.v && `
# Facades
coqc -q -R theories FractalHub theories/FractalHubSpec.v && `
coqc -q -R theories FractalHub theories/FractalHubGates.v && `
coqc -q -R theories FractalHub theories/FractalHubDerivation.v && `
coqc -q -R theories FractalHub theories/FractalHubPhonology.v && `
coqc -q -R theories FractalHub theories/FractalHubSyntaxDerivation.v && `
coqc -q -R theories FractalHub theories/FractalHubCodecRoundTrip.v
```

**ملاحظة**: في PowerShell، يُستخدم الرمز `` ` `` (backtick) لكسر الأمر على عدة أسطر.

#### اختبار سريع للتحقق من البناء الناجح

بعد البناء، يمكنك التحقق من أن جميع ملفات `.vo` تم إنشاؤها بنجاح:

```powershell
Get-ChildItem theories\*.vo -Recurse | Select-Object Name, Directory
```

يجب أن تشاهد جميع ملفات `.vo` في المجلدات الطبقية والواجهات، بما في ذلك:
- Core layer: FractalHubSpec.vo, FractalHubGates.vo, FractalHubDerivation.vo
- Phonology layer: FractalHubPhonology.vo
- Syntax layer: FractalHubSyntaxDerivation.vo
- Codec layer: FractalHubCodecRoundTrip.vo
- Facade files في الجذر

### معالجة الأخطاء

إذا ظهرت أخطاء أثناء البناء:

1. **خطأ في التبعيات**: تأكد من بناء الملفات بالترتيب الصحيح
2. **خطأ في المسار**: تأكد من أنك في مجلد `coq` عند تشغيل الأوامر
3. **خطأ في النحو**: افتح الملف `.v` وتحقق من وجود أخطاء نحوية في كود Coq

## موارد إضافية

- [موقع Coq الرسمي](https://coq.inria.fr/)
- [وثائق Coq](https://coq.inria.fr/documentation)
- [دليل Coq المرجعي](https://coq.inria.fr/refman/)
- [Coq Platform على GitHub](https://github.com/coq/platform)

## الدعم والمساعدة

إذا واجهت مشاكل:
1. تحقق من أن إصدار Windows لديك 64-بت
2. تأكد من أنك قمت بتفعيل خيار "Add Coq to PATH" أثناء التثبيت
3. حاول إعادة تثبيت Coq Platform
4. راجع سجل الأخطاء (Error log) إذا فشل التثبيت

---

**آخر تحديث**: ديسمبر 2025
