#-*-coding:utf8-*-

from typing import Union

def get_number(value: Union[int, str]) -> int:
    '''convert a int or str to int if possible, return 0 if fail'''
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isnumeric():
        return int(value)
    return 0

def is_comment(value: str) -> bool:
    '''determine if a value means comment'''
    return value == "*" or value == ""
