import speech_recognition as sr
from langchain.chat_models.gigachat import GigaChat
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_gigachat_functions_agent
import pyfiglet
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from gtts import gTTS
import playsound

# Инициализация распознавателя
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True  # Включаем автоматическую настройку порога энергии
recognizer.dynamic_energy_ratio = 1.5  # Соотношение для динамического порога энергии
recognizer.operation_timeout = None  # Тайм-аут операции (без ограничения по времени)
recognizer.dynamic_energy_adjustment_damping = 0.2  # Уровень сглаживания для динамической настройки

# Устанавливаем фиксированные настройки
recognizer.pause_threshold = 1  # Время паузы, определяющее завершение записи

def recognize_speech():
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

@tool
def draw_banner(number: str) -> str:
    """Рисует баннер с текстом результатов кода в виде Ascii-графики"""
    pyfiglet.print_figlet(number, font="epic")
    return "Draw complete"

def synthesize_speech(text: str):
    """Синтезирует речь из текста и воспроизводит её"""
    tts = gTTS(text, lang='ru')
    audio_file = 'audio.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file, True)

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
    while True:
        text = recognize_speech()
        if text:
            if "выключить программу распознавания" in text.lower():
                print("Команда для завершения распознавания получена. Выключение программы.")
                break

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
