# Moduł 11, Lekcja 106: Testowanie i optymalizacja gotowej aplikacji

"""
Witaj w lekcji, która oddziela amatorów od profesjonalistów.
Stworzenie działającej aplikacji AI to jedno. Sprawienie, by działała dobrze,
niezawodnie i precyzyjnie – to zupełnie inna, wyższa szkoła jazdy.
To jest właśnie praca AI Engineera.

Do tej pory nasza aplikacja działa. Ale czy działa optymalnie?
- Czy zawsze udziela trafnych odpowiedzi?
- Czy nie "halucynuje", czyli nie wymyśla faktów?
- Czy możemy sprawić, by była szybsza lub tańsza w użyciu?

W tej lekcji skupimy się na trzech filarach doskonalenia naszej aplikacji:
1.  **Testowanie:** Jak systematycznie sprawdzać jakość odpowiedzi.
2.  **Optymalizacja:** Jakie "pokrętła" możemy regulować, aby poprawić działanie.
3.  **Ewaluacja:** Jak mierzyć, czy nasze zmiany przynoszą pożądany efekt.
"""

# ==============================================================================
# 1. Filozofia Testowania Aplikacji Opartych na LLM
# ==============================================================================

"""
Testowanie aplikacji z LLM różni się od testowania tradycyjnego oprogramowania.
Nie ma tu prostego "działa / nie działa". Odpowiedzi są generowane, a nie sztywno zdefiniowane.
Dlatego musimy testować pod kątem jakości, a nie tylko poprawności technicznej.

Kluczowe aspekty, które będziemy testować w naszym systemie RAG:
- **Trafność (Relevance):** Czy odpowiedź jest na temat i faktycznie odpowiada na pytanie użytkownika?
- **Wierność (Faithfulness):** Czy odpowiedź jest w 100% oparta na dostarczonym kontekście (fragmentach z RODO)? Czy nie dodaje informacji "od siebie"?
- **Odporność na "głupie" pytania:** Jak system reaguje na pytania niezwiązane z tematem lub próby "złamania" promptu?

Stworzymy zestaw pytań testowych, które pomogą nam ocenić te aspekty.
"""

# Stwórz w głównym folderze projektu nowy plik o nazwie `evaluation_suite.py`
# Będzie to nasz "poligon doświadczalny".

# --- Zawartość pliku evaluation_suite.py ---
from dotenv import load_dotenv
from app.core import get_qa_chain
import time

# Wczytujemy zmienne środowiskowe
load_dotenv()

# Definiujemy nasz zestaw pytań testowych
# Dobra praktyka to mieszanie pytań prostych, złożonych i "pułapek".
evaluation_questions = [
    # Pytania ogólne, na które odpowiedź powinna być w dokumencie
    "Co to jest RODO?",
    "Jakie są prawa osoby, której dane dotyczą?",
    "Kto to jest administrator danych?",
    # Pytania szczegółowe
    "Jaki jest maksymalny czas na odpowiedź na wniosek osoby fizycznej?",
    "Jakie są kary finansowe za nieprzestrzeganie RODO?",
    # Pytania, na które prawdopodobnie nie ma odpowiedzi (test wierności)
    "Jaka jest najlepsza firma wdrażająca RODO w Polsce?",
    "Czy RODO dotyczy danych osób zmarłych?",
    # Pytania "pułapki" (off-topic)
    "Jaka jest stolica Francji?",
    "Napisz wiersz o wiośnie.",
    # Pytania podchwytliwe, testujące głębsze zrozumienie
    "Czy mogę przetwarzać dane osobowe na podstawie zgody, jeśli osoba ma 15 lat?",
]

def run_evaluation():
    print("Uruchamiam zestaw testów ewaluacyjnych...")
    qa_chain = get_qa_chain()

    if not qa_chain:
        print("Nie udało się załadować łańcucha QA. Prerywam testy.")
        return

    for i, question in enumerate(evaluation_questions):
        print(f"\n--- Pytanie {i+1}/{len(evaluation_questions)} ---")
        print(f"Pytanie: {question}")
        
        start_time = time.time()
        result = qa_chain({"query": question})
        end_time = time.time()
        
        answer = result.get("result")
        source_documents = result.get("source_documents")

        print(f"\nOdpowiedź: {answer}")
        print(f"\nCzas odpowiedzi: {end_time - start_time:.2f} s")
        print(f"Liczba dokumentów źródłowych: {len(source_documents)}")
        # Możesz też dodać wyświetlanie treści dokumentów źródłowych dla głębszej analizy
        # for doc in source_documents:
        #     print(f"  - Źródło (str. {doc.metadata.get('page', '?')}): {doc.page_content[:100]}...")

    print("\n--- Zakończono zestaw testów ---")


if __name__ == "__main__":
    run_evaluation()
# ---------------------------------------------

"""
Uruchom ten skrypt z terminala i przeanalizuj wyniki.
"""
# python evaluation_suite.py

"""
Analizując odpowiedzi, zwróć uwagę na:
- Czy odpowiedzi na pytania niezwiązane z RODO są zgodne z instrukcją w prompcie (np. "Na podstawie... nie jestem w stanie odpowiedzieć")?
- Czy odpowiedzi na pytania szczegółowe są precyzyjne?
- Czy odpowiedzi na pytania "pułapki" nie ujawniają ogólnej wiedzy modelu, tylko trzymają się kontekstu?
"""

# ==============================================================================
# 2. Główne "Pokrętła" do Optymalizacji Systemu RAG
# ==============================================================================

"""
Załóżmy, że po testach widzisz pole do poprawy. Gdzie szukać optymalizacji?
W systemie RAG mamy kilka kluczowych miejsc, które możemy regulować.
"""

# --- Pokrętło 1: Inżynieria Promptu (Plik: app/core.py) ---
"""
To najpotężniejsze i najtańsze narzędzie. Zmiana kilku słów w prompcie może diametralnie
zmienić jakość odpowiedzi.

Co można tu zmienić w `PROMPT_TEMPLATE`?
- Dodać instrukcję, aby cytował numer artykułu, na którym się opiera.
- Zmienić "ton" odpowiedzi (np. "Odpowiadaj jak prawnik do laika", "Odpowiadaj zwięźle i w punktach").
- Wzmocnić negatywne ograniczenie: "ABSOLUTNIE NIE WOLNO CI używać wiedzy spoza dostarczonego Kontekstu."
"""

# --- Pokrętło 2: Parametry Retrievera (Plik: app/core.py) ---
"""
Retriever decyduje, jakie fragmenty wiedzy trafią do modelu. To drugie najważniejsze miejsce do optymalizacji.
W funkcji `get_qa_chain`, w linii `retriever = vector_store.as_retriever(...)`, możemy modyfikować:

- `search_kwargs={"k": N}`: Liczba fragmentów (chunków) do pobrania.
    - Zwiększenie `k` (np. do 5) daje modelowi więcej kontekstu, co może pomóc przy złożonych pytaniach,
      ale zwiększa koszt i może wprowadzić "szum informacyjny".
    - Zmniejszenie `k` (np. do 2) może poprawić precyzję przy prostych pytaniach, ale może pominąć ważny kontekst.

- `search_type`: Metoda wyszukiwania. Domyślnie jest to "similarity" (podobieństwo semantyczne).
  Można też użyć "mmr" (Maximum Marginal Relevance), która stara się pobierać fragmenty
  podobne do pytania, ale jednocześnie różnorodne między sobą.
  `retriever = vector_store.as_retriever(search_type="mmr")`
"""

# --- Pokrętło 3: Sposób Dzielenia Tekstu (Plik: app/ingest_data.py) ---
"""
To zmiana na niższym poziomie, która wymaga ponownej ingestii danych (`python app/ingest_data.py`).
W `RecursiveCharacterTextSplitter` możemy regulować:

- `chunk_size`: Wielkość każdego fragmentu tekstu.
    - Większe chunki (np. 2000) dają więcej kontekstu w jednym fragmencie, ale mogą być mniej precyzyjne.
    - Mniejsze chunki (np. 500) są bardziej "skupione" na jednym zagadnieniu, ale mogą rozdzielić zdanie w połowie.

- `chunk_overlap`: Jak dużo tekstu ma się nakładać między kolejnymi fragmentami.
    - Zwiększenie `overlap` (np. do 200) zmniejsza ryzyko, że ważne informacje zostaną przecięte na granicy chunków.
"""

# --- Pokrętło 4: Model Językowy (Plik: app/core.py) ---
"""
W linii `llm = ChatOpenAI(...)` możemy zmienić model.
- `model_name="gpt-4o"`: Użycie mocniejszego (i droższego) modelu może znacząco poprawić zdolność
  rozumowania i syntezy informacji z dostarczonych fragmentów.
- `temperature=X`: "Kreatywność" modelu. Dla aplikacji Q&A opartej na faktach, `temperature=0.0`
  jest najlepszym wyborem, ponieważ chcemy jak najbardziej deterministycznych i rzeczowych odpowiedzi.
"""

# ==============================================================================
# 3. Praktyczny Cykl Optymalizacyjny
# ==============================================================================

"""
Jak wygląda profesjonalny proces optymalizacji?
To iteracyjny cykl:

1.  **Uruchom testy bazowe:** Uruchom `evaluation_suite.py` na obecnych ustawieniach i zapisz wyniki (lub zrób zrzuty ekranu). To Twój punkt odniesienia.

2.  **Postaw hipotezę:** "Wydaje mi się, że odpowiedzi są zbyt ogólne. Zwiększenie `k` z 3 do 5 w retrieverze powinno dać modelowi więcej kontekstu i poprawić szczegółowość."

3.  **Wprowadź JEDNĄ zmianę:** Zmodyfikuj kod `app/core.py`, zmieniając `k=3` na `k=5`.

4.  **Uruchom testy ponownie:** Uruchom `evaluation_suite.py` jeszcze raz.

5.  **Porównaj wyniki:** Czy odpowiedzi faktycznie stały się lepsze? Czy nie pojawiły się nowe problemy (np. model się "gubi" w nadmiarze informacji)? Czy czas odpowiedzi 
znacząco się nie wydłużył?

6.  **Zdecyduj:**
    - Jeśli zmiana pomogła -> Zachowaj ją.
    - Jeśli zmiana pogorszyła -> Wróć do poprzedniej wersji.
    - Jeśli wynik jest niejednoznaczny -> Zapisz obserwacje i przetestuj inną hipotezę.

7.  **Powtórz cykl** z kolejną hipotezą (np. "A teraz spróbuję ulepszyć prompt...").

Pamiętaj: Zawsze zmieniaj tylko JEDEN parametr na raz! W przeciwnym razie nie będziesz wiedział, która zmiana spowodowała poprawę lub pogorszenie.
"""

# ==============================================================================
# Podsumowanie i Następne Kroki
# ==============================================================================

"""
Gratulacje! Przeszedłeś właśnie od roli "konstruktora" do roli "inżyniera-optymalizatora".
Nauczyłeś się, że budowa aplikacji AI to proces ciągłego doskonalenia.

Kluczowe wnioski z tej lekcji:
- Testowanie systemów LLM wymaga oceny jakościowej (trafność, wierność).
- Posiadasz zestaw "pokręteł" (prompt, retriever, chunking, model), którymi możesz regulować działanie systemu RAG.
- Optymalizacja to iteracyjny proces oparty na cyklu: hipoteza -> zmiana -> test -> ocena.

W ostatniej lekcji praktycznej tego modułu zajmiemy się czymś, co pozwoli pokazać
Twoją pracę światu – zbudujemy prosty, ale funkcjonalny interfejs graficzny w Streamlit.
Dzięki niemu każda osoba, nawet nietechniczna, będzie mogła skorzystać z Twojego "RODO Eksperta".
"""