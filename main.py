import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("❌ Please set your OPENAI_API_KEY in a .env file or system environment variable.")
    st.stop()

# ✅ MySQL connection
db_uri = "mysql+pymysql://root:Srilekha%40666@localhost:3306/rag_demo"
db = SQLDatabase.from_uri(db_uri)

# ✅ Initialize LLM and chain
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
chain = create_sql_query_chain(llm, db)

# ✅ Streamlit UI setup
st.set_page_config(page_title="🧠 Voice RAG-SQL Chatbot", layout="centered")
st.title("🧠🗣️ Voice-Enabled RAG-SQL Chatbot")
st.caption("Ask questions about your MySQL database — by voice or typing!")

# Voice input button (using browser SpeechRecognition API)
st.markdown("""
<script>
function startDictation() {
  if (window.hasOwnProperty('webkitSpeechRecognition')) {
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.start();
    recognition.onresult = function(e) {
      document.getElementById('query').value = e.results[0][0].transcript;
      recognition.stop();
      document.getElementById('submit').click();
    };
    recognition.onerror = function(e) {
      recognition.stop();
    }
  } else {
    alert("Speech recognition not supported in this browser.");
  }
}
</script>

<button onclick="startDictation()">🎙️ Speak</button>
""", unsafe_allow_html=True)

# Query input
query = st.text_input("Ask a question about your database:", key="query")
submit = st.button("Submit", key="submit")

if submit and query:
    with st.spinner("Thinking..."):
        try:
            # ✅ Use .invoke instead of .run
            response = chain.invoke({"question": query})

            st.success(response)

            # ✅ Voice output
            st.markdown(f"""
            <script>
            var msg = new SpeechSynthesisUtterance("{response}");
            window.speechSynthesis.speak(msg);
            </script>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
