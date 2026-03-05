"""
Run full pipeline on آية الدين (Al-Baqarah 2:282) and write JSON to out.txt.

Usage (from repo root):
  PYTHONPATH=src python scripts/run_ayat_al_dayn_snapshot.py
  PYTHONPATH=src python scripts/run_ayat_al_dayn_snapshot.py --output other.txt

The output is the same structure as: python -m fvafk.cli "..." --morphology --multi-word --json
"""

import argparse
import json
import sys
from pathlib import Path

# آية الدين (سورة البقرة 2:282) - من data/quran/train.jsonl
AYAT_AL_DAYN = (
    "يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنتُم بِدَيْنٍ إِلَى أَجَلٍ مُّسَمًّى فَاكْتُبُوهُ وَلْيَكْتُب بَّيْنَكُمْ كَاتِبٌ بِالْعَدْلِ وَلَا يَأْبَ كَاتِبٌ أَن يَكْتُبَ كَمَا عَلَّمَهُ اللَّهُ فَلْيَكْتُبْ وَلْيُمْلِلِ الَّذِي عَلَيْهِ الْحَقُّ وَلْيَتَّقِ اللَّهَ رَبَّهُ وَلَا يَبْخَسْ مِنْهُ شَيْئاً فَإِن كَانَ الَّذِي عَلَيْهِ الْحَقُّ سَفِيهاً أَوْ ضَعِيفاً أَوْ لَا يَسْتَطِيعُ أَن يُمِلَّ هُوَ فَلْيُمْلِلْ وَلِيُّهُ بِالْعَدْلِ وَاسْتَشْهِدُوا شَهِيدَيْنِ مِن رِّجَالِكُمْ فَإِن لَّمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَامْرَأَتَانِ مِمَّن تَرْضَوْنَ مِنَ الشُّهَدَاءِ أَن تَضِلَّ إِحْدَاهُمَا فَتُذَكِّرَ إِحْدَاهُمَا الْأُخْرَى وَلَا يَأْبَ الشُّهَدَاءُ إِذَا مَا دُعُوا وَلَا تَسْأَمُوا أَن تَكْتُبُوهُ صَغِيراً أَوْ كَبِيراً إِلَى أَجَلِهِ ذَلِكُمْ أَقْسَطُ عِندَ اللَّهِ وَأَقْوَمُ لِلشَّهَادَةِ وَأَدْنَى أَلَّا تَرْتَابُوا إِلَّا أَن تَكُونَ تِجَارَةً حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا وَأَشْهِدُوا إِذَا تَبَايَعْتُمْ وَلَا يُضَارَّ كَاتِبٌ وَلَا شَهِيدٌ وَإِن تَفْعَلُوا فَإِنَّهُ فُسُوقٌ بِكُمْ وَاتَّقُوا اللَّهَ وَيُعَلِّمُكُمُ اللَّهُ وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("out.txt"),
        help="Output JSON file (default: out.txt)",
    )
    parser.add_argument(
        "--phonology-v2",
        action="store_true",
        help="Use Phonology V2 engine",
    )
    args = parser.parse_args()

    try:
        from fvafk.cli.main import MinimalCLI
    except ImportError:
        print("Run from repo root with: PYTHONPATH=src python scripts/run_ayat_al_dayn_snapshot.py", file=sys.stderr)
        return 1

    cli = MinimalCLI(verbose=False, json_output=True)
    result = cli.run(
        text=AYAT_AL_DAYN,
        verbose=False,
        morphology=True,
        multi_word=True,
        phonology_v2=args.phonology_v2,
        phonology_v2_details=False,
        phonology_v2_witnesses=False,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
