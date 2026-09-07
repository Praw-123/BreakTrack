const statusText = { normal: "ปกติ", warning: "ใกล้เกิน", exceeded: "เกินเวลา" };

function Employees({ people }) {
  return (
    <>
      <div className="page-header">
        <span className="page-title">รายชื่อพนักงานในแผนก</span>
        <span className="role-label">(Supervisor) หัวหน้าแผนก A</span>
      </div>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ชื่อ-สกุล</th>
              <th>รหัสพนักงาน</th>
              <th>สีหมวก</th>
              <th>แผนก</th>
              <th>สถานะปัจจุบัน</th>
            </tr>
          </thead>
          <tbody>
            {people.map((p) => (
              <tr key={p.employee_id}>
                <td>{p.name}</td>
                <td>{p.employee_id}</td>
                <td>{p.hat_color}</td>
                <td>{p.dept}</td>
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

export default Employees;
