# Moduł 2, Punkt 11: Wprowadzenie do programowania obiektowego (OOP)
#
#
#
# Do tej pory pisaliśmy kod w sposób proceduralny – tworzyliśmy dane (zmienne, listy)
# i osobno pisaliśmy funkcje, które na tych danych operowały.
# Programowanie obiektowe (ang. Object-Oriented Programming, OOP) to inny, potężny paradygmat.
# Polega on na modelowaniu problemów za pomocą "obiektów", które łączą w sobie
# zarówno dane, jak i zachowania (funkcje).
#
# 1. Czym jest Programowanie Obiektowe?
#
# Wyobraź sobie, że chcesz opisać samochód w swoim programie.
#
#     * Dane (cechy): kolor, marka, model, aktualna prędkość, ilość paliwa.
#     * Zachowania (co potrafi robić): przyspieszać, hamować, trąbić, włączać światła.
#
# W OOP tworzymy "szablon" lub "przepis" na samochód, który nazywamy KLASĄ.
# Na podstawie tego jednego szablonu możemy potem stworzyć wiele konkretnych,
# istniejących samochodów – te konkretne egzemplarze nazywamy OBIEKTAMI (lub instancjami).
#
#     * Klasa (Class): To szablon, przepis, plan (np. plan architektoniczny domu).
#                      Definiuje, jakie cechy (dane) i zachowania (metody) będzie miał każdy obiekt tego typu.
#
#     * Obiekt (Object / Instance): To konkretny, istniejący egzemplarz stworzony na podstawie klasy
#                                   (np. konkretny dom zbudowany wg planu). Każdy obiekt ma własny zestaw danych.
#
#     * Atrybut (Attribute): To cecha, dana przechowywana w obiekcie (np. `kolor = 'czerwony'`). To jak zmienna "wewnątrz" obiektu.
#
#     * Metoda (Method): To zachowanie, funkcja "wewnątrz" obiektu (np. `przyspiesz()`). Metody mogą modyfikować atrybuty obiektu.
#
#
# 2. Tworzenie pierwszej klasy – słowo kluczowe `class`
#
# Do tworzenia klas używamy słowa kluczowego `class`. Nazwy klas w Pythonie
# przyjęło się pisać wielką literą, w stylu `PascalCase` (np. `MojaSuperKlasa`).

# Definicja najprostszej możliwej klasy 'Pies'
class Pies:
    pass # 'pass' oznacza, że klasa jest na razie pusta

# Tworzenie dwóch obiektów (instancji) klasy Pies
azor = Pies()
burek = Pies()

print(type(azor)) # <class '__main__.Pies'> - Python wie, że 'azor' to obiekt klasy Pies
print(azor)       # <__main__.Pies object at 0x...> - widzimy, że to obiekt w pamięci
print(burek)      # <__main__.Pies object at 0x...> - to INNY obiekt w innym miejscu pamięci


# 3. Konstruktor `__init__` i atrybuty obiektu (`self`)
#
# Nasza klasa `Pies` jest na razie bezużyteczna. Jak nadać obiektom ich unikalne cechy (atrybuty)?
# Służy do tego specjalna metoda o nazwie `__init__` (dwa podkreślenia z każdej strony).
#
#     `__init__`: To tzw. "konstruktor". Jest to metoda, która uruchamia się AUTOMATYCZNIE
#                 za każdym razem, gdy tworzymy nowy obiekt danej klasy.
#
#     `self`: To najważniejsze i często najtrudniejsze do zrozumienia słowo w OOP. `self` to
#             odniesienie do KONKRETNEJ INSTANCJI (obiektu), na której pracujemy.
#             Gdy piszemy `self.imie = "Azor"`, mówimy Pythonowi: "dla TEGO konkretnego psa,
#             ustaw jego atrybut 'imie' na 'Azor'".

class Pies:
    # Definicja konstruktora
    def __init__(self, imie_psa, rasa_psa, wiek_psa):
        # Komunikat, żeby zobaczyć, kiedy __init__ się wykonuje
        print(f"Tworzę nowego psa! Witaj, {imie_psa}!")
        
        # Przypisujemy dane wejściowe do atrybutów TEGO konkretnego obiektu (self)
        self.imie = imie_psa
        self.rasa = rasa_psa
        self.wiek = wiek_psa

# Teraz, tworząc obiekt, musimy podać argumenty do metody __init__
azor = Pies("Azor", "Owczarek niemiecki", 5)
burek = Pies("Burek", "Mieszaniec", 3)

# Możemy teraz odwoływać się do atrybutów każdego obiektu za pomocą kropki
print(f"Mój pierwszy pies to {azor.imie}, ma {azor.wiek} lat i jest rasy {azor.rasa}.")
print(f"Mój drugi pies to {burek.imie}, ma {burek.wiek} lat i jest rasy {burek.rasa}.")


# 4. Metody – Co obiekty potrafią robić
#
# Metody to funkcje zdefiniowane wewnątrz klasy. Zawsze przyjmują `self` jako pierwszy argument,
# co daje im dostęp do atrybutów danego obiektu.

class Samochod:
    def __init__(self, marka, model):
        self.marka = marka
        self.model = model
        self.predkosc = 0 # Domyślny atrybut, ustawiany bez argumentu

    # Metoda do "przedstawiania się" obiektu
    def przedstaw_sie(self):
        print(f"Jestem samochodem marki {self.marka}, model {self.model}.")

    # Metoda, która modyfikuje stan obiektu (jego atrybuty)
    def przyspiesz(self, wartosc):
        self.predkosc += wartosc
        print(f"Przyspieszam! Moja aktualna prędkość to {self.predkosc} km/h.")

    def zatrzymaj(self):
        self.predkosc = 0
        print("Zatrzymuję się.")


# Tworzymy obiekt
moje_auto = Samochod("Ford", "Mustang")

# Wywołujemy jego metody
moje_auto.przedstaw_sie()
moje_auto.przyspiesz(50)
moje_auto.przyspiesz(30)
moje_auto.zatrzymaj()
print(f"Prędkość po zatrzymaniu: {moje_auto.predkosc}")


# 5. Dlaczego OOP jest przydatne w analizie danych?
#
# Może się to wydawać abstrakcyjne, ale w rzeczywistości biblioteki, których będziesz używać
# (jak `pandas`), są w całości zbudowane w oparciu o OOP!
#
# Pomyśl o obiekcie DataFrame z biblioteki pandas:
#   `df = pd.read_csv("dane.csv")`
#
#     * `df` to obiekt.
#     * Dane w pliku CSV stają się jego atrybutami (wewnętrzną tabelą).
#     * `df.head()`, `df.describe()`, `df.groupby()` to wszystko METODY tego obiektu,
#       które operują na jego wewnętrznych danych.
#
# OOP pozwala na **enkapsulację** – spakowanie danych i operacji na nich w jeden, logiczny,
# łatwy w użyciu byt. Dzięki temu kod jest o wiele bardziej zorganizowany i czytelny.
#
# 6. Podsumowanie
#
#     * Programowanie Obiektowe modeluje świat za pomocą klas (szablonów) i obiektów (instancji).
#     * Klasa definiuje atrybuty (dane) i metody (zachowania).
#     * `__init__` to specjalna metoda (konstruktor), która inicjalizuje nowy obiekt.
#     * `self` to odniesienie do konkretnego obiektu, na którym pracujemy.
#     * Metody to funkcje wewnątrz klasy, które operują na atrybutach obiektu (`self`).
#     * OOP pomaga organizować skomplikowany kod, czyniąc go bardziej intuicyjnym i reużywalnym.
#
# To tylko wierzchołek góry lodowej, ale te podstawy pozwolą Ci zrozumieć, jak zbudowane
# są zaawansowane narzędzia do analizy danych i jak w przyszłości tworzyć własne,
# złożone struktury do przetwarzania informacji.
#