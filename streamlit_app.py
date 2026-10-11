import streamlit as st
from google import genai

# タイトルと説明
st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot powered by Google's Gemini API."
)

# st.secrets から Gemini API キーを取得
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "Gemini APIキーが設定されていません。"
        "secrets.toml を確認してください。"
    )
    st.stop()

# Gemini クライアントを作成
client = genai.Client(api_key=gemini_api_key)

# チャット履歴を初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去のチャットを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザーの入力
if prompt := st.chat_input("メッセージを入力してください"):

    # ユーザーのメッセージを保存・表示
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini API に渡す会話履歴
    contents = [
        {
            "role": (
                "user" if m["role"] == "user" else "model"
            ),
            "parts": [{"text": m["content"]}],
        }
        for m in st.session_state.messages
    ]

    # Gemini から回答をストリーミング取得
    try:
        stream = client.models.generate_content_stream(
            model="gemini-3.8-flash",
            contents=contents,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(
                chunk.text
                for chunk in stream
                if chunk.text
            )

        # AI の回答を保存
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

    except Exception:
        st.error(
            "Gemini APIの呼び出し中にエラーが発生しました。"
            "APIキー、モデル名、通信状況を確認してください。"
        )
