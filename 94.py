# Moduł 10, Punkt 94: Docker i konteneryzacja AI
#
#
#
# Zbudowaliśmy i przetestowaliśmy naszą aplikację FastAPI lokalnie. Działa świetnie na naszym
# komputerze. Ale co teraz? Jak w prosty i niezawodny sposób uruchomić ją na serwerze
# produkcyjnym, na komputerze kolegi z zespołu, czy w chmurze?
#
# Tutaj pojawia się klasyczny problem inżynierii oprogramowania: "U mnie działa!".
# Aplikacja może nie działać na innej maszynie z powodu:
#
#     *   Różnych wersji Pythona.
#     *   Brakujących lub niekompatybilnych bibliotek.
#     *   Innych ustawień systemowych.
#
# Rozwiązaniem tego problemu jest **konteneryzacja**, a najpopularniejszym narzędziem
# do jej realizacji jest **Docker**.
#
# 1. Czym jest Docker? Metafora kontenera transportowego
#
# Wyobraź sobie, że chcesz wysłać delikatny, szklany wazon statkiem. Nie wrzucasz go
# luzem do ładowni. Zamiast tego:
#
#     1.  Pakujesz go w solidne pudełko (Twój kod aplikacji).
#     2.  Wypełniasz pudełko styropianem i folią bąbelkową (wszystkie zależności: Python,
#         biblioteki jak FastAPI, LangChain, a nawet pliki systemowe).
#     3.  Zamykasz i plombujesz pudełko.
#
# To zaplombowane pudełko to **obraz kontenera (Docker Image)**. Jest to samodzielna,
# niezmienna "paczka" zawierająca wszystko, czego Twoja aplikacja potrzebuje do działania.
#
# Gdy statek (serwer) chce "uruchomić" Twój wazon, po prostu stawia na pokładzie Twoje
# pudełko. To uruchomione pudełko to **kontener (Docker Container)**.
#
# **Kluczowa idea**: Nieważne, jaki jest statek (czy to serwer z Ubuntu, CentOS, czy
# maszyna z macOS), Twoje pudełko (kontener) zawsze będzie wyglądać i działać tak samo
# w środku. Docker zapewnia izolowane, powtarzalne środowisko.
#
# 2. Korzyści z konteneryzacji aplikacji AI
#
# *   **Powtarzalność i spójność**: Koniec z "u mnie działa". Jeśli aplikacja działa w
#     kontenerze na Twoim laptopie, będzie działać tak samo na serwerze produkcyjnym.
# *   **Izolacja zależności**: Możesz mieć w jednym kontenerze aplikację z Pythonem 3.9,
#     a w drugim z Pythonem 3.11, i nie będą one ze sobą kolidować.
# *   **Łatwość wdrożenia i skalowania**: Uruchomienie aplikacji na nowym serwerze sprowadza
#     się do jednej komendy: `docker run`. Narzędzia do orkiestracji (jak Kubernetes)
#     mogą automatycznie uruchamiać i zarządzać setkami takich kontenerów.
# *   **Przenośność**: Obraz kontenera możesz przechowywać w repozytorium (jak Docker Hub)
#     i łatwo go pobierać na dowolną maszynę z zainstalowanym Dockerem.
#
# 3. Jak "zapakować" naszą aplikację FastAPI do kontenera?
#
# Proces ten opiera się na stworzeniu prostego pliku tekstowego o nazwie `Dockerfile`.
# Jest to "przepis" lub "instrukcja montażu" dla naszego kontenera.
#
# Załóżmy, że nasza aplikacja z poprzedniej lekcji znajduje się w pliku `main.py`.
#
# **Krok 1: Stworzenie pliku `requirements.txt`**
#
# Najpierw musimy stworzyć listę wszystkich bibliotek Pythona, których potrzebuje nasza
# aplikacja. W terminalu możemy użyć `pip freeze`, ale lepiej jest stworzyć plik ręcznie,
# aby zawierał tylko niezbędne pakiety.
#
# # --- plik: requirements.txt ---
# fastapi
# uvicorn[standard]
# langchain-openai
# # --- koniec pliku requirements.txt ---
#
# **Krok 2: Stworzenie pliku `Dockerfile`**
#
# To jest serce konteneryzacji. Stwórz w głównym folderze projektu plik o nazwie `Dockerfile`
# (bez żadnego rozszerzenia).

# Dockerfile to przepis, który mówi Dockerowi, jak zbudować nasz obraz.
# Każda linijka to kolejna warstwa w obrazie.

# 1. Zacznij od oficjalnego, lekkiego obrazu Pythona w wersji 3.11
# FROM python:3.11-slim

# 2. Ustaw katalog roboczy wewnątrz kontenera
# WORKDIR /app

# 3. Skopiuj plik z zależnościami do kontenera
# COPY requirements.txt .

# 4. Zainstaluj wszystkie potrzebne biblioteki
#    --no-cache-dir zmniejsza rozmiar finalnego obrazu
# RUN pip install --no-cache-dir -r requirements.txt

# 5. Skopiuj resztę kodu naszej aplikacji do kontenera
# COPY . .

# 6. "Wystaw" port 8000, aby świat zewnętrzny mógł się komunikować
#    z serwerem Uvicorn, który będzie działał wewnątrz kontenera.
# EXPOSE 8000

# 7. Zdefiniuj komendę, która zostanie uruchomiona, gdy kontener wystartuje.
#    Uruchamiamy serwer Uvicorn.
#    --host 0.0.0.0 sprawia, że serwer jest dostępny z zewnątrz kontenera.
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

#
# **Krok 3: Budowanie obrazu i uruchamianie kontenera**
#
# Teraz, mając `Dockerfile` i resztę plików, możemy użyć komend Dockera w terminalu.
# (Musisz mieć zainstalowany Docker Desktop lub silnik Dockera na swojej maszynie).
#
# # 1. Budowanie obrazu
# # Komenda `docker build` czyta Dockerfile i tworzy obraz.
# # -t nadaje obrazowi nazwę (tag), np. `my-ai-api`.
# # . oznacza, że Dockerfile znajduje się w bieżącym katalogu.
# docker build -t my-ai-api .
#
# # 2. Uruchamianie kontenera z obrazu
# # Komenda `docker run` uruchamia kontener.
# # -d uruchamia go w tle (detached mode).
# # -p mapuje port 8000 na zewnątrz kontenera na port 8000 na naszej maszynie.
# # --name nadaje kontenerowi przyjazną nazwę.
# # my-ai-api to nazwa obrazu, którego chcemy użyć.
# docker run -d -p 8000:8000 --name my-ai-container my-ai-api
#
# # Po wykonaniu tej komendy, Twoja aplikacja jest uruchomiona!
# # Możesz wejść na http://127.0.0.1:8000/docs i zobaczysz, że działa
# # dokładnie tak samo, jak uruchamiana lokalnie, ale teraz jest w pełni
# # odizolowana i przenośna.
#
# # 3. (Opcjonalnie) Zatrzymywanie i usuwanie kontenera
# docker stop my-ai-container
# docker rm my-ai-container
#
# 4. Podsumowanie
#
# Docker i konteneryzacja to fundamentalna umiejętność w nowoczesnej inżynierii
# oprogramowania, a w świecie AI jest szczególnie ważna ze względu na złożoność zależności.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Docker rozwiązuje problem "u mnie działa"**: Tworzy spójne, powtarzalne i
#         izolowane środowiska dla Twoich aplikacji.
#     2.  **`Dockerfile` to przepis**: To prosta instrukcja krok po kroku, jak zbudować
#         obraz Twojej aplikacji.
#     3.  **Obraz vs Kontener**: Obraz to szablon, statyczna "paczka". Kontener to
#         uruchomiona, żywa instancja tego obrazu.
#     4.  **Proces jest prosty**: Zdefiniuj zależności (`requirements.txt`), napisz `Dockerfile`,
#         zbuduj obraz (`docker build`) i uruchom kontener (`docker run`).
#
# Opanowując tę technikę, jesteś gotów do wdrażania swoich aplikacji AI w dowolnym
# środowisku – od prostego serwera VPS po złożone klastry w chmurze.