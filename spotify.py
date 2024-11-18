import subprocess
import pyautogui
import time
import comtypes

def initialize_com():
    comtypes.CoInitialize()

def uninitialize_com():
    comtypes.CoUninitialize()

def open_spotify():
    subprocess.Popen(['ПУТЬ к приложению Spotify'])
    time.sleep(5) 
    pyautogui.hotkey('f11')
    return 

def play_music():
    pyautogui.press('playpause')  
    return 

def pause_music():
    pyautogui.press('playpause')  
    return 

def skip_track():
    pyautogui.press('nexttrack')  
    return 

def previous_track():
    pyautogui.press('prevtrack')  
    return

if __name__ == "__main__":
    initialize_com()
    try:
        pass  
    finally:
        uninitialize_com()
