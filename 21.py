# Moduł 3, Lekcja 21: Walidacja danych – najlepsze praktyki
#
#
#
# Opanowaliśmy już tworzenie modeli danych w Pydantic, używając wbudowanych typów
# i `Field` do podstawowej walidacji. Ale co, jeśli nasze reguły biznesowe
# są bardziej skomplikowane?
#
#     - Co, jeśli hasło musi zawierać co najmniej jedną cyfrę?
#     - Co, jeśli data końcowa projektu nie może być wcześniejsza niż data początkowa?
#     - Co, jeśli chcemy automatycznie oczyścić i sformatować dane wejściowe?
#
# Dziś poznamy zaawansowane techniki walidacji, które pozwolą nam obsłużyć
# praktycznie każdy scenariusz. To one czynią Pydantic tak potężnym narzędziem.
#
# 1. Walidatory niestandardowe – dekorator `@validator`
#
# Gdy potrzebujemy własnej logiki walidacji dla konkretnego pola, używamy
# dekoratora `@validator`. Jest to funkcja, która otrzymuje wartość pola i musi
# ją zwrócić po walidacji (lub rzucić błąd `ValueError`).
#
# UWAGA: Dekorator `@validator` jest uznawany za przestarzały (deprecated) w Pydantic v2
# na rzecz `@field_validator`. Jednak wciąż jest bardzo powszechny w istniejących
# projektach, dlatego warto go znać. Pokażemy oba podejścia.

from pydantic import BaseModel, ValidationError, field_validator, validator
from datetime import date

class RejestracjaUzytkownika(BaseModel):
    nazwa_uzytkownika: str
    haslo: str

    # Pydantic v2 (zalecane podejście)
    @field_validator('haslo')
    @classmethod
    def waliduj_haslo(cls, v: str) -> str:
        # v to wartość pola 'haslo'
        if len(v) < 8:
            raise ValueError("Hasło musi mieć co najmniej 8 znaków.")
        if not any(char.isdigit() for char in v):
            raise ValueError("Hasło musi zawierać co najmniej jedną cyfrę.")
        return v
    
    # Dla porównania - Pydantic v1 (przestarzałe, ale wciąż spotykane)
    # @validator('nazwa_uzytkownika')
    # def waliduj_nazwe_uzytkownika(cls, v):
    #     if ' ' in v:
    #         raise ValueError('Nazwa użytkownika nie może zawierać spacji.')
    #     return v

print("--- 1. Walidatory niestandardowe ---")
try:
    # Poprawne dane
    user1 = RejestracjaUzytkownika(nazwa_uzytkownika="anna_kowalska", haslo="super_tajne123")
    print(f"Sukces! Użytkownik '{user1.nazwa_uzytkownika}' zarejestrowany.")

    # Niepoprawne hasło (za krótkie)
    print("\nPróba rejestracji z za krótkim hasłem...")
    RejestracjaUzytkownika(nazwa_uzytkownika="piotr_nowak", haslo="tajne")
except ValidationError as e:
    print(f"Błąd walidacji: {e.errors()}")

try:
    # Niepoprawne hasło (brak cyfry)
    print("\nPróba rejestracji z hasłem bez cyfry...")
    RejestracjaUzytkownika(nazwa_uzytkownika="zofia_zielinska", haslo="bardzodlugiehaslo")
except ValidationError as e:
    print(f"Błąd walidacji: {e.errors()}")

#
# 2. Walidacja zależy od innych pól – dekorator `@model_validator`
#
# Często reguła walidacji dotyczy relacji między kilkoma polami. Na przykład
# data zakończenia nie może być wcześniejsza niż data rozpoczęcia.
# Do tego służy dekorator `@model_validator`.

from pydantic import model_validator

class ProjektAI(BaseModel):
    nazwa_projektu: str
    data_rozpoczecia: date
    data_zakonczenia: date

    # Ten walidator uruchamia się PO walidacji poszczególnych pól.
    @model_validator(mode='after')
    def waliduj_daty(self) -> 'ProjektAI':
        # Mamy tu dostęp do całego obiektu (self)
        start = self.data_rozpoczecia
        koniec = self.data_zakonczenia

        if start and koniec and koniec < start:
            raise ValueError("Data zakończenia nie może być wcześniejsza niż data rozpoczęcia.")
        
        return self # Zawsze musimy zwrócić obiekt 'self'

print("\n--- 2. Walidacja między polami ---")
try:
    # Poprawne daty
    projekt1 = ProjektAI(
        nazwa_projektu="Analiza sentymentu",
        data_rozpoczecia=date(2023, 1, 1),
        data_zakonczenia=date(2023, 6, 30)
    )
    print(f"Sukces! Stworzono projekt '{projekt1.nazwa_projektu}'.")

    # Niepoprawne daty
    print("\nPróba stworzenia projektu z niepoprawnymi datami...")
    ProjektAI(
        nazwa_projektu="Wykrywanie anomalii",
        data_rozpoczecia=date(2024, 1, 1),
        data_zakonczenia=date(2023, 12, 31)
    )
except ValidationError as e:
    print(f"Błąd walidacji: {e.errors()}")

#
# 3. Transformacja danych wejściowych (Sanitization)
#
# Walidatory mogą nie tylko sprawdzać dane, ale również je modyfikować
# (oczyszczać, formatować). To niezwykle przydatne, aby zapewnić spójność danych
# w całej aplikacji.

class Artykul(BaseModel):
    tytul: str
    tagi: list[str]

    # Użyjemy walidatora do oczyszczenia i sformatowania danych wejściowych
    @field_validator('tytul')
    @classmethod
    def oczysc_tytul(cls, v: str) -> str:
        # Usuwamy białe znaki i zamieniamy pierwszą literę na wielką
        return v.strip().capitalize()

    @field_validator('tagi', mode='before')
    @classmethod
    def rozdziel_tagi(cls, v: str | list[str]) -> list[str]:
        # Pozwalamy na podanie tagów jako pojedynczego stringa oddzielonego przecinkami
        if isinstance(v, str):
            # Dzielimy string, usuwamy białe znaki z każdego tagu i puste tagi
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v

print("\n--- 3. Transformacja danych ---")
# Dane wejściowe są "brudne" - dodatkowe spacje, zła wielkość liter, tagi jako string
brudne_dane = {
    "tytul": "  jak pydantic ułatwia życie analityka  ",
    "tagi": "  python, ai, pydantic, , data science "
}
artykul = Artykul(**brudne_dane)

print(f"Oczyszczony tytuł: '{artykul.tytul}'")
print(f"Sparsowane tagi: {artykul.tagi}")
print(f"Typ tagów: {type(artykul.tagi)}") # <class 'list'>

#
# 4. Podsumowanie – Najlepsze praktyki
#
#     1. Bądź precyzyjny: Używaj jak najbardziej szczegółowych typów (`date`, `EmailStr`)
#        i ograniczeń (`Field`) – Pydantic zrobi większość pracy za Ciebie.
#
#     2. Walidacja pojedynczych pól: Gdy potrzebujesz niestandardowej logiki dla jednego pola,
#        użyj `@field_validator`.
#
#     3. Walidacja relacji między polami: Gdy reguła zależy od wielu pól,
#        użyj `@model_validator`.
#
#     4. Czyść dane na wejściu: Używaj walidatorów do normalizacji i formatowania danych
#        (sanitization), aby Twoja aplikacja pracowała na spójnych, czystych danych.
#
#     5. Nie powtarzaj się (DRY): Jeśli masz złożoną regułę walidacji używaną w wielu
#        miejscach, rozważ stworzenie własnego, reużywalnego typu za pomocą adnotacji.
#        (to bardziej zaawansowany temat).
#
# Opanowanie tych technik pozwala budować niezwykle solidne i bezpieczne "potoki danych" (data pipelines),
# co jest absolutnie kluczowe w każdym poważnym projekcie AI.
#