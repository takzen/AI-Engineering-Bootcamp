# Moduł 2, Lekcja 14: Praca z bibliotekami NumPy i Pandas
#
#
# Witaj w jednej z najważniejszych lekcji kursu! Poznamy dwie biblioteki, które są
# absolutnym fundamentem analizy danych i uczenia maszynowego w Pythonie.
#
#     * NumPy (Numerical Python): To biblioteka do wydajnych obliczeń na wielowymiarowych
#       tablicach (macierzach). Jest to "silnik" dla wielu innych bibliotek.
#
#     * Pandas: To biblioteka do manipulacji i analizy danych tabelarycznych. Działa na
#       bazie NumPy, ale dodaje etykiety (nazwy wierszy i kolumn), co czyni dane
#       o wiele bardziej intuicyjnymi.
#
# Pomyśl o tym tak: NumPy to superszybki silnik, a Pandas to karoseria,
# kierownica i deska rozdzielcza, które pozwalają tym silnikiem wygodnie sterować.
#
# WAŻNE: Przed uruchomieniem tego skryptu, upewnij się, że masz zainstalowane te biblioteki.
# W terminalu/wierszu poleceń wpisz:
# pip install numpy pandas
#
# 1. NumPy – Fundament Obliczeń Naukowych
#
# Głównym obiektem w NumPy jest `ndarray` (N-dimensional array). Jest to tablica, która
# w odróżnieniu od listy Pythona, musi przechowywać elementy tego samego typu (np. same liczby).
# Dzięki temu operacje na niej są niezwykle szybkie.

import numpy as np # Standardowy alias dla numpy

# 1.1 Tworzenie tablic NumPy
# Możemy je tworzyć z list Pythona.
lista_py = [1, 2, 3, 4, 5]
tablica_np = np.array(lista_py)

print("--- NumPy ---")
print(f"Zwykła lista Pythona: {lista_py}")
print(f"Tablica NumPy (ndarray): {tablica_np}")
print(f"Typ obiektu NumPy: {type(tablica_np)}")


# 1.2 Magia wektoryzacji – Dlaczego NumPy jest szybki?
# W NumPy możemy wykonywać operacje matematyczne na całej tablicy naraz,
# bez pisania pętli `for`. Nazywa się to wektoryzacją.

# Chcemy pomnożyć każdy element przez 2.

# Sposób z listą Pythona (wymaga pętli):
wynik_lista = [x * 2 for x in lista_py]

# Sposób z NumPy (bez pętli):
wynik_tablica = tablica_np * 2

print(f"\nWynik mnożenia (lista Pythona): {wynik_lista}")
print(f"Wynik mnożenia (NumPy): {wynik_tablica}")

# Ta operacja w NumPy jest napisana w języku C i jest dziesiątki, a nawet setki razy
# szybsza dla dużych zbiorów danych niż pętla w Pythonie.

# 1.3 Inne przydatne funkcje NumPy
# NumPy pozwala łatwo tworzyć tablice i wykonywać na nich skomplikowane operacje.
tablica_zer = np.zeros(5) # Tablica z samymi zerami
zakres_liczb = np.arange(0, 10, 2) # Podobne do range(), ale tworzy tablicę
srednia = tablica_np.mean() # Obliczanie średniej
suma = tablica_np.sum() # Obliczanie sumy

print(f"\nŚrednia z tablicy {tablica_np} to: {srednia}")


# 2. Pandas – Szwajcarski scyzoryk do analizy danych
#
# Pandas wprowadza dwie kluczowe struktury:
#   - `Series`: Jednowymiarowa, etykietowana tablica (jak jedna kolumna w tabeli).
#   - `DataFrame`: Dwuwymiarowa, etykietowana tabela (jak arkusz w Excelu).

import pandas as pd # Standardowy alias dla pandas

# 2.1 Tworzenie DataFrame
# DataFrame to najważniejsza struktura w Pandas. Możemy ją stworzyć np. ze słownika.
dane_dict = {
    'imie': ['Anna', 'Piotr', 'Zofia', 'Tomasz'],
    'wiek': [28, 35, 41, 22],
    'miasto': ['Warszawa', 'Kraków', 'Gdańsk', 'Warszawa']
}

ramka_danych = pd.DataFrame(dane_dict)

print("\n\n--- Pandas ---")
print("Nasz pierwszy DataFrame:")
print(ramka_danych)


# 2.2 Wczytywanie danych z pliku – najważniejsza funkcja
# Najczęściej będziemy wczytywać dane z plików, np. CSV.
# Stwórzmy najpierw przykładowy plik.
csv_data = """id,produkt,cena
1,jabłko,2.50
2,banan,4.99
3,chleb,3.20
"""
with open("produkty.csv", "w", encoding='utf-8') as f:
    f.write(csv_data)

# Teraz wczytajmy go za pomocą jednej komendy!
df_produkty = pd.read_csv("produkty.csv")
print("\nDataFrame wczytany z pliku CSV:")
print(df_produkty)

# 2.3 Pierwsze spojrzenie na dane (inspekcja)
# Pandas daje nam świetne narzędzia do szybkiego "zrozumienia" danych.
print("\nPierwsze 2 wiersze (metoda .head()):")
print(ramka_danych.head(2))

print("\nPodstawowe informacje o ramce (metoda .info()):")
ramka_danych.info()

print("\nStatystyki opisowe dla kolumn numerycznych (metoda .describe()):")
print(ramka_danych.describe())

# 2.4 Selekcja i filtrowanie danych – serce Pandas
# To jest najważniejsza umiejętność w pracy z Pandas.

# a) Wybieranie jednej kolumny (zwraca obiekt Series)
kolumna_imiona = ramka_danych['imie']
print(f"\nWybrana kolumna 'imie':\n{kolumna_imiona}")

# b) Wybieranie wielu kolumn (zwraca nowy DataFrame)
kolumny_imie_miasto = ramka_danych[['imie', 'miasto']]
print(f"\nWybrane kolumny 'imie' i 'miasto':\n{kolumny_imie_miasto}")

# c) Filtrowanie wierszy na podstawie warunku (Boolean Indexing)
# Chcemy wybrać tylko osoby, które mają więcej niż 30 lat.
starsi_niz_30 = ramka_danych[ramka_danych['wiek'] > 30]
print(f"\nOsoby starsze niż 30 lat:\n{starsi_niz_30}")

# Chcemy wybrać tylko osoby z Warszawy.
osoby_z_warszawy = ramka_danych[ramka_danych['miasto'] == 'Warszawa']
print(f"\nOsoby z Warszawy:\n{osoby_z_warszawy}")


# 3. Podsumowanie
#
#     * NumPy dostarcza obiekt `ndarray` i mechanizm wektoryzacji, co pozwala na
#       błyskawiczne operacje numeryczne. Jest fundamentem dla całego ekosystemu AI w Pythonie.
#
#     * Pandas buduje na NumPy, dostarczając `DataFrame` – potężną strukturę do pracy
#       z danymi tabelarycznymi. Etykiety (indeksy i nazwy kolumn) czynią go niezwykle elastycznym.
#
#     * Najważniejsze operacje w Pandas to wczytywanie danych (`pd.read_csv`),
#       inspekcja (`.head()`, `.info()`, `.describe()`) oraz selekcja i filtrowanie
#       (wybieranie kolumn i filtrowanie wierszy za pomocą warunków).
#
# To dopiero początek przygody z tymi bibliotekami, ale opanowanie tych podstaw
# otwiera drzwi do praktycznie każdego zadania związanego z analizą danych.
#