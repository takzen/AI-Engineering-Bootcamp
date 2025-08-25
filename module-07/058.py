# Moduł 7, Punkt 58: Wykorzystanie grafów do zarządzania przepływem danych
#
#
#
# Do tej pory postrzegaliśmy LangGraph głównie jako narzędzie do budowy zaawansowanych, cyklicznych agentów.
# To jego najpopularniejsze zastosowanie, ale ograniczenie go tylko do tej roli byłoby niedocenieniem jego
# prawdziwej mocy. LangGraph to uniwersalna maszyna do **orkiestracji dowolnych, złożonych przepływów danych**,
# w których kolejne kroki zależą od wyników poprzednich.
#
# W tej lekcji odejdziemy od pętli agenta i zobaczymy, jak użyć LangGraph do zbudowania wieloetapowego
# procesu przetwarzania informacji, który bardziej przypomina zaawansowaną linię produkcyjną niż autonomicznego agenta.
#
# 1. Problem: Złożone, warunkowe łańcuchy
#
# Wyobraź sobie, że musisz zbudować system, który:
#
#     1. Otrzymuje temat artykułu.
#     2. Decyduje, czy temat jest prosty, czy złożony.
#     3. Jeśli temat jest prosty, generuje krótki, zwięzły artykuł.
#     4. Jeśli temat jest złożony, najpierw tworzy szczegółowy plan (konspekt), a DOPIERO POTEM,
#        na podstawie tego planu, pisze długi, rozbudowany artykuł.
#
# Próba zaimplementowania takiej logiki za pomocą `SequentialChain` byłaby bardzo trudna, jeśli nie niemożliwa.
# Potrzebujemy mechanizmu, który potrafi dynamicznie wybierać ścieżkę przetwarzania.
# LangGraph jest do tego stworzony.
#
# 2. Architektura przepływu danych w LangGraph
#
# Zamiast agenta i narzędzi, nasze węzły będą teraz reprezentować konkretne etapy przetwarzania danych.
# Nasz graf będzie przypominał diagram przepływu (flowchart):
#
#     * **Węzeł "Klasyfikator"**: Analizuje temat i decyduje o jego złożoności.
#     * **Węzeł "Generator Planu"**: Tworzy konspekt dla złożonych tematów.
#     * **Węzeł "Generator Krótkiego Artykułu"**: Pisze prosty tekst.
#     * **Węzeł "Generator Długiego Artykułu"**: Pisze tekst na podstawie planu.
#     * **Krawędź Warunkowa**: Po klasyfikacji, kieruje przepływ do odpowiedniego generatora.
#
# 3. Praktyczny przykład: Warunkowe generowanie artykułu
#
# Zbudujemy od podstaw graf, który implementuje opisaną wyżej logikę.
#
# Krok 0: Instalacja i konfiguracja
# (Zakładamy, że pakiety z poprzednich lekcji są już zainstalowane)
import os
import operator
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Zdefiniowanie Stanu
# Stan będzie przechowywał wszystkie informacje generowane w trakcie procesu.
class ArticleGenerationState(TypedDict):
    topic: str
    classification: str | None
    plan: str | None
    article: str
    
# Krok 2: Inicjalizacja modeli
# Użyjemy dwóch modeli, aby pokazać elastyczność
classifier_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
writer_llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

# Krok 3: Zdefiniowanie Węzłów jako funkcji
def classify_topic(state: ArticleGenerationState):
    print("--- WĘZEŁ: Klasyfikacja tematu ---")
    prompt = f"""Na podstawie poniższego tematu, oceń jego złożoność. Odpowiedz tylko jednym słowem: 'prosty' lub 'złożony'.
    Temat: {state['topic']}"""
    response = classifier_llm.invoke(prompt)
    return {"classification": response.content.lower()}

def generate_plan(state: ArticleGenerationState):
    print("--- WĘZEŁ: Generowanie planu artykułu ---")
    prompt = f"Stwórz szczegółowy plan (konspekt) dla artykułu na temat: {state['topic']}"
    response = writer_llm.invoke(prompt)
    return {"plan": response.content}

def generate_short_article(state: ArticleGenerationState):
    print("--- WĘZEŁ: Generowanie krótkiego artykułu ---")
    prompt = f"Napisz krótki, zwięzły artykuł (około 100 słów) na temat: {state['topic']}"
    response = writer_llm.invoke(prompt)
    return {"article": response.content}

def generate_long_article(state: ArticleGenerationState):
    print("--- WĘZEŁ: Generowanie długiego artykułu na podstawie planu ---")
    prompt = f"""Napisz długi, wyczerpujący artykuł na temat: {state['topic']}.
    Użyj poniższego planu jako struktury:
    --- PLAN ---
    {state['plan']}
    """
    response = writer_llm.invoke(prompt)
    return {"article": response.content}

# Krok 4: Zdefiniowanie Logiki Warunkowej
def route_after_classification(state: ArticleGenerationState):
    print("--- KRAWĘDŹ: Decyzja o ścieżce ---")
    if state['classification'] == "prosty":
        print("-> Kieruję do generatora krótkiego artykułu.")
        return "generate_short"
    else:
        print("-> Kieruję do generatora planu.")
        return "generate_plan"

# Krok 5: Zbudowanie Grafu
workflow = StateGraph(ArticleGenerationState)

# Dodajemy wszystkie nasze węzły
workflow.add_node("classifier", classify_topic)
workflow.add_node("plan_generator", generate_plan)
workflow.add_node("short_article_generator", generate_short_article)
workflow.add_node("long_article_generator", generate_long_article)

# Ustawiamy punkt startowy
workflow.set_entry_point("classifier")

# Dodajemy krawędź warunkową po klasyfikacji
workflow.add_conditional_edges(
    "classifier",
    route_after_classification,
    {
        "generate_short": "short_article_generator",
        "generate_plan": "plan_generator",
    }
)

# Definiujemy pozostałe, bezwarunkowe ścieżki
# Po wygenerowaniu planu, zawsze idziemy do generatora długiego artykułu
workflow.add_edge("plan_generator", "long_article_generator")

# Po napisaniu artykułu (zarówno krótkiego, jak i długiego), kończymy pracę
workflow.add_edge("short_article_generator", END)
workflow.add_edge("long_article_generator", END)

# Krok 6: Skompilowanie i Uruchomienie
app = workflow.compile()

# Testujemy na prostym temacie
print("\n--- TEST 1: TEMAT PROSTY ---")
simple_topic_input = {"topic": "korzyści z picia wody"}
result_simple = app.invoke(simple_topic_input)
print("\nFinalny artykuł:")
print(result_simple['article'])

# Testujemy na złożonym temacie
print("\n\n--- TEST 2: TEMAT ZŁOŻONY ---")
complex_topic_input = {"topic": "wpływ mechaniki kwantowej na rozwój sztucznej inteligencji"}
result_complex = app.invoke(complex_topic_input)
print("\nWygenerowany plan:")
print(result_complex['plan'])
print("\nFinalny artykuł:")
print(result_complex['article'])

#
# 4. Podsumowanie
#
# Ta lekcja pokazała, że LangGraph to nie tylko narzędzie do budowy agentów, ale przede wszystkim
# potężny silnik do orkiestracji przepływów, w których logika nie jest liniowa.
#
# Najważniejsze do zapamiętania:
#
#     1. **Myśl jak projektant procesów**: Każdy węzeł w grafie to konkretny krok w procesie przetwarzania.
#        Każda krawędź to decyzja lub przejście do kolejnego etapu.
#     2. **Grafy do złożonej logiki**: Jeśli Twój proces zawiera warunki typu "jeśli X, zrób Y, w przeciwnym razie zrób Z",
#        LangGraph jest idealnym narzędziem do jego zamodelowania.
#     3. **Stan jako pamięć procesu**: Obiekt stanu (`State`) staje się centralnym "magazynem" na wszystkie
#        artefakty wygenerowane w trakcie procesu (klasyfikacje, plany, wersje robocze).
#     4. **Ponad agentami**: Możesz użyć tej samej techniki do orkiestracji dowolnych zadań: analizy danych,
#        generowania kodu, dynamicznego tworzenia raportów i wielu innych.
#
# Opanowanie tej perspektywy pozwala na budowanie systemów, które są nie tylko inteligentne, ale także
# zorganizowane, przewidywalne i łatwe w debugowaniu.