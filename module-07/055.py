# Moduł 7, Punkt 55: Czym jest LangGraph i jak działa?
#
#
#
# Witaj w świecie prawdziwej orkiestracji AI! Do tej pory w LangChain i LangFlow budowaliśmy aplikacje,
# które działały w sposób sekwencyjny lub w ramach predefiniowanej pętli agenta. Były jak proste
# linie produkcyjne lub pracownicy wykonujący z góry określone zadania.
#
# Ale co, jeśli chcemy zbudować coś znacznie bardziej złożonego? Co, jeśli nasza aplikacja musi:
#
#     * Dynamicznie decydować, czy powrócić do poprzedniego kroku, aby spróbować innej strategii?
#     * Tworzyć złożone cykle, w których agent wielokrotnie próbuje użyć narzędzia, aż odniesie sukces?
#     * Koordynować pracę wielu różnych "aktorów" (agentów), którzy współpracują nad rozwiązaniem problemu?
#
# Tutaj standardowe łańcuchy (`Chains`) okazują się niewystarczające. Potrzebujemy narzędzia do budowy
# **cyklicznych i stanowych** przepływów. Tym narzędziem jest LangGraph.
#
# 1. Problem: Liniowość łańcuchów
#
# Standardowe łańcuchy w LangChain są jak autostrady – mają jasno określony początek i koniec.
# `SequentialChain` wykonuje kroki A -> B -> C. Nie ma w nim miejsca na powrót z kroku C do kroku A.
# Nawet standardowi Agenci, choć działają w pętli, jest to specyficzny, z góry zdefiniowany cykl (ReAct).
# Nie dają nam pełnej kontroli nad logiką tej pętli.
#
# 2. Rozwiązanie: Myślenie w kategoriach grafu stanu
#
# LangGraph to biblioteka (zbudowana na bazie LangChain) do tworzenia zaawansowanych, stanowych aplikacji AI.
# Zamiast myśleć o aplikacji jako o liniowej sekwencji, LangGraph pozwala nam modelować ją jako **graf**.
#
# Pomyśl o tym jak o grze planszowej:
#     * **Graf**: To cała plansza do gry.
#     * **Stan (State)**: To aktualne położenie wszystkich pionków, liczba punktów, posiadane karty. To "pamięć" całej gry.
#     * **Węzły (Nodes)**: To pola na planszy, na których wykonuje się akcję (np. "Rzuć kostką", "Pobierz kartę", "Zadzwoń do LLM").
#     * **Krawędzie (Edges)**: To strzałki łączące pola. Mówią, dokąd masz się udać po wykonaniu akcji na danym polu.
#
# Najważniejszą innowacją LangGraph jest wprowadzenie **krawędzi warunkowych (Conditional Edges)**.
# To jak rozdroża na planszy, gdzie na podstawie rzutu kostką (wyniku z LLM) decydujesz, czy idziesz w lewo, w prawo, czy cofasz się o trzy pola.
#
# 3. Kluczowe komponenty LangGraph
#
# Budując aplikację w LangGraph, operujesz na kilku podstawowych elementach:
#
#     * **StateGraph**: Główny obiekt, który reprezentuje Twój graf. Definiujesz w nim, jaki jest kształt
#       Twojego stanu (np. słownik Pythona).
#
#     * **Węzły (Nodes)**: To funkcje Pythona lub `Runnable` z LangChain. Każdy węzeł:
#         1. Przyjmuje na wejściu aktualny stan.
#         2. Wykonuje swoją logikę (np. wywołuje LLM, narzędzie, przetwarza dane).
#         3. Zwraca słownik z aktualizacjami do stanu.
#
#     * **Krawędzie (Edges)**: To połączenia, które dodajesz do grafu.
#         - `add_node()`: Dodaje nowy węzeł do grafu.
#         - `add_edge()`: Tworzy prostą, bezwarunkową krawędź ("po węźle A, zawsze idź do B").
#         - `add_conditional_edges()`: Tworzy krawędź warunkową. Wskazujesz węzeł, a następnie funkcję,
#           która na podstawie stanu zdecyduje, do którego z kolejnych węzłów przejść.
#         - `set_entry_point()` i `set_finish_point()`: Określa, gdzie graf ma się zacząć i skończyć.
#
# 4. LangGraph vs. Agenci LangChain – Kiedy czego używać?
#
# *   **Standardowy Agent LangChain**: Użyj go, gdy potrzebujesz szybko zbudować prostego agenta z narzędziami,
#     a predefiniowana logika pętli ReAct jest dla Ciebie wystarczająca. To jak kupno gotowego samochodu.
#
# *   **LangGraph**: Użyj go, gdy chcesz mieć **pełną, precyzyjną kontrolę** nad każdym krokiem decyzyjnym agenta.
#     To jak budowanie własnego samochodu od podstaw – sam projektujesz silnik, skrzynię biegów i zawieszenie.
#     Jest to idealne do:
#         - Budowy złożonych, wieloetapowych agentów.
#         - Tworzenia systemów, w których kilku agentów współpracuje ze sobą.
#         - Implementacji cykli "spróbuj-ponów" (np. jeśli narzędzie zwróci błąd, spróbuj innego).
#         - Wprowadzania człowieka do pętli (human-in-the-loop), gdzie na pewnym etapie człowiek musi zatwierdzić działanie agenta.
#
# 5. Konceptualny przykład: Prosty agent z narzędziem w LangGraph
#
# # Zobaczmy, jak mógłby wyglądać szkielet prostego agenta w LangGraph.
# # Uwaga: Ten kod jest konceptualny i wymaga uzupełnienia o faktyczną logikę.

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

# Krok 1: Zdefiniuj stan
# Stan to słownik, który przechowuje wszystkie dane potrzebne w trakcie działania grafu.
# TypedDict pomaga w utrzymaniu porządku i sprawdzaniu typów.
class AgentState(TypedDict):
    question: str
    agent_outcome: any
    intermediate_steps: list

# Krok 2: Zdefiniuj węzły jako funkcje Pythona
# Każdy węzeł przyjmuje stan i zwraca słownik z aktualizacjami do stanu.
# Zmieniona funkcja call_agent
def call_agent(state: AgentState):
    print("--- WĘZEŁ: Agent decyduje ---")
    
    # SPRAWDŹ STAN: Czy mamy już jakieś wyniki od narzędzi?
    if state.get("intermediate_steps") and len(state["intermediate_steps"]) > 0:
        # Jeśli tak, to znaczy, że narzędzie już zadziałało.
        # Agent powinien teraz wygenerować ostateczną odpowiedź i zakończyć pracę.
        print("Agent ma już wyniki, kończy pracę.")
        # Symulujemy ostateczną odpowiedź. Zwracamy sam tekst, a nie słownik akcji.
        final_answer = state["intermediate_steps"][-1][1] # Bierzemy ostatni wynik
        return {"agent_outcome": f"Ostateczna odpowiedź to: {final_answer}"}
    else:
        # Jeśli nie ma wyników, agent musi użyć narzędzia.
        print("Agent nie ma wyników, decyduje o użyciu narzędzia.")
        return {"agent_outcome": {"action": "call_tool", "tool_input": "pogoda w Warszawie"}}

def call_tool(state: AgentState):
    print("--- WĘZEŁ: Wykonanie narzędzia ---")
    # Tutaj wywoływalibyśmy prawdziwe narzędzie.
    # Symulujemy wynik działania narzędzia.
    tool_result = "Słonecznie, 25 stopni Celsjusza."
    return {"intermediate_steps": [("pogoda w Warszawie", tool_result)]}

# Krok 3: Zdefiniuj logikę krawędzi warunkowej
# Ta funkcja decyduje, dokąd graf ma przejść dalej.
def should_continue(state: AgentState):
    print("--- KRAWĘDŹ WARUNKOWA: Sprawdzanie decyzji agenta ---")
    if isinstance(state.get("agent_outcome"), dict) and "action" in state["agent_outcome"]:
        # Jeśli agent zdecydował się na akcję, idziemy do węzła 'action'.
        return "continue_to_action"
    else:
        # W przeciwnym razie kończymy pracę.
        return "end_work"

# Krok 4: Zbuduj graf
workflow = StateGraph(AgentState)

# Dodaj węzły do grafu
workflow.add_node("agent", call_agent)
workflow.add_node("action", call_tool)

# Ustaw punkt wejścia
workflow.set_entry_point("agent")

# Krok 5: Dodaj krawędzie
# Dodaj krawędź warunkową, która po decyzji agenta kieruje do odpowiedniego węzła.
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue_to_action": "action",
        "end_work": END  # END to specjalna stała oznaczająca koniec grafu
    }
)

# Po wykonaniu narzędzia ('action'), zawsze wracamy do agenta po kolejną decyzję.
workflow.add_edge('action', 'agent')

# Krok 6: Skompiluj graf w aplikację
app = workflow.compile()

# Można teraz uruchomić graf, przekazując początkowy stan
initial_state = {"question": "Jaka jest pogoda w Warszawie?", "intermediate_steps": []}
result = app.invoke(initial_state)
print(result)

#
# 6. Podsumowanie
#
# LangGraph to narzędzie dla zaawansowanych użytkowników, które otwiera drzwi do tworzenia
# nowej generacji aplikacji AI, opartych na cyklach, stanie i złożonej logice.
#
# Najważniejsze do zapamiętania:
#
#     * LangGraph służy do budowy **stanowych, cyklicznych grafów obliczeniowych**.
#     * Jest idealny do tworzenia **niestandardowych agentów** i systemów wieloagentowych.
#     * Kluczowe koncepcje to **Stan, Węzły i Krawędzie** (zwłaszcza warunkowe).
#     * Daje Ci **pełną kontrolę**, ale wymaga więcej pracy niż użycie gotowych agentów z LangChain.
#
# W kolejnych lekcjach zbudujemy krok po kroku nasz pierwszy, działający graf.