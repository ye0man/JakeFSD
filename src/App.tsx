import { useState, useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

function App() {
  const [pythonVersion, setPythonVersion] = useState<string>("Checking Python runtime...");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your Chief Data Architect. Describe the pipeline you want to build, and I'll propose a manifest.",
    },
  ]);
  const [input, setInput] = useState<string>("");
  const [isPlanning, setIsPlanning] = useState<boolean>(false);
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
        <div className="runtime-info">
          <strong>Runtime</strong>
          <span>{pythonVersion}</span>
        </div>
      </aside>
      <main className="chat-pane">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="bubble">
                {msg.role === "assistant" ? (
                  <pre>{msg.content}</pre>
                ) : (
                  msg.content
                )}
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
      </main>
    </div>
  );
}

export default App;
