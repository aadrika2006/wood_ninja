import cv2
import random
from tracker import HandTracker
from collision import is_collision

# ---------- INIT ----------
cap = cv2.VideoCapture(0)
tracker = HandTracker()

# fullscreen setup
cv2.namedWindow("Game", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Game", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# ---------- PNG OVERLAY ----------
def overlay_png(frame, png, x, y):
    h, w = png.shape[:2]

    if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
        return

    if png.shape[2] == 4:
        alpha = png[:, :, 3] / 255.0
        for c in range(3):
            frame[y:y+h, x:x+w, c] = (
                alpha * png[:, :, c] +
                (1 - alpha) * frame[y:y+h, x:x+w, c]
            )
    else:
        frame[y:y+h, x:x+w] = png


# ---------- LOAD IMAGES ----------
img1 = cv2.imread("log.PNG", cv2.IMREAD_UNCHANGED)
img2 = cv2.imread("logl.PNG", cv2.IMREAD_UNCHANGED)
img3 = cv2.imread("logr.PNG", cv2.IMREAD_UNCHANGED)

if img1 is None or img2 is None or img3 is None:
    print("❌ ERROR: image files not found")
    exit()

# resize all
img1 = cv2.resize(img1, (100, 100))
img2 = cv2.resize(img2, (100, 100))
img3 = cv2.resize(img3, (100, 100))

# ---------- OBJECTS ----------
objects = []

objects.append({
    "x": 300,
    "y": 500,
    "vel_x": random.randint(-5, 5),
    "vel_y": -22,
    "img": img1,
    "type": "whole"
})

gravity = 0.8
score = 0

# swipe tracking
prev_x, prev_y = 0, 0
trail = []

# ---------- GAME LOOP ----------
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    finger = tracker.get_finger_pos(frame)

    speed = 0

    if finger:
        fx, fy = finger

        # draw finger
        cv2.circle(frame, (fx, fy), 10, (0,255,0), -1)

        # calculate swipe speed
        speed = abs(fx - prev_x) + abs(fy - prev_y)
        prev_x, prev_y = fx, fy

        # trail
        trail.append((fx, fy))
        if len(trail) > 10:
            trail.pop(0)

    # draw trail
    for i in range(1, len(trail)):
        cv2.line(frame, trail[i-1], trail[i], (0,255,255), 3)

    new_objects = []

    for obj in objects:
        x, y = obj["x"], obj["y"]
        vel_x, vel_y = obj["vel_x"], obj["vel_y"]
        img = obj["img"]
        obj_h, obj_w = img.shape[:2]

        # ---------- SWIPE COLLISION ----------
        if finger and obj["type"] == "whole":
            if speed > 40 and is_collision(fx, fy, x, y, obj_w, obj_h):
                score += 1
                print("SLICE!", score)

                # spawn split pieces
                new_objects.append({
                    "x": x - 20,
                    "y": y,
                    "vel_x": -5,
                    "vel_y": -15,
                    "img": img2,
                    "type": "piece"
                })

                new_objects.append({
                    "x": x + 20,
                    "y": y,
                    "vel_x": 5,
                    "vel_y": -15,
                    "img": img3,
                    "type": "piece"
                })

                continue  # remove original

        # ---------- PHYSICS ----------
        vel_y += gravity
        x += vel_x
        y += int(vel_y)

        obj["x"], obj["y"] = x, y
        obj["vel_x"], obj["vel_y"] = vel_x, vel_y

        # keep if on screen
        if y < h:
            new_objects.append(obj)

    objects = new_objects

    # ---------- SPAWN NEW ----------
    if len(objects) < 1:
        objects.append({
            "x": random.randint(0, w - 100),
            "y": h,
            "vel_x": random.randint(-6, 6),
            "vel_y": random.randint(-28, -20),
            "img": img1,
            "type": "whole"
        })

    # ---------- DRAW ----------
    for obj in objects:
        overlay_png(frame, obj["img"], obj["x"], obj["y"])

    # ---------- UI ----------
    cv2.putText(frame, f"Score: {score}", (20,50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.imshow("Game", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()