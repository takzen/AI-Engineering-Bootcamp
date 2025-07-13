# Moduł 3, Lekcja 19: Co to jest Pydantic i dlaczego jest ważny?
#
#
#
# Witaj w Module 3! Wkraczamy w świat budowania profesjonalnych aplikacji AI.
# A fundamentem każdej dobrej aplikacji jest... jakość danych.
#
# Zasada "Garbage In, Garbage Out" (śmieci na wejściu, śmieci na wyjściu) jest w AI
# święta. Jeśli Twój model otrzyma dane w złym formacie, o złym typie lub
# niekompletne, jego predykcje będą bezwartościowe.
#
# Jak więc upewnić się, że dane, które wchodzą do naszego systemu (np. z API,
# pliku konfiguracyjnego, bazy danych), są dokładnie takie, jakich oczekujemy?
#
# Odpowiedzią jest Pydantic.
#
# 1. Problem: Zaufanie danym w dynamicznym świecie Pythona
#
# Python jest językiem dynamicznie typowanym. To znaczy, że nie musimy
# deklarować typów zmiennych. To wygodne, ale też ryzykowne.
#
# Zobaczmy problem na przykładzie funkcji przetwarzającej dane o użytkowniku.
def przetworz_uzytkownika_zle(dane: dict):
    # Spodziewamy się, że 'wiek' jest liczbą, a 'email' ma poprawny format.
    try:
        if dane['wiek'] > 18:
            print(f"{dane['imie']} jest pełnoletni/a.")
        # ... i tak dalej, mnóstwo ręcznych sprawdzeń i obsługi błędów
    except KeyError as e:
        print(f"Błąd! Brak klucza w danych: {e}")
    except TypeError as e:
        print(f"Błąd! Niepoprawny typ danych: {e}")

dane_dobre = {"imie": "Anna", "wiek": 25, "email": "anna@example.com"}
dane_zle_typ = {"imie": "Piotr", "wiek": "trzydzieści", "email": "piotr@example.com"} # wiek jako string
dane_brak_klucza = {"imie": "Zofia", "email": "zofia@example.com"} # brak wieku

print("--- Problem: Ręczna walidacja ---")
przetworz_uzytkownika_zle(dane_dobre)
przetworz_uzytkownika_zle(dane_zle_typ) # To spowoduje TypeError
przetworz_uzytkownika_zle(dane_brak_klucza) # To spowoduje KeyError

# Pisanie takich zabezpieczeń ręcznie jest żmudne, podatne na błędy i zaśmieca kod.
#
#
# 2. Pydantic – Strażnik poprawności danych
#
# Pydantic to biblioteka, która wykorzystuje standardowe podpowiedzi typów (type hints)
# w Pythonie do walidacji, parsowania i serializacji danych w czasie rzeczywistym.
#
# Pomyśl o Pydanticu jak o surowym, ale sprawiedliwym "strażniku" na wejściu do Twojej
# aplikacji. Sprawdza on "dowód osobisty" (typ) i "format" każdych danych, zanim
# wpuści je do środka.
#
# WAŻNE: Przed uruchomieniem, upewnij się, że masz zainstalowany pydantic.
# W terminalu/wierszu poleceń wpisz:
# pip install pydantic
#
# Jak to działa? Definiujemy strukturę naszych danych za pomocą klasy,
# która dziedziczy po `BaseModel` z Pydantica.

from pydantic import BaseModel, ValidationError

# Definiujemy "schemat" naszych danych za pomocą klasy
class Uzytkownik(BaseModel):
    imie: str
    wiek: int
    email: str
    jest_aktywny: bool = True # Możemy podać wartości domyślne

# 2.1 Walidacja danych
print("\n--- Rozwiązanie: Walidacja z Pydantic ---")
try:
    # Pydantic automatycznie sparsuje słownik i stworzy obiekt
    uzytkownik1 = Uzytkownik(**dane_dobre)
    print(f"Sukces! Stworzono obiekt użytkownika: {uzytkownik1.imie}, wiek: {uzytkownik1.wiek}")
    print(f"Czy jest aktywny? {uzytkownik1.jest_aktywny}") # Użyto wartości domyślnej

    # Teraz spróbujmy z niepoprawnymi danymi
    # Pydantic automatycznie wykryje błędy i rzuci jeden, czytelny wyjątek.
    print("\nPróba stworzenia obiektu z niepoprawnymi danymi...")
    uzytkownik_zly = Uzytkownik(**dane_zle_typ)
    
except ValidationError as e:
    print("Błąd walidacji Pydantic!")
    # Wyjątek 'e' zawiera bardzo szczegółowe informacje o błędach w formacie JSON
    print(e.json())

#
# 3. "Magia" Pydantica – Parsowanie i Serializacja
#
# Pydantic robi więcej niż tylko walidację.
#
#     * Inteligentne parsowanie (coercion): Pydantic próbuje "naprawić" dane.
#       Jeśli oczekuje `int`, a dostanie string `"25"`, automatycznie go skonwertuje.

dane_do_naprawy = {"imie": "Tomasz", "wiek": "42", "email": "tomasz@example.com"}
uzytkownik_naprawiony = Uzytkownik(**dane_do_naprawy)
print(f"\n--- Parsowanie danych ---")
print(f"Typ wieku po parsowaniu: {type(uzytkownik_naprawiony.wiek)}") # <class 'int'>!

#     * Serializacja: Pydantic potrafi łatwo przekształcić obiekt z powrotem
#       na słownik lub string w formacie JSON.

# .model_dump() - zamienia obiekt na słownik Pythona
slownik_z_obiektu = uzytkownik_naprawiony.model_dump()
print(f"\n--- Serializacja ---")
print(f"Obiekt zamieniony na słownik: {slownik_z_obiektu}")

# .model_dump_json() - zamienia obiekt na string JSON
json_z_obiektu = uzytkownik_naprawiony.model_dump_json(indent=2) # indent dla ładnego formatowania
print(f"Obiekt zamieniony na JSON:\n{json_z_obiektu}")

#
# 4. Pydantic w akcji – Integracja z FastAPI
#
# Pamiętasz, jak tworzyliśmy API za pomocą FastAPI? FastAPI używa Pydantica
# pod spodem do walidacji danych przychodzących i wychodzących!
#
# Gdy w FastAPI definiujesz ciało zapytania (request body) za pomocą modelu Pydantic,
# FastAPI automatycznie:
#   1. Weryfikuje, czy przychodzący JSON pasuje do Twojego modelu.
#   2. Jeśli nie, automatycznie odsyła klientowi czytelny błąd 422.
#   3. Jeśli tak, konwertuje JSON na obiekt Pydantic i przekazuje go do Twojej funkcji.
#   4. Używa modelu do automatycznego generowania dokumentacji API (Swagger/OpenAPI).
#
# To połączenie czyni budowanie solidnych, dobrze udokumentowanych API
# w Pythonie niezwykle prostym i przyjemnym.
#
#
# 5. Podsumowanie
#
#     * Pydantic to biblioteka do walidacji, parsowania i serializacji danych.
#     * Gwarantuje, że dane w Twojej aplikacji mają poprawny typ i strukturę.
#     * Definiujemy schemat danych, tworząc klasę dziedziczącą po `BaseModel`.
#     * Pydantic automatycznie konwertuje dane (np. string na int) tam, gdzie to możliwe.
#     * Umożliwia łatwą konwersję obiektów do słowników i JSON-a.
#     * Jest fundamentem nowoczesnych frameworków webowych, takich jak FastAPI.
#
# Używanie Pydantica to jeden z najlepszych sposobów na podniesienie jakości
# i niezawodności Twoich projektów AI, zapewniając, że do Twoich modeli
# i algorytmów trafiają tylko czyste, poprawne dane.
#