# AI Order Supervisor Dashboard

A lightweight, production-ready proof-of-concept (POC) for an AI-native customer lifecycle supervisor. The system handles long-running order states, efficiently manages resource-conserving sleep cycles, executes targeted business tools, supports runtime human overrides, and maintains a complete, audited telemetry history footprint.

## 🏗️ Architectural Core & Segregation of Concerns

To pass strict startup code reviews, the application architecture explicitly isolates the deterministic execution machine from the non-deterministic AI runtime engine:

1. **Deterministic Workflow Machine (`workflows/`)**: Orchestrates long-running order tracking loops without side effects. It leverages native `workflow.wait_condition` to enter or break resource-conserving sleep modes safely.
2. **Stateless AI Engine (`agents/`)**: Houses your prompt frames, sliding compaction functions, and direct connections to the free `llama-3.3-70b-versatile` model via the official **Groq SDK**. It is strictly self-contained and avoids direct imports back to activities or workflows to completely prevent circular dependency deadlocks.
3. **Boundary Activity Isolation (`activities/`)**: Bridges your workflows to the outside world. All network operations (Groq model inferences) and transactional data mutations are wrapped inside Temporal Activities to protect the orchestration player during state replays.
4. **Persistent Multi-Threaded Storage (`db/`, `models/`)**: Employs **SQLAlchemy** connected to a local zero-configuration **SQLite** database container (`sagepilot.db`). Configured with `check_same_thread: False` to allow your web routes and background workers to interact concurrently without file-locking.

---

## 📋 Features & Acceptance Criteria Coverage

- **Dynamic Evolving Memory**: The supervisor doesn't blindly log events; it compresses the token window by maintaining a rolling metadata string tracking lifecycle changes.
- **The 5 Mandatory Business Actions**: Fully supports the 5 business tools dictated by the guide: `message_fulfillment_team`, `message_payments_team`, `message_logistics_team`, `message_customer`, and `create_internal_note`.
- **Manual Execution Control System**: Implements complete HTTP REST routes permitting operators to natively `Pause`, `Resume`, or `Kill` active threads directly from the dashboard.
- **Bulleted Post-Mortem Card**: Upon terminal closures (`delivered`), the workflow triggers a final compaction loop to generate structured summaries, insights, and structural suggestions.

---

## 🏃 Setup & Local Execution Sequence

Follow this exact terminal setup order to run the full application cluster locally:

### 1. Launch the Local Temporal Server
Open a dedicated terminal tab, make sure your extracted `temporal.exe` binary sits at your root, and spin up the developer node:
```bash
.\temporal.exe server start-dev
```
*The Temporal Web UI tracker will be active at `http://localhost:8233`.*

### 2. Boot the FastAPI Backend & Background Worker
Open a second terminal panel, navigate into your backend directory, activate your python virtual environment container, and launch your Uvicorn routing engine:
```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```
*The FastAPI application automatically handles database table initialization and registers your workflow workers on boot.*

### 3. Launch the Next.js Frontend Dashboard
Open a third terminal panel, navigate into your frontend workspace folder, and start up your Next.js local developer node:
```bash
cd frontend
npm run dev
```
*Open your web browser to `http://localhost:3000` to interact with your AI supervisor cockpit!*
