# AI Real-Time Voice Interview Platform

A **real-time, voice-first AI interview system** that conducts adaptive technical and HR interviews using **live speech, multi-LLM orchestration, resume-aware RAG, LLM-based evaluation, and MCP-driven agent architecture.**

Built to demonstrate how modern **AI voice agents and LLM systems are engineered in production**, not just how APIs are used.

## Overview

This platform simulates a **real interviewer**, not a chatbot.

It conducts **live voice interviews** through the browser, dynamically adapts questions based on the candidate’s **resume and job description**, evaluates answers using a **rubric-based LLM scoring engine**, and produces a **structured final interview report**.

**The system is designed with**:

- real-time constraints
- modular AI orchestration
- explainable evaluation
- production-ready architecture

## ✨ Key Features

### Real-Time Voice Interview
- Live **WebRTC-based voice interaction**
- **Voice Activity Detection (VAD)** for natural turn-taking
- Low-latency streaming audio pipeline (PCM16 standardized)

### Adaptive AI Interviewer
- Stage-aware questioning (HR / Technical)
- Contextual follow-ups probing **depth and reasoning**
- Prompt-controlled interviewer behavior

### Resume & Job-Aware RAG
- Retrieval-Augmented Generation over:
  - Candidate resume
  - Job description
- FAISS-based vector search with Sentence Transformers
- Structured context injection (no prompt stuffing)

### Multi-LLM Orchestration
- Parallel use of **Gemini** and **Hugging Face models**
- Latency-aware response selection
- Fault-tolerant LLM aggregation

### Interview Scoring & Feedback
- **LLM-as-a-Judge** with explicit evaluation rubric
- Scores across technical depth, clarity, communication, and confidence
- Explainable strengths, weaknesses, and improvement suggestions

### MCP-Based Agent Architecture
- Implements **Model Context Protocol (MCP)**
- Independent context servers for:
  - Interview logic
  - RAG retrieval
  - Evaluation
- Central host orchestrates structured context injection

### Final Interview Report
- Auto-generated at session end
- Aggregated scores, insights, and hiring verdict
- Designed for dashboards, PDFs, and analytics

---

## 🏗️ System Architecture

```text
Browser (WebRTC)
   ↓
Voice Activity Detection (VAD)
   ↓
Audio Pipeline (PCM16)
   ├── Whisper STT
   ├── AI Interviewer (LLM Router)
   │     ├── Gemini
   │     ├── Hugging Face
   │     └── LLM Aggregation
   ├── Edge TTS
   ↓
WebRTC Audio Output
```

### AI Orchestration Layer
```text
AIInterview
   ↓
MCP Host
   ├── Interview Context Server
   ├── RAG Context Server
   ├── Evaluation Context Server
   ↓
LLM Router
```

### Post-Interview
```text
Session Memory
   ↓
Report Generator
   ↓
Final Interview Report
```

---
## 🛠️ Tech Stack

### Frontend
- **React + TypeScript + Vite** – Component-based, type-safe client
- **React Router** – Dashboard, setup, live room, reports, history, and settings
- **WebRTC + WebSockets** – Real-time audio, transcript, and interview events
- **Responsive design system** – Accessible layouts for desktop and mobile
- **Voice Activity Detection (VAD)** – Natural turn-taking and interruption handling
- **Vercel** – Frontend deployment

### Backend
- **FastAPI** – Async backend & WebSocket server
- **WebSockets** – Real-time interview communication
- **aiortc** – Server-side WebRTC handling
- **AsyncIO** – Concurrent audio and LLM pipelines
- **Render** – Backend deployment

### AI & Machine Learning
- **Google Gemini** – Fast conversational LLM
- **Hugging Face Inference API** – Open-source LLMs
- **Multi-LLM Orchestration** – Latency-aware routing & fallback
- **Whisper (OpenAI)** – Speech-to-Text (STT)
- **Edge TTS (Microsoft Neural Voices)** – Low-latency Text-to-Speech
- **Sentence Transformers** – Text embeddings
- **FAISS** – Vector similarity search
- **Retrieval-Augmented Generation (RAG)** – Resume & JD-aware questioning

### AI System Design
- **Model Context Protocol (MCP)** – Modular agent-based architecture
- **LLM-as-a-Judge** – Rubric-based answer evaluation
- **Prompt Engineering** – Controlled interviewer behavior
- **Session Memory** – Stateful interview tracking
- **Context Orchestration** – Structured prompt injection

### Infrastructure & Tooling
- **Environment-based configuration (`.env`)**
- **Modular project structure**
- **Production-ready async design**
- **Extensible for Docker & CI/CD**

---
## 📁 Project Structure
```text 
ai-voice-interviewer/
│
├── frontend/
│   └── web/                # WebRTC client
│
├── backend/
│   ├── api/                # FastAPI entry point
│   ├── realtime/
│   │   ├── websocket/      # Interview & audio sockets
│   │   ├── webrtc/         # WebRTC tracks & signaling
│   │   └── audio_stream/   # STT → AI → TTS pipeline
│   │
│   ├── ai/
│   │   ├── llm_router/     # Multi-LLM orchestration
│   │   ├── rag/            # Resume/JD RAG
│   │   ├── prompts/        # Prompt templates
│   │   └── evaluation/     # Scoring & report generation
│   │
│   ├── mcp/
│   │   ├── host/           # MCP orchestrator
│   │   └── servers/        # Context servers
│   │
│   ├── memory/             # Session & evaluation memory
│   └── infra/              # Config, logging
│
├── data/
│   ├── resumes/
│   ├── job_descriptions/
│   └── embeddings/
│
├── scripts/                # Ingestion & testing
├── docs/                   # Architecture & design docs
└── README.md
```

---

## Deployment

- **Backend** deployed on **Render**
  - Async FastAPI + WebSockets + WebRTC

- **Frontend** deployed on **Vercel**
  - Low-latency static hosting for WebRTC client

- Environment-driven configuration allows seamless scaling and provider switching

---

## Author
**Yash Jain**  
AI / ML Engineer • Backend Engineer  

> Built with a strong focus on **correctness, scalability, and real-world AI system design**.
