    def _try_wazn(self, word: str, stripped: str, kind: str) -> Optional[ResolverResult]:
        """
        يُشغّل WaznAdapter ويتحقق من النتيجة في roots_db.
        لو الجذر الرباعي غير موجود لكن أول 3 حروف موجودة → يُعيد الثلاثي.
        """
        if kind in NO_ROOT_KINDS:
            return None

        wazn_result: Optional[WaznResult] = self._wazn.resolve(
            word=word,
            stripped=stripped,
        )
        if not wazn_result:
            return None

        root = wazn_result.root
        if not root:
            return None

        confidence = 0.85 if wazn_result.match_type == "FULLMATCH" else 0.70

        # الجذر موجود مباشرة
        if self._db.is_valid(root):
            return ResolverResult._make(
                root=root,
                source="wazn_resolved",
                confidence=confidence,
                wazn=wazn_result.wazn,
            )

        # لو الجذر 4 حروف وغير موجود → جرب أول 3 حروف
        if len(root) == 4:
            tri = root[:3]
            if self._db.is_valid(tri):
                return ResolverResult._make(
                    root=tri,
                    source="wazn_resolved",
                    confidence=confidence * 0.85,
                    wazn=wazn_result.wazn,
                )

        # الجذر غير موجود في القاعدة — نعيده بثقة أقل (كما كان سابقاً)
        return ResolverResult._make(
            root=root,
            source="wazn_resolved",
            confidence=confidence * 0.6,
            wazn=wazn_result.wazn,
        )