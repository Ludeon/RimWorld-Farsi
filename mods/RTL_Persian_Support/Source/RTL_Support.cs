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

        public static void LoadPersianFont()
        {
            try
            {
                // Ensure the file is named 'persianfont' with NO extension in the Resources folder
                string bundlePath = Path.Combine(_contentPack.RootDir, "Resources", "persianfont");

                LogFile($"Attempting to load font from: {bundlePath}");

                if (File.Exists(bundlePath))
                {
                    AssetBundle bundle = AssetBundle.LoadFromFile(bundlePath);
                    if (bundle != null)
                    {
                        PersianFont = bundle.LoadAllAssets<Font>().FirstOrDefault();
                        bundle.Unload(false);
                        LogFile("Persian font loaded successfully.");
                    }
                    else
                    {
                        LogFile("ERROR: AssetBundle found but failed to load.");
                    }
                }
                else
                {
                    LogFile($"WARNING: Font bundle not found at {bundlePath}");
                }
            }
            catch (Exception e)
            {
                Log.Error($"RTL_Persian_Support: Error loading font: {e.Message}");
                LogFile($"EXCEPTION while loading font: {e.Message}");
            }
        }

        public static void ApplyChanges()
        {
            if (GUI.skin == null) return;

            bool isPersian = LanguageDatabase.activeLanguage?.folderName == "Persian";
            LogFile($"Applying GUI changes. IsPersian: {isPersian}");

            if (isPersian)
            {
                GUI.skin.label.alignment = TextAnchor.UpperRight;
                GUI.skin.button.alignment = TextAnchor.UpperRight;
                GUI.skin.textField.alignment = TextAnchor.UpperRight;
                GUI.skin.textArea.alignment = TextAnchor.UpperRight;

                if (PersianFont != null)
                {
                    if (OriginalFont == null) OriginalFont = Text.fontStyles[0].font;
                    SetGameFont(PersianFont);
                }
            }
            else
            {
                GUI.skin.label.alignment = TextAnchor.UpperLeft;
                GUI.skin.button.alignment = TextAnchor.UpperLeft;
                GUI.skin.textField.alignment = TextAnchor.UpperLeft;
                GUI.skin.textArea.alignment = TextAnchor.UpperLeft;

                if (OriginalFont != null) SetGameFont(OriginalFont);
            }
        }

        private static void SetGameFont(Font font)
        {
            for (int i = 0; i < Text.fontStyles.Length; i++)
            {
                if (Text.fontStyles[i] != null) Text.fontStyles[i].font = font;
                if (Text.textFieldStyles[i] != null) Text.textFieldStyles[i].font = font;
                if (Text.textAreaStyles[i] != null) Text.textAreaStyles[i].font = font;
            }
        }

        private static void InitDebugLog()
        {
            try
            {
                // Try creating log in the Mod's root directory
                _logFilePath = Path.Combine(_contentPack.RootDir, "debug.log");
                File.WriteAllText(_logFilePath, $"--- RTL Persian Support Debug Log ---\nTime: {DateTime.Now}\nVersion: RimWorld Mod\n\n");
                Log.Message($"[RTL Support] Logging to: {_logFilePath}");
            }
            catch (UnauthorizedAccessException)
            {
                // Fallback: If Mod folder is read-only (Program Files), write to Desktop
                string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                _logFilePath = Path.Combine(desktopPath, "RTL_Persian_Debug.log");

                try
                {
                    File.WriteAllText(_logFilePath, $"--- RTL Persian Support Debug Log (Fallback) ---\nTime: {DateTime.Now}\n\n");
                    Log.Warning($"[RTL Support] Could not write to mod folder. Logging to Desktop instead: {_logFilePath}");
                }
                catch { _logFilePath = null; } // Give up if even Desktop fails
            }
            catch (Exception e)
            {
                Log.Warning($"[RTL Support] Logging initialization failed: {e.Message}");
            }
        }

        /// <summary>
        /// Writes a line to the debug.log file.
        /// </summary>
        public static void LogFile(string message)
        {
            if (string.IsNullOrEmpty(_logFilePath)) return;

            try
            {
                using (StreamWriter writer = new StreamWriter(_logFilePath, true))
                {
                    writer.WriteLine($"[{DateTime.Now:HH:mm:ss}] {message}");
                }
            }
            catch
            {
                // Ignore errors to prevent loops
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
                switch (value)
                {
                    case TextAnchor.UpperLeft: value = TextAnchor.UpperRight; break;
                    case TextAnchor.MiddleLeft: value = TextAnchor.MiddleRight; break;
                    case TextAnchor.LowerLeft: value = TextAnchor.LowerRight; break;
                    case TextAnchor.UpperRight: value = TextAnchor.UpperLeft; break;
                    case TextAnchor.MiddleRight: value = TextAnchor.MiddleLeft; break;
                    case TextAnchor.LowerRight: value = TextAnchor.LowerLeft; break;
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
                label = PersianFixer.Fix(label);
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
                 label = PersianFixer.Fix(label);
             }
        }
    }
}
