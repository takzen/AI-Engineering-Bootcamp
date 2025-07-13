# Główny plik serwera FastAPI, który udostępnia API

"""
Główny plik aplikacji FastAPI.
Definiuje endpointy API, obsługuje zapytania i odpowiedzi.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core import get_qa_chain
from typing import List

app = FastAPI(
    title="RODO Ekspert AI API",
    description="API do zadawania pytań na temat RODO, oparte na architekturze RAG."
)

qa_chain = None

@app.on_event("startup")
def startup_event():
    """Inicjalizuje łańcuch QA przy starcie aplikacji."""
    global qa_chain
    try:
        qa_chain = get_qa_chain()
        print("Łańcuch QA został pomyślnie załadowany.")
    except Exception as e:
        print(f"BŁĄD krytyczny: Nie udało się załadować łańcucha QA: {e}")
        print("Sprawdź, czy baza wektorowa 'vector_db/' istnieje. Uruchom 'ingest_data.py'.")

# Modele danych Pydantic dla walidacji i dokumentacji API
class QueryRequest(BaseModel):
    query: str

class DocumentMetadata(BaseModel):
    page: int
    source: str

class Document(BaseModel):
    page_content: str
    metadata: DocumentMetadata

class QueryResponse(BaseModel):
    answer: str
    source_documents: List[Document]

@app.get("/")
def read_root():
    """Główny endpoint powitalny."""
    return {"message": "Witaj w API dla RODO Ekspert AI! Przejdź do /docs po dokumentację."}

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    """Główny endpoint do zadawania pytań."""
    if not qa_chain:
        raise HTTPException(status_code=503, detail="Serwer nie jest gotowy. Łańcuch QA nie został załadowany.")
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Pytanie (query) nie może być puste.")
    
    try:
        result = qa_chain.invoke({"query": request.query})
        return {
            "answer": result.get("result", ""),
            "source_documents": result.get("source_documents", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wystąpił wewnętrzny błąd serwera: {str(e)}")