#!/usr/bin/env python3
"""
Engine Hierarchy Explorer
=========================
Visualize and navigate the hierarchical structure of all grammar engines.

Usage:
    python engine_hierarchy.py                    # Show full tree
    python engine_hierarchy.py --layer 2          # Show morphology layer
    python engine_hierarchy.py --group 2.1        # Show verbal morphology
    python engine_hierarchy.py --export json      # Export to JSON
    python engine_hierarchy.py --stats            # Show statistics
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from engines.base import BaseReconstructionEngine, EngineLayer


class EngineHierarchyExplorer:
    """Navigate and visualize engine hierarchy"""
    
    def __init__(self):
        self.engines = self._discover_engines()
        self.hierarchy = self._build_hierarchy()
    
    def _discover_engines(self) -> List[type]:
        """Discover all engine classes"""
        engines = []
        
        # Import all engine modules
        try:
            from engines import phonology, morphology, lexicon, syntax, rhetoric
            # Note: generation layer temporarily excluded due to import dependencies
            
            # Collect engines from each layer
            for module in [phonology, morphology, lexicon, syntax, rhetoric]:
                for name in dir(module):
                    obj = getattr(module, name)
                    if (isinstance(obj, type) and 
                        issubclass(obj, BaseReconstructionEngine) and 
                        obj is not BaseReconstructionEngine and
                        hasattr(obj, 'SHEET_NAME')):
                        engines.append(obj)
        except Exception as e:
            print(f"⚠️  Warning: Could not import all engines: {e}")
        
        return engines
    
    def _build_hierarchy(self) -> Dict[str, Any]:
        """Build hierarchical structure"""
        hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for engine in self.engines:
            layer = engine.LAYER.name
            group = getattr(engine, 'GROUP', None) or 'Ungrouped'
            subgroup = getattr(engine, 'SUBGROUP', None) or 'Ungrouped'
            
            hierarchy[layer][group][subgroup].append(engine)
        
        return dict(hierarchy)
    
    def show_tree(self, layer_filter: Optional[int] = None, group_filter: Optional[str] = None):
        """Display hierarchical tree"""
        print("\n" + "="*80)
        print("🌳 ARABIC GRAMMAR ENGINE HIERARCHY")
        print("="*80 + "\n")
        
        for layer_name, groups in sorted(self.hierarchy.items()):
            layer_num = EngineLayer[layer_name].value
            
            # Filter by layer if specified
            if layer_filter and layer_num != layer_filter:
                continue
            
            layer_ar = {
                'PHONOLOGY': 'الصوتيات',
                'MORPHOLOGY': 'الصرف',
                'LEXICON': 'المعجم',
                'SYNTAX': 'النحو',
                'RHETORIC': 'البلاغة',
                'GENERATION': 'التوليد'
            }.get(layer_name, '')
            
            print(f"📂 Layer {layer_num}: {layer_name} ({layer_ar})")
            print("─" * 80)
            
            for group_id, subgroups in sorted(groups.items()):
                # Filter by group if specified
                if group_filter and group_id != group_filter:
                    continue
                
                if group_id != 'Ungrouped':
                    print(f"  ├─ Group {group_id}")
                
                for subgroup_id, engines in sorted(subgroups.items()):
                    if subgroup_id != 'Ungrouped':
                        print(f"  │  ├─ Subgroup {subgroup_id}")
                        prefix = "  │  │  "
                    else:
                        prefix = "  │  "
                    
                    for i, engine in enumerate(engines):
                        is_last = i == len(engines) - 1
                        connector = "└─" if is_last else "├─"
                        
                        # Get Arabic names if available
                        group_ar = getattr(engine, 'GROUP_AR', '')
                        subgroup_ar = getattr(engine, 'SUBGROUP_AR', '')
                        
                        label = f"{prefix}{connector} {engine.__name__}"
                        details = f" [{engine.SHEET_NAME}]"
                        
                        if group_ar or subgroup_ar:
                            ar_info = " | ".join(filter(None, [group_ar, subgroup_ar]))
                            details += f" ({ar_info})"
                        
                        print(label + details)
            
            print()
    
    def show_statistics(self):
        """Display hierarchy statistics"""
        print("\n" + "="*80)
        print("📊 HIERARCHY STATISTICS")
        print("="*80 + "\n")
        
        total_engines = len(self.engines)
        print(f"Total Engines: {total_engines}\n")
        
        # By layer
        print("By Layer:")
        print("─" * 40)
        for layer in EngineLayer:
            count = sum(
                len(engines)
                for groups in self.hierarchy.get(layer.name, {}).values()
                for engines in groups.values()
            )
            print(f"  Layer {layer.value} ({layer.name}): {count} engines")
        
        print()
        
        # Groups per layer
        print("Groups per Layer:")
        print("─" * 40)
        for layer_name, groups in sorted(self.hierarchy.items()):
            non_ungrouped = len([g for g in groups if g != 'Ungrouped'])
            print(f"  {layer_name}: {non_ungrouped} groups")
        
        print()
        
        # Subgroups
        print("Subgroups:")
        print("─" * 40)
        total_subgroups = 0
        for groups in self.hierarchy.values():
            for subgroups in groups.values():
                total_subgroups += len([s for s in subgroups if s != 'Ungrouped'])
        print(f"  Total: {total_subgroups} subgroups")
        
        print()
    
    def export_json(self, output_file: str = "engine_hierarchy.json"):
        """Export hierarchy to JSON"""
        export_data = {
            'metadata': {
                'version': '2.0.0',
                'total_engines': len(self.engines),
                'layers': len(EngineLayer)
            },
            'hierarchy': {}
        }
        
        for layer_name, groups in self.hierarchy.items():
            layer_data = {}
            for group_id, subgroups in groups.items():
                group_data = {}
                for subgroup_id, engines in subgroups.items():
                    group_data[subgroup_id] = [
                        {
                            'name': e.__name__,
                            'sheet_name': e.SHEET_NAME,
                            'group': getattr(e, 'GROUP', None),
                            'subgroup': getattr(e, 'SUBGROUP', None),
                            'group_ar': getattr(e, 'GROUP_AR', None),
                            'subgroup_ar': getattr(e, 'SUBGROUP_AR', None)
                        }
                        for e in engines
                    ]
                layer_data[group_id] = group_data
            export_data['hierarchy'][layer_name] = layer_data
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Exported hierarchy to {output_file}")
    
    def search_engine(self, query: str):
        """Search for engines by name or Arabic term"""
        print(f"\n🔍 Search results for: {query}\n")
        print("─" * 80)
        
        results = []
        for engine in self.engines:
            # Check name
            if query.lower() in engine.__name__.lower():
                results.append(engine)
            # Check sheet name
            elif hasattr(engine, 'SHEET_NAME') and query in engine.SHEET_NAME:
                results.append(engine)
            # Check Arabic names (handle None)
            elif (hasattr(engine, 'GROUP_AR') and getattr(engine, 'GROUP_AR') and query in getattr(engine, 'GROUP_AR')) or \
                 (hasattr(engine, 'SUBGROUP_AR') and getattr(engine, 'SUBGROUP_AR') and query in getattr(engine, 'SUBGROUP_AR')):
                results.append(engine)
        
        if results:
            for engine in results:
                print(f"📦 {engine.__name__}")
                print(f"   Sheet: {engine.SHEET_NAME}")
                print(f"   Layer: {engine.LAYER.name} ({engine.LAYER.value})")
                if hasattr(engine, 'GROUP') and engine.GROUP:
                    print(f"   Group: {engine.GROUP}")
                if hasattr(engine, 'SUBGROUP') and engine.SUBGROUP:
                    print(f"   Subgroup: {engine.SUBGROUP}")
                print(f"   Hierarchy: {engine.get_hierarchy()}")
                print()
        else:
            print("No engines found matching the query.")
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Explore Arabic Grammar Engine Hierarchy',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--layer', type=int, help='Filter by layer number (1-6)')
    parser.add_argument('--group', type=str, help='Filter by group ID (e.g., 2.1)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', type=str, choices=['json'], help='Export format')
    parser.add_argument('--search', type=str, help='Search for engine by name or term')
    
    args = parser.parse_args()
    
    explorer = EngineHierarchyExplorer()
    
    if args.stats:
        explorer.show_statistics()
    elif args.export == 'json':
        explorer.export_json()
    elif args.search:
        explorer.search_engine(args.search)
    else:
        explorer.show_tree(layer_filter=args.layer, group_filter=args.group)


if __name__ == '__main__':
    main()
