# RepoDoc: Intelligent Repo Onboarding & State Leak Auditing

## 💡 The Problem
Developer onboarding and architectural audits are historically slow, manual, and error-prone. When developers inherit a new codebase, identifying unencrypted state persistence (like tokens in `localStorage`), hardcoded secrets, and architectural boundaries requires hours of manual code reading.

## 🚀 The Solution (Working Prototype)
**RepoDoc** is an intelligent auditing tool built for the IBM Bob 2.0 Hackathon. It streamlines developer workflows by performing automated structural analysis and identifying potential state/secret leaks directly from a GitHub repository URL.

### Key Features:
- **Instant Architectural Parsing:** Fetches real repository metadata and root file structures via GitHub API.
- **Automated Leak Detection:** Identifies critical, high, and medium severity vulnerabilities (e.g., exposed `.env` files, insecure config settings).
- **Clean Architecture Foundation:** Built with a strict separation of concerns (Domain, Use Cases, Infrastructure, UI) ensuring high testability and future scalability.

## 🤖 IBM Bob IDE Integration (Core Component)
This prototype was aggressively engineered using **IBM Bob IDE** as the primary architectural collaborator. Instead of using Bob for simple code completion, Bob was utilized as an autonomous agent to scaffold entire infrastructure layers.

**Evidence of Bob Usage:**
As per hackathon requirements, all interaction summaries with IBM Bob IDE (proving the generation of APIs, UI components, and infrastructure clients) are documented in the `bob_sessions/` directory.

## 🏗️ Tech Stack
* **Frontend:** React, Vite (Zero-dependency custom UI)
* **Backend:** Python, FastAPI, Pydantic
* **Infrastructure:** HTTPX (Async API Clients)
* **AI Integration:** Engineered with a robust boundary for IBM Watsonx (`watsonx_client.py`). *Note: For this local working prototype demonstration, the LLM client utilizes an isolated internal mock to guarantee API rate-limit resilience during evaluation, while keeping the enterprise REST architecture fully intact.*

## ⚙️ Local Deployment Instructions (Judging Environment)

### 1. Start the Backend (FastAPI)
```bash
cd backend
python -m venv .venv
# Activate venv (Windows: .\.venv\Scripts\activate | Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```


### 2. Start the Frontend (React)
```bash
# Open a new terminal
cd frontend
npm install
npm run dev

```
Navigate to http://localhost:5173 in your browser. Enter any public GitHub repository URL (e.g., https://github.com/fastapi/fastapi) to see the automated audit in action.