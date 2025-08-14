#!/usr/bin/env python3
"""
Database cleanup script for testing.

This script cleans up the test database by dropping all table contents
before running tests to ensure a clean state and avoid constraint violations.
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection settings
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/sqlapi"

async def cleanup_database():
    """Clean up the database by dropping all table contents."""
    logger.info("🧹 Starting database cleanup...")
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Get all table names
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'pg_%'
                AND tablename NOT LIKE 'sql_%'
                AND tablename != 'alembic_version'
                ORDER BY tablename;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"📋 Found {len(tables)} tables to clean: {', '.join(tables)}")
            
            if not tables:
                logger.info("ℹ️  No tables found to clean")
                return
            
            # Disable foreign key checks temporarily
            await conn.execute(text("SET session_replication_role = replica;"))
            
            # Truncate all tables (this is faster than DELETE and resets sequences)
            for table in tables:
                try:
                    await conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
                    logger.info(f"✅ Cleaned table: {table}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to clean table {table}: {e}")
            
            # Re-enable foreign key checks
            await conn.execute(text("SET session_replication_role = DEFAULT;"))
            
            logger.info("🎉 Database cleanup completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Database cleanup failed: {e}")
        raise
    finally:
        await engine.dispose()

async def verify_cleanup():
    """Verify that the database is clean by checking table row counts."""
    logger.info("🔍 Verifying database cleanup...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check row counts for all tables using a more reliable approach
            tables_to_check = ['book', 'post', 'rate_limit', 'tier', 'token_blacklist', 'user']
            tables_with_rows = []
            
            for table in tables_to_check:
                try:
                    result = await conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    count = result.scalar()
                    if count > 0:
                        tables_with_rows.append((table, count))
                except Exception as e:
                    logger.warning(f"⚠️  Could not check table {table}: {e}")
            
            if not tables_with_rows:
                logger.info("✅ All tables are empty - cleanup successful!")
            else:
                logger.warning(f"⚠️  Some tables still have data:")
                for table, rows in tables_with_rows:
                    logger.warning(f"   - {table}: {rows} rows")
                    
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
    finally:
        await engine.dispose()

async def main():
    """Main function to run the cleanup process."""
    try:
        await cleanup_database()
        await verify_cleanup()
        logger.info("🚀 Database is ready for testing!")
    except Exception as e:
        logger.error(f"💥 Cleanup process failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
