using System;
using System.Collections.Generic;
using ArabicSupport;

namespace RTL_Persian
{
    public static class PersianFixer
    {
        private static readonly Dictionary<string, string> Cache = new Dictionary<string, string>();
        private const int MaxCacheSize = 8000;

        public static void ClearCache()
        {
            lock (Cache)
            {
                Cache.Clear();
            }
        }

        /// <summary>
        /// Normalizes Persian text and ensures proper character encoding.
        /// Reverses and shapes text using ArabicSupport for IMGUI compatibility.
        /// </summary>
        public static string Fix(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;

            lock (Cache)
            {
                if (Cache.TryGetValue(text, out string cached))
                    return cached;
            }

            // Idempotency check: if the text already contains a Zero Width Space marker,
            // it means it was already fixed by ArabicFixer in a previous patch hook.
            if (text.Contains("\u200B"))
            {
                return text;
            }

            // Normalize Arabic Yeh and Kaf to Persian forms before shaping
            string normalized = text.Replace('ي', 'ی').Replace('ك', 'ک');

            // Apply ArabicFixer: RTL = true, showTashkeel = true, useHinduNumbers = false
            // Note: ArabicFixer handles BiDi layout (reversing the sentence) while preserving tags.
            string result = ArabicFixer.Fix(normalized, true, true, false);
            
            // Append Zero Width Space marker to prevent double-fixing
            result += "\u200B";

            lock (Cache)
            {
                if (Cache.Count >= MaxCacheSize) Cache.Clear();
                Cache[text] = result;
            }

            return result;
        }
    }
}
