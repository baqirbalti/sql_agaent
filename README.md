# Agentic SQL Analytics Bot (LangChain + Gemini)

## 📌 Overview
This project is an **advanced SQL Agent** powered by **Google Gemini** and **LangChain**, designed to analyze data from a **SQLite database (`mydb.db`)**.  
It converts natural language queries (e.g., *"Show me the top 5 products by revenue"*) into **safe SQL queries**, executes them, and returns structured results.  

---

## ✨ Features
- 🔒 **Secure SQL Execution** – Read-only queries only (no DELETE, DROP, UPDATE, etc.)
- 📊 **Business Analytics Ready** – Supports revenue, refunds, customer segmentation, and trend analysis
- 📈 **Auto-Limit & Validation** – Prevents large result dumps and ensures safe queries
- 🤖 **LLM-Powered Reasoning** – Uses **Gemini 1.5 Pro** via LangChain for query generation
- 🛡 **Schema-Aware** – Works only on specified tables (`customers`, `orders`, `order_items`, `products`, `refunds`, `payments`)

---

## 📂 Project Structure
```
agentic_demo_project/
│── main.py # Main script with SQL Agent
│── mydb.db # SQLite database
│── sql_agent_seed.sql # SQL script to seed database
│── requirements.txt # Python dependencies
│── .env # Environment variables (API keys)

```
---

## ⚙️ Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/your-username/agentic-sql-analytics.git
cd agentic-sql-analytics


Install dependencies
pip install -r requirements.txt

3️⃣ Setup database
sqlite3 mydb.db < sql_agent_seed.sql

4️⃣ Configure environment

Create a .env file:

GOOGLE_API_KEY=your_gemini_api_key
