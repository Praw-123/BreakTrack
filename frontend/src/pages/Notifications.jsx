function Notifications({ people }) {
  const alerts = people
    .filter((p) => p.status !== "normal")
    .sort((a, b) => b.break_minutes - a.break_minutes);

  return (
    <>
      <div className="page-header">
        <span className="page-title">การแจ้งเตือนทั้งหมด</span>
        <span className="role-label">(Supervisor) หัวหน้าแผนก A</span>
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
          </div>
        ))}
      </div>
    </>
  );
}

export default Notifications;
