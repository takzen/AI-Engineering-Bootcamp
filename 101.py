# Moduł 10, Punkt 101: Automatyzacja wdrażania aplikacji AI
#
#
#
# Gratulacje! Dotarłeś do absolutnego szczytu naszej podróży. Stworzyliśmy inteligentną
# aplikację, opakowaliśmy ją w bezpieczne i skalowalne API, skonteneryzowaliśmy ją za pomocą
# Dockera i nauczyliśmy się ją testować. Pozostał ostatni krok: **zautomatyzowanie całego
# procesu od zmiany w kodzie do wdrożenia na produkcji.**
#
# To jest świat **Ciągłej Integracji i Ciągłego Wdrażania (CI/CD)**. To proces, który
# pozwala zespołom deweloperskim na szybkie, częste i – co najważniejsze – niezawodne
# dostarczanie nowych wersji oprogramowania. Dla aplikacji AI, gdzie ciągle
# eksperymentujemy z promptami i modelami, jest to absolutnie kluczowe.
#
# 1. Problem: Ręczne wdrożenie jest powolne i ryzykowne
#
# Wyobraź sobie, że chcesz wdrożyć małą poprawkę w prompcie. Proces ręczny wyglądałby tak:
#
#     1.  Zmień kod na swoim komputerze.
#     2.  Uruchom lokalnie testy (`pytest`).
#     3.  Zbuduj nowy obraz Dockera (`docker build ...`).
#     4.  Wypchnij obraz do repozytorium (np. Docker Hub).
#     5.  Zaloguj się na serwer produkcyjny przez SSH.
#     6.  Zatrzymaj stary kontener (`docker stop ...`).
#     7.  Pobierz nowy obraz (`docker pull ...`).
#     8.  Uruchom nowy kontener z nowym obrazem (`docker run ...`).
#
# Ten proces jest nie tylko żmudny, ale też niezwykle podatny na ludzkie błędy.
# Jeden pominięty krok lub literówka w komendzie może spowodować awarię całej usługi.
#
# 2. Rozwiązanie: Pipeline CI/CD
#
# Pipeline CI/CD to zautomatyzowana sekwencja kroków, która jest uruchamiana za
# każdym razem, gdy wprowadzasz zmianę do repozytorium kodu (np. przez `git push`).
# Najpopularniejszym narzędziem do budowy takich pipeline'ów jest **GitHub Actions**.
#
# **Ostateczny cel: Pełna automatyzacja**
#
# Nasz idealny, zautomatyzowany pipeline dla aplikacji AI będzie wyglądał następująco:
#
#     1.  **Trigger (Wyzwalacz)**: Deweloper wysyła zmiany do gałęzi `main` w repozytorium GitHub.
#     2.  **CI (Ciągła Integracja)**:
#         *   GitHub Actions automatycznie uruchamia serwer (tzw. "runner").
#         *   Uruchamiane są **szybkie testy jednostkowe** (`pytest` z mockowaniem).
#         *   Jeśli testy przejdą, budowany jest **nowy obraz Dockera**.
#         *   (Opcjonalnie, ale zalecane) Uruchamiane są **testy ewaluacyjne** na LangSmith
#           na podstawie zbudowanego obrazu, aby sprawdzić jakość odpowiedzi AI.
#         *   Jeśli wszystko się powiedzie, nowy obraz jest oznaczany unikalnym tagiem
#           (np. numerem commita) i wypychany do repozytorium obrazów (np. Docker Hub).
#     3.  **CD (Ciągłe Wdrażanie)**:
#         *   Po pomyślnym zakończeniu etapu CI, GitHub Actions automatycznie łączy się
#           z serwerem produkcyjnym (np. przez SSH).
#         *   Wydaje na serwerze serię komend, które pobierają nowy obraz i restartują
#           kontener, aby zaczął on używać nowej wersji aplikacji.
#
# Od momentu `git push` do momentu, gdy nowa wersja działa na produkcji, wszystko
# dzieje się automatycznie, bez interwencji człowieka.
#
# 3. Praktyczny przykład: Konfiguracja pipeline'u w GitHub Actions
#
# Aby zdefiniować taki pipeline, tworzymy plik w naszym repozytorium pod ścieżką
# `.github/workflows/deploy.yml`. Pliki te pisane są w formacie YAML.
#
# Krok 0: Przygotowanie repozytorium GitHub
# # W ustawieniach swojego repozytorium na GitHub, w sekcji "Secrets and variables" -> "Actions",
# # musisz dodać następujące "secrety" (tajne zmienne):
# # - DOCKERHUB_USERNAME: Twoja nazwa użytkownika w Docker Hub.
# # - DOCKERHUB_TOKEN: Twój token dostępowy do Docker Hub.
# # - PROD_SERVER_HOST: Adres IP lub domena Twojego serwera produkcyjnego.
# # - PROD_SERVER_USERNAME: Nazwa użytkownika na serwerze (np. `ubuntu`).
# # - PROD_SSH_KEY: Twój prywatny klucz SSH do logowania na serwer.
# # - OPENAI_API_KEY: Klucz API OpenAI, który zostanie przekazany do kontenera.

# --- Plik: .github/workflows/deploy.yml ---
name: Deploy AI App to Production

# Wyzwalacz: Uruchom ten workflow przy każdym pushu do gałęzi 'main'
on:
  push:
    branches: [ "main" ]

jobs:
  # Pierwsze zadanie: testowanie i budowanie obrazu
  test_and_build:
    runs-on: ubuntu-latest # Uruchom na maszynie wirtualnej z Ubuntu
    steps:
      # Krok 1: Pobranie kodu z repozytorium
      - name: Checkout code
        uses: actions/checkout@v4

      # Krok 2: Ustawienie środowiska Pythona
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # Krok 3: Instalacja zależności i uruchomienie testów jednostkowych
      - name: Install dependencies and run tests
        run: |
          pip install -r requirements.txt
          pytest

      # Krok 4: Logowanie do Docker Hub
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Krok 5: Budowanie i wypychanie obrazu Dockera
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          # Tagujemy obraz jako 'latest' i unikalnym numerem commita
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/my-ai-api:latest, ${{ secrets.DOCKERHUB_USERNAME }}/my-ai-api:${{ github.sha }}

  # Drugie zadanie: wdrażanie na serwerze (uruchomi się tylko, jeśli 'test_and_build' się powiedzie)
  deploy:
    needs: test_and_build # Zależność od poprzedniego zadania
    runs-on: ubuntu-latest
    steps:
      # Krok 1: Logowanie na serwer i wdrożenie
      - name: Deploy to production server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_SERVER_HOST }}
          username: ${{ secrets.PROD_SERVER_USERNAME }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            # Komendy wykonywane na serwerze produkcyjnym
            # 1. Pobierz najnowszy obraz
            docker pull ${{ secrets.DOCKERHUB_USERNAME }}/my-ai-api:latest
            # 2. Zatrzymaj i usuń stary kontener (jeśli istnieje)
            docker stop my-ai-container || true
            docker rm my-ai-container || true
            # 3. Uruchom nowy kontener z nowym obrazem i zmiennymi środowiskowymi
            docker run -d -p 8000:8000 \
              -e OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }} \
              --name my-ai-container \
              ${{ secrets.DOCKERHUB_USERNAME }}/my-ai-api:latest

#
# 4. Podsumowanie – Ostateczny Cel Inżynierii AI
#
# Zautomatyzowany, niezawodny pipeline CI/CD to ostateczny cel każdego profesjonalnego
# projektu software'owego. W świecie AI jest on podwójnie ważny, ponieważ pozwala na
# bezpieczne i szybkie eksperymentowanie oraz wdrażanie ulepszeń.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Automatyzuj wszystko**: Ręczne wdrożenia są źródłem błędów. Zaufaj zautomatyzowanym
#         procesom.
#     2.  **Testuj na każdym etapie**: Pipeline powinien zawierać zarówno szybkie testy
#         jednostkowe, jak i bardziej złożone testy jakościowe (ewaluacje), aby stanowić
#         solidną siatkę bezpieczeństwa.
#     3.  **GitHub Actions to Twój przyjaciel**: To potężne i dobrze zintegrowane narzędzie
#         do budowy dowolnie złożonych pipeline'ów CI/CD.
#     4.  **Używaj sekretów**: Nigdy nie umieszczaj kluczy API, haseł ani kluczy SSH
#         bezpośrednio w plikach konfiguracyjnych. Zawsze używaj mechanizmu sekretów
#         dostarczanego przez Twoją platformę CI/CD.
#
# Gratuluję dotarcia do końca! Posiadasz teraz pełen obraz cyklu życia aplikacji AI – od
# pomysłu i prototypu, przez budowę zaawansowanej logiki, aż po profesjonalne,
# zautomatyzowane wdrożenie na produkcję. Jesteś gotów, aby tworzyć przyszłość.