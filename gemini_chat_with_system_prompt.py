import streamlit as st
from google import genai
from google.genai import types

# Page config
st.set_page_config(page_title="Gemini Chatbot with System Prompt", page_icon="💬")

# Header
st.title("💬 Gemini Chatbot")
st.caption("Customize the chatbot's behavior using the system prompt in the sidebar")

# Initialize Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Sidebar for system prompt
st.sidebar.title("⚙️ Custom Instructions")
st.sidebar.write("Modify the system prompt below to change how the chatbot responds.")

system_prompt = st.sidebar.text_area(
    "System Prompt",
    value="You are a helpful assistant.",
    height=150,
    help="The system prompt sets the behavior and personality of the AI assistant."
)

st.sidebar.info("💡 **Tip:** Try prompts like:\n- 'You are a friendly pirate'\n- 'Respond only in haikus'\n- 'You are a coding tutor'")

# Reset chat when system prompt changes
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = system_prompt
    st.session_state.history = []

if st.session_state.system_prompt != system_prompt:
    st.session_state.system_prompt = system_prompt
    st.session_state.history = []
    st.rerun()

# Display chat history
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Create chat with system prompt
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction=system_prompt)
    )
    
    # Replay previous messages
    for msg in st.session_state.history[:-1]:
        if msg["role"] == "user":
            chat.send_message(msg["content"])

    # Get response from Gemini
    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        reply = response.text
        st.markdown(reply)

    # Add assistant message to history
    st.session_state.history.append({"role": "assistant", "content": reply})

st.sidebar.markdown("---")
st.sidebar.markdown("❤️ Made by [Build Fast with AI](https://buildfastwithai.com)")
