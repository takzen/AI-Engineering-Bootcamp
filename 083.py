# Moduł 9, Punkt 83: Zastosowanie RAG w wyszukiwarkach
#
#
#
# Wyszukiwarki internetowe, takie jak Google czy Bing, są z nami od dekad. Ich tradycyjne
# działanie opierało się na skomplikowanych algorytmach indeksowania i rankowania stron
# na podstawie słów kluczowych, linków i setek innych czynników. Wynikiem było zawsze
# to samo: **lista niebieskich linków**, przez które użytkownik musiał się samodzielnie
# przebić, aby znaleźć odpowiedź.
#
# Pojawienie się Dużych Modeli Językowych i techniki RAG zapoczątkowało największą
# rewolucję w wyszukiwaniu od lat. Nowoczesne wyszukiwarki (jak Perplexity.ai, Copilot,
# czy nowe funkcje w Google) nie dają nam już tylko listy linków. Dają nam
# **bezpośrednią, syntetyczną odpowiedź**, a linki traktują jako źródła i dowody.
#
# W tej lekcji zobaczymy, jak architektura RAG jest sercem tej rewolucji i jak możemy
# zbudować własną, uproszczoną wersję takiej "wyszukiwarki nowej generacji".
#
# 1. Problem: "Lista linków" to nie jest odpowiedź
#
# Tradycyjne wyszukiwarki mają kilka fundamentalnych problemów z perspektywy użytkownika:
#
#     * **Wymagają pracy**: Użytkownik musi otworzyć kilka linków, przeczytać je, porównać
#       informacje i samodzielnie zsyntetyzować odpowiedź na swoje pytanie.
#     * **Problem "SEO spam"**: Wyniki są często zdominowane przez strony zoptymalizowane pod
#       kątem algorytmów, a niekoniecznie te z najlepszą treścią.
#     * **Brak zrozumienia intencji**: Wyszukiwarka dopasowuje słowa kluczowe, ale nie zawsze
#       rozumie, o co tak naprawdę pyta użytkownik.
#
# 2. Architektura wyszukiwarki opartej o RAG
#
# Nowoczesna, "odpowiadająca" wyszukiwarka to w swojej istocie zaawansowany system RAG.
# Jej działanie można opisać w kilku krokach:
#
#     1. **Zrozumienie zapytania**: Pierwszy, mały LLM analizuje pytanie użytkownika, aby lepiej
#        zrozumieć jego intencję.
#     2. **Tradycyjne wyszukiwanie (Retrieval)**: System używa tradycyjnych indeksów, aby
#        błyskawicznie znaleźć 10-20 najbardziej relevantnych stron internetowych.
#     3. **Wczytanie i przetworzenie treści**: System w czasie rzeczywistym "odwiedza" te
#        strony i wczytuje ich treść.
#     4. **Synteza i generowanie (Generation)**: Najbardziej relevantne fragmenty są łączone
#        z oryginalnym pytaniem i przekazywane do potężnego LLM-a z instrukcją syntezy odpowiedzi.
#     5. **Prezentacja wyniku**: Użytkownik otrzymuje gotową odpowiedź wraz z listą klikalnych źródeł.
#
# 3. Praktyczny przykład: Budowa mini-wyszukiwarki z narzędziem
#
# Zbudowanie pełnej wyszukiwarki od zera jest niemożliwe, ale możemy z łatwością **symulować**
# jej działanie, używając gotowego narzędzia do wyszukiwania w internecie i łącząc je
# z LLM-em w prosty łańcuch RAG.
#
# Krok 0: Instalacja
# # pip install langchain-openai langchain-community tavily
#
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["TAVILY_API_KEY"] = "tvly-..."
if "OPENAI_API_KEY" not in os.environ or "TAVILY_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawione zmienne środowiskowe OpenAI i Tavily.")
    exit()

# Krok 1: Inicjalizacja komponentów
llm = ChatOpenAI(model="gpt-4o", temperature=0)
search_tool = TavilySearchResults()

# Krok 2: Definicja szablonu promptu
# Ten prompt instruuje model, jak ma działać jako silnik odpowiedzi
search_prompt = ChatPromptTemplate.from_template("""Jesteś silnikiem wyszukiwarki nowej generacji.
Twoim zadaniem jest udzielenie bezpośredniej, zwięzłej odpowiedzi na pytanie użytkownika,
bazując wyłącznie na wynikach wyszukiwania, które Ci dostarczono.
Zawsze podawaj źródła swoich informacji, jeśli są dostępne w kontekście.

Wyniki wyszukiwania (kontekst):
{context}

Pytanie użytkownika:
{question}

Odpowiedź:""")

# Krok 3: Budowa łańcucha RAG za pomocą LCEL
# Ten łańcuch jest pięknym przykładem potęgi LangChain Expression Language.
# Prześledźmy go krok po kroku:
chain = (
    # 1. Wejście: Oczekujemy słownika z kluczem "question".
    # `RunnablePassthrough.assign` przekazuje to pytanie dalej
    # i JEDNOCZEŚNIE wykonuje nową operację (wyszukiwanie).
    RunnablePassthrough.assign(
        # 2. Wywołujemy narzędzie wyszukiwania. `RunnableLambda` opakowuje
        # dowolną funkcję. Wynik wyszukiwania jest przypisywany do klucza "context".
        context=RunnableLambda(lambda x: search_tool.invoke(x["question"]))
    )
    # 3. Teraz mamy słownik z kluczami "question" i "context".
    # Przekazujemy go do naszego szablonu promptu.
    | search_prompt
    # 4. Sformatowany prompt trafia do LLM-a.
    | llm
    # 5. Odpowiedź z LLM-a jest parsowana do stringa.
    | StrOutputParser()
)

# Krok 4: Testowanie naszej mini-wyszukiwarki
print("--- Mini-wyszukiwarka RAG ---")
question = "Jakie były najważniejsze ogłoszenia na ostatniej konferencji Apple WWDC?"
print(f"Pytanie: {question}")

# Uruchamiamy łańcuch
response = chain.invoke({"question": question})

print(f"\nOdpowiedź:\n{response}")

#
# 4. Podsumowanie: Przyszłość wyszukiwania
#
# RAG fundamentalnie zmienia naszą interakcję z informacją. Zamiast być "łowcami linków",
# stajemy się rozmówcami, którzy otrzymują bezpośrednie, zsyntetyzowane odpowiedzi.
#
# Najważniejsze do zapamiętania:
#
#     1. **RAG to silnik nowoczesnych wyszukiwarek**: Architektura "wyszukaj, a potem syntetyzuj"
#        jest rdzeniem takich usług jak Perplexity, Copilot czy Google AI Overviews.
#     2. **Dwa etapy są kluczowe**: Najpierw szybkie, szerokie wyszukanie kandydatów (retrieval),
#        a potem głębokie, inteligentne zrozumienie i synteza (generation).
#     3. **Cytowanie źródeł buduje zaufanie**: Zawsze, gdy system RAG generuje odpowiedź,
#        powinien wskazywać, na jakich danych się oparł. To kluczowe dla wiarygodności.
#     4. **Możesz to zbudować sam**: Używając gotowych narzędzi (jak Tavily) i potęgi LCEL,
#        możesz w kilkunastu linijkach kodu stworzyć własną, działającą "odpowiadającą
#        wyszukiwarkę", co jeszcze kilka lat temu wymagałoby zespołu inżynierów.
#
# To pokazuje, jak techniki, które poznaliśmy w tym module, mają bezpośrednie zastosowanie
# w budowie produktów, z których korzystają miliony ludzi na całym świecie.