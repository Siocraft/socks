#!/usr/bin/env python3
"""
Convert .dat image files (48-byte header + raw RGB) to .bmp.
Expected size: 80208 bytes = 48 header + 160×167×3 RGB.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

from sock_dat_format import load_dat_rgb


def _pattern_visible(img: Image.Image, gamma: float = 0.45) -> Image.Image:
    """Make the design much more visible: percentile stretch + gamma brightening."""
    r, g, b = img.split()
    n = r.size[0] * r.size[1]
    result_r, result_g, result_b = [0] * n, [0] * n, [0] * n

    for channel, result in ((r, result_r), (g, result_g), (b, result_b)):
        arr = list(channel.get_flattened_data())
        non_zero = [x for x in arr if x > 0]
        if not non_zero:
            continue
        non_zero.sort()
        lo = non_zero[max(0, int(0.02 * len(non_zero)) - 1)]
        hi = non_zero[min(len(non_zero) - 1, int(0.98 * len(non_zero)))]
        if hi <= lo:
            hi = lo + 1
        for i, x in enumerate(arr):
            if x <= lo:
                v = 0.0
            else:
                v = min(255.0, (x - lo) * 255.0 / (hi - lo))
            v = 255.0 * (v / 255.0) ** gamma
            result[i] = round(min(255, v))

    out = Image.new("RGB", img.size)
    out.putdata(list(zip(result_r, result_g, result_b)))
    return out


def dat_to_bmp(
    dat_path: Path,
    bmp_path: Path | None = None,
    *,
    also_pattern: bool = False,
) -> tuple[Path, Path | None]:
    """Read a .dat file and write a .bmp file. Returns (raw_bmp_path, pattern_bmp_path or None)."""
    data = dat_path.read_bytes()
    _, img = load_dat_rgb(data)
    out = bmp_path or dat_path.with_suffix(".bmp")
    img.save(out, format="BMP")
    pattern_path: Path | None = None
    if also_pattern:
        base = out.with_suffix("")
        pattern_path = Path(f"{base}_pattern.bmp")
        stretched = _pattern_visible(img)
        stretched.save(pattern_path, format="BMP")
    return (out, pattern_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert .dat image files (48-byte header + 160×167 RGB) to .bmp."
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="+",
        help="Path(s) to .dat file(s) or directory/directories containing .dat files",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for .bmp outputs (default: same as each input file)",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing .bmp files",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        action="store_true",
        help="Also write a contrast-stretched _pattern.bmp so the design is visible",
    )
    args = parser.parse_args()

    inputs: list[Path] = []
    for p in args.input:
        if p.is_dir():
            inputs.extend(sorted(p.glob("*.dat")))
        else:
            inputs.append(p)

    out_dir = args.output_dir
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    for dat_path in inputs:
        if not dat_path.exists():
            print(f"Skip (not found): {dat_path}", file=sys.stderr)
            continue
        if dat_path.suffix.lower() != ".dat":
            print(f"Skip (not .dat): {dat_path}", file=sys.stderr)
            continue
        bmp_path = (out_dir / dat_path.name).with_suffix(".bmp") if out_dir else None
        if bmp_path is None:
            bmp_path = dat_path.with_suffix(".bmp")
        if bmp_path.exists() and not args.force:
            print(f"Skip (exists, use -f to overwrite): {bmp_path}", file=sys.stderr)
            continue
        try:
            raw_out, pattern_out = dat_to_bmp(dat_path, bmp_path, also_pattern=args.pattern)
            print(raw_out)
            if pattern_out is not None:
                print(pattern_out)
            ok += 1
        except Exception as e:
            print(f"Error converting {dat_path}: {e}", file=sys.stderr)

    if ok == 0 and inputs:
        sys.exit(1)


if __name__ == "__main__":
    main()
