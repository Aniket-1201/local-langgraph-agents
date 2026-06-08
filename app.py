import streamlit as st
import time

# 1. Page Configuration
st.set_page_config(page_title="Corporate Brain AI", page_icon="🧠", layout="centered")

# --- NEW: Phase 3 Monetization Wall (Sidebar) ---
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
st.markdown("Ask questions about company policies (PDFs) or database metrics (SQL).")

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
            
            # Mocking the 15-second Hugging Face delay Aniket mentioned
            time.sleep(2) 
            
            # TODO: We will replace this with Aniket's Hugging Face API call!
            mock_response = f"**UI Ready!** I received: '{prompt}'. Waiting to connect to Aniket's Hugging Face backend!"
            
            st.markdown(mock_response)
            
    # Save AI response
    st.session_state.messages.append({"role": "assistant", "content": mock_response})