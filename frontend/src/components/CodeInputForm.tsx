import { useState } from "react";
import { CodeInput } from "../types";

interface CodeInputFormProps {
  initialCode: CodeInput;
  busy: boolean;
  onRunAnalysis: (input: CodeInput) => Promise<void> | void;
}

export function CodeInputForm({ initialCode, busy, onRunAnalysis }: CodeInputFormProps) {
  const [filename, setFilename] = useState(initialCode.filename);
  const [code, setCode] = useState(initialCode.code);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onRunAnalysis({ filename, code });
  };

  return (
    <form className="code-form" onSubmit={handleSubmit}>
      <label htmlFor="filename">Filename</label>
      <input
        id="filename"
        type="text"
        value={filename}
        onChange={(event) => setFilename(event.target.value)}
        disabled={busy}
        required
      />

      <label htmlFor="code">C Source Code</label>
      <textarea
        id="code"
        spellCheck={false}
        value={code}
        onChange={(event) => setCode(event.target.value)}
        disabled={busy}
        rows={12}
        required
      />

      <button type="submit" disabled={busy}>
        {busy ? "Running Analysis..." : "Run Full Analysis"}
      </button>
    </form>
  );
}

