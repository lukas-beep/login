import curses
import random
import typing
import datetime
import pickle
import sys

from time import sleep

from typing import List, Dict, Literal, Tuple, Optional, Union, Any
from curses.textpad import Textbox, rectangle

from utils import *

from sites.stats.corona_site import main as corona_site

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

def main(stdscr, name):
    while True:
        stdscr.clear()
        stdscr.refresh()
        action: str = stats_menu(stdscr)
        if action == "covid":
            corona_site(stdscr, name)
        elif action == "exitmenu":
            return