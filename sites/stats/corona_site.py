import curses
import random
import typing
import datetime
import pickle
import requests

from bs4 import BeautifulSoup
from time import sleep
from typing import List, Dict, Literal, Tuple, Optional, Union, Any
from curses.textpad import Textbox, rectangle

from utils import *


def parse_web(url_end="#countries"):
    page = requests.get(f"https://www.worldometers.info/coronavirus/{url_end}")
    soup = BeautifulSoup(page.text, "html.parser")
    return soup


def find_state_info(soup, state, covid_info, today):
    f = soup.find("td", text=state)
    l = f.parent
    li = []
    for i in l:
        i = str(i)
        try:
            text = i.split("<")[1].split(">")[-1]
            if text == "":
                text = i.split("<")[2].split(">")[-1]

            if text == "" or text == "N/A" or text == " ":
                li.append("N/A")
            else:
                li.append(text)
        except:
            pass

    del li[8:14]
    del li[9:]
    del li[0]
    append_to_dic(li, covid_info, today)


def create_dic_info(soup, states, covid_info, today, n):
    percentage(
        states,
        [4, 32, curses.LINES // 2 - 2, curses.COLS // 2 - 16],
        find_state_info,
        soup,
        covid_info,
        today, n
    )


def append_to_dic(li, covid_info, today):
    covid_info[str(today)][li[0]] = {
        "Total Cases": li[1],
        "New Cases": li[2],
        "Total Deaths": li[3],
        "New Deaths": li[4],
        "Total Recovere": li[5],
        "New Recovered": li[6],
        "Population": li[7],
    }


def make_correct_state(state, upper_states):
    splited_of_name_state = (state.split(" "), len(state.split(" ")))
    if state in upper_states:
        state = state.upper()
    elif splited_of_name_state[1] >= 2:
        state = []
        for i in splited_of_name_state[0]:
            if i in ["of", "and"]:
                state.append(i)
            else:
                state.append(i.capitalize())
        state = "".join(i + " " for i in state)
        state = state[0:-1]

    else:
        state = state.capitalize()

    return state


def crerate_table(stdscr, command, upper_states, covid_info, date):
    clear_input_area(stdscr)
    curses.noecho()
    curses.curs_set(0)
    stdscr.addstr(
        9,
        20,
        f"Total Cases{SPACE * (2)}New Cases Total Deaths New Deaths Total Recovered New Recovered{SPACE * (4)}Population",
    )
    stdscr.hline(10, 20, curses.ACS_HLINE, 90)
    for i, state in enumerate(command):
        state = make_correct_state(state, upper_states)
        stdscr.hline(11+i, 10, " ",10)
        stdscr.addstr(11 + i, 10, state)
        info = list(covid_info[date][state].values())
        stdscr.addstr(
            11 + i,
            20,
            f"{SPACE*(11-len(info[0]))}{info[0]}{SPACE*(11-len(info[1]))}{info[1]}{SPACE*(13-len(info[2]))}{info[2]}{SPACE*(11-len(info[3]))}{info[3]}{SPACE*(16-len(info[4]))}{info[4]}{SPACE*(14-len(info[5]))}{info[5]}{SPACE*(14-len(info[6]))}{info[6]}",
        )


def clear_input_area(stdscr):
    half: int = WhenItsMoreThanIstMore(curses.COLS / 2)
    stdscr.hline(0, half, " ", half)
    stdscr.hline(1, half, " ", half)
    stdscr.hline(2, half, " ", half)
    stdscr.refresh()

def save_data(covid_info):
    with open("corona.pickle", "wb") as f:
        pickle.dump(covid_info, f)


def main(stdscr, name: str) -> None:
    states = states_list()
    upper_states = ["drc", "car", "uae", "timor-leste", "uk", "usa"]
    today = datetime.date.today()

    f = open("corona.pickle", "a+")
    f.close()
    corona_file = open("corona.pickle", "rb")
    loading = 0
    try:
        loaded_corona_info = pickle.load(corona_file)
        if loaded_corona_info.get(str(today)) == None:
            loaded_corona_info.update({str(today): {}})
            loading += 1
        # if loaded_corona_info.get(str(today - timedelta(days=1))) == None:
        #     loaded_corona_info.update({str(today - timedelta(days=1)): {}})
        #     loading += 1
        # if loaded_corona_info.get(str(today - timedelta(days=2))) == None:
        #     loaded_corona_info.update({str(today - timedelta(days=2)): {}})
        #     loading += 1
    except EOFError:
        loaded_corona_info = {str(today): {}}
    corona_file.close()
    curses.curs_set(1)

    stdscr.clear()
    stdscr.refresh()
    if loaded_corona_info.get(str(today)) == {}:
        soup = parse_web()
        create_dic_info(soup, states, loaded_corona_info, today, loading)
        loading -= 1
        stdscr.clear()
    # if loaded_corona_info.get(str(today - timedelta(days=1))) == {}:
    #     soup = parse_web("#nav-yesterday")
    #     create_dic_info(soup, states, loaded_corona_info, today - timedelta(days=1), loading)
    #     loading -= 1
    #     stdscr.clear()
    # if loaded_corona_info.get(str(today - timedelta(days=2))) == {}:
    #     soup = parse_web("#nav-yesterday2")
    #     create_dic_info(soup, states, loaded_corona_info, today - timedelta(days=2), loading)
    #     loading -= 1
    #     stdscr.clear()

    stdscr.addstr(0, 5, "Corona Virus Tracker")
    stdscr.addstr(
        5, 5, "Write coordinates to get information PATTERN(DATE,,STATE,...): "
    )
    while True:
        while True:
            stdscr.hline(5, 69, " ", curses.COLS - 69 - 1)
            rectangle(stdscr, 4, 68, 6, curses.COLS - 1)
            curses.echo()
            curses.curs_set(1)
            coordinates = to_str(stdscr.getstr(5, 69, curses.COLS - 69 - 1))
            if coordinates == ("q" * len(coordinates)):
                save_data(loaded_corona_info)
                return
            coordinates = coordinates.split(",,")
            if len(coordinates) < 2:
                stdscr.addstr(0, curses.COLS - len((msg := "Wrong input")) - 1, msg)
                stdscr.refresh()
                sleep(1.5)
                clear_input_area(stdscr)
                stdscr.getch()
            else:
                break

        date = set_date(coordinates[0], today)
        if loaded_corona_info.get(str(date)) == None: 
            stdscr.addstr(0, curses.COLS - len((msg := "this date is invalid or is unreachable")) - 1, msg)
            stdscr.refresh()
            sleep(1.5)
            clear_input_area(stdscr)
            continue
            
        states = coordinates[1].split(",")
        crerate_table(stdscr, states, upper_states, loaded_corona_info, date)
        key = stdscr.getch()
        if key == ord("q"):
            save_data(loaded_corona_info)
            stdscr.clear()
            return


def states_list():
    states = [
        "World",
        "Micronesia",
        "Saint Helena",
        "Palau",
        "Samoa",
        "Vanuatu",
        "Marshall Islands",
        "Western Sahara",
        "Solomon Islands",
        "Vatican City",
        "Montserrat",
        "Saint Pierre Miquelon",
        "Macao",
        "Falkland Islands",
        "Anguilla",
        "Greenland",
        "Wallis and Futuna",
        "Diamond Princess",
        "Cayman Islands",
        "Faeroe Islands",
        "New Caledonia",
        "Tanzania",
        "Saint Kitts and Nevis",
        "St. Barth",
        "Caribbean Netherlands",
        "Antigua and Barbuda",
        "St. Vincent Grenadines",
        "Bhutan",
        "Dominica",
        "British Virgin Islands",
        "Grenada",
        "Turks and Caicos",
        "Sao Tome and Principe",
        "Monaco",
        "Liechtenstein",
        "Saint Martin",
        "Bermuda",
        "New Zealand",
        "Sint Maarten",
        "Comoros",
        "Chad",
        "San Marino",
        "Gibraltar",
        "Liberia",
        "Niger",
        "Barbados",
        "Sierra Leone",
        "Eritrea",
        "Isle of Man",
        "Yemen",
        "Gambia",
        "Saint Lucia",
        "Equatorial Guinea",
        "Channel Islands",
        "CAR",
        "Iceland",
        "South Sudan",
        "Djibouti",
        "Hong Kong",
        "Nicaragua",
        "Congo",
        "Mauritius",
        "Burkina Faso",
        "Burundi",
        "Lesotho",
        "Mali",
        "Andorra",
        "Aruba",
        "Curaçao",
        "Taiwan",
        "Tajikistan",
        "Laos",
        "Belize",
        "Papua New Guinea",
        "Somalia",
        "Timor-Leste",
        "Bahamas",
        "Mayotte",
        "Seychelles",
        "Haiti",
        "Benin",
        "Togo",
        "Gabon",
        "Guyana",
        "Syria",
        "Guinea",
        "Suriname",
        "Mauritania",
        "Cabo Verde",
        "Malta",
        "French Guiana",
        "Sudan",
        "Martinique",
        "French Polynesia",
        "Madagascar",
        "Eswatini",
        "Trinidad and Tobago",
        "Fiji",
        "Angola",
        "Guadeloupe",
        "Réunion",
        "DRC",
        "Ivory Coast",
        "Malawi",
        "Singapore",
        "Senegal",
        "Jamaica",
        "Luxembourg",
        "Australia",
        "Maldives",
        "Cameroon",
        "Rwanda",
        "China",
        "El Salvador",
        "Cambodia",
        "Cyprus",
        "Uganda",
        "Montenegro",
        "Ghana",
        "Namibia",
        "Zimbabwe",
        "Finland",
        "Estonia",
        "Latvia",
        "Mozambique",
        "Afghanistan",
        "Albania",
        "Botswana",
        "Uzbekistan",
        "Kyrgyzstan",
        "Norway",
        "North Macedonia",
        "Nigeria",
        "Algeria",
        "Zambia",
        "Bosnia and Herzegovina",
        "Qatar",
        "Kenya",
        "Armenia",
        "Mongolia",
        "Bahrain",
        "Moldova",
        "S. Korea",
        "Slovenia",
        "Egypt",
        "Oman",
        "Lithuania",
        "Ethiopia",
        "Libya",
        "Venezuela",
        "Denmark",
        "Dominican Republic",
        "Honduras",
        "Ireland",
        "Palestine",
        "Croatia",
        "Uruguay",
        "Slovakia",
        "Kuwait",
        "Myanmar",
        "Paraguay",
        "Panama",
        "Azerbaijan",
        "Bulgaria",
        "Sri Lanka",
        "Bolivia",
        "Costa Rica",
        "Ecuador",
        "Belarus",
        "Guatemala",
        "Saudi Arabia",
        "Georgia",
        "Lebanon",
        "Greece",
        "Vietnam",
        "Tunisia",
        "Austria",
        "UAE",
        "Cuba",
        "Nepal",
        "Jordan",
        "Hungary",
        "Switzerland",
        "Serbia",
        "Kazakhstan",
        "Morocco",
        "Portugal",
        "Romania",
        "Sweden",
        "Israel",
        "Belgium",
        "Pakistan",
        "Thailand",
        "Bangladesh",
        "Canada",
        "Chile",
        "Japan",
        "Czechia",
        "Iraq",
        "Netherlands",
        "Malaysia",
        "Peru",
        "Philippines",
        "Ukraine",
        "South Africa",
        "Poland",
        "Mexico",
        "Germany",
        "Indonesia",
        "Italy",
        "Spain",
        "Colombia",
        "Argentina",
        "Iran",
        "Turkey",
        "France",
        "Russia",
        "UK",
        "Brazil",
        "India",
        "USA",
    ]

    return states
