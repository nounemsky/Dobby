from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from datetime import datetime, timedelta
import subprocess

volume_interface = None

def initialize_com():
    try:
        CoInitialize()
    except Exception as e:
        print(f"Ошибка инициализации COM: {e}")
        
def uninitialize_com():
    try:
        CoUninitialize()
    except Exception as e:
        print(f"Ошибка завершения COM: {e}")

def get_volume_interface():
    global volume_interface
    if volume_interface is None:
        initialize_com() 
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
    return volume_interface

def increase_pc_volume(step=0.1):
    volume = get_volume_interface()
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = min(current_volume + step, 1.0)
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    return f"Громкость увеличена до {int(new_volume * 100)}%"

# мут
def mute_pc_volume():
    volume = get_volume_interface()
    volume.SetMasterVolumeLevelScalar(0.0, None) 
    return "Звук отключен."

# уменьшения громкости
def decrease_pc_volume(step=0.1):
    volume = get_volume_interface()
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = max(current_volume - step, 0.0)  
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    return f"Громкость уменьшена до {int(new_volume * 100)}%"

# перезагрузки компьютера
def restart_pc():
    try:
        subprocess.call(["shutdown", "/r", "/f", "/t", "0"])  
        return "Компьютер перезагружается..."
    except Exception as e:
        return f"Ошибка при перезагрузке компьютера: {e}"

# выключения компьютера
def shutdown_pc():
    try:
        subprocess.call(["shutdown", "/s", "/f", "/t", "0"])  
        return "Компьютер выключается..."
    except Exception as e:
        return f"Ошибка при выключении компьютера: {e}"

# планирования выключения 
def schedule_shutdown(target_time):
    try:
        now = datetime.now()
        shutdown_time = datetime.strptime(target_time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)

        if shutdown_time < now:
            shutdown_time += timedelta(days=1)

        seconds = (shutdown_time - now).total_seconds()
        subprocess.call(["shutdown", "/s", "/t", str(int(seconds))])  
        return f"Компьютер будет выключен в {shutdown_time.strftime('%H:%M')}."
    except Exception as e:
        return f"Ошибка при планировании выключения: {e}"

def close_program():
    uninitialize_com()
