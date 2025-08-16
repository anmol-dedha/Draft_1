import streamlit as st
import requests, json, os

# Load API key
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY and os.path.exists("key.dev"):
    with open("key.dev", "r") as f:
        OPENROUTER_API_KEY = f.read().strip()

if not OPENROUTER_API_KEY:
    st.error("❌ OPENROUTER_API_KEY not found. Set it in env or create key.dev file.")
    st.stop()

MODEL = "deepseek/deepseek-r1-0528:free"

st.set_page_config(page_title="AnnaData_draft 1", page_icon="🌱")
st.title("🧑‍🌾 AnnaData- किसानों की सेवा में ")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
if prompt := st.chat_input("Type your question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call OpenRouter API
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        with requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": st.session_state.messages,
                "stream": True,
            },
            stream=True,
        ) as r:
            for line in r.iter_lines():
                if line and line.startswith(b"data: "):
                    data_str = line[len(b"data: "):].decode("utf-8")
                    if data_str.strip() == "[DONE]":
                        break
                    data_json = json.loads(data_str)
                    delta = data_json["choices"][0]["delta"].get("content", "")
                    full_response += delta
                    placeholder.markdown(full_response)

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": full_response})
