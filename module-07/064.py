# Moduł 7, Punkt 64: Integracja LangGraph z innymi technologiami
#
#
#
# Gratulacje! Dotarłeś do ostatniej lekcji tego kursu. Opanowałeś sztukę budowania niezwykle
# potężnych, dynamicznych i inteligentnych systemów za pomocą LangGraph. Twój graf działa
# perfekcyjnie... ale na razie tylko jako skrypt Pythona uruchamiany w terminalu.
#
# Jak udostępnić tę niesamowitą moc światu? Jak pozwolić użytkownikom na interakcję
# z Twoim wieloagentowym systemem przez stronę internetową? Jak zintegrować go z innymi
# mikroserwisami w Twojej firmie?
#
# W tej lekcji połączymy wszystko, czego się nauczyliśmy, i pokażemy, jak "opakować"
# nasz graf LangGraph w profesjonalne, skalowalne API za pomocą frameworka FastAPI.
#
# 1. Problem: Od skryptu do usługi
#
# Twój skompilowany graf (`app = workflow.compile()`) to potężny, ale zamknięty obiekt.
# Aby stał się użyteczny, musi zostać wystawiony jako **usługa (service)**, która:
#
#     * Nasłuchuje na zapytania przychodzące przez sieć (HTTP).
#     * Przyjmuje dane wejściowe w standardowym formacie (np. JSON).
#     * Uruchamia graf z tymi danymi.
#     * Zwraca wynik w tym samym, standardowym formacie.
#
# To jest dokładnie rola, do której stworzono frameworki webowe takie jak FastAPI.
#
# 2. Architektura integracji: LangGraph + FastAPI
#
# Proces integracji jest bardzo podobny do tego, który poznaliśmy przy LangFlow, ale
# ze względu na naturę LangGraph, musimy zwrócić uwagę na kilka dodatkowych aspektów,
# zwłaszcza na obsługę **strumieniowania (streaming)** i **współbieżności**.
#
# Nasz plan działania:
#     1. Zorganizuj kod w logiczną strukturę (oddzielenie logiki grafu od logiki API).
#     2. Stwórz aplikację FastAPI.
#     3. Zdefiniuj modele danych wejściowych i wyjściowych (Pydantic).
#     4. Stwórz endpoint API, który będzie uruchamiał graf.
#     5. (Zaawansowane) Zaimplementuj strumieniowanie wyników za pomocą `StreamingResponse`,
#        aby użytkownik widział postęp w czasie rzeczywistym.
#
# 3. Praktyczny przykład: Serwowanie agenta jako API ze streamingiem
#
# Opakujemy prosty graf agenta w API. Najciekawszym elementem będzie endpoint, który
# strumieniuje pośrednie kroki działania agenta, tak jak widzieliśmy to w konsoli.
#
# Krok 0: Struktura projektu i instalacja
# /langgraph_api
# |-- main.py             # Aplikacja FastAPI
# |-- graph_builder.py    # Logika budowania grafu LangGraph
#
# pip install fastapi uvicorn "langchain[llms]" langchain-openai langgraph sse-starlette

# Krok 1: Logika budowy grafu w `graph_builder.py`
# (To uproszczony graf dla demonstracji, ale wzorzec jest uniwersalny)
# --- to jest zawartość pliku graph_builder.py ---
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage

class StreamingState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def get_graph_app():
    """
    Buduje i kompiluje graf LangGraph.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def simple_agent_node(state: StreamingState):
        # Prosty agent, który tylko odpowiada
        return {"messages": [llm.invoke(state['messages'])]}

    workflow = StateGraph(StreamingState)
    workflow.add_node("agent", simple_agent_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    
    return workflow.compile()

# --- koniec pliku graph_builder.py ---


# Krok 2: Aplikacja FastAPI w `main.py`
# --- to jest zawartość pliku main.py ---
import json
from fastapi import FastAPI
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from langchain_core.messages import HumanMessage
from graph_builder import get_graph_app # Importujemy naszą fabrykę grafów

app = FastAPI(title="API dla Aplikacji LangGraph")

# Globalna instancja grafu, tworzona raz przy starcie
langgraph_app = get_graph_app()

class ChatRequest(BaseModel):
    input: str
    session_id: str # Kluczowe do zarządzania sesjami

@app.post("/stream")
async def stream_chat(request: ChatRequest):
    """
    Ten endpoint przyjmuje zapytanie i strumieniuje kroki działania grafu
    w czasie rzeczywistym za pomocą Server-Sent Events (SSE).
    """
    # Definiujemy początkowy stan dla grafu
    initial_state = {"messages": [HumanMessage(content=request.input)]}

    async def event_stream():
        # Używamy asynchronicznego streamingu `astream_events`
        # `version="v1"` to standardowy format zdarzeń
        async for event in langgraph_app.astream_events(initial_state, version="v1"):
            # Wysyłamy każde zdarzenie (wejście/wyjście z węzła) jako osobny pakiet danych
            yield json.dumps(event)

    return EventSourceResponse(event_stream())

# --- koniec pliku main.py ---


# Krok 3: Uruchomienie i testowanie
# 1. W terminalu uruchom serwer:
#    uvicorn main:app --reload
#
# 2. Testowanie API ze streamingiem jest trudniejsze w przeglądarce.
#    Użyjemy prostego klienta w Pythonie (uruchom go w osobnym terminalu):

# --- plik test_client.py ---
import requests
import json

API_URL = "http://127.0.0.1:8000/stream"
payload = {"input": "Opowiedz mi o architekturze Rzymu.", "session_id": "user123"}

with requests.post(API_URL, json=payload, stream=True) as response:
    print(f"Status: {response.status_code}\n")
    for line in response.iter_lines():
        if line:
            # Każda linia to osobne zdarzenie z serwera
            event_data = line.decode('utf-8')
            print(event_data)
            print("-" * 20)
# --- koniec pliku test_client.py ---

# Uruchamiając klienta, zobaczysz w konsoli strumień zdarzeń w formacie JSON,
# pokazujący w czasie rzeczywistym, jak Twój graf jest wykonywany na serwerze!

#
# 4. Podsumowanie – Pełna Kontrola od Prototypu do Produkcji
#
# Gratulacje! Przeszedłeś pełną drogę od podstaw Pythona, przez budowę prostych łańcuchów
# w LangChain, wizualne prototypowanie w LangFlow, aż po orkiestrację złożonych,
# wieloagentowych systemów w LangGraph i ich wdrożenie jako profesjonalne, strumieniujące API.
#
# Najważniejsze do zapamiętania:
#
#     1. **LangGraph i FastAPI to idealna para**: Elastyczność i moc LangGraph w połączeniu z
#        wydajnością i asynchronicznością FastAPI pozwalają budować systemy AI najwyższej klasy.
#     2. **Streaming jest kluczowy dla UX**: W przypadku długotrwałych operacji (a takie są
#        przepływy w LangGraph), strumieniowanie wyników jest niezbędne, aby utrzymać zaangażowanie
#        użytkownika.
#     3. **Architektura ma znaczenie**: Oddzielenie logiki budowy grafu od logiki serwera API
#        to czysta i skalowalna praktyka.
#     4. **Masz pełen zestaw narzędzi**: Znasz teraz cały stos technologiczny, który pozwala Ci
#        przekształcić dowolny pomysł na aplikację AI w działający, niezawodny i skalowalny produkt.
#
# To koniec tego kursu, ale dopiero początek Twojej przygody jako architekta
# i inżyniera nowoczesnych systemów sztucznej inteligencji. Powodzenia!