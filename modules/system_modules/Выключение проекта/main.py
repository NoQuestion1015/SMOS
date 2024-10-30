import psutil
import os

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

# Основная функция завершения процессов
def terminate_idle_processes(target_files):
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if process.info['name'] == 'idle':
                cmdline = process.info['cmdline']
                for file_name in target_files:
                    if file_name in cmdline:
                        os.kill(process.info['pid'], 9)
                        print(f"Процесс IDLE с файлом {file_name} завершен.")
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Не удалось завершить процесс: {e}")

# Функция для работы с командами из local_message.txt
def handle_shutdown_command():
    # Получение пути к local_message.txt
    script_directory = os.path.dirname(__file__)
    project_path = find_project_root(script_directory)
    if not project_path:
        print("Не удалось найти корневую папку 'SMOS'. Завершение работы.")
        return

    # Путь к файлу команд и к файлу с активными процессами
    message_path = os.path.join(project_path, 'modules', 'local_message.txt')
    config_path = os.path.join(project_path, 'config', 'activeprocessnow.txt')

    # Команды для разных типов завершения работы
    standard_shutdown_commands = {
        "выключить систему", "выключение", "выключение системы",
        "завершение работы", "завершить работу"
    }
    not_implemented_shutdown_commands = {
        "выключить компьютер", "выключение компьютера", "отключить компьютер"
    }

    # Чтение команды из файла local_message.txt
    try:
        with open(message_path, 'r') as file:
            command = file.read().strip()
    except FileNotFoundError:
        print(f"Файл {message_path} не найден.")
        return

    # Обработка команды
    if command in standard_shutdown_commands:
        try:
            with open(config_path, 'r') as file:
                target_files = [file_name.strip() for file_name in file.readlines()]
            print(f"Файлы для завершения: {target_files}")
            terminate_idle_processes(target_files)
        except FileNotFoundError:
            print(f"Файл {config_path} не найден.")
    elif command in not_implemented_shutdown_commands:
        print("Данная функция пока не реализована.")
    else:
        print("Неизвестная команда завершения работы.")

# Запуск обработчика команды завершения
handle_shutdown_command()
