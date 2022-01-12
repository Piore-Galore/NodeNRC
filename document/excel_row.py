#-*-coding:utf8-*-

from typing import List, Dict
import yaml

from document.field_descriptor import FieldDescriptor

class ExcelRow(yaml.YAMLObject):
    '''represent a excel row, with user defined "content" and predefined fields'''

    yaml_tag = "!Row"

    def __init__(self, content:dict, index: int, creator: str, last_author: str, comments: Dict[int, str]) -> None:
        super().__init__()
        self.data: dict = content
        self.index: int = index
        self.creator: str = creator
        self.last_author: str = last_author
        self.comments: Dict[int, str] = comments

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.index},{self.creator},"\
            f"{self.last_author})"

    def __eq__(self, other) -> bool:
        # python似乎可以自己递归对比dict和list的元素
        return self.comments == other.comments and self.data == other.data

    # need flatten data recursivesly
    def to_excel(self, headers: List[FieldDescriptor]) -> List:
        '''create excel lists'''
        row = []
        for header in headers:
            row.append(self.data.get(header.full_name, ""))
        return row
