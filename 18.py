# Moduł 2, Lekcja 18: Optymalizacja kodu w Pythonie
#
#
#
# Pisanie kodu, który działa, to pierwszy krok. Pisanie kodu, który działa SZYBKO
# i efektywnie, to kolejny, wyższy poziom umiejętności. W analizie danych i AI,
# gdzie przetwarzamy ogromne ilości informacji, optymalizacja jest nie tylko
# "miłym dodatkiem" – często jest koniecznością.
#
# Optymalizacja to proces modyfikowania kodu tak, aby zużywał mniej zasobów
# (czasu procesora, pamięci RAM) przy zachowaniu tej samej funkcjonalności.
#
# Złota zasada optymalizacji:
# "Przedwczesna optymalizacja jest źródłem wszelkiego zła" – Donald Knuth.
#
# Oznacza to: Najpierw napisz kod, który jest CZYSTY, POPRAWNY i zrozumiały.
# Dopiero gdy stwierdzisz, że jest on zbyt wolny, zacznij go optymalizować.
#
# 1. Jak mierzyć czas wykonania kodu? – Profilowanie
#
# Zanim zaczniesz cokolwiek optymalizować, musisz wiedzieć, CO jest wolne.
# Zgadywanie jest nieefektywne. Proces mierzenia wydajności kodu nazywamy profilowaniem.
#
#     * Prosty pomiar za pomocą modułu `time`
#       To najprostsza metoda do szybkiego zmierzenia czasu wykonania fragmentu kodu.

import time

start_time = time.time() # Zapisz czas początkowy

# Operacja, której czas chcemy zmierzyć
suma = 0
for i in range(1_000_000): # Używamy _ dla czytelności dużych liczb
    suma += i

end_time = time.time() # Zapisz czas końcowy

czas_wykonania = end_time - start_time
print(f"--- Pomiar czasu za pomocą modułu 'time' ---")
print(f"Obliczenie sumy zajęło: {czas_wykonania:.6f} sekund.")


#     * Magiczna komenda `%timeit` w Jupyter Notebook
#       Jeśli pracujesz w Jupyterze (lub IPython), masz do dyspozycji potężne narzędzie.
#       `%timeit` uruchamia kod wielokrotnie, aby uzyskać bardziej wiarygodną,
#       uśrednioną miarę czasu wykonania.
#
#       --- Przykład użycia w komórce Jupytera ---
#       %timeit sum(range(1_000_000))
#
#       Wynik będzie wyglądał np. tak:
#       25.5 ms ± 1.2 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
#       Co oznacza, że średnio operacja trwała 25.5 milisekundy.
#

#
# 2. Kluczowe techniki optymalizacji w Pythonie
#
# Oto kilka praktycznych technik, które możesz zastosować od razu.
#
#     * Używaj wbudowanych funkcji i bibliotek
#       Wbudowane funkcje Pythona oraz funkcje z bibliotek takich jak NumPy są
#       napisane w języku C i są ZAWSZE szybsze niż pętle pisane ręcznie w Pythonie.

# Przykład: Sumowanie liczb
lista_liczb = list(range(1_000_000))

# Sposób wolniejszy (pętla w Pythonie)
start_pętla = time.time()
suma_pętla = 0
for liczba in lista_liczb:
    suma_pętla += liczba
end_pętla = time.time()
print(f"\n--- Wbudowane funkcje vs Pętle ---")
print(f"Czas sumowania pętlą: {end_pętla - start_pętla:.6f} s")

# Sposób znacznie szybszy (wbudowana funkcja `sum`)
start_sum = time.time()
suma_funkcja = sum(lista_liczb)
end_sum = time.time()
print(f"Czas sumowania funkcją sum(): {end_sum - start_sum:.6f} s")

#
#     * Unikaj pętli na rzecz wektoryzacji (NumPy/Pandas)
#       To najważniejsza technika optymalizacji w analizie danych. Zamiast iterować
#       po elementach, wykonuj operacje na całych tablicach naraz.

import numpy as np

# Przykład: Mnożenie dwóch wektorów (list/tablic)
a = np.random.rand(1_000_000)
b = np.random.rand(1_000_000)

# Sposób wolny (pętla i listy Pythona)
start_lista = time.time()
wynik_lista = [a[i] * b[i] for i in range(len(a))]
end_lista = time.time()
print(f"\n--- Wektoryzacja (NumPy) vs Pętle ---")
print(f"Czas mnożenia na listach (pętla): {end_lista - start_lista:.6f} s")

# Sposób super szybki (wektoryzacja w NumPy)
start_numpy = time.time()
wynik_numpy = a * b
end_numpy = time.time()
print(f"Czas mnożenia w NumPy (wektoryzacja): {end_numpy - start_numpy:.6f} s")
# Różnica w czasie jest gigantyczna!

#
#     * Wybieraj odpowiednie struktury danych
#       Sprawdzanie, czy element istnieje w liście, jest wolne. W zbiorze (set) - błyskawiczne.

duza_lista = list(range(1_000_000))
duzy_zbior = set(duza_lista)
element_do_znalezienia = 999_999

# Sprawdzanie w liście (wolne)
start_lista_check = time.time()
_ = element_do_znalezienia in duza_lista
end_lista_check = time.time()
print(f"\n--- Odpowiednie struktury danych (set vs list) ---")
print(f"Czas sprawdzania w liście: {end_lista_check - start_lista_check:.6f} s")

# Sprawdzanie w zbiorze (błyskawiczne)
start_zbior_check = time.time()
_ = element_do_znalezienia in duzy_zbior
end_zbior_check = time.time()
print(f"Czas sprawdzania w zbiorze: {end_zbior_check - start_zbior_check:.6f} s")

#
# 3. Kiedy sięgać po więcej? Profilery i Cython
#
# Gdy powyższe techniki nie wystarczają, można sięgnąć po cięższą artylerię:
#
#     * Profilery (np. cProfile): To moduły, które analizują Twój kod i dokładnie
#       wskazują, które funkcje zajmują najwięcej czasu. Dają szczegółowy raport.
#
#     * Cython: Pozwala "przetłumaczyć" kod Pythona na język C, co może dać
#       ogromny przyrost wydajności dla operacji numerycznych, które nie dają się
#       łatwo zwektoryzować. Jest to już bardzo zaawansowana technika.
#
#
# 4. Podsumowanie
#
#     * Nie optymalizuj na ślepo! Najpierw zmierz wydajność kodu (profiluj),
#       aby znaleźć "wąskie gardła".
#
#     * Najprostszym narzędziem do pomiaru jest moduł `time` lub `%timeit` w Jupyterze.
#
#     * Najważniejsze techniki optymalizacji w Pythonie to:
#         - Używanie wbudowanych funkcji zamiast pętli.
#         - Wektoryzacja operacji za pomocą NumPy i Pandas.
#         - Dobór odpowiednich struktur danych (np. `set` do szybkiego sprawdzania przynależności).
#
#     * Pamiętaj o czytelności. Czasami nieco wolniejszy, ale zrozumiały kod jest
#       lepszy niż super-zoptymalizowany, którego nikt (włącznie z Tobą za miesiąc) nie rozumie.
#
# Efektywny kod to nie tylko taki, który działa, ale taki, który szanuje czas –
# zarówno Twój, jak i komputera.
#