# Browsint Web Interface

Interfaccia web moderna per Browsint che permette di utilizzare tutte le funzionalità dell'applicazione CLI attraverso un'interfaccia grafica intuitiva e responsive.

## 🌟 Caratteristiche

- **Interfaccia moderna e responsive** - Design pulito e professionale con Bootstrap 5
- **Tutte le funzionalità CLI** - Accesso completo a crawling, scraping e analisi OSINT
- **Monitoraggio in tempo reale** - Tracking dei task in background con aggiornamenti live
- **Gestione API Keys** - Configurazione semplice delle chiavi API
- **Export multipli** - Esportazione risultati in JSON, HTML e PDF
- **Dashboard informativa** - Stato sistema e statistiche database

## 🚀 Installazione e Avvio

### 1. Installare le dipendenze web

```bash
cd web_interface
pip install -r requirements.txt
```

### 2. Avviare l'interfaccia web

```bash
python run.py
```

Oppure direttamente:

```bash
python app.py
```

### 3. Accedere all'interfaccia

Aprire il browser e navigare a: **http://127.0.0.1:8000**

## 📋 Funzionalità Disponibili

### 🔍 Crawling & Download
- **Download singola pagina** - Scarica e analizza una singola pagina web
- **Crawl ricorsivo** - Naviga e scarica interi siti web con controllo profondità
- **Salvataggio strutturato** - Organizzazione automatica dei file scaricati

### 🕵️ OSINT Scraping
- **Analisi pagina singola** - Estrazione dati OSINT da una pagina specifica
- **Crawl con OSINT** - Crawling con estrazione automatica di informazioni sensibili
- **Rilevamento tecnologie** - Identificazione framework, librerie JS e analytics

### 🎯 Profilazione OSINT
- **Analisi domini** - WHOIS, DNS, Shodan, Wayback Machine
- **Profilazione email** - Hunter.io, Have I Been Pwned, validazione
- **Ricerca username** - Scansione profili social media con Sherlock

### 🗄️ Gestione Sistema
- **Database info** - Statistiche e informazioni sui database SQLite
- **API Keys** - Configurazione e gestione delle chiavi API
- **Profili salvati** - Visualizzazione e export dei profili OSINT

## 🎨 Interfaccia Utente

### Dashboard Principale
- Stato sistema in tempo reale
- Accesso rapido a tutte le funzionalità
- Indicatori di stato API keys e database

### Sezioni Specializzate
- **Menu laterale** per navigazione rapida
- **Form intuitivi** per input parametri
- **Risultati formattati** con syntax highlighting
- **Export integrato** per tutti i formati supportati

### Monitoraggio Task
- **Progress tracking** per operazioni lunghe
- **Notifiche toast** per feedback immediato
- **Risultati in tempo reale** con aggiornamenti automatici

## 🔧 Configurazione

### API Keys
Le API keys possono essere configurate direttamente dall'interfaccia web:

1. Navigare su **Sistema → API Keys**
2. Cliccare **Configura** per il servizio desiderato
3. Inserire la chiave API
4. Salvare la configurazione

### Servizi Supportati
- **Hunter.io** - Verifica e informazioni email
- **Shodan** - Scansione servizi e vulnerabilità
- **Have I Been Pwned** - Controllo data breach
- **WhoisXML** - Dati WHOIS avanzati
- **VirusTotal** - Analisi sicurezza
- **SecurityTrails** - Intelligence DNS

## 📊 Monitoraggio e Risultati

### Task in Background
- Crawling e analisi OSINT vengono eseguiti in background
- Monitoraggio automatico dello stato con polling
- Notifiche di completamento o errore

### Visualizzazione Risultati
- **Formattazione intelligente** basata sul tipo di dato
- **Syntax highlighting** per JSON e codice
- **Tabelle responsive** per dati strutturati
- **Cards informative** per metriche e statistiche

### Export e Condivisione
- **JSON** - Dati strutturati per elaborazione
- **HTML** - Report formattati per visualizzazione
- **PDF** - Documenti professionali per condivisione

## 🛠️ Sviluppo e Personalizzazione

### Struttura del Progetto
```
web_interface/
├── app.py              # FastAPI application
├── run.py              # Launcher script
├── requirements.txt    # Python dependencies
├── templates/
│   ├── base.html      # Base template
│   └── index.html     # Main interface
└── static/
    ├── css/
    │   └── style.css  # Custom styles
    └── js/
        └── app.js     # Frontend JavaScript
```

### Tecnologie Utilizzate
- **Backend**: FastAPI, Uvicorn
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Templating**: Jinja2
- **Icons**: Bootstrap Icons
- **Styling**: Custom CSS con variabili CSS

### API Endpoints
- `GET /` - Interfaccia principale
- `GET /api/status` - Stato sistema
- `POST /api/crawl/*` - Operazioni di crawling
- `POST /api/osint/*` - Analisi OSINT
- `GET /api/profiles/*` - Gestione profili
- `GET /api/database/*` - Informazioni database
- `POST /api/keys` - Gestione API keys

## 🔒 Sicurezza

- **Accesso locale** - Server bind su 127.0.0.1 per sicurezza
- **API keys protette** - Mascheramento delle chiavi nell'interfaccia
- **Validazione input** - Controlli lato server per tutti gli input
- **Error handling** - Gestione sicura degli errori senza leak di informazioni

## 📱 Responsive Design

L'interfaccia è completamente responsive e ottimizzata per:
- **Desktop** - Layout completo con sidebar
- **Tablet** - Layout adattivo con menu collassabile
- **Mobile** - Interfaccia touch-friendly con navigazione ottimizzata

## 🎯 Utilizzo Consigliato

1. **Avviare l'interfaccia web** con `python run.py`
2. **Configurare le API keys** necessarie
3. **Iniziare con analisi semplici** (singola pagina)
4. **Procedere con crawling** per analisi più approfondite
5. **Utilizzare OSINT** per intelligence avanzata
6. **Esportare i risultati** nei formati desiderati

## 🆘 Risoluzione Problemi

### Errori Comuni
- **Porta 8000 occupata**: Modificare la porta in `run.py`
- **Dipendenze mancanti**: Eseguire `pip install -r requirements.txt`
- **Errori API**: Verificare le chiavi API nella sezione Sistema

### Log e Debug
- I log sono visibili nella console dove è stato avviato il server
- Utilizzare il browser developer tools per debug frontend
- Controllare la sezione "Network" per errori API

---

**Browsint Web Interface** - Portare l'OSINT nel browser con stile e funzionalità! 🚀