import os
import sqlite3

# Папки с модулями
MODULES_DIR = "modules/"
USER_MODULES_DIR = os.path.join(MODULES_DIR, "user_modules")
SYSTEM_MODULES_DIR = os.path.join(MODULES_DIR, "system_modules")

# Папка для хранения базы данных
DB_FOLDER = "modules/"
DB_NAME = "all_modules.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

# Создаем папку для базы данных, если она не существует
os.makedirs(DB_FOLDER, exist_ok=True)

# Инициализация базы данных
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            filename TEXT,
            description TEXT,
            moduletype TEXT,
            modulenamefolder TEXT,
            path TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Загрузка существующих модулей из базы данных
def load_logged_modules():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM modules')
    modules = {row[0] for row in cursor.fetchall()}
    conn.close()
    return modules

# Запись нового модуля в базу данных
def log_module(name, filename, description, moduletype, modulenamefolder, path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO modules (name, filename, description, moduletype, modulenamefolder, path) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, filename, description, moduletype, modulenamefolder, path))
    conn.commit()
    conn.close()

# Удаление модуля из базы данных
def remove_module(path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM modules WHERE path = ?', (path,))
    conn.commit()
    conn.close()

# Проверка существования папки
def check_folder_exists(path):
    return os.path.exists(path)

# Проверка наличия файла main.py в папке
def check_main_file_exists(folder_path):
    return os.path.isfile(os.path.join(folder_path, "main.py"))

# Проверка и чтение информации из файла module_info.txt
def read_module_info(folder_path):
    info_file_path = os.path.join(folder_path, "module_info.txt")
    if os.path.isfile(info_file_path):
        with open(info_file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            parts = content.split("\n\n", 1)  # Разделение по двум пустым строкам
            if len(parts) == 2:
                name = parts[0].strip()
                description = parts[1].strip()
                return name, description
            else:
                print(f"Ошибка: неправильный формат module_info.txt в папке {folder_path}.")
                return None, None
    else:
        print(f"Ошибка: файл module_info.txt не найден в папке {folder_path}.")
        return None, None

# Поиск новых модулей и удаление отсутствующих
def check_for_new_and_deleted_modules(logged_modules):
    current_modules = {}

    # Проверка существующих модулей
    for path in logged_modules:
        if not check_folder_exists(os.path.dirname(path)):
            print(f"Папка для модуля по пути '{path}' отсутствует. Удаляем модуль...")
            remove_module(path)
        else:
            current_modules[path] = path

    # Поиск новых модулей в папках user_modules и system_modules
    for base_dir, moduletype in [(USER_MODULES_DIR, "user"), (SYSTEM_MODULES_DIR, "system")]:
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path) and check_main_file_exists(folder_path):
                main_file_path = os.path.join(folder_path, "main.py")
                if main_file_path not in logged_modules:
                    current_modules[folder_path] = main_file_path

    new_modules = {name: path for name, path in current_modules.items() if path not in logged_modules}
    return new_modules

# Основной процесс
initialize_database()

# Загрузка существующих модулей из базы данных
logged_modules = load_logged_modules()
new_modules = check_for_new_and_deleted_modules(logged_modules)

# Обработка новых модулей
if new_modules:
    found_modules = []
    for folder_path, main_file_path in new_modules.items():
        filename = "main.py"
        moduletype = "system" if SYSTEM_MODULES_DIR in main_file_path else "user"
        modulenamefolder = os.path.basename(folder_path)

        # Чтение информации о модуле из module_info.txt
        name, description = read_module_info(folder_path)

        if name and description:
            # Добавляем модуль в базу данных
            log_module(name, filename, description, moduletype, modulenamefolder, main_file_path)
            found_modules.append(f"Модуль добавлен: {name}, описание: {description}, тип: {moduletype}, папка: {modulenamefolder}, путь: {main_file_path}")
        else:
            print(f"Ошибка: не удалось прочитать информацию о модуле для {filename} в папке {folder_path}")

    if found_modules:
        print("Новые модули:")
        for module_info in found_modules:
            print(module_info)

# Завершающее сообщение о завершении поиска
print("Поиск завершен.")
