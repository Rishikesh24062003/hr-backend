#!/usr/bin/env python3
"""
Test script to verify API structure and endpoints
"""

from app import create_app

def test_api_structure():
    """Test API structure and endpoints."""
    print("🔧 Testing API structure...")
    
    app = create_app()
    
    print("\n📋 Registered Blueprints:")
    for blueprint in app.blueprints:
        print(f"  - {blueprint}: {app.blueprints[blueprint].url_prefix}")
    
    print("\n📋 Available Routes:")
    for rule in app.url_map.iter_rules():
        print(f"  - {rule.rule} [{', '.join(rule.methods)}]")
    
    print("\n✅ API structure test complete!")

if __name__ == "__main__":
    test_api_structure() 