import curses
import typing
import sqlite3
import mysql.connector
import json
import sys

from utils.utils import to_str, isvalidEmail, SPACE
from typing import List, Dict, Tuple, Optional, Union
from curses.textpad import rectangle

from corona_site import main as corona_site

from utils.menu import CursesMenu

def stats_menu(stdscr):
    menu: dict = {
        "title": "Stats Menu",
        "type": "menu",
        "subtitle": "Chosse what stats do you want to see ",
    }

    option_1: dict = {
        "title": "COVID-19",
        "type": "covid",
        "command": "echo covid",
    }
    # add here when more funcionalities

    menu["options"] = [
        option_1,
    ]  # add to this list when more funcionalities

    m = CursesMenu(menu)
    selected_action: Dict[str, str] = m.display()
    return selected_action["type"]

def main(stdscr):
    while True:
        stdscr.clear()
        stdscr.refresh()
        action: str = stats_menu()
        if action == "covid":
            corona_site(stdscr)
            break
        elif action == "exitmenu":
            sys.exit()