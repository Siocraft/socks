# PRD: Winpds `.dat` + image composition

## Problem and context

Winpds uses `.dat` files for sock designs. The product can import a reference image as a faint overlay (“ghost”) for manual recoloring. That workflow becomes tedious quickly as the effective grid grows (for example 24×24 and larger).

## Goal

The user selects a **base `.dat` file path** and a **reference image path**, runs a single command, and receives an **updated `.dat`** whose pixel buffer reflects the composed design—without hand-painting every cell in Winpds.

## Users

- Primary: designers working with Winpds who already have `.dat` bases and PNG/JPG/BMP artwork.

## In scope (MVP)

- Input files that match the **known layout**: **48-byte header** + raw **RGB** payload for **160×167** pixels (**80,208 bytes** total).
- **Non-destructive default:** write a **new** `.dat` (do not overwrite the base file unless the user explicitly chooses the same path).
- **Resize and paste** the image onto the canvas with documented **size presets** or `WxH`, optional **position**, and **nearest** vs smooth resampling.
- **Optional BMP export** of the decoded canvas for inspection outside Winpds (raw BMP and optional contrast-stretched “pattern” preview).

## Out of scope (initial release)

- Other `.dat` sizes, color depths, or Winpds versions not matching the assumptions below.
- Full modeling of every Winpds feature beyond this RGB bitmap payload.
- Graphical UI (optional follow-up: interactive prompts or a small GUI).

## User stories

1. As a designer, I run a CLI with **base `.dat`**, **image path**, and **output path** so I get a new design file I can open in Winpds.
2. As a designer, I **export `.dat` → BMP** to verify dimensions, placement, and colors on disk.
3. As a designer, I can **center** the overlay by default or set a **top-left position** with flags.
4. As a designer, I see **clear errors** when file size, paths, or dimensions are invalid.

## Functional requirements

- Validate that input `.dat` size equals **80,208** bytes before decoding.
- Preserve the **first 48 bytes** of the header **verbatim** on write (semantics unknown; copied for safety).
- Decode payload as **row-major RGB** for width **160** and height **167**.
- **RGBA** sources: composite onto black (same behavior as the reference implementation) before resize/paste.
- CLI flags: output path, size (`WxH` or preset), optional position `X,Y`, `--nearest` for pixel-art scaling.
- `dat2bmp`: accept files or directories of `.dat`; optional `-p` pattern BMP; `-f` force overwrite.

## Technical assumptions

| Field | Value |
|--------|--------|
| Total file size | 80,208 |
| Header | 48 bytes (opaque; preserved) |
| Pixel data | 160 × 167 × 3 bytes RGB, 8 bits per channel |
| Origin / scan order | Top-left, row-major (PIL `RGB` `frombytes`) |

BMP (or PNG) is a **preview and debug interchange** only; Winpds is not expected to read those files. The canonical edit path is **decode → PIL → encode**.

### Winpds compatibility (pattern head / “PDS 8F”)

Winpds does not treat the first 48 bytes as arbitrary padding. When opening a file (for example with **Korea-Robot Drumless**), it reads **pattern data head** information and validates the pattern type. If the header does not match what the reader expects (for example **PDS 8F Pattern**), the software shows an error such as **“Korea-Robot is not PDS 8F Pattern”** and stops loading.

The tools in this repo therefore assume the **base `.dat` was saved by Winpds** (or otherwise already has a valid head for your reader). They **copy those header bytes unchanged** when writing output. A file built only to match the **byte length** 80,208 with a **made-up** header is enough for Python round-trip tests but **will not open in Winpds**. Always start from a real design file for anything you need to open in the app.

## Success criteria

- Winpds opens the output `.dat` without error when the **input** `.dat` already opened correctly with the same reader/settings.
- Visual spot-check: pasted region matches the reference image after resize (within resampling limits).
- **Round-trip (Python):** reading bytes → image → bytes with **no edits** reproduces identical file contents (automated tests use a synthetic payload to check layout only, not Winpds semantics).

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Templates differ in dimensions or layout | Strict size check; extend format module when new samples are confirmed |
| Header fields must change when pixels change | If Winpds rejects files, use binary diff after changing one pixel in Winpds to learn header rules |
| Color interpretation differs from Winpds | Document RGB8; offer `--nearest` and palette-style workflows later if needed |
| Synthetic or hand-built headers fail Winpds validation | Only use bases exported from Winpds; do not expect arbitrary 48-byte headers to load |

## Repository layout

- [`dat-files/`](../dat-files/): put base `.dat` designs here (local-only assets may stay untracked).
- [`images/`](../images/): put overlay images here.
- [`output/`](../output/): generated outputs (gitignored by default).

## Roadmap

| Version | Deliverable |
|---------|-------------|
| v1 | Restored CLIs + shared [`sock_dat_format.py`](../sock_dat_format.py) + PRD + tests |
| v1.1 | Optional `--interactive` path prompts (“press Enter” workflow) |
| v2 | Batch processing; optional unified `socks.py` entrypoint with subcommands |
| v3 | Additional `.dat` variants if discovered and documented |

## References

- Implementation: [`add_image_to_dat.py`](../add_image_to_dat.py), [`dat2bmp.py`](../dat2bmp.py), [`sock_dat_format.py`](../sock_dat_format.py).
