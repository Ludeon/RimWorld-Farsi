using System;

namespace RTL_Persian
{
    /// <summary>
    /// Pure helper for backward progressive WordInfo lookup preserving trailing modifiers
    /// such as quality suffixes "(عالی)" or trailing adjectives/materials.
    /// </summary>
    public static class PersianWordLookupHelper
    {
        public static string ResolveWithProgressiveTail(
            string word,
            Func<string, string> tryLookup,
            Func<string, string> fallback = null)
        {
            if (string.IsNullOrEmpty(word))
                return word;

            string exact = tryLookup?.Invoke(word);
            if (!string.IsNullOrEmpty(exact))
                return exact;

            // 1. Check trailing parenthetical quality/modifier e.g. "گرز فولادی (عالی)"
            int parenIdx = word.LastIndexOf(" (", StringComparison.Ordinal);
            if (parenIdx > 0 && word.EndsWith(")", StringComparison.Ordinal))
            {
                string stem = word.Substring(0, parenIdx).TrimEnd();
                string tail = word.Substring(parenIdx);
                string parenHit = tryLookup?.Invoke(stem);
                if (!string.IsNullOrEmpty(parenHit))
                    return parenHit + tail;

                string progressiveOnStem = TryStripWordsFromRight(stem, tryLookup);
                if (!string.IsNullOrEmpty(progressiveOnStem))
                    return progressiveOnStem + tail;

                if (fallback != null)
                    return fallback(stem) + tail;
            }

            // 2. Progressively trim space-separated trailing tokens from the right
            string progressive = TryStripWordsFromRight(word, tryLookup);
            if (!string.IsNullOrEmpty(progressive))
                return progressive;

            return fallback != null ? fallback(word) : word;
        }

        private static string TryStripWordsFromRight(string text, Func<string, string> tryLookup)
        {
            if (tryLookup == null || string.IsNullOrEmpty(text))
                return null;

            int cut = text.Length;
            while ((cut = text.LastIndexOf(' ', cut - 1)) > 0)
            {
                string stem = text.Substring(0, cut).TrimEnd();
                if (stem.Length == 0)
                    break;
                string tail = text.Substring(cut);
                string hit = tryLookup(stem);
                if (!string.IsNullOrEmpty(hit))
                    return hit + tail;
            }

            return null;
        }
    }
}
