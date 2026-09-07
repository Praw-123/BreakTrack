import { Link } from "react-router-dom";

const statusText = { normal: "ปกติ", warning: "ใกล้เกิน", exceeded: "เกินเวลา" };

function Employees({ people, user }) {
  const handleDelete = async (employee_id) => {
    if (!window.confirm(`ยืนยันลบพนักงาน ${employee_id}?`)) return;

    const res = await fetch(`http://localhost:8000/employees/${employee_id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });

    if (!res.ok) {
      alert("ลบไม่สำเร็จ");
    }
  };

  return (
    <>
      <div className="page-header">
        <span className="page-title">รายชื่อพนักงานในแผนก</span>
        {user.role === "admin" && (
          <Link to="/employees/new" className="add-btn">+ เพิ่มพนักงาน</Link>
        )}
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
              {user.role === "admin" && <th>จัดการ</th>}
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
                {user.role === "admin" && (
                  <td className="action-cell">
                    <Link
                      to={`/employees/edit/${p.employee_id}`}
                      state={{ employee: p }}
                      className="edit-btn"
                    >
                      แก้ไข
                    </Link>
                    <button className="delete-btn" onClick={() => handleDelete(p.employee_id)}>
                      ลบ
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Employees;
