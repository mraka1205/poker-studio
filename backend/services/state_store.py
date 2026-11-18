"""Atomic, lock-protected persistence for projects/<episode_id>/state.json."""
import hashlib
import json
import os
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from backend.services.paths import get_project_dir


class EtagConflict(Exception):
    pass


_LOCKS: Dict[str, threading.RLock] = {}
_GUARD = threading.Lock()


def _lock(episode_id: str) -> threading.RLock:
    with _GUARD:
        return _LOCKS.setdefault(episode_id, threading.RLock())


def state_path(episode_id: str) -> Path:
    return get_project_dir(episode_id) / "state.json"


def write_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def compute_etag(episode_id: str) -> str:
    path = state_path(episode_id)
    if not path.exists():
        return ""
    return hashlib.sha1(path.read_bytes()).hexdigest()[:16]


def read_state(episode_id: str) -> dict:
    with _lock(episode_id):
        return json.loads(state_path(episode_id).read_text(encoding="utf-8-sig"))


def write_state(episode_id: str, state: dict) -> None:
    clean = {k: v for k, v in state.items() if k != "_etag"}
    with _lock(episode_id):
        path = state_path(episode_id)
        if path.exists():
            shutil.copy2(path, path.with_name("state.json.bak"))
        write_json_atomic(path, clean)


def update_state(episode_id: str, mutator: Callable[[dict], None]) -> dict:
    with _lock(episode_id):
        state = read_state(episode_id)
        mutator(state)
        write_state(episode_id, state)
        return state


def apply_patch(episode_id: str, updates: dict, base_etag: Optional[str] = None) -> str:
    with _lock(episode_id):
        if base_etag and base_etag != compute_etag(episode_id):
            raise EtagConflict("state.json changed on disk since it was loaded")
        state = read_state(episode_id)
        state.update(updates)
        write_state(episode_id, state)
        return compute_etag(episode_id)


def snapshot_state(episode_id: str, name: str) -> Path:
    with _lock(episode_id):
        src = state_path(episode_id)
        dest = src.with_name(name)
        shutil.copy2(src, dest)
        return dest


def restore_state_from(episode_id: str, src: Path, keep_rejected_as: Optional[str] = None) -> None:
    with _lock(episode_id):
        dest = state_path(episode_id)
        if keep_rejected_as and dest.exists():
            shutil.copy2(dest, dest.with_name(keep_rejected_as))
        write_json_atomic(dest, json.loads(Path(src).read_text(encoding="utf-8-sig")))
