# Moduł 3, Lekcja 20: Tworzenie modeli danych w Pydantic
#
#
#
# W poprzedniej lekcji dowiedzieliśmy się, czym jest Pydantic i dlaczego walidacja
# danych jest tak kluczowa. Stworzyliśmy prosty model `Uzytkownik`.
#
# Jednak w realnych projektach AI i data science, dane rzadko są tak proste.
# Są zagnieżdżone, zawierają listy innych obiektów, mają opcjonalne pola i wymagają
# niestandardowej walidacji. Dziś nauczymy się, jak modelować takie złożone struktury.
#
# 1. Zagnieżdżone modele (Nested Models)
#
# Często jeden obiekt zawiera w sobie inny. Na przykład, zamówienie w sklepie
# internetowym zawiera informacje o produkcie i dane klienta.
# W Pydanticu możemy po prostu użyć jednej klasy modelu jako typu w innej.

from pydantic import BaseModel, ValidationError, Field, EmailStr
from typing import List, Optional

class Adres(BaseModel):
    ulica: str
    miasto: str
    kod_pocztowy: str

class Klient(BaseModel):
    id_klienta: int
    imie: str
    # Atrybut `adres_dostawy` jest typu `Adres`, czyli innej klasy Pydantic!
    adres_dostawy: Adres

# Przykładowe dane w formacie, jaki moglibyśmy dostać z API (JSON jako słownik)
dane_zamowienia_json = {
    "id_klienta": 101,
    "imie": "Jan Kowalski",
    "adres_dostawy": {
        "ulica": "Marszałkowska 1",
        "miasto": "Warszawa",
        "kod_pocztowy": "00-001"
    }
}

print("--- 1. Zagnieżdżone modele ---")
try:
    klient = Klient(**dane_zamowienia_json)
    print("Sukces! Sparsowano zagnieżdżone dane.")
    print(f"Imię klienta: {klient.imie}")
    print(f"Miasto dostawy: {klient.adres_dostawy.miasto}")
    print(f"Typ adresu dostawy: {type(klient.adres_dostawy)}") # <class '__main__.Adres'>
except ValidationError as e:
    print(f"Błąd walidacji: {e}")

#
# 2. Listy i typy generyczne
#
# Co jeśli zamówienie zawiera listę produktów? Pythonowy moduł `typing`
# pozwala nam definiować bardziej złożone typy, jak `List` czy `Optional`.
#
#     * `List[Typ]`: Oznacza listę, której wszystkie elementy muszą być danego typu.
#     * `Optional[Typ]`: Oznacza, że pole może mieć dany typ LUB być `None`.
#                        Jest to skrót na `Union[Typ, None]`.

class Produkt(BaseModel):
    nazwa: str
    cena: float
    id_produktu: int

class Zamowienie(BaseModel):
    id_zamowienia: str
    klient: Klient # Używamy zagnieżdżonego modelu zdefiniowanego wyżej
    # Pole `produkty` to lista obiektów klasy `Produkt`
    produkty: List[Produkt]
    # Pole `kod_rabatowy` jest opcjonalne
    kod_rabatowy: Optional[str] = None

dane_pelnego_zamowienia = {
    "id_zamowienia": "ZAM-2023-XYZ",
    "klient": dane_zamowienia_json, # Możemy tu wstawić słownik, Pydantic go sparsuje
    "produkty": [
        {"nazwa": "Laptop AI PowerBook", "cena": 7999.99, "id_produktu": 1},
        {"nazwa": "Myszka analityka", "cena": 149.50, "id_produktu": 2}
    ],
    "kod_rabatowy": "WIOSNA2023"
}

print("\n--- 2. Listy i typy opcjonalne ---")
try:
    zamowienie = Zamowienie(**dane_pelnego_zamowienia)
    print("Sukces! Sparsowano pełne zamówienie.")
    print(f"ID zamówienia: {zamowienie.id_zamowienia}")
    print(f"Liczba produktów w zamówieniu: {len(zamowienie.produkty)}")
    print(f"Nazwa pierwszego produktu: {zamowienie.produkty[0].nazwa}")
    print(f"Kod rabatowy: {zamowienie.kod_rabatowy}")

    # A co, jeśli brakuje pola opcjonalnego?
    dane_bez_rabatu = dane_pelnego_zamowienia.copy()
    del dane_bez_rabatu["kod_rabatowy"]
    zamowienie_bez_rabatu = Zamowienie(**dane_bez_rabatu)
    print(f"Kod rabatowy (gdy brak): {zamowienie_bez_rabatu.kod_rabatowy}") # Będzie None
except ValidationError as e:
    print(f"Błąd walidacji: {e}")

#
# 3. Zaawansowana walidacja za pomocą `Field` i typów specjalnych
#
# Pydantic oferuje o wiele więcej niż tylko sprawdzanie typów. Możemy walidować
# format i zakres wartości.
#
#     * `Field`: Pozwala dodać dodatkowe metadane i reguły walidacji do pola.
#     * Typy specjalne: Pydantic ma wbudowane typy do walidacji popularnych formatów.

class UzytkownikAI(BaseModel):
    # gt = greater than (większe niż), le = less than or equal (mniejsze lub równe)
    id_uzytkownika: int = Field(gt=0, description="Unikalny identyfikator użytkownika.")
    nazwa_uzytkownika: str = Field(min_length=3, max_length=50)
    # Używamy specjalnego typu EmailStr do automatycznej walidacji formatu email
    email: EmailStr
    # ge = greater than or equal (większe lub równe)
    poziom_doswiadczenia: int = Field(ge=1, le=5, default=1)

print("\n--- 3. Zaawansowana walidacja z Field ---")
try:
    # Poprawne dane
    user1 = UzytkownikAI(id_uzytkownika=1, nazwa_uzytkownika="ann_ai", email="ann.ai@example.com")
    print(f"Sukces! Stworzono użytkownika: {user1.nazwa_uzytkownika}")

    # Niepoprawne dane - za krótka nazwa użytkownika
    print("\nPróba stworzenia obiektu z za krótką nazwą...")
    user_zly_login = UzytkownikAI(id_uzytkownika=2, nazwa_uzytkownika="ai", email="ai@example.com")
except ValidationError as e:
    print("Błąd walidacji Pydantic!")
    print(e.errors()) # .errors() daje bardziej zwięzłą listę błędów

try:
    # Niepoprawne dane - id nie jest większe od 0
    print("\nPróba stworzenia obiektu z niepoprawnym ID...")
    user_zle_id = UzytkownikAI(id_uzytkownika=0, nazwa_uzytkownika="admin", email="admin@example.com")
except ValidationError as e:
    print("Błąd walidacji Pydantic!")
    print(e.errors())

#
# 4. Podsumowanie
#
# Umiejętność precyzyjnego modelowania danych to fundament solidnych aplikacji.
# Dzięki Pydanticowi możemy robić to w sposób deklaratywny, czysty i bezpieczny.
#
#     * Zagnieżdżone modele: Możemy tworzyć złożone struktury, używając jednej klasy
#       Pydantic jako typu pola w innej.
#
#     * Typy generyczne: Używamy `List[Typ]` do walidacji list obiektów oraz `Optional[Typ]`
#       do definiowania pól, które mogą być puste (`None`).
#
#     * Zaawansowana walidacja: `Field` pozwala nam określić dodatkowe ograniczenia
#       (np. minimalną długość, zakres liczbowy), a specjalne typy (jak `EmailStr`)
#       automatycznie sprawdzają poprawność formatu.
#
# Te techniki pozwalają nam zdefiniować bardzo precyzyjny "kontrakt" na dane,
# co drastycznie zmniejsza liczbę błędów i upraszcza logikę w dalszej części aplikacji.
#