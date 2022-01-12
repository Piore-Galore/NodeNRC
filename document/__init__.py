#-*-coding:utf8-*-
from typing import List
from pathlib import Path
from document.excel_file import ExcelFile
from utils import logger, timer


@timer
def excel_to_yaml(input_xls: Path, yaml_list: List[Path], header_xls: Path, output_dir: Path):
    '''one function deal with excel to yaml'''
    # 可能要修改表头
    parser = ExcelFile()
    # 从excel和yaml里面分别读出来一份数据
    parser.parse_excel(input_xls)
    parser.add_origin_yaml(yaml_list)
    # 对比解析出来的yaml里面的header和
    parser.replace_header(header_xls)
    # 对比yaml和解析出来的内容的区别，设置creator和author
    parser.compare_yaml_diff()
    parser.save_as_yaml(output_dir)

@timer
def yaml_to_excel(header_xls: Path, yaml_list: List[Path], inter_xls: Path):
    '''one function deal with yaml to excel'''
    logger.debug(f"yaml to excel {header_xls} {yaml_list} {inter_xls}")
    parser = ExcelFile()
    parser.load_yaml(yaml_list)
    parser.save_as_excel(inter_xls, header_xls)
