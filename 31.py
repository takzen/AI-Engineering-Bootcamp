# Moduł 5, Punkt 31: Wprowadzenie do LangChain i jego architektury
#
#
#
# Witaj w świecie aplikacji opartych o Duże Modele Językowe (LLM)! Do tej pory wiesz już, jak komunikować się z modelem
# za pomocą API. LangChain to krok dalej – to potężny framework (biblioteka i zbiór narzędzi), który drastycznie
# upraszcza budowanie złożonych aplikacji wykorzystujących LLM, takich jak chatboty, systemy Q&A na własnych
# dokumentach, agenci i wiele innych.
#
# Pomyśl o LangChain jak o zestawie klocków Lego dla programistów AI. Zamiast budować wszystko od zera,
# dostajesz gotowe, przetestowane komponenty, które możesz ze sobą łączyć.
#
# 1. Czym jest LangChain i jaki problem rozwiązuje?
#
# Duży Model Językowy (jak np. GPT-4) sam w sobie jest niesamowity, ale ma ograniczenia:
#
#     * Nie zna "świata zewnętrznego": Nie ma dostępu do aktualnych informacji, Twoich prywatnych plików czy firmowych baz danych.
#     * Nie ma "pamięci" (poza oknem kontekstowym): Każde zapytanie jest traktowane w izolacji.
#     * Nie potrafi samodzielnie korzystać z narzędzi: Nie może przeszukać internetu czy wykonać fragmentu kodu.
#
# LangChain rozwiązuje te problemy, dostarczając standardowy interfejs do "uzbrajania" modeli LLM w dodatkowe możliwości.
# Pozwala na tworzenie tzw. "łańcuchów" (chains), które łączą model językowy z zewnętrznymi źródłami danych i narzędziami.
#
# 2. Kluczowe zalety LangChain
#
#     * Komponentowość: Dostarcza modularne i łatwe w użyciu abstrakcje dla wszystkich części składowych aplikacji AI.
#     * Gotowe implementacje: Oferuje mnóstwo gotowych do użycia łańcuchów dla typowych zastosowań (np. podsumowywanie tekstu, odpowiadanie na pytania z dokumentów).
#     * Elastyczność: Chociaż oferuje gotowce, pozwala też na tworzenie w pełni niestandardowych łańcuchów.
#     * Ogromna społeczność: Jest to projekt open-source z bardzo aktywną społecznością, co oznacza świetną dokumentację i wiele przykładów.
#
# 3. Podstawowe komponenty architektury LangChain
#
# Zrozumienie tych sześciu filarów to klucz do efektywnego korzystania z LangChain.
#
#
# 3.1. Modele (Models) – "Mózg" operacji
#
# To opakowanie (wrapper) na różne modele językowe. LangChain standaryzuje sposób komunikacji z nimi.
#
#     * LLMs: Podstawowy interfejs dla modeli przyjmujących tekst na wejściu i zwracających tekst na wyjściu (np. GPT-3, text-davinci-003).
#     * Chat Models: Interfejs zoptymalizowany pod modele konwersacyjne (np. GPT-3.5-Turbo, GPT-4), gdzie wejściem jest lista wiadomości (system, human, AI).
#     * Text Embedding Models: Modele, które zamieniają tekst na wektor liczbowy (tzw. "embedding"), co jest kluczowe do porównywania i wyszukiwania semantycznego tekstów.
#
#
# 3.2. Szablony Zapytań (Prompts) – "Instrukcje" dla mózgu
#
# Zamiast ręcznie tworzyć zapytania do modelu, używamy szablonów. Pozwala to na parametryzację i ponowne użycie zapytań.
#
# Przykład szablonu
from langchain.prompts import PromptTemplate

szablon_tlumaczenia = PromptTemplate(
    input_variables=["tekst_wejsciowy", "jezyk_docelowy"],
    template="Przetłumacz poniższy tekst na język {jezyk_docelowy}: \n\n{tekst_wejsciowy}"
)

sformatowany_prompt = szablon_tlumaczenia.format(
    tekst_wejsciowy="Hello, world!",
    jezyk_docelowy="polski"
)
print("--- Przykład szablonu ---")
print(sformatowany_prompt)
# Wynik: Przetłumacz poniższy tekst na język polski: \n\nHello, world!
#
#
# 3.3. Łańcuchy (Chains) – "Linia produkcyjna"
#
# To serce LangChain. Łańcuchy pozwalają na sekwencyjne łączenie komponentów. Najprostszy łańcuch składa się
# z szablonu zapytania (Prompt) i modelu (LLM). Bardziej złożone mogą łączyć wiele łańcuchów lub łączyć je z innymi narzędziami.
#
# # Przykład pseudo-kodu dla łańcucha
# # llm = ... (instancja modelu)
# # prompt = ... (instancja szablonu)
# # lancuch = LLMChain(llm=llm, prompt=prompt)
# # lancuch.run("jakiś input")
#
#
# 3.4. Indeksy (Indexes) – "Pamięć" i "Wiedza"
#
# Indeksy służą do strukturyzacji danych w taki sposób, aby model LLM mógł z nich efektywnie korzystać. To one pozwalają
# na podłączenie do modelu WŁASNYCH dokumentów. Proces zazwyczaj wygląda tak:
#
#     1. Document Loaders: Wczytują dane z różnych źródeł (plik .txt, .pdf, strona www, baza danych).
#     2. Text Splitters: Dzielą duże dokumenty na mniejsze fragmenty (chunki), aby zmieściły się w oknie kontekstowym modelu.
#     3. Vector Stores: Tworzą "embeddingi" (wektory liczbowe) dla każdego fragmentu i przechowują je w specjalnej bazie danych (wektorowej), która pozwala na błyskawiczne wyszukiwanie semantyczne.
#     4. Retrievers: To interfejs, który na podstawie zapytania użytkownika potrafi odnaleźć najbardziej pasujące fragmenty tekstu w bazie wektorowej.
#
#
# 3.5. Pamięć (Memory) – "Pamięć krótkotrwała"
#
# Komponenty pamięci pozwalają łańcuchom i agentom "pamiętać" poprzednie interakcje. Dzięki temu chatbot może
# odnosić się do wcześniejszych części rozmowy. LangChain oferuje różne strategie pamięci (np. przechowywanie
# całej konwersacji, przechowywanie podsumowania).
#
#
# 3.6. Agenci (Agents) – "Samodzielny pracownik"
#
# To najbardziej zaawansowany koncept. Agent wykorzystuje model LLM do podejmowania decyzji. Na podstawie zapytania
# użytkownika, agent decyduje, jakiego narzędzia (Tool) użyć. Narzędziem może być wyszukiwarka Google, kalkulator,
# interpreter Pythona, a nawet inny łańcuch. Agent działa w pętli: myśli, wybiera narzędzie, wykonuje akcję, obserwuje
# wynik i na tej podstawie planuje kolejny krok – aż do rozwiązania problemu.
#
#
# 4. Praktyczny przykład: Twój pierwszy łańcuch (Chain)
#
# Zobaczmy, jak te klocki łączą się w praktyce. Stworzymy prosty łańcuch, który będzie wymyślał nazwę dla firmy
# na podstawie opisu jej działalności.
#
# Krok 1: Instalacja niezbędnych bibliotek (wykonaj w terminalu)
# pip install langchain langchain-openai
#
# Krok 2: Konfiguracja
import os

# WAŻNE: Nigdy nie umieszczaj klucza API bezpośrednio w kodzie.
# Poniższy kod oczekuje, że ustawisz zmienną środowiskową o nazwie OPENAI_API_KEY.
# Możesz to zrobić w systemie operacyjnym lub tymczasowo, odkomentowując i uzupełniając poniższą linię:
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

# Sprawdzenie, czy klucz API jest ustawiony
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Zmienna środowiskowa OPENAI_API_KEY nie została ustawiona.")
    print("Aby uruchomić ten kod, ustaw swój klucz API OpenAI.")
    # Zakończ działanie, jeśli klucz nie jest dostępny
    exit()

# Krok 3: Załadowanie komponentów
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Komponent 1: Model (LLM)
# `temperature` kontroluje kreatywność modelu (0.0 = bardzo przewidywalny, 1.0 = bardzo kreatywny)
llm = OpenAI(temperature=0.7)

# Komponent 2: Szablon zapytania (Prompt)
szablon_nazwy_firmy = PromptTemplate(
    input_variables=["rodzaj_dzialalnosci"],
    template="Zaproponuj jedną, kreatywną nazwę dla firmy, która zajmuje się {rodzaj_dzialalnosci}."
)

# Komponent 3: Łańcuch (Chain) - łączymy model z szablonem
lancuch_nazw = LLMChain(llm=llm, prompt=szablon_nazwy_firmy)

# Krok 4: Uruchomienie łańcucha
rodzaj_biznesu = "sprzedażą ekologicznych kaw i ręcznie robionych kubków"
sugerowana_nazwa = lancuch_nazw.invoke({"rodzaj_dzialalnosci": rodzaj_biznesu})

print("\n--- Praktyczny przykład łańcucha ---")
print(f"Rodzaj działalności: {rodzaj_biznesu}")
print(f"Sugerowana nazwa od AI: {sugerowana_nazwa['text'].strip()}")

# Przykładowy wynik:
# Sugerowana nazwa od AI: Ziarno i Glina
#
#
# 5. Podsumowanie
#
# Gratulacje! Właśnie poznałeś fundamenty, na których opiera się cały ekosystem LangChain.
#
# Najważniejsze do zapamiętania:
#
#     * LangChain to framework do budowania aplikacji zasilanych przez LLM.
#     * Jego siła leży w modułowych komponentach, które można ze sobą łączyć.
#     * Model to "mózg", Prompt to "instrukcja", a Chain to "linia produkcyjna", która je łączy.
#     * Indeksy i retrievery pozwalają modelom korzystać z Twoich własnych danych.
#     * Agenci to zaawansowana koncepcja, gdzie LLM sam decyduje, jakich narzędzi użyć do rozwiązania problemu.
#
# Opanowanie tych podstaw pozwoli Ci przejść do budowania znacznie bardziej złożonych i użytecznych
# aplikacji w kolejnych lekcjach. Czas na eksperymenty!