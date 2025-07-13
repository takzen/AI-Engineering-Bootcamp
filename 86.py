# Moduł 9, Punkt 86: Analiza dużych zbiorów danych w RAG
#
#
#
# Do tej pory postrzegaliśmy RAG głównie jako narzędzie do **odpowiadania na pytania** –
# system pobierał kilka relevantnych fragmentów, aby odpowiedzieć na jedno, konkretne
# zapytanie. Ale co, jeśli nasze zadanie jest znacznie szersze? Co, jeśli chcemy
# **zrozumieć i zsyntetyzować cały duży dokument** lub nawet zbiór setek dokumentów?
#
# Przykład: "Przeanalizuj ten 1000-stronicowy raport finansowy i wypisz 5 największych
# ryzyk i szans dla firmy."
#
# Tradycyjny RAG, który pobiera tylko kilka najbardziej podobnych fragmentów, zawiedzie,
# ponieważ kluczowe informacje mogą być rozproszone po całym dokumencie. W tej lekcji
# poznamy zaawansowane techniki RAG, które pozwalają na analizę i syntezę informacji
# z dużych zbiorów danych.
#
# 1. Problem: Ograniczone okno kontekstowe
#
# Głównym ograniczeniem jest **limit okna kontekstowego** LLM-ów. Nie możemy po prostu
# "wkleić" całego 1000-stronicowego raportu do promptu. Nawet jeśli go podzielimy,
# standardowy retriever pobierze tylko kilka fragmentów, które pasują do ogólnego
# zapytania "ryzyka i szanse", prawdopodobnie pomijając wiele istotnych detali.
#
# Musimy więc zastosować bardziej zaawansowaną strategię, która pozwoli modelowi
# "przeczytać" i przetworzyć cały dokument w sposób ustrukturyzowany.
#
# 2. Architektura: Wzorzec "Map-Reduce"
#
# Jednym z najpotężniejszych wzorców do analizy dużych zbiorów danych jest **Map-Reduce**.
# To koncepcja zapożyczona z systemów przetwarzania Big Data, którą możemy zaadaptować
# do świata LLM.
#
# Proces składa się z dwóch głównych faz:
#
#     *   **Faza "Map" (Mapowanie)**:
#         1.  Dzielimy cały duży dokument (lub zbiór dokumentów) na mniejsze fragmenty (chunki).
#         2.  Następnie, **iterujemy po każdym fragmencie z osobna** i prosimy LLM o wykonanie
#             na nim tej samej, małej operacji. Na przykład: "Czy ten fragment tekstu
#             wspomina o jakimkolwiek ryzyku finansowym? Jeśli tak, wypisz je krótko."
#         3.  W ten sposób, zamiast jednego dużego zadania, mamy setki małych, równoległych
#             zadań. LLM działa jak "mapa", która przekształca każdy fragment w mały
#             kawałek interesującej nas informacji.
#
#     *   **Faza "Reduce" (Redukcja)**:
#         1.  Zbieramy wszystkie wyniki z fazy "Map" (czyli listę wszystkich zidentyfikowanych
#             ryzyk z każdego fragmentu).
#         2.  Tę skompilowaną listę przekazujemy do LLM-a po raz ostatni, z zadaniem
#             **syntezy i podsumowania**. Na przykład: "Oto lista wszystkich ryzyk
#             wspomnianych w raporcie. Zgrupuj je tematycznie, usuń duplikaty i przedstaw
#             5 najważniejszych."
#
# 3. Praktyczny przykład: Synteza recenzji produktu
#
# Zbudujemy pipeline, który przeanalizuje zbiór recenzji produktu, w fazie "Map" wyciągnie
# z każdej z nich główne zalety i wady, a w fazie "Reduce" stworzy ogólne podsumowanie.
#
# Krok 0: Instalacja
# # (Używamy tych samych pakietów co w poprzednich lekcjach)
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_text_splitters import CharacterTextSplitter

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Przygotowanie danych (zbiór recenzji)
reviews = [
    "Ten telefon ma niesamowity aparat, zdjęcia wychodzą rewelacyjnie. Niestety, bateria trzyma bardzo krótko.",
    "Bateria to dramat, nie wytrzymuje nawet całego dnia. Ale muszę przyznać, że jakość zdjęć jest powalająca.",
    "Jestem zachwycony ekranem, kolory są żywe i jasne. Aparat też jest na najwyższym poziomie. Czas pracy na baterii mógłby być lepszy.",
    "Główna zaleta to zdecydowanie aparat. Jest szybki, a zdjęcia ostre. Z drugiej strony, bateria to największa wada tego modelu.",
    "Ekran tego urządzenia jest przepiękny, oglądanie filmów to czysta przyjemność. Wydajność też jest świetna."
]
documents = [Document(page_content=r) for r in reviews]

# Inicjalizacja LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Krok 2: Definicja łańcucha dla fazy "Map"
# Ten łańcuch będzie uruchamiany dla KAŻDEJ recenzji z osobna.
map_template = """Przeanalizuj poniższą recenzję produktu i wypisz jej główne zalety i wady.
Jeśli nie ma wad lub zalet, napisz o tym.

Recenzja:
"{doc_text}"

Zalety i Wady:"""
map_prompt = ChatPromptTemplate.from_template(map_template)
map_chain = create_stuff_documents_chain(llm, map_prompt)

# Krok 3: Definicja łańcucha dla fazy "Reduce"
# Ten łańcuch otrzyma WSZYSTKIE wyniki z fazy "Map" i je podsumuje.
reduce_template = """Oto lista zalet i wad wyciągniętych z wielu recenzji produktu.
Twoim zadaniem jest stworzenie ogólnego, zwięzłego podsumowania.
Zidentyfikuj najczęściej powtarzające się motywy i przedstaw je w klarowny sposób.

Lista fragmentów:
{doc_summaries}

Podsumowanie:"""
reduce_prompt = ChatPromptTemplate.from_template(reduce_template)
reduce_chain = create_stuff_documents_chain(llm, reduce_prompt)

# Krok 4: Połączenie wszystkiego w MapReduceDocumentsChain
# Ten specjalny łańcuch automatyzuje cały proces Map-Reduce.
# `document_variable_name` mówi mu, jak ma nazywać pojedynczy dokument w `map_template`
# `return_intermediate_steps=True` pozwala nam zobaczyć wyniki z fazy "Map"
map_reduce_chain = MapReduceDocumentsChain(
    llm_chain=map_chain,
    reduce_documents_chain=ReduceDocumentsChain(
        combine_documents_chain=reduce_chain,
        collapse_documents_chain=reduce_chain,
        token_max=4000
    ),
    document_variable_name="doc_text",
    return_intermediate_steps=True
)

# Krok 5: Uruchomienie pipeline'u
print("--- Uruchamianie analizy Map-Reduce ---")
result = map_reduce_chain.invoke(documents)

print("\n--- KROKI POŚREDNIE (FAZA MAP) ---")
for i, step in enumerate(result['intermediate_steps']):
    print(f"Recenzja {i+1}:\n{step}\n")

print("\n--- WYNIK KOŃCOWY (FAZA REDUCE) ---")
print(result['output_text'])


# 4. Podsumowanie
#
# Wzorzec Map-Reduce to potężna technika, która pozwala "przeskalować" zdolności
# analityczne LLM-ów na praktycznie nieograniczone ilości danych.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Dziel i zwyciężaj**: Rozbijaj jeden duży, niemożliwy do przetworzenia problem
#         na setki mniejszych, łatwych do wykonania zadań.
#     2.  **Dwie fazy**: Najpierw "mapuj" (wyciągaj kluczowe informacje z każdego fragmentu),
#         a następnie "redukuj" (syntetyzuj i podsumowuj zebrane informacje).
#     3.  **Równoległość**: Krok "Map" jest z natury wysoce zrównoleglalny. W systemach
#         produkcyjnych, analizę każdego fragmentu można uruchomić jako osobne,
#         równoległe zadanie, co drastycznie skraca czas przetwarzania.
#     4.  **Uniwersalność**: Ten wzorzec można zastosować do wielu zadań: analizy sentymentu
#         w tysiącach komentarzy, ekstrakcji danych z setek umów prawnych, czy tworzenia
#         streszczeń z wielotomowych dzieł.
#
# Opanowując tę technikę, jesteś w stanie wykorzystać LLM-y nie tylko jako narzędzia
# do odpowiadania na pytania, ale jako potężne silniki analityczne dla dużych zbiorów danych.