# Moduł 2, Lekcja 13: Zaawansowane struktury danych: listy, słowniki, zbiory
#
#
#
# Witaj w Module 2! Wkraczamy na wyższy poziom. Opanowaliśmy już podstawy Pythona,
# a teraz skupimy się na narzędziach i technikach, które czynią go tak potężnym
# w analizie danych i AI.
#
# Zaczniemy od ponownego przyjrzenia się strukturom, które już znamy, ale tym razem
# poznamy ich zaawansowane możliwości. Efektywne korzystanie z list, słowników
# i zbiorów to klucz do pisania czystego, wydajnego i "pythonicznego" kodu.
#
# 1. Listy – Potęga "Comprehensions"
#
# Poznaliśmy już pętle `for` do tworzenia list. List Comprehension (wyrażenie listowe)
# to bardziej zwięzły, czytelny i często szybszy sposób na robienie tego samego.
# To jedna z najbardziej lubianych cech Pythona.
#
# Przykład: Stworzenie listy kwadratów liczb od 0 do 9.
#
# Sposób klasyczny:
kwadraty_standardowo = []
for i in range(10):
    kwadraty_standardowo.append(i**2)

print(f"Lista kwadratów (standardowo): {kwadraty_standardowo}")

# Sposób z List Comprehension: [wyrażenie for element in sekwencja]
kwadraty_comprehension = [i**2 for i in range(10)]
print(f"Lista kwadratów (comprehension): {kwadraty_comprehension}")

# Możemy też dodawać warunki.
# Przykład: Stwórzmy listę liczb parzystych z zakresu 0-19.
# Składnia: [wyrażenie for element in sekwencja if warunek]

parzyste = [x for x in range(20) if x % 2 == 0]
print(f"\nLiczby parzyste (comprehension z if): {parzyste}")

# Możemy też wykonywać operacje na elementach.
# Przykład: Zamień listę imion na listę tych imion pisanych wielkimi literami.
imiona = ["anna", "piotr", "zofia"]
imiona_wielkimi = [imie.upper() for imie in imiona]
print(f"Imiona wielkimi literami: {imiona_wielkimi}")


# 2. Słowniki – Bezpieczny dostęp i dynamiczne tworzenie
#
# Słowniki to serce wielu aplikacji. Poznajmy techniki, które czynią pracę z nimi łatwiejszą i bezpieczniejszą.
#
#     * Bezpieczny dostęp za pomocą metody `.get()`
#       Próba dostępu do nieistniejącego klucza za pomocą `slownik['klucz']` powoduje błąd `KeyError`.
#       Metoda `.get()` pozwala uniknąć tego błędu.

osoba = {"imie": "Jan", "wiek": 30}

# print(osoba['zawod']) # To spowoduje błąd KeyError!

# .get() zwróci None, jeśli klucz nie istnieje
zawod = osoba.get('zawod')
print(f"\nZawód (gdy nie ma klucza): {zawod}")

# Możemy też podać wartość domyślną, która zostanie zwrócona zamiast None
zawod_domyslny = osoba.get('zawod', 'Brak danych')
print(f"Zawód (z wartością domyślną): {zawod_domyslny}")

#     * Iteracja po słownikach za pomocą `.items()`
#       Metoda `.items()` zwraca pary (klucz, wartość), co jest najwygodniejszym sposobem iteracji.
print("\nIteracja po elementach słownika:")
for klucz, wartosc in osoba.items():
    print(f"  Klucz: '{klucz}', Wartość: '{wartosc}'")

#     * Dictionary Comprehensions
#       Podobnie jak w listach, możemy dynamicznie tworzyć słowniki.
#       Składnia: {klucz_wyrazenie: wartosc_wyrazenie for element in sekwencja}

# Przykład: stwórzmy słownik, gdzie kluczem jest liczba, a wartością jej kwadrat.
slownik_kwadratow = {x: x**2 for x in range(1, 6)}
print(f"\nSłownik kwadratów: {slownik_kwadratow}")

# Przykład: stwórzmy słownik na podstawie listy, filtrując słowa dłuższe niż 3 litery.
slowa = ["jabłko", "dom", "analiza", "ai", "dane"]
slownik_slow = {slowo: len(slowo) for slowo in slowa if len(slowo) > 3}
print(f"Słownik długości słów: {slownik_slow}")


# 3. Zbiory (Sets) – Potęga operacji matematycznych
#
# Główną siłą zbiorów, oprócz przechowywania unikalnych wartości, są błyskawiczne
# operacje matematyczne. Są one niezwykle przydatne w analizie danych do porównywania grup.
#
# Załóżmy, że mamy dwie grupy użytkowników, którzy polubili różne produkty AI.
uzytkownicy_produktu_A = {"Anna", "Piotr", "Zofia", "Tomasz"}
uzytkownicy_produktu_B = {"Krzysztof", "Zofia", "Anna", "Marta"}

#     * Suma (Union): Kto polubił produkt A LUB produkt B?
suma_uzytkownikow = uzytkownicy_produktu_A.union(uzytkownicy_produktu_B)
# lub prościej za pomocą operatora |
suma_uzytkownikow_operatorem = uzytkownicy_produktu_A | uzytkownicy_produktu_B
print(f"\nWszyscy unikalni użytkownicy: {suma_uzytkownikow_operatorem}")

#     * Część wspólna (Intersection): Kto polubił produkt A I produkt B?
wspolni_uzytkownicy = uzytkownicy_produktu_A.intersection(uzytkownicy_produktu_B)
# lub prościej za pomocą operatora &
wspolni_uzytkownicy_operatorem = uzytkownicy_produktu_A & uzytkownicy_produktu_B
print(f"Użytkownicy, którzy polubili oba produkty: {wspolni_uzytkownicy_operatorem}")

#     * Różnica (Difference): Kto polubił produkt A, ale NIE polubił produktu B?
roznica_uzytkownikow = uzytkownicy_produktu_A.difference(uzytkownicy_produktu_B)
# lub prościej za pomocą operatora -
roznica_uzytkownikow_operatorem = uzytkownicy_produktu_A - uzytkownicy_produktu_B
print(f"Użytkownicy, którzy polubili tylko produkt A: {roznica_uzytkownikow_operatorem}")

#     * Różnica symetryczna (Symmetric Difference): Kto polubił tylko jeden z dwóch produktów?
roz_symetryczna = uzytkownicy_produktu_A.symmetric_difference(uzytkownicy_produktu_B)
# lub prościej za pomocą operatora ^
roz_symetryczna_operatorem = uzytkownicy_produktu_A ^ uzytkownicy_produktu_B
print(f"Użytkownicy, którzy polubili tylko jeden produkt: {roz_symetryczna_operatorem}")


# 4. Kiedy czego używać? – Podsumowanie
#
# Wybór odpowiedniej struktury danych jest kluczowy dla wydajności i czytelności kodu.
#
#     * Użyj LISTY (list), gdy:
#         - Kolejność elementów jest ważna.
#         - Dopuszczasz duplikaty.
#         - Chcesz mieć dostęp do elementów po ich indeksie (pozycji).
#         Przykład: Sekwencja kroków w algorytmie, historia transakcji.
#
#     * Użyj SŁOWNIKA (dict), gdy:
#         - Potrzebujesz powiązać unikalny klucz z wartością (mapowanie).
#         - Potrzebujesz szybkiego dostępu do danych na podstawie identyfikatora.
#         - Kolejność (w starszych Pythonach) nie była gwarantowana.
#         Przykład: Konfiguracja programu, profil użytkownika, dane JSON z API.
#
#     * Użyj ZBIORU (set), gdy:
#         - Chcesz przechowywać tylko unikalne elementy.
#         - Potrzebujesz bardzo szybkiego sprawdzania, czy element istnieje w kolekcji.
#         - Chcesz wykonywać operacje matematyczne (suma, część wspólna, różnica).
#         - Kolejność nie ma znaczenia.
#         Przykład: Zbiór unikalnych tagów, porównywanie dwóch list klientów.
#
#
# 5. Podsumowanie lekcji
#
# Opanowanie zaawansowanych technik pracy z wbudowanymi strukturami danych to Twój
# "superpower" jako programisty Pythona.
#
#     * List Comprehensions to zwięzły i wydajny sposób na tworzenie i transformowanie list.
#     * Metoda `.get()` chroni przed błędami w słownikach, a `.items()` ułatwia iterację.
#     * Dictionary Comprehensions pozwalają dynamicznie budować słowniki.
#     * Operacje na zbiorach (`|`, `&`, `-`, `^`) to potężne narzędzie do porównywania kolekcji danych.
#
# Te techniki będą pojawiać się nieustannie w kodzie bibliotek analitycznych,
# więc ich dobre zrozumienie jest fundamentem dalszej nauki.
#