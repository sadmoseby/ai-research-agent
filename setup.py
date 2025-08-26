#!/usr/bin/env python3
"""
Setup script for the Lean Research Agent.
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    return run_command("pip install -r requirements.txt", "Installing dependencies")


def setup_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    template_file = Path(".env.template")

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    if template_file.exists():
        try:
            env_file.write_text(template_file.read_text())
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.template not found")
        return False


def create_directories():
    """Create necessary directories."""
    try:
        Path("proposals").mkdir(exist_ok=True)
        print("✅ Created proposals directory")
        return True
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False


def run_tests():
    """Run setup tests."""
    return run_command("python test_setup.py", "Running setup tests")


def main():
    """Main setup function."""
    print("🚀 Setting up Lean Research Agent...\n")

    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_env_file),
        ("Creating directories", create_directories),
        ("Running tests", run_tests),
    ]

    for description, step_func in steps:
        print(f"\n{description}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {description}")
            print("Please fix the error and run setup again.")
            sys.exit(1)

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env and add your OPENAI_API_KEY")
    print("2. Optionally add GITHUB_TOKEN and TAVILY_API_KEY")
    print("3. Test with: python main.py propose --idea 'your research idea'")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
