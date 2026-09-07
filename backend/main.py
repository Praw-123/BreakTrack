from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from datetime import datetime

from database import SessionLocal
from models import Employee, User
from auth import verify_password, create_access_token

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
async def break_status(websocket: WebSocket):
    await websocket.accept()

    while True:
        for emp in employees:
            emp["break_minutes"] += 0.2

            if emp["break_minutes"] >= 15:
                emp["status"] = "exceeded"
            elif emp["break_minutes"] >= 12:
                emp["status"] = "warning"
            else:
                emp["status"] = "normal"

        payload = {
            "timestamp": datetime.now().isoformat(),
            "people": employees,
        }

        await websocket.send_json(payload)
        await asyncio.sleep(1)
