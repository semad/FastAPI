#!/usr/bin/env python3
"""
Auto Migration Script for FastAPI

This script automatically runs database migrations and creates tables
when needed.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.setup import create_tables

async def main():
    print("🚀 Auto Migration Script")
    print("📊 Creating database tables...")
    
    try:
        await create_tables()
        print("✅ Database tables created successfully!")
        print("📋 Tables created:")
        print("   - user")
        print("   - book") 
        print("   - post")
        print("   - rate_limit")
        print("   - tier")
        print("   - token_blacklist")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
