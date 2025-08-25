# Moduł 5, Punkt 40: Zastosowanie LangChain w chatbotach
#
#
#
# Witaj w lekcji, która jest zwieńczeniem naszej dotychczasowej pracy. Poznaliśmy już wszystkie klocki:
# prompty, pamięć, łańcuchy, a nawet agentów. Teraz złożymy je w jedną z najpopularniejszych i najbardziej
# praktycznych aplikacji AI – w pełni funkcjonalnego chatbota.
#
# W tej lekcji nie wprowadzimy wielu nowych komponentów. Zamiast tego skupimy się na tym, jak **prawidłowo
# połączyć** zdobytą wiedzę, aby stworzyć spójną, inteligententną i "pamiętającą" aplikację konwersacyjną.
#
# 1. Anatomia Nowoczesnego Chatbota
#
# Dobry chatbot to znacznie więcej niż prosty system "pytanie-odpowiedź". Składa się z kilku kluczowych elementów,
# które wspólnie tworzą wrażenie naturalnej rozmowy:
#
#     * **Persona (Osobowość)**: Czy bot ma być formalnym ekspertem, zabawnym pomocnikiem, a może sarkastycznym asystentem?
#       Zdefiniowanie jego charakteru jest kluczowe dla spójności.
#     * **Pamięć Krótkoterminowa**: Zdolność do pamiętania poprzednich wiadomości w ramach jednej sesji.
#       Bez tego każda wiadomość jest traktowana w izolacji.
#     * **Logika Konwersacji**: Mechanizm, który przetwarza nowe pytanie w kontekście dotychczasowej rozmowy
#       i generuje odpowiedź zgodną z nadaną mu personą.
#     * **(Opcjonalnie) Dostęp do Wiedzy i Narzędzi**: Możliwość korzystania z zewnętrznych źródeł (bazy danych, internet)
#       do odpowiadania na pytania wykraczające poza ogólną wiedzę modelu.
#
# 2. Jak LangChain modeluje komponenty chatbota?
#
# LangChain dostarcza idealne narzędzia do zamodelowania każdego z tych elementów:
#
#     * **Persona -> `SystemMessage` w `ChatPromptTemplate`**: To "dusza" i "instrukcja obsługi" dla Twojego bota.
#       W tej wiadomości definiujesz jego charakter, styl odpowiedzi i główny cel. Jest to najważniejszy element
#       w kształtowaniu zachowania chatbota.
#
#     * **Pamięć -> `ConversationBufferMemory` lub podobne**: Odpowiada za przechowywanie historii rozmowy.
#
#     * **Logika Konwersacji -> Łańcuch (`Runnable` z LCEL)**: Sercem chatbota jest łańcuch, który łączy prompt,
#       model i parser wyjścia. Nowoczesne podejście z LangChain Expression Language (LCEL) sprawia,
#       że jest to eleganckie i łatwe do zarządzania.
#
#     * **Dostęp do Wiedzy -> Agenci i Narzędzia**: Jeśli chatbot ma mieć dodatkowe "moce", budujemy go jako agenta,
#       dając mu dostęp do narzędzi (tak jak w poprzednich lekcjach).
#
# 3. Praktyczny przykład: Budowa Chatbota-Specjalisty
#
# Stworzymy chatbota z konkretną personą: będzie to pomocny, ale lekko sarkastyczny asystent dla programistów.
# Zbudujemy go w formie interaktywnej aplikacji konsolowej.
#
# Krok 1: Instalacja i konfiguracja
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

# Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-TWOJ_KLUCZ_API"

if "OPENAI_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY.")
    exit()

# Krok 2: Definicja komponentów chatbota
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

# Pamięć, która będzie przechowywać historię konwersacji.
# `memory_key` musi pasować do zmiennej w MessagesPlaceholder.
pamieta_rozmowe = ConversationBufferMemory(memory_key="historia_rozmowy", return_messages=True)

# Definiujemy prompt z jasno określoną personą w SystemMessage.
# To jest najważniejsza część, która nadaje charakter naszemu botowi.
prompt = ChatPromptTemplate(
    input_variables=["input", "historia_rozmowy"],
    messages=[
        ("system", """Jesteś sarkastycznym, ale niezwykle kompetentnym asystentem dla programistów o nazwie 'CodeSnark'.
        Twoim zadaniem jest pomagać w rozwiązywaniu problemów z kodem, ale zawsze z nutą dowcipu i ironii.
        Nigdy nie przyznajesz, że jesteś modelem AI. Odpowiadasz zwięźle i na temat, ale nie możesz się powstrzymać
        przed lekkim dogryzieniem użytkownikowi. Na przykład, jeśli pyta o prosty błąd, możesz zacząć od
        "No cóż, wygląda na to, że znowu zapomniałeś o średniku, prawda?"."""),
        MessagesPlaceholder(variable_name="historia_rozmowy"),
        ("human", "{input}"),
    ]
)

# Łączymy wszystko w jeden łańcuch
chatbot_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=pamieta_rozmowe,
    verbose=False  # Ustaw na True, aby zobaczyć, co dzieje się "pod maską"
)

# Krok 3: Stworzenie pętli interaktywnej
print("🤖 Jesteś połączony z CodeSnark. Zadaj pytanie dotyczące programowania (lub wpisz 'wyjscie', aby zakończyć).")

while True:
    user_input = input("Ty: ")
    if user_input.lower() == 'wyjscie':
        print("CodeSnark: No nareszcie, myślałem, że będziesz tu siedział cały dzień. Do zobaczenia.")
        break

    # Wywołujemy łańcuch, który automatycznie zarządza pamięcią
    response = chatbot_chain.invoke({"input": user_input})
    print(f"CodeSnark: {response['text']}")

#
# 4. Rozbudowa Chatbota: Co dalej?
#
# Ten chatbot to doskonała baza. Możesz go teraz rozbudować, wykorzystując wiedzę z całego modułu:
#
#     * **Dodanie narzędzi**: Zmień `LLMChain` w agenta, dając mu dostęp do wyszukiwarki internetowej, aby mógł
#       znaleźć linki do dokumentacji lub najnowszych bibliotek.
#     * **Połączenie z bazą wiedzy**: Stwórz system RAG (Retrieval-Augmented Generation), aby bot mógł odpowiadać
#       na pytania na podstawie Twoich prywatnych dokumentów (np. wewnętrznej dokumentacji projektu).
#     * **Udostępnienie światu**: Opakuj go w interfejs Streamlit lub API FastAPI, tak jak w poprzedniej lekcji,
#       aby mogli z niego korzystać inni.
#
# 5. Podsumowanie
#
# Zbudowanie dobrego chatbota to sztuka łączenia odpowiednich komponentów w spójną całość.
#
# Najważniejsze do zapamiętania:
#
#     1. **Persona jest królem**: `SystemMessage` to najważniejsze narzędzie do kształtowania zachowania bota.
#     2. **Pamięć to podstawa**: Bez komponentu `Memory`, nie ma mowy o płynnej konwersacji.
#     3. **Struktura to klucz**: Używanie `ChatPromptTemplate` z `MessagesPlaceholder` to standardowy i niezawodny
#        wzorzec budowy chatbotów w LangChain.
#     4. **Chatbot to system**: Traktuj go jako system złożony z modułów (osobowość, pamięć, logika), które możesz
#        wymieniać i ulepszać, a nie jako pojedynczy, monolityczny byt.
#
# Masz teraz wszystkie umiejętności, aby tworzyć własne, wyspecjalizowane i inteligentne aplikacje konwersacyjne.