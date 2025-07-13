# Aplikacja w Streamlit, która będzie "oknem" na nasz system

"""
Ten plik tworzy interfejs użytkownika (UI) dla aplikacji RODO Ekspert AI
przy użyciu biblioteki Streamlit. UI komunikuje się z backendem FastAPI.
"""
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="RODO Ekspert AI", page_icon="🤖", layout="wide")

st.title("🤖 RODO Ekspert AI")
st.caption("Zadaj pytanie dotyczące RODO, a AI odpowie na podstawie oficjalnego tekstu rozporządzenia.")

# Inicjalizacja historii czatu w stanie sesji
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetlanie wcześniejszych wiadomości
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Pole do wprowadzania nowego pytania
if prompt := st.chat_input("Jak brzmi Twoje pytanie dotyczące RODO?"):
    # Dodaj i wyświetl wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Przygotuj i wyślij zapytanie do API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Analizuję treść rozporządzenia... ⏳")
        
        try:
            response = requests.post(API_URL, json={"query": prompt}, timeout=120)
            response.raise_for_status()  # Sprawdź, czy nie ma błędu HTTP
            
            result = response.json()
            answer = result.get("answer", "Przepraszam, wystąpił błąd w odpowiedzi.")
            
            message_placeholder.markdown(answer)
            
            # Opcjonalnie: wyświetl źródła
            with st.expander("Zobacz źródła odpowiedzi"):
                for doc in result.get("source_documents", []):
                    st.markdown(f"**Źródło (strona {doc['metadata']['page']}):**")
                    st.info(doc['page_content'])

            # Dodaj odpowiedź AI do historii
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except requests.exceptions.RequestException as e:
            error_message = f"Błąd połączenia z serwerem API. Upewnij się, że backend działa. Szczegóły: {e}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})