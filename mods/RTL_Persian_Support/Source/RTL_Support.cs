using System;
using System.IO;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

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

            // 2. Initialize Logging (Try Mod Folder, Fallback to Desktop)
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

        private static void InitDebugLog()
        {
            try
            {
                // Try creating log in the Mod's root directory
                _logFilePath = Path.Combine(_contentPack.RootDir, "error.log");
                
                // Reset the log file on startup
                File.WriteAllText(_logFilePath, $"--- RTL Persian Support Error Log ---\nTime: {DateTime.Now}\nVersion: RimWorld 1.6\n\n");
                
                // Subscribe to Unity's log event to capture ALL game logs
                Application.logMessageReceived += HandleLog;
                
                Log.Message($"[RTL Support] Logging to: {_logFilePath}");
            }
            catch (UnauthorizedAccessException)
            {
                // Fallback: If Mod folder is read-only (Program Files), write to Desktop
                string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                _logFilePath = Path.Combine(desktopPath, "RTL_Persian_Error.log");

                try
                {
                    File.WriteAllText(_logFilePath, $"--- RTL Persian Support Error Log (Fallback) ---\nTime: {DateTime.Now}\n\n");
                    Application.logMessageReceived += HandleLog;
                    Log.Warning($"[RTL Support] Could not write to mod folder. Logging to Desktop instead: {_logFilePath}");
                }
                catch { _logFilePath = null; } // Give up if even Desktop fails
            }
            catch (Exception e)
            {
                Log.Warning($"[RTL Support] Logging initialization failed: {e.Message}");
            }
        }

        private static void HandleLog(string logString, string stackTrace, LogType type)
        {
            if (string.IsNullOrEmpty(_logFilePath)) return;

            // Filter out our own log messages to avoid duplication if we use Log.Message inside LogFile (we don't, but good practice)
            // Also, we might want to filter out spammy logs if needed, but user asked for "this log", implying the full log.

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
                catch
                {
                    // Ignore file access errors during logging to prevent crashes
                }
            }
        }

        /// <summary>
        /// Writes a line to the error.log file.
        /// </summary>
        public static void LogFile(string message)
        {
            // We can just use the HandleLog mechanism by calling Log.Message, 
            // BUT if we want to write internal debug info without spamming the in-game console, we write directly.
            
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
            // CRITICAL FIX: Manually reset Anchor to UpperLeft without triggering our RTL patch
            // This prevents the "Alignment was UpperRight at end of frame" error.
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
            // If suppression is active, let the game set UpperLeft normally
            if (RTL_Support.suppressAnchorPatch) return;

            if (LanguageDatabase.activeLanguage?.folderName == "Persian")
            {
                Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                if (mod != null && mod.settings.enableRTLAlignment)
                {
                    switch (value)
                    {
                        // Force Left-Aligned text to be Right-Aligned (RTL style)
                        case TextAnchor.UpperLeft: value = TextAnchor.UpperRight; break;
                        case TextAnchor.MiddleLeft: value = TextAnchor.MiddleRight; break;
                        case TextAnchor.LowerLeft: value = TextAnchor.LowerRight; break;

                        // FIX: Do NOT swap Right-Aligned text to Left.
                        // Keep it Right-Aligned so it anchors correctly at the screen edge.
                        case TextAnchor.UpperRight:
                            // value = TextAnchor.UpperLeft; // REMOVED THIS LINE
                            break;
                        case TextAnchor.MiddleRight:
                            // value = TextAnchor.MiddleLeft; // REMOVED THIS LINE
                            break;
                        case TextAnchor.LowerRight:
                            // value = TextAnchor.LowerLeft; // REMOVED THIS LINE
                            break;
                    }
                }
            }
        }
    }

    // --- NEW PATCH: Fix Text Before Drawing ---
    [HarmonyPatch(typeof(Widgets), "Label", new Type[] { typeof(Rect), typeof(string) })]
    public static class Patch_Widgets_Label
    {
        [HarmonyPrefix]
        public static void Prefix(ref string label)
        {
            if (LanguageDatabase.activeLanguage?.folderName == "Persian")
            {
                Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                if (mod != null && mod.settings.enablePersianFixer && !label.Contains('{'))
                {
                    label = PersianFixer.Fix(label);
                }
            }
        }
    }

    // Patch buttons as well
    [HarmonyPatch(typeof(Widgets), "ButtonText", new Type[] { typeof(Rect), typeof(string), typeof(bool), typeof(bool), typeof(bool), typeof(TextAnchor?) })]
    public static class Patch_Widgets_ButtonText
    {
        [HarmonyPrefix]
        public static void Prefix(ref string label)
        {
             if (LanguageDatabase.activeLanguage?.folderName == "Persian")
             {
                 Mod_RTL_Persian_Support mod = LoadedModManager.GetMod<Mod_RTL_Persian_Support>();
                 if (mod != null && mod.settings.enablePersianFixer && !label.Contains('{'))
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
        public bool enableRTLAlignment = false;
        public bool enablePersianFixer = false;

        public override void ExposeData()
        {
            Scribe_Values.Look(ref enablePersianFont, "enablePersianFont", true);
            Scribe_Values.Look(ref enableRTLAlignment, "enableRTLAlignment", false);
            Scribe_Values.Look(ref enablePersianFixer, "enablePersianFixer", false);
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
            listing.CheckboxLabeled("Enable RTL text alignments (default: Disabled)", ref settings.enableRTLAlignment);
            listing.CheckboxLabeled("Enable Persian text fixing (letter shaping, default: Disabled)", ref settings.enablePersianFixer);
            listing.End();
        }

        public override string SettingsCategory() => "RTL Persian Support";
    }
}
