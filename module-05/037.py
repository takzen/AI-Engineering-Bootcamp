# Moduł 5, Punkt 37: Tworzenie dynamicznych aplikacji AI z LangChain
#
#
#
# Do tej pory budowaliśmy łańcuchy, które działały w sposób liniowy lub sekwencyjny. Nawet nasi agenci, choć inteligentni,
# podążali za ogólnym celem. Ale co, jeśli chcemy zbudować aplikację, która sama decyduje, którą z kilku predefiniowanych
# ścieżek wybrać, w zależności od zapytania użytkownika?
#
# W tej lekcji nauczymy się tworzyć **dynamiczne aplikacje**, które potrafią inteligentnie kierować (routować) zapytania
# do odpowiednich, wyspecjalizowanych łańcuchów.
#
# 1. Statyczna vs. Dynamiczna Aplikacja
#
#     * **Aplikacja statyczna/sekwencyjna**: Podąża jedną, z góry ustaloną ścieżką. Wyobraź sobie linię montażową – każdy
#       produkt przechodzi przez te same stacje w tej samej kolejności.
#
#     * **Aplikacja dynamiczna**: Działa jak sortownia paczek. Na podstawie "etykiety" (charakteru zapytania),
#       decyduje, na którą taśmę (do którego łańcucha) ma trafić paczka (zapytanie), aby zostać poprawnie obsłużona.
#
# 2. Problem: Jeden łańcuch do wszystkiego to zły pomysł
#
# Załóżmy, że tworzymy chatbota-eksperta. Chcemy, aby odpowiadał na pytania z różnych dziedzin, np. fizyki i historii.
# Moglibyśmy spróbować stworzyć jeden, gigantyczny prompt, który instruuje model, jak ma być ekspertem od wszystkiego.
# Jednak takie podejście jest:
#
#     * **Niewydajne**: Prompt staje się długi i skomplikowany.
#     * **Niezawodne**: Model może się "pogubić" i mieszać style odpowiedzi.
#     * **Trudne w utrzymaniu**: Każda zmiana w jednej "dziedzinie" wymaga edycji całego, wielkiego promptu.
#
# Lepszym rozwiązaniem jest stworzenie kilku mniejszych, wyspecjalizowanych łańcuchów (jeden dla fizyki, jeden dla historii)
# i zbudowanie "inteligentnego rozdzielacza" (routera), który skieruje pytanie do właściwego eksperta.
#
# 3. Rozwiązanie: `RunnableBranch` – Logika warunkowa w LangChain
#
# `RunnableBranch` to potężne narzędzie z LangChain Expression Language (LCEL), które działa jak instrukcja `if-elif-else` w Pythonie.
# Pozwala na zdefiniowanie serii warunków i przypisanych do nich łańcuchów.
#
# Budowa dynamicznego łańcucha z `RunnableBranch` przebiega w trzech krokach:
#     1. **Stworzenie łańcucha-klasyfikatora**: To łańcuch, który analizuje zapytanie użytkownika i przypisuje mu kategorię (np. "fizyka", "historia", "ogólne").
#     2. **Stworzenie wyspecjalizowanych łańcuchów**: Budujemy osobne łańcuchy dla każdej kategorii.
#     3. **Zbudowanie `RunnableBranch`**: Łączymy wszystko w całość, definiując, który łańcuch ma być uruchomiony dla danej kategorii.
#
# 4. Praktyczny przykład: Bot-Ekspert z Fizyki i Historii
#
# Zbudujemy aplikację, która na podstawie pytania zdecyduje, czy skierować je do "fizyka", "historyka", czy odpowiedzieć w sposób ogólny.
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch, RunnablePassthrough

# Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Inicjalizacja modelu, którego będziemy używać we wszystkich łańcuchach
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Krok 1: Stworzenie łańcucha-klasyfikatora
szablon_klasyfikatora = ChatPromptTemplate.from_template(
    """Na podstawie poniższego pytania użytkownika, zaklasyfikuj je do jednej z następujących kategorii: fizyka, historia, ogólne.
Odpowiedz tylko i wyłącznie JEDNYM słowem: 'fizyka', 'historia' lub 'ogólne'.

Pytanie: {pytanie}
Klasyfikacja:"""
)
lancuch_klasyfikujacy = szablon_klasyfikatora | llm | StrOutputParser()

# Krok 2: Stworzenie wyspecjalizowanych łańcuchów
szablon_fizyka = ChatPromptTemplate.from_template(
    "Jesteś światowej klasy fizykiem. Odpowiedz na poniższe pytanie w sposób precyzyjny i naukowy.\nPytanie: {pytanie}"
)
lancuch_fizyka = szablon_fizyka | llm | StrOutputParser()

szablon_historia = ChatPromptTemplate.from_template(
    "Jesteś profesorem historii z ogromną wiedzą. Odpowiedz na poniższe pytanie, podając kontekst i ważne daty.\nPytanie: {pytanie}"
)
lancuch_historia = szablon_historia | llm | StrOutputParser()

szablon_ogolny = ChatPromptTemplate.from_template(
    "Jesteś pomocnym asystentem AI. Odpowiedz na poniższe pytanie w sposób prosty i zrozumiały.\nPytanie: {pytanie}"
)
lancuch_ogolny = szablon_ogolny | llm | StrOutputParser()

# Krok 3: Zbudowanie `RunnableBranch`
# `RunnableBranch` przyjmuje listę par: (warunek, łańcuch) oraz domyślny łańcuch.
rozgalezienie = RunnableBranch(
    (lambda x: "fizyka" in x["kategoria"], lancuch_fizyka),
    (lambda x: "historia" in x["kategoria"], lancuch_historia),
    lancuch_ogolny  # Domyślna ścieżka, jeśli żaden warunek nie zostanie spełniony
)

# Krok 4: Połączenie wszystkiego w jeden, dynamiczny łańcuch
# Używamy `RunnablePassthrough.assign`, aby przekazać oryginalne pytanie dalej w łańcuchu,
# jednocześnie dodając do niego wynik klasyfikacji.
pelny_lancuch = RunnablePassthrough.assign(
    kategoria=lambda x: lancuch_klasyfikujacy.invoke({"pytanie": x["pytanie"]})
) | rozgalezienie

# Krok 5: Testowanie dynamicznej aplikacji
print("--- Testowanie dynamicznego bota ---")

pytanie1 = "Jakie były główne przyczyny wybuchu II Wojny Światowej?"
print(f"\n[PYTANIE]: {pytanie1}")
wynik1 = pelny_lancuch.invoke({"pytanie": pytanie1})
print(f"[ODPOWIEDŹ BOTA]: {wynik1}")

pytanie2 = "Wyjaśnij zasadę nieoznaczoności Heisenberga."
print(f"\n[PYTANIE]: {pytanie2}")
wynik2 = pelny_lancuch.invoke({"pytanie": pytanie2})
print(f"[ODPOWIEDŹ BOTA]: {wynik2}")

pytanie3 = "Jaki jest przepis na dobrą szarlotkę?"
print(f"\n[PYTANIE]: {pytanie3}")
wynik3 = pelny_lancuch.invoke({"pytanie": pytanie3})
print(f"[ODPOWIEDŹ BOTA]: {wynik3}")

#
# 5. Podsumowanie
#
# Opanowanie routingu za pomocą `RunnableBranch` przenosi Twoje umiejętności tworzenia aplikacji AI na zupełnie nowy poziom.
#
# Najważniejsze do zapamiętania:
#
#     * Dynamiczne aplikacje potrafią **wybierać ścieżkę działania** w zależności od danych wejściowych.
#     * Zamiast jednego, skomplikowanego łańcucha, buduj **wiele małych, wyspecjalizowanych łańcuchów**.
#     * Użyj **łańcucha-klasyfikatora**, aby "oznakować" przychodzące zapytania.
#     * `RunnableBranch` działa jak **`if-elif-else` dla LangChain**, kierując dane do odpowiedniego, wyspecjalizowanego łańcucha.
#     * Ten wzorzec (klasyfikator + rozgałęzienie) jest niezwykle potężny i uniwersalny.
#
# Możesz teraz budować znacznie bardziej złożone i "inteligentne" systemy, które reagują na potrzeby użytkownika w sposób kontekstowy i precyzyjny.