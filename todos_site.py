import curses
import random
import typing
import datetime
import pickle

from time import sleep
from utils import copy2clip, to_str, WhenItsMoreThanIstMore, iota, len_of_words, word_split
from typing import List, Dict, Literal, Tuple, Optional, Union, Any
from curses.textpad import Textbox, rectangle

from menu import CursesMenu

def menu(is_todo=True) -> Optional[str]:
    menu: dict = {"title": "Menu", "type": "menu", "subtitle": "Todos menu"}
    opitions: List[Dict[str, Optional[str]]] = []
    
    opitions.append({"title": "ADD TASK", "type": "add", "command": "echo add"}) # option_1

    if is_todo:
        opitions.append({"title": "VIEW TODO LIST", "type": "view", "command": "echo view"}) # option_2
    else:
        opitions.append({"title": "VIEW TODO LIST - no todos", "type": None}) # option_2

    menu["options"] = [*opitions]

    m = CursesMenu(menu)
    selected_action: Dict[str, str] = m.display()
    return selected_action["type"]


def add_todo(title: str, subtasks: str) -> None:
    subtasks: List[str] = subtasks.split("--")
    subtasks = [task.rstrip().lstrip() for task in subtasks]
    params = [title, subtasks, datetime.datetime.now()]
    keys = list(loaded_todos.keys())
    if keys:
        id = keys[-1]
    else:
        id = -1
    loaded_todos[id+1] = params


def add_site(stdscr, msg: str = "") -> None:
    # TODO add copiing text
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(1)
    stdscr.clear()

    stdscr.addstr(0, curses.COLS - len(msg) - 1, msg)

    stdscr.addstr(2, 2, "Here write your title and then subtasks:")

    stdscr.addstr(16, 15, "'--' char is for new subtask")
    stdscr.addstr(18, 15, "For confirm Ctrl+G + Any")

    stdscr.refresh()
    curses.echo()

    rectangle(stdscr, 1, 42, 3, 95)
    rectangle(stdscr, 3, 19, 14, 95)
    title: str = to_str(stdscr.getstr(2, 43, 52))
    curses.noecho()
    rectangle(stdscr, 1, 42 , 3, 95)
    rectangle(stdscr, 3, 19, 14, 95)

    stdscr.refresh()

    quote_win = curses.newwin(10, 75, 4, 20)
    text_box = Textbox(quote_win, insert_mode=True)
    curses.curs_set(2)
    text: str = text_box.edit()

    curses.curs_set(0)
    stdscr.getch()
    curses.curs_set(1)
    stdscr.refresh()
    add_todo(title, text)


def main(stdscr, name: str) -> None:
    
    global loaded_todos
    
    f = open("todos.pickle", "a+")
    f.close()
    todo_file = open("todos.pickle", "rb")
    try:
        loaded_todos = pickle.load(todo_file)
    except EOFError:
        loaded_todos = {}
    todo_file.close()
    curses.curs_set(1)

    while True:
        stdscr.clear()
        stdscr.refresh()
        is_any_task: bool = True    
        if loaded_todos == {}:
            is_any_task: bool = False
            

        action: str = menu(is_any_task)
        if action == "view":
            view_site(stdscr, name)
        elif action == "add":
            add_site(stdscr)
        elif action == "exitmenu":
            todo_file = open("todos.pickle", "wb") 
            pickle.dump(loaded_todos, todo_file)
            todo_file.close()
            exit()