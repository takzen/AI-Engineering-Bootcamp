# Moduł 2, Lekcja 17: Wprowadzenie do środowiska Jupyter Notebook
#
#
#
# Do tej pory pisaliśmy kod w plikach `.py` i uruchamialiśmy je jako całość.
# To świetne podejście do tworzenia aplikacji, ale w analizie danych i eksperymentach z AI
# często potrzebujemy czegoś bardziej interaktywnego. Czegoś, co pozwoli nam uruchamiać
# małe fragmenty kodu, natychmiast widzieć wyniki, wizualizować dane i pisać notatki
# w jednym miejscu.
#
# Tym narzędziem jest Jupyter Notebook – interaktywny "notatnik" dla programisty.
#
# 1. Czym jest Jupyter Notebook?
#
# Jupyter Notebook to aplikacja webowa, która pozwala tworzyć i udostępniać dokumenty
# zawierające jednocześnie:
#
#     * Live Code: Kod Pythona, który można edytować i uruchamiać w locie.
#     * Wizualizacje: Wykresy i diagramy generowane przez kod, wyświetlane bezpośrednio pod nim.
#     * Tekst narracyjny: Sformatowane notatki, wyjaśnienia, a nawet wzory matematyczne.
#
# Jest to standardowe narzędzie do tzw. Eksploracyjnej Analizy Danych (EDA),
# prototypowania modeli AI i prezentowania wyników swojej pracy.
#
# Dlaczego go kochamy?
#   - Interaktywność: Uruchamiasz kod komórka po komórce.
#   - Natychmiastowy feedback: Wyniki, tabele i wykresy pojawiają się od razu.
#   - Dokumentacja: Możesz opisać każdy krok swojej analizy obok kodu.
#   - Łatwość udostępniania: Wysyłasz jeden plik `.ipynb`, który zawiera wszystko.
#
#
# 2. Instalacja i uruchomienie
#
# Jupyter jest często instalowany razem z dystrybucjami Pythona dla analityków (jak Anaconda),
# ale jeśli go nie masz, instalacja jest prosta.
#
# WAŻNE: W terminalu/wierszu poleceń wpisz:
# pip install notebook
#
# Jak uruchomić Jupyter Notebook?
# 1. Otwórz terminal/wiersz poleceń.
# 2. Przejdź do folderu, w którym chcesz przechowywać swoje notatniki (np. `cd Dokumenty/moj_kurs_ai`).
# 3. Wpisz komendę:
#    jupyter notebook
#
# Ta komenda uruchomi serwer Jupyter na Twoim komputerze i otworzy nową kartę
# w przeglądarce internetowej. Zobaczysz listę plików w bieżącym folderze.
# Aby stworzyć nowy notatnik, kliknij: New -> Python 3.
#
#
# 3. Podstawowe elementy Notebooka – Komórki (Cells)
#
# Notatnik składa się z komórek. Każda komórka może być jednego z dwóch głównych typów:
#
#     * Code: Do pisania i wykonywania kodu Pythona.
#     * Markdown: Do pisania sformatowanego tekstu (nagłówki, listy, pogrubienia).
#
# Aby uruchomić aktywną komórkę, użyj skrótu klawiszowego: `Shift + Enter`.
#
# --- Przykład komórki typu 'Code' ---
# To jest przykład kodu, który wpisałbyś w komórce 'Code' w Jupyterze.

print("Witaj w Jupyter Notebook!")
zmienna = 10 + 5
print(f"Wynik to: {zmienna}")

# Po wciśnięciu Shift + Enter, pod komórką pojawi się wynik:
# Witaj w Jupyter Notebook!
# Wynik to: 15

# --- Przykład komórki typu 'Markdown' ---
# To jest tekst, który wpisałbyś w komórce 'Markdown'.
#
# # To jest główny nagłówek
# ## To jest podtytuł
#
# Możemy tworzyć listy:
# * Punkt pierwszy
# * Punkt drugi
#
# A także pisać **pogrubionym** lub *pochylonym* tekstem.
#
# Po wciśnięciu Shift + Enter, tekst zostanie pięknie sformatowany.
#
#
# 4. Stan (State) Notebooka i kolejność wykonywania
#
# TO JEST BARDZO WAŻNE: Wszystkie komórki w jednym notatniku dzielą ten sam "stan".
# Oznacza to, że zmienna zdefiniowana w jednej komórce jest dostępna we wszystkich innych.
#
# --- Komórka 1 ---
imie = "Zenek"
# (Uruchamiamy: Shift + Enter)

# --- Komórka 2 (może być gdziekolwiek w notatniku) ---
print(f"Cześć, {imie}!")
# (Uruchamiamy: Shift + Enter)
# Wynik: Cześć, Zenek!

# Kluczowe jest to, w jakiej KOLEJNOŚCI uruchamiasz komórki, a nie gdzie one
# znajdują się na stronie. Numery `In [1]:`, `In [2]:` po lewej stronie komórek
# pokazują właśnie kolejność wykonania.
#
#
# 5. Praktyczny przykład – Analiza danych w Jupyterze
#
# Zobaczmy, jak wyglądałaby praca z biblioteką pandas i tworzenie wykresów.
#
# --- Komórka 1: Import bibliotek ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Magiczna komenda Jupytera, która sprawia, że wykresy wyświetlają się w notatniku
# %matplotlib inline

# --- Komórka 2: Tworzenie danych ---
dane = {
    'miesiac': ['Sty', 'Lut', 'Mar', 'Kwi', 'Maj'],
    'sprzedaz': [150, 220, 180, 300, 280],
    'nowi_klienci': [20, 25, 22, 35, 30]
}
df = pd.DataFrame(dane)

# --- Komórka 3: Wyświetlenie danych ---
# W Jupyterze nie musisz nawet używać print() dla ostatniej linijki w komórce.
# Wynik zostanie automatycznie wyświetlony.
df.head()
# (Po uruchomieniu pod komórką pojawi się ładnie sformatowana tabela)

# --- Komórka 4: Tworzenie wizualizacji ---
plt.figure(figsize=(8, 5)) # Ustawienie rozmiaru wykresu
plt.plot(df['miesiac'], df['sprzedaz'], marker='o') # Rysowanie wykresu liniowego
plt.title("Miesięczna sprzedaż")
plt.xlabel("Miesiąc")
plt.ylabel("Sprzedaż (w tys. PLN)")
plt.grid(True)
plt.show()
# (Po uruchomieniu pod komórką pojawi się wygenerowany wykres)


# 6. Podsumowanie
#
#     * Jupyter Notebook to interaktywne środowisko do pracy z kodem, tekstem i wizualizacjami.
#     * Jest standardem w analizie danych i AI do eksploracji i prototypowania.
#     * Notatnik składa się z komórek (Code i Markdown), które uruchamiamy za pomocą `Shift + Enter`.
#     * Wszystkie komórki dzielą ten sam stan (zmienne), a ważna jest kolejność ich wykonywania.
#     * Jupyter pozwala na natychmiastową wizualizację danych za pomocą bibliotek jak `Matplotlib`.
#
# Od teraz wiele naszych zadań, zwłaszcza tych związanych z analizą i wizualizacją danych,
# będziemy wykonywać właśnie w Jupyter Notebookach. Czas zacząć eksperymentować!
