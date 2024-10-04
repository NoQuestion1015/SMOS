import speech_recognition as sr
import time

# Инициализация распознавателя
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 300
recognizer.pause_threshold = 1

# Путь к файлу с приоритетом распознавания
priority_file = "config/recognition_perm.txt"

def check_priority():
    """Функция для проверки текущего приоритета распознавания речи."""
    try:
        with open(priority_file, 'r') as file:
            priority = file.read().strip()
        return priority == "system"
    except FileNotFoundError:
        print("Файл priority не найден.")
        return False

def recognize_speech():
    """Функция для распознавания речи."""
    with sr.Microphone() as source:
        print("Скажите что-нибудь...")
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        print(f"Вы сказали: {text}")
        return text
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return None
    except sr.RequestError as e:
        print(f"Ошибка сервиса; {e}")
        return None

def main():
    priority_notified = False  # Флаг, чтобы вывести сообщение только один раз
    while True:
        if check_priority():
            # Сбрасываем флаг уведомления, если приоритет вернулся к системе
            priority_notified = False
            # Распознавание речи
            text = recognize_speech()
            if text:
                if "выключить программу распознавания" in text.lower():
                    print("Команда для завершения распознавания получена. Выключение программы.")
                    break
        else:
            if not priority_notified:
                print("Приоритет не у системы. Ожидание...")
                priority_notified = True
            time.sleep(1)  # Ожидание перед следующей проверкой

if __name__ == "__main__":
    main()
