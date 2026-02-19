"""
Pattern Catalog - Arabic Morphological Patterns
Comprehensive collection of verb forms, noun patterns, and broken plurals
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class PatternType(Enum):
    """Pattern types"""
    VERB_FORM_I = "verb_form_i"
    VERB_FORM_II = "verb_form_ii"
    VERB_FORM_III = "verb_form_iii"
    VERB_FORM_IV = "verb_form_iv"
    VERB_FORM_V = "verb_form_v"
    VERB_FORM_VI = "verb_form_vi"
    VERB_FORM_VII = "verb_form_vii"
    VERB_FORM_VIII = "verb_form_viii"
    VERB_FORM_IX = "verb_form_ix"
    VERB_FORM_X = "verb_form_x"
    
    NOUN_MASDAR = "noun_masdar"
    NOUN_ACTIVE_PARTICIPLE = "noun_active_participle"
    NOUN_PASSIVE_PARTICIPLE = "noun_passive_participle"
    NOUN_INSTRUMENT = "noun_instrument"
    NOUN_PLACE_TIME = "noun_place_time"
    
    BROKEN_PLURAL = "broken_plural"
    ADJECTIVE = "adjective"


@dataclass
class PatternTemplate:
    """Simple pattern template"""
    name: str
    template: str
    description: str
    pattern_type: str = "unknown"
    examples: Optional[List[str]] = None


class PatternCatalog:
    """Catalog of Arabic morphological patterns"""
    
    @classmethod
    def load_full_catalog(cls) -> Dict[str, List[PatternTemplate]]:
        """Load complete pattern catalog"""
        return {
            "verb_forms": cls._load_verb_patterns(),
            "noun_patterns": cls._load_noun_patterns(),
            "broken_plurals": cls._load_broken_plural_patterns(),
            "adjectives": cls._load_adjective_patterns(),
        }
    
    @classmethod
    def _load_verb_patterns(cls) -> List[PatternTemplate]:
        """Load verb form patterns (Forms I-X)"""
        return [
            # Form I (فَعَلَ)
            PatternTemplate(
                name="FORM_I_FATHA",
                template="فَعَلَ",
                description="Form I - فَتَحَ pattern",
                pattern_type="verb_form_i",
                examples=["كَتَبَ", "ذَهَبَ", "فَعَلَ"]
            ),
            PatternTemplate(
                name="FORM_I_KASRA",
                template="فَعِلَ",
                description="Form I - فَهِمَ pattern",
                pattern_type="verb_form_i",
                examples=["شَرِبَ", "عَلِمَ", "فَهِمَ"]
            ),
            PatternTemplate(
                name="FORM_I_DAMMA",
                template="فَعُلَ",
                description="Form I - حَسُنَ pattern",
                pattern_type="verb_form_i",
                examples=["حَسُنَ", "كَرُمَ", "عَظُمَ"]
            ),
            
            # Form II (فَعَّلَ)
            PatternTemplate(
                name="FORM_II",
                template="فَعَّلَ",
                description="Form II - causative/intensive",
                pattern_type="verb_form_ii",
                examples=["عَلَّمَ", "كَسَّرَ", "فَهَّمَ"]
            ),
            
            # Form III (فَاعَلَ)
            PatternTemplate(
                name="FORM_III",
                template="فَاعَلَ",
                description="Form III - mutual action",
                pattern_type="verb_form_iii",
                examples=["قَاتَلَ", "جَاهَدَ", "سَافَرَ"]
            ),
            
            # Form IV (أَفْعَلَ)
            PatternTemplate(
                name="FORM_IV",
                template="أَفْعَلَ",
                description="Form IV - causative",
                pattern_type="verb_form_iv",
                examples=["أَكْرَمَ", "أَخْرَجَ", "أَسْلَمَ"]
            ),
            
            # Form V (تَفَعَّلَ)
            PatternTemplate(
                name="FORM_V",
                template="تَفَعَّلَ",
                description="Form V - reflexive of Form II",
                pattern_type="verb_form_v",
                examples=["تَعَلَّمَ", "تَكَلَّمَ", "تَقَدَّمَ"]
            ),
            
            # Form VI (تَفَاعَلَ)
            PatternTemplate(
                name="FORM_VI",
                template="تَفَاعَلَ",
                description="Form VI - reflexive of Form III",
                pattern_type="verb_form_vi",
                examples=["تَقَاتَلَ", "تَعَاوَنَ", "تَبَادَلَ"]
            ),
            
            # Form VII (اِنْفَعَلَ)
            PatternTemplate(
                name="FORM_VII",
                template="اِنْفَعَلَ",
                description="Form VII - passive/reflexive",
                pattern_type="verb_form_vii",
                examples=["اِنْكَسَرَ", "اِنْفَتَحَ", "اِنْقَطَعَ"]
            ),
            
            # Form VIII (اِفْتَعَلَ)
            PatternTemplate(
                name="FORM_VIII",
                template="اِفْتَعَلَ",
                description="Form VIII - reflexive",
                pattern_type="verb_form_viii",
                examples=["اِجْتَمَعَ", "اِخْتَارَ", "اِشْتَغَلَ"]
            ),
            
            # Form IX (اِفْعَلَّ)
            PatternTemplate(
                name="FORM_IX",
                template="اِفْعَلَّ",
                description="Form IX - colors/defects",
                pattern_type="verb_form_ix",
                examples=["اِحْمَرَّ", "اِخْضَرَّ", "اِصْفَرَّ"]
            ),
            
            # Form X (اِسْتَفْعَلَ)
            PatternTemplate(
                name="FORM_X",
                template="اِسْتَفْعَلَ",
                description="Form X - seeking/requesting",
                pattern_type="verb_form_x",
                examples=["اِسْتَخْرَجَ", "اِسْتَقْبَلَ", "اِسْتَغْفَرَ"]
            ),
        ]
    
    @classmethod
    def _load_noun_patterns(cls) -> List[PatternTemplate]:
        """Load noun patterns"""
        return [
            # Masdar patterns
            PatternTemplate(
                name="MASDAR_FACL",
                template="فَعْل",
                description="Masdar Form I pattern",
                pattern_type="noun_masdar",
                examples=["ضَرْب", "أَكْل", "فَتْح"]
            ),
            PatternTemplate(
                name="MASDAR_FICAAL",
                template="فِعَال",
                description="Masdar Form I pattern",
                pattern_type="noun_masdar",
                examples=["جِهَاد", "قِتَال", "نِزَال"]
            ),
            PatternTemplate(
                name="MASDAR_TAFCEEL",
                template="تَفْعِيل",
                description="Masdar Form II",
                pattern_type="noun_masdar",
                examples=["تَعْلِيم", "تَكْسِير", "تَفْهِيم"]
            ),
            
            # Active participle
            PatternTemplate(
                name="ACTIVE_PARTICIPLE_FAACIL",
                template="فَاعِل",
                description="Active participle Form I",
                pattern_type="noun_active_participle",
                examples=["كَاتِب", "ذَاهِب", "قَارِئ"]
            ),
            PatternTemplate(
                name="ACTIVE_PARTICIPLE_MUFACCIL",
                template="مُفَعِّل",
                description="Active participle Form II",
                pattern_type="noun_active_participle",
                examples=["مُعَلِّم", "مُكَسِّر", "مُفَهِّم"]
            ),
            
            # Passive participle
            PatternTemplate(
                name="PASSIVE_PARTICIPLE_MAFCOOL",
                template="مَفْعُول",
                description="Passive participle Form I",
                pattern_type="noun_passive_participle",
                examples=["مَكْتُوب", "مَقْرُوء", "مَفْهُوم"]
            ),
            
            # Instrument nouns
            PatternTemplate(
                name="INSTRUMENT_MIFCAAL",
                template="مِفْعَال",
                description="Instrument noun",
                pattern_type="noun_instrument",
                examples=["مِفْتَاح", "مِقْيَاس", "مِنْشَار"]
            ),
            
            # Place/Time nouns
            PatternTemplate(
                name="PLACE_MAFCAL",
                template="مَفْعَل",
                description="Place/time noun",
                pattern_type="noun_place_time",
                examples=["مَكْتَب", "مَدْرَسَة", "مَطْبَخ"]
            ),
        ]
    
    @classmethod
    def _load_broken_plural_patterns(cls) -> List[PatternTemplate]:
        """Load broken plural patterns"""
        return [
            PatternTemplate(
                name="PLURAL_AFCAAL",
                template="أَفْعَال",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["أَقْلَام", "أَبْوَاب", "أَيَّام"]
            ),
            PatternTemplate(
                name="PLURAL_FUCOOL",
                template="فُعُول",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["بُيُوت", "عُيُون", "قُلُوب"]
            ),
            PatternTemplate(
                name="PLURAL_FACAALIL",
                template="فَعَائِل",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["رَسَائِل", "مَسَائِل", "وَسَائِل"]
            ),
            PatternTemplate(
                name="PLURAL_FUCALAA",
                template="فُعَلَاء",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["عُلَمَاء", "شُعَرَاء", "فُقَهَاء"]
            ),
        ]
    
    @classmethod
    def _load_adjective_patterns(cls) -> List[PatternTemplate]:
        """Load adjective patterns"""
        return [
            PatternTemplate(
                name="ADJECTIVE_FACEEL",
                template="فَعِيل",
                description="Intensive adjective",
                pattern_type="adjective",
                examples=["كَرِيم", "رَحِيم", "عَظِيم"]
            ),
            PatternTemplate(
                name="ADJECTIVE_AFCAL",
                template="أَفْعَل",
                description="Comparative/superlative",
                pattern_type="adjective",
                examples=["أَكْبَر", "أَصْغَر", "أَحْسَن"]
            ),
        ]
