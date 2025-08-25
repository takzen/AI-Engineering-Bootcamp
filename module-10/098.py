# Moduł 10, Punkt 98: Integracja FastAPI z bazą danych
#
#
#
# Nasze API staje się coraz bardziej zaawansowane. Potrafimy je już budować, konteneryzować
# i projektować z myślą o skalowalności. Ale do tej pory brakowało nam jednego, kluczowego
# elementu, który jest sercem niemal każdej poważnej aplikacji: **trwałego przechowywania danych**.
#
# Nasze dotychczasowe API były bezstanowe, co jest świetne dla skalowalności, ale oznacza
# również, że po restarcie serwera wszystkie informacje przepadały. Co, jeśli chcemy
# trwale zapisywać historię konwersacji, dane użytkowników czy logi zapytań?
# Do tego potrzebujemy bazy danych.
#
# W tej lekcji nauczymy się, jak zintegrować naszą aplikację FastAPI z popularną,
# relacyjną bazą danych PostgreSQL, używając do tego potężnej biblioteki SQLAlchemy.
#
# 1. Dlaczego potrzebujemy bazy danych?
#
#     *   **Trwałość (Persistence)**: Dane zapisane w bazie przetrwają restarty aplikacji i awarie serwera.
#     *   **Zarządzanie stanem**: Zamiast przesyłać całą historię rozmowy w każdym zapytaniu,
#         możemy przechowywać ją w bazie i odwoływać się do niej po unikalnym ID sesji.
#     *   **Dane użytkowników**: Przechowywanie profili, ustawień i uprawnień użytkowników.
#     *   **Logowanie i analityka**: Zapisywanie każdego zapytania i odpowiedzi w celu późniejszej analizy.
#
# 2. Nasz stos technologiczny
#
#     *   **PostgreSQL**: Potężna, niezawodna i niezwykle popularna relacyjna baza danych open-source.
#     *   **SQLAlchemy**: To "złoty standard" w świecie Pythona do pracy z bazami danych SQL.
#         Działa jako **ORM (Object-Relational Mapper)**, co oznacza, że pozwala nam operować
#         na danych w bazie za pomocą obiektów Pythona, zamiast pisać surowe zapytania SQL.
#     *   **Alembic**: Narzędzie do zarządzania **migracjami bazy danych**. Pozwala na wersjonowanie
#         zmian w strukturze naszej bazy (np. dodanie nowej tabeli lub kolumny) w sposób
#         kontrolowany i powtarzalny.
#
# 3. Architektura integracji
#
# Proces połączenia FastAPI z bazą danych składa się z kilku kroków:
#
#     1.  **Definicja modeli SQLAlchemy**: Tworzymy klasy w Pythonie, które odpowiadają tabelom
#         w naszej bazie danych.
#     2.  **Zarządzanie sesją bazy danych**: Tworzymy mechanizm, który zarządza połączeniami
#         z bazą danych dla każdego zapytania API.
#     3.  **Definicja modeli Pydantic**: Tworzymy osobne modele dla danych przychodzących
#         i wychodzących z API, aby oddzielić logikę API od logiki bazy danych.
#     4.  **Implementacja operacji CRUD**: W naszych endpointach tworzymy logikę do
#         tworzenia (Create), odczytu (Read), aktualizacji (Update) i usuwania (Delete) danych.
#
# 4. Praktyczny przykład: Zapisywanie historii konwersacji
#
# Zbudujemy API, które będzie trwale zapisywać każdą wiadomość z chatbota w bazie PostgreSQL.
#
# Krok 0: Instalacja
# # pip install fastapi "uvicorn[standard]" sqlalchemy "psycopg2-binary" alembic
# # Uwaga: Potrzebujesz działającego serwera PostgreSQL. Możesz go uruchomić np. w kontenerze Docker.
#
# Krok 1: Struktura projektu
# /api_with_db
# |-- alembic/             # Folder generowany przez Alembic
# |-- alembic.ini          # Plik konfiguracyjny Alembic
# |-- app/
# |   |-- __init__.py
# |   |-- main.py          # Główny plik FastAPI
# |   |-- database.py      # Konfiguracja połączenia z bazą
# |   |-- models.py        # Modele SQLAlchemy (tabele)
# |   |-- schemas.py       # Modele Pydantic (API)
# |   |-- crud.py          # Logika operacji na bazie (CRUD)

# --- Plik app/database.py ---
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname" # Zastąp swoimi danymi

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Plik app/models.py ---
from sqlalchemy import Column, Integer, String, Text
from .database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String) # "user" lub "assistant"
    content = Column(Text)

# --- Plik app/schemas.py ---
from pydantic import BaseModel

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    session_id: str
    class Config:
        orm_mode = True # Pozwala Pydantic na pracę z obiektami SQLAlchemy

# --- Plik app/crud.py ---
from sqlalchemy.orm import Session
from . import models, schemas

def create_chat_message(db: Session, session_id: str, message: schemas.MessageCreate):
    db_message = models.ChatMessage(**message.dict(), session_id=session_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_by_session(db: Session, session_id: str):
    return db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).all()

# --- Plik app/main.py ---
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine

# Ta komenda tworzy tabele w bazie, jeśli nie istnieją.
# W produkcji używamy do tego migracji Alembic.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Funkcja "dependency", która dostarcza sesję bazy danych do endpointów
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sessions/{session_id}/messages/", response_model=schemas.Message)
def add_message_to_session(session_id: str, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_chat_message(db=db, session_id=session_id, message=message)

@app.get("/sessions/{session_id}/messages/", response_model=List[schemas.Message])
def read_session_messages(session_id: str, db: Session = Depends(get_db)):
    return crud.get_messages_by_session(db=db, session_id=session_id)

#
# Krok 5: Migracje z Alembic
# # W terminalu, w głównym folderze projektu:
# # 1. Inicjalizacja Alembic (tylko raz na projekt)
# #    alembic init alembic
# # 2. (Edytuj plik alembic.ini i `env.py`, aby wskazać na modele i bazę danych)
# # 3. Stworzenie nowej migracji
# #    alembic revision --autogenerate -m "Create chat messages table"
# # 4. Zastosowanie migracji do bazy danych
# #    alembic upgrade head
#
# 5. Podsumowanie
#
# Integracja z bazą danych przekształca nasze proste, efemeryczne API w pełnoprawne,
# trwałe aplikacje.
#
# Najważniejsze do zapamiętania:
#
#     1.  **Oddzielaj warstwy**: Dobrą praktyką jest oddzielenie logiki API (FastAPI),
#         definicji tabel (SQLAlchemy), schematów API (Pydantic) i logiki biznesowej
#         (funkcje CRUD) do osobnych plików.
#     2.  **SQLAlchemy jako ORM**: Używaj SQLAlchemy do mapowania tabel na obiekty Pythona,
#         co upraszcza i ustandaryzowuje interakcje z bazą.
#     3.  **Zarządzaj sesjami**: Używaj mechanizmu zależności (`Depends`) w FastAPI, aby
#         zapewnić, że każde zapytanie API otrzymuje własną, czystą sesję bazy danych,
#         która jest poprawnie zamykana.
#     4.  **Używaj migracji (Alembic)**: Nigdy nie modyfikuj struktury produkcyjnej bazy
#         danych ręcznie. Używaj narzędzi do migracji, aby wszystkie zmiany były
#         wersjonowane i powtarzalne.
#
# Opanowując tę umiejętność, jesteś w stanie budować kompletne, zaawansowane aplikacje,
# które nie tylko inteligentnie przetwarzają dane, ale także trwale je przechowują
# i zarządzają nimi w bezpieczny i skalowalny sposób.