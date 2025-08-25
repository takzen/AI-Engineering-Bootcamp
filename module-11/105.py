# Moduł 11, Lekcja 105: Integracja różnych technologii (LangChain, RAG, FastAPI)

"""
Witaj w najważniejszej i najbardziej ekscytującej lekcji tego modułu!
Do tej pory tworzyliśmy osobne klocki: szkielet API, plik z danymi.
Teraz połączymy je w jeden, inteligentny mechanizm, używając do tego potęgi LangChain.

W tej lekcji zbudujemy kompletny potok RAG (Retrieval-Augmented Generation).
Nauczymy naszą aplikację, jak:
1. Przetworzyć dokument PDF na "wiedzę" zrozumiałą dla maszyny.
2. Zbudować mechanizm wyszukiwania, który odnajdzie najtrafniejsze fragmenty wiedzy.
3. Połączyć tę wiedzę z potężnym modelem językowym (LLM), aby wygenerować precyzyjną odpowiedź.
4. Zintegrować cały ten proces z naszym API w FastAPI.

To tutaj dzieje się prawdziwa magia AI. Zaczynajmy!
"""

# ==============================================================================
# Krok 1: Ingestia Danych – Zamiana PDF na Bazę Wektorową
# ==============================================================================

"""
Nasz model AI nie potrafi "czytać" PDF-ów. Musimy przekształcić dokument w format,
z którym może pracować. Ten proces nazywa się "ingestią" (ang. ingestion) i składa się z 4 etapów:
1.  **Load (Załaduj):** Wczytanie surowego tekstu z pliku PDF.
2.  **Split (Podziel):** Pocięcie długiego tekstu na mniejsze, zarządzalne fragmenty (chunki).
3.  **Embed (Osadź):** Zamiana każdego fragmentu tekstu na wektor (listę liczb), który reprezentuje jego znaczenie semantyczne.
4.  **Store (Zapisz):** Zapisanie wektorów i odpowiadających im fragmentów tekstu w specjalnej bazie danych – bazie wektorowej.

Stworzymy do tego dedykowany skrypt, który będziemy uruchamiać tylko raz, aby przygotować naszą bazę wiedzy.
"""

# Stwórz nowy plik w folderze 'app/' o nazwie 'ingest_data.py'
# i wklej do niego poniższy kod.

# --- Zawartość pliku app/ingest_data.py ---
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

# Wczytujemy zmienne środowiskowe (m.in. klucz API)
load_dotenv()

# Definiujemy ścieżki do danych i bazy wektorowej
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'rodo_pl.pdf')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'vector_db')

def main():
    print("Rozpoczynam proces ingestii danych...")

    # 1. ŁADOWANIE DOKUMENTU
    print(f"Ładowanie dokumentu z: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    if not documents:
        print("Nie udało się załadować dokumentu. Sprawdź ścieżkę i zawartość pliku.")
        return

    print(f"Załadowano {len(documents)} stron.")

    # 2. DZIELENIE TEKSTU NA FRAGMENTY
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"Dokument podzielono na {len(chunks)} fragmentów (chunków).")

    # 3. TWORZENIE EMBEDDINGÓW I ZAPIS DO BAZY WEKTOROWEJ
    print("Tworzenie embeddingów i zapisywanie w bazie wektorowej ChromaDB...")
    # Używamy modelu embeddingów od OpenAI
    embeddings = OpenAIEmbeddings()

    # Tworzymy bazę ChromaDB z fragmentów dokumentu i zapisujemy ją na dysku
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    print("-" * 50)
    print("Proces ingestii zakończony pomyślnie!")
    print(f"Baza wektorowa została utworzona w: {DB_PATH}")
    print("-" * 50)


if __name__ == "__main__":
    # Upewnij się, że masz plik rodo_pl.pdf w folderze 'data'
    if not os.path.exists(PDF_PATH):
        print(f"BŁĄD: Nie znaleziono pliku PDF pod ścieżką: {PDF_PATH}")
        print("Upewnij się, że umieściłeś plik z RODO w folderze 'data'.")
    else:
        main()
# ---------------------------------------------

"""
Teraz uruchom ten skrypt. W terminalu, będąc w głównym folderze projektu, wykonaj:
"""
# python app/ingest_data.py

"""
Ten proces może potrwać chwilę (w zależności od wielkości dokumentu i szybkości internetu),
ponieważ wysyła każdy fragment tekstu do API OpenAI, aby zamienić go na wektor.
Po zakończeniu w głównym folderze projektu pojawi się nowy katalog `vector_db/` – to jest nasza gotowa baza wiedzy!
"""

# ==============================================================================
# Krok 2: Budowa Łańcucha Q&A w LangChain
# ==============================================================================

"""
Mamy już bazę wiedzy. Teraz zbudujemy mechanizm, który będzie z niej korzystał.
Stworzymy do tego nowy plik `core.py` w folderze `app/`, który będzie sercem logiki naszej aplikacji.
"""

# Stwórz plik 'app/core.py' i wklej do niego poniższy kod.

# --- Zawartość pliku app/core.py ---
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'vector_db')

# To jest kluczowy element – szablon promptu.
# Dajemy modelowi AI bardzo konkretne instrukcje, jak ma się zachowywać.
# Nakazujemy mu być ekspertem od RODO i odpowiadać TYLKO na podstawie dostarczonych fragmentów.
PROMPT_TEMPLATE = """\
Jesteś precyzyjnym i pomocnym asystentem AI, który specjalizuje się w Rozporządzeniu o Ochronie Danych Osobowych (RODO).
Twoim zadaniem jest odpowiedzieć na pytanie użytkownika wyłącznie na podstawie dostarczonego poniżej kontekstu.
Kontekst zawiera fragmenty dokumentu RODO.
Jeśli w kontekście nie ma wystarczających informacji, aby odpowiedzieć na pytanie, odpowiedz:
"Na podstawie dostarczonych fragmentów dokumentu RODO nie jestem w stanie udzielić odpowiedzi na to pytanie."
Nie próbuj wymyślać odpowiedzi. Odpowiadaj zawsze w języku polskim.

Kontekst:
{context}

Pytanie:
{question}

Odpowiedź:"""


def get_qa_chain():
    """
    Ta funkcja buduje i zwraca gotowy do użycia łańcuch RetrievalQA.
    """
    # 1. Wskazujemy na model embeddingów, którego użyliśmy do stworzenia bazy
    embeddings = OpenAIEmbeddings()

    # 2. Ładujemy istniejącą bazę wektorową z dysku
    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    # 3. Tworzymy "retrievera" – mechanizm do wyszukiwania w bazie wektorowej.
    # search_kwargs={"k": 3} oznacza, że dla każdego pytania pobierze 3 najtrafniejsze fragmenty.
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 4. Inicjalizujemy model LLM, który będzie generował odpowiedzi
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)

    # 5. Tworzymy szablon promptu
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    # 6. Łączymy wszystkie elementy w jeden, potężny łańcuch RetrievalQA
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff", # "stuff" to prosta metoda, która "upycha" wszystkie fragmenty w jednym prompcie
        retriever=retriever,
        return_source_documents=True, # Chcemy wiedzieć, na podstawie których fragmentów model odpowiedział
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain
# ---------------------------------------------

# ==============================================================================
# Krok 3: Integracja Łańcucha z API w FastAPI
# ==============================================================================

"""
Mamy już serce naszej aplikacji w `core.py`. Teraz podłączmy je do naszego API w `main.py`,
aby można było z niego korzystać "z zewnątrz".
"""

# Zmodyfikuj plik 'app/main.py', aby wyglądał następująco:

# --- Zaktualizowana zawartość pliku app/main.py ---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core import get_qa_chain
from typing import List

# Tworzymy instancję aplikacji FastAPI
app = FastAPI(
    title="RODO Ekspert AI API",
    description="API dla aplikacji opartej na wiedzy z dokumentu RODO."
)

# Inicjalizujemy łańcuch QA raz, przy starcie aplikacji.
# Dzięki temu nie musimy go budować przy każdym zapytaniu, co oszczędza czas.
try:
    qa_chain = get_qa_chain()
except Exception as e:
    qa_chain = None
    print(f"BŁĄD: Nie udało się zainicjalizować łańcucha QA: {e}")
    print("Upewnij się, że baza wektorowa istnieje (uruchomiono ingest_data.py).")

# Definiujemy modele danych dla zapytań i odpowiedzi, używając Pydantic.
# To zapewnia walidację danych i generuje świetną dokumentację API.
class QueryRequest(BaseModel):
    query: str

class Document(BaseModel):
    page_content: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    source_documents: List[Document]

@app.get("/")
def read_root():
    return {"message": "Witaj w API dla projektu RODO Ekspert AI! Przejdź do /docs, aby zobaczyć dokumentację."}


@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    """
    Główny endpoint do zadawania pytań.
    Przyjmuje pytanie i zwraca odpowiedź wraz z dokumentami źródłowymi.
    """
    if not qa_chain:
        raise HTTPException(status_code=503, detail="Serwer nie jest gotowy. Łańcuch QA nie został poprawnie załadowany.")

    if not request.query:
        raise HTTPException(status_code=400, detail="Pytanie (query) nie może być puste.")

    try:
        result = qa_chain({"query": request.query})
        return {
            "answer": result.get("result", "Wystąpił błąd podczas generowania odpowiedzi."),
            "source_documents": result.get("source_documents", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wystąpił wewnętrzny błąd serwera: {e}")

# ---------------------------------------------

# ==============================================================================
# Krok 4: Moment Prawdy – Testowanie zintegrowanej aplikacji
# ==============================================================================

"""
Wszystkie elementy są na swoim miejscu! Czas na wielki test.

Uruchom serwer API (jeśli nie jest już uruchomiony):
"""
# uvicorn app.main:app --reload

"""
Teraz otwórz przeglądarkę i przejdź do interaktywnej dokumentacji, którą FastAPI
wygenerowało dla Ciebie automatycznie: http://127.0.0.1:8000/docs

1. Zobaczysz tam swój endpoint `/ask`. Rozwiń go.
2. Kliknij przycisk "Try it out".
3. W polu "Request body" wpisz przykładowe pytanie dotyczące RODO, np.:
   {
     "query": "Jakie są prawa osoby, której dane dotyczą?"
   }
4. Kliknij "Execute".

Po chwili powinieneś otrzymać odpowiedź w formacie JSON, zawierającą zarówno wygenerowaną
odpowiedź tekstową, jak i listę fragmentów z dokumentu PDF, na podstawie których
model sformułował swoją odpowiedź.

Udało się! Zintegrowałeś trzy potężne technologie w jeden działający system!
"""

# ==============================================================================
# Podsumowanie i Następne Kroki
# ==============================================================================

"""
To była bardzo intensywna, ale niezwykle ważna lekcja. Nauczyłeś się:
- Jak przetwarzać surowe dokumenty i tworzyć z nich bazę wiedzy (RAG).
- Jak używać LangChain do orkiestracji złożonych procesów AI.
- Jak kluczowa jest inżynieria promptów do kontrolowania zachowania modelu.
- Jak połączyć całą logikę AI z profesjonalnym API w FastAPI.

W następnej lekcji zajmiemy się testowaniem i optymalizacją. Zobaczymy, co można
poprawić, aby nasza aplikacja była jeszcze bardziej precyzyjna i niezawodna.
Następnie zbudujemy prosty interfejs graficzny, aby każdy mógł z niej wygodnie korzystać.
"""