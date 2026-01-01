#  Vibe-Sync: AI Voice & Gesture RGB Control

A high-tech interface that combines **Google Speech Recognition** and **MediaPipe Hand Tracking** to control physical hardware. 

## ✨ Key Features
- **Pinch-to-Talk:** Pinch your thumb and index finger together to trigger the microphone.
- **Voice Commands:** Say "Red", "Blue", "Purple", or "Cyan" to instantly change the vibe.
- **Neon HUD:** A sleek, minimal overlay that tracks your hand with a glowing neon effect.
- **Visualizer:** A professional-grade audio meter that shows your voice levels while recording.

## 🛠️ Hardware Setup
- **Arduino Board** (Uno, Nano, or Mega)
- **Common Cathode RGB LED**
- **3x 220Ω Resistors**

### Wiring:
- **Red Pin:** Arduino Pin 9
- **Green Pin:** Arduino Pin 10
- **Blue Pin:** Arduino Pin 11
- **Ground:** GND


## 🚀 Installation & Launch
1. **Flash Arduino:** Upload the `controller.ino` file (Set to 115200 Baud).
2. **Install Python:** ```bash
   pip install opencv-python mediapipe pyserial SpeechRecognition sounddevice numpy
