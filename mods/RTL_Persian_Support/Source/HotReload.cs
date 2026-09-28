using System;
using HarmonyLib;
using UnityEngine;
using Verse;
using RimWorld;

namespace RTL_Persian
{
    /// <summary>
    /// Live Translation Hot-Reload Engine.
    /// Allows translators and developers to press Ctrl + F5 in-game to instantly
    /// reload all XML files and font scalings without restarting RimWorld.
    /// </summary>
    [HarmonyPatch(typeof(UIRoot), "UIRootOnGUI")]
    public static class Patch_HotReload_OnGUI
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            if (Event.current != null && Event.current.type == EventType.KeyDown)
            {
                if (Event.current.control && Event.current.keyCode == KeyCode.F5)
                {
                    ExecuteHotReload();
                    Event.current.Use();
                }
            }
        }

        public static void ExecuteHotReload()
        {
            try
            {
                RTL_Support.LogFile("Triggering Live Translation Hot-Reload (Ctrl + F5)...");

                // 1. Clear BiDi shaping cache
                PersianFixer.ClearCache();

                // 2. Reload active language XML assets from disk
                if (LanguageDatabase.activeLanguage != null)
                {
                    LanguageDatabase.activeLanguage.LoadData();
                    RTL_Support.LogFile($"Reloaded language data for: {LanguageDatabase.activeLanguage.folderName}");
                }

                // 3. Refresh fonts and GUI alignments
                RTL_Support.dirty = true;
                RTL_Support.ApplyChanges();

                // 4. Notify player in-game
                if (Current.ProgramState == ProgramState.Playing)
                {
                    Messages.Message("بازخوانی زنده ترجمه فارسی انجام شد (Ctrl+F5).", MessageTypeDefOf.TaskCompletion, false);
                }
                else
                {
                    Log.Message("[RTL Support] Persian translation successfully hot-reloaded (Ctrl+F5).");
                }
            }
            catch (Exception ex)
            {
                RTL_Support.LogFile($"HotReload failed with error: {ex}");
                Log.Warning($"[RTL Support] HotReload error: {ex.Message}");
            }
        }
    }
}
