import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Users() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  const token = localStorage.getItem("token");

  const loadUsers = async () => {
    try {
      const res = await fetch("http://localhost:8000/users", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        setError("โหลดข้อมูลไม่สำเร็จ");
        return;
      }
      setUsers(await res.json());
    } catch {
      setError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleDelete = async (user) => {
    if (!window.confirm(`ยืนยันลบบัญชี ${user.username}?`)) return;

    const res = await fetch(`http://localhost:8000/users/${user.id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "ลบไม่สำเร็จ");
      return;
    }
    loadUsers();
  };

  const roleText = { admin: "ผู้ดูแลระบบ", supervisor: "หัวหน้าแผนก" };

  return (
    <>
      <div className="page-header">
        <span className="page-title">จัดการผู้ใช้งาน</span>
        <Link to="/users/new" className="add-btn">+ เพิ่มผู้ใช้งาน</Link>
      </div>

      {error && <div className="login-error">{error}</div>}

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ชื่อผู้ใช้งาน</th>
              <th>สิทธิ์</th>
              <th>แผนกที่รับผิดชอบ</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>
                  <span className={`badge ${u.role === "admin" ? "exceeded" : "normal"}`}>
                    {roleText[u.role] || u.role}
                  </span>
                </td>
                <td>{u.dept || "ทุกแผนก"}</td>
                <td>
                  <button className="delete-btn" onClick={() => handleDelete(u)}>
                    ลบ
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Users;
