# -*- coding: utf-8 -*-
"""
ทดสอบว่า YOLO ตรวจจับลูกบอลของเราได้ไหม (คลาส 32 = sports ball)
รันแล้วชูลูกบอลให้กล้องเห็น กด q เพื่อออก
ถ้าเห็นกรอบเขียว + ตัวเลข confidence = ใช้ได้
"""
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
SPORTS_BALL = 32

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # conf ต่ำหน่อย (0.25) เพื่อดูว่ามันพอเห็นบ้างไหม
    results = model(frame, classes=[SPORTS_BALL], conf=0.25, verbose=False)

    found = 0
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ball {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        found += 1

    cv2.putText(frame, f"detected: {found}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("YOLO Ball Test - press q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
