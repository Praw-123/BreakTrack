import { useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Overview from "./pages/Overview";
import Employees from "./pages/Employees";
import AddEmployee from "./pages/AddEmployee";
import EditEmployee from "./pages/EditEmployee";
import Notifications from "./pages/Notifications";
import LiveCamera from "./pages/LiveCamera";
import Login from "./pages/Login";
import "./App.css";
import Users from "./pages/Users";
import AddUser from "./pages/AddUser";

function App() {
  const [people, setPeople] = useState([]);
  const [user, setUser] = useState(() => {
    const role = localStorage.getItem("role");
    return role ? { role, dept: localStorage.getItem("dept") } : null;
  });

  useEffect(() => {
    if (!user) return;

    const token = localStorage.getItem("token");
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPeople(data.people);
    };
    return () => ws.close();
  }, [user]);

  const handleLogin = (data) => {
    setUser({ role: data.role, dept: data.dept });
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
  };

  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<Login onLogin={handleLogin} />} />
      </Routes>
    );
  }

  return (
    <div className="app">
      <Sidebar user={user} onLogout={handleLogout} />
      <main className="content">
        <Routes>
          <Route path="/" element={<Overview people={people} user={user} />} />
          <Route path="/employees" element={<Employees people={people} user={user} />} />
          <Route path="/employees/new" element={<AddEmployee />} />
          <Route path="/employees/edit/:employee_id" element={<EditEmployee />} />
          <Route path="/notifications" element={<Notifications people={people} user={user} />} />
          <Route path="/camera" element={<LiveCamera />} />
          <Route path="/users" element={<Users />} />
          <Route path="/users/new" element={<AddUser />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
