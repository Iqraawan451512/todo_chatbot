"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import {
  sendMessage,
  ChatResponse,
  ParsedTask,
  parseTaskListFromResponse,
} from "@/lib/api";

// ── Types ──────────────────────────────────────────────────────────
type FlowState =
  | "action_select"
  | "collecting_inputs"
  | "sending"
  | "show_result";

type ActionType = "add" | "view" | "complete" | "delete" | "update";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

interface ChatWidgetProps {
  userId: string;
}

// ── Action definitions ─────────────────────────────────────────────
const ACTIONS: { key: ActionType; label: string; icon: string; desc: string }[] = [
  { key: "add", label: "Add Task", icon: "+", desc: "Create a new task" },
  { key: "view", label: "View Tasks", icon: "☰", desc: "Browse your tasks" },
  { key: "complete", label: "Complete", icon: "✓", desc: "Mark task done" },
  { key: "delete", label: "Delete", icon: "✕", desc: "Remove a task" },
  { key: "update", label: "Update", icon: "✎", desc: "Edit a task" },
];

const VIEW_FILTERS = ["All", "Pending", "Completed"] as const;

// ── Component ──────────────────────────────────────────────────────
export default function ChatWidget({ userId }: ChatWidgetProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [flowState, setFlowState] = useState<FlowState>("action_select");
  const [currentAction, setCurrentAction] = useState<ActionType | null>(null);
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [loading, setLoading] = useState(false);
  const [freeText, setFreeText] = useState("");

  // Guided flow inputs
  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [selectedFilter, setSelectedFilter] = useState<string>("All");
  const [fetchedTasks, setFetchedTasks] = useState<ParsedTask[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [updateField, setUpdateField] = useState<"title" | "description" | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  // Collecting step tracker (for multi-step flows)
  const [step, setStep] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, flowState, step]);

  // ── API call helper ────────────────────────────────────────────
  const doSend = useCallback(
    async (text: string): Promise<ChatResponse | null> => {
      setMessages((prev) => [...prev, { role: "user", content: text }]);
      setFlowState("sending");
      setLoading(true);
      try {
        const res = await sendMessage(userId, text, conversationId);
        setConversationId(res.conversation_id);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: res.response },
        ]);
        return res;
      } catch (err) {
        const errorMsg =
          err instanceof Error ? err.message : "Something went wrong";
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Error: ${errorMsg}` },
        ]);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [userId, conversationId]
  );

  // ── Reset to action select ────────────────────────────────────
  const resetFlow = useCallback(() => {
    setFlowState("action_select");
    setCurrentAction(null);
    setStep(0);
    setTaskTitle("");
    setTaskDescription("");
    setSelectedFilter("All");
    setFetchedTasks([]);
    setSelectedTaskId(null);
    setNewTitle("");
    setNewDescription("");
    setUpdateField(null);
    setConfirmDelete(false);
  }, []);

  // ── Action handlers ───────────────────────────────────────────
  const startAction = (action: ActionType) => {
    setCurrentAction(action);
    setFlowState("collecting_inputs");
    setStep(0);
  };

  // ADD TASK flow
  const handleAddSubmit = async () => {
    if (!taskTitle.trim()) return;
    const msg = taskDescription.trim()
      ? `Add a task "${taskTitle}" with description "${taskDescription}"`
      : `Add a task "${taskTitle}"`;
    await doSend(msg);
    setFlowState("show_result");
  };

  // VIEW TASKS flow
  const handleViewSubmit = async () => {
    const filterMap: Record<string, string> = {
      All: "Show all my tasks",
      Pending: "Show my pending tasks",
      Completed: "Show my completed tasks",
    };
    await doSend(filterMap[selectedFilter] || "Show my tasks");
    setFlowState("show_result");
  };

  // COMPLETE TASK flow — first fetch tasks, then pick one
  const handleCompleteFlow = async () => {
    if (step === 0) {
      // Fetch task list
      const res = await doSend("Show my pending tasks");
      if (res) {
        const tasks = parseTaskListFromResponse(res);
        setFetchedTasks(tasks);
      }
      setStep(1);
      setFlowState("collecting_inputs");
    }
  };

  const handleCompleteSubmit = async () => {
    if (selectedTaskId === null) return;
    await doSend(`Complete task ${selectedTaskId}`);
    setFlowState("show_result");
  };

  // DELETE TASK flow
  const handleDeleteFlow = async () => {
    if (step === 0) {
      const res = await doSend("Show all my tasks");
      if (res) {
        const tasks = parseTaskListFromResponse(res);
        setFetchedTasks(tasks);
      }
      setStep(1);
      setFlowState("collecting_inputs");
    }
  };

  const handleDeleteSubmit = async () => {
    if (selectedTaskId === null) return;
    await doSend(`Delete task ${selectedTaskId}`);
    setFlowState("show_result");
  };

  // UPDATE TASK flow
  const handleUpdateFlow = async () => {
    if (step === 0) {
      const res = await doSend("Show all my tasks");
      if (res) {
        const tasks = parseTaskListFromResponse(res);
        setFetchedTasks(tasks);
      }
      setStep(1);
      setFlowState("collecting_inputs");
    }
  };

  const handleUpdateSubmit = async () => {
    if (selectedTaskId === null) return;
    if (updateField === "title" && newTitle.trim()) {
      await doSend(`Update task ${selectedTaskId} title to "${newTitle}"`);
      setFlowState("show_result");
    } else if (updateField === "description" && newDescription.trim()) {
      await doSend(`Update task ${selectedTaskId} description to "${newDescription}"`);
      setFlowState("show_result");
    }
  };

  // Free text send
  const handleFreeTextSend = async () => {
    const text = freeText.trim();
    if (!text || loading) return;
    setFreeText("");
    await doSend(text);
    setFlowState("show_result");
  };

  // ── Kick off fetch-first flows on action start ────────────────
  useEffect(() => {
    if (flowState === "collecting_inputs" && step === 0) {
      if (currentAction === "complete") handleCompleteFlow();
      if (currentAction === "delete") handleDeleteFlow();
      if (currentAction === "update") handleUpdateFlow();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentAction, flowState]);

  // ── Render helpers ────────────────────────────────────────────

  const renderActionButtons = () => (
    <div style={{ padding: "8px 0" }}>
      <p style={{
        margin: "0 0 12px 0",
        fontSize: "0.875rem",
        color: "var(--color-text-muted)",
        fontWeight: 500,
      }}>
        What would you like to do?
      </p>
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "8px",
      }}>
        {ACTIONS.map((action) => (
          <button
            key={action.key}
            onClick={() => startAction(action.key)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "12px",
              borderRadius: "10px",
              border: "1px solid var(--color-border)",
              background: "var(--color-surface)",
              cursor: "pointer",
              textAlign: "left",
              transition: "all 0.15s ease",
              fontSize: "0.875rem",
              color: "var(--color-text)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "var(--color-primary)";
              e.currentTarget.style.background = "var(--color-primary-light)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--color-border)";
              e.currentTarget.style.background = "var(--color-surface)";
            }}
          >
            <span style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: "var(--color-primary-light)",
              color: "var(--color-primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 700,
              fontSize: "1rem",
              flexShrink: 0,
            }}>
              {action.icon}
            </span>
            <div>
              <div style={{ fontWeight: 600 }}>{action.label}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                {action.desc}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  const renderCollectingInputs = () => {
    if (!currentAction) return null;

    switch (currentAction) {
      case "add":
        return (
          <div className="animate-fade-in" style={{ padding: "8px 0" }}>
            <p style={{ margin: "0 0 8px", fontWeight: 600, fontSize: "0.875rem" }}>
              New Task
            </p>
            <input
              type="text"
              value={taskTitle}
              onChange={(e) => setTaskTitle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && (taskTitle.trim() ? handleAddSubmit() : null)}
              placeholder="Task title..."
              autoFocus
              style={inputStyle}
            />
            <input
              type="text"
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && (taskTitle.trim() ? handleAddSubmit() : null)}
              placeholder="Description (optional)..."
              style={{ ...inputStyle, marginTop: "8px" }}
            />
            <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
              <button onClick={resetFlow} style={secondaryBtnStyle}>Cancel</button>
              <button
                onClick={handleAddSubmit}
                disabled={!taskTitle.trim()}
                style={{
                  ...primaryBtnStyle,
                  opacity: taskTitle.trim() ? 1 : 0.5,
                }}
              >
                Add Task
              </button>
            </div>
          </div>
        );

      case "view":
        return (
          <div className="animate-fade-in" style={{ padding: "8px 0" }}>
            <p style={{ margin: "0 0 8px", fontWeight: 600, fontSize: "0.875rem" }}>
              Filter Tasks
            </p>
            <div style={{ display: "flex", gap: "8px" }}>
              {VIEW_FILTERS.map((f) => (
                <button
                  key={f}
                  onClick={() => setSelectedFilter(f)}
                  style={{
                    padding: "8px 16px",
                    borderRadius: "8px",
                    border: "1px solid",
                    borderColor: selectedFilter === f ? "var(--color-primary)" : "var(--color-border)",
                    background: selectedFilter === f ? "var(--color-primary)" : "var(--color-surface)",
                    color: selectedFilter === f ? "white" : "var(--color-text)",
                    cursor: "pointer",
                    fontSize: "0.875rem",
                    fontWeight: 500,
                    transition: "all 0.15s ease",
                  }}
                >
                  {f}
                </button>
              ))}
            </div>
            <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
              <button onClick={resetFlow} style={secondaryBtnStyle}>Cancel</button>
              <button onClick={handleViewSubmit} style={primaryBtnStyle}>
                Show Tasks
              </button>
            </div>
          </div>
        );

      case "complete":
        if (step < 1 || loading) {
          return (
            <div className="animate-fade-in" style={{ padding: "8px 0" }}>
              <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                Fetching your tasks...
              </p>
            </div>
          );
        }
        return (
          <div className="animate-fade-in" style={{ padding: "8px 0" }}>
            <p style={{ margin: "0 0 8px", fontWeight: 600, fontSize: "0.875rem" }}>
              Select task to complete
            </p>
            {fetchedTasks.length === 0 ? (
              <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                No tasks found. Try adding one first!
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                {fetchedTasks.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTaskId(t.id)}
                    style={{
                      ...taskPickerStyle,
                      borderColor: selectedTaskId === t.id ? "var(--color-success)" : "var(--color-border)",
                      background: selectedTaskId === t.id ? "#ECFDF5" : "var(--color-surface)",
                    }}
                  >
                    <span style={taskIdBadge}>#{t.id}</span>
                    <span>{t.title}</span>
                  </button>
                ))}
              </div>
            )}
            <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
              <button onClick={resetFlow} style={secondaryBtnStyle}>Cancel</button>
              {fetchedTasks.length > 0 && (
                <button
                  onClick={handleCompleteSubmit}
                  disabled={selectedTaskId === null}
                  style={{
                    ...primaryBtnStyle,
                    background: "var(--color-success)",
                    opacity: selectedTaskId !== null ? 1 : 0.5,
                  }}
                >
                  Complete
                </button>
              )}
            </div>
          </div>
        );

      case "delete":
        if (step < 1 || loading) {
          return (
            <div className="animate-fade-in" style={{ padding: "8px 0" }}>
              <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                Fetching your tasks...
              </p>
            </div>
          );
        }
        return (
          <div className="animate-fade-in" style={{ padding: "8px 0" }}>
            <p style={{ margin: "0 0 8px", fontWeight: 600, fontSize: "0.875rem" }}>
              Select task to delete
            </p>
            {fetchedTasks.length === 0 ? (
              <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                No tasks to delete.
              </p>
            ) : (
              <>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  {fetchedTasks.map((t) => (
                    <button
                      key={t.id}
                      onClick={() => { setSelectedTaskId(t.id); setConfirmDelete(false); }}
                      style={{
                        ...taskPickerStyle,
                        borderColor: selectedTaskId === t.id ? "var(--color-danger)" : "var(--color-border)",
                        background: selectedTaskId === t.id ? "#FEF2F2" : "var(--color-surface)",
                      }}
                    >
                      <span style={taskIdBadge}>#{t.id}</span>
                      <span>{t.title}</span>
                    </button>
                  ))}
                </div>
                {selectedTaskId !== null && !confirmDelete && (
                  <div style={{
                    marginTop: "10px",
                    padding: "10px",
                    borderRadius: "8px",
                    background: "#FEF2F2",
                    border: "1px solid #FECACA",
                    fontSize: "0.875rem",
                  }}>
                    Are you sure you want to delete this task?
                    <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                      <button onClick={resetFlow} style={secondaryBtnStyle}>Cancel</button>
                      <button
                        onClick={() => setConfirmDelete(true)}
                        style={{ ...primaryBtnStyle, background: "var(--color-danger)" }}
                      >
                        Yes, Delete
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
            <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
              {!selectedTaskId && (
                <button onClick={resetFlow} style={secondaryBtnStyle}>Cancel</button>
              )}
              {confirmDelete && (
                <button
                  onClick={handleDeleteSubmit}
                  style={{ ...primaryBtnStyle, background: "var(--color-danger)" }}
                >
                  Confirm Delete
                </button>
              )}
            </div>
          </div>
        );

      case "update":
        if (step < 1 || loading) {
          return (
            <div className="animate-fade-in" style={{ padding: "8px 0" }}>
              <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                Fetching your tasks...
              </p>
            </div>
          );
        }
        return (
          <div className="animate-fade-in" style={{ padding: "8px 0" }}>
            <p style={{ margin: "0 0 8px", fontWeight: 600, fontSize: "0.875rem" }}>
              Select task to update
            </p>
            {fetchedTasks.length === 0 ? (
              <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                No tasks to update.
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                {fetchedTasks.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => { setSelectedTaskId(t.id); setUpdateField(null); }}
                    style={{
                      ...taskPickerStyle,
                      borderColor: selectedTaskId === t.id ? "var(--color-primary)" : "var(--color-border)",
                      background: selectedTaskId === t.id ? "var(--color-primary-light)" : "var(--color-surface)",
                    }}
                  >
                    <span style={taskIdBadge}>#{t.id}</span>
                    <span>{t.title}</span>
                  </button>
                ))}
              </div>
            )}
            {/* Step 2: Choose what to update */}
            {selectedTaskId !== null && updateField === null && (
              <div style={{ marginTop: "10px" }}>
                <p style={{ margin: "0 0 8px", fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
                  What do you want to update?
                </p>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => setUpdateField("title")}
                    style={{
                      ...secondaryBtnStyle,
                      flex: 1,
                      borderColor: "var(--color-primary)",
                      color: "var(--color-primary)",
                    }}
                  >
                    Title
                  </button>
                  <button
                    onClick={() => setUpdateField("description")}
                    style={{
                      ...secondaryBtnStyle,
                      flex: 1,
                      borderColor: "var(--color-primary)",
                      color: "var(--color-primary)",
                    }}
                  >
                    Description
                  </button>
                </div>
              </div>
            )}
            {/* Step 3: Input for the chosen field */}
            {selectedTaskId !== null && updateField === "title" && (
              <div style={{ marginTop: "10px" }}>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && newTitle.trim() && handleUpdateSubmit()}
                  placeholder="New title..."
                  autoFocus
                  style={inputStyle}
                />
              </div>
            )}
            {selectedTaskId !== null && updateField === "description" && (
              <div style={{ marginTop: "10px" }}>
                <input
                  type="text"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && newDescription.trim() && handleUpdateSubmit()}
                  placeholder="New description..."
                  autoFocus
                  style={inputStyle}
                />
              </div>
            )}
            <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
              <button onClick={resetFlow} style={secondaryBtnStyle}>Cancel</button>
              {selectedTaskId !== null && updateField !== null && (
                <button
                  onClick={handleUpdateSubmit}
                  disabled={updateField === "title" ? !newTitle.trim() : !newDescription.trim()}
                  style={{
                    ...primaryBtnStyle,
                    opacity: (updateField === "title" ? newTitle.trim() : newDescription.trim()) ? 1 : 0.5,
                  }}
                >
                  Update {updateField === "title" ? "Title" : "Description"}
                </button>
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // ── Main render ───────────────────────────────────────────────
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "100%",
      background: "var(--color-surface)",
      borderRadius: "16px",
      boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        padding: "16px 20px",
        background: "var(--gradient-hero)",
        color: "white",
      }}>
        <h2 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>
          TodoHub Assistant
        </h2>
        <p style={{ margin: "2px 0 0", fontSize: "0.75rem", opacity: 0.85 }}>
          Manage your tasks with AI
        </p>
      </div>

      {/* Messages area */}
      <div style={{
        flex: 1,
        overflowY: "auto",
        padding: "16px",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
      }}>
        {messages.length === 0 && flowState === "action_select" && (
          <div style={{
            textAlign: "center",
            padding: "24px 16px",
            color: "var(--color-text-muted)",
          }}>
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>👋</div>
            <p style={{ margin: "0 0 4px", fontWeight: 600, color: "var(--color-text)" }}>
              Welcome to TodoHub!
            </p>
            <p style={{ margin: 0, fontSize: "0.875rem" }}>
              Choose an action below or type a message.
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className="animate-fade-in"
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div style={{
              maxWidth: "85%",
              padding: "10px 14px",
              borderRadius: msg.role === "user" ? "12px 12px 2px 12px" : "12px 12px 12px 2px",
              background: msg.role === "user" ? "var(--color-user-bubble)" : "var(--color-assistant-bubble)",
              color: msg.role === "user" ? "white" : "var(--color-text)",
              fontSize: "0.875rem",
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{
            display: "flex",
            gap: "4px",
            padding: "10px 14px",
            alignSelf: "flex-start",
          }}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="animate-pulse"
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  background: "var(--color-text-muted)",
                  animationDelay: `${i * 0.2}s`,
                }}
              />
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div style={{
        borderTop: "1px solid var(--color-border)",
        padding: "12px 16px",
        background: "var(--color-bg)",
      }}>
        {/* Guided flow area */}
        {flowState === "action_select" && renderActionButtons()}
        {flowState === "collecting_inputs" && renderCollectingInputs()}
        {flowState === "show_result" && (
          <div className="animate-fade-in" style={{ padding: "8px 0" }}>
            <button onClick={resetFlow} style={primaryBtnStyle}>
              ← Back to Actions
            </button>
          </div>
        )}

        {/* Free text input — always visible */}
        <div style={{
          display: "flex",
          gap: "8px",
          marginTop: "10px",
        }}>
          <input
            type="text"
            value={freeText}
            onChange={(e) => setFreeText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleFreeTextSend()}
            placeholder="Or type a message..."
            disabled={loading}
            style={{
              ...inputStyle,
              flex: 1,
              background: "var(--color-surface)",
            }}
          />
          <button
            onClick={handleFreeTextSend}
            disabled={loading || !freeText.trim()}
            style={{
              ...primaryBtnStyle,
              opacity: freeText.trim() && !loading ? 1 : 0.5,
              padding: "10px 16px",
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Shared styles ──────────────────────────────────────────────────

const inputStyle: React.CSSProperties = {
  padding: "10px 14px",
  borderRadius: "8px",
  border: "1px solid var(--color-border)",
  fontSize: "0.875rem",
  outline: "none",
  width: "100%",
  color: "var(--color-text)",
  background: "var(--color-bg)",
  transition: "border-color 0.15s ease",
};

const primaryBtnStyle: React.CSSProperties = {
  padding: "10px 20px",
  borderRadius: "8px",
  border: "none",
  background: "var(--color-primary)",
  color: "white",
  cursor: "pointer",
  fontSize: "0.875rem",
  fontWeight: 600,
  transition: "all 0.15s ease",
};

const secondaryBtnStyle: React.CSSProperties = {
  padding: "10px 20px",
  borderRadius: "8px",
  border: "1px solid var(--color-border)",
  background: "var(--color-surface)",
  color: "var(--color-text)",
  cursor: "pointer",
  fontSize: "0.875rem",
  fontWeight: 500,
  transition: "all 0.15s ease",
};

const taskPickerStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid var(--color-border)",
  background: "var(--color-surface)",
  cursor: "pointer",
  textAlign: "left",
  fontSize: "0.875rem",
  transition: "all 0.15s ease",
  color: "var(--color-text)",
};

const taskIdBadge: React.CSSProperties = {
  fontSize: "0.75rem",
  fontWeight: 600,
  color: "var(--color-primary)",
  background: "var(--color-primary-light)",
  padding: "2px 6px",
  borderRadius: "4px",
  flexShrink: 0,
};
