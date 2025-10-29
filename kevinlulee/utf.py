# utf_constants.py
# Common Unicode “UTF” constants as Python module-level defs.
# Each constant is a one-character string. Comments include the official name and code point.

# ── Dots & Bullets ──────────────────────────────────────────────────────────────
SMALL_DOT              = "·"  # MIDDLE DOT — U+00B7
MIDDLE_DOT             = "·"  # MIDDLE DOT — U+00B7
HEART                  = "♥"  # BLACK HEART SUIT — U+2665
# BULLET                 = "•"  # BULLET — U+2022
# TRIANGULAR_BULLET      = "‣"  # TRIANGULAR BULLET — U+2023
# BULLET_OPERATOR        = "∙"  # BULLET OPERATOR — U+2219
# DOT_OPERATOR           = "⋅"  # DOT OPERATOR — U+22C5
# ONE_DOT_LEADER         = "․"  # ONE DOT LEADER — U+2024
# TWO_DOT_LEADER         = "‥"  # TWO DOT LEADER — U+2025
# ELLIPSIS               = "…"  # HORIZONTAL ELLIPSIS — U+2026
#
# # ── Dashes & Hyphens ────────────────────────────────────────────────────────────
# HYPHEN                 = "‐"  # HYPHEN — U+2010
# NON_BREAKING_HYPHEN    = "-"  # NON-BREAKING HYPHEN — U+2011
# FIGURE_DASH            = "‒"  # FIGURE DASH — U+2012
# EN_DASH                = "–"  # EN DASH — U+2013
# EM_DASH                = "—"  # EM DASH — U+2014
# HORIZONTAL_BAR         = "―"  # HORIZONTAL BAR — U+2015
# MINUS_SIGN             = "−"  # MINUS SIGN — U+2212
#
# # ── Quotation Marks ─────────────────────────────────────────────────────────────
# LEFT_SINGLE_QUOTE      = "‘"  # LEFT SINGLE QUOTATION MARK — U+2018
# RIGHT_SINGLE_QUOTE     = "’"  # RIGHT SINGLE QUOTATION MARK — U+2019
# SINGLE_LOW9_QUOTE      = "‚"  # SINGLE LOW-9 QUOTATION MARK — U+201A
# LEFT_DOUBLE_QUOTE      = "“"  # LEFT DOUBLE QUOTATION MARK — U+201C
# RIGHT_DOUBLE_QUOTE     = "”"  # RIGHT DOUBLE QUOTATION MARK — U+201D
# DOUBLE_LOW9_QUOTE      = "„"  # DOUBLE LOW-9 QUOTATION MARK — U+201E
# SINGLE_PRIME           = "′"  # PRIME — U+2032
# DOUBLE_PRIME           = "″"  # DOUBLE PRIME — U+2033
#
# # ── Arrows ──────────────────────────────────────────────────────────────────────
# LEFT_ARROW             = "←"  # LEFTWARDS ARROW — U+2190
# UP_ARROW               = "↑"  # UPWARDS ARROW — U+2191
# RIGHT_ARROW            = "→"  # RIGHTWARDS ARROW — U+2192
# DOWN_ARROW             = "↓"  # DOWNWARDS ARROW — U+2193
# LEFT_RIGHT_ARROW       = "↔"  # LEFT RIGHT ARROW — U+2194
# UP_DOWN_ARROW          = "↕"  # UP DOWN ARROW — U+2195
# NORTH_WEST_ARROW       = "↖"  # NORTH WEST ARROW — U+2196
# NORTH_EAST_ARROW       = "↗"  # NORTH EAST ARROW — U+2197
# SOUTH_EAST_ARROW       = "↘"  # SOUTH EAST ARROW — U+2198
# SOUTH_WEST_ARROW       = "↙"  # SOUTH WEST ARROW — U+2199
# THIN_LEFT_ARROW        = "⟵"  # LONG LEFTWARDS ARROW — U+27F5
# THIN_RIGHT_ARROW       = "⟶"  # LONG RIGHTWARDS ARROW — U+27F6
# THIN_LEFT_RIGHT_ARROW  = "⟷"  # LONG LEFT RIGHT ARROW — U+27F7
# DOUBLE_LEFT_ARROW      = "⇐"  # LEFTWARDS DOUBLE ARROW — U+21D0
# DOUBLE_RIGHT_ARROW     = "⇒"  # RIGHTWARDS DOUBLE ARROW — U+21D2
# DOUBLE_LEFT_RIGHT_ARROW= "⇔"  # LEFT RIGHT DOUBLE ARROW — U+21D4
#
# # ── Mathematical Operators & Relations ─────────────────────────────────────────
# TIMES                  = "×"  # MULTIPLICATION SIGN — U+00D7
# DIVIDE                 = "÷"  # DIVISION SIGN — U+00F7
# PLUS_MINUS             = "±"  # PLUS-MINUS SIGN — U+00B1
# MULTIPLY               = "×"  # MULTIPLICATION SIGN — U+00D7
# FRACTION_SLASH         = "⁄"  # FRACTION SLASH — U+2044
# EQUALS                 = "="  # EQUALS SIGN — U+003D
# NOT_EQUAL              = "≠"  # NOT EQUAL TO — U+2260
# APPROX_EQUAL           = "≈"  # ALMOST EQUAL TO — U+2248
# IDENTICAL_TO           = "≡"  # IDENTICAL TO — U+2261
# LESS_THAN_OR_EQUAL     = "≤"  # LESS-THAN OR EQUAL TO — U+2264
# GREATER_THAN_OR_EQUAL  = "≥"  # GREATER-THAN OR EQUAL TO — U+2265
# MUCH_LESS_THAN         = "≪"  # MUCH LESS-THAN — U+226A
# MUCH_GREATER_THAN      = "≫"  # MUCH GREATER-THAN — U+226B
# INFINITY               = "∞"  # INFINITY — U+2211
# NABLA                  = "∇"  # NABLA — U+2207
# PARTIAL_DIFF           = "∂"  # PARTIAL DIFFERENTIAL — U+2202
# FOR_ALL                = "∀"  # FOR ALL — U+2200
# THERE_EXISTS           = "∃"  # THERE EXISTS — U+2203
# ELEMENT_OF             = "∈"  # ELEMENT OF — U+2208
# NOT_AN_ELEMENT_OF      = "∉"  # NOT AN ELEMENT OF — U+2209
# CONTAINS_AS_MEMBER     = "∋"  # CONTAINS AS MEMBER — U+220B
# PROPORTIONAL_TO        = "∝"  # PROPORTIONAL TO — U+221D
# SQUARE_ROOT            = "√"  # SQUARE ROOT — U+221A
# CUBE_ROOT              = "∛"  # CUBE ROOT — U+221B
# FOURTH_ROOT            = "∜"  # FOURTH ROOT — U+221C
# SUMMATION              = "∑"  # N-ARY SUMMATION — U+2211
# PRODUCT                = "∏"  # N-ARY PRODUCT — U+220F
# INTEGRAL               = "∫"  # INTEGRAL — U+222B
# DOUBLE_INTEGRAL        = "∬"  # DOUBLE INTEGRAL — U+222C
# TRIPLE_INTEGRAL        = "∭"  # TRIPLE INTEGRAL — U+222D
# ANGLE                  = "∠"  # ANGLE — U+2220
# MEASURED_ANGLE         = "∡"  # MEASURED ANGLE — U+2221
# RIGHT_ANGLE            = "∟"  # RIGHT ANGLE — U+221F
# PARALLEL_TO            = "∥"  # PARALLEL TO — U+2225
# PERPENDICULAR          = "⊥"  # UP TACK — U+22A5
# LOGICAL_AND            = "∧"  # LOGICAL AND — U+2227
# LOGICAL_OR             = "∨"  # LOGICAL OR — U+2228
# LOGICAL_NOT            = "¬"  # NOT SIGN — U+00AC
# IMPLIES                = "⇒"  # RIGHTWARDS DOUBLE ARROW — U+21D2
# EQUIVALENT             = "⇔"  # LEFT RIGHT DOUBLE ARROW — U+21D4
#
# # ── Set & Logic Symbols ─────────────────────────────────────────────────────────
# EMPTY_SET              = "∅"  # EMPTY SET — U+2205
# SUBSET_OF              = "⊂"  # SUBSET OF — U+2282
# SUPERSET_OF            = "⊃"  # SUPERSET OF — U+2283
# SUBSET_EQ              = "⊆"  # SUBSET OF OR EQUAL TO — U+2286
# SUPERSET_EQ            = "⊇"  # SUPERSET OF OR EQUAL TO — U+2287
# UNION                  = "∪"  # UNION — U+222A
# INTERSECTION           = "∩"  # INTERSECTION — U+2229
#
# # ── Currency ────────────────────────────────────────────────────────────────────
# EURO                   = "€"  # EURO SIGN — U+20AC
# POUND                  = "£"  # POUND SIGN — U+00A3
# YEN                    = "¥"  # YEN SIGN — U+00A5
# RUPEE                  = "₹"  # INDIAN RUPEE SIGN — U+20B9
# WON                    = "₩"  # WON SIGN — U+20A9
# NAIRA                  = "₦"  # NAIRA SIGN — U+20A6
# SHEKEL                 = "₪"  # NEW SHEQEL SIGN — U+20AA
# LIRA                   = "₺"  # TURKISH LIRA SIGN — U+20BA
# BITCOIN                = "₿"  # BITCOIN SIGN — U+20BF
# CENT_SIGN              = "¢"  # CENT SIGN — U+00A2
#
# # ── Punctuation & Editorial Marks ───────────────────────────────────────────────
# DEGREE                 = "°"  # DEGREE SIGN — U+00B0
# SECTION_SIGN           = "§"  # SECTION SIGN — U+00A7
# PILCROW                = "¶"  # PILCROW SIGN — U+00B6
# COPYRIGHT              = "©"  # COPYRIGHT SIGN — U+00A9
# REGISTERED             = "®"  # REGISTERED SIGN — U+00AE
# TRADEMARK              = "™"  # TRADE MARK SIGN — U+2122
# MICRO_SIGN             = "µ"  # MICRO SIGN — U+00B5
# INTERROBANG            = "‽"  # INTERROBANG — U+203D
# INVERTED_QUESTION_MARK = "¿"  # INVERTED QUESTION MARK — U+00BF
# INVERTED_EXCLAMATION   = "¡"  # INVERTED EXCLAMATION MARK — U+00A1
#
# # ── Spaces (use carefully; many are zero-width or invisible) ────────────────────
# NO_BREAK_SPACE         = "\u00A0"  # NO-BREAK SPACE — U+00A0
# EN_SPACE               = "\u2002"  # EN SPACE — U+2002
# EM_SPACE               = "\u2003"  # EM SPACE — U+2003
# THREE_PER_EM_SPACE     = "\u2004"  # THREE-PER-EM SPACE — U+2004
# FOUR_PER_EM_SPACE      = "\u2005"  # FOUR-PER-EM SPACE — U+2005
# SIX_PER_EM_SPACE       = "\u2006"  # SIX-PER-EM SPACE — U+2006
# FIGURE_SPACE           = "\u2007"  # FIGURE SPACE — U+2007
# PUNCTUATION_SPACE      = "\u2008"  # PUNCTUATION SPACE — U+2008
# THIN_SPACE             = "\u2009"  # THIN SPACE — U+2009
# HAIR_SPACE             = "\u200A"  # HAIR SPACE — U+200A
# ZERO_WIDTH_SPACE       = "\u200B"  # ZERO WIDTH SPACE — U+200B
# ZERO_WIDTH_NON_JOINER  = "\u200C"  # ZERO WIDTH NON-JOINER — U+200C
# ZERO_WIDTH_JOINER      = "\u200D"  # ZERO WIDTH JOINER — U+200D
# NARROW_NO_BREAK_SPACE  = "\u202F"  # NARROW NO-BREAK SPACE — U+202F
# MEDIUM_MATHEMATICAL_SPACE = "\u205F"  # MEDIUM MATHEMATICAL SPACE — U+205F
# WORD_JOINER            = "\u2060"  # WORD JOINER — U+2060
# ZERO_WIDTH_NBSP        = "\uFEFF"  # ZERO WIDTH NO-BREAK SPACE — U+FEFF
#
# # ── Fractions ───────────────────────────────────────────────────────────────────
# ONE_HALF               = "½"  # VULGAR FRACTION ONE HALF — U+00BD
# ONE_QUARTER            = "¼"  # VULGAR FRACTION ONE QUARTER — U+00BC
# THREE_QUARTERS         = "¾"  # VULGAR FRACTION THREE QUARTERS — U+00BE
# ONE_THIRD              = "⅓"  # VULGAR FRACTION ONE THIRD — U+2153
# TWO_THIRDS             = "⅔"  # VULGAR FRACTION TWO THIRDS — U+2154
# ONE_FIFTH              = "⅕"  # VULGAR FRACTION ONE FIFTH — U+2155
# TWO_FIFTHS             = "⅖"  # VULGAR FRACTION TWO FIFTHS — U+2156
# THREE_FIFTHS           = "⅗"  # VULGAR FRACTION THREE FIFTHS — U+2157
# FOUR_FIFTHS            = "⅘"  # VULGAR FRACTION FOUR FIFTHS — U+2158
#
# # ── Superscripts & Subscripts ───────────────────────────────────────────────────
# SUPERSCRIPT_ZERO       = "⁰"  # SUPERSCRIPT ZERO — U+2070
# SUPERSCRIPT_ONE        = "¹"  # SUPERSCRIPT ONE — U+00B9
# SUPERSCRIPT_TWO        = "²"  # SUPERSCRIPT TWO — U+00B2
# SUPERSCRIPT_THREE      = "³"  # SUPERSCRIPT THREE — U+00B3
# SUPERSCRIPT_MINUS      = "⁻"  # SUPERSCRIPT MINUS — U+207B
# SUBSCRIPT_ZERO         = "₀"  # SUBSCRIPT ZERO — U+2080
# SUBSCRIPT_ONE          = "₁"  # SUBSCRIPT ONE — U+2081
# SUBSCRIPT_TWO          = "₂"  # SUBSCRIPT TWO — U+2082
# SUBSCRIPT_THREE        = "₃"  # SUBSCRIPT THREE — U+2083
# SUBSCRIPT_MINUS        = "₋"  # SUBSCRIPT MINUS — U+208B
#
# # ── Boxes, Checks, and Ballots ──────────────────────────────────────────────────
# BALLOT_BOX             = "☐"  # BALLOT BOX — U+2610
# BALLOT_BOX_WITH_CHECK  = "☑"  # BALLOT BOX WITH CHECK — U+2611
# BALLOT_BOX_WITH_X      = "☒"  # BALLOT BOX WITH X — U+2612
# CHECK_MARK             = "✓"  # CHECK MARK — U+2713
# HEAVY_CHECK_MARK       = "✔"  # HEAVY CHECK MARK — U+2714
# MULTIPLICATION_X       = "✗"  # BALLOT X — U+2717
# HEAVY_MULTIPLICATION_X = "✘"  # HEAVY BALLOT X — U+2718
#
# # ── Geometric Shapes ────────────────────────────────────────────────────────────
# BLACK_CIRCLE           = "●"  # BLACK CIRCLE — U+25CF
# WHITE_CIRCLE           = "○"  # WHITE CIRCLE — U+25CB
# BLACK_SQUARE           = "■"  # BLACK SQUARE — U+25A0
# WHITE_SQUARE           = "□"  # WHITE SQUARE — U+25A1
# BLACK_SMALL_SQUARE     = "▪"  # BLACK SMALL SQUARE — U+25AA
# WHITE_SMALL_SQUARE     = "▫"  # WHITE SMALL SQUARE — U+25AB
# BLACK_DIAMOND          = "◆"  # BLACK DIAMOND — U+25C6
# WHITE_DIAMOND          = "◇"  # WHITE DIAMOND — U+25C7
# BLACK_TRIANGLE_UP      = "▲"  # BLACK UP-POINTING TRIANGLE — U+25B2
# BLACK_TRIANGLE_DOWN    = "▼"  # BLACK DOWN-POINTING TRIANGLE — U+25BC
# BLACK_TRIANGLE_LEFT    = "◀"  # BLACK LEFT-POINTING TRIANGLE — U+25C0
# BLACK_TRIANGLE_RIGHT   = "▶"  # BLACK RIGHT-POINTING TRIANGLE — U+25B6
#
# # ── Box Drawing (samples) ───────────────────────────────────────────────────────
# BOX_DRAWINGS_LIGHT_H   = "─"  # BOX DRAWINGS LIGHT HORIZONTAL — U+2500
# BOX_DRAWINGS_LIGHT_V   = "│"  # BOX DRAWINGS LIGHT VERTICAL — U+2502
# BOX_DRAWINGS_LIGHT_TL  = "┌"  # BOX DRAWINGS LIGHT DOWN AND RIGHT — U+250C
# BOX_DRAWINGS_LIGHT_TR  = "┐"  # BOX DRAWINGS LIGHT DOWN AND LEFT — U+2510
# BOX_DRAWINGS_LIGHT_BL  = "└"  # BOX DRAWINGS LIGHT UP AND RIGHT — U+2514
# BOX_DRAWINGS_LIGHT_BR  = "┘"  # BOX DRAWINGS LIGHT UP AND LEFT — U+2518
# BOX_DRAWINGS_LIGHT_T   = "┬"  # BOX DRAWINGS LIGHT DOWN AND HORIZONTAL — U+252C
# BOX_DRAWINGS_LIGHT_B   = "┴"  # BOX DRAWINGS LIGHT UP AND HORIZONTAL — U+2534
# BOX_DRAWINGS_LIGHT_L   = "├"  # BOX DRAWINGS LIGHT VERTICAL AND RIGHT — U+251C
# BOX_DRAWINGS_LIGHT_R   = "┤"  # BOX DRAWINGS LIGHT VERTICAL AND LEFT — U+2524
# BOX_DRAWINGS_LIGHT_C   = "┼"  # BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL — U+253C
#
# # ── Miscellaneous Symbols ───────────────────────────────────────────────────────
# HEART_BLACK            = "♥"  # BLACK HEART SUIT — U+2665
# HEART_WHITE            = "♡"  # WHITE HEART SUIT — U+2661
# SPADE_BLACK            = "♠"  # BLACK SPADE SUIT — U+2660
# CLUB_BLACK             = "♣"  # BLACK CLUB SUIT — U+2663
# DIAMOND_BLACK          = "♦"  # BLACK DIAMOND SUIT — U+2666
# MUSIC_NOTE             = "♪"  # EIGHTH NOTE — U+266A
# MUSIC_NOTES            = "♫"  # BEAMED EIGHTH NOTES — U+266B
# STAR_BLACK             = "★"  # BLACK STAR — U+2605
# STAR_WHITE             = "☆"  # WHITE STAR — U+2606
# WARNING_SIGN           = "⚠"  # WARNING SIGN — U+26A0
# INFO_SOURCE            = "ℹ"  # INFORMATION SOURCE — U+2139
# RECYCLE_SYMBOL         = "♻"  # BLACK UNIVERSAL RECYCLING SYMBOL — U+267B
# SCISSORS               = "✂"  # BLACK SCISSORS — U+2702
# PENCIL                 = "✎"  # LOWER RIGHT PENCIL — U+270E
#
# # ── Brackets & Delimiters (curly/angle etc.) ────────────────────────────────────
# LEFT_SINGLE_ANGLE      = "‹"  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK — U+2039
# RIGHT_SINGLE_ANGLE     = "›"  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK — U+203A
# LEFT_DOUBLE_ANGLE      = "«"  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK — U+00AB
# RIGHT_DOUBLE_ANGLE     = "»"  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK — U+00BB
# LEFT_CEILING           = "⌈"  # LEFT CEILING — U+2308
# RIGHT_CEILING          = "⌉"  # RIGHT CEILING — U+2309
# LEFT_FLOOR             = "⌊"  # LEFT FLOOR — U+230A
# RIGHT_FLOOR            = "⌋"  # RIGHT FLOOR — U+230B
# LEFT_ANGLE_BRACKET     = "⟨"  # MATHEMATICAL LEFT ANGLE BRACKET — U+27E8
# RIGHT_ANGLE_BRACKET    = "⟩"  # MATHEMATICAL RIGHT ANGLE BRACKET — U+27E9
#
# # ── Misc Technical ──────────────────────────────────────────────────────────────
# DEGREE_CELSIUS         = "℃"  # DEGREE CELSIUS — U+2103
# DEGREE_FAHRENHEIT      = "℉"  # DEGREE FAHRENHEIT — U+2109
# OHM_SIGN               = "Ω"  # GREEK CAPITAL LETTER OMEGA — U+03A9 (commonly Ω)
# PER_MILLE              = "‰"  # PER MILLE SIGN — U+2030
# PER_TEN_THOUSAND       = "‱"  # PER TEN THOUSAND SIGN — U+2031
# LEFT_ARROW_HOOK        = "↩"  # LEFTWARDS ARROW WITH HOOK — U+21A9
# RIGHT_ARROW_HOOK       = "↪"  # RIGHTWARDS ARROW WITH HOOK — U+21AA
# RETURN_SYMBOL          = "⏎"  # RETURN SYMBOL — U+23CE
# ESCAPE_SYMBOL          = "⎋"  # BROKEN CIRCLE WITH NORTHWEST ARROW — U+238B
#
