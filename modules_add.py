import os
import sqlite3
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

# Папка с модулями
MODULES_DIR = "modules/"

# Папка, где будет храниться база данных
DB_FOLDER = "modules/"  # Например, папка database в текущей директории
DB_NAME = "all_modules.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)  # Полный путь к базе данных

# Убедимся, что папка для базы данных существует
os.makedirs(DB_FOLDER, exist_ok=True)

# Функция для создания базы данных и таблицы
def initialize_database():
    conn = sqlite3.connect(DB_PATH)  # Используем путь к базе данных
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            name TEXT,
            filename TEXT PRIMARY KEY,
            command TEXT,
            description TEXT,
            moduletype TEXT,
            modulenamefolder TEXT,
            path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Функция для загрузки существующих модулей из базы данных
def load_logged_modules():
    conn = sqlite3.connect(DB_PATH)  # Используем путь к базе данных
    cursor = conn.cursor()
    cursor.execute('SELECT filename, path FROM modules')
    modules = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return modules

# Функция для добавления нового модуля в базу данных
def log_module(module_name, filename, command, description, moduletype, modulenamefolder, path):
    conn = sqlite3.connect(DB_PATH)  # Используем путь к базе данных
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO modules (name, filename, command, description, moduletype, modulenamefolder, path) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                   (module_name, filename, command, description, moduletype, modulenamefolder, path))
    conn.commit()
    conn.close()

# Функция для удаления модуля из базы данных
def remove_module(filename):
    conn = sqlite3.connect(DB_PATH)  # Используем путь к базе данных
    cursor = conn.cursor()
    cursor.execute('DELETE FROM modules WHERE filename = ?', (filename,))
    conn.commit()
    conn.close()

# Функция для проверки наличия папки
def check_folder_exists(path):
    return os.path.exists(path)

# Функция для сканирования всех подпапок в папке modules и поиска новых/удалённых модулей
def check_for_new_and_deleted_modules(logged_modules):
    current_modules = {}
    
    # Проверяем существующие модули
    for module_name, path in logged_modules.items():
        if not check_folder_exists(os.path.dirname(path)):
            print(f"Папка для модуля '{module_name}' отсутствует. Удаляем модуль...")
            remove_module(module_name)  # Удаляем модуль из базы данных
        else:
            current_modules[module_name] = path  # Оставляем существующий модуль

    # Поиск новых модулей
    for root, dirs, files in os.walk(MODULES_DIR):
        for filename in files:
            if filename.endswith(".py"):
                folder_name = os.path.basename(root)
                full_path = os.path.join(root, filename)
                current_modules[filename] = full_path

    new_modules = {filename: path for filename, path in current_modules.items() if filename not in logged_modules}
    return new_modules

# Функция для анализа модуля с помощью GigaChat
def analyze_module_with_giga(module_code, query):
    payload = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content="Ты являешься управляющим добавления модулей. " + query
            )
        ],
        temperature=0.1,
        max_tokens=200,
    )

    with GigaChat(credentials="ODZjNDQ0ZjEtNjYwYS00NzUzLTlkNjgtYjVjZTk2ZTRjYWQzOmFkMzE3MDAwLWI5ZmItNGJkYi1iNjNhLTMwYzNjNWRjYmM0MA==", verify_ssl_certs=False) as giga:
        payload.messages.append(Messages(role=MessagesRole.USER, content=module_code))
        response = giga.chat(payload)
        return response.choices[0].message.content if response.choices else None

# Основной цикл работы
initialize_database()  # Инициализация базы данных при запуске

# Загрузка существующего лога
logged_modules = load_logged_modules()
new_modules = check_for_new_and_deleted_modules(logged_modules)

# Обработка новых модулей
if new_modules:
    found_modules = []  # Список для хранения информации о найденных модулях
    for module_name, module_path in new_modules.items():
        # Получаем имя файла
        filename = os.path.basename(module_path)
        
        # Определяем тип модуля по папке, в которой он находится
        moduletype = "user"  # Предполагаем, что все модули являются пользовательскими
        modulenamefolder = os.path.basename(os.path.dirname(module_path))  # Получаем имя папки с модулем
        
        if 'system_modules' in module_path:
            moduletype = "system"

        # Чтение кода нового модуля
        try:
            with open(module_path, "r") as file:
                module_code = file.read()
        except Exception as e:
            print(f"Ошибка при чтении файла {filename}: {e}")
            continue  # Пропускаем модуль, если произошла ошибка

        print(f"Найден новый модуль: {filename}. Отправляем на анализ...")

        # 1. Анализ кода модуля
        analysis_query = "Вот код модуля:\n" + module_code + "\nОбъясни, что делает этот код, без лишних слов."
        description = analyze_module_with_giga(module_code, analysis_query)

        if description:
            # 2. Генерация названия модуля
            name_query = f"Опиши модуль: {description}. Придумай название для него, без лишних слов. Придумай название для него, без лишних слов.(на русском)"
            module_name = analyze_module_with_giga(module_code, name_query)

            if module_name:
                # 3. Генерация команды для запуска модуля
                command_query = f"На основе названия '{module_name}' и описания '{description}',  придумай команду для запуска модуля, команда должна быть простой и на русском языке, по типу открой бразуер или открой графический редактор, создай напоминание и так далее, без лишних слов."
                command = analyze_module_with_giga(module_code, command_query)

                if command:
                    # Добавляем модуль в базу данных
                    log_module(module_name, filename, command, description, moduletype, modulenamefolder, module_path)
                    found_modules.append(f"Модуль добавлен: {module_name}, команда: {command}, описание: {description}, тип: {moduletype}, папка: {modulenamefolder}, путь: {module_path}")
                else:
                    print(f"Не удалось получить команду для модуля: {filename}")
            else:
                print(f"Не удалось получить название для модуля: {filename}")
        else:
            print(f"Не удалось проанализировать модуль: {filename}")

    if found_modules:
        print("Новые модули:")
        for module_info in found_modules:
            print(module_info)

# В конце программы выводим, если были найдены новые или удаленные модули
print("Поиск завершен.")
