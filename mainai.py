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

# Инициализация распознавателя
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_ratio = 1.5
recognizer.operation_timeout = 5
recognizer.dynamic_energy_adjustment_damping = 0.2
recognizer.pause_threshold = 1

# Кодовое слово для активации бота
activation_keywords = ["смарт", "smart"]

# Таймер паузы бота
pause_time = 30  # Таймер на 30 секунд
bot_active = False
timer = None

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

giga = GigaChat(credentials="MzZkZmNkMWUtMDQyNC00YzVlLWI1ZjUtNTAwNjI0YzJjOTg3OjVmZDM3NWE5LTUwNTYtNDNjNi05MGQ1LWY3OWM3MjdhZDU2Yg==", scope="GIGACHAT_API_PERS", model="GigaChat", verify_ssl_certs=False)

agent = create_gigachat_functions_agent(giga, new_tools)

agent_executor = AgentExecutor(
    agent=agent,
    tools=new_tools,
    verbose=False,
)

chat_history = []

def main():
    global bot_active
    while True:
        text = recognize_speech()
        if text:
            # Проверяем на команду выключения
            if "выключить программу распознавания" in text:
                print("Команда для завершения распознавания получена. Выключение программы.")
                break

            # Если бот не активен, ждем кодового слова
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

def handle_request(text):
    start_timer()  # Сбрасываем таймер при каждом новом запросе
    print(f"Пользователь: {text}")
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

if __name__ == "__main__":
    main()
