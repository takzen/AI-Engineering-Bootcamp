# Moduł 11, Lekcja 104: Tworzenie własnej aplikacji AI od podstaw

"""
Witaj w pierwszej lekcji praktycznej! To tutaj teoria zamienia się w kod,
a Twój pomysł na projekt zaczyna nabierać realnych kształtów.
W tej lekcji nie napiszemy jeszcze skomplikowanej logiki AI, ale zrobimy coś
znacznie ważniejszego: zbudujemy solidny fundament pod całą aplikację.

To tutaj zaczyna się prawdziwa praca inżyniera – od zaplanowania struktury,
przygotowania środowiska i upewnienia się, że wszystkie podstawowe elementy
działają, zanim dodamy do nich złożoność.

Celem tej lekcji jest stworzenie i skonfigurowanie szkieletu naszego projektu
oraz uruchomienie najprostszego "Hello, World" dla naszego serwera API.
"""

# ==============================================================================
# 1. Plan Działania – Architektura Projektu
# ==============================================================================

"""
Zanim napiszemy choćby jedną linijkę kodu, musimy mieć plan. Dobra organizacja
plików i folderów to klucz do utrzymania porządku w projekcie, który będzie się rozwijał.
Nasza aplikacja będzie miała następującą strukturę:
"""

# project_rodo_ai/
# │
# ├── app/                      # Folder na główną logikę naszej aplikacji (backend)
# │   ├── __init__.py           # Sprawia, że 'app' jest pakietem Pythona
# │   └── main.py               # Główny plik z naszym serwerem FastAPI
# │
# ├── data/                     # Folder na surowe dane źródłowe
# │   └── rodo_pl.pdf           # Tutaj umieścimy nasz dokument do analizy
# │
# ├── ui/                       # Folder na kod interfejsu użytkownika
# │   └── app_ui.py             # Aplikacja w Streamlit
# │
# ├── .env                      # Plik do przechowywania "sekretów" (np. klucza API)
# │
# ├── requirements.txt          # Lista wszystkich bibliotek potrzebnych do projektu
# │
# └── .gitignore                # Plik określający, które pliki ignorować w systemie kontroli wersji Git

"""
Stwórz teraz w swoim edytorze kodu dokładnie taką strukturę folderów i pustych plików.
Pamiętaj, aby plik __init__.py w folderze 'app/' był pusty.
"""

# ==============================================================================
# 2. Izolacja Środowiska – Wirtualne Środowisko
# ==============================================================================

"""
Profesjonalne projekty w Pythonie zawsze tworzy się w izolowanym środowisku wirtualnym.
Dzięki temu zależności (biblioteki) jednego projektu nie kolidują z innymi.

Otwórz terminal w głównym folderze swojego projektu (np. 'project_rodo_ai/') i wykonaj poniższe komendy.
"""

# Krok 1: Stworzenie wirtualnego środowiska o nazwie '.venv'
# python -m venv .venv

# Krok 2: Aktywacja środowiska
# Na systemach Linux/macOS:
# source .venv/bin/activate

# Na systemie Windows:
# .venv\Scripts\activate

"""
Po poprawnej aktywacji, na początku linii w terminalu powinna pojawić się nazwa środowiska, np. '(.venv)'.
Od teraz wszystkie instalowane biblioteki trafią tylko do tego projektu.
"""

# ==============================================================================
# 3. Niezbędne Narzędzia – Instalacja Zależności
# ==============================================================================

"""
Nasza aplikacja będzie potrzebowała kilku zewnętrznych bibliotek. Zdefiniujemy je
w pliku 'requirements.txt', co pozwoli każdemu łatwo zainstalować dokładnie te same wersje.

Otwórz plik 'requirements.txt' i wklej do niego poniższą zawartość:
"""
# --- Zawartość pliku requirements.txt ---
# fastapi           # Framework do budowy naszego API
# uvicorn[standard] # Serwer, na którym będzie działać FastAPI
# python-dotenv     # Do wczytywania zmiennych środowiskowych z pliku .env
# langchain         # Główny framework do pracy z LLM
# openai            # Oficjalna biblioteka OpenAI
# pypdf             # Do wczytywania i parsowania plików PDF
# chromadb          # Baza wektorowa, w której będziemy przechowywać naszą wiedzę
# tiktoken          # Tokenizer używany przez OpenAI do liczenia tokenów
# streamlit         # Do stworzenia prostego interfejsu użytkownika
# requests          # Do komunikacji między interfejsem a naszym API
# ------------------------------------------

"""
Teraz, upewniwszy się, że wirtualne środowisko jest aktywne,
zainstaluj wszystkie te biblioteki jedną komendą w terminalu:
"""
# pip install -r requirements.txt

# ==============================================================================
# 4. Bezpieczeństwo Sekretów – Plik .env
# ==============================================================================

"""
NIGDY nie umieszczaj kluczy API bezpośrednio w kodzie. To bardzo zła i niebezpieczna praktyka.
Użyjemy pliku '.env', który będzie przechowywał nasz klucz.

Otwórz plik '.env' i wpisz do niego swój klucz API od OpenAI:
"""
# OPENAI_API_KEY="sk-..."

"""
Ważne: Plik '.env' nigdy nie powinien trafić do publicznego repozytorium (np. na GitHub).
Otwórz plik '.gitignore' i dodaj do niego poniższe wpisy, aby mieć pewność, że ani
środowisko wirtualne, ani klucze API nie zostaną przypadkowo opublikowane.
"""
# --- Zawartość pliku .gitignore ---
# .venv/
# .env
# __pycache__/
# vector_db/
# ----------------------------------

# ==============================================================================
# 5. Pierwszy Działający Element – "Hello, World" w FastAPI
# ==============================================================================

"""
Mamy już całą strukturę. Czas napisać pierwszy kod i sprawdzić, czy wszystko działa.
Uruchomimy najprostszy możliwy serwer API.

Otwórz plik 'app/main.py' i wklej do niego poniższy kod:
"""
# --- Zawartość pliku app/main.py ---
from fastapi import FastAPI

# Tworzymy instancję aplikacji FastAPI
app = FastAPI(
    title="RODO Ekspert AI API",
    description="API dla aplikacji opartej na wiedzy z dokumentu RODO."
)

@app.get("/")
def read_root():
    """
    To jest nasz pierwszy, główny endpoint.
    Gdy ktoś wejdzie na główny adres naszego API, otrzyma tę odpowiedź.
    """
    return {"message": "Witaj w API dla projektu RODO Ekspert AI!"}
# -----------------------------------

"""
Teraz czas na moment prawdy! Uruchommy nasz serwer.
W terminalu, w głównym folderze projektu, wykonaj komendę:
"""
# uvicorn app.main:app --reload

"""
Wyjaśnienie komendy:
- 'uvicorn': nazwa serwera, który uruchamiamy.
- 'app.main:app': ścieżka do naszej aplikacji. Znajdź w pakiecie 'app', w pliku 'main', obiekt o nazwie 'app'.
- '--reload': bardzo przydatna flaga. Powoduje, że serwer automatycznie uruchomi się ponownie po każdej zmianie w kodzie.

Jeśli wszystko poszło dobrze, powinieneś zobaczyć w terminalu informację,
że aplikacja działa pod adresem http://127.0.0.1:8000.

Otwórz ten adres w przeglądarce. Powinieneś zobaczyć: {"message":"Witaj w API dla projektu RODO Ekspert AI!"}
"""

# ==============================================================================
# Podsumowanie i Następne Kroki
# ==============================================================================

"""
Gratulacje! Właśnie stworzyłeś solidny szkielet pod swoją aplikację AI.
To może nie wyglądać na wiele, ale wykonałeś kluczową pracę inżynierską:
- Zaplanowałeś strukturę projektu.
- Skonfigurowałeś izolowane środowisko pracy.
- Zarządziłeś zależnościami.
- Zabezpieczyłeś klucze API.
- Uruchomiłeś działający serwer API.

Masz teraz idealną bazę do dalszej pracy.

W następnej lekcji zajmiemy się logiką pozyskiwania i przetwarzania danych.
Napiszemy skrypt, który wczyta nasz dokument PDF z RODO, podzieli go
na fragmenty i przygotuje do umieszczenia w bazie wektorowej. Do dzieła!
"""