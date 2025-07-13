# Jednorazowy skrypt do przetworzenia PDF i stworzenia bazy wektorowej
# 
"""
Ten skrypt odpowiada za proces "ingestii" danych.
Jego zadaniem jest wczytanie dokumentu PDF, podzielenie go na mniejsze fragmenty,
stworzenie dla nich wektorowych reprezentacji (embeddingów) i zapisanie ich
w trwałej bazie wektorowej ChromaDB na dysku.

Należy go uruchomić tylko raz, aby przygotować bazę wiedzy dla aplikacji.
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

# Wczytanie zmiennych środowiskowych (klucza API) z pliku .env
load_dotenv()

# Definicja stałych ze ścieżkami
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'rodo_pl.pdf')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'vector_db')

def main():
    """Główna funkcja orkiestrująca procesem ingestii."""
    print("Rozpoczynam proces ingestii danych...")

    if not os.path.exists(PDF_PATH):
        print(f"BŁĄD: Plik PDF nie został znaleziony pod ścieżką: {PDF_PATH}")
        print("Upewnij się, że umieściłeś plik 'rodo_pl.pdf' w folderze 'data'.")
        return

    # Krok 1: Ładowanie dokumentu PDF
    print(f"Ładowanie dokumentu z: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"Załadowano {len(documents)} stron z dokumentu.")

    # Krok 2: Dzielenie tekstu na mniejsze fragmenty (chunki)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=120)
    chunks = text_splitter.split_documents(documents)
    print(f"Dokument podzielono na {len(chunks)} fragmentów (chunków).")

    # Krok 3: Tworzenie embeddingów i zapis w bazie wektorowej
    print("Tworzenie embeddingów i zapisywanie w bazie wektorowej ChromaDB...")
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    print("-" * 50)
    print("Proces ingestii zakończony pomyślnie!")
    print(f"Baza wektorowa została utworzona w lokalizacji: {DB_PATH}")
    print("-" * 50)

if __name__ == "__main__":
    main()