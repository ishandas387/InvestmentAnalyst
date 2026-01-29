import streamlit as st
import sys
import os
import uuid
from langchain_core.messages import HumanMessage, AIMessage

# 1. SETUP PATHS
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.streamlit.graph import app

# 2. SESSION STATE INITIALIZATION
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages_ui" not in st.session_state:
    st.session_state.messages_ui = []

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# 3. PAGE CONFIG
st.set_page_config(page_title="Investment Analyst", page_icon="💹", layout="wide")
st.title("💹 Agentic Investment Analyst")

# 4. SIDEBAR (The Reset Button lives here)
with st.sidebar:
    st.header("🛠️ Controls")

    if st.button("🆕 Start New Conversation", use_container_width=True, type="primary"):
        # Reset everything: IDs and UI history
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages_ui = []
        st.rerun()

    if st.button("🗑️ Clear Chat Display"):
        st.session_state.messages_ui = []
        st.rerun()

# 5. DISPLAY UI CHAT HISTORY
for msg in st.session_state.messages_ui:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            st.code(msg["sql"], language="sql")

# 6. DYNAMIC LOGIC GATE: Review Mode vs. Input Mode
snapshot = app.get_state(config)

# CASE A: The agent is interrupted and waiting for your review
if snapshot.next:
    with st.container(border=True):
        st.warning("🤖 **Review Required:** The agent has prepared a query.")
        proposed_sql = snapshot.values.get("sql_query", "No SQL found.")
        st.code(proposed_sql, language="sql")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve & Execute", use_container_width=True, type="primary"):
                with st.status("🚀 Running Query...", expanded=True) as status:
                    for event in app.stream(None, config=config):
                        for node_name, output in event.items():
                            status.write(f"✔️ Finished: {node_name}")
                            if node_name == "analysis" and "analysis" in output:
                                analysis_text = output["analysis"]
                                st.session_state.messages_ui.append({"role": "assistant", "content": analysis_text})
                st.rerun()

        with col2:
            feedback = st.text_input("Feedback / Fix instructions:", key="fb_input")
            if st.button("❌ Reject & Edit", use_container_width=True):
                # Update state with feedback and resume to let the agent rewrite
                fb_msg = f"Rejected. Feedback: {feedback if feedback else 'Rewrite this query.'}"
                app.update_state(config, {"messages": [HumanMessage(content=fb_msg)]})
                # Resume execution to move past the breakpoint
                for event in app.stream(None, config=config):
                    pass
                st.rerun()

# CASE B: No active interrupt - Show the normal chat input
else:
    if prompt := st.chat_input("Ask about your portfolio..."):
        # Add to UI immediately
        st.session_state.messages_ui.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Start streaming the Agent
        with st.chat_message("assistant"):
            with st.status("Analyst working...", expanded=True) as status:
                input_state = {"messages": [HumanMessage(content=prompt)]}
                current_sql = ""

                for event in app.stream(input_state, config=config):
                    for node_name, output in event.items():
                        status.write(f"✔️ {node_name} finished")
                        if output and isinstance(output, dict):
                            if "sql_query" in output:
                                current_sql = output["sql_query"]
                                status.code(current_sql, language="sql")
                            if "analysis" in output:
                                analysis_text = output["analysis"]
                                st.markdown(analysis_text)
                                st.session_state.messages_ui.append({
                                    "role": "assistant",
                                    "content": analysis_text,
                                    "sql": current_sql
                                })

            # Check if we hit an interrupt during the stream
            if app.get_state(config).next:
                st.rerun()