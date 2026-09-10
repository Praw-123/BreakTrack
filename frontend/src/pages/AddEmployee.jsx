import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function AddEmployee() {
  const [form, setForm] = useState({
    employee_id: "",
    name: "",
    dept: "แผนก A",
    hat_color: "",
  });
  const [availableColors, setAvailableColors] = useState([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  // ดึงเฉพาะสีหมวกที่ยังไม่มีใครใช้
  useEffect(() => {
    const loadColors = async () => {
      try {
        const res = await fetch("http://localhost:8000/colors/available", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;

        const colors = await res.json();
        setAvailableColors(colors);
        setForm((f) => ({ ...f, hat_color: colors[0] || "" }));
      } catch {
        setError("โหลดรายชื่อสีหมวกไม่สำเร็จ");
      }
    };
    loadColors();
  }, [token]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const noColorLeft = availableColors.length === 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const res = await fetch("http://localhost:8000/employees", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
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
        {noColorLeft ? (
          <div className="login-error">
            สีหมวกถูกใช้ครบทุกสีแล้ว (8 สี) ไม่สามารถเพิ่มพนักงานใหม่ได้
            กรุณาลบพนักงานเดิมก่อน หรือเปลี่ยนไปใช้วิธีระบุตัวตนอื่น
          </div>
        ) : (
          <select name="hat_color" value={form.hat_color} onChange={handleChange}>
            {availableColors.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        )}

        <button type="submit" disabled={noColorLeft}>บันทึก</button>
      </form>
    </>
  );
}

export default AddEmployee;
