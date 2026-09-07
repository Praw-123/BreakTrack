import { useState } from "react";
import { useNavigate } from "react-router-dom";

const HAT_COLORS = ["แดง", "น้ำเงิน", "เขียว", "เหลือง", "ชมพู", "ส้ม", "ฟ้า", "ม่วง"];

function AddEmployee() {
  const [form, setForm] = useState({
    employee_id: "",
    name: "",
    dept: "แผนก A",
    hat_color: "แดง",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const res = await fetch("http://localhost:8000/employees", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "เพิ่มพนักงานไม่สำเร็จ");
        return;
      }

      setSuccess("เพิ่มพนักงานสำเร็จ");
      setTimeout(() => navigate("/employees"), 800);
    } catch (err) {
      setError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
    }
  };

  return (
    <>
      <div className="page-header">
        <span className="page-title">เพิ่มพนักงานใหม่</span>
      </div>

      <form className="add-employee-form" onSubmit={handleSubmit}>
        {error && <div className="login-error">{error}</div>}
        {success && <div className="form-success">{success}</div>}

        <label>รหัสพนักงาน</label>
        <input
          name="employee_id"
          value={form.employee_id}
          onChange={handleChange}
          placeholder="เช่น EMP-006"
          required
        />

        <label>ชื่อ-สกุล</label>
        <input
          name="name"
          value={form.name}
          onChange={handleChange}
          placeholder="เช่น อรุณ ทองดี"
          required
        />

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

        <button type="submit">บันทึก</button>
      </form>
    </>
  );
}

export default AddEmployee;
