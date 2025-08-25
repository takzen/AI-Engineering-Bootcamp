# Moduł 7, Punkt 56: Tworzenie workflow dla agentów AI
#
#
#
# Teoria za nami, czas na praktykę! W tej lekcji zbudujemy od podstaw kompletny, choć prosty,
# workflow dla agenta AI. Naszym celem jest odtworzenie popularnej pętli **ReAct (Reason + Act)**,
# ale w sposób, który daje nam pełną kontrolę nad każdym jej elementem.
#
# Zbudujemy agenta, który potrafi odpowiedzieć na pytanie, a jeśli nie zna odpowiedzi,
# samodzielnie zdecyduje o użyciu narzędzia (wyszukiwarki internetowej), aby ją znaleźć.
# Zobaczysz, jak idee Stanu, Węzłów i Krawędzi łączą się w spójną, działającą aplikację.
#
# 1. Przepis na workflow agenta w LangGraph
#
# Nasz proces będzie składał się z kilku jasno zdefiniowanych kroków:
#
#     1. **Zdefiniowanie Stanu**: Określimy, jakie informacje musimy przechowywać w trakcie działania
#        naszego agenta (np. historię wiadomości).
#     2. **Zdefiniowanie Narzędzi**: Damy naszemu agentowi "supermoc" – dostęp do wyszukiwarki.
#     3. **Stworzenie Węzła Agenta ("Mózg")**: Będzie to funkcja, która wywołuje LLM, aby ten
#        podjął decyzję, co robić dalej.
#     4. **Stworzenie Węzła Akcji ("Ręce")**: Będzie to funkcja, która wykonuje narzędzie,
#        jeśli agent tak zdecyduje.
#     5. **Zdefiniowanie Logiki Warunkowej**: Stworzymy funkcję, która sprawdzi decyzję agenta i
#        skieruje przepływ albo do wykonania narzędzia, albo do zakończenia pracy.
#     6. **Zbudowanie i Skompilowanie Grafu**: Połączymy wszystkie te elementy w jeden,
#        działający i cykliczny graf.
#
# 2. Praktyczna implementacja
#
# Krok 0: Instalacja i konfiguracja
# pip install langchain-openai langgraph tavily-python

import os
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

# Ustaw klucze API. Potrzebujesz klucza OpenAI oraz klucza do Tavily Search (darmowy na tavily.com)
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["TAVILY_API_KEY"] = "tvly-..."

if "OPENAI_API_KEY" not in os.environ or "TAVILY_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawione zmienne środowiskowe OPENAI_API_KEY i TAVILY_API_KEY.")
    exit()

# Krok 1: Zdefiniowanie Stanu
# Stan będzie przechowywał listę wiadomości.
# Używamy `Annotated` i `operator.add`, aby LangGraph wiedział,
# że nowe wiadomości mają być dodawane do listy, a nie ją nadpisywać.
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

# Krok 2: Zdefiniowanie Narzędzi
# Tworzymy jedno narzędzie - wyszukiwarkę Tavily.
# To narzędzie zostanie później "udostępnione" naszemu modelowi.
tools = [TavilySearchResults(max_results=1)]
tool_executor = ToolNode(tools) # ToolNode to gotowy węzeł do wykonywania narzędzi

# Krok 3: Stworzenie Węzła Agenta ("Mózg")
# Inicjalizujemy model i "wiążemy" go z narzędziami. Dzięki temu model wie,
# jakich narzędzi może używać i w jakiej formie zwracać decyzję o ich użyciu.
model = ChatOpenAI(model="gpt-4o", temperature=0)
model = model.bind_tools(tools)

# Funkcja węzła, która wywołuje model
def call_model(state: AgentState):
    print("--- WĘZEŁ: Wywołanie modelu (Agent) ---")
    response = model.invoke(state['messages'])
    # Dodajemy odpowiedź modelu do stanu (do listy wiadomości)
    return {"messages": [response]}

# Krok 4: Zdefiniowanie Logiki Warunkowej
# Ta funkcja sprawdza ostatnią wiadomość w stanie.
# Jeśli zawiera ona wywołanie narzędzia, kieruje do węzła akcji.
# W przeciwnym razie, kończy pracę.
def should_continue(state: AgentState):
    print("--- KRAWĘDŹ: Sprawdzanie decyzji ---")
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        print("-> Decyzja: Użyj narzędzia.")
        return "continue"
    else:
        print("-> Decyzja: Zakończ.")
        return "end"

# Krok 5: Zbudowanie Grafu
workflow = StateGraph(AgentState)

# Dodajemy węzły:
# 'agent' to nasz "mózg" (funkcja call_model)
# 'action' to nasze "ręce" (gotowy węzeł ToolNode)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_executor)

# Ustawiamy punkt startowy
workflow.set_entry_point("agent")

# Dodajemy krawędź warunkową. Po wykonaniu węzła 'agent',
# funkcja `should_continue` zdecyduje, czy iść do 'action', czy zakończyć (END).
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

# Po wykonaniu akcji (narzędzia), zawsze wracamy do agenta,
# aby mógł on ocenić wynik i podjąć kolejną decyzję.
workflow.add_edge("action", "agent")

# Krok 6: Skompilowanie i Uruchomienie
app = workflow.compile()

# Możemy teraz uruchomić nasz workflow z początkowym zapytaniem
from langchain_core.messages import HumanMessage

initial_input = {"messages": [HumanMessage(content="Jaka jest teraz pogoda w San Francisco? Podaj w stopniach Celsjusza.")]}
for s in app.stream(initial_input, {"recursion_limit": 5}):
    print(s)
    print("----")

# Możesz też zobaczyć wizualizację grafu w postaci ASCII
# app.get_graph().print_ascii()

#
# 3. Podsumowanie
#
# Właśnie zbudowałeś swój pierwszy, w pełni kontrolowany, cykliczny workflow dla agenta AI!
# Zamiast polegać na gotowym agencie z LangChain, sam zdefiniowałeś każdy krok jego "procesu myślowego".
#
# Najważniejsze do zapamiętania:
#
#     1. **Stan jest kluczowy**: Prawidłowe zdefiniowanie stanu (`AgentState`) pozwala na przekazywanie
#        informacji między węzłami.
#     2. **Węzły wykonują pracę**: Każdy węzeł to funkcja, która wykonuje określoną operację (decyzja LLM,
#        wykonanie narzędzia) i aktualizuje stan.
#     3. **Krawędzie warunkowe sterują przepływem**: To one implementują logikę decyzyjną, tworząc
#        inteligentne i dynamiczne pętle.
#     4. **Kontrola to potęga**: Ten wzorzec daje Ci pełną władzę nad zachowaniem agenta, pozwalając na
#        implementację złożonych strategii, obsługi błędów i współpracy wielu agentów.
#
# Masz teraz fundament, aby budować znacznie bardziej zaawansowane i niezawodne systemy AI.