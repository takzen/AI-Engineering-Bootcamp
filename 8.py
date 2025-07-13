# Moduł 2, Punkt 8: Operacje na plikach i podstawy pracy z danymi
#
#
#
# Do tej pory nasz kod działał tylko w pamięci komputera. Po zakończeniu programu wszystkie dane
# (zmienne, listy) znikały. Aby móc zapisywać wyniki naszej pracy na stałe lub wczytywać dane
# z zewnętrznych źródeł, musimy nauczyć się operacji na plikach.
# Jest to absolutnie fundamentalna umiejętność dla każdego analityka i programisty.
#
# 1. Dlaczego praca z plikami jest tak ważna?
#
#     * Trwałość danych: Zapisujemy dane (np. wyniki obliczeń, raporty), aby móc do nich wrócić później.
#     * Źródło danych: Wczytujemy dane do analizy z plików tekstowych, CSV, Excel itp.
#     * Komunikacja z innymi programami: Pliki są uniwersalnym sposobem wymiany informacji.
#
# 2. Otwieranie i zamykanie plików – instrukcja `with`
#
# Aby pracować z plikiem, musimy go najpierw otworzyć. Najlepszym i najbezpieczniejszym sposobem
# jest użycie instrukcji `with`.
#
# Składnia: with open("nazwa_pliku.txt", "tryb") as nazwa_zmiennej:
#
#     `with`: Gwarantuje, że plik zostanie automatycznie zamknięty po zakończeniu bloku kodu,
#             nawet jeśli wystąpi błąd. To niezwykle ważne!
#     `open()`: Wbudowana funkcja Pythona do otwierania plików.
#     `"nazwa_pliku.txt"`: Ścieżka do pliku, z którym chcemy pracować.
#     `"tryb"`: Określa, co chcemy robić z plikiem (np. czytać, pisać).
#     `as nazwa_zmiennej`: Otwarty plik zostaje przypisany do zmiennej, przez którą będziemy się do niego odwoływać.

# Przykład: poniższy kod nic nie robi, ale poprawnie otwiera i zamyka plik.
try:
    with open("nieistniejacy_plik.txt", "r") as plik:
        pass # słowo kluczowe oznaczające "nic nie rób"
except FileNotFoundError:
    print("Celowo pokazujemy, że 'with' działa nawet przy błędach.")
    print("Plik nie istnieje, ale program nie zawiesił się na próbie jego zamknięcia.")


# 3. Tryby otwierania plików
#
# Drugi argument funkcji open() to tryb. Najważniejsze z nich to:
#
#     'r' (read) - odczyt: Domyślny tryb. Plik musi istnieć, w przeciwnym razie wystąpi błąd.
#
#     'w' (write) - zapis: Jeśli plik nie istnieje, zostanie utworzony.
#                          UWAGA: Jeśli plik istnieje, jego zawartość zostanie CAŁKOWICIE USUNIĘTA (nadpisana)!
#
#     'a' (append) - dopisywanie: Jeśli plik nie istnieje, zostanie utworzony.
#                                Jeśli plik istnieje, nowe dane zostaną dopisane na jego końcu.


# 4. Zapisywanie danych do pliku (`'w'` i `'a'`)
#
# Używamy metody .write() na zmiennej plikowej.

# Używamy trybu 'w', aby stworzyć plik od nowa.
with open("lista_zakupow.txt", "w") as plik:
    plik.write("Jajka\n")
    plik.write("Mleko\n")
    plik.write("Chleb\n") # \n to znak nowej linii, musimy dodawać go ręcznie!

print("Plik 'lista_zakupow.txt' został utworzony/nadpisany.")

# Używamy trybu 'a', aby dopisać coś na końcu.
with open("lista_zakupow.txt", "a") as plik:
    plik.write("Masło\n")

print("Dopisano 'Masło' do pliku.")


# 5. Odczytywanie danych z pliku (`'r'`)
#
# Istnieje kilka sposobów, ale najprostszy i najbardziej wydajny to iteracja po pliku w pętli for.

print("\nZawartość pliku 'lista_zakupow.txt':")
with open("lista_zakupow.txt", "r") as plik:
    for linia in plik:
        # metoda .strip() usuwa białe znaki (spacje, tabulatory, nowe linie) z początku i końca tekstu.
        # Jest to bardzo ważne, aby pozbyć się znaków '\n'.
        print(f" - {linia.strip()}")

# Inne metody odczytu (mniej popularne w codziennym użyciu):
#
#   plik.read()     - wczytuje CAŁY plik jako jeden, wielki string. Niebezpieczne dla dużych plików!
#   plik.readlines() - wczytuje CAŁY plik jako listę stringów (każdy element to jedna linia).

#
# 6. Praktyczny przykład – Przetwarzanie pliku CSV
#
# CSV (Comma-Separated Values) to bardzo popularny format przechowywania danych tabelarycznych.
# To zwykły plik tekstowy, gdzie kolumny są oddzielone przecinkami.
#
# Krok 1: Stwórzmy przykładowy plik danych.
dane_do_zapisu = [
    "imie,wiek,miasto\n",
    "Anna,28,Warszawa\n",
    "Piotr,35,Kraków\n",
    "Zofia,41,Gdańsk\n"
]

with open("dane.csv", "w") as plik_csv:
    for rekord in dane_do_zapisu:
        plik_csv.write(rekord)

print("\nUtworzono plik 'dane.csv'.")

# Krok 2: Wczytajmy i przetwórzmy te dane.
# Chcemy przekształcić je w listę słowników - to bardzo częsta operacja.

lista_osob = []
print("Przetwarzanie pliku CSV:")

try:
    with open("dane.csv", "r") as plik_csv:
        # Odczytujemy nagłówek (pierwszą linię), aby znać nazwy kolumn
        naglowek = plik_csv.readline().strip().split(',')

        # Iterujemy po pozostałych liniach pliku
        for linia in plik_csv:
            wartosci = linia.strip().split(',')

            # Tworzymy słownik dla jednego rekordu (osoby)
            osoba_slownik = {
                naglowek[0]: wartosci[0],
                naglowek[1]: int(wartosci[1]), # Konwertujemy wiek na liczbę
                naglowek[2]: wartosci[2]
            }
            lista_osob.append(osoba_slownik)

except FileNotFoundError:
    print("BŁĄD: Plik 'dane.csv' nie został znaleziony!")
except Exception as e:
    print(f"Wystąpił nieoczekiwany błąd: {e}")


# Wyświetlmy wynik naszej pracy
print("\nDane przetworzone do listy słowników:")
print(lista_osob)

# Możemy teraz łatwo pracować z tymi danymi
print("\nDane poszczególnych osób:")
for osoba in lista_osob:
    print(f"{osoba['imie']} ma {osoba['wiek']} lat i mieszka w mieście {osoba['miasto']}.")



# 7. Podsumowanie
#
# Gratulacje! Potrafisz teraz komunikować swoje programy ze światem zewnętrznym za pomocą plików.
# To krok milowy w kierunku tworzenia użytecznych aplikacji i analizowania prawdziwych danych.
#
# Najważniejsze do zapamiętania:
#
#     * Zawsze używaj instrukcji `with open(...) as ...`, aby bezpiecznie pracować z plikami.
#     * Rozumiesz kluczowe tryby: 'r' (odczyt), 'w' (zapis/nadpisanie) i 'a' (dopisywanie).
#     * Do zapisu używasz metody `.write()`, pamiętając o ręcznym dodawaniu znaku nowej linii `\n`.
#     * Do odczytu najwygodniej jest iterować po pliku w pętli `for`, używając `.strip()` do czyszczenia linii.
#     * Potrafisz wczytać prosty plik CSV, podzielić linie za pomocą `.split(',')` i przekształcić dane w bardziej użyteczną strukturę (np. listę słowników).
#
# W następnych modułach zobaczymy, jak specjalistyczne biblioteki (np. `csv` i `pandas`) jeszcze bardziej ułatwiają pracę z plikami i danymi.
