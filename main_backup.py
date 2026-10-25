
import cv2
import mediapipe as mp
import pyautogui
import math
import time

# Mouse settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

SCREEN_W, SCREEN_H = pyautogui.size()
CAM_W, CAM_H = 640, 480

SMOOTHING = 3
PINCH_THRESHOLD = 0.45
CLICK_COOLDOWN = 0.5

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)

if not camera.isOpened():
    print("ERROR: Webcam not available.")
    hands.close()
    raise SystemExit(1)

smooth_x = SCREEN_W / 2
smooth_y = SCREEN_H / 2

left_was_pinched = False
right_was_pinched = False
last_click_time = 0


def distance(a, b):
    dx = (a.x - b.x) * CAM_W
    dy = (a.y - b.y) * CAM_H
    return math.hypot(dx, dy)


print("\nHAND GESTURE MOUSE STARTED")
print("Index finger = Move cursor")
print("Thumb + index = Left click")
print("Thumb + middle = Right click")
print("Press Q in camera window to quit")

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Cannot read webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (CAM_W, CAM_H))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        status = "SHOW YOUR HAND"

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            mp_draw.draw_landmarks(
                frame, hand, mp_hands.HAND_CONNECTIONS
            )

            thumb = lm[4]
            index = lm[8]
            middle = lm[12]

            # Scale pinch distance using palm width
            palm_width = max(distance(lm[5], lm[17]), 1)

            left_ratio = distance(thumb, index) / palm_width
            right_ratio = distance(thumb, middle) / palm_width

            left_pinched = left_ratio < PINCH_THRESHOLD
            right_pinched = right_ratio < PINCH_THRESHOLD

            now = time.time()

            # Click once when a pinch begins
            if now - last_click_time >= CLICK_COOLDOWN:

                if (
                    right_pinched
                    and not right_was_pinched
                    and right_ratio < left_ratio
                ):
                    pyautogui.click(button="right")
                    status = "RIGHT CLICK"
                    last_click_time = now

                elif (
                    left_pinched
                    and not left_was_pinched
                    and left_ratio <= right_ratio
                ):
                    pyautogui.click(button="left")
                    status = "LEFT CLICK"
                    last_click_time = now

            # Move cursor when index finger is raised
            index_up = lm[8].y < lm[6].y

            if index_up and not left_pinched and not right_pinched:
                target_x = index.x * (SCREEN_W - 1)
                target_y = index.y * (SCREEN_H - 1)

                smooth_x += (target_x - smooth_x) / SMOOTHING
                smooth_y += (target_y - smooth_y) / SMOOTHING

                cursor_x = max(
                    1, min(SCREEN_W - 2, int(smooth_x))
                )
                cursor_y = max(
                    1, min(SCREEN_H - 2, int(smooth_y))
                )

                pyautogui.moveTo(
                    cursor_x, cursor_y, _pause=False
                )
                status = "MOVE"

            elif status == "SHOW YOUR HAND":
                status = "READY"

            # Display pinch values for debugging
            cv2.putText(
                frame,
                f"L: {left_ratio:.2f}  R: {right_ratio:.2f}",
                (10, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            left_was_pinched = left_pinched
            right_was_pinched = right_pinched

        else:
            left_was_pinched = False
            right_was_pinched = False

        cv2.rectangle(
            frame, (0, 0), (CAM_W, 55), (30, 30, 30), -1
        )

        cv2.putText(
            frame,
            status,
            (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("Hand Gesture Mouse", frame)

        key = cv2.waitKey(1) & 0xFF

        if key in (ord("q"), ord("Q")):
            break

finally:
    camera.release()
    hands.close()
    cv2.destroyAllWindows()
    print("Hand Gesture Mouse stopped.")
