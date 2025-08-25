# Moduł 3, Lekcja 22: Serializacja i deserializacja JSON
#
#
#
# W dzisiejszym świecie programy nieustannie wymieniają się danymi:
# - Aplikacja webowa komunikuje się z serwerem.
# - Skrypt Pythona odpytuje model AI przez API.
# - Program zapisuje swoją konfigurację do pliku.
#
# Aby ta wymiana była możliwa, obiekty i struktury danych z pamięci komputera
# (np. słowniki, listy Pythona) muszą zostać przetłumaczone na format, który
# można łatwo przesłać przez sieć lub zapisać do pliku.
#
# Ten proces nazywamy SERIALIZACJĄ. Proces odwrotny – odtwarzanie obiektów
# z tego formatu – to DESERIALIZACJA.
#
# Najpopularniejszym formatem wymiany danych w internecie jest JSON.
#
# 1. Co to jest JSON (JavaScript Object Notation)?
#
# JSON to lekki, tekstowy format zapisu danych, który jest bardzo czytelny
# zarówno dla ludzi, jak i dla maszyn. Jego składnia jest bardzo podobna
# do słowników i list w Pythonie.
#
# Przykład JSON:

"""
{
  "imie": "Anna",
  "wiek": 30,
  "jestStudentem": false,
  "kursy": ["Python dla AI", "Analiza Danych"],
  "adres": {
    "ulica": "Polna",
    "miasto": "Poznań"
  }
}
"""
# Mapowanie JSON na typy Pythona:
# - Obiekt JSON `{...}` -> Słownik Pythona `dict`
# - Tablica JSON `[...]` -> Lista Pythona `list`
# - String `"..."`      -> `str`
# - Liczba `123`, `3.14` -> `int`, `float`
# - `true` / `false`    -> `True` / `False`
# - `null`              -> `None`
#
#
# 2. Wbudowany moduł `json` w Pythonie
#
# Python posiada standardowy moduł `json` do pracy z tym formatem.
# Oferuje on dwie pary kluczowych funkcji:
#
#     * `json.dumps()`: Serializuje obiekt Pythona do STRINGA w formacie JSON.
#                       (dump s -> dump to string)
#     * `json.loads()`: Deserializuje STRING w formacie JSON do obiektu Pythona.
#                       (load s -> load from string)


import json

# Obiekt Pythona (słownik)
osoba_dict = {
    "imie": "Piotr",
    "wiek": 42,
    "email": None,
    "hobby": ["programowanie", "góry"]
}

print("--- 1. Serializacja (Python -> JSON string) ---")
# Serializacja do stringa
json_string = json.dumps(osoba_dict, indent=2, ensure_ascii=False)
# indent=2 -> dodaje wcięcia, aby JSON był czytelny
# ensure_ascii=False -> pozwala na poprawne wyświetlanie polskich znaków

print("Typ po serializacji:", type(json_string))
print("Wynikowy string JSON:\n", json_string)



print("\n--- 2. Deserializacja (JSON string -> Python) ---")
# Deserializacja ze stringa
nowy_slownik = json.loads(json_string)

print("Typ po deserializacji:", type(nowy_slownik))
print("Odtworzony słownik Pythona:\n", nowy_slownik)
print(f"Hobby odtworzonej osoby: {nowy_slownik['hobby']}")


#     * `json.dump()`: Serializuje obiekt Pythona i zapisuje go do PLIKU.
#                      (dump -> dump to file)
#     * `json.load()`: Wczytuje dane z PLIKU w formacie JSON i deserializuje je.
#                      (load -> load from file)

print("\n--- 3. Zapis i odczyt z pliku ---")
# Zapis do pliku
with open("dane.json", "w", encoding="utf-8") as plik:
    json.dump(osoba_dict, plik, indent=2, ensure_ascii=False)
print("Dane zostały zapisane do pliku 'dane.json'")

# Odczyt z pliku
with open("dane.json", "r", encoding="utf-8") as plik:
    dane_z_pliku = json.load(plik)

print("Dane odczytane z pliku:")
print(dane_z_pliku)


# 3. Serializacja z Pydantic – Łatwiej, szybciej, bezpieczniej
#
# Jak widzieliśmy w poprzednich lekcjach, Pydantic ma wbudowane, zoptymalizowane
# mechanizmy serializacji i deserializacji.
#
# DESERIALIZACJA w Pydanticu to po prostu tworzenie instancji modelu!
# Pydantic nie tylko konwertuje JSON na obiekt, ale od razu go WALIDUJE.

from pydantic import BaseModel, EmailStr

class Uzytkownik(BaseModel):
    id: int
    nazwa: str
    email: EmailStr

json_data_z_api = '{"id": 101, "nazwa": "AI_User", "email": "user@example.com"}'

print("\n--- 4. Deserializacja z Pydantic ---")
# Pydantic może przyjąć słownik lub bezpośrednio sparsowany JSON
uzytkownik_obj = Uzytkownik.model_validate_json(json_data_z_api)

print("Typ po deserializacji z Pydantic:", type(uzytkownik_obj))
print("Odtworzony obiekt Pydantic:", uzytkownik_obj)
print(f"Email użytkownika: {uzytkownik_obj.email}")


# SERIALIZACJA w Pydanticu to wywołanie jednej z metod `.model_dump*()`
print("\n--- 5. Serializacja z Pydantic ---")
# Serializacja do słownika
slownik_z_pydantic = uzytkownik_obj.model_dump()
print("Słownik z obiektu Pydantic:", slownik_z_pydantic)

# Serializacja do stringa JSON
json_z_pydantic = uzytkownik_obj.model_dump_json(indent=2)
print("String JSON z obiektu Pydantic:\n", json_z_pydantic)


# 4. Kiedy używać `json`, a kiedy Pydantic?
#
#     * Użyj wbudowanego modułu `json`, gdy:
#         - Pracujesz z prostymi, niestandardowymi strukturami danych.
#         - Piszesz szybki skrypt i nie potrzebujesz formalnej walidacji.
#         - Nie masz z góry zdefiniowanego schematu danych.
#
#     * Użyj Pydantic, gdy:
#         - Budujesz aplikację lub API, gdzie jakość i spójność danych są kluczowe.
#         - Chcesz jednocześnie deserializować i walidować dane.
#         - Twój kod operuje na jasno zdefiniowanych schematach (modelach) danych.
#         - Chcesz mieć pewność, że dane, na których pracujesz, są poprawne.
#         - W 99% przypadków w profesjonalnym projekcie AI – Pydantic jest lepszym wyborem.
#
#
# 5. Podsumowanie
#
#     * Serializacja to proces konwersji obiektu Pythona na format do zapisu/przesyłania (np. JSON).
#     * Deserializacja to proces odwrotny – odtwarzanie obiektu z tego formatu.
#     * Wbudowany moduł `json` oferuje `dumps/loads` (do/z stringów) oraz `dump/load` (do/z plików).
#     * Pydantic integruje deserializację z walidacją, co czyni proces o wiele bezpieczniejszym.
#     * Metody `.model_validate_json()` i `.model_dump_json()` w Pydanticu to potężne
#       narzędzia do konwersji między obiektami a formatem JSON.
#
# Zrozumienie tego przepływu danych jest absolutnie fundamentalne do pracy z API
# i budowania systemów opartych na danych.
#