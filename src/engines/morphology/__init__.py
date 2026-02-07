"""Morphology-related engines."""

from engines.morphology.active_participle_engine import ActiveParticipleEngine
from engines.morphology.passive_participle_engine import PassiveParticipleEngine
from engines.morphology.adjective_engine import AdjectiveEngine
from engines.morphology.superlative_engine import SuperlativeEngine
from engines.morphology.mimi_nouns_engine import MimiNounsEngine
from engines.morphology.ism_marra_engine import IsmMarraEngine
from engines.morphology.ism_hay_a_engine import IsmHayaaEngine
from engines.morphology.ism_ala_engine import IsmAlaEngine
from engines.morphology.nisba_engine import NisbaEngine
from engines.morphology.tasgheer_engine import TasgheerEngine
from engines.morphology.masdar_sinai_engine import MasdarSinaiEngine
from engines.morphology.mubalagh_sigha_engine import MubalaghSighaEngine
from engines.morphology.taajjub_engine import TaajjubEngine
from engines.morphology.binaa_engine import BinaaEngine
from engines.morphology.gender_engine import GenderEngine
from engines.morphology.mabni_majhool_engine import MabniMajhoolEngine
from engines.morphology.afaal_khamsa_engine import AfaalKhamsaEngine
from engines.morphology.ism_maqsor_engine import IsmMaqsorEngine
from engines.morphology.ism_mamdod_engine import IsmMamdodEngine
from engines.morphology.ism_manqus_engine import IsmManqusEngine
from engines.morphology.verbs_engine import VerbsEngine
from engines.morphology.common_attributes_engine import CommonAttributesEngine

__all__ = [
    'ActiveParticipleEngine', 'PassiveParticipleEngine', 'AdjectiveEngine',
    'SuperlativeEngine', 'MimiNounsEngine', 'IsmMarraEngine', 'IsmHayaaEngine',
    'IsmAlaEngine', 'NisbaEngine', 'TasgheerEngine', 'MasdarSinaiEngine',
    'MubalaghSighaEngine', 'TaajjubEngine', 'BinaaEngine', 'GenderEngine',
    'MabniMajhoolEngine', 'AfaalKhamsaEngine', 'IsmMaqsorEngine',
    'IsmMamdodEngine', 'IsmManqusEngine', 'VerbsEngine', 'CommonAttributesEngine'
]
