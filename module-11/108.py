# Moduł 11, Lekcja 108: Budowanie portfolio AI

"""
Witaj w warsztatowej lekcji, w której zbudujemy Twoją najważniejszą wizytówkę
jako AI Engineera – profesjonalne portfolio na GitHubie.

W poprzedniej lekcji mówiliśmy, DLACZEGO portfolio jest kluczowe.
Dzisiaj skupimy się na tym, JAK je stworzyć, aby robiło piorunujące wrażenie.
To nie będzie tylko repozytorium z kodem. Zbudujemy kompletną historię
o Twoich umiejętnościach, procesie myślowym i zdolności do rozwiązywania problemów.

Celem tej lekcji jest przekształcenie Twojego projektu końcowego w perełkę portfolio,
która przyciągnie uwagę rekruterów i menedżerów technicznych.
Przejdziemy krok po kroku przez wszystkie elementy – od profilu na GitHubie
po perfekcyjny plik README.
"""

# ==============================================================================
# 1. Fundament: Twój Profil na GitHubie
# ==============================================================================

"""
Zanim ktoś wejdzie do Twojego repozytorium z projektem, zobaczy Twój profil.
To pierwsze wrażenie. Zadbaj o to, by było profesjonalne.

Twoja lista zadań do wykonania na profilu GitHub:
1.  **Zdjęcie profilowe:** Użyj profesjonalnego, wyraźnego zdjęcia (headshot). Unikaj awatarów z gier czy zdjęć z wakacji.
2.  **Imię i nazwisko:** Upewnij się, że są prawdziwe i spójne z Twoim CV.
3.  **Bio:** Krótki, ale treściwy opis. Użyj słów kluczowych.
    - Przykład: "Python Developer & AI Enthusiast specializing in building LLM-based applications with LangChain and FastAPI. Open to new opportunities."
4.  **Lokalizacja i linki:** Uzupełnij lokalizację (np. "Warsaw, Poland") i dodaj link do swojego profilu na LinkedIn.
5.  **Przypięte repozytoria (Pinned Repositories):** To najważniejsza część Twojego profilu!
    - Możesz przypiąć do 6 repozytoriów.
    - Upewnij się, że Twój projekt końcowy z tego kursu jest przypięty jako pierwszy z lewej.
    - Dodaj do niego krótki, chwytliwy opis.
"""

# ==============================================================================
# 2. Serce Portfolio: Repozytorium Twojego Projektu
# ==============================================================================

"""
Samo wrzucenie kodu na GitHuba to za mało. Twoje repozytorium musi być
przejrzyste, dobrze zorganizowane i łatwe do zrozumienia dla kogoś,
kto widzi je po raz pierwszy.

Elementy idealnego repozytorium projektu:
-   **Logiczna nazwa:** np. `ai-legal-assistant-rag` lub `rodo-expert-ai`. Nazwa powinna sugerować, co to za projekt.
-   **Krótki opis (About):** Jedno zdanie pod nazwą repozytorium, np. "A RAG-based AI assistant for answering questions about GDPR, built with FastAPI and LangChain."
-   **Tematy (Topics):** Dodaj tagi! Są one klikalne i pomagają w wyszukiwaniu.
    - Przykłady: `python`, `fastapi`, `langchain`, `rag`, `llm`, `openai`, `streamlit`, `portfolio-project`
-   **Plik `README.md`:** To absolutnie najważniejszy plik w repozytorium. Poświęcimy mu cały następny punkt.
-   **Plik `requirements.txt`:** Musi być kompletny, aby każdy mógł łatwo odtworzyć Twoje środowisko.
-   **Plik `.gitignore`:** Upewnij się, że ignoruje pliki `.env`, `__pycache__`, `.venv` i folder z bazą wektorową. To świadczy o profesjonalizmie.
-   **Czysta historia commitów:** Staraj się pisać opisowe commity (np. "feat: Add RAG chain logic" zamiast "update").
"""

# ==============================================================================
# 3. Perfekcyjny Plik README.md – Twoja Strona Lądowania
# ==============================================================================

"""
Plik README to historia Twojego projektu. To tutaj przekonujesz rekrutera,
że warto poświęcić czas na przejrzenie Twojego kodu. Musi być napisany
w formacie Markdown (.md).

Struktura idealnego pliku README:
"""

# --- POCZĄTEK SZABLONU README.md (skopiuj i dostosuj) ---
"""
# 🤖 RODO Ekspert AI

![Project Demo GIF](link_do_twojego_gifa_lub_zdjecia.gif)

## 📄 Opis projektu

RODO Ekspert AI to inteligentny asystent oparty na architekturze RAG (Retrieval-Augmented Generation),
zaprojektowany do precyzyjnego odpowiadania na pytania dotyczące Rozporządzenia o Ochronie Danych Osobowych (RODO).
Aplikacja wykorzystuje duży model językowy (LLM) do rozumienia pytań w języku naturalnym i generowania
odpowiedzi wyłącznie na podstawie treści oficjalnego dokumentu RODO.

Projekt ten został zrealizowany jako praca końcowa w ramach kursu AI Engineer i stanowi
pokaz praktycznych umiejętności w budowaniu i wdrażaniu nowoczesnych aplikacji AI.

## 🎯 Główne cele i rozwiązany problem

- **Problem:** Dostęp do wiedzy prawnej, takiej jak RODO, jest utrudniony dla osób nietechnicznych z powodu
  skomplikowanego języka i obszernej treści.
- **Rozwiązanie:** Stworzenie intuicyjnego interfejsu Q&A, który "tłumaczy" zawiłości prawne na zrozumiałe
  odpowiedzi, bazując na rzetelnym źródle.
- **Cel:** Zbudowanie od podstaw kompletnej aplikacji webowej AI, od przetwarzania danych, przez logikę backendu,
  aż po interfejs użytkownika.

## 🛠️ Architektura i wykorzystane technologie

Aplikacja składa się z trzech głównych komponentów:

1.  **Proces Ingestii Danych:** Skrypt w Pythonie, który wczytuje dokument PDF, dzieli go na fragmenty,
    generuje embeddingi i zapisuje je w bazie wektorowej ChromaDB.
2.  **Backend API:** Zbudowany w **FastAPI**, udostępnia endpoint `/ask`, który przyjmuje zapytania i zwraca odpowiedzi.
3.  **Frontend:** Prosty i interaktywny interfejs użytkownika stworzony w **Streamlit**, który komunikuje się z API.

**Stack technologiczny:**
- **Język:** Python 3.10+
- **Orkiestracja AI:** LangChain
- **Model LLM:** OpenAI GPT-3.5-Turbo / GPT-4o
- **Embeddingi:** OpenAI `text-embedding-ada-002`
- **Baza wektorowa:** ChromaDB
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Serwer:** Uvicorn

![Diagram Architektury](link_do_twojego_diagramu.png)
_Pro tip: Stwórz prosty diagram w narzędziu takim jak diagrams.net (draw.io) i umieść go w repozytorium._

## 🚀 Jak uruchomić projekt lokalnie

1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/twoj-nick/twoj-projekt.git
    cd twoj-projekt
    ```
2.  **Stwórz i aktywuj wirtualne środowisko:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate   # Windows
    ```
3.  **Zainstaluj zależności:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Skonfiguruj klucz API:**
    - Stwórz plik `.env` w głównym folderze projektu.
    - Dodaj do niego swój klucz: `OPENAI_API_KEY="sk-..."`

5.  **Przygotuj bazę wiedzy:**
    - Umieść plik `rodo_pl.pdf` w folderze `data/`.
    - Uruchom skrypt do ingestii danych:
    ```bash
    python app/ingest_data.py
    ```

6.  **Uruchom serwer API:**
    ```bash
    uvicorn app.main:app --reload
    ```
    Serwer będzie dostępny pod adresem `http://127.0.0.1:8000`.

7.  **Uruchom interfejs użytkownika:**
    - Otwórz drugi terminal i aktywuj to samo środowisko wirtualne.
    - Uruchom aplikację Streamlit:
    ```bash
    streamlit run ui/app_ui.py
    ```
    Interfejs będzie dostępny w przeglądarce pod adresem wskazanym w terminalu.

## 💡 Wyzwania i wnioski

Podczas realizacji projektu napotkałem kilka kluczowych wyzwań:
- **Optymalizacja promptów:** Znalezienie idealnego balansu w instrukcjach dla modelu, aby zapewnić wierność odpowiedzi
  i jednocześnie unikać zbyt "sztywnych" lub nienaturalnych sformułowań.
- **Dzielenie dokumentu (Chunking):** Eksperymentowanie z rozmiarem i nakładaniem się fragmentów tekstu, aby
  zmaksymalizować trafność odnajdywanego kontekstu bez utraty ważnych informacji.
- **Zapewnienie braku "halucynacji":** Wdrożenie ścisłych reguł w prompcie, aby model odmawiał odpowiedzi
  na pytania wykraczające poza zakres dokumentu RODO.

## 📈 Możliwe dalsze kierunki rozwoju

- Dodanie obsługi wielu dokumentów jednocześnie.
- Implementacja historii czatu dla bardziej kontekstowych konwersacji.
- Zapakowanie aplikacji do kontenera Docker w celu ułatwienia wdrożenia.
- Wdrożenie aplikacji na platformie chmurowej (np. AWS, Heroku).
"""
# --- KONIEC SZABLONU README.md ---

# ==============================================================================
# 4. Efekt "WOW" – Wizualizacje
# ==============================================================================

"""
Ludzie są wzrokowcami. Dobrze przygotowane repozytorium zyskuje 100 punktów,
jeśli zawiera elementy wizualne.

1.  **GIF Demonstracyjny:** To najlepszy sposób, aby w kilka sekund pokazać, jak działa Twoja aplikacja.
    - Użyj darmowego narzędzia (np. ScreenToGif, GIPHY Capture, Kap) do nagrania krótkiego filmu
      z interakcji z Twoją aplikacją Streamlit (zadajesz pytanie, otrzymujesz odpowiedź).
    - Zapisz go jako plik `.gif` i umieść w głównym folderze repozytorium.
    - Podlinkuj go na samej górze pliku README.

2.  **Diagram Architektury:**
    - Narysuj prosty schemat przepływu danych w Twojej aplikacji (np. Użytkownik -> Streamlit -> FastAPI -> LangChain -> LLM -> Odpowiedź).
    - Użyj darmowego narzędzia online, np. `diagrams.net` (dawniej `draw.io`).
    - Zapisz diagram jako plik `.png`, umieść w repozytorium i podlinkuj w README.
    - To pokazuje, że nie tylko piszesz kod, ale też myślisz jak architekt systemów.
"""

# ==============================================================================
# Podsumowanie i Następne Kroki
# ==============================================================================

"""
Twoje portfolio na GitHubie jest gotowe. To już nie jest tylko zbiór plików,
ale profesjonalna prezentacja Twoich umiejętności, która opowiada historię
o Twojej drodze od pomysłu do działającego produktu.

Twój plan działania:
1.  Dopracuj swój publiczny profil na GitHubie.
2.  Stwórz nowe, czyste repozytorium dla swojego projektu.
3.  Wypchnij tam swój kod, dbając o `.gitignore` i `requirements.txt`.
4.  Skorzystaj z szablonu, aby stworzyć wyczerpujący plik README.md.
5.  Nagraj GIF-a i narysuj diagram architektury, aby wzbogacić swoje README.
6.  Przypnij to repozytorium do swojego profilu.

Teraz jesteś w pełni gotowy, aby z dumą umieszczać link do swojego GitHuba
w CV, na LinkedIn i w wiadomościach do rekruterów.

W ostatniej lekcji tego modułu porozmawiamy o tym, co dalej – jak utrzymać tempo
i kontynuować rozwój w dynamicznym świecie AI, aby Twoje umiejętności
były zawsze aktualne.
"""