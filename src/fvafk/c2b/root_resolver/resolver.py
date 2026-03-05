# -*- coding: utf-8 -*-
"""
RootResolver: main engine for root extraction — CLI → Wazn → Heuristic.
Always returns canonicalized root (بون→بين, شوء→شيء) via _canonicalize_result.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .heuristic import heuristic_root, HeuristicResult
from .roots_db import RootsDB
from .wazn_adapter import WaznAdapter, WaznResult


NO_ROOT_KINDS = frozenset({
    "particle", "operator", "demonstrative",
    "conjunction", "mabni", "name",
})

_NO_ROOT_WORDS_BARE = frozenset({
    "الله", "اللهم", "لله",
    "يأيها", "ياايها",
})


def _bare(s: str) -> str:
    if not s:
        return ""
    return "".join(
        c for c in (s or "").replace("-", "").strip()
        if not (0x064B <= ord(c) <= 0x0652 or ord(c) == 0x0670)
    ).strip()


@dataclass
class ResolverResult:
    root: str
    root_formatted: str
    source: str
    confidence: float
    wazn: str
    heuristic_reason: str

    @classmethod
    def _make(
        cls,
        root: str,
        source: str,
        confidence: float,
        wazn: str = "",
        heuristic_reason: str = "",
    ) -> "ResolverResult":
        formatted = "-".join(list(root)) if root else ""
        return cls(
            root=root,
            root_formatted=formatted,
            source=source,
            confidence=confidence,
            wazn=wazn,
            heuristic_reason=heuristic_reason,
        )


class RootResolver:
    def __init__(self, roots_db: RootsDB, wazn_adapter: WaznAdapter) -> None:
        self._db = roots_db
        self._wazn = wazn_adapter

    @classmethod
    def build(
        cls,
        patterns_csv: str | Path,
        roots_csv: str | Path,
    ) -> "RootResolver":
        db = RootsDB.load(Path(roots_csv))
        adapter = WaznAdapter.load(patterns_csv)
        return cls(db, adapter)

    def resolve(
        self,
        word: str,
        stripped: str = "",
        cli_root: str = "",
        kind: str = "",
        show_source: bool = False,
    ) -> ResolverResult:
        bare_word = _bare(word)
        bare_stripped = _bare(stripped)

        if bare_word in _NO_ROOT_WORDS_BARE or bare_stripped in _NO_ROOT_WORDS_BARE:
            return ResolverResult._make(
                root="",
                source="no_root",
                confidence=1.0,
                heuristic_reason="لفظ_الجلالة_أو_اسم",
            ) if show_source else ResolverResult._make(root="", source="", confidence=0.0)

        use_stripped = stripped
        if len(bare_stripped) < 3:
            use_stripped = bare_word
        if use_stripped.startswith("ال") and len(use_stripped) > 2:
            use_stripped = use_stripped[2:]

        result = self._try_cli(cli_root, kind)
        if result:
            result = self._canonicalize_result(result)
            return result if show_source else self._strip_meta(result)

        result = self._try_wazn(word, use_stripped, kind)
        if result:
            result = self._canonicalize_result(result)
            return result if show_source else self._strip_meta(result)

        if kind in NO_ROOT_KINDS:
            return ResolverResult._make(
                root="",
                source="no_root",
                confidence=1.0,
                heuristic_reason="مبني_أو_أداة",
            ) if show_source else self._strip_meta(ResolverResult._make(root="", source="", confidence=0.0))

        result = self._try_heuristic(word, use_stripped, kind)
        result = self._canonicalize_result(result)
        return result if show_source else self._strip_meta(result)

    def _try_cli(self, cli_root: str, kind: str) -> Optional[ResolverResult]:
        if not cli_root or kind in NO_ROOT_KINDS:
            return None
        # تنعيم إلى bare ثم canonicalize (بون→بين، شوء→شيء) ثم التنسيق بالشرطات
        cli_bare = (cli_root or "").replace("-", "").strip()
        cli_bare = self._db.normalize(cli_bare)
        if not cli_bare:
            return None
        if len(cli_bare) not in (3, 4):
            return None
        cli_bare = self._db.canonicalize(cli_bare)
        if not self._db.is_rootlike(cli_bare):
            return None
        # النتيجة: root بدون شرطات (و _make يضيف root_formatted ب-ي-ن)
        return ResolverResult._make(
            root=cli_bare,
            source="cli_verified",
            confidence=0.95,
        )

    def _try_wazn(self, word: str, stripped: str, kind: str) -> Optional[ResolverResult]:
        if kind in NO_ROOT_KINDS:
            return None
        wazn_result: Optional[WaznResult] = self._wazn.resolve(word=word, stripped=stripped)
        if not wazn_result:
            return None
        root = wazn_result.root
        if not root:
            return None
        # بعد استخراج root من wazn (قد يكون "ب-و-ن" أو "بون")
        bare = (root or "").replace("-", "").strip()
        # canonicalize: بون→بين، شوء→شيء (و↔ي في الحرف الأوسط)
        bare = self._db.canonicalize(bare)
        root = "-".join(bare) if bare else ""

        confidence = 0.85 if wazn_result.match_type == "FULLMATCH" else 0.70

        if self._db.is_rootlike(bare):
            return ResolverResult._make(
                root=root,
                source="wazn_resolved",
                confidence=confidence,
                wazn=wazn_result.wazn,
            )
        if len(bare) == 4:
            tri_bare = (bare[:3] or "").replace("-", "").strip()
            tri_bare = self._db.canonicalize(tri_bare)
            tri = "-".join(tri_bare) if tri_bare else ""
            if tri_bare and self._db.is_rootlike(tri_bare):
                return ResolverResult._make(
                    root=tri,
                    source="wazn_resolved",
                    confidence=confidence * 0.85,
                    wazn=wazn_result.wazn,
                )
            return None
        return None

    def _try_heuristic(self, word: str, stripped: str, kind: str) -> ResolverResult:
        h: HeuristicResult = heuristic_root(
            word=word,
            stripped=stripped,
            kind=kind,
            roots_db=self._db,
        )
        return ResolverResult._make(
            root=h.root,
            source="heuristic",
            confidence=h.confidence,
            heuristic_reason=h.reason,
        )

    def _canonicalize_result(self, result: ResolverResult) -> ResolverResult:
        """توحيد: كل نتيجة ذات جذر غير فارغ تُعاد بصيغة canonical (بون→بين، شوء→شيء)."""
        if not result or not result.root:
            return result
        bare = (result.root or "").replace("-", "").strip()
        bare = self._db.canonicalize(bare)
        if not bare:
            return result
        return ResolverResult._make(
            root=bare,
            source=result.source,
            confidence=result.confidence,
            wazn=result.wazn,
            heuristic_reason=result.heuristic_reason,
        )

    @staticmethod
    def _strip_meta(result: ResolverResult) -> ResolverResult:
        return ResolverResult(
            root=result.root,
            root_formatted=result.root_formatted,
            source="",
            confidence=0.0,
            wazn="",
            heuristic_reason="",
        )
