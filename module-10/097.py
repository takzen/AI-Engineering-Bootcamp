# Moduł 10, Punkt 97: Tworzenie skalowalnych API
#
#
#
# Potrafimy już stworzyć API za pomocą FastAPI i "zapakować" je do przenośnego kontenera
# Docker. To ogromny krok naprzód. Ale co się stanie, gdy nasza aplikacja stanie się
# popularna i jedno "pudełko" (jeden kontener) przestanie wystarczać do obsługi
# całego ruchu?
#
# W tej lekcji przejdziemy od myślenia o pojedynczym kontenerze do myślenia o **całej
# flocie kontenerów**, które współpracują ze sobą, aby obsłużyć dowolnie duże
# obciążenie. Nauczymy się podstawowych zasad projektowania API, które są z natury
# **skalowalne**.
#
# 1. Problem: Monolit vs. Mikroserwisy
#
# Wyobraź sobie, że cała nasza aplikacja – przyjmowanie zapytań, logika AI, łączenie
# z bazą danych – jest zamknięta w jednym, dużym kontenerze. To tzw. **architektura
# monolityczna**. Jest prosta na początku, ale ma poważne wady, gdy chcemy ją skalować:
#
#     *   **Trudność w skalowaniu**: Jeśli tylko jedna część aplikacji (np. generowanie
#         odpowiedzi przez LLM) jest "wąskim gardłem", musimy skalować (tworzyć kopie)
#         całego, wielkiego monolitu. To nieefektywne.
#     *   **Niska odporność na błędy**: Błąd w jednej, mało istotnej części aplikacji
#         może spowodować awarię całego serwisu.
#
# Rozwiązaniem jest podejście oparte na **mikroserwisach**: dzielimy naszą dużą aplikację
# na mniejsze, niezależne usługi, które komunikują się ze sobą przez API. W świecie
# aplikacji AI, minimalny, ale bardzo potężny podział, to oddzielenie API od "workerów".
#
# 2. Kluczowa zasada skalowalności: Bezstanowość (Statelessness)
#
# To najważniejsza koncepcja w projektowaniu skalowalnych API.
#
# **API bezstanowe** to takie, które **nie przechowuje żadnych informacji o poprzednich
# zapytaniach**. Każde zapytanie jest traktowane jako zupełnie nowe i zawiera wszystkie
# informacje potrzebne do jego przetworzenia.
#
# *   **Zły projekt (stanowy)**:
#     1.  `POST /session`: Użytkownik tworzy sesję i dostaje `session_id`.
#     2.  `POST /session/{id}/message`: Użytkownik wysyła wiadomość w ramach sesji.
#         Serwer musi gdzieś w swojej pamięci przechowywać historię tej sesji.
#     **Problem**: Jeśli ten konkretny serwer (kontener) ulegnie awarii, cała historia
#     rozmowy przepada. Co więcej, każde kolejne zapytanie od tego użytkownika musi
#     trafić do **dokładnie tego samego serwera**, co uniemożliwia proste skalowanie
#     za pomocą load balancera.
#
# *   **Dobry projekt (bezstanowy)**:
#     1.  `POST /chat`: Użytkownik wysyła zapytanie, które w ciele żądania zawiera nie
#         tylko nową wiadomość, ale także **całą dotychczasową historię rozmowy**
#         oraz `session_id`.
#     **Zaleta**: Każde zapytanie jest kompletne. Load balancer może je wysłać do **dowolnego,
#     dostępnego kontenera**, ponieważ żaden z nich nie musi "pamiętać" niczego
#     o tej sesji. Stan (historia rozmowy) jest przechowywany po stronie klienta
#     (np. w przeglądarce) lub w zewnętrznej, współdzielonej bazie danych (np. Redis).
#
# 3. Architektura skalowalnego API: Load Balancer + Flota Kontenerów
#
# W praktyce, skalowalne wdrożenie naszej aplikacji wygląda następująco:
#
# **[Użytkownik] -> [Load Balancer] -> [Kontener 1 (API)] | [Kontener 2 (API)] | [Kontener 3 (API)] ...**
#
#     *   **Kontenery API**: To są identyczne kopie (repliki) naszego obrazu Dockera
#         z aplikacją FastAPI. Każda z nich jest bezstanowa.
#
#     *   **Load Balancer (np. Nginx, Traefik, lub usługa chmurowa jak AWS ALB)**:
#         To "kontroler ruchu". Jego zadaniem jest:
#         1.  Przyjmowanie wszystkich przychodzących zapytań.
#         2.  Rozdzielanie ich równomiernie pomiędzy wszystkie dostępne kontenery.
#         3.  Monitorowanie "zdrowia" kontenerów – jeśli jeden z nich ulegnie awarii,
#             load balancer przestaje do niego wysyłać ruch.
#
# **Jak to skalujemy?** Prosto! Jeśli ruch na naszej stronie rośnie, po prostu
# **uruchamiamy więcej identycznych kontenerów** (`docker run ...`) i dodajemy je
# do puli w load balancerze. Jeśli ruch maleje, wyłączamy zbędne kontenery.
#
# 4. Praktyczny przykład: Bezstanowy endpoint w FastAPI
#
# Zmodyfikujmy naszą aplikację, aby jej endpoint był w pełni bezstanowy, gotowy
# do skalowania.
#
# Krok 0: Przygotowanie aplikacji
# # (Używamy tej samej bazy co w poprzednich lekcjach)
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Nie ustawiono zmiennej środowiskowej OPENAI_API_KEY.")

app = FastAPI(title="Skalowalne API Chatbota")

# Logika AI - inicjalizowana raz
llm = ChatOpenAI(model="gpt-3.5-turbo")
prompt = ChatPromptTemplate.from_messages([
    ("system", "Jesteś pomocnym asystentem. Odpowiedz na ostatnie pytanie, biorąc pod uwagę historię rozmowy."),
    # W praktyce tu byłby `MessagesPlaceholder`, ale dla prostoty użyjemy formatowania
    ("user", "Historia: {chat_history}\n\nPytanie: {question}")
])
chain = prompt | llm | StrOutputParser()

# Krok 1: Definicja bezstanowego modelu danych wejściowych
# Oczekujemy, że klient przy każdym zapytaniu prześle nam całą historię.
class StatelessChatRequest(BaseModel):
    question: str
    # Lista słowników reprezentujących poprzednie wiadomości
    chat_history: List[Dict[str, str]] = []

# Krok 2: Stworzenie bezstanowego endpointu
@app.post("/stateless-chat")
async def stateless_chat(request: StatelessChatRequest):
    """
    Ten endpoint jest w 100% bezstanowy. Nie przechowuje żadnych
    informacji o sesji na serwerze.
    """
    # Formatujemy historię do prostego stringa dla naszego łańcucha
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.chat_history])
    
    # Wywołujemy łańcuch, przekazując zarówno nowe pytanie, jak i pełną historię
    response = chain.invoke({
        "question": request.question,
        "chat_history": history_str
    })
    
    # Zwracamy tylko nową odpowiedź. To klient jest odpowiedzialny
    # za dodanie jej do swojej lokalnej historii i przesłanie jej
    # z powrotem przy kolejnym zapytaniu.
    return {"answer": response}

#
# 5. Podsumowanie
#
# Projektowanie z myślą o skalowalności od samego początku to klucz do budowy
# systemów, które są w stanie obsłużyć realny ruch.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Dąż do bezstanowości (Statelessness)**: Twoje endpointy API nie powinny
#         przechowywać żadnego stanu związanego z sesją użytkownika. Cały potrzebny
#         kontekst powinien być przesyłany w każdym zapytaniu.
#     2.  **Stan przechowuj na zewnątrz**: Jeśli musisz przechowywać stan (np. historię
#         rozmowy), rób to w zewnętrznej, współdzielonej bazie danych (np. Redis,
#         PostgreSQL), a nie w pamięci serwera API.
#     3.  **Skaluj horyzontalnie**: Dzięki bezstanowości, możesz po prostu dodawać
#         kolejne, identyczne kopie Twojego kontenera, aby zwiększyć przepustowość.
#     4.  **Używaj Load Balancera**: To on jest odpowiedzialny za rozdzielanie ruchu
#         pomiędzy Twoje skonteneryzowane instancje aplikacji.
#
# Mając tę wiedzę, jesteś gotów projektować i wdrażać nie tylko inteligentne, ale
# także potężne i odporne na duże obciążenie aplikacje AI.