# Moduł 8, Punkt 77: Automatyzacja testowania aplikacji LangChain
#
#
#
# Dotarliśmy do ostatniego, ale być może najważniejszego elementu w cyklu życia profesjonalnej
# aplikacji AI: **automatyzacji testowania**. Ręczne testowanie i debugowanie są niezbędne
# na etapie rozwoju, ale w świecie, gdzie aplikacje zmieniają się codziennie,
# potrzebujemy systemu, który będzie naszym niezmordowanym, automatycznym strażnikiem jakości.
#
# W tej lekcji połączymy wszystko, czego nauczyliśmy się o testowaniu i ewaluacji w LangSmith,
# z koncepcjami **Ciągłej Integracji / Ciągłego Wdrażania (CI/CD)**, aby stworzyć
# zautomatyzowany pipeline, który zapewnia, że każda zmiana w naszej aplikacji
# jest dokładnie sprawdzana, zanim trafi do użytkowników.
#
# 1. Problem: Manualne testowanie nie skaluje się
#
# Wyobraź sobie, że Twój zespół wprowadza 10 zmian dziennie do kodu aplikacji. Czy jesteś
# w stanie za każdym razem ręcznie:
#
#     * Przetestować dziesiątki kluczowych przypadków użycia?
#     * Sprawdzić, czy nowa zmiana nie zepsuła czegoś, co działało wcześniej (regresja)?
#     * Ocenić, czy jakość odpowiedzi nie uległa pogorszeniu?
#     * Zweryfikować, czy koszty i latencja nie wzrosły drastycznie?
#
# Oczywiście, że nie. To prosta droga do wypalenia i wprowadzania błędów na produkcję.
# Potrzebujemy automatyzacji.
#
# 2. Architektura zautomatyzowanego pipeline'u testowego
#
# Profesjonalny pipeline CI/CD dla aplikacji LangChain opiera się na kilku filarach,
# które współdziałają ze sobą. Proces ten jest zazwyczaj uruchamiany automatycznie
# po każdej zmianie w kodzie (np. po `git push`).
#
# **[Zmiana w kodzie (git push)] -> [1. Uruchomienie testów jednostkowych (pytest)] -> [2. Uruchomienie ewaluacji w LangSmith] -> [3. Wdrożenie (jeśli testy przejdą)]**
#
#     **Etap 1: Testy Jednostkowe (szybkie testy)**
#     *   **Cel**: Sprawdzenie "zdrowia" i poprawności strukturalnej kodu.
#     *   **Co robi?**: Uruchamia zestaw testów `pytest`, które, jak już wiemy, **mockują wywołania LLM**.
#         Sprawdzają one, czy prompty są poprawnie formatowane, czy dane są poprawnie parsowane,
#         czy logika warunkowa w grafie działa.
#     *   **Dlaczego jest pierwszy?**: Te testy są bardzo szybkie (trwają sekundy) i tanie (nie
#         używają API). Jeśli one zawiodą, nie ma sensu przechodzić do droższych etapów.
#
#     **Etap 2: Testy Ewaluacyjne (testy jakości)**
#     *   **Cel**: Sprawdzenie jakości i zachowania aplikacji w interakcji z prawdziwym LLM.
#     *   **Co robi?**: Uruchamia skrypt, który wykorzystuje SDK LangSmith do przeprowadzenia
#         automatycznej ewaluacji. Skrypt:
#         a) Pobiera zdefiniowane wcześniej zestawy danych (datasets) z LangSmith.
#         b) Uruchamia testowaną wersję aplikacji dla każdego przykładu z zestawu.
#         c) Używa ewaluatorów (np. oceny przez LLM, sprawdzania podobieństwa semantycznego),
#            aby ocenić każdą odpowiedź.
#     *   **Dlaczego jest drugi?**: Te testy są wolniejsze i droższe. Uruchamiamy je tylko,
#         gdy mamy pewność, że podstawowa logika kodu jest poprawna.
#
#     **Etap 3: Raportowanie i decyzja**
#     *   **Cel**: Podjęcie decyzji, czy zmiana może zostać wdrożona.
#     *   **Co robi?**: Skrypt CI/CD analizuje wyniki z obu etapów.
#         - Jeśli testy jednostkowe zawiodły, pipeline jest przerywany, a deweloper dostaje powiadomienie.
#         - Jeśli testy ewaluacyjne pokazują spadek jakości (np. średnia ocena poprawności spadła
#           poniżej 90%) lub znaczący wzrost kosztów/latencji, pipeline również jest przerywany.
#         - Tylko jeśli **wszystkie testy przejdą pomyślnie**, zmiana jest automatycznie łączona
#           z główną gałęzią kodu i wdrażana na produkcję.
#
# 3. Praktyczny przykład: Skrypt do uruchamiania ewaluacji
#
# Poniższy kod pokazuje, jak mógłby wyglądać skrypt Pythona, który jest częścią
# pipeline'u CI/CD i uruchamia ewaluację w LangSmith.
#
# Krok 0: Przygotowanie w LangSmith
# 1. Stwórz projekt w LangSmith (np. "Moja-Aplikacja-Ewaluacje").
# 2. Stwórz zestaw danych (dataset) z przykładami wejść i oczekiwanych wyjść.
#    Nazwij go np. "podstawowe-przypadki-testowe".
#
# Kod skryptu `run_evaluation.py`:

from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain.evaluation import run_evaluator, EvaluatorType
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Funkcja budująca łańcuch, który chcemy przetestować
def get_chain_to_test():
    # WAŻNE: W prawdziwym CI/CD, ten kod importowalibyśmy
    # z głównego kodu naszej aplikacji.
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_template("Napisz jedno, zwięzłe zdanie na temat: {input}")
    chain = prompt | llm | StrOutputParser()
    return chain

# Inicjalizacja klienta LangSmith
# Klucze API i nazwa projektu powinny być ustawione jako zmienne środowiskowe w systemie CI/CD
client = Client()

# Nazwa naszego zestawu danych w LangSmith
DATASET_NAME = "podstawowe-przypadki-testowe"

# Pobieramy łańcuch, który będziemy testować
chain_to_test = get_chain_to_test()

# Definiujemy ewaluator, którego chcemy użyć.
# Tutaj używamy LLM (GPT-4) do oceny "zwięzłości" odpowiedzi.
conciseness_evaluator = EvaluatorType.CRITERIA
eval_config = {"criteria": "conciseness"}

# Uruchamiamy ewaluację
# LangSmith automatycznie znajdzie dataset o podanej nazwie,
# uruchomi `chain_to_test` dla każdego przykładu,
# a następnie oceni wyniki za pomocą `conciseness_evaluator`.
test_results = client.run_on_dataset(
    dataset_name=DATASET_NAME,
    llm_or_chain_factory=chain_to_test,
    evaluation={
        "conciseness": run_evaluator(conciseness_evaluator, **eval_config)
    },
    project_name="Ewaluacja - Zwiezlosc",
    concurrency_level=5, # Możemy uruchamiać testy równolegle
)

# W prawdziwym pipeline CI/CD, w tym miejscu przeanalizowalibyśmy obiekt `test_results`,
# sprawdzili średnią ocenę i na tej podstawie zwrócili kod wyjścia (0 dla sukcesu, 1 dla porażki).
print("Ewaluacja zakończona. Sprawdź wyniki w projekcie 'Ewaluacja - Zwiezlosc' w LangSmith.")

#
# 4. Podsumowanie
#
# Automatyzacja testowania to Święty Graal niezawodnej inżynierii AI. To ona daje nam
# pewność, że nasza aplikacja nie tylko działa w momencie tworzenia, ale będzie
# działać stabilnie w przyszłości, mimo ciągłych zmian i rozwoju.
#
# Najważniejsze do zapamiętania:
#
#     1. **Dwuetapowe testowanie**: Zawsze zaczynaj od szybkich, tanich testów jednostkowych
#        z mockowaniem, a dopiero potem przechodź do wolniejszych, droższych testów
#        ewaluacyjnych z prawdziwym LLM.
#     2. **LangSmith jako centrum ewaluacji**: Używaj LangSmith do przechowywania zestawów
#        danych i jako silnika do przeprowadzania i analizowania wyników ewaluacji.
#     3. **Integruj z CI/CD**: Proces testowania musi być automatyczny i uruchamiany przy
#        każdej zmianie kodu. Narzędzia takie jak GitHub Actions, GitLab CI czy Jenkins są
#        do tego idealne.
#     4. **Testowanie to ciągły proces**: Twoje zestawy danych powinny być żywe. Regularnie
#        dodawaj do nich nowe, trudne przypadki, które odkryjesz podczas monitorowania
#        aplikacji na produkcji.
#
# Opanowując ten proces, zamykasz pełne koło profesjonalnego cyklu życia aplikacji AI:
# od pomysłu, przez budowę i wdrożenie, aż po ciągłe, zautomatyzowane zapewnianie jakości.