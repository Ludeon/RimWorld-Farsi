using System;
using System.Collections.Generic;

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
        /// RimWorld 1.6 runs on Unity 2022 with native HarfBuzz & BiDi text shaping.
        /// Text must NOT be reversed or replaced with Presentation Forms-B,
        /// as modern Unity natively shapes standard Unicode Persian (0x0600-0x06FF).
        /// </summary>
        public static string Fix(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;

            lock (Cache)
            {
                if (Cache.TryGetValue(text, out string cached))
                    return cached;
            }

            // Normalize Arabic Yeh and Kaf to Persian forms
            string result = text;
            if (result.IndexOf('ي') != -1) result = result.Replace('ي', 'ی');
            if (result.IndexOf('ك') != -1) result = result.Replace('ك', 'ک');

            lock (Cache)
            {
                if (Cache.Count >= MaxCacheSize) Cache.Clear();
                Cache[text] = result;
            }

            return result;
        }
    }
}
