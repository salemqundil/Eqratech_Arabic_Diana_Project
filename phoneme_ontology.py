"""Phoneme ontology loader and helpers.

Loads Arabic phoneme/diacritic/operator ontology from YAML
(`config/phoneme_ontology.yaml`) and exposes small helper utilities
for other parts of the project (engines, tokenizer, training prep).

Example:
    from phoneme_ontology import get_ontology, list_particles
    ont = get_ontology()
    particles = list_particles()
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os


_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "config", "phoneme_ontology.yaml")


@dataclass
class Ontology:
    raw: Dict[str, Any]

    # Convenience selectors
    def phoneme_inventory(self) -> List[Dict[str, Any]]:
        return self.raw.get("phonemes", {}).get("inventory", [])

    def functional_sets(self) -> Dict[str, List[str]]:
        return self.raw.get("phonemes", {}).get("functional_sets", {})

    def diacritics_labels(self) -> Dict[str, Dict[str, Any]]:
        return self.raw.get("diacritics", {}).get("labels", {})

    def tri_past_patterns(self) -> List[Dict[str, str]]:
        return self.raw.get("diacritics", {}).get("tri_past_patterns", [])

    def allowed_syllable_gates(self) -> List[str]:
        return self.raw.get("syllables", {}).get("allowed_gates", [])

    def particles(self) -> List[Any]:
        # Return as untyped list to avoid strict typing issues from YAML
        return list(self.raw.get("operators", {}).get("particles", []))

    def demonstratives(self) -> List[str]:
        return self.raw.get("operators", {}).get("demonstratives", [])

    def relatives(self) -> List[str]:
        return self.raw.get("operators", {}).get("relatives", [])

    def interrogatives(self) -> List[str]:
        return self.raw.get("operators", {}).get("interrogatives", [])

    def i3rab_types(self) -> List[str]:
        return self.raw.get("operators", {}).get("i3rab", {}).get("types", [])

    def labels(self) -> Dict[str, Any]:
        return self.raw.get("labels", {})

    def rules(self) -> Dict[str, Any]:
        return self.raw.get("rules", {})


_CACHED: Optional[Ontology] = None


def get_ontology(path: Optional[str] = None) -> Ontology:
    """Load the ontology YAML (cached) and return a typed wrapper.

    Args:
        path: Optional override path; defaults to config/phoneme_ontology.yaml
    """
    global _CACHED
    if _CACHED is not None and path is None:
        return _CACHED

    yaml_path = path or _DEFAULT_PATH
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Ontology YAML not found: {yaml_path}")

    # Local import to avoid hard dependency when not needed
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise ImportError("PyYAML is required to load the ontology. Install with `pip install pyyaml`.\n" + str(e))

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    ont = Ontology(raw=data)
    if path is None:
        _CACHED = ont
    return ont


# Helper functions commonly needed across the project
def list_particles() -> List[str]:
    items: List[str] = []
    for p in get_ontology().particles():
        if isinstance(p, dict) and "form" in p:
            form_val = p["form"]
            if isinstance(form_val, str) and form_val:
                items.append(form_val)
    return items


def list_demonstratives() -> List[str]:
    return list(get_ontology().demonstratives())


def list_relatives() -> List[str]:
    return list(get_ontology().relatives())


def list_interrogatives() -> List[str]:
    return list(get_ontology().interrogatives())


def mudari_prefixes() -> List[str]:
    return list(get_ontology().functional_sets().get("mudari_prefix", []))


def ten_augments() -> List[str]:
    return list(get_ontology().functional_sets().get("ten_augments", []))


def allowed_syllable_gates() -> List[str]:
    return list(get_ontology().allowed_syllable_gates())


__all__ = [
    "Ontology",
    "get_ontology",
    "list_particles",
    "list_demonstratives",
    "list_relatives",
    "list_interrogatives",
    "mudari_prefixes",
    "ten_augments",
    "allowed_syllable_gates",
]


if __name__ == "__main__":
    ont = get_ontology()
    print("Particles:", list_particles()[:10])
    print("Demonstratives:", list_demonstratives())
    print("Relatives:", list_relatives())
    print("Interrogatives:", list_interrogatives())
    print("Mudari prefixes:", mudari_prefixes())
    print("Syllable gates:", allowed_syllable_gates())
