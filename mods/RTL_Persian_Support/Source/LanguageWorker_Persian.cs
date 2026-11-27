using System;
using System.Collections.Generic;
using Verse;
using RimWorld;

namespace RTL_Persian
{
    /// <summary>
    /// Custom LanguageWorker for Persian (فارسی).
    /// Handles Persian pluralization rules, numeral-noun agreements,
    /// Ezāfeh lookups, and text post-processing.
    /// </summary>
    public class LanguageWorker_Persian : LanguageWorker
    {
        private const char ZWNJ = '\u200C'; // Zero-Width Non-Joiner (نیم‌فاصله)
        private const char Kasra = '\u0650'; // Persian Kasra for Ezāfeh (ـِ)

        // Common singular Persian nouns naturally ending in "-ان" that must still be pluralized.
        private static readonly HashSet<string> SingularAnNouns = new HashSet<string>(StringComparer.Ordinal)
        {
            "آسمان", "استخوان", "انسان", "ایوان", "باران", "بیمارستان",
            "پیمان", "جان", "جریان", "جهان", "حیوان", "داستان",
            "درمان", "دندان", "دوران", "دهان", "زبان", "زمان",
            "زندان", "ساختمان", "طوفان", "عنوان", "فرمان", "قهرمان",
            "کمان", "کیهان", "گلدان", "لیوان", "مکان", "میدان",
            "نان", "نشان"
        };

        /// <summary>
        /// Persian has no grammatical gender.
        /// </summary>
        public override int TotalNumCaseCount => 1;

        /// <summary>
        /// Pluralizes a word according to Persian grammar:
        /// 1. If count >= 0 (numeral is present): Persian nouns remain SINGULAR (e.g. "۵ استعمارگر", not "۵ استعمارگران").
        /// 2. If count == -1 (generic plural):
        ///    - Checks WordInfo/plural.txt table.
        ///    - If not in table, applies natural Persian plural suffix (ZWNJ + ها).
        /// </summary>
        public override string Pluralize(string str, Gender gender, int count = -1)
        {
            if (string.IsNullOrEmpty(str))
                return str;

            // In Persian, when accompanied by a count (>= 0), nouns remain singular:
            if (count >= 0)
                return str;

            // Generic plural (count == -1) with progressive KeyTail lookup + natural fallback:
            return PersianWordLookupHelper.ResolveWithProgressiveTail(
                str,
                stem => TryLookupPluralForm(stem, gender, out string lookupPlural, count) ? lookupPlural : null,
                stem =>
                {
                    if (stem.EndsWith("ها") || (stem.EndsWith("ان") && !SingularAnNouns.Contains(stem)))
                        return stem;
                    return stem + ZWNJ + "ها";
                }
            );
        }

        /// <summary>
        /// Indefinite article in Persian ("یک ..." or suffix "ـی").
        /// </summary>
        public override string WithIndefiniteArticle(string str, Gender gender, bool plural = false, bool name = false)
        {
            if (string.IsNullOrEmpty(str) || name)
                return str;

            return "یک " + str;
        }

        /// <summary>
        /// Definite article in Persian: Persian has no overt definite article.
        /// </summary>
        public override string WithDefiniteArticle(string str, Gender gender, bool plural = false, bool name = false)
        {
            return str;
        }

        /// <summary>
        /// Ordinal numbers in Persian (اول، دوم، سوم، چهارم...).
        /// </summary>
        public override string OrdinalNumber(int number, Gender gender = Gender.None)
        {
            switch (number)
            {
                case 1: return "اول";
                case 2: return "دوم";
                case 3: return "سوم";
                case 4: return "چهارم";
                case 5: return "پنجم";
                case 6: return "ششم";
                case 7: return "هفتم";
                case 8: return "هشتم";
                case 9: return "نهم";
                case 10: return "دهم";
                default: return number + "ـم";
            }
        }

        /// <summary>
        /// In Persian, numerals always take singular nouns.
        /// Returns args[0] (singular).
        /// </summary>
        public override string ResolveNumCase(float number, List<string> args)
        {
            if (args == null || args.Count == 0)
                return "";

            return args[0];
        }

        protected override string GetFormForNumber(int num, string formOne, string formSeveral, string formMany)
        {
            return formOne;
        }

        /// <summary>
        /// Resolves custom language functions, including {ezafeh: {0}}.
        /// </summary>
        public override string ResolveFunction(string functionName, List<string> args, string fullStringForReference)
        {
            if (string.Equals(functionName, "ezafeh", StringComparison.OrdinalIgnoreCase) && args.Count > 0)
            {
                string word = args[0].Trim();
                return PersianWordLookupHelper.ResolveWithProgressiveTail(
                    word,
                    stem => TryLookUp("ezafeh", stem, 1, out string result, fullStringForReference) ? result : null,
                    stem =>
                    {
                        if (stem.EndsWith("ا") || stem.EndsWith("و"))
                            return stem + "ی";
                        if (stem.EndsWith("ه"))
                            return stem + ZWNJ + "ی";
                        if (stem.EndsWith("ی"))
                            return stem + Kasra.ToString();
                        return stem + Kasra.ToString();
                    }
                );
            }

            return base.ResolveFunction(functionName, args, fullStringForReference);
        }

        /// <summary>
        /// Final text post-processing for Persian: normalizes Arabic Yeh/Kaf to authentic Persian forms.
        /// </summary>
        public override string PostProcessed(string str)
        {
            str = base.PostProcessed(str);
            if (string.IsNullOrEmpty(str))
                return str;

            return str.Replace('ك', 'ک').Replace('ي', 'ی').Replace('ى', 'ی');
        }
    }
}
