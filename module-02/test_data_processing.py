import data_processing


# # Test 1: Testujemy funkcję wyczysc_tekst
def test_wyczysc_tekst_standardowy():
    # Słowo kluczowe `assert` sprawdza, czy warunek jest prawdziwy.
    # Jeśli nie jest, rzuca błąd AssertionError i test jest oblany.
    assert data_processing.wyczysc_tekst("  Witaj Świecie!  ") == "witaj świecie!"
    assert data_processing.wyczysc_tekst("Python") == "python"
    assert data_processing.wyczysc_tekst("") == ""

# # Test 2: Testujemy funkcję oblicz_srednia
def test_oblicz_srednia_standardowy():
    assert data_processing.oblicz_srednia([1, 2, 3]) == 2.0
    assert data_processing.oblicz_srednia([10, 20, 30, 40]) == 25.0
#
# # Test 3: Testujecd my przypadki brzegowe (edge cases)
def test_oblicz_srednia_pusta_lista():
    # Sprawdzamy, jak funkcja zachowuje się dla pustej listy
    assert data_processing.oblicz_srednia([]) == 0