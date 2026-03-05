"""
PatternMatcher: Recognize Arabic morphological patterns.
"""

from __future__ import annotations

import re
import unicodedata
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




def _remove_tanwin_alif(word: str) -> str:
    """
    Remove tanwin alif and tanwin itself: عَظِيمًا → عَظِيم
    """
    FATHATAN = "\u064B"
    DAMMATAN = "\u064C"
    KASRATAN = "\u064D"
    ALIF = "\u0627"
    
    # 1. Remove (fathatan + alif)
    word = word.replace(FATHATAN + ALIF, "")
    
    # 2. Remove (alif + fathatan) - reversed order
    word = word.replace(ALIF + FATHATAN, "")
    
    # 3. Remove standalone alif at end after fatha
    word = re.sub(r'َ' + ALIF + r'$', 'َ', word)
    
    # 4. Remove remaining tanwin
    TANWIN = {FATHATAN, DAMMATAN, KASRATAN}
    for t in TANWIN:
        word = word.replace(t, "")
    
    return word

class PatternDatabase:
    def __init__(self) -> None:
        self.patterns: List[PatternTemplate] = []
        self._initialize_patterns()

    def _initialize_patterns(self) -> None:
        # Load all patterns from CSV only
        extra_patterns = AwzanPatternLoader.load()
        
        patterns_list = []
        seen: Set[Tuple[str, PatternType]] = set()
        
        for data in extra_patterns:
            tpl = data["template"]
            pt = data["pattern_type"]
            if (tpl, pt) in seen:
                continue
            seen.add((tpl, pt))
            patterns_list.append(
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
        
        self.patterns.extend(patterns_list)
        
        # Build category index
        self._by_category = {}
        for p in patterns_list:
            self._by_category.setdefault(p.category, []).append(p)

    def get_all(self) -> List[PatternTemplate]:
        return self.patterns

    def get_by_category(self, category: str) -> List[PatternTemplate]:
        return self._by_category.get(category, [])


class PatternMatcher:
    def __init__(self, database: Optional[PatternDatabase] = None) -> None:
        self.database = database or PatternDatabase()

    def match(self, word: str, root: Root) -> Optional[Pattern]:
        if not word or not root:
            return None
        
        normalized = self._normalize(word)
        
        # Try categories in priority order
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
                matched, confidence = self._matches(normalized, candidate, template.pattern_type)
                
                if matched:
                    return Pattern(
                        name=template.pattern_type.value,
                        template=template.template,
                        pattern_type=template.pattern_type,
                        stem=word,
                        features={**template.feature_map(), "confidence": f"{confidence:.2f}"},
                    )
        
        # Try all remaining patterns
        for template in self.database.get_all():
            if id(template) in checked:
                continue
            
            if not template.matches_root_type(root):
                continue
            
            candidate = self._instantiate_template(template.template, root)
            matched, confidence = self._matches(normalized, candidate, template.pattern_type)
            
            if matched:
                return Pattern(
                    name=template.pattern_type.value,
                    template=template.template,
                    pattern_type=template.pattern_type,
                    stem=word,
                    features={**template.feature_map(), "confidence": f"{confidence:.2f}"},
                )
        
        return None

    def _normalize(self, word: str) -> str:
        # Remove tanwin + support alif first (عَظِيمًا → عَظِيم) so matching works
        text = _remove_tanwin_alif(word)
        # Convert any remaining Tanwin to standard short vowels
        text = text.replace('ً', 'َ').replace('ٌ', 'ُ').replace('ٍ', 'ِ')
        
        # Remove definiteness (Al-)
        if text.startswith("ال") and len(text) > 3:
            idx = 2
            while idx < len(text) and text[idx] in "ْ":
                idx += 1
            
            stem_start = idx
            stem = text[stem_start:]
            
            # Remove sun letter shadda
            if len(stem) > 1 and stem[1] == 'ّ':
                stem = stem[0] + stem[2:]
            
            text = stem

        # Remove support alif after fathatan
        if text.endswith("َا") and len(text) > 3:
            pass

        # Normalize hamza and alif
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
    ) -> Tuple[bool, float]:
        # Remove tanwin and tanwin alif first
        word = _remove_tanwin_alif(word)
        
        # Normalize to NFD so equivalent diacritic orderings compare equal
        # (e.g. ل+shadda+fatha vs ل+fatha+shadda for Form II عَلَّمَ)
        word = unicodedata.normalize("NFD", word)
        candidate = unicodedata.normalize("NFD", candidate)

        # Exact match
        if word == candidate:
            return True, 1.0

        # Strip diacritics and compare
        stripped_word = self._strip_diacritics(word)
        stripped_candidate = self._strip_diacritics(candidate)
        
        # Consonants must match
        if stripped_word != stripped_candidate:
            return False, 0.0
        
        # Check shadda consistency
        # If candidate has shadda, word MUST have shadda
        if 'ّ' in candidate and 'ّ' not in word:
            return False, 0.0
        
        # If candidate has no shadda, word should not have shadda
        if 'ّ' not in candidate and 'ّ' in word:
            return False, 0.0
        
        # Lenient match: ignore final short vowel differences
        def strip_final_vowel(s):
            if s and s[-1] in "َُِ":
                return s[:-1]
            return s
        
        if strip_final_vowel(word) == strip_final_vowel(candidate):
            return True, 0.95
        
        # If lengths match (and stripped text matches), good enough
        if len(word) == len(candidate):
            return True, 0.90
        
        # Special handling for Form X
        if pattern_type == PatternType.FORM_X:
            return True, 0.9
        
        # Vowel mismatch but consonants match
        return True, 0.60

    def _strip_diacritics(self, text: str) -> str:
        # Standardize hamza carriers - preserve hamza!
        # For root extraction, we need to keep hamza distinct
        # Only normalize the CARRIER, not the hamza itself
        text = (
            text.replace("أ", "ء")   # hamza on alif → standalone hamza
            .replace("إ", "ء")       # hamza under alif → standalone hamza
            .replace("آ", "ءا")      # alif madda → hamza + alif
            .replace("ؤ", "ءو")      # hamza on waw → hamza + waw
            .replace("ئ", "ءي")      # hamza on ya → hamza + ya
        )
        
        # Remove diacritics (keep shadda!)
        diacritics = "ْٰٓٔٱًٌٍ"
        for mark in diacritics:
            text = text.replace(mark, "")
        
        return text