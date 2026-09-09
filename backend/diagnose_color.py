# -*- coding: utf-8 -*-
"""
เครื่องมือวินิจฉัย: ดูว่าทำไมตรวจจับไม่ติด
แสดงค่าจริงทุกอย่าง -> YOLO เห็นไหม, ค่าสีเท่าไหร่, แต่ละสีได้สัดส่วนเท่าไหร่

รันแล้วชูลูกบอล กด q เพื่อออก
"""
import cv2
import numpy as np
from ultralytics import YOLO

import config

model = YOLO(config.YOLO_MODEL)
cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)

print("=" * 70)
print("กด q ที่หน้าต่างภาพเพื่อออก")
print("=" * 70)

frame_no = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_no += 1

    results = model(
        frame,
        classes=[config.SPORTS_BALL_CLASS_ID],
        conf=0.10,          # ตั้งต่ำมาก เพื่อดูว่า YOLO เห็นบ้างไหม
        verbose=False,
    )

    boxes = results[0].boxes
    y_text = 30
    cv2.putText(frame, f"YOLO found: {len(boxes)}", (10, y_text),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])

        region = frame[max(y1, 0):y2, max(x1, 0):x2]
        if region.size == 0:
            continue

        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

        # ค่าเฉลี่ยตรงกลางลูกบอล (เลี่ยงขอบที่มีพื้นหลังปน)
        h_c, w_c = hsv.shape[:2]
        cy0, cy1 = int(h_c * 0.35), int(h_c * 0.65)
        cx0, cx1 = int(w_c * 0.35), int(w_c * 0.65)
        core = hsv[cy0:cy1, cx0:cx1]
        mean_h = float(np.mean(core[:, :, 0])) if core.size else 0
        mean_s = float(np.mean(core[:, :, 1])) if core.size else 0
        mean_v = float(np.mean(core[:, :, 2])) if core.size else 0

        # คำนวณสัดส่วนของทุกสี
        scores = []
        for color_name, ranges in config.COLOR_RANGES.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for (h_low, h_high) in ranges:
                lower = np.array([h_low, config.MIN_SATURATION, config.MIN_VALUE])
                upper = np.array([h_high, 255, 255])
                mask |= cv2.inRange(hsv, lower, upper)
            ratio = np.count_nonzero(mask) / mask.size
            scores.append((ratio, color_name))

        scores.sort(reverse=True)
        best_ratio, best_color = scores[0]
        passed = best_ratio >= config.MIN_COLOR_RATIO

        # ---------- พิมพ์ลง console ----------
        if frame_no % 10 == 0:
            print(f"\n[frame {frame_no}] YOLO conf={conf:.2f}  box={x2-x1}x{y2-y1}px")
            print(f"   HSV กลางลูกบอล: H={mean_h:.0f}  S={mean_s:.0f}  V={mean_v:.0f}")
            print(f"   เกณฑ์ปัจจุบัน: MIN_SATURATION={config.MIN_SATURATION} "
                  f"MIN_VALUE={config.MIN_VALUE} MIN_COLOR_RATIO={config.MIN_COLOR_RATIO}")
            for r, c in scores[:3]:
                print(f"     {c:<10} ratio={r:.3f}")
            print(f"   ==> {'PASS' if passed else 'FAIL'}  best={best_color} ({best_ratio:.3f})")

        # ---------- วาดบนภาพ ----------
        color_box = (0, 255, 0) if passed else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color_box, 2)
        cv2.putText(frame, f"conf={conf:.2f}", (x1, max(y1 - 30, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_box, 2)
        cv2.putText(frame, f"H={mean_h:.0f} S={mean_s:.0f} V={mean_v:.0f}",
                    (x1, max(y1 - 10, 28)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_box, 2)
        cv2.putText(frame, f"ratio={best_ratio:.2f} {'PASS' if passed else 'FAIL'}",
                    (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_box, 2)

    cv2.imshow("Diagnose - press q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
