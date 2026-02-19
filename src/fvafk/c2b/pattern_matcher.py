"""
PatternMatcher: Recognize Arabic morphological patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .awzan_loader import AwzanPatternLoader
from .morpheme import Pattern, PatternType, Root


@dataclass(frozen=True)
class PatternTemplate:
    template: str
    pattern_type: PatternType
    category: str
    form: Optional[str] = None
    meaning: Optional[str] = None
    cv_simple: Optional[str] = None
    cv_detailed: Optional[str] = None
    cv_advanced: Optional[str] = None
    notes: Optional[str] = None

    def feature_map(self) -> Dict[str, str]:
        features: Dict[str, str] = {
            "pattern_type": self.pattern_type.name,
            "category": self.category,
        }
        if self.form:
            features["form"] = self.form
        if self.meaning:
            features["meaning"] = self.meaning
        if self.cv_simple:
            features["cv_simple"] = self.cv_simple
        if self.cv_detailed:
            features["cv_detailed"] = self.cv_detailed
        if self.cv_advanced:
            features["cv_advanced"] = self.cv_advanced
        if self.notes:
            features["notes"] = self.notes
        return features
    def matches_root_type(self, root: Root) -> bool:
        count = sum(1 for c in self.template if c in {'ف', 'ع', 'ل'})
        if len(root.letters) >= count:
            return True
        return False


class PatternDatabase:
    def __init__(self) -> None:
        self.patterns: List[PatternTemplate] = []
        self._initialize_patterns()

    def _initialize_patterns(self) -> None:
        base = [
            PatternTemplate(template="فَعَلَ", pattern_type=PatternType.FORM_I, category="verb", form="I"),
            PatternTemplate(template="فَعَلَ", pattern_type=PatternType.FORM_I, category="verb", form="I"),
            PatternTemplate(template="فَعِلَ", pattern_type=PatternType.FORM_I, category="verb", form="I"),
            PatternTemplate(template="فَعُلَ", pattern_type=PatternType.FORM_I, category="verb", form="I"),
            PatternTemplate(template="فَعَّلَ", pattern_type=PatternType.FORM_II, category="verb", form="II"),
            PatternTemplate(template="فَاعَلَ", pattern_type=PatternType.FORM_III, category="verb", form="III"),
            PatternTemplate(template="أَفْعَلَ", pattern_type=PatternType.FORM_IV, category="verb", form="IV"),
            PatternTemplate(template="تَفَعَّلَ", pattern_type=PatternType.FORM_V, category="verb", form="V"),
            PatternTemplate(template="تَفَاعَلَ", pattern_type=PatternType.FORM_VI, category="verb", form="VI"),
            PatternTemplate(template="انْفَعَلَ", pattern_type=PatternType.FORM_VII, category="verb", form="VII"),
            PatternTemplate(template="افْتَعَلَ", pattern_type=PatternType.FORM_VIII, category="verb", form="VIII"),
            PatternTemplate(template="اسْتَفْعَلَ", pattern_type=PatternType.FORM_X, category="verb", form="X"),
            PatternTemplate(template="فَاعِل", pattern_type=PatternType.ACTIVE_PARTICIPLE, category="noun"),
            PatternTemplate(template="مَفْعُول", pattern_type=PatternType.PASSIVE_PARTICIPLE, category="noun"),
            PatternTemplate(template="مَفْعَل", pattern_type=PatternType.PLACE_TIME_NOUN, category="noun"),
            PatternTemplate(template="فِعَال", pattern_type=PatternType.VERBAL_NOUN, category="noun"),
            PatternTemplate(template="فَعِيل", pattern_type=PatternType.INTENSIVE, category="noun"),
            PatternTemplate(template="أَفْعَل", pattern_type=PatternType.ELATIVE, category="noun"),
            PatternTemplate(template="فَاعِلُون", pattern_type=PatternType.SOUND_MASCULINE_PLURAL, category="plural"),
            PatternTemplate(template="فَاعِلِين", pattern_type=PatternType.SOUND_MASCULINE_PLURAL, category="plural"),
            PatternTemplate(template="فَاعِلَات", pattern_type=PatternType.SOUND_FEMININE_PLURAL, category="plural"),
            PatternTemplate(template="فُعُول", pattern_type=PatternType.BROKEN_PLURAL_FUUL, category="plural"),
            PatternTemplate(template="فِعَال", pattern_type=PatternType.BROKEN_PLURAL_FIAAL, category="plural"),
            PatternTemplate(template="أَفْعَال", pattern_type=PatternType.BROKEN_PLURAL_AFAAL, category="plural"),
            PatternTemplate(template="فِعَل", pattern_type=PatternType.BROKEN_PLURAL_FIUL, category="plural"),
            # High-impact broken plurals (Qur'anic frequent)
            PatternTemplate(template="فُعَّل", pattern_type=PatternType.BROKEN_PLURAL_FU33AL, category="plural"),
            PatternTemplate(template="فُعَلَاء", pattern_type=PatternType.BROKEN_PLURAL_FU3ALAA, category="plural"),
            PatternTemplate(template="فُعَلَاءُ", pattern_type=PatternType.BROKEN_PLURAL_FU3ALAA, category="plural"),
        ]
        extra_patterns = AwzanPatternLoader.load()
        seen_templates = {p.template for p in base}
        for data in extra_patterns:
            tpl = data["template"]
            if tpl in seen_templates:
                continue
            seen_templates.add(tpl)
            base.append(
                PatternTemplate(
                    template=tpl,
                    pattern_type=data["pattern_type"],
                    category=data["category"],
                    form=data["form"],
                    meaning=data["meaning"],
                    cv_simple=data["cv_simple"],
                    cv_detailed=data["cv_detailed"],
                    cv_advanced=data["cv_advanced"],
                    notes=data["notes"],
                )
            )
        self.patterns.extend(base)

    def get_all(self) -> List[PatternTemplate]:
        return self.patterns

    def get_by_category(self, category: str) -> List[PatternTemplate]:
        return [p for p in self.patterns if p.category == category]


from fvafk.c1.cv_pattern import advanced_cv_pattern
from fvafk.c1.cv_pattern import cv_pattern


class PatternMatcher:
    def __init__(self, database: Optional[PatternDatabase] = None) -> None:
        self.database = database or PatternDatabase()

    def match(self, word: str, root: Root) -> Optional[Pattern]:
        if not word or not root:
            return None
        # IMPORTANT (per awzan_test_report): compute CV from the ORIGINAL word (with tashkeel)
        # not from stripped/normalized stems.
        advanced_cv_word = self._sanitize_cv(advanced_cv_pattern(word))
        simple_cv_word = cv_pattern(word)
        normalized = self._normalize(word)
        categories = ["verb", "noun", "plural"]
        checked = set()
        for category in categories:
            for template in self.database.get_by_category(category):
                if id(template) in checked:
                    continue
                checked.add(id(template))
                if not template.matches_root_type(root):
                    continue
                candidate = self._instantiate_template(template.template, root)
                matched, confidence = self._matches(
                    normalized,
                    candidate,
                    template.pattern_type,
                    advanced_cv_word,
                    template,
                )
                if matched:
                    return Pattern(
                        name=template.pattern_type.value,
                        template=template.template,
                        pattern_type=template.pattern_type,
                        stem=word,
                        features={**template.feature_map(), "confidence": f"{confidence:.2f}"},
                    )
        for template in self.database.get_all():
            if id(template) in checked:
                continue
            if not template.matches_root_type(root):
                continue
            candidate = self._instantiate_template(template.template, root)
            matched, confidence = self._matches(
                normalized,
                candidate,
                template.pattern_type,
                advanced_cv_word,
                template,
            )
            if matched:
                return Pattern(
                    name=template.pattern_type.value,
                    template=template.template,
                    pattern_type=template.pattern_type,
                    stem=word,
                    features={**template.feature_map(), "confidence": f"{confidence:.2f}"},
                )

        # ------------------------------------------------------------------
        # CV-based fallback (golden rule from docs/awzan_test_report.md)
        # ------------------------------------------------------------------
        # If exact template instantiation didn't match (often due to missing diacritics
        # or orthographic variants), fall back to matching by CV / Advanced_CV fields
        # in the awzan database, computed from the original word.
        #
        # This increases coverage; confidence is lower than exact instantiation.
        for template in self.database.get_all():
            # Prefer Advanced_CV when available.
            if template.cv_advanced:
                template_cv_adv = self._sanitize_cv(template.cv_advanced)
                if template_cv_adv and template_cv_adv == advanced_cv_word:
                    return Pattern(
                        name=template.pattern_type.value,
                        template=template.template,
                        pattern_type=template.pattern_type,
                        stem=word,
                        features={**template.feature_map(), "confidence": "0.75"},
                    )
            if template.cv_simple and template.cv_simple == simple_cv_word:
                return Pattern(
                    name=template.pattern_type.value,
                    template=template.template,
                    pattern_type=template.pattern_type,
                    stem=word,
                    features={**template.feature_map(), "confidence": "0.70"},
                )

        return None

    def _normalize(self, word: str) -> str:
        text = word.replace('ً', '').replace('ٌ', '').replace('ٍ', '')
        # If the surface had fathatan, Arabic orthography often adds a final alif (…ًا).
        # After stripping marks, drop this support-alif to match templates (e.g., عظيمًا -> عظيم).
        if "\u064b" in word and text.endswith("ا") and len(text) > 3:
            text = text[:-1]
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ى', 'ي')
        return text.strip()

    def _instantiate_template(self, template_str: str, root: Root) -> str:
        chars = []
        l_count = 0
        for ch in template_str:
            if ch == 'ف':
                chars.append(root.letters[0])
            elif ch == 'ع':
                chars.append(root.letters[1])
            elif ch == 'ل':
                if l_count == 0:
                    idx = 2
                else:
                    idx = min(3, len(root.letters) - 1)
                chars.append(root.letters[idx])
                l_count += 1
            else:
                chars.append(ch)
        return ''.join(chars)

    def _matches(
        self,
        word: str,
        candidate: str,
        pattern_type: PatternType,
        advanced_cv_word: str,
        template: PatternTemplate,
    ) -> Tuple[bool, float]:
        if word == candidate:
            return True, 1.0
        stripped_word = self._strip_diacritics(word)
        stripped_candidate = self._strip_diacritics(candidate)
        if pattern_type == PatternType.BROKEN_PLURAL_FUUL:
            candidate_no_waw = candidate.replace("و", "")
            stripped_candidate_no_waw = self._strip_diacritics(candidate_no_waw)
            if stripped_word == stripped_candidate_no_waw:
                return True, 0.85
        if stripped_word != stripped_candidate:
            return False, 0.0
        if template.cv_advanced:
            template_cv = self._sanitize_cv(template.cv_advanced)
            if template_cv and (not advanced_cv_word or advanced_cv_word != template_cv):
                return False, 0.25
        if len(word) == len(candidate):
            return True, 0.95
        if pattern_type == PatternType.FORM_X:
            return True, 0.9
        return False, 0.0

    @staticmethod
    def _sanitize_cv(value: str) -> str:
        return "".join(ch for ch in value if ch.isalpha())

    def _strip_diacritics(self, text: str) -> str:
        diacritics = "َُِْٰٓٔٱ" + "ًٌٍ"
        had_fathatan = "\u064b" in text
        for d in diacritics:
            text = text.replace(d, '')
        # Normalize hamza carriers to bare alif for robust matching (e.g., أخرج vs افعل).
        text = (
            text.replace("أ", "ا")
            .replace("إ", "ا")
            .replace("آ", "ا")
        )
        text = re.sub(r'[\u064B-\u0650\u0652-\u065F\u0670]', '', text)
        if had_fathatan and text.endswith("ا") and len(text) > 3:
            text = text[:-1]
        return text
