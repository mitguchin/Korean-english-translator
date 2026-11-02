"""한국어 → 영어 번역기. 실행: python -m streamlit run app.py"""
import html
from urllib.parse import urlencode

import requests
import streamlit as st


class TranslationError(Exception):
    """Display a useful service error without leaking request text or URLs."""


def translate_to_english(text: str) -> str:
    # MyMemory accepts at most 500 UTF-8 bytes per request.
    if len(text.encode("utf-8")) > 500:
        raise TranslationError("문장이 너무 깁니다. 짧게 나누어 입력해 주세요.")
    try:
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": "ko|en", "mt": "1"},
            timeout=(5, 15),
        )
        if response.status_code == 429:
            raise TranslationError("번역 서비스의 접속 한도에 도달했습니다. 잠시 후 다시 시도해 주세요.")
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout as exc:
        raise TranslationError("번역 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.") from exc
    except requests.exceptions.RequestException as exc:
        raise TranslationError("번역 서버에 연결하지 못했습니다. 아래 버튼으로 Google 번역에서 열 수 있습니다.") from exc
    except ValueError as exc:
        raise TranslationError("번역 서버에서 올바른 응답을 받지 못했습니다.") from exc

    if not isinstance(data, dict):
        raise TranslationError("번역 서버의 응답 형식이 올바르지 않습니다.")
    if data.get("quotaFinished") is True:
        raise TranslationError("무료 번역 서비스의 하루 사용 한도를 소진했습니다. 아래 Google 번역 버튼을 이용해 주세요.")
    if str(data.get("responseStatus")) != "200":
        raise TranslationError("번역 서비스가 요청을 처리하지 못했습니다. 아래 Google 번역 버튼을 이용해 주세요.")
    result_data = data.get("responseData")
    result = result_data.get("translatedText") if isinstance(result_data, dict) else None
    if not isinstance(result, str) or not result.strip():
        raise TranslationError("번역 결과가 비어 있습니다. 문장을 바꾸어 다시 시도해 주세요.")
    return html.unescape(result).strip()


st.set_page_config(page_title="한국어 → 영어 번역", page_icon="🌐", layout="centered")
st.title("한국어 → 영어 번역")
st.write("한국어 문장을 입력하면 영어로 번역해 드립니다.")

with st.form("translate"):
    text = st.text_area(
        "번역할 한국어", height=180, max_chars=150,
        placeholder="예: 오늘 저녁은 뭘 먹을까?",
    )
    st.caption("한 번에 150자까지 · 입력 내용은 MyMemory 번역 서비스로 전송됩니다.")
    submitted = st.form_submit_button("영어로 번역", type="primary", use_container_width=True)

if submitted:
    st.session_state.pop("translation", None)
    st.session_state.pop("failed_text", None)
    source = text.strip()
    if not source:
        st.warning("번역할 한국어 문장을 입력해 주세요.")
    else:
        try:
            with st.spinner("영어로 번역하고 있어요…"):
                st.session_state.translation = translate_to_english(source)
        except TranslationError as exc:
            st.error(str(exc))
            st.session_state.failed_text = source

if "translation" in st.session_state:
    st.subheader("영어 번역 결과")
    st.code(st.session_state.translation, language=None, wrap_lines=True)
    st.caption("결과 오른쪽 위 복사 버튼을 누르면 복사할 수 있습니다.")

if "failed_text" in st.session_state:
    url = "https://translate.google.com/?" + urlencode(
        {"sl": "ko", "tl": "en", "text": st.session_state.failed_text, "op": "translate"}
    )
    st.link_button("Google 번역에서 직접 열기 ↗", url)

st.caption("인터넷 연결이 필요합니다. 무료 번역 서비스에는 일일 사용 한도가 있습니다.")
