# Moduł 2, Lekcja 15: Tworzenie i obsługa API w Pythonie
#
#
#
# W dzisiejszym, połączonym świecie, programy rzadko działają w izolacji.
# Komunikują się ze sobą, wymieniając dane i usługi. Sercem tej komunikacji jest API.
#
# API (Application Programming Interface - Interfejs Programowania Aplikacji) to zbiór
# reguł i protokołów, który określa, jak różne aplikacje mogą ze sobą rozmawiać.
#
# Pomyśl o tym jak o menu w restauracji:
#     - Ty (klient) nie musisz wiedzieć, jak kucharz przygotowuje danie.
#     - Menu (API) mówi Ci, co możesz zamówić (jakie są dostępne "funkcje").
#     - Składasz zamówienie kelnerowi w określony sposób (wysyłasz zapytanie do API).
#     - Kuchnia (serwer) przygotowuje danie i Ci je dostarcza (serwer zwraca odpowiedź).
#
# W świecie AI API używamy non-stop do:
#     - Odpytywania modeli językowych (np. API od OpenAI, Google).
#     - Pobierania danych (np. z giełdy, serwisów pogodowych).
#     - Udostępniania naszych własnych, wytrenowanych modeli innym.
#
# Dziś nauczymy się być zarówno klientem restauracji (konsumować API),
# jak i kucharzem (tworzyć własne API).
#
# WAŻNE: Przed uruchomieniem tego skryptu, upewnij się, że masz zainstalowane potrzebne biblioteki.
# W terminalu/wierszu poleceń wpisz:
# pip install requests fastapi "uvicorn[standard]"
#
# ---------------------------------------------------------------------------------
# CZĘŚĆ 1: KONSUMOWANIE API (JESTEŚMY KLIENTEM)
# ---------------------------------------------------------------------------------
#
# Do wysyłania zapytań do zewnętrznych API użyjemy biblioteki `requests`.
# Jest ona niezwykle prosta i intuicyjna.

import requests
import json # Moduł do pracy z formatem JSON

# 1.1 Wysyłanie prostego zapytania GET
#
# Użyjemy darmowego, publicznego API do testowania: JSONPlaceholder.
# Chcemy pobrać informacje o poście numer 1.
URL = "https://jsonplaceholder.typicode.com/posts/1"

print("--- Konsumowanie API ---")
print(f"Wysyłam zapytanie GET na adres: {URL}")

# Wysyłamy zapytanie i przechowujemy odpowiedź w zmiennej
response = requests.get(URL)

# 1.2 Sprawdzanie odpowiedzi
#
# Zawsze należy sprawdzić, czy nasze zapytanie się powiodło.
# Służy do tego kod statusu HTTP. Najważniejszy dla nas to `200 OK`.
if response.status_code == 200:
    print("Sukces! Otrzymano odpowiedź (status 200 OK).")
    
    # API najczęściej zwracają dane w formacie JSON (JavaScript Object Notation).
    # Biblioteka `requests` ma wbudowaną metodę do parsowania JSON-a na słownik Pythona.
    dane = response.json()
    
    print("\nOdebrane dane w formacie JSON, sparsowane do słownika Pythona:")
    print(dane)
    
    print(f"\nTytuł posta: {dane['title']}")
    
else:
    print(f"Błąd! Nie udało się pobrać danych. Status: {response.status_code}")


# 1.3 Przykład z kontekstem AI: Zapytanie do modelu językowego (koncepcja)
#
# Tak wyglądałoby (w uproszczeniu) zapytanie do API modelu AI, np. od OpenAI.
# UWAGA: Ten kod jest zakomentowany, ponieważ wymaga prawdziwego klucza API.
"""
openai_api_url = "https://api.openai.com/v1/chat/completions"
api_key = "TWOJ_PRAWDZIWY_KLUCZ_API" # Nigdy nie umieszczaj klucza bezpośrednio w kodzie!

# Klucze API i inne wrażliwe dane przesyła się w nagłówkach (headers)
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Do wysyłania danych (np. naszego polecenia) używamy metody POST i przekazujemy dane w ciele (body)
body = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Opowiedz krótki dowcip o programowaniu."}
    ]
}

# Używamy metody POST do wysłania danych
# response_ai = requests.post(openai_api_url, headers=headers, json=body)

# if response_ai.status_code == 200:
#     odpowiedz_ai = response_ai.json()
#     print(odpowiedz_ai['choices'][0]['message']['content'])
"""

# ---------------------------------------------------------------------------------
# CZĘŚĆ 2: TWORZENIE WŁASNEGO API (JESTEŚMY KUCHNIĄ)
# ---------------------------------------------------------------------------------
#
# Chcemy teraz udostępnić naszą własną funkcję lub model światu.
# Użyjemy do tego nowoczesnej biblioteki `FastAPI`. Jest ona niezwykle szybka,
# łatwa w użyciu i automatycznie generuje interaktywną dokumentację.
#
# UWAGA: Poniższy kod należy zapisać w osobnym pliku, np. `moje_api.py`.
# Następnie, aby go uruchomić, wchodzimy do terminala, przechodzimy do folderu
# z tym plikiem i wpisujemy komendę:
# uvicorn moje_api:app --reload
#
# `uvicorn` - to serwer, który uruchamia naszą aplikację
# `moje_api` - nazwa pliku Pythona (bez .py)
# `app` - nazwa zmiennej w pliku, która przechowuje naszą aplikację FastAPI
# `--reload` - powoduje, że serwer automatycznie restartuje się po każdej zmianie w kodzie
#
# Poniżej znajduje się kod, który umieścilibyśmy w pliku `moje_api.py`:
"""
from fastapi import FastAPI

# Tworzymy instancję aplikacji FastAPI
app = FastAPI(
    title="Moje pierwsze API do AI",
    description="To API demonstruje, jak udostępnić prosty model."
)

# 2.1 Definiowanie endpointu za pomocą dekoratora
# Dekorator `@app.get("/")` mówi FastAPI: "Gdy ktoś wyśle zapytanie GET
# na główny adres URL (np. http://127.0.0.1:8000/), uruchom poniższą funkcję."
@app.get("/")
def read_root():
    # FastAPI automatycznie przekonwertuje ten słownik na format JSON
    return {"message": "Witaj w moim API! Jestem gotów do pracy."}


# 2.2 Endpoint, który przyjmuje parametry
# Chcemy stworzyć endpoint, który będzie symulował analizę sentymentu tekstu.
# Endpoint będzie dostępny pod adresem /analiza-sentymentu
@app.get("/analiza-sentymentu")
def analizuj_sentyment(tekst: str):
    # W prawdziwej aplikacji tutaj wywołalibyśmy nasz model AI
    print(f"Otrzymano tekst do analizy: '{tekst}'")
    
    sentyment = "neutralny"
    pewnosc = 0.6
    
    if "super" in tekst.lower() or "świetny" in tekst.lower():
        sentyment = "pozytywny"
        pewnosc = 0.95
    elif "źle" in tekst.lower() or "fatalny" in tekst.lower():
        sentyment = "negatywny"
        pewnosc = 0.98
        
    return {
        "analizowany_tekst": tekst,
        "wynik_analizy": {
            "sentyment": sentyment,
            "pewnosc_modelu": pewnosc
        }
    }

# Po uruchomieniu serwera (uvicorn moje_api:app --reload), wejdź w przeglądarce na:
# 1. http://127.0.0.1:8000/ - zobaczysz wiadomość powitalną.
# 2. http://127.0.0.1:8000/analiza-sentymentu?tekst=Ten kurs jest super! - zobaczysz wynik analizy.
# 3. http://127.0.0.1:8000/docs - zobaczysz DARMOWĄ, interaktywną dokumentację API!
"""


# 3. Podsumowanie
#
#     * API to standard komunikacji między aplikacjami.
#
#     * Do konsumowania (używania) API w Pythonie używamy głównie biblioteki `requests`.
#       Wysyłamy zapytanie (np. `requests.get()`), sprawdzamy status odpowiedzi
#       i przetwarzamy otrzymane dane (najczęściej z formatu JSON).
#
#     * Do tworzenia własnych API świetnie nadaje się biblioteka `FastAPI`.
#       Definiujemy "endpointy" (adresy URL) za pomocą dekoratorów (`@app.get`)
#       i piszemy funkcje, które obsługują zapytania.
#
#     * Umiejętność pracy z API jest absolutnie kluczowa dla każdego specjalisty AI,
#       zarówno do pozyskiwania danych, jak i do wdrażania własnych modeli.
