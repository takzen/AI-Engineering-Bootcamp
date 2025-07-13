# Moduł 9, Punkt 85: Tworzenie inteligentnych systemów rekomendacyjnych
#
#
#
# Systemy rekomendacyjne są jednym z filarów współczesnego internetu. Jednak tradycyjne
# podejścia często opierają się na analizie zachowań (filtrowanie kolaboracyjne) lub
# prostym dopasowaniu tagów (filtrowanie oparte na treści). Mają one problem ze
# zrozumieniem złożonych, ludzkich preferencji wyrażonych w języku naturalnym.
#
# Technika RAG (Retrieval-Augmented Generation) pozwala nam zbudować zupełnie nową
# generację systemów rekomendacyjnych – **systemów konwersacyjnych i rozumiejących**.
# Zamiast klikać w produkty, użytkownik może po prostu **opisać**, czego szuka,
# a system, niczym doświadczony doradca, znajdzie dla niego idealne propozycje.
#
# 1. Jak RAG rewolucjonizuje rekomendacje?
#
# Wyobraź sobie, że prowadzisz księgarnię.
#
#     *   **Tradycyjny system**: "Pokaż mi książki z kategorii 'fantastyka'."
#     *   **System oparty o RAG**: "Szukam książki fantasy, która jest mroczna i filozoficzna jak
#         film 'Blade Runner', ale unika typowych tropów z elfami i krasnoludami."
#
# Tradycyjny system nie zrozumie takiego zapytania. System RAG, dzięki magii embeddingów
# i LLM-ów, jest w stanie pojąć te niuanse, znaleźć odpowiednich kandydatów i uzasadnić
# swój wybór.
#
# 2. Architektura systemu rekomendacyjnego RAG
#
# Architektura jest bardzo podobna do systemu Q&A, ale zmienia się cel i zawartość bazy wiedzy.
#
#     1.  **Indeksowanie (Baza Produktów)**:
#         *   **Dane**: Zamiast fragmentów dokumentacji, nasza baza wiedzy zawiera **szczegółowe,
#           dobrze napisane opisy każdego produktu** (np. książki, filmu, kursu online).
#         *   **Proces**: Każdy opis produktu jest zamieniany na wektor (embedding) i przechowywany
#           w bazie wektorowej. Dobra jakość opisów jest tu absolutnie kluczowa!
#
#     2.  **Rekomendacja (Wyszukiwanie i Generowanie)**:
#         *   **Zapytanie**: Użytkownik wpisuje swoje preferencje w języku naturalnym.
#         *   **Retrieval**: System zamienia zapytanie na wektor i wyszukuje w bazie **produkty
#           o najbardziej podobnych semantycznie opisach**.
#         *   **Generation**: Znalezione produkty (kandydaci) są przekazywane do LLM-a wraz z
#           oryginalnym zapytaniem i specjalnym promptem.
#
# 3. Kluczowy element: Prompt rekomendacyjny
#
# Prompt w systemie rekomendacyjnym jest inny niż w Q&A. Jego zadaniem jest nie tylko
# odpowiedzieć, ale **przekonać, doradzić i uzasadnić**.
#
# Przykład dobrego promptu rekomendacyjnego:
# ```
# Jesteś światowej klasy, entuzjastycznym doradcą klienta w naszej księgarni.
# Twoim zadaniem jest pomoc klientowi w znalezieniu idealnej książki.
#
# Na podstawie jego prośby oraz poniższej listy książek-kandydatów, które pasują do jego opisu,
# wybierz 1-3 najlepsze propozycje.
#
# Dla każdej propozycji:
# 1. Podaj tytuł.
# 2. Napisz krótkie, angażujące uzasadnienie, dlaczego TA konkretna książka spodoba się klientowi,
#    nawiązując bezpośrednio do jego prośby.
#
# Kandydaci:
# {context}
#
# Prośba klienta:
# {question}
#
# Twoje rekomendacje:
# ```
#
# 4. Praktyczny przykład: Doradca filmowy
#
# Zbudujemy prosty system, który na podstawie opisu nastroju i preferencji poleci film
# z naszej małej, wewnętrznej bazy.
#
# Krok 0: Instalacja i przygotowanie danych
# # (Używamy tych samych pakietów co w poprzedniej lekcji)
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Stworzenie bazy wektorowej z opisami produktów (filmów)
print("--- Indeksowanie bazy filmów ---")
movie_descriptions = [
    Document(page_content="Matrix: Innowacyjny thriller science-fiction, pełen akcji, filozoficznych pytań o naturę rzeczywistości i ikonicznego stylu cyberpunku.", metadata={"title": "Matrix"}),
    Document(page_content="Forrest Gump: Ciepła, wzruszająca i pełna humoru opowieść o życiu prostego człowieka, która jest jednocześnie podróżą przez historię Ameryki. Idealny film na poprawę nastroju.", metadata={"title": "Forrest Gump"}),
    Document(page_content="Blade Runner 2049: Mroczne, powolne i wizualnie oszałamiające kino neo-noir. Stawia głębokie pytania o to, co to znaczy być człowiekiem w świecie pełnym technologii.", metadata={"title": "Blade Runner 2049"})
]
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(movie_descriptions, embeddings)
retriever = vectorstore.as_retriever()

# Krok 2: Zdefiniowanie promptu i łańcucha rekomendacyjnego
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

recommendation_template = """Jesteś entuzjastycznym kinomanem i doradcą. Twoim zadaniem jest polecenie idealnego filmu.
Na podstawie prośby użytkownika i poniższych opisów filmów, które pasują do jego zapytania,
sformułuj angażującą i spersonalizowaną rekomendację.

Dopasowane filmy (kontekst):
{context}

Prośba użytkownika:
{question}

Twoja rekomendacja:
"""
recommendation_prompt = ChatPromptTemplate.from_template(recommendation_template)

# Budujemy łańcuch RAG, tak jak w poprzedniej lekcji
recommendation_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | recommendation_prompt
    | llm
    | StrOutputParser()
)

# Krok 3: Testowanie systemu
print("\n--- Testowanie doradcy filmowego ---")

user_request = "Szukam czegoś do myślenia, w mrocznym klimacie science-fiction, ale niekoniecznie z masą akcji."
print(f"PROŚBA KLIENTA: {user_request}")

# Uruchamiamy łańcuch
recommendation = recommendation_chain.invoke(user_request)

print(f"\nREKOMENDACJA BOTA:\n{recommendation}")

#
# 5. Podsumowanie
#
# Wykorzystanie RAG do budowy systemów rekomendacyjnych to potężna technika, która
# przenosi interakcję z klientem na zupełnie nowy, konwersacyjny poziom.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Jakość opisów jest kluczowa**: Baza wektorowa jest tak dobra, jak opisy, które
#         do niej włożysz. Bogate, szczegółowe opisy produktów pozwalają na znacznie
#         lepsze dopasowanie semantyczne.
#     2.  **Prompt definiuje "osobowość" doradcy**: To w prompcie decydujesz, czy Twój
#         system ma być formalnym ekspertem, entuzjastycznym sprzedawcą czy analitycznym
#         porównywarką.
#     3.  **Rekomendacja to więcej niż odpowiedź**: Celem jest nie tylko podanie listy
#         produktów, ale zbudowanie zaufania poprzez trafne, spersonalizowane uzasadnienie
#         wyboru.
#
# Opanowując ten wzorzec, jesteś w stanie budować systemy, które nie tylko sprzedają,
# ale przede wszystkim rozumieją i doradzają, tworząc znacznie lepsze doświadczenia
# dla użytkowników.