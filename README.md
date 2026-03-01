Replace the contents of README.md with the following:

# PhishPup

## Overview

PhishPup is a send-time decision verification assistant for email communication.

The system evaluates the real-world consequences of a message before it is sent. It does not block messages and does not classify conversations as scams. Instead, it analyzes the action performed by the message and provides a structured decision report.

PhishPup functions as a consequence validation layer comparable to how spell-check validates text.

The application runs as a local web interface for development and as a Chrome extension integrated with Gmail for the primary user experience.

---

## Problem

Digital communication tools prioritize speed while many actions performed within conversations are irreversible. Common issues include:

* sharing authentication codes or credentials
* sending sensitive information externally
* agreeing to commitments without verification
* approving requests under urgency or authority pressure

Many security and operational incidents originate from human decisions rather than system compromise. Current communication platforms do not validate the consequences of outgoing messages.

PhishPup introduces a decision checkpoint prior to message transmission.

---

## Core Concept

PhishPup evaluates the action a message performs rather than attempting to detect scams.

Primary question:

If this message is sent, what action occurs and what consequence follows?

The analysis considers four dimensions:

* Intent: the action expressed in the message
* Context: prior conversation content
* Destination: message recipients
* Payload: information being transmitted

The system produces a deterministic decision report rather than a probability score.

---

## Context Understanding

An optional AI layer converts a user-provided situation description into structured context including category, sensitivity, and focus areas.

The AI component does not determine safety outcomes. Final decisions are produced exclusively by the deterministic reasoning engine.

AI provides semantic understanding. Rules enforce consistent consequences.

---

## User Workflow (Gmail Extension)

1. Compose an email in Gmail
2. Open the PhishPup extension
3. Optionally describe the communication context
4. Select Check Email
5. Review the generated decision report
6. Send or modify the message

---

## Decision Results

PhishPup returns one of three outcomes:

SAFE
The message appears consistent with context.

CHECK
The message may contain a potential issue requiring review.

STOP_VERIFY
The message may cause irreversible consequences and should be verified through an independent channel.

Results are deterministic and reproducible.

---

## Example

Message:
Here is the verification code: 482193

Result:
STOP_VERIFY
Account access transfer is being performed
The request exhibits urgency
The action is irreversible
Verification should occur through the official application

---

## Architecture

Frontend: React demonstration interface
Backend: FastAPI service
Engine: deterministic rule-based reasoning system
AI layer: optional context interpreter
Integration: Chrome extension for Gmail

### API

POST /analyze

Request:
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

---

## Reasoning Engine

Processing pipeline:

1. Extract intended action
2. Detect persuasion signals
3. Evaluate recoverability
4. Determine outcome severity
5. Produce structured explanation

Identical inputs always produce identical outputs.

---

## Running Locally

Backend:
uvicorn main:app --reload

Frontend demo:
cd frontend
npm run dev

Chrome extension:
Load the phishpup-extension directory using chrome://extensions developer mode.

---

## Future Direction

* automatic send interception
* attachment awareness
* calendar-aware commitments
* messaging platform integrations

---

## Summary

PhishPup provides deterministic verification of communication actions prior to transmission.
