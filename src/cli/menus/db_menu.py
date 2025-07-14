"""
Database menu module for the Browsint CLI application.
"""
from colorama import Fore, Style
from typing import TYPE_CHECKING
from ..utils import clear_screen, prompt_for_input
import logging
from pathlib import Path

if TYPE_CHECKING:
    from ..scraper_cli import ScraperCLI

logger = logging.getLogger("browsint.cli")

def display_db_menu() -> str:
    '''Visualizza il menu del database e restituisce la scelta dell'utente.'''
    #clear_screen()
    print(f"\n{Fore.BLUE}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'GESTIONE DATABASE E API':^36}{Fore.BLUE} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=== Database ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Informazioni Generali Database")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Esegui Backup Database")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Svuota Cache delle Query")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Gestione Tabelle Database")
    print(f"\n{Fore.CYAN}=== API Keys ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Visualizza API Keys configurate")
    print(f"{Fore.YELLOW}6.{Style.RESET_ALL} Aggiungi/Aggiorna API Key")
    print(f"{Fore.YELLOW}7.{Style.RESET_ALL} Rimuovi API Key")
    print(f"\n{Fore.YELLOW}0.{Style.RESET_ALL} Torna al menu Opzioni Generali")

    return prompt_for_input("Scelta: ")

def handle_db_choice(cli_instance: 'ScraperCLI', choice: str) -> None:
    '''
    Gestisce la scelta dell'utente nel menu del database.
    
    Args:
        cli_instance: L'istanza di ScraperCLI per accedere ai metodi
        choice: La scelta dell'utente
    '''
    match choice:
        case "1": _display_db_info(cli_instance)
        case "2": _perform_db_backup(cli_instance)
        case "3": _clear_query_cache(cli_instance)
        case "4": _clear_specific_table(cli_instance)
        case "5": show_api_keys(cli_instance)
        case "6": add_api_key(cli_instance)
        case "7": remove_api_key(cli_instance)
        case "0": return
        case _:
            print(f"{Fore.RED}✗ Scelta non valida")
            input(f"{Fore.CYAN}\nPremi INVIO per continuare...{Style.RESET_ALL}")

def _display_db_info(cli_instance: 'ScraperCLI') -> None:
    """Mostra informazioni sui database."""
    while True:
        print(f"\n{Fore.BLUE}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'INFORMAZIONI DATABASE':^36}{Fore.BLUE} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        # Mostra le opzioni disponibili
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Mostra info di tutti i database")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Seleziona database specifico\n")
        print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("Scelta: ").strip()
        
        if choice == "1":
            for db_name in ["websites", "osint"]:
                try:
                    size = cli_instance.db_manager.get_database_size(db_name) 
                    tables = cli_instance.db_manager.get_all_table_names(db_name)
                    
                    print(f"\n{Fore.CYAN}Database {db_name.upper()}:{Style.RESET_ALL}")
                    print(f"  Dimensione: {size:.2f} MB")
                    print(f"  Tabelle ({len(tables)}):")
                    for table in tables:
                        row_count = cli_instance.db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}", db_name=db_name)
                        count = row_count['count'] if row_count else 0
                        print(f"    - {table} ({count} righe)")
                except Exception as e:
                    print(f"{Fore.RED}Errore lettura info {db_name}: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "2":
            print(f"\n{Fore.CYAN}Database disponibili:{Style.RESET_ALL}")
            print("1. websites")
            print("2. osint")
            db_choice = prompt_for_input("\nSeleziona database (0 per annullare): ").strip()
            
            if db_choice == "1":
                db_name = "websites"
            elif db_choice == "2":
                db_name = "osint"
            else:
                continue
                
            try:
                size = cli_instance.db_manager.get_database_size(db_name)
                tables = cli_instance.db_manager.get_all_table_names(db_name)
                
                print(f"\n{Fore.CYAN}Database {db_name.upper()}:{Style.RESET_ALL}")
                print(f"  Dimensione: {size:.2f} MB")
                print(f"  Tabelle ({len(tables)}):")
                for table in tables:
                    row_count = cli_instance.db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}", db_name=db_name)
                    count = row_count['count'] if row_count else 0
                    print(f"    - {table} ({count} righe)")
            except Exception as e:
                print(f"{Fore.RED}Errore lettura info {db_name}: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "0":
            break

def _perform_db_backup(cli_instance: 'ScraperCLI') -> None:
    """Esegue il backup dei database."""
    while True:
        print(f"\n{Fore.BLUE}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'BACKUP DATABASE':^36}{Fore.BLUE} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Backup di tutti i database")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Backup database specifico\n")
        print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("Scelta: ").strip()
        
        if choice == "1":
            print(f"\n{Fore.YELLOW}⏳ Backup di tutti i database in corso...{Style.RESET_ALL}")
            for db_name in ["websites", "osint"]:
                try:
                    success, result = cli_instance.db_manager.backup_database(db_name)
                    if success:
                        print(f"{Fore.YELLOW}✓ Backup {db_name} completato in: {result}{Style.RESET_ALL}")
                        backup_size = Path(result).stat().st_size / (1024 * 1024)
                        print(f"{Fore.CYAN}Dimensione backup: {backup_size:.2f} MB{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}✗ Backup {db_name} fallito: {result}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}✗ Errore durante il backup di {db_name}: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "2":
            print(f"\n{Fore.CYAN}Database disponibili:{Style.RESET_ALL}")
            print("1. websites")
            print("2. osint")
            db_choice = prompt_for_input("\nSeleziona database (0 per annullare): ").strip()
            
            if db_choice == "1":
                db_name = "websites"
            elif db_choice == "2":
                db_name = "osint"
            else:
                continue
                
            try:
                print(f"\n{Fore.YELLOW}⏳ Backup database {db_name} in corso...{Style.RESET_ALL}")
                success, result = cli_instance.db_manager.backup_database(db_name)
                if success:
                    print(f"{Fore.YELLOW}✓ Backup completato in: {result}{Style.RESET_ALL}")
                    backup_size = Path(result).stat().st_size / (1024 * 1024)
                    print(f"{Fore.CYAN}Dimensione backup: {backup_size:.2f} MB{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Backup fallito: {result}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Errore durante il backup: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "0":
            break

def _clear_query_cache(cli_instance: 'ScraperCLI') -> None:
    """Svuota la cache delle query."""
    while True:
        print(f"\n{Fore.BLUE}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'GESTIONE CACHE':^36}{Fore.BLUE} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Svuota tutta la cache")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Svuota cache per database specifico")
        print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("Scelta: ").strip()
        
        if choice == "1":
            try:
                cli_instance.db_manager.clear_cache()
                print(f"{Fore.YELLOW}✓ Cache delle query svuotata con successo{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Errore pulizia cache: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "2":
            print(f"\n{Fore.CYAN}Database disponibili:{Style.RESET_ALL}")
            print("1. websites")
            print("2. osint")
            db_choice = prompt_for_input("Scelta (0 per annullare): ").strip()
            
            if db_choice == "1":
                db_name = "websites"
            elif db_choice == "2":
                db_name = "osint"
            else:
                continue
                
            try:
                # Chiamiamo clear_cache senza il parametro del database
                cli_instance.db_manager.clear_cache()
                print(f"{Fore.YELLOW}✓ Cache delle query svuotata con successo{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Errore pulizia cache: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "0":
            break

def _clear_specific_table(cli_instance: 'ScraperCLI') -> None:
    """Svuota le tabelle del database."""
    while True:
        print(f"\n{Fore.BLUE}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'GESTIONE TABELLE':^36}{Fore.BLUE} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Svuota tutte le tabelle di tutti i database")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Svuota tutte le tabelle di un database")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Svuota una tabella specifica")
        print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("Scelta: ").strip()
        
        if choice == "1":
            print(f"{Fore.RED}⚠️ ATTENZIONE: Stai per eliminare TUTTI i dati da TUTTI i database!{Style.RESET_ALL}")
            
            # Mostra riepilogo dei dati che verranno eliminati
            for db_name in ["websites", "osint"]:
                try:
                    tables = cli_instance.db_manager.get_all_table_names(db_name)
                    if tables:
                        print(f"\n{Fore.CYAN}Database {db_name.upper()}:{Style.RESET_ALL}")
                        for table in tables:
                            row_count = cli_instance.db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}", db_name=db_name)
                            count = row_count['count'] if row_count else 0
                            print(f"  - {table} ({count} righe)")
                except Exception as e:
                    print(f"{Fore.RED}Errore lettura tabelle {db_name}: {e}{Style.RESET_ALL}")

            confirm = prompt_for_input(f"\n{Fore.RED}⚠️ Confermi di voler eliminare TUTTI i dati? (s/N): ").strip().lower()
            
            if confirm == 's':
                double_confirm = prompt_for_input(f"{Fore.RED}⚠️ Questa azione non può essere annullata! Conferma nuovamente: (s/N) ").strip().lower()
                if double_confirm == 's':
                    for db_name in ["websites", "osint"]:
                        try:
                            success, cleared = cli_instance.db_manager.clear_all_tables(db_name)
                            if success:
                                print(f"{Fore.YELLOW}✓ Tabelle di {db_name} svuotate con successo:{Style.RESET_ALL}")
                                for table in cleared:
                                    print(f"  - {table}")
                            else:
                                print(f"{Fore.RED}✗ Errore durante lo svuotamento di {db_name}{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}✗ Errore durante lo svuotamento di {db_name}: {e}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Operazione annullata{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Operazione annullata{Style.RESET_ALL}")
            
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "2":
            print(f"\n{Fore.CYAN}Database disponibili:{Style.RESET_ALL}")
            print("1. websites")
            print("2. osint")
            db_choice = prompt_for_input("Scelta (0 per annullare): ").strip()
            
            if db_choice == "1":
                db_name = "websites"
            elif db_choice == "2":
                db_name = "osint"
            else:
                continue
            
            try:
                tables = cli_instance.db_manager.get_all_table_names(db_name)
                if not tables:
                    print(f"{Fore.YELLOW}⚠ Nessuna tabella trovata nel database {db_name}{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
                    continue
                
                print(f"\n{Fore.RED}⚠️ ATTENZIONE: Stai per eliminare tutti i dati da {db_name}!{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}Tabelle che verranno svuotate:{Style.RESET_ALL}")
                for table in tables:
                    row_count = cli_instance.db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}", db_name=db_name)
                    count = row_count['count'] if row_count else 0
                    print(f"  - {table} ({count} righe)")
                
                confirm = prompt_for_input(f"\n{Fore.RED}⚠️ Confermi di voler eliminare TUTTI i dati da {db_name}? (s/N): ").strip().lower()
                
                if confirm == 's':
                    double_confirm = prompt_for_input(f"{Fore.RED}⚠️ Questa azione non può essere annullata! Conferma nuovamente: (s/N) ").strip().lower()
                    if double_confirm == 's':
                        success, cleared = cli_instance.db_manager.clear_all_tables(db_name)
                        if success:
                            print(f"{Fore.YELLOW}✓ Tabelle di {db_name} svuotate con successo:{Style.RESET_ALL}")
                            for table in cleared:
                                print(f"  - {table}")
                        else:
                            print(f"{Fore.RED}✗ Errore durante lo svuotamento{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Operazione annullata{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Operazione annullata{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "3":
            print(f"\n{Fore.CYAN}Database disponibili:{Style.RESET_ALL}")
            print("1. websites")
            print("2. osint")
            db_choice = prompt_for_input("Scelta (0 per annullare): ").strip()
            
            if db_choice == "1":
                db_name = "websites"
            elif db_choice == "2":
                db_name = "osint"
            else:
                continue
            
            try:
                tables = cli_instance.db_manager.get_all_table_names(db_name)
                if not tables:
                    print(f"{Fore.YELLOW}⚠ Nessuna tabella trovata nel database {db_name}{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
                    continue
                    
                print(f"\n{Fore.CYAN}Tabelle disponibili in {db_name}:{Style.RESET_ALL}")
                for i, table in enumerate(tables, 1):
                    row_count = cli_instance.db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}", db_name=db_name)
                    count = row_count['count'] if row_count else 0
                    print(f"{i}. {table} ({count} righe)")
                
                table_choice = prompt_for_input("\nSeleziona numero tabella (0 per annullare): ").strip()
                
                if table_choice.isdigit() and 0 < int(table_choice) <= len(tables):
                    table_name = tables[int(table_choice)-1]
                    confirm = prompt_for_input(f"{Fore.RED}⚠️ Confermi di voler svuotare {table_name}? (s/N): ").strip().lower()
                    
                    if confirm == 's':
                        if cli_instance.db_manager.clear_table(table_name, db_name):
                            print(f"{Fore.YELLOW}✓ Tabella {table_name} svuotata con successo{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}✗ Errore durante lo svuotamento della tabella{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "0":
            break

def show_api_keys(cli_instance: 'ScraperCLI') -> None:
    '''Visualizza le API keys configurate, mascherandone parzialmente il valore per sicurezza.'''
    if not cli_instance.api_keys:
        print(f"{Fore.YELLOW}⚠ Nessuna API key configurata.")
        return
    print(f"\n{Fore.CYAN}API Keys Configurate:{Style.RESET_ALL}")
    table = []
    for service, key_value in cli_instance.api_keys.items():
        masked_key = key_value[:4] + "****" + key_value[-4:] if len(key_value) > 8 else "****"
        table.append([service, masked_key])
    if table:
        from tabulate import tabulate
        print(tabulate(table, headers=["Servizio", "API Key (Mascherata)"], tablefmt="pretty"))

        
    else:
        print(f"{Fore.YELLOW}Nessuna API key trovata.{Style.RESET_ALL}")

    input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")

def add_api_key(cli_instance: 'ScraperCLI') -> None:
    import maskpass
    '''Permette all'utente di aggiungere o modificare una API key.'''
    print(f"\n{Fore.CYAN}Aggiungi/Modifica API Key{Style.RESET_ALL}")
    supported_services = {
        "hunterio": "HUNTER_IO_API_KEY",
        "hibp": "HIBP_API_KEY",
        "shodan": "SHODAN_API_KEY",
        "whoisxml": "WHOISXML_API_KEY",
        "virustotal": "VIRUSTOTAL_API_KEY",
        "securitytrails": "SECURITYTRAILS_API_KEY"
    }
    
    print("\nServizi supportati:")
    for i, (service, env_var) in enumerate(supported_services.items(), 1):
        print(f"{i}. {service} ({env_var})")
    
    try:
        choice = int(prompt_for_input("\nSeleziona il numero del servizio (0 per annullare): "))
        if choice == 0:
            return
        if 1 <= choice <= len(supported_services):
            service_name = list(supported_services.keys())[choice - 1]
            env_var = supported_services[service_name]
            print(f"{Fore.CYAN}Inserisci la API key per {service_name}: {Style.RESET_ALL}", end='', flush=True)
            api_key = maskpass.askpass('', mask='*').strip()
            if not api_key:
                print(f"{Fore.RED}✗ API key non può essere vuota.")
                return
            
            # Salva nel file .env
            from dotenv import set_key
            set_key(cli_instance.env_file, env_var, api_key)
            # Aggiorna le variabili d'ambiente
            import os
            os.environ[env_var] = api_key
            # Aggiorna il dizionario delle API keys
            cli_instance.api_keys[service_name] = api_key
            # Aggiorna l'estrattore OSINT
            cli_instance.osint_extractor.api_keys = cli_instance.api_keys
            
            print(f"{Fore.YELLOW}✓ API key per '{service_name}' salvata con successo.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Scelta non valida.")
    except ValueError:
        print(f"{Fore.RED}✗ Inserire un numero valido.")

def remove_api_key(cli_instance: 'ScraperCLI') -> None:
    '''Permette all'utente di rimuovere una API key.'''
    if not cli_instance.api_keys:
        print(f"{Fore.YELLOW}⚠ Nessuna API key configurata da rimuovere.")
        return

    service_mapping = {
        "hunterio": "HUNTER_IO_API_KEY",
        "hibp": "HIBP_API_KEY",
        "shodan": "SHODAN_API_KEY",
        "whoisxml": "WHOISXML_API_KEY",
        "virustotal": "VIRUSTOTAL_API_KEY",
        "securitytrails": "SECURITYTRAILS_API_KEY"
    }

    try:
        services = list(cli_instance.api_keys.keys())
        for i, service in enumerate(services, 1):
            print(f"{i}. {service}")
        
        choice = int(prompt_for_input("\nSeleziona il numero del servizio da rimuovere (0 per annullare): "))
        if choice == 0:
            return
        if 1 <= choice <= len(services):
            service_name = services[choice - 1]
            env_var = service_mapping[service_name]
            
            confirm = prompt_for_input(f"{Fore.YELLOW}Confermi la rimozione della API key per {service_name}? (s/N): {Style.RESET_ALL}").lower()
            if confirm == 's':
                # Rimuovi dal file .env
                from dotenv import unset_key
                unset_key(cli_instance.env_file, env_var) # libreria per gestire le variabili d'ambiente
                # Rimuovi dalla variabile d'ambiente
                import os
                os.environ.pop(env_var, None) 
                # Rimuovi dal dizionario delle API keys
                cli_instance.api_keys.pop(service_name, None)
                # Aggiorna l'estrattore OSINT
                cli_instance.osint_extractor.api_keys = cli_instance.api_keys
                
                print(f"{Fore.YELLOW}✓ API key per '{service_name}' rimossa con successo.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Scelta non valida.")
    except ValueError:
        print(f"{Fore.RED}✗ Inserire un numero valido.")