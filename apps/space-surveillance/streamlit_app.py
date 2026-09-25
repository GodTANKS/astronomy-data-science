import base64
import hashlib
import os
import runpy
import shutil
import sys
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import streamlit as st
from cryptography.fernet import Fernet, InvalidToken

APP_ROOT = Path(__file__).resolve().parent
PAYLOAD_DIR = APP_ROOT / "payload"
EXPECTED_SHA256 = "54e806a5ccce86375d021fe63837221a6aa28927085470854842b5fb47597e6e"

def _load_key():
    try:
        key = st.secrets["SPACE_BETA_KEY"]
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        return str(key).strip()
    except Exception:
        st.set_page_config(page_title="SGP4 + AI 우주감시 Beta", page_icon="🛰️", layout="wide")
        st.error("Beta 실행 키가 아직 설정되지 않았습니다.")
        st.info("배포 관리자에게 문의해 주세요.")
        st.stop()

def _prepare_runtime():
    parts = sorted(PAYLOAD_DIR.glob("part-*.txt"))
    if not parts:
        raise RuntimeError("Encrypted beta payload was not found.")

    encrypted = base64.b64decode("".join(p.read_text(encoding="ascii").strip() for p in parts))
    actual_sha = hashlib.sha256(encrypted).hexdigest()
    if actual_sha != EXPECTED_SHA256:
        raise RuntimeError("Beta payload integrity check failed.")

    key = _load_key()
    try:
        zipped = Fernet(key.encode("utf-8")).decrypt(encrypted)
    except InvalidToken:
        st.set_page_config(page_title="SGP4 + AI 우주감시 Beta", page_icon="🛰️", layout="wide")
        st.error("Beta 실행 키가 올바르지 않습니다.")
        st.stop()

    runtime = Path(tempfile.gettempdir()) / "sgp4_ai_space_beta_v01"
    marker = runtime / ".ready"
    if not marker.exists():
        if runtime.exists():
            shutil.rmtree(runtime)
        runtime.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(BytesIO(zipped)) as zf:
            zf.extractall(runtime)
        marker.write_text(EXPECTED_SHA256, encoding="utf-8")

    return runtime

runtime = _prepare_runtime()
if str(runtime) not in sys.path:
    sys.path.insert(0, str(runtime))
os.chdir(runtime)
runpy.run_path(str(runtime / "main.py"), run_name="__main__")