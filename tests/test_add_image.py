"""Integration tests for add_image_to_dat."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from add_image_to_dat import add_image_to_dat
from sock_dat_format import HEADER_SIZE, HEIGHT, WIDTH, dump_dat_rgb, load_dat_rgb


def test_add_image_preserves_header(tmp_path: Path) -> None:
    header = bytes((i * 7) % 256 for i in range(HEADER_SIZE))
    base = dump_dat_rgb(header, Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 10)))
    dat_path = tmp_path / "base.dat"
    dat_path.write_bytes(base)

    overlay_path = tmp_path / "overlay.png"
    Image.new("RGB", (4, 4), (255, 0, 0)).save(overlay_path)

    out_path = tmp_path / "out.dat"
    add_image_to_dat(
        dat_path,
        overlay_path,
        out_path,
        size=(4, 4),
        position=(0, 0),
        resample=Image.Resampling.NEAREST,
    )

    out_bytes = out_path.read_bytes()
    assert out_bytes[:HEADER_SIZE] == header
    h2, img2 = load_dat_rgb(out_bytes)
    assert h2 == header
    assert img2.getpixel((0, 0)) == (255, 0, 0)
