# Moduł 9, Punkt 81: Tworzenie chatbotów z bazą wiedzy
#
#
#
# Do tej pory poznaliśmy wszystkie fundamentalne klocki systemu RAG: ładowanie dokumentów,
# dzielenie ich na fragmenty, tworzenie wektorów i przechowywanie ich w bazie.
# Teraz czas na najciekawszy etap: złożenie tych wszystkich elementów w jedną, spójną
# całość – **chatbota, który potrafi prowadzić rozmowę w oparciu o dostarczoną mu wiedzę**.
#
# W tej lekcji zbudujemy kompletny pipeline, który naśladuje działanie komercyjnych
# rozwiązań typu "Chat with your PDF". Zobaczymy, jak połączyć wyszukiwanie w bazie
# wektorowej z pamięcią konwersacji, aby stworzyć naturalne i kontekstowe doświadczenie
# dla użytkownika.
#
# 1. Problem: Kontekst to więcej niż tylko ostatnie pytanie
#
# Prosty system Q&A na dokumentach działa w prosty sposób: bierze pytanie, szuka odpowiedzi
# i zapomina o sprawie. Chatbot musi działać inaczej. Rozważmy taką konwersację:
#
#     *   **Użytkownik**: "Jakie są główne cechy frameworka LangChain?"
#     *   **Bot**: (Szuka w bazie i odpowiada) "Główne cechy to modularność, agenci, łańcuchy..."
#     *   **Użytkownik**: "A co z jego zastosowaniem w chatbotach?"
#
# Pytanie "A co z jego zastosowaniem w chatbotach?" jest niekompletne. Aby system mógł na
# nie poprawnie odpowiedzieć, musi pamiętać, że "jego" odnosi się do "frameworka LangChain"
# z poprzedniego pytania.
#
# 2. Architektura chatbota RAG z pamięcią
#
# Aby rozwiązać ten problem, musimy połączyć dwie koncepcje, które już znamy:
#
#     *   **System RAG**: Do wyszukiwania informacji w bazie wiedzy.
#     *   **Pamięć Konwersacji**: Do przechowywania historii rozmowy.
#
# Nasz zaawansowany pipeline będzie wyglądał następująco:
#
#     1.  **Generowanie samodzielnego pytania**: Bierzemy nowe pytanie użytkownika ORAZ historię
#         rozmowy i przekazujemy je do LLM-a z zadaniem: "Na podstawie tej konwersacji, przeformułuj
#         ostatnie pytanie tak, aby było w pełni samodzielne i zrozumiałe bez kontekstu".
#         (Wynik: "Jakie jest zastosowanie frameworka LangChain w chatbotach?").
#
#     2.  **Wyszukiwanie (Retrieval)**: Używamy tego nowego, samodzielnego pytania do przeszukania
#         naszej bazy wektorowej w poszukiwaniu relevantnych fragmentów.
#
#     3.  **Generowanie odpowiedzi**: Bierzemy oryginalne pytanie, historię rozmowy ORAZ znalezione
#         fragmenty i przekazujemy je do głównego LLM-a z instrukcją: "Biorąc pod uwagę całą tę
#         konwersację oraz poniższy kontekst, odpowiedz na ostatnie pytanie użytkownika".
#
# Ten trójetapowy proces zapewnia, że bot rozumie pełen kontekst rozmowy i jednocześnie
# opiera swoje odpowiedzi na faktach z bazy wiedzy.
#
# 3. Praktyczny przykład: Budowa łańcucha konwersacyjnego RAG
#
# Zbudujemy ten zaawansowany łańcuch, używając `Runnable` z LangChain Expression Language (LCEL).
#
# Krok 0: Instalacja i przygotowanie bazy wektorowej
# (Użyjemy kodu z poprzedniej lekcji, aby stworzyć `vectorstore` FAISS)
# pip install langchain-openai langchain-community faiss-cpu

import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Tworzymy bazę wektorową (kod z poprzedniej lekcji)
text = "LangChain to potężny framework do budowy aplikacji AI. Szczególnie dobrze nadaje się do tworzenia zaawansowanych chatbotów, ponieważ pozwala na integrację z pamięcią i narzędziami."
documents = [Document(page_content=text, metadata={"source": "lekcja-81"})]
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(k=1)
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# Krok 1: Stworzenie łańcucha do przeformułowywania pytania
# Ten prompt ma za zadanie stworzyć samodzielne pytanie
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", "Na podstawie poniższej historii rozmowy, przeformułuj ostatnie pytanie tak, aby było samodzielnym pytaniem."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Krok 2: Stworzenie łańcucha do generowania odpowiedzi
# Ten prompt używa zarówno kontekstu z bazy wiedzy, jak i historii, aby odpowiedzieć
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Odpowiedz na pytanie użytkownika na podstawie poniższego kontekstu i historii rozmowy.\n\nKontekst:\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Krok 3: Połączenie obu łańcuchów w jeden, kompletny pipeline RAG
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Krok 4: Uruchomienie i testowanie konwersacji
# Inicjujemy historię rozmowy
chat_history = []

# Pierwsze pytanie
print("--- Pytanie 1 ---")
question1 = "Co to jest LangChain?"
response1 = rag_chain.invoke({"input": question1, "chat_history": chat_history})
print(f"Użytkownik: {question1}")
print(f"Bot: {response1['answer']}")

# Aktualizujemy historię
chat_history.append(HumanMessage(content=question1))
chat_history.append(AIMessage(content=response1['answer']))

# Drugie pytanie, które zależy od kontekstu
print("\n--- Pytanie 2 ---")
question2 = "Do czego szczególnie dobrze się nadaje?"
response2 = rag_chain.invoke({"input": question2, "chat_history": chat_history})
print(f"Użytkownik: {question2}")
print(f"Bot: {response2['answer']}")


# 4. Podsumowanie
#
# Właśnie zbudowałeś kompletny, konwersacyjny system RAG, który jest fundamentem dla
# większości nowoczesnych, inteligentnych chatbotów opartych na wiedzy.
#
# Najważniejsze do zapamiętania:
#
#     1. **Problem kontekstu jest kluczowy**: Aby chatbot mógł prowadzić naturalną rozmowę,
#        musi rozumieć, do czego odnoszą się zaimki i niekompletne pytania.
#     2. **Przeformułowanie pytania**: Pierwszy krok zaawansowanego RAG to stworzenie
#        samodzielnego pytania na podstawie historii. To ono jest używane do przeszukiwania
#        bazy wiedzy.
#     3. **Wzbogacona generacja**: Finalna odpowiedź jest generowana na podstawie pełnego
#        kontekstu: historii rozmowy ORAZ relevantnych fragmentów z bazy wiedzy.
#     4. **LCEL to Twój przyjaciel**: LangChain Expression Language i gotowe funkcje, takie jak
#        `create_retrieval_chain`, niezwykle upraszczają budowę tak złożonych pipeline'ów.
#
# Masz teraz w ręku potężny wzorzec architektoniczny, który możesz rozwijać, dodając
# bardziej zaawansowane techniki retrievalu, agentów czy integracje z innymi narzędziami.