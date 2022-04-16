import curses
import time
from curses.textpad import rectangle

curses.initscr()

def generate_percent_per_item(iterable: list):
    lenght = len(iterable)
    ppi = 100 / lenght
    return ppi

def percentage(iterable: list, pos, do, soup, covid_info, today, n):
    ppi = generate_percent_per_item(iterable)
    win = curses.newwin(*pos)
    y,x = win.getmaxyx()
    rectangle(win, 0, 0 , y-2, x-1)
    loading = ppi
    i_iterable = iter(iterable)
    while loading < 100:
        loading += ppi
        do(soup, next(i_iterable), covid_info, today)
        time.sleep(0.01)
        update_progress(win, loading, n,(y,x))
    win.erase()

def update_progress(win, progress ,n, cor):
    rangex = (30 / float(100)) * progress
    pos = int(rangex)
    display = '#'
    if pos != 0:
        win.addstr(1, pos, "{}".format(display))
        win.addstr(cor[0]-1, 0, f"this will load: {n} times")
        win.refresh()
#TODO: implement random loading messages