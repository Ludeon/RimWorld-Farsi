# ترجمه فارسی رسمی RimWorld

<div align="center">

[![RimWorld Version](https://img.shields.io/badge/RimWorld-1.5%2B-blue.svg?logo=steam)](https://rimworldgame.com/)
[![Latest Release](https://img.shields.io/github/v/release/Ludeon/RimWorld-Farsi?color=success&logo=github)](https://github.com/Ludeon/RimWorld-Farsi/releases)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Ludeon/RimWorld-Farsi/persianCorrectionPythonBeta.yml?branch=main&label=CI%2FCD&logo=githubactions)](https://github.com/Ludeon/RimWorld-Farsi/actions)
[![Python Version](https://img.shields.io/badge/Python-3.12%20%7C%203.13%20%7C%20PEP%202026-3776AB.svg?logo=python&logoColor=white)](https://peps.python.org/pep-2026/)
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

این بسته ترجمه با نسخه **RimWorld 1.5+** کاملاً سازگار است و از تمام بسته‌های الحاقی رسمی پشتیبانی می‌کند:

| بسته الحاقی (DLC) | وضعیت پشتیبانی | مسیر پوشه مقصد در دایرکتوری بازی |
| :--- | :---: | :--- |
| **RimWorld Core (پایه)** | پشتیبانی کامل | `Data/Core/Languages/Persian` |
| **Royalty DLC** | پشتیبانی کامل | `Data/Royalty/Languages/Persian` |
| **Ideology DLC** | پشتیبانی کامل | `Data/Ideology/Languages/Persian` |
| **Biotech DLC** | پشتیبانی کامل | `Data/Biotech/Languages/Persian` |
| **Anomaly DLC** | پشتیبانی کامل | `Data/Anomaly/Languages/Persian` |
| **Odyssey** | در حال انجام | `Data/Odyssey/Languages/Persian` |

---

## 🚀 راهنمای نصب

روش نصب مناسب برای سیستم خود را انتخاب کنید:

### روش ۱: نصب خودکار در ویندوز (پیشنهادی)

1. فایل [`AutoFaInstall.bat`](AutoFaInstall.bat) را از پوشه اصلی مخزن کپی یا دریافت کنید.
2. آن را در پوشه اصلی نصب بازی قرار دهید (پوشه‌ای که فایل `RimWorldWin64.exe` در آن قرار دارد).
3. روی فایل `AutoFaInstall.bat` دابل‌کلیک کرده و آن را اجرا کنید. این اسکریپت جدیدترین نسخه ترجمه را از گیت‌هاب دانلود کرده و پوشه‌های هر بسته الحاقی را در مسیر درست جایگزین می‌کند.

---

### روش ۲: نصب دستی (تمامی سیستم‌عامل‌ها)

1. فایل آخرین نسخه (`persian.language.zip`) را از [صفحه Releases](https://github.com/Ludeon/RimWorld-Farsi/releases) دانلود کنید.
2. مسیر نصب بازی را در رایانه خود پیدا کنید:
   * **ویندوز:** `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\`
   * **لینوکس:** `~/.steam/steam/steamapps/common/Rimworld/`
   * **مک:** `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app` *(راست‌کلیک و انتخاب "Show Package Contents")*
3. محتوای پوشه‌های فایل زیپ را در پوشه `Languages` متناظر در مسیر `Data/<DLC>/Languages/` کپی کرده و نام آن را `Persian` بگذارید:
   * پوشه `Core` را در `<RimWorld>/Data/Core/Languages/Persian` کپی کنید.
   * پوشه `Royalty` را در `<RimWorld>/Data/Royalty/Languages/Persian` کپی کنید.
   * پوشه `Ideology` را در `<RimWorld>/Data/Ideology/Languages/Persian` کپی کنید.
   * پوشه `Biotech` را در `<RimWorld>/Data/Biotech/Languages/Persian` کپی کنید.
   * پوشه `Anomaly` را در `<RimWorld>/Data/Anomaly/Languages/Persian` کپی کنید.

> [!IMPORTANT]
> اگر از قبل پوشه‌ای با نام `Persian` در این مسیرها وجود دارد، توصیه می‌شود ابتدا آن را حذف کنید تا فایل‌های منسوخ و قدیمی باقی نمانند.
> دقت کنید پوشه `Persian` باید مستقیماً شامل زیرپوشه‌های ترجمه مانند `Keyed` و `DefInjected` و فایل `LanguageInfo.xml` باشد.

---

### روش ۳: نصب پیشرفته توسعه‌دهندگان (لینک‌های نمادین / Symbolic Links)

اگر مخزن را در سیستم خود `clone` کرده‌اید، می‌توانید با پیوند نمادین، تغییرات ترجمه را بدون نیاز به کپی مجدد، به‌صورت لحظه‌ای در بازی مشاهده کنید:

- **ویندوز (Command Prompt به صورت Administrator):**
  ```cmd
  mklink /D "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Languages\Persian" "C:\path\to\RimWorld-Farsi\Data\Core"
  ```
- **لینوکس یا مک:**
  ```bash
  ln -s ~/Documents/github/RimWorld-Farsi/Data/Core ~/.steam/steam/steamapps/common/Rimworld/Data/Core/Languages/Persian
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
   - مجموعه آزمون‌های واحد و یکپارچه در `tools/rtl-processor/tests/` با پشتیبانی کامل از پایتون 3.12، 3.13 و آماده‌سازی برای نسخه تقویمی **PEP 2026**.
2. **مود اختصاصی سی‌شارپ (`mods/RTL_Persian_Support/`)**:
   - پچ هارمونی برای اصلاح بی‌درنگ متون و پشتیبانی بهینه از فونت‌های فارسی در منوهای بازی.
3. **پایپ‌لاین CI/CD گیت‌هاب اکشنز (`.github/workflows/`)**:
   - اجرای آزمون‌های خودکار، فرمت‌بندی کد طبق استانداردهای Black و PEP 8، بررسی نوع‌داده‌ها با Mypy و بسته‌بندی ریلیزها.

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
