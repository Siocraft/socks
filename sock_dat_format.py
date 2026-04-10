"""Winpds sock .dat layout used by this repo: 48-byte header + 160×167 RGB."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

HEADER_SIZE = 48
WIDTH = 160
HEIGHT = 167
BYTES_PER_PIXEL = 3
EXPECTED_PAYLOAD = WIDTH * HEIGHT * BYTES_PER_PIXEL
EXPECTED_SIZE = HEADER_SIZE + EXPECTED_PAYLOAD


def validate_dat_bytes(data: bytes) -> None:
    if len(data) != EXPECTED_SIZE:
        raise ValueError(
            f"Unexpected .dat size: {len(data)} (expected {EXPECTED_SIZE}). "
            f"Format may differ; this tool assumes a {HEADER_SIZE}-byte header + "
            f"{WIDTH}×{HEIGHT} RGB."
        )


def load_dat_rgb(data: bytes) -> tuple[bytes, Image.Image]:
    """Split raw file bytes into header and an RGB PIL image (WIDTH×HEIGHT)."""
    validate_dat_bytes(data)
    header = data[:HEADER_SIZE]
    pixels = data[HEADER_SIZE:]
    img = Image.frombytes("RGB", (WIDTH, HEIGHT), pixels)
    return header, img


def ensure_rgb_canvas(img: Image.Image) -> Image.Image:
    """Return a WIDTH×HEIGHT RGB image, resizing with nearest if needed."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.size != (WIDTH, HEIGHT):
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
    return img


def dump_dat_rgb(header: bytes, img: Image.Image) -> bytes:
    """Concatenate header with raw RGB bytes. Header must be length HEADER_SIZE."""
    if len(header) != HEADER_SIZE:
        raise ValueError(f"Header must be {HEADER_SIZE} bytes, got {len(header)}")
    body = ensure_rgb_canvas(img)
    return header + body.tobytes()


def read_dat_file(path: Path) -> tuple[bytes, Image.Image]:
    return load_dat_rgb(path.read_bytes())


def write_dat_file(path: Path, header: bytes, img: Image.Image) -> None:
    path.write_bytes(dump_dat_rgb(header, img))
