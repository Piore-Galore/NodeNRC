#-*-coding:utf8-*-
from __future__ import annotations
from collections import OrderedDict
from typing import Dict, List
import itertools
import yaml
from openpyxl.worksheet.worksheet import Worksheet

from nodes.array_node import ArrayNode
from nodes.struct_node import StructNode
from nodes.root_node import RootNode
from utils.logger import logger
from utils import str_utils

from .excel_row import ExcelRow
from .field_descriptor import FieldDescriptor
from . import field_descriptor

class ExcelSheet(yaml.YAMLObject):
    '''represents a excel sheet'''

    yaml_tag = "!Sheet"


    def __init__(self, name: str, index: int, excel_name: str = ""):
        super().__init__()
        self.name: str = name
        self.index: int = index
        self.excel_name: str = excel_name
        self.version_id: int = 1
        self.headers: List[FieldDescriptor] = []
        self.body: List[ExcelRow] = []
        # 从属的excel名字，版本号

    def find_header_by_index(self, index) -> FieldDescriptor:
        '''get header with given index'''
        for header in self.headers:
            if header.index == index:
                return header
        return None

    @staticmethod
    def parse_header(header_chunk: List[List[str]], headers: List[FieldDescriptor]):
        '''parse header rows into FieldDescriptors'''
        fields, types, names, realms, comments = header_chunk
        for index, (field, typ, name, realm, comment) in enumerate(itertools.zip_longest(fields, types, names, realms, comments)):
            headers.append(FieldDescriptor(index, field, typ, name, realm, comment))

    @staticmethod
    def parse_sheet(sheet_name: str, sheet_index: int, sheet: OrderedDict) -> ExcelSheet:
        '''parse given sheet into Document object'''
        document: ExcelSheet = ExcelSheet(sheet_name, sheet_index)
        document.parse_header(sheet[0:5], document.headers)
        runtime = []
        for index, content_row in enumerate(sheet[5:]):
            if len(content_row) == 0:
                # 空行跳过
                continue
            content_row += [""] * (len(document.headers) - len(content_row))
            comments: Dict[int, str] = {}
            runtime_content: Dict = document.parse_row(content_row, comments)
            runtime.append(ExcelRow(runtime_content, index, "", "", comments))
        document.set_body(runtime)
        return document

    def parse_row(self, contents: List, comments: Dict[int, str]) -> Dict:
        '''parse a row into plain python dict'''
        root = RootNode()
        parser_nodes = [root]
        for index, value in enumerate(contents):
            header = self.find_header_by_index(index)
            if not header:
                logger.debug(f"can't find header with index {index}")
                continue
            if header.field_name == field_descriptor.COMMENT_TAG:
                comments[index] = value
                continue
            if header.is_array:
                if header.is_primitive or header.is_enum:
                    # 在一格里面定义的数组，直接处理完
                    # 这可以看作一个primitive value，所以不能continue，按照primitive的逻辑处理
                    current_node = parser_nodes[-1]
                    values: List[str] = str(value).split(';')
                    current_node.set_key_value(header.name, values)
                    logger.debug(f"{index}.Create One Column Array.{len(values)}.with.{values}")
                else:
                    # 数组声明，需要靠后面的数据补齐
                    array_count: int = str_utils.get_number(value)
                    total = array_count
                    array_node: ArrayNode = ArrayNode(header, total, None)
                    # 只要是数组声明，数组名一定是声明之后的那一列的name，所以直接在这里面向后拿到名字
                    array_node.name = self.find_header_by_index(index + 1).name
                    parser_nodes.append(array_node)
                    logger.debug(f"{index}.Create Array.{total}")
                    continue
            elif header.is_struct:
                total = header.get_struct_child_count()
                prev_node = parser_nodes[-1]
                parser_nodes.append(StructNode(header, total, header.name))
                logger.debug(f"{index}.Create Struct.{total}.{header.name}")
                continue
            current_node = parser_nodes[-1]
            if header.is_comment:
                # 给comment拼一个新的名字，避免重复
                current_node.set_key_value(header.name + str(index), value)
            else:
                current_node.set_key_value(header.name, value)
            logger.debug(f"{index}.Set Value To.{type(current_node)}.{header.name}={value}"\
                f",{current_node.done}")
            while current_node.done:
                current_node = parser_nodes.pop()
                if len(parser_nodes) <= 0:
                    continue
                prev_node = parser_nodes[-1]
                prev_node.set_key_value(current_node.name, current_node.payload)
                logger.debug(f"{index}.Set Value Up.{type(prev_node)}."\
                    f"{current_node.name},{prev_node.done}")
                if isinstance(prev_node, ArrayNode) and not prev_node.done:
                    logger.debug(f"{index},push node back, {type(current_node)}")
                    current_node.reset()
                    parser_nodes.append(current_node)
                else:
                    current_node = prev_node
        return root.payload

    def set_body(self, body):
        '''override current data list'''
        self.body = body

    def save_as_yaml(self, path):
        '''dump as yaml'''
        with open(path, "w", encoding='utf8') as file:
            yaml.dump(self, stream=file, allow_unicode=True, sort_keys=False)

    def write_to_excel(self, excel_sheet: Worksheet):
        '''clear the sheet and write data into it'''
        # 清空excel sheet里面的内容
        if excel_sheet.max_row > 5:
            excel_sheet.delete_rows(6, excel_sheet.max_row - 6 + 1)
        logger.debug(f"Clear excel {excel_sheet.title}")
        for row in self.body:
            excel_row = self.yaml_to_excel_row(row)
            excel_sheet.append(excel_row)
        logger.debug(f"write to excel {excel_sheet.title} Done")

    def yaml_to_excel_row(self, row: ExcelRow):
        ''' generate a list for excel row from yaml data based on header'''
        excel_row = []
        row_data = row.data
        while len(excel_row) < len(self.headers):
            logger.debug(f"write to excel row {len(excel_row)}")
            self.deal_next_value(excel_row, row_data)
        for key, comment in row.comments.items():
            excel_row[key] = comment
        return excel_row

    def deal_next_value(self, excel_row: List, row_data: List):
        '''deal with next value'''
        next_index: int = len(excel_row)
        header = self.headers[next_index]
        if header.is_comment:
            # 之后统一处理，这里就单纯填个空
            excel_row.append("")
            return
        if header.is_array:
            self.add_array(excel_row, row_data, header, next_index)
            return
        if header.is_struct:
            # 因为add_struct只负责添加struct body，所以header在这里加一下
            excel_row.append("")
            self.add_struct(len(row_data[header.name]), excel_row, row_data[header.name])
            return
        if header.is_primitive:
            self.add_primitive(excel_row, row_data, header)
            return
        if header.is_enum:
            if header.name in row_data:
                excel_row.append(row_data[header.name])
            else:
                excel_row.append("")
            return

    def add_primitive(self, excel_row: List, row_data: List, header: FieldDescriptor):
        '''recursive add primitive'''
        # 处理之前确认一下这个名字是不是真的对应primitive value, 如果是其他东西就填个空值
        if header.name in row_data and not isinstance(row_data[header.name], dict) and not isinstance(row_data[header.name], list):
            excel_row.append(row_data[header.name])
        else:
            excel_row.append("")
        return

    def add_array(self, excel_row: List, row_data: List, header: FieldDescriptor, next_index: int):
        '''recursive add array'''
         # 这里单行的数组会被判定为primitive，所以需要放在前面，之后再看看怎么更好一点
        if header.is_primitive or header.is_enum:
            # 单行数组直接根据;打散，然后作为数组加进去
            if header.name in row_data:
                excel_row.append(';'.join(map(str, str(row_data[header.name]))))
            else:
                excel_row.append('')
        else:
            array_data = {}
            next_header = self.headers[next_index + 1]
            # 多行数组的数组名在数组定义的后一列，去后一列拿到数组的名字，然后才能拿到这个数组对应的数据
            # 如果内容为空，也要继续，至少要把对应的数据段填满
            if next_header.name in row_data:
                array_data = row_data[next_header.name]
            # 根据这个数组的数据真正长度，推算出当前格子的value
            excel_row.append(str(len(array_data)) if len(array_data) > 0 else "")
            if self.headers[next_index + 1].is_primitive:
                # 处理普通的数组，按照顺序塞进去，不够的用空字符串填满
                for i in range(header.get_array_child_count()):
                    if i < len(array_data):
                        excel_row.append(array_data[i])
                    else:
                        excel_row.append("")
            elif self.headers[next_index + 1].is_struct:
                # 处理结构体数组，这种数组第一格是结构体定义，value是空
                excel_row.append("")
                for i in range(header.get_array_child_count()):
                    if i < len(array_data):
                        # 将查找的字典更新到对应的struct里面，然后把struct的结构信息(长度)也传进去
                        self.add_struct(next_header.get_struct_child_count(), excel_row, array_data[i])
                    else:
                        self.add_struct(next_header.get_struct_child_count(), excel_row, {})
                return
        return

    def add_struct(self, struct_len: int, excel_row: List, row_data: List):
        '''recursive add struct'''
        for _ in range(struct_len):
            self.deal_next_value(excel_row, row_data)
