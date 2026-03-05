#!/usr/bin/env python
"""
Simple test to validate the infrastructure components.

This test validates that:
1. BaseReconstructionEngine can be imported and used
2. Harakat engine loads data correctly
3. Web app can be imported and initialized
4. Main engine can collect all engines
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_base_engine_import():
    """Test that BaseReconstructionEngine can be imported."""
    from base_reconstruction_engine import BaseReconstructionEngine
    assert BaseReconstructionEngine is not None
    print("✓ BaseReconstructionEngine imported successfully")


def test_harakat_engine():
    """Test that harakat engine works."""
    from harakat_engine import حركات, HarakatEngine
    
    # Test that the class exists
    assert حركات is not None
    assert HarakatEngine is not None
    
    # Test that it can load data
    df = حركات.make_df()
    assert len(df) > 0, "Harakat engine should load data"
    assert 'UTF-8' in df.columns, "Harakat data should have UTF-8 column"
    
    print(f"✓ Harakat engine loaded {len(df)} rows successfully")


def test_web_app():
    """Test that web app can be imported."""
    from web_app.main import app
    
    assert app is not None
    assert app.title == "Eqratech Arabic Diana Project"
    
    print(f"✓ Web app imported successfully: {app.title}")


def test_engine_collection():
    """Test that Main_engine can collect all engines."""
    from Main_engine import collect_engines
    from base_reconstruction_engine import BaseReconstructionEngine
    
    engines = collect_engines()
    
    assert len(engines) > 0, "Should collect at least one engine"
    
    # Verify all engines inherit from BaseReconstructionEngine
    for engine in engines:
        assert issubclass(engine, BaseReconstructionEngine), \
            f"{engine.__name__} should inherit from BaseReconstructionEngine"
    
    print(f"✓ Collected {len(engines)} engines, all inherit from BaseReconstructionEngine")


def test_engine_has_sheet_name():
    """Test that engines have SHEET_NAME attribute."""
    from Main_engine import collect_engines
    
    engines = collect_engines()
    
    for engine in engines[:5]:  # Test first 5
        assert hasattr(engine, 'SHEET_NAME'), \
            f"{engine.__name__} should have SHEET_NAME attribute"
        assert hasattr(engine, 'make_df'), \
            f"{engine.__name__} should have make_df method"
    
    print("✓ All tested engines have required attributes")


def main():
    """Run all tests."""
    print("Running infrastructure tests...\n")
    
    try:
        test_base_engine_import()
        test_harakat_engine()
        test_web_app()
        test_engine_collection()
        test_engine_has_sheet_name()
        
        print("\n✅ All tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
