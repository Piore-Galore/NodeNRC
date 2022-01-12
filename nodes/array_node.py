#-*-coding:utf8-*-

import copy
from typing import List
from document import field_descriptor
from document.field_descriptor import FieldDescriptor
from .parser_node import ParserNode
# uncomment following line to enable logger
# from utils.logger import logger

class ArrayNode(ParserNode):
    '''a parser node that treat its conent as an array'''

    def __init__(self, header: FieldDescriptor, total: int, name: str):
        super().__init__(header, total, name)
        self.payload: List = []
        self.max_length: int = 0 # header里面定义的数组长度，不管有没有填满，都需要达到这个长度才能，被认为是done
        self.real_length: int = 0 # 每个row里面array自己定义的长度，读到这个长度的内容后，忽略掉后面的部分

    def set_key_value(self, key, value):
        '''add value to the payload list'''
        # 统计元素数量时不包括comment
        if self.real_length < self.total:
            self.payload.append(copy.copy(value))
            if key != field_descriptor.COMMENT_TAG:
                self.real_length += 1
        self.max_length += 1

    @property
    def done(self) -> bool:
        '''check if payload is greater than total'''
        return self.max_length >= int(self.header.type_name)

    def reset(self):
        self.payload.clear()
        self.max_length = 0
        self.real_length = 0
