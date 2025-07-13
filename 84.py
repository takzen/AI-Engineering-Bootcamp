# Moduł 9, Punkt 84: Jak połączyć RAG z LangChain?
#
#
#
# To pytanie może wydawać się nieco mylące, ponieważ w rzeczywistości nie "łączymy" RAG z LangChain.
# Prawidłowe ujęcie jest takie: **RAG to wzorzec architektoniczny, a LangChain to framework,
# którego używamy do zaimplementowania tego wzorca w praktyce.**
#
# LangChain dostarcza wszystkie niezbędne, modularne komponenty (klocki), a następnie daje nam
# "klej" – LangChain Expression Language (LCEL) – aby połączyć te klocki w jeden, spójny
# i działający pipeline RAG.
#
# W tej lekcji zbudujemy od zera kompletny łańcuch RAG, aby zobaczyć, jak każdy
# z komponentów LangChain odgrywa swoją rolę w tym procesie.
#
# 1. Przepis na RAG w LangChain
#
# Budowa pipeline'u RAG w LangChain przypomina składanie dania z przepisu. Potrzebujemy
# następujących "składników" (komponentów LangChain):
#
#     1.  **Retriever**: Obiekt, który potrafi przyjąć zapytanie (string) i zwrócić listę
#         relevantnych dokumentów. Najczęściej tworzymy go na bazie Bazy Wektorowej
#         (np. FAISS, PGVector). To nasza "ręka sięgająca do biblioteki".
#
#     2.  **Prompt Template**: Szablon, który definiuje, jak połączyć znalezione dokumenty (kontekst)
#         z oryginalnym pytaniem użytkownika w jedną, zrozumiałą dla LLM-a instrukcję.
#
#     3.  **Model (LLM)**: "Mózg", który otrzyma sformatowany prompt i wygeneruje na jego podstawie
#         odpowiedź (np. `ChatOpenAI`).
#
#     4.  **Output Parser**: (Opcjonalny, ale zalecany) Komponent, który oczyszcza i formatuje
#         surową odpowiedź z modelu do pożądanej formy (np. prostego stringa).
#
#     5.  **Klej (LCEL)**: LangChain Expression Language, czyli operator `|` (pipe), który
#         pozwala nam elegancko połączyć te wszystkie składniki w jeden, wykonywalny łańcuch.
#
# 2. Praktyczny przykład: Budowa pełnego łańcucha RAG
#
# Zbudujmy od podstaw prosty, ale kompletny pipeline RAG.
#
# Krok 0: Instalacja
# # pip install langchain-openai langchain-community faiss-cpu
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Stworzenie i przygotowanie Retrievera
# (W realnej aplikacji, ten etap byłby bardziej rozbudowany, z loaderami i splitterami)
documents = [
    Document(page_content="Krzysztof Kolumb dopłynął do Ameryki w 1492 roku.", metadata={"source": "podrecznik-historii.pdf"}),
    Document(page_content="Stolicą Polski jest Warszawa.", metadata={"source": "encyklopedia-geografii.pdf"}),
    Document(page_content="LangChain to framework do budowy aplikacji opartych o LLM.", metadata={"source": "dokumentacja-langchain.md"})
]
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(k=1) # Będziemy pobierać 1 najbardziej relevantny dokument

# Krok 2: Zdefiniowanie szablonu promptu
# Ten prompt jasno instruuje model, jak ma się zachować.
template = """Jesteś pomocnym asystentem. Odpowiedz na pytanie bazując wyłącznie na poniższym kontekście.
Jeśli kontekst nie zawiera odpowiedzi, powiedz, że nie wiesz.

Kontekst:
{context}

Pytanie:
{question}

Odpowiedź:
"""
prompt = ChatPromptTemplate.from_template(template)

# Krok 3: Zbudowanie łańcucha za pomocą LCEL
# To jest serce naszej aplikacji, gdzie łączymy wszystkie komponenty.
rag_chain = (
    # Wejście do łańcucha to słownik {"question": "..."}.
    # RunnablePassthrough() przekazuje to pytanie dalej.
    # Jednocześnie, `assign` tworzy nowy klucz "context",
    # którego wartością jest wynik działania retrievera.
    {"context": retriever, "question": RunnablePassthrough()}
    # Wynik: słownik {"context": [Dokumenty], "question": "..."}
    
    # Przekazujemy ten słownik do szablonu promptu
    | prompt
    # Wynik: obiekt `PromptValue`
    
    # Przekazujemy sformatowany prompt do modelu LLM
    | ChatOpenAI(model="gpt-4o")
    # Wynik: obiekt `AIMessage`
    
    # Parsujemy odpowiedź z modelu do prostego stringa
    | StrOutputParser()
    # Wynik: string z odpowiedzią
)

# Krok 4: Uruchomienie i testowanie łańcucha
print("--- Testowanie pipeline'u RAG ---")

# Pytanie 1: Odpowiedź jest w naszej bazie wiedzy
question1 = "Kto odkrył Amerykę?"
print(f"\nPYTANIE: {question1}")
answer1 = rag_chain.invoke(question1)
print(f"ODPOWIEDŹ: {answer1}")

# Pytanie 2: Odpowiedź również jest w bazie wiedzy
question2 = "Czym jest LangChain?"
print(f"\nPYTANIE: {question2}")
answer2 = rag_chain.invoke(question2)
print(f"ODPOWIEDŹ: {answer2}")

# Pytanie 3: Odpowiedzi NIE MA w naszej bazie wiedzy
question3 = "Ile lat ma Słońce?"
print(f"\nPYTANIE: {question3}")
answer3 = rag_chain.invoke(question3)
print(f"ODPOWIEDŹ: {answer3}")

#
# 3. Podsumowanie
#
# Właśnie zobaczyłeś, jak LangChain służy jako potężny system do implementacji
# wzorca RAG. To nie są dwie oddzielne technologie, które trzeba "łączyć" –
# to wzorzec i narzędzie stworzone dla siebie nawzajem.
#
# Najważniejsze do zapamiętania:
#
#     1. **LangChain dostarcza komponenty**: Każdy element pipeline'u RAG (Retriever, Prompt,
#        LLM, Parser) jest reprezentowany przez gotową do użycia klasę w LangChain.
#     2. **LCEL jest spoiwem**: LangChain Expression Language (`|`) pozwala na eleganckie,
#        czytelne i deklaratywne łączenie tych komponentów w działający pipeline.
#     3. **Kontrola nad przepływem**: Dzięki LCEL, masz pełną kontrolę nad tym, jak dane
#        przepływają przez system – co jest przekazywane, gdzie i w jakiej formie.
#
# Opanowanie tego wzorca jest absolutną podstawą do budowy niemal każdej nowoczesnej,
# opartej na faktach aplikacji AI.