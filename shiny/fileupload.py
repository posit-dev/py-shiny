from typing import Union, Optional, BinaryIO
import tempfile
import os

from . import utils

class FileUploadOperation:
    def __init__(self, id: str, dir: str, file_infos: list[dict[str, Union[str, int]]]) -> None:
        self._id = id
        self._dir = dir
        self._file_infos = file_infos
        self._file_obj: Optional[BinaryIO] = None

    def __enter__(self) -> None:
        filename = os.path.join(self._dir, self._id)
        print("UPLOAD ENTER: ", filename)
        self._file_obj = open(filename, "ab")

    def __exit__(self, type, value, trace) -> None:
        if self._file_obj is not None:
            self._file_obj.close()
        self._file_obj = None

    def write_chunk(self, chunk: bytes) -> None:
        if self._file_obj is None:
            raise RuntimeError(f"FileUploadOperation {self._id} is not open.")
        self._file_obj.write(chunk)

    def finish(self) -> str:
        return os.path.join(self._dir, self._id)

class FileUploadManager:
    def __init__(self) -> None:
        self._dir: str = tempfile.mkdtemp(prefix = "fileupload-")
        self._operations: dict[str, FileUploadOperation] = {}

    def create_upload_operation(self, file_infos: list[dict[str, Union[str, int]]]) -> str:
        # [{'name': 'file.html', 'size': 18, 'type': 'text/html'}]
        id = utils.rand_hex(12)
        self._operations[id] = FileUploadOperation(id, self._dir, file_infos)
        return id

    def get_upload_operation(self, id: str) -> Optional[FileUploadOperation]:
        if id in self._operations:
            return self._operations[id]
        else:
            return None

