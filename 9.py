# Moduł 2, Punkt 9: Programowanie asynchroniczne w AI (asyncio)
#
#
#
# UWAGA: To jest temat zaawansowany! Naszym celem jest zrozumienie KONCEPCJI i problemu,
# który rozwiązuje, a nie zostanie ekspertami w tej dziedzinie od razu.
#
# Do tej pory nasz kod wykonywał się synchronicznie – linijka po linijce.
# Jeśli jakaś operacja trwała długo (np. pobieranie dużego pliku),
# cały program czekał, aż się zakończy. W świecie AI, gdzie często komunikujemy się
# z zewnętrznymi serwisami (API modeli językowych, bazy danych), takie czekanie jest
# ogromnym marnotrawstwem czasu i zasobów.
#
# 1. Problem: Czekanie, czyli zadania "I/O-bound"
#
# Zadania "I/O-bound" (ang. Input/Output bound) to takie, w których program nie wykonuje
# skomplikowanych obliczeń, ale głównie czeka na dane z zewnątrz:
#     - Czekanie na odpowiedź z serwera (np. od API OpenAI).
#     - Czekanie na odczytanie pliku z dysku twardego.
#     - Czekanie na dane z bazy danych.
#
# Wyobraź sobie, że musisz zadać 5 pytań modelowi AI.
# Synchronicznie:
# 1. Wysyłasz pytanie 1 -> CZEKASZ na odpowiedź... (np. 3 sekundy) -> Dostajesz odpowiedź.
# 2. Wysyłasz pytanie 2 -> CZEKASZ na odpowiedź... (np. 2 sekundy) -> Dostajesz odpowiedź.
# 3. ...i tak dalej.
# Całkowity czas = suma czasów oczekiwania.
#
# Czy nie byłoby lepiej wysłać wszystkie 5 pytań na raz i zbierać odpowiedzi,
# gdy tylko będą gotowe? To właśnie jest idea programowania asynchronicznego.

#
# 2. Rozwiązanie: asyncio – Robienie czegoś innego podczas czekania
#
# `asyncio` to wbudowana w Pythona biblioteka, która pozwala pisać kod asynchroniczny.
# Działa to jak sprawny kucharz w kuchni:
#   - Synchroniczny kucharz: Bierze jedno jajko, smaży je od początku do końca, podaje na talerz. Potem bierze drugie...
#   - Asynchroniczny kucharz: Wstawia wodę na herbatę, a w czasie gdy się gotuje, kroi warzywa.
#     Słyszy, że woda się zagotowała, więc zalewa herbatę i wraca do krojenia.
#
# Python `asyncio` robi to samo – gdy czeka na operację I/O, może zająć się innym zadaniem.
#
# 3. Nowe słowa kluczowe: `async` i `await`
#
# Aby to wszystko działało, Python wprowadza dwa nowe słowa kluczowe:
#
#     `async def`: Tak definiujemy funkcję, która jest "specjalna" – można ją wstrzymać i wznowić.
#                  Nazywamy ją korutyną (coroutine).
#
#     `await`: Tego słowa używamy wewnątrz funkcji `async def`, aby powiedzieć:
#              "W tym miejscu poczekaj na wynik wolnej operacji (np. zapytania do AI),
#              ale w międzyczasie pozwól Pythonowi zająć się innymi zadaniami".

#
# 4. Przykład praktyczny: Synchronicznie vs Asynchronicznie
#
# Zobaczmy różnicę w działaniu. Zamiast prawdziwych zapytań do AI, zasymulujemy
# czas oczekiwania za pomocą funkcji `sleep`.
# Będziemy potrzebować modułów `time` (do mierzenia czasu) i `asyncio`.

import time
import asyncio

# --- WERSJA SYNCHRONICZNA ---

def zapytaj_ai_sync(pytanie):
    """Symuluje synchroniczne zapytanie do AI, które trwa 2 sekundy."""
    print(f" > Wysyłam synchronicznie pytanie: '{pytanie}'...")
    time.sleep(2)  # Blokujące czekanie - cały program stoi w miejscu!
    print(f" < Otrzymałem synchronicznie odpowiedź na: '{pytanie}'!")
    return f"Odpowiedź na {pytanie}"

print("--- START WERSJI SYNCHRONICZNEJ ---")
start_time_sync = time.time()

zapytaj_ai_sync("Jaka jest pogoda?")
zapytaj_ai_sync("Opowiedz dowcip.")
zapytaj_ai_sync("Kto był pierwszym królem Polski?")

end_time_sync = time.time()
print(f"\nCałkowity czas wykonania synchronicznego: {end_time_sync - start_time_sync:.2f} sekund.\n")
# Oczekiwany czas: ~6 sekund (2s + 2s + 2s)

# --- WERSJA ASYNCHRONICZNA ---

async def zapytaj_ai_async(pytanie):
    """Symuluje asynchroniczne zapytanie do AI, które trwa 2 sekundy."""
    print(f" > Wysyłam asynchronicznie pytanie: '{pytanie}'...")
    # WAŻNE: Używamy asyncio.sleep() zamiast time.sleep()!
    # time.sleep() blokuje wszystko, asyncio.sleep() "oddaje kontrolę" i pozwala
    # wykonywać inne zadania podczas czekania.
    await asyncio.sleep(2)
    print(f" < Otrzymałem asynchronicznie odpowiedź na: '{pytanie}'!")
    return f"Odpowiedź na {pytanie}"

# Musimy stworzyć główną funkcję asynchroniczną, która zarządza uruchamianiem zadań.
async def main():
    print("--- START WERSJI ASYNCHRONICZNEJ ---")
    start_time_async = time.time()

    # asyncio.gather() to sposób, aby uruchomić wiele zadań "jednocześnie"
    # i poczekać, aż wszystkie się zakończą.
    wyniki = await asyncio.gather(
        zapytaj_ai_async("Jaka jest pogoda?"),
        zapytaj_ai_async("Opowiedz dowcip."),
        zapytaj_ai_async("Kto był pierwszym królem Polski?")
    )
    # Zwróć uwagę, że wszystkie komunikaty "Wysyłam..." pojawiły się niemal od razu!
    
    end_time_async = time.time()
    print(f"\nCałkowity czas wykonania asynchronicznego: {end_time_async - start_time_async:.2f} sekund.")
    # Oczekiwany czas: ~2 sekundy (czas najdłuższego zadania)
    print(f"Otrzymane wyniki: {wyniki}")


# Aby uruchomić główną funkcję asynchroniczną, używamy asyncio.run()
if __name__ == "__main__":
    asyncio.run(main())


#
# 5. Podsumowanie i znaczenie dla AI
#
# Jak widać na przykładzie, wersja asynchroniczna wykonała się 3x szybciej!
# Zamiast sumować czasy oczekiwania (2+2+2), całkowity czas był równy czasowi
# najdłuższej operacji (ponieważ wszystkie trwały tyle samo, wyszło ~2 sekundy).
#
# Kluczowe koncepcje do zapamiętania:
#
#     * Kod synchroniczny wykonuje jedną rzecz na raz i czeka.
#     * Kod asynchroniczny może wykonywać inne zadania, podczas gdy czeka na operacje I/O (np. sieć, dysk).
#     * Używamy `async def` do tworzenia funkcji, które można wstrzymywać (korutyn).
#     * Używamy `await`, aby poczekać na wynik korutyny, pozwalając innym zadaniom działać.
#     * `asyncio.gather()` jest świetnym narzędziem do jednoczesnego uruchamiania wielu zadań.
#
# W kontekście AI i analizy danych `asyncio` jest potężnym narzędziem, gdy:
#
#     * Odpytujesz API wielu modeli jednocześnie.
#     * Pobierasz wiele zbiorów danych z różnych źródeł internetowych.
#     * Tworzysz aplikację webową (np. chatbota), która musi obsługiwać wielu użytkowników jednocześnie bez blokowania się.
#
# Nie przejmuj się, jeśli nie wszystko jest od razu jasne. Najważniejsze to zapamiętać,
# że gdy Twój program głównie CZEKA, `asyncio` jest narzędziem, które może drastycznie go przyspieszyć.
