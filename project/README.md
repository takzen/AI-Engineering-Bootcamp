# Finalny, dopracowany plik README.md dla Twojego GitHuba

# 🤖 RODO Ekspert AI

![Project Demo GIF](https://user-images.githubusercontent.com/username/repo/demo.gif)  <!-- Zastąp linkiem do własnego GIFa! -->

## 📄 Opis projektu

RODO Ekspert AI to inteligentny asystent oparty na architekturze RAG (Retrieval-Augmented Generation), zaprojektowany do precyzyjnego odpowiadania na pytania dotyczące Rozporządzenia o Ochronie Danych Osobowych (RODO). Aplikacja wykorzystuje duży model językowy (LLM) do rozumienia pytań w języku naturalnym i generowania odpowiedzi wyłącznie na podstawie treści oficjalnego dokumentu RODO.

Projekt ten został zrealizowany jako pokaz praktycznych umiejętności w budowaniu i wdrażaniu nowoczesnych aplikacji AI od podstaw.

## 🎯 Główne cele i rozwiązany problem

-   **Problem:** Dostęp do wiedzy prawnej, takiej jak RODO, jest utrudniony dla osób nietechnicznych z powodu skomplikowanego języka i obszernej treści.
-   **Rozwiązanie:** Stworzenie intuicyjnego interfejsu Q&A, który "tłumaczy" zawiłości prawne na zrozumiałe odpowiedzi, bazując na rzetelnym źródle.
-   **Cel:** Zbudowanie od podstaw kompletnej aplikacji webowej AI, od przetwarzania danych, przez logikę backendu, aż po interfejs użytkownika.

## 🛠️ Architektura i wykorzystane technologie

Aplikacja składa się z trzech głównych komponentów:

1.  **Proces Ingestii Danych:** Skrypt w Pythonie, który wczytuje dokument PDF, dzieli go na fragmenty, generuje embeddingi i zapisuje je w bazie wektorowej ChromaDB.
2.  **Backend API:** Zbudowany w **FastAPI**, udostępnia endpoint `/ask`, który przyjmuje zapytania i zwraca odpowiedzi.
3.  **Frontend:** Prosty i interaktywny interfejs użytkownika stworzony w **Streamlit**, który komunikuje się z API.

**Stack technologiczny:**
-   **Język:** Python 3.10+
-   **Orkiestracja AI:** LangChain
-   **Model LLM:** OpenAI GPT-3.5-Turbo
-   **Baza wektorowa:** ChromaDB
-   **Backend:** FastAPI
-   **Frontend:** Streamlit

## 🚀 Jak uruchomić projekt lokalnie

1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/twoj-nick/project_rodo_ai.git
    cd project_rodo_ai
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
    -   Skopiuj plik `.env.example` do nowego pliku `.env`.
    -   W pliku `.env` wklej swój klucz API od OpenAI.

5.  **Przygotuj bazę wiedzy:**
    -   Pobierz pełny tekst RODO w formacie PDF i umieść go w folderze `data/` pod nazwą `rodo_pl.pdf`.
    -   Uruchom skrypt do ingestii danych:
    ```bash
    python app/ingest_data.py
    ```

6.  **Uruchom serwer API (w pierwszym terminalu):**
    ```bash
    uvicorn app.main:app --reload
    ```
    Serwer będzie dostępny pod adresem `http://127.0.0.1:8000`.

7.  **Uruchom interfejs użytkownika (w drugim terminalu):**
    ```bash
    streamlit run ui/app_ui.py
    ```
    Interfejs otworzy się automatycznie w Twojej przeglądarce.

## 📈 Możliwe dalsze kierunki rozwoju

-   Dodanie obsługi wielu dokumentów jednocześnie.
-   Implementacja historii czatu dla bardziej kontekstowych konwersacji.
-   Zapakowanie aplikacji do kontenera Docker w celu ułatwienia wdrożenia.