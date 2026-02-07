---
id: 8
title: Bonus Features - Sub-agents, Urdu, Voice
stage: green
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: iqra
command: implement bonus features
labels: ["sub-agents", "urdu", "voice", "bonus", "refactor"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: https://github.com/Iqraawan451512/todo_chatbot/pull/1
files:
  - backend/app/agent/language_agent.py
  - backend/app/agent/intent_agent.py
  - backend/app/agent/task_agent.py
  - backend/app/agent/response_agent.py
  - backend/app/agent/runner.py
  - frontend/src/components/ChatWidget.tsx
tests:
  - Python AST syntax check on all 5 backend agent files — PASS
  - TypeScript tsc --noEmit on frontend — PASS
---

## Prompt

Continue working on the existing codebase. Your task is to implement the following BONUS FEATURES completely and cleanly:

1) Reusable Intelligence (Sub-agents) — Break the AI agent into smaller, specialized sub-agents: LanguageAgent (detects language), IntentAgent (parses intent), TaskAgent (executes MCP tools), ResponseAgent (formats response). Refactor runner.py as a thin orchestrator.

2) Urdu Language Support — Auto-detect English, Urdu script, and Roman Urdu. Respond in the same language. Support all intents in all 3 languages.

3) Voice Commands — Add browser Speech Recognition API support with EN/UR toggle, mic button with pulse animation, graceful fallback for unsupported browsers.

RULES: Do not ask for clarification, Do not stop midway, Produce production-ready code.

## Response snapshot

Implemented all 3 bonus features end-to-end:

**Sub-agents Architecture:**
- `language_agent.py` — Unicode range detection for Urdu script, keyword dictionary for Roman Urdu
- `intent_agent.py` — Intent detection with keyword dicts for EN/UR/Roman UR, param extraction
- `task_agent.py` — Pure MCP tool execution with TaskResult dataclass
- `response_agent.py` — Response formatting with `_t(lang, en, ur, roman_ur)` translation helper
- `runner.py` — Thin orchestrator: Language → Intent → Task → Response pipeline

**Urdu Support:**
- Urdu script detection via Unicode ranges `\u0600-\u06FF`
- Roman Urdu detection via 60+ common word dictionary
- All 5 intents translated to Urdu script and Roman Urdu
- Error messages translated per language

**Voice Input:**
- Web Speech API with `SpeechRecognition` / `webkitSpeechRecognition`
- EN/UR language toggle button
- Mic button with CSS pulse animation when listening
- Graceful fallback — mic hidden if browser doesn't support

## Outcome

- ✅ Impact: Added 3 major bonus features — sub-agent architecture, trilingual support, voice input
- 🧪 Tests: Python AST parse OK on 5 files, TypeScript tsc --noEmit clean
- 📁 Files: 5 backend files (4 new + 1 rewritten), 1 frontend file modified
- 🔁 Next prompts: Commit and push changes, test all flows manually
- 🧠 Reflection: Sub-agent architecture cleanly separates concerns. Language detection is heuristic-based (no LLM call) which keeps latency low but may need tuning for edge cases.

## Evaluation notes (flywheel)

- Failure modes observed: SpeechRecognition type not in standard TS lib (fixed with `any` ref), UTF-8 encoding needed for Python syntax check on Windows
- Graders run and results (PASS/FAIL): Python AST PASS, TypeScript PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add unit tests for language detection and intent parsing
