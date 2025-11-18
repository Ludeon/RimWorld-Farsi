using System;
using System.Collections.Generic;
using System.Text;
using System.Linq;

namespace RTL_Persian
{
    public static class PersianFixer
    {
        // Maps raw character to [Isolated, Final, Initial, Medial] forms
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
            { 'ﻻ', new[] { 'ﻻ', 'ﻼ', 'ﻻ', 'ﻼ' } }
        };

        public static string Fix(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;

            // Quick check: does the string contain any Persian/Arabic characters?
            // 0600-06FF is the main Arabic Unicode block
            bool hasPersian = false;
            foreach (char c in text) { if (c >= 0x0600 && c <= 0x06FF) { hasPersian = true; break; } }
            if (!hasPersian) return text;

            char[] chars = text.ToCharArray();
            char[] fixedChars = new char[chars.Length];

            for (int i = 0; i < chars.Length; i++)
            {
                char c = chars[i];
                if (!Maps.ContainsKey(c))
                {
                    fixedChars[i] = c;
                    continue;
                }

                // Logic to determine connectivity based on neighbors
                bool prevConnects = (i > 0) && IsConnectable(chars[i - 1]) && CanConnectToNext(chars[i - 1]);
                bool nextConnects = (i < chars.Length - 1) && IsConnectable(chars[i + 1]) && CanConnectToPrev(chars[i + 1]);

                if (prevConnects && nextConnects)
                    fixedChars[i] = Maps[c][3]; // Medial
                else if (prevConnects && !nextConnects)
                    fixedChars[i] = Maps[c][1]; // Final
                else if (!prevConnects && nextConnects)
                    fixedChars[i] = Maps[c][2]; // Initial
                else
                    fixedChars[i] = Maps[c][0]; // Isolated
            }

            // Finally, reverse the string because Unity draws LTR
            Array.Reverse(fixedChars);
            return new string(fixedChars);
        }

        private static bool IsConnectable(char c) => Maps.ContainsKey(c);

        // Letters that cannot connect to the NEXT letter (Left side in RTL)
        private static readonly HashSet<char> NonConnectors = new HashSet<char>
        { 'آ', 'ا', 'د', 'ذ', 'ر', 'ز', 'ژ', 'و', 'ؤ', 'إ', 'أ' };

        private static bool CanConnectToNext(char c) => !NonConnectors.Contains(c);
        private static bool CanConnectToPrev(char c) => true;
    }
}
