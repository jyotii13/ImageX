from PIL import Image

from imagex.features.invert import run


class TestInvertRun:
    def test_invert_rgb_changes_pixels(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        img = Image.open(src)
        original_pixel = img.getpixel((0, 0))
        out = tmp_path / "inverted.png"
        assert run(src, out, {})

        result = Image.open(out)
        inverted = result.getpixel((0, 0))
        # red (255,0,0) -> cyan (0,255,255)
        expected = tuple(255 - v for v in original_pixel)
        assert inverted == expected

    def test_invert_preserves_size(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        img = Image.open(src)
        out = tmp_path / "inv.png"
        assert run(src, out, {})

        result = Image.open(out)
        assert result.width == img.width
        assert result.height == img.height

    def test_invert_rgba_handles_alpha(self, tmp_images, tmp_path):
        src = tmp_images / "with_alpha.png"
        img = Image.open(src)
        out = tmp_path / "inv_alpha.png"
        assert run(src, out, {})

        result = Image.open(out)
        assert result.mode == "RGBA"
        assert result.width == img.width
        assert result.height == img.height

    def test_invert_white_to_black(self, tmp_path):
        src = tmp_path / "white.png"
        Image.new("RGB", (10, 10), color="white").save(str(src))
        out = tmp_path / "black.png"
        assert run(src, out, {})

        result = Image.open(out)
        assert result.getpixel((0, 0)) == (0, 0, 0)

    def test_invert_black_to_white(self, tmp_path):
        src = tmp_path / "black.png"
        Image.new("RGB", (10, 10), color="black").save(str(src))
        out = tmp_path / "white.png"
        assert run(src, out, {})

        result = Image.open(out)
        assert result.getpixel((0, 0)) == (255, 255, 255)
