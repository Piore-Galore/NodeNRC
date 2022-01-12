#-*-coding:utf8-*-

from abc import abstractmethod
from utils.logger import logger
from document.field_descriptor import FieldDescriptor

class ParserNode():
    '''a based node for parsing a row'''

    def __init__(self, header: FieldDescriptor, total: int, name: str):
        super().__init__()
        self.total: int = total
        self.count: int = 0
        self._name: str = name
        self.header: FieldDescriptor = header
        self.payload = None

    @abstractmethod
    def set_key_value(self, key, value):
        '''set key to value'''

    @property
    def name(self) -> str:
        '''return name of the node'''
        return self._name

    @name.setter
    def name(self, new_name: str):
        '''set the name of current node with new_name'''
        if self._name:
            logger.warning(f"name {self._name} will be replaced by {new_name}")
        self._name = new_name

    @property
    def done(self) -> bool:
        '''return True if the node is finished with parsring'''
        return True

    def reset(self):
        '''reset current count to zero'''
        self.count = 0
