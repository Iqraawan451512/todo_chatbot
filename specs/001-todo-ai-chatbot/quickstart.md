# Quickstart: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-02-06

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend and Better Auth)
- Neon PostgreSQL account (free tier works)
- OpenAI API key

## Environment Variables

Create a `.env` file at the project root:

```env
# Database
DATABASE_URL=postgresql://user:password@project-pooler.neon.tech/dbname?sslmode=require

# OpenAI
OPENAI_API_KEY=sk-...

# Better Auth (frontend)
BETTER_AUTH_SECRET=your-secret-key

# ChatKit (production only)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
```

## Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install fastapi uvicorn sqlmodel psycopg2-binary
pip install openai-agents
pip install mcp
pip install python-dotenv

# Run the server
uvicorn backend.app.main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
npm install @openai/chatkit-react
npm install better-auth

# Run development server
npm run dev
```

## Verify Setup

1. Backend health check:
   ```bash
   curl http://localhost:8000/health
   ```

2. Send a test chat message:
   ```bash
   curl -X POST http://localhost:8000/api/test-user/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Add a task to buy groceries"}'
   ```

3. Expected response:
   ```json
   {
     "conversation_id": 1,
     "response": "I've added 'Buy groceries' to your task list!",
     "tool_calls": [
       {
         "tool": "add_task",
         "arguments": {"user_id": "test-user", "title": "Buy groceries"},
         "result": {"task_id": 1, "status": "created", "title": "Buy groceries"}
       }
     ]
   }
   ```

## Statelessness Verification

1. Send a chat message and note the conversation_id
2. Stop the backend server (`Ctrl+C`)
3. Restart the backend server
4. Send another message with the same conversation_id
5. Verify the conversation history is intact

## Project Structure

```text
backend/
├── app/
│   ├── main.py            # FastAPI bootstrap + health check
│   ├── config.py           # Settings from environment
│   ├── db/
│   │   ├── engine.py       # SQLModel engine (Neon pooled)
│   │   └── models.py       # Task, Conversation, Message
│   ├── api/
│   │   └── chat.py         # POST /api/{user_id}/chat
│   ├── agent/
│   │   ├── agent.py        # OpenAI Agent definition
│   │   └── runner.py       # Agent execution with history
│   ├── mcp/
│   │   ├── server.py       # MCP server setup
│   │   └── tools.py        # 5 task tools
│   └── services/
│       ├── conversations.py # Load/create conversations
│       └── messages.py      # Persist messages
└── tests/

frontend/
├── src/
│   ├── app/                # Next.js app
│   ├── components/         # ChatKit wrapper
│   └── lib/                # Auth + API client
└── package.json
```
