from PIL import Image
from scripts.verify_frames import check_image, histogram, intersection


def test_checks(tmp_path):
    good = tmp_path / "g.png"
    Image.effect_noise((540, 960), 40).convert("RGB").save(good)
    bad_ratio = tmp_path / "r.png"
    Image.effect_noise((800, 600), 40).convert("RGB").save(bad_ratio)
    blank = tmp_path / "b.png"
    Image.new("RGB", (540, 960), (10, 90, 40)).save(blank)
    assert check_image(good, None, None, min_bytes=0)["errors"] == []
    assert any("9:16" in e for e in check_image(bad_ratio, None, None, min_bytes=0)["errors"])
    assert any("uniform" in e for e in check_image(blank, None, None, min_bytes=0)["errors"])
    assert check_image(tmp_path / "nope.png", None, None)["errors"] == ["file missing"]
    h = histogram(Image.open(good))
    assert abs(intersection(h, h) - 1.0) < 1e-6
