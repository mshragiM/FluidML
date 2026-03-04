#!/usr/bin/env python3
"""
Verification script to test the RF framework installation and functionality
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} MISSING: {filepath}")
        return False

def check_directory_structure():
    """Verify directory structure"""
    print("=" * 60)
    print("CHECKING DIRECTORY STRUCTURE")
    print("=" * 60)
    
    checks = [
        ("rf_framework.py", "Main framework file"),
        ("rf_cli.py", "CLI file"),
        ("templates/firmware/rfr_common.h.j2", "Common header template"),
        ("templates/firmware/rf_trees_array.h.j2", "Trees array template"),
        ("templates/firmware/bitcast_utils.h.j2", "Bitcast utils template"),
        ("templates/firmware/scaler_constants.h.j2", "Scaler constants template"),
        ("templates/firmware/myproj_axi.cpp.j2", "AXI implementation template"),
        ("templates/firmware/myproj_core.cpp.j2", "Core implementation template"),
        ("templates/firmware/model_predict.cpp.j2", "Model predict template"),
        ("templates/test/X_test.h.j2", "X_test header template"),
        ("templates/test/rfr_tb.cpp.j2", "Testbench template"),
    ]
    
    all_exist = True
    for filepath, description in checks:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n" + "=" * 60)
    print("CHECKING DEPENDENCIES")
    print("=" * 60)
    
    required_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'sklearn': 'scikit-learn',
        'jinja2': 'jinja2',
        'yaml': 'pyyaml'
    }
    
    all_installed = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} is NOT installed")
            all_installed = False
    
    return all_installed

def check_framework_import():
    """Try to import the framework"""
    print("\n" + "=" * 60)
    print("CHECKING FRAMEWORK IMPORT")
    print("=" * 60)
    
    try:
        from rf_framework import RFFramework, RFConfig
        print("✓ RF Framework imported successfully")
        
        # Test instantiation
        config = RFConfig()
        print("✓ RFConfig instantiated successfully")
        
        framework = RFFramework()
        print("✓ RFFramework instantiated successfully")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import framework: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_conversion():
    """Test numpy to Python list conversion"""
    print("\n" + "=" * 60)
    print("TESTING DATA CONVERSION")
    print("=" * 60)
    
    try:
        import numpy as np
        
        # Test array conversion
        test_array = np.array([1.5, 2.3, 3.7])
        
        # Method used in framework
        converted = [float(x) for x in test_array]
        
        print(f"Original type: {type(test_array)}")
        print(f"Converted type: {type(converted)}")
        print(f"Element type: {type(converted[0])}")
        print(f"Is iterable: {hasattr(converted, '__iter__')}")
        
        # Test iteration
        for i, val in enumerate(converted[:3]):
            formatted = f"{val:.6f}f"
            print(f"  [{i}] {formatted}")
        
        print("✓ Data conversion works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Data conversion failed: {e}")
        return False

def test_template_rendering():
    """Test Jinja2 template rendering"""
    print("\n" + "=" * 60)
    print("TESTING TEMPLATE RENDERING")
    print("=" * 60)
    
    try:
        from jinja2 import Environment, FileSystemLoader
        
        template_dir = 'templates'
        if not Path(template_dir).exists():
            print(f"✗ Templates directory not found: {template_dir}")
            return False
        
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Test loading a simple template
        try:
            template = env.get_template('firmware/rfr_common.h.j2')
            print("✓ Template loaded successfully")
            
            # Test rendering with sample data
            context = {
                'n_features': 5,
                'n_targets': 3,
                'n_trees': 20,
                'max_depth': 6,
                'max_nodes': 128,
                'precision_type': 'float',
                'precision': 'float'
            }
            
            rendered = template.render(**context)
            
            if '#define N_FEATURES 5' in rendered:
                print("✓ Template rendered correctly")
                return True
            else:
                print("✗ Template rendering produced unexpected output")
                return False
                
        except Exception as e:
            print(f"✗ Template rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ Template system failed: {e}")
        return False

def run_full_verification():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("RF FRAMEWORK VERIFICATION")
    print("=" * 60 + "\n")
    
    results = {
        'Directory Structure': check_directory_structure(),
        'Dependencies': check_dependencies(),
        'Framework Import': check_framework_import(),
        'Data Conversion': test_data_conversion(),
        'Template Rendering': test_template_rendering()
    }
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✓ ALL CHECKS PASSED - Framework is ready to use!")
        print("=" * 60)
        print("\nYou can now run:")
        print("  python rf_cli.py quick-start --data <url> --features <cols> --targets <cols> --jinja2")
    else:
        print("\n" + "=" * 60)
        print("✗ SOME CHECKS FAILED - Please fix the issues above")
        print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = run_full_verification()
    sys.exit(0 if success else 1)
