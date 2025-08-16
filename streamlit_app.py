import streamlit as st
import requests, json

# ✅ Load API key directly from Streamlit secrets
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

MODEL = "deepseek/deepseek-r1-0528:free"

st.set_page_config(page_title="AnnaData Draft 1", page_icon="🌱")
st.title("🧑‍🌾 AnnaData - किसानों की सेवा में")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("अपना सवाल लिखें..."):
    # Save user message
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
                    try:
                        data_json = json.loads(data_str)
                        delta = data_json["choices"][0]["delta"].get("content", "")
                        full_response += delta
                        placeholder.markdown(full_response)
                    except Exception as e:
                        placeholder.markdown(f"⚠️ Error parsing: {e}")

        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": full_response})
