# Moduł 7, Punkt 65: Zastosowanie LangGraph w systemach rekomendacyjnych
#
#
#
# W poprzednich modułach dowiedzieliśmy się, jak LLM-y mogą tworzyć rekomendacje, rozumiejąc
# język naturalny. Zazwyczaj opierało się to na prostym procesie: wyszukaj podobne pozycje,
# a następnie poproś LLM o wygenerowanie odpowiedzi. Był to proces jednokierunkowy.
#
# Ale co, jeśli chcemy stworzyć system, który jest bardziej jak rozmowa z doświadczonym sprzedawcą
# lub kuratorem sztuki? System, który nie tylko daje odpowiedź, ale zadaje dodatkowe pytania,
# doprecyzowuje nasze potrzeby i iteracyjnie zawęża poszukiwania, aby znaleźć idealną propozycję?
#
# To jest zadanie, do którego LangGraph jest stworzony idealnie.
#
# 1. Ograniczenia tradycyjnych rekomendacji AI
#
# Prosty system RAG (Retrieval-Augmented Generation) jest potężny, ale ma swoje ograniczenia:
#
#     * **Brak interakcji**: Użytkownik zadaje pytanie i dostaje odpowiedź. Nie ma miejsca na dialog
#       i doprecyzowanie.
#     * **Problem z niejednoznacznością**: Jeśli zapytanie użytkownika jest niejasne (np. "poleć mi
#       jakiś ciekawy film"), system może dać przypadkową lub nietrafioną odpowiedź.
#     * **Brak przezroczystości**: Użytkownik nie wie, dlaczego system polecił mu akurat te pozycje.
#
# 2. LangGraph jako silnik konwersacyjnego asystenta rekomendacji
#
# LangGraph pozwala nam zbudować system, który działa w inteligentnej, interaktywnej pętli.
# Zamiast prostego przepływu, tworzymy cykliczny graf, który potrafi:
#
#     1. **Zrozumieć początkową prośbę.**
#     2. **Wyszukać wstępnych kandydatów.**
#     3. **Przeanalizować kandydatów** i zdecydować, czy są wystarczająco dobrzy, aby je polecić.
#     4. **Jeśli nie są**, system może **zadać użytkownikowi doprecyzowujące pytanie** ("Widzę, że
#        lubisz science-fiction. Wolisz coś w klimacie cyberpunku czy raczej space operę?").
#     5. **Przyjąć odpowiedź użytkownika**, zaktualizować swój stan wiedzy o jego preferencjach i
#        **ponownie rozpocząć cykl** wyszukiwania, tym razem z bardziej precyzyjnymi kryteriami.
#
# 3. Praktyczny przykład: Interaktywny asystent filmowy
#
# Zbudujemy uproszczony graf, który po otrzymaniu zapytania, wyszukuje filmy, a następnie
# decyduje, czy polecić je od razu, czy poprosić o więcej informacji.
#
# Krok 0: Instalacja i konfiguracja
import os
import operator
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Przygotowanie danych i zdefiniowanie stanu
# Nasza mini-baza filmów
movie_db = {
    "Matrix": "Film akcji science-fiction o hakerze, który odkrywa, że świat jest symulacją.",
    "Forrest Gump": "Dramat komediowy o człowieku o niskim IQ, ale wielkim sercu, który bierze udział w kluczowych wydarzeniach w historii USA.",
    "Blade Runner 2049": "Mroczny, filozoficzny film neo-noir science-fiction o poszukiwaniu prawdy o własnej tożsamości.",
    "Władca Pierścieni": "Epicki film fantasy o drużynie, która musi zniszczyć potężny artefakt, aby ocalić świat."
}

class RecommendationState(TypedDict):
    # Przechowujemy całą historię rozmowy
    messages: Annotated[list[AnyMessage], operator.add]
    # Przechowujemy listę znalezionych kandydatów
    candidates: List[str]

# Krok 2: Zdefiniowanie węzłów
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Węzeł, który przeszukuje naszą "bazę danych"
def retrieve_movies_node(state: RecommendationState):
    print("--- WĘZEŁ: Wyszukiwanie kandydatów ---")
    last_message = state['messages'][-1].content
    # Proste wyszukiwanie na podstawie słów kluczowych
    found_movies = [title for title, desc in movie_db.items() if any(word in desc.lower() for word in last_message.lower().split())]
    print(f"-> Znaleziono: {found_movies}")
    return {"candidates": found_movies}

# Główny węzeł agenta, który analizuje sytuację
def recommendation_agent_node(state: RecommendationState):
    print("--- WĘZEŁ: Agent rekomendacyjny ---")
    # Budujemy prompt, który zawiera prośbę użytkownika i znalezionych kandydatów
    system_prompt = f"""Jesteś asystentem filmowym. Twoim zadaniem jest pomoc użytkownikowi.
Oto kandydaci, których znaleziono na podstawie jego prośby: {state['candidates']}.

Przeanalizuj prośbę użytkownika i kandydatów.
- Jeśli kandydaci dobrze pasują i jest ich niewielu, sformułuj ostateczną rekomendację i uzasadnienie.
- Jeśli kandydatów jest wielu lub nie jesteś pewien, zadaj użytkownikowi doprecyzowujące pytanie, aby zawęzić wybór.
- Jeśli nie ma kandydatów, poinformuj o tym użytkownika."""
    
    # Dołączamy systemowy prompt do historii rozmowy
    contextual_messages = [SystemMessage(content=system_prompt)] + state['messages']
    response = llm.invoke(contextual_messages)
    return {"messages": [response]}

# Krok 3: Zdefiniowanie logiki routingu
# Ta funkcja zdecyduje, czy pętla ma trwać dalej
def router_function(state: RecommendationState):
    print("--- KRAWĘDŹ WARUNKOWA: Decyzja o kontynuacji ---")
    # Prosta logika: jeśli ostatnia wiadomość od AI zawiera znak zapytania,
    # oznacza to, że prosimy użytkownika o doprecyzowanie i czekamy na jego odpowiedź
    # (w realnej aplikacji tutaj graf by się zatrzymał i czekał na input)
    if '?' in state['messages'][-1].content:
        print("-> Decyzja: Pytanie do użytkownika, kontynuuj pętlę.")
        return "continue"
    else:
        print("-> Decyzja: Odpowiedź finalna, zakończ.")
        return "end"

# Krok 4: Zbudowanie grafu
workflow = StateGraph(RecommendationState)

workflow.add_node("retriever", retrieve_movies_node)
workflow.add_node("agent", recommendation_agent_node)

workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "agent")

workflow.add_conditional_edges(
    "agent",
    router_function,
    {
        # W prawdziwej aplikacji, "continue" zatrzymałoby graf i czekało na input.
        # Tutaj dla demonstracji kończymy, ale pokazujemy potencjał pętli.
        "continue": END,
        "end": END,
    }
)

app = workflow.compile()

# Krok 5: Uruchomienie i testowanie
print("\n--- TEST 1: Zapytanie niejednoznaczne ---")
# Oczekujemy, że agent zada pytanie doprecyzowujące
vague_input = {"messages": [HumanMessage(content="Poleć mi jakiś film science-fiction.")]}
result = app.invoke(vague_input)
print("\nKońcowa wiadomość od agenta:")
print(result['messages'][-1].content)

print("\n\n--- TEST 2: Zapytanie precyzyjne ---")
# Oczekujemy, że agent da konkretną rekomendację
specific_input = {"messages": [HumanMessage(content="Szukam czegoś o hakerach i symulacji.")]}
result = app.invoke(specific_input)
print("\nKońcowa wiadomość od agenta:")
print(result['messages'][-1].content)


# 4. Podsumowanie
#
# LangGraph przekształca systemy rekomendacyjne z prostych wyszukiwarek w inteligentnych,
# konwersacyjnych partnerów. Zamiast jednorazowej transakcji, tworzymy dialog.
#
# Najważniejsze do zapamiętania:
#
#     1. **Interaktywność to klucz**: Wykorzystaj cykliczną naturę LangGraph do budowy systemów,
#        które zadają pytania i iteracyjnie doprecyzowują potrzeby użytkownika.
#     2. **Stan przechowuje kontekst**: Obiekt stanu jest idealnym miejscem do przechowywania nie
#        tylko historii rozmowy, ale także listy potencjalnych kandydatów i zmieniających się
#        preferencji użytkownika.
#     3. **Agent jako kurator**: Główny węzeł agenta nie musi od razu dawać odpowiedzi. Jego rolą
#        może być ocena sytuacji i podjęcie decyzji, czy wie wystarczająco dużo, aby udzielić
#        dobrej porady.
#
# To podejście otwiera drzwi do tworzenia znacznie bardziej spersonalizowanych, transparentnych
# i ostatecznie bardziej użytecznych systemów rekomendacyjnych.