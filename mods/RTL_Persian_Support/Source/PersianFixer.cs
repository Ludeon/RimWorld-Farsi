using System;
using System.Collections.Generic;
using System.Text;
using System.Linq;

namespace RTL_Persian
{
    public static class PersianFixer
    {
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

            // 1. Check if processing is needed
            bool hasPersian = false;
            foreach (char c in text) { if (c >= 0x0600 && c <= 0x06FF) { hasPersian = true; break; } }
            if (!hasPersian) return text;

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
                bool nextConnects = (i < processed.Count - 1) && Maps.ContainsKey(processed[i + 1]) && true; // Right-to-left, "next" means left.

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
            return new string(fixedChars);
        }

        private static List<char> PrepareText(string text)
        {
            List<char> result = new List<char>();
            char[] chars = text.ToCharArray();

            for (int i = 0; i < chars.Length; i++)
            {
                char c = chars[i];

                // A. Normalization (Arabic -> Persian)
                if (c == 'ي') c = 'ی';
                if (c == 'ك') c = 'ک';

                // B. Ligature Check: Lam (ل) + Alef (ا)
                if (c == 'ل' && i + 1 < chars.Length)
                {
                    char next = chars[i + 1];
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
