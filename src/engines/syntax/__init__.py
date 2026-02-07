"""Syntax-related engines."""

from engines.syntax.fael_engine import FaelEngine
from engines.syntax.haal_engine import HaalEngine
from engines.syntax.ishtighal_engine import IshtighalEngine
from engines.syntax.istifham_engine import IstifhamEngine
from engines.syntax.jawab_engine import JawabEngine
from engines.syntax.mafoul_ajlih_engine import MafoulAjlihEngine
from engines.syntax.mafoul_bih_engine import MafoulBihEngine
from engines.syntax.mafoul_mutlaq_engine import MafoulMutlaqEngine
from engines.syntax.mobtada_khabar_engine import MobtadaKhabarEngine
from engines.syntax.naeb_fael_engine import NaebFaelEngine
from engines.syntax.qasr_engine import QasrEngine
from engines.syntax.tamyeez_engine import TamyeezEngine
from engines.syntax.taqdim_engine import TaqdimEngine

__all__ = [
    'FaelEngine', 'HaalEngine', 'IshtighalEngine',
    'IstifhamEngine', 'JawabEngine', 'MafoulAjlihEngine', 'MafoulBihEngine',
    'MafoulMutlaqEngine', 'MobtadaKhabarEngine', 'NaebFaelEngine',
    'QasrEngine', 'TamyeezEngine', 'TaqdimEngine'
]
