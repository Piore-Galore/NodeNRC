#-*-coding:utf8-*-

from typing import Dict
from .struct_node import StructNode

# uncomment following line to enable logger
# from utils.logger import logger

class RootNode(StructNode):
    '''root node for parsing a row'''

    def __init__(self):
        super().__init__({}, 1, "__root__")
        self.payload: Dict = {}

    @property
    def done(self):
        '''root node should never done'''
        return False
