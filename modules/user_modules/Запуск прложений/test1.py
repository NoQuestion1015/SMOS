import os
import subprocess
import re
import shlex

# Функция для получения приложений из .desktop файлов
def get_graphical_apps():
    apps = []
    desktop_dirs = [
        '/usr/share/applications', 
        os.path.expanduser('~/.local/share/applications')
    ]
    
    for directory in desktop_dirs:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith('.desktop'):
                    filepath = os.path.join(directory, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            app_info = {}
                            for line in file:
                                if line.startswith('Name='):
                                    app_info['name'] = line.split('=')[1].strip()
                                elif line.startswith('Exec='):
                                    # Убираем аргументы командной строки вроде %U
                                    exec_command = re.sub(r' %\w', '', line.split('=')[1].strip())
                                    app_info['exec'] = exec_command
                            if 'name' in app_info and 'exec' in app_info:
                                apps.append(app_info)
                    except Exception as e:
                        print(f"Ошибка при чтении {filename}: {e}")
    
    return apps

# Функция для имитации запуска приложения в терминале
def launch_application(command):
    try:
        # Используем shlex для разделения команды на аргументы
        print(f"Запуск {command}...")
        subprocess.Popen(shlex.split(command))
    except Exception as e:
        print(f"Не удалось запустить приложение: {e}")

# Основная логика программы
def main():
    apps = get_graphical_apps()

    if not apps:
        print("Не найдено приложений.")
        return

    # Выводим список всех приложений с порядковым номером
    for i, app in enumerate(apps):
        print(f"{i + 1}. {app['name']}")

    # Пользователь выбирает номер приложения
    try:
        choice = int(input("\nВыберите номер приложения для запуска: ")) - 1
        if 0 <= choice < len(apps):
            print(f"Запуск приложения: {apps[choice]['name']}")
            launch_application(apps[choice]['exec'])
        else:
            print("Неправильный выбор.")
    except ValueError:
        print("Нужно ввести число.")

if __name__ == "__main__":
    main()
