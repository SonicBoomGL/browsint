# Test che i database siano creati correttamente, contengano le tabelle corrette e vengano ripuliti.

import os
import sqlite3
import sys

import pytest

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.db import DatabaseConnectionError, DatabaseSchemaError
from src.db.manager import DatabaseManager
from src.db.schema import SCHEMAS

# Percorso temporaneo per i database di test
TEST_DB_PATH = "/tmp/test_database.db"


@pytest.fixture
def db_manager():
    """Fixture per creare e distruggere un DatabaseManager per i test."""
    # Inizializza il DatabaseManager con un database temporaneo
    manager = DatabaseManager(TEST_DB_PATH)
    yield manager  # Ritorna il manager per i test
    # Cleanup: Rimuove il database dopo il test
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_database_creation_and_schema(db_manager):
    """Testa la creazione del database e la verifica degli schemi."""
    # Assicura che il database venga creato senza errori
    try:
        db_manager.create_database(SCHEMAS)
    except (DatabaseConnectionError, DatabaseSchemaError) as e:
        pytest.fail(f"Errore durante la creazione del database: {e}")

    # Verifica che il file del database sia stato creato
    assert os.path.exists(TEST_DB_PATH), "Il file del database non è stato creato."

    # Connessione al database per verificare le tabelle
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # Verifica che tutte le tabelle definite negli schemi siano presenti
    for table_name in SCHEMAS.keys():
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        result = cursor.fetchone()
        assert result is not None, f"La tabella '{table_name}' non è stata creata."

    conn.close()


def test_database_cleanup(db_manager):
    """Testa la pulizia del database."""
    # Crea il database
    db_manager.create_database(SCHEMAS)

    # Assicura che il file del database esista
    assert os.path.exists(TEST_DB_PATH), "Il file del database non è stato creato."

    # Rimuove il database
    db_manager.cleanup()

    # Verifica che il file del database sia stato rimosso
    assert not os.path.exists(TEST_DB_PATH), "Il file del database non è stato rimosso."
