# PhishPup

## Overview

PhishPup is a **decision‑verification assistant for communication**.

Before you send a message, PhishPup explains what your message *does in the real world* — not just what it says.

It does not block you.
It does not replace you.
It helps you make an informed decision.

Think of it as spell‑check for consequences instead of words.

---

## The Problem

Modern communication tools optimize speed, but many actions inside conversations are irreversible:

* sharing verification codes
* sending private information externally
* agreeing to commitments you can’t fulfill
* approving requests under pressure

Most digital mistakes are not hacks — they are rushed human decisions.

Software validates data before storing it.
Humans send irreversible messages with zero validation.

**PhishPup adds a decision checkpoint before sending.**

---

## Core Idea

PhishPup does not classify messages or detect scams.

It evaluates the *action* a message performs.

It answers:

> If this message is sent, what happens next?

The system analyzes four dimensions:

* **Intent** — what the user is about to do
* **Context** — what has already been said
* **Destination** — who receives the action
* **Payload** — what information leaves

It then returns a decision report instead of a probability score.

---

## Optional AI Context Understanding

Users can optionally describe the situation:

> “This is a recruiter scheduling an interview”
> “This is IT support asking for login help”

An LLM converts that description into structured context (category, sensitivity, focus areas).

Important:
The AI **does not decide safety**.
The deterministic engine makes the final decision.

AI understands context.
Rules enforce consequences.

---

## Workflow

1. Write your message
2. (Optional) describe the situation
3. Click **Check Email**
4. Review consequences
5. Choose to send or edit

PhishPup advises — the human decides.

---

## Decision Results

PhishPup returns one of three outcomes:

**SAFE**
Message appears consistent with context

**CHECK**
Something may be wrong — review before sending

**STOP_VERIFY**
This action may cause irreversible consequences

No probabilities. No hallucinations. Deterministic results.

---

## Example

Message:
"Here is the verification code: 482193"

Result:
STOP_VERIFY
You are transferring account access
The request creates urgency
This action cannot be undone
Verify inside the official application instead

---

## Architecture

Frontend: React
Backend: FastAPI
Engine: Deterministic rule‑based reasoning
AI Layer: Optional context interpreter

API:
POST /analyze
{
conversation: string,
draft: string,
metadata: {
recipients: string[],
source: string,
attachments: [{ name: string, type: string }],
interpreted_context: object
}
}

Returns:

* status
* commitment
* consequence
* reason
* recommendation
* context_used
* destination_count

No database
No authentication
Works without API keys

---

## Reasoning Engine

Pipeline:

1. Extract intended action
2. Detect persuasion signals
3. Evaluate reversibility
4. Simulate post‑send outcome
5. Produce explanation

Identical input always produces identical output.

Reliability matters more than guesswork near a send button.

---

## Running Locally

### Development (hot reload)

**Terminal 1 — backend:**
```bash
uvicorn main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

The browser talks to the Vite dev server; Vite proxies `/analyze`, `/interpret_context`, and `/health` to the FastAPI backend. Frontend changes hot reload without rebuilding.

### Production (single server)

```bash
cd frontend
npm install --cache .npm-cache
npm run build
cd ..
ENV=prod uvicorn main:app
```

Open: [http://localhost:8000](http://localhost:8000)

---

## Future Direction

* Gmail send‑time verification
* Chat integrations
* attachment awareness
* calendar‑aware commitments

Goal: a universal safety layer for human decisions in software.

---

## One‑line pitch

PhishPup checks the consequences of your message before you send it.
