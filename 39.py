# Moduł 5, Punkt 39: Jak zintegrować LangChain z innymi technologiami?
#
#
#
# Gratulacje! Dotarłeś prawie do końca tego modułu. Znasz już budowę łańcuchów, agentów, pamięci i dynamicznych aplikacji.
# Stworzyłeś "mózg" operacji. Ale jak sprawić, by świat zewnętrzny mógł z niego korzystać? Jak zamienić skrypt
# Pythona w prawdziwą, interaktywną aplikację webową, z którą może wejść w interakcję każdy, nie tylko programista?
#
# W tej lekcji nauczysz się, jak "opakować" logikę LangChain i udostępnić ją za pomocą popularnych frameworków.
#
# 1. Problem: Aplikacja w próżni
#
# Twój skrypt `.py` z agentem czy chatbotem jest potężny, ale sam w sobie jest bezużyteczny dla końcowego użytkownika.
# Nie ma interfejsu graficznego, nie można go wywołać przez internet, nie da się go zintegrować z innymi systemami.
# Aby Twoja aplikacja AI stała się produktem, musi mieć "most" do świata zewnętrznego.
#
# 2. Rozwiązanie: Frameworki webowe i API
#
# LangChain to silnik, a frameworki webowe to karoseria i deska rozdzielcza. Pozwalają one "wystawić"
# logikę LangChain jako usługę, z którą można się komunikować. Dwa najpopularniejsze podejścia to:
#
#     * **Tworzenie API (np. za pomocą FastAPI lub Flask)**:
#       To profesjonalne podejście. Twoja aplikacja LangChain staje się backendem, który udostępnia punkty
#       końcowe (endpoints), np. `/chat`. Dowolna inna aplikacja (frontend w JavaScripcie, aplikacja mobilna,
#       inny serwis) może wysłać zapytanie do tego punktu i otrzymać odpowiedź. To idealne rozwiązanie
#       do budowy skalowalnych, produkcyjnych systemów.
#
#     * **Tworzenie interaktywnej aplikacji webowej (np. za pomocą Streamlit lub Gradio)**:
#       To najszybszy sposób na stworzenie działającego prototypu lub wewnętrznego narzędzia z interfejsem
#       użytkownika. Frameworki te pozwalają w kilku linijkach kodu Pythona stworzyć przyciski, pola tekstowe
#       i inne elementy UI, które bezpośrednio komunikują się z Twoim kodem LangChain.
#
# W tej lekcji skupimy się na **Streamlit**, ponieważ pozwala błyskawicznie zobaczyć efekty naszej pracy.
#
# 3. Praktyczny przykład: Interfejs webowy dla chatbota z pamięcią
#
# Zbudujemy prostą, ale w pełni funkcjonalną aplikację webową, która pozwoli użytkownikom rozmawiać
# z naszym chatbotem z jednej z poprzednich lekcji.
#
# Krok 1: Instalacja niezbędnych bibliotek
# pip install langchain langchain-openai streamlit
#
# Krok 2: Stworzenie pliku, np. `chatbot_app.py` i umieszczenie w nim poniższego kodu.

import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# WAŻNE: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    st.error("BŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    st.stop()

# Krok 3: Definicja logiki LangChain
# Dobrą praktyką jest umieszczenie logiki tworzenia łańcucha w funkcji.
def get_conversation_chain():
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    # Pamięć musi przechowywać wiadomości, aby można je było później wyświetlić
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    prompt = ChatPromptTemplate(
        input_variables=["input", "chat_history"],
        messages=[
            MessagesPlaceholder(variable_name="chat_history"),
            "{input}"
        ]
    )
    
    return LLMChain(llm=llm, memory=memory, prompt=prompt, verbose=True)

# Krok 4: Budowa interfejsu użytkownika w Streamlit
st.title("🤖 Mój Własny Chatbot z Pamięcią")
st.write("Witaj! To jest prosty interfejs dla chatbota opartego o LangChain.")

# Inicjalizacja stanu sesji, aby przechowywać historię rozmowy i łańcuch
# To kluczowy element, który pozwala Streamlit "pamiętać" stan między interakcjami.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    st.session_state.chain = get_conversation_chain()

# Wyświetlanie dotychczasowych wiadomości
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Pobieranie nowego zapytania od użytkownika
if prompt := st.chat_input("Napisz swoją wiadomość tutaj..."):
    # Dodaj i wyświetl wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Wygeneruj i wyświetl odpowiedź AI
    with st.chat_message("assistant"):
        with st.spinner("AI myśli..."):
            response = st.session_state.chain.invoke({"input": prompt})
            st.markdown(response["text"])
            st.session_state.messages.append({"role": "assistant", "content": response["text"]})

# Krok 5: Uruchomienie aplikacji
# Zapisz plik i w terminalu (w tym samym folderze) wykonaj komendę:
# streamlit run chatbot_app.py
# (gdzie `chatbot_app.py` to nazwa Twojego pliku)

#
# 4. Podsumowanie – Jesteś Architektem Aplikacji AI
#
# Ta lekcja zamyka klamrą cały proces tworzenia aplikacji. Nauczyłeś się nie tylko budować inteligentny "silnik"
# za pomocą LangChain, ale także dawać mu "karoserię" i "interfejs", aby mógł służyć ludziom.
#
# Najważniejsze do zapamiętania:
#
#     * Aplikacje LangChain rzadko żyją w próżni – muszą być zintegrowane z innymi technologiami.
#     * **FastAPI** to profesjonalny wybór do tworzenia backendu i API dla Twojej aplikacji.
#     * **Streamlit** to fantastyczne, niezwykle szybkie narzędzie do budowy prototypów, dem i wewnętrznych aplikacji z UI.
#     * Wzorzec integracji jest prosty: opakuj logikę LangChain w funkcję, a następnie wywołuj ją z poziomu frameworka webowego.
#     * **`st.session_state`** w Streamlit jest odpowiednikiem pamięci dla interfejsu – przechowuje stan między odświeżeniami strony.
#
# Masz teraz kompletny zestaw narzędzi, aby przejść od pomysłu, przez budowę logiki w LangChain, aż po wdrożenie
# interaktywnej aplikacji. Twoja przygoda z tworzeniem inteligentnych systemów dopiero się zaczyna!