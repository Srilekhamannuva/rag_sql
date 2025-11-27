import os
import win32com.client
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI

# ========== Load Environment Variables ==========
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ Please set your OPENAI_API_KEY in a .env file or system environment variable.")

# ========== Connect to MySQL ==========
db_uri = "mysql+pymysql://root:Srilekha%40666@localhost:3306/rag_demo"
db = SQLDatabase.from_uri(db_uri)

# ========== Initialize LLM + Chain ==========
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
chain = create_sql_query_chain(llm, db)

# ========== Initialize Text-to-Speech ==========
engine = pyttsx3.init(driverName='sapi5')
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)  # Female voice (if available)

def speak(text):
    """Convert text to speech and display it."""
    print(f"\n🧩 Answer: {text}\n")
    engine.say(text)
    engine.runAndWait()

# ========== Initialize Speech Recognition ==========
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    """Listen from the microphone and convert speech to text."""
    with mic as source:
        print("🎙️ Listening... (say 'exit' to quit)")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print(f"🧠 You said: {query}")
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that. Please repeat.")
        return None
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return None

# ========== Start Chatbot ==========
print("🧠 Voice-Enabled RAG-SQL Chatbot Ready!\n")

while True:
    mode = input("👉 Press [T] to type or [V] to speak your question: ").strip().lower()

    if mode == "t":
        query = input("🧠 Type your question: ")
    elif mode == "v":
        query = listen()
    else:
        speak("Invalid choice. Please press T or V.")
        continue

    if not query:
        continue
    if query.lower() in ["exit", "quit", "stop"]:
        speak("Goodbye! Have a great day.")
        break

    try:
        response = chain.invoke({"question": query})
        speak(response)
    except Exception as e:
        speak(f"Error: {str(e)}")
