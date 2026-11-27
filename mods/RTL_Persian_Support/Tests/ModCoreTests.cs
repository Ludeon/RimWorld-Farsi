using System;
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
            // Repeated calls must remain idempotent via ZWS guard
            Assert.Equal(fixedOnce, PersianFixer.Fix(fixedOnce));

            string noMarker = PersianFixer.FixNoMarker("سلام دنیا");
            Assert.False(noMarker.Contains("\u200B", StringComparison.Ordinal));
        }

        [Fact]
        public void PersianFixer_PreservesRichTextTagsCleanly()
        {
            const string input = "<color=#FF0000>هشدار مهم</color>";
            string output = PersianFixer.FixNoMarker(input);
            Assert.Contains("<color=#FF0000>", output);
            Assert.Contains("</color>", output);
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
            Assert.Contains("1234", output);
        }

        [Fact]
        public void PersianFixer_NullOrEmpty_ReturnsGracefully()
        {
            Assert.Null(PersianFixer.Fix(null));
            Assert.Equal(string.Empty, PersianFixer.Fix(string.Empty));
        }
    }
}
