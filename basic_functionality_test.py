#!/usr/bin/env python3
"""
Basic Functionality Test for AgenticSeek
Tests core components without requiring full dependency installation
"""

import sys
import os
import configparser

def test_config_loading():
    """Test if configuration file can be loaded"""
    print("Testing configuration loading...")
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        print("✓ Configuration loaded successfully")
        print(f"  - Provider: {config['MAIN']['provider_name']}")
        print(f"  - Model: {config['MAIN']['provider_model']}")
        print(f"  - Agent Name: {config['MAIN']['agent_name']}")
        print(f"  - Work Directory: {config['MAIN']['work_dir']}")
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_environment_setup():
    """Test if environment is properly set up"""
    print("\nTesting environment setup...")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✓ .env file exists")
    else:
        print("✗ .env file missing")
        return False
    
    # Check Python version
    python_version = sys.version_info
    print(f"  - Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major == 3 and python_version.minor >= 10:
        print("✓ Python version is compatible")
    else:
        print("⚠ Warning: Python 3.10+ is recommended")
    
    return True

def test_project_structure():
    """Test if project structure is intact"""
    print("\nTesting project structure...")
    
    required_dirs = [
        'sources',
        'sources/agents',
        'sources/tools',
        'prompts',
        'prompts/base',
        'prompts/jarvis',
        'frontend',
        'llm_server',
        'llm_router',
        'tests'
    ]
    
    required_files = [
        'cli.py',
        'api.py',
        'requirements.txt',
        'docker-compose.yml',
        'README.md'
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Missing directory: {dir_path}")
            all_good = False
    
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"✓ File exists: {file_path}")
        else:
            print(f"✗ Missing file: {file_path}")
            all_good = False
    
    return all_good

def test_imports():
    """Test if basic imports work"""
    print("\nTesting basic imports...")
    
    try:
        # Test imports that don't require external dependencies
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # These should work without external deps
        from sources.schemas import QueryRequest, QueryResponse
        print("✓ Schema imports successful")
        
        from sources.logger import Logger
        print("✓ Logger import successful")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AgenticSeek Basic Functionality Test")
    print("=" * 60)
    
    tests = [
        test_config_loading,
        test_environment_setup,
        test_project_structure,
        test_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  - Total tests: {len(results)}")
    print(f"  - Passed: {sum(results)}")
    print(f"  - Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✓ All basic tests passed!")
        print("\nNext steps to run AgenticSeek:")
        print("1. Install Python 3.10 (recommended)")
        print("2. Create virtual environment")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Run installation script: ./install.sh")
        print("5. Start Docker services: sudo ./start_services.sh")
        print("6. Start LLM provider (e.g., ollama serve)")
        print("7. Run: python3 cli.py or python3 api.py")
    else:
        print("\n✗ Some tests failed. Please fix the issues before running.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()