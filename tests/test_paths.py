import pytest
from backend.services.paths import (InvalidIdError, get_project_dir, projects_dir,
                                    validate_episode_id, validate_scene_id)


@pytest.mark.parametrize("bad", ["", "..", "../x", "a/b", "a\\b", "-x", "a" * 65, "ep 1", "ep01.sample", None])
def test_bad_episode_ids(bad):
    with pytest.raises(InvalidIdError):
        validate_episode_id(bad)


@pytest.mark.parametrize("ok", ["ep01-sample", "ep02--playwithjj", "ep04-poker-hand", "a"])
def test_good_episode_ids(ok):
    assert validate_episode_id(ok) == ok
    assert get_project_dir(ok) == projects_dir() / ok


def test_scene_ids():
    assert validate_scene_id("scene_01") == "scene_01"
    for bad in ["scene_1", "scene_01.png", "../scene_01", "scene_0001"]:
        with pytest.raises(InvalidIdError):
            validate_scene_id(bad)
