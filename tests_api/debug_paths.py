"""Debug script to check path resolution for .env file."""

from pathlib import Path

print("Debugging path resolution...")
print(f"Current working directory: {Path.cwd()}")
print(f"__file__ location: {__file__}")
print(f"tests_api directory: {Path(__file__).parent}")
print(f"Parent of tests_api: {Path(__file__).parent.parent}")
print(f"src directory: {Path(__file__).parent.parent / 'src'}")
print(f".env file path: {Path(__file__).parent.parent / 'src' / '.env'}")

# Check if files exist
paths_to_check = [
    Path(__file__).parent.parent / "src" / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent / ".env",
    Path.cwd() / ".env",
    Path.cwd() / "src" / ".env"
]

print("\nChecking if paths exist:")
for path in paths_to_check:
    exists = path.exists()
    print(f"  {path}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
    if exists:
        print(f"    Size: {path.stat().st_size} bytes")
