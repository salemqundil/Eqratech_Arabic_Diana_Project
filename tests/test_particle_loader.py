"""
Tests for Particle Loader Module
"""

import pytest
from fvafk.particle_loader import (
    ParticleLoader, ParticleCategory, ParticleData
)


class TestParticleLoader:
    """Test particle loader functionality"""
    
    @pytest.fixture
    def loader(self):
        """Create a particle loader"""
        loader = ParticleLoader()
        loader.load_all()
        return loader
    
    def test_loader_loads_particles(self, loader):
        """Test that loader loads particles"""
        assert len(loader.particles) > 0
    
    def test_get_prepositions(self, loader):
        """Test getting prepositions"""
        prepositions = loader.get_prepositions()
        assert len(prepositions) > 0
        
        # All should be prepositions
        for prep in prepositions:
            assert prep.category == ParticleCategory.PREPOSITION
    
    def test_get_conjunctions(self, loader):
        """Test getting conjunctions"""
        conjunctions = loader.get_conjunctions()
        assert len(conjunctions) > 0
        
        # All should be conjunctions
        for conj in conjunctions:
            assert conj.category == ParticleCategory.CONJUNCTION
    
    def test_get_interrogatives(self, loader):
        """Test getting interrogatives"""
        interrogatives = loader.get_particles_by_category(ParticleCategory.INTERROGATIVE)
        assert len(interrogatives) > 0
        
        # All should be interrogatives
        for interr in interrogatives:
            assert interr.category == ParticleCategory.INTERROGATIVE
    
    def test_get_specific_particle(self, loader):
        """Test getting a specific particle"""
        # Get a preposition we know exists
        bi = loader.get_particle("بِ")
        assert bi is not None
        assert bi.category == ParticleCategory.PREPOSITION
    
    def test_create_node_from_preposition(self, loader):
        """Test creating a node from a preposition particle"""
        bi = loader.get_particle("بِ")
        assert bi is not None
        
        node = loader.create_node_from_particle(bi)
        assert node is not None
        assert node.surface == "بِ"
        assert node.can_govern_case()
    
    def test_particle_has_metadata(self, loader):
        """Test that particles have metadata"""
        bi = loader.get_particle("بِ")
        assert bi is not None
        assert bi.metadata is not None
        assert 'source' in bi.metadata


class TestParticleData:
    """Test ParticleData structure"""
    
    def test_create_particle_data(self):
        """Test creating particle data"""
        particle = ParticleData(
            surface="في",
            category=ParticleCategory.PREPOSITION,
            meaning="in"
        )
        
        assert particle.surface == "في"
        assert particle.category == ParticleCategory.PREPOSITION
        assert particle.meaning == "in"
    
    def test_particle_metadata_defaults(self):
        """Test that metadata defaults to empty dict"""
        particle = ParticleData(
            surface="في",
            category=ParticleCategory.PREPOSITION
        )
        
        assert particle.metadata == {}


class TestParticleCategories:
    """Test particle category functionality"""
    
    def test_category_enum_values(self):
        """Test that all expected categories exist"""
        expected_categories = [
            'PREPOSITION',
            'CONJUNCTION',
            'INTERROGATIVE',
            'NASB',
            'NEGATIVE',
            'VERB_LIKE',
            'CONDITIONAL',
            'EXCEPTION',
            'OTHER'
        ]
        
        for cat_name in expected_categories:
            assert hasattr(ParticleCategory, cat_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
