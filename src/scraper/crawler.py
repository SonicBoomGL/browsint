import logging
import time
from collections import deque
from urllib.parse import urlparse, urljoin, unquote
from colorama import Fore, Style
from bs4 import BeautifulSoup
from typing import Optional, Any
from scraper.fetcher import WebFetcher
from scraper.parser import WebParser
from scraper.utils.robots_parser import RobotsParser, RobotsData
from db.manager import DatabaseManager
from pathlib import Path
from scraper.utils.extractors import extract_emails, extract_phone_numbers, filter_phone_numbers, filter_emails
from scraper.utils.web_analysis import detect_framework, detect_js_libraries, detect_analytics
import json


logger = logging.getLogger("scraper.crawler")

class Crawler:
    '''
    Funzione: Crawler
    Classe responsabile per la navigazione e il download ricorsivo di pagine web (crawling).
    Parametri formali:
        self -> Riferimento all'istanza della classe
        WebFetcher fetcher -> Istanza di WebFetcher per scaricare pagine
        WebParser parser -> Istanza di WebParser per analizzare pagine
        DatabaseManager db_manager -> Istanza di DatabaseManager per operazioni sul database
        osint_extractor -> Istanza opzionale di OSINTExtractor per profilazione OSINT
        dict[str, Path] base_dirs -> Dizionario con le directory di base per il salvataggio
    Valore di ritorno:
        None -> Il costruttore non restituisce un valore esplicito
    '''
    def __init__(self, fetcher: WebFetcher, parser: WebParser, db_manager: DatabaseManager, osint_extractor=None, base_dirs: dict[str, Path] = None):
        self.fetcher = fetcher
        self.parser = parser
        self.db_manager = db_manager
        self.osint_extractor = osint_extractor
        self.visited_urls = set()
        self.base_domain = ""
        self.base_dirs = base_dirs or {}
        self.current_site_dir = None
        self.already_profiled_in_session = set()
        self.robots_parser = RobotsParser()
        self.robots_data: Optional[RobotsData] = None
        self.respect_robots = True

    def set_osint_extractor(self, extractor):
        '''
        Funzione: set_osint_extractor
        Imposta o aggiorna l'istanza di OSINTExtractor utilizzata dal crawler.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            extractor -> L'istanza di OSINTExtractor da impostare
        Valore di ritorno:
            None -> La funzione non restituisce un valore
        '''
        self.osint_extractor = extractor
        if extractor:
            self.already_profiled_in_session = set()


    def _normalize_url(self, url: str, base_url: str) -> str | None:
        '''
        Funzione: _normalize_url
        Normalizza un URL relativo o assoluto rispetto a un URL base, rimuovendo frammenti e decodificando.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            str url -> L'URL da normalizzare
            str base_url -> L'URL base per risolvere URL relativi
        Valore di ritorno:
            str | None -> L'URL normalizzato o None in caso di errore
        '''
        try:
            absolute_url = urljoin(base_url, url.strip())
            parsed_url = urlparse(absolute_url)
            clean_url = parsed_url._replace(fragment="").geturl()
            clean_url = unquote(clean_url)
            if clean_url.endswith("/") and parsed_url.path != "/":
                clean_url = clean_url.rstrip("/")
            return clean_url
        except Exception as e:
            logger.warning(f"Errore normalizzazione URL '{url}': {e}")
            return None

    def _is_internal_url(self, url: str) -> bool:
        '''
        Funzione: _is_internal_url
        Verifica se un dato URL appartiene allo stesso dominio del sito base del crawling.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            str url -> L'URL da controllare
        Valore di ritorno:
            bool -> True se l'URL è interno, False altrimenti
        '''
        if not self.base_domain:
            return False
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc == self.base_domain
        except Exception:
            return False

 
    def _save_page_info(self, url: str, title: str, status_code: int, content_length: int, content_type: str) -> Optional[int]:
        '''
        Funzione: _save_page_info
        Salva le informazioni di una pagina nel database o le aggiorna se esistenti.
        Parametri formali:
            self -> Riferimento all'instance della classe
            str url -> URL della pagina
            str title -> Titolo della pagina
            int status_code -> Codice di stato HTTP della risposta
            int content_length -> Dimensione del contenuto in byte
            str content_type -> Tipo di contenuto (es. text/html)
        Valore di ritorno:
            int | None -> ID della pagina salvata/aggiornata, o None in caso di errore
        '''
        domain = urlparse(url).netloc
        website_id = self._get_or_create_website(domain)
        if not website_id:
            logger.error(f"Impossibile ottenere o creare website_id per il dominio {domain}")
            return None

        try:
            with self.db_manager.transaction("websites") as cursor:
                # Check if page exists
                cursor.execute(
                    "SELECT id FROM pages WHERE url = ? AND website_id = ?",
                    (url, website_id)
                )
                existing_page = cursor.fetchone()

                if existing_page:
                    page_id = existing_page['id']
                    cursor.execute(
                        "UPDATE pages SET status_code = ?, content_length = ?, content_type = ?, last_checked = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (status_code, content_length, content_type, page_id)
                    )
                    logger.info(f"Pagina '{url}' aggiornata (ID: {page_id}).")
                    return page_id
                else:
                    cursor.execute(
                        "INSERT INTO pages (website_id, url, title, status_code, content_length, content_type) VALUES (?, ?, ?, ?, ?, ?)",
                        (website_id, url, title, status_code, content_length, content_type)
                    )
                    return cursor.lastrowid

        except Exception as e:
            logger.error(f"Errore durante il salvataggio della pagina '{url}': {e}")
            return None

    def _get_or_create_website(self, domain: str) -> Optional[int]:
        '''
        Funzione: _get_or_create_website
        Recupera l'ID del sito web dal database o lo crea se non esiste.
        '''
        try:
            with self.db_manager.transaction("websites") as cursor:
                # Check if website exists
                cursor.execute("SELECT id FROM websites WHERE domain = ?", (domain,))
                existing_website = cursor.fetchone()
                
                if existing_website:
                    return existing_website['id']
                
                # Create new website
                cursor.execute(
                    "INSERT INTO websites (domain) VALUES (?)",
                    (domain,)
                )
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Errore durante la creazione del website per il dominio '{domain}': {e}")
            return None

    def _save_link_info(self, page_id: int, href: str, anchor_text: str, is_internal: bool) -> None:
        '''
        Funzione: _save_link_info
        Salva le informazioni di un link nel database.
        Parametri formali:
            self -> Riferimento all'instance della classe
            int page_id -> ID della pagina da cui è stato estratto il link
            str href -> URL del link
            str anchor_text -> Testo del link
            bool is_internal -> Indica se il link è interno al dominio
        Valore di ritorno:
            None -> La funzione non restituisce un valore esplicito
        '''
        try:
            with self.db_manager.transaction("websites") as cursor:
                # Check if link already exists
                cursor.execute(
                    "SELECT id FROM links WHERE page_id = ? AND href = ?",
                    (page_id, href)
                )
                existing_link = cursor.fetchone()
                
                if not existing_link:
                    cursor.execute(
                        "INSERT INTO links (page_id, href, anchor_text, is_internal, is_followed) VALUES (?, ?, ?, ?, ?)",
                        (page_id, href, anchor_text, is_internal, 1)
                    )
        except Exception as e:
            logger.error(f"Errore durante il salvataggio del link '{href}' da pagina ID {page_id}: {e}")


    def _save_metadata_info(self, page_id: int, metadata: dict[str, Any]) -> None:
        '''
        Funzione: _save_metadata
        Salva i metadati di una pagina nel database.
        Parametri formali:
            self -> Riferimento all'instance della classe
            int page_id -> ID della pagina a cui si riferiscono i metadati
            dict[str, Any] metadata -> Dizionario dei metadati
        Valore di ritorno:
            None -> La funzione non restituisce un valore esplicito
        '''
        if not metadata:
            return

        try:
            with self.db_manager.transaction("websites") as cursor:
                for name, content in metadata.items():
                    if isinstance(content, (list, dict)):
                        content = json.dumps(content)  # Serialize complex types to JSON string
                    cursor.execute(
                        "INSERT OR IGNORE INTO meta_data (page_id, meta_name, meta_content) VALUES (?, ?, ?)",
                        (page_id, name, str(content))
                    )
        except Exception as e:
            logger.error(f"Errore durante il salvataggio dei metadati per pagina ID {page_id}: {e}")


    def _setup_site_directories(self, domain: str) -> None:
        '''
        Funzione: _setup_site_directories
        Imposta la struttura delle directory locale per salvare i contenuti scaricati di un sito.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            str domain -> Il dominio del sito per cui creare la struttura di directory
        Valore di ritorno:
            None -> La funzione non restituisce un valore
        '''
        if not self.base_dirs.get("downloaded_tree"):
            logger.error("Downloaded tree directory not configured")
            return

        clean_domain = domain.replace('www.', '')

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        site_dir_name = f"{clean_domain}_{timestamp}"

        self.current_site_dir = self.base_dirs["downloaded_tree"] / site_dir_name

        try:
            self.current_site_dir.mkdir(exist_ok=True)

            subdirs = ["html", "images", "documents", "other"]
            for subdir in subdirs:
                (self.current_site_dir / subdir).mkdir(exist_ok=True)

            logger.info(f"Created site directory structure at {self.current_site_dir}")

            latest_link = self.base_dirs["downloaded_tree"] / f"{clean_domain}_latest"
            if latest_link.exists():
                latest_link.unlink()
            elif latest_link.is_dir() and not latest_link.is_symlink():
                 logger.warning(f"'{latest_link}' è una directory, non un symlink. Non verrà sostituita.")
            else:
                try:
                    latest_link.symlink_to(self.current_site_dir, target_is_directory=True)
                except OSError as e_symlink:
                     logger.error(f"Errore creazione symlink '{latest_link}': {e_symlink}")


        except Exception as e:
            logger.error(f"Error creating site directories: {e}")
            self.current_site_dir = None


    def _get_file_path_for_url(self, url: str, content_type_header: str) -> tuple[Path, str]:
        '''
        Funzione: _get_file_path_for_url
        Determina il percorso del file e il nome del file per un URL dato.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            str url -> L'URL del contenuto
            str content_type_header -> Il tipo di contenuto HTTP
        Valore di ritorno:
            tuple[Path, str] -> (directory di salvataggio, nome file)
        '''
        if not self.current_site_dir:
            logger.error("Site directory not initialized")
            return Path("."), "error.html"

        parsed_url = urlparse(url)
        path_components = parsed_url.path.strip("/").split("/")
        
        # Determine the content directory based on content type
        if 'html' in content_type_header or not content_type_header:
            base_dir = self.current_site_dir / "html"
        elif any(ext in content_type_header for ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico']):
            base_dir = self.current_site_dir / "images"
        elif any(ext in content_type_header for ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'csv', 'xml', 'json']):
            base_dir = self.current_site_dir / "documents"
        else:
            base_dir = self.current_site_dir / "other"
        # Create subdirectories based on URL path
        if path_components and path_components[0]:
            current_dir = base_dir
            for component in path_components[:-1]:
                current_dir = current_dir / component
                current_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine filename
            if path_components[-1]:
                file_name = path_components[-1]
                if not '.' in file_name:
                    if 'html' in content_type_header:
                        file_name += '.html'
                    elif 'xml' in content_type_header:
                        file_name += '.xml'
                    elif 'json' in content_type_header:
                        file_name += '.json'
                    else:
                        file_name += '.html'
            else:
                file_name = 'index.html'
        else:
            current_dir = base_dir
            file_name = 'index.html'

        # Sanitize filename
        file_name = "".join(c if c.isalnum() or c in ['.', '-', '_'] else '_' for c in file_name)[:100]
        
        return current_dir, file_name

    def _save_robots_data(self, website_id: int, robots_data: RobotsData, robots_content: str) -> Optional[int]:
        """Save robots.txt data to database"""
        try:
            with self.db_manager.transaction("websites") as cursor:
                # Save robots.txt content and metadata using REPLACE
                cursor.execute(
                    "INSERT OR REPLACE INTO robots_txt (website_id, content, crawl_delay) VALUES (?, ?, ?)",
                    (website_id, robots_content, robots_data.crawl_delay)
                )
                robots_txt_id = cursor.lastrowid

                # Save rules
                for rule in robots_data.rules:
                    cursor.execute(
                        "INSERT INTO robots_rules (robots_txt_id, path, allow, is_sensitive) VALUES (?, ?, ?, ?)",
                        (robots_txt_id, rule.path, rule.allow, rule.is_sensitive)
                    )

                # Save sitemaps
                for sitemap in robots_data.sitemaps:
                    cursor.execute(
                        "INSERT OR REPLACE INTO robots_sitemaps (robots_txt_id, url) VALUES (?, ?)",
                        (robots_txt_id, sitemap)
                    )

                return robots_txt_id

        except Exception as e:
            logger.error(f"Error saving robots.txt data: {e}")
            return None

    def _fetch_and_parse_robots(self, base_url: str, queue: deque) -> Optional[RobotsData]:
        """Fetch and parse robots.txt for a given domain"""
        robots_url = urljoin(base_url, "/robots.txt")
        logger.info(f"Fetching robots.txt from {robots_url}")
        
        robots_content = self.fetcher.fetch(robots_url)
        if not robots_content:
            logger.warning(f"No robots.txt found at {robots_url}")
            return None
            
        robots_data = self.robots_parser.parse(robots_content, base_url)
        self.robots_parser.print_analysis(robots_data, base_url)
        
        # Interactive choice for robots.txt compliance
        while True:
            print(f"\n{Fore.YELLOW}Do you want to respect robots.txt rules?{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}y{Style.RESET_ALL} - Yes, follow robots.txt rules (ethical)")
            print(f"  {Fore.RED}n{Style.RESET_ALL} - No, ignore robots.txt rules and crawl restricted paths")
            choice = input(f"\nYour choice (y/n): ").strip().lower()
            
            if choice in ['y', 'n']:
                self.respect_robots = (choice == 'y')
                if not self.respect_robots:
                    print(f"\n{Fore.RED}Warning: robots.txt rules will be ignored. This may be against the site's terms of service.{Style.RESET_ALL}")
                    
                    # Add only concrete disallowed paths (no wildcards) to crawl queue
                    disallowed_paths = [rule.path for rule in robots_data.rules 
                                      if not rule.allow and '*' not in rule.path and '?' not in rule.path]
                    
                    if disallowed_paths:
                        print(f"\n{Fore.YELLOW}Adding {len(disallowed_paths)} restricted paths to crawl queue:{Style.RESET_ALL}")
                        for path in disallowed_paths:
                            target_url = urljoin(base_url, path)
                            if path.endswith('/'):  # È una directory
                                print(f"  {Fore.BLUE}[DIR]{Style.RESET_ALL} {target_url}")
                            else:
                                print(f"  {Fore.MAGENTA}[FILE]{Style.RESET_ALL} {target_url}")
                            queue.append((target_url, 0))  # Aggiungi con profondità 0 per assicurare l'esplorazione
                        
                        # Se ci sono path sensibili, evidenziali in modo speciale
                        sensitive_paths = [path for path in disallowed_paths 
                                         if any(rule.path == path and rule.is_sensitive for rule in robots_data.rules)]
                        if sensitive_paths:
                            print(f"\n{Fore.RED}🔒 Found {len(sensitive_paths)} sensitive paths to explore:{Style.RESET_ALL}")
                            for path in sensitive_paths:
                                target_url = urljoin(base_url, path)
                                print(f"  {Fore.RED}[SENSITIVE]{Style.RESET_ALL} {target_url}")
                break
            else:
                print(f"\n{Fore.RED}Invalid choice. Please enter 'y' or 'n'.{Style.RESET_ALL}")
        
        # Save to database if we're in download mode
        website_id = self._get_or_create_website(self.base_domain)
        if website_id:
            self._save_robots_data(website_id, robots_data, robots_content)
        
        return robots_data

    def _should_crawl_url(self, url: str) -> bool:
        """Check if a URL should be crawled based on robots.txt rules"""
        if not self.respect_robots or not self.robots_data:
            return True
            
        return self.robots_parser.is_allowed(url, self.robots_data.rules)

    def start_crawl(self, start_url: str, depth_limit: int = 2, politeness_delay: float = 1.0, perform_osint_on_pages: bool = False, save_to_disk: bool = True) -> dict:
        '''
        Funzione: start_crawl
        Avvia il processo di crawling web a partire da un URL dato, con limite di profondità e opzioni per modalità.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            str start_url -> L'URL da cui iniziare il crawling
            int depth_limit -> Il limite massimo di profondità del crawling
            float politeness_delay -> Il ritardo in secondi tra le richieste per rispettare la politeness
            bool perform_osint_on_pages -> Se True, esegue la profilazione OSINT su ogni pagina scaricata
            bool save_to_disk -> Se True, salva i file su disco nella struttura downloaded_tree
        Valore di ritorno:
            dict -> Dizionario contenente statistiche riassuntive del crawling
        '''
        stats = {
            'urls_visited': 0,
            'pages_saved': 0,
            'download_path': None,
            'errors': 0,
            'robots_txt': None,
            'restricted_paths_crawled': 0
        }
        osint_findings_summary = {
            "entities_profiled": [],
            "page_technologies": {}
        }

        self.base_domain = urlparse(start_url).netloc
        if not self.base_domain:
            logger.error(f"URL di partenza non valido, impossibile estrarre base_domain: {start_url}")
            stats['errors'] +=1
            return stats

        # Setup directory structure only if we're saving to disk
        if save_to_disk:
            self._setup_site_directories(self.base_domain)
            if not self.current_site_dir:
                logger.error(f"Impossibile creare la struttura delle directory per {self.base_domain}. Crawling interrotto.")
                stats['errors'] +=1
                return stats
            stats['download_path'] = str(self.current_site_dir)
            print(f"Content will be saved to: {self.current_site_dir}{Style.RESET_ALL}\n")

        print(f"\n{Fore.CYAN}Starting crawl of {start_url} (Mode: {'OSINT' if perform_osint_on_pages else 'Download'})")

        queue = deque([(start_url, 0)])
        self.visited_urls.clear()

        # Fetch and parse robots.txt
        self.robots_data = self._fetch_and_parse_robots(start_url, queue)
        if self.robots_data:
            stats['robots_txt'] = self.robots_data.to_dict()
            if self.robots_data.crawl_delay > politeness_delay:
                logger.info(f"Adjusting politeness delay to match robots.txt crawl-delay: {self.robots_data.crawl_delay}s")
                politeness_delay = self.robots_data.crawl_delay

        # Initialize appropriate database schema based on mode
        if perform_osint_on_pages:
            self.db_manager.init_schema("osint")
        else:
            self.db_manager.init_schema("websites")

        while queue:
            current_url, current_depth = queue.popleft()

            if current_url in self.visited_urls:
                continue

            if current_depth > depth_limit:
                logger.debug(f"Raggiunto limite profondità per: {current_url}")
                continue

            # Check robots.txt rules
            if not self._should_crawl_url(current_url):
                logger.info(f"Skipping {current_url} (blocked by robots.txt)")
                continue

            print(f"{Fore.YELLOW}Crawling{Style.RESET_ALL}: {current_url} (Profondità: {current_depth})")
            self.visited_urls.add(current_url)
            stats['urls_visited'] += 1

            time.sleep(politeness_delay)
            page_response = self.fetcher.fetch_full_response(current_url)

            if not page_response or not page_response.content:
                logger.warning(f"Nessun contenuto scaricato per {current_url}. Status: {page_response.status_code if page_response else 'N/A'}")
                stats['errors'] += 1
                continue

            page_content_bytes = page_response.content
            page_content_text = None
            content_type_header = page_response.headers.get('Content-Type', '').lower()

            # Save file to disk only in download mode
            if save_to_disk and not perform_osint_on_pages:
                try:
                    save_dir, file_name = self._get_file_path_for_url(current_url, content_type_header)
                    save_path = save_dir / file_name
                    save_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(save_path, 'wb') as f:
                        f.write(page_content_bytes)
                    stats['pages_saved'] += 1
                    logger.info(f"Pagina '{current_url}' salvata in '{save_path}'")

                except Exception as e:
                    logger.error(f"Errore salvataggio {current_url} in {save_path if 'save_path' in locals() else 'N/A'}: {e}", exc_info=True)
                    stats['errors'] += 1

            parsed_data = {}
            page_id = None

            if any(ct in content_type_header for ct in ['html', 'xml', 'text', 'json']):
                try:
                    encoding_to_try = page_response.encoding if page_response.encoding else 'utf-8'
                    page_content_text = page_content_bytes.decode(encoding_to_try, errors='replace')
                    parsed_data = self.parser.parse(page_content_text, current_url)

                    # Save to websites database only in download mode
                    if not perform_osint_on_pages:
                        page_id = self._save_page_info(
                            url=current_url,
                            title=parsed_data.get("title", ""),
                            status_code=page_response.status_code,
                            content_length=len(page_content_bytes),
                            content_type=content_type_header
                        )

                        if page_id and parsed_data.get("metadata"):
                            self._save_metadata_info(page_id, parsed_data["metadata"])

                except Exception as e_parse_decode:
                    logger.warning(f"Errore decodifica/parsing contenuto per {current_url} (Content-Type: {content_type_header}): {e_parse_decode}")

            # Process links for both modes (OSINT and Download)
            if parsed_data and "links" in parsed_data and current_depth < depth_limit:
                for link_info in parsed_data["links"]:
                    if not (link_url := link_info.get("url")):
                        continue

                    if not (normalized_link := self._normalize_url(link_url, current_url)):
                        continue

                    is_internal = self._is_internal_url(normalized_link)
                    
                    # In download mode, save link info to database
                    if not perform_osint_on_pages and page_id:
                        self._save_link_info(page_id, normalized_link, link_info.get("text", ""), is_internal)

                    # For both modes, add internal links to queue
                    if is_internal and normalized_link not in self.visited_urls:
                        if len(queue) < 2000:
                            queue.append((normalized_link, current_depth + 1))
                        else:
                            logger.warning(f"Coda crawler piena, link ignorato: {normalized_link}")

            # Process page content for OSINT mode
            if perform_osint_on_pages and page_content_text and self.osint_extractor:
                print(f"    {Fore.MAGENTA}Avvio OSINT per pagina: {current_url}{Style.RESET_ALL}")

                try:
                    page_emails = extract_emails(page_content_text)
                    page_phones = extract_phone_numbers(page_content_text)
                    filtered_emails = filter_emails(page_emails, self.base_domain, logger)
                    filtered_phones = filter_phone_numbers(page_phones)

                    for email in filtered_emails:
                        if email not in self.already_profiled_in_session:
                            print(f"      {Fore.BLUE}Profilazione email trovata: {email}{Style.RESET_ALL}")
                            email_profile_result = self.osint_extractor.profile_email(email)
                            osint_findings_summary["entities_profiled"].append({
                                "page_url": current_url,
                                "entity_type": "email",
                                "entity": email,
                                "profile_details": email_profile_result
                            })
                            self.already_profiled_in_session.add(email)
                        else:
                            logger.debug(f"Email {email} già profilata in questa sessione.")

                    if filtered_phones:
                        osint_findings_summary["entities_profiled"].append({
                            "page_url": current_url,
                            "entity_type": "phone_numbers_found",
                            "entity": list(filtered_phones),
                            "profile_details": {"message": "Numeri di telefono estratti dalla pagina."}
                        })

                    # Detect technologies
                    page_tech = {}
                    soup_from_parser = BeautifulSoup(page_content_text, 'html.parser')

                    tech_frameworks = detect_framework(soup_from_parser, page_response.headers, page_content_text, current_url)
                    tech_js = detect_js_libraries(soup_from_parser, page_content_text)
                    tech_analytics = detect_analytics(page_content_text)

                    if tech_frameworks and tech_frameworks != "Unknown" and tech_frameworks != []: page_tech["framework_cms"] = tech_frameworks
                    if tech_js: page_tech["js_libraries"] = tech_js
                    if tech_analytics: page_tech["analytics"] = tech_analytics

                    if page_tech:
                        osint_findings_summary["page_technologies"][current_url] = page_tech

                except Exception as e_osint:
                    logger.error(f"Errore durante l'analisi OSINT per {current_url}: {e_osint}", exc_info=True)

        if perform_osint_on_pages:
            # Cerca profili social per il dominio/brand alla fine del crawling
            try:
                from scraper.utils.osint_sources import find_brand_social_profiles
                
                # Pulizia del nome del dominio per la ricerca social
                clean_brand = self.base_domain.lower()
                clean_brand = clean_brand.replace('www.', '')
                
                # Rimuovi estensioni comuni dei domini
                common_tlds = ['.com', '.it', '.org', '.net', '.edu', '.gov', '.io', '.co.uk', '.eu', '.info', '.biz']
                for tld in common_tlds:
                    if clean_brand.endswith(tld):
                        clean_brand = clean_brand[:-len(tld)]
                        break
                
                # Prendi solo la prima parte del dominio
                clean_brand = clean_brand.split('.')[0]
                
                print(f"\n{Fore.CYAN}Ricerca profili social per il brand '{clean_brand}' (dominio: {self.base_domain})...{Style.RESET_ALL}")
                social_results = find_brand_social_profiles(clean_brand, logger, self.base_dirs)
                
                if social_results and not social_results.get("error"):
                    profiles = social_results.get("profiles", {})
                    if profiles:
                        print(f"{Fore.YELLOW}✓ Trovati {len(profiles)} possibili profili social{Style.RESET_ALL}")
                        
                        # Aggiungi ogni profilo trovato alla lista delle entità
                        for platform, data in profiles.items():
                            osint_findings_summary["entities_profiled"].append({
                                "page_url": start_url,
                                "entity_type": "social_profile",
                                "entity": data.get("username", clean_brand),
                                "profile_details": {
                                    "platform": platform,
                                    "url": data.get("url"),
                                    "confidence": f"{data.get('confidence', 1.0) * 100:.1f}%"
                                }
                            })
                    else:
                        print(f"{Fore.YELLOW}Nessun profilo social trovato per '{clean_brand}'{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"Errore durante la ricerca dei profili social per {self.base_domain}: {e}", exc_info=True)
            
            stats['osint_summary'] = osint_findings_summary

        return stats