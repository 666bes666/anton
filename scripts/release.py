#!/usr/bin/env python3
"""
Release script for managing semantic versioning and automated releases.
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Command failed: {command}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    return result

def get_current_version() -> str:
    """Get the current version from git tags."""
    result = run_command("git describe --tags --abbrev=0", check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    return "v0.0.0"

def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on semantic versioning."""
    # Remove 'v' prefix if present
    version = current_version.lstrip('v')
    major, minor, patch = map(int, version.split('.'))
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"v{major}.{minor}.{patch}"

def create_release(version: str, message: str):
    """Create a new release with git tag."""
    print(f"Creating release {version}")
    
    # Create tag
    run_command(f'git tag -a {version} -m "{message}"')
    
    # Push tag
    run_command(f"git push origin {version}")
    
    print(f"✅ Release {version} created successfully!")

def main():
    parser = argparse.Parser(description="Create a new release")
    parser.add_argument(
        "bump_type", 
        choices=['major', 'minor', 'patch'],
        help="Type of version bump"
    )
    parser.add_argument(
        "--message", "-m",
        default="Automated release",
        help="Release message"
    )
    
    args = parser.parse_args()
    
    # Check if we're on main branch
    result = run_command("git branch --show-current")
    current_branch = result.stdout.strip()
    
    if current_branch != "main":
        print("❌ Releases can only be created from the main branch")
        sys.exit(1)
    
    # Check if working directory is clean
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("❌ Working directory is not clean. Please commit or stash changes.")
        sys.exit(1)
    
    # Get current version and bump it
    current_version = get_current_version()
    new_version = bump_version(current_version, args.bump_type)
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    # Confirm with user
    response = input(f"Create release {new_version}? (y/N): ")
    if response.lower() != 'y':
        print("Release cancelled")
        sys.exit(0)
    
    # Create release
    create_release(new_version, args.message)

if __name__ == "__main__":
    main()
