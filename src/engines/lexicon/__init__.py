"""Lexicon-related engines."""

from .proper_nouns_engine import ProperNounsEngine
from .generic_nouns_engine import GenericNounsEngine
from .place_engine import PlaceEngine
from .a3lam_amakin_engine import A3lamAmakinEngine
from .a3lam_ashkhas_engine import A3lamAshkhasEngine
from .a3lam_manqula_engine import A3lamManqulaEngine
from .asma_allah_engine import AsmaAllahEngine
from .adad_names_engine import AdadNamesEngine
from .kainat_aqila_engine import KainatAqilaEngine
from .kainat_ghair_aqila_engine import KainatGhairAqilaEngine
from .jins_ifradi_engine import JinsIfradiEngine
from .jins_jamii_engine import JinsJamiiEngine
from .musatalahat_sharia_engine import MusatalahatShariaEngine

__all__ = [
    "ProperNounsEngine",
    "GenericNounsEngine",
    "PlaceEngine",
    "A3lamAmakinEngine",
    "A3lamAshkhasEngine",
    "A3lamManqulaEngine",
    "AsmaAllahEngine",
    "AdadNamesEngine",
    "KainatAqilaEngine",
    "KainatGhairAqilaEngine",
    "JinsIfradiEngine",
    "JinsJamiiEngine",
    "MusatalahatShariaEngine",
]
