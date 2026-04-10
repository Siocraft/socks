"""
Local UI for sock .dat preview and image overlay (Streamlit).

Run: py -m streamlit run streamlit_app.py   (Windows)
     python -m streamlit run streamlit_app.py
(Use `-m` so Streamlit is found without `streamlit.exe` on PATH.)
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from add_image_to_dat import SIZE_PRESETS, add_image_to_dat
from dat2bmp import _pattern_visible
from sock_dat_format import EXPECTED_SIZE, HEIGHT, WIDTH, load_dat_rgb

st.set_page_config(page_title="Sock .dat", layout="wide")
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] { margin-bottom: 0.35rem; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    h3 { margin-top: 0.25rem !important; margin-bottom: 0.35rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.header("Sock `.dat` composer")
with st.expander("Format", expanded=False):
    st.caption(
        f"Base file: **{EXPECTED_SIZE:,} bytes** (48-byte header + {WIDTH}×{HEIGHT} RGB). "
        "Only the canvas is changed; header is copied from the base."
    )

col_u1, col_u2 = st.columns(2)
with col_u1:
    st.caption("Base `.dat`")
    base_file = st.file_uploader("base_dat", type=["dat"], label_visibility="collapsed")
with col_u2:
    st.caption("Overlay image")
    overlay_file = st.file_uploader(
        "overlay_img", type=["png", "jpg", "jpeg", "bmp", "webp"], label_visibility="collapsed"
    )

base_preview = None
base_error = None
if base_file is not None:
    raw = base_file.getvalue()
    if len(raw) != EXPECTED_SIZE:
        base_error = f"Wrong size: {len(raw)} bytes (expected {EXPECTED_SIZE})."
    else:
        try:
            _, rgb = load_dat_rgb(raw)
            base_preview = _pattern_visible(rgb)
        except Exception as e:
            base_error = str(e)

if base_error:
    st.error(base_error)

_THUMB_MAX = 220


def _thumb(img: Image.Image, max_side: int = _THUMB_MAX) -> Image.Image:
    w, h = img.size
    if max(w, h) <= max_side:
        return img
    scale = max_side / max(w, h)
    return img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


pv1, pv2 = st.columns(2)
with pv1:
    if base_preview is not None:
        st.caption("Base (contrast)")
        st.image(_thumb(base_preview), use_container_width=False)
with pv2:
    if overlay_file is not None:
        overlay_preview = Image.open(io.BytesIO(overlay_file.getvalue()))
        st.caption("Overlay (source)")
        st.image(_thumb(overlay_preview.convert("RGB")), use_container_width=False)

preset_names = list(SIZE_PRESETS.keys())
r1, r2, r3 = st.columns([1.1, 1.4, 1])
with r1:
    size_mode = st.radio("Size", ["Preset", "Custom"], horizontal=True, label_visibility="collapsed")
with r2:
    if size_mode == "Preset":
        choice = st.selectbox("Preset", preset_names, index=preset_names.index("64x32"), label_visibility="collapsed")
        size = SIZE_PRESETS[choice]
    else:
        c1, c2 = st.columns(2)
        ow = c1.number_input("W", min_value=1, max_value=WIDTH, value=64)
        oh = c2.number_input("H", min_value=1, max_value=HEIGHT, value=32)
        size = (int(ow), int(oh))
with r3:
    center = st.checkbox("Center", value=True)
    nearest = st.checkbox("Pixel art", value=False)

if not center:
    px, py = st.columns(2)
    pos_x = px.number_input("X", min_value=0, max_value=WIDTH - 1, value=0)
    pos_y = py.number_input("Y", min_value=0, max_value=HEIGHT - 1, value=0)
    position: tuple[int, int] | None = (int(pos_x), int(pos_y))
else:
    position = None

run = st.button(
    "Compose",
    type="primary",
    disabled=base_file is None or overlay_file is None,
    use_container_width=True,
)

if run and base_file is not None and overlay_file is not None:
    raw = base_file.getvalue()
    if len(raw) != EXPECTED_SIZE:
        st.error(f"Base .dat must be {EXPECTED_SIZE} bytes.")
    else:
        resample = Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            base_path = td_path / "base.dat"
            img_path = td_path / "overlay.png"
            out_path = td_path / "out.dat"
            base_path.write_bytes(raw)
            img_path.write_bytes(overlay_file.getvalue())
            try:
                add_image_to_dat(
                    base_path,
                    img_path,
                    out_path,
                    size=size,
                    position=position,
                    resample=resample,
                )
                out_bytes = out_path.read_bytes()
                st.session_state["composed_dat"] = out_bytes
                st.session_state["composed_name"] = (
                    f"{Path(base_file.name).stem}_with_{Path(overlay_file.name).stem}.dat"
                )
            except Exception as e:
                st.error(str(e))

if "composed_dat" in st.session_state and st.session_state["composed_dat"]:
    dat_bytes = st.session_state["composed_dat"]
    _, out_rgb = load_dat_rgb(dat_bytes)
    st.caption("Result (contrast)")
    st.image(_thumb(_pattern_visible(out_rgb)), use_container_width=False)
    st.download_button(
        "Download `.dat`",
        data=dat_bytes,
        file_name=st.session_state.get("composed_name", "composed.dat"),
        mime="application/octet-stream",
        use_container_width=True,
    )
