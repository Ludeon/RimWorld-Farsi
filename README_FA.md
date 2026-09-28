# ترجمه فارسی رسمی بازی RimWorld

<div align="center">

[![RimWorld Version](https://img.shields.io/badge/RimWorld-1.5%2B-blue.svg?logo=steam)](https://rimworldgame.com/)
[![Latest Release](https://img.shields.io/github/v/release/Ludeon/RimWorld-Farsi?color=success&logo=github)](https://github.com/Ludeon/RimWorld-Farsi/releases)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Ludeon/RimWorld-Farsi/persianCorrectionPythonBeta.yml?branch=main&label=CI%2FCD&logo=githubactions)](https://github.com/Ludeon/RimWorld-Farsi/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

**[English Documentation (README.md)](README.md)**

</div>

---

این مخزن شامل **بسته رسمی ترجمه فارسی بازی RimWorld** است که با پشتیبانی استودیوی **Ludeon** ایجاد شده و توسط جامعه بازیکنان و مترجمان فارسی‌زبان به‌طور مداوم نگه‌داری و توسعه داده می‌شود.

---

## 📚 مرکز راهنماها و مستندات پروژه

برای دسترسی سریع به راهنماهای تخصصی، از جدول زیر استفاده کنید:

| راهنما | توضیحات | مخاطب |
| :--- | :--- | :--- |
| 📖 **[راهنمای شیوه‌نامه ترجمه](docs/TRANSLATION_GUIDE.md)** | اصول حروف‌چینی فارسی (`ک`/`ی`)، نیم‌فاصله (ZWNJ)، متغیرها (`{0}`) و واژه‌نامه تخصصی اصطلاحات بازی. | مترجمان و بازبین‌ها |
| 🧠 **[چالش‌های فنی و موتور بازی](docs/TECHNICAL_CHALLENGES.md)** | چرایی عدم پشتیبانی بومی Unity IMGUI از متن‌های راست‌به‌چپ (RTL)، جدایی حروف و معماری راه‌حل دولایه. | توسعه‌دهندگان و مادنویسان |
| 🛠️ **[گردش کار توسعه و ابزارها](docs/DEVELOPER_WORKFLOW.md)** | راه‌اندازی محیط مدرن پایتون با `uv`، هوک‌های pre-commit، تست‌ها و اسکریپت همگام‌سازی `./tools/sync.sh`. | توسعه‌دهندگان پایتون و ابزارها |
| 📊 **[پیشرفت ترجمه بسته‌ها (TODO)](docs/TODO.md)** | وضعیت خط به خط ترجمه بسته اصلی و تمامی بسته‌های الحاقی (DLC). | عموم کاربران |
| 🤝 **[راهنمای مشارکت (Contributing)](CONTRIBUTING.md)** | قواعد شاخه‌بندی گیت، استاندارد پیام‌های کامیت و فرآیند ارسال Pull Request. | تمامی مشارکت‌کنندگان |

---

## ⚡ نصب آسان و سریع (۱ کلیک)

### روش ۱: نصب خودکار با اسکریپت‌های هوشمند (پیشنهادی)

* **ویندوز**:
  1. مخزن را دریافت یا کلون کنید.
  2. روی فایل [`install.bat`](install.bat) دوبار کلیک کنید. این اسکریپت به‌صورت هوشمند محل نصب استیم یا ریم‌ورلد را شناسایی کرده (یا در صورت نیاز پنجره انتخاب پوشه را باز می‌کند)، ترجمه‌ها را کپی نموده و فایل‌های کش زبان (`.tar`) را پاکسازی می‌کند.
* **لینوکس / استیم‌دک (Steam Deck)**:
  1. یک ترمینال در پوشه پروژه باز کنید.
  2. دستور `./install.sh` را اجرا نمایید.

---

### روش ۲: نصب دستی (تمامی سیستم‌عامل‌ها)

1. فایل آخرین نسخه (`persian.language.zip`) را از [صفحه انتشارها (Releases)](https://github.com/Ludeon/RimWorld-Farsi/releases) دانلود کنید.
2. مسیر نصب بازی را در رایانه خود باز کنید:
   * **ویندوز:** `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\`
   * **لینوکس:** `~/.steam/steam/steamapps/common/Rimworld/`
   * **مک:** `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app`
3. محتویات پوشه‌های هر ماژول (`Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly`, `Odyssey`) را در مسیر متناظر آن در بازی کپی کنید:  
   `<RimWorld>/Data/<DLC>/Languages/Persian (فارسی)`
4. در صورت وجود هرگونه فایل با نام `Persian (فارسی).tar` در آن پوشه‌ها، آن را حذف کنید تا بازی مستقیماً فایل‌های ترجمه جدید را بخواند.

---

## ⚙️ فعال‌سازی درون بازی

1. بازی **RimWorld** را اجرا کنید.
2. در منوی اصلی، وارد منوی **تنظیمات (Options)** یا آیکون **پرچم زبان** شوید.
3. زبان **Persian (فارسی)** را انتخاب کنید. رابط کاربری بلافاصله به زبان فارسی تغییر خواهد کرد.

> [!TIP]
> **سازگاری ۱۰۰٪ با فایل‌های ذخیره (Save Game)**: نصب یا حذف این بسته زبان هیچ‌گونه تغییری در منطق بازی ایجاد نکرده و به هیچ عنوان به سیوهای قبلی آسیب نمی‌رساند.

---

## 📦 جدول سازگاری و وضعیت بسته‌های الحاقی (DLC)

| بسته الحاقی (DLC) | وضعیت | مسیر در مخزن | مسیر مقصد در بازی |
| :--- | :---: | :---: | :--- |
| **RimWorld Core (پایه)** | پشتیبانی کامل | `Core/` | `<RimWorld>/Data/Core/Languages/Persian (فارسی)` |
| **Royalty DLC** | پشتیبانی کامل | `Royalty/` | `<RimWorld>/Data/Royalty/Languages/Persian (فارسی)` |
| **Ideology DLC** | پشتیبانی کامل | `Ideology/` | `<RimWorld>/Data/Ideology/Languages/Persian (فارسی)` |
| **Biotech DLC** | پشتیبانی کامل | `Biotech/` | `<RimWorld>/Data/Biotech/Languages/Persian (فارسی)` |
| **Anomaly DLC** | پشتیبانی کامل | `Anomaly/` | `<RimWorld>/Data/Anomaly/Languages/Persian (فارسی)` |
| **Odyssey** | در حال انجام | `Odyssey/` | `<RimWorld>/Data/Odyssey/Languages/Persian (فارسی)` |

---

## 🖼️ پیش‌نمایش محیط بازی

<div align="center">
  <img src="https://github.com/user-attachments/assets/87633f91-a012-4567-8f07-15aec21a4be2" alt="RimWorld Persian Translation Screenshot" width="850" />
</div>

---

## 🧩 نکات معماری و چالش‌های متن راست‌به‌چپ (RTL)

رابط کاربری ریم‌ورلد با استفاده از **Unity IMGUI** پیاده‌سازی شده است و فاقد سیستم مدرن Text Mesh است:

> *"RimWorld uses IMGUI. There are no text meshes."*  
> — **تاینان سیلوستر (Tynan Sylvester)**، خالق ریم‌ورلد ([مسئله ۱۱ مخزن عربی](https://github.com/Ludeon/RimWorld-ar/issues/11))

به دلیل نبود موتور اتصال حروف (Shaping) و چینش راست‌به‌چپ در IMGUI، حروف فارسی به صورت جدا از هم (`پ ا ر س ی`) و معکوس رندر می‌شوند. برای حل این مشکل، این پروژه از یک **معماری دولایه** بهره می‌برد:
1. **پیش‌پردازش استاتیک فرم‌های یونی‌کد (`tools/rtl-processor/`)**: تبدیل حروف به اَشکال متصل استاندارد (Unicode Presentation Forms-B) و معکوس‌سازی ترتیب کلمات برای سازگاری کامل با بازی خالص بدون نیاز به مد.
2. **پچ زمان اجرا هارمونی (`mods/RTL_Persian_Support/`)**: هوک کردن متدهای `GUI.Label` در حافظه برای تصحیح نام‌های متغیر مهره‌ها، متن‌های پویای نبرد و جایگزینی قلم بازی (`IranianSans.ttf`).

برای مطالعه تحلیل کامل فنی، به **[docs/TECHNICAL_CHALLENGES.md](docs/TECHNICAL_CHALLENGES.md)** مراجعه نمایید.

---

## 🚫 بخش‌هایی که به انگلیسی باقی مانده‌اند

برای حفظ سازگاری با مادها و جلوگیری از باگ‌های بازی:
- **اسامی پیش‌فرض شخصیت‌ها و عناوین فکشن‌ها**: در بخش‌هایی که بازی کلید ترجمه برای آن‌ها ندارد به زبان اصلی باقی مانده‌اند.
- **حالت توسعه‌دهنده (Developer Mode) و لاگ‌های خطا**: جهت امکان عیب‌یابی فنی دست‌نخورده باقی مانده‌اند.
- **شناسه کلیدهای میانبر (Keybindings)**: برای تطابق با صفحه‌کلیدهای فیزیکی به انگلیسی حفظ شده‌اند.
- **تیتراژ سازندگان اصلی بازی**: برای احترام به توسعه‌دهندگان اولیه دست‌نخورده باقی مانده است.

---

## 🏆 مشارکت‌کنندگان و قدردانی

### مدیر پروژه و مترجم اصلی
* **دانیال پهلوان** ([@DanialPahlavan](https://github.com/DanialPahlavan))

### مشارکت‌کنندگان پیشین
* **سید عبداللهی** ([@SeyedAbdollahi](https://github.com/SeyedAbdollahi))

### قدردانی‌ها
* **استودیوی Ludeon** برای خلق دنیای شگفت‌انگیز RimWorld و پشتیبانی از جامعه ترجمه.
* **@mtimoustafa** و **@asidsx** برای پیشگامی در توسعه ابزارهای اصلاح RTL در RimWorld ([Ludeon/RimWorld-ar#13](https://github.com/Ludeon/RimWorld-ar/issues/13)).

---

## 📜 پروانه (License)

این پروژه متن‌باز بوده و تحت مجوز **GNU General Public License v3.0** منتشر شده است. برای اطلاعات بیشتر فایل [LICENSE](LICENSE) را مشاهده کنید.
