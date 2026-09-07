import { NavLink } from "react-router-dom";

const menu = [
  { to: "/", label: "ภาพรวม" },
  { to: "/employees", label: "รายชื่อพนักงาน" },
  { to: "/notifications", label: "การแจ้งเตือน" },
];

function Sidebar() {
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
    </aside>
  );
}

export default Sidebar;
