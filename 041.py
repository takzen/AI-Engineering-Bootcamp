# Moduł 5, Punkt 41: Tworzenie modeli rekomendacyjnych w LangChain
#
#
#
# Systemy rekomendacyjne są wszędzie – od Netflixa sugerującego filmy, po Amazon polecający produkty.
# Tradycyjnie buduje się je w oparciu o algorytmy takie jak filtrowanie kolaboracyjne (użytkownicy podobni do Ciebie
# polubili też...) czy filtrowanie oparte na treści (ten film to thriller, więc polubisz też inne thrillery).
#
# LangChain i Duże Modele Językowe wprowadzają zupełnie nowe, potężne podejście do rekomendacji,
# oparte na **głębokim rozumieniu języka naturalnego i zdolności do rozumowania**.
#
# 1. Czym jest "rekomendacja" w kontekście LLM?
#
# W świecie LLM rekomendacja przestaje być tylko dopasowywaniem wzorców. Staje się **dialogiem i rozumowaniem**.
# Użytkownik nie musi już klikać w produkty, aby system się go "nauczył". Może po prostu opisać, czego szuka,
# w bardzo abstrakcyjny sposób:
#
#     * "Szukam książki, która ma klimat podobny do filmu 'Blade Runner', ale dzieje się w świecie fantasy."
#     * "Poleć mi jakiś podcast o technologii, ale prowadzony w lekki i zabawny sposób, idealny na dojazdy do pracy."
#     * "Chcę kupić prezent dla taty, który lubi historię II Wojny Światowej i majsterkowanie."
#
# Tradycyjny system rekomendacyjny zawiódłby przy takich zapytaniach. System oparty o LLM jest w stanie
# zrozumieć te niuanse i zarekomendować coś trafnego.
#
# 2. Architektura systemu rekomendacyjnego z LangChain
#
# Najskuteczniejszy wzorzec budowy takiego systemu to **RAG (Retrieval-Augmented Generation)**, który już poznaliśmy.
# W kontekście rekomendacji proces wygląda następująco:
#
#     1. **Baza Wiedzy**: Posiadasz zbiór danych o swoich produktach/treściach (np. filmy, książki, artykuły)
#        z ich szczegółowymi opisami.
#     2. **Indeksowanie (Indexing)**: Za pomocą modelu embeddingowego tworzysz wektory liczbowe dla opisów
#        każdego z Twoich produktów i umieszczasz je w bazie wektorowej. To jest Twoja "pamięć długoterminowa" o ofercie.
#     3. **Wyszukiwanie (Retrieval)**: Gdy użytkownik wpisuje swoje zapytanie (np. "smutny film o przyjaźni"),
#        system zamienia to zapytanie na wektor i wyszukuje w bazie wektorowej N najbardziej podobnych semantycznie produktów.
#     4. **Generowanie Rekomendacji (Generation)**: Najbardziej pasujące produkty (np. 5 filmów) są przekazywane
#        wraz z oryginalnym zapytaniem użytkownika do LLM-a. Prompt instruuje model: "Biorąc pod uwagę prośbę
#        użytkownika i te oto filmy, wybierz 3 najlepsze i krótko uzasadnij, dlaczego będą mu się podobać".
#
# Ten ostatni krok to magia – LLM nie tylko wybiera, ale też **tworzy spersonalizowane uzasadnienie**,
# co znacznie zwiększa zaufanie i trafność rekomendacji.
#
# 3. Praktyczny przykład: Rekomendacja filmów na podstawie opisu
#
# Aby uprościć przykład i skupić się na kluczowym etapie generowania, pominiemy krok z bazą wektorową.
# Zamiast tego przekażemy listę dostępnych opcji bezpośrednio w prompcie. To podejście działa dla małych zbiorów danych.
#
# Krok 1: Instalacja i konfiguracja
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 2: Przygotowanie danych i komponentów
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# Nasza uproszczona "baza danych" filmów
baza_filmow = [
    {"tytul": "Incepcja", "opis": "Thriller science-fiction o złodziejach, którzy kradną informacje, wchodząc do snów innych ludzi. Złożona fabuła, spektakularne efekty wizualne."},
    {"tytul": "Skazani na Shawshank", "opis": "Dramat o bankierze niesłusznie skazanym na dożywocie, który przez lata zachowuje nadzieję i godność. Opowieść o przyjaźni i przetrwaniu."},
    {"tytul": "Władca Pierścieni: Drużyna Pierścienia", "opis": "Epicki film fantasy o hobbicie, który musi zniszczyć potężny pierścień, aby uratować świat przed siłami zła. Magia, bitwy i niezwykła podróż."},
    {"tytul": "Blade Runner 2049", "opis": "Mroczny, klimatyczny film neo-noir science-fiction o poszukiwaniu prawdy w futurystycznym świecie. Stawia pytania o naturę człowieczeństwa. Powolne tempo, wizualne arcydzieło."},
    {"tytul": "Coco", "opis": "Wzruszająca animacja o chłopcu, który wyrusza w podróż do Krainy Umarłych, aby odkryć tajemnicę swojej rodziny. Piękna opowieść o muzyce, rodzinie i pamięci."}
]

# Formatujemy naszą bazę do czytelnego dla LLM stringa
dostepne_filmy_str = "\n".join([f"- Tytuł: {f['tytul']}\n  Opis: {f['opis']}" for f in baza_filmow])

# Kluczowy element - szablon promptu, który instruuje model, jak ma rozumować
szablon_rekomendacji = ChatPromptTemplate.from_template(
    """Jesteś światowej klasy ekspertem od kina i osobistym doradcą filmowym.
Twoim zadaniem jest pomoc użytkownikowi w wyborze idealnego filmu na wieczór.

Na podstawie prośby użytkownika i poniższej listy dostępnych filmów, zarekomenduj 1-3 tytuły, które najlepiej pasują do jego preferencji.
Dla każdej rekomendacji, napisz jedno zdanie uzasadnienia, dlaczego ten konkretny film będzie dobrym wyborem.

Dostępne filmy:
{dostepne_filmy}

---
Prośba użytkownika: {zapytanie_uzytkownika}
---

Twoje rekomendacje:"""
)

# Tworzymy łańcuch rekomendacyjny
lancuch_rekomendacyjny = szablon_rekomendacji | llm | StrOutputParser()

# Krok 3: Uruchomienie systemu
zapytanie_uzytkownika = "Chciałbym obejrzeć coś z gatunku science-fiction, co jest wizualnie piękne i zmusza do głębszych przemyśleń."
print(f"Zapytanie użytkownika: {zapytanie_uzytkownika}\n")

# Wywołujemy łańcuch z przygotowanymi danymi
rekomendacje = lancuch_rekomendacyjny.invoke({
    "dostepne_filmy": dostepne_filmy_str,
    "zapytanie_uzytkownika": zapytanie_uzytkownika
})

print("--- Otrzymane Rekomendacje ---")
print(rekomendacje)

#
# 4. Kiedy używać LLM do rekomendacji?
#
#     * **Problem "zimnego startu"**: Gdy masz nowego użytkownika i brak o nim danych historycznych.
#     * **Złożone preferencje**: Gdy użytkownicy opisują swoje potrzeby językiem naturalnym.
#     * **Rekomendacje z uzasadnieniem**: Gdy chcesz nie tylko polecić produkt, ale też wyjaśnić, dlaczego jest on dobrym wyborem.
#     * **Systemy konwersacyjne**: Gdy chatbot ma dynamicznie dobierać rekomendacje w trakcie rozmowy.
#
# 5. Podsumowanie
#
# Wykorzystanie LLM-ów do rekomendacji to zmiana paradygmatu – przechodzimy od analizy kliknięć do analizy intencji.
#
# Najważniejsze do zapamiętania:
#
#     1. **Rekomendacje LLM opierają się na rozumieniu języka**, a nie tylko na statystyce.
#     2. Najlepszy wzorzec architektoniczny to **RAG**, który łączy wyszukiwanie w bazie wektorowej z rozumowaniem LLM.
#     3. **Dobry opis produktu/treści** jest kluczowy, ponieważ to na jego podstawie model dokonuje oceny.
#     4. Zdolność LLM-a do **generowania uzasadnień** jest jego unikalną "supermocą" w świecie systemów rekomendacyjnych.
#
# To potężne narzędzie pozwala tworzyć systemy, które są nie tylko trafne, ale także bardziej ludzkie i interaktywne.