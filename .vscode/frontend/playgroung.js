import React, { useState } from "react";
import axios from "axios";
import "./playground.css";

function Playground() {

  const [code, setCode] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);

  const runCode = async () => {

    if (!code.trim()) {
      alert("Please enter code");
      return;
    }

    setLoading(true);
    setOutput("Running...");

    try {

      const response = await axios.post(
        "http://127.0.0.1:5000/run",
        { code: code }
      );

      const result = response.data.result;
      let outputText = "";
      
      if (result.stdout) {
        outputText += `Output:\n${result.stdout}`;
      }
      
      if (result.stderr) {
        outputText += (outputText ? "\n" : "") + `Errors:\n${result.stderr}`;
      }
      
      if (!result.stdout && !result.stderr) {
        outputText = "(No output)";
      }
      
      outputText += `\n\nExit Code: ${result.returncode}`;
      
      setOutput(outputText);

    } catch (error) {
      setOutput(`Execution Error: ${error.message}`);
    }

    setLoading(false);
  };

  return (
    <div className="playground">

      <h2>⚡ Live Code Playground</h2>

      <textarea
        className="code-editor"
        placeholder="Write or paste Python code here..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />

      <button onClick={runCode} className="run-btn" disabled={loading}>
        {loading ? "⏳ Running..." : "▶ Run Code"}
      </button>

      <div className="output-box">
        <h3>📟 Output</h3>
        <pre>{output || "Run code to see output here..."}</pre>
      </div>

    </div>
  );
}

export default Playground;

