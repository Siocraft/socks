"""Tests for Winpds .dat RGB layout helpers."""

from __future__ import annotations

import pytest
from PIL import Image

from sock_dat_format import (
    HEADER_SIZE,
    HEIGHT,
    WIDTH,
    EXPECTED_SIZE,
    dump_dat_rgb,
    load_dat_rgb,
    validate_dat_bytes,
)


def test_round_trip_bytes_identical() -> None:
    header = bytes((i * 3) % 256 for i in range(HEADER_SIZE))
    img = Image.new("RGB", (WIDTH, HEIGHT), (17, 200, 99))
    data = dump_dat_rgb(header, img)
    assert len(data) == EXPECTED_SIZE
    h2, img2 = load_dat_rgb(data)
    assert h2 == header
    assert img2.tobytes() == img.tobytes()


def test_validate_dat_bytes_wrong_size() -> None:
    with pytest.raises(ValueError, match="Unexpected .dat size"):
        validate_dat_bytes(b"short")


def test_dump_dat_wrong_header_length() -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), (1, 2, 3))
    with pytest.raises(ValueError, match="Header must be"):
        dump_dat_rgb(b"\x00" * 47, img)


def test_ensure_resize_via_dump() -> None:
    """Smaller images are expanded to canvas via ensure_rgb_canvas inside dump."""
    header = b"\xab" * HEADER_SIZE
    small = Image.new("RGB", (10, 10), (255, 0, 0))
    data = dump_dat_rgb(header, small)
    _, full = load_dat_rgb(data)
    assert full.size == (WIDTH, HEIGHT)
