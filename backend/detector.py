import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from ultralytics import YOLO

import config

model = YOLO(config.YOLO_MODEL)
FONT = ImageFont.truetype("C:/Windows/Fonts/tahoma.ttf", 22)


def put_thai_text(frame, text, position, color=(0, 255, 0)):
    """วาดข้อความภาษาไทยบนภาพ (cv2.putText วาดภาษาไทยไม่ได้)"""
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    draw.text(position, text, font=FONT, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def find_color_balls(frame):
    """หาลูกบอลสีกลม ๆ ทั่วทั้งเฟรม ไม่ผูกกับตำแหน่งคน"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    balls = []

    for color_name, ranges in config.COLOR_RANGES.items():
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for (lower, upper) in ranges:
            mask |= cv2.inRange(hsv, np.array(lower), np.array(upper))

        # ลบจุดสีเล็ก ๆ รบกวนออก แล้วเติมรูให้ก้อนสีทึบขึ้น
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if area < config.MIN_BALL_AREA:
                continue

            (x, y), radius = cv2.minEnclosingCircle(c)
            circle_area = np.pi * radius * radius
            circularity = area / circle_area if circle_area > 0 else 0

            if circularity >= config.MIN_CIRCULARITY:
                balls.append({
                    "color": color_name,
                    "center": (int(x), int(y)),
                    "radius": int(radius),
                })

    return balls


def read_dominant_color(frame, box):
    """
    อ่านสีเด่นภายในกรอบที่กำหนด
    คืนชื่อสีถ้าตรงกับสีที่ลงทะเบียนไว้ / คืน None ถ้าไม่ตรงสีไหนเลย
    """
    x1, y1, x2, y2 = box
    region = frame[max(y1, 0):y2, max(x1, 0):x2]
    if region.size == 0:
        return None

    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

    best_color = None
    best_ratio = 0.0

    for color_name, ranges in config.COLOR_RANGES.items():
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for (lower, upper) in ranges:
            mask |= cv2.inRange(hsv, np.array(lower), np.array(upper))

        ratio = np.count_nonzero(mask) / mask.size
        if ratio > best_ratio:
            best_ratio = ratio
            best_color = color_name

    # ต้องมีสัดส่วนสีมากพอ ถึงจะเชื่อว่าเป็นสีนั้นจริง
    if best_ratio >= config.MIN_COLOR_RATIO:
        return best_color
    return None


def find_employee_balls(frame):
    """
    หาลูกบอลของพนักงาน ต้องผ่าน 2 เงื่อนไขพร้อมกัน (AND)
      1. YOLO ยืนยันว่าเป็นวัตถุทรงกลม (คลาส sports ball)
      2. สีภายในกรอบนั้นตรงกับสีที่ลงทะเบียนให้พนักงาน

    ถ้าขาดข้อใดข้อหนึ่ง จะไม่ถูกนับ เพื่อป้องกันการตรวจจับผิดพลาด
    ซึ่งอาจทำให้พนักงานถูกแจ้งเตือนโดยไม่เป็นธรรม
    """
    results = model(
        frame,
        classes=[config.SPORTS_BALL_CLASS_ID],
        conf=config.BALL_CONFIDENCE_THRESHOLD,
        verbose=False,
    )

    balls = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # ---------- เงื่อนไขที่ 2: ต้องมีสีตรงกับที่ลงทะเบียนไว้ ----------
        color = read_dominant_color(frame, (x1, y1, x2, y2))
        if color is None:
            continue  # เป็นลูกบอลจริง แต่ไม่ใช่สีของพนักงานคนไหน จึงไม่นับ

        balls.append({
            "color": color,
            "box": (x1, y1, x2, y2),
            "center": ((x1 + x2) // 2, (y1 + y2) // 2),
            "radius": max(x2 - x1, y2 - y1) // 2,
            "confidence": float(box.conf[0]),
        })

    return balls


def detect_people(frame):
    """ตรวจคนด้วย YOLO + จับคู่กับลูกบอลสีที่อยู่ใกล้หัวที่สุด"""
    results = model(frame, classes=[config.PERSON_CLASS_ID],
                     conf=config.CONFIDENCE_THRESHOLD, verbose=False)

    boxes = [tuple(map(int, b.xyxy[0])) for b in results[0].boxes]
    balls = find_color_balls(frame)

    people = []
    for box in boxes:
        x1, y1, x2, y2 = box
        head_x, head_y = (x1 + x2) / 2, y1

        best_color, best_dist = None, float("inf")
        for ball in balls:
            bx, by = ball["center"]
            dist = ((bx - head_x) ** 2 + (by - head_y) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_color = ball["color"]

        people.append({"box": box, "hat_color": best_color})

    return people, balls


if __name__ == "__main__":
    cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        balls = find_employee_balls(frame)

        for ball in balls:
            x1, y1, x2, y2 = ball["box"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f'{ball["color"]}  ({ball["confidence"]:.2f})'
            frame = put_thai_text(frame, label, (x1, max(y1 - 28, 0)))

        cv2.putText(frame, f"employee balls: {len(balls)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Detector Test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
