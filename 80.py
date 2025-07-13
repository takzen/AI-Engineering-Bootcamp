# Moduł 9, Punkt 80: Wykorzystanie PostgreSQL i FAISS do przechowywania danych
#
#
#
# Wiemy już, że sercem systemu RAG jest proces indeksowania: ładowanie, dzielenie i tworzenie
# wektorów (embeddings) z naszych dokumentów. Ale gdzie te wszystkie dane – oryginalne fragmenty
# tekstu, ich wektory i dodatkowe informacje (metadane) – mają być przechowywane?
#
# Odpowiedź na to pytanie jest kluczowa dla wydajności, skalowalności i możliwości naszego
# systemu. W tej lekcji przyjrzymy się dwóm popularnym i bardzo różnym podejściom:
# ultraszybkiej, lokalnej bibliotece **FAISS** oraz potężnej, relacyjnej bazie danych
# **PostgreSQL** z rozszerzeniem wektorowym.
#
# 1. Problem: Gdzie trzymać naszą "bibliotekę wiedzy"?
#
# Nasza zindeksowana wiedza składa się z dwóch rodzajów danych:
#
#     * **Dane wektorowe (Embeddings)**: Gęste wektory liczbowe, które reprezentują znaczenie
#       fragmentów tekstu. Potrzebujemy systemu, który potrafi błyskawicznie przeszukiwać
#       miliony takich wektorów w poszukiwaniu najbliższych semantycznie sąsiadów.
#
#     * **Dane źródłowe i metadane**: Oryginalny tekst fragmentu oraz dodatkowe informacje
#       o nim, np. z jakiego dokumentu pochodzi (`source`), numer strony (`page`), data
#       utworzenia. Metadane są kluczowe do filtrowania wyników i cytowania źródeł.
#
# Wybór technologii do przechowywania tych danych to decyzja architektoniczna.
#
# 2. FAISS: Szybkość i prostota do prototypowania
#
# **FAISS (Facebook AI Similarity Search)** to biblioteka, a nie baza danych. Jest to
# wysoce zoptymalizowane narzędzie do niezwykle szybkiego wyszukiwania podobieństwa
# w ogromnych zbiorach wektorów.
#
# *   **Jak to działa?**: FAISS tworzy w pamięci (lub w pliku na dysku) specjalną strukturę
#     danych zwaną indeksem, która pozwala na błyskawiczne znajdowanie najbliższych sąsiadów
#     bez konieczności porównywania zapytania z każdym pojedynczym wektorem w bazie.
# *   **Zalety**:
#     - **Niezwykła szybkość**: Jest to jedno z najszybszych rozwiązań na rynku.
#     - **Lokalne działanie**: Nie wymaga serwera. Działa jako biblioteka w Twoim kodzie Pythona.
#     - **Idealne na start**: Świetne do prototypowania, eksperymentów i mniejszych zastosowań.
# *   **Wady**:
#     - **Brak cech bazy danych**: Domyślnie nie oferuje trwałości (indeks w pamięci znika
#       po restarcie), transakcji czy łatwego zarządzania danymi (dodawanie/usuwanie
#       pojedynczych wektorów jest skomplikowane).
#     - **Separacja od metadanych**: FAISS przechowuje tylko wektory. Metadane musisz trzymać
#       osobno i samodzielnie mapować wyniki z FAISS do odpowiednich metadanych.
#
# 3. PostgreSQL + pgvector: Potęga i unifikacja dla produkcji
#
# **PostgreSQL** to jedna z najpopularniejszych, niezwykle solidnych relacyjnych baz danych
# open-source. Sama w sobie nie potrafi obsługiwać wektorów. Ale dzięki rozszerzeniu
# **pgvector**, zyskuje tę "supermoc".
#
# *   **Jak to działa?**: `pgvector` dodaje do PostgreSQL nowy typ danych `vector` oraz możliwość
#     tworzenia specjalnych indeksów (np. HNSW, IVFFlat) do efektywnego przeszukiwania tych wektorów.
# *   **Zalety**:
#     - **Wszystko w jednym miejscu!**: To największa zaleta. W jednej tabeli, w jednym wierszu
#       możesz przechowywać ID, treść fragmentu, wszystkie metadane ORAZ jego wektor.
#     - **Uproszczona architektura**: Nie potrzebujesz dwóch osobnych systemów (jednego na
#       wektory, drugiego na metadane). Upraszcza to backupy, zarządzanie i development.
#     - **Potęga SQL**: Możesz łączyć wyszukiwanie wektorowe z tradycyjnym filtrowaniem SQL.
#       Np.: "Znajdź mi fragmenty podobne do X, ale tylko z dokumentów utworzonych po
#       dacie Y i należących do kategorii Z".
# *   **Wady**:
#     - **Wydajność przy ogromnej skali**: Przy setkach milionów lub miliardach wektorów,
#       dedykowane bazy wektorowe (jak Pinecone czy Weaviate) mogą być bardziej wydajne.
#
# 4. Praktyczny przykład: Budowa i użycie indeksu FAISS
#
# Zobaczmy, jak w praktyce zbudować prosty system RAG z użyciem FAISS.
#
# Krok 0: Instalacja
# pip install langchain-openai langchain-community faiss-cpu
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Przygotowanie danych (ładowanie i dzielenie)
# W realnej aplikacji użylibyśmy Document Loaders. Tutaj symulujemy ten proces.
text = """
LangChain to framework do tworzenia aplikacji opartych o duże modele językowe.
Umożliwia łączenie LLM-ów z zewnętrznymi źródłami danych.
FAISS to biblioteka do szybkiego wyszukiwania podobieństwa.
PostgreSQL z rozszerzeniem pgvector pozwala na przechowywanie wektorów w bazie SQL.
"""

text_splitter = CharacterTextSplitter(chunk_size=150, chunk_overlap=20)
docs_as_string = text_splitter.split_text(text)
# Zamieniamy stringi na obiekty Document, dodając metadane
documents = [Document(page_content=t, metadata={"source": "lekcja-80"}) for t in docs_as_string]

print("--- Podzielone dokumenty ---")
for doc in documents:
    print(doc)

# Krok 2: Inicjalizacja modelu embeddingowego
embeddings = OpenAIEmbeddings()

# Krok 3: Stworzenie indeksu FAISS z dokumentów
# Ta komenda wykonuje wszystkie kluczowe kroki:
# 1. Bierze każdy dokument.
# 2. Tworzy dla niego embedding za pomocą `OpenAIEmbeddings`.
# 3. Buduje w pamięci indeks FAISS ze wszystkich wektorów.
print("\n--- Tworzenie indeksu FAISS ---")
vectorstore = FAISS.from_documents(documents, embeddings)
print("Indeks został stworzony w pamięci.")

# Krok 4: Użycie indeksu do wyszukiwania podobieństwa
query = "Jakie są zastosowania LangChain?"
print(f"\n--- Wyszukiwanie dla zapytania: '{query}' ---")

# `similarity_search` zamienia zapytanie na wektor i znajduje najbardziej podobne dokumenty w indeksie.
found_docs = vectorstore.similarity_search(query, k=2) # k=2 oznacza, że chcemy 2 najlepsze wyniki

print("\nZnalezione dokumenty:")
for doc in found_docs:
    print(f"Źródło: {doc.metadata['source']}, Treść: {doc.page_content}")

# (Konceptualny przykład dla PostgreSQL + pgvector)
# # W przypadku pgvector, kod wyglądałby podobnie, ale zamiast `FAISS.from_documents`,
# # użylibyśmy obiektu `PGVector`, podając mu dane do połączenia z bazą danych.
# # from langchain_community.vectorstores.pgvector import PGVector
# #
# # CONNECTION_STRING = "postgresql+psycopg2://user:password@host:port/dbname"
# # COLLECTION_NAME = "moje_dokumenty"
# #
# # vectorstore_pg = PGVector.from_documents(
# #     embedding=embeddings,
# #     documents=documents,
# #     collection_name=COLLECTION_NAME,
# #     connection_string=CONNECTION_STRING,
# # )
# # Wyniki byłyby trwale zapisane w bazie PostgreSQL.

#
# 5. Podsumowanie: Kiedy czego używać?
#
# Wybór technologii zależy od Twojego projektu:
#
# *   **Użyj FAISS, gdy**:
#     - Szybko prototypujesz i eksperymentujesz.
#     - Twoja aplikacja działa lokalnie, a zbiór danych nie jest olbrzymi.
#     - Nie potrzebujesz zaawansowanego filtrowania po metadanych.
#     - Szybkość jest absolutnym priorytetem.
#
# *   **Wybierz PostgreSQL z `pgvector`, gdy**:
#     - Budujesz produkcyjną, skalowalną aplikację.
#     - Chcesz przechowywać dane, metadane i wektory w jednym, spójnym systemie.
#     - Potrzebujesz zaawansowanych możliwości filtrowania (łączenie SQL i wyszukiwania wektorowego).
#     - Zależy Ci na łatwym zarządzaniu, backupach i transakcyjności.
#
# Zrozumienie zalet i wad obu podejść pozwoli Ci zbudować solidną i wydajną architekturę dla Twojego systemu RAG.