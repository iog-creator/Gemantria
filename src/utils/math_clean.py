import re

def extract_number(text:str)->str:

    # first bare integer/float wins

    m = re.search(r'(?<![\w/.-])([+-]?\d+(?:\.\d+)?)', text)

    return m.group(1) if m else text.strip()[:64]
