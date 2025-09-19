"""
Advanced Analytics SQL Agent with Gemini + SQLite (mydb.db)

This script demonstrates an advanced implementation of a secure SQL agent designed for
complex business analytics and reporting, powered by Google Gemini.

Key Features:
🔒 Same security guardrails (read-only, validation, etc.)
📊 Advanced analytics queries (revenue analysis, customer segmentation, etc.)
📈 Business intelligence capabilities (trends, rankings, aggregations)
🔄 Multi-turn conversation support
📋 Comprehensive business logic documentation in system prompt
"""

# Load environment variables (must include GOOGLE_API_KEY for Gemini)
from dotenv import load_dotenv; load_dotenv()

# Core LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini integration
from langchain.agents import initialize_agent, AgentType
from langchain.schema import SystemMessage
from langchain_community.utilities import SQLDatabase

# Validation + tools
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type
import sqlalchemy
import re

# --- Database Configuration ---
DB_URL = "sqlite:///mydb.db"  # your new DB

engine = sqlalchemy.create_engine(DB_URL)

class QueryInput(BaseModel):
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

class SafeSQLTool(BaseTool):
    name: str = "execute_sql"
    description: str = "Execute one read-only SELECT."
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, sql: str) -> str | dict:
        s = sql.strip().rstrip(";")

        # Security validation
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE)\b", s, re.I):
            return "ERROR: write operations are not allowed."
        if ";" in s:
            return "ERROR: multiple statements are not allowed."
        if not re.match(r"(?is)^\s*select\b", s):
            return "ERROR: only SELECT statements are allowed."

        # Auto-limit for safety
        if not re.search(r"\blimit\s+\d+\b", s, re.I) and not re.search(r"\bcount\(|\bgroup\s+by\b|\bsum\(|\bavg\(|\bmax\(|\bmin\(", s, re.I):
            s += " LIMIT 200"

        try:
            with engine.connect() as conn:
                result = conn.exec_driver_sql(s)
                rows = result.fetchall()
                cols = list(result.keys()) if result.keys() else []
                return {"columns": cols, "rows": [list(r) for r in rows]}
        except Exception as e:
            return f"ERROR: {e}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError


# --- Schema Setup ---
db = SQLDatabase.from_uri(
    DB_URL,
    include_tables=["customers", "orders", "order_items", "products", "refunds", "payments"]
)

schema_context = db.get_table_info()

system = f"""You are a careful analytics engineer for SQLite.
Use only listed tables. Revenue = sum(quantity*unit_price_cents) - refunds.amount_cents.
\n\nSchema:\n{schema_context}"""

# --- Gemini Model ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# --- Tool & Agent ---
tool = SafeSQLTool()
agent = initialize_agent(
    tools=[tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,  # still works with Gemini in LangChain
    verbose=True,
    agent_kwargs={"system_message": SystemMessage(content=system)}
)

# --- Example Analytics Queries ---

print(agent.invoke({"input": "Top 5 products by gross revenue (before refunds). Include product name and total_cents."})["output"])

print(agent.invoke({"input": "Weekly net revenue for the last 6 weeks. Return week_start, net_cents."})["output"])

print(agent.invoke({"input": "For each customer, show their first_order_month, total_orders, last_order_date. Return 10 rows."})["output"])

print(agent.invoke({"input": "Rank customers by lifetime net revenue (sum of items minus refunds). Show rank, customer, net_cents. Top 10."})["output"])

print(agent.invoke({"input": "What categories drive the most revenue?"})["output"])

print(agent.invoke({"input": "Break the top category down by product with totals."})["output"])
