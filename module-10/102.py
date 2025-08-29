# Moduł 10, Punkt 102: Skalowanie aplikacji FastAPI
#
#
#
# Po stworzeniu działającej aplikacji FastAPI, kolejnym naturalnym krokiem jest przygotowanie jej do obsługi większego ruchu.
# Skalowanie to proces dostosowywania aplikacji i infrastruktury, aby mogła ona sprawnie obsłużyć rosnącą liczbę użytkowników i żądań,
# bez znaczącego spadku wydajności. FastAPI, dzięki swojej asynchronicznej naturze, jest doskonale przygotowane do skalowania.
#
#
# 1. Co to znaczy "skalować" aplikację?
#
# Skalowalność to zdolność systemu do radzenia sobie z rosnącym obciążeniem. Wyróżniamy dwa główne podejścia:
#
#     Skalowanie wertykalne (Vertical Scaling): "Większy serwer". Polega na zwiększeniu zasobów maszyny, na której działa aplikacja
#     (np. dodanie więcej CPU, RAM). Jest to proste, ale ma swoje granice i szybko staje się bardzo kosztowne.
#
#     Skalowanie horyzontalne (Horizontal Scaling): "Więcej serwerów". Polega na dodaniu kolejnych maszyn (lub procesów)
#     i rozdzielaniu ruchu pomiędzy nimi. To standardowe podejście w nowoczesnych aplikacjach webowych, oferujące
#     większą elastyczność i odporność na awarie.
#
# W tej lekcji skupimy się głównie na skalowaniu horyzontalnym w kontekście FastAPI.
#
#
# 2. Fundament skalowania – Asynchroniczność (async/await)
#
# Zanim zaczniemy dodawać serwery, musimy upewnić się, że nasza aplikacja w pełni wykorzystuje swój potencjał na JEDNYM procesie.
# Kluczem jest asynchroniczność.
#
# FastAPI jest zbudowane na serwerze ASGI (Asynchronous Server Gateway Interface), co pozwala na obsługę wielu żądań
# "jednocześnie" w ramach jednego wątku, bez blokowania go.
#
#     Operacja blokująca: Zatrzymuje cały proces, aż do jej zakończenia. W tym czasie serwer nie może obsłużyć żadnych innych żądań.
#     Przykład: `time.sleep()`, długa, synchroniczna operacja na pliku lub w bazie danych.
#
#     Operacja nieblokująca: Pozwala serwerowi zająć się innymi zadaniami, podczas gdy czeka na zakończenie operacji (np. na odpowiedź z bazy 
#     danych lub innego API).
#     Przykład: `await asyncio.sleep()`, użycie asynchronicznej biblioteki do obsługi bazy (np. `databases`, `tortoise-orm`).

# ZŁY PRZYKŁAD: Blokowanie serwera
import time
from fastapi import FastAPI

app_bad = FastAPI()

@app_bad.get("/block")
def block_endpoint():
    # Ta funkcja blokuje cały proces na 5 sekund.
    # W tym czasie serwer nie jest w stanie odpowiedzieć na żadne inne żądanie.
    time.sleep(5)
    return {"message": "Zablokowane na 5 sekund!"}

# DOBRY PRZYKŁAD: Użycie asynchroniczności
import asyncio
from fastapi import FastAPI

app_good = FastAPI()

@app_good.get("/non-block")
async def non_block_endpoint():
    # Słowo kluczowe 'async' informuje FastAPI, że to operacja asynchroniczna.
    # 'await' "zawiesza" tę funkcję na 5 sekund, ale pozwala serwerowi
    # w tym czasie obsługiwać inne żądania.
    await asyncio.sleep(5)
    return {"message": "Czekałem 5 sekund, ale serwer działał!"}

# WNIOSEK: Zawsze używaj `async def` dla endpointów wykonujących operacje I/O (wejścia/wyjścia),
# takie jak zapytania do bazy danych, odczyt plików czy komunikacja z innymi serwisami.
# Używaj asynchronicznych bibliotek, aby uniknąć blokowania.
#
#
# 3. Skalowanie na jednej maszynie – Procesy robocze (Workers)
#
# Nawet najlepiej napisany kod asynchroniczny jest ograniczony przez tzw. GIL (Global Interpreter Lock) w Pythonie.
# W skrócie, GIL pozwala tylko jednemu wątkowi na wykonywanie kodu Pythona w danym momencie, co uniemożliwia
# pełne wykorzystanie wielordzeniowych procesorów przez jeden proces.
#
# Rozwiązaniem jest uruchomienie wielu procesów Pythona. Każdy proces będzie miał swój własny interpreter i pętlę zdarzeń asyncio.
# Do zarządzania tymi procesami używamy serwera produkcyjnego, takiego jak Gunicorn.
#
# Gunicorn to dojrzały, produkcyjny serwer WSGI, który może działać jako menedżer procesów dla serwerów ASGI, takich jak Uvicorn.
#
#     Instalacja Gunicorna:
#     pip install gunicorn
#
#     Rekomendowana konfiguracja produkcyjna: Użyj Gunicorna do zarządzania procesami roboczymi (workers) Uvicorna.

# Załóżmy, że nasza aplikacja znajduje się w pliku `main.py`, a obiekt FastAPI nazywa się `app`.
# main.py
from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
 return {"message": "Hello from a worker!"}

# Uruchomienie aplikacji z 4 procesami roboczymi (workers):
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

#     -w 4: Określa liczbę procesów roboczych (workers). Gunicorn uruchomi 4 niezależne procesy z Twoją aplikacją.
#     -k uvicorn.workers.UvicornWorker: Mówi Gunicornowi, aby używał klasy roboczej Uvicorna. Jest to kluczowe dla obsługi aplikacji ASGI.
#     main:app: Wskazuje na plik `main.py` i obiekt `app` wewnątrz niego.

# Ile workerów ustawić?
# Dobrą zasadą na początek jest: `2 * (liczba rdzeni CPU) + 1`.
# Dla serwera z 2 rdzeniami CPU, byłoby to `2 * 2 + 1 = 5` workerów.
# Tę wartość należy dostosować na podstawie monitoringu obciążenia.
#
#
# 4. Odciążenie aplikacji – Zadania w tle (Background Tasks)
#
# Czasami endpoint musi wykonać operację, która trwa długo (np. wysłanie e-maila, wygenerowanie raportu, przetworzenie obrazu),
# ale użytkownik nie musi czekać na jej wynik. Zmuszanie użytkownika do czekania psuje doświadczenie i niepotrzebnie blokuje proces roboczy.
#
# Rozwiązanie: Wykonuj takie zadania w tle.
#
#     Proste zadania w tle w FastAPI:
#     FastAPI ma wbudowany mechanizm `BackgroundTasks`, który jest idealny do prostych operacji typu "uruchom i zapomnij".

from fastapi import BackgroundTasks, FastAPI

app_tasks = FastAPI()

def write_notification(email: str, message=""):
    with open("log.txt", mode="a") as email_file:
        content = f"notification for {email}: {message}\n"
        email_file.write(content)

@app_tasks.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    # Dodajemy zadanie do wykonania w tle.
    # Odpowiedź do użytkownika zostanie wysłana NATYCHMIAST,
    # a funkcja write_notification wykona się "w tle".
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}

#     Zaawansowane zadania w tle – Kolejki zadań (Task Queues):
#     Do bardziej złożonych i niezawodnych systemów zadań w tle używa się dedykowanych narzędzi, takich jak Celery z brokerem wiadomości (np. 
#     Redis lub RabbitMQ).
#     Aplikacja FastAPI jedynie dodaje zadanie do kolejki, a osobne procesy robocze Celery je pobierają i wykonują.
#     To znacznie bardziej skalowalne i odporne na błędy rozwiązanie.
#
#
# 5. Skalowanie na wiele maszyn – Load Balancer
#
# Gdy jedna maszyna, nawet z wieloma workerami, przestaje wystarczać, przechodzimy do skalowania na wiele maszyn.
# W takiej architekturze potrzebujemy komponentu, który będzie rozdzielał ruch przychodzący pomiędzy nasze serwery.
# Tym komponentem jest Load Balancer.
#
# Jak to działa:
# 1. Użytkownik wysyła żądanie na jeden adres (np. `api.twojafirma.com`).
# 2. Load Balancer (np. Nginx, HAProxy, AWS ELB) odbiera to żądanie.
# 3. Load Balancer przekazuje żądanie do jednego z dostępnych serwerów aplikacyjnych (każdy z nich ma uruchomionego Gunicorna z workerami Uvicorna).
# 4. Serwer aplikacyjny przetwarza żądanie i odsyła odpowiedź do Load Balancera, a ten do użytkownika.
#
# Prosty schemat:
# [Użytkownik] <--> [Internet] <--> [Load Balancer] <--> [Serwer 1 z Gunicorn], [Serwer 2 z Gunicorn], [Serwer 3 z Gunicorn] ...
#
# Zalety tego podejścia:
#     Wysoka dostępność: Jeśli jeden serwer aplikacyjny ulegnie awarii, Load Balancer przestanie kierować do niego ruch.
#     Elastyczność: Można dynamicznie dodawać i usuwać serwery w zależności od obciążenia.
#
#
# 6. Inne ważne aspekty skalowania
#
#     Baza danych: Często to baza danych staje się "wąskim gardłem". Skalowanie aplikacji musi iść w parze ze skalowaniem bazy (np. przez replikację, 
#     sharding, użycie wydajniejszych instancji).
#
#     Caching: Przechowywanie często odpytywanych, rzadko zmieniających się danych w szybkiej pamięci podręcznej (np. Redis) może drastycznie 
#     zmniejszyć obciążenie bazy danych i przyspieszyć odpowiedzi API.
#
#     Monitoring i Logowanie: Nie można skalować czegoś, czego się nie mierzy. Należy wdrożyć monitoring kluczowych metryk (czas odpowiedzi, 
#     użycie CPU/RAM, liczba błędów) i centralne logowanie, aby móc podejmować świadome decyzje o skalowaniu.
#
#
# Podsumowanie
#
# Skalowanie aplikacji FastAPI to wieloetapowy proces, który zaczyna się już na poziomie kodu.
#
#     Krok 1: Pisz asynchroniczny kod (`async def`) i używaj nieblokujących bibliotek, aby maksymalnie wykorzystać potencjał jednego procesu.
#
#     Krok 2: Użyj serwera produkcyjnego jak Gunicorn z workerami Uvicorna (`gunicorn -k uvicorn.workers.UvicornWorker`), aby w pełni wykorzystać 
#     moc wielordzeniowych procesorów na jednej maszynie.
#
#     Krok 3: Długotrwałe operacje przenieś do zadań w tle (`BackgroundTasks` lub Celery), aby nie blokować odpowiedzi dla użytkownika.
#
#     Krok 4: Gdy jedna maszyna to za mało, wprowadź Load Balancer i uruchom swoją aplikację na wielu serwerach.
#
#     Krok 5: Pamiętaj o skalowaniu pozostałych komponentów (baza danych, cache) i monitoruj swoją infrastrukturę.
#
# Przejście od prostej aplikacji do skalowalnego systemu to kluczowy krok w rozwoju każdego profesjonalnego projektu webowego.