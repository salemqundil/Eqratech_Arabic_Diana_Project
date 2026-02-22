import inspect
import importlib
import pkgutil
import pandas as pd
from pathlib import Path

from base_reconstruction_engine import BaseReconstructionEngine


def _iter_engine_modules():
    base_dir = Path(__file__).parent
    for module_info in pkgutil.iter_modules([str(base_dir)]):
        name = module_info.name
        if not name.endswith('_engine') and not name.endswith('_engine'.replace('_', '')):
            # keep only *engine.py style modules by loose heuristic
            pass
        try:
            yield importlib.import_module(name)
        except Exception:
            continue


def collect_engines():
    engines = []
    for mod in _iter_engine_modules():
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, BaseReconstructionEngine) and obj is not BaseReconstructionEngine:
                # Ensure class defines SHEET_NAME and make_df
                if hasattr(obj, 'SHEET_NAME') and hasattr(obj, 'make_df'):
                    engines.append(obj)
    # Remove duplicates by sheet name keeping first appearance
    seen = set()
    unique = []
    for e in engines:
        sn = getattr(e, 'SHEET_NAME', e.__name__)
        if sn not in seen:
            unique.append(e)
            seen.add(sn)
    return unique


def export_all(output_path: str = 'full_multilayer_grammar.xlsx'):
    engines = collect_engines()
    with pd.ExcelWriter(output_path) as writer:
        for engine_cls in engines:
            try:
                df = engine_cls.make_df()
                sheet = engine_cls.SHEET_NAME[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet, index=False)
            except Exception as e:
                # Optionally: log or collect errors; for now skip failing engine
                continue


def main():
    export_all()


if __name__ == "__main__":
    main()