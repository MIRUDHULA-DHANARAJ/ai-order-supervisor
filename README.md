# AI Order Supervisor Dashboard

An AI-powered Order Supervisor that continuously monitors customer orders, detects issues, decides the next action using an LLM, and allows human operators to pause, resume, or stop workflows at any time.

The project demonstrates how AI Agents and Temporal Workflows can work together to build reliable, long-running business automation.

---
# Video Walkthrough

https://www.loom.com/share/2cd5c1fefe8d4bbd89408c9fe0e42ca6


# Project Overview

The system monitors an order from the moment it is created until it is delivered.

Whenever the order status changes, the workflow wakes up, gathers the latest information, asks the AI agent what should happen next, performs the recommended business action, stores everything in the database, and waits for the next event.

Unlike traditional automation, the workflow can safely "sleep" for hours or even days without consuming system resources.

---

# Features

- AI-powered order supervision
- Long-running Temporal workflows
- Human-in-the-loop control
- Pause, Resume and Kill workflows
- Order timeline tracking
- AI memory summarization
- Business tool execution
- Complete audit history
- SQLite database storage
- REST APIs using FastAPI
- Modern Next.js dashboard

---

# Project Architecture

```
                    Next.js Dashboard
                           │
                           ▼
                    FastAPI Backend
                           │
                           ▼
                Temporal Workflow Engine
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
     Workflow Logic              Activity Layer
                                        │
                     ┌──────────────────┴─────────────────┐
                     ▼                                    ▼
               PostgreSQL Database (Supabase)               AI Supervisor Agent
                                                        │
                                                        ▼
                                               Groq Llama 3.3 70B
```

---

# Project Structure

```
order-supervisor/
│
├── backend/
│
│   ├── api/
│   │      REST API endpoints
│   │
│   ├── workflows/
│   │      Temporal workflow definitions
│   │
│   ├── activities/
│   │      External operations and AI execution
│   │
│   ├── agents/
│   │      LLM prompts and AI logic
│   │
│   ├── db/
│   │      Database configuration
│   │
│   ├── models/
│   │      SQLAlchemy models
│   │
│   ├── schemas/
│   │      Request and response schemas
│   │
│   ├── services/
│   │      Business logic
│   │
│   ├── core/
│   │      Configuration and utilities
│   │
│   ├── worker.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│      Next.js dashboard
│
└── README.md
```

---

# Technology Stack

### Backend

- Python
- FastAPI
- Temporal
- SQLAlchemy
- PostgreSQL (Supabase)
- Pydantic

### AI

- Groq API
- Llama-3.3-70B-Versatile

### Frontend

- Next.js
- React
- Tailwind CSS

---

# Workflow

```
Customer Order Created
          │
          ▼
Temporal Workflow Starts
          │
          ▼
Waits for Events
          │
          ▼
Order Status Changes
          │
          ▼
Activity Executes
          │
          ▼
AI Agent Reviews Order
          │
          ▼
Selects Business Action
          │
          ▼
Stores Timeline & Memory
          │
          ▼
Workflow Sleeps Again
```

---

# Business Actions

The AI Supervisor can perform the following actions:

- Message Fulfillment Team
- Message Payments Team
- Message Logistics Team
- Message Customer
- Create Internal Note

---

# Human Controls

Operators can manually control any running workflow.

- Pause Workflow
- Resume Workflow
- Kill Workflow

These controls are available through REST APIs and the dashboard.

---

# Database

PostgreSQL (via Supabase) is used to store:

- Orders
- Timeline Events
- AI Memory
- Internal Notes
- Workflow Status
- AI Decisions

---

# API Endpoints

| Method | Endpoint | Description |
|----------|----------------|----------------------------|
| POST | /orders | Create a new order |
| GET | /orders | Get all orders |
| GET | /orders/{id} | Get order details |
| POST | /orders/{id}/pause | Pause workflow |
| POST | /orders/{id}/resume | Resume workflow |
| POST | /orders/{id}/kill | Stop workflow |

---

# Getting Started

## 1. Start Temporal Server

```bash
.\temporal.exe server start-dev
```

Temporal UI:

```
http://localhost:8233
```

---

## 2. Start Backend

```bash
cd backend

.\.venv\Scripts\Activate.ps1

uvicorn main:app --reload --port 8000
```

Backend:

```
http://localhost:8000
```

---

## 3. Start Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:3000
```

---

# Example Order Lifecycle

```
Order Created
      │
      ▼
Payment Pending
      │
      ▼
Payment Confirmed
      │
      ▼
Preparing Order
      │
      ▼
Shipped
      │
      ▼
Out For Delivery
      │
      ▼
Delivered
```

During every stage, the AI Supervisor checks the latest order information and decides whether any action is required.

---

# AI Memory

Instead of storing every conversation forever, the AI maintains a compact running summary of important events.

Example:

- Payment delay detected
- Customer contacted
- Logistics notified
- Shipment dispatched
- Customer confirmed delivery

This allows the AI to remember the important history while keeping prompts efficient.

---

# Why Temporal?

Temporal provides:

- Long-running workflows
- Reliable execution
- Automatic retries
- Durable state
- Event-based workflow execution
- Safe workflow replay

---

# Future Improvements

- Email notifications
- SMS integration
- WhatsApp integration
- Multi-agent collaboration
- Docker deployment
- Authentication
- Role-based access control
- Real-time WebSocket updates

---

# Author

**Mirudhula D**


Focused on building production-ready AI systems using Python, FastAPI, Temporal, LLMs, and modern backend technologies.
