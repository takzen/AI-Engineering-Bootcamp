# Moduł 7, Punkt 57: Obsługa błędów i fallbacki w LangGraph
#
#
#
# Stworzyliśmy działający workflow agenta. Ale co się stanie, gdy coś pójdzie nie tak?
# Co, jeśli wybrane przez agenta narzędzie zwróci błąd? Albo API, z którego korzysta, będzie niedostępne?
#
# W tradycyjnych systemach LangChain, błąd w narzędziu często powodował zatrzymanie całej pętli agenta.
# LangGraph daje nam bezprecedensową kontrolę, aby elegancko obsługiwać takie sytuacje, tworzyć
# ścieżki zapasowe (fallbacki) i budować systemy, które są znacznie bardziej **odporne na awarie (resilient)**.
#
# 1. Dlaczego obsługa błędów jest tak ważna w systemach AI?
#
#     * **Niezawodność narzędzi**: Narzędzia komunikują się ze światem zewnętrznym (API, bazy danych),
#       który może być niestabilny.
#     * **Błędy w wywołaniach LLM**: Czasem API LLM może zwrócić błąd (np. z powodu przeciążenia)
#       lub wygenerować nieprawidłowo sformatowaną odpowiedź (np. zły JSON).
#     * **"Głupie" decyzje agenta**: Agent może próbować użyć narzędzia w nieprawidłowy sposób,
#       przekazując mu złe argumenty.
#
# Zignorowanie tych problemów prowadzi do frustrujących i zawodnych aplikacji. LangGraph pozwala nam
# przechwycić błąd, poinformować o nim agenta i pozwolić mu podjąć nową, świadomą decyzję.
#
# 2. Architektura odpornego na błędy workflow
#
# Kluczem jest modyfikacja naszego istniejącego grafu. Zamiast prostej pętli "agent -> akcja -> agent",
# wprowadzimy logikę, która potrafi obsłużyć błąd w węźle akcji.
#
#     1. **Przechwytywanie błędu**: Zmodyfikujemy nasz węzeł akcji tak, aby używał bloku `try...except`.
#        Jeśli wykonanie narzędzia się powiedzie, zwracamy wynik. Jeśli wystąpi błąd, zwracamy
#        informację o błędzie.
#     2. **Nowy stan dla błędów**: Rozszerzymy nasz `AgentState`, dodając pole, które będzie
#        przechowywać informację o błędzie.
#     3. **Nowa krawędź warunkowa**: Po wykonaniu akcji, nowa krawędź sprawdzi, czy operacja się
#        powiodła. Jeśli tak, wracamy do agenta. Jeśli nie, możemy skierować przepływ do
#        specjalnego węzła obsługi błędów lub po prostu wrócić do agenta z informacją o porażce.
#
# 3. Praktyczny przykład: Agent, który uczy się na błędach
#
# Zmodyfikujemy agenta z poprzedniej lekcji. Stworzymy "zepsute" narzędzie, które celowo będzie
# zwracać błąd, i zobaczymy, jak nasz graf sobie z tym poradzi.
#
# Krok 0: Instalacja i konfiguracja
# (Zakładamy, że pakiety z poprzedniej lekcji są już zainstalowane)
import os
import operator
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Stworzenie "zepsutego" narzędzia
# Narzędzie to będzie zawsze zwracać błąd, symulując awarię zewnętrznego API.
def broken_tool(query: str):
    """To jest zepsute narzędzie, które zawsze zawodzi."""
    raise ValueError(f"Niestety, narzędzie zepsuło się podczas przetwarzania zapytania: {query}")

# Krok 2: Rozszerzenie Stanu o obsługę błędów
class ResilientAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    # Dodajemy nowe pole, które będzie przechowywać informację o błędzie
    error: str | None

# Krok 3: Zmodyfikowanie węzła akcji
# Zamiast używać gotowego `ToolNode`, stworzymy własną funkcję,
# która opakowuje wykonanie narzędzia w blok try...except.
def execute_tools_with_error_handling(state: ResilientAgentState):
    print("--- WĘZEŁ: Próba wykonania narzędzia ---")
    # Pobieramy ostatnią wiadomość, która powinna zawierać wywołanie narzędzia
    last_message = state['messages'][-1]
    
    # Symulujemy wykonawcę narzędzi
    tool_executor = ToolNode([broken_tool])

    try:
        # Próbujemy wykonać narzędzie
        response = tool_executor.invoke(state)
        print("-> Sukces: Narzędzie wykonane poprawnie.")
        # Jeśli się udało, zwracamy wynik i czyścimy flagę błędu
        return {"messages": response, "error": None}
    except Exception as e:
        print(f"-> BŁĄD: Narzędzie zwróciło wyjątek: {e}")
        # Jeśli wystąpił błąd, tworzymy wiadomość o błędzie
        # i ustawiamy flagę błędu w stanie.
        error_message = ToolMessage(content=f"Błąd wykonania narzędzia: {e}", tool_call_id=last_message.tool_calls[0]['id'])
        return {"messages": [error_message], "error": "tool_error"}

# Krok 4: Zbudowanie nowego grafu z logiką fallback
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools([broken_tool])

def call_model(state: ResilientAgentState):
    print("--- WĘZEŁ: Wywołanie modelu (Agent) ---")
    response = model.invoke(state['messages'])
    return {"messages": [response]}

def should_continue(state: ResilientAgentState):
    print("--- KRAWĘDŹ: Sprawdzanie decyzji ---")
    if state['messages'][-1].tool_calls:
        return "continue_to_action"
    else:
        return "end_work"

# Budujemy graf
workflow = StateGraph(ResilientAgentState)
workflow.add_node("agent", call_model)
# Używamy naszego nowego, odpornego na błędy węzła akcji
workflow.add_node("action", execute_tools_with_error_handling)
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue_to_action": "action", "end_work": END}
)

# Po wykonaniu akcji, zawsze wracamy do agenta.
# Teraz agent otrzyma informację albo o sukcesie, albo o porażce narzędzia.
workflow.add_edge("action", "agent")

app = workflow.compile()

# Krok 5: Uruchomienie i obserwacja
from langchain_core.messages import HumanMessage

# Uruchamiamy workflow. Oczekujemy, że agent najpierw spróbuje użyć narzędzia,
# otrzyma informację o błędzie, a następnie w kolejnym kroku odpowie użytkownikowi,
# uwzględniając ten błąd.
initial_input = {"messages": [HumanMessage(content="Użyj swojego zepsutego narzędzia.")]}
for s in app.stream(initial_input, {"recursion_limit": 5}):
    print(s)
    print("----")

#
# 4. Podsumowanie
#
# Dzięki elastyczności LangGraph, przekształciliśmy naszego prostego agenta w odporny na błędy system.
# Agent nie tylko napotyka na błąd, ale jest o nim informowany i może na niego zareagować w kolejnym cyklu.
#
# Najważniejsze do zapamiętania:
#
#     1. **Przewiduj problemy**: Zawsze zakładaj, że zewnętrzne narzędzia i API mogą zawieść.
#     2. **Opakowuj w `try...except`**: Twórz własne węzły akcji, które potrafią przechwycić wyjątki i
#        zamienić je w użyteczną informację dla agenta.
#     3. **Wykorzystaj stan**: Użyj stanu grafu, aby przekazywać informacje o błędach. Dzięki temu
#        agent w kolejnym kroku wie, co poszło nie tak.
#     4. **Projektuj ścieżki zapasowe (fallbacki)**: Możesz rozbudować graf o kolejne węzły warunkowe,
#        które po wykryciu błędu spróbują użyć innego narzędzia, poproszą użytkownika o pomoc,
#        lub po prostu poinformują o problemie.
#
# Budowanie odpornych na błędy workflow to cecha charakterystyczna profesjonalnych, produkcyjnych systemów AI.
# LangGraph daje Ci wszystkie narzędzia, aby osiągnąć ten poziom niezawodności.