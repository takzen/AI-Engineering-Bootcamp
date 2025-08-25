# Moduł 10, Punkt 99: Jak zabezpieczyć API przed nieautoryzowanym dostępem?
#
#
#
# Zbudowaliśmy potężne, skalowalne API, które łączy się z bazą danych. Jest ono
# gotowe do obsługi ruchu. Ale jest jeden, krytyczny problem: na razie nasze API
# jest **całkowicie otwarte**. Każdy, kto zna jego adres, może z niego korzystać,
# generując zapytania do LLM i potencjalnie ogromne koszty, a także uzyskując dostęp
# do danych, do których nie powinien.
#
# W tej lekcji nauczymy się, jak zaimplementować podstawowy, ale bardzo solidny
# mechanizm zabezpieczeń: **uwierzytelnianie za pomocą kluczy API (API Keys)**.
#
# 1. Problem: Otwarte drzwi
#
# Publicznie dostępne, niezabezpieczone API jest jak dom z otwartymi na oścież drzwiami.
# Jest to zaproszenie dla:
#
#     *   **Niezautoryzowanych użytkowników**: Osób i botów, które będą używać Twojej
#         aplikacji bez Twojej zgody.
#     *   **Ataków typu "Denial-of-Service" (DoS)**: Ktoś może celowo zalać Twoje API
#         ogromną liczbą zapytań, aby wygenerować wysokie koszty i zablokować usługę
#         dla prawdziwych użytkowników.
#     *   **Wycieków danych**: Jeśli API daje dostęp do wrażliwych informacji, każdy
#         będzie mógł je odczytać.
#
# Musimy wprowadzić mechanizm, który pozwoli nam jednoznacznie zidentyfikować, kto
# wysyła zapytanie i czy ma prawo to robić.
#
# 2. Rozwiązanie: Uwierzytelnianie za pomocą klucza API
#
# Jest to jedna z najprostszych i najpopularniejszych metod zabezpieczania API.
#
# *   **Jak to działa?**:
#     1.  Ty, jako właściciel API, generujesz unikalny, tajny klucz (długi ciąg znaków)
#         dla każdego uprawnionego klienta (np. dla swojej aplikacji frontendowej lub
#         dla partnera biznesowego).
#     2.  Klient, wysyłając zapytanie do Twojego API, musi dołączyć ten klucz w specjalnym
#         **nagłówku HTTP**, np. `X-API-Key`.
#     3.  Twoja aplikacja FastAPI, zanim przetworzy zapytanie, sprawdza ten nagłówek.
#         Porównuje otrzymany klucz z listą prawidłowych, zapisanych po stronie serwera.
#     4.  Jeśli klucz jest prawidłowy, zapytanie jest przetwarzane. Jeśli jest nieprawidłowy
#         lub go brakuje, API natychmiast zwraca błąd `401 Unauthorized` lub `403 Forbidden`.
#
# *   **Zalety**:
#     - Proste w implementacji i zrozumieniu.
#     - Skuteczne w odfiltrowaniu niezautoryzowanego ruchu.
#
# 3. Implementacja w FastAPI
#
# FastAPI, dzięki swojemu systemowi **zależności (Dependencies)**, czyni implementację
# tego mechanizmu niezwykle elegancką i reużywalną. Stworzymy specjalną funkcję-zależność,
# którą będziemy mogli "wstrzyknąć" do każdego endpointu, który chcemy zabezpieczyć.
#
# Krok 0: Przygotowanie aplikacji
# # Będziemy bazować na prostej aplikacji z poprzednich lekcji.
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# Konfiguracja API
# os.environ["MY_APP_API_KEY"] = "super-secret-key-123" # Przechowuj klucz w zmiennej środowiskowej!
if "MY_APP_API_KEY" not in os.environ:
    raise ValueError("Nie ustawiono klucza API aplikacji w zmiennych środowiskowych.")

app = FastAPI(title="Bezpieczne API")

# Krok 1: Definicja schematu klucza API
# Mówimy FastAPI, że będziemy oczekiwać klucza w nagłówku o nazwie "X-Api-Key"
api_key_header_scheme = APIKeyHeader(name="X-Api-Key")

# Pobieramy nasz "poprawny" klucz ze zmiennych środowiskowych
VALID_API_KEY = os.environ.get("MY_APP_API_KEY")

# Krok 2: Stworzenie funkcji-zależności do weryfikacji klucza
async def verify_api_key(api_key: str = Depends(api_key_header_scheme)):
    """
    Ta funkcja jest naszą "bramką". FastAPI automatycznie pobierze wartość
    z nagłówka X-Api-Key i przekaże ją jako argument `api_key`.
    """
    print(f"Otrzymano klucz API: {api_key}")
    if api_key != VALID_API_KEY:
        # Jeśli klucz jest nieprawidłowy, rzucamy wyjątek HTTPException.
        # FastAPI zamieni go na odpowiednią odpowiedź HTTP z kodem błędu.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nieprawidłowy lub brakujący klucz API",
        )
    # Jeśli klucz jest poprawny, funkcja po prostu się kończy,
    # a FastAPI kontynuuje przetwarzanie endpointu.
    return api_key

# Krok 3: Zabezpieczenie endpointów za pomocą zależności
# Endpoint publiczny - nie wymaga klucza
@app.get("/", summary="Endpoint publiczny")
def public_endpoint():
    return {"message": "Witaj! To jest publiczny endpoint."}

# Endpoint zabezpieczony - wymaga poprawnego klucza API
# Dodajemy `Depends(verify_api_key)` do listy argumentów endpointu.
# FastAPI najpierw uruchomi funkcję `verify_api_key`. Jeśli ona zwróci błąd,
# wykonanie `secure_endpoint` zostanie przerwane.
@app.get("/secure", summary="Endpoint zabezpieczony", dependencies=[Depends(verify_api_key)])
def secure_endpoint():
    return {"message": "Witaj w strefie chronionej! Twój klucz API jest poprawny."}
    
# Możemy również pobrać zweryfikowany klucz i użyć go w logice
@app.get("/secure/key-info", summary="Endpoint z informacją o kluczu")
def secure_endpoint_with_key_info(verified_key: str = Depends(verify_api_key)):
    # Tutaj `verified_key` będzie zawierał poprawny klucz,
    # który możemy np. użyć do identyfikacji klienta.
    return {"message": f"Dostęp przyznany. Używasz klucza kończącego się na: ...{verified_key[-4:]}"}


# Krok 4: Testowanie
# Uruchom aplikację: `uvicorn main:app --reload`
# Wejdź na http://127.0.0.1:8000/docs

# 1. Spróbuj wykonać zapytanie do `/secure`. Zobaczysz błąd `403 Forbidden`.
# 2. W prawym górnym rogu Swagger UI kliknij przycisk "Authorize".
# 3. Wpisz swój tajny klucz (`super-secret-key-123`) w pole `X-Api-Key` i kliknij "Authorize".
# 4. Teraz, gdy ponownie spróbujesz wykonać zapytanie do `/secure`, przeglądarka
#    automatycznie dołączy nagłówek z kluczem, a zapytanie przejdzie pomyślnie!

#
# 4. Podsumowanie
#
# Zabezpieczenie API jest absolutnie niezbędnym krokiem przed wdrożeniem jakiejkolwiek
# aplikacji na produkcję, a w przypadku kosztownych aplikacji AI jest to podwójnie
# ważne.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Nigdy nie wdrażaj niezabezpieczonego API**: Zawsze implementuj jakąś formę
#         uwierzytelniania.
#     2.  **Klucze API to prosta i skuteczna metoda**: Są idealne do zabezpieczania
#         komunikacji serwer-serwer lub dla zaufanych klientów.
#     3.  **FastAPI `Depends` to Twój mechanizm strażnika**: Twórz funkcje-zależności,
#         aby hermetyzować logikę weryfikacji i w prosty sposób dołączać ją do
#         dowolnego endpointu.
#     4.  **Przechowuj klucze bezpiecznie**: Klucze API (zarówno ten po stronie serwera,
#         jak i te używane przez klientów) to wrażliwe dane. Przechowuj je w
#         zmiennych środowiskowych lub w bezpiecznych menedżerach sekretów,
#         nigdy na stałe w kodzie.
#
# Opanowując tę technikę, jesteś gotów do budowy nie tylko inteligentnych i skalowalnych,
# ale także bezpiecznych i gotowych na produkcję aplikacji AI.