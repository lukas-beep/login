import curses
import random
import typing
import datetime
import pickle

from time import sleep
from utils.utils import copy2clip, to_str, WhenItsMoreThanIstMore, iota, len_of_words, word_split, SPACE
from typing import List, Dict, Literal, Tuple, Optional, Union, Any
from curses.textpad import Textbox, rectangle

from utils.menu import CursesMenu

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



def generate_status(todo):
    subtasks = todo[1]
    with open("l.txt","w") as o:
        o.write(str(subtasks))
    done = 0
    for subtask in subtasks:
        subtask_status = subtask[1]
        done += subtask_status
    undone = len(subtasks) - done
    #2713 true
    #2717 false
    if undone == 0:
        return "\u2713"
    elif undone == len(subtasks):
        return "\u2717"
    else:
        return f"{done}/{len(subtasks)}"
    
    
def clear_input_area(stdscr):
    half: int = WhenItsMoreThanIstMore(curses.COLS / 2)
    stdscr.hline(0, half, " ", half)
    stdscr.hline(1, half, " ", half)
    stdscr.hline(2, half, " ", half)
    stdscr.refresh()


def delete_todo(id: int) -> bool:
    loaded_todos.pop(id)
    return True


def edit_todo(id: int, title: str, content: str, date=datetime.datetime.now()) -> bool:
    params: list = [title, content,date , generate_status(loaded_todos[id])]
    loaded_todos[id] = params
    return True

def input_area_manager(what_for, stdscr, type: str, todos_idxs=None, todos=None, todo_id=None):
    curses.echo()
    if what_for == "view":
        if type == "d":
            msg = "Here type id for delete: " 
        elif type == "o":
            msg = "Here type id for open: "
        elif type == "e":
            msg = "Here type id for edit: "
        else:
            return False
            
        stdscr.addstr(
            1, curses.COLS - 7 - len(msg), msg
        )
        rectangle(stdscr, 0, curses.COLS - 7 - 1, 2, curses.COLS - 1)
        stdscr.refresh()
        id: str = to_str(stdscr.getstr(1, curses.COLS - 7, 6))
        curses.noecho()
        stdscr.refresh()
        if type in id:
            clear_input_area(stdscr)

        elif not id.isdigit():
            clear_input_area(stdscr)
            stdscr.addstr(
                1, curses.COLS - len((msg := "This id is not a digit")), msg
            )
            stdscr.refresh()
            sleep(2)
            clear_input_area(stdscr)
        elif not int(id) in todos_idxs:
            clear_input_area(stdscr)
            stdscr.addstr(
                1,
                curses.COLS - len((msg := "todo with this id does not exsist")),
                msg,
            )
            stdscr.refresh()
            sleep(2)
            clear_input_area(stdscr)
        else:
            stdscr.timeout(-1)
            if type == "d":
                new: bool = delete_todo(int(id))
                clear_input_area(stdscr)
                stdscr.addstr(
                    1,
                    curses.COLS - len((msg := "todo was deleted")),
                    msg,
                )
                stdscr.refresh()
                sleep(2)
                clear_input_area(stdscr)
            
            elif type == "o":
                new: bool = view_todo(stdscr, int(id))
                
            return new
    elif what_for == "view note":
        if type == "d":
            msg = "Here type id for done: " 
        elif type == "u":
            msg = "Here type id for undone: "
        else:
            return False
            
        stdscr.addstr(
            1, curses.COLS - 7 - len(msg), msg
        )
        rectangle(stdscr, 0, curses.COLS - 7 - 1, 2, curses.COLS - 1)
        stdscr.refresh()
        id: str = to_str(stdscr.getstr(1, curses.COLS - 7, 6))
        curses.noecho()
        stdscr.refresh()
        subtasks_len = len(loaded_todos[todo_id][1])
        if type in id:
            clear_input_area(stdscr)

        elif not id.isdigit():
            clear_input_area(stdscr)
            stdscr.addstr(
                1, curses.COLS - len((msg := "This id is not a digit")), msg
            )
            stdscr.refresh()
            sleep(2)
            clear_input_area(stdscr)
        elif  int(id) > subtasks_len and int(id) < 0:
            clear_input_area(stdscr)
            stdscr.addstr(
                1,
                curses.COLS - len((msg := "subtask with this id does not exsist")),
                msg,
            )
            stdscr.refresh()
            sleep(2)
            clear_input_area(stdscr)
        else:
            stdscr.timeout(-1)
            if type == "d":
                loaded_todos[todo_id][1][int(id)][1] = True
                new = True
                edit_todo(todo_id,loaded_todos[todo_id][0], loaded_todos[todo_id][1], loaded_todos[todo_id][2])
                sleep(2)
                clear_input_area(stdscr)
            
            elif type == "u":
                loaded_todos[todo_id][1][int(id)][1] = False
                new = True
                edit_todo(todo_id,loaded_todos[todo_id][0], loaded_todos[todo_id][1], loaded_todos[todo_id][2])
                sleep(2)
                clear_input_area(stdscr)
      
            return new

def view_todo(stdscr, id) -> bool: 

    stdscr.clear()
    stdscr.refresh()
    stdscr.clear()

    # todo[0]: str
    # todo[1]: tuple
    # todo[2]: tuple | datetime
    # todo[3]: int
    def graphic(stdscr, id):
        col_table = curses.COLS//2-44
        stdscr.addstr(2+2, 38 - len((msg := "Here is title:")), msg)
        stdscr.addstr(2+2, 39, loaded_todos[id][0])
        
        stdscr.addstr(4+2, 38 - len((msg := "Here is subtasks:")), msg)
        stdscr.addstr(6+2, col_table , f"{SPACE * (4)}ID{SPACE * (70)}TITLE  STATUS")
        stdscr.hline(7+2,col_table, curses.ACS_HLINE, 15+70+4)
        subtasks: tuple = loaded_todos[id][1]
        for i, subtask in enumerate(subtasks):
            id_len = len(str(i))
            id = (" "*(6-id_len))+str(i)
            title_len = len(subtask[0])
            title = (" "*(75-title_len))+str(subtask[0])
            status_icon = "\u2713" if subtask[1] else "\u2717"
            status = (" "*(8-1))+ status_icon
            line = id + title + status
            stdscr.addstr(8+2 + i, col_table, line)

        rectangle(stdscr, 3, 38, 5, 91)
                       
    stdscr.refresh()
    new = True
    while True:
        if new:
            new = False
            graphic(stdscr, id)
            stdscr.refresh()
            
        key: int = stdscr.getch()
        if key == ord("q"):
            stdscr.clear()
            return True
        elif key in (ord("d"), ord("u")):
            new = input_area_manager("view note", stdscr, chr(key), todo_id=id)
    return False

def view_site(stdscr, name: str):
    def graphic(stdscr) -> Tuple[Any, int, list[int], list]:
        
        stdscr.clear()
        stdscr.refresh()
        index: int = -1
        
        todos: dict = loaded_todos.copy() # *just for safety
        
        TABLE_HEIGHT = len(todos)
                  
        pad_size: tuple = (
            TABLE_HEIGHT + 10,
            curses.COLS - 3,
        )
        col_table = pad_size[1]//2-51-2
        pad = curses.newpad(*pad_size)

        pad.addstr(0,col_table, f"{SPACE * (4)}ID{SPACE * (70)}TITLE{SPACE * (10)}DATE  STATUS")
        pad.hline(1,col_table, curses.ACS_HLINE, 103)
        for index, todo_id in enumerate(todos):
            id_len = len(str(todo_id))
            id = (" "*(6-id_len))+str(todo_id)
            title_len = len(todos[todo_id][0])
            title = (" "*(75-title_len))+str(todos[todo_id][0])
            date_len = len(str(todos[todo_id][2]).split(" ")[0])
            date = (" "*(14-date_len))+str(str(todos[todo_id][2]).split(" ")[0])
            status_len = len(todos[todo_id][3])
            status = (" "*(8-status_len)+todos[todo_id][3])
            #2713 true
            #2717 false
            line = id + title + date + status
            pad.addstr(index+2, col_table, line)

        return pad, index, todos

    pad_row: int = 0
    new: bool = True
    while True:

        if new:
            pad, index, todos = graphic(stdscr)
            todos_idxs: list = [todo_key for todo_key in todos]
            pad.refresh(pad_row, 0, 3, 3, curses.LINES - 3, curses.COLS - 3)
            stdscr.refresh()
            new: bool = False
            if index == -1:
                break
            
        stdscr.timeout(0)
        key: int = stdscr.getch()
        if key == 113:  # q
            break
        elif key in (ord("d"), ord("o")):
            new = input_area_manager("view",stdscr, chr(key), todos_idxs, todos)
            pass

        """if (len(todos) / 5) > 2:

            if key == curses.KEY_DOWN:  # down arrow
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
                new: bool = True"""
                
    stdscr.timeout(-1)
    return False
    

def add_todo(title: str, subtasks: list) -> None:
    params = [title, tuple(subtasks), datetime.datetime.now(), "\u2717"]
    keys = list(loaded_todos.keys())
    if keys:
        id = keys[-1]
    else:
        id = -1
    loaded_todos[id+1] = params


def clear_subtasks_area(stdscr):
    for i in range(10):
        stdscr.hline(7+i,34," ", 67)


def add_site(stdscr, msg: str = "") -> None:
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(1)
    stdscr.clear()

    stdscr.addstr(0, curses.COLS - len(msg) - 1, msg)

    stdscr.addstr(2, 2, "Here write your title:")

    curses.echo()
    subtasks = []
    rectangle(stdscr, 1, 25, 3, 78)
    title: str = to_str(stdscr.getstr(2, 26, 52))
    rectangle(stdscr, 1, 25, 3, 78)
    stdscr.addstr(18,3,"if you done with subtasks type 'q'")
    stdscr.addstr(19,3,"if you want to delete subtask type 'delete <id>'")
    
    n = 0
    while n < 10:
        stdscr.addstr(5, 6, f"Here write your {n+1}. subtask: ")
        stdscr.hline(5,34," ", 67)
        rectangle(stdscr, 4,33,6,101)
        subtask = to_str(stdscr.getstr(5, 34, 67)).lstrip()
        rectangle(stdscr, 4,33,6,101)
        if "q" in subtask:
            break
        elif "delete" in subtask:
            command = subtask.split(" ")
            if len(command) >= 2 and command[1].isdigit():
                id = int(command[1])
                if len(subtasks) >= id:
                    subtasks.pop(id)
                    n -= 1
                else:
                    stdscr.addstr(0, curses.COLS - len((msg := "This id does not exists ")) - 1, msg)
            else:
                stdscr.addstr(0, curses.COLS - len((msg := "This command is not valid ")) - 1, msg)
        elif subtask: #* checks if subtask isn't empty(amater way)
            n += 1
            subtasks.append([subtask,False])
            
        clear_subtasks_area(stdscr)
        for index, subtask_ in enumerate(subtasks):
            stdscr.hline(7+index,34," ", 67)
            stdscr.addstr(7+index, 34, f"{index}. {subtask_[0]}")
            
    stdscr.refresh()
    curses.noecho()
    curses.curs_set(0)
    stdscr.getch()
    curses.curs_set(1)
    stdscr.refresh()
    add_todo(title, subtasks)


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
            break