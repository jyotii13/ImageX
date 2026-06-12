from PIL import Image

from imagex.features.rotate import run


class TestRotateRun:
    def test_rotate_right(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        img = Image.open(src)
        out = tmp_path / "right.png"
        assert run(src, out, {"method": Image.ROTATE_270})

        rotated = Image.open(out)
        assert rotated.width == img.height
        assert rotated.height == img.width

    def test_rotate_left(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        img = Image.open(src)
        out = tmp_path / "left.png"
        assert run(src, out, {"method": Image.ROTATE_90})

        rotated = Image.open(out)
        assert rotated.width == img.height
        assert rotated.height == img.width

    def test_rotate_180(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        out = tmp_path / "180.png"
        assert run(src, out, {"method": Image.ROTATE_180})

        rotated = Image.open(out)
        original = Image.open(src)
        assert rotated.width == original.width
        assert rotated.height == original.height

    def test_preserves_format(self, tmp_images, tmp_path):
        src = tmp_images / "image.webp"
        out = tmp_path / "out.webp"
        assert run(src, out, {"method": Image.ROTATE_90})

        rotated = Image.open(out)
        assert rotated.format == "WEBP"

    def test_run_without_args_raises(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        out = tmp_path / "out.jpg"
        try:
            run(src, out, None)
            assert False, "should have raised"
        except ValueError as e:
            assert "args required" in str(e).lower()
