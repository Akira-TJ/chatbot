import streamlit as st
from google import genai

# タイトルと説明
st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot powered by Google's Gemini API."
)

# Gemini APIキーの入力
gemini_api_key = st.text_input(
    "Gemini API Key",
    type="password"
)

if not gemini_api_key:
    st.info(
        "Gemini APIキーを入力してください。",
        icon="🗝️"
    )

else:
    # Geminiクライアントを作成
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

        # Gemini APIに渡す会話履歴
        contents = [
            {
                "role": (
                    "user"
                    if m["role"] == "user"
                    else "model"
                ),
                "parts": [{"text": m["content"]}],
            }
            for m in st.session_state.messages
        ]

        # Geminiから回答をストリーミング取得
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

            # AIの回答を保存
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
