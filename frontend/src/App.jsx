import { useEffect, useState } from "react";

function App() {
  const [people, setPeople] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data);
      setPeople(data.people);
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      <h1>BreakTrack</h1>
      <p>เปิด Console (F12) เพื่อดูข้อมูล</p>
    </div>
  );
}

export default App;
