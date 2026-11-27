using System;
using System.Collections.Generic;
using ArabicSupport;
using Xunit;

namespace RTL_Persian.Tests
{
    public class ModCoreTests
    {
        [Fact]
        public void PersianFixer_PureLatinText_RemainsUnchanged()
        {
            const string input = "RimWorld 1.6 (English)";
            Assert.Equal(input, PersianFixer.Fix(input));
            Assert.Equal(input, PersianFixer.FixNoMarker(input));
        }

        [Fact]
        public void PersianFixer_PersianText_ShapesAndAppendsIdempotencyMarker()
        {
            string fixedOnce = PersianFixer.Fix("سلام دنیا");
            Assert.EndsWith("\u200B", fixedOnce);
            Assert.Equal(fixedOnce, PersianFixer.Fix(fixedOnce));

            string noMarker = PersianFixer.FixNoMarker("سلام دنیا");
            Assert.False(noMarker.Contains("\u200B", StringComparison.Ordinal));
        }

        [Theory]
        [InlineData("بمب دست‌ساز (IED)")]
        [InlineData("پیشرفت (91%)")]
        [InlineData("علف (91% رشد کرده)")]
        [InlineData("دما: -5C")]
        public void PersianFixer_PairedBracketsNumbersAndPercentages_PreservesBracketSemantics(string input)
        {
            string output = PersianFixer.FixNoMarker(input);
            Assert.False(string.IsNullOrEmpty(output));
            // Brackets must remain balanced and tokens must survive intact
            int openParens = output.Split('(').Length - 1;
            int closeParens = output.Split(')').Length - 1;
            Assert.Equal(openParens, closeParens);
            if (input.Contains("IED", StringComparison.Ordinal))
                Assert.Contains("IED", output, StringComparison.Ordinal);
            if (input.Contains("91%", StringComparison.Ordinal))
                Assert.Contains("91%", output, StringComparison.Ordinal);
            if (input.Contains("-5C", StringComparison.Ordinal))
                Assert.Contains("-5C", output, StringComparison.Ordinal);
        }

        [Fact]
        public void PersianFixer_PreservesRichTextTagsCleanly()
        {
            const string input = "<color=#FF0000><b>هشدار</b>: (IED)</color>";
            string output = PersianFixer.FixNoMarker(input);
            Assert.Contains("<color=#FF0000>", output, StringComparison.Ordinal);
            Assert.Contains("</color>", output, StringComparison.Ordinal);
            Assert.Contains("<b>", output, StringComparison.Ordinal);
            Assert.Contains("</b>", output, StringComparison.Ordinal);
            Assert.Contains("IED", output, StringComparison.Ordinal);
        }

        [Fact]
        public void PersianFixer_MultiLine_PreservesTopToBottomOrder()
        {
            string output = PersianFixer.FixNoMarker("اول\nدوم");
            string[] lines = output.Split('\n');
            Assert.Equal(2, lines.Length);
            Assert.Equal(PersianFixer.FixNoMarker("اول"), lines[0]);
            Assert.Equal(PersianFixer.FixNoMarker("دوم"), lines[1]);
        }

        [Fact]
        public void PersianFixer_ZwnjPreventsJoiningAndIsStrippedCleanly()
        {
            string withZwnj = PersianFixer.FixNoMarker("می‌توانند");
            string withoutZwnj = PersianFixer.FixNoMarker("میتوانند");
            Assert.False(withZwnj.Contains("\u200C", StringComparison.Ordinal));
            Assert.NotEqual(withoutZwnj, withZwnj);
        }

        [Fact]
        public void PersianFixer_GluedTimeUnitGetsSpacedCleanly()
        {
            string output = PersianFixer.FixNoMarker("12ساعت");
            Assert.Contains("12", output, StringComparison.Ordinal);
            Assert.Contains(" ", output, StringComparison.Ordinal);
        }

        [Fact]
        public void ArabicFixer_ConsecutiveSpacesWithRtlFalse_DoesNotThrow()
        {
            string output = ArabicFixer.Fix("hello   world", false);
            Assert.NotNull(output);
        }

        [Fact]
        public void ArabicFixer_TashkeelAndDigits_DoesNotThrowOutOfRange()
        {
            string output = ArabicFixer.Fix("مُحَمَّد 1234", true, true, false);
            Assert.NotNull(output);
            Assert.Contains("1234", output, StringComparison.Ordinal);
        }

        [Fact]
        public void PersianFixer_NullOrEmpty_ReturnsGracefully()
        {
            Assert.Null(PersianFixer.Fix(null));
            Assert.Equal(string.Empty, PersianFixer.Fix(string.Empty));
        }

        [Fact]
        public void ProgressiveLookup_MatchesStemAndPreservesQualityOrModifierTail()
        {
            var table = new Dictionary<string, string>
            {
                { "گرز فولادی", "گرزِ فولادی" },
                { "تفنگ", "تفنگِ" },
            };

            string Lookup(string k) => table.TryGetValue(k, out string v) ? v : null;

            Assert.Equal(
                "گرزِ فولادی (عالی)",
                PersianWordLookupHelper.ResolveWithProgressiveTail("گرز فولادی (عالی)", Lookup)
            );
            Assert.Equal(
                "تفنگِ پلاسمایی سبک",
                PersianWordLookupHelper.ResolveWithProgressiveTail("تفنگ پلاسمایی سبک", Lookup)
            );
            Assert.Equal(
                "کلاه‌خودِ (افسانه‌ای)",
                PersianWordLookupHelper.ResolveWithProgressiveTail(
                    "کلاه‌خود (افسانه‌ای)",
                    Lookup,
                    stem => stem + "\u0650"
                )
            );
        }
    }
}
