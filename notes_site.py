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


def menu(is_note=True) -> str:
    menu: dict = {"title": "Menu", "type": "menu", "subtitle": "Notes menu"}
    opitions: List[Dict[str, Optional[str]]] = []
    
    opitions.append({"title": "ADD NOTE", "type": "add", "command": "echo add"}) # option_1

    if is_note:
        opitions.append({"title": "VIEW NOTES", "type": "view", "command": "echo view"}) # option_2
    else:
        opitions.append({"title": "VIEW NOTES - no notes", "type": None}) # option_2

    menu["options"] = [*opitions]

    m = CursesMenu(menu)
    selected_action: Dict[str, str] = m.display()
    return selected_action["type"]


def view_note(stdscr, id: int, notes_idxs: List[int], notes: List[list]) -> bool:

    stdscr.clear()
    stdscr.refresh()
    stdscr.clear()

    note: list = notes[notes_idxs.index(id)]
    # note[0]: str
    # note[1]: str
    # note[2]: tuple | datetime
    # note[3]: int

    stdscr.addstr(2, 38 - len((msg := "Here is title:")), msg)
    stdscr.addstr(2, 39, note[0])

    note_content: str = note[1].split("\n")
    for i, line in enumerate(note_content):
        if "\\n" in line:
            stdscr.addstr(4 + i, 16, " "*10)
        else:
            stdscr.addstr(4 + i, 16, line)

    rectangle(stdscr, 1, 38, 3, 86)
    rectangle(stdscr, 3, 15, 14, 86)

    stdscr.refresh()
    while True:
        key: int = stdscr.getch()
        if key == ord("q"):
            stdscr.clear()
            return True
    return False


def clear_input_area(stdscr):
    half: int = WhenItsMoreThanIstMore(curses.COLS / 2)
    stdscr.hline(0, half, " ", half)
    stdscr.hline(1, half, " ", half)
    stdscr.hline(2, half, " ", half)
    stdscr.refresh()


def delete_note(id: int) -> bool:
    loaded_notes.pop(id)
    return True


def edit_note(id: int, title: str, content: str) -> bool:
    params: list = [title, content, datetime.datetime.now()]
    loaded_notes[id] = params
    return True


def view_edit_note(stdscr, id: int, notes_idxs: list, notes: List[list]) -> bool:
    #TODO: do dynamic writing in note with pygui
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(1)
    stdscr.clear()

    note: list = notes[id]
    # note[0]: str
    # note[1]: str
    # note[2]: tuple | datetime
    # note[3]: int

    stdscr.addstr(18, 74, note[0])
    note_content: str = note[1].split("\n")
    for i, line in enumerate(note_content):
        stdscr.addstr(20 + i, 51, line)
    rectangle(stdscr, 17, 73, 19, 121)
    rectangle(stdscr, 19, 50, 30, 121)

    stdscr.addstr(2, 2, "Here write your title and then note:")

    stdscr.addstr(18, 15, "For confirm Ctrl+G + Any")

    stdscr.refresh()
    curses.echo()

    rectangle(stdscr, 1, 38, 3, 86)
    rectangle(stdscr, 3, 15, 14, 86)
    title: str = to_str(stdscr.getstr(2, 39, 47))
    curses.noecho()
    rectangle(stdscr, 1, 38, 3, 86)
    rectangle(stdscr, 3, 15, 14, 86)

    stdscr.refresh()

    note_win = curses.newwin(10, 70, 4, 16)
    text_box = Textbox(note_win, insert_mode=True)
    curses.curs_set(2)
    text: str = text_box.edit()

    curses.curs_set(0)
    stdscr.getch()
    stdscr.refresh()

    return edit_note(id, title, text)


def view_site(stdscr, name: str):
    # TODO LATER: do resizable with update_lines_cols

    def graphic(stdscr) -> Tuple[Any, int, list[int], list]:
        stdscr.clear()
        stdscr.refresh()
        index: int = -1
        
        notes: dict = loaded_notes.copy() # *just for safety
        
        NOTES_IN_LINE = curses.COLS // 27 # ! 5 default
        NOTE_HEIGHT = 6 # ! 6 is minimal and default

        pad_size: tuple = (
            (NOTE_HEIGHT + 5) * WhenItsMoreThanIstMore(len(notes) / NOTES_IN_LINE),
            curses.COLS - 3,
        )
        pad = curses.newpad(*pad_size)

        #notes = notes[::-1] # sort notes from newest
        size_rectangle: List[int] = [0, 0, NOTE_HEIGHT, 20]  # height width
        for index, note_id in enumerate(notes):
            title_lines: list = word_split(notes[note_id][0], 18)
            
            if index % NOTES_IN_LINE == 0 and index != 0:
                size_rectangle[0] += NOTE_HEIGHT + 4
                size_rectangle[2] += NOTE_HEIGHT + 4
                size_rectangle[1] = 0
                size_rectangle[3] = 20
            
            for i, line in enumerate(title_lines):
                pad.addstr(
                    size_rectangle[0] + 1 + i,
                    size_rectangle[1] + 1,
                    "".join(line)
                )# title
            pad.addstr(
                size_rectangle[2] - 1,
                size_rectangle[3] - len(str(note_id)),
                str(note_id),
            )  # id

            note_date: str = str(notes[note_id][2]).split(" ")[0]  # date
            pad.addstr(size_rectangle[2] - 1, size_rectangle[3] - 19, note_date)
                
            pad.hline(size_rectangle[0] + 4, size_rectangle[1] + 1, "-", 19)
            rectangle(pad, *size_rectangle)

            size_rectangle[1] += 27
            size_rectangle[3] += 27
        return pad, index, size_rectangle, notes

    pad_row: int = 0
    new: bool = True
    while True:

        if new:
            pad, index, size_rectangle, notes = graphic(stdscr)
            notes_idxs: list = [note_key for note_key in notes]
            pad.refresh(pad_row, 0, 3, 3, curses.LINES - 3, curses.COLS - 3)
            stdscr.refresh()
            new: bool = False
            if index == -1:
                break
        
        lines_old = curses.LINES
        cols_old = curses.COLS
        curses.update_lines_cols() # TODO FIXME LATER: this isnt working properly...
        if lines_old != curses.LINES and cols_old != curses.COLS:
            new: bool = True
        stdscr.timeout(0)
        key: int = stdscr.getch()
        if key == 113:  # q
            break
        elif key == ord("d"):  # delete
            curses.echo()
            stdscr.addstr(
                1, curses.COLS - 7 - len((msg := "Here type id for delete: ")), msg
            )
            rectangle(stdscr, 0, curses.COLS - 7 - 1, 2, curses.COLS - 1)
            id: str = to_str(stdscr.getstr(1, curses.COLS - 7, 6))
            curses.noecho()
            if "d" in id:
                clear_input_area(stdscr)

            elif not id.isdigit():
                clear_input_area(stdscr)
                stdscr.addstr(
                    1, curses.COLS - len((msg := "This id is not a digit")), msg
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)
            elif not int(id) in notes_idxs:
                clear_input_area(stdscr)
                stdscr.addstr(
                    1,
                    curses.COLS - len((msg := "Note with this id does not exsist")),
                    msg,
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)
            else:
                stdscr.timeout(-1)
                new: bool = delete_note(int(id))
                clear_input_area(stdscr)
                stdscr.addstr(
                    1,
                    curses.COLS - len((msg := "Note was deleted")),
                    msg,
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)

        elif key == ord("o"):  # open
            curses.echo()
            stdscr.addstr(
                1, curses.COLS - 7 - len((msg := "Here type id for open: ")), msg
            )
            rectangle(stdscr, 0, curses.COLS - 7 - 1, 2, curses.COLS - 1)
            id: str = to_str(stdscr.getstr(1, curses.COLS - 7, 6))
            curses.noecho()
            if "o" in id:
                clear_input_area(stdscr)
            elif not id.isdigit():
                clear_input_area(stdscr)
                stdscr.addstr(
                    1, curses.COLS - len((msg := "This id is not a digit")), msg
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)
            elif not int(id) in notes_idxs:
                clear_input_area(stdscr)
                stdscr.addstr(
                    1,
                    curses.COLS - len((msg := "Note with this id does not exsist")),
                    msg,
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)
            else:
                stdscr.timeout(-1)
                new: bool = view_note(stdscr, int(id), notes_idxs, notes)
        elif key == ord("e"):
            curses.echo()
            stdscr.addstr(
                1, curses.COLS - 7 - len((msg := "Here type id for edit: ")), msg
            )
            rectangle(stdscr, 0, curses.COLS - 7 - 1, 2, curses.COLS - 1)
            id: int = to_str(stdscr.getstr(1, curses.COLS - 7, 6))
            curses.noecho()
            if "e" in id:
                clear_input_area(stdscr)
            elif not id.isdigit():
                clear_input_area(stdscr)
                stdscr.addstr(
                    1, curses.COLS - len((msg := "This id is not a digit")), msg
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)
            elif not int(id) in notes_idxs:
                clear_input_area(stdscr)
                stdscr.addstr(
                    1,
                    curses.COLS - len((msg := "Note with this id does not exsist")),
                    msg,
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)
            else:
                stdscr.timeout(-1)
                new: bool = view_edit_note(stdscr, int(id), notes_idxs, notes)

        if (len(notes) / 5) > 2:

            if key == curses.KEY_DOWN:  # down arrow
                stdscr.addstr("y")
                if pad_row >= size_rectangle[2] - curses.LINES + 9:
                    pad_row: Literal[0, -1] = (
                        0 if pad_row > size_rectangle[2] - curses.LINES + 9 else -1
                    )  # ? i dont know why i need to use -1
                pad_row += 1
                new: bool = True
            elif key == curses.KEY_UP:  # up arrow
                if pad_row <= 0:
                    pad_row = size_rectangle[2] - curses.LINES + 10
                pad_row -= 1
                new: bool = True
                
    stdscr.timeout(-1)
    return False
    


def add_note(title: str, note: str) -> None:
    params = [title, note, datetime.datetime.now()]
    keys = list(loaded_notes.keys())
    if keys:
        id = keys[-1]
    else:
        id = -1
    loaded_notes[id+1] = params


def add_site(stdscr, name: str, msg: str = "", copyed_text: bool = False) -> None:
    # TODO add copiing text
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(1)
    stdscr.clear()

    stdscr.addstr(0, curses.COLS - len(msg) - 1, msg)
    if copyed_text:
        stdscr.addstr(
            1, curses.COLS - len((msg := "The text was copyed to clipboard")) - 1, msg
        )
    stdscr.addstr(2, 2, "Here write your title and then note:")

    stdscr.addstr(16, 15, "'\\n' char is for new line")
    stdscr.addstr(18, 15, "For confirm Ctrl+G + Any")

    stdscr.refresh()
    curses.echo()

    rectangle(stdscr, 1, 38, 3, 86)
    rectangle(stdscr, 3, 15, 14, 86)
    title: str = to_str(stdscr.getstr(2, 39, 47))
    curses.noecho()
    rectangle(stdscr, 1, 38, 3, 86)
    rectangle(stdscr, 3, 15, 14, 86)

    stdscr.refresh()

    quote_win = curses.newwin(10, 70, 4, 16)
    text_box = Textbox(quote_win, insert_mode=True)
    curses.curs_set(2)
    text: str = text_box.edit()

    curses.curs_set(0)
    stdscr.getch()
    curses.curs_set(1)
    stdscr.refresh()
    add_note(title, text)


def main(stdscr, name: str) -> None:

    global loaded_notes
    note_file = open("notes.pickle", "rb")
    try:
        loaded_notes = pickle.load(note_file)
    except EOFError:
        loaded_notes = {}
    note_file.close()
    curses.curs_set(1)

    while True:
        stdscr.clear()
        stdscr.refresh()
        is_note: bool = True    
        if loaded_notes == {}:
            is_note: bool = False
            

        action: str = menu(is_note)
        if action == "view":
            view_site(stdscr, name)
        elif action == "add":
            add_site(stdscr, name)
        elif action == "exitmenu":
            note_file = open("notes.pickle", "wb") 
            pickle.dump(loaded_notes, note_file)
            note_file.close()
            exit()
