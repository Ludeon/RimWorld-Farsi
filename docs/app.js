/**
 * RimWorld-Farsi Documentation Portal Client Application
 * Handles:
 *  - Real-time Interactive Placeholder & Grammar AST Tester
 *  - Searchable Translation Glossary with category filtering
 *  - Multi-platform Installation Tabs
 *  - Theme Toggle (Dark/Light) with localStorage persistence
 *  - Clipboard Copy Actions with Toast Feedback
 */

// 1. Comprehensive Canonical Glossary Dataset
const GLOSSARY_DATA = [
  { en: "Colonist", fa: "استعمارگر", cat: "core", desc: "ساکنان مستعمره بازیکن" },
  { en: "Colony", fa: "مستعمره", cat: "core", desc: "سکونت‌گاه و پایگاه بازیکن" },
  { en: "Pawn", fa: "مهره / فرد / استعمارگر", cat: "core", desc: "اشاره به شخصیت‌ها و کاراکترها در بازی" },
  { en: "Faction", fa: "فرقه / گروه", cat: "core", desc: "جناح‌ها، قبایل و حکومت‌ها" },
  { en: "Mechanoid", fa: "مکانوید", cat: "core", desc: "ربات‌ها و ماشین‌های جنگی خودمختار باستانی" },
  { en: "Raider", fa: "غارتگر", cat: "core", desc: "دشمنان مهاجم و دزدان دریایی" },
  { en: "Trader", fa: "بازرگان / تاجر", cat: "core", desc: "کاروان‌های دادوستد و دادوستدگران مداری" },
  { en: "Caravan", fa: "کاروان", cat: "core", desc: "گروه اعزامی برای سفر روی نقشه جهان" },
  { en: "Hediff", fa: "وضعیت سلامت / عارضه", cat: "core", desc: "بیماری‌ها، جراحت‌ها، ایمپلنت‌ها و حالات بدنی" },
  { en: "Mood", fa: "روحیه", cat: "core", desc: "میزان رضایت و وضعیت روانی پاون‌ها" },
  { en: "Need", fa: "نیاز", cat: "core", desc: "نیازهای پایه‌ای مانند غذا، استراحت و تفریح" },
  { en: "Thought", fa: "فکر / احساس", cat: "core", desc: "بازخوردهای ذهنی و حافظه احساسی مهره‌ها" },
  { en: "Ideoligion", fa: "آیین / باور", cat: "core", desc: "سیستم عقیدتی و مذهبی (بسته گسترش Ideology)" },
  { en: "Psycaster", fa: "روان‌پیما", cat: "core", desc: "استفاده‌کنندگان از توانایی‌های فراروانی (Royalty)" },
  { en: "Xenotype", fa: "گونه ژنتیکی", cat: "core", desc: "نژادها و تغییرات ژنتیکی (بسته گسترش Biotech)" },
  { en: "Anomaly / Entity", fa: "ناهنجاری / ماهیت ناشناخته", cat: "core", desc: "موجودات و پدیده‌های ناشناخته لاوکرافتی (Anomaly)" },
  { en: "Study / Research", fa: "پژوهش / تحقیق", cat: "core", desc: "توسعه فناوری یا بررسی ماهیت‌های ناشناخته" },
  { en: "Blueprint", fa: "طرح اولیه", cat: "core", desc: "نقشه سازه‌ها قبل از پایان ساخت‌وساز" },
  { en: "Drop pod", fa: "کپسول پرتاب", cat: "core", desc: "کپسول‌های فرود و حمل‌ونقل مداری" },
  { en: "Draft", fa: "آماده‌باش نظامی", cat: "core", desc: "تغییر وضعیت کنترل پاون به حالت رزمی مستقیم" },
  
  // Hediffs
  { en: "Blood loss", fa: "خون‌ریزی", cat: "hediff", desc: "کاهش سطح خون ناشی از جراحت باز" },
  { en: "Hypothermia", fa: "سرمازدگی", cat: "hediff", desc: "افت خطرناک دمای مرکزی بدن" },
  { en: "Heatstroke", fa: "گرمازدگی", cat: "hediff", desc: "افزایش خطرناک دمای بدن در اثر حرارت شدید" },
  { en: "Toxic buildup", fa: "مسمومیت سموم", cat: "hediff", desc: "انباشت مواد شیمیایی آلوده در بدن" },
  { en: "Malnutrition", fa: "سوءتغذیه", cat: "hediff", desc: "کمبود مزمن کالری و گرسنگی مفرط" },
  { en: "Bionic arm", fa: "دست بیونیک", cat: "hediff", desc: "اندام مصنوعی پیشرفته با بازدهی بالا" },
  { en: "Bionic eye", fa: "چشم بیونیک", cat: "hediff", desc: "ایمپلنت بینایی با دقت فرابشری" },
  { en: "Carcinoma", fa: "تومور بدخیم", cat: "hediff", desc: "رشد توده سرطانی در بافت‌های بدن" },
  { en: "Plague", fa: "طاعون", cat: "hediff", desc: "بیماری عفونی کشنده و پرسرعت" },
  { en: "Wound infection", fa: "عفونت زخم", cat: "hediff", desc: "تهاجم باکتریایی به زخم مداوا نشده" },

  // Traits
  { en: "Bloodlust", fa: "عطش خون", cat: "trait", desc: "لذت بردن از مشاهده خشونت و کشتار" },
  { en: "Psychopath", fa: "سنگدل / سایکوپات", cat: "trait", desc: "فقدان مطلق حس همدلی با دیگران" },
  { en: "Kind", fa: "مهربان", cat: "trait", desc: "رفتار دلگرم‌کننده با سایر هم‌نوعان" },
  { en: "Hard worker", fa: "سخت‌کوش", cat: "trait", desc: "سرعت بالاتر در انجام کلیه کارهای فیزیکی" },
  { en: "Cannibal", fa: "آدم‌خوار", cat: "trait", desc: "علاقه به مصرف گوشت انسان" },
  { en: "Pyromaniac", fa: "آتش‌افروز", cat: "trait", desc: "شیفتگی بیمارگونه به آتش و اشتعال" },
  { en: "Iron-willed", fa: "فولادین‌اراده", cat: "trait", desc: "مقاومت استثنایی در برابر فشارهای عصبی" },
  { en: "Jogger", fa: "تیزپا", cat: "trait", desc: "سرعت دویدن بالاتر از میانگین" },

  // Capacities
  { en: "Consciousness", fa: "هوشیاری", cat: "capacity", desc: "سطح فعالیت شناختی و ادراک مغز" },
  { en: "Moving", fa: "تحرک", cat: "capacity", desc: "توانایی راه‌رفتن و دویدن روی پاها" },
  { en: "Manipulation", fa: "دستکاری", cat: "capacity", desc: "توانایی استفاده از دست‌ها و ابزارها" },
  { en: "Sight", fa: "بینایی", cat: "capacity", desc: "توانایی دیدن، هدف‌گیری و مسیریابی" },
  { en: "Hearing", fa: "شنوایی", cat: "capacity", desc: "توانایی شنیدن اصوات و برقراری ارتباط" },
  { en: "Breathing", fa: "تنفس", cat: "capacity", desc: "عملکرد ریه‌ها در تبادل اکسیژن" },
  { en: "Blood filtration", fa: "تصفیه خون", cat: "capacity", desc: "توانایی کلیه‌ها و کبد در مبارزه با سموم" },
  { en: "Blood pumping", fa: "گردش خون", cat: "capacity", desc: "عملکرد قلب در پمپاژ خون به بافت‌ها" }
];

// 2. DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabs();
  initPlayground();
  initGlossary();
  initCopyButtons();
});

// 3. Theme Toggle Engine
function initTheme() {
  const themeToggleBtn = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('rw_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('rw_theme', newTheme);
      updateThemeIcon(newTheme);
      showToast(`حالت ${newTheme === 'dark' ? 'تاریک' : 'روشن'} فعال شد.`);
    });
  }
}

function updateThemeIcon(theme) {
  const iconSpan = document.getElementById('themeIcon');
  if (iconSpan) {
    iconSpan.textContent = theme === 'dark' ? '🌙' : '☀️';
  }
}

// 4. Tab Engine
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      const parentContainer = btn.closest('.tab-container');
      
      // Update buttons in this container
      parentContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Update contents
      parentContainer.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });
}

// 5. Interactive Placeholder & Grammar Playground Engine
function initPlayground() {
  const inputArea = document.getElementById('playgroundInput');
  const tokensList = document.getElementById('tokensList');
  const grammarStatus = document.getElementById('grammarStatus');
  const typographyStatus = document.getElementById('typographyStatus');
  const typoAlerts = document.getElementById('typoAlerts');

  if (!inputArea) return;

  function runDiagnostics() {
    const text = inputArea.value;
    
    // 5.1 Parse Placeholders {...}
    const tokenRegex = /\{([^}]+)\}/g;
    const tokens = [];
    let match;
    let hasMalformedToken = false;

    // Check for unclosed '{'
    const openBraces = (text.match(/\{/g) || []).length;
    const closeBraces = (text.match(/\}/g) || []).length;
    if (openBraces !== closeBraces) {
      hasMalformedToken = true;
    }

    while ((match = tokenRegex.exec(text)) !== null) {
      const rawToken = match[1].trim();
      let tokenType = "متغیر ساده";
      
      if (/^\d+(_\w+)?$/.test(rawToken)) {
        tokenType = "شاخص موقعیتی (Positional)";
      } else if (rawToken.includes('?')) {
        tokenType = "شرط چندشاخه (Conditional)";
        const parts = rawToken.split('?');
        const branches = parts[1] ? parts[1].split(':') : [];
        if (branches.length === 2 && branches[0].trim() === branches[1].trim()) {
          hasMalformedToken = true;
          tokenType = "⚠️ خطای شاخه‌های شرطی یکسان";
        }
      } else if (rawToken.startsWith('lookup:') || rawToken.startsWith('ezafeh:')) {
        tokenType = "تابع گرامری (Macro Function)";
      } else if (/^[A-Z_]+/.test(rawToken)) {
        tokenType = "متغیر اسمی (Named Variable)";
      }
      
      tokens.push({ raw: `{${rawToken}}`, type: tokenType });
    }

    // Render Tokens
    if (tokensList) {
      if (tokens.length === 0) {
        tokensList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 0.5rem;">هیچ نشانگر گرامری یافت نشد.</div>';
      } else {
        tokensList.innerHTML = tokens.map(t => `
          <div class="token-row">
            <span class="token-key">${escapeHtml(t.raw)}</span>
            <span class="token-type">${t.type}</span>
          </div>
        `).join('');
      }
    }

    // Update Grammar Status
    if (grammarStatus) {
      if (hasMalformedToken) {
        grammarStatus.className = 'status-badge error';
        grammarStatus.textContent = '❌ ساختار نامعتبر';
      } else if (tokens.length > 0) {
        grammarStatus.className = 'status-badge valid';
        grammarStatus.textContent = '✅ معتبر و استاندارد';
      } else {
        grammarStatus.className = 'status-badge valid';
        grammarStatus.textContent = 'متن بدون نشانگر';
      }
    }

    // 5.2 Typography & Persian Linter Diagnostics
    const issues = [];
    
    // Arabic Codepoints
    if (text.includes('\u0643')) {
      issues.push("حرف عربی 'ك' (U+0643) شناسایی شد؛ باید با 'ک' فارسی جایگزین شود.");
    }
    if (text.includes('\u064A')) {
      issues.push("حرف عربی 'ي' (U+064A) شناسایی شد؛ باید با 'ی' فارسی جایگزین شود.");
    }
    
    // English Punctuation next to Persian
    if (/[\u0600-\u06FF],/.test(text)) {
      issues.push("ویرگول انگلیسی ',' شناسایی شد؛ از ویرگول فارسی '،' استفاده کنید.");
    }
    if (/[\u0600-\u06FF]\?/.test(text)) {
      issues.push("علامت سؤال لاتین '?' در متن فارسی شناسایی شد؛ از '؟' استفاده کنید.");
    }
    if (/[\u0600-\u06FF];/.test(text)) {
      issues.push("نقطه‌ویرگول لاتین ';' شناسایی شد؛ از '؛' فارسی استفاده کنید.");
    }

    // ZWNJ for verbal prefixes
    if (/(^|\s)می\s+[\u0600-\u06FF]/.test(text)) {
      issues.push("پیشوند 'می' بدون نیم‌فاصله شناسایی شد (از نیم‌فاصله استفاده شود: مانند 'می‌رود').");
    }
    if (/(^|\s)نمی\s+[\u0600-\u06FF]/.test(text)) {
      issues.push("پیشوند 'نمی' بدون نیم‌فاصله شناسایی شد (از نیم‌فاصله استفاده شود: مانند 'نمی‌تواند').");
    }

    // Render Typography Status
    if (typographyStatus && typoAlerts) {
      if (issues.length === 0) {
        typographyStatus.className = 'status-badge valid';
        typographyStatus.textContent = '✅ تایپوگرافی پاک';
        typoAlerts.innerHTML = '<div style="color: var(--accent-emerald); font-size: 0.85rem; padding: 0.5rem;">عاری از حروف عربی و خطاهای نشانه‌گذاری و نیم‌فاصله.</div>';
      } else {
        typographyStatus.className = 'status-badge error';
        typographyStatus.textContent = `⚠️ ${issues.length} ایراد ویرایشی`;
        typoAlerts.innerHTML = issues.map(iss => `
          <div style="color: var(--accent-rose); font-size: 0.82rem; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.4rem;">
            <span>•</span> ${iss}
          </div>
        `).join('');
      }
    }
  }

  inputArea.addEventListener('input', runDiagnostics);
  runDiagnostics(); // initial run

  // Preset Chips
  document.querySelectorAll('.preset-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const preset = chip.getAttribute('data-preset');
      if (preset === 'gender') {
        inputArea.value = "استعمارگر {0_nameDef} به {1_label} نگاه کرده و {PAWN_gender ? با او سخن گفت : به او پاسخ داد}.";
      } else if (preset === 'pos') {
        inputArea.value = "کاروان حامل {0} بسته دارو به رهبری {1} به سلامت وارد مستعمره شد.";
      } else if (preset === 'macro') {
        inputArea.value = "درمان با استفاده از {lookup: {0_label}; ezafeh; 1} با موفقیت به پایان رسید.";
      } else if (preset === 'arabic_error') {
        inputArea.value = "كلونيست به ديدار يار رفت , آيا او ميتواند كمك كند?";
      } else if (preset === 'zwnj_error') {
        inputArea.value = "استعمارگر می رود تا ساختمان ها را بررسی کند.";
      }
      runDiagnostics();
      showToast('نمونه آزمایشی بارگذاری شد.');
    });
  });
}

// 6. Interactive Glossary Search Engine
function initGlossary() {
  const searchInput = document.getElementById('glossarySearch');
  const tableBody = document.getElementById('glossaryBody');
  const chips = document.querySelectorAll('.category-chip');
  let currentCategory = 'all';

  if (!tableBody) return;

  function renderTable() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    
    const filtered = GLOSSARY_DATA.filter(item => {
      const matchesCategory = currentCategory === 'all' || item.cat === currentCategory;
      const matchesQuery = !query || 
        item.en.toLowerCase().includes(query) || 
        item.fa.toLowerCase().includes(query) || 
        item.desc.toLowerCase().includes(query);
      return matchesCategory && matchesQuery;
    });

    if (filtered.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 2rem;">
            هیچ اصطلاحی با عبارت جستجوشده یافت نشد.
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = filtered.map(item => `
      <tr>
        <td style="font-weight: 700; color: var(--accent-amber);">${escapeHtml(item.fa)}</td>
        <td class="font-latin" style="color: var(--accent-cyan);">${escapeHtml(item.en)}</td>
        <td><span class="badge-tag">${getCategoryLabel(item.cat)}</span></td>
        <td>
          <button class="btn-copy" onclick="copyDefSnippet('${escapeHtml(item.en)}', '${escapeHtml(item.fa)}')">
            کپی تگ Def
          </button>
        </td>
      </tr>
    `).join('');
  }

  if (searchInput) {
    searchInput.addEventListener('input', renderTable);
  }

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentCategory = chip.getAttribute('data-cat');
      renderTable();
    });
  });

  renderTable(); // initial render
}

function getCategoryLabel(cat) {
  switch (cat) {
    case 'core': return 'واژه کلیدی';
    case 'hediff': return 'عارضه / سلامت';
    case 'trait': return 'ویژگی شخصیتی';
    case 'capacity': return 'توانمندی پاون';
    default: return 'سایر';
  }
}

// 7. Clipboard Utilities
function initCopyButtons() {
  document.querySelectorAll('.btn-code-copy').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const targetElem = document.getElementById(targetId);
      if (targetElem) {
        copyToClipboard(targetElem.innerText.trim());
      }
    });
  });
}

window.copyDefSnippet = function(en, fa) {
  const snippet = `<label>${fa}</label> <!-- EN: ${en} -->`;
  copyToClipboard(snippet);
  showToast(`تگ XML کپی شد: ${fa}`);
};

window.copyText = function(text) {
  copyToClipboard(text);
  showToast('دستور در کلیپ‌بورد کپی شد!');
};

function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text);
  } else {
    const tempInput = document.createElement('textarea');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
  }
}

function showToast(message) {
  let toast = document.getElementById('appToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'appToast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
}
