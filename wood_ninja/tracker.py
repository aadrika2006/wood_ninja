import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands

class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_finger_pos(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = image.shape
                tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                cx = int(tip.x * w)
                cy = int(tip.y * h)

                return cx, cy

        return None