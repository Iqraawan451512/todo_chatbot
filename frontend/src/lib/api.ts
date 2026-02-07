const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls?: Array<{
    tool: string;
    arguments: string;
    result?: string;
  }>;
}

export interface ParsedTask {
  id: number;
  title: string;
  description?: string;
  status: string;
}

export async function sendMessage(
  userId: string,
  message: string,
  conversationId?: number
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/${userId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId ?? null,
    }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.detail || error.error || "Request failed");
  }

  return res.json();
}

export function parseTaskListFromResponse(res: ChatResponse): ParsedTask[] {
  const tasks: ParsedTask[] = [];
  if (!res.tool_calls) return tasks;

  for (const call of res.tool_calls) {
    if (!call.result) continue;
    try {
      const parsed = JSON.parse(call.result);
      // Handle array of tasks directly
      const items = Array.isArray(parsed) ? parsed : parsed.tasks ?? parsed.items ?? [];
      for (const item of items) {
        if (item && typeof item.id === "number" && typeof item.title === "string") {
          tasks.push({
            id: item.id,
            title: item.title,
            description: item.description ?? undefined,
            status: item.status ?? "pending",
          });
        }
      }
    } catch {
      // Result wasn't JSON or didn't have expected shape — skip
    }
  }

  return tasks;
}
