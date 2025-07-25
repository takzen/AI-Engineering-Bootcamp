# Moduł 2, Punkt 12: Modułowość i organizacja kodu w AI
#
#
#
# Teraz nauczymy się, jak składać je w większe,
# dobrze zorganizowane projekty. To krok, który oddziela proste skrypty od profesjonalnych aplikacji.
#
# 1. Problem: Chaos w jednym pliku
#
# Gdy program rośnie, trzymanie całego kodu w jednym pliku (np. `main.py`) staje się koszmarem.
#
#     * Czytelność spada: Plik ma setki, a potem tysiące linii. Trudno cokolwiek w nim znaleźć.
#     * Reużywalność jest zerowa: Jeśli chcesz użyć jakiejś funkcji w innym projekcie, musisz ją kopiować i wklejać.
#     * Współpraca jest trudna: Gdy kilka osób pracuje nad tym samym plikiem, ciągle wchodzą sobie w drogę.
#     * Testowanie jest uciążliwe: Trudno jest wyizolować i przetestować mały fragment kodu.
#
# Wyobraźmy sobie prosty projekt AI, napisany w jednym pliku.

# --- PRZYKŁAD "ZŁEJ" ORGANIZACJI: WSZYSTKO W JEDNYM MIEJSCU ---

import random

# Funkcja pomocnicza, która mogłaby być gdzie indziej
def uzyskaj_pogode(miasto):
    print(f"Łączę się z serwisem pogodowym dla miasta {miasto}...")
    temperatury = {"Warszawa": 15, "Kraków": 18, "Online": 20}
    return temperatury.get(miasto, "Nie znam pogody dla tego miasta.")

# Główna klasa logiki AI
class AsystentAI:
    def __init__(self, imie):
        self.imie = imie
        
    def przywitaj_sie(self):
        print(f"Cześć, jestem {self.imie}, Twój osobisty asystent AI.")
        
    def przetworz_polecenie(self, polecenie):
        if "pogoda" in polecenie:
            # Logika biznesowa miesza się z logiką pomocniczą
            miasto = polecenie.split("w ")[-1]
            pogoda = uzyskaj_pogode(miasto)
            print(f"Odpowiedź AI: {pogoda}")
        elif "żart" in polecenie:
            zarty = ["Dlaczego programiści mylą Halloween z Bożym Narodzeniem? Bo OCT 31 == DEC 25.", "Co mówi wąż programista? Sssssss-sharp."]
            print(f"Odpowiedź AI: {random.choice(zarty)}")
        else:
            print("Odpowiedź AI: Nie rozumiem polecenia.")

# Główna część programu (uruchomienie)
# print("\n--- Uruchamiam program w jednym pliku ---")
# moj_asystent = AsystentAI("Zenek")
# moj_asystent.przywitaj_sie()
# moj_asystent.przetworz_polecenie("jaka jest pogoda w Warszawa")
# moj_asystent.przetworz_polecenie("opowiedz żart")

# Powyższy kod działa, ale jest sztywny i nieuporządkowany.


# 2. Rozwiązanie: Moduły – czyli pliki jako zestawy narzędzi
#
# Modułowość polega na dzieleniu kodu na mniejsze, logiczne pliki (moduły).
# Znasz już to! `import math`, `import requests` - to wszystko było importowanie modułów.
#
# Kluczowa informacja: KAŻDY PLIK .PY W TWOIM PROJEKCIE MOŻE BYĆ MODUŁEM!
#
# Stwórzmy teraz logiczną strukturę dla naszego projektu. Wyobraź sobie, że tworzymy
# następujące pliki w jednym folderze:
#
# my_ai_project/
# ├── main.py          # Główny plik, który uruchamia program.
# ├── ai_core.py       # Definicja naszej głównej klasy AsystentAI.
# └── utils.py         # Funkcje pomocnicze (jak pogoda, operacje na tekście itp.).

# Poniżej symulujemy zawartość tych plików.

# --- Plik: utils.py ---
# Ten plik zawiera użyteczne, samodzielne funkcje.

def uzyskaj_pogode_z_modulu(miasto):
    """
    Zwraca symulowaną temperaturę dla danego miasta.
    Funkcja jest teraz w osobnym pliku 'utils.py'.
    """
    print(f"Funkcja z utils.py: Łączę się z serwisem pogodowym dla miasta {miasto}...")
    temperatury = {"Warszawa": 15, "Kraków": 18, "Online": 20}
    return temperatury.get(miasto, "Nie znam pogody dla tego miasta.")

def powiedz_zart_z_modulu():
    """Zwraca losowy żart."""
    zarty = ["Dlaczego programiści mylą Halloween z Bożym Narodzeniem? Bo OCT 31 == DEC 25.", "Co mówi wąż programista? Sssssss-sharp."]
    return random.choice(zarty)

# --- Plik: ai_core.py ---
# Ten plik definiuje główną logikę naszej aplikacji.

# Importujemy funkcje z naszego WŁASNEGO modułu `utils.py`!
# (W prawdziwym projekcie te pliki leżałyby obok siebie)
# from utils import uzyskaj_pogode_z_modulu, powiedz_zart_z_modulu

class LepszyAsystentAI:
    def __init__(self, imie):
        self.imie = imie
        
    def przywitaj_sie(self):
        print(f"Cześć, jestem {self.imie}, Twój modułowy asystent AI.")
        
    def przetworz_polecenie(self, polecenie):
        if "pogoda" in polecenie:
            miasto = polecenie.split("w ")[-1]
            # Wywołujemy zaimportowaną funkcję!
            pogoda = uzyskaj_pogode_z_modulu(miasto)
            print(f"Odpowiedź AI: {pogoda}")
        elif "żart" in polecenie:
            # Wywołujemy drugą zaimportowaną funkcję!
            zart = powiedz_zart_z_modulu()
            print(f"Odpowiedź AI: {zart}")
        else:
            print("Odpowiedź AI: Nie rozumiem polecenia.")

# --- Plik: main.py ---
# Ten plik jest teraz czysty, krótki i służy tylko do "orkiestracji" -
# czyli łączenia klocków i uruchamiania całości.

# Importujemy klasę z naszego modułu `ai_core.py`
# from ai_core import LepszyAsystentAI

def uruchom_aplikacje():
    print("\n--- Uruchamiam program w wersji modułowej ---")
    
    # Tworzymy obiekt asystenta
    # moj_lepszy_asystent = LepszyAsystentAI("Zenek")
    # moj_lepszy_asystent.przywitaj_sie()
    
    # Symulujemy interakcję z użytkownikiem
    # moj_lepszy_asystent.przetworz_polecenie("jaka jest pogoda w Kraków")
    # moj_lepszy_asystent.przetworz_polecenie("opowiedz żart")


# 3. Magiczne `if __name__ == "__main__":`
#
# Został nam jeden problem. Co, jeśli chcemy, aby plik `utils.py` był jednocześnie
# modułem do importowania ORAZ samodzielnym skryptem do testowania?
#
# Python ma specjalną zmienną `__name__`.
#   - Jeśli uruchamiasz plik BEZPOŚREDNIO (np. `python utils.py`), to `__name__` ma w nim wartość `"__main__"`.
#   - Jeśli IMPORTUJESZ plik do innego (np. `import utils`), to `__name__` ma w nim wartość `"utils"` (nazwa pliku).
#
# Używamy tej wiedzy, aby oddzielić kod "do uruchomienia" od kodu "do importu".

# --- Plik: utils_z_zabezpieczeniem.py ---
def jakas_funkcja():
    return "To jest funkcja do importu."

# Ten blok kodu wykona się TYLKO, gdy uruchomimy ten plik bezpośrednio.
# NIE wykona się, gdy go zaimportujemy.
if __name__ == "__main__":
    print("Uruchomiłeś ten plik bezpośrednio!")
    print("Służy to do testowania funkcji z tego modułu.")
    wynik = jakas_funkcja()
    print(f"Test funkcji: {wynik}")



# 4. Podsumowanie – Zasady dobrej organizacji
#
# Dzielenie kodu na moduły to klucz do tworzenia skalowalnych i profesjonalnych aplikacji AI.
#
#     * Jedna odpowiedzialność: Każdy plik (moduł) powinien odpowiadać za jedną, logiczną część programu
#       (np. `utils.py` za narzędzia, `data_loader.py` za ładowanie danych, `model.py` za logikę modelu).
#
#     * Czysty punkt wejścia: Twój główny plik (`main.py`) powinien być krótki i czytelny.
#       Jego zadaniem jest importowanie potrzebnych komponentów i ich uruchomienie.
#
#     * Używaj `if __name__ == "__main__":`: Zabezpieczaj kod przeznaczony do testowania lub
#       bezpośredniego uruchomienia, aby nie wykonywał się przy imporcie.
#
#     * Myśl o przyszłości: Nawet mały projekt warto zacząć od podziału na 2-3 pliki.
#       To dobry nawyk, który zaprocentuje, gdy projekt urośnie.
#
# Masz teraz solidne fundamenty Pythona,
# które pozwolą Ci przejść do bardziej zaawansowanych zagadnień i bibliotek
# kluczowych w świecie sztucznej inteligencji.
#