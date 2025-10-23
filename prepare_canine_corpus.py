"""
تحضير بيانات تدريب نموذج CANINE من مخرجات المولد الصوتي-الصرفي.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from comprehensive_arabic_generator import (
    AdvancedArabicGenerator,
    ComprehensiveArabicSystem,
    WeightCategory,
)


SAMPLE_ROOTS = ["كتب", "ضرب", "علم", "كرم", "جلس", "دحرج", "زعزع"]


def ensure_text(value) -> str:
    """تحويل أي قيمة إلى تمثيل نصي مع المحافظة على الترميز."""
    if isinstance(value, WeightCategory):
        return value.value
    return str(value)


def generate_base_structures() -> Tuple[Dict[str, List[str]], Dict[str, Dict[str, Dict]], List[str]]:
    """
    توليد المقاطع، الأوزان، والأشكال المزيدة دون ترشيح.
    """
    system = ComprehensiveArabicSystem()
    syllables = system.syllable_gen.generate_all_syllables()

    morph_data: Dict[str, Dict[str, Dict]] = {}
    for category, weights in system.matrix.morphological_weights.items():
        morph_data[category] = {}
        for weight_name, weight_info in weights.items():
            template = weight_info["template"]
            weight_type = weight_info["type"]
            forms: List[str] = []
            for root in SAMPLE_ROOTS:
                if weight_type == WeightCategory.TRILATERAL_VERB and len(root) != 3:
                    continue
                if weight_type == WeightCategory.QUADRILATERAL_VERB and len(root) != 4:
                    continue
                if weight_type == WeightCategory.AUGMENTED_VERB and len(root) != 3:
                    continue
                if weight_type in {WeightCategory.BASIC_NOUN, WeightCategory.DERIVED_NOUN} and len(root) != 3:
                    continue
                if weight_type == WeightCategory.PARTICLE:
                    # الأوزان من فئة الأدوات ثابتة
                    forms.append(template)
                    continue
                form = system.morph_gen.apply_weight_to_root(root, template)
                if form:
                    forms.append(form)
            morph_data[category][weight_name] = {
                "type": ensure_text(weight_type),
                "template": template,
                "forms": forms,
            }

    all_forms: List[str] = []
    for category in morph_data.values():
        for info in category.values():
            all_forms.extend(info["forms"])

    augmented_map = system.aug_gen.generate_augmented_forms({"all_forms": all_forms})
    augmented_forms = augmented_map.get("all_forms", [])

    return syllables, morph_data, augmented_forms


def apply_optimizations(
    syllables: Dict[str, List[str]],
    morph_data: Dict[str, Dict[str, Dict]],
    augmented_forms: List[str],
    top_augmented: int,
) -> Tuple[Dict[str, List[str]], Dict[str, Dict[str, Dict]], List[str]]:
    """
    تطبيق التحسينات المتقدمة للمولد.
    """
    advanced = AdvancedArabicGenerator()
    opt_syllables = {
        pattern: advanced.optimize_phonotactics(forms) for pattern, forms in syllables.items()
    }

    opt_morph: Dict[str, Dict[str, Dict]] = {}
    for category, weights in morph_data.items():
        opt_morph[category] = {}
        for weight_name, info in weights.items():
            realistic_forms = [form for form in info["forms"] if advanced.is_realistic_form(form)]
            opt_morph[category][weight_name] = {**info, "forms": realistic_forms}

    sorted_augmented = sorted(set(augmented_forms))
    selected_augmented = advanced.select_by_frequency(sorted_augmented, top_n=top_augmented)

    return opt_syllables, opt_morph, selected_augmented


def export_corpus(
    syllables: Dict[str, List[str]],
    morph_data: Dict[str, Dict[str, Dict]],
    augmented_forms: Iterable[str],
    output_dir: Path,
) -> Tuple[int, int, int]:
    """
    حفظ البيانات في ملف TSV مع ملف تعريف JSON مرافق.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = output_dir / "canine_corpus.tsv"
    metadata_path = output_dir / "canine_corpus_meta.json"

    syllable_count = sum(len(forms) for forms in syllables.values())
    morph_count = sum(len(info["forms"]) for category in morph_data.values() for info in category.values())
    augmented_list = list(augmented_forms)
    augmented_count = len(augmented_list)

    with open(corpus_path, "w", encoding="utf-8") as f:
        f.write("type\tcategory\tsubtype\tform\n")
        for pattern, forms in syllables.items():
            for form in forms:
                f.write(f"syllable\t{pattern}\t-\t{form}\n")
        for category, weights in morph_data.items():
            for weight_name, info in weights.items():
                for form in info["forms"]:
                    f.write(f"morph\t{category}\t{weight_name}\t{form}\n")
        for form in augmented_list:
            f.write(f"augmented\tall_forms\t-\t{form}\n")

    metadata = {
        "syllable_count": syllable_count,
        "morph_count": morph_count,
        "augmented_count": augmented_count,
        "total_records": syllable_count + morph_count + augmented_count,
        "source_roots": SAMPLE_ROOTS,
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return syllable_count, morph_count, augmented_count


def prepare_corpus(output_dir: Path, optimized: bool, top_augmented: int) -> Dict[str, int]:
    """
    توليد وتصدير بيانات CANINE، مع خيار التحسين.
    """
    syllables, morph_data, augmented_forms = generate_base_structures()
    if optimized:
        syllables, morph_data, augmented_forms = apply_optimizations(
            syllables, morph_data, augmented_forms, top_augmented
        )
    counts = export_corpus(syllables, morph_data, augmented_forms, output_dir)
    return {
        "syllable_count": counts[0],
        "morph_count": counts[1],
        "augmented_count": counts[2],
        "total_records": sum(counts),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="تجهيز بيانات تدريب CANINE.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/canine_training"),
        help="المجلد الذي سيتم حفظ البيانات فيه.",
    )
    parser.add_argument(
        "--optimized",
        action="store_true",
        help="استخدام النسخة المحسّنة من البيانات (تحسينات صوتية وصرفية).",
    )
    parser.add_argument(
        "--top-augmented",
        type=int,
        default=1000,
        help="عدد الأشكال المزيدة الأعلى تواتراً (محاكاة) ضمن البيانات المحسّنة.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = prepare_corpus(args.output_dir, args.optimized, args.top_augmented)
    print("✅ تم تجهيز بيانات CANINE")
    print(f"  • عدد المقاطع: {stats['syllable_count']}")
    print(f"  • عدد الأوزان: {stats['morph_count']}")
    print(f"  • عدد الأشكال المزيدة: {stats['augmented_count']}")
    print(f"  • إجمالي السجلات: {stats['total_records']}")
    print(f"  • المجلد: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()

