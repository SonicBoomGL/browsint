"""
Modulo: Database Schema (db/schema.py)
Definizione degli schemi (strutture delle tabelle) per tutti i database dell'applicazione.

Ogni chiave del dizionario SCHEMAS corrisponde al nome logico di un database,
e il valore associato è una stringa contenente le istruzioni SQL CREATE TABLE
separate da punto e virgola (;).
"""

SCHEMAS = {
    "websites": '''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            status_code INTEGER,
            content_length INTEGER,
            content_type TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id INTEGER NOT NULL,
            href TEXT NOT NULL,
            anchor_text TEXT,
            is_internal BOOLEAN NOT NULL DEFAULT 1,
            is_followed BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
            UNIQUE(page_id, href)
        );

        CREATE TABLE IF NOT EXISTS meta_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id INTEGER NOT NULL,
            meta_name TEXT NOT NULL,
            meta_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
            UNIQUE(page_id, meta_name)
        );

        CREATE TABLE IF NOT EXISTS robots_txt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            content TEXT,
            crawl_delay FLOAT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE,
            UNIQUE(website_id)
        );

        CREATE TABLE IF NOT EXISTS robots_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robots_txt_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            allow BOOLEAN NOT NULL DEFAULT 0,
            is_sensitive BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (robots_txt_id) REFERENCES robots_txt(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS robots_sitemaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robots_txt_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (robots_txt_id) REFERENCES robots_txt(id) ON DELETE CASCADE,
            UNIQUE(robots_txt_id, url)
        );
    ''',
    "osint": '''
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT CHECK(type IN ('company', 'person', 'domain')) NOT NULL,
            name TEXT NOT NULL,
            domain TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS domain_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            registrar TEXT,
            registration_date TIMESTAMP,
            expiration_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE,
            UNIQUE(entity_id)
        );

        CREATE TABLE IF NOT EXISTS osint_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            raw_data TEXT,
            extracted_fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE,
            UNIQUE(entity_id, source)
        );

        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            email TEXT,
            phone TEXT,
            source TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE,
            UNIQUE(entity_id, email, phone)
        );
    '''
}