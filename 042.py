# ####################################################################
# Moduł 5, Punkt 42: Skalowanie aplikacji LangChain
# ####################################################################
#
# Zbudowałeś już zaawansowane aplikacje AI. Działają świetnie na Twoim komputerze. Ale co się stanie,
# gdy z Twojego chatbota będzie chciało skorzystać jednocześnie 100, 1000 lub 10 000 użytkowników?
# Prosta aplikacja oparta na Streamlit lub pojedynczy skrypt Pythona natychmiast ulegnie przeciążeniu.
#
# Skalowanie to proces projektowania aplikacji w taki sposób, aby mogła ona obsługiwać rosnącą liczbę
# zapytań bez znaczącego spadku wydajności. W kontekście LangChain jest to wyzwanie krytyczne,
# ponieważ operacje na LLM są z natury powolne i kosztowne.
#
# ##################################################
# 1. Główne wyzwania w skalowaniu aplikacji LLM
# ##################################################
#
#     * Latencja (Opóźnienia): Odpowiedzi od modeli LLM mogą trwać od kilkuset milisekund do wielu sekund.
#       Użytkownik nie będzie czekał w nieskończoność na odpowiedź.
#     * Współbieżność (Concurrency): Jak obsłużyć setki jednoczesnych zapytań, gdy każde z nich blokuje zasoby,
#       czekając na odpowiedź z API OpenAI?
#     * Zarządzanie stanem (State Management): Gdzie przechowywać historię konwersacji dla tysięcy użytkowników?
#       Pamięć wbudowana w obiekt `ConversationBufferMemory` działa tylko dla jednej sesji i nie jest skalowalna.
#     * Koszty (Costs): Każde zapytanie do API kosztuje. Niezoptymalizowana aplikacja pod dużym obciążeniem
#       może wygenerować astronomiczne rachunki.
#
# ##################################################
# 2. Kluczowe techniki skalowania w LangChain
# ##################################################
#
# Na szczęście LangChain i ekosystem Pythona oferują narzędzia do walki z tymi problemami.
#
# # 2.1. Caching (Buforowanie)
# # ---------------------------
# # Nie wykonuj dwa razy tej samej pracy! Jeśli dwóch użytkowników zada to samo pytanie, odpowiedź powinna zostać
# # pobrana z pamięci podręcznej, a nie przez ponowne wywołanie LLM.
# #
# #     * `langchain.cache.InMemoryCache`: Prosty cache w pamięci RAM. Dobry do testów, ale znika po restarcie aplikacji.
# #     * `langchain.cache.SQLiteCache`: Zapisuje cache do pliku bazy danych SQLite. Trwały, ale może być wolny pod dużym obciążeniem.
# #     * `langchain.cache.RedisCache`: **Rozwiązanie produkcyjne**. Używa zewnętrznej, błyskawicznej bazy danych Redis do przechowywania cache.
#
import langchain
from langchain.cache import SQLiteCache

# Ustawienie globalnego cache dla LangChain
langchain.llm_cache = SQLiteCache(database_path=".langchain.db")

# Od teraz wszystkie wywołania LLM będą automatycznie buforowane.

# # 2.2. Przetwarzanie asynchroniczne i wsadowe (Async & Batch)
# # -----------------------------------------------------------
# # Zamiast czekać na zakończenie jednej operacji, aby rozpocząć następną, wykonuj je równolegle.
# #
# #     * `ainvoke()`: Asynchroniczna wersja `invoke()`. Pozwala Twojej aplikacji obsługiwać inne zadania,
# #       podczas gdy w tle czeka na odpowiedź od LLM. Kluczowe we frameworkach webowych jak FastAPI.
# #     * `abatch()`: Asynchroniczne przetwarzanie wsadowe. Wysyła listę zapytań w jednej paczce,
# #       co jest znacznie bardziej wydajne niż wysyłanie ich pojedynczo w pętli.
#
# # 2.3. Zewnętrzna, skalowalna pamięć konwersacji
# # ------------------------------------------------
# # Zapomnij o `ConversationBufferMemory`. Na produkcji historia rozmowy musi być przechowywana na zewnątrz,
# # np. w bazie danych. LangChain wspiera ten model poprzez `ChatMessageHistory`.
# #
# #     * `RedisChatMessageHistory`: Przechowuje historię rozmowy dla danego `session_id` w bazie Redis.
# #     * `SQLChatMessageHistory`: Przechowuje historię w dowolnej bazie danych wspieranej przez SQLAlchemy (PostgreSQL, MySQL, etc.).
#
# ####################################################################
# 3. Architektura skalowalnej aplikacji - wzorzec "Worker-Queue"
# ####################################################################
#
# # To profesjonalny wzorzec architektoniczny, który oddziela szybką część aplikacji (interfejs użytkownika) od wolnej (przetwarzanie LLM).
#
# # [Użytkownik] <--> [1. API (np. FastAPI)] <--> [2. Kolejka zadań (np. Redis)] <--> [3. Worker (Celery + LangChain)]
#
# # 1. API (Frontend/Web Server): Lekki serwer (np. FastAPI) przyjmuje zapytanie od użytkownika. Zamiast je przetwarzać,
# #    natychmiast umieszcza je jako "zadanie" w kolejce i informuje użytkownika: "Przyjąłem, przetwarzam...".
# # 2. Kolejka Zadań (Message Queue): System taki jak Redis lub RabbitMQ przechowuje listę zadań do wykonania.
# # 3. Worker: Osobny proces (lub wiele procesów!), który nasłuchuje na kolejce. Gdy pojawia się nowe zadanie,
# #    pobiera je, wykonuje powolną logikę LangChain (wywołanie LLM, RAG, etc.), a wynik zapisuje do bazy danych.
#
# # Ta architektura pozwala na niezależne skalowanie: możesz mieć 2 serwery API i 50 wolniejszych Workerów,
# # dynamicznie dostosowując zasoby do obciążenia.
#
# #######################################################
# 4. Praktyczny przykład: Konceptualny blueprint
# #######################################################
#
# # Poniżej znajduje się uproszczony, konceptualny kod, jak mogłaby wyglądać taka architektura z FastAPI i Celery.
#
# # --- Plik: api.py (to, co widzi użytkownik) ---
from fastapi import FastAPI
# from tasks import run_langchain_task  # Importujemy zadanie z pliku workera - odkomentuj gdy plik tasks.py istnieje

app = FastAPI()

# # Przykładowa definicja zadania, aby kod był wykonywalny bez pliku tasks.py
# # W prawdziwym projekcie ta część byłaby w pliku tasks.py
# class MockTask:
#     def __init__(self, id):
#         self.id = id
#     def delay(self, *args, **kwargs):
#         print(f"Zlecono zadanie z argumentami: {args}, {kwargs}")
#         return self
#
# run_langchain_task = MockTask(id="mock_task_123")
# # Koniec bloku z mock'iem

@app.post("/chat")
async def chat_endpoint(user_input: str, session_id: str):
    # Nie uruchamiamy łańcucha tutaj!
    # Zamiast tego, zlecamy zadanie do wykonania w tle.
    # W prawdziwym projekcie, odkomentuj poniższą linię:
    # task = run_langchain_task.delay(user_input, session_id)
    # return {"message": "Zapytanie przyjęte do realizacji", "task_id": task.id}
    
    # Zastępczy kod, aby API działało:
    print(f"Przyjęto zapytanie dla sesji {session_id} z treścią: {user_input}")
    return {"message": "Zapytanie przyjęte do realizacji (symulacja)", "task_id": "mock_task_123"}


# --- Plik: tasks.py (nasz worker) ---
from celery import Celery
from langchain_openai import ChatOpenAI
from langchain.memory import RedisChatMessageHistory
# # ... inne potrzebne importy, np. do budowy łańcucha

# Konfiguracja Celery do użycia Redis jako brokera wiadomości
# Upewnij się, że serwer Redis jest uruchomiony na localhost:6379
# celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# @celery_app.task
# def run_langchain_task(user_input: str, session_id: str):
#     # Tutaj dzieje się cała "wolna" magia LangChain
#     llm = ChatOpenAI(model="gpt-4o")
#
#     # Używamy zewnętrznej pamięci powiązanej z sesją użytkownika
#     memory = RedisChatMessageHistory(session_id=session_id, url="redis://localhost:6379/0")
#
#     # Przykładowa budowa i wywołanie łańcucha (chain)
#     # chain = ... # Tutaj budujesz swój łańcuch z użyciem 'llm' i 'memory'
#     # result = chain.invoke({"input": user_input})
#
#     # Zapisz wynik do bazy danych, aby API mogło go później pobrać
#     # np. database.save_result(session_id, result)
#
#     print(f"Zadanie dla sesji {session_id} zakończone.")
#     return "Wynik zapisany w bazie" # Celery musi coś zwrócić


# #######################################################
# 5. Podsumowanie
# #######################################################
#
# # Skalowanie aplikacji LangChain to nie problem samego LangChaina, ale problem architektury oprogramowania.
# # To krok, który oddziela hobbystyczne projekty od profesjonalnych wdrożeń.
#
# # Najważniejsze do zapamiętania:
#
# # 1. Oddzielaj szybkie od wolnego: Architektura "Worker-Queue" (np. FastAPI + Celery) to złoty standard.
# #    Nie pozwól, aby wolne wywołania LLM blokowały Twój interfejs użytkownika.
# # 2. Zewnętrzny stan: Przenieś cache i pamięć konwersacji do zewnętrznych, szybkich baz danych jak Redis.
# # 3. Myśl asynchronicznie: Wykorzystuj `ainvoke` i `abatch` wszędzie tam, gdzie to możliwe, aby maksymalnie
# #    wykorzystać zasoby.
# # 4. Monitoruj i optymalizuj: Używaj narzędzi takich jak LangSmith do śledzenia wydajności, kosztów i
# #    opóźnień, aby znaleźć i wyeliminować wąskie gardła w systemie.
#
# # Opanowanie tych technik pozwoli Ci budować aplikacje AI, które są nie tylko inteligentne, ale także szybkie,
# # niezawodne i gotowe na obsługę tysięcy użytkowników.