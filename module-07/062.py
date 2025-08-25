# Moduł 7, Punkt 62: Debugowanie i testowanie workflow
#
#
#
# Zbudowaliśmy już niezwykle potężne, ale i skomplikowane, cykliczne grafy. A jak wiadomo,
# im większa złożoność, tym większe prawdopodobieństwo, że coś pójdzie nie tak.
# Debugowanie przepływu w LangGraph, gdzie stan zmienia się w pętli, a decyzje
# są podejmowane dynamicznie, wymaga specyficznych narzędzi i strategii.
#
# W tej ostatniej lekcji modułu nauczymy się, jak skutecznie "zaglądać pod maskę"
# naszych grafów, aby zrozumieć ich działanie, zdiagnozować problemy i zapewnić
# ich niezawodność.
#
# 1. Wyzwania w debugowaniu grafów
#
# W przeciwieństwie do prostych, liniowych łańcuchów, problemy w LangGraph mogą być bardziej subtelne:
#
#     * **Nieskończone pętle**: Agent może wpaść w cykl, w którym ciągle próbuje użyć tego samego,
#       wadliwego narzędzia, nigdy nie dochodząc do rozwiązania.
#     * **Błędny routing**: Krawędź warunkowa może kierować przepływ do złego węzła z powodu
#       nieprecyzyjnej logiki w funkcji routującej.
#     * **Nieprawidłowe aktualizacje stanu**: Jeden z węzłów może niepoprawnie modyfikować stan,
#       co "zatruwa" dane dla wszystkich kolejnych węzłów w grafie.
#     * **Zgubiony kontekst**: W złożonym przepływie łatwo zapomnieć o przekazaniu kluczowej
#       informacji w stanie, co powoduje, że kolejny węzeł działa "na ślepo".
#
# 2. Narzędzia i techniki debugowania w LangGraph
#
# Na szczęście mamy do dyspozycji potężny arsenał, aby radzić sobie z tymi wyzwaniami.
#
#     **2.1. `stream()` i `invoke()` – Podstawowy wgląd**
#     Sposób, w jaki uruchamiamy graf, jest naszą pierwszą linią debugowania.
#     *   **`app.invoke()`**: Uruchamia cały graf i zwraca tylko ostateczny stan. Dobre do
#         szybkiego sprawdzenia finalnego wyniku.
#     *   **`app.stream()`**: **Twoje podstawowe narzędzie do debugowania**. Uruchamia graf krok
#         po kroku, zwracając (yield) stan po wykonaniu **każdego węzła**. Pozwala to na
#         obserwowanie, jak stan ewoluuje w czasie. W naszych poprzednich przykładach
#         używaliśmy pętli `for s in app.stream(...)`, aby drukować te pośrednie stany.
#
#     **2.2. Wizualizacja grafu**
#     Czasem najlepszym sposobem na zrozumienie problemu jest zobaczenie całej architektury.
#     LangGraph pozwala na wygenerowanie wizualizacji grafu w kilku formatach.
#
#     **2.3. Konfiguracja `recursion_limit`**
#     Aby zapobiec nieskończonym pętlom, każdy graf kompilowany jest z domyślnym limitem
#     rekurencji (zwykle 25 kroków). Jeśli graf przekroczy ten limit, zwróci błąd.
#
#     **2.4. LangSmith – Profesjonalne śledzenie (Tracing)**
#     To bez wątpienia **najpotężniejsze narzędzie do debugowania LangGraph**.
#     Po skonfigurowaniu środowiska do pracy z LangSmith (poprzez zmienne środowiskowe),
#     każde uruchomienie grafu jest automatycznie rejestrowane jako jeden, nadrzędny "ślad" (trace).
#     W panelu LangSmith można zobaczyć wizualizację ścieżki, jaką podążył przepływ, oraz
#     dokładny stan wejściowy i wyjściowy dla każdego wykonanego węzła.
#
# 3. Praktyczny przykład: Debugowanie z `stream` i wizualizacją
#
# Poniższy kod demonstruje, jak używać `stream` do inspekcji stanu oraz jak wizualizować graf.

from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage

# Prosty graf do celów demonstracyjnych
class DebugState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    counter: int

def node_a(state: DebugState):
    print("-> Wykonuję węzeł A")
    return {"counter": state['counter'] + 1, "messages": [SystemMessage(content="Węzeł A został wykonany.")]}

def node_b(state: DebugState):
    print("-> Wykonuję węzeł B")
    return {"counter": state['counter'] + 1, "messages": [SystemMessage(content="Węzeł B został wykonany.")]}

def should_finish(state: DebugState):
    if state['counter'] >= 2:
        return "end"
    return "continue"

workflow = StateGraph(DebugState)
workflow.add_node("A", node_a)
workflow.add_node("B", node_b)
workflow.set_entry_point("A")
workflow.add_edge("A", "B")
workflow.add_conditional_edges(
    "B",
    should_finish,
    {"continue": "A", "end": END}
)
app = workflow.compile()


# Krok 1: Uruchomienie ze `stream` i analiza wyjścia
print("--- Debugowanie za pomocą `stream` ---")

# Definiujemy początkowy stan
initial_state = {
    "messages": [HumanMessage(content="Start")],
    "counter": 0
}

# Używamy pętli, aby drukować stan po każdym kroku
for step in app.stream(initial_state, {"recursion_limit": 5}):
    # `step` to słownik, gdzie kluczem jest nazwa węzła, który właśnie się zakończył
    node_name = list(step.keys())[0]
    state_after_node = step[node_name]

    print(f"\n=== Krok zakończony: Węzeł '{node_name}' ===")
    print(f"Licznik: {state_after_node['counter']}")
    print("Stan wiadomości:")
    for msg in state_after_node['messages']:
        # .pretty_print() to metoda do ładnego drukowania wiadomości
        print(f"  - {msg.pretty_print()}")
    print("-" * 30)


# Krok 2: Wizualizacja architektury
print("\n--- Wizualizacja grafu w ASCII ---")
# Drukuje graf w postaci ASCII w konsoli, abyś mógł zobaczyć jego strukturę
app.get_graph().print_ascii()

# Możesz także wygenerować obrazek PNG (wymaga `pip install pillow py-svg`)
# try:
#     app.get_graph().draw_png(output_file_path="debug_workflow.png")
#     print("\nWygenerowano obrazek grafu: debug_workflow.png")
# except ImportError:
#     print("\nAby wygenerować obrazek PNG, zainstaluj: pip install pillow py-svg")


# 4. Podsumowanie
#
# Debugowanie w LangGraph to proces iteracyjny, polegający na obserwowaniu ewolucji stanu
# i weryfikowaniu, czy przepływ podąża oczekiwaną ścieżką.
#
# Najważniejsze do zapamiętania:
#
#     1. **`stream()` to Twój najlepszy przyjaciel**: Jest to podstawowe narzędzie do śledzenia
#        krok po kroku, jak zmienia się stan Twojej aplikacji.
#     2. **Wizualizuj, aby zrozumieć**: Używaj `print_ascii()` lub `draw_png()`, aby upewnić się,
#        że architektura Twojego grafu jest poprawna.
#     3. **Kontroluj pętle**: Pamiętaj o `recursion_limit`, aby chronić się przed
#        niekontrolowanymi cyklami.
#     4. **Używaj LangSmith do poważnej pracy**: Do głębokiej analizy, monitoringu i debugowania
#        złożonych, produkcyjnych systemów, LangSmith jest niezastąpionym, standardowym narzędziem.
#
# Opanowując te techniki, zyskujesz pewność siebie w budowaniu i utrzymywaniu nawet najbardziej
# skomplikowanych i dynamicznych systemów AI.