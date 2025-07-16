from db.manager import DatabaseManager


def init_databases() -> bool:
    '''Inizializza i database e le loro configurazioni.'''

    db_manager = DatabaseManager.get_instance() # Pattern singleton per assicurarsi che solo un istanza esiste

    # Initialize schemas for all databases
    if db_manager.init_schema():
        print("✓ Database schemas initialized successfully")
        return True
    else:
        print("✗ Error initializing database schemas")
        return False


if __name__ == "__main__":
    init_databases()
