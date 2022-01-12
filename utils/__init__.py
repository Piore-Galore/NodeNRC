#-*-coding:utf8-*-

'''这里有很多共用的函数'''

import os
import re
import getpass
import shutil
import platform
import subprocess
import sys
import webbrowser
from time import time
from typing import Dict
from pathlib import Path
from functools import lru_cache

from svn.exception import SvnException
from svn.local import LocalClient

from .logger import logger

TRUNK = "trunk"
STRIP_USERNAME = r"Username: (?P<name>.*)"
SVN_CMD = "svn"
WINDOWS = 'Windows'
MAC = 'Darwin'
IGNORED_ACCOUNT = ('next_ci', 'kobuilder')

@lru_cache(maxsize=1)
def get_svn_info(file_path=None) -> Dict[str, str]:
    '''get svn related info
    获取当前目录的svn项目信息，包括用户id，svn项目名称，分支名称等
    '''
    try:
        svn_path = find_svn()
        folder = Path(__file__) if not file_path else Path(file_path)
        if not folder.is_dir():
            folder = folder.parent
        client = LocalClient(folder.as_posix(), svn_filepath=svn_path)
        info = client.info()
        url = info['url']
        url_segs = url.replace("http://", "").split("/")
        realm = url_segs[1].upper()
        user = get_svn_auth(realm, svn_path)
        if not user:
            user = getpass.getuser().lower()
        branch = TRUNK if url_segs[3] == TRUNK else "/".join(url_segs[3:4])
        return {
            'svn': svn_path,
            'user': user,
            'realm': realm,
            'branch': branch,
            'info': info
        }
    except SvnException:
        logger.exception("failed to get realm")
        return None

def get_realm():
    '''get realm of current svn repo
    获取当前目录的svn项目名称
    '''
    try:
        info = get_svn_info()
        return info['realm']
    except SvnException:
        logger.exception("failed to get realm")
        return ""

def extract_username(line: bytes):
    '''extract username from svn commands'''
    line = line.decode('utf8')
    match = re.match(STRIP_USERNAME, line)
    if not match:
        return None
    group = match.groupdict()
    return group.get("name")

def get_svn_auth(realm: str, svn_path: str) -> str:
    '''extract svn auth with command line'''
    if realm == "":
        return None
    lines = ""
    try:
        lines = subprocess.check_output([svn_path, "auth", realm])
    except subprocess.CalledProcessError:
        logger.exception("error when trying to get auth")
    valid_users = []
    for line in lines.splitlines():
        name = extract_username(line)
        if not name:
            continue
        valid_users.append(name)
    count = len(valid_users)
    if count == 0:
        return None
    if count == 1:
        return valid_users[0]
    for user in valid_users:
        if user in IGNORED_ACCOUNT:
            continue
        return user
    return None

def check_file_usable(path: Path) -> bool:
    '''check if given path exists and usable'''
    if not path:
        return False
    if not path.exists():
        return True
    if not path.is_file():
        return True
    try:
        # must use 'ab' here. w or wb will change the content of the file
        path.open(mode="ab")
        return True
    except IOError:
        return False

@lru_cache(maxsize=1)
def find_svn() -> str:
    '''find a valid svn path'''
    svn_path = shutil.which(SVN_CMD)
    if svn_path:
        return svn_path
    logger.info("can't find svn in system path, try to find it in engine")
    python_path = Path(sys.executable)
    if '/Engine/Binaries/ThirdParty/Python3/' in python_path.as_posix():
        third = python_path
        while third and third.name:
            if third.name == "ThirdParty":
                break
            third = third.parent
        guess_path = third / 'svn' / 'Win64' / 'svn.exe'
        if guess_path.exists():
            return str(guess_path.absolute())
        else:
            logger.info("can't find svn in engine")
    return "svn"

def open_by_default(file: Path):
    '''open a file with system default program'''
    file_path = str(file.absolute())
    plat = platform.platform()
    if WINDOWS in plat:
        os.startfile(file_path)
    elif MAC in plat:
        subprocess.Popen(('open', file_path))
    else:
        subprocess.Popen(('xdg-open', file_path))

def open_wechat_work(user: str) -> None:
    '''open chat with given user name'''
    webbrowser.open(f"wxwork://message?username={user}")

def timer(func):
    def wrap_func(*args, **kwargs):
        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        logger.info(f"Function {func.__name__!r} executed in {(time_end-time_start):.4f}s")
        return result
    return wrap_func
