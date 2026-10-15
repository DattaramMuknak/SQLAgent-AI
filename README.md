# SQLAgent AI

### Autonomous Text-to-SQL Analytics Agent

**SQLAgent AI** is an end-to-end AI analytics application that allows users to interact with a relational database using natural language.

Instead of manually writing SQL queries, users can ask questions such as:

> How many customers are there?

> Show me the top 10 customers by total spending.

> Show me the total revenue by country.

The system translates natural-language questions into SQL, validates and safely executes the generated queries against a read-only SQLite database, recovers from SQL execution errors through a controlled correction workflow, summarizes the results, and generates visualizations when useful.

SQLAgent AI supports **multiple LLM providers — Google Gemini and Groq — through configuration**, allowing the underlying provider to be changed without changing the application workflow.

---

## Live Demo

### Try SQLAgent AI

**https://sqlagent-ai.streamlit.app/**

> Ask your database. Let the agent handle the SQL.

### Source Code

**https://github.com/AbdelrhmanAkl/SQLAgent-AI**

---

## What This Project Demonstrates

SQLAgent AI combines LLMs, agentic workflow orchestration, relational databases, SQL validation, error recovery, and data visualization into a single application.

### Core capabilities

- Natural Language → SQL
- LLM-powered SQL generation
- Multi-provider LLM architecture
- LangGraph workflow orchestration
- Schema-aware SQL generation
- SQL validation
- Read-only database execution
- Error-driven SQL self-correction
- Controlled retry logic
- AI-powered result summarization
- Automatic visualization
- Streamlit deployment
- Secure API key management
- Automated testing

The objective is not simply to generate SQL.

It is to build a **controlled analytics workflow around an LLM**, where SQL generation, validation, execution, error recovery, summarization, and visualization are explicitly separated.

---

# Key Features

## 1. Natural Language Database Queries

Users can query the relational database without manually writing SQL.

For example:

```text
Show me the top 10 customers by total spending
```

The agent uses the available database schema to determine the required tables, relationships, aggregations, ordering, and limits.

---

## 2. Multi-Provider LLM Support

SQLAgent AI supports multiple LLM providers through the `LLM_PROVIDER` configuration.

| Provider | Configuration |
|---|---|
| Google Gemini | `LLM_PROVIDER=gemini` |
| Groq | `LLM_PROVIDER=groq` |

The provider can be changed without modifying the main application workflow.

For example:

```env
LLM_PROVIDER=gemini
```

or:

```env
LLM_PROVIDER=groq
```

This separates the application workflow from the underlying LLM provider.

---

# Agent Workflow

The application is orchestrated using **LangGraph**.

```text
User Question
      |
      v
Schema Inspection
      |
      v
SQL Generation
      |
      v
SQL Validation
      |
      v
Read-Only Execution
      |
      +---------------- Success ----------------+
      |                                         |
      |                                         v
      |                                Result Summarization
      |                                         |
      |                                         v
      |                                Visualization Check
      |                                         |
      |                                         v
      |                                  Final Response
      |
      +---------------- Error ------------------+
                        |
                        v
                  SQL Correction
                        |
                        v
                      Retry
```

The workflow provides explicit control over the agent's execution path rather than relying on an uncontrolled LLM loop.

---

# SQL Self-Correction

SQLAgent AI uses database execution errors as feedback.

When a generated query fails, the workflow sends the relevant information to a dedicated SQL correction stage.

```text
Generated SQL
      |
      v
Database Execution
      |
      v
Execution Error
      |
      v
Previous SQL + Error
      |
      v
SQL Correction Agent
      |
      v
Corrected SQL
      |
      v
Database Execution
```

The correction stage receives:

- Original user question
- Database schema
- Previous SQL query
- Database execution error

It then generates a corrected SQL query.

### Retry Policy

**Maximum SQL attempts: 2**

This provides controlled error recovery while preventing an infinite execution loop.

---

# Read-Only SQL Execution

Connecting an LLM directly to a database requires execution controls.

SQLAgent AI restricts generated queries to read-oriented operations.

### Allowed

```sql
SELECT ...
```

```sql
WITH ...
```

### Blocked

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
REPLACE
TRUNCATE
ATTACH
DETACH
```

The application is therefore focused on database analytics and exploration rather than database modification.

> These controls are appropriate for the portfolio application demonstrated here. A production system should use additional database-level permissions and security controls.

---

# AI-Powered Result Summarization

After successful SQL execution, the returned data is passed to a dedicated summarization stage.

For example:

### User

```text
How many customers are there?
```

### Generated SQL

```sql
SELECT COUNT(*) FROM Customer;
```

### Database Result

```text
59
```

### Final Response

```text
There are 59 customers.
```

The summarization stage is instructed to use information contained in the SQL result and avoid introducing unsupported facts.

---

# Automatic Visualization

SQLAgent AI analyzes returned datasets and determines whether visualization is useful.

For example:

```text
Show me the total revenue by country
```

can produce a structured dataset suitable for visualization.

For simple scalar queries such as:

```text
How many customers are there?
```

the application avoids creating an unnecessary chart.

Visualization is implemented using **Plotly**.

---

# Database

SQLAgent AI uses the **SQLite Chinook database**, a relational sample database representing a digital music store.

The database contains entities including:

- Customer
- Invoice
- InvoiceLine
- Artist
- Album
- Track
- Genre
- Employee
- Playlist
- PlaylistTrack
- MediaType

This provides a relational environment for demonstrating:

- SQL generation
- JOIN operations
- Aggregations
- GROUP BY
- ORDER BY
- Filtering
- Ranking
- Revenue analytics
- Customer analytics
- Music analytics

---

# Example Queries

## 01 — Customer Analytics

### Question

```text
How many customers are there?
```

### Generated SQL

```sql
SELECT COUNT(*) FROM Customer;
```

### Example Result

```text
There are 59 customers.
```

---

## 02 — Customer Spending

### Question

```text
Show me the top 10 customers by total spending
```

### Example Generated SQL

```sql
SELECT
    Customer.CustomerId,
    Customer.FirstName,
    Customer.LastName,
    SUM(Invoice.Total) AS TotalSpent
FROM Customer
JOIN Invoice
    ON Customer.CustomerId = Invoice.CustomerId
GROUP BY
    Customer.CustomerId,
    Customer.FirstName,
    Customer.LastName
ORDER BY TotalSpent DESC
LIMIT 10;
```

---

## 03 — Revenue Analytics

### Question

```text
Show me the total revenue by country
```

### Example Generated SQL

```sql
SELECT
    BillingCountry,
    SUM(Total) AS TotalRevenue
FROM Invoice
GROUP BY BillingCountry;
```

The resulting dataset can be visualized automatically.

---

## 04 — Music Analytics

### Question

```text
Show me the most popular genres
```

The agent determines the required tables and SQL operations from the available database schema.

---

# Architecture

```text
                         +----------------------+
                         |        User          |
                         | Natural Language     |
                         |       Query          |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |     SQLAgent AI      |
                         |       LangGraph      |
                         +----------+-----------+
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
          +------------------+             +----------------------+
          | SQLite Database  |             | Multi-Provider LLM  |
          | Schema & Data    |             | Gemini / Groq        |
          +--------+---------+             +----------+-----------+
                   |                                  |
                   +---------------+------------------+
                                   |
                                   v
                         +----------------------+
                         | SQL Validation &     |
                         | Safe Execution       |
                         +----------+-----------+
                                    |
                         +----------+----------+
                         |                     |
                      Success                 Error
                         |                     |
                         v                     v
                +----------------+    +----------------+
                | Result         |    | SQL Correction|
                | Summarization  |    | Agent         |
                +-------+--------+    +-------+--------+
                        |                     |
                        v                     |
                +----------------+            |
                | Visualization  |            |
                | Decision       |            |
                +-------+--------+            |
                        |                     |
                        +----------+----------+
                                   |
                                   v
                         +----------------------+
                         |   Final Response     |
                         | Answer + SQL + Data  |
                         | + Visualization      |
                         +----------------------+
```

---

# LangGraph Workflow

The agent is implemented as a stateful graph.

### Core Nodes

```text
generate_sql
     |
     v
execute_sql
     |
     +------ success ------> summarize_result
     |                              |
     |                              v
     |                       prepare_chart
     |
     +------ error --------> correct_sql
                                    |
                                    v
                                  retry
```

### Conditional Execution

```text
execute_sql
    |
    +---- success ------> summarize_result
    |
    +---- error --------> correct_sql
    |
    +---- max retries --> end
```

This explicit graph structure provides controlled execution and retry behavior.

---

# Multi-Provider Design

LLM integration is isolated from the rest of the application.

The SQL generation and result summarization layers select the provider based on:

```env
LLM_PROVIDER
```

## Gemini

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key
```

## Groq

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
```

Only configure the provider you intend to use locally.

The application also supports **Streamlit Secrets**, allowing the same codebase to be deployed without exposing API keys in the repository.

---

# Tech Stack

| Technology | Role |
|---|---|
| Python | Core development |
| Streamlit | Interactive web application |
| LangGraph | Agent workflow orchestration |
| LangChain | LLM integration |
| Google Gemini | SQL generation, correction, and summarization |
| Groq | Alternative LLM provider |
| SQLite | Relational database |
| SQLGlot | SQL parsing and validation |
| Pandas | Data processing |
| Plotly | Interactive visualization |
| python-dotenv | Local environment configuration |
| Pytest | Automated testing |

---

# Project Structure

```text
SQLAgent-AI/
│
├── app.py
│
├── database/
│   └── chinook.db
│
├── src/
│   ├── __init__.py
│   ├── graph.py
│   ├── database.py
│   ├── sql_generator.py
│   ├── summarizer.py
│   └── chart_tool.py
│
├── tests/
│   ├── test_database.py
│   ├── test_gemini.py
│   └── test_sql_generator.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/AbdelrhmanAkl/SQLAgent-AI.git
cd SQLAgent-AI
```

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file in the project root.

## Option 1 — Gemini

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key
```

## Option 2 — Groq

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
```

Only configure the provider you intend to use locally.

### Security

Never commit `.env` files or API keys to GitHub.

The repository excludes `.env` through `.gitignore`.

---

# Run Locally

Start the Streamlit application:

```bash
streamlit run app.py
```

Then open the local Streamlit URL displayed in the terminal.

---

# Streamlit Cloud Deployment

SQLAgent AI is deployed using **Streamlit Community Cloud**.

### Production Application

https://sqlagent-ai.streamlit.app/

For deployment, configure the required secrets through Streamlit's Secrets manager.

### Gemini

```toml
LLM_PROVIDER = "gemini"
GOOGLE_API_KEY = "your_gemini_api_key"
```

### Groq

```toml
LLM_PROVIDER = "groq"
GROQ_API_KEY = "your_groq_api_key"
```

The application supports both environment variables and Streamlit Secrets.

API keys are not stored in the GitHub repository.

---

# Testing

The project includes automated tests covering database and SQL-generation-related functionality.

Run the complete test suite:

```bash
python -m pytest -q
```

### Current Local Validation

```text
10 passed
```

The test suite verifies core application behavior and SQL-related functionality.

---

# Security Considerations

SQLAgent AI demonstrates a controlled architecture for connecting an LLM to a relational database.

Current protections include:

- Read-only SQL policy
- Restricted SQL operations
- Schema-aware SQL generation
- Controlled retry count
- API key exclusion from Git
- Environment-based configuration
- Streamlit Secrets support
- SQL parsing and validation

### Production Hardening

The current implementation is a portfolio application.

A production deployment should additionally consider:

- Database-level permissions
- Query timeouts
- Resource limits
- Authentication
- Auditing
- Monitoring
- Stronger SQL security controls

---

# Engineering Highlights

## Controlled Agent Execution

LangGraph explicitly controls workflow transitions and retry behavior.

## Provider Abstraction

Gemini and Groq can be selected through configuration without changing the application workflow.

## Error-Driven Recovery

Database execution errors are fed back into the SQL correction stage.

## Database Safety

Generated SQL is restricted to read-oriented operations.

## Separation of Concerns

The system separates major responsibilities:

```text
Database Access
      |
SQL Generation
      |
SQL Validation
      |
Agent Orchestration
      |
Result Summarization
      |
Visualization
```

This structure makes the application easier to understand, maintain, and extend.

---

# Future Improvements

Potential future directions include:

- Multi-database support
- PostgreSQL integration
- MySQL integration
- Conversation memory
- Multi-turn analytics
- Query history
- User authentication
- Role-based database permissions
- Advanced SQL validation
- Query cost estimation
- Streaming agent execution
- Improved chart selection
- Observability and tracing
- Production database connectors
- Database-level query timeouts
- Query result caching

These are future directions rather than capabilities currently claimed as part of the implementation.

---

# Why SQLAgent AI?

SQLAgent AI demonstrates how an LLM can be integrated into a structured software system rather than being used as a standalone chatbot.

The project combines:

```text
LLMs
  +
Agentic Workflows
  +
Relational Databases
  +
Text-to-SQL
  +
Validation
  +
Self-Correction
  +
Data Visualization
  +
Cloud Deployment
```

The result is an end-to-end AI analytics application capable of translating natural-language questions into database operations and returning understandable analytical results.

---