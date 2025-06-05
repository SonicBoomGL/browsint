from db.manager import DatabaseManager


def init_databases() -> bool:
    # Get database manager instance
    db_manager = DatabaseManager.get_instance()

    # Initialize schemas for all databases
    if db_manager.init_schema():
        print("✓ Database schemas initialized successfully")
        return True
    else:
        print("✗ Error initializing database schemas")
        return False


if __name__ == "__main__":
    init_databases()
