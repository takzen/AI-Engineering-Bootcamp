# Moduł 3, Lekcja 23: Obsługa błędów i wyjątków w modelach Pydantic
#
#
#
# Wiemy już, że Pydantic jest naszym strażnikiem danych. Gdy dane są niepoprawne,
# Pydantic rzuca wyjątek `ValidationError`. To świetne, bo zatrzymuje "śmieci"
# na wejściu do naszej aplikacji.
#
# Ale co dalej? Jak możemy "złapać" ten wyjątek, zrozumieć go i przekazać
# użytkownikowi (lub innemu systemowi) czytelną informację o tym, co poszło nie tak?
#
# Dziś nauczymy się, jak profesjonalnie obsługiwać błędy walidacji,
# jak dostosowywać komunikaty o błędach i jak integrować tę logikę
# z aplikacjami, takimi jak FastAPI.
#
# 1. Anatomia wyjątku `ValidationError`
#
# Gdy Pydantic rzuca `ValidationError`, nie jest to zwykły błąd. To obiekt,
# który zawiera w sobie mnóstwo użytecznych informacji o WSZYSTKICH błędach
# walidacji, jakie wystąpiły.
#
# Kluczową metodą tego wyjątku jest `.errors()`. Zwraca ona listę słowników,
# gdzie każdy słownik opisuje jeden konkretny błąd.

from pydantic import BaseModel, Field, ValidationError, field_validator, EmailStr

class UzytkownikAPI(BaseModel):
    id_uzytkownika: int = Field(gt=0)
    email: EmailStr
    wiek: int = Field(ge=18)

# Przygotujmy dane z wieloma błędami
niepoprawne_dane = {
    "id_uzytkownika": -5,       # Błąd: nie jest większe od 0
    "email": "to-nie-jest-email", # Błąd: niepoprawny format
    "wiek": 17                  # Błąd: nie jest większe lub równe 18
}

print("--- 1. Analiza wyjątku ValidationError ---")
try:
    UzytkownikAPI(**niepoprawne_dane)
except ValidationError as e:
    print("Wystąpił błąd walidacji! Oto jego struktura:")
    
    # Metoda .errors() daje nam listę słowników z detalami
    lista_bledow = e.errors()
    
    # Przeanalizujmy, co zawiera każdy błąd
    for blad in lista_bledow:
        print("\n--- Szczegóły błędu ---")
        print(f"  Lokalizacja (pole): {blad['loc']}") # Gdzie wystąpił błąd
        print(f"  Komunikat błędu: {blad['msg']}")   # Opis błędu
        print(f"  Typ błędu: {blad['type']}")     # Wewnętrzny typ błędu Pydantic
        
    # Metoda .json() zwraca te same informacje w formacie JSON
    # print("\nBłędy w formacie JSON:")
    # print(e.json(indent=2))

# Dzięki tej strukturze możemy programistycznie analizować błędy i na nie reagować.
#
#
# 2. Tłumaczenie błędów na język użytkownika
#
# Domyślne komunikaty Pydantica są po angielsku i są techniczne.
# W aplikacji skierowanej do polskiego użytkownika chcielibyśmy wyświetlać
# bardziej przyjazne komunikaty.

def przetlumacz_bledy_pydantic(e: ValidationError) -> dict:
    """Tłumaczy listę błędów Pydantic na bardziej przyjazny format."""
    przetlumaczone_bledy = {}
    for blad in e.errors():
        nazwa_pola = blad['loc'][0] # Pobieramy nazwę pola
        
        # Prosta logika tłumaczenia - w realnej aplikacji byłaby bardziej rozbudowana
        if "greater than" in blad['msg']:
            komunikat = f"Wartość musi być większa niż {blad['ctx']['gt']}."
        elif "valid email address" in blad['msg']:
            komunikat = "Proszę podać poprawny adres email."
        else:
            komunikat = "Wprowadzono niepoprawną wartość."
            
        przetlumaczone_bledy[nazwa_pola] = komunikat
        
    return przetlumaczone_bledy

print("\n--- 2. Tłumaczenie błędów ---")
try:
    UzytkownikAPI(**niepoprawne_dane)
except ValidationError as e:
    przyjazne_bledy = przetlumacz_bledy_pydantic(e)
    print("Przyjazne komunikaty o błędach:")
    print(przyjazne_bledy)
    
# Taki słownik można łatwo wysłać jako odpowiedź API, aby front-end mógł
# wyświetlić błędy przy odpowiednich polach formularza.
#
#
# 3. Niestandardowe komunikaty błędów w walidatorach
#
# Pamiętasz, jak tworzyliśmy własne walidatory? Możemy w nich definiować
# własne, precyzyjne komunikaty błędów, rzucając wyjątek `ValueError` z tekstem.

class Haslo(BaseModel):
    wartosc: str
    
    @field_validator('wartosc')
    @classmethod
    def waliduj_zlozonosc_hasla(cls, v: str) -> str:
        if len(v) < 8:
            # Rzucamy ValueError z naszym własnym komunikatem
            raise ValueError("Hasło jest za krótkie, wymagane jest minimum 8 znaków.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Hasło musi zawierać przynajmniej jedną cyfrę (0-9).")
        if not any(c.isupper() for c in v):
            raise ValueError("Hasło musi zawierać przynajmniej jedną wielką literę.")
        return v

print("\n--- 3. Niestandardowe komunikaty w walidatorach ---")
try:
    print("Próba walidacji hasła bez wielkiej litery...")
    Haslo(wartosc="bardzotajne123")
except ValidationError as e:
    # Komunikat z ValueError zostanie przechwycony przez Pydantic
    print(f"Komunikat przechwycony przez Pydantic: {e.errors()[0]['msg']}")


# 4. Obsługa błędów Pydantic w FastAPI
#
# To jest miejsce, gdzie cała magia się łączy. FastAPI robi to wszystko za nas!
#
# Gdy definiujesz endpoint, który jako argument przyjmuje model Pydantic:
#
# `async def stworz_uzytkownika(uzytkownik: UzytkownikAPI):`
#
# FastAPI automatycznie:
# 1. Otacza proces walidacji blokiem `try...except ValidationError`.
# 2. Jeśli walidacja się nie powiedzie, przechwytuje wyjątek `e`.
# 3. Wywołuje na nim `e.errors()` lub `e.json()`.
# 4. Formatuje te błędy w standardowy sposób.
# 5. Zwraca do klienta odpowiedź HTTP z kodem błędu `422 Unprocessable Entity`
#    i ciałem (body) zawierającym szczegółową listę błędów walidacji.
#
# Dzięki temu nie musisz pisać tej logiki ręcznie w każdym endpoincie!
# Otrzymujesz solidną, standardową obsługę błędów "za darmo".
#
#
# 5. Podsumowanie
#
#     * Wyjątek `ValidationError` to bogaty obiekt, a nie prosty błąd.
#       Używaj metody `.errors()` aby programistycznie dostać się do szczegółów błędów.
#
#     * Możemy iterować po liście błędów, aby tworzyć własne, przyjazne dla użytkownika
#       komunikaty, np. w innym języku.
#
#     * Rzucając `ValueError` wewnątrz niestandardowych walidatorów (`@field_validator`),
#       możemy w pełni kontrolować treść komunikatu o błędzie.
#
#     * Frameworki takie jak FastAPI automatyzują proces obsługi `ValidationError`,
#       zwracając klientowi szczegółowe i ustandaryzowane odpowiedzi o błędach.
#
# Profesjonalna obsługa błędów to cecha, która odróżnia prosty skrypt od solidnej,
# produkcyjnej aplikacji. Dzięki Pydanticowi jest to o wiele prostsze.
#