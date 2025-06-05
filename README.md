# Browsint

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Beta-orange.svg)

## 📝 Descrizione

Browsint è un toolkit OSINT (Open Source Intelligence) in Python per la raccolta e l'analisi di informazioni da fonti pubbliche su domini, siti web ed entità correlate.

## 🔑 Funzionalità Principali

- **Downlaod pagine**: Download delle pagine web per una analisi offline
- **Crawling Web**: Esplorazione automatica di siti web
- **Analisi OSINT**: Raccolta di informazioni da servizi come WHOIS, DNS, Shodan
- **Estrazione Dati**: Email, numeri di telefono, tecnologie web, profili social
- **Database Locale**: Salvataggio dei dati in SQLite per analisi successive

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

Per utilizzare le funzionalità OSINT, crea un file `.env` nella directory radice del progetto con le seguenti API keys:

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

Le API keys sono necessarie per il pieno funzionamento delle funzionalità OSINT, ma l'applicazione può essere utilizzata anche con un sottoinsieme di keys o senza di esse, con funzionalità limitate.

## 📖 Utilizzo

Esegui lo script principale:
```bash
python main.py
```

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT.