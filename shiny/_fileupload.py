# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

import copy
import os
import pathlib
import shutil
import tempfile
from typing import BinaryIO, List, Optional, cast

from . import _utils
from .types import FileInfo

# File uploads happen through a series of requests. This requires a browser
# which supports the HTML5 File API.
#
# 1. Client tells server that one or more files are about to be uploaded, with
#    an "uploadInit" message; the server responds with a "jobId" and "uploadUrl"
#    that the client should use to upload the files. From the server's
#    perspective, the messages look like this:
#    RECV {"method":"uploadInit","args":[[{"name":"mtcars.csv","size":1303,"type":"text/csv"}]],"tag":2}
#    SEND {"response":{"tag":2,"value":{"jobId":"1651ddebfb643a26e6f18aa1","uploadUrl":"session/3cdbe3c4d1318225fee8f2e3417a1c99/upload/1651ddebfb643a26e6f18aa1?w="}}}
#
# 2. For each file (sequentially):
#    b. Client makes a POST request with the file data.
#    c. Server sends a 200 response to the client.
#
# 3. Repeat 2 until all files have been uploaded.
#
# 4. Client tells server that all files have been uploaded, along with the
#    input ID that this data should be associated with. The server responds
#    with the tag ID and a null message. The messages look like this:
#    RECV {"method":"uploadEnd","args":["1651ddebfb643a26e6f18aa1","file1"],"tag":3}
#    SEND {"response":{"tag":3,"value":null}}


class FileUploadOperation:
    def __init__(
        self, parent: FileUploadManager, id: str, dir: str, file_infos: List[FileInfo]
    ) -> None:
        self._parent: FileUploadManager = parent
        self._id: str = id
        self._dir: str = dir
        # Copy file_infos and add a "datapath" entry for each file.
        self._file_infos: list[FileInfo] = [
            cast(FileInfo, {**fi, "datapath": ""}) for fi in copy.deepcopy(file_infos)
        ]
        self._n_uploaded: int = 0
        self._current_file_obj: Optional[BinaryIO] = None

    # Start uploading one of the files.
    def file_begin(self) -> None:
        file_info: FileInfo = self._file_infos[self._n_uploaded]
        file_ext = pathlib.Path(file_info["name"]).suffix
        file_info["datapath"] = os.path.join(
            self._dir, str(self._n_uploaded) + file_ext
        )
        self._current_file_obj = open(file_info["datapath"], "ab")

    # Finish uploading one of the files.
    def file_end(self) -> None:
        if self._current_file_obj is not None:
            self._current_file_obj.close()
        self._current_file_obj = None
        self._n_uploaded += 1

    # Write a chunk of data for the currently-open file.
    def write_chunk(self, chunk: bytes) -> None:
        if self._current_file_obj is None:
            raise RuntimeError(f"FileUploadOperation for {self._id} is not open.")
        self._current_file_obj.write(chunk)

    # End the entire operation, which can consist of multiple files.
    def finish(self) -> List[FileInfo]:
        if self._n_uploaded != len(self._file_infos):
            raise RuntimeError(
                f"Not all files for FileUploadOperation {self._id} were uploaded."
            )
        self._parent.on_job_finished(self._id)
        return self._file_infos

    # Context handlers for `with`
    def __enter__(self) -> None:
        self.file_begin()

    def __exit__(self, type, value, trace) -> None:  # type: ignore
        self.file_end()


class FileUploadManager:
    def __init__(self) -> None:
        # TODO: Remove basedir when app exits.
        self._basedir: str = tempfile.mkdtemp(prefix="fileupload-")
        self._operations: dict[str, FileUploadOperation] = {}

    def create_upload_operation(self, file_infos: List[FileInfo]) -> str:
        job_id = _utils.rand_hex(12)
        dir = tempfile.mkdtemp(dir=self._basedir)
        self._operations[job_id] = FileUploadOperation(self, job_id, dir, file_infos)
        return job_id

    def get_upload_operation(self, id: str) -> Optional[FileUploadOperation]:
        if id in self._operations:
            return self._operations[id]
        else:
            return None

    def on_job_finished(self, job_id: str) -> None:
        del self._operations[job_id]

    # Remove the directories containing file uploads; this is to be called when
    # a session ends.
    def rm_upload_dir(self) -> None:
        shutil.rmtree(self._basedir)
