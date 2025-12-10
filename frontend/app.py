import streamlit as st
import requests
import uuid
from typing import List
from PIL import Image
import io

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Retail Media Creative Tool", layout="wide")
st.title("🧠 Retail Media Creative Tool")

# Assign unique user session
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

user_id = st.session_state["user_id"]

# Store uploaded IDs
if "packshot_id" not in st.session_state:
    st.session_state["packshot_id"] = None

if "background_id" not in st.session_state:
    st.session_state["background_id"] = None

# Sidebar
st.sidebar.subheader("Session")
st.sidebar.write(f"User: `{user_id}`")

st.sidebar.subheader("Creative Settings")
fmt = st.sidebar.selectbox("Format", ["story", "feed", "banner"])
canvas_id = st.sidebar.text_input("Canvas ID", value="canvas-" + user_id[:8])
width, height = {"story": (1080, 1920), "feed": (1080, 1080), "banner": (1200, 628)}[fmt]

# Upload helpers
def upload_to_backend(uploaded_file):
    """Uploads file to backend and returns its image_id."""
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        resp = requests.post(f"{BACKEND_URL}/upload", files=files)
        resp.raise_for_status()
        data = resp.json()
        return data["image_id"]
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None

# Upload UI
st.sidebar.markdown("### Assets Upload")

pack_file = st.sidebar.file_uploader("Packshot", ["png", "jpg", "jpeg"])
if pack_file and st.sidebar.button("Upload Packshot"):
    st.session_state["packshot_id"] = upload_to_backend(pack_file)
    st.success(f"Packshot uploaded → {st.session_state['packshot_id']}")

bg_file = st.sidebar.file_uploader("Background (optional)", ["png", "jpg", "jpeg"])
if bg_file and st.sidebar.button("Upload Background"):
    st.session_state["background_id"] = upload_to_backend(bg_file)
    st.success(f"Background uploaded → {st.session_state['background_id']}")

# -----------------------------------------------
# TEXT BLOCKS
# -----------------------------------------------
st.subheader("Text Blocks")
text_blocks: List[dict] = []

cols = st.columns(3)
with cols[0]:
    headline = st.text_input("Headline", "Fresh Strawberries")
with cols[1]:
    price = st.text_input("Price", "£2.50")
with cols[2]:
    tag = st.text_input("Tag", "Available at Tesco")

text_blocks.append({"id": "headline", "text": headline, "font_size": 24, "color": "#000000", "x": 100, "y": 220})
text_blocks.append({"id": "price", "text": price, "font_size": 32, "color": "#FF0000", "x": 100, "y": height - 200})
text_blocks.append({"id": "tag", "text": tag, "font_size": 18, "color": "#000000", "x": 100, "y": 80})

# Build canvas
canvas = {
    "id": canvas_id,
    "user_id": user_id,
    "format": fmt,
    "width": width,
    "height": height,
    "background_image_id": st.session_state["background_id"],
    "packshot_ids": [st.session_state["packshot_id"]] if st.session_state["packshot_id"] else [],
    "text_blocks": text_blocks,
    "extra": {},
}

st.subheader("Preview Canvas JSON")
with st.expander("Show JSON"):
    st.json(canvas)

# -----------------------------------------------
# BUTTONS: VALIDATE  |  AUTOFIX  |  RENDER
# -----------------------------------------------
cols2 = st.columns(3)

# VALIDATE
with cols2[0]:
    if st.button("✅ Validate"):
        resp = requests.post(f"{BACKEND_URL}/validate", json=canvas)
        if resp.ok:
            data = resp.json()
            st.success(f"Validation Passed: {data['passed']}")
            for issue in data["issues"]:
                if issue["severity"] == "error":
                    st.error(f"{issue['code']} → {issue['message']}")
                else:
                    st.warning(f"{issue['code']} → {issue['message']}")
        else:
            st.error(resp.text)

# AUTOFIX
with cols2[1]:
    if st.button("🛠 Auto-Fix"):
        resp = requests.post(f"{BACKEND_URL}/autofix", json={"canvas": canvas})
        if resp.ok:
            data = resp.json()
            st.success("Auto fixes applied.")
            st.json(data["canvas"])
        else:
            st.error(resp.text)

# RENDER
with cols2[2]:
    if st.button("🎨 Render"):
        resp = requests.post(f"{BACKEND_URL}/render", json={"canvas": canvas, "formats": [fmt]})

        if resp.ok:
            data = resp.json()
            st.success("CREATIVE GENERATED 🎉")

            for c in data["creatives"]:
                st.write(f"Format: {c['format']}  →  {c['path']}")

                # show inline
                img_bytes = requests.get(f"{BACKEND_URL}/file_proxy", params={"path": c["path"]}).content
                st.image(img_bytes, caption=c["format"])

            st.info(f"Audit Log: {data['audit_log_path']}")
        else:
            st.error(resp.text)

# -----------------------------------------------
# BACKEND HEALTH
# -----------------------------------------------
st.subheader("🩺 Backend Health Check")
if st.button("🔍 Check Health"):
    try:
        resp = requests.get(f"{BACKEND_URL}/health")
        st.json(resp.json())
    except Exception as e:
        st.error(e)
