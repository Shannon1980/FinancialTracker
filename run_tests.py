#!/usr/bin/env python3
"""
Test runner script for SEAS Financial Tracker
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main test runner"""
    print("🧪 SEAS Financial Tracker - Test Runner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('seas-financial-tracker.py'):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Install test dependencies
    if not run_command("pip install -r requirements-test.txt", "Installing test dependencies"):
        print("❌ Failed to install test dependencies")
        sys.exit(1)
    
    # Run linting
    print("\n🔍 Running code quality checks...")
    
    # Black formatting check
    if not run_command("black --check .", "Checking code formatting"):
        print("⚠️ Code formatting issues found. Run 'black .' to fix.")
    
    # Flake8 linting
    if not run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Running critical linting checks"):
        print("⚠️ Critical linting issues found.")
    
    # Type checking
    if not run_command("mypy . --ignore-missing-imports", "Running type checking"):
        print("⚠️ Type checking issues found.")
    
    # Security scan
    if not run_command("bandit -r . -f txt", "Running security scan"):
        print("⚠️ Security issues found.")
    
    # Run tests
    print("\n🧪 Running tests...")
    
    # Unit tests
    if not run_command("pytest tests/unit/ -v --cov=. --cov-report=term-missing", "Running unit tests"):
        print("❌ Unit tests failed")
        sys.exit(1)
    
    # Integration tests (if they exist)
    if os.path.exists('tests/integration/'):
        if not run_command("pytest tests/integration/ -v", "Running integration tests"):
            print("❌ Integration tests failed")
            sys.exit(1)
    
    # Generate coverage report
    run_command("pytest --cov=. --cov-report=html", "Generating coverage report")
    
    print("\n🎉 All tests completed successfully!")
    print("📊 Coverage report generated in htmlcov/index.html")
    print("🚀 Ready for deployment!")


if __name__ == "__main__":
    main()
