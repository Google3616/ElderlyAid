from PIL import Image
import pytesseract
import pyautogui
import subprocess
from AppKit import NSWorkspace
import mss
import matplotlib.pyplot as plt

GRID_COLUMNS = 8
GRID_ROWS = 6

def read_screen(preview=False):
    with mss.mss() as sct:
        screen = sct.monitors[1]

        screen_width = screen["width"]
        screen_height = screen["height"]
        top = screen["top"]
        left = screen["left"]

        cell_width = screen_width // GRID_COLUMNS
        cell_height = screen_height // GRID_ROWS

        grid_text = {}

        for row in range(GRID_ROWS):
            for col in range(GRID_COLUMNS):
                region = {
                    "top": top + row * cell_height,
                    "left": left + col * cell_width,
                    "width": cell_width,
                    "height": cell_height
                }

                img = sct.grab(region)
                img_pil = Image.frombytes("RGB", img.size, img.rgb)

                if preview:
                    plt.imshow(img_pil)
                    plt.title(f"Grid Cell ({col}, {row})")
                    plt.axis("off")
                    plt.show()

                # Preprocess: grayscale and binarize
                gray = img_pil.convert("L")
                bw = gray.point(lambda x: 0 if x < 128 else 255, '1')

                # Use image_to_data to get confidence scores
                data = pytesseract.image_to_data(bw, config="--psm 6", output_type=pytesseract.Output.DICT)

                text_parts = [
                    word for word, conf in zip(data["text"], data["conf"])
                    if word.strip() and conf != '-1' and int(conf) >= 75
                ]
                text = " ".join(text_parts)
                grid_text[(col, row)] = text

        return grid_text


def get_system_context():
    # Mouse Position
    mouse_x, mouse_y = pyautogui.position()

    # Active App
    active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
    app_name = active_app.localizedName()

    # Active Window Title (AppleScript)
    try:
        script = f'tell application "{app_name}" to get name of front window'
        window_title = subprocess.check_output(['osascript', '-e', script], text=True).strip()
    except subprocess.CalledProcessError:
        window_title = "(Unknown or no active window)"

    # All Visible Windows
    try:
        script_all = '''
        set window_list to {}
        tell application "System Events"
            repeat with proc in application processes
                repeat with win in windows of proc
                    if visible of win is true then
                        set end of window_list to name of win
                    end if
                end repeat
            end repeat
        end tell
        return window_list
        '''
        all_windows = subprocess.check_output(['osascript', '-e', script_all], text=True).strip().split(", ")
    except subprocess.CalledProcessError:
        all_windows = []

    return {
        "mouse_position": (mouse_x, mouse_y),
        "active_app": app_name,
        "active_window_title": window_title,
        "all_visible_windows": all_windows
    }


def capture_data(preview_grid=False):
    print("[Assistant] Gathering context...")

    grid = read_screen(preview=preview_grid)
    system = get_system_context()

    state = {
        "grid_text": grid,
        "mouse_position": system["mouse_position"],
        "active_app": system["active_app"],
        "active_window_title": system["active_window_title"],
        "visible_windows": system["all_visible_windows"]
    }

    return state
