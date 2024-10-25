import sqlite3
from datetime import datetime

# Путь к базе данных уведомлений
db_path = '/home/noquestion/Рабочий стол/SMOS/Ключ для дальнейшего запуска/Тест 2/config/notifications.db'

# Функция для создания базы данных (если она еще не создана)
def create_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            importance INTEGER NOT NULL,  -- Уровень важности от 1 до 10
            need_confirm TEXT NOT NULL DEFAULT 'false',  -- Подтверждение: true или false
            starttime TEXT,  -- Время отложенного уведомления (может быть пустым)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Функция для добавления нового уведомления в базу данных
def add_notification(name, description, notif_type, importance, need_confirm, starttime):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notifications (name, description, type, importance, need_confirm, starttime)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, description, notif_type, importance, need_confirm, starttime))
    conn.commit()
    conn.close()

# Функция для получения данных от пользователя
def get_user_input():
    print("Введите данные для нового уведомления:")
    
    name = input("Название: ")
    description = input("Описание: ")
    notif_type = input("Тип (системное/пользовательское): ")
    
    while True:
        try:
            importance = int(input("Важность (1-10): "))
            if 1 <= importance <= 10:
                break
            else:
                print("Пожалуйста, введите число от 1 до 10.")
        except ValueError:
            print("Пожалуйста, введите корректное число.")

    need_confirm = input("Требуется ли подтверждение (true/false): ").lower()
    need_confirm = 'true' if need_confirm == 'true' else 'false'

    starttime = input("Время уведомления (в формате ДД:ММ:ГГ ЧЧ:ММ:СС или оставьте пустым для немедленного показа): ")

    # Если введена пустая строка для времени, устанавливаем starttime в None
    starttime = starttime if starttime.strip() else None

    return name, description, notif_type, importance, need_confirm, starttime

# Основная функция тестирования
def main():
    create_db()
    name, description, notif_type, importance, need_confirm, starttime = get_user_input()
    add_notification(name, description, notif_type, importance, need_confirm, starttime)
    print("Уведомление успешно добавлено в базу данных.")

if __name__ == '__main__':
    main()
