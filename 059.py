# Moduł 7, Punkt 59: Tworzenie rozgałęzień w LangGraph
#
#
#
# W poprzednich lekcjach wielokrotnie używaliśmy mechanizmu, który jest absolutnym sercem
# i największą siłą LangGraph: **krawędzi warunkowych (conditional edges)**.
# To one pozwalają naszym grafom na "myślenie" i dynamiczne podejmowanie decyzji.
#
# W tej lekcji przyjrzymy się im z bliska. Zrozumiemy, jak działają, jakie są najlepsze
# praktyki ich tworzenia i jak wykorzystać je do budowy jeszcze bardziej inteligentnych
# i elastycznych przepływów.
#
# 1. Czym jest rozgałęzienie (Branching)?
#
# Rozgałęzienie to nic innego jak punkt w naszym grafie, w którym przepływ może pójść
# jedną z kilku możliwych ścieżek. To odpowiednik instrukcji `if-elif-else` w tradycyjnym
# programowaniu, ale przeniesiony na poziom architektury całej aplikacji.
#
# W LangGraph implementujemy to za pomocą metody `add_conditional_edges()`.
#
# 2. Anatomia `add_conditional_edges()`
#
# Spójrzmy na sygnaturę tej metody, aby w pełni zrozumieć jej działanie:
#
# `workflow.add_conditional_edges(start_node, path_function, path_map)`
#
#     * `start_node` (string): Nazwa węzła, **po którym** ma nastąpić decyzja. To jest nasz
#       punkt rozgałęzienia.
#
#     * `path_function` (funkcja): To "mózg" rozgałęzienia. Jest to funkcja, która:
#         - Przyjmuje na wejściu aktualny stan grafu (`state`).
#         - Analizuje ten stan.
#         - **Zwraca stringa**, który jest kluczem do podjęcia decyzji (np. "użyj_narzędzia",
#           "odpowiedz_użytkownikowi", "wystąpił_błąd").
#
#     * `path_map` (słownik): To "mapa drogowa". Jest to słownik, który mapuje klucze
#       zwracane przez `path_function` na nazwy kolejnych węzłów w grafie.
#       - Klucz: String zwrócony przez `path_function`.
#       - Wartość: Nazwa węzła, do którego ma trafić przepływ.
#
# 3. Praktyczny przykład: Wielokierunkowy agent-klasyfikator
#
# Zbudujemy agenta, który na podstawie pytania użytkownika decyduje, czy powinien:
#     A. Odpowiedzieć na pytanie ogólne.
#     B. Użyć narzędzia do wyszukiwania w internecie (dla pytań o aktualne wydarzenia).
#     C. Użyć narzędzia-kalkulatora (dla pytań matematycznych).
#
# To idealny przykład na rozgałęzienie z więcej niż dwiema ścieżkami.
#
# Krok 0: Instalacja i konfiguracja
# (Zakładamy, że pakiety z poprzednich lekcji są już zainstalowane)
import os
import operator
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["TAVILY_API_KEY"] = "tvly-..."
if "OPENAI_API_KEY" not in os.environ or "TAVILY_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawione zmienne środowiskowe.")
    exit()

# Krok 1: Zdefiniowanie Stanu i Narzędzi
class MultiAgentState(TypedDict):
    messages: Annotated[list, operator.add]

# Dwa różne narzędzia: wyszukiwarka i kalkulator (symulowany)
search_tool = TavilySearchResults(max_results=1)
def calculator_tool(expression: str):
    """Prosty kalkulator do wykonywania operacji matematycznych."""
    return eval(expression)

tools = [search_tool, calculator_tool]
tool_executor = ToolNode(tools)

# Krok 2: Zdefiniowanie węzłów
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

def agent_node(state: MultiAgentState):
    print("--- WĘZEŁ: Agent decyzyjny ---")
    response = model.invoke(state['messages'])
    return {"messages": [response]}

# Krok 3: Stworzenie zaawansowanej funkcji routującej (`path_function`)
# To jest serce naszej lekcji.
def router_function(state: MultiAgentState):
    print("--- KRAWĘDŹ WARUNKOWA: Wybór ścieżki ---")
    last_message = state['messages'][-1]

    # Sprawdzamy, czy agent chce użyć jakiegokolwiek narzędzia
    if last_message.tool_calls:
        # Sprawdzamy, jakiego narzędzia chce użyć
        tool_name = last_message.tool_calls[0]['name']
        print(f"-> Agent chce użyć narzędzia: {tool_name}")
        
        if tool_name == 'tavily_search_results_json':
            return "route_to_search"
        elif tool_name == 'calculator_tool':
            return "route_to_calculator"
        else:
            # Ścieżka awaryjna
            return "end_work"
    else:
        # Jeśli nie ma wywołania narzędzia, kończymy
        print("-> Agent chce zakończyć pracę.")
        return "end_work"

# Krok 4: Zbudowanie Grafu
workflow = StateGraph(MultiAgentState)

workflow.add_node("agent", agent_node)
# Używamy jednego, generycznego węzła do wykonywania wszystkich narzędzi
workflow.add_node("action_node", tool_executor)
workflow.set_entry_point("agent")

# Dodajemy naszą zaawansowaną krawędź warunkową
workflow.add_conditional_edges(
    "agent",
    router_function,
    {
        # Nasza "mapa drogowa"
        "route_to_search": "action_node",
        "route_to_calculator": "action_node",
        "end_work": END
    }
)

# Po wykonaniu dowolnej akcji, wracamy do agenta
workflow.add_edge("action_node", "agent")

# Krok 5: Skompilowanie i Testowanie
app = workflow.compile()

# Test 1: Pytanie wymagające wyszukiwarki
print("\n--- TEST 1: Wyszukiwanie w internecie ---")
internet_question = {"messages": [HumanMessage(content="Kto jest reżyserem filmu Oppenheimer?")]}
for s in app.stream(internet_question, {"recursion_limit": 5}):
    print(s)
    print("----")

# Test 2: Pytanie wymagające kalkulatora
print("\n--- TEST 2: Obliczenia matematyczne ---")
math_question = {"messages": [HumanMessage(content="Ile to jest 123 * 4?")]}
for s in app.stream(math_question, {"recursion_limit": 5}):
    print(s)
    print("----")
    
# Test 3: Pytanie ogólne
print("\n--- TEST 3: Pytanie ogólne ---")
general_question = {"messages": [HumanMessage(content="Napisz krótki wiersz o wiośnie.")]}
for s in app.stream(general_question, {"recursion_limit": 5}):
    print(s)
    print("----")

#
# 4. Podsumowanie
#
# Opanowanie `add_conditional_edges` to umiejętność, która pozwala na tworzenie prawdziwie
# dynamicznych i inteligentnych systemów. Zamiast prostych pętli, możemy budować złożone
# drzewa decyzyjne i maszyny stanowe.
#
# Najważniejsze do zapamiętania:
#
#     1. **Rozgałęzienie = `add_conditional_edges`**: To podstawowy mechanizm decyzyjny w LangGraph.
#     2. **Funkcja routująca to "mózg" decyzji**: Ta funkcja analizuje stan i zwraca stringa,
#        który jest kluczem do wyboru następnej ścieżki.
#     3. **Mapa drogowa (`path_map`) to "nogi"**: Słownik ten tłumaczy klucz z funkcji routującej
#        na konkretny następny węzeł do wykonania.
#     4. **Możliwości są nieograniczone**: Możesz tworzyć dowolnie złożone rozgałęzienia, kierując
#        przepływ do różnych pod-grafów, implementując logikę fallbacków, czy prosząc o pomoc
#        człowieka w pętli (human-in-the-loop).
#
# Jesteś teraz w stanie projektować przepływy, które nie tylko wykonują zadania, ale
# w inteligentny sposób zarządzają własnym procesem ich wykonywania.