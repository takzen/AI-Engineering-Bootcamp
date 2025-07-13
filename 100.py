# Moduł 10, Punkt 100: Testowanie i debugowanie aplikacji FastAPI
#
#
#
# Gratulacje! Dotarłeś do setnej, ostatniej lekcji tego kompleksowego kursu. Zbudowaliśmy
# i wdrożyliśmy naszą aplikację AI jako bezpieczne, skalowalne API. Ale skąd mamy
# pewność, że nasze API działa poprawnie? Jak możemy automatycznie weryfikować,
# czy nowa zmiana w kodzie nie zepsuła któregoś z endpointów?
#
# W tej lekcji nauczymy się, jak pisać **testy integracyjne** dla naszej aplikacji FastAPI.
# To kluczowy element profesjonalnego developmentu, który daje nam pewność siebie
# podczas wdrażania zmian i zapewnia stabilność naszej usługi.
#
# 1. Dlaczego testujemy API?
#
# Testowanie API różni się od testów jednostkowych, które poznaliśmy wcześniej.
# W testach jednostkowych mockowaliśmy wywołania LLM, aby testować logikę w izolacji.
# W testach integracyjnych dla API testujemy **cały przepływ zapytania HTTP**:
#
#     *   Czy serwer poprawnie przyjmuje zapytanie?
#     *   Czy walidacja danych (Pydantic) działa zgodnie z oczekiwaniami?
#     *   Czy endpoint zwraca poprawny kod statusu HTTP (200, 201, 404, 403)?
#     *   Czy struktura odpowiedzi JSON jest prawidłowa?
#
# Testy te nie sprawdzają jakości odpowiedzi LLM (od tego mamy ewaluacje w LangSmith),
# ale sprawdzają, czy "hydraulika" naszego API działa bez zarzutu.
#
# 2. Narzędzia: `pytest` i `TestClient` od FastAPI
#
# FastAPI jest stworzone z myślą o testowaniu. Dostarcza wbudowaną klasę `TestClient`,
# która pozwala na wysyłanie "udawanych" zapytań HTTP do naszej aplikacji bez potrzeby
# uruchamiania prawdziwego serwera. Działa to niezwykle szybko i idealnie nadaje się
# do integracji z frameworkiem `pytest`.
#
# **Workflow testowania:**
#
#     1.  Stwórz instancję `TestClient`, przekazując mu naszą aplikację FastAPI.
#     2.  W funkcji testowej, użyj klienta do wykonania zapytania (np. `client.get("/items/1")`).
#     3.  Sprawdź (za pomocą `assert`) kod statusu odpowiedzi.
#     4.  Sprawdź (za pomocą `assert`) zawartość odpowiedzi JSON.
#
# 3. Praktyczny przykład: Pisanie testów dla naszego API
#
# Napiszemy zestaw testów dla aplikacji z zabezpieczonymi endpointami, którą stworzyliśmy
# w poprzedniej lekcji.
#
# Krok 0: Struktura projektu i instalacja
# # Upewnij się, że masz zainstalowany pytest: pip install pytest
#
# /api_security
# |-- main.py             # Kod naszej aplikacji FastAPI
# |-- test_main.py        # Plik z naszymi testami
#
# Krok 1: Kod aplikacji w `main.py`
# # (Używamy kodu z lekcji 99. o zabezpieczaniu API)
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# Ustawiamy klucz na potrzeby testów
os.environ["MY_APP_API_KEY"] = "test-key"

app = FastAPI(title="Testowane API")
api_key_header_scheme = APIKeyHeader(name="X-Api-Key")
VALID_API_KEY = os.environ.get("MY_APP_API_KEY")

async def verify_api_key(api_key: str = Depends(api_key_header_scheme)):
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nieprawidłowy klucz API")
    return api_key

@app.get("/")
def public_endpoint():
    return {"message": "Witaj! To jest publiczny endpoint."}

@app.get("/secure", dependencies=[Depends(verify_api_key)])
def secure_endpoint():
    return {"message": "Dostęp przyznany."}

# Krok 2: Kod testów w `test_main.py`
from fastapi.testclient import TestClient
from .main import app # Importujemy naszą aplikację FastAPI

# Tworzymy instancję klienta testowego.
# Będziemy jej używać we wszystkich testach.
client = TestClient(app)

def test_read_public_endpoint():
    # Wysyłamy zapytanie GET do endpointu "/"
    response = client.get("/")
    # Sprawdzamy, czy kod statusu to 200 OK
    assert response.status_code == 200
    # Sprawdzamy, czy odpowiedź JSON jest zgodna z oczekiwaniami
    assert response.json() == {"message": "Witaj! To jest publiczny endpoint."}

def test_read_secure_endpoint_no_key():
    # Próbujemy uzyskać dostęp do zabezpieczonego endpointu BEZ klucza API
    response = client.get("/secure")
    # Oczekujemy błędu 403 Forbidden (a nie 401, bo tak zdefiniowaliśmy w kodzie)
    assert response.status_code == 403
    assert response.json() == {"detail": "Nieprawidłowy klucz API"}

def test_read_secure_endpoint_wrong_key():
    # Próbujemy uzyskać dostęp z NIEPRAWIDŁOWYM kluczem API
    headers = {"X-Api-Key": "wrong-key-123"}
    response = client.get("/secure", headers=headers)
    # Również oczekujemy błędu 403
    assert response.status_code == 403

def test_read_secure_endpoint_correct_key():
    # Próbujemy uzyskać dostęp z PRAWIDŁOWYM kluczem API
    headers = {"X-Api-Key": "test-key"}
    response = client.get("/secure", headers=headers)
    # Oczekujemy sukcesu (kod 200)
    assert response.status_code == 200
    assert response.json() == {"message": "Dostęp przyznany."}

# Krok 3: Uruchomienie testów
# # W terminalu, w głównym folderze projektu, wystarczy wpisać:
# pytest
#
# # Pytest automatycznie znajdzie pliki `test_*.py` i funkcje `test_*()`,
# # uruchomi je i przedstawi zwięzły raport z wynikami.
#
# 4. Debugowanie w FastAPI
#
# A co, jeśli test zawiedzie lub aplikacja zachowuje się nieoczekiwanie podczas
# ręcznego testowania?
#
# *   **Logi Uvicorn**: Pierwszym miejscem, gdzie szukasz informacji, jest konsola,
#     w której działa serwer Uvicorn. Każde przychodzące zapytanie jest tam logowane,
#     wraz z kodem statusu odpowiedzi. Błędy serwera (kodu 500) również zostaną tam
#     wyświetlone wraz z pełnym tracebackiem.
# *   **Stary, dobry `print()`**: W trakcie developmentu, umieszczanie `print()`
#     wewnątrz funkcji endpointu to najszybszy sposób, aby zobaczyć wartości
#     zmiennych czy stan obiektów w momencie przetwarzania zapytania.
# *   **Debuger Pythona**: Możesz uruchomić swoją aplikację FastAPI w trybie debugowania
#     w edytorze kodu (np. VS Code). Ustawiasz "breakpoint" w linii kodu wewnątrz
#     endpointu, a gdy nadejdzie zapytanie, wykonanie programu zatrzyma się w tym
#     miejscu, pozwalając Ci na interaktywne sprawdzanie zmiennych i przechodzenie
#     przez kod krok po kroku.
#
# 5. Podsumowanie – Zakończenie Kursu
#
# Testowanie to nie jest dodatek – to integralna część cyklu życia aplikacji, która
# gwarantuje jej stabilność, niezawodność i ułatwia jej utrzymanie w przyszłości.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Testuj swoje API**: Pisz testy integracyjne, aby weryfikować działanie
#         endpointów, walidację danych i kody odpowiedzi HTTP.
#     2.  **Używaj `TestClient`**: To wbudowane w FastAPI narzędzie, które sprawia,
#         że pisanie testów jest proste i szybkie.
#     3.  **Pokrywaj przypadki brzegowe**: Testuj nie tylko "szczęśliwą ścieżkę",
#         ale także przypadki błędów – brakujące dane, nieprawidłowe wartości,
#         błędne uwierzytelnianie.
#     4.  **Automatyzuj w CI/CD**: Podobnie jak testy ewaluacyjne, testy API powinny
#         być częścią Twojego zautomatyzowanego pipeline'u wdrożeniowego.
#
# **Gratulacje!** Ukończyłeś cały kurs. Posiadasz teraz kompleksową wiedzę, która
# prowadzi od podstawowych koncepcji AI, przez budowę zaawansowanych, inteligentnych
# systemów, aż po ich profesjonalne testowanie, wdrożenie i monitorowanie. Jesteś
# w pełni wyposażony, aby tworzyć nową generację aplikacji AI. Powodzenia w Twoich
# przyszłych projektach!