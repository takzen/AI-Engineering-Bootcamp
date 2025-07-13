# Moduł 7, Punkt 61: Tworzenie dynamicznych systemów AI w LangGraph
#
#
#
# Opanowaliśmy już budowę pojedynczych, cyklicznych agentów. Potrafimy tworzyć przepływy, które
# obsługują błędy i dynamicznie wybierają ścieżki. Ale co, jeśli jeden agent to za mało?
# Co, jeśli do rozwiązania złożonego problemu potrzebujemy **zespołu wyspecjalizowanych ekspertów**,
# którzy współpracują ze sobą, przekazując sobie zadanie na kolejnych etapach?
#
# W tej lekcji wejdziemy na najwyższy poziom orkiestracji AI, ucząc się, jak budować
# **dynamiczne systemy wieloagentowe (multi-agent systems)**. To tutaj LangGraph pokazuje
# swoją prawdziwą, rewolucyjną moc.
#
# 1. Problem: Ograniczenia pojedynczego agenta
#
# Nawet najbardziej zaawansowany pojedynczy agent ma swoje granice. Próba "nauczenia" go wszystkiego
# i dania mu dziesiątek narzędzi prowadzi do problemów:
#
#     * **Przeładowanie kontekstu**: Prompt staje się gigantyczny i skomplikowany, co może "dezorientować" model.
#     * **Konflikt ról**: Agentowi trudno jest być jednocześnie kreatywnym pisarzem, precyzyjnym programistą i analitykiem danych.
#     * **Brak specjalizacji**: Agent staje się "specjalistą od wszystkiego, czyli od niczego".
#
# Lepszym podejściem, inspirowanym ludzkimi zespołami, jest stworzenie kilku mniejszych,
# wyspecjalizowanych agentów i jednego "kierownika projektu", który zarządza ich pracą.
#
# 2. Architektura systemu wieloagentowego: Wzorzec "Supervisor-Workers"
#
# Architektura, którą zbudujemy, opiera się na prostym, ale niezwykle potężnym wzorcu:
#
#     * **Supervisor (Nadzorca/Orkiestrator)**: To główny agent-router. Jego jedynym zadaniem jest
#       analiza aktualnego stanu problemu i **zdecydowanie, który z podległych mu agentów
#       (workerów) powinien teraz przejąć pałeczkę**.
#
#     * **Workers (Pracownicy/Specjaliści)**: To wyspecjalizowane agenty. Każdy z nich jest ekspertem
#       w swojej wąskiej dziedzinie i ma dostęp tylko do narzędzi potrzebnych do jego pracy.
#       Na przykład:
#         - **Researcher**: Agent z dostępem do internetu, odpowiedzialny za zbieranie informacji.
#         - **Coder**: Agent, który potrafi pisać i analizować kod.
#         - **Critic**: Agent, który ocenia pracę innych i sugeruje poprawki.
#
#     * **Współdzielony Stan (Shared State)**: Wszyscy agenci operują na tym samym obiekcie stanu.
#       To ich "wspólna tablica", na której zapisują wyniki swojej pracy, umożliwiając płynną
#       współpracę.
#
#     * **Pętla Współpracy**: Przepływ wygląda następująco:
#       Supervisor -> Worker A -> Supervisor -> Worker B -> Supervisor -> ... -> Zakończenie
#
# 3. Praktyczny przykład: Zespół "Researcher & Coder"
#
# Zbudujemy system, w którym Supervisor zarządza dwoma specjalistami: Researcherem, który szuka
# informacji w sieci, i Coderem, który pisze kod.
#
# Krok 0: Instalacja i konfiguracja
# (Zakładamy, że pakiety z poprzednich lekcji są już zainstalowane)
import os
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Konfiguracja API
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["TAVILY_API_KEY"] = "tvly-..."
if "OPENAI_API_KEY" not in os.environ or "TAVILY_API_KEY" not in os.environ:
    print("\nBŁĄD: Upewnij się, że masz ustawione zmienne środowiskowe.")
    exit()

# Krok 1: Zdefiniowanie Narzędzi i Stanu
tool = TavilySearchResults(max_results=2)
tools = [tool]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # 'next_agent' będzie przechowywać nazwę agenta, który ma działać w następnym kroku
    next_agent: str

# Krok 2: Zdefiniowanie Agentów-Pracowników (Workers)
# Dla uproszczenia, zdefiniujemy ich jako proste, wywoływalne łańcuchy, a nie pełne grafy.
def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    agent = prompt | llm.bind_tools(tools)
    return agent

llm = ChatOpenAI(model="gpt-4o", temperature=0)
researcher_agent = create_agent(llm, tools, "Jesteś researcherem. Użyj narzędzi do wyszukiwania, aby znaleźć informacje.")
coder_agent = create_agent(llm, [], "Jesteś ekspertem od pisania kodu w Pythonie. Pisz kompletne, działające skrypty.")

# Krok 3: Zdefiniowanie Węzłów dla każdego Agenta
def researcher_node(state: AgentState):
    print("--- WĘZEŁ: Researcher ---")
    result = researcher_agent.invoke(state)
    return {"messages": [result]}

def coder_node(state: AgentState):
    print("--- WĘZEŁ: Coder ---")
    result = coder_agent.invoke(state)
    return {"messages": [result]}

# Krok 4: Zdefiniowanie Nadzorcy (Supervisor) i Logiki Routingu
# Lista członków zespołu, którą Nadzorca będzie znał
members = ["Researcher", "Coder"]
system_prompt_supervisor = (
    "Jesteś nadzorcą zespołu składającego się z następujących pracowników: {members}. "
    "Na podstawie historii konwersacji, wybierz pracownika, który ma wykonać następne zadanie. "
    "Każdy pracownik wykona jedno zadanie, a następnie zwróci kontrolę do Ciebie. "
    "Gdy zadanie jest w pełni ukończone, odpowiedz słowem 'FINISH'."
)

options = ["FINISH"] + members
# Tworzymy model dla nadzorcy, który jest zmuszony do wyboru jednej z opcji
supervisor_chain = (
    ChatPromptTemplate.from_messages([
        ("system", system_prompt_supervisor),
        MessagesPlaceholder(variable_name="messages"),
    ]).partial(members=", ".join(members))
    | llm.with_structured_output(schema={"next": options})
)

def supervisor_node(state: AgentState):
    print("--- WĘZEŁ: Supervisor ---")
    # Zawsze wywołujemy nadzorcę z całą historią
    response = supervisor_chain.invoke(state)
    print(f"-> Nadzorca wybrał: {response['next']}")
    return {"next_agent": response['next']}

# Krok 5: Zbudowanie Grafu
workflow = StateGraph(AgentState)

# Dodajemy węzły dla każdego członka zespołu i nadzorcy
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Coder", coder_node)
workflow.add_node("supervisor", supervisor_node)

# Definiujemy, jak Nadzorca kieruje pracą
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"], # Klucz do routingu to wartość 'next_agent' w stanie
    {member: member for member in members} | {"FINISH": END}
)

# Po wykonaniu pracy, każdy worker zwraca kontrolę do nadzorcy
for member in members:
    workflow.add_edge(member, "supervisor")

workflow.set_entry_point("supervisor")
app = workflow.compile()

# Krok 6: Uruchomienie Systemu
print("\n--- TEST: System wieloagentowy w akcji ---")
complex_task = {"messages": [HumanMessage(content="Znajdź w internecie najnowsze informacje o bibliotece LangGraph, a następnie napisz prosty skrypt w Pythonie, który demonstruje jej użycie.")]}
for s in app.stream(complex_task, {"recursion_limit": 10}):
    if "__end__" not in s:
        print(s)
        print("----")

#
# 4. Podsumowanie
#
# Właśnie zbudowałeś swój pierwszy, dynamiczny system wieloagentowy. To potężny wzorzec,
# który pozwala na rozwiązywanie znacznie bardziej złożonych problemów niż przy użyciu
# pojedynczego agenta.
#
# Najważniejsze do zapamiętania:
#
#     1. **Specjalizacja ponad generalizacją**: Zamiast jednego agenta "od wszystkiego", twórz
#        zespoły wyspecjalizowanych ekspertów.
#     2. **Supervisor jako router**: Centralny agent-nadzorca jest kluczem do orkiestracji
#        pracy całego zespołu. Jego głównym zadaniem jest podejmowanie decyzji "kto następny?".
#     3. **Współdzielony stan to komunikacja**: Obiekt stanu jest "wspólną tablicą", dzięki której
#        agenci mogą widzieć wyniki pracy swoich poprzedników.
#     4. **LangGraph to idealne narzędzie**: Dzięki grafowej naturze i krawędziom warunkowym,
#        LangGraph jest stworzony do modelowania takich złożonych, cyklicznych interakcji.
#
# Opanowanie tej architektury otwiera drzwi do budowy nowej klasy aplikacji AI, które potrafią
# w zorganizowany i inteligentny sposób współpracować nad osiągnięciem celu.