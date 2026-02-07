---
id: 6
title: Frontend Redesign Implementation
stage: green
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: architect
command: implement
labels: ["frontend", "redesign", "ux", "guided-flow", "landing-page"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/globals.css
  - frontend/src/app/layout.tsx
  - frontend/src/app/page.tsx
  - frontend/src/components/ChatWidget.tsx
  - frontend/src/lib/api.ts
tests:
  - TypeScript type check (tsc --noEmit) — PASS
---

## Prompt

Implement the following plan:

# TodoHub Frontend Redesign Plan

## Overview
Redesign the frontend with a landing page + guided chatbot UX. No backend changes needed.

## Layout: Two-Column Split
- Left (40%): Chat panel with guided flow
- Right (60%): Landing page with hero section
- Mobile (<768px): Stack vertically (hero banner on top, chat below)

## Color Scheme
- Primary: #4F46E5 (Indigo)
- Background: #F8FAFC (Slate 50)
- Hero gradient: #4F46E5 → #7C3AED
- User bubbles: Indigo, Assistant bubbles: Light gray
- Success: #10B981, Danger: #EF4444

## Files to Create/Modify
1. globals.css (NEW) — CSS custom properties, reset, animations
2. layout.tsx (MODIFY) — Import globals.css, update title to "TodoHub"
3. page.tsx (REWRITE) — Two-column layout with landing content
4. ChatWidget.tsx (REWRITE) — Guided flow state machine with 5 action buttons
5. api.ts (MODIFY) — Add parseTaskListFromResponse() helper

## Response snapshot

Implemented the full frontend redesign:

1. **globals.css** — Created design system with CSS custom properties (indigo primary, slate background, hero gradient), body reset, scrollbar styling, and fade/slide/pulse animations.

2. **layout.tsx** — Updated to import globals.css and changed title from "Todo AI Chatbot" to "TodoHub".

3. **page.tsx** — Rewrote with two-column layout: sticky ChatWidget on left (40%), landing page on right (60%) with hero gradient section, feature cards (Chat Naturally, Guided Actions, Instant Updates), example commands section, and footer. Includes responsive CSS for mobile stacking at <768px.

4. **ChatWidget.tsx** — Complete rewrite with state machine (action_select → collecting_inputs → sending → show_result). Five action buttons: Add Task (title + optional description inputs), View Tasks (All/Pending/Completed filter buttons), Complete Task (auto-fetches pending tasks, select to complete), Delete Task (auto-fetches tasks, select with confirmation), Update Task (auto-fetches tasks, select then enter new title). Includes free-text input fallback, animated message bubbles, typing indicator dots, and gradient header.

5. **api.ts** — Added ParsedTask interface and parseTaskListFromResponse() helper that extracts tasks from tool_calls[].result JSON (handles arrays, .tasks, and .items shapes).

TypeScript type check passed cleanly (tsc --noEmit).

## Outcome

- ✅ Impact: Complete frontend redesign with guided UX and landing page — 5 files touched
- 🧪 Tests: tsc --noEmit passed with zero errors
- 📁 Files: 1 created (globals.css), 4 modified (layout.tsx, page.tsx, ChatWidget.tsx, api.ts)
- 🔁 Next prompts: Test all 5 guided flows end-to-end with backend running, verify mobile responsive layout
- 🧠 Reflection: Inline styles used throughout for simplicity; could be migrated to Tailwind/CSS modules later if design system grows

## Evaluation notes (flywheel)

- Failure modes observed: Next.js build blocked by locked .next directory from running dev server (Windows EPERM); tsc --noEmit used as fallback validation
- Graders run and results (PASS/FAIL): TypeScript type check — PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with live backend to verify parseTaskListFromResponse parsing matches actual API response shape
