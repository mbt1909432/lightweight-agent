#!/usr/bin/env python3
"""
Quick build script for lightweight-agent package
"""
import subprocess
import sys
import os

def main():
    """Build the package"""
    print("Building lightweight-agent package...")
    
    # Check if build is installed
    try:
        import build
    except ImportError:
        print("Error: 'build' package not found. Install it with: pip install build")
        sys.exit(1)
    
    # Run build
    result = subprocess.run([sys.executable, "-m", "build"], cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        print("\n✅ Build successful!")
        print("\nBuilt files:")
        dist_dir = os.path.join(os.path.dirname(__file__), "dist")
        if os.path.exists(dist_dir):
            for file in os.listdir(dist_dir):
                print(f"  - dist/{file}")
        print("\nTo install locally:")
        print("  pip install dist/lightweight_agent-*.whl")
        print("\nTo upload to PyPI:")
        print("  twine upload dist/*")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

