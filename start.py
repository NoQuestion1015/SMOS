import subprocess
import os
from playsound import playsound

# Путь к папке с конфигурационными файлами
config_folder = "config"

# Путь к папке с аудиофайлами
sound_folder = "sound"

# Файл ключа распознавания речи
recognition_file = os.path.join(config_folder, "recognition_perm.txt")

# Проверка и создание файла recognition_perm.txt
def check_or_create_recognition_file():
    # Создаем папку config, если её нет
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)

    # Создаем файл или очищаем его, если он существует, и записываем 'ai'
    with open(recognition_file, 'w') as f:
        f.write('ai')


# Проверка конфигурационного файла
check_or_create_recognition_file()

# Файлы для воспроизведения
sound_startup_1 = os.path.join(sound_folder, "systemstartedsound.mp3")
sound_startup_2 = os.path.join(sound_folder, "systemstarted.mp3")

# Проигрываем звуки
playsound(sound_startup_1)
playsound(sound_startup_2)

# Путь к скрипту основного ИИ
mainai = "mainai.py"
systemos = "systemos.py"

# Запуск основного ИИ в IDLE
subprocess.Popen(['idle', '-r', mainai])
subprocess.Popen(['idle', '-r', systemos])

# Сообщение о запуске основного ИИ
print("Основной ИИ запущен.")
