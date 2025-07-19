#!/usr/bin/env python3
"""
Quick start script for NewsNinja
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_setup():
    """Check if basic setup is complete"""
    if not Path('.env').exists():
        print("❌ .env file not found. Please run 'python setup.py' first.")
        return False
    
    if not Path('audio').exists():
        Path('audio').mkdir(exist_ok=True)
    
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    try:
        subprocess.Popen([sys.executable, "backend.py"])
        print("✓ Backend started on http://localhost:1234")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting frontend...")
    time.sleep(2)  # Give backend time to start
    try:
        subprocess.run(["streamlit", "run", "frontend.py"])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")

def main():
    print("🥷 NewsNinja Quick Start")
    print("=" * 30)
    
    if not check_setup():
        return
    
    print("Starting NewsNinja application...")
    print("Backend will run on: http://localhost:1234")
    print("Frontend will open in your browser")
    print("\nPress Ctrl+C to stop both servers")
    print("-" * 30)
    
    if start_backend():
        start_frontend()

if __name__ == "__main__":
    main()