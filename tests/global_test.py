import sys
from pathlib import Path

# Aggiungi il percorso del progetto al sys.path se necessario
# Adatta questo percorso in base a dove salvi test_functions.py
# Se test_functions.py è nella stessa directory di main.py, potresti non aver bisogno di questo.
# Se è in src/scraper/, potresti aver bisogno di sys.path.insert(0, str(Path(__file__).parent.parent.parent))
src_path = str(Path(__file__).parent.parent.parent) # Assuming test_functions.py is in src/scraper/ or similar
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    #print(f"Added {src_path} to sys.path") # Debugging line

from cli.scraper_cli import ScraperCLI
from colorama import Fore, Style
import time

# Inizializza la CLI (carica configurazione, DB, fetcher, parser, ecc.)
# Potrebbe essere necessario gestire eventuali errori di inizializzazione qui
try:
    cli_app = ScraperCLI()
except RuntimeError as e:
    print(f"{Fore.RED}Errore durante l'inizializzazione della CLI: {e}{Style.RESET_ALL}")
    sys.exit(1)


def test_analyze_page_structure(url="https://www.gsaurora.com/"):
    print(f"\n{Fore.BLUE}--- Test: analyze_page_structure ---{Style.RESET_ALL}")
    cli_app.analyze_page_structure() # La funzione chiederà l'URL internamente, ma possiamo anche passare qui


def test_start_website_crawl_base(url="https://www.gsaurora.com/", depth=1):
    print(f"\n{Fore.BLUE}--- Test: start_website_crawl_base ---{Style.RESET_ALL}")
    # Simula l'input dell'utente per URL e profondità se necessario, o chiama direttamente
    # cli_app.start_website_crawl_base() # Richiede input utente
    # Oppure modifica temporaneamente _get_validated_url_input e _get_depth_input o passa valori direttamente
    print(f"{Fore.YELLOW}Eseguendo crawl base per {url} con profondità {depth}...{Style.RESET_ALL}")
    try:
        crawl_stats = cli_app.crawler.start_crawl(url, depth_limit=depth, perform_osint_on_pages=False)
        cli_app._display_base_crawl_stats(crawl_stats)
    except Exception as e:
        print(f"{Fore.RED}Errore nel test crawl base: {e}{Style.RESET_ALL}")


def test_start_website_crawl_with_osint(url="https://www.gsaurora.com/", depth=1):
    print(f"\n{Fore.BLUE}--- Test: start_website_crawl_with_osint ---{Style.RESET_ALL}")
    # Simula l'input dell'utente o chiama direttamente
    # cli_app.start_website_crawl_with_osint() # Richiede input utente
    print(f"{Fore.YELLOW}Eseguendo crawl OSINT per {url} con profondità {depth}...{Style.RESET_ALL}")
    try:
         if not cli_app.osint_extractor:
             print(f"{Fore.RED}OSINT Extractor non disponibile. Impossibile procedere.{Style.RESET_ALL}")
             return

         crawl_stats = cli_app.crawler.start_crawl(
             url,
             depth_limit=depth,
             perform_osint_on_pages=True
         )
         cli_app._display_base_crawl_stats(crawl_stats)
         if "osint_summary" in crawl_stats:
             cli_app.display_crawl_osint_report(crawl_stats["osint_summary"], url)
    except Exception as e:
        print(f"{Fore.RED}Errore nel test crawl OSINT: {e}{Style.RESET_ALL}")


def test_profile_domain_cli(domain="gsaurora.com"):
    print(f"\n{Fore.BLUE}--- Test: profile_domain_cli ---{Style.RESET_ALL}")
    # cli_app.profile_domain_cli() # Richiede input utente
    print(f"{Fore.YELLOW}Profilando dominio: {domain}...{Style.RESET_ALL}")
    try:
        profile = cli_app.osint_extractor.profile_domain(domain)
        if profile and not profile.get("error"):
             cli_app.osint_extractor._display_osint_profile(profile, domain)
        elif profile and profile.get("error"):
            print(f"{Fore.RED}✗ Errore Profilazione Dominio: {profile.get('error')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ Nessun risultato significativo per '{domain}'.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Errore nel test profilazione dominio: {e}{Style.RESET_ALL}")


def test_profile_email_cli(email="info@gsaurora.com"):
    print(f"\n{Fore.BLUE}--- Test: profile_email_cli ---{Style.RESET_ALL}")
    # cli_app.profile_email_cli() # Richiede input utente
    print(f"{Fore.YELLOW}Profilando email: {email}...{Style.RESET_ALL}")
    try:
        profile_result = cli_app.osint_extractor.profile_email(email)
        if profile_result and not profile_result.get("error"):
            cli_app.osint_extractor._display_osint_profile(profile_result, email)
        elif profile_result and profile_result.get("error"):
             print(f"{Fore.RED}✗ Errore Profilazione Email: {profile_result.get('error')}{Style.RESET_ALL}")
        else:
             print(f"{Fore.YELLOW}⚠ Nessun risultato significativo per '{email}'.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Errore nel test profilazione email: {e}{Style.RESET_ALL}")


def test_profile_username_cli(username="testuser"):
    print(f"\n{Fore.BLUE}--- Test: profile_username_cli ---{Style.RESET_ALL}")
    # cli_app.profile_username_cli() # Richiede input utente
    print(f"{Fore.YELLOW}Profilando username: {username}...{Style.RESET_ALL}")
    try:
        profile_result = cli_app.osint_extractor.profile_username(username)
        if profile_result and not profile_result.get("error"):
            cli_app.osint_extractor._display_osint_profile(profile_result, username)
        elif profile_result and profile_result.get("error"):
             print(f"{Fore.RED}✗ Errore Profilazione Username: {profile_result.get('error')}{Style.RESET_ALL}")
        else:
             print(f"{Fore.YELLOW}⚠ Nessun risultato significativo per '{username}'.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Errore nel test profilazione username: {e}{Style.RESET_ALL}")


def test_show_osint_profiles_cli():
    print(f"\n{Fore.BLUE}--- Test: show_osint_profiles_cli ---{Style.RESET_ALL}")
    cli_app.show_osint_profiles_cli()


def test_config_menu():
     print(f"\n{Fore.BLUE}--- Test: config_menu (Mostra API Keys) ---{Style.RESET_ALL}")
     cli_app.show_api_keys() # Puoi chiamare show_api_keys direttamente


# Menu di test rapido
def quick_test_menu():
    while True:
        print(f"\n{Fore.BLUE}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'MENU TEST RAPIDO':^36}{Fore.BLUE} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Test Analisi Pagina Singola (OSINT base)")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Test Crawl Base")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Test Crawl con OSINT")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Test Profilazione Dominio")
        print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Test Profilazione Email")
        print(f"{Fore.YELLOW}6.{Style.RESET_ALL} Test Profilazione Username")
        print(f"{Fore.YELLOW}7.{Style.RESET_ALL} Mostra Profili OSINT salvati")
        print(f"{Fore.YELLOW}8.{Style.RESET_ALL} Mostra API Keys configurate")
        print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Esci dal menu test")

        choice = input(f"\n{Fore.CYAN}Seleziona un test da eseguire: {Style.RESET_ALL}").strip()

        if choice == "1":
            test_analyze_page_structure() # Chiederà l'input URL
        elif choice == "2":
            # Puoi chiedere input o usare valori di default
            url = input(f"{Fore.CYAN}Inserisci URL per Crawl Base (default: https://www.gsaurora.com/): {Style.RESET_ALL}").strip() or "https://www.gsaurora.com/"
            depth_str = input(f"{Fore.CYAN}Inserisci profondità (default: 1): {Style.RESET_ALL}").strip()
            depth = int(depth_str) if depth_str.isdigit() else 1
            test_start_website_crawl_base(url, depth)
        elif choice == "3":
            # Puoi chiedere input o usare valori di default
            url = input(f"{Fore.CYAN}Inserisci URL per Crawl OSINT (default: https://www.gsaurora.com/): {Style.RESET_ALL}").strip() or "https://www.gsaurora.com/"
            depth_str = input(f"{Fore.CYAN}Inserisci profondità (default: 1): {Style.RESET_ALL}").strip()
            depth = int(depth_str) if depth_str.isdigit() else 1
            test_start_website_crawl_with_osint(url, depth)
        elif choice == "4":
            domain = input(f"{Fore.CYAN}Inserisci dominio da profilare (default: gsaurora.com): {Style.RESET_ALL}").strip() or "gsaurora.com"
            test_profile_domain_cli(domain)
        elif choice == "5":
            email = input(f"{Fore.CYAN}Inserisci email da profilare (default: info@gsaurora.com): {Style.RESET_ALL}").strip() or "info@gsaurora.com"
            test_profile_email_cli(email)
        elif choice == "6":
            username = input(f"{Fore.CYAN}Inserisci username da profilare (default: testuser): {Style.RESET_ALL}").strip() or "testuser"
            test_profile_username_cli(username)
        elif choice == "7":
            test_show_osint_profiles_cli()
        elif choice == "8":
            test_config_menu()
        elif choice == "0":
            print(f"{Fore.YELLOW}Uscita dal menu test.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Scelta non valida. Riprova.{Style.RESET_ALL}")

        input(f"{Fore.CYAN}\nPremi INVIO per continuare...{Style.RESET_ALL}")


if __name__ == "__main__":
    quick_test_menu()