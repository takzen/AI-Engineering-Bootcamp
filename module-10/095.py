# Moduł 10, Punkt 95: Budowanie obrazów Dockera
#
#
#
# W poprzedniej lekcji nauczyliśmy się, czym jest Docker i jak stworzyć prosty `Dockerfile`
# dla naszej aplikacji. Teraz pójdziemy o krok dalej. Budowanie obrazów Dockera to sztuka,
# a dobrze napisany `Dockerfile` może znacząco wpłynąć na szybkość budowania,
# rozmiar finalnego obrazu i bezpieczeństwo naszej aplikacji.
#
# W tej lekcji poznamy najlepsze praktyki i zaawansowane techniki, które pozwolą Ci
# tworzyć profesjonalne, zoptymalizowane obrazy Dockera dla Twoich aplikacji AI.
#
# 1. Anatomia `Dockerfile` – Przypomnienie
#
# `Dockerfile` to plik tekstowy z instrukcjami. Każda instrukcja tworzy nową **warstwę (layer)**
# w obrazie. Docker jest inteligentny – jeśli nic się nie zmieniło w danej warstwie,
# użyje jej z pamięci podręcznej (cache) przy kolejnym budowaniu, co znacznie
# przyspiesza proces. To prowadzi nas do pierwszej, kluczowej zasady.
#
# 2. Optymalizacja cache'u warstw
#
# **Zasada**: Umieszczaj instrukcje, które zmieniają się najrzadziej, na samej górze
# `Dockerfile`, a te, które zmieniają się najczęściej (jak kopiowanie kodu aplikacji),
# na samym dole.
#
# *   **Zły `Dockerfile`**:
#     FROM python:3.11-slim
#     WORKDIR /app
#     COPY . .  # Kopiuje WSZYSTKO na raz
#     RUN pip install -r requirements.txt
#     CMD ["uvicorn", "main:app"]
#
#     **Problem**: Przy każdej, nawet najmniejszej zmianie w kodzie (`main.py`), cała
#     warstwa `COPY` jest unieważniana, a co za tym idzie, Docker musi **ponownie instalować
#     wszystkie zależności** z `requirements.txt`, co jest bardzo wolne.
#
# *   **Dobry, zoptymalizowany `Dockerfile`**:
#     (To jest wersja, której nauczyliśmy się w poprzedniej lekcji i jest to standardowa dobra praktyka)

# 1. Obraz bazowy (zmienia się rzadko)
#FROM python:3.11-slim
# 2. Katalog roboczy
#WORKDIR /app
# 3. Kopiuj TYLKO plik z zależnościami
#COPY requirements.txt .
# 4. Instaluj zależności. Ta warstwa zostanie zbuforowana,
#    dopóki plik requirements.txt się nie zmieni.
#RUN pip install --no-cache-dir -r requirements.txt
# 5. DOPIERO TERAZ kopiuj resztę kodu, który zmienia się często.
#COPY . .
# 6. Port i komenda startowa
#EXPOSE 8000
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

#     **Efekt**: Teraz, gdy zmieniasz tylko kod w `main.py`, Docker unieważni tylko warstwę
#     `COPY . .` i błyskawicznie przebuduje obraz, wykorzystując z cache'u warstwę z już
#     zainstalowanymi zależnościami. Czas budowania skraca się z minut do sekund.
#
# 3. Redukcja rozmiaru obrazu
#
# Duże obrazy Dockera są problematyczne – wolniej się je przesyła do repozytoriów,
# dłużej startują i zajmują więcej miejsca na dysku.
#
#     **Technika 1: Używaj oficjalnych obrazów `-slim`**
#     Zamiast `python:3.11`, używaj `python:3.11-slim`. Wersje "slim" są pozbawione wielu
#     narzędzi i pakietów systemowych, które rzadko są potrzebne w typowej aplikacji
#     webowej, co znacząco zmniejsza ich rozmiar.
#
#     **Technika 2: Plik `.dockerignore`**
#     To odpowiednik pliku `.gitignore`. Możesz w nim zdefiniować pliki i foldery,
#     które **nigdy** nie powinny być kopiowane do obrazu. To kluczowe, aby unikać
#     kopiowania niepotrzebnych rzeczy.
#
#     # --- plik: .dockerignore ---
#     __pycache__/
#     *.pyc
#     .git
#     .venv/
#     Dockerfile
#     .dockerignore
#     # --- koniec pliku .dockerignore ---
#
#     **Technika 3: Wielostopniowe budowanie (Multi-stage Builds)**
#
#     To bardziej zaawansowana, ale niezwykle potężna technika. Pozwala ona użyć
#     jednego, "dużego" obrazu do zbudowania aplikacji (np. zainstalowania zależności),
#     a następnie skopiować tylko finalne artefakty do drugiego, "małego" i czystego
#     obrazu produkcyjnego.
#
#     *   **Przykład zaawansowanego `Dockerfile` z Multi-stage Build**:
#
# # --- ETAP 1: Budowanie (Builder Stage) ---
# # Używamy pełnego obrazu Pythona jako "środowiska budującego"
# FROM python:3.11 as builder
#
# WORKDIR /app
#
# # Tworzymy wirtualne środowisko wewnątrz obrazu budującego
# RUN python -m venv /opt/venv
# # Upewniamy się, że używamy pip z tego środowiska
# ENV PATH="/opt/venv/bin:$PATH"
#
# # Kopiujemy i instalujemy zależności do wirtualnego środowiska
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
#
#
# # --- ETAP 2: Produkcja (Production Stage) ---
# # Zaczynamy od nowa, z małego, czystego obrazu slim
# FROM python:3.11-slim
#
# WORKDIR /app
#
# # Kopiujemy TYLKO wirtualne środowisko z zainstalowanymi zależnościami
# # z poprzedniego etapu! Nie kopiujemy już narzędzi do budowania.
# COPY --from=builder /opt/venv /opt/venv
#
# # Kopiujemy nasz kod aplikacji
# COPY . .
#
# # Ustawiamy ścieżkę, aby używać Pythona z naszego skopiowanego środowiska
# ENV PATH="/opt/venv/bin:$PATH"
#
# EXPOSE 8000
#
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#
#     **Korzyść**: Finalny obraz produkcyjny zawiera tylko to, co jest absolutnie niezbędne
#     do uruchomienia aplikacji (Python, zależności, kod), a nie zawiera żadnych
#     narzędzi i plików tymczasowych, które były potrzebne tylko na etapie instalacji.
#
# 4. Podsumowanie
#
# Budowanie obrazów Dockera to coś więcej niż tylko napisanie kilku komend. To proces
# inżynieryjny, którego celem jest stworzenie obrazów, które są:
#
#     *   **Szybkie w budowaniu** (dzięki optymalizacji cache'u).
#     *   **Małe i wydajne** (dzięki `.dockerignore` i technikom multi-stage).
#     *   **Bezpieczne** (dzięki używaniu minimalnych obrazów bazowych).
#
# Najważniejsze do zapamiętania:
#
#     1.  **Kolejność ma znaczenie**: Rzeczy, które rzadko się zmieniają, umieszczaj na górze
#         `Dockerfile`.
#     2.  **Nie kopiuj śmieci**: Używaj `.dockerignore`, aby wykluczyć niepotrzebne pliki.
#     3.  **Używaj `-slim`**: To najprostszy sposób na zmniejszenie rozmiaru obrazu.
#     4.  **Rozważ Multi-stage Builds**: Dla aplikacji produkcyjnych jest to standardowa
#         praktyka, która pozwala na tworzenie minimalnych i bezpieczniejszych obrazów.
#
# Opanowanie tych technik sprawi, że Twoje procesy wdrożeniowe będą szybsze,
# a aplikacje lżejsze i bardziej bezpieczne.