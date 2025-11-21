using System;
using System.Collections.Generic;
using System.Text;
using System.Linq;
using System.Text.RegularExpressions;

namespace RTL_Persian
{
    public static class PersianFixer
    {
        // --- Cache ---
        private static readonly Dictionary<string, string> Cache = new Dictionary<string, string>();
        private const int MaxCacheSize = 5000;

        public static void ClearCache()
        {
            Cache.Clear();
        }

        // --- 1. Mappings ---
        // Maps: [Isolated, Final, Initial, Medial]
        private static readonly Dictionary<char, char[]> Maps = new Dictionary<char, char[]>
        {
            { 'آ', new[] { 'آ', 'ﺂ', 'آ', 'ﺂ' } },
            { 'ا', new[] { 'ا', 'ﺎ', 'ا', 'ﺎ' } },
            { 'ب', new[] { 'ب', 'ﺐ', 'ﺑ', 'ﺒ' } },
            { 'پ', new[] { 'پ', 'ﭗ', 'ﭘ', 'ﭙ' } },
            { 'ت', new[] { 'ت', 'ﺖ', 'ﺗ', 'ﺘ' } },
            { 'ث', new[] { 'ث', 'ﺚ', 'ﺛ', 'ﺜ' } },
            { 'ج', new[] { 'ج', 'ﺞ', 'ﺟ', 'ﺠ' } },
            { 'چ', new[] { 'چ', 'ﭻ', 'ﭼ', 'ﭽ' } },
            { 'ح', new[] { 'ح', 'ﺢ', 'ﺣ', 'ﺤ' } },
            { 'خ', new[] { 'خ', 'ﺦ', 'ﺧ', 'ﺨ' } },
            { 'د', new[] { 'د', 'ﺪ', 'د', 'ﺪ' } },
            { 'ذ', new[] { 'ذ', 'ﺬ', 'ذ', 'ﺬ' } },
            { 'ر', new[] { 'ر', 'ﺮ', 'ر', 'ﺮ' } },
            { 'ز', new[] { 'ز', 'ﺰ', 'ز', 'ﺰ' } },
            { 'ژ', new[] { 'ژ', 'ﮋ', 'ژ', 'ﮋ' } },
            { 'س', new[] { 'س', 'ﺲ', 'ﺳ', 'ﺴ' } },
            { 'ش', new[] { 'ش', 'ﺶ', 'ﺷ', 'ﺸ' } },
            { 'ص', new[] { 'ص', 'ﺺ', 'ﺻ', 'ﺼ' } },
            { 'ض', new[] { 'ض', 'ﺾ', 'ﺿ', 'ﻀ' } },
            { 'ط', new[] { 'ط', 'ﻂ', 'ﻃ', 'ﻄ' } },
            { 'ظ', new[] { 'ظ', 'ﻆ', 'ﻇ', 'ﻈ' } },
            { 'ع', new[] { 'ع', 'ﻊ', 'ﻋ', 'ﻌ' } },
            { 'غ', new[] { 'غ', 'ﻎ', 'ﻏ', 'ﻐ' } },
            { 'ف', new[] { 'ف', 'ﻒ', 'ﻓ', 'ﻔ' } },
            { 'ق', new[] { 'ق', 'ﻖ', 'ﻗ', 'ﻘ' } },
            { 'ک', new[] { 'ک', 'ﮏ', 'ﮐ', 'ﮑ' } },
            { 'گ', new[] { 'گ', 'ﮓ', 'ﮔ', 'ﮕ' } },
            { 'ل', new[] { 'ل', 'ﻞ', 'ﻟ', 'ﻠ' } },
            { 'م', new[] { 'م', 'ﻢ', 'ﻣ', 'ﻤ' } },
            { 'ن', new[] { 'ن', 'ﻦ', 'ﻧ', 'ﻨ' } },
            { 'و', new[] { 'و', 'ﻮ', 'و', 'ﻮ' } },
            { 'ه', new[] { 'ه', 'ﻪ', 'ﻫ', 'ﻬ' } },
            { 'ی', new[] { 'ی', 'ﯽ', 'ﯾ', 'ﯿ' } },
            { 'ئ', new[] { 'ئ', 'ﺊ', 'ﺋ', 'ﺌ' } },
            { 'ء', new[] { 'ء', 'ء', 'ء', 'ء' } },
            { 'ة', new[] { 'ة', 'ﺔ', 'ﺗ', 'ﺘ' } },
            { 'ؤ', new[] { 'ؤ', 'ﺆ', 'ؤ', 'ﺆ' } },
            { 'إ', new[] { 'إ', 'ﺈ', 'إ', 'ﺈ' } },
            { 'أ', new[] { 'أ', 'ﺄ', 'أ', 'ﺄ' } },
            // Lam-Alef Special Chars (0xFEFB is standard for La Isolated)
            { (char)0xFEFB, new[] { 'ﻻ', 'ﻼ', 'ﻻ', 'ﻼ' } }
        };

        // Characters that do NOT connect to the left (Next character)
        private static readonly HashSet<char> NonConnectors = new HashSet<char>
        {
            'آ', 'ا', 'د', 'ذ', 'ر', 'ز', 'ژ', 'و', 'ؤ', 'إ', 'أ',
            (char)0xFEFB // Lam-Alef cannot connect to the next char
        };

        public static string Fix(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;

            // Check Cache
            if (Cache.TryGetValue(text, out string cached))
                return cached;

            // Handle Rich Text
            if (text.IndexOf('<') != -1 && text.IndexOf('>') != -1)
            {
                string result = FixRichText(text);
                AddToCache(text, result);
                return result;
            }

            // 1. Check if processing is needed
            bool hasPersian = false;
            for (int i = 0; i < text.Length; i++)
            {
                if (text[i] >= 0x0600 && text[i] <= 0x06FF)
                {
                    hasPersian = true;
                    break;
                }
            }
            
            if (!hasPersian) 
            {
                AddToCache(text, text);
                return text;
            }

            // 2. Pre-process: Normalize & Handle Ligatures (Lam + Alef)
            List<char> processed = PrepareText(text);

            // 3. Reshape (Contextual Forms)
            char[] fixedChars = new char[processed.Count];
            for (int i = 0; i < processed.Count; i++)
            {
                char c = processed[i];
                if (!Maps.ContainsKey(c))
                {
                    fixedChars[i] = c;
                    continue;
                }

                // Connectivity Logic
                bool prevConnects = (i > 0) && Maps.ContainsKey(processed[i - 1]) && CanConnectToNext(processed[i - 1]);
                
                // Fix: Check if current char can connect to next
                bool nextConnects = (i < processed.Count - 1) && Maps.ContainsKey(processed[i + 1]) && CanConnectToNext(c);

                if (prevConnects && nextConnects)
                    fixedChars[i] = Maps[c][3]; // Medial
                else if (prevConnects && !nextConnects)
                    fixedChars[i] = Maps[c][1]; // Final
                else if (!prevConnects && nextConnects)
                    fixedChars[i] = Maps[c][2]; // Initial
                else
                    fixedChars[i] = Maps[c][0]; // Isolated
            }

            // 4. Reverse for Unity Rendering
            Array.Reverse(fixedChars);
            string finalResult = new string(fixedChars);
            
            AddToCache(text, finalResult);
            return finalResult;
        }

        // Regex for matching Rich Text tags
        private static readonly Regex RichTextTagRegex = new Regex("<[^>]+>", RegexOptions.Compiled);

        private static string FixRichText(string text)
        {
            var tags = new List<string>();
            // Regex to find tags. Matches <tag> or <tag=value> or </tag>
            string masked = RichTextTagRegex.Replace(text, match =>
            {
                tags.Add(match.Value);
                return "\uF8FF";
            });

            // Recursively fix the masked string (which has no tags now)
            string fixedMasked = Fix(masked);

            // Replace markers back with tags
            StringBuilder sb = new StringBuilder();
            int tagIndex = 0;
            foreach (char c in fixedMasked)
            {
                if (c == '\uF8FF')
                {
                    if (tagIndex < tags.Count)
                    {
                        sb.Append(tags[tagIndex++]);
                    }
                }
                else
                {
                    sb.Append(c);
                }
            }
            return sb.ToString();
        }

        private static void AddToCache(string key, string value)
        {
            if (Cache.Count >= MaxCacheSize)
            {
                Cache.Clear();
            }
            Cache[key] = value;
        }

        private static List<char> PrepareText(string text)
        {
            List<char> result = new List<char>(text.Length);
            
            for (int i = 0; i < text.Length; i++)
            {
                char c = text[i];

                // A. Normalization (Arabic -> Persian)
                if (c == 'ي') c = 'ی';
                if (c == 'ك') c = 'ک';

                // B. Ligature Check: Lam (ل) + Alef (ا)
                if (c == 'ل' && i + 1 < text.Length)
                {
                    char next = text[i + 1];
                    // Check various forms of Alef
                    if (next == 'ا' || next == 'آ' || next == 'أ' || next == 'إ')
                    {
                        // Replace 'Lam' + 'Alef' with single special char 0xFEFB
                        result.Add((char)0xFEFB);
                        i++; // Skip the Alef
                        continue;
                    }
                }

                result.Add(c);
            }
            return result;
        }

        private static bool CanConnectToNext(char c) => !NonConnectors.Contains(c);
    }
}
