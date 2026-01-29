# 💹 AI Investment Analyst

An intelligent, stateful agent built with **LangGraph** and **SQLite** that transforms natural language into financial insights. This project features a dual-interface system (Terminal & Web UI) and a **Human-in-the-Loop (HITL)** safety layer for secure database interaction.



## 🌟 Key Features
* **Dual Interface:** Run the agent via a high-performance **Terminal CLI** (powered by Rich) or a professional **Streamlit Web UI**.
* **Human-in-the-Loop (HITL):** A dedicated breakpoint pauses execution before database queries run, allowing you to **Approve**, **Reject**, or **Edit** proposed SQL.
* **Stateful Memory:** Uses `SqliteSaver` to persist conversation threads. The agent remembers your portfolio context even after the application restarts.
* **Context Summarization:** Automatically condenses long conversation histories into system summaries to stay within LLM token limits while retaining core facts.
* **Dynamic Visualization:** Generates financial charts and plots based on query results using a sandboxed execution pattern.
* **Debug Dashboard:** A built-in "Message Inspector" allows you to view the raw state, message IDs, and hidden system prompts in real-time.

## 🏗️ Architecture Flow

### Nodes
![Screenshot 2026-01-29 at 10.05.49 PM.png](screenshots%2FScreenshot%202026-01-29%20at%2010.05.49%E2%80%AFPM.png)

The agent follows a cyclic graph pattern:
1.  **Summarize:** Condenses previous messages to maintain a "clean" context window.
2.  **Generate SQL:** Translates natural language into schema-aware SQLite queries.
3.  **Human Review (Breakpoint):** The graph pauses. The user must approve the SQL via the UI or Terminal.
4.  **Execute & Visualize:** Approved queries run against the DB, and data is passed to a visualization node.
5.  **Analyze:** Synthesizes raw data and charts into a human-readable financial report.

## 🚀 Getting Started

### 1. Prerequisites
* **Python 3.10+** (Use `python3` command on macOS/Linux)
* [OpenRouter API Key](https://openrouter.ai/keys) (Set in your `.env` file)

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/your-username/InvestmentAnalyst.git](https://github.com/your-username/InvestmentAnalyst.git)
cd InvestmentAnalyst

# Install dependencies
pip install langgraph langchain-openai python-dotenv rich streamlit pandas pillow
````

### 3. Running the Application
The project includes a unified launcher (main.py) to handle database health checks and environment setup.

To launch the Streamlit UI:

```Bash
python3 main.py --ui
````
To launch the Terminal CLI:

```Bash
python3 main.py
```
## 📂 Project Structure

1. **agent/** : Contains the LangGraph definition, nodes, and state logic.
2. **db/**: Database managers and initialization scripts.
3. **ui/**: Both terminal.py and the app_ui.py (Streamlit) interfaces.
4. **main.py**: The entry point for the application.

## 📈 Roadmap
1. [ ] Schema RAG: Implementing vector search to handle databases with hundreds of tables.
2. [ ] Narrative RAG: Integrating unstructured data (PDFs/Earnings Reports) with SQL results.

🛡️ Security
Read-Only Enforcement: The agent is restricted to SELECT statements to prevent accidental data deletion.

Sandboxed Viz: Python code generated for charts is executed in an isolated environment

### CLI

![Screenshot 2026-01-19 at 10.02.44 PM.png](screenshots%2FScreenshot%202026-01-19%20at%2010.02.44%E2%80%AFPM.png)
![Screenshot 2026-01-19 at 10.04.09 PM.png](screenshots%2FScreenshot%202026-01-19%20at%2010.04.09%E2%80%AFPM.png)
![Screenshot 2026-01-19 at 10.04.25 PM.png](screenshots%2FScreenshot%202026-01-19%20at%2010.04.25%E2%80%AFPM.png)
![Screenshot 2026-01-19 at 10.05.49 PM.png](screenshots%2FScreenshot%202026-01-19%20at%2010.05.49%E2%80%AFPM.png)
![Screenshot 2026-01-19 at 10.06.09 PM.png](screenshots%2FScreenshot%202026-01-19%20at%2010.06.09%E2%80%AFPM.png)
![Screenshot 2026-01-19 at 10.06.42 PM.png](screenshots%2FScreenshot%202026-01-19%20at%2010.06.42%E2%80%AFPM.png)
![Screenshot 2026-01-22 at 9.31.23 PM.png](screenshots%2FScreenshot%202026-01-22%20at%209.31.23%E2%80%AFPM.png)
![Screenshot 2026-01-22 at 9.35.33 PM.png](screenshots%2FScreenshot%202026-01-22%20at%209.35.33%E2%80%AFPM.png)

### UI
![Screenshot 2026-01-29 at 10.08.12 PM.png](screenshots%2FScreenshot%202026-01-29%20at%2010.08.12%E2%80%AFPM.png)
![Screenshot 2026-01-29 at 10.08.31 PM.png](screenshots%2FScreenshot%202026-01-29%20at%2010.08.31%E2%80%AFPM.png)
![Screenshot 2026-01-29 at 10.09.00 PM.png](screenshots%2FScreenshot%202026-01-29%20at%2010.09.00%E2%80%AFPM.png)