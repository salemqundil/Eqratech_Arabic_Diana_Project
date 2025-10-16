# Google Colab Usage Guide
# دليل استخدام Google Colab

## English Guide

### What is Google Colab?

Google Colab (Colaboratory) is a free cloud-based Jupyter notebook environment that requires no setup and runs entirely in the cloud. It's perfect for running Python code, especially for data science and machine learning projects.

### Why Use Colab with This Project?

- **No Installation Required**: Work with the project immediately without installing Python or dependencies
- **Free Computing Resources**: Access to free CPU and GPU resources
- **Easy Sharing**: Share your work with others through a simple link
- **Arabic Text Support**: Full Unicode support for Arabic text processing

### Getting Started

1. **Open the Notebook**
   - Click the "Open in Colab" badge in the README
   - Or visit: https://colab.research.google.com/github/salemqundil/Eqratech_Arabic_Diana_Project/blob/main/Eqratech_Arabic_Colab.ipynb

2. **Run the Setup Cells**
   - Click on the first code cell
   - Press `Shift + Enter` to run it
   - Continue running cells in order

3. **Explore the Features**
   - Each cell is documented in both English and Arabic
   - Modify code cells to experiment with different features
   - Add your own cells to try new things

### What Can You Do?

#### 1. Generate Phoneme Data
```python
from phonemes_engine import PhonemesEngine
df = PhonemesEngine.make_df()
print(df.head())
```

#### 2. Work with Verbs
```python
from verbs_engine import VerbsEngine
df_verbs = VerbsEngine.make_df()
print(df_verbs.head())
```

#### 3. Generate Sentences
```python
from simple_sentence_generator import SimpleSentenceGenerator
generator = SimpleSentenceGenerator()
generator.load_basic_engines()
```

#### 4. Export Full Grammar
```python
from export_full_multilayer_grammar_minimal import main as export_main
export_main()
```

### Tips for Success

1. **Run Cells in Order**: The cells are designed to run sequentially
2. **Wait for Completion**: Some operations (like exports) may take several minutes
3. **Save Your Work**: Use `File > Save a copy in Drive` to save your modifications
4. **Restart if Needed**: If something goes wrong, use `Runtime > Restart runtime`

### Troubleshooting

**Problem**: Import errors
- **Solution**: Make sure you ran the installation cell first

**Problem**: File not found errors
- **Solution**: Verify you ran the repository cloning cell

**Problem**: Arabic text not displaying correctly
- **Solution**: The environment setup cell handles this automatically; rerun it if needed

### Advanced Usage

#### Custom Engine Exploration
```python
import glob
engines = glob.glob('*_engine.py')
for engine in engines:
    print(engine)
```

#### Working with CSV Data
```python
import pandas as pd
df = pd.read_csv('your_file.csv')
df.head()
```

#### Downloading Results
```python
from google.colab import files
files.download('filename.xlsx')
```

---

## الدليل العربي

### ما هو Google Colab؟

Google Colab (Colaboratory) هو بيئة دفتر Jupyter مجانية قائمة على السحابة لا تتطلب أي إعداد وتعمل بالكامل في السحابة. إنه مثالي لتشغيل كود Python، وخاصة لمشاريع علوم البيانات والتعلم الآلي.

### لماذا استخدام Colab مع هذا المشروع؟

- **لا يتطلب تثبيت**: العمل مع المشروع فوراً دون تثبيت Python أو المتطلبات
- **موارد حوسبة مجانية**: الوصول إلى موارد CPU و GPU مجانية
- **مشاركة سهلة**: شارك عملك مع الآخرين من خلال رابط بسيط
- **دعم النص العربي**: دعم كامل لـ Unicode لمعالجة النصوص العربية

### البدء

1. **افتح الدفتر**
   - انقر على شارة "Open in Colab" في ملف README
   - أو قم بزيارة: https://colab.research.google.com/github/salemqundil/Eqratech_Arabic_Diana_Project/blob/main/Eqratech_Arabic_Colab.ipynb

2. **قم بتشغيل خلايا الإعداد**
   - انقر على خلية الكود الأولى
   - اضغط `Shift + Enter` لتشغيلها
   - استمر في تشغيل الخلايا بالترتيب

3. **استكشف الميزات**
   - كل خلية موثقة بالإنجليزية والعربية
   - عدّل خلايا الكود لتجربة ميزات مختلفة
   - أضف خلايا خاصة بك لتجربة أشياء جديدة

### ماذا يمكنك أن تفعل؟

#### 1. توليد بيانات الفونيمات
```python
from phonemes_engine import PhonemesEngine
df = PhonemesEngine.make_df()
print(df.head())
```

#### 2. العمل مع الأفعال
```python
from verbs_engine import VerbsEngine
df_verbs = VerbsEngine.make_df()
print(df_verbs.head())
```

#### 3. توليد الجمل
```python
from simple_sentence_generator import SimpleSentenceGenerator
generator = SimpleSentenceGenerator()
generator.load_basic_engines()
```

#### 4. تصدير القواعد الكاملة
```python
from export_full_multilayer_grammar_minimal import main as export_main
export_main()
```

### نصائح للنجاح

1. **قم بتشغيل الخلايا بالترتيب**: الخلايا مصممة للتشغيل بشكل متسلسل
2. **انتظر الإكمال**: قد تستغرق بعض العمليات (مثل التصدير) عدة دقائق
3. **احفظ عملك**: استخدم `File > Save a copy in Drive` لحفظ تعديلاتك
4. **أعد التشغيل إذا لزم الأمر**: إذا حدث خطأ ما، استخدم `Runtime > Restart runtime`

### استكشاف الأخطاء وإصلاحها

**المشكلة**: أخطاء الاستيراد
- **الحل**: تأكد من أنك قمت بتشغيل خلية التثبيت أولاً

**المشكلة**: أخطاء الملف غير موجود
- **الحل**: تحقق من أنك قمت بتشغيل خلية استنساخ المستودع

**المشكلة**: النص العربي لا يعرض بشكل صحيح
- **الحل**: خلية إعداد البيئة تتعامل مع هذا تلقائياً؛ أعد تشغيلها إذا لزم الأمر

### الاستخدام المتقدم

#### استكشاف المحركات المخصصة
```python
import glob
engines = glob.glob('*_engine.py')
for engine in engines:
    print(engine)
```

#### العمل مع بيانات CSV
```python
import pandas as pd
df = pd.read_csv('your_file.csv')
df.head()
```

#### تحميل النتائج
```python
from google.colab import files
files.download('filename.xlsx')
```

---

## Additional Resources / موارد إضافية

- **GitHub Repository**: https://github.com/salemqundil/Eqratech_Arabic_Diana_Project
- **Colab Documentation**: https://colab.research.google.com/notebooks/intro.ipynb
- **Python Documentation**: https://docs.python.org/3/
- **Pandas Documentation**: https://pandas.pydata.org/docs/

## Support / الدعم

For issues or questions, please:
- Open an issue on GitHub
- Check existing issues for solutions

للمشاكل أو الأسئلة، يرجى:
- فتح issue على GitHub
- التحقق من المشاكل الموجودة للحلول
