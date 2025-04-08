# main.py
from screen_reader import capture_data
from voice_output import speak_text
from draw_screen import highlight
from assistant_core import ask_gpt,emulate_keys
import ast

def main(): 
    text = capture_data()
    response = ask_gpt(system=str(text),prompt="I can't find my test.sh script on my screen, can you highlight it?.")
    print(response)
    if (response['highlight']):
        print(response['highlight'])
        highlight(response['highlight'][0],response['highlight'][1])
    if (response['message']):
        print(response['message'])
    if (response['keys']):
        print(response['keys'])
        emulate_keys(response['keys'])
    
    

if __name__ == "__main__":
    main()
