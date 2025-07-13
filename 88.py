# Moduł 9, Punkt 88: Skalowanie aplikacji opartych na RAG
#
#
#
# Zbudowaliśmy i zoptymalizowaliśmy nasz system RAG. Działa świetnie na naszym laptopie
# z kilkoma dokumentami. Ale co się stanie, gdy nasza baza wiedzy urośnie do milionów
# dokumentów, a z aplikacji zacznie korzystać tysiące użytkowników jednocześnie?
#
# Prosta, monolityczna architektura, którą budowaliśmy do tej pory, nie wytrzyma takiego
# obciążenia. Skalowanie aplikacji RAG to wyzwanie inżynieryjne, które wymaga przemyślanej
# architektury i wyboru odpowiednich, produkcyjnych komponentów.
#
# 1. "Wąskie gardła" w skalowaniu RAG
#
# Aby zrozumieć, jak skalować RAG, musimy najpierw zidentyfikować, które jego części
# staną się problemem pod dużym obciążeniem.
#
#     *   **Indeksowanie**:
#         - **Czas**: Tworzenie wektorów (embedding) dla milionów dokumentów może trwać wiele godzin lub dni.
#         - **Zasoby**: Proces ten wymaga znaczącej mocy obliczeniowej (często GPU).
#
#     *   **Przechowywanie (Vector Store)**:
#         - **Pamięć**: Przechowywanie milionów wektorów w pamięci RAM (jak w domyślnym FAISS) jest niemożliwe.
#         - **Wydajność zapytań**: Baza wektorowa musi być w stanie obsłużyć tysiące zapytań o podobieństwo na sekundę.
#
#     *   **Wyszukiwanie (Retrieval)**:
#         - **Latencja**: Samo zapytanie do dużej, rozproszonej bazy wektorowej może wprowadzać zauważalne opóźnienia.
#
#     *   **Generowanie (Generation)**:
#         - **Współbieżność**: Każde wywołanie LLM-a jest blokujące i trwa. Obsługa wielu jednoczesnych
#           użytkowników wymaga architektury, która potrafi zarządzać tymi operacjami asynchronicznie.
#
# 2. Architektura skalowalnego systemu RAG
#
# Rozwiązaniem tych problemów jest przejście od architektury monolitycznej do **architektury
# rozproszonej, opartej na mikroserwisach i wyspecjalizowanych, zarządzanych usługach**.
#
# **Faza 1: Asynchroniczny, potokowy proces indeksowania (Indexing Pipeline)**
#
# Proces indeksowania powinien być całkowicie oddzielony od głównej aplikacji. Często
# realizuje się go jako potok danych (data pipeline) przy użyciu narzędzi takich jak
# Apache Airflow, Kafka lub prostych kolejek zadań (Celery/Redis).
#
# **[Nowy Dokument] -> [Kolejka Zadań] -> [Worker do Ładowania/Dzielenia] -> [Kolejka Zadań] -> [Worker do Embeddingu (z GPU)] -> [Produkcyjna Baza Wektorowa]**
#
# *   **Zalety**:
#     - Proces jest asynchroniczny i nie blokuje głównej aplikacji.
#     - Można go łatwo skalować, dodając więcej workerów do każdego etapu.
#     - Można użyć wyspecjalizowanych maszyn (np. z GPU) tylko do kosztownego kroku embeddingu.
#
# **Faza 2: Produkcyjna Baza Wektorowa**
#
# Zapominamy o lokalnym FAISS. Na produkcji potrzebujemy prawdziwej, zarządzanej bazy wektorowej.
#
# *   **Opcje**:
#     - **Dedykowane, zarządzane usługi**: **Pinecone, Weaviate, Milvus, ChromaDB (w wersji chmurowej)**. To najczęstszy i najłatwiejszy wybór. Oferują wysoką wydajność, skalowalność i proste API.
#     - **PostgreSQL z `pgvector`**: Jak już wiemy, to świetna opcja, jeśli chcemy trzymać wszystko w jednym miejscu, ale wymaga samodzielnego zarządzania i skalowania serwera PostgreSQL.
#
# **Faza 3: Skalowalna aplikacja "Query-Time"**
#
# Sama aplikacja, która odpowiada na pytania, również musi być skalowalna. Tutaj stosujemy
# wzorzec, który już znamy.
#
# **[Użytkownik] -> [API (FastAPI)] -> [1. Retrieval] -> [2. Generation (LLM)] -> [Odpowiedź]**
#
# *   **API (FastAPI)**: Aplikacja jest opakowana w API i uruchamiana w wielu instancjach
#     za load balancerem.
# *   **Krok 1: Retrieval**: Aplikacja łączy się z **zewnętrzną, produkcyjną bazą wektorową**
#     (np. Pinecone), aby pobrać kontekst.
# *   **Krok 2: Generation**: Aplikacja wywołuje API LLM (np. OpenAI).
#
# Cały ten proces powinien być **asynchroniczny**, aby serwer API mógł obsługiwać
# wiele zapytań jednocześnie.
#
# 3. Praktyczny przykład: Konceptualny kod z użyciem Pinecone
#
# Poniższy kod jest konceptualny, aby pokazać, jak zmieniłaby się nasza logika przy przejściu
# na produkcyjną bazę wektorową, taką jak Pinecone.
#
# Krok 0: Instalacja
# # pip install langchain-openai langchain-pinecone
import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

# Konfiguracja API i Pinecone
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["PINECONE_API_KEY"] = "..."
# os.environ["PINECONE_ENVIRONMENT"] = "us-west1-gcp" # lub inny region
if "OPENAI_API_KEY" not in os.environ or "PINECONE_API_KEY" not in os.environ:
    print("\nBŁĄD: Skonfiguruj zmienne środowiskowe dla OpenAI i Pinecone.")
    exit()

# Załóżmy, że mamy już zaindeksowane dokumenty
documents = [
    Document(page_content="Skalowalny RAG używa produkcyjnych baz wektorowych.", metadata={"id": "doc1"}),
    Document(page_content="Pinecone to popularna, zarządzana baza wektorowa.", metadata={"id": "doc2"})
]
embeddings = OpenAIEmbeddings()
index_name = "rag-production-index" # Nazwa naszego indeksu w panelu Pinecone

# Krok 1: Indeksowanie (w tle, w osobnym potoku)
# Ta operacja dodaje dokumenty do zdalnego, zarządzanego indeksu Pinecone.
# Nie tworzy niczego lokalnie.
print("--- Indeksowanie danych w Pinecone ---")
# PineconeVectorStore.from_documents(documents, embeddings, index_name=index_name)
print("Dane (symulacyjnie) zindeksowane.")

# Krok 2: Użycie istniejącego indeksu w aplikacji Query-Time
print("\n--- Użycie produkcyjnego retrievera ---")
# W naszej aplikacji FastAPI, nie tworzymy indeksu od nowa.
# Łączymy się z ISTNIEJĄCYM, już wypełnionym indeksem w chmurze Pinecone.
vectorstore_prod = PineconeVectorStore.from_existing_index(index_name, embeddings)
retriever_prod = vectorstore_prod.as_retriever()

# Krok 3: Wyszukiwanie
query = "Jakiej bazy używać w produkcyjnym RAG?"
print(f"Zapytanie: {query}")
found_docs = retriever_prod.invoke(query)

print("\nZnalezione dokumenty z Pinecone:")
print(found_docs)


# 4. Podsumowanie
#
# Skalowanie RAG to przede wszystkim problem **inżynierii danych i architektury systemów rozproszonych**.
# Wymaga to przejścia od prostych, lokalnych narzędzi do wyspecjalizowanych, zarządzanych usług w chmurze.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Oddzielaj indeksowanie od zapytań**: Proces indeksowania powinien być osobnym,
#         asynchronicznym potokiem danych (data pipeline).
#     2.  **Wybierz produkcyjną bazę wektorową**: Zapomnij o lokalnym FAISS na produkcji.
#         Wybierz zarządzaną usługę jak Pinecone, Weaviate, Milvus, czy dobrze
#         skonfigurowany PostgreSQL z pgvector.
#     3.  **Myśl w kategoriach usług**: Twoja aplikacja RAG na produkcji to nie jeden skrypt,
#         ale zbiór współpracujących ze sobą, skalowalnych usług: API, bazy wektorowej,
#         i potoku indeksującego.
#     4.  **Asynchroniczność jest kluczowa**: Zarówno komunikacja z bazą wektorową, jak i
#         z LLM-em w Twoim API powinna być asynchroniczna, aby zapewnić wysoką współbieżność.
#
# Opanowanie tych koncepcji pozwoli Ci budować systemy RAG, które są w stanie obsłużyć
# realne, biznesowe obciążenia i rosnąć wraz z Twoimi potrzebami.