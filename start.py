import subprocess
import os
from playsound import playsound

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
    os.path.join(modules_folder, "config_module.txt"): "test",  # Файл без начального содержимого
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

# Запуск основного ИИ в IDLE
subprocess.Popen(['idle', '-r', mainai])
subprocess.Popen(['idle', '-r', systemos])

# Сообщение о запуске основного ИИ
print("Основной ИИ запущен.")
