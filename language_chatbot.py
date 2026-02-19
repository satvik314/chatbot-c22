import streamlit as st
from google import genai
from google.genai import types

# Page config
st.set_page_config(page_title="Gemini Chatbot with System Prompt", page_icon="💬")

# Header
st.title("💬 Satvik's Chatbot")
st.caption("I built this chatbot as a part of Gen AI LaunchPad")

# Initialize Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ----------------------------
# Persona presets
# ----------------------------
PERSONAS = {
    "Default (Helpful Assistant)": "You are a helpful assistant.",

    "Tamil Tutor (தமிழ்)": (
        "You are a friendly Tamil language tutor. "
        "Respond primarily in Tamil, but you may include short English explanations when helpful. "
        "Correct mistakes gently, provide 2-3 alternatives, and include pronunciation in Latin script when useful. "
        "Keep responses concise and practical for daily conversation."
    ),

    "Marathi Tutor (मराठी)": (
        "You are a friendly Marathi language tutor. "
        "Respond primarily in Marathi, with brief English explanations if needed. "
        "Correct mistakes gently, provide 2-3 alternative phrases, and include pronunciation in Latin script when useful. "
        "Focus on everyday conversation and polite forms."
    ),

    "Telugu Tutor (తెలుగు)": (
        "You are a friendly Telugu language tutor. "
        "Respond primarily in Telugu, with brief English explanations if needed. "
        "Correct mistakes gently, provide 2-3 alternative phrases, and include pronunciation in Latin script when useful. "
        "Prefer short, everyday-life sentences and include both questions and answers when relevant."
    ),

    "Hindi Tutor (हिंदी)": (
        "You are a friendly Hindi language tutor. "
        "Respond primarily in Hindi, with brief English explanations if needed. "
        "Correct mistakes gently, provide 2-3 alternative phrases, and include pronunciation in Latin script when useful. "
        "Focus on polite, everyday conversation."
    ),
}

# ----------------------------
# Sidebar - Custom Instructions
# ----------------------------
st.sidebar.title("⚙️ Custom Instructions")
st.sidebar.write("Choose a persona preset or edit the system prompt to change how the chatbot responds.")

selected_persona = st.sidebar.selectbox(
    "Persona Preset",
    options=list(PERSONAS.keys()),
    index=0,
    help="Pick a preset system prompt (persona) for the assistant."
)

# Init session state
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = selected_persona

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = PERSONAS[selected_persona]

if "history" not in st.session_state:
    st.session_state.history = []

# If persona changes, load its prompt + reset chat
if st.session_state.selected_persona != selected_persona:
    st.session_state.selected_persona = selected_persona
    st.session_state.system_prompt = PERSONAS[selected_persona]
    st.session_state.history = []
    st.rerun()

# Editable system prompt box
system_prompt = st.sidebar.text_area(
    "System Prompt (Editable)",
    value=st.session_state.system_prompt,
    height=180,
    help="You can tweak the preset prompt here. Changing it will reset the chat."
)

# Reset chat when system prompt changes (manual edits)
if st.session_state.system_prompt != system_prompt:
    st.session_state.system_prompt = system_prompt
    st.session_state.history = []
    st.rerun()

st.sidebar.info(
    "💡 **Tip:** Try prompts like:\n"
    "- 'You are a friendly pirate'\n"
    "- 'Respond only in haikus'\n"
    "- 'You are a coding tutor'"
)

# Optional: a reset button
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.history = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("❤️ Made by [Satvik](https://www.linkedin.com/in/satvik-paramkusham/)")

# ----------------------------
# Display chat history
# ----------------------------
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------
# Chat input + model call
# ----------------------------
if prompt := st.chat_input("Type your message here..."):
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Create chat with system prompt
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=st.session_state.system_prompt
        ),
    )

    # Replay previous messages (user + assistant) to preserve context
    for msg in st.session_state.history[:-1]:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            chat.send_message(content)
        elif role == "assistant":
            # Provide assistant turns back to the model as context
            chat.send_message(f"(assistant previously said) {content}")

    # Get response from Gemini
    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        reply = response.text
        st.markdown(reply)

    # Add assistant message to history
    st.session_state.history.append({"role": "assistant", "content": reply})
