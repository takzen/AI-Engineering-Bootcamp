# Moduł 10, Punkt 93: Tworzenie endpointów w FastAPI
#
#
#
# Znamy już ogólną teorię działania FastAPI. Teraz czas na praktykę i poznanie różnych
# "smaków" endpointów. Endpoint to pojedynczy, adresowalny punkt w naszym API, który
# wykonuje konkretną akcję. Sposób, w jaki go zdefiniujemy, determinuje, jak inne
# aplikacje będą się z nim komunikować.
#
# W tej lekcji nauczymy się tworzyć endpointy, które przyjmują dane na różne sposoby:
# jako część adresu URL, jako parametry zapytania i jako złożone obiekty w ciele żądania.
#
# 1. Metody HTTP: Czasownik Twojego zapytania
#
# Każdy endpoint jest powiązany z jedną z metod HTTP, która określa rodzaj operacji,
# jaką chcemy wykonać. Najważniejsze z nich to:
#
#     *   **GET**: Służy do **pobierania** danych. Powinien być operacją tylko do odczytu.
#     *   **POST**: Służy do **tworzenia** nowych zasobów. Dane do stworzenia zasobu są
#         przesyłane w ciele żądania.
#     *   **PUT**: Służy do **pełnej aktualizacji** istniejącego zasobu.
#     *   **DELETE**: Służy do **usuwania** zasobu.
#
# FastAPI udostępnia dla każdej z tych metod odpowiedni dekorator: `@app.get()`,
# `@app.post()`, `@app.put()`, `@app.delete()`.
#
# 2. Sposoby przekazywania danych do endpointu
#
# FastAPI pozwala na eleganckie definiowanie, skąd mają pochodzić dane dla parametrów
# naszej funkcji. Zobaczmy to na praktycznych przykładach.
#
# Krok 0: Przygotowanie aplikacji
# # Utwórz plik `main.py` z poniższą zawartością.
# # Aby go uruchomić, użyj komendy: uvicorn main:app --reload
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Inicjalizacja aplikacji
app = FastAPI(title="Praktyka z Endpointami")

# Prosta "baza danych" w pamięci do celów demonstracyjnych
fake_items_db = [
    {"item_name": "Laptop"},
    {"item_name": "Myszka"},
    {"item_name": "Klawiatura"},
]

# Krok 1: Endpoint z parametrem w ścieżce (Path Parameter)
# Idealny do identyfikowania konkretnego zasobu.
@app.get("/items/{item_id}", summary="Pobierz pojedynczy przedmiot")
def get_item_by_id(item_id: int):
    """
    Pobiera przedmiot z naszej "bazy danych" na podstawie jego ID (indeksu).
    FastAPI automatycznie skonwertuje `item_id` z URL na `int`.
    """
    if 0 <= item_id < len(fake_items_db):
        return fake_items_db[item_id]
    return {"error": "Przedmiot nie znaleziony"}

# Przykład wywołania: GET http://127.0.0.1:8000/items/1
# Zwróci: {"item_name": "Myszka"}

# Krok 2: Endpoint z parametrami zapytania (Query Parameters)
# Idealny do filtrowania, sortowania, paginacji.
@app.get("/search", summary="Wyszukaj przedmioty")
def search_items(query: str, case_sensitive: bool = False):
    """
    Przeszukuje listę przedmiotów. `query` jest parametrem wymaganym.
    `case_sensitive` jest opcjonalny i domyślnie ma wartość `False`.
    """
    results = []
    for item in fake_items_db:
        name = item["item_name"]
        if not case_sensitive:
            name = name.lower()
            query = query.lower()
        if query in name:
            results.append(item)
    return results

# Przykład wywołania: GET http://127.0.0.1:8000/search?query=top
# Zwróci: [{"item_name": "Laptop"}]
# Przykład wywołania: GET http://127.0.0.1:8000/search?query=Top&case_sensitive=true
# Zwróci: [] (pustą listę)

# Krok 3: Endpoint z ciałem żądania (Request Body)
# Idealny do tworzenia nowych zasobów z użyciem metody POST.
# Najpierw definiujemy model danych za pomocą Pydantic.
class Item(BaseModel):
    item_name: str
    tags: List[str] = [] # Opcjonalna lista tagów

@app.post("/items", summary="Dodaj nowy przedmiot", status_code=201)
def create_item(item: Item):
    """
    Dodaje nowy przedmiot do naszej "bazy danych".
    FastAPI automatycznie zwaliduje, czy dane w ciele żądania
    pasują do modelu `Item`. `status_code=201` ustawia domyślny
    kod odpowiedzi HTTP na "201 Created".
    """
    new_item = item.dict()
    fake_items_db.append(new_item)
    return {"status": "Przedmiot dodany", "item": new_item}

# Przykład wywołania: POST http://127.0.0.1:8000/items
# z ciałem JSON:
# {
#   "item_name": "Monitor",
#   "tags": ["gaming", "4k"]
# }
# Zwróci: {"status": "Przedmiot dodany", "item": {"item_name": "Monitor", "tags": ["gaming", "4k"]}}

# Krok 4: Endpoint łączący wszystkie techniki
# Możemy łączyć parametry ze ścieżki, z zapytania i z ciała żądania w jednym endpoincie.
@app.put("/items/{item_id}", summary="Zaktualizuj przedmiot")
def update_item(item_id: int, item_update: Item, importance: int | None = None):
    """
    Aktualizuje istniejący przedmiot.
    - `item_id` pochodzi ze ścieżki.
    - `item_update` pochodzi z ciała żądania.
    - `importance` to opcjonalny parametr zapytania.
    """
    if 0 <= item_id < len(fake_items_db):
        fake_items_db[item_id] = item_update.dict()
        return {
            "status": "Przedmiot zaktualizowany",
            "item_id": item_id,
            "new_data": item_update,
            "importance": importance
        }
    return {"error": "Przedmiot nie znaleziony"}

# Przykład wywołania: PUT http://127.0.0.1:8000/items/0?importance=5
# z ciałem JSON:
# {
#   "item_name": "Nowy Laptop Pro",
#   "tags": ["praca", "dev"]
# }

#
# 3. Podsumowanie
#
# Opanowanie różnych sposobów definiowania endpointów to klucz do tworzenia elastycznych
# i intuicyjnych w użyciu API.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Używaj odpowiedniej metody HTTP**: `GET` do pobierania, `POST` do tworzenia, `PUT` do
#         aktualizacji.
#     2.  **Parametry w ścieżce (`/items/{id}`)** służą do identyfikacji konkretnego zasobu.
#     3.  **Parametry w zapytaniu (`?query=...`)** służą do filtrowania, sortowania i opcji.
#     4.  **Ciało żądania (Request Body)** służy do przesyłania złożonych danych, a Pydantic
#         automatycznie je waliduje.
#     5.  **Możesz łączyć techniki**: Jeden endpoint może jednocześnie korzystać z parametrów
#         ze ścieżki, zapytania i ciała żądania.
#
# Eksperymentuj z tymi przykładami w interaktywnej dokumentacji pod adresem `/docs`,
# aby w pełni zrozumieć, jak działa każdy z mechanizmów.