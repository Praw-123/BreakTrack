import { useState } from "react";

function Notifications({ people, user }) {
  const [ackingId, setAckingId] = useState(null);

  const alerts = people
    .filter((p) => p.status !== "normal")
    .sort((a, b) => b.break_minutes - a.break_minutes);

  const roleLabel =
    user.role === "admin" ? "ผู้ดูแลระบบ" : `หัวหน้า${user.dept}`;

  const token = localStorage.getItem("token");

  const handleAcknowledge = async (employeeId) => {
    setAckingId(employeeId);
    try {
      await fetch(`http://localhost:8000/employees/${employeeId}/acknowledge`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      // ไม่ต้องอัปเดต state เอง รอ WebSocket ส่งข้อมูลใหม่มาใน 1 วินาทีถัดไป
    } catch {
      // เงียบไว้ก่อน ถ้าพลาดพนักงานจะยังค้างอยู่ในรายการ กดรับทราบใหม่ได้
    } finally {
      setAckingId(null);
    }
  };

  return (
    <>
      <div className="page-header">
        <span className="page-title">การแจ้งเตือนทั้งหมด</span>
        <span className="role-label">{roleLabel}</span>
      </div>

      <div className="notify-list">
        {alerts.length === 0 && (
          <p className="notify-empty">ยังไม่มีการแจ้งเตือนในขณะนี้</p>
        )}

        {alerts.map((p) => (
          <div className="notify-item" key={p.employee_id}>
            <span className={`dot ${p.status}`}></span>
            <div>
              <div className="notify-title">
                {p.name} พักเกินเวลาที่กำหนด ({p.break_minutes.toFixed(0)} นาที)
              </div>
              <div className="notify-sub">แผนก {p.dept}</div>
            </div>

            {p.status === "exceeded" && (
              <button
                className="ack-btn"
                disabled={ackingId === p.employee_id}
                onClick={() => handleAcknowledge(p.employee_id)}
              >
                {ackingId === p.employee_id ? "กำลังรับทราบ..." : "รับทราบ"}
              </button>
            )}
          </div>
        ))}
      </div>
    </>
  );
}

export default Notifications;
