# Moduł 11, punkt 110: Praktyczna Realizacja Projektu Końcowego
# Projekt: Specjalistyczny Doradca AI (RODO Ekspert)
#
# Witaj w module finałowym! To tutaj cała zdobyta wiedza złoży się w jeden, działający i imponujący projekt.
# Zbudujemy od podstaw aplikację, która będzie ekspertem w dziedzinie RODO.
# Będzie to Twoja wizytówka jako AI Engineera – dowód, że potrafisz nie tylko korzystać z AI, ale tworzyć realne, wartościowe narzędzia.
#
# Cel projektu: Stworzenie aplikacji webowej, która precyzyjnie odpowiada na pytania dotyczące
# Rozporządzenia o Ochronie Danych Osobowych (RODO), bazując wyłącznie na jego treści.
#
# Stack technologiczny, którego użyjemy:
# - Backend API: FastAPI
# - Orkiestracja AI: LangChain
# - Baza Wiedzy: Mechanizm RAG (Retrieval-Augmented Generation) z bazą wektorową ChromaDB
# - Frontend: Streamlit
#
# Zaczynajmy!

# ==============================================================================
# Krok 1: Przygotowanie środowiska i struktury projektu
# ==============================================================================
#
# Dobre przygotowanie to podstawa. Zadbajmy o porządek od samego początku.

# 1. Stwórz wirtualne środowisko
# W terminalu, w głównym folderze projektu, wykonaj:
# python -m venv .venv
# source .venv/bin/activate  # na Linux/macOS
# .venv\Scripts\activate      # na Windows

# 2. Zainstaluj niezbędne biblioteki
# Stwórz plik 'requirements.txt' i wklej do niego poniższe zależności.
# Następnie zainstaluj je poleceniem: pip install -r requirements.txt
#
# Plik requirements.txt:
# langchain
# openai
# python-dotenv
# uvicorn
# fastapi
# pydantic
# pypdf
# chromadb
# tiktoken
# streamlit
# requests

# 3. Stwórz strukturę folderów
# Nasz projekt będzie wyglądał tak:
#
# /twoj-projekt-rodo/
# |-- .venv/
# |-- app/
# |   |-- main.py             # Główny plik z logiką FastAPI
# |   |-- core.py             # Serce naszej aplikacji - logika RAG i LangChain
# |   |-- ingest_data.py      # Skrypt do przetwarzania dokumentu RODO i tworzenia bazy wektorowej
# |
# |-- data/
# |   |-- rodo_pl.pdf         # Tutaj umieść plik PDF z tekstem RODO
# |
# |-- ui/
# |   |-- app_ui.py           # Plik z interfejsem użytkownika w Streamlit
# |
# |-- .env                    # Plik z kluczem API do OpenAI
# |-- requirements.txt

# ==============================================================================
# Krok 2: Pozyskanie i Przetworzenie Danych (Ingestion)
# ==============================================================================
#
# To jest serce mechanizmu RAG. Musimy "nauczyć" naszą aplikację treści RODO.
# Zrobimy to w pliku 'app/ingest_data.py'.

# 1. Znajdź i pobierz dokument
# Znajdź w internecie pełny, jednolity tekst RODO w formacie PDF.
# Zapisz go w folderze 'data/' jako 'rodo_pl.pdf'.

# 2. Napisz skrypt 'ingest_data.py'
# Ten skrypt będzie jednorazowo uruchamiany, aby przetworzyć PDF i zapisać go w bazie wektorowej.

# przykładowy kod dla app/ingest_data.py:
"""
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# Ścieżka do dokumentu i do bazy danych wektorowej
PDF_PATH = "../data/rodo_pl.pdf"
DB_PATH = "../vector_db"

def main():
    # 1. Ładowanie dokumentu PDF
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"Załadowano {len(documents)} stron z dokumentu.")

    # 2. Dzielenie tekstu na mniejsze fragmenty (chunki)
    # To kluczowy krok, aby zmieścić fragmenty w kontekście modelu i uzyskać trafne wyniki.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"Podzielono dokument na {len(chunks)} fragmentów.")

    # 3. Tworzenie embeddingów i zapisywanie w bazie wektorowej ChromaDB
    # Embeddingi to numeryczne reprezentacje tekstu.
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print("Baza wektorowa została pomyślnie utworzona i zapisana.")

if __name__ == "__main__":
    main()
"""

# Uruchom ten skrypt z terminala, będąc w folderze 'app/':
# python ingest_data.py
# Po wykonaniu, w głównym folderze projektu powstanie nowy katalog 'vector_db/'.

# ==============================================================================
# Krok 3: Budowa Rdzenia Logiki AI (app/core.py)
# ==============================================================================
#
# Tutaj stworzymy logikę, która przyjmuje pytanie i generuje odpowiedź.
# Użyjemy do tego LangChain, aby połączyć LLM z naszą bazą wiedzy.

# przykładowy kod dla app/core.py:
"""
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "../vector_db"

# Szablon promptu – to tutaj dzieje się magia!
# Nakazujemy modelowi, aby był precyzyjny, odpowiadał po polsku
# i bazował WYŁĄCZNIE na dostarczonym kontekście (fragmentach RODO).
PROMPT_TEMPLATE = \"\"\"
Jesteś precyzyjnym asystentem AI, ekspertem od rozporządzenia RODO.
Odpowiadaj na pytania TYLKO I WYŁĄCZNIE na podstawie dostarczonego poniżej kontekstu.
Jeśli w kontekście nie ma odpowiedzi na pytanie, odpowiedz: "Na podstawie dostępnych danych nie jestem w stanie odpowiedzieć na to pytanie.".
Odpowiadaj rzeczowo i konkretnie, w języku polskim.

Kontekst:
{context}

Pytanie:
{question}

Odpowiedź:
\"\"\"

def get_qa_chain():
    # 1. Załaduj istniejącą bazę wektorową
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    # 2. Skonfiguruj model LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)

    # 3. Stwórz retriever, który będzie wyszukiwał relevantne fragmenty w bazie
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 4. Połącz wszystko w łańcuch RetrievalQA
    prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain
"""

# ==============================================================================
# Krok 4: Uruchomienie API za pomocą FastAPI (app/main.py)
# ==============================================================================
#
# Czas udostępnić naszą logikę światu za pomocą prostego API.

# przykładowy kod dla app/main.py:
"""
from fastapi import FastAPI
from pydantic import BaseModel
from app.core import get_qa_chain

app = FastAPI(
    title="RODO Ekspert API",
    description="API do zadawania pytań na temat RODO"
)

# Inicjalizacja łańcucha QA przy starcie aplikacji
qa_chain = get_qa_chain()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    \"\"\"
    Endpoint przyjmuje pytanie użytkownika i zwraca odpowiedź wygenerowaną
    przez model oraz źródła, na których się oparł.
    \"\"\"
    result = qa_chain({"query": request.query})
    
    answer = result.get("result", "Wystąpił błąd.")
    source_documents = result.get("source_documents", [])
    
    sources = [doc.metadata.get("source", "") for doc in source_documents]
    
    return {"answer": answer, "sources": list(set(sources))}
"""

# Aby uruchomić serwer API, przejdź do głównego folderu projektu i wykonaj w terminalu:
# uvicorn app.main:app --reload

# Możesz teraz przetestować API, np. wbudowanej dokumentacji Swiggera pod adresem http://127.0.0.1:8000/docs

# ==============================================================================
# Krok 5: Stworzenie Interfejsu Użytkownika (ui/app_ui.py)
# ==============================================================================
#
# Zbudujmy prosty, ale funkcjonalny interfejs, aby każdy mógł skorzystać z naszej aplikacji.

# przykładowy kod dla ui/app_ui.py:
"""
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="RODO Ekspert AI", layout="centered")
st.title("🤖 RODO Ekspert AI")
st.caption("Zadaj pytanie dotyczące RODO, a AI odpowie na podstawie oficjalnego dokumentu.")

# Inicjalizacja historii czatu
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetlanie historii czatu
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Pole do wprowadzania pytania przez użytkownika
if prompt := st.chat_input("Jakie jest Twoje pytanie?"):
    # Wyświetl pytanie użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Przygotuj się na odpowiedź AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Analizuję dokument RODO... ⏳")
        
        try:
            # Wyślij zapytanie do API
            response = requests.post(API_URL, json={"query": prompt})
            response.raise_for_status() # Sprawdź czy nie ma błędu HTTP
            
            result = response.json()
            answer = result.get("answer", "Przepraszam, wystąpił błąd.")
            
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except requests.exceptions.RequestException as e:
            message_placeholder.error(f"Błąd połączenia z API: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Błąd: {e}"})

"""

# Aby uruchomić interfejs, otwórz nowy terminal i (w głównym folderze projektu) wykonaj:
# streamlit run ui/app_ui.py

# ==============================================================================
# Krok 6: Testowanie, Optymalizacja i Prezentacja w Portfolio
# ==============================================================================
#
# Masz działającą aplikację! Teraz czas na pracę inżyniera.

# 1. Testowanie:
# - Zadawaj trudne, wieloznaczne pytania.
# - Sprawdzaj, czy model faktycznie odmawia odpowiedzi, gdy nie ma jej w kontekście.
# - Testuj pytania o dane, których nie ma w RODO (np. "Jaka jest stolica Polski?").

# 2. Optymalizacja:
# - Eksperymentuj z `chunk_size` i `chunk_overlap` w `ingest_data.py`. Czy mniejsze/większe fragmenty dają lepsze wyniki?
# - Modyfikuj `PROMPT_TEMPLATE` w `core.py`. Dodaj instrukcje, aby model cytował konkretne artykuły.
# - Zmień `search_kwargs={"k": 3}` w `core.py`. Czy pobranie większej liczby fragmentów (`k=5`) poprawia jakość odpowiedzi?

# 3. Budowanie Portfolio (Moduły 107-108):
# - Stwórz wspaniały plik `README.md` w głównym folderze projektu. Opisz w nim cel, architekturę i jak uruchomić aplikację.
# - Nagraj krótkie wideo (np. za pomocą Loom) pokazujące działanie aplikacji.
# - Umieść projekt na swoim GitHubie. To Twój najważniejszy zasób podczas szukania pracy.
# - Opisz napotkane wyzwania (np. "problem z halucynacjami modelu i jak go rozwiązałem poprzez inżynierię promptów").

#
# Gratulacje! Ukończyłeś swój pierwszy kompleksowy projekt AI.
# To dowód Twoich umiejętności i fantastyczny start do dalszego rozwoju w tej ekscytującej dziedzinie.
#