"use client";

import { useState } from "react";
import ChatWidget from "@/components/ChatWidget";

export default function Home() {
  const userId = "dev-user";
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      {/* Full-screen landing page */}
      <div style={{ minHeight: "100vh" }}>
        {/* Hero Section */}
        <div style={{
          background: "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)",
          color: "white",
          padding: "0 24px",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
        }}>
          {/* Nav */}
          <nav style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "20px 0",
            maxWidth: "1100px",
            width: "100%",
            margin: "0 auto",
          }}>
            <div style={{ fontSize: "1.35rem", fontWeight: 800, letterSpacing: "-0.01em" }}>
              TodoHub
            </div>
            <button
              onClick={() => setChatOpen(true)}
              style={{
                padding: "10px 24px",
                borderRadius: "8px",
                border: "2px solid rgba(255,255,255,0.3)",
                background: "rgba(255,255,255,0.1)",
                color: "white",
                cursor: "pointer",
                fontSize: "0.9rem",
                fontWeight: 600,
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,0.2)";
                e.currentTarget.style.borderColor = "rgba(255,255,255,0.5)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,0.1)";
                e.currentTarget.style.borderColor = "rgba(255,255,255,0.3)";
              }}
            >
              Open Chat
            </button>
          </nav>

          {/* Hero content */}
          <div style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            maxWidth: "1100px",
            width: "100%",
            margin: "0 auto",
            paddingBottom: "80px",
          }}>
            <div style={{ textAlign: "center", maxWidth: "680px" }}>
              <div style={{
                display: "inline-block",
                padding: "6px 16px",
                borderRadius: "20px",
                background: "rgba(255,255,255,0.15)",
                fontSize: "0.85rem",
                fontWeight: 600,
                marginBottom: "24px",
                letterSpacing: "0.02em",
              }}>
                AI-Powered Task Management
              </div>
              <h1 style={{
                margin: "0 0 20px",
                fontSize: "3.25rem",
                fontWeight: 800,
                lineHeight: 1.12,
                letterSpacing: "-0.03em",
              }}>
                Manage your tasks with{" "}
                <span style={{
                  background: "linear-gradient(90deg, #E0E7FF, #C4B5FD)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}>
                  natural conversation
                </span>
              </h1>
              <p style={{
                margin: "0 auto 36px",
                fontSize: "1.15rem",
                lineHeight: 1.65,
                opacity: 0.85,
                maxWidth: "520px",
              }}>
                Create, update, and organize your tasks just by chatting.
                No forms, no friction — just tell the AI what you need.
              </p>
              <button
                onClick={() => setChatOpen(true)}
                style={{
                  padding: "14px 36px",
                  borderRadius: "10px",
                  border: "none",
                  background: "white",
                  color: "#4F46E5",
                  cursor: "pointer",
                  fontSize: "1rem",
                  fontWeight: 700,
                  transition: "all 0.2s ease",
                  boxShadow: "0 4px 14px rgba(0,0,0,0.15)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,0.2)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "0 4px 14px rgba(0,0,0,0.15)";
                }}
              >
                Start Chatting
              </button>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div style={{
          padding: "80px 24px",
          background: "var(--color-bg)",
        }}>
          <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
            <h2 style={{
              margin: "0 0 8px",
              fontSize: "1.75rem",
              fontWeight: 700,
              color: "var(--color-text)",
              textAlign: "center",
            }}>
              How it works
            </h2>
            <p style={{
              margin: "0 0 48px",
              color: "var(--color-text-muted)",
              fontSize: "1rem",
              textAlign: "center",
            }}>
              Three simple ways to manage your tasks
            </p>

            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "24px",
              maxWidth: "900px",
              margin: "0 auto",
            }}>
              {[
                {
                  icon: "💬",
                  title: "Chat Naturally",
                  desc: 'Say "Add a task to buy groceries" and it\'s done. No forms to fill out.',
                },
                {
                  icon: "🎯",
                  title: "Guided Actions",
                  desc: "Use the quick-action buttons for step-by-step task management.",
                },
                {
                  icon: "⚡",
                  title: "Instant Updates",
                  desc: "Complete, update, or delete tasks in seconds with simple commands.",
                },
              ].map((feature) => (
                <div
                  key={feature.title}
                  style={{
                    padding: "32px 28px",
                    borderRadius: "14px",
                    background: "var(--color-surface)",
                    border: "1px solid var(--color-border)",
                    textAlign: "center",
                  }}
                >
                  <div style={{ fontSize: "2rem", marginBottom: "14px" }}>
                    {feature.icon}
                  </div>
                  <h3 style={{
                    margin: "0 0 8px",
                    fontSize: "1.1rem",
                    fontWeight: 700,
                    color: "var(--color-text)",
                  }}>
                    {feature.title}
                  </h3>
                  <p style={{
                    margin: 0,
                    fontSize: "0.9rem",
                    color: "var(--color-text-muted)",
                    lineHeight: 1.6,
                  }}>
                    {feature.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Example Commands */}
        <div style={{
          padding: "64px 24px",
          background: "var(--color-surface)",
          borderTop: "1px solid var(--color-border)",
        }}>
          <div style={{ maxWidth: "1100px", margin: "0 auto", textAlign: "center" }}>
            <h2 style={{
              margin: "0 0 8px",
              fontSize: "1.75rem",
              fontWeight: 700,
              color: "var(--color-text)",
            }}>
              Try these commands
            </h2>
            <p style={{
              margin: "0 0 32px",
              color: "var(--color-text-muted)",
              fontSize: "1rem",
            }}>
              Type any of these into the chat to get started
            </p>

            <div style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "10px",
              justifyContent: "center",
            }}>
              {[
                '"Add a task to buy groceries"',
                '"Show my tasks"',
                '"Complete task 1"',
                '"Update task 2 to call the dentist"',
                '"Delete task 3"',
                '"Show my pending tasks"',
              ].map((cmd) => (
                <div
                  key={cmd}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "24px",
                    background: "var(--color-primary-light)",
                    color: "var(--color-primary)",
                    fontSize: "0.875rem",
                    fontWeight: 500,
                    fontFamily: "monospace",
                  }}
                >
                  {cmd}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: "28px 24px",
          borderTop: "1px solid var(--color-border)",
          background: "var(--color-bg)",
          textAlign: "center",
          fontSize: "0.85rem",
          color: "var(--color-text-muted)",
        }}>
          TodoHub — Built with FastAPI, OpenAI Agents SDK & Next.js
        </div>
      </div>

      {/* Floating chat toggle button */}
      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            width: "60px",
            height: "60px",
            borderRadius: "50%",
            border: "none",
            background: "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)",
            color: "white",
            cursor: "pointer",
            boxShadow: "0 4px 20px rgba(79,70,229,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "1.5rem",
            transition: "all 0.2s ease",
            zIndex: 1000,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "scale(1.1)";
            e.currentTarget.style.boxShadow = "0 6px 28px rgba(79,70,229,0.5)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
            e.currentTarget.style.boxShadow = "0 4px 20px rgba(79,70,229,0.4)";
          }}
          aria-label="Open chat"
        >
          💬
        </button>
      )}

      {/* Floating chat panel */}
      {chatOpen && (
        <div
          className="animate-slide-up"
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            width: "400px",
            height: "600px",
            maxHeight: "calc(100vh - 48px)",
            maxWidth: "calc(100vw - 48px)",
            zIndex: 1001,
            borderRadius: "16px",
            overflow: "hidden",
            boxShadow: "0 8px 40px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.05)",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* Minimize / close bar */}
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
            padding: "0 8px",
            background: "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)",
          }}>
            <button
              onClick={() => setChatOpen(false)}
              style={{
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.8)",
                cursor: "pointer",
                fontSize: "1.25rem",
                padding: "8px",
                lineHeight: 1,
                transition: "color 0.15s ease",
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = "white"; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = "rgba(255,255,255,0.8)"; }}
              aria-label="Minimize chat"
            >
              ✕
            </button>
          </div>
          <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
            <ChatWidget userId={userId} />
          </div>
        </div>
      )}
    </>
  );
}
