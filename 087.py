# Moduł 9, Punkt 87: Testowanie i optymalizacja RAG
#
#
#
# Zbudowaliśmy już kilka potężnych aplikacji opartych o RAG. Działają, odpowiadają
# na pytania, dają rekomendacje. Ale skąd wiemy, czy działają **dobrze**?
# Skąd wiemy, że nasz system jest **lepszy** niż proste wyszukiwanie po słowach kluczowych?
# A co ważniejsze, skąd wiemy, że zmiana, którą właśnie wprowadziliśmy (np. nowy
# model embeddingowy, inny rozmiar chunka), faktycznie coś poprawiła?
#
# W tej lekcji zajmiemy się systematycznym i mierzalnym podejściem do testowania
# i optymalizacji pipeline'ów RAG. To proces, który zamienia budowanie RAG
# z intuicyjnej sztuki w precyzyjną inżynierię.
#
# 1. Dwa filary jakości w RAG
#
# Jakość systemu RAG opiera się na dwóch głównych filarach, i oba musimy mierzyć:
#
#     1.  **Jakość Wyszukiwania (Retrieval Quality)**:
#         *   **Pytanie**: Czy nasz system potrafi znaleźć **właściwe** fragmenty dokumentów
#           w odpowiedzi na pytanie użytkownika?
#         *   **Metryki**: `Hit Rate` (czy przynajmniej jeden poprawny dokument został znaleziony?),
#           `MRR` (Mean Reciprocal Rank - jak wysoko na liście wyników jest pierwszy poprawny dokument?).
#
#     2.  **Jakość Generowania (Generation Quality)**:
#         *   **Pytanie**: Zakładając, że system znalazł dobre fragmenty, czy potrafi na
#           ich podstawie sformułować **poprawną, wierną i użyteczną** odpowiedź?
#         *   **Metryki**: `Faithfulness` (czy odpowiedź trzyma się faktów z podanego kontekstu?),
#           `Answer Relevancy` (czy odpowiedź jest na temat?), `Conciseness` (zwięzłość).
#
# Optymalizacja polega na iteracyjnym ulepszaniu obu tych filarów.
#
# 2. RAGAs: Framework do ewaluacji RAG
#
# Ręczna ocena tych metryk jest żmudna i subiektywna. Na szczęście istnieją
# wyspecjalizowane narzędzia, takie jak **RAGAs**. Jest to framework open-source,
# który pozwala na automatyczną, opartą na LLM-ach, ewaluację jakości pipeline'ów RAG.
#
# *   **Jak to działa?**: RAGAs używa LLM-ów do "oceniania" pracy innego LLM-a.
#     Na przykład, aby ocenić `Faithfulness`, RAGAs prosi LLM-ewaluatora: "Oto
#     wygenerowana odpowiedź i kontekst, na którym miała się opierać. Zidentyfikuj
#     wszystkie stwierdzenia w odpowiedzi, które NIE wynikają z podanego kontekstu."
# *   **Integracja z LangChain**: RAGAs jest głęboko zintegrowany z ekosystemem
#     LangChain, co ułatwia jego użycie.
#
# 3. Praktyczny przykład: Ewaluacja prostego systemu RAG
#
# Zbudujemy prosty pipeline RAG i zobaczymy, jak można go ocenić za pomocą RAGAs.
#
# Krok 0: Instalacja
# # pip install langchain-openai faiss-cpu ragas datasets
import os
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 1: Budowa pipeline'u RAG do przetestowania
# (Uproszczony pipeline dla demonstracji)
documents = [
    Document(page_content="Warszawa jest stolicą Polski i największym miastem w kraju.", metadata={"source": "doc1"}),
    Document(page_content="Paryż to stolica Francji, znana z Wieży Eiffla.", metadata={"source": "doc2"})
]
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

template = "Kontekst: {context}\n\nPytanie: {question}\n\nOdpowiedź:"
prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Krok 2: Przygotowanie zestawu danych do ewaluacji
# W RAGAs, zestaw danych potrzebuje kilku kluczowych kolumn.
eval_data = {
    'question': [
        "Jaka jest stolica Polski?",
        "Co jest symbolem Paryża?"
    ],
    'ground_truth': [ # Wzorcowa, idealna odpowiedź
        "Stolicą Polski jest Warszawa.",
        "Symbolem Paryża jest Wieża Eiffla."
    ]
}
eval_dataset = Dataset.from_dict(eval_data)

# Krok 3: Uruchomienie ewaluacji
# Ta funkcja opakowuje nasz łańcuch, aby RAGAs mógł go wywołać
def get_ragas_response(query_dict):
    response = rag_chain.invoke(query_dict['question'])
    # RAGAs potrzebuje 'answer' i 'contexts'
    # Pobieramy kontekst z retrievera
    contexts = [doc.page_content for doc in retriever.invoke(query_dict['question'])]
    return {"answer": response, "contexts": contexts}

# Przetwarzamy nasz zestaw danych, aby dodać odpowiedzi z naszego pipeline'u
results_list = []
for entry in eval_dataset:
    response_dict = get_ragas_response(entry)
    results_list.append({
        "question": entry['question'],
        "ground_truth": entry['ground_truth'],
        "answer": response_dict['answer'],
        "contexts": response_dict['contexts']
    })
results_dataset = Dataset.from_list(results_list)

# Uruchamiamy ewaluację z wybranymi metrykami
print("--- Uruchamianie ewaluacji RAGAs ---")
evaluation_result = evaluate(
    dataset=results_dataset,
    metrics=[
        faithfulness,      # Czy odpowiedź trzyma się kontekstu?
        answer_relevancy,  # Czy odpowiedź jest na temat?
        context_recall,    # Czy retriever znalazł wszystkie potrzebne informacje?
        context_precision, # Czy w pobranym kontekście nie ma śmieci?
    ],
)

print("\n--- Wyniki ewaluacji ---")
print(evaluation_result)
# Wynikiem będzie słownik z ocenami dla każdej metryki, np. {'faithfulness': 1.0, 'answer_relevancy': 0.95, ...}

#
# 4. Iteracyjny proces optymalizacji
#
# Mając te mierzalne wyniki, możemy zacząć eksperymentować i optymalizować.
#
# 1.  **Postaw hipotezę**: "Myślę, że zwiększenie rozmiaru chunka (`chunk_size`) poprawi
#     `context_recall`, ponieważ retriever będzie pobierał więcej otaczającego kontekstu."
# 2.  **Zbuduj wariant**: Stwórz nową wersję swojego pipeline'u ze zmienionym `chunk_size`.
# 3.  **Przeprowadź ewaluację**: Uruchom ten sam zestaw danych na nowej wersji.
# 4.  **Porównaj wyniki**: Porównaj wyniki metryk z obu wersji. Czy `context_recall` faktycznie
#     wzrósł? Czy nie pogorszyła się przy tym `context_precision`?
#
# Ten cykl pozwala na podejmowanie decyzji o optymalizacji w oparciu o twarde dane,
# a nie intuicję.
#
# 5. Podsumowanie
#
# Testowanie i optymalizacja RAG to proces naukowy, który wymaga odpowiednich narzędzi
# i metodycznego podejścia.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Mierz oba filary**: Zawsze oceniaj zarówno jakość wyszukiwania (retrieval),
#         jak i jakość generowania odpowiedzi.
#     2.  **Automatyzuj ewaluację**: Używaj frameworków takich jak RAGAs, aby uzyskać
#         obiektywne, mierzalne i powtarzalne wyniki oceny jakości.
#     3.  **Buduj "złoty" zestaw danych**: Stwórz i pielęgnuj wysokiej jakości zestaw
#         danych testowych, który będzie Twoim benchmarkiem do mierzenia postępów.
#     4.  **Optymalizuj iteracyjnie**: Wprowadzaj jedną zmianę na raz i mierz jej wpływ
#         na metryki. To jedyny sposób, aby naprawdę zrozumieć, co poprawia Twój system.
#
# Dzięki takiemu podejściu, jesteś w stanie przekształcić swój działający prototyp RAG
# w wysoce zoptymalizowany, niezawodny i precyzyjny system informacyjny.