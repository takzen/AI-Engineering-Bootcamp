# Moduł 10, Punkt 92: Wprowadzenie do FastAPI
#
#
#
# W poprzedniej lekcji zbudowaliśmy nasze pierwsze API. Użyliśmy do tego frameworka FastAPI,
# ale zrobiliśmy to w bardzo uproszczony sposób. Teraz czas na głębsze zanurzenie się
# w świat FastAPI, aby zrozumieć jego kluczowe koncepcje i możliwości.
#
# Dobre zrozumienie FastAPI pozwoli Ci tworzyć bardziej zaawansowane, bezpieczne
# i wydajne API dla Twoich aplikacji AI.
#
# 1. Czym tak naprawdę jest FastAPI?
#
# FastAPI to nowoczesny, wysokowydajny framework webowy w Pythonie do budowania API.
# "Framework webowy" oznacza, że dostarcza on gotowy zestaw narzędzi i struktur,
# które drastycznie upraszczają tworzenie aplikacji sieciowych. Zamiast pisać od zera
# obsługę protokołu HTTP, routing czy walidację danych, używamy gotowych,
# przetestowanych komponentów.
#
# FastAPI opiera się na dwóch filarach:
#
#     *   **Starlette**: To mikro-framework, który dostarcza podstawową funkcjonalność webową
#         (routing, obsługa żądań i odpowiedzi). FastAPI go "opakowuje" i rozszerza.
#     *   **Pydantic**: To biblioteka do walidacji danych. Jest ona sercem tego, co czyni
#         FastAPI tak potężnym i łatwym w użyciu.
#
# 2. Kluczowe koncepcje w FastAPI
#
#     **a) Operacje ścieżki (Path Operations)**
#
#     To podstawowy element każdej aplikacji FastAPI. Jest to połączenie:
#     *   **Ścieżki (Path)**: Adres URL, np. `/users/me` lub `/items/{item_id}`.
#     *   **Operacji (Operation)**: Jedna ze standardowych metod HTTP, np. `GET`, `POST`, `PUT`, `DELETE`.
#
#     W kodzie definiujemy to za pomocą **dekoratorów**, np. `@app.get("/")` czy `@app.post("/items")`.
#
#     **b) Parametry ścieżki (Path Parameters)**
#
#     Pozwalają na przekazywanie wartości bezpośrednio w adresie URL.
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

#     # Wywołanie: GET http://127.0.0.1:8000/items/5
#     # FastAPI automatycznie sprawdzi, czy `item_id` (czyli 5) jest liczbą całkowitą.
#
#     **c) Parametry zapytania (Query Parameters)**
#
#     To parametry przekazywane po znaku `?` w adresie URL. Są idealne do filtrowania i sortowania.
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

#     # Wywołanie: GET http://127.0.0.1:8000/items/?skip=0&limit=20
#     # FastAPI automatycznie przypisze `skip=0` i `limit=20`.
#     # Jeśli parametry nie zostaną podane, użyje wartości domyślnych.
#
#     **d) Ciało zapytania (Request Body)**
#
#     Gdy potrzebujemy przesłać złożone dane (jak w naszych aplikacjach AI), używamy ciała
#     zapytania, najczęściej w formacie JSON. Tutaj wkracza **Pydantic**.
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.post("/items/")
def create_item(item: Item):
    return item

#     # Wywołanie: POST http://127.0.0.1:8000/items/ z ciałem JSON:
#     # { "name": "Laptop", "price": 4999.99 }
#     # FastAPI automatycznie:
#     # 1. Odczyta ciało zapytania.
#     # 2. Sprawdzi, czy zawiera `name` (string) i `price` (float).
#     # 3. Utworzy instancję klasy `Item`.
#     # 4. Przekaże ten obiekt do naszej funkcji.
#     # Jeśli dane będą nieprawidłowe (np. cena jako string), automatycznie zwróci błąd 422.
#
#     **e) Asynchroniczność (`async` i `await`)**
#
#     To najważniejsza cecha z perspektywy aplikacji AI. Jeśli nasza funkcja wykonuje
#     operację, która wymaga czekania (np. wywołanie API LLM, zapytanie do bazy danych),
#     możemy ją zdefiniować jako `async def`.
#
#     Dzięki temu, gdy serwer czeka na odpowiedź z zewnątrz, **nie jest zablokowany** i może
#     w tym czasie obsługiwać inne, przychodzące zapytania. To drastycznie zwiększa
#     wydajność i przepustowość naszej aplikacji.
async def run_long_task():
    # `asyncio.sleep` symuluje długotrwałą operację, jak wywołanie LLM
    await asyncio.sleep(5)
    return "Zadanie zakończone"

@app.post("/long-task")
async def start_long_task():
    result = await run_long_task()
    return {"result": result}
#
# 3. Automatyczna dokumentacja: Twój najlepszy przyjaciel
#
# FastAPI automatycznie generuje dokumentację w dwóch standardach:
#
#     *   **/docs**: Interaktywna dokumentacja **Swagger UI**. Pozwala na przeglądanie
#         wszystkich endpointów i, co najważniejsze, **testowanie ich bezpośrednio w przeglądarce**.
#     *   **/redoc**: Alternatywny widok dokumentacji, bardziej statyczny i czytelny.
#
# Ta funkcja jest bezcenna. Nie musisz ręcznie pisać dokumentacji – ona tworzy się sama
# na podstawie Twojego kodu, typów danych i docstringów.
#
# 4. Podsumowanie
#
# Zrozumienie tych kluczowych koncepcji FastAPI pozwoli Ci na swobodne i świadome
# tworzenie API.
#
# Najważniejsze do zapamiętania:
#
#     1.  **FastAPI to framework**: Dostarcza gotowe rozwiązania do budowy aplikacji webowych.
#     2.  **Pydantic to serce walidacji**: Definiowanie modeli danych za pomocą Pydantic
#         zapewnia bezpieczeństwo i świetną dokumentację.
#     3.  **Dekoratory definiują endpointy**: Używaj `@app.get`, `@app.post` itp., aby
#         określić, jak Twoje API ma reagować na zapytania.
#     4.  **`async`/`await` dla wydajności**: Zawsze używaj `async def` dla endpointów,
#         które wykonują operacje wejścia/wyjścia (I/O), takie jak wywołania LLM.
#     5.  **Korzystaj z `/docs`**: Interaktywna dokumentacja to Twoje podstawowe narzędzie
#         do testowania i eksploracji API podczas rozwoju.
#
# Masz teraz solidne fundamenty, aby budować nie tylko proste, ale także złożone,
# wielo-endpointowe i wydajne API dla Twoich aplikacji AI.