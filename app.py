"""Run with: python -m streamlit run app.py."""
import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="한국어 → 영어 번역", page_icon="🌐", layout="centered")
st.title("한국어 → 영어 번역")
st.write("한국어 문장을 입력하면 영어로 번역해 드립니다.")

with st.form("translate"):
    text = st.text_area(
        "번역할 한국어", height=180, max_chars=4500,
        placeholder="예: 오늘 날씨가 좋아서 산책하고 싶어요.",
    )
    st.caption("인터넷 연결이 필요하며, 번역할 내용은 Google 번역으로 전송됩니다.")
    submitted = st.form_submit_button("영어로 번역", type="primary", use_container_width=True)

if submitted:
    st.session_state.pop("translation", None)
    source = text.strip()
    if not source:
        st.warning("번역할 한국어 문장을 입력해 주세요.")
    else:
        try:
            with st.spinner("영어로 번역하고 있어요…"):
                result = GoogleTranslator(source="ko", target="en").translate(source)
            if not isinstance(result, str) or not result.strip():
                st.error("번역 결과를 받지 못했습니다. 잠시 후 다시 시도해 주세요.")
            else:
                st.session_state.translation = result
        except Exception:
            st.error("번역 서비스에 연결하지 못했습니다. 인터넷 연결을 확인하거나 잠시 후 다시 시도해 주세요.")

if "translation" in st.session_state:
    st.subheader("영어 번역 결과")
    st.code(st.session_state.translation, language=None, wrap_lines=True)
    st.caption("결과 오른쪽 위 복사 버튼을 누르면 복사할 수 있습니다.")
