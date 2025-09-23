# خدمة الإحصائيات - منصة نائبك.كوم

خدمة مصغرة لإدارة الإحصائيات وعداد الزوار في منصة نائبك.كوم، مبنية باستخدام Flask وقاعدة بيانات SQLite.

## 🎯 الوظائف الرئيسية

- **إدارة الإحصائيات العامة**: إضافة وتحديث المقاييس والإحصائيات
- **الإحصائيات اليومية**: تتبع البيانات اليومية مع نطاقات زمنية
- **ملخص الإحصائيات**: تجميع البيانات حسب الفئات
- **قاعدة بيانات محلية**: SQLite لتخزين البيانات بكفاءة
- **واجهات برمجية RESTful**: APIs شاملة ومنظمة
- **فحص الصحة**: مراقبة حالة الخدمة وقاعدة البيانات

## 🏗️ البنية التقنية

### التقنيات المستخدمة
- **Backend**: Flask 2.3.3
- **قاعدة البيانات**: SQLite
- **CORS**: Flask-CORS 4.0.0
- **النشر**: Gunicorn 21.2.0

### النماذج الأساسية
- `statistics`: الإحصائيات العامة
- `daily_stats`: الإحصائيات اليومية

## 🚀 التثبيت والتشغيل

### المتطلبات
- Python 3.11+
- Flask 2.3.3+

### خطوات التثبيت

1. **استنساخ المشروع**
```bash
git clone https://github.com/alcounsol17/naebak-statistics-service.git
cd naebak-statistics-service
```

2. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

3. **تشغيل الخادم**
```bash
python app.py
```

الخدمة ستعمل على `http://localhost:8007`

## 📊 APIs المتاحة

### النقاط الأساسية
- `GET /` - معلومات الخدمة
- `GET /health` - فحص صحة الخدمة
- `POST /stats` - إضافة أو تحديث إحصائية
- `GET /stats` - الحصول على الإحصائيات مع فلاتر
- `POST /stats/daily` - إضافة إحصائية يومية
- `GET /stats/daily` - الحصول على الإحصائيات اليومية
- `GET /stats/summary` - ملخص الإحصائيات حسب الفئة

### أمثلة على الاستخدام

#### إضافة إحصائية جديدة
```bash
curl -X POST http://localhost:8007/stats \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "total_users",
    "metric_value": 1500,
    "category": "users",
    "description": "إجمالي عدد المستخدمين"
  }'
```

#### الحصول على الإحصائيات
```bash
# جميع الإحصائيات
curl http://localhost:8007/stats

# إحصائيات فئة معينة
curl http://localhost:8007/stats?category=users

# إحصائية محددة
curl http://localhost:8007/stats?metric_name=total_users
```

#### إضافة إحصائية يومية
```bash
curl -X POST http://localhost:8007/stats/daily \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-09-23",
    "metric_name": "daily_visitors",
    "metric_value": 250,
    "category": "traffic"
  }'
```

#### الحصول على الإحصائيات اليومية
```bash
# إحصائيات نطاق زمني
curl "http://localhost:8007/stats/daily?start_date=2025-09-01&end_date=2025-09-30"

# إحصائيات فئة معينة
curl "http://localhost:8007/stats/daily?category=traffic"
```

## 🗄️ هيكل قاعدة البيانات

### جدول statistics
```sql
CREATE TABLE statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    category TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### جدول daily_stats
```sql
CREATE TABLE daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, metric_name, category)
);
```

## 🔧 الإعدادات

### متغيرات البيئة
```env
PORT=8007                    # منفذ الخادم
FLASK_ENV=development        # بيئة التطوير
DB_PATH=statistics.db        # مسار قاعدة البيانات
```

### إعدادات الإنتاج
```bash
# تشغيل مع Gunicorn
gunicorn -w 4 -b 0.0.0.0:8007 app:app
```

## 📁 هيكل المشروع

```
naebak-statistics-service/
├── app.py                   # التطبيق الرئيسي
├── requirements.txt         # المتطلبات
├── Dockerfile              # إعدادات Docker
├── statistics.db           # قاعدة البيانات (تُنشأ تلقائياً)
└── README.md               # هذا الملف
```

## 🚀 النشر

### Docker
```bash
# بناء الصورة
docker build -t naebak-statistics-service .

# تشغيل الحاوية
docker run -p 8007:8007 naebak-statistics-service
```

### النشر اليدوي
```bash
# تشغيل مع Gunicorn
gunicorn -w 4 -b 0.0.0.0:8007 app:app
```

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى Branch (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 📞 التواصل

- **المشروع**: [نائبك.كوم](https://naebak.com)
- **المطور**: alcounsol17
- **GitHub**: [https://github.com/alcounsol17](https://github.com/alcounsol17)

## 🔄 التحديثات الأخيرة

### الإصدار 1.0.0 (سبتمبر 2025)
- ✅ إطلاق النسخة الأولى
- ✅ APIs شاملة للإحصائيات
- ✅ دعم الإحصائيات اليومية
- ✅ ملخص الإحصائيات حسب الفئة
- ✅ قاعدة بيانات SQLite محلية
- ✅ معالجة الأخطاء المتقدمة
- ✅ دعم CORS للتطبيقات الأمامية
- ✅ فحص صحة الخدمة

---

**ملاحظة**: هذه الخدمة جزء من منظومة نائبك.كوم المتكاملة لربط المواطنين بنوابهم في البرلمان.
