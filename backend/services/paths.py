import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
_EPISODE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_SCENE_RE = re.compile(r"^scene_\d{2,3}$")


class InvalidIdError(ValueError):
    pass


def projects_dir() -> Path:
    """projects/ root; override with env POKER_STUDIO_PROJECTS_DIR (used by tests)."""
    return Path(os.environ.get("POKER_STUDIO_PROJECTS_DIR") or (BASE_DIR / "projects")).resolve()


def validate_episode_id(value: str) -> str:
    if not isinstance(value, str) or not _EPISODE_RE.fullmatch(value):
        raise InvalidIdError(f"Invalid episode id: {value!r}")
    return value


def validate_scene_id(value: str) -> str:
    if not isinstance(value, str) or not _SCENE_RE.fullmatch(value):
        raise InvalidIdError(f"Invalid scene id: {value!r}")
    return value


def get_project_dir(episode_id: str) -> Path:
    validate_episode_id(episode_id)
    root = projects_dir()
    path = (root / episode_id).resolve()
    if path.parent != root:
        raise InvalidIdError(f"Episode path escapes projects dir: {episode_id!r}")
    return path
