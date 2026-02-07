"""
Trace V1 (Plan-aligned, lightweight):

- Keep `FormCodecV2` reversible and "raw"
- Put *all* modifications in gates over `FormStream`
- Record each gate application as a `TraceStep`

This does not attempt formal proof; it is designed to be formalizable later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple

from .form_codec_v2 import FormCodecV2, FormStream, GraphemeToken, stable_hash


class GateFn(Protocol):
    def __call__(self, stream: FormStream, *, rule_id: Optional[str] = None) -> FormStream: ...


@dataclass(frozen=True)
class TokenDiff:
    """
    A stable-ish token diff for trace/debugging.

    We describe changes at the *token text* level. This is intentionally simple:
    later versions can add minimal edit paths or richer diffs.
    """

    op: str  # "equal" | "replace" | "insert" | "delete"
    a_range: Tuple[int, int]
    b_range: Tuple[int, int]
    a_text: Tuple[str, ...]
    b_text: Tuple[str, ...]


def _token_texts(tokens: Sequence[GraphemeToken]) -> List[str]:
    return [t.to_text() for t in tokens]


def diff_tokens(a: FormStream, b: FormStream) -> List[TokenDiff]:
    """
    Token-level diff using SequenceMatcher over token texts.
    """
    from difflib import SequenceMatcher

    a_txt = _token_texts(a.tokens)
    b_txt = _token_texts(b.tokens)
    sm = SequenceMatcher(a=a_txt, b=b_txt)
    out: List[TokenDiff] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        out.append(
            TokenDiff(
                op=tag,
                a_range=(i1, i2),
                b_range=(j1, j2),
                a_text=tuple(a_txt[i1:i2]),
                b_text=tuple(b_txt[j1:j2]),
            )
        )
    return out


@dataclass(frozen=True)
class TraceStep:
    gate_id: str
    rule_id: Optional[str]
    before_hash: str
    after_hash: str
    diff: Tuple[TokenDiff, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Trace:
    """
    A lightweight trace capturing a chain of gate applications.

    Important: Trace does not by itself reproduce the final form.
    Replay requires the same deterministic gates (provided via a registry).
    """

    inventory_id: str
    original_hash: str
    steps: Tuple[TraceStep, ...] = field(default_factory=tuple)

    def append(self, step: TraceStep) -> "Trace":
        return Trace(self.inventory_id, self.original_hash, self.steps + (step,))


def hash_stream(stream: FormStream) -> str:
    """
    Hash identity for a FormStream based on exact decoded text (NFC).
    """
    return stable_hash(stream.decode())


def apply_gate_with_trace(
    stream: FormStream,
    trace: Trace,
    *,
    gate_id: str,
    gate: GateFn,
    rule_id: Optional[str] = None,
) -> Tuple[FormStream, Trace]:
    before_hash = hash_stream(stream)
    out = gate(stream, rule_id=rule_id)
    after_hash = hash_stream(out)
    step = TraceStep(
        gate_id=gate_id,
        rule_id=rule_id,
        before_hash=before_hash,
        after_hash=after_hash,
        diff=tuple(diff_tokens(stream, out)),
    )
    return out, trace.append(step)


def replay(
    original: FormStream,
    trace: Trace,
    *,
    registry: Dict[str, GateFn],
) -> FormStream:
    """
    Replay a trace from an original `FormStream` given a registry of deterministic gates.

    This verifies hash chaining and re-applies gates in order.
    """
    if trace.original_hash != hash_stream(original):
        raise ValueError("Trace replay error: original_hash does not match provided stream.")

    current = original
    for step in trace.steps:
        if step.gate_id not in registry:
            raise KeyError(f"Missing gate in registry: {step.gate_id}")
        if hash_stream(current) != step.before_hash:
            raise ValueError(f"Trace replay error: before_hash mismatch at gate {step.gate_id}")
        current = registry[step.gate_id](current, rule_id=step.rule_id)
        if hash_stream(current) != step.after_hash:
            raise ValueError(f"Trace replay error: after_hash mismatch at gate {step.gate_id}")
    return current


def new_trace(stream: FormStream) -> Trace:
    return Trace(inventory_id=stream.inventory_id, original_hash=hash_stream(stream))


def encode_with_trace(codec: FormCodecV2, text: str) -> Tuple[FormStream, Trace]:
    fs = codec.encode(text)
    return fs, new_trace(fs)

