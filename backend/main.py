from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from datetime import datetime

from fastapi import Depends, Header
from database import SessionLocal
from models import Employee, User
from auth import verify_password, create_access_token, decode_access_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- โหลดพนักงานจากฐานข้อมูลตอนเริ่มเซิร์ฟเวอร์ ----------
def load_employees():
    db = SessionLocal()
    rows = db.query(Employee).all()
    result = [
        {
            "employee_id": r.employee_id,
            "name": r.name,
            "dept": r.dept,
            "hat_color": r.hat_color,
            "break_minutes": 0,
        }
        for r in rows
    ]
    db.close()
    return result


employees = load_employees()


# ---------- Login ----------
class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == data.username).first()
    db.close()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="username หรือ password ไม่ถูกต้อง")

    token = create_access_token(
        {"sub": user.username, "role": user.role, "dept": user.dept}
    )
    return {"access_token": token, "role": user.role, "dept": user.dept}


# ---------- WebSocket (ของเดิม ไม่เปลี่ยน) ----------
@app.websocket("/ws")
async def break_status(websocket: WebSocket, token: str = Query(None)):
    try:
        token_data = decode_access_token(token)
    except Exception:
        await websocket.close(code=1008)  # 1008 = Policy Violation
        return

    await websocket.accept()
    user_role = token_data.get("role")
    user_dept = token_data.get("dept")

    while True:
        for emp in employees:
            emp["break_minutes"] += 0.2

            if emp["break_minutes"] >= 15:
                emp["status"] = "exceeded"
            elif emp["break_minutes"] >= 12:
                emp["status"] = "warning"
            else:
                emp["status"] = "normal"

        # ---------- กรองข้อมูลตามสิทธิ์ ----------
        if user_role == "admin":
            visible_employees = employees
        else:
            visible_employees = [e for e in employees if e["dept"] == user_dept]

        payload = {
            "timestamp": datetime.now().isoformat(),
            "people": visible_employees,
        }

        await websocket.send_json(payload)
        await asyncio.sleep(1)

# ---------- ตรวจสอบสิทธิ์ Admin ----------
def require_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบก่อน")

    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="token ไม่ถูกต้องหรือหมดอายุ")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="ต้องเป็นผู้ดูแลระบบเท่านั้น")

    return payload


# ---------- เพิ่มพนักงานใหม่ ----------
class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    dept: str
    hat_color: str


@app.post("/employees")
def create_employee(data: EmployeeCreate, current_user: dict = Depends(require_admin)):
    db = SessionLocal()

    existing = db.query(Employee).filter(
        Employee.employee_id == data.employee_id
    ).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="รหัสพนักงานนี้มีอยู่แล้ว")

    new_emp = Employee(
        employee_id=data.employee_id,
        name=data.name,
        dept=data.dept,
        hat_color=data.hat_color,
    )
    db.add(new_emp)
    db.commit()
    db.close()

    # เพิ่มเข้ารายการที่ WebSocket ใช้อยู่ด้วย จะได้ขึ้นทันทีไม่ต้องรีสตาร์ทเซิร์ฟเวอร์
    employees.append({
        "employee_id": data.employee_id,
        "name": data.name,
        "dept": data.dept,
        "hat_color": data.hat_color,
        "break_minutes": 0,
        "status": "normal",
    })

    return {"message": "เพิ่มพนักงานสำเร็จ"}

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, current_user: dict = Depends(require_admin)):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        db.close()
        raise HTTPException(status_code=404, detail="ไม่พบพนักงานคนนี้")

    db.delete(emp)
    db.commit()
    db.close()

    global employees
    employees = [e for e in employees if e["employee_id"] != employee_id]

    return {"message": "ลบพนักงานสำเร็จ"}

class EmployeeUpdate(BaseModel):
    name: str
    dept: str
    hat_color: str


@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: str, data: EmployeeUpdate, current_user: dict = Depends(require_admin)
):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        db.close()
        raise HTTPException(status_code=404, detail="ไม่พบพนักงานคนนี้")

    emp.name = data.name
    emp.dept = data.dept
    emp.hat_color = data.hat_color
    db.commit()
    db.close()

    for e in employees:
        if e["employee_id"] == employee_id:
            e["name"] = data.name
            e["dept"] = data.dept
            e["hat_color"] = data.hat_color
            break

    return {"message": "แก้ไขพนักงานสำเร็จ"}

class EmployeeUpdate(BaseModel):
    name: str
    dept: str
    hat_color: str


@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: str, data: EmployeeUpdate, current_user: dict = Depends(require_admin)
):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        db.close()
        raise HTTPException(status_code=404, detail="ไม่พบพนักงานคนนี้")

    emp.name = data.name
    emp.dept = data.dept
    emp.hat_color = data.hat_color
    db.commit()
    db.close()

    for e in employees:
        if e["employee_id"] == employee_id:
            e["name"] = data.name
            e["dept"] = data.dept
            e["hat_color"] = data.hat_color
            break

    return {"message": "แก้ไขพนักงานสำเร็จ"}

