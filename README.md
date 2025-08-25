# Kompletny Przewodnik Budowy Projektu: RODO Ekspert AI

Witaj w szczegółowym przewodniku krok po kroku, który dokumentuje proces tworzenia aplikacji **RODO Ekspert AI**. Ten plik jest kompletnym podsumowaniem modułu praktycznego i zawiera wszystkie fragmenty kodu oraz wyjaśnienia niezbędne do zrozumienia i odtworzenia projektu od zera.

## Spis Treści
1. [Cel i Architektura Projektu](#1-cel-i-architektura-projektu)
2. [Krok 1: Struktura Projektu i Konfiguracja Środowiska](#2-krok-1-struktura-projektu-i-konfiguracja-środowiska)
3. [Krok 2: Proces Ingestii Danych – Tworzenie Bazy Wiedzy](#3-krok-2-proces-ingestii-danych--tworzenie-bazy-wiedzy)
4. [Krok 3: Rdzeń Logiki AI – Budowa Łańcucha Q&A](#4-krok-3-rdzeń-logiki-ai--budowa-łańcucha-qa)
5. [Krok 4: Backend API w FastAPI](#5-krok-4-backend-api-w-fastapi)
6. [Krok 5: Interfejs Użytkownika w Streamlit](#6-krok-5-interfejs-użytkownika-w-streamlit)
7. [Krok 6: Uruchomienie Kompletnej Aplikacji](#7-krok-6-uruchomienie-kompletnej-aplikacji)

---

## 1. Cel i Architektura Projektu

### Cel
Celem projektu jest stworzenie inteligentnego asystenta, który potrafi precyzyjnie odpowiadać na pytania dotyczące Rozporządzenia o Ochronie Danych Osobowych (RODO). Aplikacja ma być oparta wyłącznie na treści oficjalnego dokumentu, aby zapewnić wierność i wiarygodność odpowiedzi, eliminując ryzyko "halucynacji" modelu AI.

### Architektura
Projekt opiera się na nowoczesnej architekturze **RAG (Retrieval-Augmented Generation)**, która składa się z trzech głównych części:
- **Backend API (FastAPI):** Serce aplikacji, które obsługuje logikę i komunikuje się z modelem AI.
- **Baza Wektorowa (ChromaDB):** Przechowuje przetworzoną "wiedzę" z dokumentu RODO w formie wektorów.
- **Frontend (Streamlit):** Prosty i interaktywny interfejs graficzny dla użytkownika końcowego.

---

## 2. Krok 1: Struktura Projektu i Konfiguracja Środowiska

Na początku tworzymy logiczną strukturę folderów i plików konfiguracyjnych.

### Struktura folderów:
```
project_rodo_ai/
├── app/
│   ├── __init__.py
│   ├── core.py
│   ├── ingest_data.py
│   └── main.py
├── data/
│   └── README.md
├── ui/
│   └── app_ui.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

### `requirements.txt`
Plik z listą wszystkich niezbędnych bibliotek.
```python
fastapi
uvicorn[standard]
python-dotenv
langchain
langchain-openai
langchain-community
pypdf
chromadb
tiktoken
streamlit
requests
```
**Instalacja:** `pip install -r requirements.txt`

### `.env.example`
Szablon dla pliku `.env`, który będzie przechowywał nasz klucz API.
```
OPENAI_API_KEY="sk-..."
```
Użytkownik musi skopiować ten plik do `.env` i wkleić swój klucz.

### `.gitignore`
Plik informujący Git, które pliki i foldery ma ignorować. To kluczowy element świadczący o dobrych praktykach.
```
.venv/
.env
__pycache__/
vector_db/
```

---

## 3. Krok 2: Proces Ingestii Danych – Tworzenie Bazy Wiedzy

Ten etap polega na przetworzeniu dokumentu PDF na format zrozumiały dla maszyny. Tworzymy dedykowany skrypt, który uruchamiamy tylko raz.

### `app/ingest_data.py`
Skrypt ten wykonuje następujące operacje:
1.  Wczytuje dokument PDF z folderu `data/`.
2.  Dzieli go na mniejsze, nakładające się na siebie fragmenty tekstu (chunki).
3.  Używa modelu embeddingów OpenAI do zamiany każdego fragmentu na wektor liczbowy.
4.  Zapisuje wektory wraz z oryginalnymi fragmentami tekstu w bazie wektorowej ChromaDB na dysku.

```python
# app/ingest_data.py

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'rodo_pl.pdf')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'vector_db')

def main():
    print("Rozpoczynam proces ingestii danych...")

    if not os.path.exists(PDF_PATH):
        print(f"BŁĄD: Plik PDF nie został znaleziony pod ścieżką: {PDF_PATH}")
        return

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"Załadowano {len(documents)} stron.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=120)
    chunks = text_splitter.split_documents(documents)
    print(f"Dokument podzielono na {len(chunks)} fragmentów.")

    print("Tworzenie embeddingów i zapisywanie w bazie ChromaDB...")
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print("Proces ingestii zakończony pomyślnie!")

if __name__ == "__main__":
    main()
```
**Uruchomienie:** `python app/ingest_data.py`

---

## 4. Krok 3: Rdzeń Logiki AI – Budowa Łańcucha Q&A

W tym kroku tworzymy serce naszej aplikacji – mechanizm, który potrafi inteligentnie odpowiadać na pytania.

### `app/core.py`
Ten plik zawiera funkcję `get_qa_chain`, która:
1.  Ładuje wcześniej utworzoną bazę wektorową ChromaDB.
2.  Konfiguruje model językowy (np. GPT-3.5-Turbo).
3.  Definiuje **Prompt Template** – kluczowy zestaw instrukcji dla modelu AI, nakazujący mu odpowiadać tylko na podstawie dostarczonego kontekstu.
4.  Tworzy **Retrievera**, który na podstawie pytania użytkownika wyszukuje w bazie wektorowej najbardziej relevantne fragmenty tekstu.
5.  Łączy wszystkie te elementy w jeden `RetrievalQA` chain z biblioteki LangChain.

```python
# app/core.py

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'vector_db')

PROMPT_TEMPLATE = """
Jesteś precyzyjnym i pomocnym asystentem AI, który specjalizuje się w RODO.
Twoim zadaniem jest odpowiedzieć na pytanie użytkownika wyłącznie na podstawie dostarczonego poniżej Kontekstu.
Jeśli w Kontekście nie ma wystarczających informacji, odpowiedz:
"Na podstawie dostarczonych fragmentów dokumentu RODO nie jestem w stanie udzielić odpowiedzi na to pytanie."
Nie próbuj wymyślać odpowiedzi. Odpowiadaj zawsze w języku polskim.

Kontekst:
{context}

Pytanie:
{question}

Odpowiedź:
"""

def get_qa_chain():
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain
```

---

## 5. Krok 4: Backend API w FastAPI

Teraz udostępnimy naszą logikę AI światu za pomocą profesjonalnego API.

### `app/main.py`
Ten plik:
1.  Tworzy instancję aplikacji FastAPI.
2.  Podczas startu serwera, jednorazowo inicjalizuje łańcuch Q&A z `core.py`.
3.  Definiuje endpoint `POST /ask`, który przyjmuje pytanie od użytkownika w formacie JSON.
4.  Używa Pydantic do walidacji danych wejściowych i wyjściowych, co zapewnia bezpieczeństwo i automatyczną dokumentację.
5.  Przekazuje pytanie do łańcucha QA, otrzymuje odpowiedź i zwraca ją do klienta wraz z dokumentami źródłowymi.

```python
# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core import get_qa_chain
from typing import List

app = FastAPI(
    title="RODO Ekspert AI API",
    description="API do zadawania pytań na temat RODO."
)

qa_chain = None

@app.on_event("startup")
def startup_event():
    global qa_chain
    qa_chain = get_qa_chain()

class QueryRequest(BaseModel):
    query: str

class DocumentMetadata(BaseModel):
    page: int
    source: str

class Document(BaseModel):
    page_content: str
    metadata: DocumentMetadata

class QueryResponse(BaseModel):
    answer: str
    source_documents: List[Document]

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    if not qa_chain:
        raise HTTPException(status_code=503, detail="Serwer nie jest gotowy.")
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Pytanie nie może być puste.")
    
    try:
        result = qa_chain.invoke({"query": request.query})
        return {
            "answer": result.get("result", ""),
            "source_documents": result.get("source_documents", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
**Uruchomienie serwera API:** `uvicorn app.main:app --reload`

---

## 6. Krok 5: Interfejs Użytkownika w Streamlit

Na koniec tworzymy prosty i intuicyjny interfejs graficzny.

### `ui/app_ui.py`
Ten skrypt:
1.  Tworzy interfejs webowy za pomocą biblioteki Streamlit, przypominający okno czatu.
2.  Zarządza historią konwersacji w stanie sesji.
3.  Gdy użytkownik wpisze pytanie, wysyła zapytanie `POST` do naszego API w FastAPI.
4.  Odbiera odpowiedź z backendu i wyświetla ją użytkownikowi.
5.  Dodatkowo, w rozwijanej sekcji (`expander`), pokazuje fragmenty dokumentu, na podstawie których została wygenerowana odpowiedź, co zwiększa transparentność.

```python
# ui/app_ui.py

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="RODO Ekspert AI", page_icon="🤖", layout="wide")
st.title("🤖 RODO Ekspert AI")
st.caption("Zadaj pytanie dotyczące RODO, a AI odpowie na podstawie oficjalnego tekstu rozporządzenia.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Jak brzmi Twoje pytanie?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Analizuję dokument... ⏳")
        
        try:
            response = requests.post(API_URL, json={"query": prompt}, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("answer", "Wystąpił błąd.")
            message_placeholder.markdown(answer)
            
            with st.expander("Zobacz źródła odpowiedzi"):
                for doc in result.get("source_documents", []):
                    st.info(f"**Źródło (strona {doc['metadata']['page']}):**\n\n{doc['page_content']}")

            st.session_state.messages.append({"role": "assistant", "content": answer})

        except requests.exceptions.RequestException as e:
            error_message = f"Błąd połączenia z API: {e}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
```
**Uruchomienie interfejsu:** `streamlit run ui/app_ui.py`

---

## 7. Krok 6: Uruchomienie Kompletnej Aplikacji

Aby uruchomić cały system, potrzebujesz dwóch otwartych okien terminala w głównym folderze projektu.

1.  **W pierwszym terminalu** uruchom serwer backendowy:
    ```bash
    uvicorn app.main:app --reload
    ```
2.  **W drugim terminalu** uruchom interfejs użytkownika:
    ```bash
    streamlit run ui/app_ui.py
    ```

Aplikacja otworzy się automatycznie w przeglądarce, gotowa do działania!

---

To wszystko! Właśnie przeszedłeś przez cały proces tworzenia zaawansowanej aplikacji AI. Gratulacje!
