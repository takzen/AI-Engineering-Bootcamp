# Moduł 2, Lekcja 16: Testowanie kodu w Pythonie
#
#
#
# Dotychczas, aby sprawdzić, czy nasz kod działa, uruchamialiśmy go i "na oko"
# ocenialiśmy wyniki. To dobre na początku, ale w profesjonalnych projektach,
# zwłaszcza w AI, gdzie wyniki mogą być subtelne i trudne do oceny,
# potrzebujemy bardziej systematycznego podejścia.
#
# Testowanie to proces automatycznego weryfikowania, czy poszczególne fragmenty
# kodu (funkcje, klasy) działają zgodnie z oczekiwaniami.
#
# Dlaczego testowanie jest tak ważne?
#
#     * Pewność siebie: Gdy wprowadzasz zmiany w jednym miejscu, testy dają Ci pewność,
#       że nie zepsułeś czegoś w innym. To tzw. testy regresji.
#     * Lepszy design: Pisanie testowalnego kodu zmusza do tworzenia mniejszych,
#       bardziej wyspecjalizowanych funkcji, co prowadzi do lepszej architektury.
#     * Dokumentacja: Testy są żywą dokumentacją. Pokazują, jak dana funkcja
#       powinna być używana i czego można się po niej spodziewać.
#     * Wiarygodność w AI: Czy możesz ufać wynikom swojego modelu, jeśli nie jesteś
#       pewien, czy funkcja przygotowująca dane działa poprawnie?
#
# 1. Wprowadzenie do `pytest` – potężnego frameworka do testów
#
# Chociaż Python ma wbudowany moduł `unittest`, społeczność pokochała `pytest`
# za jego prostotę, czytelność i potężne funkcje.
#
# WAŻNE: Przed uruchomieniem, upewnij się, że masz zainstalowany pytest.
# W terminalu/wierszu poleceń wpisz:
# pip install pytest
#
# Jak działa `pytest`?
# 1. `pytest` automatycznie skanuje Twój projekt w poszukiwaniu plików o nazwach
#    `test_*.py` lub `*_test.py`.
# 2. Wewnątrz tych plików szuka funkcji o nazwach `test_*()`.
# 3. Uruchamia każdą z tych funkcji.
# 4. Jeśli funkcja zakończy się bez błędu, test jest zaliczony (PASSED).
# 5. Jeśli w funkcji wystąpi błąd `AssertionError` (lub jakikolwiek inny),
#    test jest oblany (FAILED).
#
# 2. Pisanie pierwszego testu
#
# Wyobraźmy sobie, że mamy plik `data_processing.py` z kilkoma funkcjami,
# które będziemy używać w naszym projekcie AI.
#
# --- Plik: data_processing.py ---
def wyczysc_tekst(tekst):
    """Usuwa białe znaki z początku i końca oraz zamienia tekst na małe litery."""
    if not isinstance(tekst, str):
        raise TypeError("Wejście musi być stringiem")
    return tekst.strip().lower()

def oblicz_srednia(lista_liczb):
    """Oblicza średnią arytmetyczną z listy liczb."""
    if not lista_liczb:
        return 0
    return sum(lista_liczb) / len(lista_liczb)

#
# Teraz stwórzmy plik z testami dla tych funkcji.
# Nazwijmy go `test_data_processing.py` i umieśćmy w tym samym folderze.
#
# --- Plik: test_data_processing.py ---
#
# import data_processing # Importujemy moduł, który chcemy testować
#
# # Test 1: Testujemy funkcję wyczysc_tekst
# def test_wyczysc_tekst_standardowy():
#     # Słowo kluczowe `assert` sprawdza, czy warunek jest prawdziwy.
#     # Jeśli nie jest, rzuca błąd AssertionError i test jest oblany.
#     assert data_processing.wyczysc_tekst("  Witaj Świecie!  ") == "witaj świecie!"
#     assert data_processing.wyczysc_tekst("Python") == "python"
#     assert data_processing.wyczysc_tekst("") == ""
#
# # Test 2: Testujemy funkcję oblicz_srednia
# def test_oblicz_srednia_standardowy():
#     assert data_processing.oblicz_srednia([1, 2, 3]) == 2.0
#     assert data_processing.oblicz_srednia([10, 20, 30, 40]) == 25.0
#
# # Test 3: Testujemy przypadki brzegowe (edge cases)
# def test_oblicz_srednia_pusta_lista():
#     # Sprawdzamy, jak funkcja zachowuje się dla pustej listy
#     assert data_processing.oblicz_srednia([]) == 0
#
#
# JAK TO URUCHOMIĆ?
# 1. Wejdź do terminala/wiersza poleceń.
# 2. Przejdź do folderu, w którym znajdują się oba pliki (`data_processing.py` i `test_data_processing.py`).
# 3. Wpisz po prostu komendę:
#    pytest
#
# `pytest` sam znajdzie i uruchomi testy, a na koniec wyświetli zwięzłe podsumowanie.
#
#
# 3. Testowanie, czy funkcja poprawnie rzuca błędy
#
# Co jeśli chcemy sprawdzić, czy nasza funkcja prawidłowo zgłasza błąd,
# np. gdy otrzyma nieprawidłowe dane? `pytest` ma do tego specjalny "context manager".
#
# --- Dodajemy do pliku: test_data_processing.py ---
#
# import pytest # Potrzebujemy importować pytest do zaawansowanych funkcji
#
# def test_wyczysc_tekst_niepoprawny_typ():
#     # Używamy `pytest.raises`, aby powiedzieć: "Oczekuję, że kod wewnątrz
#     # tego bloku rzuci wyjątek typu TypeError".
#     with pytest.raises(TypeError):
#         data_processing.wyczysc_tekst(123) # Ta linia POWINNA spowodować błąd
#
#     # Jeśli błąd nie wystąpi, test zostanie oblany!
#
#
# 4. Struktura testów "Given-When-Then"
#
# Dobrą praktyką jest organizowanie testów w trzech logicznych krokach,
# co czyni je bardziej czytelnymi (nawet jeśli nie piszemy tego jawnie w komentarzach).
#
# def test_przykladowy_w_stylu_gwt():
#     # 1. Given (Dane wejściowe)
#     # Przygotuj wszystkie potrzebne dane i warunki początkowe.
#     lista_wejsciowa = [-10, 0, 10, 20]
#     oczekiwany_wynik = 5.0
#
#     # 2. When (Akcja)
#     # Wywołaj testowaną funkcję / wykonaj akcję.
#     rzeczywisty_wynik = oblicz_srednia(lista_wejsciowa)
#
#     # 3. Then (Asercja)
#     # Sprawdź, czy wynik jest zgodny z oczekiwaniami.
#     assert rzeczywisty_wynik == oczekiwany_wynik
#
#
# 5. Podsumowanie
#
# Testowanie nie jest dodatkiem, ale integralną częścią procesu tworzenia
# solidnego i niezawodnego oprogramowania.
#
#     * Automatyczne testy dają Ci pewność, że Twój kod działa i nie psujesz go przy modyfikacjach.
#     * `pytest` to nowoczesny i prosty w użyciu framework do testowania w Pythonie.
#     * `pytest` automatycznie znajduje i uruchamia testy z plików `test_*.py` i funkcji `test_*()`.
#     * Kluczem do testowania jest instrukcja `assert`, która sprawdza, czy warunek jest prawdziwy.
#     * Do sprawdzania, czy funkcja poprawnie rzuca wyjątki, używamy `with pytest.raises(TypWyjatku):`.
#     * Struktura "Given-When-Then" pomaga pisać czyste i zrozumiałe testy.
#
# Zaczynając pisać testy dla swojego kodu, nawet najprostsze, wchodzisz na wyższy
# poziom profesjonalizmu i budujesz solidne fundamenty pod przyszłe, skomplikowane projekty AI.
#