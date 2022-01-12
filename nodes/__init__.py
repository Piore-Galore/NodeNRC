#-*-coding:utf8-*-

import re

def is_valid_sheet_name(name: str) -> bool:
    '''return true if a sheet name is valid'''
    result = re.match(r"[A-Z,_]{3,20}", name)
    if not result:
        return False
    return True
