"""
Quick script to test Supabase database connection
"""
from sqlalchemy import create_engine, text
from config.settings import settings

def test_connection():
    """Test database connection"""
    print(f"Testing connection to: {settings.DATABASE_URL.split('@')[1]}")

    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)

        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📊 PostgreSQL version: {version}")

            # Check existing tables
            result = connection.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()

            if tables:
                print(f"\n📋 Existing tables ({len(tables)}):")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("\n📋 No tables found yet (ready for migration)")

            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
