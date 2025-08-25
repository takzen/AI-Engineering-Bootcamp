# Moduł 5, Punkt 33: Wykorzystanie pamięci (memory) w LangChain
#
#
#
# Czy kiedykolwiek zastanawiałeś się, jak chatboty "pamiętają" poprzednie części rozmowy? Domyślnie, Duże Modele Językowe
# są **stateless** (bezstanowe). Oznacza to, że każde zapytanie traktują jako zupełnie nowe, odizolowane zadanie,
# bez żadnej wiedzy o poprzednich interakcjach. To tak, jakbyś co 30 sekund rozmawiał z osobą z amnezją.
#
# Aby budować użyteczne aplikacje konwersacyjne, musimy dać naszym łańcuchom "pamięć".
#
# 1. Problem bezstanowości LLM
#
# Wyobraź sobie łańcuch z poprzedniej lekcji. Gdybyś uruchomił go dwa razy:
#     1. Uruchomienie: "Cześć, nazywam się Bartek." -> Odpowiedź AI: "Cześć Bartek! Miło mi Cię poznać."
#     2. Uruchomienie: "Jak mam na imię?" -> Odpowiedź AI: "Przepraszam, ale nie wiem, jak masz na imię."
#
# Model nie ma pojęcia o pierwszej interakcji, ponieważ każde wywołanie jest niezależne.
# LangChain rozwiązuje ten problem za pomocą komponentu `Memory`.
#
# 2. Jak działa pamięć w LangChain?
#
# Pamięć w LangChain to nie magia – to sprytny mechanizm, który przed każdym nowym zapytaniem do modelu,
# dołącza do niego historię dotychczasowej konwersacji.
#
# Proces wygląda następująco:
#     1. Użytkownik wysyła nowe zapytanie (np. "Jakie jest najpopularniejsze miasto w Polsce?").
#     2. Komponent `Memory` wczytuje historię dotychczasowej rozmowy.
#     3. LangChain dynamicznie "wstrzykuje" historię do szablonu zapytania (promptu).
#     4. Pełny, rozbudowany prompt (zawierający historię i nowe pytanie) jest wysyłany do LLM.
#     5. Odpowiedź LLM oraz nowe zapytanie użytkownika są zapisywane w pamięci na potrzeby przyszłych interakcji.
#
# Dzięki temu model ma pełen kontekst i może odnosić się do wcześniejszych fragmentów rozmowy.
#
# 3. Najważniejsze typy pamięci
#
# LangChain oferuje wiele strategii zarządzania pamięcią. Oto trzy najpopularniejsze:
#
#     * `ConversationBufferMemory`: Najprostszy typ pamięci. Przechowuje całą rozmowę słowo w słowo
#       i dołącza ją do każdego kolejnego zapytania.
#       Zaleta: Pełen, nienaruszony kontekst.
#       Wada: Przy długich rozmowach tekst może przekroczyć limit tokenów modelu (tzw. context window).
#
#     * `ConversationBufferWindowMemory`: Rozwiązanie problemu `ConversationBufferMemory`. Przechowuje tylko
#       `k` ostatnich interakcji. Jeśli ustawimy `k=3`, pamiętać będzie tylko 3 ostatnie wymiany zdań.
#       Zaleta: Chroni przed przepełnieniem okna kontekstowego.
#       Wada: Model "zapomina" o najstarszych częściach rozmowy.
#
#     * `ConversationSummaryBufferMemory`: Bardzo inteligentne połączenie. Przechowuje `k` ostatnich
#       interakcji w całości, a starsze części rozmowy **podsumowuje** za pomocą LLM.
#       Zaleta: Zachowuje kluczowe informacje z całej rozmowy, nie przekraczając limitu tokenów.
#       Wada: Wymaga dodatkowych wywołań API do tworzenia podsumowań, co zwiększa koszt.
#
# 4. Praktyczny przykład: Budowa łańcucha z pamięcią
#
# Zbudujmy prostego chatbota, który będzie pamiętał nasze imię. Użyjemy `ConversationBufferMemory`.

# --- Konfiguracja i importy ---
import os
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

# WAŻNE: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Zmienna środowiskowa OPENAI_API_KEY nie została ustawiona.")
    exit()

# Inicjalizujemy model LLM
llm = OpenAI(temperature=0.7)

# Krok 1: Inicjalizacja pamięci
# `memory_key` musi odpowiadać nazwie zmiennej w szablonie promptu, która przechowa historię.
pamieta_rozmowe = ConversationBufferMemory(memory_key="historia_rozmowy")

# Krok 2: Stworzenie szablonu promptu z miejscem na historię
# Zauważ specjalną zmienną {historia_rozmowy} - to tutaj LangChain automatycznie wstawi historię rozmowy!
szablon_bota = PromptTemplate(
    input_variables=["historia_rozmowy", "input"],
    template="""Jesteś pomocnym i rozmownym asystentem AI. Poniżej znajduje się historia dotychczasowej konwersacji.
Odpowiadaj zwięźle i grzecznie.

Historia konwersacji:
{historia_rozmowy}

Człowiek: {input}
AI:"""
)

# Krok 3: Stworzenie łańcucha i podłączenie do niego pamięci
lancuch_konwersacyjny = LLMChain(
    llm=llm,
    prompt=szablon_bota,
    verbose=True,  # Zobacz, jak prompt zmienia się z każdą interakcją!
    memory=pamieta_rozmowe
)

# Krok 4: Przeprowadzenie konwersacji
print("\n--- Rozpoczynamy konwersację z botem (ma pamięć!) ---")

# Pierwsze zapytanie
print("\n[CZŁOWIEK]: Cześć, nazywam się Ania.")
wynik1 = lancuch_konwersacyjny.invoke({"input": "Cześć, nazywam się Ania."})
print(f"[AI]: {wynik1['text'].strip()}")

# Drugie zapytanie - bot powinien już wiedzieć, że rozmawia z Anią
print("\n[CZŁOWIEK]: Jaka jest stolica Francji?")
wynik2 = lancuch_konwersacyjny.invoke({"input": "Jaka jest stolica Francji?"})
print(f"[AI]: {wynik2['text'].strip()}")

# Trzecie zapytanie - testujemy pamięć!
print("\n[CZŁOWIEK]: A tak w ogóle, to jak mam na imię?")
wynik3 = lancuch_konwersacyjny.invoke({"input": "A tak w ogóle, to jak mam na imię?"})
print(f"[AI]: {wynik3['text'].strip()}")

#
# 5. Podsumowanie
#
# Dodanie pamięci do łańcuchów to przełomowy moment w budowaniu aplikacji konwersacyjnych.
#
# Najważniejsze do zapamiętania:
#
#     * LLM-y są bezstanowe, a komponent `Memory` w LangChain rozwiązuje ten problem.
#     * Pamięć działa poprzez dynamiczne wstawianie historii rozmowy do promptu.
#     * Istnieją różne typy pamięci (`Buffer`, `Window`, `Summary`), które należy dobrać do konkretnego zadania.
#     * Kluczowe jest dopasowanie `memory_key` w obiekcie pamięci do nazwy zmiennej w szablonie (`{historia_rozmowy}`).
#     * Użycie `verbose=True` jest bezcenne do zrozumienia i debugowania, jak pamięć modyfikuje prompt.
#
# Teraz, gdy nasze łańcuchy mają pamięć, jesteśmy o krok od budowy prawdziwych, interaktywnych agentów!