using System;
using System.IO;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;
using RimWorld;

namespace RTL_Persian
{
    [StaticConstructorOnStartup]
    public class RTL_Support
    {
        public static Font PersianFont;
        public static Font OriginalFont;
        private static ModContentPack _contentPack;

        // Cached Font Assets
        private static Font _vazirmatnFont;
        private static Font _iranianSansFont;
        private static Font _osFont;

        // Cached Base Font Sizes for Scaling
        private static int[] _baseFontSizes;
        private static int[] _baseTextFieldFontSizes;
        private static int[] _baseTextAreaFontSizes;
        private static int[] _baseTextAreaReadOnlyFontSizes;

        // Flags to manage updates and safety
        public static bool dirty = true;
        public static bool suppressAnchorPatch = false;

        // Debug Log Path
        private static string _logFilePath;
        private static readonly object _logLock = new object();

        static RTL_Support()
        {
            // 1. Identify the Mod Pack
            _contentPack = LoadedModManager.RunningMods.FirstOrDefault(m => m.PackageId.ToLower() == "danial.rtlpersiansupport");

            if (_contentPack == null)
            {
                Log.Error("RTL_Persian_Support: Could not find own ModContentPack.");
                return;
            }

            // 2. Initialize Logging
            InitDebugLog();
            LogFile("RTL_Persian_Support initialized.");

            // 3. Log Active Mods
            LogLoadedMods();

            // 4. Load Fonts
            LoadPersianFont();

            // 5. Apply Harmony Patches
            try
            {
                var harmony = new Harmony("danial.rtlpersiansupport");
                harmony.PatchAll(Assembly.GetExecutingAssembly());
                LogFile("Harmony patches applied successfully.");
            }
            catch (Exception ex)
            {
                LogFile($"CRITICAL ERROR: Harmony patching failed: {ex}");
                Log.Error($"RTL Harmony Error: {ex}");
            }
        }

        public static void LoadPersianFont()
        {
            try
            {
                LogFile("Loading Persian fonts...");

                // Method 1: Try loading Vazirmatn.ttf (modern UI typeface)
                _vazirmatnFont = LoadFontFile("Vazirmatn.ttf");

                // Method 2: Try loading IranianSans.ttf (classic typeface)
                _iranianSansFont = LoadFontFile("IranianSans.ttf");

                // Method 3: Try loading from AssetBundle if available
                if (_vazirmatnFont == null && _iranianSansFont == null)
                {
                    _vazirmatnFont = LoadFontFromAssetBundle("persianfont");
                }

                // Method 4: Fallback to OS installed Persian / Arabic fonts
                _osFont = LoadOSFont();

                // Select active font according to user settings
                UpdateSelectedFont();

                if (PersianFont != null)
                {
                    LogFile($"Active Persian font ready: {PersianFont.name}");
                }
                else
                {
                    Log.Warning("[RTL Support] Could not load any Persian font. UI will use default game font.");
                }
            }
            catch (Exception e)
            {
                Log.Error($"[RTL Support] Error loading font: {e.Message}");
                LogFile($"EXCEPTION while loading font: {e}");
            }
        }

        private static Font LoadFontFile(string filename)
        {
            try
            {
                string fontPath = Path.Combine(_contentPack.RootDir, filename);
                if (!File.Exists(fontPath))
                {
                    LogFile($"Font file {filename} not found at {fontPath}");
                    return null;
                }

                MethodInfo createFontFromPath = typeof(Font).GetMethod("Internal_CreateFontFromPath", BindingFlags.NonPublic | BindingFlags.Static);
                if (createFontFromPath != null)
                {
                    Font font = new Font();
                    createFontFromPath.Invoke(null, new object[] { font, fontPath });
                    font.name = Path.GetFileNameWithoutExtension(filename);
                    LogFile($"Successfully loaded font from TTF at {fontPath}");
                    return font;
                }
                else
                {
                    LogFile("Internal_CreateFontFromPath method not found on UnityEngine.Font.");
                }
            }
            catch (Exception ex)
            {
                LogFile($"Internal_CreateFontFromPath failed for {filename}: {ex.Message}");
            }
            return null;
        }

        private static Font LoadFontFromAssetBundle(string bundleName)
        {
            try
            {
                string bundlePath = Path.Combine(_contentPack.RootDir, "Resources", bundleName);
                if (File.Exists(bundlePath))
                {
                    AssetBundle bundle = AssetBundle.LoadFromFile(bundlePath);
                    if (bundle != null)
                    {
                        Font font = bundle.LoadAllAssets<Font>().FirstOrDefault();
                        bundle.Unload(false);
                        LogFile($"Font loaded from AssetBundle {bundleName}");
                        return font;
                    }
                }
            }
            catch (Exception ex)
            {
                LogFile($"AssetBundle {bundleName} load failed: {ex.Message}");
            }
            return null;
        }

        private static Font LoadOSFont()
        {
            try
            {
                string[] fontCandidates = new string[] { "Vazirmatn", "Iranian Sans", "Tahoma", "Arial", "DejaVu Sans", "Segoe UI" };
                Font font = Font.CreateDynamicFontFromOSFont(fontCandidates, 16);
                if (font != null)
                {
                    font.name = "OS_Dynamic_Persian";
                    LogFile("Persian font dynamically created from OS fonts fallback.");
                    return font;
                }
            }
            catch (Exception ex)
            {
                LogFile($"OS font fallback failed: {ex.Message}");
            }
            return null;
        }

        public static void UpdateSelectedFont()
        {
            Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
            PersianFontChoice choice = mod?.settings?.selectedFont ?? PersianFontChoice.Vazirmatn;

            switch (choice)
            {
                case PersianFontChoice.IranianSans:
                    PersianFont = _iranianSansFont ?? _vazirmatnFont ?? _osFont;
                    break;
                case PersianFontChoice.SystemDefault:
                    PersianFont = _osFont ?? _vazirmatnFont ?? _iranianSansFont;
                    break;
                case PersianFontChoice.Vazirmatn:
                default:
                    PersianFont = _vazirmatnFont ?? _iranianSansFont ?? _osFont;
                    break;
            }
        }

        private static void CacheBaseFontSizes()
        {
            if (_baseFontSizes == null && Text.fontStyles != null)
            {
                _baseFontSizes = new int[Text.fontStyles.Length];
                for (int i = 0; i < Text.fontStyles.Length; i++)
                {
                    _baseFontSizes[i] = Text.fontStyles[i]?.fontSize ?? 0;
                }
            }
            if (_baseTextFieldFontSizes == null && Text.textFieldStyles != null)
            {
                _baseTextFieldFontSizes = new int[Text.textFieldStyles.Length];
                for (int i = 0; i < Text.textFieldStyles.Length; i++)
                {
                    _baseTextFieldFontSizes[i] = Text.textFieldStyles[i]?.fontSize ?? 0;
                }
            }
            if (_baseTextAreaFontSizes == null && Text.textAreaStyles != null)
            {
                _baseTextAreaFontSizes = new int[Text.textAreaStyles.Length];
                for (int i = 0; i < Text.textAreaStyles.Length; i++)
                {
                    _baseTextAreaFontSizes[i] = Text.textAreaStyles[i]?.fontSize ?? 0;
                }
            }
            if (_baseTextAreaReadOnlyFontSizes == null && Text.textAreaReadOnlyStyles != null)
            {
                _baseTextAreaReadOnlyFontSizes = new int[Text.textAreaReadOnlyStyles.Length];
                for (int i = 0; i < Text.textAreaReadOnlyStyles.Length; i++)
                {
                    _baseTextAreaReadOnlyFontSizes[i] = Text.textAreaReadOnlyStyles[i]?.fontSize ?? 0;
                }
            }
        }

        private static void ApplyStyleFontsAndSizes(GUIStyle[] styles, int[] baseSizes, Font font, float scale)
        {
            if (styles == null) return;
            for (int i = 0; i < styles.Length; i++)
            {
                if (styles[i] == null) continue;
                if (font != null)
                {
                    styles[i].font = font;
                }
                if (baseSizes != null && i < baseSizes.Length && baseSizes[i] > 0)
                {
                    styles[i].fontSize = Mathf.RoundToInt(baseSizes[i] * scale);
                }
            }
        }

        public static void ApplyChanges()
        {
            if (GUI.skin == null) return;

            CacheBaseFontSizes();

            bool isPersian = LanguageDatabase.activeLanguage?.folderName == "Persian";
            LogFile($"Applying GUI changes. IsPersian: {isPersian}");

            Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
            bool enableFont = mod == null || mod.settings.enablePersianFont;
            bool enableRTL = mod != null && mod.settings.enableRTLAlignment;
            float fontScale = mod?.settings?.fontScale ?? 1.0f;

            if (isPersian)
            {
                if (enableRTL)
                {
                    GUI.skin.label.alignment = TextAnchor.UpperRight;
                    GUI.skin.button.alignment = TextAnchor.UpperRight;
                    GUI.skin.textField.alignment = TextAnchor.UpperRight;
                    GUI.skin.textArea.alignment = TextAnchor.UpperRight;
                }

                if (enableFont)
                {
                    UpdateSelectedFont();
                    if (PersianFont != null)
                    {
                        if (OriginalFont == null && Text.fontStyles != null && Text.fontStyles.Length > 0 && Text.fontStyles[0] != null)
                        {
                            OriginalFont = Text.fontStyles[0].font;
                        }
                        SetGameFont(PersianFont, fontScale);
                    }
                }
            }
            else
            {
                GUI.skin.label.alignment = TextAnchor.UpperLeft;
                GUI.skin.button.alignment = TextAnchor.UpperLeft;
                GUI.skin.textField.alignment = TextAnchor.UpperLeft;
                GUI.skin.textArea.alignment = TextAnchor.UpperLeft;

                if (OriginalFont != null)
                {
                    SetGameFont(OriginalFont, 1.0f);
                }
            }
        }

        private static readonly FieldInfo _fontsField = typeof(Text).GetField("fonts", BindingFlags.NonPublic | BindingFlags.Static);

        private static void SetGameFont(Font font, float scale = 1.0f)
        {
            if (font == null) return;

            if (_fontsField != null)
            {
                Font[] fontsArr = (Font[])_fontsField.GetValue(null);
                if (fontsArr != null)
                {
                    for (int i = 0; i < fontsArr.Length; i++)
                    {
                        fontsArr[i] = font;
                    }
                }
            }

            ApplyStyleFontsAndSizes(Text.fontStyles, _baseFontSizes, font, scale);
            ApplyStyleFontsAndSizes(Text.textFieldStyles, _baseTextFieldFontSizes, font, scale);
            ApplyStyleFontsAndSizes(Text.textAreaStyles, _baseTextAreaFontSizes, font, scale);
            ApplyStyleFontsAndSizes(Text.textAreaReadOnlyStyles, _baseTextAreaReadOnlyFontSizes, font, scale);
        }

        private static void InitDebugLog()
        {
            try
            {
                _logFilePath = Path.Combine(_contentPack.RootDir, "error.log");
                File.WriteAllText(_logFilePath, $"--- RTL Persian Support Error Log ---\nTime: {DateTime.Now}\nVersion: RimWorld 1.6\n\n");
                Application.logMessageReceived += HandleLog;
                Log.Message($"[RTL Support] Logging to: {_logFilePath}");
            }
            catch (UnauthorizedAccessException)
            {
                string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                _logFilePath = Path.Combine(desktopPath, "RTL_Persian_Error.log");
                try
                {
                    File.WriteAllText(_logFilePath, $"--- RTL Persian Support Error Log (Fallback) ---\nTime: {DateTime.Now}\n\n");
                    Application.logMessageReceived += HandleLog;
                    Log.Warning($"[RTL Support] Could not write to mod folder. Logging to Desktop instead: {_logFilePath}");
                }
                catch { _logFilePath = null; }
            }
            catch (Exception e)
            {
                Log.Warning($"[RTL Support] Logging initialization failed: {e.Message}");
            }
        }

        private static void HandleLog(string logString, string stackTrace, LogType type)
        {
            if (string.IsNullOrEmpty(_logFilePath)) return;

            lock (_logLock)
            {
                try
                {
                    using (StreamWriter writer = new StreamWriter(_logFilePath, true))
                    {
                        writer.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{type}] {logString}");
                        if (type == LogType.Exception || type == LogType.Error || type == LogType.Assert)
                        {
                            writer.WriteLine(stackTrace);
                        }
                    }
                }
                catch { }
            }
        }

        public static void LogFile(string message)
        {
            if (string.IsNullOrEmpty(_logFilePath)) return;

            lock (_logLock)
            {
                try
                {
                    using (StreamWriter writer = new StreamWriter(_logFilePath, true))
                    {
                        writer.WriteLine($"[{DateTime.Now:HH:mm:ss}] [Info] {message}");
                    }
                }
                catch { }
            }
        }

        private static void LogLoadedMods()
        {
            LogFile("--- Active Mod List ---");
            foreach (var mod in LoadedModManager.RunningMods)
            {
                LogFile($"- {mod.Name} [{mod.PackageId}]");
            }
            LogFile("-----------------------");
        }
    }

    // Patch 1: Trigger update when language changes
    [HarmonyPatch(typeof(LanguageDatabase), "SelectLanguage")]
    public static class Patch_SelectLanguage
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            RTL_Support.LogFile("Language changed.");
            RTL_Support.dirty = true;
            PersianFixer.ClearCache();
        }
    }

    // Patch 2: Apply changes safely at the start of the GUI loop
    [HarmonyPatch(typeof(Text), "StartOfOnGUI")]
    public static class Patch_StartOfOnGUI
    {
        [HarmonyPrefix]
        public static void Prefix()
        {
            if (Text.Anchor != TextAnchor.UpperLeft)
            {
                RTL_Support.suppressAnchorPatch = true;
                Text.Anchor = TextAnchor.UpperLeft;
                RTL_Support.suppressAnchorPatch = false;
            }
        }

        [HarmonyPostfix]
        public static void Postfix()
        {
            if (RTL_Support.dirty)
            {
                RTL_Support.ApplyChanges();
                RTL_Support.dirty = false;
            }
        }
    }

    // Patch 3: Force RTL alignment logic for Text widgets
    [HarmonyPatch(typeof(Text), "Anchor", MethodType.Setter)]
    public static class Patch_TextAnchor
    {
        [HarmonyPrefix]
        public static void Prefix(ref TextAnchor value)
        {
            if (RTL_Support.suppressAnchorPatch) return;

            if (LanguageDatabase.activeLanguage?.folderName == "Persian")
            {
                Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                if (mod != null && mod.settings.enableRTLAlignment)
                {
                    switch (value)
                    {
                        case TextAnchor.UpperLeft: value = TextAnchor.UpperRight; break;
                        case TextAnchor.MiddleLeft: value = TextAnchor.MiddleRight; break;
                        case TextAnchor.LowerLeft: value = TextAnchor.LowerRight; break;
                    }
                }
            }
        }
    }

    // Patch 4: Cleanly reset Anchor at frame boundary in UIRoot
    [HarmonyPatch(typeof(UIRoot), "UIRootOnGUI")]
    public static class Patch_UIRoot_UIRootOnGUI
    {
        [HarmonyPrefix]
        public static void Prefix()
        {
            if (Text.Anchor != TextAnchor.UpperLeft)
            {
                RTL_Support.suppressAnchorPatch = true;
                Text.Anchor = TextAnchor.UpperLeft;
                RTL_Support.suppressAnchorPatch = false;
            }
        }

        [HarmonyPostfix]
        public static void Postfix()
        {
            if (Text.Anchor != TextAnchor.UpperLeft)
            {
                RTL_Support.suppressAnchorPatch = true;
                Text.Anchor = TextAnchor.UpperLeft;
                RTL_Support.suppressAnchorPatch = false;
            }
        }
    }

    [HarmonyPatch(typeof(UIRoot_Entry), "UIRootOnGUI")]
    public static class Patch_UIRoot_Entry_UIRootOnGUI
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            if (Text.Anchor != TextAnchor.UpperLeft)
            {
                RTL_Support.suppressAnchorPatch = true;
                Text.Anchor = TextAnchor.UpperLeft;
                RTL_Support.suppressAnchorPatch = false;
            }
        }
    }

    [HarmonyPatch(typeof(UIRoot_Play), "UIRootOnGUI")]
    public static class Patch_UIRoot_Play_UIRootOnGUI
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            if (Text.Anchor != TextAnchor.UpperLeft)
            {
                RTL_Support.suppressAnchorPatch = true;
                Text.Anchor = TextAnchor.UpperLeft;
                RTL_Support.suppressAnchorPatch = false;
            }
        }
    }

    // Patch 5: Layout bounding box and line wrap calculations
    [HarmonyPatch(typeof(Text), "CalcHeight")]
    public static class Patch_Text_CalcHeight
    {
        [HarmonyPrefix]
        public static void Prefix(ref string text, float width)
        {
            if (LanguageDatabase.activeLanguage?.folderName == "Persian")
            {
                Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                if (mod != null && mod.settings.enablePersianFixer)
                {
                    text = PersianFixer.Fix(text);
                }
            }
        }
    }

    [HarmonyPatch(typeof(Text), "CalcSize")]
    public static class Patch_Text_CalcSize
    {
        [HarmonyPrefix]
        public static void Prefix(ref string text)
        {
            if (LanguageDatabase.activeLanguage?.folderName == "Persian")
            {
                Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                if (mod != null && mod.settings.enablePersianFixer)
                {
                    text = PersianFixer.Fix(text);
                }
            }
        }
    }

    // Patch 6: Fix Text before drawing Widgets.Label
    [HarmonyPatch(typeof(Widgets), "Label", new Type[] { typeof(Rect), typeof(string) })]
    public static class Patch_Widgets_Label
    {
        [HarmonyPrefix]
        public static void Prefix(ref string label)
        {
            if (LanguageDatabase.activeLanguage?.folderName == "Persian")
            {
                Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                if (mod != null && mod.settings.enablePersianFixer)
                {
                    label = PersianFixer.Fix(label);
                }
            }
        }
    }

    // Patch 7: Fix Text before drawing Widgets.ButtonText
    [HarmonyPatch(typeof(Widgets), "ButtonText", new Type[] { typeof(Rect), typeof(string), typeof(bool), typeof(bool), typeof(bool), typeof(TextAnchor?) })]
    public static class Patch_Widgets_ButtonText
    {
        [HarmonyPrefix]
        public static void Prefix(ref string label)
        {
            if (LanguageDatabase.activeLanguage?.folderName == "Persian")
            {
                Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                if (mod != null && mod.settings.enablePersianFixer)
                {
                    label = PersianFixer.Fix(label);
                }
            }
        }
    }

    // Font Choice Enum
    public enum PersianFontChoice
    {
        Vazirmatn = 0,
        IranianSans = 1,
        SystemDefault = 2
    }

    // Mod Settings
    public class ModSettings_RTL_Persian_Support : ModSettings
    {
        public bool enablePersianFont = true;
        public bool enableRTLAlignment = true;
        public bool enablePersianFixer = true;
        public PersianFontChoice selectedFont = PersianFontChoice.Vazirmatn;
        public float fontScale = 1.0f;

        public override void ExposeData()
        {
            Scribe_Values.Look(ref enablePersianFont, "enablePersianFont", true);
            Scribe_Values.Look(ref enableRTLAlignment, "enableRTLAlignment", true);
            Scribe_Values.Look(ref enablePersianFixer, "enablePersianFixer", true);
            Scribe_Values.Look(ref selectedFont, "selectedFont", PersianFontChoice.Vazirmatn);
            Scribe_Values.Look(ref fontScale, "fontScale", 1.0f);
        }
    }

    // Mod Main Class
    public class Mod_RTL_Persian_Support : Verse.Mod
    {
        public ModSettings_RTL_Persian_Support settings;

        public Mod_RTL_Persian_Support(ModContentPack content) : base(content)
        {
            settings = GetSettings<ModSettings_RTL_Persian_Support>();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Listing_Standard listing = new Listing_Standard();
            listing.Begin(inRect);

            listing.CheckboxLabeled("Enable Persian font (default: Enabled)", ref settings.enablePersianFont);
            listing.CheckboxLabeled("Enable RTL text alignments (default: Enabled)", ref settings.enableRTLAlignment);
            listing.CheckboxLabeled("Enable Persian text fixing (letter shaping, default: Enabled)", ref settings.enablePersianFixer);

            listing.Gap(12f);
            listing.Label("Persian Typeface / قلم فارسی:");
            if (listing.RadioButton("Vazirmatn (وزیرمتن - Modern UI, Recommended)", settings.selectedFont == PersianFontChoice.Vazirmatn))
            {
                if (settings.selectedFont != PersianFontChoice.Vazirmatn)
                {
                    settings.selectedFont = PersianFontChoice.Vazirmatn;
                    RTL_Support.UpdateSelectedFont();
                    RTL_Support.dirty = true;
                }
            }
            if (listing.RadioButton("Iranian Sans (ایرانیان سنس - Classic)", settings.selectedFont == PersianFontChoice.IranianSans))
            {
                if (settings.selectedFont != PersianFontChoice.IranianSans)
                {
                    settings.selectedFont = PersianFontChoice.IranianSans;
                    RTL_Support.UpdateSelectedFont();
                    RTL_Support.dirty = true;
                }
            }
            if (listing.RadioButton("System / OS Default (قلم سیستم)", settings.selectedFont == PersianFontChoice.SystemDefault))
            {
                if (settings.selectedFont != PersianFontChoice.SystemDefault)
                {
                    settings.selectedFont = PersianFontChoice.SystemDefault;
                    RTL_Support.UpdateSelectedFont();
                    RTL_Support.dirty = true;
                }
            }

            listing.Gap(12f);
            int scalePct = Mathf.RoundToInt(settings.fontScale * 100);
            string scaleLabel = $"Font Scale: {scalePct}% (Steam Deck / Handheld: 110%-120%)";
            float newScale = listing.SliderLabeled(scaleLabel, settings.fontScale, 0.8f, 1.4f, 0.5f);
            if (Mathf.Abs(newScale - settings.fontScale) > 0.01f)
            {
                settings.fontScale = (float)Math.Round(newScale, 2);
                RTL_Support.dirty = true;
            }

            listing.End();
        }

        public override string SettingsCategory() => "RTL Persian Support";
    }
}
