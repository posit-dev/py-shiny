from typing import Union
import tempfile
import os

from . import utils

class FileUploadManager:
    def __init__(self):
        self._basedir: str = tempfile.mkdtemp(prefix = "fileupload-")
        self._ids: set[str] = set()

    def create_upload_operation(self, file_infos: list[dict[str, Union[str, int]]]):
        # [{'name': 'file.html', 'size': 18, 'type': 'text/html'}]
        id = utils.rand_hex(12)
        self._ids.add(id)
        return id

    def has_upload_operation(self, id: str):
        if id in self._ids:
            return True
        else:
            return False

    def write_chunk(self, id: str, chunk: bytes):
        filename = os.path.join(self._basedir, id)
        with open(filename, "ab") as f:
            f.write(chunk)
