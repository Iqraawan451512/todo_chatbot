---
id: 7
title: Floating Chatbot and Update Field Choice
stage: green
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: architect
command: implement
labels: ["frontend", "ux", "floating-chat", "update-flow"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/page.tsx
  - frontend/src/components/ChatWidget.tsx
tests:
  - TypeScript type check (tsc --noEmit) — PASS
---

## Prompt

every logic is working correctly but do one thing that is if i updated the tasks its should give me option update tittle or description and the second thing is landing page content is good but do one thing that is in landing page you are showing chatbot in left and landing page in right thats not looking good so do one thing that is show a landing page page in full screen and a chatbot like a troggle type i click the chatbot its open and i can minimix it too

## Response snapshot

Two changes implemented:

1. **Update flow now offers Title vs Description choice**: After selecting a task to update, user sees two buttons — "Title" and "Description". Choosing one reveals the appropriate input field. The submit message adapts accordingly (`Update task {id} title to "..."` or `Update task {id} description to "..."`).

2. **Full-screen landing page + floating toggle chatbot**: Replaced the two-column split layout with a full-screen landing page (hero, features, example commands, footer). The chatbot is now a floating widget: a circular chat bubble in the bottom-right corner that opens/closes a 400x600px floating panel with the ChatWidget. The panel slides up with animation and can be closed via the X button.

## Outcome

- ✅ Impact: Two UX improvements — update field choice and floating chatbot widget
- 🧪 Tests: tsc --noEmit passed with zero errors
- 📁 Files: 2 modified (page.tsx fully rewritten, ChatWidget.tsx edited for update flow)
- 🔁 Next prompts: Test update title and update description flows end-to-end with backend
- 🧠 Reflection: Floating chatbot pattern is more conventional for SaaS landing pages; update field choice adds needed flexibility

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): TypeScript type check — PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with live backend to verify update description message is handled correctly by the AI agent
