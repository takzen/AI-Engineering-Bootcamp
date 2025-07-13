# Moduł 8, Punkt 71: Tworzenie zaawansowanych logów i analiz błędów
#
#
#
# Opanowaliśmy już podstawy monitorowania i debugowania w LangSmith. Wiemy, jak przeglądać
# ślady, identyfikować błędy i analizować wydajność. Ale co, jeśli domyślne informacje,
# które zbiera LangSmith, to za mało? Co, jeśli do pełnej analizy potrzebujemy
# **własnego, specyficznego dla naszej aplikacji kontekstu biznesowego**?
#
# W tej lekcji nauczymy się, jak przejść od pasywnego obserwatora do aktywnego architekta
# naszych logów. Wzbogacimy nasze ślady o niestandardowe metadane, tagi i zdarzenia,
# przekształcając LangSmith z narzędzia do debugowania w potężną platformę analityczną.
#
# 1. Problem: Domyślne logi nie znają Twojego biznesu
#
# Standardowy ślad w LangSmith jest doskonały w pokazywaniu, **co** technicznie zrobiła aplikacja.
# Nie wie on jednak nic o szerszym kontekście, w którym ta operacja została wykonana:
#
#     * Który użytkownik (`user_id`) zainicjował to zapytanie?
#     * Z jakiej wersji promptu (`prompt_version`) korzystała ta instancja aplikacji?
#     * Czy był to użytkownik z planu "darmowego" czy "premium"?
#     * Jaki konkretny dokument (`document_id`) był analizowany w tym przebiegu RAG?
#
# Bez tych informacji, analiza błędów i wydajności jest ograniczona. Nie możemy odpowiedzieć na
# pytania typu: "Czy nasz nowy prompt v2 generuje więcej błędów dla użytkowników darmowych?".
#
# 2. Techniki wzbogacania logów w LangSmith
#
# LangChain i LangSmith SDK dostarczają prostych, ale potężnych mechanizmów do dodawania
# własnego kontekstu.
#
#     **Technika 1: Metadane i Tagi w czasie wywołania**
#     To najprostszy i najczęstszy sposób na dodanie kontekstu. Podczas wywoływania łańcucha
#     lub grafu, możemy przekazać specjalny argument `configurable`.
#
#     **Technika 2: Śledzenie niestandardowych funkcji za pomocą `@traceable`**
#     Czasem jeden węzeł w naszym grafie wykonuje kilka skomplikowanych operacji. Domyślnie,
#     w LangSmith zobaczymy go jako jeden, monolityczny blok. Dekorator `@traceable` z biblioteki
#     `langsmith` pozwala "opakować" dowolną funkcję Pythona, dzięki czemu pojawi się ona
#     w śladzie jako osobny, zagnieżdżony krok (span).
#
#     **Technika 3: Programistyczne dodawanie opinii (Feedback)**
#     Oprócz manualnego klikania w panelu, możemy wysyłać opinie bezpośrednio z naszego kodu.
#     Pozwala to na automatyzację oceny, np. na podstawie logiki biznesowej
#     ("jeśli odpowiedź nie zawierała żadnego źródła, oznacz ją jako złą").
#
# 3. Praktyczny przykład: Wzbogacony system RAG
#
# Zbudujemy prosty graf RAG i wzbogacimy jego ślady o niestandardowe informacje.
#
# Krok 0: Instalacja i konfiguracja
# pip install langchain-openai langgraph langsmith
import os
from typing import TypedDict, Annotated
import operator
from langsmith import traceable, Client
from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage

# Konfiguracja API i LangSmith
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "ls__..."
# os.environ["LANGCHAIN_PROJECT"] = "Zaawansowane Logi"
if "LANGCHAIN_TRACING_V2" not in os.environ:
    print("\nBŁĄD: Skonfiguruj zmienne środowiskowe LangSmith, aby zobaczyć efekty.")
    exit()

# Krok 1: Definicja stanu i "udawanej" bazy danych
class RagState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    context: str

# Krok 2: Tworzenie wzbogaconych węzłów
# Używamy dekoratora @traceable, aby ta funkcja pojawiła się jako osobny krok w LangSmith
@traceable(name="RetrieveDocuments")
def retrieve_documents_node(state: RagState):
    print("--- WĘZEŁ: Pobieranie dokumentów ---")
    # W prawdziwej aplikacji tutaj byłoby zapytanie do bazy wektorowej.
    # My symulujemy pobranie kontekstu.
    retrieved_context = "LangSmith to platforma do debugowania, testowania i monitorowania aplikacji LLM."
    return {"context": retrieved_context}

# Drugi węzeł, który generuje odpowiedź
@traceable(name="GenerateAnswer")
def generate_answer_node(state: RagState):
    print("--- WĘZEŁ: Generowanie odpowiedzi ---")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = f"""Na podstawie poniższego kontekstu, odpowiedz na pytanie użytkownika.
Kontekst: {state['context']}
Pytanie: {state['messages'][-1].content}"""
    response = llm.invoke(prompt)
    return {"messages": [AIMessage(content=response.content)]}

# Krok 3: Budowa grafu
workflow = StateGraph(RagState)
workflow.add_node("retriever", retrieve_documents_node)
workflow.add_node("generator", generate_answer_node)
workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "generator")
workflow.add_edge("generator", END)
app = workflow.compile()

# Krok 4: Uruchomienie grafu z metadanymi
print("\n--- Uruchomienie grafu z metadanymi ---")
initial_input = {"messages": [HumanMessage(content="Czym jest LangSmith?")]}
config = {
    "configurable": {
        "metadata": {
            "user_id": "user-5678",
            "prompt_version": "rag-v1.2",
            "customer_plan": "premium",
        },
        "tags": ["rag_system", "test_run"],
    }
}

# Uruchamiamy graf, przekazując konfigurację
run_result = app.invoke(initial_input, config=config)
print(f"Finalna odpowiedź: {run_result['messages'][-1].content}")

# Krok 5: Programistyczne dodanie opinii
print("\n--- Programistyczne dodawanie opinii ---")
# Pobieramy ID ostatniego uruchomienia. W prawdziwej aplikacji
# uzyskalibyśmy to ID z nagłówków odpowiedzi lub kontekstu.
# Tutaj musimy je znaleźć manualnie lub użyć bardziej zaawansowanych technik.
# Dla celów demonstracyjnych, zakładamy, że mamy ID.
# run_id = ...
# client = Client()
# client.create_feedback(
#     run_id=run_id,
#     key="quality_score", # Niestandardowy klucz oceny
#     score=0.9, # Ocena numeryczna
#     comment="Odpowiedź była trafna i zwięzła."
# )
print("Opinia została (symulacyjnie) dodana. Sprawdź swój ślad w LangSmith.")


# 4. Podsumowanie
#
# Wzbogacanie logów przekształca LangSmith z narzędzia deweloperskiego w platformę analityki
# biznesowej dla Twoich aplikacji AI. Pozwala na znacznie głębsze zrozumienie,
# jak aplikacja jest używana i gdzie występują problemy.
#
# Najważniejsze do zapamiętania:
#
#     1. **Kontekst to wszystko**: Dodawaj metadane (`metadata`) do swoich wywołań, aby powiązać
#        techniczne logi z kontekstem biznesowym (użytkownicy, wersje, plany).
#     2. **Rozbijaj złożoność**: Używaj dekoratora `@traceable`, aby uzyskać wgląd w wewnętrzne
#        operacje Twoich węzłów i funkcji.
#     3. **Automatyzuj ocenę**: Wykorzystaj programistyczny dostęp do opinii (`feedback`), aby
#        implementować własne, automatyczne systemy oceny jakości odpowiedzi.
#
# Dzięki tym technikom, Twoja zdolność do analizy i optymalizacji aplikacji wkracza na
# zupełnie nowy poziom, pozwalając na podejmowanie decyzji na podstawie bogatych,
# kontekstowych danych.