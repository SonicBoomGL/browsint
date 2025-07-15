
---
## a. Oggetto

Browsint è un toolkit python dedicato all' OSINT (Open Source Intelligence), progettato per la raccolta e l'analisi di informazioni da diverse fonti pubbliche. Il tool è in grado di investigare su persone, domini, siti web ed entità correlate.

---
## b. Scopo

Lo scopo principale di Browsint è fornire un'interfaccia a riga di comando (CLI) per eseguire varie operazioni di intelligence open source, tra cui il download e il crawling di siti web, lo scraping OSINT per l'estrazione di dati e l'investigazione manuale di domini, email e username. 
Il tool permette inoltre la gestione del database e delle API keys, e la possibilità di salvare i report in diversi formati come JSON, HTML e PDF.

---
## c. Analisi Tecnica

Browsint è un'applicazione Python strutturata con un'architettura modulare, basata su classi e funzioni per gestire le diverse funzionalità.

**Librerie e Moduli Principali:**

- **`requests`**: Essenziale per effettuare richieste HTTP e scaricare il contenuto delle pagine web da analizzare.
    
- **`bs4` (BeautifulSoup)**: Fondamentale per il parsing del contenuto HTML delle pagine web, consentendo l'estrazione strutturata dei dati.
    
- **`colorama`**: Utilizzata per la formattazione dell'output della console con colori e stili, migliorando notevolmente la leggibilità dell'interfaccia CLI.
    
- **`pathlib`**: Gestisce i percorsi dei file e delle directory in modo efficiente e orientato agli oggetti, garantendo la compatibilità tra i diversi sistemi operativi per il salvataggio dei dati.
    
- **`logging`**: Impiegata per la gestione dei log dell'applicazione, fornendo un meccanismo robusto per tracciare eventi, debug e errori.
    
- **`dotenv`**: Cruciale per caricare e gestire in sicurezza le variabili d'ambiente, in particolare le API keys necessarie per l'interazione con servizi esterni.
    
- **`tabulate`**: Permette la formattazione tabellare dei dati nell'output della console, rendendo i risultati delle analisi più leggibili e organizzati.
    
- **`urllib.parse`**: Fondamentale per la manipolazione e il parsing degli URL, necessaria per il crawling e l'analisi dei link.
    
- **`validators`**: Impiegata per la validazione di input come URL ed email, assicurando che i dati forniti dall'utente siano nel formato corretto prima di essere elaborati.
    
- **`DatabaseManager` (modulo personalizzato `db.manager`)**: Gestisce tutte le interazioni con il database interno (probabilmente SQLite), occupandosi della persistenza dei dati raccolti, delle query e delle operazioni di backup.
    
- **`WebFetcher` (modulo personalizzato `scraper.fetcher`)**: Responsabile del recupero del contenuto delle pagine web, gestendo la cache, i ritardi di richiesta e la riprova in caso di errori.
    
- **`WebParser` (modulo personalizzato `scraper.parser`)**: Si occupa dell'analisi del contenuto HTML grezzo per estrarre informazioni chiave come link, metadati, testo e altri elementi strutturati.
    
- **`OSINTExtractor` (modulo personalizzato `scraper.extractors.osint_extractor`)**: L'orchestratore centrale per l'estrazione e l'elaborazione dei dati OSINT da diverse fonti, coordinando le chiamate a servizi esterni e l'aggregazione delle informazioni.
    
- **`Crawler` (modulo personalizzato `scraper.crawler`)**: Implementa la logica di navigazione ricorsiva dei siti web, gestendo la coda di URL da visitare, la profondità di crawling e l'integrazione con l'estrazione OSINT.
    
- **Moduli Utility (`scraper.utils.*`)**: Un insieme di moduli che contengono funzioni di supporto per il trattamento dei dati (`data_processing`), l'estrazione di pattern specifici (`extractors` per email/telefoni), l'interazione con client API esterni (`clients`), la formattazione dei report (`formatters`), l'analisi web (es. rilevamento tecnologie in `web_analysis`) e il parsing di `robots.txt` (`robots_parser`).   

**Struttura del Codice:**

L'applicazione è orchestrata dalla classe `ScraperCLI` (in scraper_cli.py), che funge da interfaccia principale a riga di comando. Questa classe inizializza tutti i componenti necessari (gestori di database, estrattori OSINT, fetcher web, parser e crawler) e gestisce il flusso di esecuzione attraverso un menu interattivo.

I menu specifici (Download, OSINT, Scraping, Database) sono implementati in moduli separati (`download_menu.py`, `osint_menu.py`, `scraping_menu.py`, `db_menu.py`), ognuno con le proprie funzioni per visualizzare le opzioni e gestire le scelte dell'utente. Questo approccio modulare facilita la manutenzione e l'espansione del codice.

**Gestione delle API Keys:**

Le API keys sono caricate da variabili d'ambiente e da un file .env (best practice). 
È presente un menu dedicato alla gestione delle API keys che permette di visualizzarle, aggiungerle/aggiornarle e rimuoverle in modo interattivo.

---
## d. Eventuali Commenti su Particolari Procedure Implementate

Alcune caratteristiche chiave:

**SCALABILITA'**

- **Modularità dei Menu**: La chiara separazione delle funzionalità in moduli di menu distinti (`download_menu`, `osint_menu`, `db_menu`, `scraping_menu`) rende il codice ben organizzato e facile da navigare. Ogni modulo si occupa della logica di visualizzazione e gestione delle scelte relative alla propria area.

- **Modularità delle funzioni tecniche:** Organizzazione del progetto modulare con classi e file dedicati a specifiche responsabilità.
  La divisione principale riguarda l'utilizzo di funzioni specifiche divise in cartelle utils/ ai moduli principali come `OSINTExtractor` e `ScraperCLI`.
  Questa suddivisione permette un facile aggiornamento, debug e l'aggiunta di nuove funzionalità senza impattare l'intera codebase, favorendo la scalabilità. Ogni componente è progettato per essere quanto più indipendente possibile.


**SALVATAGGIO DATI**

- **Gestione delle Directory**: La funzione `setup` nella classe `ScraperCLI` si occupa della creazione automatica delle directory necessarie per l'archiviazione dei dati (es. `url_downloaded`, `site_analysis`, `osint_exports`, `pdf_reports`), garantendo che l'applicazione abbia i percorsi di output pronti all'uso.
    
- **Persistenza dei Dati**: L'utilizzo di un `DatabaseManager` permette la persistenza dei dati raccolti, il che è fondamentale per applicazioni OSINT che gestiscono grandi volumi di informazioni. Le opzioni di backup e visualizzazione dei record del database sono pensate per l'utilizzo .


**VISUALIZZAZIONE DATI**

- **Formattazione Output**: L'uso di `colorama` per colorare l'output della console e `tabulate` per presentare i dati in tabelle strutturate permette una chiara visione dei risultati già dal termine della scansione tramite la CLI. 
    
- **Esportazione Report**: La possibilità di esportare i risultati delle analisi in formati comuni come JSON, HTML e PDF permette la revisione dei dati in qualunque momento e la presentazione di un risultato formale come possibile prova di vulnerabilità esistenti.


---
## e. Indicazioni su Come e Cosa Dare in Input e Cosa Aspettarsi in Output


#### **INPUT**

- **Scelte di Menu**: L'utente deve inserire numeri corrispondenti alle opzioni del menu visualizzate.
    
- **URL**: Richiesto per il download di singole pagine, il crawling di siti web e l'analisi della struttura delle pagine.
    
- **Dominio/IP**: Richiesto per l'analisi OSINT di domini.
    
- **Indirizzo Email**: Richiesto per la profilazione di indirizzi email.
    
- **Username**: Richiesto per la ricerca di username sui social media.
    
- **Nomi File**: Richiesti per il download multiplo da un file di URL o per specificare il nome del file di output.
    
- **API Keys**: Richieste durante la configurazione per i servizi esterni (Hunter.io, Shodan, HaveIBeenPwned, VirusTotal, SecurityTrails, WhoisXMLAPI).
    
- **Profondità Crawl**: Un valore numerico intero per definire la profondità massima durante il crawling.
    

---
#### **OUTPUT**

- **Contenuto Pagine Web**: Il download di singole pagine o il crawling produce il contenuto HTML delle pagine scaricate, salvato in directory specifiche.
    
- **Report OSINT**: Le analisi di domini, email o username generano profili dettagliati con informazioni raccolte da varie fonti.
    
- **Statistiche di Crawling**: Dopo un'operazione di crawling, vengono visualizzate statistiche di base come il numero di URL visitati e pagine salvate.
    
- **Analisi Struttura Pagina**: L'analisi di una singola pagina web estrae dati base, inclusi email, numeri di telefono e tecnologie utilizzate dal sito.
    
- **Report Esportati**: I risultati delle analisi e dei profili possono essere esportati in formato JSON, HTML e PDF, salvati in directory dedicate.
    
- **Informazioni Database**: Il menu del database visualizza informazioni sulla dimensione dei database e le tabelle presenti, con il conteggio delle righe.
    
- **API Keys Configurate**: È possibile visualizzare un elenco delle API keys attualmente configurate nel sistema.
    
- **Messaggi di Stato**: L'applicazione fornisce feedback costante tramite messaggi a console (colorati per indicare successo, errore o avviso) sullo stato delle operazioni in corso.
    

---
#### **POSSIBILI WORKFLOW:**

1. **Configurazione Iniziale e Gestione API Keys:**
    
    - **Input**: Avviare `main.py`, navigare nel menu "Opzioni di Sistema" (Opzione 4 dal menu principale), quindi scegliere "Gestisci API Keys" (Opzione 5 dal sottomenu). L'utente può scegliere di visualizzare, aggiungere/aggiornare o rimuovere API keys inserendo i valori richiesti.
    - **Output**: Conferma della corretta configurazione o rimozione delle API keys, visualizzazione dello stato attuale delle keys.
2. **Download di una Singola Pagina Web:**
    
    - **Input**: Dal menu principale, selezionare "Crawl & Download" (Opzione 1), poi "Download singola pagina web" (Opzione 1). L'utente dovrà fornire l'URL della pagina desiderata.
        
    - **Output**: Messaggio di conferma del download e percorso del file HTML salvato (e potenzialmente di un file JSON con la struttura della pagina) nella directory `url_downloaded`.
        
3. **Crawling di un Sito Web con Analisi OSINT Integrata:**
    
    - **Input**: Dal menu principale, selezionare "Crawl & Download" (Opzione 1), poi "Crawl e download struttura sito web" (Opzione 3). Fornire l'URL di partenza e la profondità di crawling desiderata. Il sistema chiederà se si vuole attivare l'analisi OSINT durante il crawling.
        
    - **Output**: Statistiche di crawling (URLs visitati, pagine salvate), progressi in tempo reale, eventuali risultati OSINT estratti durante il crawling (es. profili social rilevati, email). Tutti i file HTML scaricati verranno salvati nella directory `site_analysis`.
        
4. **Analisi OSINT di un Dominio:**
    
    - **Input**: Dal menu principale, selezionare "Investigazione OSINT" (Opzione 2), poi "Analisi OSINT Dominio/IP" (Opzione 1). Inserire il dominio o l'indirizzo IP da analizzare.
        
    - **Output**: Un report testuale dettagliato visualizzato a console con informazioni WHOIS, DNS, dati Shodan (se configurato), ecc. Verrà data la possibilità di esportare questo report in JSON, HTML o PDF, salvati nella directory `osint_exports` o `pdf_reports`.
        
5. **Analisi Strutturale di una Pagina Web (Scraping):**
    
    - **Input**: Dal menu principale, selezionare "OSINT Scraping" (Opzione 3), poi "Analizza struttura singola pagina web" (Opzione 1). Fornire l'URL della pagina.
        
    - **Output**: Una lista strutturata di elementi estratti dalla pagina (email, numeri di telefono, link interni/esterni, tecnologie usate), visualizzata a console. Anche qui, sarà possibile esportare i dati in vari formati.


---
#### **CARTELLE DI OUTPUT**

Browsint organizza l'output in diverse directory per mantenere i risultati chiari e accessibili. Tutte le cartelle di output vengono create automaticamente nella directory data/ nella radice del progetto al primo avvio, se non già esistenti.

- **`url_downloaded/`**: Questa cartella contiene i file HTML delle singole pagine web scaricate. Se l'opzione è stata selezionata, troverai anche file JSON che rappresentano la struttura e i dati principali estratti dalla pagina, come link, metadati e contenuto testuale.
	
- **`downloaded_tree/`**: stesso contenuto di url_downloaded/ , ma generato in seguito al crawling ricorsivo del sito web.
	
- **`site_analysis/`**: Utilizzata per i risultati del crawling ricorsivo di siti web. Al suo interno troverai sottocartelle per ogni dominio scansionato, contenenti i file HTML di tutte le pagine scaricate. Questa cartella può anche ospitare report JSON, HTML o PDF che riepilogano l'analisi della struttura complessiva del sito o i dati OSINT estratti durante il crawling.
    
- **`osint_exports/`**: Qui sono salvati i report dettagliati delle analisi OSINT effettuate su domini, indirizzi email o username. I report sono disponibili in formato JSON o HTML, fornendo una panoramica completa delle informazioni raccolte dalle varie fonti.
	
- **osint_usernames/**: Qui vengono salvati i file txt generati dalla libreria sherlock in seguito alla ricerca diretta degli username sulle piattaforme social.
	
- **`pdf_reports/`**: Questa directory è dedicata esclusivamente ai report esportati in formato PDF. Qui troverai le versioni PDF dei risultati delle analisi OSINT e delle analisi di scraping, formattate per una facile lettura, stampa e condivisione.

---
## f. Conclusioni

Browsint è uno tool OSINT versatile, offre un'ampia gamma di funzionalità per la raccolta e l'analisi di informazioni da fonti pubbliche. L' interfaccia a riga di comando con la chiara struttura a menu, lo rende accessibile anche a utenti non esperti, pur mantenendo la profondità tecnica necessaria per operazioni di intelligence. 
La gestione integrata delle API keys e la capacità di esportare i risultati in vari formati ne fanno un tool completo utilizzabile anche da professionisti e appassionati di OSINT.