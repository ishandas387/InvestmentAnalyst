import streamlit as st
import sys
import os
from langchain_core.messages import HumanMessage, AIMessage

# 1. FIX PATHS: Add project root to sys.path so 'agent' can be imported
# This assumes app_ui.py is in a 'ui/' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.streamlit.graph import app  # Import your compiled LangGraph app

# 2. PAGE CONFIG
st.set_page_config(page_title="AI Investment Analyst", page_icon="💹", layout="wide")
st.title("💹 Agentic Investment Analyst")

# 3. INITIALIZE SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user_1234"

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# 4. SIDEBAR CONTROLS
with st.sidebar:
    st.header("🛠️ Controls")
    debug_mode = st.toggle("Debug Mode", value=False)

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        # Optional: You could also wipe the SQLite thread here if desired
        st.rerun()

    if debug_mode:
        st.divider()
        st.subheader("🪲 Message State (Checkpointer)")
        snapshot = app.get_state(config)
        msgs = snapshot.values.get("messages", [])
        if msgs:
            debug_data = []
            for m in msgs:
                debug_data.append({
                    "Type": m.__class__.__name__,
                    "Content": (m.content[:100] + "...") if len(m.content) > 100 else m.content,
                    "ID": str(m.id)[:8] if hasattr(m, 'id') else "N/A"
                })
            st.table(debug_data)

# 5. DISPLAY CHAT HISTORY (Synced with LangGraph)
from langchain_core.messages import HumanMessage, AIMessage

# Fetch the current state from the SQLite database using the thread_id
config = {"configurable": {"thread_id": "user_1234"}}
current_state = app.get_state(config)
messages = current_state.values.get("messages", [])

for msg in messages:
    # Identify the role
    role = "user" if isinstance(msg, HumanMessage) else "assistant"

    with st.chat_message(role):
        st.markdown(msg.content)

        # If it's an AI message, we can check if it has the sql_query
        # (Note: In Part 2, sql_query is a separate key in the state,
        # so we'd pull the LATEST one or store it in message metadata)
        if role == "assistant" and hasattr(msg, "additional_kwargs"):
            if "sql" in msg.additional_kwargs:
                st.code(msg.additional_kwargs["sql"], language="sql")

# 6. HUMAN-IN-THE-LOOP (HITL) SECTION
# We check if the graph is currently interrupted BEFORE allowing new input
snapshot = app.get_state(config)

if snapshot.next:
    with st.container(border=True):
        st.warning("🤖 **Review Required:** The agent has prepared a query but needs approval to access the database.")

        # Extract the proposed SQL from the state
        proposed_sql = snapshot.values.get("sql_query", "No SQL query found in state.")
        st.code(proposed_sql, language="sql")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Approve & Execute", use_container_width=True, type="primary"):
                with st.spinner("Executing query and finalizing analysis..."):
                    # Passing 'None' tells LangGraph to resume from the breakpoint
                    for event in app.stream(None, config=config):
                        for node_name, output in event.items():
                            if node_name == "analysis" and "analysis" in output:
                                final_text = output["analysis"]
                                st.session_state.messages.append({"role": "assistant", "content": final_text})
                st.rerun()

        with col2:
            feedback = st.text_input("Feedback / Fix instructions:", placeholder="e.g., 'Filter for 2024 only'")
            if st.button("❌ Reject & Edit", use_container_width=True):
                # Update state with the human feedback
                feedback_msg = f"User rejected the query. Feedback: {feedback if feedback else 'Please try a different approach.'}"
                app.update_state(config, {"messages": [HumanMessage(content=feedback_msg)]})

                # Resume so the agent can react to the feedback and generate a new query
                for event in app.stream(None, config=config):
                    pass
                st.rerun()

# 7. USER INPUT LOOP
# We only show the input box if the agent isn't waiting for a review
else:
    if prompt := st.chat_input("Ask about your portfolio or market data..."):
        # Add user message to UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process with Assistant
        with st.chat_message("assistant"):
            status_container = st.status("Analyst is working...", expanded=True)
            current_sql = ""

            # Start streaming the graph
            input_state = {"messages": [HumanMessage(content=prompt)]}

            for event in app.stream(input_state, config=config):
                # If we hit an interrupt, the loop ends here
                for node_name, output in event.items():
                    status_container.write(f"✔️ Finished: {node_name}")

                    # ADD THIS SAFETY CHECK:
                    if output is not None and isinstance(output, dict):
                        if "sql_query" in output:
                            current_sql = output["sql_query"]
                            status_container.code(current_sql, language="sql")

                        if "analysis" in output:
                            analysis_text = output["analysis"]
                            st.markdown(analysis_text)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": analysis_text,
                                "sql": current_sql
                            })

            status_container.update(label="Step Complete", state="complete", expanded=False)

            # If the graph stopped because of an interrupt, refresh to show the buttons
            if app.get_state(config).next:
                st.rerun()