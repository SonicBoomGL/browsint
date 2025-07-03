# Browsint

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Beta-orange.svg)

## 📝 Descrizione

Browsint è un toolkit OSINT (Open Source Intelligence) in Python per la raccolta e l'analisi di informazioni da fonti pubbliche su persone, domini, siti web ed entità correlate.

## 🔑 Funzionalità Principali

**1. Download & Crawl Siti Web**: Download HTML + struttura da link e file. Download ricorsivo con crwaling.
**2. Scraping OSINT Web**: Estrazioni dati presenti/nascosti nella pagina (anche in modo ricorsivo tramite crwaling)
**3. Investigazione Manuale**: Analisi dominio (Sodam, whois, dns,..), profilazione email / username...
**4. Opzioni di sistema**: Gestione DB, backup database, Gestione API keys 

Per ogni analisi sarà possibile salvare il report nei seguenti formati: JSON, HTML, PDF.

## 🚀 Installazione

1. Clona il repository:
```bash
git clone https://github.com/tuo-utente/browsint.git
cd browsint
```

2. Crea e attiva l'ambiente virtuale:
```bash
python3 -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

## ⚙️ Configurazione

Per utilizzare al massimo le funzionalità OSINT, crea un file `.env` nella directory radice del progetto con le seguenti API keys:

```env
HUNTER_IO_API_KEY=your_key_here
SHODAN_API_KEY=your_key_here
HIBP_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
SECURITYTRAILS_API_KEY=your_key_here
WHOISXMLAPI_API_KEY=your_key_here
```

Puoi anche utilizzare il menu di configurazione dell'applicazione per gestire le API keys in modo interattivo.

### Ottenere le API Keys

Per ottenere le API keys necessarie, registrati sui seguenti servizi:

- Hunter.io: https://hunter.io/users/sign_up
- Shodan: https://account.shodan.io/register
- HaveIBeenPwned: https://haveibeenpwned.com/API/Key
- VirusTotal: https://www.virustotal.com/gui/join-us
- SecurityTrails: https://securitytrails.com/app/signup
- WhoisXMLAPI: https://whois.whoisxmlapi.com/signup

L'applicazione può essere utilizzata anche con un sottoinsieme di keys o senza di esse, con funzionalità limitate.

## 📖 Utilizzo

Esegui lo script principale:
```bash
python3 src/main.py
```

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT.
