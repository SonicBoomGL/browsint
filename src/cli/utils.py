"""
Utility functions for the Browsint CLI application.
"""
import os
from datetime import datetime
import json
from colorama import Fore, Style

def json_serial(obj):
    '''
    Funzione: json_serial
    Serializza oggetti non serializzabili di default in JSON.
    Parametri formali:
        object obj -> Oggetto da serializzare
    Valore di ritorno:
        any -> Rappresentazione serializzabile dell'oggetto o eccezione TypeError
    '''
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)  # Converte i set in liste
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
    return input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}").strip()

def confirm_action(message: str, default_yes: bool = True) -> bool:
    '''Chiede conferma all'utente per un'azione.'''
    options = "(S/n)" if default_yes else "(s/N)"
    choice = prompt_for_input(f"{Fore.YELLOW}{message} {options}: {Style.RESET_ALL}")

    if default_yes:
        return choice.lower() in ('s', '')
    else:
        return choice.lower() == 's' 