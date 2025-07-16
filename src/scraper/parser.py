import json
import logging
from typing import Any, Dict, List, Optional, TypedDict
from urllib.parse import urljoin, urlparse, unquote

from bs4 import BeautifulSoup

logger = logging.getLogger("scraper.parser")

class LinkInfo(TypedDict):
    '''
    Funzione: LinkInfo
    Rappresenta le informazioni su un link estratto da una pagina web.
    Attributi:
        TypedDict -> Classe per rappresentare un dizionario con tipi specifici
    Parametri formali:
        str url -> URL del link
        str text -> Testo di ancoraggio del link
        str rel -> Relazione del link (es. "nofollow", "noopener")
        bool is_internal -> Indica se il link è interno al dominio della pagina
    '''
    url: str
    text: str
    rel: str
    is_internal: bool # ìCampo aggiunto per corrispondere all'uso del crawler

class ExtractedData(TypedDict):
    '''
    Funzione: ExtractedData
    Rappresenta i dati estratti da una pagina web.
    Attributi:
        TypedDict -> Classe per rappresentare un dizionario con tipi specifici
    Parametri formali:
        str url -> URL della pagina
        str title -> Titolo della pagina
        str description -> Descrizione della pagina
        str content -> Contenuto testuale principale della pagina
        list[LinkInfo] links -> Lista di link estratti dalla pagina
        dict[str, Any] metadata -> Metadati estratti dalla pagina (es. dati strutturati)
        int content_length -> Lunghezza del contenuto in byte
        Optional[str] lang -> Lingua della pagina (attributo 'lang' del tag <html>)
        Optional[str] canonical_url -> URL canonico della pagina (se presente)
        int image_count -> Numero di immagini nella pagina
        int css_count -> Numero di fogli di stile CSS nella pagina
        int js_count -> Numero di script JavaScript nella pagina
        int internal_links_count -> Numero di link interni alla pagina
        int external_links_count -> Numero di link esterni alla pagina
    '''

    url: str
    title: str
    description: str
    content: str
    links: list[LinkInfo]
    metadata: dict[str, Any]
    content_length: int
    lang: Optional[str]
    canonical_url: Optional[str]
    image_count: int
    css_count: int
    js_count: int
    internal_links_count: int
    external_links_count: int


class WebParser:
    '''
    Funzione: WebParser
    Classe per l'analisi e l'estrazione di dati strutturati da pagine HTML.
    Parametri formali:
        self -> Riferimento all'istanza della classe
        dict[str, dict[str, Any]] | None extraction_rules -> Dizionario con regole di estrazione personalizzate
    '''

    def __init__(self, extraction_rules: dict[str, dict[str, Any]] | None = None) -> None:
        self.extraction_rules = extraction_rules or {}

    def parse(self, html: str, url: str, encoding: str = "utf-8") -> ExtractedData:
        '''
        Funzione: parse
        Analizza il contenuto HTML di una pagina e estrae le informazioni rilevanti.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            str html -> Contenuto HTML da analizzare
            str url -> URL di origine (necessario per risolvere link relativi e determinare interni/esterni)
            str encoding -> Codifica del testo HTML
        Valore di ritorno:
            ExtractedData -> Dizionario contenente i dati estratti dalla pagina
        '''
        
        if not html:
            logger.warning("HTML vuoto, impossibile effettuare il parsing")
            return {
                "url": url,
                "error": "HTML vuoto",
                "title": "",
                "description": "",
                "content": "",
                "links": [],
                "metadata": {},
                "content_length": 0,
                "lang": None,
                "canonical_url": None,
                "image_count": 0,
                "css_count": 0,
                "js_count": 0,
                "internal_links_count": 0,
                "external_links_count": 0
            }

        try:
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html, "html.parser", from_encoding=encoding)

            # Extract basic data
            links = self._extract_links(soup, url)
            internal_links_count = sum(1 for link in links if link["is_internal"])
            external_links_count = len(links) - internal_links_count

            # Extract new metadata
            content_length = len(html.encode(encoding))
            lang_attr = soup.html.get('lang') if soup.html else None
            
            canonical_link = soup.find("link", attrs={"rel": "canonical"})
            canonical_url = canonical_link.get("href") if canonical_link else None

            # Count elements
            image_count = len(soup.find_all("img"))
            css_count = len(soup.find_all("link", rel="stylesheet"))
            js_count = len(soup.find_all("script", src=True))

            data: ExtractedData = {
                "url": url,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "content": self._extract_content(soup),
                "links": links,
                "metadata": self._extract_metadata(soup),
                "content_length": content_length,
                "lang": lang_attr,
                "canonical_url": canonical_url,
                "image_count": image_count,
                "css_count": css_count,
                "js_count": js_count,
                "internal_links_count": internal_links_count,
                "external_links_count": external_links_count
            }

            # Apply custom extraction rules
            for field, rule in self.extraction_rules.items():
                data[field] = self._apply_extraction_rule(soup, rule)

            return data

        except UnicodeDecodeError:
            logger.error(f"Errore di codifica per {url}")
            return {
                "url": url,
                "error": "Errore di codifica",
                "title": "",
                "description": "",
                "content": "",
                "links": [],
                "metadata": {},
                "content_length": 0,
                "lang": None,
                "canonical_url": None,
                "image_count": 0,
                "css_count": 0,
                "js_count": 0,
                "internal_links_count": 0,
                "external_links_count": 0
            }
        except Exception as e:
            logger.error(f"Errore durante il parsing di {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "title": "",
                "description": "",
                "content": "",
                "links": [],
                "metadata": {},
                "content_length": 0,
                "lang": None,
                "canonical_url": None,
                "image_count": 0,
                "css_count": 0,
                "js_count": 0,
                "internal_links_count": 0,
                "external_links_count": 0
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        '''
        Funzione: _extract_title
        Estrae il titolo della pagina web dal tag <title> o <h1>.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            BeautifulSoup soup -> Oggetto BeautifulSoup della pagina
        Valore di ritorno:
            str -> Il titolo della pagina o una stringa vuota
        '''
        if soup.title:
            return soup.title.text.strip()

        h1 = soup.find("h1")
        if h1:
            return h1.text.strip()

        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        '''
        Funzione: _extract_description
        Estrae la descrizione della pagina web dai meta tag 'description' o 'og:description'.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            BeautifulSoup soup -> Oggetto BeautifulSoup della pagina
        Valore di ritorno:
            str -> La descrizione della pagina o una stringa vuota
        '''
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()

        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()

        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        '''
        Funzione: _extract_content
        Estrae il contenuto testuale principale della pagina utilizzando euristiche.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            BeautifulSoup soup -> Oggetto BeautifulSoup della pagina
        Valore di ritorno:
            str -> Il contenuto testuale principale o tutto il testo della pagina come fallback
        '''
        content_candidates = [
            soup.find("article"),
            soup.find("main"),
            soup.find("div", class_=["content", "main-content", "post-content", "article-content"]),
            soup.find(id=["content", "main-content", "post-content", "article-content"]),
        ]

        for candidate in content_candidates:
            if candidate:
                return candidate.get_text(separator="\n", strip=True)

        paragraphs = soup.find_all("p")
        if paragraphs:
            return "\n".join([p.get_text(strip=True) for p in paragraphs])

        return soup.get_text(separator="\n", strip=True)

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[LinkInfo]:
        '''
        Funzione: _extract_links
        Estrae tutti i link presenti nella pagina HTML.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            BeautifulSoup soup -> Oggetto BeautifulSoup della pagina
            str base_url -> URL base per risolvere link relativi e determinare se sono interni
        Valore di ritorno:
            list[LinkInfo] -> Lista di dizionari contenenti le informazioni sui link
        '''
        links: list[LinkInfo] = []
        base_domain = urlparse(base_url).netloc # Determine base domain for internal check

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("#"):
                continue

            abs_url = urljoin(base_url, href)
            # Optional: Normalize the absolute URL further if needed (e.g., remove session IDs)
            # abs_url = self._normalize_url(abs_url) # Requires adding a separate normalization method

            anchor_text = a_tag.get_text(strip=True)

            # Determine if the link is internal
            try:
                parsed_link_url = urlparse(abs_url)
                is_internal = parsed_link_url.netloc == base_domain
            except Exception:
                is_internal = False # Assume external if parsing fails

            links.append(
                {
                    "url": unquote(abs_url), # Decode URL-encoded characters
                    "text": anchor_text or "",
                    "rel": a_tag.get("rel", ""),
                    "is_internal": is_internal # Add the internal/external status
                }
            )

        return links

    def _extract_metadata(self, soup: BeautifulSoup) -> dict[str, Any]:
        '''
        Funzione: _extract_metadata
        Estrae metadati dai tag <meta> e dati strutturati (JSON-LD) dalla pagina.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            BeautifulSoup soup -> Oggetto BeautifulSoup della pagina
        Valore di ritorno:
            dict[str, Any] -> Dizionario contenente i metadati estratti
        '''
        metadata: dict[str, Any] = {}

        # Seach for meta tags with name or property attributes 
        # and content attribute, which are common for metadata
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            if name and meta.get("content"):
                metadata[name] = meta["content"]

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                json_data = json.loads(script.string)
                metadata["structured_data"] = json_data
            except:
                pass

        return metadata

    def _apply_extraction_rule(self, soup: BeautifulSoup, rule: dict[str, Any]) -> Any:
        '''
        Funzione: _apply_extraction_rule
        Applica una regola di estrazione personalizzata al contenuto HTML.
        Parametri formali:
            self -> Riferimento all'istanza della classe
            BeautifulSoup soup -> Oggetto BeautifulSoup della pagina
            dict[str, Any] rule -> Dizionario contenente le regole di estrazione
        Valore di ritorno:
            Any -> Il dato estratto in base alla regola, o None se la regola non è valida o non trova elementi
        '''
        if not rule:
            return None
        # If a function is provided in the rule, call it with the soup object
        if callable(rule.get("function")):
            return rule["function"](soup)

        selector = rule.get("selector")
        attribute = rule.get("attribute", "text")
        multiple = rule.get("multiple", False)

        if not selector:
            return None

        if multiple:
            elements = soup.select(selector)
            if attribute == "text":
                return [el.get_text(strip=True) for el in elements]
            else:
                return [el.get(attribute, "") for el in elements]
        else:
            element = soup.select_one(selector)
            if not element:
                return None

            if attribute == "text":
                return element.get_text(strip=True)
            else:
                return element.get(attribute, "")