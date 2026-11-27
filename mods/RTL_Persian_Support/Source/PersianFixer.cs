using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;
using ArabicSupport;
using UnityEngine;
using Verse;

namespace RTL_Persian
{
    public static class PersianFixer
    {
        private struct WrapCacheKey : IEquatable<WrapCacheKey>
        {
            public readonly string Text;
            public readonly int StyleKey;
            public readonly int WidthKey;

            public WrapCacheKey(string text, int styleKey, int widthKey)
            {
                Text = text;
                StyleKey = styleKey;
                WidthKey = widthKey;
            }

            public bool Equals(WrapCacheKey other)
            {
                return StyleKey == other.StyleKey
                    && WidthKey == other.WidthKey
                    && string.Equals(Text, other.Text, StringComparison.Ordinal);
            }

            public override bool Equals(object obj) => obj is WrapCacheKey other && Equals(other);

            public override int GetHashCode()
            {
                unchecked
                {
                    int hash = Text != null ? Text.GetHashCode() : 0;
                    hash = (hash * 397) ^ StyleKey;
                    hash = (hash * 397) ^ WidthKey;
                    return hash;
                }
            }
        }

        private struct ProtectedToken
        {
            public char Marker;
            public string Value;

            public ProtectedToken(char marker, string value)
            {
                Marker = marker;
                Value = value;
            }
        }

        private static readonly Dictionary<string, string> Cache = new Dictionary<string, string>();
        private static readonly Dictionary<WrapCacheKey, string> WrapCache = new Dictionary<WrapCacheKey, string>();
        private const int MaxCacheSize = 8000;
        private const int MaxWrapCacheSize = 4000;

        private static readonly Regex PairedRichTagRegex = new Regex(
            @"<(color|b|i|size|material)(?:=[^>]*)?>(.*?)</\1>",
            RegexOptions.Singleline | RegexOptions.IgnoreCase | RegexOptions.Compiled
        );

        private static readonly Regex AnyRichTagRegex = new Regex(
            @"</?(?:color|b|i|size|material)(?:=[^>]*)?>",
            RegexOptions.IgnoreCase | RegexOptions.Compiled
        );

        private static readonly Regex GluedTimeUnitRegex = new Regex(
            @"(\d)(ساعت|روز|دقیقه|ثانیه|سال)(?![\u0600-\u06FF\uFB50-\uFEFC])",
            RegexOptions.Compiled
        );

        private static GUIContent _measureContent;

        public static void ClearCache()
        {
            lock (Cache)
            {
                Cache.Clear();
            }
            lock (WrapCache)
            {
                WrapCache.Clear();
            }
        }

        /// <summary>
        /// Normalizes, shapes, and applies BiDi visual ordering for Unity IMGUI rendering.
        /// Appends a Zero-Width Space marker to keep repeated calls idempotent.
        /// </summary>
        public static string Fix(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;

            lock (Cache)
            {
                if (Cache.TryGetValue(text, out string cached))
                    return cached;
            }

            if (text.Contains("\u200B") || ContainsPresentationForms(text) || !ContainsArabicOrPersian(text))
            {
                return text;
            }

            string normalized = PreprocessText(text);
            string result = FixInternalMultiLine(normalized) + "\u200B";

            lock (Cache)
            {
                if (Cache.Count >= MaxCacheSize) Cache.Clear();
                Cache[text] = result;
            }

            return result;
        }

        /// <summary>
        /// Shapes and reorders text without appending a ZWS marker (safe for TextMesh / TextMeshPro).
        /// </summary>
        public static string FixNoMarker(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;
            string clean = text.Replace("\u200B", "");
            if (ContainsPresentationForms(clean) || !ContainsArabicOrPersian(clean))
            {
                return clean;
            }
            return FixInternalMultiLine(PreprocessText(clean));
        }

        /// <summary>
        /// Wraps logical RTL paragraphs to fit within width using Unity's GUIStyle metrics,
        /// then shapes and reorders each visual line individually so lines read top-to-bottom.
        /// </summary>
        public static string FixForWidth(string text, float width, GUIStyle style, float height = -1f)
        {
            if (string.IsNullOrEmpty(text)) return text;
            if (text.Contains("\u200B") || ContainsPresentationForms(text) || !ContainsArabicOrPersian(text))
                return text;

            if (style == null || !style.wordWrap || width <= 4f)
                return Fix(text);

            // If box height can't fit 2 lines anyway, avoid introducing synthetic newlines
            if (height >= 0f && height < style.lineHeight * 1.5f)
                return Fix(text);

            int fontId = style.font != null ? style.font.GetInstanceID() : 0;
            int styleKey = unchecked((fontId * 397) ^ (style.fontSize << 4) ^ (int)style.fontStyle);
            int widthKey = Mathf.RoundToInt(width);
            var key = new WrapCacheKey(text, styleKey, widthKey);

            lock (WrapCache)
            {
                if (WrapCache.TryGetValue(key, out string cached))
                    return cached;
            }

            string normalized = PreprocessText(text);
            string[] paragraphs = normalized.Split('\n');
            float oneLineMaxHeight = Math.Max(style.lineHeight * 1.45f, MeasureLineHeight("A", style, 10000f) * 1.45f);
            var finalLines = new List<string>(paragraphs.Length);

            for (int p = 0; p < paragraphs.Length; p++)
            {
                string para = paragraphs[p];
                if (para.Length == 0)
                {
                    finalLines.Add(string.Empty);
                    continue;
                }

                string singleFixed = FixInternalSingleLine(para);
                if (FitsOnSingleLine(singleFixed, style, width, oneLineMaxHeight))
                {
                    finalLines.Add(singleFixed);
                    continue;
                }

                WrapParagraphLogical(para, width, style, oneLineMaxHeight, finalLines);
            }

            string result = string.Join("\n", finalLines) + "\u200B";

            lock (WrapCache)
            {
                if (WrapCache.Count >= MaxWrapCacheSize) WrapCache.Clear();
                WrapCache[key] = result;
            }

            return result;
        }

        private static string PreprocessText(string text)
        {
            string s = text.Replace("\r\n", "\n").Replace('\r', '\n');
            s = s.Replace('ي', 'ی').Replace('ك', 'ک');
            s = GluedTimeUnitRegex.Replace(s, "$1 $2");
            return s;
        }

        private static float MeasureLineHeight(string line, GUIStyle style, float width)
        {
            if (_measureContent == null) _measureContent = new GUIContent();
            _measureContent.text = line.IndexOf('<') >= 0 ? ColoredText.StripTags(line) : line;
            return style.CalcHeight(_measureContent, width);
        }

        private static bool FitsOnSingleLine(string fixedLine, GUIStyle style, float width, float oneLineMaxHeight)
        {
            if (_measureContent == null) _measureContent = new GUIContent();
            _measureContent.text = fixedLine.IndexOf('<') >= 0 ? ColoredText.StripTags(fixedLine) : fixedLine;
            if (style.CalcSize(_measureContent).x <= width - 0.5f)
                return true;
            return style.CalcHeight(_measureContent, width) <= oneLineMaxHeight;
        }

        private static void WrapParagraphLogical(string para, float width, GUIStyle style, float oneLineMaxHeight, List<string> outputLines)
        {
            List<string> words = SplitWordsPreservingTags(para);
            if (words.Count == 0)
            {
                outputLines.Add(string.Empty);
                return;
            }

            var activeTags = new List<(string name, string openTag)>(4);
            int start = 0;

            while (start < words.Count)
            {
                int lo = start + 1;
                int hi = words.Count;
                int bestEnd = start + 1;
                string bestFixed = null;

                while (lo <= hi)
                {
                    int mid = lo + ((hi - lo) >> 1);
                    string candidateRaw = BuildWrappedSlice(words, start, mid, activeTags);
                    string candidateFixed = FixInternalSingleLine(candidateRaw);

                    if (FitsOnSingleLine(candidateFixed, style, width, oneLineMaxHeight))
                    {
                        bestEnd = mid;
                        bestFixed = candidateFixed;
                        lo = mid + 1;
                    }
                    else
                    {
                        hi = mid - 1;
                    }
                }

                if (bestFixed == null)
                {
                    string fallbackRaw = BuildWrappedSlice(words, start, start + 1, activeTags);
                    bestFixed = FixInternalSingleLine(fallbackRaw);
                    bestEnd = start + 1;
                }

                outputLines.Add(bestFixed);

                for (int w = start; w < bestEnd; w++)
                {
                    UpdateTagStack(words[w], activeTags);
                }
                start = bestEnd;
            }
        }

        private static List<string> SplitWordsPreservingTags(string para)
        {
            var words = new List<string>();
            int i = 0;
            int len = para.Length;
            var current = new StringBuilder();

            while (i < len)
            {
                char c = para[i];
                if (c == '<')
                {
                    int close = para.IndexOf('>', i + 1);
                    if (close > i)
                    {
                        current.Append(para, i, close - i + 1);
                        i = close + 1;
                        continue;
                    }
                }

                if (c == ' ')
                {
                    if (current.Length > 0)
                    {
                        words.Add(current.ToString());
                        current.Clear();
                    }
                    i++;
                    continue;
                }

                current.Append(c);
                i++;
            }

            if (current.Length > 0)
                words.Add(current.ToString());

            return words;
        }

        private static string BuildWrappedSlice(List<string> words, int start, int end, List<(string name, string openTag)> initialTags)
        {
            var sb = new StringBuilder();
            for (int t = 0; t < initialTags.Count; t++)
            {
                sb.Append(initialTags[t].openTag);
            }

            for (int w = start; w < end; w++)
            {
                if (w > start) sb.Append(' ');
                sb.Append(words[w]);
            }

            var endTags = new List<(string name, string openTag)>(initialTags);
            for (int w = start; w < end; w++)
            {
                UpdateTagStack(words[w], endTags);
            }
            for (int t = endTags.Count - 1; t >= 0; t--)
            {
                sb.Append("</").Append(endTags[t].name).Append('>');
            }

            return sb.ToString();
        }

        private static void UpdateTagStack(string word, List<(string name, string openTag)> stack)
        {
            if (word.IndexOf('<') < 0) return;

            MatchCollection matches = AnyRichTagRegex.Matches(word);
            for (int i = 0; i < matches.Count; i++)
            {
                string tag = matches[i].Value;
                if (tag.StartsWith("</", StringComparison.Ordinal))
                {
                    string closeName = tag.Substring(2, tag.Length - 3).Trim().ToLowerInvariant();
                    for (int s = stack.Count - 1; s >= 0; s--)
                    {
                        if (stack[s].name == closeName)
                        {
                            stack.RemoveAt(s);
                            break;
                        }
                    }
                }
                else
                {
                    int eqIdx = tag.IndexOf('=');
                    int nameLen = (eqIdx >= 0 ? eqIdx : tag.Length - 1) - 1;
                    if (nameLen > 0)
                    {
                        string openName = tag.Substring(1, nameLen).Trim().ToLowerInvariant();
                        stack.Add((openName, tag));
                    }
                }
            }
        }

        private static string FixInternalMultiLine(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;
            if (text.IndexOf('\n') < 0)
                return FixInternalSingleLine(text);

            string[] lines = text.Split('\n');
            for (int i = 0; i < lines.Length; i++)
            {
                lines[i] = FixInternalSingleLine(lines[i]);
            }
            return string.Join("\n", lines);
        }

        private static string FixInternalSingleLine(string text)
        {
            if (string.IsNullOrEmpty(text) || ContainsPresentationForms(text) || !ContainsArabicOrPersian(text))
            {
                return text;
            }

            List<ProtectedToken> protectedTokens = null;
            string working = text;

            if (working.IndexOf('<') >= 0)
            {
                protectedTokens = new List<ProtectedToken>();

                // Step 1: Handle paired tags like <color=#999999FF>inner</color>
                working = PairedRichTagRegex.Replace(working, m =>
                {
                    string full = m.Value;
                    string inner = m.Groups[2].Value;
                    int openEnd = full.IndexOf('>') + 1;
                    int closeStart = full.LastIndexOf('<');
                    string openTag = full.Substring(0, openEnd);
                    string closeTag = full.Substring(closeStart);

                    bool innerIsRtl = ContainsArabicOrPersian(inner);
                    string fixedInner = FixInternalSingleLine(inner);
                    int idx = protectedTokens.Count;
                    char marker = innerIsRtl ? (char)(0xE000 + idx) : (char)(0xE800 + idx);
                    protectedTokens.Add(new ProtectedToken(marker, openTag + fixedInner + closeTag));
                    return marker.ToString();
                });

                // Step 2: Handle any remaining unmatched RichText tags
                working = AnyRichTagRegex.Replace(working, m =>
                {
                    int idx = protectedTokens.Count;
                    char marker = (char)(0xF000 + idx);
                    protectedTokens.Add(new ProtectedToken(marker, m.Value));
                    return marker.ToString();
                });
            }

            string normalized = working.Replace('ي', 'ی').Replace('ك', 'ک');

            string shaped;
            if (ContainsArabicOrPersian(normalized))
            {
                shaped = ArabicFixer.Fix(normalized, true, true, false);
                shaped = shaped.Replace("\u200C", "");
            }
            else
            {
                shaped = ArabicFixerTool.BidiReorder.ReorderLogicalToVisual(normalized);
            }

            if (protectedTokens != null && protectedTokens.Count > 0)
            {
                for (int i = 0; i < protectedTokens.Count; i++)
                {
                    shaped = shaped.Replace(protectedTokens[i].Marker.ToString(), protectedTokens[i].Value);
                }
            }

            return shaped;
        }

        private static bool ContainsPresentationForms(string text)
        {
            for (int i = 0; i < text.Length; i++)
            {
                char c = text[i];
                if (c >= '\uFB50' && c <= '\uFEFC')
                    return true;
            }
            return false;
        }

        private static bool ContainsArabicOrPersian(string text)
        {
            for (int i = 0; i < text.Length; i++)
            {
                char c = text[i];
                if ((c >= '\u0600' && c <= '\u06FF') || (c >= '\u0750' && c <= '\u077F'))
                    return true;
            }
            return false;
        }
    }
}
