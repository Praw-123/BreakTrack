const statusText = { normal: "ปกติ", warning: "ใกล้เกิน", exceeded: "เกินเวลา" };

function Overview({ people }) {
  const alertList = people.filter((p) => p.status === "exceeded");
  const deptCount = new Set(people.map((p) => p.dept)).size;
  const avgMinutes =
    people.length > 0
      ? (people.reduce((s, p) => s + p.break_minutes, 0) / people.length).toFixed(1)
      : 0;

  return (
    <>
      <div className="page-header">
        <span className="page-title">ภาพรวมทั้งหมด</span>
        <span className="role-label">(Supervisor) หัวหน้าแผนก A</span>
      </div>

      {alertList.length > 0 && (
        <div className="alert-banner">
          ⚠️ พนักงานพักเกินเวลา: {alertList.map((p) => p.name).join(", ")}
        </div>
      )}

      <div className="summary-row">
        <div className="summary-card">
          <div className="label">พนักงานในพื้นที่พัก</div>
          <div className="value">{people.length} คน</div>
        </div>
        <div className="summary-card">
          <div className="label">แจ้งเตือนตอนนี้</div>
          <div className="value">{alertList.length} รายการ</div>
        </div>
        <div className="summary-card">
          <div className="label">เวลาพักเฉลี่ย</div>
          <div className="value">{avgMinutes} นาที</div>
        </div>
        <div className="summary-card">
          <div className="label">แผนกที่ดูแล</div>
          <div className="value">{deptCount} แผนก</div>
        </div>
      </div>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ชื่อ</th>
              <th>แผนก</th>
              <th>เวลาพักสะสม</th>
              <th>สถานะ</th>
            </tr>
          </thead>
          <tbody>
            {people.map((p) => (
              <tr key={p.employee_id}>
                <td>{p.name}</td>
                <td>{p.dept}</td>
                <td>{p.break_minutes.toFixed(1)} นาที</td>
                <td>
                  <span className={`badge ${p.status}`}>{statusText[p.status]}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Overview;
