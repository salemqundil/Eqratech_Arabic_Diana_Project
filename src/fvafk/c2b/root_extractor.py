"""
Root extraction for Arabic words.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import List, Optional, Set, Tuple

from .morpheme import Root, RootType


def normalize_hamza_for_roots(text: str) -> str:
    """
    Universal hamza normalization for root extraction.

    Applies Arabic orthographic rules:
    - Hamza carriers → base letters
    - Preserves linguistic structure
    - Works for ALL Arabic words

    Args:
        text: Arabic text with possible hamza carriers

    Returns:
        Normalized text with hamza carriers replaced by base letters

    Examples:
        >>> normalize_hamza_for_roots("مُؤْمِنُونَ")
        "مامنون"  # ؤ → ا
        >>> normalize_hamza_for_roots("أَكَلَ")
        "اكل"  # أ → ا
    """
    text = unicodedata.normalize('NFC', text)
    text = text.replace('أ', 'ا')
    text = text.replace('إ', 'ا')
    text = text.replace('آ', 'ا')
    text = text.replace('ؤ', 'ا')
    text = text.replace('ئ', 'ي')
    text = ''.join(
        c
        for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return unicodedata.normalize('NFC', text)


@dataclass(frozen=True)
class RootExtractionResult:
    root: Optional[Root]
    normalized_word: str
    stripped_word: str
    prefix: str
    suffix: str


class RootExtractor:
    DIACRITICS = "َُِْٰٓٔٱًٌٍّ"
    WEAK_LETTERS = {'و', 'ي', 'ا', 'ء'}
    PATTERN_LETTERS = {'ا', 'و', 'ي'}

    PREFIXES = [
        'است',  # استفعل
        'ال', 'وال', 'فال', 'بال', 'كال', 'لل',  # أل التعريف
        'س', 'سي', 'سو',  # حرف استقبال
        'ف', 'و', 'ب', 'ك', 'ل',  # حروف عطف/جر
        'م', 'ت', 'ي', 'ن', 'أ',  # حروف مضارعة
        'تـ', 'يـ', 'نـ'
    ]
    SUFFIXES = [
        'ون', 'ين', 'ات', 'ان', 'تم', 'تن', 'وا',  # ضمائر جمع
        'ها', 'هم', 'هما', 'هن', 'كم', 'كن',  # ضمائر غائب/مخاطب
        # NOTE: Do NOT include bare "ن" here: it is too ambiguous and frequently
        # a true radical (e.g., مؤمنون -> مؤمن + ون).
        'ني', 'نا', 'ك', 'ه', 'ة'  # ضمائر مفرد + تاء مربوطة
    ]

    # Keep this conservative: multi-letter pronouns only.
    # Single-letter endings like (ي/ك/ه) are too ambiguous and can be true radicals
    # or orthographic endings (e.g., رمى -> رمي after ى->ي).
    PRONOUN_SUFFIXES = {'ها', 'هم', 'هما', 'هن', 'كم', 'كن', 'كما', 'ني', 'نا'}
    VERB_NUMBER_SUFFIXES = {'وا', 'ون', 'ين', 'ان', 'ات', 'تم', 'تن', 'ن'}

    # Quran-oriented "do not split" stems (only peel attached pronouns after them)
    _NO_SPLIT_STEMS = {"سيما"}

    # Rule table: (set of stripped forms, root letters). Applied only when stripping rules produce one of these forms.
    # No external knowledge: add entries here to get a root for a given stripped form.
    STRIPPED_FORM_TO_ROOT: List[Tuple[Set[str], Tuple[str, ...]]] = [
        ({"ترا", "يري", "راي"}, ("ر", "أ", "ي")),
        ({"وي", "وى", "ويٰ"}, ("س", "و", "ي")),  # applied only when prefix contains "است" (see below)
    ]

    def __init__(self, known_roots: Optional[Set[str]] = None):
        self.known_roots = known_roots or set()

    def extract(self, word: str) -> Optional[Root]:
        context = self._extract_context(word)
        return context.root

    def extract_with_affixes(self, word: str) -> RootExtractionResult:
        return self._extract_context(word)

    def _extract_context(self, word: str) -> RootExtractionResult:
        if not word:
            return RootExtractionResult(None, "", "", "", "")

        normalized_display = normalize_hamza_for_roots(self._normalize(word, expand_shadda=False))
        normalized_for_extraction = normalize_hamza_for_roots(self._normalize(word, expand_shadda=True))

        def _score_root(letters: Tuple[str, ...]) -> int:
            # Prefer triliteral, penalize weak letters.
            weak = sum(1 for ch in letters if ch in self.WEAK_LETTERS)
            base = 2 if len(letters) == 3 else 1
            return base * 10 + (10 - weak)

        def _build_candidate(*, allow_bkl: bool, allow_faw_fatha: bool) -> Tuple[RootExtractionResult, int]:
            stripped_extraction, prefix, suffix = self._strip_affixes(
                normalized_for_extraction,
                original_word=word,
                allow_bkl_clitics=allow_bkl,
                allow_faw_fatha_clitics=allow_faw_fatha,
            )
            stripped_display, _p2, _s2 = self._strip_affixes(
                normalized_display,
                original_word=word,
                allow_bkl_clitics=allow_bkl,
                allow_faw_fatha_clitics=allow_faw_fatha,
            )

            # Rule: if stripped form matches a rule table entry, return that root (no other inference).
            prefix_parts = (prefix or "").split("+")
            for forms, letters in self.STRIPPED_FORM_TO_ROOT:
                if stripped_extraction not in forms:
                    continue
                # Second rule (س-و-ي) applies only when prefix contains "است".
                if letters == ("س", "و", "ي") and "است" not in prefix_parts:
                    continue
                root = Root(letters=letters, root_type=RootType.TRILATERAL)
                return (
                    RootExtractionResult(
                        root=root,
                        normalized_word=normalized_display,
                        stripped_word=stripped_display,
                        prefix=prefix,
                        suffix=suffix,
                    ),
                    _score_root(root.letters),
                )

            consonants = self._extract_consonants(stripped_extraction, stripped_word=stripped_extraction)
            # Uthmani dagger alif (ٰ) often marks فَعْلَان (…ٰن) where final ن is pattern,
            # not a radical (e.g., الرَّحْمَٰنِ -> ر-ح-م).
            if "ٰ" in word and len(consonants) == 4 and consonants[-1] == "ن":
                maybe = consonants[:-1]
                if self._is_valid_root(maybe):
                    consonants = maybe

            root: Optional[Root] = None
            score = 0
            if self._is_valid_root(consonants):
                root_type = RootType.TRILATERAL if len(consonants) == 3 else RootType.QUADRILATERAL
                letters = tuple(consonants[: len(consonants)])
                root = Root(letters=letters, root_type=root_type)
                score = _score_root(letters)

            return (
                RootExtractionResult(
                    root=root,
                    normalized_word=normalized_display,
                    stripped_word=stripped_display,
                    prefix=prefix,
                    suffix=suffix,
                ),
                score,
            )

        # Explore a small candidate set and pick the best root score.
        # - `allow_bkl_clitics` helps tokens like: كزرع، بالكتاب...
        # - `allow_faw_fatha_clitics` helps tokens like: وَعَمِلُوا / فَآزَرَهُ
        #   but can be wrong for lexical فَ... like: فَضْلًا.
        candidates: List[Tuple[RootExtractionResult, int, Tuple[bool, bool]]] = []
        for allow_bkl in (False, True):
            for allow_faw in (False, True):
                cand, score = _build_candidate(allow_bkl=allow_bkl, allow_faw_fatha=allow_faw)
                # Prefer stripping ب when word starts with ب (بِدَيْنٍ → د-ي-ن not ب-د-ن).
                if cand.root and cand.root.letters[0] == "ب" and (word.startswith("ب") or word.startswith("بِ")):
                    score -= 5
                candidates.append((cand, score, (allow_bkl, allow_faw)))

        # Pick max score; tie-breaker prefers conservative (no bkl, no faw-fatha).
        def _tie_key(item):
            cand, score, (allow_bkl, allow_faw) = item
            penalty = (1 if allow_bkl else 0) + (1 if allow_faw else 0)
            # If the original explicitly starts with وَ/فَ and the candidate actually stripped
            # that clitic, prefer that candidate when scores are tied.
            prefer = 0
            if word.startswith("وَ") and ("و" in (cand.prefix or "").split("+")):
                prefer = 1
            if word.startswith("فَ") and ("ف" in (cand.prefix or "").split("+")):
                prefer = 1
            return (score, prefer, -penalty)

        best = max(candidates, key=_tie_key)
        return best[0]

    def _normalize(
        self, word: str, *, expand_shadda: bool = True, preserve_harakat: bool = False
    ) -> str:
        """
        تطبيع الكلمة (همزة، ألف، ى). عند preserve_harakat=True يُحافظ على التشكيل ولا يحذفه.
        """
        buffer: List[str] = []
        i = 0
        while i < len(word):
            ch = word[i]
            if ch == 'ّ':
                if expand_shadda and buffer:
                    buffer.append(buffer[-1])
                i += 1
                continue
            if not preserve_harakat and (ch in self.DIACRITICS or ch == 'ـ'):
                i += 1
                continue
            buffer.append(ch)
            i += 1
        text = ''.join(buffer)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ى', 'ي')
        if not preserve_harakat:
            text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ى', 'ي').replace('ـ', '')
        if not preserve_harakat:
            text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        return text.strip()

    def _strip_diacritics_surface(self, text: str) -> str:
        return "".join(
            ch for ch in unicodedata.normalize("NFC", text)
            if unicodedata.combining(ch) == 0
        ).replace("ـ", "").strip()

    def _strip_affixes(
        self,
        word: str,
        *,
        original_word: str = "",
        allow_bkl_clitics: bool = False,
        allow_faw_fatha_clitics: bool = False,
    ) -> Tuple[str, str, str]:
        """
        Segment word into (core, prefix_str, suffix_str).

        Note: `word` is typically already normalized (diacritics removed, hamza normalized).
        `original_word` is used only for a small amount of disambiguation for clitic prefixes.
        """
        text = word
        prefix_parts: List[str] = []

        # If this token had an initial shadda, the extraction-normalized form may begin
        # with a doubled letter (e.g., مَّغفرة -> ممغفرة). Collapse one copy so that
        # derivational prefixes like (مـ) do not leak into the extracted root.
        if original_word and "ّ" in original_word and len(text) >= 2 and text[0] == text[1]:
            text = text[1:]

        # NO_SPLIT stems: keep the stem intact, only allow pronoun suffix stripping later.
        # Example: سِيمَاهُمْ -> سيما + هم (do NOT strip "سي" as a prefix)
        no_split_mode = False
        if text.startswith("سيما"):
            no_split_mode = True

        # Remove tanwin-supporting alif for fathatan (…ًا) at the end of the token.
        # This helps pattern matching and prevents stems like: عظيمًا -> عظيما.
        if original_word and ("\u064b" in original_word) and text.endswith("ا") and len(text) > 3:
            text = text[:-1]

        # Lam of purpose/command (لام التعليل/الأمر): لِ + imperfect verb.
        # Example: لِيَغِيظَ -> ل + يغيظ; also after و/ف: وَلْيَتَّقِ -> و then ل then يتقي
        def _strip_lam_if_imperfect():
            if (not no_split_mode) and len(text) >= 2 and text.startswith("ل") and text[1] in {"ي", "ت", "ن", "أ"}:
                return True
            return False
        if _strip_lam_if_imperfect():
            text = text[1:]
            prefix_parts.append("ل")
        # After stripping و/ف we may see ل + imperfect again (وَلْيَتَّقِ).
        # Clitic loop runs next; we'll strip ل there if allow_bkl; for لام الأمر we strip ل here when at start.

        # 1) complex multi-letter prefixes (است، ال، وال، إلخ)
        # أل التعريف: نزعها إذا بقي حرفان فأكثر (الشح→شح، الظن→ظن)
        DEFINITE_ARTICLE_PREFIXES = frozenset({"ال", "وال", "فال", "بال", "كال", "لل"})
        if not no_split_mode:
            complex_prefixes = [p for p in self.PREFIXES if len(p) >= 2]
            for prefix in sorted(complex_prefixes, key=len, reverse=True):
                # Prevent mis-segmentation of "سيما" as (سي + ما...)
                if prefix == "سي" and text.startswith("سيما"):
                    continue
                min_remain = 2 if prefix in DEFINITE_ARTICLE_PREFIXES else 3
                if text.startswith(prefix) and len(text) - len(prefix) >= min_remain:
                    text = text[len(prefix) :]
                    prefix_parts.append(prefix)
                    break

        # 2) clitic-like single-letter prefixes (و/ف) can repeat
        # Important: do NOT re-run this after stripping morphological prefixes,
        # otherwise verbs like "تَوَلَّوْا" may lose the root-initial "و".
        # We keep this conservative to avoid stripping true root letters (e.g., ك in كتاب).
        clitic_prefixes = ["ف", "و"] + (["ب", "ك", "ل"] if allow_bkl_clitics else [])

        def _has_clitic_fatha(pfx: str, original: str) -> bool:
            # True for وَ / فَ only (avoid stripping lexical وُ like: وُجوههم)
            if not original or len(original) < 2:
                return False
            return original.startswith(pfx + "َ")

        for _ in range(3):
            removed = False
            for prefix in clitic_prefixes:
                if text.startswith(prefix) and len(text) - len(prefix) >= 3:
                    remainder = text[len(prefix) :]
                    # For ف/و keep conservative check to avoid stripping radicals like ف in فضل.
                    if prefix in {"ف", "و"}:
                        if not (allow_faw_fatha_clitics and _has_clitic_fatha(prefix, original_word)):
                            if remainder and remainder[0] not in {'ا', 'أ', 'إ', 'آ', 'ٱ', 'ل', 'س', 'ي', 'ت', 'ن', 'م'}:
                                continue
                    text = text[len(prefix) :]
                    prefix_parts.append(prefix)
                    removed = True
                    break
            if not removed:
                break

        # 2a) After و/ف, strip لام الأمر/التعليل when ل + ي/ت/ن/أ (وَلْيَتَّقِ → ل then يتقي).
        if _strip_lam_if_imperfect():
            text = text[1:]
            prefix_parts.append("ل")

        # 2b) derivational prefixes after clitics (است/ان/افت/ات...)
        # Needed for tokens like: فاستغلظ (clitic ف then derivational است)
        if not no_split_mode:
            # Protect Form VIII (افتعل/انتفعال) from being mis-segmented as Form VII (انفعل).
            # Pattern: ا + C1 + ت + ... should NOT have 'ان' stripped.
            # Example: انتحار = ا+ن+ت+حار (Form VIII), NOT ان+تحار (Form VII).
            _is_form8 = False
            if text.startswith('ا') and len(text) >= 4:
                lets = [ch for ch in text if ch.isalpha() and '\u0600' <= ch <= '\u06FF']
                if len(lets) >= 4 and lets[2] == 'ت':
                    _is_form8 = True

            deriv_prefixes = ["است", "ان", "افت", "ات"]
            for dp in deriv_prefixes:
                if text.startswith(dp) and len(text) - len(dp) >= 2:
                    # Skip ان if this is Form VIII
                    if dp == "ان" and _is_form8:
                        continue
                    # Protect Form IV (أَفْعَلَ) from mis-segmentation as Form VII (انفعل).
                    # Form IV: أَنْزَلَ (after normalization: انزل) should strip 'أ' only, not 'ان'.
                    # Pattern: ا + ن + consonant + vowel/consonant (but NOT ا+ن+ت which is Form VIII).
                    # If we have 'ان' and the remainder starts with a strong consonant (not ت),
                    # this is likely Form IV, so strip only 'أ' instead of 'ان'.
                    if dp == "ان" and len(text) >= 4:
                        remainder = text[2:]  # after removing 'ان'
                        if remainder and remainder[0] not in {'ت', 'ف', 'ا', 'و', 'ي'}:
                            # Likely Form IV: strip only 'ا', not 'ان'
                            text = text[1:]
                            prefix_parts.append("ا")
                            continue
                    rest = text[len(dp) :]
                    # Rule: if prefix "است" stripped and remainder in {وي,وى}, set stem to سوي (one rule only).
                    if dp == "است" and len(rest) < 3:
                        surf = self._strip_diacritics_surface(original_word) if original_word else ""
                        if "استو" in surf and rest in {"وي", "وى"}:
                            text = "سوي"
                            prefix_parts.append(dp)
                            break
                        # otherwise: do not strip dp in this case
                        continue
                    text = rest
                    prefix_parts.append(dp)
                    break

        # Special case: future marker "س" before imperfect prefix (ي/ت/ن/أ)
        if (not no_split_mode) and text.startswith("س") and len(text) - 1 >= 3 and len(text) >= 2 and text[1] in {"ي", "ت", "ن", "أ"}:
            text = text[1:]
            prefix_parts.append("س")

        # 3) suffixes (peel pronouns first to avoid contaminating radicals)
        suffix_parts: List[str] = []

        def _ends_with_tanwin_fath(original: str) -> bool:
            # Fathatan mark or the common written form (ًا) or explicit (انًا)
            return ("\u064b" in original) or original.endswith("ًا") or original.endswith("انًا")

        # 4a) peel pronominal suffixes (allow leaving 2 letters)
        for _ in range(2):
            removed = False
            for suffix in sorted(self.PRONOUN_SUFFIXES, key=len, reverse=True):
                if text.endswith(suffix) and len(text) - len(suffix) >= 2:
                    # Prevent tanwin confusion: ...انًا must not be segmented as ...وا + نا
                    if suffix == "نا" and original_word and _ends_with_tanwin_fath(original_word):
                        continue
                    # Also prevent common accusative-tanwin nouns that become "...وانا" after
                    # stripping diacritics (e.g., رضوانًا -> رضوانا), which would otherwise
                    # be incorrectly segmented as: ...وا + نا.
                    if suffix == "نا" and text[:-len(suffix)].endswith("وا"):
                        continue
                    text = text[:-len(suffix)]
                    suffix_parts.append(suffix)
                    removed = True
                    break
            if not removed:
                break

        # 4b) peel inflectional suffixes (require 3 letters remain)
        for _ in range(2):  # حد أقصى لاحقتان
            removed = False
            for suffix in sorted(self.SUFFIXES, key=len, reverse=True):
                # Do NOT peel pronominal suffixes in this stage. They are handled in 4a
                # with additional disambiguation (e.g., preventing tanwin→"نا" confusion).
                if suffix in self.PRONOUN_SUFFIXES:
                    continue
                # Avoid over-segmentation of plural/long-vowel bases before هم:
                # "وجوههم" should be (وجوه + هم), not (وجو + ه + هم)
                if suffix == "ه" and ("هم" in suffix_parts) and text.endswith(("وه", "يه", "اه")):
                    continue
                # Require ≥4 letters remain for "ين" so we don't strip from تَدَايَنتُم → تداين (ين is radical).
                min_remain = 4 if suffix == "ين" else 3
                if text.endswith(suffix) and len(text) - len(suffix) >= min_remain:
                    text = text[:-len(suffix)]
                    suffix_parts.append(suffix)
                    removed = True
                    break
            if not removed:
                break

        # 4) morphological single-letter prefixes (imperfect/nominal markers)
        # Allow up to 2 strips so لِيَتَّقِ → ل then ي then ت → قى (stem ق-و-ي).
        morph_prefixes = ["ت", "ي", "ن", "أ", "م"]
        for _ in range(2):
            removed = False
            for prefix in morph_prefixes:
                if text.startswith(prefix) and len(text) - len(prefix) >= 2:
                    # تراهم → ترا+هم: do not strip ت from ترا (رأى with ت prefix).
                    if prefix == "ت" and text == "ترا" and "هم" in suffix_parts:
                        continue
                    # مَرَّ (مرر): do not strip م when remainder would be doubled letter (رر).
                    if prefix == "م" and len(text) == 3 and text[0] == "م" and text[1] == text[2]:
                        continue
                    text = text[len(prefix) :]
                    prefix_parts.append(prefix)
                    removed = True
                    break
            if not removed:
                break

        # 4b) After morph prefixes, strip derivational prefix (است/ان/…) so استطيع → طيع.
        # Also strip "ست" as است when ا was dropped (يَسْتَطِيعُ → يستطيع → ستطيع).
        if not no_split_mode:
            if text.startswith("ست") and len(text) - 2 >= 2:
                rest = text[2:]
                if len(rest) >= 2 and rest[0] not in self.PATTERN_LETTERS:
                    text = rest
                    prefix_parts.append("است")
            # Re-check Form VIII pattern (same as above) to protect ان from stripping
            # after morphological prefixes have been removed.
            _is_form8 = False
            if text.startswith('ا') and len(text) >= 4:
                lets = [ch for ch in text if ch.isalpha() and '\u0600' <= ch <= '\u06FF']
                if len(lets) >= 4:
                    if lets[2] == 'ت':
                        _is_form8 = True
                    elif len(lets) >= 5 and lets[1] == 'ن' and lets[2] == 'ت':
                        _is_form8 = True

            deriv_prefixes = ["است", "ان", "افت", "ات"]
            for dp in deriv_prefixes:
                if text.startswith(dp) and len(text) - len(dp) >= 2:
                    # Skip ان if this is Form VIII
                    if dp == "ان" and _is_form8:
                        continue
                    rest = text[len(dp) :]
                    if dp == "است" and len(rest) < 3:
                        surf = self._strip_diacritics_surface(original_word) if original_word else ""
                        if "استو" in surf and rest in {"وي", "وى"}:
                            text = "سوي"
                            prefix_parts.append(dp)
                            break
                        continue
                    text = rest
                    prefix_parts.append(dp)
                    break

        # Keep boundaries between multiple affixes for clarity.
        prefix_str = "+".join(prefix_parts)
        suffix_str = "+".join(reversed(suffix_parts))
        return text.strip(), prefix_str, suffix_str

    def _extract_consonants(self, word: str, *, stripped_word: str = "") -> List[str]:
        use_stripped = stripped_word or word
        letters = [ch for ch in word if self._is_arabic_letter(ch)]
        consonants: List[str] = []
        for idx, letter in enumerate(letters):
            if letter in self.PATTERN_LETTERS and 0 < idx < len(letters) - 1:
                prev_is_consonant = letters[idx - 1] not in self.PATTERN_LETTERS
                next_is_consonant = letters[idx + 1] not in self.PATTERN_LETTERS
                if prev_is_consonant and next_is_consonant:
                    continue
            consonants.append(letter)

        # إزالة التكرار الناتج عن الشدة في الأوزان الصرفية
        consonants = self._deduplicate_gemination(consonants)
        pattern_filtered = [ch for ch in consonants if ch not in self.PATTERN_LETTERS]
        if len(consonants) > len(pattern_filtered) >= 3:
            consonants = pattern_filtered
        # Restore middle و/ي when it was filtered and we have a short defective stem (e.g. طيع → ط-و-ع).
        # Do not restore when ي is radical: د-ي-ن, غ-ي-ظ.
        if len(consonants) == 2 and len(letters) == 3 and letters[1] in self.PATTERN_LETTERS:
            if (letters[0], letters[2]) not in (("د", "ن"), ("غ", "ظ")):
                consonants = list(letters)
        # Doubled root مَرَّ (مرر): if we have 2 consonants but letters had 3 with last two same, use full.
        if len(consonants) == 2 and len(letters) == 3 and letters[1] == letters[2]:
            consonants = list(letters)

        consonants = self._trim_weak_ending(consonants)

        # Form III/VI: middle ا is elongation (فاعل/تفاعل) → drop for 3-radical root.
        dropped_middle_alif = False
        if len(consonants) == 4 and consonants[1] == "ا":
            consonants = [consonants[0], consonants[2], consonants[3]]
            dropped_middle_alif = True

        # Form VIII (افتعل): infixed ت after first radical (ا + C1 + ت + C2 + C3)
        # Examples: اقترض → ق-ر-ض, اعتمد → ع-م-د, انتحار → ن-ح-ر
        # The initial ا gets filtered out early (it's in PATTERN_LETTERS), so we check
        # the original letters in use_stripped to detect the pattern.
        if len(consonants) == 4 and consonants[1] == 'ت':
            lets = [ch for ch in use_stripped if self._is_arabic_letter(ch)]
            # Pattern: ا C1 ت C2 C3 (letters[0]='ا', letters[2]='ت')
            if len(lets) >= 5 and lets[0] == 'ا' and lets[2] == 'ت':
                # Remove the infixed ت: consonants = [C1, ت, C2, C3] → [C1, C2, C3]
                consonants = [consonants[0]] + consonants[2:]


        if len(consonants) == 4 and consonants[0] == consonants[1] and consonants[2] != consonants[0]:
            consonants = consonants[1:]
        # Defective ف-و-ي when word ends with وا (اتقوا → قوا): last ا is suffix, root ends in ي.
        if len(consonants) == 3 and consonants[-1] == "ا" and use_stripped.endswith("وا"):
            consonants = consonants[:-1] + ["ي"]

        if len(consonants) in (3, 4):
            # واوي اسم مفعول (مُفَعَّل من فعّل): last radical و not ي (e.g. مُسَمًّى → س-م-و).
            # After stripping م the stem is سَمَّى (سممي) so check for م doubling in stem.
            if len(consonants) == 3 and consonants[-1] == "ي":
                lets = [ch for ch in use_stripped if self._is_arabic_letter(ch)]
                if len(lets) >= 4 and use_stripped.endswith(("ى", "ي")):
                    # مُفَعَّل: م + C + C + same + ى, or after stripping م: C + C + C + ى (سممي).
                    if len(lets) >= 5 and use_stripped.startswith("م") and lets[2] == lets[3]:
                        consonants = consonants[:-1] + ["و"]
                    elif len(lets) == 4 and lets[1] == lets[2]:  # سممي: س م م ي
                        consonants = consonants[:-1] + ["و"]
            # Defective واوي in short stem (استطاع → طيع → ط-و-ع). Do NOT apply when we just
            # dropped middle ا (Form III ب-ي-ع has ي as radical).
            if not dropped_middle_alif:
                letters_only = [ch for ch in word if self._is_arabic_letter(ch)]
                if (
                    len(consonants) == 3
                    and consonants[1] == "ي"
                    and "و" not in letters_only
                    and len(letters_only) <= 4
                ):
                    consonants = [consonants[0], "و", consonants[2]]
            return consonants
        if len(consonants) > 4:
            return consonants[:4]
        if len(consonants) == 2:
            # Defective stem (e.g. قى → ق-و-ي; ابا from يَأْبَ → أ-ب-ي).
            expanded = self._expand_defective_root(consonants, word=use_stripped)
            if expanded:
                return expanded
        if len(consonants) < 3:
            return letters[:3] if len(letters) >= 3 else letters
        return consonants
    
    def _deduplicate_gemination(self, consonants: List[str]) -> List[str]:
        """
        إزالة الحروف المضعفة الناتجة عن الشدة في الأوزان الصرفية.
        
        مثال:
        - "زرراع" → ["ز", "ر", "ر", "ا", "ع"] → ["ز", "ر", "ا", "ع"]
        - "كتب" → ["ك", "ت", "ب"] → ["ك", "ت", "ب"] (بدون تغيير)
        
        القاعدة: إذا كان هناك حرفان متتاليان متطابقان، نزيل أحدهما
        إلا إذا كان الجذر رباعياً حقيقياً (مثل: زلزل، وسوس).
        """
        if len(consonants) <= 3:
            return consonants
        
        result: List[str] = []
        i = 0
        while i < len(consonants):
            current = consonants[i]
            # تحقق من وجود حرف متطابق تالٍ
            if i + 1 < len(consonants) and consonants[i + 1] == current:
                # أضف الحرف مرة واحدة فقط
                result.append(current)
                # تجاوز الحرف المكرر
                i += 2
            else:
                result.append(current)
                i += 1
        
        return result

    def _trim_weak_ending(self, consonants: List[str]) -> List[str]:
        """
        Remove trailing weak letters (pattern fillers) while keeping at least three strong radicals.
        """
        trimmed = list(consonants)
        while len(trimmed) > 3 and trimmed[-1] in self.WEAK_LETTERS:
            trimmed.pop()
        return trimmed

    def _expand_defective_root(
        self, two_consonants: List[str], *, word: str = ""
    ) -> Optional[List[str]]:
        """
        Expand a 2-consonant defective stem to 3-radical root (ف-ع-ل).
        E.g. قى → ق-و-ي; ابا (يَأْبَ) → أ-ب-ي when word ends with ا.
        """
        if len(two_consonants) != 2:
            return None
        c1, c2 = two_consonants
        if c2 in {"و", "ي"}:
            return [c1, "و", c2]
        if c1 in {"و", "ي"} and c2 not in self.PATTERN_LETTERS:
            return [c1, c2, "ي"] if c1 == "ي" else [c1, c2, "و"]
        # يائي مثل أَبَى: ابا or اب (يَأْبَ) → ا-ب-ي.
        if c1 in {"ا", "أ", "إ"} and (word.rstrip().endswith("ا") or word.rstrip() in ("اب", "أب")):
            return [c1, c2, "ي"]
        # يَتَّقِ (Form V من و-ق-ي): stem تق → root ق-و-ي.
        if (c1, c2) == ("ت", "ق") and word.rstrip() == "تق":
            return ["ق", "و", "ي"]
        return None

    def _is_valid_root(self, letters: List[str]) -> bool:
        if len(letters) not in (3, 4):
            return False
        if self.known_roots:
            root_str = '-'.join(letters)
            if root_str not in self.known_roots:
                return False
        return all(self._is_arabic_letter(ch) for ch in letters)

    def _is_arabic_letter(self, ch: str) -> bool:
        return bool(ch) and ((0x0621 <= ord(ch) <= 0x064A) or ch in {'ة', 'ى'})
