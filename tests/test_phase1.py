"""
Phase 1 Tests: Project Setup & Environment Configuration
"""
import pytest
import os
from pathlib import Path


def test_project_structure():
    """Test that all required directories exist"""
    base_dir = Path("e:/srp")
    
    required_dirs = [
        base_dir / "backend",
        base_dir / "frontend",
        base_dir / "agents",
        base_dir / "mcp",
        base_dir / "tests"
    ]
    
    for directory in required_dirs:
        assert directory.exists(), f"Directory {directory} does not exist"
        assert directory.is_dir(), f"{directory} is not a directory"


def test_env_example_exists():
    """Test that .env.example file exists"""
    env_example = Path("e:/srp/.env.example")
    assert env_example.exists(), ".env.example file not found"
    
    # Check it contains required keys
    with open(env_example, 'r') as f:
        content = f.read()
        assert "GEMINI_API_KEY" in content
        assert "CHROMA_PERSIST_DIR" in content


def test_requirements_file():
    """Test that requirements.txt exists and has required packages"""
    requirements_file = Path("e:/srp/requirements.txt")
    assert requirements_file.exists(), "requirements.txt not found"
    
    with open(requirements_file, 'r') as f:
        content = f.read()
        required_packages = [
            "fastapi",
            "uvicorn",
            "google-generativeai",
            "chromadb",
            "python-dotenv",
            "pillow",
            "pytest"
        ]
        
        for package in required_packages:
            assert package in content, f"Package {package} not in requirements.txt"


def test_readme_exists():
    """Test that README.md exists and has basic sections"""
    readme = Path("e:/srp/README.md")
    assert readme.exists(), "README.md not found"
    
    with open(readme, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Features" in content
        assert "Tech Stack" in content
        assert "Quick Start" in content


def test_gitignore_exists():
    """Test that .gitignore exists"""
    gitignore = Path("e:/srp/.gitignore")
    assert gitignore.exists(), ".gitignore not found"
    
    with open(gitignore, 'r') as f:
        content = f.read()
        assert "venv/" in content
        assert ".env" in content
        assert "chroma_db/" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
