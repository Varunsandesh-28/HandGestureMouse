# 🖐️ Hand Gesture Mouse

A Python-based touchless computer control system that uses hand gestures and a webcam to control the mouse cursor, perform clicks, drag and drop, and control Windows Magnifier zoom.

## 📌 Problem Statement

Traditional computer interaction requires a physical mouse or touchpad. This project explores a hands-free alternative that allows users to interact with their computer using simple hand gestures detected through a webcam.

## 💡 Solution

Hand Gesture Mouse uses computer vision and hand landmark detection to recognize gestures and translate them into mouse actions and keyboard shortcuts.

## ✨ Features

- 🖱️ **Cursor Movement** — Move the mouse using your index fingertip.
- 👆 **Drag and Drop** — Use a thumb-index finger pinch.
- 🖱️ **Right Click** — Use a thumb-middle finger pinch.
- 🔍 **Zoom In** — Move an open palm closer to the webcam.
- 🔎 **Zoom Out** — Move a closed fist farther from the webcam.
- 🎥 **Real-Time Hand Tracking** — Detect hand landmarks through a webcam.
- 🛑 **Hand Detection Safety** — Stop cursor movement when no hand is detected.

## 🛠️ Technologies Used

- Python
- OpenCV
- MediaPipe
- PyAutoGUI
- Windows Magnifier

## ⚙️ Requirements

- Windows computer
- Python 3.12 or a compatible Python version
- Webcam
- Git (optional)

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/HandGestureMouse.git
cd HandGestureMouse
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment on Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install opencv-python mediapipe pyautogui
```

### 5. Run the application

```bash
python main.py
```

## 🎮 How to Use

| Gesture | Action |
|---|---|
| Move index fingertip | Move cursor |
| Pinch thumb and index finger | Drag and drop |
| Pinch thumb and middle finger | Right click |
| Open palm and move closer | Zoom in |
| Close fist and move away | Zoom out |
| Press `Q` in the camera window | Exit application |

**Magnifier setup:** Open Windows Magnifier using `Windows + Plus (+)` before using zoom gestures.

## 📂 Project Structure

```text
HandGestureMouse/
├── main.py
├── main_backup.py
├── .gitignore
└── README.md
```

## 🔒 Privacy

The application processes webcam frames locally while running. It does not require a cloud AI service for its core hand-tracking workflow.

## ⚠️ Limitations

- Requires a working webcam and suitable lighting.
- Gesture recognition may vary with camera position and hand visibility.
- Zoom gestures depend on Windows Magnifier and keyboard shortcut compatibility.
- This project is currently designed for Windows.

## 🔮 Future Improvements

- Gesture sensitivity calibration
- Improved gesture recognition
- Customizable mouse controls
- Packaged Windows executable
- Improved accessibility and user experience

## 🤝 Contributing

Suggestions and improvements are welcome. Fork the repository and submit a pull request.

## 📜 License

This project is open source. Add a license file, such as the MIT License, if you want to permit reuse under those terms.

---

**Built with Python, computer vision, and hand gestures.**
