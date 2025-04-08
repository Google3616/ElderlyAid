import openai
import re
import time
import pyautogui
import keyboard
from PIL import ImageGrab
import io
import base64
from draw_screen import highlight

# Set your OpenAI API key here
API_KEY = "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"

# Get current screen as bytes
def capture_screen():
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()

# Extract screen info using GPT-4-vision
from io import BytesIO

import base64
import openai
import pyautogui
from io import BytesIO

def summarize_screen(IMG = None):
    # Capture screenshot
    screenshot = pyautogui.screenshot()
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    # Create OpenAI client
    client = openai.OpenAI(api_key=API_KEY)

    # Call GPT-4o
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that analyzes screenshots of a computer desktop. "
                "The user will provide you a screenshot of the desktop, and you will divide the screen into a 5x8 grid. "
                "For each cell in the grid (from top-left to bottom-right), summarize any meaningful text or interface elements you see. "
                "Use coordinates like (0,0) for the top-left cell, (4,7) for the bottom-right. "
                "Only return a dictionary with keys like (0,0), (0,1)... and short text summaries as values describing the text content or icons."
            )
        },
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                {"type": "text", "text": "Please return a dictionary of summaries from the grid, nothing else."}
            ]
        }
    ],
        max_tokens=1000
    )


    return response.choices[0].message.content.strip()


# GPT-3.5 to process instructions and generate actions
def ask_gpt(prompt: str, system="", model="gpt-3.5-turbo", max_tokens=2000):
    client = openai.OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return parse_response(response.choices[0].message.content.strip())

def parse_response(response: str):
    highlight = None
    message = None
    key_groups = []

    highlight_match = re.search(r"highlight:\((\d+),\s*(\d+)\)", response)
    if highlight_match:
        highlight = (int(highlight_match.group(1)), int(highlight_match.group(2)))

    response_match = re.search(r"response:([^\n]+)", response)
    if response_match:
        message = response_match.group(1).strip()

    group_matches = re.findall(r"\\(([^)]+)\\)", response)
    for group in group_matches:
        keys = [k.strip().upper() for k in group.split()]
        key_groups.append(keys)

    return {
        "highlight": highlight,
        "message": message,
        "keys": key_groups
    }

def emulate_keys(key_groups):
    key_map = {
        "CMD": "command",
        "CTRL": "ctrl",
        "SHIFT": "shift",
        "ALT": "alt",
        "ENTER": "enter",
        "SPACE": "space"
    }

    for group in key_groups:
        print(f"Pressing group: {group}")
        resolved = [key_map.get(k, k.lower()) for k in group]

        if len(resolved) == 1:
            k = resolved[0]
            if len(k) == 1:
                pyautogui.write(k, interval=0.033)
            else:
                keyboard.press_and_release(k)
        else:
            keyboard.press_and_release("+".join(resolved))

        time.sleep(0.25)

def main():
    time.sleep(5)
    issue = "I need to open the Maps app."
    screen_image = capture_screen()
    screen_summary = summarize_screen(screen_image)

    print("Screen Summary:", screen_summary)

    system_message = (
        "You are an intelligent desktop assistant. The user screen is summarized here in a 5x8 grid on the screen (screen is 2560 x 1640): " + screen_summary + ". "
        "The issue is given by the prompt. If helpful, return 'highlight:(X,Y)'. "
        "Also return a helpful response 'response:...' and key press combos to open and close apps or any other shortcuts:[(CMD SPACE), (M), (A), (P), (ENTER)]. "
        "**Use keypresses** to automate app launching and typing. **You must** use keypresses to open apps to assist the elderly people. You also must have a helpful message."
    )

    result = ask_gpt(issue, system=system_message)
    print(result)
    if result["message"]:
        print("Assistant Response:", result["message"])
    if result["highlight"]:
        highlight(result['highlight'][0],result['highlight'][1])
    if result["keys"]:
        emulate_keys(result["keys"])

if __name__ == "__main__":
    main()
