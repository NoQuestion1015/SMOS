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
def write_message(message):
    try:
        with open(message_file, "w") as file:
            file.write(message)
        print(f"Сообщение '{message}' записано в {message_file}")
    except Exception as e:
        print(f"Ошибка при записи сообщения: {e}")

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
    # Очищаем файл messagetosystem.txt при запуске программы
    try:
        with open(system_message_file, "w") as file:
            file.write("")  # Очищаем содержимое
        print(f"Файл {system_message_file} успешно очищен.")
    except Exception as e:
        print(f"Ошибка при очистке {system_message_file}: {e}")

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
        # Проверка текущего приоритета
        current_priority = check_recognition_priority()

        if current_priority == "system":
            print("Приоритет системы, начинаем проверку файла messagetosystem.txt.")

            # Проверка изменения файла messagetosystem.txt
            system_message, changed = check_system_message_change(last_system_message)
            if changed:
                print(f"Найдено новое сообщение: {system_message}")
                last_system_message = system_message  # Обновляем последнее сообщение

                # Проверка, содержит ли сообщение команду
                for command, path_to_file in commands_dict.items():
                    if command in system_message.lower():
                        print(f"Команда '{command}' найдена в сообщении.")
                        write_message(system_message)  # Записываем всю команду в local_message.txt
                        launch_module(path_to_file)    # Запуск модуля
                        break
                else:
                    print("Команда не найдена. Переключение на ИИ.")
                    reset_priority_to_ai()
                    continue

            # Запуск распознавания речи
            print("Скажите что-нибудь...")
            text = recognize_speech()
            if text:
                for command, path_to_file in commands_dict.items():
                    if command in text.lower():
                        print(f"Команда '{command}' найдена в распознанной речи.")
                        write_message(text)  # Записываем всю команду в local_message.txt
                        launch_module(path_to_file)    # Запуск модуля
                        break
                else:
                    print("Команда не найдена. Переключение на ИИ.")
                    reset_priority_to_ai()

        elif current_priority != "system" and last_priority != current_priority:
            print("Приоритет у ИИ. Ожидание переключения на систему...")
            last_priority = current_priority

if __name__ == "__main__":
    main()
