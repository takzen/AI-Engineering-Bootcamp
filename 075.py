# Moduł 8, Punkt 75: Tworzenie testów jednostkowych dla aplikacji AI
#
#
#
# Przez cały ten kurs skupialiśmy się na budowie potężnych aplikacji. Nauczyliśmy się je monitorować
# i debugować, gdy już działają. Ale jak możemy zapewnić ich jakość **zanim** trafią na produkcję?
# Jak możemy zautomatyzować proces sprawdzania, czy nasze zmiany nie zepsuły czegoś, co wcześniej działało?
#
# Odpowiedzią jest **testowanie jednostkowe (unit testing)** – fundamentalna praktyka w inżynierii
# oprogramowania, którą musimy zaadaptować do unikalnych wyzwań świata LLM. W tej lekcji
# zobaczymy, jak pisać i uruchamiać testy dla naszych pipeline'ów AI.
#
# 1. Wyzwanie: Jak testować coś, co jest niedeterministyczne?
#
# Tradycyjny test jednostkowy jest prosty: `assert funkcja(2) == 4`. Sprawdzamy, czy dla danego
# wejścia otrzymujemy **dokładnie** to samo, oczekiwane wyjście.
#
# W przypadku LLM jest to prawie niemożliwe. Nawet przy `temperaturze=0`, model może zwrócić
# odpowiedź z drobnymi różnicami w sformułowaniu ("Stolicą Polski jest Warszawa." vs "Warszawa jest
# stolicą Polski."). Asercja `==` zawiedzie.
#
# Musimy więc zmienić nasze podejście. Zamiast testować **dokładną treść**, będziemy testować
# **cechy i strukturę** odpowiedzi.
#
# 2. Kluczowe strategie testowania jednostkowego dla AI
#
# Oto kilka praktycznych strategii, które możemy zastosować, używając popularnych frameworków
# do testowania, takich jak `pytest`.
#
# **Strategia 1: Mockowanie wywołań LLM**
# To podstawowa i najważniejsza technika. Podczas testów jednostkowych **nie chcemy faktycznie
# wywoływać API OpenAI**. Jest to powolne, kosztowne i niedeterministyczne. Zamiast tego,
# "udajemy" (mockujemy) odpowiedź modelu.
#
# *   **Jak to działa?**: Używamy bibliotek takich jak `unittest.mock` w Pythonie, aby "podmienić"
#     metodę `llm.invoke()` tak, by zamiast wysyłać zapytanie do API, zwracała z góry
#     zdefiniowaną, stałą odpowiedź.
# *   **Co testujemy?**: W ten sposób nie testujemy samego LLM (zakładamy, że OpenAI wie, jak go
#     zbudować), ale testujemy **naszą logikę dookoła niego**. Sprawdzamy, czy nasz łańcuch
#     poprawnie formatuje prompt, czy poprawnie parsuje odpowiedź, czy poprawnie wywołuje
#     kolejne kroki.
#
# **Strategia 2: Testowanie struktury i walidacja (zamiast równości)**
# Skoro nie możemy sprawdzać dokładnej treści, sprawdzajmy jej właściwości.
#
# *   **Czy odpowiedź jest poprawnym JSON-em?**: Jeśli nasz łańcuch ma zwracać JSON, test może
#     polegać na próbie sparsowania odpowiedzi za pomocą `json.loads()`.
# *   **Czy odpowiedź zawiera kluczowe słowa?**: Możemy sprawdzać, czy w odpowiedzi znajdują się
#     oczekiwane frazy (`assert "Paryż" in odpowiedz`).
# *   **Czy odpowiedź pasuje do wzorca (Regex)?**: Jeśli oczekujemy odpowiedzi w określonym
#     formacie (np. listy punktowanej), możemy użyć wyrażeń regularnych do jej walidacji.
#
# **Strategia 3: Testowanie za pomocą ewaluatorów LangChain**
# LangChain dostarcza potężny zestaw gotowych **ewaluatorów**, które można wykorzystać wewnątrz
# testów `pytest`. Pozwalają one na bardziej zaawansowaną, semantyczną ocenę.
#
# *   **Jak to działa?**: W teście definiujesz wejście i oczekiwane wyjście (reference).
#     Następnie, po uzyskaniu rzeczywistej odpowiedzi z Twojego łańcucha, wywołujesz
#     ewaluator, który je porównuje.
# *   **Przykładowe ewaluatory**:
#     *   `EmbeddingDistanceEvalChain`: Sprawdza, czy semantyczne podobieństwo między
#         odpowiedzią a wzorcem jest wystarczająco wysokie.
#     *   `CriteriaEvalChain`: Używa innego LLM, aby ocenić, czy odpowiedź spełnia
#         określone kryteria (np. "czy jest zwięzła?", "czy jest nieszkodliwa?").
#
# 3. Praktyczny przykład: Testowanie prostego łańcucha z `pytest` i mockowaniem
#
# # Załóżmy, że mamy prosty łańcuch do generowania tytułów w pliku `title_generator.py`.
# # Poniżej znajduje się kod testów dla tego łańcucha.

# --- Kod aplikacji w pliku: title_generator.py ---
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_title_chain():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_template("Zaproponuj chwytliwy tytuł dla artykułu o: {topic}")
    chain = prompt | llm | StrOutputParser()
    return chain
# --- Koniec pliku title_generator.py ---


# --- Kod testów w pliku: test_title_generator.py ---
import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
# Załóżmy, że ta funkcja istnieje w pliku title_generator.py
# from title_generator import get_title_chain

# Używamy pytest.fixture, aby stworzyć "udawanego" LLM-a,
# którego będziemy mogli używać w naszych testach.
@pytest.fixture
def mocked_llm():
    mock = MagicMock()
    # Definiujemy, co ma zwrócić nasz udawany model, gdy zostanie wywołany
    mock.invoke.return_value = AIMessage(content="AI: Rewolucja w Twojej Kuchni")
    return mock

def test_title_chain_formats_prompt_correctly(mocked_llm):
    # Tworzymy łańcuch, ale "wstrzykujemy" do niego nasz udawany model.
    # W bardziej złożonej aplikacji zrobilibyśmy to przez modyfikację obiektu.
    # Dla uproszczenia, tutaj ręcznie odtwarzamy łańcuch z mockiem.
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_template("Zaproponuj chwytliwy tytuł dla artykułu o: {topic}")
    chain = prompt | mocked_llm | StrOutputParser()
    
    # Uruchamiamy łańcuch
    topic = "gotowanie z pomocą AI"
    chain.invoke({"topic": topic})

    # NAJWAŻNIEJSZY TEST: Sprawdzamy, z jakimi danymi (promptem)
    # nasz udawany model został faktycznie wywołany.
    # To testuje całą logikę formatowania promptu, która dzieje się przed LLM.
    call_args = mocked_llm.invoke.call_args
    prompt_value = call_args.args[0]
    
    # Sprawdzamy, czy sformatowany prompt zawiera nasz temat
    assert topic in prompt_value.to_string()
    # Sprawdzamy, czy prompt ma poprawną strukturę
    assert "Zaproponuj chwytliwy tytuł" in prompt_value.to_string()

def test_title_chain_returns_string_content(mocked_llm):
    # Podobnie jak wyżej, tworzymy łańcuch z mockiem
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    
    prompt = ChatPromptTemplate.from_template("Zaproponuj chwytliwy tytuł dla artykułu o: {topic}")
    chain = prompt | mocked_llm | StrOutputParser()

    # Uruchamiamy łańcuch i sprawdzamy wynik
    result = chain.invoke({"topic": "dowolny temat"})

    # Sprawdzamy, czy wynik jest stringiem i czy jest to treść naszej "udawanej" odpowiedzi
    assert isinstance(result, str)
    assert result == "AI: Rewolucja w Twojej Kuchni"
# --- Koniec pliku test_title_generator.py ---

# # Aby uruchomić te testy, w terminalu (w folderze z plikami) wystarczy wpisać komendę `pytest`.
#
# 4. Podsumowanie
#
# # Testowanie jednostkowe w AI to nie testowanie samego modelu, ale **testowanie logiki
# # i architektury, którą budujemy wokół niego**. To kluczowy element zapewniania jakości
# # i stabilności naszych aplikacji.
#
# # Najważniejsze do zapamiętania:
#
# #     1. **Mockuj wywołania LLM**: Unikaj prawdziwych wywołań API w testach jednostkowych.
# #        Testuj swoją logikę, a nie zewnętrzną usługę.
# #     2. **Testuj strukturę, nie treść**: Sprawdzaj formaty (JSON, lista), obecność
# #        kluczowych słów, zgodność z wzorcami, a nie dokładną równość stringów.
# #     3. **Weryfikuj wejścia do komponentów**: Najcenniejszy test to sprawdzenie, czy dane
# #        wejściowe do kluczowych komponentów (jak LLM) są poprawnie sformułowane.
# #     4. **Integruj z CI/CD**: Zautomatyzowane testy powinny być częścią Twojego procesu
# #        ciągłej integracji. Każda zmiana w kodzie powinna automatycznie uruchamiać zestaw
# #        testów, aby natychmiast wykryć ewentualne regresje.
#
# # Wprowadzając te praktyki, zyskujesz pewność, że Twoja aplikacja AI jest nie tylko
# # inteligentna, ale także solidna, niezawodna i gotowa na dalszy rozwój.