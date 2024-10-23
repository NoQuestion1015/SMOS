import subprocess
import os
from playsound import playsound
import time

# Путь к папке с конфигурационными файлами
config_folder = "config"

# Путь к папке с аудиофайлами
sound_folder = "sound"

modules_folder = "modules"

system_modules_folder = "modules/system_modules"

user_modules_folder = "modules/user_modules"

# Файлы ключа распознавания речи
recognition_file = os.path.join(config_folder, "recognition_perm.txt")

# Список папок и файлов для создания
folders_to_create = [
    config_folder,
    sound_folder,
    modules_folder,
    system_modules_folder,
    user_modules_folder,
]

files_to_create = {
    os.path.join(config_folder, "recognition_perm.txt"): "ai",  # Изначальное содержимое
    os.path.join(config_folder, "needtoai.txt"): None,# Файл без начального содержимого
}

# Функция для создания папок
def create_folders(folders):
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

# Функция для создания файлов
def create_files(files):
    for file_path, initial_content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                if initial_content is not None:
                    f.write(initial_content)

# Проверка и создание папок и файлов
create_folders(folders_to_create)
create_files(files_to_create)

# Проигрываем звуки
playsound(os.path.join(sound_folder, "systemstartedsound.mp3"))
playsound(os.path.join(sound_folder, "systemstarted.mp3"))

# Путь к скрипту основного ИИ
mainai = "mainai.py"
systemos = "systemos.py"
moduleadd = "modules_add.py"
moduleinit = "modules_init.py"

# Запуск основного ИИ в IDLE
mainai_start = subprocess.Popen(['idle', '-r', mainai])
moduleadd_start = subprocess.Popen(['idle', '-r', moduleadd])
time.sleep(10)
moduleinit_start = subprocess.Popen(['idle', '-r', moduleinit])
time.sleep(5)
systemos_start = subprocess.Popen(['idle', '-r', systemos])

# Закрытие отработанных модулей
time.sleep(5)
moduleadd_start.terminate()
moduleinit_start.terminate()

# Сообщение о запуске основного ИИ
print("Основной ИИ запущен.")
