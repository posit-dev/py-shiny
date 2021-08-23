from typing import Union, Optional, BinaryIO
import tempfile
import os
import copy

from . import utils

# Information about a single file, with a structure like:
#   {'name': 'mtcars.csv', 'size': 1303, 'type': 'text/csv'}
FileInfo = dict[str, Union[str, int]]

class FileUploadOperation:
    def __init__(self, parent: 'FileUploadManager', id: str, dir: str, file_infos: list[FileInfo]) -> None:
        self._parent: FileUploadManager = parent
        self._id: str = id
        self._dir: str = dir
        # Copy file_infos and add a "datapath" entry for each file.
        self._file_infos: list[FileInfo] = [{**fi, "datapath": ""} for fi in copy.deepcopy(file_infos)]
        self._n_uploaded: int = 0
        self._current_file_obj: Optional[BinaryIO] = None

    # Start uploading one of the files.
    def file_begin(self) -> None:
        file_info: FileInfo = self._file_infos[self._n_uploaded]
        file_info["datapath"] = os.path.join(self._dir, str(file_info["name"]))
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
    def finish(self) -> list[FileInfo]:
        if self._n_uploaded != len(self._file_infos):
            raise RuntimeError(f"Not all files for FileUploadOperation {self._id} were uploaded.")
        self._parent.on_job_finished(self._id)
        return self._file_infos

    # Context handlers for `with`
    def __enter__(self) -> None:
        self.file_begin()

    def __exit__(self, type, value, trace) -> None:
        self.file_end()


class FileUploadManager:
    def __init__(self) -> None:
        self._dir: str = tempfile.mkdtemp(prefix = "fileupload-")
        self._operations: dict[str, FileUploadOperation] = {}

    def create_upload_operation(self, file_infos: list[FileInfo]) -> str:
        job_id = utils.rand_hex(12)
        self._operations[job_id] = FileUploadOperation(self, job_id, self._dir, file_infos)
        return job_id

    def get_upload_operation(self, id: str) -> Optional[FileUploadOperation]:
        if id in self._operations:
            return self._operations[id]
        else:
            return None

    def on_job_finished(self, job_id: str) -> None:
        del self._operations[job_id]
