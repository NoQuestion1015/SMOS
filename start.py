import subprocess
import os
import time
from playsound import playsound
import signal

# Путь к папке с конфигурационными файлами
config_folder = "config"
sound_folder = "sound"
modules_folder = "modules"
system_modules_folder = "modules/system_modules"
user_modules_folder = "modules/user_modules"

# Файлы ключа распознавания речи и файла состояния
recognition_file = os.path.join(config_folder, "recognition_perm.txt")
cont_start_key_file = os.path.join(config_folder, "cont_start_key.txt")

# Список папок и файлов для создания
folders_to_create = [
    config_folder,
    sound_folder,
    modules_folder,
    system_modules_folder,
    user_modules_folder,
]

files_to_create = {
    recognition_file: "ai",
    cont_start_key_file: "False",  # Начальное состояние, которое можно изменить по мере необходимости
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

# Путь к скриптам
mainai = "mainai.py"
systemos = "systemos.py"
moduleadd = "modules_add.py"
moduleinit = "modules_init.py"
updateproject = "updater.py"

# Запуск скрипта обновления проекта
updateproject_start = subprocess.Popen(['idle', '-r', updateproject])

# Функция для проверки файла cont_start_key.txt
def check_start_key():
    with open(cont_start_key_file, 'r') as f:
        return f.read().strip()

# Функция для завершения процесса IDLE
def kill_idle_process():
    # Находим ID процесса IDLE, запущенного для этого скрипта
    parent_pid = os.getppid()  # Получаем ID родительского процесса
    os.kill(parent_pid, signal.SIGKILL)  # Убиваем процесс IDLE

# Цикл проверки файла на ключ запуска
while True:
    key = check_start_key()
    
    if key == "True":
        print("Ключ True обнаружен, продолжаем запуск...")
        
        # Запуск остальных скриптов
        moduleadd_start = subprocess.Popen(['idle', '-r', moduleadd])
        time.sleep(10)
        moduleinit_start = subprocess.Popen(['idle', '-r', moduleinit])
        time.sleep(5)
        systemos_start = subprocess.Popen(['idle', '-r', systemos])
        mainai_start = subprocess.Popen(['idle', '-r', mainai])

        # Закрытие отработанных модулей
        time.sleep(5)
        moduleadd_start.terminate()
        moduleinit_start.terminate()
        
        print("Основной ИИ запущен.")
        break  # Выходим из цикла, так как работа завершена
    
    elif key == "False":
        print("Ключ False обнаружен, завершаем работу.")
        kill_idle_process()  # Завершаем процесс IDLE
        break  # Выходим из цикла, так как процесс завершен

    time.sleep(1)  # Задержка между проверками файла состояния
