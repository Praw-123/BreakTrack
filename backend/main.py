from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

employees = [
    {"employee_id": "EMP-001", "name": "สมชาย ใจดี", "dept": "แผนก A",
     "hat_color": "แดง", "break_minutes": 0},
    {"employee_id": "EMP-002", "name": "ประสิทธิ์ เก่งกล้า", "dept": "แผนก B",
     "hat_color": "น้ำเงิน", "break_minutes": 0},
]

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
