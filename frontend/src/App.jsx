import { useEffect, useState } from "react";

function App() {
  const [people, setPeople] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPeople(data.people);
    };

    return () => ws.close();
  }, []);

  const statusColor = {
    normal: "#e8f5e9",
    warning: "#fff8e1",
    exceeded: "#ffebee",
  };

  const statusText = {
    normal: "ปกติ",
    warning: "ใกล้เกิน",
    exceeded: "เกินเวลา",
  };

  const alertList = people.filter((p) => p.status === "exceeded");

  return (
    <div style={{ fontFamily: "sans-serif", padding: "24px" }}>
      <h1>BreakTrack</h1>

      {alertList.length > 0 && (
        <div style={{ background: "#f44336", color: "white", padding: "12px", borderRadius: "8px", marginBottom: "16px" }}>
          ⚠️ พนักงานพักเกินเวลา: {alertList.map((p) => p.name).join(", ")}
        </div>
      )}

      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: "8px" }}>ชื่อ</th>
            <th style={{ textAlign: "left", padding: "8px" }}>แผนก</th>
            <th style={{ textAlign: "left", padding: "8px" }}>เวลาพักสะสม (นาที)</th>
            <th style={{ textAlign: "left", padding: "8px" }}>สถานะ</th>
          </tr>
        </thead>
        <tbody>
          {people.map((p) => (
            <tr key={p.employee_id} style={{ background: statusColor[p.status] }}>
              <td style={{ padding: "8px" }}>{p.name}</td>
              <td style={{ padding: "8px" }}>{p.dept}</td>
              <td style={{ padding: "8px" }}>{p.break_minutes.toFixed(1)}</td>
              <td style={{ padding: "8px" }}>{statusText[p.status]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
