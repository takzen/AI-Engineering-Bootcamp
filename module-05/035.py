# Moduł 5, Punkt 35: Połączenie LangChain z bazami danych
#
#
#
# Do tej pory nasi agenci potrafili korzystać z internetu. To potężna umiejętność, ale co z danymi, które nie są publicznie dostępne?
# Co z kluczowymi informacjami o Twojej firmie – danymi o sprzedaży, użytkownikach, produktach – które są bezpiecznie
# przechowywane w bazach danych?
#
# To jedno z najważniejszych i najbardziej praktycznych zastosowań LLM w biznesie: stworzenie interfejsu w języku naturalnym
# do zadawania pytań o firmowe dane. Zamiast pisać skomplikowane zapytania SQL, użytkownik mógłby po prostu zapytać:
# "Ilu klientów z Warszawy złożyło zamówienie w zeszłym miesiącu?".
#
# 1. Problem: LLM nie zna Twojej bazy danych
#
# Model językowy nie ma pojęcia o strukturze Twojej bazy, tabelach, kolumnach ani relacjach między nimi.
# Musimy dać mu narzędzia, aby mógł się tej struktury "nauczyć", a następnie na jej podstawie samodzielnie
# konstruować i wykonywać zapytania SQL.
#
# LangChain oferuje do tego celu wyspecjalizowanego **Agenta SQL**.
#
# 2. Jak działa Agent SQL?
#
# Agent SQL to zaawansowany agent, który jest fabrycznie wyposażony w zestaw narzędzi (tzw. `SQLDatabaseToolkit`)
# zoptymalizowanych do pracy z bazami danych. Jego pętla myślenia (ReAct) wygląda mniej więcej tak:
#
#     1. **Analiza pytania**: Użytkownik pyta: "Który produkt sprzedaje się najlepiej?".
#     2. **Inspekcja schematu**: Agent używa narzędzia `list_tables_sql_tool`, aby zobaczyć, jakie tabele są w bazie (np. `produkty`, `sprzedaz`).
#     3. **Sprawdzenie kolumn**: Używa narzędzia `info_sql_tool`, aby sprawdzić, jakie kolumny mają te tabele (np. `produkty` ma `id_produktu`, `nazwa`; `sprzedaz` ma `id_produktu`, `ilosc`).
#     4. **Napisanie zapytania SQL**: Na podstawie zdobytej wiedzy, LLM konstruuje poprawne zapytanie SQL, np. `SELECT nazwa FROM produkty JOIN sprzedaz ON produkty.id_produktu = sprzedaz.id_produktu 
#       GROUP BY nazwa ORDER BY SUM(ilosc) DESC LIMIT 1`.
#     5. **Wykonanie zapytania**: Używa narzędzia `query_sql_tool`, aby wykonać wygenerowany kod SQL na bazie danych.
#     6. **Interpretacja wyniku**: Otrzymuje wynik z bazy (np. `[('Laptop',)]`), a następnie formułuje ostateczną odpowiedź w języku naturalnym: "Najlepiej sprzedającym się produktem jest Laptop."
#
#
# 3. Praktyczny przykład: Agent odpowiadający na pytania o sprzedaż
#
# Stworzymy prostą, tymczasową bazę danych w pamięci (`SQLite`) i podłączymy do niej agenta, który będzie
# odpowiadał na pytania dotyczące produktów i sprzedaży.
#
# Krok 1: Instalacja niezbędnych bibliotek
# pip install langchain langchain-openai sqlalchemy
#
# Krok 2: Konfiguracja API i tworzenie tymczasowej bazy danych
import os
import sqlite3
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent, AgentExecutor

# WAŻNE: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Tworzymy tymczasową bazę danych SQLite w pamięci RAM
# Dzięki temu nie musimy tworzyć żadnych plików na dysku.
baza_plik = ":memory:"
conn = sqlite3.connect(baza_plik, check_same_thread=False)
cursor = conn.cursor()

# Tworzymy tabele i wstawiamy przykładowe dane
cursor.executescript("""
CREATE TABLE produkty (
    id_produktu INTEGER PRIMARY KEY,
    nazwa TEXT NOT NULL,
    cena REAL NOT NULL
);

CREATE TABLE sprzedaz (
    id_sprzedazy INTEGER PRIMARY KEY,
    id_produktu INTEGER,
    ilosc INTEGER NOT NULL,
    FOREIGN KEY (id_produktu) REFERENCES produkty (id_produktu)
);

INSERT INTO produkty (id_produktu, nazwa, cena) VALUES
(1, 'Laptop', 4500.00),
(2, 'Myszka', 150.00),
(3, 'Klawiatura', 250.00);

INSERT INTO sprzedaz (id_sprzedazy, id_produktu, ilosc) VALUES
(1, 1, 10), -- 10 laptopów
(2, 2, 50), -- 50 myszek
(3, 3, 30), -- 30 klawiatur
(4, 1, 5);  -- dodatkowe 5 laptopów
""")
conn.commit()
print("--- Tymczasowa baza danych została utworzona i wypełniona danymi. ---")

# --- Budowa Agenta SQL ---

# Krok 3: Stworzenie obiektu `SQLDatabase`
# LangChain potrzebuje specjalnego "opakowania" (wrappera) na połączenie z bazą danych.
# Używamy do tego standardowego formatu URI dla SQLAlchemy.
db = SQLDatabase.from_uri(f"sqlite:///{baza_plik}",
                          sample_rows_in_table_info=2) # Dodajemy przykładowe wiersze do opisu tabeli, co pomaga modelowi

# Krok 4: Inicjalizacja LLM i Agenta
llm = ChatOpenAI(model="gpt-4", temperature=0)

# `create_sql_agent` to potężna funkcja, która automatycznie:
# - Tworzy odpowiedni zestaw narzędzi (SQLDatabaseToolkit)
# - Wybiera zoptymalizowany pod SQL szablon promptu
# - Łączy to wszystko w gotowego do pracy agenta
agent_sql = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",
    verbose=True
)

# Krok 5: Uruchomienie Agenta i zadawanie pytań
print("\n--- Pytanie 1: Proste zliczenie ---")
pytanie1 = "Ile mamy produktów w ofercie?"
wynik1 = agent_sql.invoke(pytanie1)
print(f"\nKońcowa odpowiedź: {wynik1['output']}")

print("\n\n--- Pytanie 2: Zapytanie wymagające JOIN i agregacji ---")
pytanie2 = "Jaka jest łączna wartość sprzedaży produktu 'Laptop'?"
wynik2 = agent_sql.invoke(pytanie2)
print(f"\nKońcowa odpowiedź: {wynik2['output']}")

# Zamknięcie połączenia z bazą danych
conn.close()

#
# 4. Podsumowanie
#
# Właśnie zbudowałeś system, który pozwala na konwersację z bazą danych w języku naturalnym.
# To niezwykle potężne narzędzie, które może zdemokratyzować dostęp do danych w każdej organizacji.
#
# Najważniejsze do zapamiętania:
#
#     * Agent SQL to specjalistyczny agent LangChain, który potrafi samodzielnie pisać i wykonywać zapytania SQL.
#     * Kluczem do jego działania jest zestaw narzędzi (`SQLDatabaseToolkit`), które pozwalają mu na inspekcję schematu bazy.
#     * Proces zaczyna się od opakowania połączenia z bazą w obiekt `SQLDatabase` od LangChain.
#     * Funkcja `create_sql_agent` znacznie upraszcza cały proces, automatycznie konfigurując większość elementów.
#     * Dzięki `verbose=True` możesz śledzić "proces myślowy" agenta – od analizy schematu, przez pisanie kodu SQL, po interpretację wyników.
#
# Opanowanie tej techniki otwiera drzwi do tworzenia zaawansowanych aplikacji analitycznych i systemów Business Intelligence,
# które są dostępne dla każdego, nie tylko dla osób znających SQL.