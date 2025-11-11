from pathlib import Path
import json

from app.core.utils import load_storage, save_storage


def test_load_storage_returns_empty_for_missing_file(tmp_path: Path) -> None:
    target = tmp_path / "data.json"

    assert load_storage(target) == {}


def test_save_storage_persists_data(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    payload = {"key": "value"}

    save_storage(target, payload)

    assert json.loads(target.read_text(encoding="utf-8")) == payload
    assert load_storage(target) == payload

