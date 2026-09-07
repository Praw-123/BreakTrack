import { useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";

const HAT_COLORS = ["แดง", "น้ำเงิน", "เขียว", "เหลือง", "ชมพู", "ส้ม", "ฟ้า", "ม่วง"];

function EditEmployee() {
  const { employee_id } = useParams();
  const location = useLocation();
  const existing = location.state?.employee;
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: existing?.name || "",
    dept: existing?.dept || "แผนก A",
    hat_color: existing?.hat_color || "แดง",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const res = await fetch(`http://localhost:8000/employees/${employee_id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "แก้ไขไม่สำเร็จ");
        return;
      }

      setSuccess("แก้ไขสำเร็จ");
      setTimeout(() => navigate("/employees"), 800);
    } catch (err) {
      setError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
    }
  };

  if (!existing) {
    return (
      <div className="page-header">
        <span className="page-title">ไม่พบข้อมูลพนักงาน กรุณากลับไปหน้ารายชื่อแล้วกดแก้ไขใหม่</span>
      </div>
    );
  }

  return (
    <>
      <div className="page-header">
        <span className="page-title">แก้ไขพนักงาน: {employee_id}</span>
      </div>

      <form className="add-employee-form" onSubmit={handleSubmit}>
        {error && <div className="login-error">{error}</div>}
        {success && <div className="form-success">{success}</div>}

        <label>รหัสพนักงาน (แก้ไขไม่ได้)</label>
        <input value={employee_id} disabled />

        <label>ชื่อ-สกุล</label>
        <input name="name" value={form.name} onChange={handleChange} required />

        <label>แผนก</label>
        <select name="dept" value={form.dept} onChange={handleChange}>
          <option value="แผนก A">แผนก A</option>
          <option value="แผนก B">แผนก B</option>
        </select>

        <label>สีหมวก</label>
        <select name="hat_color" value={form.hat_color} onChange={handleChange}>
          {HAT_COLORS.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <button type="submit">บันทึกการแก้ไข</button>
      </form>
    </>
  );
}

export default EditEmployee;
