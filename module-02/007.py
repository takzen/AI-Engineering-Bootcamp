# Moduł 2, Punkt 7: Podstawowe składnie i struktury w Pythonie
# 
# 
# 
# 1. Komentarze – Notatki w kodzie
# 
# Komentarze to fragmenty tekstu w kodzie, które są całkowicie ignorowane przez interpreter Pythona. Służą one do:
# 
#     Dokumentowania kodu: Wyjaśniania, co robi dany fragment, dlaczego został napisany w taki, a nie inny sposób.
# 
#     Tymczasowego wyłączania kodu: Zamiast usuwać linię kodu, można ją "zakomentować", aby sprawdzić, jak program zachowa się bez niej.
# 
# Jak tworzyć komentarze?
# 
#     Komentarz jednoliniowy: Zaczyna się od znaku #. Wszystko od # do końca linii jest ignorowane.

# To jest komentarz. Python go zignoruje.
print("Hello, World!")  # Ten komentarz wyjaśnia, co robi linia po lewej.


# Komentarz wieloliniowy (docstring): Formalnie to nie jest komentarz, a wieloliniowy string, ale jest powszechnie używany do dokumentowania 
# funkcji i modułów. Tworzy się go za pomocą potrójnych 
# cudzysłowów """ lub apostrofów '''.

"""
To jest komentarz,
który zajmuje
kilka linii.
Jest często używany jako tzw. docstring do opisywania funkcji.
"""
def moja_funkcja():
    """To jest oficjalny docstring tej funkcji."""
    pass

# 2. Zmienne – Pojemniki na dane
# 
# Zmienna to nazwany "pojemnik" w pamięci komputera, w którym możemy przechowywać dane (np. liczbę, tekst, listę).
# 
# Kluczowe cechy zmiennych w Pythonie:
# 
#     Dynamiczne typowanie: Nie musisz deklarować typu zmiennej (np. int czy string). Python sam "domyśli się" typu na podstawie przypisanej wartości.
# 
#     Przypisanie wartości: Używamy do tego znaku równości =.

# Tworzenie zmiennych i przypisywanie im wartości
imie = "Anna"         # Python wie, że to jest tekst (string)
wiek = 25             # Python wie, że to jest liczba całkowita (integer)
wzrost = 1.72         # Python wie, że to jest liczba zmiennoprzecinkowa (float)
jest_studentem = True # Python wie, że to jest wartość logiczna (boolean)

# Możemy wyświetlić wartość zmiennej za pomocą funkcji print()
print(imie)
print(wiek)

# Wartość zmiennej można w każdej chwili zmienić
wiek = 26
print("Nowy wiek:", wiek)


# Zasady nazewnictwa zmiennych:
# 
#     Nazwy mogą zawierać litery, cyfry i znak podkreślenia _.
# 
#     Nie mogą zaczynać się od cyfry.
# 
#     Wielkość liter ma znaczenie (wiek to inna zmienna niż Wiek).
# 
#     Dobrą praktyką jest używanie snake_case (małe litery i podkreślenia), np. liczba_punktow, nazwa_uzytkownika.
# 
# 3. Podstawowe typy danych
# 
# Każda wartość w Pythonie ma swój typ. Oto najważniejsze z nich:
# 
#     Tekst (str - string): Ciąg znaków umieszczony w cudzysłowach " lub apostrofach '.
    
przywitanie = "Dzień dobry"
nazwa_kursu = 'Python dla analityków'

# Liczby całkowite (int - integer): Liczby bez części ułamkowej.

liczba_jablek = 5
rok_urodzenia = 1990

# Liczby zmiennoprzecinkowe (float): Liczby z częścią ułamkową (używamy kropki, nie przecinka).

cena_produktu = 19.99
pi = 3.14159

# Wartości logiczne (bool - boolean): Reprezentują prawdę lub fałsz. Tylko dwie możliwe wartości: True i False (pisane z dużej litery!).

czy_pada_deszcz = True
czy_jest_slonce = False

# Typ None (NoneType): Specjalny typ reprezentujący "brak wartości". Jest to często używane do inicjalizacji zmiennej, która dopiero później 
# otrzyma właściwą wartość.

zwyciezca_loterii = None


# Aby sprawdzić typ zmiennej, można użyć funkcji type():

x = 10
y = "Tekst"
print(type(x))  # <class 'int'>
print(type(y))  # <class 'str'>

# 4. Operatory – Działania na danych
# 
# Operatory to specjalne symbole, które wykonują operacje na zmiennych i wartościach.
# 
#     Operatory arytmetyczne:
# 
#         + (dodawanie)
# 
#         - (odejmowanie)
# 
#         * (mnożenie)
# 
#         / (dzielenie, zawsze zwraca float)
# 
#         // (dzielenie całkowite, obcina część ułamkową)
# 
#         % (modulo, reszta z dzielenia)
# 
#         ** (potęgowanie)
    
a = 10
b = 3
print(a + b)  # 13
print(a / b)  # 3.333...
print(a // b) # 3
print(a % b)  # 1
print(a ** b) # 1000


# Operatory porównania (zwracają True lub False):
# 
#     == (równe)
# 
#     != (różne)
# 
#     > (większe niż)
# 
#     < (mniejsze niż)
# 
#     >= (większe lub równe)
# 
#     <= (mniejsze lub równe)

x = 5
y = 8
print(x == 5) # True
print(x != y) # True
print(y < 10) # True


# Operatory logiczne (łączą warunki):
# 
#     and (zwraca True, jeśli oba warunki są prawdziwe)
# 
#     or (zwraca True, jeśli co najmniej jeden warunek jest prawdziwy)
# 
#     not (negacja, odwraca wartość logiczną)

wiek = 20
ma_prawo_jazdy = True
print(wiek > 18 and ma_prawo_jazdy == True) # True
print(wiek < 18 or ma_prawo_jazdy == False) # False
print(not ma_prawo_jazdy) # False


# 5. Kontrola przepływu – Instrukcje warunkowe
# 
# Instrukcje warunkowe pozwalają na wykonywanie różnych bloków kodu w zależności od tego, czy dany warunek jest spełniony. UWAGA: W Pythonie bloki 
# kodu definiuje się za pomocą wcięć (zwykle 4 spacje), 
# a nie nawiasów klamrowych!
# 
#     if: Wykonuje kod, jeśli warunek jest prawdziwy.
# 
#     else: Wykonuje kod, jeśli warunek w if był fałszywy.
# 
#     elif (skrót od "else if"): Sprawdza kolejny warunek, jeśli poprzednie (if, elif) były fałszywe.

temperatura = 15

if temperatura > 25:
    print("Jest gorąco! Ubierz krótkie spodenki.")
elif temperatura > 10:  # Ten warunek jest sprawdzany, bo pierwszy (if) był fałszywy
    print("Jest ciepło. Wystarczy bluza.")
else:
    print("Jest zimno! Ubierz kurtkę.")

# Wynik: "Jest ciepło. Wystarczy bluza."
# 
# 6. Pętle – Powtarzanie kodu
# 
# Pętle służą do wielokrotnego wykonywania tego samego bloku kodu.
# 
#     Pętla for: Idealna do iterowania (przechodzenia) po elementach sekwencji (np. liście, tekście).
    
owoce = ["jabłko", "banan", "wiśnia"]

# Pętla przejdzie po każdym elemencie listy 'owoce'
for owoc in owoce:
    print("Lubię jeść:", owoc)

# Iterowanie po znakach w stringu
for litera in "Python":
    print(litera)

# Użycie funkcji range() do wykonania pętli określoną liczbę razy
for i in range(5):  # range(5) generuje liczby od 0 do 4
    print("Iteracja numer:", i)


# Pętla while: Wykonuje blok kodu tak długo, jak długo jej warunek jest prawdziwy.

licznik = 0
while licznik < 5:
    print("Licznik ma wartość:", licznik)
    licznik = licznik + 1  # Ważne! Musimy zmieniać wartość licznika, aby uniknąć pętli nieskończonej.

print("Koniec pętli while.")


# Instrukcje break i continue w pętlach:
# 
#     break: Natychmiast przerywa działanie pętli.
# 
#     continue: Przerywa bieżącą iterację i przechodzi do następnej.

for i in range(10): # od 0 do 9
    if i == 3:
        continue  # Pomiń iterację, gdy i jest równe 3
    if i == 7:
        break     # Zakończ pętlę, gdy i jest równe 7
    print(i)

# Wynik: 0, 1, 2, 4, 5, 6
# 
# 
# 7. Podstawowe struktury danych
# 
# Oprócz prostych typów jak int czy str, Python oferuje wbudowane struktury do przechowywania kolekcji danych.
# 
#     Lista (list):
# 
#         Uporządkowana, modyfikowalna kolekcja elementów.
# 
#         Elementy mogą się powtarzać.
# 
#         Tworzona za pomocą nawiasów kwadratowych [].
    
liczby = [1, 5, 2, 8, 2]
print(liczby[0])         # Dostęp do pierwszego elementu (indeksowanie od 0) -> 1
liczby.append(10)        # Dodanie elementu na koniec -> [1, 5, 2, 8, 2, 10]
liczby[1] = 99           # Zmiana wartości elementu -> [1, 99, 2, 8, 2, 10]
print(len(liczby))       # Sprawdzenie długości listy -> 6


# Krotka (tuple):
# 
#     Uporządkowana, ale niemodyfikowalna (immutable) kolekcja.
# 
#     Szybsza od listy, używana tam, gdzie dane nie powinny się zmieniać.
# 
#     Tworzona za pomocą nawiasów okrągłych ().

wspolrzedne = (10.5, 25.2)
print(wspolrzedne[0]) # Dostęp działa tak samo jak w liście -> 10.5
# wspolrzedne[0] = 5.0 # To spowoduje błąd! TypeError


# Słownik (dict):
# 
#     Nieuporządkowana (w starszych Pythonach) kolekcja par klucz-wartość.
# 
#     Modyfikowalny. Klucze muszą być unikalne i niezmienne (np. string, liczba).
# 
#     Tworzony za pomocą nawiasów klamrowych {}.

osoba = {
    "imie": "Jan",
    "nazwisko": "Kowalski",
    "wiek": 30
}
print(osoba["imie"])      # Dostęp do wartości poprzez klucz -> "Jan"
osoba["wiek"] = 31        # Modyfikacja wartości
osoba["zawod"] = "lekarz" # Dodanie nowej pary klucz-wartość
print(osoba)


# Zbiór (set):
# 
#     Nieuporządkowana, modyfikowalna kolekcja unikalnych elementów.
# 
#     Idealny do usuwania duplikatów i operacji matematycznych na zbiorach.
# 
#     Tworzony za pomocą funkcji set() lub {} (ale pusty {} tworzy słownik!).

numery_lotto = {5, 12, 9, 23, 12, 5}
print(numery_lotto) # Wynik: {5, 9, 12, 23} - duplikaty zostały usunięte

unikalne_litery = set("programowanie")
print(unikalne_litery) # {'e', 'o', 'r', 'm', 'i', 'p', 'g', 'a', 'n', 'w'}


# 8. Funkcje – Organizacja i ponowne użycie kodu
# 
# Funkcja to nazwany blok kodu, który wykonuje określone zadanie. Można go wywoływać wielokrotnie w różnych miejscach programu.
# 
#     Definiowanie funkcji: Używamy słowa kluczowego def.
# 
#     Parametry: Dane wejściowe, które funkcja może przyjąć.
# 
#     Zwracanie wartości: Używamy słowa kluczowego return, aby funkcja "oddała" wynik swojej pracy.

# Definicja prostej funkcji bez parametrów
def przywitaj_sie():
    print("Cześć! Miło Cię widzieć.")

# Wywołanie funkcji
przywitaj_sie()

# Definicja funkcji z parametrami i zwracaniem wartości
def dodaj(a, b):
    wynik = a + b
    return wynik

# Wywołanie funkcji i przypisanie jej wyniku do zmiennej
suma = dodaj(5, 7)
print("Wynik dodawania:", suma) # Wynik dodawania: 12

wynik_inny = dodaj(100, -50)
print(wynik_inny) # 50


# Podsumowanie
# 
# Opanowanie powyższych koncepcji to kamień milowy w nauce Pythona. Są to absolutne podstawy, które pojawiają się w każdym, nawet najbardziej złożonym 
# programie.
# 
# Najważniejsze do zapamiętania:
# 
#     Używaj komentarzy (#) do wyjaśniania kodu.
# 
#     Zmienne przechowują dane, a ich typ jest nadawany dynamicznie.
# 
#     Znasz już podstawowe typy danych: str, int, float, bool.
# 
#     Potrafisz używać operatorów do wykonywania działań i porównań.
# 
#     Kontrolujesz przepływ programu za pomocą if/elif/else, pamiętając o kluczowej roli wcięć.
# 
#     Potrafisz powtarzać operacje za pomocą pętli for (dla sekwencji) i while (dla warunków).
# 
#     Wiesz, jak przechowywać kolekcje danych w listach, krotkach, słownikach i zbiorach.
# 
#     Umiesz grupować kod w reużywalne bloki za pomocą funkcji def.
# 
# Teraz najlepsze, co możesz zrobić, to praktykować! Otwórz edytor kodu i spróbuj napisać proste programy, eksperymentując z każdym z omówionych tutaj 
# elementów. Powodzenia