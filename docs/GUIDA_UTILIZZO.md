## a. Oggetto

Browsint è un toolkit Python open source per l'OSINT (Open Source Intelligence), progettato per la raccolta e l'analisi automatizzata di informazioni da pagine web e fonti pubbliche. Il tool è in grado di investigare in profondità su domini, indirizzi email e, per estensione, su entità correlate, aggregando dati da varie piattaforme e servizi esterni.

---
## b. Scopo

Lo scopo principale di Browsint è fornire un'interfaccia a riga di comando (CLI) completa e intuitiva per eseguire una vasta gamma di operazioni di intelligence open source. Questo include funzionalità avanzate di download e crawling ricorsivo di siti web, uno scraping mirato per l'estrazione dettagliata di dati da singole pagine, e un'investigazione OSINT strutturata su domini e email attraverso l'integrazione con API di terze parti (es. WHOIS, DNS, Shodan, Hunter.io, Have I Been Pwned). Il tool offre inoltre una gestione centralizzata del database SQLite per la persistenza dei dati raccolti e delle API keys configurate, e la possibilità di esportare i report delle analisi in diversi formati come JSON, HTML e PDF per una facile consultazione e condivisione.

---
## c. Analisi Tecnica 

Browsint è un'applicazione Python strutturata con un'architettura modulare e a strati, basata su classi e funzioni per gestire le diverse funzionalità in modo efficiente e manutenibile.

#### Librerie e Moduli Principali:

- **`requests`**: Utilizzata estensivamente dal `WebFetcher` (`scraper/fetcher.py`) per effettuare richieste HTTP/HTTPS. Gestisce timeout, retries e la configurazione di `User-Agent`. La classe `FetchResponse` incapsula la risposta completa (status code, content, headers, URL).
    
- **`bs4` (BeautifulSoup)**: Fondamentale per il parsing del contenuto HTML. La classe `WebParser` (`scraper/parser.py`) utilizza BeautifulSoup per navigare il DOM ed estrarre elementi specifici, come link (`LinkInfo`), titoli, descrizioni e altri metadati, inclusa la gestione di regole di estrazione personalizzate (`_apply_extraction_rule`).
    
- **`sqlite3`**: Il modulo integrato di Python per interagire con i database SQLite. È il pilastro del `DatabaseManager` (`db/manager.py`), che gestisce le connessioni, le transazioni e le operazioni CRUD sui database `websites.db` e `osint.db`.
    
- **`colorama`**: Utilizzata in tutti i moduli CLI (`cli/menus/*.py`, `cli/utils.py`) per la formattazione dell'output della console con colori e stili, migliorando la leggibilità.
    
- **`pathlib`**: Gestisce i percorsi dei file e delle directory in modo efficiente e cross-platform, usata per l'organizzazione di database (`data/db/`) e output (`data/output/`).
    
- **`logging`**: Implementa un sistema di logging su più livelli (`INFO`, `WARNING`, `ERROR`, `DEBUG`) per tracciare il flusso dell'applicazione e facilitare il debug. Configurato in `main.py` e utilizzato in ogni modulo per reportistica interna.
    
- **`dotenv`**: Carica variabili d'ambiente da un file `.env` per la gestione sicura delle API keys (`scraper_cli.py`).
    
- **`validators`**: Per la validazione di URL e domini, essenziale per garantire la correttezza degli input dell'utente (`scraper_cli.py`, `validators.py`).
    
- **`tabulate`**: Per una presentazione chiara e formattata dei dati tabellari nella console CLI (es. `osint_menu.py`, `scraping_menu.py`).
    
- **`dnspython`**: Esegue query DNS per recuperare record (A, MX, NS, TXT) (`scraper/utils/clients.py`).
    
- **`python-whois`**: Recupera informazioni WHOIS sui domini (`scraper/utils/clients.py`).
    
- **`shodan`**: API wrapper per interagire con Shodan per la scoperta di servizi su IP/domini (`scraper/utils/clients.py`).
    
- **`phonenumbers`**: Per il parsing, la validazione e la formattazione dei numeri di telefono (`scraper/utils/extractors.py`).
    
- **`requests_cache`**: Integrata nel `WebFetcher` per il caching delle risposte HTTP, riducendo le richieste ridondanti e migliorando le performance.
    
- **`reportlab` (implicito tramite `formatters.py`)**: Utilizzata per la generazione di report PDF complessi (`create_pdf_domain_report`, `create_pdf_page_report` in `scraper/utils/formatters.py`).
    

---
#### Architettura e Flow (Relazione tra i moduli):

1. **Avvio (`main.py`):** Il punto di ingresso inizializza l'ambiente (logging, `colorama`) e crea un'istanza di `ScraperCLI`.
    
2. **Orchestratore CLI (`cli/scraper_cli.py`):** Questa classe è il cuore del controllo. Nel suo costruttore (`__init__`), istanzia e inietta le dipendenze principali:
    
    - `WebFetcher` (per richieste HTTP).
        
    - `WebParser` (per l'analisi HTML).
        
    - `DatabaseManager` (per la persistenza dei dati, tramite `DatabaseManager.get_instance()` per il Singleton).
        
    - `OSINTExtractor` (per le operazioni OSINT).
        
    - Crawler (per il crawling ricorsivo).
        
        Quindi, ScraperCLI gestisce il menu principale, delegando la logica specifica ai vari sottomenu (es. _download_menu, _osint_menu, _options_menu).
        
3. **Recupero Dati (`scraper/fetcher.py`):** Il `WebFetcher` è responsabile di ottenere il contenuto di una URL. Implementa la "politeness" (`_respect_politeness`) rispettando i `Crawl-Delay` da `robots.txt` e gestisce i tentativi di download in caso di errori (`download_page`, `download_full_page`). Il caching delle risposte HTTP è implementato per ottimizzare le performance.
    
4. **Parsing HTML (`scraper/parser.py`):** Il `WebParser` riceve il contenuto HTML dal `WebFetcher` e lo analizza usando BeautifulSoup. Estrae link, titoli, descrizioni e altri dati strutturati.
    
5. **Crawling (`scraper/crawler.py`):** Il `Crawler` gestisce la logica di navigazione ricorsiva. Mantiene una `deque` di URL da visitare, rispetta le direttive di `robots.txt` (`RobotsParser`), e salva i dati estratti (pagine, link, entità) nel `DatabaseManager`. Integra l'estrazione di email, telefoni (`extract_emails`, `extract_phone_numbers` in `scraper/utils/extractors.py`) e il rilevamento di tecnologie web (`web_analysis.py`).
    
6. **Gestione Database (`db/manager.py` e `db/schema.py`):** Il `DatabaseManager` è un Singleton che fornisce un'interfaccia centralizzata per interagire con i database SQLite. Le definizioni delle tabelle sono in `db/schema.py`. Ogni operazione sul database è incapsulata in una transazione (`transaction` context manager) per garantire l'atomicità e l'integrità dei dati.
    
7. **Estrazione OSINT (`scraper/extractors/osint_extractor.py`):** Questo modulo orchestra le chiamate a servizi esterni (WHOIS, DNS, Shodan, Hunter.io, HIBP) tramite `scraper/utils/clients.py` e `scraper/utils/osint_sources.py`. Processa i dati grezzi ricevuti e li struttura (`data_processing.py`) prima di persisterli nel database OSINT.
    
8. **Interfaccia Utente (`cli/menus/*.py`):** I moduli `download_menu.py`, `osint_menu.py`, `scraping_menu.py` e `db_menu.py` gestiscono l'interazione con l'utente, visualizzando i menu, raccogliendo gli input e invocando i metodi appropriati sull'istanza di `ScraperCLI`.
    

---
#### Snippet di codice particolarmente importanti:

- **Singleton del DatabaseManager (`db/manager.py`):**
    
    
    ```python
    class DatabaseManager:
        _instance: Optional["DatabaseManager"] = None
    
        @classmethod
        def get_instance(cls, db_path: str | None = None) -> "DatabaseManager":
            if cls._instance is None:
                cls._instance = cls(db_path)
            return cls._instance
    ```
    
    Questo garantisce che tutte le parti dell'applicazione utilizzino la stessa connessione ai database, evitando problemi di concorrenza e gestione delle risorse.

---

- **Transazioni Database (`db/manager.py`):**
    
    
    ```python
    @contextmanager
    def transaction(self, db_name: str) -> Iterator[sqlite3.Cursor]:
        conn = self._connections.get(db_name)
        if not conn:
            raise ValueError(f"No active connection for database: {db_name}")
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
            logger.debug(f"Transaction committed for {db_name}.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back for {db_name} due to: {e}", exc_info=True)
            raise
    ```
    
    L'uso di `@contextmanager` con `yield` permette di definire un blocco `with` che gestisce automaticamente il `COMMIT` o `ROLLBACK` delle transazioni, fondamentale per l'integrità dei dati in caso di errori.

---


- **Politiche di Politeness nel WebFetcher (`scraper/fetcher.py`):**
    
    
    ```python
    class WebFetcher:
        # ...
        def _respect_politeness(self):
            # ...
            # Logic to parse robots.txt and apply crawl delay
            # ...
            if self.robots_data and self.robots_data.crawl_delay > 0:
                sleep_time = self.robots_data.crawl_delay + random.uniform(0.5, 2.0)
                logger.info(f"Respecting crawl delay, sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
            # ...
    ```
    
    Questo frammento evidenzia l'impegno a non sovraccaricare i server web, rispettando il `Crawl-Delay` specificato nel file `robots.txt` del sito, migliorando l'etica e la stabilità del crawling.
    


## d. Commenti su particolari procedure implementate

1. **Gestione Caching HTTP** (scraper/fetcher.py):
    
    Il WebFetcher implementa un robusto sistema di caching delle risposte HTTP. Questo riduce significativamente il numero di richieste effettive verso i server web per risorse già scaricate, accelerando le operazioni di crawling e scraping, riducendo il carico sui server target e minimizzando il rischio di essere bloccati. Il caching è gestito in modo persistente su disco, consentendo di riprendere le operazioni senza dover riscaricare tutti i contenuti.

---
   
2. **Validazione e Pulizia Input** (scraper/utils/validators.py):
    
    Sono implementate funzioni specifiche come validate_domain che non solo verificano la validità sintattica di domini e URL, ma li puliscono anche da prefissi http(s)://, www., e sottocartelle per garantire che i dati siano uniformi prima di essere processati o memorizzati. Questo previene duplicati e incoerenze nel database.

---

3. **Parsing di robots.txt e Direttive di Crawling** (scraper/utils/robots_parser.py):
    
    Il Crawler utilizza un RobotsParser dedicato che interpreta le direttive Allow e Disallow presenti nei file robots.txt. Questo assicura che il crawler rispetti le politiche di accesso dei siti web, evitando di accedere a sezioni private o non autorizzate e prevenendo blocchi da parte dei server. Vengono anche identificati e segnalati percorsi potenzialmente "sensibili" (is_sensitive in RobotsRule).

---
   
4. **Serializzazione JSON Sicura** (cli/utils.py):
    
    La funzione json_serial è cruciale per la gestione dell'esportazione dei dati in formato JSON. Estende il comportamento di serializzazione predefinito di json.dump, permettendo di convertire tipi di dati non serializzabili di default (come oggetti datetime e set) in formati compatibili con JSON (ISO format per le date, liste per i set). Questo garantisce che tutti i dati del database possano essere correttamente esportati.

---

5. **Estrazione e Filtraggio Intelligente di Contatti** (scraper/utils/extractors.py):
    
    Le funzioni extract_emails e extract_phone_numbers non si limitano a trovare pattern regex, ma incorporano logiche di filtraggio per ridurre i falsi positivi (es. escludendo numeri che sembrano date, IP, o sequenze numeriche semplici). Per le email, viene considerata anche la relazione con il dominio per distinguere email interne/esterne (filter_emails). Per i numeri di telefono, phonenumbers viene usato per una validazione robusta basata su standard internazionali.

---

5. **Reportistica Dinamica** (scraper/utils/formatters.py):
    
    Il modulo formatters.py offre funzioni per generare report in diversi formati (testo per console, HTML e PDF). Questo include la formattazione avanzata per i dati OSINT di dominio (format_domain_osint_report, formal_html_report_domain, create_pdf_domain_report) e per le analisi di pagina (format_page_analysis_report, formal_html_report_page, create_pdf_page_report), rendendo i risultati dell'analisi facilmente condivisibili e leggibili.
    

---

## e. Utilizzo e Report

Per avviare l'applicazione, è necessario eseguire il file `main.py` dalla riga di comando.

```bash
python3 src/main.py
```

Al primo avvio, o quando è necessario ricreare la struttura del database, è **fortemente consigliato** eseguire lo script di inizializzazione del database:

Se si dovessero verificare problemi con la creazione dei database è possibile utilizzare il seguente codice per creare unicamente la struttura dei db:

```bash
python3 src/init_db.py
```



L'applicazione presenterà un menu principale interattivo che guiderà l'utente attraverso le diverse funzionalità. Seguire le istruzioni a schermo per navigare tra le opzioni.

### Input richiesti

Il tool richiederà all'utente vari input a seconda della funzionalità scelta:

- **URL/Dominio:** Per operazioni di download, crawling, scraping e analisi OSINT di domini. La validazione automatica (`_get_validated_url_input` in `scraper_cli.py`) garantirà la correttezza del formato.
    
- **Profondità di Crawling:** Un numero intero che indica quanti livelli di link il crawler deve seguire a partire dall'URL iniziale (`_get_depth_input` in `scraper_cli.py`).
    
- **Percorso File:** Per il download multiplo da una lista di URL o per il ripristino di backup.
    
- **API Keys:** Per le funzionalità OSINT che si basano su servizi esterni (Hunter.io, Shodan, ecc.), il tool richiederà le API keys pertinenti. Queste possono essere inserite al momento o configurate stabilmente tramite il menu "Gestione Database e API", dove verranno salvate nel file `.env`.
    
- **Conferme:** Per azioni distruttive (es. eliminazione database, svuotamento tabelle), il tool richiederà una conferma esplicita (`confirm_action` in `cli/utils.py`).

<div style="page-break-before: always;"></div>
### Output attesi e Report Generati

I dati raccolti e le analisi generate da Browsint vengono salvati in una struttura di directory organizzata sotto la cartella `data/output/`, e i database sotto `data/db/`:

- **`data/db/`**: Contiene i file del database SQLite (`websites.db` e `osint.db`) che persistono tutti i dati strutturati raccolti.
    
- **`data/output/downloaded_pages/`**: All'interno, troverai sottocartelle per ogni dominio scansionato (es. `example.com/`), contenenti i file HTML grezzi di tutte le pagine scaricate.
    
- **`data/output/osint_exports/`**: Qui sono salvati i report dettagliati delle analisi OSINT effettuate su domini, indirizzi email o username. I report sono disponibili in formato JSON o HTML, fornendo una panoramica completa delle informazioni raccolte dalle varie fonti esterne.
    
- **`data/output/osint_usernames/`**: Questa directory accoglie i file `.txt` generati dalla libreria Sherlock in seguito alla ricerca di username su piattaforme social.
    
- **`data/output/pdf_reports/`**: Contiene le versioni PDF dei risultati delle analisi OSINT e delle analisi di scraping, formattate per una facile lettura, stampa e condivisione.
    

Ogni operazione CLI visualizzerà anche un riepilogo testuale direttamente nella console, fornendo feedback immediato sull'andamento e sui risultati delle operazioni.

---
## f. Conclusioni

Browsint è un tool OSINT versatile e tecnicamente robusto che offre un'ampia gamma di funzionalità per la raccolta e l'analisi di informazioni da fonti pubbliche. L'interfaccia a riga di comando, con la sua chiara struttura a menu e l'uso di `colorama` per un output leggibile, lo rende accessibile anche a utenti non esperti, pur mantenendo la profondità tecnica e la granularità necessarie per operazioni di intelligence più complesse. La gestione integrata delle API keys, la persistenza dei dati tramite SQLite e la capacità di esportare i risultati in vari formati ne fanno un toolkit completo e potente, adatto sia a professionisti della sicurezza e dell'OSINT che a semplici appassionati. La sua architettura modulare, con una chiara separazione delle responsabilità tra fetcher, parser, crawler, estrattori OSINT e gestore del database, ne facilita l'estensione, la manutenibilità e il testing.