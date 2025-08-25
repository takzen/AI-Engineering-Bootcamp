# Moduł 5, Punkt 38: Testowanie i debugowanie aplikacji LangChain
#
#
#
# Stworzyłeś już swoje pierwsze łańcuchy, agentów i dynamiczne aplikacje. Gratulacje!
# Teraz stajesz przed jednym z największych wyzwań w pracy z LLM: Co zrobić, gdy coś nie działa tak, jak powinno?
#
# Aplikacje oparte na modelach językowych często zachowują się jak "czarne skrzynki" (black boxes).
# Wysyłasz zapytanie i otrzymujesz odpowiedź, ale co dokładnie działo się po drodze? Jaki ostateczny prompt
# zobaczył model? Jakich narzędzi użył agent?
#
# W tej lekcji nauczysz się zaglądać do wnętrza tej czarnej skrzynki.
#
# 1. Dlaczego debugowanie w LangChain jest inne?
#
# W przeciwieństwie do tradycyjnego programowania, gdzie błędy są zazwyczaj jasne (np. `SyntaxError`, `NullPointerException`),
# problemy w LangChain są często bardziej subtelne:
#
#     * **Zły prompt**: Najczęstszy problem. Po dodaniu historii konwersacji i zmiennych, ostateczny prompt
#       może wyglądać inaczej, niż się spodziewałeś, co "dezorientuje" model.
#     * **Niedeterminizm LLM**: Nawet przy niskiej `temperaturze`, model może generować nieco inne odpowiedzi.
#     * **Błędna logika agenta**: Agent może uporczywie wybierać złe narzędzie lub wpaść w pętlę.
#     * **Złożoność łańcuchów**: W długiej sekwencji łańcuchów trudno jest określić, które ogniwo zawiodło.
#
# 2. Podstawowe narzędzia do debugowania
#
# LangChain oferuje wbudowane mechanizmy, które są pierwszą linią obrony w walce z błędami.
#
#     * **`verbose=True`**: Najprostsze i najczęściej używane narzędzie. Po ustawieniu tego parametru
#       w łańcuchu lub agencie, LangChain będzie drukował w konsoli podstawowe informacje o przebiegu
#       wykonania – wejścia, wyjścia i "myśli" agenta.
#
#     * **`langchain.debug = True`**: Globalny "włącznik" trybu debugowania. Daje znacznie więcej informacji
#       niż `verbose`. Zobaczysz szczegółowe dane wejściowe i wyjściowe dla KAŻDEGO komponentu łańcucha,
#       włącznie z dokładną treścią promptów wysyłanych do LLM.
#
#     * **LangSmith**: To profesjonalna platforma od twórców LangChain, stworzona specjalnie do śledzenia (tracing),
#       monitorowania i debugowania aplikacji LLM. To jak "narzędzia deweloperskie przeglądarki" dla LangChain.
#       Pozwala na wizualne prześledzenie każdego kroku, analizę kosztów i opóźnień oraz przechowywanie
#       historii wszystkich wywołań. Konfiguracja jest banalnie prosta – wystarczy ustawić kilka zmiennych środowiskowych.
#
# 3. Praktyczny przykład: Debugowanie Agenta SQL
#
# Użyjemy agenta SQL z poprzedniej lekcji, aby zobaczyć te narzędzia w akcji. Jego proces decyzyjny jest
# na tyle złożony, że idealnie nadaje się do debugowania.
#
# Krok 1: Instalacja i konfiguracja
import os
import sqlite3
import langchain
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent

# WAŻNE: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Przygotowujemy tę samą bazę danych co poprzednio
baza_plik = ":memory:"
conn = sqlite3.connect(baza_plik, check_same_thread=False)
cursor = conn.cursor()
cursor.executescript("""
CREATE TABLE pracownicy (id INTEGER PRIMARY KEY, nazwisko TEXT NOT NULL, stanowisko TEXT NOT NULL, pensja REAL NOT NULL);
INSERT INTO pracownicy (id, nazwisko, stanowisko, pensja) VALUES
(1, 'Kowalski', 'Analityk', 7000.00), (2, 'Nowak', 'Programista', 12000.00), (3, 'Wiśniewska', 'Programista', 13500.00);
""")
conn.commit()

db = SQLDatabase.from_uri(f"sqlite:///{baza_plik}")
llm = ChatOpenAI(model="gpt-4", temperature=0)

# --- Test 1: Użycie `verbose=True` ---
print("\n--- Test 1: Debugowanie za pomocą `verbose=True` ---")
agent_verbose = create_sql_agent(llm=llm, db=db, agent_type="openai-tools", verbose=True)
agent_verbose.invoke("Kto zarabia najwięcej i na jakim stanowisku?")
# W konsoli zobaczysz "myśli" agenta: jakie narzędzia rozważa, jaki SQL generuje.

# --- Test 2: Użycie `langchain.debug = True` ---
print("\n\n--- Test 2: Szczegółowe debugowanie z `langchain.debug = True` ---")
# Włączamy globalny tryb debugowania
langchain.debug = True
agent_debug = create_sql_agent(llm=llm, db=db, agent_type="openai-tools") # verbose nie jest już potrzebne
agent_debug.invoke("Ilu mamy programistów?")
# Zauważ znacznie większą szczegółowość logów: [llm/start], [chain/start], etc.
# Widzisz dokładny JSON wysłany do API i otrzymaną odpowiedź.
# Wyłączamy tryb debugowania, aby nie wpływał na kolejne uruchomienia.
langchain.debug = False

# --- Test 3: Użycie LangSmith ---
print("\n\n--- Test 3: Profesjonalne śledzenie z LangSmith ---")
# Aby to zadziałało, musisz:
# 1. Zarejestrować się na https://smith.langchain.com/ i stworzyć projekt.
# 2. Utworzyć klucz API w ustawieniach projektu.
# 3. Ustawić poniższe zmienne środowiskowe:
#
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "ls__TWOJ_KLUCZ_LANGSMITH"
# os.environ["LANGCHAIN_PROJECT"] = "Nazwa Twojego Projektu" # Opcjonalnie, ale dobra praktyka

if os.environ.get("LANGCHAIN_TRACING_V2") == "true":
    print("LangSmith jest włączony. Uruchamiam agenta...")
    agent_langsmith = create_sql_agent(llm=llm, db=db, agent_type="openai-tools")
    agent_langsmith.invoke("Podaj średnią pensję analityka.")
    print("\nGotowe! Przejdź do swojego panelu LangSmith, aby zobaczyć pełny, interaktywny ślad wykonania (trace).")
else:
    print("LangSmith nie jest skonfigurowany. Pomiędzy testem.")

conn.close()

#
# 4. Podsumowanie
#
# Debugowanie aplikacji LLM z zgadywania zamienia się w inżynierię, gdy masz odpowiednie narzędzia.
#
# Najważniejsze do zapamiętania:
#
#     * Zawsze zaczynaj od `verbose=True`, aby uzyskać szybki wgląd w działanie łańcucha.
#     * Gdy potrzebujesz więcej szczegółów, włącz `langchain.debug = True`, aby zobaczyć wszystko, co dzieje się "pod maską".
#     * Do poważnych projektów i monitoringu **używaj LangSmith**. To standard branżowy, który oszczędza
#       mnóstwo czasu i pozwala na dogłębną analizę działania aplikacji.
#     * **Najważniejsza zasada debugowania**: Zawsze sprawdzaj ostateczny, w pełni sformatowany prompt,
#       który trafia do modelu. To tam najczęściej kryje się przyczyna problemu.
#
# Posiadając te umiejętności, jesteś w pełni gotów do budowania, testowania i utrzymywania złożonych
# i niezawodnych aplikacji opartych o LangChain. Powodzenia!