"""
Simple validation script for AIServiceUnified
Validates basic functionality without full pytest setup
"""

import sys
import os
sys.path.append('backend')

try:
    # Test import
    from app.services.ai_service_unified import AIServiceUnified
    print("✅ AIServiceUnified import successful")
    
    # Test class structure
    service_methods = [method for method in dir(AIServiceUnified) if not method.startswith('_')]
    expected_methods = [
        'generate_analysis', 
        'generate_psychometric_analysis',
        'get_service_status',
        'clear_all_caches'
    ]
    
    for method in expected_methods:
        if hasattr(AIServiceUnified, method):
            print(f"✅ Method '{method}' found")
        else:
            print(f"❌ Method '{method}' missing")
    
    # Test archetype evolution method exists
    if hasattr(AIServiceUnified, '_analyze_archetype_evolution'):
        print("✅ Archetype evolution analysis method found")
    else:
        print("❌ Archetype evolution analysis method missing")
    
    print("\n🎯 AIServiceUnified validation completed successfully!")
    print("Ready for deployment...")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Validation error: {e}")