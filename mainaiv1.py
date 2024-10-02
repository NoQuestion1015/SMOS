import time
import threading
import speech_recognition as sr
from langchain.chat_models.gigachat import GigaChat
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_gigachat_functions_agent
from langchain_core.messages import AIMessage, HumanMessage
from gtts import gTTS
import playsound

# Инициализация распознавателя
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 100
recognizer.pause_threshold = 0.5
recognizer.dynamic_energy_ratio = 1.5
recognizer.operation_timeout = None
recognizer.dynamic_energy_adjustment_damping = 0.2

# Инициализация переменных
is_active = False
timer = None
timeout_duration = 30  # Время таймера в секундах
chat_history = []

# Инициализация GigaChat
giga = GigaChat(credentials="MzZkZmNkMWUtMDQyNC00YzVlLWI1ZjUtNTAwNjI0YzJjOTg3OjVmZDM3NWE5LTUwNTYtNDNjNi05MGQ1LWY3OWM3MjdhZDU2Yg==", scope="GIGACHAT_API_PERS", model="GigaChat", verify_ssl_certs=False)
search_tool = DuckDuckGoSearchRun()
new_tools = [search_tool]
agent = create_gigachat_functions_agent(giga, new_tools)
agent_executor = AgentExecutor(agent=agent, tools=new_tools, verbose=False)

def recognize_speech():
    with sr.Microphone() as source:
        print("Скажите кодовое слово или запрос...")
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

def reset_timer():
    global timer
    if timer:
        timer.cancel()
    timer = threading.Timer(timeout_duration, pause_bot)
    timer.start()

def pause_bot():
    global is_active
    is_active = False
    print("Бот снова на паузе.")

def activate_bot():
    global is_active
    is_active = True
    print("Бот активирован.")
    reset_timer()

def synthesize_speech(text: str):
    """Синтезирует речь из текста и воспроизводит её"""
    tts = gTTS(text, lang='ru')
    audio_file = 'audio.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file, True)

def main():
    global is_active
    is_active = False  # Бот изначально на паузе

    while True:
        text = recognize_speech()
        if text:
            if "выключить программу распознавания" in text.lower():
                print("Команда для завершения распознавания получена. Выключение программы.")
                break

            if is_active:
                print(f"Обработка запроса: {text}")
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
                reset_timer()  # Сбросить таймер на новый запрос
            else:
                # Проверка на кодовое слово
                if "smart" in text.lower() or "смарт" in text.lower():
                    parts = text.split(" ", 1)  # Разделяем текст на кодовое слово и остальную часть
                    if len(parts) > 1:  # Если есть дополнительный текст после кодового слова
                        request = parts[1]  # Получаем текст запроса
                        activate_bot()  # Активируем бота
                        print(f"Обработка запроса: {request}")
                        result = agent_executor.invoke(
                            {
                                "chat_history": chat_history,
                                "input": request,
                            }
                        )
                        response = result["output"]
                        chat_history.append(HumanMessage(content=request))
                        chat_history.append(AIMessage(content=response))
                        
                        print(f"Агент: {response}")
                        
                        # Озвучивание ответа бота
                        synthesize_speech(response)
                        reset_timer()  # Сбросить таймер на новый запрос
                    else:
                        activate_bot()  # Просто активируем бота без запроса
                else:
                    print("Скажите кодовое слово")

if __name__ == "__main__":
    main()
