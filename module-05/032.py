# Moduł 5, Punkt 32: Prompt chaining – jak skutecznie budować łańcuchy zapytań
#
#
#
# W poprzedniej lekcji stworzyliśmy nasz pierwszy, prosty łańcuch (`LLMChain`), który łączył szablon zapytania z modelem językowym.
# To świetny start, ale prawdziwa moc LangChain ujawnia się, gdy zaczynamy łączyć kilka takich łańcuchów w sekwencje.
# Proces ten nazywamy "chainingiem" (od ang. chain - łańcuch).
#
# 1. Dlaczego łączyć łańcuchy?
#
# Wyobraź sobie, że chcesz wykonać bardziej złożone zadanie, na przykład:
# "Dla danego produktu wymyśl chwytliwą nazwę, a następnie na jej podstawie stwórz krótkie hasło reklamowe."
#
# Próba zrobienia tego w jednym zapytaniu do LLM jest możliwa, ale często daje gorsze, mniej przewidywalne rezultaty.
# Model może się "pogubić", skupiając się tylko na jednej części zadania.
#
# Lepszym podejściem jest rozbicie problemu na mniejsze, logiczne kroki:
#     Krok 1: Wygeneruj nazwę produktu. (Jeden łańcuch)
#     Krok 2: Weź wygenerowaną nazwę i stwórz dla niej hasło reklamowe. (Drugi łańcuch)
#
# Łączenie łańcuchów pozwala nam na:
#
#     * Dzielenie złożonych zadań na proste etapy.
#     * Większą kontrolę nad całym procesem.
#     * Uzyskiwanie bardziej spójnych i lepszych jakościowo wyników.
#     * Ponowne wykorzystywanie poszczególnych "ogniw" łańcucha w innych miejscach.
#
# W LangChain służą do tego głównie dwa rodzaje łańcuchów sekwencyjnych: `SimpleSequentialChain` i `SequentialChain`.
#
# 2. `SimpleSequentialChain` – Prosta sekwencja krok po kroku
#
# To najprostszy sposób na połączenie łańcuchów. Działa jak linia produkcyjna:
# wyjście z pierwszego łańcucha staje się wejściem dla drugiego.
#
# Kluczowe cechy:
#     * Przyjmuje tylko jedno wejście na początku.
#     * Zwraca tylko jedno wyjście na końcu.
#     * Idealny do prostych, liniowych zadań.
#
# Zobaczmy to na naszym przykładzie z nazwą i hasłem reklamowym.

# --- Konfiguracja i importy (wspólne dla obu przykładów) ---
import os
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# WAŻNE: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Zmienna środowiskowa OPENAI_API_KEY nie została ustawiona.")
    exit()

# Inicjalizujemy model, tak jak poprzednio
llm = OpenAI(temperature=0.7)

# --- Przykład 1: SimpleSequentialChain ---
from langchain.chains import SimpleSequentialChain

# Łańcuch 1: Generowanie nazwy firmy
prompt_nazwa = PromptTemplate(
    input_variables=["rodzaj_dzialalnosci"],
    template="Zaproponuj jedną, kreatywną nazwę dla firmy, która zajmuje się {rodzaj_dzialalnosci}."
)
lancuch_nazwa = LLMChain(llm=llm, prompt=prompt_nazwa)

# Łańcuch 2: Tworzenie hasła reklamowego dla wygenerowanej nazwy
# Zauważ, że `input_variables` to 'nazwa_firmy' - to będzie wyjście z `lancuch_nazwa`
prompt_haslo = PromptTemplate(
    input_variables=["nazwa_firmy"],
    template="Stwórz krótkie, chwytliwe hasło reklamowe dla firmy o nazwie: {nazwa_firmy}"
)
lancuch_haslo = LLMChain(llm=llm, prompt=prompt_haslo)

# Łączymy łańcuchy w prostą sekwencję
# `verbose=True` to bardzo przydatna opcja, która pokazuje w konsoli, co dzieje się na każdym etapie łańcucha!
sekwencja_prosta = SimpleSequentialChain(chains=[lancuch_nazwa, lancuch_haslo], verbose=True)

# Uruchamiamy całą sekwencję z jednym początkowym wejściem
print("\n--- Przykład SimpleSequentialChain ---")
rodzaj_biznesu = "sprzedażą wegańskich lodów rzemieślniczych"
wynik_koncowy = sekwencja_prosta.invoke(rodzaj_biznesu)

print(f"\nRodzaj działalności: {rodzaj_biznesu}")
print(f"Finalny wynik (hasło reklamowe): {wynik_koncowy['output'].strip()}")


# 3. `SequentialChain` – Zaawansowane sekwencje z wieloma wejściami/wyjściami
#
# `SimpleSequentialChain` jest świetny, ale ma ograniczenie: co, jeśli drugi łańcuch potrzebuje więcej informacji
# niż tylko wynik poprzedniego? Na przykład, co jeśli do stworzenia hasła reklamowego chcemy użyć
# ZARÓWNO wygenerowanej nazwy, JAK I oryginalnego opisu działalności?
#
# Tu z pomocą przychodzi `SequentialChain`.
#
# Kluczowe cechy:
#     * Może obsługiwać wiele wejść początkowych.
#     * Może przekazywać wiele zmiennych między łańcuchami.
#     * Pozwala na dostęp do wyników pośrednich.
#
# Aby go użyć, musimy jawnie zdefiniować zmienne wejściowe (`input_variables`) i wyjściowe (`output_variables`) dla każdego łańcucha.

# --- Przykład 2: SequentialChain ---
from langchain.chains import SequentialChain

# Łańcuch 1: Generowanie tytułu dla artykułu na blogu
prompt_tytul = PromptTemplate.from_template(
    "Napisz chwytliwy tytuł dla artykułu na blogu o temacie: {temat}."
)
# Definiujemy, że wyjście z tego łańcucha będzie dostępne pod kluczem 'tytul'
lancuch_tytul = LLMChain(llm=llm, prompt=prompt_tytul, output_key="tytul")

# Łańcuch 2: Pisanie wstępu do artykułu
# Ten łańcuch potrzebuje DWÓCH zmiennych: oryginalnego tematu i świeżo wygenerowanego tytułu
prompt_wstep = PromptTemplate.from_template(
    "Napisz krótki, angażujący akapit wprowadzający do artykułu o tytule '{tytul}', który dotyczy tematu: {temat}."
)
# Wyjście z tego łańcucha nazwiemy 'wstep'
lancuch_wstep = LLMChain(llm=llm, prompt=prompt_wstep, output_key="wstep")

# Łączymy łańcuchy w zaawansowaną sekwencję
sekwencja_zlozona = SequentialChain(
    chains=[lancuch_tytul, lancuch_wstep],
    input_variables=["temat"],
    # Określamy, jakie zmienne chcemy otrzymać na końcu całego procesu
    output_variables=["tytul", "wstep"],
    verbose=True
)

# Uruchamiamy sekwencję
print("\n\n--- Przykład SequentialChain ---")
temat_artykulu = "korzyści płynące z regularnej medytacji"
wynik_zlozony = sekwencja_zlozona.invoke({"temat": temat_artykulu})

print(f"\nOryginalny temat: {temat_artykulu}")
print("-" * 30)
print(f"Wygenerowany tytuł: {wynik_zlozony['tytul'].strip()}")
print(f"Wygenerowany wstęp: {wynik_zlozony['wstep'].strip()}")

#
# 4. Podsumowanie
#
# Opanowanie łączenia łańcuchów to fundamentalna umiejętność w pracy z LangChain. Pozwala tworzyć
# znacznie bardziej zaawansowane i niezawodne aplikacje.
#
# Najważniejsze do zapamiętania:
#
#     * Rozbijaj złożone problemy na mniejsze, sekwencyjne kroki.
#     * Użyj `SimpleSequentialChain` do prostych zadań typu "wyjście A -> wejście B".
#     * Użyj `SequentialChain` do bardziej złożonych przepływów, gdy potrzebujesz zarządzać wieloma zmiennymi wejściowymi i wyjściowymi.
#     * Pamiętaj o `output_key` w `LLMChain`, gdy budujesz `SequentialChain`, aby poprawnie nazwać zmienne.
#     * Korzystaj z `verbose=True` podczas tworzenia i debugowania łańcuchów, aby dokładnie widzieć, co się dzieje "pod maską".
#
# W kolejnych lekcjach zobaczymy, jak do naszych łańcuchów dołączyć pamięć i zewnętrzne narzędzia.