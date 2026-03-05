"""
Particle Loader Module

This module loads Arabic particles (حروف) from CSV files and integrates
them with the node schema framework for morphological and syntactic analysis.

Supported particle types:
- Prepositions (حروف الجر)
- Conjunctions (حروف العطف)
- Interrogatives (أدوات الاستفهام)
- Nasb particles (أدوات النصب)
- Negative particles (أدوات النفي)
- And more from operators_catalog_split.csv
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from .node_schema import Node, NodeType, Case, create_preposition
except ImportError:
    from node_schema import Node, NodeType, Case, create_preposition


class ParticleCategory(Enum):
    """Categories of Arabic particles"""
    PREPOSITION = "preposition"              # حرف جر
    CONJUNCTION = "conjunction"              # حرف عطف
    INTERROGATIVE = "interrogative"          # أداة استفهام
    NASB = "nasb"                           # أداة نصب
    NEGATIVE = "negative"                    # أداة نفي
    VERB_LIKE = "verb_like"                 # حرف مشبه بالفعل
    CONDITIONAL = "conditional"              # أداة شرط
    EXCEPTION = "exception"                  # أداة استثناء
    OTHER = "other"


@dataclass
class ParticleData:
    """Data structure for a particle entry"""
    surface: str                           # Surface form (e.g., "في")
    category: ParticleCategory             # Particle category
    meaning: Optional[str] = None          # Semantic meaning
    example: Optional[str] = None          # Usage example
    governs_case: Optional[Case] = None    # Case governed (for prepositions)
    syntactic_function: Optional[str] = None
    semantic_function: Optional[str] = None
    metadata: Dict = None                  # Additional metadata
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ParticleLoader:
    """
    Loads particles from various CSV sources and provides unified access
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize particle loader
        
        Args:
            data_dir: Path to data directory. If None, uses repository root.
        """
        if data_dir is None:
            # Try to find repository root
            current = Path(__file__).parent
            while current.parent != current:
                if (current / 'data').exists():
                    data_dir = current
                    break
                current = current.parent
            else:
                data_dir = Path.cwd()
        
        self.data_dir = Path(data_dir)
        self.particles: List[ParticleData] = []
        self._loaded = False
    
    def load_all(self):
        """Load particles from all available sources"""
        if self._loaded:
            return
        
        # Try to load from operators_catalog_split.csv first
        operators_file = self.data_dir / 'data' / 'arabic_json' / 'operators_catalog_split.csv'
        if operators_file.exists():
            self._load_operators_catalog(operators_file)
        
        # Load from individual CSV files
        self._load_prepositions()
        self._load_conjunctions()
        self._load_interrogatives()
        self._load_nasb_tools()
        self._load_negatives()
        
        self._loaded = True
    
    def _load_operators_catalog(self, filepath: Path):
        """
        Load particles from operators_catalog_split.csv
        
        This is the primary source when available.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse based on available columns
                    # Adapt this based on actual file structure
                    particle = self._parse_operator_row(row)
                    if particle:
                        self.particles.append(particle)
        except Exception as e:
            print(f"Warning: Could not load operators_catalog_split.csv: {e}")
    
    def _parse_operator_row(self, row: Dict) -> Optional[ParticleData]:
        """Parse a row from operators_catalog_split.csv"""
        # This will need to be adapted based on actual file structure
        # For now, return None as placeholder
        return None
    
    def _load_prepositions(self):
        """Load prepositions from preposition_meanings.csv"""
        filepath = self.data_dir / 'preposition_meanings.csv'
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('is_deleted') == '1':
                        continue
                    
                    surface = row.get('preposition', '').strip()
                    if not surface:
                        continue
                    
                    # Extract just the particle without parenthetical explanation
                    if '(' in surface:
                        surface = surface.split('(')[0].strip()
                    
                    particle = ParticleData(
                        surface=surface,
                        category=ParticleCategory.PREPOSITION,
                        meaning=row.get('meaning'),
                        example=row.get('example'),
                        governs_case=Case.GEN,  # Prepositions govern genitive
                        syntactic_function=row.get('syntactic_effect'),
                        semantic_function=row.get('semantic_logical'),
                        metadata={'source': 'preposition_meanings.csv', 'id': row.get('id')}
                    )
                    self.particles.append(particle)
        except Exception as e:
            print(f"Warning: Could not load prepositions: {e}")
    
    def _load_conjunctions(self):
        """Load conjunctions from coordinating_conjunctions.csv"""
        filepath = self.data_dir / 'coordinating_conjunctions.csv'
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('is_deleted') == '1':
                        continue
                    
                    surface = row.get('letter', '').strip()
                    if not surface:
                        continue
                    
                    # Extract just the particle
                    if '(' in surface:
                        surface = surface.split('(')[0].strip()
                    
                    particle = ParticleData(
                        surface=surface,
                        category=ParticleCategory.CONJUNCTION,
                        meaning=row.get('usages'),
                        example=row.get('example'),
                        syntactic_function=row.get('usages'),
                        metadata={
                            'source': 'coordinating_conjunctions.csv',
                            'id': row.get('id'),
                            'type': row.get('type'),
                            'notes': row.get('notes')
                        }
                    )
                    self.particles.append(particle)
        except Exception as e:
            print(f"Warning: Could not load conjunctions: {e}")
    
    def _load_interrogatives(self):
        """Load interrogative particles from interrogative_tools_categories.csv"""
        filepath = self.data_dir / 'interrogative_tools_categories.csv'
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('is_deleted') == '1':
                        continue
                    
                    surface = row.get('tool', '').strip()
                    if not surface:
                        continue
                    
                    particle = ParticleData(
                        surface=surface,
                        category=ParticleCategory.INTERROGATIVE,
                        meaning=row.get('explanation'),
                        example=row.get('example'),
                        syntactic_function=row.get('subject'),
                        metadata={
                            'source': 'interrogative_tools_categories.csv',
                            'id': row.get('id'),
                            'type': row.get('type')
                        }
                    )
                    self.particles.append(particle)
        except Exception as e:
            print(f"Warning: Could not load interrogatives: {e}")
    
    def _load_nasb_tools(self):
        """Load nasb particles from present_naseb_tools.csv"""
        filepath = self.data_dir / 'present_naseb_tools.csv'
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('is_deleted') == '1':
                        continue
                    
                    surface = row.get('tool', '').strip()
                    if not surface:
                        continue
                    
                    particle = ParticleData(
                        surface=surface,
                        category=ParticleCategory.NASB,
                        meaning=row.get('meaning'),
                        example=row.get('example'),
                        metadata={
                            'source': 'present_naseb_tools.csv',
                            'id': row.get('id')
                        }
                    )
                    self.particles.append(particle)
        except Exception as e:
            print(f"Warning: Could not load nasb tools: {e}")
    
    def _load_negatives(self):
        """Load negative particles from tool_negatives.csv"""
        filepath = self.data_dir / 'tool_negatives.csv'
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('is_deleted') == '1':
                        continue
                    
                    surface = row.get('tool', '').strip()
                    if not surface:
                        continue
                    
                    particle = ParticleData(
                        surface=surface,
                        category=ParticleCategory.NEGATIVE,
                        meaning=row.get('meaning'),
                        example=row.get('example'),
                        metadata={
                            'source': 'tool_negatives.csv',
                            'id': row.get('id'),
                            'effect': row.get('effect')
                        }
                    )
                    self.particles.append(particle)
        except Exception as e:
            print(f"Warning: Could not load negatives: {e}")
    
    def get_particles_by_category(self, category: ParticleCategory) -> List[ParticleData]:
        """Get all particles of a specific category"""
        if not self._loaded:
            self.load_all()
        return [p for p in self.particles if p.category == category]
    
    def get_particle(self, surface: str) -> Optional[ParticleData]:
        """Get particle data by surface form"""
        if not self._loaded:
            self.load_all()
        
        for particle in self.particles:
            if particle.surface == surface:
                return particle
        return None
    
    def get_prepositions(self) -> List[ParticleData]:
        """Get all prepositions"""
        return self.get_particles_by_category(ParticleCategory.PREPOSITION)
    
    def get_conjunctions(self) -> List[ParticleData]:
        """Get all conjunctions"""
        return self.get_particles_by_category(ParticleCategory.CONJUNCTION)
    
    def create_node_from_particle(self, particle: ParticleData, slot: int = 0) -> Optional[Node]:
        """
        Create a Node from particle data for use in energy evaluation
        
        Args:
            particle: Particle data
            slot: Position slot
            
        Returns:
            Node instance or None if particle type not supported
        """
        if particle.category == ParticleCategory.PREPOSITION:
            case = particle.governs_case or Case.GEN
            return create_preposition(
                id=f"particle_{slot}",
                surface=particle.surface,
                governs_case=case,
                slot=slot
            )
        
        # Add more particle types as needed
        return None


def demonstrate_particle_loader():
    """Demonstrate particle loader functionality"""
    print("=" * 70)
    print("PARTICLE LOADER DEMONSTRATION")
    print("=" * 70)
    print()
    
    loader = ParticleLoader()
    loader.load_all()
    
    print(f"Total particles loaded: {len(loader.particles)}")
    print()
    
    # Show prepositions
    prepositions = loader.get_prepositions()
    print(f"Prepositions (حروف الجر): {len(prepositions)} particles")
    print("Sample prepositions:")
    for prep in prepositions[:5]:
        print(f"  - {prep.surface:5s} : {prep.meaning or 'N/A'}")
    print()
    
    # Show conjunctions
    conjunctions = loader.get_conjunctions()
    print(f"Conjunctions (حروف العطف): {len(conjunctions)} particles")
    print("Sample conjunctions:")
    for conj in conjunctions[:5]:
        print(f"  - {conj.surface:5s} : {conj.meaning or 'N/A'}")
    print()
    
    # Show interrogatives
    interrogatives = loader.get_particles_by_category(ParticleCategory.INTERROGATIVE)
    print(f"Interrogatives (أدوات الاستفهام): {len(interrogatives)} particles")
    print("Sample interrogatives:")
    for interr in interrogatives[:5]:
        print(f"  - {interr.surface:5s} : {interr.meaning or 'N/A'}")
    print()
    
    # Demonstrate node creation
    print("=" * 70)
    print("NODE CREATION FROM PARTICLES")
    print("=" * 70)
    print()
    
    # Get a specific preposition
    bi_particle = loader.get_particle("بِ")
    if bi_particle:
        node = loader.create_node_from_particle(bi_particle)
        if node:
            print(f"Created node for 'بِ' (bi):")
            print(f"  Type: {node.type.value}")
            print(f"  Surface: {node.surface}")
            print(f"  Governs: {node.case_mood.case.value}")
            print(f"  Can govern case: {node.can_govern_case()}")
            print(f"  Meaning: {bi_particle.meaning}")
    else:
        print("Could not find particle 'بِ'")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_particle_loader()
