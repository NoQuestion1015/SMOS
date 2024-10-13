import os
import sqlite3
import subprocess
import speech_recognition as sr

# Путь к базе данных и файлам
ACTIVE_DB_PATH = "modules/active_modules.db"
message_file = "modules/local_message.txt"
system_message_file = "config/messagetosystem.txt"
config_file = "config/recognition_perm.txt"

# Инициализация распознавателя
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 300
recognizer.pause_threshold = 1

# Функция для проверки приоритета
def check_recognition_priority():
    try:
        with open(config_file, "r") as file:
            priority = file.read().strip()
            return priority
    except FileNotFoundError:
        print("Файл recognition_perm.txt не найден.")
        return None

# Функция распознавания речи
def recognize_speech():
    with sr.Microphone() as source:
        print("Скажите что-нибудь...")
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        print(f"Вы сказали: {text}")
        return text
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return None
    except sr.RequestError as e:
        print(f"Ошибка сервиса; {e}")
        return None

# Инициализация базы данных
def load_active_modules():
    conn = sqlite3.connect(ACTIVE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT modulename, modulecommands, pathtofile FROM active_modules")
    modules = cursor.fetchall()
    conn.close()
    return modules

# Функция для записи команды в файл local_message.txt
def write_message(command):
    try:
        with open(message_file, "w") as file:
            file.write(command)
        print(f"Команда '{command}' записана в {message_file}")
    except Exception as e:
        print(f"Ошибка при записи команды: {e}")

# Функция для проверки изменений в messagetosystem.txt
def check_system_message_change(last_message):
    try:
        with open(system_message_file, "r") as file:
            current_message = file.read().strip()
            return current_message, current_message != last_message
    except FileNotFoundError:
        print(f"Файл {system_message_file} не найден.")
        return None, False

# Функция для запуска модуля
def launch_module(path_to_file):
    try:
        subprocess.Popen(['idle', '-r', path_to_file])
        print(f"Запуск модуля: {path_to_file}")
    except Exception as e:
        print(f"Ошибка при запуске модуля: {e}")

# Функция для сброса приоритета на AI
def reset_priority_to_ai():
    try:
        with open(config_file, "w") as file:
            file.write("ai")
        print(f"Приоритет сброшен на 'ai' в {config_file}")
    except Exception as e:
        print(f"Ошибка при сбросе приоритета: {e}")

def main():
    last_priority = None  # Храним последнее значение приоритета
    last_system_message = ""  # Храним последнее сообщение из messagetosystem.txt

    # Загрузка активных модулей и команд
    active_modules = load_active_modules()
    commands_dict = {}  # Словарь для команд и путей к модулям

    print("Активные модули и их команды:")
    for modulename, modulecommands, pathtofile in active_modules:
        commands = modulecommands.split(",")
        commands = [cmd.strip().lower() for cmd in commands]
        for command in commands:
            commands_dict[command] = pathtofile
        print(f"Модуль: {modulename}, Команды: {commands}")

    while True:
        current_priority = check_recognition_priority()

        if current_priority == "system":
            if last_priority != "system":
                print("Приоритет системы, начинаем проверку файла messagetosystem.txt.")
                last_priority = "system"

            # Проверка на изменения в файле messagetosystem.txt
            current_system_message, changed = check_system_message_change(last_system_message)
            if changed:
                last_system_message = current_system_message
                print(f"Найдено новое сообщение: {current_system_message}")

                # Проверка, если команда распознана
                command_lower = current_system_message.lower()
                if command_lower in commands_dict:
                    print(f"Распознана команда: {command_lower}")
                    write_message(command_lower)  # Запись команды в local_message.txt
                    path_to_file = commands_dict[command_lower]
                    launch_module(path_to_file)  # Запуск модуля
                else:
                    print("Команда не найдена. Сбрасываем приоритет на AI.")
                    reset_priority_to_ai()  # Сбрасываем приоритет на AI
                    continue  # Возвращаемся к ожиданию

            # Запускаем дальнейшее распознавание речи
            text = recognize_speech()
            if text:
                text_lower = text.lower()

                # Проверка, если команда распознана
                if text_lower in commands_dict:
                    print(f"Распознана команда: {text_lower}")
                    write_message(text_lower)  # Запись команды в local_message.txt
                    path_to_file = commands_dict[text_lower]
                    launch_module(path_to_file)  # Запуск модуля
                else:
                    print("Команда не найдена. Сбрасываем приоритет на AI.")
                    reset_priority_to_ai()  # Сбрасываем приоритет на AI

                    if "выключить программу распознавания" in text_lower:
                        print("Команда для завершения распознавания получена. Выключение программы.")
                        break

        elif current_priority != "system" and last_priority != current_priority:
            print("Приоритет у ИИ. Ожидание переключения на систему...")
            last_priority = current_priority

if __name__ == "__main__":
    main()
