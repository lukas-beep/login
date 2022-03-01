import curses
import uuid
import random
from sqlite3.dbapi2 import Connection
import typing
import sqlite3

from utils import copy2clip
from typing import List, Dict, Tuple, Optional, Union
from curses.textpad import Textbox, rectangle

from menu import CursesMenu


def menu() -> str:
    menu: dict = {"title": "Menu", "type": "menu", "subtitle": "quotes menu"}

    option_1: dict = {"title": "POST QUOTE", "type": "post", "command": "echo post"}

    option_2: dict = {"title": "VIEW QUOTES", "type": "view", "command": "echo view"}

    menu["options"] = [option_1, option_2]

    m = CursesMenu(menu)
    selected_action: Dict[str, str] = m.display()
    return selected_action["type"]


def next_quote() -> List[str]:
    quotes = cursor.execute("SELECT author, content FROM quotes WHERE official = 1").fetchall()
    quote = random.choice(quotes)
    quote = {"author": quote[0], "quote": quote[1]}
    return quote


def main_site(stdscr):
    quote: List[str, str] = next_quote()

    while True:
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr(10, 10, quote["quote"])
        try:
            stdscr.addstr(
                curses.LINES - 5, curses.COLS - len(quote["author"]) - 4, "-- " + quote["author"]
            )
        except IndexError:
            print(quote)

        key: int = stdscr.getch()
        if key == 10:  # ENTER
            quote = next_quote()
        elif key == 115:  # s
            stdscr.addstr(
                1, curses.COLS - len((msg := "Search func comming soon")) - 1, msg
            )
        elif key == 113:  # q
            break
    stdscr.refresh()


def add_quote(name: str, quote: str):
    params = [1 , name, "\u201c" + quote.rstrip() + "\u201d"]
    cursor.execute("INSERT INTO quotes (official, author, content) VALUES (?, ?, ?)", params)
    connection.commit()


def post_site(stdscr, name: str, msg: str = "", copyed_text: bool = False):
    stdscr.clear()
    stdscr.refresh()
    stdscr.clear()

    stdscr.addstr(0, curses.COLS - len(msg) - 1, msg)
    if copyed_text:
        stdscr.addstr(
            1, curses.COLS - len((msg := "The text was copyed to clipboard")) - 1, msg
        )
    stdscr.addstr(2, 2, "Here write your quote:")
    stdscr.addstr(18, 15, "For confirm Ctrl+G + Any")
    rectangle(stdscr, 3, 15, 14, 86)
    stdscr.refresh()

    quote_win = curses.newwin(10, 70, 4, 16,)
    text_box = Textbox(quote_win, insert_mode=True)
    curses.curs_set(2)
    text: str = text_box.edit()

    curses.curs_set(0)
    stdscr.getch()
    if len(text) <= 10:
        copy2clip(text)
        post_site(stdscr, name, msg="can't have less than 11 chars", copyed_text=True)

    elif "     " in text:
        copy2clip(text)
        post_site(
            stdscr,
            name,
            msg="can't have empty/more than 5 spaces at one spot",
            copyed_text=True,
        )
    else:
        curses.curs_set(1)
        stdscr.refresh()
        add_quote(name, text)


def main(stdscr, name: str):
    global cursor, connection
    connection = sqlite3.connect("quotes.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, official INTEGER, author TEXT, content TEXT)"
    )
    connection.commit()
    curses.curs_set(1)
    while True:
        stdscr.clear()
        stdscr.refresh()
        action: str = menu()
        if action == "view":
            main_site(stdscr)
        elif action == "post":
            post_site(stdscr, name)
        elif action == "exitmenu":
            connection.close()
            break


# TODO LATER use typing module to simplyfi code to read by other person(module typing)
# TODO do a func that search in view site(def main_site) for quotes filtered by name(def search_quote_by_name)
