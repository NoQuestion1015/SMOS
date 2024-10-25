import sqlite3
import time
import os
from datetime import datetime
from gtts import gTTS
import playsound
import speech_recognition as sr

# Функция для поиска корневой папки проекта
def find_project_root(start_path):
    current_path = start_path

    while True:
        if os.path.basename(current_path) == 'SMOS':
            print(f"Корневая папка 'SMOS' найдена: {current_path}")
            return current_path
        
        parent_path = os.path.dirname(current_path)
        
        if parent_path == current_path:
            print("Корневая папка 'SMOS' не найдена.")
            return None
        
        current_path = parent_path

# Получаем путь к директории скрипта и определяем корневой путь проекта
script_directory = os.path.dirname(__file__)
project_path = find_project_root(script_directory)

# Проверяем, был ли найден корневой путь проекта
if not project_path:
    raise Exception("Корневая папка 'SMOS' не найдена. Проверьте структуру проекта.")

# Устанавливаем пути к файлам на основе найденного корня проекта
db_path = os.path.join(project_path, 'config', 'notifications.db')
recognition_perm_path = os.path.join(project_path, 'config', 'recognition_perm.txt')
notify_confirm_sound = os.path.join(project_path, 'sound', 'notify_confirm.mp3')
notify_confirmed_sound = os.path.join(project_path, 'sound', 'notify_confirmed.mp3')
notification_sound = os.path.join(project_path, 'sound', 'notifysound.mp3')

# Хранение ID уже обработанных уведомлений
processed_notifications = set()

# Функция для создания базы данных уведомлений
def create_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            importance INTEGER NOT NULL,  -- Уровень важности от 1 до 10
            need_confirm TEXT NOT NULL DEFAULT 'false',  -- Подтверждение: true или false
            starttime TEXT,  -- Время отложенного уведомления (может быть пустым)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Функция для проверки новых уведомлений
def check_notifications():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications WHERE importance > 0')
    notifications = cursor.fetchall()
    conn.close()
    return notifications

# Функция для изменения приоритета системы
def change_system_priority(priority):
    with open(recognition_perm_path, 'w') as f:
        f.write(priority)

# Функция для воспроизведения звукового файла
def play_sound(file_path):
    playsound.playsound(file_path, True)

# Функция для синтеза речи и воспроизведения
def speak(text):
    tts = gTTS(text, lang='ru')
    audio = 'audio.mp3'
    tts.save(audio)
    playsound.playsound(audio, True)

# Функция для распознавания речи (код простой реализации)
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слушаю...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="ru-RU").lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

# Функция для проверки, нужно ли проигрывать уведомление (с учетом starttime)
def should_play_notification(starttime):
    if not starttime:  # Если starttime пустое, играем сразу
        return True
    current_time = datetime.now()
    notif_time = datetime.strptime(starttime, '%d:%m:%y %H:%M:%S')
    return current_time >= notif_time  # Играем, если текущее время >= starttime

# Функция для обработки уведомлений
def handle_notifications():
    global processed_notifications

    while True:
        notifications = check_notifications()
        
        for notification in notifications:
            notification_id, name, description, notif_type, importance, need_confirm, starttime, timestamp = notification

            if notification_id not in processed_notifications and should_play_notification(starttime):
                if importance < 5:
                    play_sound(notification_sound)

                elif importance >= 5:
                    previous_priority = open(recognition_perm_path).read().strip()
                    change_system_priority('notify')

                    speak(f"Важное уведомление: {name}. {description}")

                    if need_confirm == 'true':
                        play_sound(notify_confirm_sound)

                        confirmed = False
                        while not confirmed:
                            user_input = recognize_speech()
                            confirm_words = ['ок', 'окей', 'да', 'хорошо', 'подтверждаю', 'подтвердил', 'принял', 'есть', 'подтверждение']

                            if user_input in confirm_words:
                                play_sound(notify_confirmed_sound)
                                confirmed = True

                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM notifications WHERE id = ?', (notification_id,))
                        conn.commit()
                        conn.close()

                    change_system_priority(previous_priority)

                processed_notifications.add(notification_id)

        time.sleep(1)

# Основная программа
if __name__ == '__main__':
    create_db()
    handle_notifications()
