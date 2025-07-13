# Moduł 7, Punkt 63: Optymalizacja przepływów w LangGraph
#
#
#
# Zbudowaliśmy dynamiczne, wieloagentowe systemy. Działają, podejmują decyzje, współpracują.
# Ale czy działają **wydajnie**? Czy są **szybkie**? Czy nie generują **niepotrzebnych kosztów**?
#
# Optymalizacja to ostatni, kluczowy krok, który oddziela imponujący prototyp od niezawodnego,
# produkcyjnego systemu. W tej lekcji poznamy zaawansowane techniki, które pozwolą "wycisnąć"
# z naszych grafów maksimum wydajności, oszczędzając czas i pieniądze.
#
# 1. Dlaczego optymalizacja jest kluczowa?
#
# W złożonych grafach łatwo wpaść w pułapki, które generują problemy:
#
#     * **Koszty**: Każde dodatkowe, nieprzemyślane wywołanie LLM, zwłaszcza potężnych modeli
#       jak GPT-4o, bezpośrednio przekłada się na wyższe rachunki.
#     * **Latencja (Opóźnienia)**: Użytkownicy oczekują szybkich odpowiedzi. System, który
#       każe czekać kilkanaście sekund na wynik, jest niepraktyczny.
#     * **Złożoność**: Nieefektywne, "zagmatwane" grafy są trudniejsze w utrzymaniu i debugowaniu.
#
# 2. Kluczowe techniki optymalizacji w LangGraph
#
#     **Technika 1: Redukcja i dobór wywołań LLM**
#     To najważniejsza optymalizacja.
#     *   **Użyj właściwego modelu do zadania**: Nie każdy węzeł potrzebuje mocy GPT-4o. Do prostych
#         zadań, jak klasyfikacja czy routing (tak jak w naszych poprzednich przykładach),
#         często wystarczy znacznie szybszy i tańszy model, np. GPT-3.5-Turbo.
#     *   **Wymuszaj ustrukturyzowane wyjście**: Zamiast prosić model o odpowiedź w tekście, a potem
#         używać kolejnego wywołania do jej sparsowania, użyj `.with_structured_output()`.
#         Zmusza to model do zwrócenia odpowiedzi w idealnie sformatowanym obiekcie (np. JSON),
#         oszczędzając jedno wywołanie API.
#
#     **Technika 2: Równoległe wykonywanie węzłów (Parallel Execution)**
#     To jedna z "supermocy" grafów. Jeśli masz w przepływie dwa lub więcej zadań, które
#     nie zależą od siebie nawzajem, LangGraph może je wykonać **równolegle**!
#     To jak zamiana jednopasmowej drogi w dwupasmową autostradę.
#
#     **Technika 3: Efektywne zarządzanie stanem**
#     *   **Nie zaśmiecaj stanu**: Przekazuj w stanie tylko te informacje, które są faktycznie
#         potrzebne w kolejnych krokach.
#     *   **Nadpisuj zamiast dodawać**: Domyślnie, `operator.add` w `Annotated` dokleja nowe
#         wiadomości do listy. Czasem bardziej efektywne jest nadpisanie konkretnego pola
#         w stanie, zamiast ciągłego rozbudowywania listy.
#
#     **Technika 4: Streaming wyników**
#     Choć nie skraca to całkowitego czasu obliczeń, streaming (`app.stream()`) znacznie
#     poprawia **odczuwaną przez użytkownika wydajność**. Użytkownik widzi pierwsze fragmenty
#     odpowiedzi niemal natychmiast, zamiast czekać w ciszy na pełny wynik.
#
# 3. Praktyczny przykład: Równoległa analiza tematu
#
# Zbudujemy graf, który otrzymuje temat, a następnie **w tym samym czasie** uruchamia dwa węzły:
# jeden, który szuka argumentów "za", i drugi, który szuka argumentów "przeciw".
# Na koniec, trzeci węzeł zbiera wyniki obu i tworzy zbalansowane podsumowanie.
#
# Krok 0: Instalacja i konfiguracja
import os
import operator
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Zdefiniowanie Stanu
class AnalysisState(TypedDict):
    topic: str
    pros: str | None
    cons: str | None
    summary: str | None

# Krok 2: Zdefiniowanie Węzłów analitycznych
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def pro_analyst_node(state: AnalysisState):
    print("--- WĘZEŁ: Analiza argumentów 'ZA' (może działać równolegle) ---")
    prompt = f"Wypisz w punktach trzy kluczowe argumenty 'za' dla tematu: {state['topic']}"
    response = llm.invoke(prompt)
    return {"pros": response.content}

def con_analyst_node(state: AnalysisState):
    print("--- WĘZEŁ: Analiza argumentów 'PRZECIW' (może działać równolegle) ---")
    prompt = f"Wypisz w punktach trzy kluczowe argumenty 'przeciw' dla tematu: {state['topic']}"
    response = llm.invoke(prompt)
    return {"cons": response.content}

def summarizer_node(state: AnalysisState):
    print("--- WĘZEŁ: Generowanie podsumowania (działa po zakończeniu obu analiz) ---")
    prompt = f"""Na podstawie poniższych argumentów 'za' i 'przeciw', napisz krótkie, zbalansowane podsumowanie na temat: {state['topic']}.

Argumenty ZA:
{state['pros']}

Argumenty PRZECIW:
{state['cons']}
"""
    response = llm.invoke(prompt)
    return {"summary": response.content}

# Krok 3: Zbudowanie Grafu z rozgałęzieniem równoległym
workflow = StateGraph(AnalysisState)

# Dodajemy wszystkie węzły
workflow.add_node("pro_analyst", pro_analyst_node)
workflow.add_node("con_analyst", con_analyst_node)
workflow.add_node("summarizer", summarizer_node)

# Ustawiamy punkt startowy
# LangGraph jest na tyle inteligentny, że jeśli zdefiniujemy kilka punktów startowych,
# postara się je wykonać równolegle.
workflow.set_entry_point("pro_analyst")
workflow.set_entry_point("con_analyst")

# Definiujemy, że po wykonaniu obu analizatorów, przepływ ma trafić do podsumowania.
# 'summarizer' stanie się punktem zbornym, który poczeka na zakończenie obu ścieżek.
workflow.add_edge("pro_analyst", "summarizer")
workflow.add_edge("con_analyst", "summarizer")

# Po podsumowaniu kończymy pracę
workflow.add_edge("summarizer", END)

# Krok 4: Skompilowanie i Uruchomienie
app = workflow.compile()

# Uruchamiamy graf. Obserwuj kolejność komunikatów w konsoli - węzły analizy
# powinny wystartować niemal jednocześnie, a węzeł podsumowania dopiero po nich.
analysis_input = {"topic": "praca zdalna"}
result = app.invoke(analysis_input)

print("\n\n--- WYNIKI KOŃCOWE ---")
print(f"Temat: {result['topic']}")
print(f"\nArgumenty ZA:\n{result['pros']}")
print(f"\nArgumenty PRZECIW:\n{result['cons']}")
print(f"\nZbalansowane Podsumowanie:\n{result['summary']}")


# 4. Podsumowanie
#
# Optymalizacja to nie tylko "wisienka na torcie", ale fundamentalny element budowy
# profesjonalnych, skalowalnych aplikacji AI.
#
# Najważniejsze do zapamiętania:
#
#     1. **Myśl o kosztach i czasie**: Zawsze zastanawiaj się, czy dane wywołanie LLM jest
#        konieczne i czy nie można użyć tańszego/szybszego modelu.
#     2. **Równoległość to Twoja tajna broń**: Jeśli zadania są niezależne, wykonuj je równolegle.
#        LangGraph sprawia, że jest to zaskakująco proste do zaimplementowania.
#     3. **Zarządzaj stanem świadomie**: Dbaj o to, by stan był czysty i zawierał tylko
#        niezbędne informacje, co ułatwia debugowanie i zwiększa wydajność.
#     4. **Od prototypu do optymalizacji**: Cykl pracy często wygląda tak: najpierw zbuduj
#        działający graf, a następnie szukaj w nim "wąskich gardeł" i optymalizuj je,
#        korzystając z poznanych technik.
#
# Dzięki tym umiejętnościom jesteś w stanie tworzyć systemy, które są nie tylko inteligentne,
# ale także szybkie, oszczędne i gotowe na wyzwania produkcyjne.