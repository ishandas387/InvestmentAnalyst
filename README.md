# 💹 AI Investment Analyst

An intelligent, stateful agent built with **LangGraph** and **SQLite** that transforms natural language into financial insights. This project features a **Human-in-the-Loop (HITL)** safety layer, allowing you to review and edit SQL queries before they touch your production data.

## 🌟 Key Features
* **Agentic SQL Generation:** Uses `gpt-oss-20b` (via OpenRouter) to translate complex financial questions into SQLite queries.
* **Human-in-the-Loop (HITL):** A dedicated node pauses execution so you can **Approve**, **Reject**, or **Edit** the proposed SQL.
* **Persistent SQLite Backend:** Stores 100+ instruments and transaction history. Includes an idempotent manager that health-checks the DB on startup.
* **Workflow Visualization:** Automatically generates a `graph_flow.png` visualizing the AI's decision-making logic.

## 🏗️ Architecture Flow

![graph_flow.png](graph_flow.png)

The agent follows a cyclic graph pattern:
1.  **Generate:** LLM creates SQL based on the database schema.
2.  **Guardrail:** Validates that the SQL is a `SELECT` statement.
3.  **Review:** **(Human Pause)** User views the SQL and decides its fate.
4.  **Execute:** If approved, the query runs against SQLite.
5.  **Analyze:** Raw data is summarized into a human-readable financial insight.

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10+
* [OpenRouter API Key](https://openrouter.ai/keys) (Enable "Free model publication" in [Privacy Settings](https://openrouter.ai/settings/privacy)).

### 2. Installation
```bash

# Install dependencies
pip install langgraph langchain-openai python-dotenv rich pygraphviz