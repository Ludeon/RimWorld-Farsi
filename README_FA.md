# ترجمه فارسی رسمی RimWorld

<div align="center">

[![RimWorld Version](https://img.shields.io/badge/RimWorld-1.5%2B-blue.svg?logo=steam)](https://rimworldgame.com/)
[![Latest Release](https://img.shields.io/github/v/release/Ludeon/RimWorld-Farsi?color=success&logo=github)](https://github.com/Ludeon/RimWorld-Farsi/releases)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Ludeon/RimWorld-Farsi/persianCorrectionPythonBeta.yml?branch=main&label=CI%2FCD&logo=githubactions)](https://github.com/Ludeon/RimWorld-Farsi/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

**[English Documentation (README.md)](README.md)**

</div>

---

این مخزن شامل **بسته رسمی ترجمه فارسی بازی RimWorld** است که با پشتیبانی استودیوی **Ludeon** ایجاد شده و توسط جامعه بازیکنان فارسی‌زبان به‌طور مداوم نگه‌داری و توسعه داده می‌شود.

به دلیل اینکه نسخه‌های بسته‌بندی‌شده درون به‌روزرسانی‌های رسمی استیم ممکن است همیشه آخرین تغییرات و اصلاحات را در بر نداشته باشند، بازیکنان می‌توانند همواره جدیدترین نسخه ترجمه را از طریق این مخزن دریافت و نصب کنند.

---

## 📦 جدول سازگاری نسخه‌ها و بسته‌های الحاقی (DLC)

این بسته ترجمه با نسخه **RimWorld 1.5+** کاملاً سازگار است و بر اساس معماری رسمی مخازن محلی‌سازی لودیون استودیوز (Ludeon Studios) سازمان‌دهی شده است:

| بسته الحاقی (DLC) | وضعیت پشتیبانی | ماژول در مخزن | مسیر پوشه مقصد در دایرکتوری بازی |
| :--- | :---: | :---: | :--- |
| **RimWorld Core (پایه)** | پشتیبانی کامل | `Core/` | `<RimWorld>/Data/Core/Languages/Persian (فارسی)` |
| **Royalty DLC** | پشتیبانی کامل | `Royalty/` | `<RimWorld>/Data/Royalty/Languages/Persian (فارسی)` |
| **Ideology DLC** | پشتیبانی کامل | `Ideology/` | `<RimWorld>/Data/Ideology/Languages/Persian (فارسی)` |
| **Biotech DLC** | پشتیبانی کامل | `Biotech/` | `<RimWorld>/Data/Biotech/Languages/Persian (فارسی)` |
| **Anomaly DLC** | پشتیبانی کامل | `Anomaly/` | `<RimWorld>/Data/Anomaly/Languages/Persian (فارسی)` |
| **Odyssey** | در حال انجام | `Odyssey/` | `<RimWorld>/Data/Odyssey/Languages/Persian (فارسی)` |

---

## 🚀 راهنمای نصب

روش نصب مناسب برای سیستم خود را انتخاب کنید:

### روش ۱: نصب خودکار و آسان (پیشنهادی)

* **ویندوز**:
  1. مخزن را دریافت یا کلون کنید.
  2. فایل [`install.bat`](install.bat) را اجرا کنید. این اسکریپت به‌صورت هوشمند محل نصب استیم یا ریم‌ورلد را شناسایی کرده (یا پنجره انتخاب پوشه را باز می‌کند)، فایل‌های ماژول‌ها را در مسیر بازی کپی کرده و فایل‌های فشرده کش زبان (`.tar`) را پاکسازی می‌کند.
* **لینوکس یا استیم‌دک (Steam Deck)**:
  1. ترمینال را در پوشه پروژه باز کنید.
  2. اسکریپت `./install.sh` را اجرا نمایید.

---

### روش ۲: نصب دستی (تمامی سیستم‌عامل‌ها)

1. فایل آخرین نسخه (`persian.language.zip`) را از [صفحه Releases](https://github.com/Ludeon/RimWorld-Farsi/releases) دانلود کرده یا مخزن را کلون کنید.
2. مسیر نصب بازی را در رایانه خود پیدا کنید:
   * **ویندوز:** `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\`
   * **لینوکس:** `~/.steam/steam/steamapps/common/Rimworld/`
   * **مک:** `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app` *(راست‌کلیک و انتخاب "Show Package Contents")*
3. محتوای هر پوشه ماژول (`Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly`, `Odyssey`) را در مسیر متناظر داخل پوشه زبان بازی کپی کنید:
   * محتوای `Core` در `<RimWorld>/Data/Core/Languages/Persian (فارسی)`
   * محتوای `Royalty` در `<RimWorld>/Data/Royalty/Languages/Persian (فارسی)`
   * محتوای `Ideology` در `<RimWorld>/Data/Ideology/Languages/Persian (فارسی)`
   * محتوای `Biotech` در `<RimWorld>/Data/Biotech/Languages/Persian (فارسی)`
   * محتوای `Anomaly` در `<RimWorld>/Data/Anomaly/Languages/Persian (فارسی)`
4. فایل‌های فشرده کش قبلی (`Persian (فارسی).tar` یا `Persian.tar`) را در این مسیرها حذف کنید تا بازی مستقیماً فایل‌های بروز شده را لود کند.

---

### روش ۳: همگام‌سازی مستقیم توسعه‌دهندگان (`tools/sync.sh`)

اگر در حال ترجمه یا توسعه هستید، می‌توانید با اسکریپت همگام‌سازی، تغییرات را بدون کپی دستی ارسال یا دریافت کنید:

```bash
# ارسال ترجمه‌های مخزن به بازی
./tools/sync.sh --gamepath "/path/to/RimWorld"

# دریافت ترجمه‌های تغییر یافته از بازی به مخزن
./tools/sync.sh --gamepath "/path/to/RimWorld" --direction pull
```

---

## ⚙️ فعال‌سازی در بازی

1. بازی RimWorld را اجرا کنید.
2. در منوی اصلی روی آیکون **پرچم (زبان‌ها)** یا بخش **Options** کلیک کنید.
3. زبان **Persian (فارسی)** را انتخاب کنید.
4. رابط کاربری به‌صورت خودکار بارگذاری مجدد شده و متون فارسی نمایش داده می‌شوند.

> [!TIP]
> **سازگاری با سیو‌های قبلی**: این ترجمه کاملاً با بازی‌های ذخیره‌شده شما سازگار است و هیچ‌گونه تداخلی با سیوهای قبلی ایجاد نمی‌کند. برای استفاده از آن نیازی به آغاز بازی جدید ندارید.

---

## 🖼️ نمایی از بازی

<div align="center">
  <img src="https://github.com/user-attachments/assets/87633f91-a012-4567-8f07-15aec21a4be2" alt="نمایی از ترجمه فارسی ریم‌ورلد" width="850" />
</div>

---

## 🛠️ ابزارها و زیرساخت فنی

به منظور حل چالش‌های متون راست‌به‌چپ (RTL) و حروف‌چینی فارسی در موتور بازی:

1. **پردازشگر متون RTL (`tools/rtl-processor/`)**:
   - اسکریپت پایتون پیشرفته اصلاح متن و تنظیم جهت حروف (`PersianFixer.py`).
   - سیستم خودکار اعتبارسنجی ساختار XML (`validate_xml.py`).
   - مجموعه آزمون‌های واحد و یکپارچه در `tools/rtl-processor/tests/` با پشتیبانی از پایتون 3.11 تا 3.13 و منطبق با استانداردهای مدرن پایتون (PEP 8, PEP 585, PEP 604, PEP 621).
2. **مود اختصاصی سی‌شارپ (`mods/RTL_Persian_Support/`)**:
   - پچ هارمونی برای اصلاح بی‌درنگ متون و پشتیبانی بهینه از فونت‌های فارسی در منوهای بازی.
3. **پایپ‌لاین CI/CD گیت‌هاب اکشنز (`.github/workflows/`)**:
   - اجرای آزمون‌های خودکار، فرمت‌بندی و لینتینگ سریع با Ruff، بررسی دقیق نوع‌داده‌ها با Mypy و بسته‌بندی ریلیزها.

---

## 🤝 مشارکت در پروژه

ما از مشارکت تمامی علاقه‌مندان، اعم از مترجمان و برنامه‌نویسان، استقبال می‌کنیم!

- برای آشنایی با دستورالعمل‌های ترجمه، استانداردهای نگارشی و نحوه تنظیم محیط توسعه، راهنمای جامع **[CONTRIBUTING.md](CONTRIBUTING.md)** را مطالعه کنید.
- قبل از شروع ترجمه یک بخش بزرگ، بخش [Issues](https://github.com/Ludeon/RimWorld-Farsi/issues) را بررسی کنید یا تیکت جدیدی ایجاد نمایید تا از دوباره‌کاری جلوگیری شود.

---

## 🚫 بخش‌هایی که انگلیسی باقی مانده‌اند

برخی از بخش‌های بازی عمداً به زبان انگلیسی باقی می‌مانند:
- **نام‌های پیش‌فرض برخی شخصیت‌ها و نام جناح‌ها**: به دلیل عدم ارائه شناسه ترجمه توسط موتور بازی.
- **حالت توسعه‌دهنده (Dev Mode) و گزارش‌های لاگ**: برای حفظ کارایی در عیب‌یابی فنی و اشکال‌زدایی.
- **کلیدهای میانبر**: برای هماهنگی با کیبوردهای استاندارد و راهنماهای مرجع.
- **فهرست توسعه‌دهندگان اصلی بازی**: برای ادای احترام به سازندگان بازی.

---

## 🏆 مشارکت‌کنندگان و قدردانی

### مترجم فعال و نگه‌دارنده
* **دانیال پهلوان** ([@DanialPahlavan](https://github.com/DanialPahlavan))

### همکاران پیشین
* **سید عبداللهی** ([@SeyedAbdollahi](https://github.com/SeyedAbdollahi))

### سپاس‌گزاری ویژه
* **@mtimoustafa** و **@asidsx** به پاس توسعه ابزارهای بنیادین راست‌به‌چپ در RimWorld.

---

## 📜 پروانه و مجوز انتشار

این پروژه یک نرم‌افزار آزاد است که تحت پروانه **GNU General Public License v3.0** منتشر شده است. برای اطلاعات بیشتر فایل [LICENSE](LICENSE) را مشاهده کنید.
