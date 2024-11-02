import speech_recognition as sr
from langchain.chat_models.gigachat import GigaChat
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_gigachat_functions_agent
import pyfiglet
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from gtts import gTTS
import playsound
import threading
import os

# Инициализация распознавателя
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_ratio = 1.5
recognizer.operation_timeout = 5
recognizer.dynamic_energy_adjustment_damping = 0.2
recognizer.pause_threshold = 1

# Кодовые слова для активации и переключения приоритета
activation_keywords = ["смарт", "smart"]
system_keyword = "система"

# Таймер паузы бота
pause_time = 30  # Таймер на 30 секунд
bot_active = False
timer = None

# Файл приоритета распознавания речи
priority_file = 'config/recognition_perm.txt'
ai_priority_value = 'ai'

def start_timer():
    global timer
    if timer:
        timer.cancel()  # Отменяем текущий таймер, если есть
    timer = threading.Timer(pause_time, set_bot_pause)  # Запускаем новый таймер
    timer.start()

def stop_timer():
    global timer
    if timer:
        timer.cancel()  # Останавливаем таймер

def set_bot_pause():
    global bot_active
    bot_active = False
    print("Бот снова на паузе")

def check_priority():
    """Проверяет, находится ли приоритет распознавания речи у ИИ."""
    if os.path.exists(priority_file):
        with open(priority_file, 'r') as file:
            priority = file.read().strip()
            return priority == ai_priority_value
    return False

def recognize_speech():
    with sr.Microphone() as source:
        print("Скажите что-нибудь...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        print(f"Вы сказали: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return None
    except sr.RequestError as e:
        print(f"Ошибка сервиса: {e}")
        return None
    except TimeoutError:
        print("Ошибка: превышено время ожидания.")
        return None


def check_for_system_keyword(text):
    """Проверяет, начинается ли запрос с кодового слова 'система' и записывает запрос системы в файл."""
    if text.startswith(system_keyword):
        # Отделяем команду, которая идёт после слова "система"
        system_command = text[len(system_keyword):].strip()

        # Сменяем приоритет на system
        with open(priority_file, 'w') as file:
            file.write("system")
        print("Приоритет сменён на system.")

        # Записываем команду системы в файл messagetosystem.txt
        system_message_file = 'config/messagetosystem.txt'
        with open(system_message_file, 'w') as file:
            file.write(system_command)
        print(f"Запрос системы записан в {system_message_file}: {system_command}")
        
        return True
    return False

@tool
def draw_banner(number: str) -> str:
    """Рисует баннер с текстом результатов кода в виде Ascii-графики"""
    pyfiglet.print_figlet(number, font="epic")
    return "Draw complete"

def synthesize_speech(text: str):
    """Синтезирует речь из текста и воспроизводит её"""
    stop_timer()  # Останавливаем таймер на время озвучивания
    tts = gTTS(text, lang='ru')
    audio_file = 'audio.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file, True)
    start_timer()  # Возобновляем таймер после озвучивания

search_tool = DuckDuckGoSearchRun()
new_tools = [search_tool, draw_banner]

giga = GigaChat(credentials="ODZjNDQ0ZjEtNjYwYS00NzUzLTlkNjgtYjVjZTk2ZTRjYWQzOmViZDQyNWVkLTVlZTctNGVlNC05M2MzLWFhOTMzZGRmOWRmMg==", scope="GIGACHAT_API_PERS", model="GigaChat", verify_ssl_certs=False)

agent = create_gigachat_functions_agent(giga, new_tools)

agent_executor = AgentExecutor(
    agent=agent,
    tools=new_tools,
    verbose=False,
)

chat_history = []
priority_message_printed = False  # Флаг для контроля вывода сообщения

def handle_request(text):
    start_timer()  # Сбрасываем таймер при каждом новом запросе
    print(f"Пользователь: {text}")
    
    if check_for_system_keyword(text):
        synthesize_speech("Приоритет сменён на системные команды.")
        return  # Не отправляем запрос ИИ, если приоритет сменился на system

    result = agent_executor.invoke(
        {
            "chat_history": chat_history,
            "input": text,
        }
    )
    response = result["output"]
    chat_history.append(HumanMessage(content=text))
    chat_history.append(AIMessage(content=response))
    
    print(f"Агент: {response}")
    
    # Озвучивание ответа бота
    synthesize_speech(response)

def main():
    global bot_active, priority_message_printed
    while True:
        # Проверяем приоритет перед началом распознавания речи
        if not check_priority():
            if not priority_message_printed:
                print("Распознавание речи отключено: приоритет не у ИИ.")
                priority_message_printed = True
            continue  # Пропускаем итерацию, если приоритет не у ИИ
        else:
            if priority_message_printed:
                print("Приоритет вернулся к ИИ, продолжаем распознавание.")
                priority_message_printed = False

        text = recognize_speech()
        if text:
            # Проверяем на команду выключения
            if "выключить программу распознавания" in text:
                print("Команда для завершения распознавания получена. Выключение программы.")
                break

            # Проверяем на кодовое слово 'система'
            if check_for_system_keyword(text):
                continue  # Пропускаем дальнейшую обработку, если найдено кодовое слово

            # Если бот не активен, ждем кодового слова активации
            if not bot_active:
                if any(keyword in text for keyword in activation_keywords):
                    bot_active = True
                    print("Бот активирован. Введите свой запрос.")
                    
                    # Отделяем запрос от кодового слова, если есть
                    for keyword in activation_keywords:
                        if text.startswith(keyword):
                            text = text.replace(keyword, "").strip()
                            break
                    
                    if text:
                        # Если есть запрос после активации, сразу отправляем его
                        handle_request(text)
                    else:
                        # Иначе ждём запроса от пользователя
                        synthesize_speech("Введите свой запрос")
                    
                    start_timer()  # Запускаем таймер на 30 секунд
            else:
                handle_request(text)

if __name__ == "__main__":
    main()
