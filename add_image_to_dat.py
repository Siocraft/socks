#!/usr/bin/env python3
"""
Add an image onto a .dat sock design. Resize the image to a chosen size and composite
onto the canvas. Output is a new .dat file.
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image

# Same format as dat2bmp
HEADER_SIZE = 48
WIDTH = 160
HEIGHT = 167
BYTES_PER_PIXEL = 3
EXPECTED_PAYLOAD = WIDTH * HEIGHT * BYTES_PER_PIXEL
EXPECTED_SIZE = HEADER_SIZE + EXPECTED_PAYLOAD

SIZE_PRESETS = {
    "8x8": (8, 8),
    "16x16": (16, 16),
    "32x32": (32, 32),
    "64x32": (64, 32),
    "32x64": (32, 64),
    "64x64": (64, 64),
    "80x80": (80, 80),
    "80x40": (80, 40),
    "160x167": (160, 167),  # full canvas
}


def _parse_size(s: str) -> tuple[int, int]:
    m = re.match(r"^(\d+)\s*[x×]\s*(\d+)$", s.strip(), re.IGNORECASE)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        if 0 < w <= WIDTH and 0 < h <= HEIGHT:
            return (w, h)
        raise ValueError(f"Size {s} must be within 1x1 to {WIDTH}x{HEIGHT}")
    if s.strip().lower() in SIZE_PRESETS:
        return SIZE_PRESETS[s.strip().lower()]
    raise ValueError(
        f"Invalid size '{s}'. Use WxH (e.g. 64x32) or preset: {', '.join(SIZE_PRESETS)}"
    )


def _dat_to_pil(data: bytes) -> Image.Image:
    if len(data) != EXPECTED_SIZE:
        raise ValueError(f"Expected .dat size {EXPECTED_SIZE}, got {len(data)}")
    pixels = data[HEADER_SIZE:]
    return Image.frombytes("RGB", (WIDTH, HEIGHT), pixels)


def _pil_to_dat(header: bytes, img: Image.Image) -> bytes:
    if img.size != (WIDTH, HEIGHT) or img.mode != "RGB":
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
        if img.mode != "RGB":
            img = img.convert("RGB")
    return header + img.tobytes()


def add_image_to_dat(
    base_dat_path: Path,
    image_path: Path,
    output_dat_path: Path,
    size: tuple[int, int],
    position: tuple[int, int] | None = None,
    resample: int = Image.Resampling.LANCZOS,
) -> Path:
    """
    Composite image onto base .dat and write a new .dat.
    position is (x, y) top-left; if None, image is centered.
    """
    data = base_dat_path.read_bytes()
    header = data[:HEADER_SIZE]
    base_img = _dat_to_pil(data)

    overlay = Image.open(image_path)
    if overlay.mode == "RGBA":
        overlay_rgb = Image.new("RGB", overlay.size, (0, 0, 0))
        overlay_rgb.paste(overlay, mask=overlay.split()[3])
    else:
        overlay_rgb = overlay.convert("RGB")

    ow, oh = size
    overlay_resized = overlay_rgb.resize((ow, oh), resample)

    if position is None:
        # center on canvas
        x = max(0, (WIDTH - ow) // 2)
        y = max(0, (HEIGHT - oh) // 2)
    else:
        x, y = position

    # clip to canvas
    x = max(0, min(x, WIDTH - 1))
    y = max(0, min(y, HEIGHT - 1))

    if overlay_resized.mode == "RGBA":
        base_img.paste(overlay_resized, (x, y), overlay_resized.split()[3])
    else:
        base_img.paste(overlay_resized, (x, y))

    out_data = _pil_to_dat(header, base_img)
    output_dat_path.write_bytes(out_data)
    return output_dat_path


def main() -> None:
    presets_str = ", ".join(SIZE_PRESETS)
    parser = argparse.ArgumentParser(
        description="Add an image onto a .dat sock design with chosen size."
    )
    parser.add_argument(
        "base_dat",
        type=Path,
        help="Path to the base .dat design",
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Path to the image to add (e.g. PNG)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output .dat path or directory (if dir, file is named <base>_with_<image>.dat)",
    )
    parser.add_argument(
        "-s",
        "--size",
        default="64x32",
        metavar="WxH|preset",
        help=f"Size of the image on the canvas. Presets: {presets_str}. Default: 64x32",
    )
    parser.add_argument(
        "-p",
        "--position",
        type=str,
        default=None,
        metavar="X,Y",
        help="Top-left position (default: center)",
    )
    parser.add_argument(
        "--nearest",
        action="store_true",
        help="Use nearest-neighbor resize (pixel-art style) instead of smooth",
    )
    args = parser.parse_args()

    try:
        size = _parse_size(args.size)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    position = None
    if args.position is not None:
        parts = args.position.replace(",", " ").split()
        if len(parts) != 2:
            print("Error: --position must be X,Y (e.g. 10,20)", file=sys.stderr)
            sys.exit(1)
        try:
            position = (int(parts[0]), int(parts[1]))
        except ValueError:
            print("Error: position must be two integers", file=sys.stderr)
            sys.exit(1)

    if not args.base_dat.exists():
        print(f"Error: base .dat not found: {args.base_dat}", file=sys.stderr)
        sys.exit(1)
    if not args.image.exists():
        print(f"Error: image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if output_path.suffix.lower() != ".dat":
        output_path = output_path / f"{args.base_dat.stem}_with_{args.image.stem}.dat"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resample = Image.Resampling.NEAREST if args.nearest else Image.Resampling.LANCZOS
    try:
        out = add_image_to_dat(
            args.base_dat,
            args.image,
            output_path,
            size=size,
            position=position,
            resample=resample,
        )
        print(out)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
