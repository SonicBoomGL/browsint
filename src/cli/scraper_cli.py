"""
Main CLI class for the Browsint application.
"""
import sys
from pathlib import Path
from textwrap import indent
from urllib.parse import urlparse
import json
import logging
import re
import time
from datetime import datetime
from colorama import Fore, Style
from tabulate import tabulate
import validators
import os
from dotenv import load_dotenv, set_key, unset_key

# Import the database manager
from db.manager import DatabaseManager

# Import scraper components
from scraper.extractors.osint_extractor import OSINTExtractor
from scraper.fetcher import WebFetcher
from scraper.parser import WebParser
from scraper.crawler import Crawler

# Import menu modules
from .menus import osint_menu, download_menu, db_menu, scraping_menu
# Import utilities
from .utils import json_serial, clear_screen, prompt_for_input, confirm_action

# Initialize loggers
logger = logging.getLogger("browsint.cli")
crawler_logger = logging.getLogger("scraper.crawler")
fetcher_logger = logging.getLogger("scraper.fetcher")
db_logger = logging.getLogger("DatabaseManager")

class ScraperCLI:
    '''
    Classe: ScraperCLI
    Gestisce l'interfaccia a riga di comando per lo strumento OSINT (ORCHESTRATORE).
    '''
    def __init__(self):
        '''
        Funzione: __init__
        Inizializza l'interfaccia a riga di comando per lo strumento OSINT.
        '''
        # Prima chiamiamo setup per inizializzare i percorsi
        self.setup()
        
        # Carichiamo le API keys dalle variabili d'ambiente e dal file .env
        self.api_keys = self._load_api_keys_from_env()
        
        # Infine inizializziamo tutti i componenti
        self.db_manager = DatabaseManager()
        self.osint_extractor = OSINTExtractor(
            api_keys=self.api_keys,
            data_dir=self.data_dir,
            dirs=self.dirs
        )
        self.web_fetcher = WebFetcher()
        self.web_parser = WebParser()
        self.crawler = Crawler(
            fetcher=self.web_fetcher,
            parser=self.web_parser,
            db_manager=self.db_manager,
            osint_extractor=self.osint_extractor,
            base_dirs=self.dirs
        )
        self.running = True

    def setup(self) -> None:
        '''
        Funzione: setup
        Inizializza la configurazione di base delle directory e dei file.
        '''
        self.base_dir = Path(__file__).parent.parent.parent
        self.env_file = self.base_dir / ".env"
        self.data_dir = self.base_dir / "data"

        # Crea il file .env se non esiste
        if not self.env_file.exists():
            self.env_file.touch()

        self.dirs = {
            "sites": self.data_dir / "url_downloaded",
            "analysis": self.data_dir / "site_analysis",
            "reports": self.data_dir / "downloaded_reports",
            "osint_exports": self.data_dir / "osint_exports",
            "downloaded_tree": self.data_dir / "downloaded_tree",
            "osint_usernames": self.data_dir / "osint_usernames",
            "pdf_reports": self.data_dir / "pdf_reports"
        }

        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {dir_path}")

    def _load_api_keys_from_env(self) -> dict:
        '''
        Funzione: _load_api_keys_from_env
        Carica le API keys dalle variabili d'ambiente e dal file .env.
        '''
        # Carica le variabili dal file .env
        load_dotenv(self.env_file)
        
        api_keys = {
            "hunterio": os.getenv("HUNTER_IO_API_KEY"),
            "hibp": os.getenv("HIBP_API_KEY"),
            "shodan": os.getenv("SHODAN_API_KEY"),
            "whoisxml": os.getenv("WHOISXML_API_KEY"),
            "virustotal": os.getenv("VIRUSTOTAL_API_KEY"),
            "securitytrails": os.getenv("SECURITYTRAILS_API_KEY")
        }
        return {k: v for k, v in api_keys.items() if v}

    def show_banner(self) -> None:
        '''
        Funzione: show_banner
        Mostra un banner ASCII art all'avvio dell'applicazione.
        '''
        banner = fr"""{Fore.CYAN}
██████╗ ██████╗  ██████╗ ██╗    ██╗███████╗██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔════╝██║████╗  ██║╚══██╔══╝
██████╔╝██████╔╝██║   ██║██║ █╗ ██║███████╗██║██╔██╗ ██║   ██║   
██╔══██╗██╔══██╗██║   ██║██║███╗██║╚════██║██║██║╚██╗██║   ██║   
██████╔╝██║  ██║╚██████╔╝╚███╔███╔╝███████║██║██║ ╚████║   ██║   
╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   
            {Fore.YELLOW}Web Intelligence & OSINT Collection Tool{Style.RESET_ALL}
            {Fore.BLUE}Version ALPHA{Style.RESET_ALL}

{Fore.LIGHTBLUE_EX}{'='*60}{Style.RESET_ALL}

            """
        print(banner)
        time.sleep(0.5)

    def run(self) -> None:
        '''
        Funzione: run
        Avvia il loop principale dell'applicazione CLI.
        '''
        try:
            self.show_banner()

            required_keys = ["shodan", "whoisxml", "hunterio", "hibp"]
            if self.api_keys:
                missing_keys = [key for key in required_keys if key not in self.api_keys or not self.api_keys.get(key)]
                if missing_keys:
                    print(f"{Fore.YELLOW}⚠ API keys mancanti o non valorizzate per: {', '.join(missing_keys)}")
                    print(f"{Fore.YELLOW}⚠ Alcune funzionalità OSINT potrebbero non funzionare correttamente.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠ File di configurazione API non caricato o vuoto. Molte funzionalità OSINT saranno limitate.{Style.RESET_ALL}")

            while self.running:
                try:
                    choice = self.display_main_menu()
                    self._handle_main_menu_choice(choice)
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Grazie per aver usato Browsint! Arrivederci!{Style.RESET_ALL}")
                    return

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Grazie per aver usato Browsint! Arrivederci!{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Errore generale nell'applicazione: {e}", exc_info=True)
            print(f"\n{Fore.RED}✗ Si è verificato un errore imprevisto: {e}{Style.RESET_ALL}")

    def display_main_menu(self) -> str:
        '''Visualizza il menu principale e restituisce la scelta dell'utente.'''
        print(f"{Fore.BLUE}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'BROWSINT - MENU PRINCIPALE':^36}{Fore.BLUE} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Download & Crawl Siti Web (per analisi offline)")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Scraping OSINT Web ")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Investigazione Manuale")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Opzioni di sistema (DB, Cache, API Keys)\n")
        print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Esci")
        return prompt_for_input(f"{Fore.CYAN}Scelta: {Style.RESET_ALL}")

    def _handle_main_menu_choice(self, choice: str):
        '''Gestisce la scelta dell'utente nel menu principale.'''
        match choice:
            case "1": self._download_websites_menu()
            case "2": self._scrape_crawl_websites_menu()
            case "3": self._osint_menu()
            case "4": self._options_menu()
            case "0":
                print(f"\n{Fore.YELLOW}Grazie per aver usato Browsint! Arrivederci!{Style.RESET_ALL}")
                self.running = False
            case _:
                print(f"{Fore.RED}✗ Scelta non valida")
                input(f"{Fore.CYAN}\nPremi INVIO per continuare...{Style.RESET_ALL}")

    def _download_websites_menu(self):
        '''Menu per il download di siti web.'''
        while True:
            choice = download_menu.display_download_menu()
            if choice == "0":
                break
            download_menu.handle_download_choice(self, choice)

    def _scrape_crawl_websites_menu(self):
        '''Menu per lo scraping e crawling di siti web.'''
        while True:
            choice = scraping_menu.display_scraping_menu()
            if choice == "0":
                break
            scraping_menu.handle_scraping_choice(self, choice)

    def _osint_menu(self):
        '''Menu per le funzionalità OSINT.'''
        while True:
            choice = osint_menu.display_osint_menu()
            if choice == "0":
                break
            osint_menu.handle_osint_choice(self, choice)

    def _options_menu(self):
        '''Menu per le opzioni di sistema.'''
        while True:
            choice = db_menu.display_db_menu()
            if choice == "0":
                break
            db_menu.handle_db_choice(self, choice)
    
            
    def _get_validated_url_input(self, prompt_message: str) -> str:
        '''
        Funzione: _get_validated_url_input
        Ottiene e valida un input URL.
        '''
        url = prompt_for_input(prompt_message)
        if not url or not validators.url(url):
            print(f"{Fore.RED}✗ URL non valido.")
            return None
        return url

    def _get_depth_input(self, default: int = 2, message: str = None) -> int:
        '''
        Funzione: _get_depth_input
        Ottiene e valida un input di profondità.
        '''
        if message is None:
            message = f"Inserisci il limite di profondità (default: {default}): "
        depth_str = prompt_for_input(message)
        return int(depth_str) if depth_str.isdigit() else default
