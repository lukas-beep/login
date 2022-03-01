import subprocess
import regex as re

from typing import List

SPACE = " "

def copy2clip(txt: str) -> int:
    cmd='echo ' + txt.strip() + '|clip'
    return subprocess.check_call(cmd, shell=True)


def len_of_words(l: List[str]) -> tuple:
    lenghts: List[int] = []
    for w in l:
        lenghts.append(len(w))
    return tuple(zip(l,lenghts))


def WhenItsMoreThanIstMore(num: float) -> int:
    num_: str = str(num)
    num_ = num_.split('.')
    if num > int(num_[0]):
        return int(num_[0]) + 1
    return int(num_[0])


def to_str(s: str) -> str:
    return str(s)[2:-1]


iota_counter = 0
def iota(reset=False, previous=False):
    global iota_counter
    
    if reset:
        iota_counter = 0 
    
    if not previous:
        iota_counter += 1
    else:
        return iota_counter
    
    return iota_counter
    

def isvalidEmail(email: str) -> bool:
    pattern = "^\S+@\S+\.\S+$"
    objs = re.search(pattern, email)
    try:
        if objs.string == email:
            return True
    except:
        return False
    
    
def word_split(words: str, lenght_of_line: int):
    words_str = words
    words = words.split(" ")
    lines = []
    long = False
    lens_ = len_of_words(words)
    for i in lens_:
        i = i[1]
        if i > 19:
            long = True
            break
    if long:
        for i in range(3):
            lines.append(words_str[19 * i: 19 * (i + 1)])
    else:
        id = 0
        line_len = 0
        
        line = []
        lens = []
        while id <= len(words)-1:
            word = words[id] + (" " if id < len(words)-1 else "")
            
            if line_len < lenght_of_line:
                id += 1
            elif line_len == lenght_of_line:
                lens.append(line_len)
                lines.append("".join(line))
                line = []
                line_len = 0
                id += 1
            elif line_len > lenght_of_line:
                x = line.pop()
                lens.append(line_len - len(x))
                lines.append("".join(line))
                line = []
                line.append(x)
                line_len = 0
                id += 1
                
            line.append(word)
            line_len += len(word)
        if line:
            lens.append(line_len)
            lines.append("".join(line))
    return lines
            