# Moduł 5, Punkt 36: Jak obsługiwać API OpenAI w LangChain?
#
#
#
# Do tej pory używaliśmy modeli OpenAI w naszych łańcuchach i agentach. LangChain doskonale ukrywa
# całą złożoność bezpośredniej komunikacji z API, pozwalając nam skupić się na logice aplikacji.
#
# Jednak aby tworzyć naprawdę zaawansowane i zoptymalizowane rozwiązania, musimy wiedzieć, jak "dostroić"
# połączenie z modelem. To jak nauka regulacji silnika w samochodzie – pozwala wycisnąć z niego maksimum
# wydajności, kontrolować "spalanie" (koszty) i dostosować jego pracę do konkretnych warunków.
#
# 1. Dlaczego świadoma obsługa API jest kluczowa?
#
#     * **Kontrola kosztów**: Każde wywołanie API kosztuje. Parametry takie jak `max_tokens` pozwalają
#       bezpośrednio ograniczyć maksymalny koszt pojedynczego zapytania.
#     * **Kontrola zachowania**: Parametr `temperature` decyduje, czy model ma być kreatywny i "szalony",
#       czy raczej precyzyjny i trzymający się faktów.
#     * **Wybór odpowiedniego narzędzia**: OpenAI oferuje różne modele (GPT-3.5, GPT-4, GPT-4o, DALL-E).
#       Musisz wiedzieć, jak wybrać i skonfigurować ten właściwy dla Twojego zadania.
#     * **Optymalizacja wydajności**: Zaawansowane parametry pozwalają precyzyjniej sterować generowanym tekstem.
#
# 2. Kluczowe obiekty: `ChatOpenAI` vs `OpenAI`
#
# W LangChain spotkasz głównie dwa obiekty do interakcji z modelami OpenAI:
#
#     * `ChatOpenAI`: **To jest standard, którego powinieneś używać w 99% przypadków.** Jest przeznaczony
#       dla nowoczesnych modeli czatu (np. `gpt-4o`, `gpt-4`, `gpt-3.5-turbo`). Jego wejściem jest lista
#       wiadomości (System, Human, AI), co idealnie nadaje się do konwersacji i złożonych instrukcji.
#
#     * `OpenAI`: To starszy obiekt, przeznaczony dla modeli typu "completion" (uzupełnianie tekstu),
#       jak `gpt-3.5-turbo-instruct`. Przyjmuje na wejściu prosty ciąg znaków (string).
#       Dziś używany znacznie rzadziej.
#
# W tej lekcji skupimy się na `ChatOpenAI`.
#
# 3. Podstawowa konfiguracja połączenia
#
#     * **Klucz API (`api_key`)**: To najważniejszy element. LangChain domyślnie szuka klucza
#       w zmiennej środowiskowej o nazwie `OPENAI_API_KEY`. To najlepsza i najbezpieczniejsza praktyka.
#       **NIGDY nie umieszczaj klucza bezpośrednio w kodzie!**
#
#     * **Nazwa modelu (`model` lub `model_name`)**: Tutaj podajesz, którego modelu OpenAI chcesz użyć,
#       np. `"gpt-4o"`, `"gpt-4-turbo"`, `"gpt-3.5-turbo"`.
#
# 4. Dostrajanie modelu – najważniejsze parametry
#
# Te parametry przekazujesz podczas tworzenia obiektu `ChatOpenAI`.
#
#     * `temperature` (liczba od 0.0 do 2.0): Kontroluje "kreatywność" lub "przypadkowość" odpowiedzi.
#         - `0.0`: Maksymalnie deterministyczny. Idealny do zadań opartych na faktach, klasyfikacji, ekstrakcji danych.
#         - `0.7`: Dobry balans między kreatywnością a spójnością. Domyślna wartość.
#         - `1.0+`: Bardzo kreatywny. Dobry do brainstormingu, pisania poezji, ale może generować nonsensowne odpowiedzi.
#
#     * `max_tokens` (liczba całkowita): Maksymalna liczba tokenów (fragmentów słów), jaką model może wygenerować w odpowiedzi.
#       To **kluczowy parametr do kontroli kosztów** i zapobiegania zbyt długim odpowiedziom.
#
#     * `model_kwargs` (słownik): "Worek" na wszystkie inne, bardziej zaawansowane parametry, które
#       obsługuje API OpenAI, ale nie mają one swoich dedykowanych argumentów w klasie `ChatOpenAI`.
#       Przykłady: `top_p`, `frequency_penalty`, `presence_penalty`.
#
# 5. Praktyczny przykład: Porównanie parametrów w działaniu
#
# Zobaczmy, jak `temperature` i `max_tokens` wpływają na wynik.
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# --- Definiujemy dwa różne modele ---

# Model 1: Precyzyjny i "nudny" analityk
llm_precyzyjny = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.0
)

# Model 2: Kreatywny i "artystyczny" poeta
llm_kreatywny = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.9
)

# Model 3: "Gaduła" z limitem słów
llm_ograniczony = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=15 # Ustawiamy bardzo niski limit tokenów
)

# Tworzymy prosty szablon i łańcuch do testów
prompt = ChatPromptTemplate.from_template("Opisz słońce w jednym, obrazowym zdaniu dla {odbiorca}.")
lancuch = prompt | StrOutputParser()

# --- Testujemy modele ---
print("\n--- Test 1: Model precyzyjny (temperature=0.0) ---")
wynik1 = lancuch.invoke({"odbiorca": "ucznia podstawówki"}, config={"llm": llm_precyzyjny})
print(f"Odpowiedź: {wynik1}")

print("\n--- Test 2: Model kreatywny (temperature=0.9) ---")
wynik2 = lancuch.invoke({"odbiorca": "ucznia podstawówki"}, config={"llm": llm_kreatywny})
print(f"Odpowiedź: {wynik2}")

print("\n--- Test 3: Model z limitem tokenów (max_tokens=15) ---")
wynik3 = lancuch.invoke({"odbiorca": "ucznia podstawówki"}, config={"llm": llm_ograniczony})
print(f"Odpowiedź: {wynik3}")

#
# 6. Podsumowanie
#
# Świadome zarządzanie parametrami API to umiejętność, która odróżnia amatora od profesjonalisty.
# Pozwala tworzyć aplikacje, które są nie tylko funkcjonalne, ale także niezawodne i zoptymalizowane kosztowo.
#
# Najważniejsze do zapamiętania:
#
#     * **Zawsze używaj zmiennych środowiskowych** do przechowywania klucza API.
#     * Wybieraj `ChatOpenAI` dla nowoczesnych modeli i zadań konwersacyjnych.
#     * `temperature` to Twoje pokrętło "kreatywności" – używaj niskich wartości dla zadań analitycznych i wysokich dla kreatywnych.
#     * `max_tokens` to Twój "bezpiecznik" finansowy – ustawiaj go, aby kontrolować długość odpowiedzi i koszty.
#     * Pamiętaj o jawnym wyborze modelu (`model="..."`), aby korzystać z najnowszych i najlepszych dostępnych opcji.
#
# Eksperymentuj z tymi parametrami, aby zobaczyć, jak wpływają na Twoje własne łańcuchy i agentów!