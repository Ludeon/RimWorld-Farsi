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

            // 4. Load Font
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
                LogFile("Loading Persian font...");

                // Method 1: Try loading IranianSans.ttf directly using Unity's Font path creation
                string fontPath = Path.Combine(_contentPack.RootDir, "IranianSans.ttf");
                if (File.Exists(fontPath))
                {
                    try
                    {
                        MethodInfo createFontFromPath = typeof(Font).GetMethod("Internal_CreateFontFromPath", BindingFlags.NonPublic | BindingFlags.Static);
                        if (createFontFromPath != null)
                        {
                            Font font = new Font();
                            createFontFromPath.Invoke(null, new object[] { font, fontPath });
                            PersianFont = font;
                            LogFile($"Successfully loaded Persian font from TTF at {fontPath}");
                        }
                        else
                        {
                            LogFile("Internal_CreateFontFromPath method not found on UnityEngine.Font.");
                        }
                    }
                    catch (Exception ex)
                    {
                        LogFile($"Internal_CreateFontFromPath failed: {ex.Message}");
                    }
                }
                else
                {
                    LogFile($"IranianSans.ttf not found at {fontPath}");
                }

                // Method 2: Try loading from AssetBundle if available
                if (PersianFont == null)
                {
                    string bundlePath = Path.Combine(_contentPack.RootDir, "Resources", "persianfont");
                    if (File.Exists(bundlePath))
                    {
                        try
                        {
                            AssetBundle bundle = AssetBundle.LoadFromFile(bundlePath);
                            if (bundle != null)
                            {
                                PersianFont = bundle.LoadAllAssets<Font>().FirstOrDefault();
                                bundle.Unload(false);
                                LogFile("Persian font loaded from AssetBundle.");
                            }
                        }
                        catch (Exception ex)
                        {
                            LogFile($"AssetBundle load failed: {ex.Message}");
                        }
                    }
                }

                // Method 3: Fallback to OS installed Persian / Arabic fonts
                if (PersianFont == null)
                {
                    try
                    {
                        string[] fontCandidates = new string[] { "Iranian Sans", "Tahoma", "Arial", "DejaVu Sans", "Segoe UI" };
                        PersianFont = Font.CreateDynamicFontFromOSFont(fontCandidates, 16);
                        if (PersianFont != null)
                        {
                            LogFile("Persian font dynamically created from OS fonts fallback.");
                        }
                    }
                    catch (Exception ex)
                    {
                        LogFile($"OS font fallback failed: {ex.Message}");
                    }
                }

                if (PersianFont != null)
                {
                    LogFile($"Persian font ready: {PersianFont.name}");
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

        public static void ApplyChanges()
        {
            if (GUI.skin == null) return;

            bool isPersian = LanguageDatabase.activeLanguage?.folderName == "Persian";
            LogFile($"Applying GUI changes. IsPersian: {isPersian}");

            Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
            bool enableFont = mod == null || mod.settings.enablePersianFont;
            bool enableRTL = mod != null && mod.settings.enableRTLAlignment;

            if (isPersian)
            {
                if (enableRTL)
                {
                    GUI.skin.label.alignment = TextAnchor.UpperRight;
                    GUI.skin.button.alignment = TextAnchor.UpperRight;
                    GUI.skin.textField.alignment = TextAnchor.UpperRight;
                    GUI.skin.textArea.alignment = TextAnchor.UpperRight;
                }

                if (enableFont && PersianFont != null)
                {
                    if (OriginalFont == null && Text.fontStyles.Length > 0 && Text.fontStyles[0] != null)
                    {
                        OriginalFont = Text.fontStyles[0].font;
                    }
                    SetGameFont(PersianFont);
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
                    SetGameFont(OriginalFont);
                }
            }
        }

        private static void SetGameFont(Font font)
        {
            if (font == null) return;

            for (int i = 0; i < Text.fontStyles.Length; i++)
            {
                if (Text.fontStyles[i] != null) Text.fontStyles[i].font = font;
            }
            for (int i = 0; i < Text.textFieldStyles.Length; i++)
            {
                if (Text.textFieldStyles[i] != null) Text.textFieldStyles[i].font = font;
            }
            for (int i = 0; i < Text.textAreaStyles.Length; i++)
            {
                if (Text.textAreaStyles[i] != null) Text.textAreaStyles[i].font = font;
            }
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

    // Mod Settings
    public class ModSettings_RTL_Persian_Support : ModSettings
    {
        public bool enablePersianFont = true;
        public bool enableRTLAlignment = true;
        public bool enablePersianFixer = true;

        public override void ExposeData()
        {
            Scribe_Values.Look(ref enablePersianFont, "enablePersianFont", true);
            Scribe_Values.Look(ref enableRTLAlignment, "enableRTLAlignment", true);
            Scribe_Values.Look(ref enablePersianFixer, "enablePersianFixer", true);
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
            listing.End();
        }

        public override string SettingsCategory() => "RTL Persian Support";
    }
}
