rm -rf .venv
echo "RESTARTING VENV"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pillow pytesseract pyautogui mss matplotlib pyttsx3 pyqt5 openai keyboard

