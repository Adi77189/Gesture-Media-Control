import cv2
import mediapipe as mp
import pyautogui
import time

print("Gesture Controlled System Control Started")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# -------- FINGER COUNT FUNCTION -------- #
def count_fingers(hand_landmarks, hand_label):
    lm = hand_landmarks.landmark
    fingers = []

    # Thumb
    if hand_label == "Right":
        fingers.append(1 if lm[4].x > lm[2].x else 0)
    else:
        fingers.append(1 if lm[4].x < lm[2].x else 0)

    # Other fingers
    finger_tips = [8, 12, 16, 20]
    for tip in finger_tips:
        fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

    return fingers.count(1)
# -------------------------------------- #

cap = cv2.VideoCapture(0)

last_action_time = 0
cooldown = 1.2  # seconds (important to avoid spam)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture_text = ""

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):

            hand_label = results.multi_handedness[idx].classification[0].label
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            finger_count = count_fingers(hand_landmarks, hand_label)
            current_time = time.time()

            # -------- GESTURE ACTIONS -------- #
            if finger_count == 5:
                gesture_text = "PLAY / PAUSE"
                if current_time - last_action_time > cooldown:
                    pyautogui.press("playpause")
                    last_action_time = current_time

            elif finger_count == 1:
                gesture_text = "VOLUME UP"
                if current_time - last_action_time > cooldown:
                    pyautogui.press("volumeup")
                    last_action_time = current_time

            elif finger_count == 2:
                gesture_text = "VOLUME DOWN"
                if current_time - last_action_time > cooldown:
                    pyautogui.press("volumedown")
                    last_action_time = current_time

            elif finger_count == 0:
                gesture_text = "MUTE"
                if current_time - last_action_time > cooldown:
                    pyautogui.press("volumemute")
                    last_action_time = current_time
            # -------------------------------- #

            cv2.putText(
                frame,
                gesture_text,
                (40, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.4,
                (0, 255, 0),
                3
            )

    cv2.imshow("Gesture Controlled Media System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
