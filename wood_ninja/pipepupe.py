import cv2
import mediapipe as mp

# 1. Initialize MediaPipe Hands and Drawing Utils
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 2. Configure the Hands model
hands = mp_hands.Hands(
    static_image_mode=False,        # False for video stream, True for images
    max_num_hands=1,                # Maximum number of hands to detect
    min_detection_confidence=0.7,   # Threshold for initial detection
    min_tracking_confidence=0.7     # Threshold for tracking consistency
)

# 3. Initialize Webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # 4. Pre-process the image
    # Flip horizontally for a selfie-view display
    image = cv2.flip(image, 1)
    # Convert from OpenCV's default BGR to RGB (required by MediaPipe)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 5. Process the image to find hands
    # To improve performance, mark the image as not writeable
    image_rgb.flags.writeable = False
    results = hands.process(image_rgb)
    image_rgb.flags.writeable = True

    # 6. Extract Landmarks and Track the Finger
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            # MediaPipe assigns a number (0-20) to each hand joint.
            # The Index Finger Tip is landmark #8.
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # The coordinates (x, y) are normalized between 0.0 and 1.0. 
            # We need to multiply them by the image dimensions to get actual pixel coordinates.
            h, w, c = image.shape
            cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            # Draw a large circle specifically on the index finger tip
            cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            # (Optional) Draw the rest of the hand skeleton
            mp_drawing.draw_landmarks(
                image, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS
            )

    # 7. Display the output
    cv2.imshow('MediaPipe Finger Tracking', image)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 8. Clean up
cap.release()
cv2.destroyAllWindows()