# Moduł 10, Punkt 91: Jak stworzyć API dla modelu AI?
#
#
#
# Gratulacje! Dotarłeś do modułu, w którym nasze aplikacje AI w końcu "wychodzą do ludzi".
# Do tej pory tworzyliśmy potężne skrypty i przepływy, ale działały one tylko na naszym
# komputerze. Aby udostępnić nasz model światu – np. na stronie internetowej, w aplikacji
# mobilnej czy jako usługę dla innego serwisu – musimy stworzyć dla niego **API**.
#
# API (Application Programming Interface) to nic innego jak **"drzwi wejściowe"** do naszej
# aplikacji. To ustandaryzowany sposób, w jaki inne programy mogą wysyłać do niej
# zapytania i otrzymywać odpowiedzi przez internet. W tej lekcji nauczymy się, jak
# zbudować takie API za pomocą frameworka FastAPI.
#
# 1. Dlaczego FastAPI jest idealnym wyborem?
#
# Mogliśmy użyć innych narzędzi (jak Flask czy Django), ale FastAPI jest obecnie
# standardem w świecie API dla AI i machine learningu z kilku kluczowych powodów:
#
#     *   **Wydajność**: Jest to jeden z najszybszych frameworków webowych w Pythonie.
#     *   **Asynchroniczność**: Świetnie radzi sobie z obsługą wielu jednoczesnych zapytań
#         i długotrwałych operacji (jak czekanie na odpowiedź z LLM), nie blokując przy tym
#         całego serwera.
#     *   **Walidacja danych**: Dzięki integracji z Pydantic, automatycznie sprawdza, czy
#         dane przychodzące do naszego API mają poprawny format.
#     *   **Automatyczna dokumentacja**: FastAPI samo tworzy interaktywną dokumentację dla
#         naszego API, co jest bezcenne podczas testowania i udostępniania go innym.
#
# 2. Anatomia prostej aplikacji API
#
# Budowa API w FastAPI sprowadza się do kilku prostych kroków:
#
#     1.  **Stworzenie instancji aplikacji FastAPI.**
#     2.  **Zdefiniowanie modelu danych wejściowych** za pomocą Pydantic (co będziemy przyjmować?).
#     3.  **Stworzenie "endpointu"** (adresu URL), który będzie nasłuchiwał na zapytania.
#     4.  **Umieszczenie w nim logiki** naszej aplikacji AI.
#     5.  **Zwrócenie wyniku** w formacie JSON.
#
# 3. Praktyczny przykład: API dla prostego łańcucha AI
#
# Stworzymy kompletne, działające API dla prostego łańcucha, który generuje nazwy
# dla firm.
#
# Krok 0: Instalacja
# # W terminalu wykonaj:
# # pip install fastapi "uvicorn[standard]" langchain-openai
import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import Str, która "opakowuje" łańcuch LangChain
# generujący ciekawostki na zadany temat.
#
# Krok 0: Instalacja i struktura projektu
# # W terminalu zainstaluj niezbędne pakiety:
# # pip install fastapi "uvicorn[standard]" langchain-openai
#
# # Stwórz jeden plik o nazwie `main.py`.
import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    # W prawdziwej aplikacji lepiej rzucić wyjątek, ale tutaj dla prostoty używamy print
    exit()

# Krok 1: Definicja modeli danych (Pydantic)
# To definiuje, jakiego formatu JSON oczekujemy na wejściu i co zwrócimy na wyjściu.
class QueryRequest(BaseModel):
    topic: str
    
class QueryResponse(BaseModel):
    fact: str

# Krok 2: Inicjalizacja aplikacji FastAPI i łańcucha LangChain
app = FastAPI(
    title="API do generowania ciekawostek",
    description="Proste API oparte na FastAPI i LangChain."
)

# WAŻNE: Łańcuch tworzymy raz,OutputParser

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    # W prawdziwej aplikacji, obsłużylibyśmy to inaczej, ale tutaj zatrzymujemy program.
    raise ValueError("Nie ustawiono zmiennej środowiskowej OPENAI_API_KEY.")

# Krok 1: Inicjalizacja naszej logiki AI (łańcucha LangChain)
# WAŻNE: Robimy to tylko raz, na poziomie globalnym, przy starcie aplikacji.
# Dzięki temu nie tworzymy nowego łańcucha przy każdym zapytaniu, co oszczędza zasoby.
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
prompt = ChatPromptTemplate.from_template(
    "Zaproponuj jedną, kreatywną nazwę dla firmy, która zajmuje się: {description}"
)
chain = prompt | llm | StrOutputParser()

# Krok 2: Stworzenie instancji aplikacji FastAPI
# Możemy dodać tytuł i opis, które pojawią się w automatycznej dokumentacji.
app = FastAPI(
    title="API do generowania nazw firm",
    description="Proste API oparte o LangChain do brainstormingu nazw.",
)

# Krok 3: Zdefiniowanie modelu danych wejściowych
# Ta klasa mówi FastAPI, że oczekujemy w zapytaniu obiektu JSON
# z jednym polem o nazwie "description", które jest stringiem.
class CompanyNameRequest(BaseModel):
    description: str

# Krok 4: Stworzenie endpointu API
# `@app.post("/generate-name")` to "dekorator", który mówi FastAPI:
# - Nasłuchuj na zapytania typu POST pod adresem /generate-name
# - Funkcja poniżej obsłuży te zapytania.
@app.post("/generate-name")
async def generate_name(request: CompanyNameRequest):
    """
    Przyjmuje opis firmy i zwraca propozycję nazwy.
    """
    # FastAPI automatycznie sprawdzi, czy dane w zapytaniu pasują do modelu
    # `CompanyNameRequest` i przekaże je jako obiekt `request`.
    
    # Wywołujemy naszą logikę AI, przekazując dane z zapytania
    generated_name = chain.invoke({"description": request.description})
    
    # Zwracamy wynik w formacie JSON
    return {"company_name": generated_name}

# Dodatkowy, prosty endpoint do sprawdzania, czy API działa
@app.get("/")
def read_root():
    return {"status": "API działa poprawnie"}

# Krok 5: Uruchomienie serwera
# Aby uruchomić tę aplikację, zapisz ją jako np. `main.py` i w terminalu wpisz:
# uvicorn main:app --reload
#
# - `uvicorn`: To serwer, który uruchamia naszą aplikację.
# - `main`: Nazwa pliku Pythona (main.py).
# - `app`: Nazwa obiektu FastAPI w naszym pliku.
# - `--reload`: Powoduje, że serwer automatycznie restartuje się po każdej zmianie w kodzie.
#
# Po uruchomieniu, otwórz w przeglądarce adres http://127.0.0.1:8000/docs
# Zobaczysz tam interaktywną dokumentację, gdzie możesz przetestować swój endpoint!

#
# 4. Podsumowanie
#
# Właśnie przekształciłeś swój model AI ze skryptu w pełnoprawną, działającą usługę sieciową.
#
# Najważniejsze do zapamiętania:
#
#     1.  **API to "drzwi" do Twojego modelu**: Umożliwia komunikację z innymi aplikacjami.
#     2.  **FastAPI to idealne narzędzie**: Jest szybkie, asynchroniczne i generuje świetną
#         dokumentację.
#     3.  **Proces jest prosty**: Zdefiniuj model danych wejściowych (Pydantic), stwórz
#         endpoint (`@app.post`), wywołaj w nim swoją logikę AI i zwróć wynik.
#     4.  **Inicjalizuj raz**: Kosztowne obiekty (jak modele czy łańcuchy) twórz na poziomie
#         globalnym, a nie wewnątrz funkcji endpointu.
#
# Masz teraz fundamentalną umiejętność, która pozwala na wdrażanie i integrację Twoich
# rozwiązań AI w realnym świecie. W kolejnej lekcji zobaczymy, jak "zapakować" tę
# aplikację w kontener Docker, aby można ją było łatwo uruchomić na dowolnym serwerze.