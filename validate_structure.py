#!/usr/bin/env python3
"""
Simple validation script that checks the RDF kernel structure without importing dependencies.
"""

import os
import ast
import sys

def check_file_exists(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} missing: {path}")
        return False

def check_python_syntax(path):
    """Check if a Python file has valid syntax."""
    try:
        with open(path, 'r') as f:
            ast.parse(f.read())
        print(f"  ✓ Valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def check_class_exists(path, class_name):
    """Check if a class is defined in a Python file."""
    try:
        with open(path, 'r') as f:
            tree = ast.parse(f.read())
        
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if class_name in classes:
            print(f"  ✓ Class {class_name} found")
            return True
        else:
            print(f"  ✗ Class {class_name} not found")
            return False
    except Exception as e:
        print(f"  ✗ Error checking class: {e}")
        return False

def check_function_exists(path, func_name):
    """Check if a function is defined in a Python file."""
    try:
        with open(path, 'r') as f:
            tree = ast.parse(f.read())
        
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if func_name in functions:
            print(f"  ✓ Function {func_name} found")
            return True
        else:
            print(f"  ✗ Function {func_name} not found")
            return False
    except Exception as e:
        print(f"  ✗ Error checking function: {e}")
        return False

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("RDF Kernel Structure Validation")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check project files
    print("1. Checking project files...")
    all_checks_passed &= check_file_exists("pyproject.toml", "Project config")
    all_checks_passed &= check_file_exists("README.md", "README")
    all_checks_passed &= check_file_exists("LICENSE", "License")
    all_checks_passed &= check_file_exists("requirements.txt", "Requirements")
    print()
    
    # Check kernel package
    print("2. Checking kernel package...")
    all_checks_passed &= check_file_exists("rdf_kernel/__init__.py", "Package init")
    all_checks_passed &= check_file_exists("rdf_kernel/__main__.py", "Package main")
    all_checks_passed &= check_file_exists("rdf_kernel/kernel.py", "Kernel module")
    all_checks_passed &= check_file_exists("rdf_kernel/magics.py", "Magics module")
    all_checks_passed &= check_file_exists("rdf_kernel/sparql_connection.py", "SPARQL connection")
    all_checks_passed &= check_file_exists("rdf_kernel/constants.py", "Constants")
    all_checks_passed &= check_file_exists("rdf_kernel/install.py", "Install module")
    print()
    
    # Check Python syntax
    print("3. Checking Python syntax...")
    for module in ["__init__.py", "__main__.py", "kernel.py", "magics.py", 
                   "sparql_connection.py", "constants.py", "install.py"]:
        path = f"rdf_kernel/{module}"
        if os.path.exists(path):
            all_checks_passed &= check_python_syntax(path)
    print()
    
    # Check key classes
    print("4. Checking key classes...")
    all_checks_passed &= check_class_exists("rdf_kernel/kernel.py", "RDFKernel")
    all_checks_passed &= check_class_exists("rdf_kernel/magics.py", "MagicProcessor")
    all_checks_passed &= check_class_exists("rdf_kernel/sparql_connection.py", "SPARQLConnection")
    print()
    
    # Check key functions
    print("5. Checking key functions...")
    all_checks_passed &= check_function_exists("rdf_kernel/kernel.py", "do_execute")
    all_checks_passed &= check_function_exists("rdf_kernel/magics.py", "process_magic")
    all_checks_passed &= check_function_exists("rdf_kernel/sparql_connection.py", "query")
    all_checks_passed &= check_function_exists("rdf_kernel/install.py", "main")
    print()
    
    # Check examples and tests
    print("6. Checking examples and tests...")
    all_checks_passed &= check_file_exists("examples.ipynb", "Example notebook")
    all_checks_passed &= check_file_exists("test_kernel.py", "Test file")
    print()
    
    # Summary
    print("=" * 60)
    if all_checks_passed:
        print("✓ All validation checks PASSED")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Install kernel: pip install -e .")
        print("  3. Register kernel: install-rdf-kernel --user")
        print("  4. Run tests: pytest test_kernel.py")
        print("  5. Start Jupyter: jupyter notebook")
        return 0
    else:
        print("✗ Some validation checks FAILED")
        return 1
    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main())
