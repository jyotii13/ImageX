from PIL import Image

from imagex.features.grayscale import run


class TestGrayscaleRun:
    def test_grayscale_converts_mode(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        out = tmp_path / "gray.jpg"
        assert run(src, out, {"mode": "grayscale"})

        result = Image.open(out)
        assert result.mode == "L"

    def test_grayscale_preserves_size(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        img = Image.open(src)
        out = tmp_path / "gray.png"
        assert run(src, out, {"mode": "grayscale"})

        result = Image.open(out)
        assert result.width == img.width
        assert result.height == img.height

    def test_bw_threshold_high(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        out = tmp_path / "white.png"
        assert run(src, out, {"mode": "bw", "threshold": 255})

        result = Image.open(out)
        assert result.mode == "L"
        # threshold 255 means everything below 255 becomes black
        # our red image (255,0,0) -> L ~ 76 -> 0 = black
        assert result.getpixel((0, 0)) == 0

    def test_bw_threshold_low(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        out = tmp_path / "black.png"
        assert run(src, out, {"mode": "bw", "threshold": 0})

        result = Image.open(out)
        # threshold 0 means only pure black stays black
        # our red image -> L ~ 76 -> 255 = white
        assert result.getpixel((0, 0)) == 255

    def test_run_without_args_raises(self, tmp_images, tmp_path):
        src = tmp_images / "test.jpg"
        out = tmp_path / "out.jpg"
        try:
            run(src, out, None)
            assert False, "should have raised"
        except ValueError as e:
            assert "args required" in str(e).lower()
