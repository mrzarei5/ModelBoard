import streamlit as st
from agent.agent_executor import agent_executor


st.title("🤖 AI Model Finder & Comparison Assistant")
st.write("""
Ask anything about AI models from Hugging Face!  
**Examples:**  
- "Find a small English model for text summarization."  
- "Show text generation models with more than 1000 likes."  
- "Compare Mixtral-8x7B-Instruct-v0.1 and Qwen1.5-32B-Chat."  
- "Show me details for llama-2-7b-chat."  
""")

if "history" not in st.session_state:
    st.session_state.history = []
if "already_asked" not in st.session_state:
    st.session_state.already_asked = False

def clear_asked():
    st.session_state.already_asked = False

def clear_input():
    st.session_state.user_input = ""

user_input = st.text_input("Your question:", key="user_input", on_change=clear_asked)

if st.button("Ask") or (user_input and not st.session_state.get("already_asked")):
    st.session_state["already_asked"] = True
    if user_input:
        with st.spinner("Thinking..."):
            try:
                response = agent_executor.invoke({"input": user_input})
                output = response["output"] if isinstance(response, dict) and "output" in response else str(response)
            except Exception as e:
                output = f"⚠️ Agent error: {e}"
            st.session_state.history.append(("You", user_input))
            st.session_state.history.append(("Agent", output))
            st.text_area("Agent response:", value=output, height=300)


    st.session_state["already_asked"] = False

if st.session_state.history:
    st.write("---")
    st.write("### Conversation history")
    for role, message in st.session_state.history[-10:]:
        st.markdown(f"**{role}:** {message}")

st.caption("Built with Streamlit • LangChain • OpenAI • Hugging Face • Local leaderboard model database.")