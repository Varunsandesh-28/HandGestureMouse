
import cv2
import mediapipe as mp
import pyautogui
import math
import time

# ==========================================
# SETTINGS
# ==========================================

CAM_W = 640
CAM_H = 480

SMOOTHING = 0.25
ZOOM_IN_RATIO = 1.15
ZOOM_OUT_RATIO = 0.87
ZOOM_COOLDOWN = 1.0

DRAG_PINCH_RATIO = 0.35
RIGHT_CLICK_RATIO = 0.35

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

SCREEN_W, SCREEN_H = pyautogui.size()

# ==========================================
# WINDOWS MAGNIFIER
# ==========================================

def magnifier_zoom_in():
    try:
        pyautogui.hotkey("win", "+")
        time.sleep(0.1)
    except Exception as e:
        print("Zoom-in shortcut failed:", e)


def magnifier_zoom_out():
    try:
        pyautogui.hotkey("win", "-")
        time.sleep(0.1)
    except Exception as e:
        print("Zoom-out shortcut failed:", e)


# IMPORTANT:
# Open Magnifier manually before starting:
# Press Windows + Plus (+).


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def distance(a, b):
    dx = (a.x - b.x) * CAM_W
    dy = (a.y - b.y) * CAM_H
    return math.hypot(dx, dy)


def is_finger_up(lm, tip, pip):
    return lm[tip].y < lm[pip].y


def get_finger_states(lm):
    thumb_open = distance(lm[4], lm[2]) > 35
    index_up = is_finger_up(lm, 8, 6)
    middle_up = is_finger_up(lm, 12, 10)
    ring_up = is_finger_up(lm, 16, 14)
    pinky_up = is_finger_up(lm, 20, 18)

    return (
        thumb_open,
        index_up,
        middle_up,
        ring_up,
        pinky_up
    )


# ==========================================
# MEDIAPIPE SETUP
# ==========================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.65,
    min_tracking_confidence=0.65
)

# ==========================================
# WEBCAM SETUP
# ==========================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)

if not cap.isOpened():
    hands.close()
    raise SystemExit(
        "Webcam could not be opened. Check your camera."
    )

print("Hand Gesture Mouse started!")
print("Open Magnifier using Windows + Plus.")
print("Press Q in the camera window to quit.")

# ==========================================
# STATE VARIABLES
# ==========================================

prev_x = SCREEN_W / 2
prev_y = SCREEN_H / 2

dragging = False
right_pinching = False

zoom_mode = None
zoom_baseline = None
last_zoom_time = 0

# ==========================================
# MAIN LOOP
# ==========================================

try:
    while True:
        success, frame = cap.read()

        if not success:
            print("Could not read webcam frame.")
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (CAM_W, CAM_H))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        label = "NO HAND - cursor stopped"
        hand_size = 0

        # ----------------------------------
        # HAND DETECTED
        # ----------------------------------

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            hand_size = distance(lm[0], lm[9])

            (
                thumb_open,
                index_up,
                middle_up,
                ring_up,
                pinky_up
            ) = get_finger_states(lm)

            open_palm = all([
                thumb_open,
                index_up,
                middle_up,
                ring_up,
                pinky_up
            ])

            closed_fist = not any([
                thumb_open,
                index_up,
                middle_up,
                ring_up,
                pinky_up
            ])

            # ==============================
            # ZOOM IN: OPEN PALM MOVES CLOSER
            # ==============================

            if open_palm:
                label = "OPEN PALM - move closer"

                if zoom_mode != "open":
                    zoom_mode = "open"
                    zoom_baseline = hand_size

                elif (
                    zoom_baseline is not None
                    and hand_size >= zoom_baseline * ZOOM_IN_RATIO
                    and time.time() - last_zoom_time
                    >= ZOOM_COOLDOWN
                ):
                    magnifier_zoom_in()
                    last_zoom_time = time.time()
                    zoom_baseline = hand_size
                    label = "ZOOM IN"

            # ==============================
            # ZOOM OUT: FIST MOVES AWAY
            # ==============================

            elif closed_fist:
                label = "FIST - move away"

                if zoom_mode != "fist":
                    zoom_mode = "fist"
                    zoom_baseline = hand_size

                elif (
                    zoom_baseline is not None
                    and hand_size <= zoom_baseline * ZOOM_OUT_RATIO
                    and time.time() - last_zoom_time
                    >= ZOOM_COOLDOWN
                ):
                    magnifier_zoom_out()
                    last_zoom_time = time.time()
                    zoom_baseline = hand_size
                    label = "ZOOM OUT"

            # ==============================
            # MOUSE CONTROL
            # ==============================

            else:
                zoom_mode = None
                zoom_baseline = None

                palm_width = max(
                    distance(lm[5], lm[17]),
                    1
                )

                thumb_index = distance(lm[4], lm[8])
                thumb_middle = distance(lm[4], lm[12])

                index_pinch = (
                    thumb_index / palm_width
                    < DRAG_PINCH_RATIO
                )

                middle_pinch = (
                    thumb_middle / palm_width
                    < RIGHT_CLICK_RATIO
                )

                # Right click once per pinch
                if middle_pinch and not right_pinching:
                    pyautogui.click(button="right")
                    label = "RIGHT CLICK"

                right_pinching = middle_pinch

                # Left pinch: drag and drop
                if index_pinch and not dragging:
                    pyautogui.mouseDown(button="left")
                    dragging = True
                    label = "DRAGGING"

                elif not index_pinch and dragging:
                    pyautogui.mouseUp(button="left")
                    dragging = False
                    label = "DROP"

                # Move cursor using index fingertip
                target_x = int(lm[8].x * SCREEN_W)
                target_y = int(lm[8].y * SCREEN_H)

                smooth_x = (
                    prev_x
                    + (target_x - prev_x) * SMOOTHING
                )

                smooth_y = (
                    prev_y
                    + (target_y - prev_y) * SMOOTHING
                )

                pyautogui.moveTo(
                    int(smooth_x),
                    int(smooth_y)
                )

                prev_x = smooth_x
                prev_y = smooth_y

            # Debug information
            cv2.putText(
                frame,
                label,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Hand size: {hand_size:.1f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 0),
                2
            )

            if zoom_baseline is not None:
                cv2.putText(
                    frame,
                    f"Baseline: {zoom_baseline:.1f}",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 0),
                    2
                )

        # ----------------------------------
        # NO HAND DETECTED
        # ----------------------------------

        else:
            zoom_mode = None
            zoom_baseline = None
            right_pinching = False

            if dragging:
                pyautogui.mouseUp(button="left")
                dragging = False

            cv2.putText(
                frame,
                "NO HAND - cursor stopped",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        # Show webcam window
        cv2.imshow("Hand Gesture Mouse", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    if dragging:
        pyautogui.mouseUp(button="left")

    hands.close()
    cap.release()
    cv2.destroyAllWindows()

    print("Hand Gesture Mouse stopped.")
