import wget
import os
import zipfile
import shutil
import playsound
import subprocess
import speech_recognition as sr
import time

# Инициализация распознавателя
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 300
recognizer.pause_threshold = 1

# Укажите имя пользователя и название репозитория
username = "NoQuestion1015"
repository = "SMOS"

# Путь к файлу cont_start_key.txt
start_key_path = os.path.join(os.getcwd(), "config", "cont_start_key.txt")

# Функция для проверки и загрузки обновлений
def check_for_updates(save_directory):
    try:
        # Создание папки для проверки обновлений
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
            print(f"Создана папка для обновлений: {save_directory}")
        
        # Укажите путь, куда будет сохранён файл
        zip_file_path = os.path.join(save_directory, f"{repository}.zip")

        # Попытка загрузить ZIP-архив с ветки master, затем с ветки main
        try:
            url = f"https://github.com/{username}/{repository}/archive/master.zip"
            print("Загрузка обновления с ветки master...")
            wget.download(url, zip_file_path)
        except Exception as e:
            print(f"Не удалось загрузить с ветки master: {e}")
            try:
                url = f"https://github.com/{username}/{repository}/archive/main.zip"
                print("Загрузка обновления с ветки main...")
                wget.download(url, zip_file_path)
            except Exception as e:
                print(f"Не удалось загрузить с ветки main: {e}")
                return
        
        print(f"\nЗагрузка завершена: {zip_file_path}")

        # Распаковка ZIP-архива
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(save_directory)

        # Получение имени папки проекта после разархивации
        extracted_folder = os.path.join(save_directory, f"{repository}-master")
        if not os.path.exists(extracted_folder):
            extracted_folder = os.path.join(save_directory, f"{repository}-main")

        # Проверка наличия файла projectversion.txt в загруженной версии
        new_version_file_path = os.path.join(extracted_folder, "config", "projectversion.txt")
        if not os.path.exists(new_version_file_path):
            print("Файл версии в скачанном проекте не найден.")
            return

        # Чтение новой версии
        with open(new_version_file_path, 'r') as file:
            new_version = file.read().strip()

        # Проверка текущей версии
        current_version_file_path = os.path.join(os.getcwd(), "config", "projectversion.txt")
        if not os.path.exists(current_version_file_path):
            print("Файл версии текущего проекта не найден.")
            return

        with open(current_version_file_path, 'r') as file:
            current_version = file.read().strip()

        # Сравнение версий
        if new_version == current_version:
            print("Обновление не требуется. Текущая версия актуальна.")
            shutil.rmtree(save_directory)
            print(f"Папка обновления удалена: {save_directory}")
        elif is_newer_version(new_version, current_version):
            print(f"Доступна новая версия: {new_version}. Текущая версия: {current_version}.")
            ask_for_update(save_directory, extracted_folder)
        else:
            print("Вы используете последнюю версию.")

    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")

# Функция сравнения версий
def is_newer_version(new_version, current_version):
    new_version_parts = list(map(int, new_version.split('.')))
    current_version_parts = list(map(int, current_version.split('.')))

    for new, current in zip(new_version_parts, current_version_parts):
        if new > current:
            return True
        elif new < current:
            return False

    return len(new_version_parts) > len(current_version_parts)

# Функция запроса подтверждения обновления
def ask_for_update(save_directory, extracted_folder):
    try:
        playsound.playsound(os.path.join(os.getcwd(), "sound", "updateuserrequest.mp3"))
        print("Ожидание подтверждения от пользователя...")

        while True:
            text = recognize_speech()
            if text:
                text_lower = text.lower()
                if any(phrase in text_lower for phrase in ["установить сейчас", "начать установку", "обновить"]):
                    print("Подтверждение установки получено.")
                    # Запись False в cont_start_key.txt для отключения запуска
                    with open(start_key_path, 'w') as file:
                        file.write("False")
                    install_update(save_directory, extracted_folder)
                    break
                elif any(phrase in text_lower for phrase in ["установить позже", "отложить", "отменить установку"]):
                    # Запись True в cont_start_key.txt для разрешения запуска позже
                    with open(start_key_path, 'w') as file:
                        file.write("True")
                    playsound.playsound(os.path.join(os.getcwd(), "sound", "updatedelayed.mp3"))
                    print("Установка отложена.")
                    shutil.rmtree(save_directory)
                    print(f"Папка обновления удалена: {save_directory}")
                    break

    except Exception as e:
        print(f"Ошибка при запросе подтверждения: {e}")

# Функция распознавания речи
def recognize_speech():
    try:
        with sr.Microphone() as source:
            print("Скажите что-нибудь...")
            audio = recognizer.listen(source)
        
        text = recognizer.recognize_google(audio, language="ru-RU")
        print(f"Вы сказали: {text}")
        return text
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return None
    except sr.RequestError as e:
        print(f"Ошибка сервиса; {e}")
        return None

# Логика установки обновления
def install_update(save_directory, extracted_folder):
    try:
        playsound.playsound(os.path.join(os.getcwd(), "sound", "updatestarted.mp3"))
        print("Установка обновления началась...")

        # Создание архива текущей версии
        archive_path = os.path.join(save_directory, "backup.zip")
        with zipfile.ZipFile(archive_path, 'w') as backup_zip:
            for foldername, subfolders, filenames in os.walk(os.getcwd()):
                if save_directory in foldername:
                    continue
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    backup_zip.write(file_path, os.path.relpath(file_path, os.getcwd()))
        
        print(f"Создан архив с резервной копией: {archive_path}")

        # Удаление старой версии (кроме папки checkupdate)
        for foldername, subfolders, filenames in os.walk(os.getcwd()):
            if save_directory in foldername:
                continue
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                os.remove(file_path)
        
        print("Старая версия удалена.")

        # Копирование новой версии
        for foldername, subfolders, filenames in os.walk(extracted_folder):
            for filename in filenames:
                src_path = os.path.join(foldername, filename)
                dest_path = os.path.join(os.getcwd(), os.path.relpath(src_path, extracted_folder))
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy(src_path, dest_path)
        
        print("Новая версия установлена.")
        playsound.playsound(os.path.join(os.getcwd(), "sound", "updatedone.mp3"))

        # Запуск новой версии
        print("Запуск новой версии...")
        subprocess.Popen(['python', 'start.py'])
        print("Новая версия запущена.")
        exit()

    except Exception as e:
        print(f"Ошибка при установке обновления: {e}")

# Укажите путь к папке для обновлений
check_for_updates("checkupdate")
