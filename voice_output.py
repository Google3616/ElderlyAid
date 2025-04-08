# voice_output.py
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 140)  # Slower, clearer speech

def speak_text(text):
    engine.say(text)
    engine.runAndWait()
