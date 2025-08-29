# Moduł 2, Punkt 10: Obsługa błędów i debugowanie kodu
#
#
#
# Witaj w jednej z najważniejszych lekcji. Pisanie kodu to jedno, ale pisanie kodu,
# który jest odporny na błędy i nieprzewidziane sytuacje, to zupełnie inna, wyższa umiejętność.
# W tej lekcji nauczymy się, jak elegancko obsługiwać błędy i jak tropić usterki (bugi) w naszych programach.
#
# 1. Błędy (wyjątki) – nieunikniony element programowania
#
# Błędy w Pythonie, nazywane wyjątkami (Exceptions), zdarzają się cały czas.
# Dzielą się na wiele typów, a oto kilka, które już mogłeś spotkać:
#
#     * SyntaxError: Błąd składni, np. brakujący nawias, literówka w słowie kluczowym.
#                    Python nawet nie uruchomi takiego kodu.
#     * NameError: Użycie zmiennej, która nie została wcześniej zdefiniowana.
#     * TypeError: Próba wykonania operacji na niewłaściwym typie danych, np. dodanie liczby do tekstu.
#     * ValueError: Typ danych jest poprawny, ale wartość nieodpowiednia, np. próba konwersji "abc" na int.
#     * IndexError: Próba odwołania się do elementu listy pod indeksem, który nie istnieje.
#     * KeyError: Próba odwołania się do klucza w słowniku, który nie istnieje.
#     * FileNotFoundError: Próba otwarcia pliku, którego nie ma.
#     * ZeroDivisionError: Próba dzielenia przez zero.
#
# Nieobsłużony wyjątek powoduje natychmiastowe zatrzymanie programu i wyświetlenie tzw. tracebacku.
#
# 2. Blok `try...except` – Łapanie wyjątków
#
# Już poznaliśmy podstawy tego bloku. Służy on do "pilnowania" fragmentu kodu,
# w którym spodziewamy się błędu, i pozwala nam na reakcję, zamiast "wykrzaczenia" programu.
#
# Składnia:
# try:
#     # Kod, który może rzucić wyjątek
# except TypWyjątku:
#     # Kod, który wykona się TYLKO, jeśli wystąpił dany typ wyjątku

def dzielenie_liczb():
    try:
        liczba1 = int(input("Podaj pierwszą liczbę: "))
        liczba2 = int(input("Podaj drugą liczbę: "))
        wynik = liczba1 / liczba2
        print(f"Wynik dzielenia to: {wynik}")
    except ValueError:
        print("Błąd! Wprowadzono niepoprawną wartość. Proszę podać liczby.")
    except ZeroDivisionError:
        print("Błąd! Nie można dzielić przez zero.")

# Wywołaj funkcję i spróbuj podać np. tekst lub 0 jako drugą liczbę.
# dzielenie_liczb()

# Możemy też łapać kilka wyjątków naraz lub użyć ogólnego `Exception`.
def dzielenie_liczb_ogolnie():
    try:
        liczba1 = int(input("Podaj pierwszą liczbę: "))
        liczba2 = int(input("Podaj drugą liczbę: "))
        wynik = liczba1 / liczba2
        print(f"Wynik dzielenia to: {wynik}")
    except (ValueError, ZeroDivisionError):
        print("Błąd! Wprowadzono niepoprawne dane lub próbowano dzielić przez zero.")
    except Exception as e:
        # To złapie każdy inny, niespodziewany błąd. 'as e' przypisuje obiekt błędu do zmiennej e.
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        print(f"Typ błędu: {type(e)}")

# dzielenie_liczb_ogolnie()


# 3. Klauzule `else` i `finally`
#
# Blok `try...except` można rozszerzyć o dwie dodatkowe klauzule:
#
#     `else`: Ten blok kodu wykona się, jeśli w bloku `try` NIE wystąpił żaden wyjątek.
#            Jest to dobre miejsce na kod, który zależy od powodzenia operacji z `try`.
#
#     `finally`: Ten blok kodu wykona się ZAWSZE – niezależnie od tego, czy był błąd,
#                czy go nie było. Idealne miejsce na operacje "sprzątające", np. zamykanie
#                połączenia z bazą danych, czy zwalnianie zasobów.

plik_do_przeczytania = "dane.csv" # Plik, który stworzyliśmy w poprzedniej lekcji
# plik_do_przeczytania = "nieistniejacy.txt" # Możesz odkomentować, by przetestować błąd

try:
    print(f"\nPróbuję otworzyć plik: {plik_do_przeczytania}")
    plik = open(plik_do_przeczytania, 'r')
    # UWAGA: Celowo nie używamy 'with', aby pokazać działanie 'finally' przy zamykaniu pliku
    zawartosc = plik.read(50) # Czytamy pierwsze 50 znaków
except FileNotFoundError:
    print("Błąd! Plik nie został znaleziony.")
else:
    # Ten blok wykona się tylko, jeśli plik został pomyślnie otwarty
    print("Plik otwarty pomyślnie. Oto jego początek:")
    print(zawartosc)
finally:
    # Ten blok wykona się ZAWSZE, abyśmy mogli posprzątać
    # Sprawdzamy, czy zmienna 'plik' została utworzona, zanim spróbujemy ją zamknąć
    if 'plik' in locals() and not plik.closed:
        plik.close()
        print("Operacja zakończona, plik został zamknięty w bloku 'finally'.")
    else:
        print("Operacja zakończona (plik nie został otwarty lub już jest zamknięty).")


# 4. Świadome rzucanie wyjątków – `raise`
#
# Czasami chcemy sami wywołać błąd w naszym kodzie. Dzieje się tak, gdy dane wejściowe
# są technicznie poprawne (np. to liczba), ale logicznie błędne dla naszego programu (np. wiek ujemny).
# Używamy do tego słowa kluczowego `raise`.


def ustaw_wiek_uzytkownika(wiek):
    if not isinstance(wiek, int):
        raise TypeError("Wiek musi być liczbą całkowitą.")
    if wiek < 0:
        raise ValueError("Wiek nie może być ujemny.")
    if wiek > 130:
        raise ValueError("Wiek jest nierealistycznie wysoki.")
    
    print(f"Wiek użytkownika ustawiony na {wiek}.")

try:
    # ustaw_wiek_uzytkownika(25)      # Poprawne
    ustaw_wiek_uzytkownika("abc")   # Spowoduje TypeError
    # ustaw_wiek_uzytkownika(-5)      # Spowoduje ValueError
    # ustaw_wiek_uzytkownika(200)     # Spowoduje ValueError
except (TypeError, ValueError) as e:
    print(f"Nie udało się ustawić wieku. Powód: {e}")


# 5. Debugowanie – Sztuka znajdowania błędów
#
# Obsługa błędów to jedno, ale co, jeśli nasz program nie działa tak, jak oczekujemy,
# ale nie rzuca żadnych wyjątków? Wtedy musimy debugować.
#
#     * Metoda 1: Stary, dobry `print()`
#       Najprostsza i często najszybsza metoda. Wstawiaj `print()` w różnych miejscach
#       kodu, aby zobaczyć, jakie wartości mają zmienne na poszczególnych etapach.

def oblicz_srednia(lista_liczb):
    suma = 0
    print(f"DEBUG: Rozpoczynam obliczenia dla listy: {lista_liczb}")
    for liczba in lista_liczb:
        # Celowy błąd: zamiast dodawać, mnożymy.
        # suma *= liczba 
        suma += liczba # Poprawna linia
        print(f"DEBUG: Aktualna liczba: {liczba}, aktualna suma: {suma}")
    
    srednia = suma / len(lista_liczb)
    print(f"DEBUG: Końcowa suma: {suma}, ilość elementów: {len(lista_liczb)}")
    return srednia

print(f"\nWynik (z debugowaniem): {oblicz_srednia([10, 20, 30])}")

#     * Metoda 2: Czytanie Tracebacku
#       Gdy program się "wykrzacza", dostajesz traceback. Nie bój się go! Czytaj go od dołu do góry.
#       - Ostatnia linia: Mówi Ci, jaki był typ błędu i co go spowodowało.
#       - Linia powyżej: Pokazuje dokładną linię kodu, która zawiodła.
#       - Linie wyżej: Pokazują "ścieżkę wywołań" – która funkcja wywołała którą.

#     * Metoda 3: Użycie Debuggera
#       Każde porządne środowisko programistyczne (IDE) jak VS Code, PyCharm czy nawet IDLE
#       ma wbudowany debugger. Pozwala on na:
#       - Ustawianie "breakpointów": Miejsc, w których program ma się zatrzymać.
#       - Wykonywanie kodu linijka po linijce.
#       - Podglądanie wartości wszystkich zmiennych w czasie rzeczywistym.
#       To najpotężniejsze narzędzie do tropienia skomplikowanych błędów.
#
# 6. Podsumowanie
#
#     * Błędy (wyjątki) są naturalną częścią programowania. Nie należy się ich bać.
#     * Używaj bloku `try...except`, aby obsługiwać spodziewane błędy i zapobiegać awarii programu.
#     * Łap konkretne wyjątki (`ValueError`, `TypeError`) zamiast ogólnego `Exception`, kiedy tylko możesz.
#     * Rozszerzaj `try...except` o `else` (dla kodu "na sukces") i `finally` (dla kodu "sprzątającego").
#     * Używaj `raise`, aby sygnalizować błędy wynikające z logiki Twojego programu.
#     * Debuguj za pomocą `print()`, ucząc się czytać tracebacki, a w przyszłości – korzystając z profesjonalnego debuggera.
#
# Pisanie kodu, który dobrze radzi sobie z błędami, to oznaka dojrzałości programistycznej.
#