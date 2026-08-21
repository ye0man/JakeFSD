import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";

function App() {
  const [pythonVersion, setPythonVersion] = useState<string>("Checking Python runtime...");

  useEffect(() => {
    async function checkRuntime() {
      setPythonVersion(await invoke("python_runtime_version"));
    }
    checkRuntime();
  }, []);

  return (
    <main className="container">
      <h1>JakeFSD</h1>
      <p>Open-source, local-first IDE for data pipelines.</p>
      <p>
        <strong>{pythonVersion}</strong>
      </p>
      <p>
        <em>Design with AI, run deterministically.</em>
      </p>
    </main>
  );
}

export default App;
