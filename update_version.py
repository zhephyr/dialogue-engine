"""
Version Update Script

Automatically updates version numbers across the project.

Usage:
    python update_version.py <new_version> [--message "Release notes"]
    python update_version.py patch              # 0.1.0 -> 0.1.1
    python update_version.py minor              # 0.1.0 -> 0.2.0
    python update_version.py major              # 0.1.0 -> 1.0.0
    python update_version.py 0.2.0              # Set specific version
"""

import sys
import re
from datetime import date
from pathlib import Path


def get_current_version():
    """Read current version from version.py"""
    version_file = Path("version.py")
    content = version_file.read_text()
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in version.py")


def parse_version(version_str):
    """Parse version string into (major, minor, patch)"""
    parts = version_str.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version_str}")
    return tuple(int(p) for p in parts)


def increment_version(current, increment_type):
    """Increment version based on type (major, minor, patch)"""
    major, minor, patch = parse_version(current)
    
    if increment_type == "major":
        return f"{major + 1}.0.0"
    elif increment_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif increment_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid increment type: {increment_type}")


def update_version_file(new_version, message=""):
    """Update version.py with new version and history entry"""
    version_file = Path("version.py")
    content = version_file.read_text()
    
    # Update version string
    content = re.sub(
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        content
    )
    
    # Add to version history if message provided
    if message:
        today = date.today().strftime("%Y-%m-%d")
        history_entry = f"{new_version} ({today})\n{'-' * (len(new_version) + 12)}\n- {message}\n\n"
        
        # Insert after VERSION_HISTORY = """
        content = re.sub(
            r'(VERSION_HISTORY\s*=\s*""")\n',
            f'\\1\n{history_entry}',
            content
        )
    
    version_file.write_text(content)
    print(f"✓ Updated version.py to {new_version}")


def update_readme(new_version):
    """Update README.md with new version"""
    readme_file = Path("README.md")
    content = readme_file.read_text()
    
    # Update version badge/header
    content = re.sub(
        r'\*\*Version \d+\.\d+\.\d+\*\*',
        f'**Version {new_version}**',
        content
    )
    
    readme_file.write_text(content)
    print(f"✓ Updated README.md to {new_version}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python update_version.py <version|major|minor|patch> [--message 'Release notes']")
        print("\nExamples:")
        print("  python update_version.py patch")
        print("  python update_version.py minor --message 'Added new features'")
        print("  python update_version.py 0.2.0 --message 'Major update'")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    version_arg = sys.argv[1]
    
    # Parse message if provided
    message = ""
    if "--message" in sys.argv:
        msg_idx = sys.argv.index("--message")
        if msg_idx + 1 < len(sys.argv):
            message = sys.argv[msg_idx + 1]
    
    # Determine new version
    if version_arg in ["major", "minor", "patch"]:
        new_version = increment_version(current_version, version_arg)
    else:
        # Validate format
        try:
            parse_version(version_arg)
            new_version = version_arg
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    print(f"New version: {new_version}")
    
    # Confirm
    response = input(f"\nUpdate version from {current_version} to {new_version}? [y/N] ")
    if response.lower() not in ["y", "yes"]:
        print("Cancelled.")
        sys.exit(0)
    
    # Perform updates
    try:
        update_version_file(new_version, message)
        update_readme(new_version)
        print(f"\n✓ Successfully updated to version {new_version}")
        print("\nDon't forget to:")
        print("  1. Commit the changes")
        print(f"  2. Tag the release: git tag v{new_version}")
        print("  3. Push with tags: git push --tags")
    except Exception as e:
        print(f"\n✗ Error updating version: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
