# Moduł 8, Punkt 76: Analiza błędów promptów i optymalizacja wyników
#
#
#
# Dotarliśmy do sedna inżynierii AI. Możemy mieć najlepszą architekturę, najszybsze modele i
# perfekcyjnie zorganizowany graf, ale jeśli instrukcje, które przekazujemy do LLM, są
# nieprecyzyjne, niejasne lub mylące, cały system zawiedzie.
#
# **Prompt to kod źródłowy dla Dużego Modelu Językowego.**
#
# W tej lekcji nauczymy się, jak być lepszymi "programistami" dla LLM-ów. Zobaczymy, jak
# używać LangSmith do diagnozowania typowych błędów w promptach i jak je systematycznie
# poprawiać, aby uzyskać pożądane, niezawodne wyniki.
#
# 1. Dlaczego prompty zawodzą? Typowe "bugi" w instrukcjach
#
# Błąd w prompcie rzadko jest błędem składniowym. To znacznie bardziej subtelne problemy:
#
#     * **Niejasność (Ambiguity)**: Prosimy o "podsumowanie", ale nie precyzujemy, czy ma być
#       to podsumowanie dla eksperta, czy dla laika, w punktach czy w formie eseju.
#     * **Brak Kontekstu (Missing Context)**: Model otrzymuje zadanie, ale nie ma wystarczająco
#       dużo informacji, aby je dobrze wykonać.
#     * **Sprzeczne Instrukcje (Conflicting Instructions)**: W jednym prompcie prosimy model,
#       aby był "zwięzły i szczegółowy" jednocześnie.
#     * **Niezamierzony Bias (Unintended Bias)**: Sposób, w jaki formułujemy pytanie,
#       subtelnie sugeruje modelowi pożądaną odpowiedź.
#     * **Złe Formatowanie (Poor Formatting)**: Instrukcje są wymieszane z danymi wejściowymi
#       w sposób, który jest trudny do przetworzenia dla modelu.
#
# 2. LangSmith jako mikroskop do analizy promptów
#
# LangSmith jest niezastąpiony w diagnozowaniu tych problemów, ponieważ pozwala Ci zobaczyć
# **dokładnie to, co zobaczył model**.
#
#     * **Widoczność ostatecznego promptu**: W widoku śladu możesz zobaczyć w pełni wyrenderowany
#       prompt – z wstawioną historią konwersacji, pobranym kontekstem z bazy RAG i wszystkimi
#       innymi zmiennymi. To często ujawnia, że prompt wygląda zupełnie inaczej, niż zakładałeś.
#
#     * **Playground do iteracji**: To Twoje laboratorium. Możesz wziąć dowolny historyczny,
#       problematyczny prompt, otworzyć go w Playground, na żywo go modyfikować i natychmiast
#       uruchamiać ponownie, aby zobaczyć, czy Twoja poprawka działa. To skraca cykl
#       debugowania z minut do sekund.
#
# 3. "Książka kucharska" optymalizacji promptów
#
# Przeanalizujmy kilka typowych anty-wzorców i sposoby ich naprawy.
#
#     **Anty-wzorzec 1: Zbyt ogólne polecenie**
#
#     *   **Problem**: Model dostaje niejasne polecenie i "zgaduje", czego od niego oczekujemy.
#     *   **Zły prompt**:
"""
Podsumuj poniższy tekst.

Tekst: [długi artykuł o fotosyntezie]
"""
#     *   **Rozwiązanie**: Bądź ultra-precyzyjny. Użyj techniki "role-playing", zdefiniuj format
#         wyjściowy i określ grupę docelową.
#     *   **Dobry prompt**:
"""
Jesteś nauczycielem biologii. Twoim zadaniem jest podsumowanie poniższego tekstu dla ucznia liceum.
Stwórz zwięzłe podsumowanie w formie 3-5 kluczowych punktów. Używaj prostego, zrozumiałego języka.

Tekst: [długi artykuł o fotosyntezie]
"""
#
#     **Anty-wzorzec 2: Używanie negacji**
#
#     *   **Problem**: Modele często mają problem z instrukcjami negatywnymi ("nie rób...", "unikaj...").
#         Widzą kluczowe słowo i skupiają się na nim, często robiąc dokładnie to, czego zabroniliśmy.
#     *   **Zły prompt**:
"""
Opisz nasz nowy produkt. Nie wspominaj o cenie.
"""
#     *   **Rozwiązanie**: Formułuj instrukcje w sposób pozytywny. Zamiast mówić, czego ma nie robić,
#         powiedz, na czym ma się skupić.
#     *   **Dobry prompt**:
"""
Opisz nasz nowy produkt. Skup się wyłącznie na jego kluczowych funkcjach i korzyściach dla użytkownika.
"""
#
#     **Anty-wzorzec 3: Mieszanie instrukcji z danymi**
#
#     *   **Problem**: Modelowi trudno jest odróżnić, co jest jego instrukcją, a co danymi do przetworzenia,
#         jeśli są one wymieszane w jednym bloku tekstu.
#     *   **Zły prompt**:
"""
Przetłumacz na angielski to jest moje zadanie ten tekst: "Dzień dobry, świecie!".
"""
#     *   **Rozwiązanie**: Używaj wyraźnych separatorów (np. `---`, `###`) lub tagów w stylu XML,
#         aby jasno oddzielić instrukcje od danych.
#     *   **Dobry prompt**:
"""
Twoim zadaniem jest tłumaczenie tekstu na język angielski.
--- TEKST DO PRZETŁUMACZENIA ---
Dzień dobry, świecie!
--- TŁUMACZENIE ---
"""
#
# 4. Iteracyjny proces optymalizacji promptu
#
# Optymalizacja to nie jednorazowa czynność, ale ciągły cykl.
#
#     1.  **Obserwuj w LangSmith**: Znajdź w logach ślad z niezadowalającą odpowiedzią.
#     2.  **Analizuj prompt**: Otwórz krok LLM i dokładnie przeanalizuj ostateczny, wyrenderowany prompt.
#         Zidentyfikuj potencjalny anty-wzorzec.
#     3.  **Postaw hipotezę**: "Myślę, że problemem jest zbyt ogólne polecenie. Muszę dodać personę i format wyjściowy".
#     4.  **Eksperymentuj w Playground**: Otwórz ślad w Playground. Zmodyfikuj prompt zgodnie ze swoją
#         hipotezą i uruchom go ponownie. Powtarzaj, aż uzyskasz satysfakcjonujący wynik.
#     5.  **Wdróż i testuj regresję**: Zaktualizuj szablon promptu w swoim kodzie. Uruchom pełen zestaw
#         testów ewaluacyjnych, aby upewnić się, że poprawka nie zepsuła odpowiedzi dla innych przypadków.
#
# 5. Podsumowanie
#
# Inżynieria promptów (Prompt Engineering) to kluczowa umiejętność w erze AI. To połączenie
# nauki, sztuki i metodycznej pracy detektywistycznej.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Traktuj prompty jak kod**: Wymagają takiej samej staranności, refaktoryzacji i testowania.
#     2.  **Bądź precyzyjny i jednoznaczny**: Im mniej miejsca na interpretację zostawisz modelowi,
#         tym bardziej przewidywalne będą jego odpowiedzi.
#     3.  **Używaj formatowania i separatorów**: Pomóż modelowi zrozumieć strukturę Twojego zapytania.
#     4.  **LangSmith to Twoje IDE do promptów**: Używaj go do analizy, eksperymentowania i iteracji,
#         aby doskonalić swoje instrukcje w oparciu o twarde dane.
#
# Opanowanie tej sztuki pozwoli Ci w pełni wykorzystać potencjał Dużych Modeli Językowych i
# budować aplikacje, które są nie tylko inteligentne, ale także precyzyjne i niezawodne.