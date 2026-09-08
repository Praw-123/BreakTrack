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
        for (h_low, h_high) in ranges:
            lower = np.array([h_low, config.MIN_SATURATION, config.MIN_VALUE])
            upper = np.array([h_high, 255, 255])
            mask |= cv2.inRange(hsv, lower, upper)

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

        balls = find_color_balls(frame)

        for ball in balls:
            cx, cy = ball["center"]
            r = ball["radius"]
            cv2.circle(frame, (cx, cy), r, (255, 0, 255), 2)
            frame = put_thai_text(frame, ball["color"], (max(cx - r, 0), max(cy - r - 28, 0)))

        cv2.imshow("Detector Test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
