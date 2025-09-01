import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
from collections import deque, Counter
import random
from PIL import ImageFont, ImageDraw, Image
from logger_client import send_log  # Assumes this works

# === Load dataset
df = pd.read_csv("../data/isl_landmarks_complete.csv")

# === Normalize function
def normalize_landmarks(landmarks):
    landmarks = np.array(landmarks).reshape(21, 3)
    wrist = landmarks[0]
    relative = landmarks - wrist
    norm = np.linalg.norm(relative)
    return (relative / norm).flatten() if norm != 0 else relative.flatten()

# === Prepare templates
templates = {}
for label in df['label'].unique():
    vectors = df[df['label'] == label].iloc[:, 1:].values
    templates[label] = [normalize_landmarks(vec) for vec in vectors]

# === Mediapipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# === Webcam & buffer
cap = cv2.VideoCapture(0)
prediction_buffer = deque(maxlen=5)

# === Score tracking
correct_count = 0
attempted = 0

# === Letters to train
letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
random.shuffle(letters)
current_index = 0
target_letter = letters[current_index]

# === Font setup
FONT_PATH = "../fonts/Montserrat-Regular.ttf"  # Ensure this path exists
FONT_LARGE = ImageFont.truetype(FONT_PATH, 40)
FONT_MEDIUM = ImageFont.truetype(FONT_PATH, 30)
FONT_SMALL = ImageFont.truetype(FONT_PATH, 24)

# === UI drawing function
def draw_modern_ui(frame, target_letter, most_common, feedback, correct_count, attempted):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(pil_img)

    # Adjusted positions and sizes for UI elements
    ui_x_start = 20
    ui_y_start = 20
    ui_width = 300
    ui_height = 50
    spacing = 10

    # Background Cards
    draw.rectangle([(ui_x_start, ui_y_start), (ui_x_start + ui_width, ui_y_start + ui_height)], fill=(20, 20, 20))  # Letter
    draw.rectangle([(ui_x_start, ui_y_start + (ui_height + spacing)), 
                    (ui_x_start + ui_width, ui_y_start + 2 * (ui_height + spacing))], fill=(20, 20, 20))  # Prediction
    draw.rectangle([(ui_x_start, ui_y_start + 2 * (ui_height + spacing)), 
                    (ui_x_start + ui_width, ui_y_start + 3 * (ui_height + spacing))], fill=(20, 20, 20))  # Feedback
    draw.rectangle([(ui_x_start, ui_y_start + 3 * (ui_height + spacing)), 
                    (ui_x_start + ui_width, ui_y_start + 4 * (ui_height + spacing))], fill=(20, 20, 20))  # Score

    # Content Text
    draw.text((ui_x_start + 10, ui_y_start + 10), f"Sign: {target_letter}", font=FONT_MEDIUM, fill=(255, 255, 255))
    draw.text((ui_x_start + 10, ui_y_start + ui_height + spacing + 10), f"Prediction: {most_common or '...'}", 
              font=FONT_SMALL, fill=(161, 227, 166))
    draw.text((ui_x_start + 10, ui_y_start + 2 * (ui_height + spacing) + 10), feedback, 
              font=FONT_SMALL, fill=(50, 220, 120) if "Correct" in feedback else (255, 80, 80))
    
    accuracy = (correct_count / attempted) * 100 if attempted else 0
    draw.text((ui_x_start + 10, ui_y_start + 3 * (ui_height + spacing) + 10), 
              f"Score: {correct_count}/{attempted} ({accuracy:.1f}%)", font=FONT_SMALL, fill=(200, 200, 200))

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# === Get landmarks
def get_live_landmarks(frame):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            coords = []
            for lm in hand_landmarks.landmark:
                coords.extend([lm.x, lm.y, lm.z])
            return coords
    return None

# === Prediction logic
def predict_label(normalized_vec):
    min_distances = {}
    for label, vectors in templates.items():
        distances = [np.linalg.norm(normalized_vec - vec) for vec in vectors]
        min_distances[label] = min(distances)
    return min(min_distances, key=min_distances.get)

# === State
already_logged = False

# === Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    raw_landmarks = get_live_landmarks(frame)
    feedback = ""
    most_common = ""

    if raw_landmarks and len(raw_landmarks) == 63:
        normalized = normalize_landmarks(raw_landmarks)
        prediction = predict_label(normalized)
        prediction_buffer.append(prediction)

        most_common = Counter(prediction_buffer).most_common(1)[0][0]

        if most_common == target_letter:
            feedback = "Correct!"
            if not already_logged:
                correct_count += 1
                attempted += 1
                send_log(
                    user_id="sidd_001",
                    target_letter=target_letter,
                    predicted_letter=most_common,
                    correct=True
                )
                already_logged = True
        else:
            feedback = "Try again"
            already_logged = False

    frame = draw_modern_ui(
        frame,
        target_letter=target_letter,
        most_common=most_common,
        feedback=feedback,
        correct_count=correct_count,
        attempted=attempted
    )

    cv2.imshow("ISL Trainer", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('n'):
        if not already_logged:
            attempted += 1
            send_log(
                user_id="sidd_001",
                target_letter=target_letter,
                predicted_letter=most_common,
                correct=(most_common == target_letter)
            )

        current_index += 1
        if current_index < len(letters):
            target_letter = letters[current_index]
            prediction_buffer.clear()
            already_logged = False
        else:
            print("Training complete!")
            break

cap.release()
cv2.destroyAllWindows()
