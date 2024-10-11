import os
import sqlite3

# Путь к базам данных
ACTIVE_DB_PATH = "modules/active_modules.db"
ALL_DB_PATH = "modules/all_modules.db"
COMMANDS_FILE = "modules/local_command.txt"

def initialize_database():
    # Инициализация базы данных all_modules.db
    conn = sqlite3.connect(ALL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            name TEXT,
            filename TEXT PRIMARY KEY,
            command TEXT,
            description TEXT,
            moduletype TEXT,
            modulenamefolder TEXT
            path TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # Инициализация базы данных active_modules.db
    conn = sqlite3.connect(ACTIVE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_modules (
            modulename TEXT,
            modulecommands TEXT,
            moduletype TEXT,
            filename TEXT,
            modulenamefolder TEXT,
            pathtofile TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_active_commands_file():
    # Создание файла active_commands.txt
    with open(COMMANDS_FILE, "w") as file:
        file.write("")  # Создаем пустой файл

def load_modules():
    # Загружаем модули из базы данных all_modules.db
    conn = sqlite3.connect(ALL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modules")
    modules = cursor.fetchall()
    conn.close()

    return modules

def activate_modules():
    # Загружаем модули
    modules = load_modules()
    
    # Соединяем с базой active_modules.db
    conn = sqlite3.connect(ACTIVE_DB_PATH)
    cursor = conn.cursor()

    for module in modules:
        modulename = module[0]
        filename = module[1]
        modulenamefolder = module[5]
        moduletype = module[4]

        # Определяем путь к папке модуля в зависимости от типа модуля
        if moduletype == "system":
            module_folder_path = os.path.join("modules", "system_modules", modulenamefolder)
        elif moduletype == "user":
            module_folder_path = os.path.join("modules", "user_modules", modulenamefolder)
        else:
            print(f"Ошибка: Неизвестный тип модуля '{moduletype}' для модуля '{modulename}'.")
            continue
        
        # Отладочные сообщения
        print(f"Проверяем папку модуля: {module_folder_path}")
        
        # Проверяем наличие папки модуля
        if os.path.exists(module_folder_path):
            print(f"Папка модуля '{modulenamefolder}' найдена.")
            # Проверяем наличие файла с именем из базы
            script_file_path = os.path.join(module_folder_path, filename)
            command_file_path = os.path.join(module_folder_path, "command.txt")

            if os.path.exists(script_file_path) and os.path.exists(command_file_path):
                # Читаем команды из command.txt
                with open(command_file_path, "r") as command_file:
                    commands = command_file.read().strip()
                
                # Формируем полный путь до файла
                full_path_to_file = os.path.join("modules", moduletype + "_modules", modulenamefolder, filename)
                
                # Добавляем модуль в active_modules.db
                cursor.execute("INSERT INTO active_modules (modulename, modulecommands, moduletype, filename, modulenamefolder, pathtofile) VALUES (?, ?, ?, ?, ?, ?)", 
                               (modulename, commands, moduletype, filename, modulenamefolder, full_path_to_file))
                print(f"Модуль '{modulename}' активирован и добавлен в базу данных активных модулей.")
            else:
                if not os.path.exists(script_file_path):
                    print(f"Ошибка: Файл скрипта '{filename}' не найден в '{module_folder_path}'.")
                if not os.path.exists(command_file_path):
                    print(f"Ошибка: Файл 'command.txt' не найден в '{module_folder_path}'.")
        else:
            print(f"Ошибка: Папка модуля '{modulenamefolder}' не найдена.")

    conn.commit()
    conn.close()

def main():
    initialize_database()
    create_active_commands_file()
    activate_modules()

if __name__ == "__main__":
    main()
