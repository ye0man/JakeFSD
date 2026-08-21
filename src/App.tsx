import { useState, useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import * as yaml from "js-yaml";
import "./App.css";
import Canvas, { type Pipeline } from "./components/Canvas";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

function App() {
  const [pythonVersion, setPythonVersion] = useState<string>("Checking Python runtime...");
  const [activeTab, setActiveTab] = useState<"chat" | "canvas" | "preview">("chat");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your Chief Data Architect. Describe the pipeline you want to build, and I'll propose a manifest.",
    },
  ]);
  const [input, setInput] = useState<string>("");
  const [isPlanning, setIsPlanning] = useState<boolean>(false);
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function checkRuntime() {
      try {
        setPythonVersion(await invoke("python_runtime_version"));
      } catch {
        setPythonVersion("Python runtime not available");
      }
    }
    checkRuntime();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const intent = input.trim();
    if (!intent) return;

    setMessages((prev) => [...prev, { role: "user", content: intent }]);
    setInput("");
    setIsPlanning(true);

    try {
      const plan = await invoke<string>("plan_from_intent", { intent });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Here's a proposed pipeline:\n\n```yaml\n" + plan + "\n```" },
      ]);
      const parsed = yaml.load(plan) as { project?: { pipeline?: Pipeline } };
      if (parsed?.project?.pipeline) {
        setPipeline(parsed.project.pipeline);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "system", content: `Error generating plan: ${String(err)}` },
      ]);
    } finally {
      setIsPlanning(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      handleSend();
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>JakeFSD</h1>
        <p className="tagline">Design with AI, run deterministically.</p>
        <nav className="tabs">
          <button
            className={activeTab === "chat" ? "active" : ""}
            onClick={() => setActiveTab("chat")}
          >
            Chat
          </button>
          <button
            className={activeTab === "canvas" ? "active" : ""}
            onClick={() => setActiveTab("canvas")}
          >
            Canvas
          </button>
          <button
            className={activeTab === "preview" ? "active" : ""}
            onClick={() => setActiveTab("preview")}
          >
            Preview
          </button>
        </nav>
        <div className="runtime-info">
          <strong>Runtime</strong>
          <span>{pythonVersion}</span>
        </div>
      </aside>
      <main className="main-content">
        {activeTab === "chat" && (
          <div className="chat-pane">
            <div className="messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="bubble">
                    {msg.role === "assistant" ? <pre>{msg.content}</pre> : msg.content}
                  </div>
                </div>
              ))}
              {isPlanning && (
                <div className="message assistant">
                  <div className="bubble">Thinking...</div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="input-bar">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe your pipeline..."
                disabled={isPlanning}
              />
              <button onClick={handleSend} disabled={isPlanning || !input.trim()}>
                Send
              </button>
            </div>
          </div>
        )}
        {activeTab === "canvas" && (
          <div className="canvas-pane">
            {pipeline ? (
              <Canvas pipeline={pipeline} />
            ) : (
              <div className="empty-state">
                Ask the assistant to generate a pipeline first.
              </div>
            )}
          </div>
        )}
        {activeTab === "preview" && (
          <div className="empty-state">Preview pane coming in the next update.</div>
        )}
      </main>
    </div>
  );
}

export default App;
