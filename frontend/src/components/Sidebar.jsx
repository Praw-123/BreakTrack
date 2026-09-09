import { NavLink } from "react-router-dom";

const menu = [
  { to: "/", label: "ภาพรวม" },
  { to: "/employees", label: "รายชื่อพนักงาน" },
  { to: "/camera", label: "กล้องเรียลไทม์" },
  { to: "/notifications", label: "การแจ้งเตือน" },
];


function Sidebar({ user, onLogout }) {
  return (
    <aside className="sidebar">
      <h2>BreakTrack</h2>
      <nav>
        {menu.map((m) => (
          <NavLink
            key={m.to}
            to={m.to}
            end
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            {m.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          {user.role === "admin" ? "ผู้ดูแลระบบ" : `หัวหน้า${user.dept}`}
        </div>
        <button className="logout-btn" onClick={onLogout}>
          ออกจากระบบ
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
