# AI Real-Time Voice Interview Platform

A production-grade AI system that conducts real-time technical and HR interviews using
voice-based interaction, adaptive questioning, and multi-LLM orchestration.

This project demonstrates modern AI engineering concepts including:
- Real-time voice agents
- Context-aware RAG
- Multi-LLM aggregation
- MCP (Model Context Protocol)
- Function calling & structured outputs
- Evaluation-aware AI systems

---

## 🚀 Key Features
- Real-time voice-to-voice AI interviewer (WebRTC)
- Streaming STT → LLM → TTS pipeline
- Resume & Job Description aware questioning (RAG)
- Multi-LLM routing for latency and accuracy optimization
- MCP-based modular agent architecture
- Automated interview evaluation & feedback

---

## 🧠 System Architecture (High Level)

Browser (WebRTC)
↓
Streaming Gateway
↓
AI Orchestrator (MCP Host)
├── RAG Server
├── Interview Logic Server
├── Evaluation Server
└── Analytics Server
↓
Multi-LLM Router


---

## 🛠️ Tech Stack
**Backend**
- FastAPI
- WebSockets / WebRTC
- Python AsyncIO

**AI**
- LLMs (OpenAI / Gemini / HF)
- Vector Databases (FAISS / Qdrant)
- MCP (Model Context Protocol)

**Frontend**
- WebRTC
- React (planned)

---

## 📌 Project Status
🚧 Currently under active development  
Phase-based implementation following production AI system design.

---

## 📄 Documentation
See `/docs` for architecture and design decisions.
