from __future__ import annotations

from pathlib import Path
from typing import cast

from shiny.bookmark._serializers import is_unserializable, serializer_file_input


def _upload(tmp_path: Path, job: str, content: bytes) -> dict[str, str | int]:
    # Each upload job writes its files into its own folder, named by position,
    # so the first file of every job is `0.csv`.
    upload_dir = tmp_path / job
    upload_dir.mkdir()
    datapath = upload_dir / "0.csv"
    datapath.write_bytes(content)
    return {
        "name": "x.csv",
        "size": len(content),
        "type": "text/csv",
        "datapath": str(datapath),
    }


def _save(file_info: dict[str, str | int], state_dir: Path) -> str:
    """Bookmark one uploaded file and return its saved name."""
    saved = serializer_file_input([file_info], state_dir)
    assert not is_unserializable(saved)
    return cast("list[dict[str, str]]", saved)[0]["datapath"]


def test_file_inputs_with_same_file_name_keep_their_own_file(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    a = _save(_upload(tmp_path, "job_a", b"AAA"), state_dir)
    b = _save(_upload(tmp_path, "job_b", b"BBB"), state_dir)

    assert a != b
    assert (state_dir / a).read_bytes() == b"AAA"
    assert (state_dir / b).read_bytes() == b"BBB"


def test_saved_file_names_are_bare_and_keep_their_suffix(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    names = [_save(_upload(tmp_path, f"job_{i}", b"x"), state_dir) for i in range(3)]

    assert len(set(names)) == 3
    for name in names:
        assert Path(name).name == name
        assert Path(name).suffix == ".csv"
