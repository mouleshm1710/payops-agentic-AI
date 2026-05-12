# AI Payroll Resolution & Support Platform

An enterprise-grade AI-powered payroll operations platform built using FastAPI, React, Azure Cloud Services, Retrieval-Augmented Generation (RAG), and Agentic AI workflows.

The platform helps employees and HR operations teams resolve payroll-related issues using AI-driven reasoning, policy retrieval, workflow orchestration, and operational analytics dashboards.

<img width="940" height="1233" alt="image" src="https://github.com/user-attachments/assets/366e52dc-635d-4fd2-90ff-ec96f1d2ca90" />

---

# Project Overview

This platform was designed to simulate a real-world enterprise payroll support system where:

- Employees can ask payroll and HR policy questions
- AI retrieves payroll transaction data from Azure SQL
- AI retrieves policy context from Azure AI Search
- Agentic workflows orchestrate reasoning steps dynamically
- HR teams can monitor payroll anomalies and operational exceptions
- Operational dashboards provide payroll intelligence insights

The solution combines:
- Agentic AI orchestration
- Retrieval-Augmented Generation (RAG)
- Azure cloud services
- Operational analytics
- Enterprise-style frontend experience
- Cloud-native deployment and CI/CD

---

# Key Features

## Employee AI Assistant
- Payroll issue resolution
- Overtime clarification
- PTO policy explanation
- Deduction analysis
- Approval status checks
- Payroll anomaly explanations

## Agentic AI Workflow
- Intent classification
- Execution planning
- Conditional retrieval routing
- Parallel context retrieval
- Combined reasoning
- Final response orchestration

## RAG Policy Intelligence
- Azure AI Search integration
- Policy document retrieval
- Grounded AI responses
- Payroll + policy context merging

## HR Operations Dashboard
- Payroll risk monitoring
- Overtime trend analysis
- Ticket monitoring
- High-risk payroll records
- Payroll anomaly dashboards
- Operational analytics

## Cloud-Native Architecture
- Dockerized frontend and backend
- Azure deployment
- GitHub Actions CI/CD
- Azure Container Registry (ACR)
- Azure Web Apps

---

# Tech Stack

## Frontend
- React
- Vite
- JavaScript
- Enterprise Dashboard UI

## Backend
- FastAPI
- Python
- SQLAlchemy
- pyodbc
- LangGraph-style orchestration

## AI & RAG
- OpenAI API
- Azure AI Search
- Retrieval-Augmented Generation (RAG)
- Agentic AI workflows

## Database & Storage
- Azure SQL Database
- Azure Blob Storage

## Cloud & DevOps
- Docker
- GitHub Actions
- Azure Container Registry (ACR)
- Azure Web Apps

---

# System Architecture

```text
Frontend (React UI)
        ↓
FastAPI Backend
        ↓
Agentic Workflow Engine
        ↓
-----------------------------
|                           |
Azure SQL             Azure AI Search
(Payroll Data)        (Policy RAG)
|                           |
-----------------------------
        ↓
Combined Reasoning Layer
        ↓
Final AI Response
```

---

# Project Structure

```text
3_root/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── services/
│   │   ├── routers/
│   │   ├── retrieval/
│   │   ├── tools/
│   │   └── main.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── data/
├── notebooks/
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

# Agentic Workflow

The platform uses a multi-step AI workflow instead of a simple chatbot.

## Workflow Steps

1. Intent Classification
2. Execution Planning
3. Payroll SQL Retrieval
4. Policy RAG Retrieval
5. Shared Context Consolidation
6. Combined Reasoning
7. Final Response Packaging

Example:
- Payroll-only questions → SQL retrieval
- Policy-only questions → RAG retrieval
- Combined questions → both retrieval pipelines

---

# Payroll Analytics Features

The HR operations dashboard includes:

- Payroll risk levels
- Overtime trend analysis
- Approval bottlenecks
- Ticket status monitoring
- Anomaly distribution analysis
- High-risk employee tracking

---

# Azure Services Used

| Service | Purpose |
|---|---|
| Azure SQL Database | Payroll transaction storage |
| Azure Blob Storage | Policy document storage |
| Azure AI Search | RAG document retrieval |
| Azure Web Apps | Frontend & backend hosting |
| Azure Container Registry | Docker image hosting |
| GitHub Actions | CI/CD pipeline |

---

# Dockerized Deployment

## Local Deployment

```bash
docker compose up --build
```

Frontend:
```text
http://localhost:3000
```

Backend:
```text
http://localhost:8000/docs
```

---

# CI/CD Pipeline

GitHub Actions pipeline automatically:

1. Builds Docker images
2. Pushes images to Azure Container Registry
3. Azure Web Apps pull latest images
4. Deploys updated application

---

# Environment Variables

## Backend `.env`

```env
AZURE_SQL_SERVER=
AZURE_SQL_DATABASE=
AZURE_SQL_USERNAME=
AZURE_SQL_PASSWORD=

AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_KEY=
AZURE_SEARCH_INDEX=

OPENAI_API_KEY=
```

---

# Sample Questions

- Why was my overtime payment reduced?
- What does the PTO carry-over policy say?
- Why is my payroll approval still pending?
- Explain the deductions in my latest payroll.
- Why did my net pay change significantly this month?
- What does the overtime policy say regarding approvals?

---

# Key Learnings

This project provided hands-on experience with:

- Agentic AI system design
- RAG architecture implementation
- Azure cloud deployment
- FastAPI backend engineering
- React operational dashboards
- Docker containerization
- CI/CD automation
- Azure SQL integrations
- Enterprise workflow orchestration
- AI-powered operational analytics

---

# Future Enhancements

- Multi-agent orchestration
- Human-in-the-loop workflows
- Azure OpenAI integration
- RBAC authentication
- Real-time payroll streaming
- LangSmith observability
- Role-based dashboards
- Ticket auto-resolution workflows
- AI-powered escalation routing

---

# Final Outcome

The final solution became a fully functional cloud-hosted AI payroll operations platform capable of:

- Payroll issue resolution
- HR policy intelligence
- Payroll anomaly analysis
- Agentic AI orchestration
- Operational monitoring
- Enterprise cloud deployment

This project simulates a realistic enterprise AI product combining:
- AI engineering
- cloud engineering
- data engineering
- frontend systems
- operational analytics
- and DevOps automation.
