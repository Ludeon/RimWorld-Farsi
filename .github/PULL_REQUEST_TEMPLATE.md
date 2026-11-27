## 📝 خلاصه تغییرات (Summary of Changes)
<!-- لطفاً خلاصه‌ای از تغییرات خود، پرونده‌های اصلاح شده و دلیل آن را ذکر کنید. توجه: PRها را روی شاخه beta باز کنید. -->

## 🔍 انگیزه و زمینه (Motivation / Context)
<!-- این تغییر کدام Issue یا مشکل داخل بازی را حل می‌کند؟ (Fixes #...) -->

## 📦 بخش‌های تغییر یافته (Modified Components)
- [ ] `Core` / `Royalty` / `Ideology` / `Biotech` / `Anomaly` / `Odyssey` (XML)
- [ ] `mods/RTL_Persian_Support` (C# / Fonts)
- [ ] `tools/` / `.github/` / Installers (`install.bat`, `install.sh`)
- [ ] مستندات (`README*`, `docs/`)

---

## ✅ چک‌لیست الزامی پیش از ارسال (Mandatory PR Checklist)

لطفاً پیش از باز کردن درخواست ادغام (PR) روی شاخه `beta`، تمام موارد زیر را بررسی و علامت بزنید:

- [ ] اجرای موفق سامانه تضمین کیفیت ۵گانه محلی (`python tools/qa/run_qa.py`).
- [ ] اجرای تست‌های واحد پایتون (`pytest`) و تست/بیلد C# در صورت تغییر کد (`dotnet test mods/RTL_Persian_Support/Tests/RTL_Persian_Support.Tests.csproj`).
- [ ] حفظ کامل و دست‌نخورده متغیرها و براکت‌های قالب‌بندی (`{0}`, `{1}`, `{PAWN_nameDef}`).
- [ ] استفاده از کاراکترهای استاندارد فارسی (`ک` U+06A9 و `ی` U+06CC به جای ك و ي عربی).
- [ ] رعایت علائم نگارشی فارسی (`،` و `؛` و `؟`).
- [ ] رعایت فاصله مجازی (ZWNJ) برای پیشوندهای فعلی (`می‌`/`نمی‌`) و جمع (`ها`).
- [ ] عدم وجود نقطه در پایان تگ‌های `reportString` (وظایف پاون‌ها).
- [ ] همخوانی با واژه‌نامه مرجع ریم‌ورلد در [`AGENTS.md`](../AGENTS.md).
