from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from datetime import datetime
import time
from fastapi.responses import StreamingResponse
from fastapi import Depends, Header
import cv2
import config
from detector import find_employee_balls, put_thai_text
from database import SessionLocal
from models import Employee, User
from auth import verify_password, create_access_token, decode_access_token, hash_password



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
            "status": "normal",
        }
        for r in rows
    ]
    db.close()
    return result


employees = load_employees()
latest_frame = None

# เวลาที่เห็นพนักงานแต่ละคนครั้งล่าสุด {employee_id: datetime}
# เก็บแยกจาก employees เพราะ employees ถูกส่งเป็น JSON ผ่าน WebSocket
# ซึ่งแปลง datetime ไม่ได้
last_seen = {}


async def camera_loop():
    """จับภาพ 20 fps เพื่อความลื่น แต่ตรวจจับสีทุก 1 วินาที เพื่อไม่เปลืองเครื่อง"""
    global latest_frame
    cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)

    frame_count = 0
    last_balls = []

    while True:
        ret, frame = cap.read()

        if ret:
            frame_count += 1

            # ---------- ตรวจจับทุก 20 เฟรม (~1 วินาที) ----------
            if frame_count % 20 == 0:
                last_balls = find_employee_balls(frame)
                detected_colors = {b["color"] for b in last_balls}

                now = datetime.now()

                for emp in employees:
                    if emp["hat_color"] in detected_colors:
                        eid = emp["employee_id"]
                        prev = last_seen.get(eid)

                        # ---------- กันโกง: แยกรอบการพัก ----------
                        # หายไปจากกล้องนานเกินเกณฑ์ = ถือเป็นรอบพักใหม่ เริ่มนับจาก 0
                        # ถ้าหายไปไม่นาน (เดินออกแล้วรีบกลับ) = รอบเดิม นับต่อ
                        if prev is not None:
                            gap = (now - prev).total_seconds() / 60 * config.TIME_SCALE
                            if gap > config.SESSION_GAP_MINUTES:
                                emp["break_minutes"] = 0

                        last_seen[eid] = now

                        # 1 รอบ = 1 วินาทีจริง คูณด้วยตัวเร่งเวลาสำหรับสาธิต
                        emp["break_minutes"] += (1 / 60) * config.TIME_SCALE

                        if emp["break_minutes"] >= config.MAX_BREAK_MINUTES:
                            emp["status"] = "exceeded"
                        elif emp["break_minutes"] >= config.WARNING_MINUTES:
                            emp["status"] = "warning"
                        else:
                            emp["status"] = "normal"
                    else:
                        # ---------- กันโกง: ไม่เจอในเฟรมนี้ ----------
                        # ถ้าสถานะเป็น "เกินเวลา" ไม่รีเซ็ตเอง ต้องรอหัวหน้ากด "รับทราบ"
                        # กันไม่ให้แจ้งเตือนหายไปเองก่อนหัวหน้าจะทันเห็น
                        eid = emp["employee_id"]
                        prev = last_seen.get(eid)
                        if prev is not None and emp["status"] != "exceeded":
                            gap = (now - prev).total_seconds() / 60 * config.TIME_SCALE
                            if gap > config.SESSION_GAP_MINUTES:
                                emp["break_minutes"] = 0
                                emp["status"] = "normal"
                                del last_seen[eid]
            # ---------- วาดกรอบจากผลตรวจล่าสุด (ทุกเฟรม) ----------
            for ball in last_balls:
                x1, y1, x2, y2 = ball["box"]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                frame = put_thai_text(frame, ball["color"], (x1, max(y1 - 30, 0)))

            latest_frame = frame

        await asyncio.sleep(0.05)   # 20 fps



@app.on_event("startup")
async def start_camera():
    asyncio.create_task(camera_loop())
def generate_frames():
    """แปลงเฟรมล่าสุดเป็นภาพ JPEG ส่งออกแบบ stream ต่อเนื่อง"""
    while True:
        if latest_frame is not None:
            _, buffer = cv2.imencode(".jpg", latest_frame)
            frame_bytes = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        time.sleep(0.05)


@app.get("/video_feed")
def video_feed(token: str = Query(None)):
    try:
        decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบก่อน")

    return StreamingResponse(
        generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame"
    )



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
        # ---------- กรองข้อมูลตามสิทธิ์ (ของเดิม) ----------
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

# ---------- ตรวจสอบสิทธิ์: admin ทุกแผนก / supervisor เฉพาะแผนกตัวเอง ----------
def require_own_dept_or_admin(employee_id: str, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบก่อน")

    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="token ไม่ถูกต้องหรือหมดอายุ")

    if payload.get("role") != "admin":
        emp = next((e for e in employees if e["employee_id"] == employee_id), None)
        if emp is None:
            raise HTTPException(status_code=404, detail="ไม่พบพนักงานคนนี้")
        if emp["dept"] != payload.get("dept"):
            raise HTTPException(status_code=403, detail="รับทราบได้เฉพาะพนักงานในแผนกตนเองเท่านั้น")

    return payload


# ---------- หัวหน้าแผนกกดรับทราบ ปิดรอบแจ้งเตือน ----------
@app.post("/employees/{employee_id}/acknowledge")
def acknowledge_break(
    employee_id: str, current_user: dict = Depends(require_own_dept_or_admin)
):
    emp = next((e for e in employees if e["employee_id"] == employee_id), None)
    if emp is None:
        raise HTTPException(status_code=404, detail="ไม่พบพนักงานคนนี้")

    emp["break_minutes"] = 0
    emp["status"] = "normal"
    last_seen.pop(employee_id, None)

    return {"message": "รับทราบเรียบร้อย"}


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

# ---------- จัดการบัญชีผู้ใช้งาน (เฉพาะ Admin) ----------
class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    dept: str | None = None


@app.get("/users")
def list_users(current_user: dict = Depends(require_admin)):
    db = SessionLocal()
    rows = db.query(User).all()
    result = [
        {"id": u.id, "username": u.username, "role": u.role, "dept": u.dept}
        for u in rows
    ]
    db.close()
    return result


@app.get("/departments/available")
def available_departments(current_user: dict = Depends(require_admin)):
    """คืนเฉพาะแผนกที่ยังไม่มีหัวหน้าแผนก เพื่อไม่ให้เลือกซ้ำ"""
    db = SessionLocal()
    taken = {
        u.dept
        for u in db.query(User).filter(User.role == "supervisor").all()
        if u.dept
    }
    db.close()
    return [d for d in config.DEPARTMENTS if d not in taken]


@app.post("/users")
def create_user(data: UserCreate, current_user: dict = Depends(require_admin)):
    db = SessionLocal()

    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="ชื่อผู้ใช้งานนี้มีอยู่แล้ว")

    if data.role not in ("admin", "supervisor"):
        db.close()
        raise HTTPException(status_code=400, detail="สิทธิ์ต้องเป็น admin หรือ supervisor เท่านั้น")

    # ---------- กติกา: หัวหน้าแผนกได้แผนกละ 1 คนเท่านั้น ----------
    if data.role == "supervisor":
        if not data.dept:
            db.close()
            raise HTTPException(status_code=400, detail="กรุณาเลือกแผนกที่รับผิดชอบ")

        if data.dept not in config.DEPARTMENTS:
            db.close()
            raise HTTPException(status_code=400, detail="ไม่พบแผนกนี้ในระบบ")

        taken = db.query(User).filter(
            User.role == "supervisor", User.dept == data.dept
        ).first()
        if taken:
            db.close()
            raise HTTPException(
                status_code=400,
                detail=f"{data.dept} มีหัวหน้าแผนกอยู่แล้ว (บัญชี {taken.username})",
            )

    new_user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
        dept=data.dept if data.role == "supervisor" else None,
    )
    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "เพิ่มผู้ใช้งานสำเร็จ"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(require_admin)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานคนนี้")

    # กันลบบัญชีตัวเอง จะได้ไม่ล็อกตัวเองออกจากระบบ
    if user.username == current_user.get("sub"):
        db.close()
        raise HTTPException(status_code=400, detail="ไม่สามารถลบบัญชีของตัวเองได้")

    # กันลบ admin คนสุดท้าย จะได้ไม่มีใครดูแลระบบได้เลย
    if user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            db.close()
            raise HTTPException(status_code=400, detail="ต้องมีผู้ดูแลระบบอย่างน้อย 1 บัญชี")

    db.delete(user)
    db.commit()
    db.close()

    return {"message": "ลบผู้ใช้งานสำเร็จ"}
