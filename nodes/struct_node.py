#-*-coding:utf8-*-

import copy
from typing import Dict
from document.field_descriptor import FieldDescriptor
from utils import str_utils
from .parser_node import ParserNode

# uncomment following line to enable logger
# from utils.logger import logger

class StructNode(ParserNode):
    '''a parser node that treat its content as a dictionary'''

    def __init__(self, header: FieldDescriptor, total: int, name: str):
        super().__init__(header, total, name)
        self.payload: Dict = {}
        self.real_length = 0

    def set_key_value(self, key, value):
        '''set key to value(deep copied)'''
        self.payload[key] = copy.copy(value)
        # 计数的时候忽略掉注释
        if not str_utils.is_comment(key):
            self.real_length += 1

    @property
    def done(self):
        '''check if payload is greater than total'''
        return self.real_length >= self.total

    def reset(self):
        self.payload.clear()
        self.real_length = 0
