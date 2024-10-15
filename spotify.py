import subprocess
import pyautogui
import time
import comtypes

def initialize_com():
    """Инициализирует COM для текущего потока."""
    comtypes.CoInitialize()

def uninitialize_com():
    """Деинициализирует COM для текущего потока."""
    comtypes.CoUninitialize()

# --- Основные функции управления Spotify ---

def open_spotify():
    """Открывает Spotify и переводит в полноэкранный режим."""
    subprocess.Popen(['путь к приложению Spotify'])
    time.sleep(5)  # Подождите, пока приложение откроется
    pyautogui.hotkey('f11')  # Нажатие F11 для полноэкранного режима
    return "Spotify открыт в полноэкранном режиме."

def play_music():
    """Возобновляет воспроизведение музыки."""
    pyautogui.press('playpause')  # Нажимает клавишу Play/Pause
    return "Музыка возобновлена."

def pause_music():
    """Приостанавливает воспроизведение музыки."""
    pyautogui.press('playpause')  # Нажимает клавишу Play/Pause
    return "Музыка приостановлена."

def skip_track():
    """Переключает на следующий трек."""
    pyautogui.press('nexttrack')  # Нажимает клавишу Next Track
    return "Переключился на следующий трек."

def previous_track():
    """Переключает на предыдущий трек."""
    pyautogui.press('prevtrack')  # Нажимает клавишу Previous Track
    return "Переключился на предыдущий трек."

# Инициализация COM в основном потоке
if __name__ == "__main__":
    initialize_com()
    try:
        # Запуск вашего бота или другого кода
        pass  # Здесь добавьте код для запуска бота
    finally:
        uninitialize_com()
