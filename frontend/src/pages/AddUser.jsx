import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function AddUser() {
  const [form, setForm] = useState({
    username: "",
    password: "",
    role: "supervisor",
    dept: "",
  });
  const [availableDepts, setAvailableDepts] = useState([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const token = localStorage.getItem("token");

  // ดึงเฉพาะแผนกที่ยังไม่มีหัวหน้าแผนก
  useEffect(() => {
    const loadDepts = async () => {
      try {
        const res = await fetch("http://localhost:8000/departments/available", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;

        const depts = await res.json();
        setAvailableDepts(depts);
        setForm((f) => ({ ...f, dept: depts[0] || "" }));
      } catch {
        setError("โหลดรายชื่อแผนกไม่สำเร็จ");
      }
    };
    loadDepts();
  }, [token]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const noDeptLeft = availableDepts.length === 0;
  const blocked = form.role === "supervisor" && noDeptLeft;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const res = await fetch("http://localhost:8000/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: form.username,
          password: form.password,
          role: form.role,
          dept: form.role === "supervisor" ? form.dept : null,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "เพิ่มผู้ใช้งานไม่สำเร็จ");
        return;
      }

      setSuccess("เพิ่มผู้ใช้งานสำเร็จ");
      setTimeout(() => navigate("/users"), 800);
    } catch {
      setError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
    }
  };

  return (
    <>
      <div className="page-header">
        <span className="page-title">เพิ่มผู้ใช้งานใหม่</span>
      </div>

      <form className="add-employee-form" onSubmit={handleSubmit}>
        {error && <div className="login-error">{error}</div>}
        {success && <div className="form-success">{success}</div>}

        <label>ชื่อผู้ใช้งาน</label>
        <input name="username" value={form.username} onChange={handleChange} required />

        <label>รหัสผ่าน</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          required
        />

        <label>สิทธิ์การใช้งาน</label>
        <select name="role" value={form.role} onChange={handleChange}>
          <option value="supervisor">หัวหน้าแผนก (Supervisor)</option>
          <option value="admin">ผู้ดูแลระบบ (Admin)</option>
        </select>

        {form.role === "supervisor" && (
          <>
            <label>แผนกที่รับผิดชอบ</label>

            {noDeptLeft ? (
              <div className="login-error">
                ทุกแผนกมีหัวหน้าแผนกครบแล้ว หากต้องการเปลี่ยนตัว
                กรุณาลบบัญชีหัวหน้าแผนกเดิมก่อน
              </div>
            ) : (
              <select name="dept" value={form.dept} onChange={handleChange}>
                {availableDepts.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            )}
          </>
        )}

        <button type="submit" disabled={blocked}>
          บันทึก
        </button>
      </form>
    </>
  );
}

export default AddUser;
