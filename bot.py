import telebot
import config
from telebot import types
import datetime
import time
import subprocess
import os
import ctypes  

from comands import shutdown_pc, schedule_shutdown, restart_pc, increase_pc_volume, decrease_pc_volume, mute_pc_volume
from spotify import play_music, pause_music, skip_track, previous_track

bot = telebot.TeleBot(config.TOKEN)

# Папка
SAVE_FOLDER = "ПУТЬ К ПАПКЕ"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def validate_time_format(time_str):
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

is_playing = False
is_rebooting = False
is_shutting_down = False
current_volume = 100
current_spotify_volume = 100
scheduled_time = None  
is_muted = False  
previous_volume = current_volume  

def show_notification():
    ctypes.windll.user32.MessageBoxW(0, "Dobby запущен!", "Уведомление", 1)

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id == config.owner_id:
        bot.send_message(message.chat.id, "Добро пожаловать, Хозяин!")
        main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этому боту.")

@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'voice'])
def handle_files(message):
    if message.chat.id == config.owner_id:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            if message.document:
                file_info = bot.get_file(message.document.file_id)
                file_extension = message.document.file_name.split('.')[-1]
                filename = f"{timestamp}.{file_extension}"
            elif message.photo:
                file_info = bot.get_file(message.photo[-1].file_id)
                filename = f"{timestamp}.jpg"
            elif message.video:
                file_info = bot.get_file(message.video.file_id)
                filename = f"{timestamp}.mp4"
            elif message.audio:
                file_info = bot.get_file(message.audio.file_id)
                filename = f"{timestamp}.mp3"
            elif message.voice:
                file_info = bot.get_file(message.voice.file_id)
                filename = f"{timestamp}.ogg"

            file_path = file_info.file_path
            save_path = os.path.join(SAVE_FOLDER, filename)

            downloaded_file = bot.download_file(file_path)
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.send_message(message.chat.id, f"Файл успешно сохранен в C:\\Telegram Files") # ПОМЕНЯТЬ НА СВОЙ
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при загрузке файла: {e}")
    else:
        bot.send_message(message.chat.id, "У вас нет доступа.")

def main_menu(chat_id):
    ACTION_PROMPT = "Выберите действие:"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🖥")
    item2 = types.KeyboardButton("Spotify")

    markup.add(item1, item2)
    bot.send_message(chat_id, ACTION_PROMPT, reply_markup=markup)

def update_computer_markup(chat_id):
    BACK_BUTTON_TEXT = "Назад"
    computer_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    volume_button = types.KeyboardButton("🔈")
    shutdown_button = types.KeyboardButton("🔌")
    restart_button = types.KeyboardButton("🔄")
    back_button = types.KeyboardButton(BACK_BUTTON_TEXT)

    computer_markup.add(volume_button, shutdown_button, restart_button)
    computer_markup.add(back_button)

    bot.send_message(chat_id, "Выберите действие:", reply_markup=computer_markup)

def update_spotify_markup(chat_id):
    global is_playing
    spotify_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    left_button = types.KeyboardButton("◀")
    pause_button = types.KeyboardButton("🔉" if is_playing else "⏸️")
    right_button = types.KeyboardButton("▶")
    back_button = types.KeyboardButton("Назад")

    spotify_markup.add(left_button, pause_button, right_button)
    spotify_markup.add(back_button)

    bot.send_message(chat_id, "Spotify:", reply_markup=spotify_markup)

def update_volume_markup(chat_id):
    volume_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    plus_button = types.KeyboardButton("➕🔟")
    current_volume_button = types.KeyboardButton(f"🔈{current_volume}%")
    minus_button = types.KeyboardButton("➖🔟")
    back_button = types.KeyboardButton("Назад")

    volume_markup.add(plus_button, current_volume_button, minus_button)
    volume_markup.add(back_button)

    bot.send_message(chat_id, "Выберите действие для регулировки громкости:", reply_markup=volume_markup)


def cancel_timer():
    try:
        subprocess.call(["shutdown", "/a"]) 
        return "Таймер отменен."
    except Exception as e:
        return f"Ошибка при отмене таймера: {e}"


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_message(message):
    global is_playing, is_rebooting, is_shutting_down, current_volume, scheduled_time, current_volume, is_muted, previous_volume
    if message.chat.type == 'private':
        text = message.text.lower()

        if text == 'молодец':
            bot.send_message(message.chat.id, 'Спасибо, Хозяин!')

        elif text == 'кто ты?':
            bot.send_message(message.chat.id, 'Добби, Хозяин!')

        elif text == '🖥':
            update_computer_markup(message.chat.id)

        elif text == '🔈':
            update_volume_markup(message.chat.id)

        elif text == f"🔈{current_volume}%":  

            if not is_muted:
                previous_volume = current_volume
                mute_pc_volume()  
                current_volume = 0
                is_muted = True
                bot.send_message(message.chat.id, "Звук выключен.")
            else:
                current_volume = previous_volume
                increase_pc_volume(current_volume / 100)
                is_muted = False
                bot.send_message(message.chat.id, f"Громкость восстановлена на {current_volume}%.")
                
            update_volume_markup(message.chat.id)

        elif text == '➕🔟':
            if is_muted:
                is_muted = False  
            current_volume = min(current_volume + 10, 100)
            increase_pc_volume()
            bot.send_message(message.chat.id, "Громкость увеличена на 10%.")
            update_volume_markup(message.chat.id)


        elif text == '➖🔟':
            if is_muted:
                is_muted = False  
            current_volume = max(current_volume - 10, 0)
            decrease_pc_volume()
            bot.send_message(message.chat.id, "Громкость уменьшена на 10%.")
            update_volume_markup(message.chat.id)

        elif text == 'spotify':
            update_spotify_markup(message.chat.id)

        elif text == '◀':
            bot.send_message(message.chat.id, "Переключаю на предыдущий трек.")
            bot.send_message(message.chat.id, previous_track())

        elif text == '🔉' or text == '⏸️':
            if is_playing:
                bot.send_message(message.chat.id, "Приостановка воспроизведения.")
                bot.send_message(message.chat.id, pause_music())
                is_playing = False
            else:
                bot.send_message(message.chat.id, "Возобновление воспроизведения.")
                bot.send_message(message.chat.id, play_music())
                is_playing = True
            update_spotify_markup(message.chat.id)

        elif text == '▶':
            bot.send_message(message.chat.id, "Переключаю на следующий трек.")
            bot.send_message(message.chat.id, skip_track())

        elif text == 'назад':
            main_menu(message.chat.id)

        elif text == '🔌':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            quick_shutdown_button = types.KeyboardButton("Быстрое выключение")
            schedule_shutdown_button = types.KeyboardButton("Запланировать")
            cancel_shutdown_button = types.KeyboardButton("Удалить таймер")
            back_button = types.KeyboardButton("Назад")
            markup.add(quick_shutdown_button, schedule_shutdown_button, cancel_shutdown_button)
            markup.add(back_button)
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

        elif text == 'быстрое выключение':
            if not is_shutting_down:
                is_shutting_down = True
                bot.send_message(message.chat.id, "Закрываю все программы...")
                time.sleep(3)
                bot.send_message(message.chat.id, "Сохраняю данные...")
                time.sleep(5)
                bot.send_message(message.chat.id, "Завершаю все процессы...")
                time.sleep(5)
                bot.send_message(message.chat.id, shutdown_pc())
                bot.send_message(message.chat.id, "Компьютер выключен!")
                is_shutting_down = False
            else:
                bot.send_message(message.chat.id, "Команда на выключение уже выполняется.")

        elif text == 'запланировать':
            bot.send_message(message.chat.id, "Введите время в формате HH:MM (24-часовой формат):")
            bot.register_next_step_handler(message, handle_schedule_shutdown)

        elif text == 'удалить таймер':
            if scheduled_time:
                bot.send_message(message.chat.id, cancel_timer())
                scheduled_time = None  
            else:
                bot.send_message(message.chat.id, "Нет запланированного таймера для удаления.")

        elif text == '🔄':
            if not is_rebooting:
                is_rebooting = True
                bot.send_message(message.chat.id, "Закрываю программы...")
                time.sleep(3)
                bot.send_message(message.chat.id, "Сохраняю данные...")
                time.sleep(5)
                bot.send_message(message.chat.id, "Завершаю все процессы...")
                time.sleep(5)
                bot.send_message(message.chat.id, restart_pc())
                bot.send_message(message.chat.id, "Перезапускаю систему...")
                time.sleep(5)
                bot.send_message(message.chat.id, "Перезагрузка завершена!")
                is_rebooting = False
            else:
                bot.send_message(message.chat.id, "Команда на перезагрузку уже выполняется.")

        else:
            bot.send_message(message.chat.id, "Команда не распознана. Попробуйте снова.")

def handle_schedule_shutdown(message):
    global scheduled_time  
    target_time = message.text
    if validate_time_format(target_time):
        scheduled_time = target_time  
        result = schedule_shutdown(target_time)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите время в правильном формате HH:MM.")


if __name__ == "__main__":
    show_notification()  
    bot.infinity_polling(none_stop=True)  
