# Moduł 10, Punkt 96: Uruchamianie aplikacji AI w kontenerze
#
#
#
# Stworzyliśmy zoptymalizowany, lekki i bezpieczny obraz Dockera dla naszej aplikacji.
# Mamy naszą idealną "paczkę". Teraz czas nauczyć się, jak ją "rozpakować" i uruchomić
# jako działający kontener. To właśnie w tym kroku nasza skonteneryzowana aplikacja
# zaczyna żyć i służyć użytkownikom.
#
# W tej lekcji poznamy najważniejsze komendy do zarządzania cyklem życia kontenerów
# oraz techniki, które ułatwiają pracę z nimi podczas rozwoju i na produkcji.
#
# 1. Obraz vs. Kontener – Kluczowe rozróżnienie
#
# Zanim przejdziemy do komend, ugruntujmy tę fundamentalną różnicę:
#
#     *   **Obraz (Image)**: To jest szablon, przepis, plik na dysku. Jest niezmienny i
#         stanowi "klasę" w programowaniu obiektowym. Zawiera wszystko: system operacyjny,
#         biblioteki, kod.
#
#     *   **Kontener (Container)**: To jest żywa, uruchomiona instancja obrazu. Jest to
#         "obiekt" stworzony na podstawie klasy. Można go uruchamiać, zatrzymywać,
#         restartować i usuwać. Można mieć wiele kontenerów działających na podstawie
#         tego samego obrazu.
#
# 2. Podstawowe komendy do zarządzania kontenerami
#
# Wszystkie te komendy wykonujemy w terminalu, na maszynie z zainstalowanym Dockerem.
# Załóżmy, że nasz obraz ma nazwę `my-ai-api`.
#
#     **a) Uruchamianie kontenera: `docker run`**
#
#     To najważniejsza komenda. Poznaliśmy ją już wcześniej, ale teraz rozbijmy ją na
#     części i poznajmy najważniejsze flagi:
#
# docker run -d -p 8080:8000 --name my-app-instance1 my-ai-api
#
#     *   `docker run`: Główna komenda.
#     *   `-d` (`--detach`): Uruchamia kontener w **tle** (w trybie "detached"). Bez tej flagi,
#         Twój terminal byłby zablokowany przez logi z kontenera.
#     *   `-p 8080:8000` (`--publish`): **Mapowanie portów**. To kluczowy element. Mówi on Dockerowi:
#         "Wszystko, co przychodzi na port `8080` na mojej maszynie-hoście, przekaż do portu
#         `8000` wewnątrz kontenera". `8000` to port, który wystawiliśmy (`EXPOSE`)
#         w `Dockerfile` i na którym nasłuchuje Uvicorn.
#     *   `--name my-app-instance1`: Nadaje kontenerowi przyjazną, unikalną nazwę. Ułatwia to
#         późniejsze zarządzanie nim.
#     *   `my-ai-api`: Nazwa obrazu, z którego ma powstać kontener.
#
#     **b) Listowanie działających kontenerów: `docker ps`**
#
#     Jak sprawdzić, co aktualnie działa?
#
# docker ps
#
#     # Zobaczymy tabelę z informacjami o wszystkich uruchomionych kontenerach:
#     # ID kontenera, nazwę obrazu, komendę, czas działania, status, porty i nazwę.
#
#     # Aby zobaczyć WSZYSTKIE kontenery (również te zatrzymane), dodaj flagę -a:
# docker ps -a
#
#     **c) Zaglądanie do logów kontenera: `docker logs`**
#
#     Twój kontener działa w tle, ale co jeśli chcesz zobaczyć, co wypisuje na standardowe
#     wyjście (np. logi z Uvicorna)?
#
# docker logs my-app-instance1
#
#     # Aby śledzić logi w czasie rzeczywistym (jak `tail -f` w Linuksie), dodaj flagę -f:
# docker logs -f my-app-instance1
#
#     **d) Zatrzymywanie, uruchamianie i restartowanie kontenera**
#
#     Zarządzanie stanem kontenera jest proste:
#
# # Zatrzymuje działający kontener
# docker stop my-app-instance1
#
# # Uruchamia ponownie zatrzymany kontener
# docker start my-app-instance1
#
# # Zatrzymuje i natychmiast uruchamia ponownie
# docker restart my-app-instance1
#
#     **e) Usuwanie kontenera: `docker rm`**
#
#     Gdy kontener nie jest już potrzebny, możesz go usunąć. **Uwaga: kontener musi być
#     najpierw zatrzymany!**
#
# docker stop my-app-instance1
# docker rm my-app-instance1
#
#     # Skrót do zatrzymania i usunięcia za jednym razem (używaj ostrożnie!):
# docker rm -f my-app-instance1
#
# 3. Przekazywanie zmiennych środowiskowych – klucz do konfiguracji
#
# Nasza aplikacja AI potrzebuje kluczy API. **NIGDY nie wpisuj kluczy na stałe do `Dockerfile`!**
# Byłoby to ogromne zagrożenie bezpieczeństwa. Zamiast tego, przekazujemy je jako
# **zmienne środowiskowe** podczas uruchamiania kontenera za pomocą flagi `-e`.
#
# docker run -d -p 8080:8000 \
#   -e OPENAI_API_KEY="sk-..." \
#   -e TAVILY_API_KEY="tvly-..." \
#   --name my-secure-app \
#   my-ai-api
#
#     *   **Jak to działa?**: Docker ustawia te zmienne środowiskowe wewnątrz kontenera,
#         zanim uruchomi główną komendę. Nasz kod Pythona, używając `os.environ.get("OPENAI_API_KEY")`,
#         będzie mógł je normalnie odczytać.
#     *   **Zaleta**: Kod aplikacji pozostaje czysty i uniwersalny. Konfiguracja (klucze,
#         ustawienia bazy danych itp.) jest wstrzykiwana z zewnątrz w momencie uruchomienia.
#
# 4. Podsumowanie
#
# Opanowanie tych kilku podstawowych komend daje Ci pełną kontrolę nad cyklem życia
# Twoich skonteneryzowanych aplikacji.
#
# Najważniejsze do zapamiętania:
#
#     1.  **`docker run` tworzy i uruchamia**: To podstawowa komenda, a jej najważniejsze
#         flagi to `-d` (działanie w tle) i `-p` (mapowanie portów).
#     2.  **`docker ps` pokazuje, co działa**: To Twoje centrum dowodzenia do sprawdzania
#         statusu kontenerów.
#     3.  **`docker logs` pozwala zajrzeć do środka**: Niezbędne do debugowania problemów
#         w działającej aplikacji.
#     4.  **`stop`/`start`/`rm` do zarządzania cyklem życia**: Proste komendy do kontrolowania
#         kontenerów.
#     5.  **Używaj zmiennych środowiskowych (`-e`) do konfiguracji**: Nigdy nie umieszczaj
#         wrażliwych danych (jak klucze API) bezpośrednio w obrazie.
#
# Mając tę wiedzę, jesteś w stanie nie tylko budować przenośne obrazy, ale także
# efektywnie zarządzać nimi w dowolnym środowisku deweloperskim czy produkcyjnym.