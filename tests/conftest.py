import pytest


@pytest.fixture(autouse=True)
def _isolated_projects_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("POKER_STUDIO_PROJECTS_DIR", str(tmp_path))
    return tmp_path
