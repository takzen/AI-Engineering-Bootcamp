# Moduł 9, Punkt 82: Tworzenie aplikacji z dostępem do dokumentacji
#
#
#
# Jednym z najbardziej frustrujących problemów, zarówno dla deweloperów, jak i dla użytkowników,
# jest przeszukiwanie obszernej, często chaotycznej dokumentacji. Znalezienie tej jednej,
# konkretnej informacji o funkcji, parametrze czy sposobie konfiguracji może zająć mnóstwo czasu.
#
# A co, jeśli moglibyśmy po prostu "zapytać" dokumentację o to, czego potrzebujemy,
# używając języka naturalnego? W tej lekcji zbudujemy dokładnie taką aplikację –
# inteligentnego asystenta, który będzie ekspertem od konkretnej, dostarczonej mu
# dokumentacji technicznej.
#
# 1. Problem: Dokumentacja jest dla ludzi, nie dla maszyn (do tej pory)
#
# Dokumentacja techniczna, czy to w formie stron internetowych, plików Markdown, czy PDF-ów,
# jest zoptymalizowana pod kątem czytania przez człowieka. Tradycyjne wyszukiwarki
# (oparte na słowach kluczowych) często zawodzą, ponieważ nie rozumieją intencji
# ani kontekstu zapytania.
#
# Przykład: Szukasz informacji o tym, "jak obsłużyć błędy w API". Tradycyjna wyszukiwarka
# może nie znaleźć nic, jeśli w dokumentacji użyto sformułowań "exception handling" lub
# "error responses". System oparty o RAG rozumie, że te frazy oznaczają to samo.
#
# 2. Architektura Asystenta Dokumentacji
#
# Nasza aplikacja będzie klasycznym, ale dobrze zaimplementowanym systemem RAG.
# Kluczem do sukcesu będzie staranne przygotowanie danych w fazie indeksowania.
#
#     *   **Faza Indeksowania**:
#         1.  **Loader**: Użyjemy specjalizowanych loaderów do wczytania treści bezpośrednio
#             ze stron internetowych (np. `WebBaseLoader`) lub z repozytorium kodu, gdzie
#             często przechowywana jest dokumentacja (np. w plikach `.md`).
#         2.  **Splitter**: Wybierzemy splitter, który potrafi inteligentnie dzielić tekst,
#             szanując strukturę kodu i nagłówków (np. `RecursiveCharacterTextSplitter`
#             skonfigurowany pod kątem Markdown lub kodu).
#         3.  **Embedding & Storing**: Stworzymy wektory i zapiszemy je w bazie, która będzie
#             naszą "encyklopedią" na temat danej technologii.
#
#     *   **Faza Odpowiadania**:
#         1.  **Retrieval**: Na podstawie pytania użytkownika, znajdziemy najbardziej
#             relevantne fragmenty dokumentacji.
#         2.  **Generation**: Poprosimy LLM, aby na podstawie tych fragmentów, nie tylko
#             odpowiedział na pytanie, ale też, jeśli to możliwe, **podał przykładowy
#             fragment kodu** i **link do źródłowego dokumentu**. To niezwykle podnosi
#             użyteczność aplikacji.
#
# 3. Praktyczny przykład: Asystent dokumentacji LangSmith
#
# Zbudujemy prosty system Q&A, który będzie odpowiadał na pytania na podstawie oficjalnej
# dokumentacji LangSmith. Wczytamy treść bezpośrednio ze strony internetowej.
#
# Krok 0: Instalacja
# pip install langchain-openai langchain-community faiss-cpu beautifulsoup4
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Ładowanie i indeksowanie dokumentacji
print("--- Faza 1: Ładowanie i indeksowanie dokumentacji LangSmith ---")

# Używamy loadera do wczytania treści z podanej strony internetowej
# (bs_kwargs ogranicza parsowanie do głównej treści strony)
loader = WebBaseLoader(
    web_path="https://docs.smith.langchain.com/overview",
    bs_kwargs=dict(parse_only=("main",)),
)
docs = loader.load()

# Dzielimy wczytany tekst na mniejsze fragmenty
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
documents = text_splitter.split_documents(docs)

print(f"Załadowano i podzielono na {len(documents)} fragmentów.")

# Tworzymy embeddingi i budujemy indeks FAISS
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)

# Tworzymy retriever, który będzie przeszukiwał naszą bazę
retriever = vectorstore.as_retriever()

print("Indeks wektorowy został pomyślnie stworzony.")

# Krok 2: Budowa łańcucha Q&A
print("\n--- Faza 2: Budowa łańcucha Q&A ---")
llm = ChatOpenAI(model="gpt-4o")

# Tworzymy prompt, który instruuje model, jak ma korzystać z kontekstu
# i prosi o cytowanie źródeł
prompt = ChatPromptTemplate.from_template("""Jesteś ekspertem od dokumentacji LangSmith.
Odpowiedz na pytanie użytkownika, bazując wyłącznie na poniższym kontekście.
Jeśli to możliwe, podaj link do źródła, który znajduje się w metadanych.

Kontekst:
{context}

Pytanie: {input}

Odpowiedź:""")

# Budujemy łańcuchy, tak jak w poprzedniej lekcji (ale bez historii rozmowy)
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# Krok 3: Testowanie aplikacji
print("\n--- Faza 3: Testowanie aplikacji ---")

# Pytanie 1
question1 = "What is LangSmith?"
print(f"\nUżytkownik: {question1}")
response1 = retrieval_chain.invoke({"input": question1})
print(f"Asystent: {response1['answer']}")

# Pytanie 2
question2 = "How can I test my LLM applications?"
print(f"\nUżytkownik: {question2}")
response2 = retrieval_chain.invoke({"input": question2})
print(f"Asystent: {response2['answer']}")


# 4. Dalsze kroki i ulepszenia
#
# Ten prosty system to doskonała baza. Można go rozbudować o:
#
#     *   **Wczytywanie wielu źródeł**: `WebBaseLoader` może przyjąć listę adresów URL,
#         aby zbudować bazę wiedzy z całej witryny dokumentacji.
#     *   **Obsługa wielu typów plików**: Można połączyć kilka loaderów (dla stron WWW,
#         PDF-ów, plików Markdown) w jeden pipeline.
#     *   **Pamięć konwersacji**: Można go przekształcić w chatbota, dodając mechanizm
#         `create_history_aware_retriever`, który poznaliśmy wcześniej.
#     *   **Cytowanie źródeł**: Można zmodyfikować prompt i logikę tak, aby na końcu
#         odpowiedzi zawsze pojawiała się lista dokumentów, z których skorzystano,
#         wraz z linkami.
#
# 5. Podsumowanie
#
# Stworzenie inteligentnego asystenta dokumentacji to jedno z najbardziej praktycznych
# i wartościowych zastosowań technologii RAG. Drastycznie skraca ono czas potrzebny
# na znalezienie informacji i obniża barierę wejścia do nauki nowych technologii.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Dobry Loader to podstawa**: Wybierz loader odpowiedni do formatu, w jakim
#         przechowywana jest Twoja dokumentacja.
#     2.  **Inteligentny Splitting**: Dostosuj parametry splittera do charakteru treści
#         (np. inaczej dzielimy prozę, a inaczej kod).
#     3.  **Prompt jest kluczowy**: Poświęć czas na stworzenie promptu, który nie tylko
#         prosi o odpowiedź, ale także o cytowanie źródeł i podawanie przykładów,
#         co znacząco podnosi jakość i użyteczność finalnej aplikacji.
#
# Masz teraz w ręku przepis na zbudowanie narzędzia, które może zaoszczędzić setki
# godzin pracy Tobie i Twojemu zespołowi.