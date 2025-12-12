import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { TaupyClient } from "./taupyClient";

function App() {
  const [sentCount, setSentCount] = useState(0);

  const client = useMemo(() => new TaupyClient(), []);

  useEffect(() => {
    client.connect();

    return () => {
      client.close();
    };
  }, [client]);

  const sendSampleEvent = () => {
    setSentCount((current) => {
      const next = current + 1;
      client.send({ type: "click", id: "taupy-sample", value: next });
      console.log("[TauPy] Sent test event", { count: next });
      return next;
    });
  };

  return (
    <div className="app">
      <main className="panel">
        <h1>React starter</h1>
        <p>Edit `src/App.tsx` and keep this window open to see updates instantly.</p>

        <div className="grid">
          <div>
            <div className="label">Events sent</div>
            <div className="value">{sentCount}</div>
          </div>
        </div>

        <div className="actions">
          <button type="button" onClick={sendSampleEvent}>
            Send test event
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
