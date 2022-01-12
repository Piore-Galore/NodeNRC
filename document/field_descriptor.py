#-*-coding:utf8-*-

from typing import List
import yaml
from utils import str_utils

# uncomment following line to enable logger
# from utils.logger import logger

PRIMITIVES = ("bool", "string", "float", "double", "int32", "uint64", "uint32",\
    "sint32", "sint64", "fixed32", "fixed64", "sfixed32", "sfixed64")

REQUIRED = "required"
OPTIONAL = "optional"
REPEATED = "repeated"
ENUM_PREFIX = "enum."
STRUCT_SUFFIX = "_struct"
CLIENT_TAGS = ("c", "cli", "client")
SERVER_TAGS = ("s", "svr", "server")
BOTH_TAGS = ("", "b", "both")
COMMENT_TAG = "*"

class FieldDescriptor(yaml.YAMLObject):
    '''describe a field'''

    yaml_tag = "!Descriptor"

    def __init__(self, index: int, field_name: str, type_name: str, full_name: str, realm: str, comment: str):
        super().__init__()
        # column
        self.index: int = index
        # row 0: required/optional/required_struct/optional_struct ...
        self.field_name: str = field_name
        # row 1: uint32/string/enum/could be child count as well ...
        self.type_name: str = type_name
        # row 2: readable names
        self.full_name: str = full_name
        # row 3: empty for now
        self.realm: str = realm
        # row 4: comments
        self.comment: str = comment

    def __eq__(self, other):
        return self.index == other.index and self.field_name == other.field_name \
            and self.type_name == other.type_name and self.full_name == other.full_name \
            and self.realm == other.realm and self.comment == other.comment

    @property
    def is_enum(self):
        '''return true if the field is a enum'''
        return str(self.type_name).startswith(ENUM_PREFIX)

    def get_enum_name(self):
        '''return enum name'''
        if not self.is_enum:
            return None
        return self.type_name[len(ENUM_PREFIX):]

    @property
    def is_required(self):
        '''return true if this field is required'''
        return self.field_name.startswith(REQUIRED)

    @property
    def is_comment(self):
        '''return true if this field is comment'''
        return str_utils.is_comment(str(self.field_name))

    @property
    def is_optional(self):
        '''return true if this field is optional'''
        return self.field_name.startswith(OPTIONAL)

    @property
    def is_primitive(self):
        '''return true if this field is a primitive field'''
        if not isinstance(self.type_name, str):
            return False
        for primitive in PRIMITIVES:
            if self.type_name.startswith(primitive):
                return True
        return False

    @property
    def is_array(self):
        '''return true if this is a repeated field'''
        return self.field_name == REPEATED

    def get_array_child_count(self):
        '''gets child count of the struct'''
        if not self.is_array:
            return None
        return str_utils.get_number(self.type_name)

    @property
    def is_struct(self):
        '''return true if field name endswith _struct'''
        return str(self.field_name).endswith(STRUCT_SUFFIX)

    @property
    def name(self):
        '''return the name used'''
        return self.full_name

    def get_struct_child_count(self):
        '''gets child count of the struct'''\
        '''return None if this not a repeated field'''
        if not self.is_struct:
            return None
        return str_utils.get_number(self.type_name)

    @property
    def is_both(self):
        '''check if we should export this to both server and client'''
        if not self.realm:
            return True
        return self.realm in BOTH_TAGS

    @property
    def is_server(self):
        '''check if we should export this field to server'''
        if self.is_both:
            return True
        return self.realm in SERVER_TAGS

    @property
    def is_client(self):
        '''check if we should export this field to client'''
        if self.is_both:
            return True
        return self.realm in CLIENT_TAGS

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.index},{self.field_name},"\
            f"{self.type_name},{self.full_name},{self.realm})"

    def to_excel(self) -> List:
        '''write to list for exporting to excel file'''
        return [self.field_name, self.type_name, self.full_name, self.realm, self.comment]
