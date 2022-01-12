#-*-coding:utf8-*-

import collections
import xml.etree
import svn.constants

import svn.local

from utils import find_svn
from utils.logger import logger

_STATUS_ENTRY = \
    collections.namedtuple(
        '_STATUS_ENTRY', [
            'name',
            'type_raw_name',
            'type',
            'revision',
        ])

class RocoSvnClient(svn.local.LocalClient):
    '''a customized svn client for new roco'''

    def __init__(self, path_, *args, **kwargs):
        if 'svn_filepath' not in kwargs:
            local_svn = find_svn()
            kwargs['svn_filepath'] = local_svn
            logger.debug(f"uses local svn {local_svn}")
        super().__init__(path_, *args, **kwargs)

    def __repr__(self):
        return f"<SVN(ROCO/LOCAL) {self.path}"

    def status(self, rel_path=None):
        return self.internal_status(rel_path=rel_path, update=False)

    def status_update(self, rel_path=None):
        return self.internal_status(rel_path=rel_path, update=True)

    def internal_status(self, rel_path=None, update=False):
        path = self.path
        if rel_path is not None:
            path += '/' + rel_path

        cmd = ['--xml', path]

        if update:
            cmd.append('-u')

        raw = self.run_command(
            'status', cmd,
            do_combine=True)

        root = xml.etree.ElementTree.fromstring(raw)

        list_ = root.findall('target/entry') + root.findall('changelist/entry')
        for entry in list_:
            entry_attr = entry.attrib
            name = entry_attr['path']

            wcstatus = entry.find('wc-status')
            wcstatus_attr = wcstatus.attrib

            change_type_raw = wcstatus_attr['item']
            change_type = svn.constants.STATUS_TYPE_LOOKUP[change_type_raw]

            # This will be absent if the file is "unversioned". It'll be "-1"
            # if added but not committed.
            revision = wcstatus_attr.get('revision')
            if revision is not None:
                revision = int(revision)

            yield _STATUS_ENTRY(
                name=name,
                type_raw_name=change_type_raw,
                type=change_type,
                revision=revision
            )
