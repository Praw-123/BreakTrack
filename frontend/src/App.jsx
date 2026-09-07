import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Overview from "./pages/Overview";
import Employees from "./pages/Employees";
import Notifications from "./pages/Notifications";
import "./App.css";

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

  return (
    <div className="app">
      <Sidebar />
      <main className="content">
        <Routes>
          <Route path="/" element={<Overview people={people} />} />
          <Route path="/employees" element={<Employees people={people} />} />
          <Route path="/notifications" element={<Notifications people={people} />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
