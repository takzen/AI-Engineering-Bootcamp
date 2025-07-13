      
# Moduł 6, Punkt 52: Integracja LangFlow z FastAPI
#
#
#
# W poprzedniej lekcji nauczyliśmy się eksportować nasze wizualne przepływy z LangFlow do kodu Pythona.
# To był kluczowy krok, który uwolnił naszą aplikację z interfejsu graficznego.
#
# Teraz czas na ostateczny etap: zamianę tego wyeksportowanego kodu w profesjonalne, skalowalne i
# niezawodne API, z którego mogą korzystać inne aplikacje. Narzędziem, które idealnie się do tego nadaje,
# jest FastAPI.
#
# 1. Dlaczego FastAPI?
#
# FastAPI to nowoczesny, wysokowydajny framework webowy w Pythonie. Jest to preferowany wybór do budowy API
# dla aplikacji opartych o LLM z kilku powodów:
#
#     * **Asynchroniczność**: FastAPI jest zbudowane na asynchroniczności, co pozwala na obsługę wielu
#       jednoczesnych zapytań bez blokowania. Jest to idealne dla operacji I/O-bound, takich jak
#       oczekiwanie na odpowiedź z API OpenAI.
#     * **Wydajność**: Jest jednym z najszybszych frameworków Pythona.
#     * **Łatwość użycia**: Ma prostą i intuicyjną składnię.
#     * **Automatyczna dokumentacja**: FastAPI automatycznie generuje interaktywną dokumentację API (Swagger UI),
#       co jest absolutnie bezcenne podczas testowania i udostępniania API innym deweloperom.
#
# 2. Od wizualnego przepływu do działającego API – proces
#
# Nasz plan działania jest prosty i powtarzalny:
#
#     1. **Zbuduj i sfinalizuj** swój przepływ w LangFlow.
#     2. **Wyeksportuj** go do pliku Pythona (np. `exported_flow.py`).
#     3. **Stwórz nowy projekt** z prostą strukturą plików.
#     4. **Zainstaluj** niezbędne zależności: `fastapi`, `uvicorn` i biblioteki używane w przepływie.
#     5. **Stwórz główny plik aplikacji** (`main.py`), który zaimportuje logikę z `exported_flow.py`.
#     6. **Zdefiniuj endpoint API**, który będzie przyjmował zapytanie od użytkownika i wywoływał łańcuch.
#     7. **Uruchom i przetestuj** swoją nową aplikację API.
#
# 3. Praktyczny przykład: Serwowanie chatbota jako API
#
# Załóżmy, że w LangFlow zbudowaliśmy i przetestowaliśmy prostego chatbota z pamięcią.
#
# **Krok 1: Eksport przepływu**
# W LangFlow, wyeksportuj swój przepływ jako plik Pythona. Zapisz go pod nazwą `exported_flow.py`.
#
# **Krok 2: Struktura projektu**
# Stwórz folder dla swojego projektu i umieść w nim pliki w następujący sposób:
# /moj_chatbot_api
# |-- main.py         # Nasza aplikacja FastAPI
# |-- exported_flow.py # Kod wyeksportowany z LangFlow
#
# **Krok 3: Instalacja zależności**
# Otwórz terminal w folderze projektu i zainstaluj potrzebne pakiety:
# pip install fastapi uvicorn "langchain[llms]" langchain-openai
#
# **Krok 4: Zawartość `exported_flow.py` (Uproszczony przykład)**
# Wyeksportowany kod może być długi. Najważniejsza jest w nim funkcja, która buduje i zwraca łańcuch.
# Dla uproszczenia, załóżmy, że wygląda ona tak:

# Ten plik symuluje kod wyeksportowany z LangFlow
# W rzeczywistości będzie on bardziej złożony, ale kluczowa jest funkcja budująca.
# --- to jest zawartość pliku exported_flow.py ---
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

def get_chain():
    """
    Ta funkcja buduje i zwraca gotowy do użycia łańcuch.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    prompt = ChatPromptTemplate.from_template("Napisz krótką anegdotę na temat: {temat}")
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain

# --- koniec pliku exported_flow.py ---


# **Krok 5: Tworzenie aplikacji FastAPI w `main.py`**
# To jest serce naszej nowej usługi.

# --- to jest zawartość pliku main.py ---
from fastapi import FastAPI
from pydantic import BaseModel
from exported_flow import get_chain  # Importujemy naszą logikę!

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="API dla Chatbota LangChain",
    description="Proste API do interakcji z łańcuchem stworzonym w LangFlow."
)

# Definicja modelu danych wejściowych za pomocą Pydantic
# To zapewnia walidację i świetną dokumentację
class ChatRequest(BaseModel):
    temat: str
    user_id: str | None = None  # Opcjonalne ID użytkownika do przyszłej obsługi sesji

# Tworzymy instancję łańcucha TYLKO RAZ, przy starcie aplikacji.
# To kluczowa optymalizacja, aby nie tworzyć obiektu przy każdym zapytaniu!
langchain_chain = get_chain()

@app.post("/chat", summary="Wywołuje łańcuch chatbota")
async def chat(request: ChatRequest):
    """
    Przyjmuje zapytanie od użytkownika i zwraca odpowiedź wygenerowaną przez łańcuch.
    """
    print(f"Otrzymano zapytanie na temat: {request.temat}")
    
    # Wywołujemy nasz łańcuch z danymi z zapytania
    response = langchain_chain.invoke({"temat": request.temat})
    
    return {"response": response['text']}

# --- koniec pliku main.py ---


# **Krok 6: Uruchomienie i testowanie API**
# 1. W terminalu, w głównym folderze projektu, uruchom serwer:
#    uvicorn main:app --reload
#
#    --reload sprawia, że serwer automatycznie restartuje się po każdej zmianie w kodzie.
#
# 2. Otwórz przeglądarkę i wejdź na adres: http://127.0.0.1:8000/docs
#
# 3. Zobaczysz piękną, interaktywną dokumentację swojego API. Możesz tam:
#    - Rozwinąć endpoint `/chat`.
#    - Kliknąć "Try it out".
#    - Wpisać w pole `temat` np. "programowanie w Pythonie".
#    - Kliknąć "Execute".
#
# 4. Poniżej zobaczysz pełne zapytanie `cURL`, adres URL oraz odpowiedź serwera z wygenerowaną anegdotą!
#
#
# 4. Podsumowanie
#
# Właśnie przeszedłeś pełną drogę od wizualnego prototypu do działającej, profesjonalnej usługi API.
#
# Najważniejsze do zapamiętania:
#
#     1. **LangFlow do prototypowania, FastAPI do produkcji**: To idealne połączenie szybkości i niezawodności.
#     2. **Eksport to most**: Funkcja eksportu kodu z LangFlow jest kluczowym mostem łączącym te dwa światy.
#     3. **Oddzielaj logikę**: Logika LangChain (w `exported_flow.py`) jest oddzielona od logiki serwera API (w `main.py`).
#     4. **Inicjalizuj raz**: Twórz instancję łańcucha na poziomie globalnym, a nie wewnątrz funkcji endpointu, aby oszczędzać zasoby.
#     5. **Korzystaj z auto-dokumentacji**: Interfejs pod `/docs` jest Twoim najlepszym przyjacielem podczas testowania i rozwoju.
#
# Masz teraz solidne podstawy do budowania i wdrażania dowolnej aplikacji AI, przekształcając swoje wizualne pomysły w realne, działające produkty.

    