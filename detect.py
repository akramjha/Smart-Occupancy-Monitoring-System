from ultralytics import YOLO
import cv2
from datetime import datetime
import os

# =========================
# CONFIGURATION
# =========================

ALERT_THRESHOLD = 2
CONFIDENCE_THRESHOLD = 0.50
max_people_detected = 0
start_time = datetime.now()
last_screenshot_time = None
LOG_FILE = "logs/detection_log.csv"

# Create folders if they don't exist
os.makedirs("logs", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

# Create CSV log file if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("Timestamp,PeopleCount\n")

# =========================
# LOAD MODEL
# =========================

model = YOLO("yolov8n.pt")

# =========================
# OPEN WEBCAM
# =========================

cap = cv2.VideoCapture(0)

while True:

    # Read webcam frame
    success, frame = cap.read()

    if not success:
        print("Failed to access webcam.")
        break

    # Run YOLO detection
    results = model(frame)

    # Reset people counter
    people_count = 0

    # Process detections
    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])
            confidence = float(box.conf[0])

            label = model.names[cls]

            # Only detect people
            if label == "person" and confidence > CONFIDENCE_THRESHOLD:

                people_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Draw bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                # Display label and confidence
                cv2.putText(
                    frame,
                    f"{label} {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

    max_people_detected = max(
    max_people_detected,
    people_count
    )

    if people_count > ALERT_THRESHOLD:
        status = "CROWDED"
    else:
        status = "NORMAL"

    with open("data.txt", "w") as f:
        f.write(
            f"{people_count},{status},{max_people_detected}"
        )

    # Display people count
    cv2.putText(
        frame,
        f"People Count: {people_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    cv2.putText(
        frame,
        f"Max People: {max_people_detected}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    if people_count <= ALERT_THRESHOLD:
        status = "NORMAL"
        cv2.putText(
            frame,
            f"Status: {status}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,0,255),
            2
        )

    # =========================
    # CROWD ALERT
    # =========================
    if people_count > ALERT_THRESHOLD:
        status = "CROWDED"
        cv2.putText(
            frame,
            f"Status: {status}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        # Save screenshot
        current_time = datetime.now()

        if(
            last_screenshot_time is None
            or
            (current_time - last_screenshot_time).seconds >= 10
        ):
        
            screenshot_time = current_time.strftime(
                "%Y%m%d_%H%M%S"
            )
            screenshot_path = (
                f"screenshots/crowd_{screenshot_time}.jpg"
            )

            cv2.imwrite(screenshot_path, frame)

            last_screenshot_time = current_time

    # =========================
    # LOG DATA
    # =========================

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp},{people_count}\n")

    current_time = datetime.now().strftime("%H: %M: %S")

    cv2.putText(
        frame,
        f"Time: {current_time}",
        (20, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255,255,255),
        2
    )

    cv2.putText(
    frame,
    f"Confidence Threshold: {CONFIDENCE_THRESHOLD * 100:.0f}%",
    (20, 200),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (255, 255, 255),
    2
    )

    runtime_seconds = int(
        (datetime.now() - start_time).total_seconds()
    )

    cv2.putText(
    frame,
    f"Runtime: {runtime_seconds}s",
    (20, 240),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (255, 255, 255),
    2
    )

    # Show video
    cv2.imshow(
        "Occupancy Monitoring System",
        frame
    )

    # Press ESC to exit
    if cv2.waitKey(1) == 27:
        break


# Cleanup
cap.release()
cv2.destroyAllWindows()