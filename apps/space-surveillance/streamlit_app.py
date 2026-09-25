import base64
import hashlib
import os
import runpy
import shutil
import sys
import tempfile
import zipfile
from io import BytesIO
from urllib.parse import quote
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

# Public beta contact / Q&A
st.divider()
st.subheader("✉️ 문의 / Q&A")
st.caption("실습 오류, 연구 내용, 교육 활용과 관련한 질문을 남겨 주세요. 문의 메일: whgns8364@gmail.com")

with st.form("space_beta_qa"):
    qa_name = st.text_input("이름 / 소속", placeholder="예: 홍길동 / ○○고등학교")
    qa_email = st.text_input("회신 받을 이메일", placeholder="example@email.com")
    qa_message = st.text_area(
        "질문 내용",
        placeholder="궁금한 점이나 실행 중 발생한 문제를 적어 주세요.",
        height=140
    )
    qa_submit = st.form_submit_button("질문 작성 완료")

if qa_submit:
    if not qa_email.strip() or not qa_message.strip():
        st.warning("회신 받을 이메일과 질문 내용을 입력해 주세요.")
    else:
        subject = "[SGP4+AI Beta Q&A] 우주감시 웹 실습 문의"
        body = "\n".join([
            "SGP4 + AI 우주감시 Beta 문의",
            "",
            f"이름 / 소속: {qa_name.strip() or '미기재'}",
            f"회신 이메일: {qa_email.strip()}",
            "",
            "질문 내용",
            "------------------------------",
            qa_message.strip(),
        ])
        mailto = "mailto:whgns8364@gmail.com?subject=" + quote(subject) + "&body=" + quote(body)
        st.success("질문 내용이 준비되었습니다. 아래 버튼을 눌러 이메일로 보내 주세요.")
        st.link_button("✉️ 작성한 질문 이메일로 보내기", mailto)

st.markdown(
    '홈페이지의 <a href="https://GodTANKS.github.io/astronomy-data-science/#contact" target="_blank">문의·Q&A 페이지</a>에서도 질문을 작성할 수 있습니다.',
    unsafe_allow_html=True,
)