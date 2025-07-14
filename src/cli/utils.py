"""
Utility functions for the Browsint CLI application.
"""
import os
from datetime import datetime
import json
from colorama import Fore, Style

def json_serial(obj):
    '''
    Serializza oggetti non serializzabili di default in JSON.
    Parametri formali:
        object obj -> Oggetto da serializzare
    Valore di ritorno:
        any -> Rappresentazione serializzabile dell'oggetto o eccezione TypeError
    '''
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def clear_screen():
    '''Cancella la console per una migliore visualizzazione.'''
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

def prompt_for_input(prompt: str) -> str:
    '''Chiede un input all'utente con un prompt formattato.'''
    return input(f"\n{Fore.CYAN}{prompt}{Style.RESET_ALL}").strip()

def confirm_action(message: str, default_yes: bool = True) -> bool:
    '''Chiede conferma all'utente per un'azione.'''
    options = "(S/n)" if default_yes else "(s/N)"
    choice = prompt_for_input(f"{Fore.YELLOW}{message} {options}: {Style.RESET_ALL}")

    if default_yes:
        return choice.lower() in ('s', '')
    else:
        return choice.lower() == 's' 


def export_menu() -> str:
    print(f"{Fore.BLUE}\nScegli il formato di esportazione:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} JSON")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} HTML")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} PDF")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Tutti")
    print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Annulla")
    return prompt_for_input("Scelta: ").strip()
