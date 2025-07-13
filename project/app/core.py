# Serce logiki AI, buduje łańcuch LangChain

"""
Ten plik zawiera kluczową logikę aplikacji – tworzenie i konfigurację łańcucha Q&A.
Funkcja `get_qa_chain` buduje kompletny potok RAG (Retrieval-Augmented Generation),
który jest sercem naszego inteligentnego asystenta.
"""
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'vector_db')

PROMPT_TEMPLATE = """
Jesteś precyzyjnym i pomocnym asystentem AI, który specjalizuje się w Rozporządzeniu o Ochronie Danych Osobowych (RODO).
Twoim zadaniem jest odpowiedzieć na pytanie użytkownika wyłącznie na podstawie dostarczonego poniżej Kontekstu.
Kontekst zawiera fragmenty dokumentu RODO.
Jeśli w Kontekście nie ma wystarczających informacji, aby odpowiedzieć na pytanie, odpowiedz:
"Na podstawie dostarczonych fragmentów dokumentu RODO nie jestem w stanie udzielić odpowiedzi na to pytanie."
Nie próbuj wymyślać odpowiedzi. Odpowiadaj zawsze w języku polskim, rzeczowo i zwięźle.

Kontekst:
{context}

Pytanie:
{question}

Odpowiedź:
"""

def get_qa_chain():
    """Buduje i zwraca gotowy do użycia łańcuch RetrievalQA."""
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain