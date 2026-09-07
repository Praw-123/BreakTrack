from database import SessionLocal, Base, engine
from models import User, Employee
from auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ---------- ลบข้อมูลเก่าก่อน (เผื่อรันซ้ำ) ----------
db.query(User).delete()
db.query(Employee).delete()

# ---------- บัญชีผู้ใช้งาน ----------
users = [
    User(username="admin", password_hash=hash_password("admin123"),
         role="admin", dept=None),
    User(username="supervisor_a", password_hash=hash_password("super123"),
         role="supervisor", dept="แผนก A"),
]

# ---------- พนักงาน ----------
employees = [
    Employee(employee_id="EMP-001", name="สมชาย ใจดี", dept="แผนก A", hat_color="แดง"),
    Employee(employee_id="EMP-002", name="ประสิทธิ์ เก่งกล้า", dept="แผนก B", hat_color="น้ำเงิน"),
    Employee(employee_id="EMP-003", name="มาลี พักดี", dept="แผนก A", hat_color="เขียว"),
    Employee(employee_id="EMP-004", name="วิชัย ตรงเวลา", dept="แผนก A", hat_color="เหลือง"),
    Employee(employee_id="EMP-005", name="วัฒนา แจ่มใส", dept="แผนก B", hat_color="ชมพู"),
]

db.add_all(users)
db.add_all(employees)
db.commit()
db.close()

print("seed data inserted")
