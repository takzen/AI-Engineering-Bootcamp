# Moduł 5, Punkt 34: Tworzenie agentów AI i ich narzędzi (Tools)
#
#
#
# Dotarliśmy do jednego z najbardziej ekscytujących tematów w LangChain: Agentów.
# Do tej pory nasze łańcuchy były jak posłuszni pracownicy na linii produkcyjnej – wykonywały z góry określoną sekwencję zadań.
# Agenci to krok dalej. To inteligentni "menedżerowie", którzy sami decydują, jakich narzędzi użyć, aby rozwiązać postawiony przed nimi problem.
#
# 1. Czym jest Agent?
#
# Agent to byt, który używa LLM nie tylko do prostej odpowiedzi, ale do **myślenia i podejmowania decyzji**.
# Zamiast sztywno podążać ścieżką, agent działa w pętli:
#
#     1. **Analizuje** zapytanie użytkownika.
#     2. **Decyduje**, czy może odpowiedzieć od razu, czy potrzebuje użyć jakiegoś narzędzia (Tool).
#     3. Jeśli wybierze narzędzie, **wykonuje** je.
#     4. **Obserwuje** wynik działania narzędzia.
#     5. Na podstawie obserwacji **ponownie analizuje** problem i decyduje o kolejnym kroku.
#
# Ten cykl (znany jako pętla ReAct: Reason + Act) trwa, dopóki agent nie uzna, że znalazł ostateczną odpowiedź dla użytkownika.
#
# 2. Czym jest Narzędzie (Tool)?
#
# Narzędzie to "supermoc", którą dajemy agentowi. To nic innego jak funkcja, której agent może użyć do interakcji
# ze światem zewnętrznym. Każde narzędzie ma dwie kluczowe cechy, które LLM musi zrozumieć:
#
#     * `name`: Krótka, zwięzła nazwa (np. `wyszukiwarka_internetowa`).
#     * `description`: Bardzo ważny opis w języku naturalnym, wyjaśniający, **co to narzędzie robi i kiedy należy go użyć**.
#       To na podstawie tego opisu LLM decyduje, czy dane narzędzie jest odpowiednie do rozwiązania problemu.
#
# Przykłady narzędzi:
#     * Wyszukiwarka internetowa (do sprawdzania aktualnych informacji).
#     * Kalkulator (do precyzyjnych obliczeń matematycznych).
#     * Interpreter Pythona (do wykonywania kodu).
#     * Dostęp do bazy danych SQL (do zadawania pytań o dane firmowe).
#     * Dostęp do API (np. do sprawdzania pogody, kursów walut).
#
# 3. Jak zbudować Agenta?
#
# Proces tworzenia agenta w nowoczesnym LangChain składa się z kilku kroków:
#
#     1. **Zdefiniowanie Narzędzi**: Wybieramy gotowe narzędzia z biblioteki LangChain lub tworzymy własne.
#     2. **Wybranie Modelu**: Agenci najlepiej działają z modelami czatu (jak `ChatOpenAI`), które są zoptymalizowane pod kątem instrukcji i logiki.
#     3. **Stworzenie Promptu**: Tworzymy specjalny prompt, który instruuje model, jak ma się zachowywać jako agent i jak korzystać z narzędzi. Na szczęście LangChain Hub dostarcza gotowe, przetestowane szablony.
#     4. **Połączenie komponentów**: Używamy funkcji `create_..._agent`, aby połączyć LLM, narzędzia i prompt w jednego, spójnego agenta.
#     5. **Stworzenie `AgentExecutor`**: To "silnik" wykonawczy, który bierze naszego agenta i faktycznie uruchamia pętlę myślenia i działania.
#
# 4. Praktyczny przykład: Agent z dostępem do internetu
#
# Zbudujemy agenta, który potrafi odpowiadać na pytania dotyczące aktualnych wydarzeń, korzystając z wyszukiwarki internetowej.
# Użyjemy do tego narzędzia Tavily Search, które jest świetnie zintegrowane z LangChain.
#
# Krok 1: Instalacja niezbędnych bibliotek
# pip install langchain langchain-openai tavily-python
#
# Krok 2: Konfiguracja API
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor

# WAŻNE: Potrzebujesz DWÓCH kluczy API: OpenAI i Tavily Search.
# 1. Ustaw klucz OpenAI:
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_OPENAI"
# 2. Zarejestruj się na https://tavily.com/, aby uzyskać darmowy klucz API i ustaw go:
# os.environ["TAVILY_API_KEY"] = "tvly-TWOJ_KLUCZ_TAVILY"

if "OPENAI_API_KEY" not in os.environ or "TAVILY_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawione zmienne środowiskowe OPENAI_API_KEY i TAVILY_API_KEY.")
    exit()

# --- Budowa Agenta ---

# Krok 1: Zdefiniowanie Narzędzi
# Tworzymy listę narzędzi, które agent będzie miał do dyspozycji.
# Na razie będzie to tylko jedno narzędzie - wyszukiwarka Tavily.
narzedzia = [TavilySearchResults(max_results=2)]

# Krok 2: Wybranie Modelu
# Używamy modelu czatu, który dobrze radzi sobie z rozumowaniem.
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

# Krok 3: Stworzenie Promptu z LangChain Hub
# LangChain Hub to repozytorium gotowych zasobów. Ściągamy sprawdzony szablon promptu dla agentów.
# Ten prompt instruuje model, jak ma używać dostarczonych narzędzi.
prompt_agenta = hub.pull("hwchase17/openai-tools-agent")
print("\n--- Pobrany szablon promptu ---")
print(prompt_agenta.messages)
print("-" * 30)

# Krok 4: Połączenie komponentów w Agenta
agent = create_openai_tools_agent(llm, narzedzia, prompt_agenta)

# Krok 5: Stworzenie `AgentExecutor` - silnika wykonawczego
# To on będzie zarządzał pętlą myślenia i działania.
# `verbose=True` jest kluczowe, aby zobaczyć "myśli" agenta!
agent_executor = AgentExecutor(agent=agent, tools=narzedzia, verbose=True)

# Krok 6: Uruchomienie Agenta
print("\n--- Uruchamiamy Agenta ---")
pytanie = "Kto jest aktualnym prezydentem Brazylii i w którym roku się urodził?"
wynik = agent_executor.invoke({"input": pytanie})

print("\n--- Wynik końcowy ---")
print(f"Pytanie: {pytanie}")
print(f"Odpowiedź Agenta: {wynik['output']}")

#
# 5. Podsumowanie
#
# Gratulacje! Stworzyłeś swojego pierwszego, w pełni autonomicznego agenta AI.
#
# Najważniejsze do zapamiętania:
#
#     * Agent to nie tylko wykonawca, ale byt, który **myśli, planuje i decyduje**.
#     * Narzędzia (Tools) to "supermoce" agenta, a ich **opis jest kluczowy** dla LLM.
#     * Agent działa w pętli **ReAct (Reason + Act)**, analizując problem i dobierając odpowiednie narzędzia.
#     * Budowa agenta to proces składania klocków: **Narzędzia + LLM + Prompt = Agent**, który jest uruchamiany przez **AgentExecutor**.
#     * Używanie `verbose=True` w `AgentExecutor` pozwala zajrzeć "do głowy" agenta i zrozumieć jego proces decyzyjny.
#
# To dopiero początek. Możesz tworzyć własne narzędzia, dawać agentom dostęp do baz danych i budować
# skomplikowane systemy, które automatyzują złożone zadania.