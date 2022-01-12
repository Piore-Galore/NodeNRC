#-*-coding:utf8-*-


import subprocess
from pathlib import Path
from typing import List

from .logger import logger

COMMIT_CMD = "commit"
UPDATE_CMD = "update"
REVERT_CMD = "revert"
BLAME_CMD = "blame"
LOG_CMD = "log"

TORTOISE_SVN_PROC = "TortoiseProc.exe"

def convert_paths(paths: List[Path]) -> str:
    '''try convert given path into tortoise svn format'''
    if isinstance(paths, str):
        paths = Path(paths)
    if isinstance(paths, Path):
        paths = [paths]
    if isinstance(paths, list):
        logger.info(f"show commit paths {paths}")
        strings = []
        for p in paths:
            strings.append(str(p))
        return "*".join(strings)
    raise ValueError(f"can't convert given path {paths}")

def run_tortoise_command(command: str, path, close_end: int = 0):
    '''internal command for running tortoise svn command'''
    if not command:
        raise ValueError(f"command not valid, got: {command}")
    commands = [TORTOISE_SVN_PROC, f"/command:{command}"]
    if path:
        path_string = convert_paths(path)
        commands.append(f'/path:"{path_string}"')
    commands.append(f"/closeend:{close_end}")
    subprocess.Popen(" ".join(commands))

def commit(path_or_path_list):
    '''commit given file item with tortoise svn'''
    run_tortoise_command(COMMIT_CMD, path_or_path_list)

def update(path_or_path_list):
    '''update given file item with tortoise svn'''
    run_tortoise_command(UPDATE_CMD, path_or_path_list)

def blame(path_or_path_list):
    '''blame given file item with tortoise svn'''
    run_tortoise_command(BLAME_CMD, path_or_path_list)

def log(path_or_path_list):
    '''show log of given file item with tortoise svn'''
    run_tortoise_command(LOG_CMD, path_or_path_list)

def revert(path_or_path_list):
    '''revert given file item with tortoise svn'''
    run_tortoise_command(REVERT_CMD, path_or_path_list)
