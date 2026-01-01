import cv2
import mediapipe as mp
import serial
import time
import speech_recognition as sr
import numpy as np
import math
import threading
import sounddevice as sd

# ---------- System Setup ----------
SERIAL_PORT = 'COM3'  # <--- CHANGE THIS TO YOUR PORT (e.g., 'COM5')
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0) 
    time.sleep(2)
except Exception as e:
    ser = None
    print(f"Serial Error: {e}. Running in simulation mode.")

recognizer = sr.Recognizer()
mic = sr.Microphone()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
WIN_NAME = "VIBE_SYNC_HUD"

cv2.namedWindow(WIN_NAME, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# ---------- State ----------
current_rgb = [0, 255, 255] 
is_listening = False
last_recognized = "READY"
mic_level = 0
last_serial_time = time.time()

COLORS = {
    "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
    "yellow": (255, 255, 0), "purple": (160, 0, 255), "pink": (255, 50, 120),
    "white": (255, 255, 255), "cyan": (0, 255, 255), "orange": (255, 60, 0)
}

def audio_callback(indata, frames, time_info, status):
    global mic_level
    if is_listening:
        vol = np.linalg.norm(indata) * 20
        mic_level = vol
    else:
        mic_level = 0

try:
    audio_stream = sd.InputStream(callback=audio_callback)
    audio_stream.start()
except:
    print("Mic not found for volume meter.")

def speech_thread():
    global current_rgb, is_listening, last_recognized
    while True:
        if is_listening:
            with mic as source:
                try:
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=2)
                    text = recognizer.recognize_google(audio).lower()
                    last_recognized = text
                    for word in COLORS:
                        if word in text:
                            current_rgb = list(COLORS[word])
                            break
                except: pass
                is_listening = False
        time.sleep(0.1)

threading.Thread(target=speech_thread, daemon=True).start()

def draw_minimal_ui(img):
    h, w = img.shape[:2]
    color_bgr = (current_rgb[2], current_rgb[1], current_rgb[0])
    text = f"{last_recognized.upper()}"
    t_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 1.2, 2)[0]
    cv2.putText(img, text, (w//2 - t_size[0]//2, 60), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0,0,0), 4, cv2.LINE_AA)
    cv2.putText(img, text, (w//2 - t_size[0]//2, 60), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255,255,255), 2, cv2.LINE_AA)

    mx, my, mw, mh = int(w*0.95), int(h*0.9), 15, int(h*0.35)
    cv2.rectangle(img, (mx, my-mh), (mx+mw, my), (20,20,20), -1)
    
    if is_listening:
        curr_h = int(np.clip(mic_level * (mh/50), 0, mh))
        for i in range(curr_h):
            mix = i / mh
            b = int(color_bgr[0] * (1-mix) + 255 * mix)
            g = int(color_bgr[1] * (1-mix) + 255 * mix)
            r = int(color_bgr[2] * (1-mix) + 255 * mix)
            cv2.line(img, (mx, my-i), (mx+mw, my-i), (b, g, r), 1)
        cv2.putText(img, "REC", (mx - 60, my - mh - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    return img

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    hud = np.zeros_like(frame)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        lm = results.multi_hand_landmarks[0].landmark
        pts = [(int(l.x * WIDTH), int(l.y * HEIGHT)) for l in lm]
        dist = math.hypot(pts[4][0]-pts[8][0], pts[4][1]-pts[8][1])
        if dist < 40: is_listening = True

        c_bgr = (current_rgb[2], current_rgb[1], current_rgb[0])
        t = 8 if is_listening else 2
        for conn in mp_hands.HAND_CONNECTIONS:
            cv2.line(hud, pts[conn[0]], pts[conn[1]], c_bgr, t, cv2.LINE_AA)
            cv2.line(hud, pts[conn[0]], pts[conn[1]], (255,255,255), 1, cv2.LINE_AA)

    hud = draw_minimal_ui(hud)
    
    if ser and (time.time() - last_serial_time > 0.05):
        try:
            packet = f"{current_rgb[0]},{current_rgb[1]},{current_rgb[2]}\n".encode()
            ser.write(packet)
            last_serial_time = time.time()
        except Exception: pass

    combined = cv2.addWeighted(frame, 0.8, hud, 1.0, 0)
    cv2.imshow(WIN_NAME, combined)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
