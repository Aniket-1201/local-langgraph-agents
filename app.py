import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="Corporate Brain AI", page_icon="🧠", layout="centered")

# --- Phase 3 Monetization Wall (Sidebar) ---
with st.sidebar:
    st.header("☕ Support the Project")
    st.markdown(
        "Running custom AI models is expensive! Right now, this system runs on a free CPU tier. "
        "If you like this tool, consider donating $5 to help us upgrade to a lightning-fast GPU server."
    )
    st.button("Donate $5 for GPU servers 🚀")
    st.divider()
    st.markdown("**Core Engineers:**")
    st.markdown("- **Atharva:** Frontend UI & RAG Data Pipelines")
    st.markdown("- **Aniket:** Backend API & QLoRA Fine-tuning")
# ------------------------------------------------

# 2. Main Header
st.title("🧠 Corporate Brain AI")
st.markdown("Ask questions about GENAI (PDFs) or database metrics (SQL).")

# 3. Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. User Input
if prompt := st.chat_input("Ask a question (e.g., 'What are the 3 tool types?' or 'How many employees in Eng_Sys_Ops?'):"):
    
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI thinking animation
    with st.chat_message("assistant"):
        with st.spinner("AI is routing your question..."):
            
            # Live Production API URL pointing to Aniket's backend Space
            API_URL = "https://AniketDeshpande1201-Space-deployment.hf.space/api/chat"
            payload = {"question": prompt}
            
            try:
                # Call the dual-agent routing backend
                api_request = requests.post(API_URL, json=payload, timeout=500)
                api_request.raise_for_status()
                final_response = api_request.json()["response"]
            except requests.exceptions.Timeout:
                final_response = "⚠️ The request timed out. The backend is taking longer than usual to route this query."
            except Exception as e:
                final_response = f"⚠️ Failed to connect to Corporate Brain Backend: {e}"
            
            st.markdown(final_response)
            
    # Save AI response
    st.session_state.messages.append({"role": "assistant", "content": final_response})