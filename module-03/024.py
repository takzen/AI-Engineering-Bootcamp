# Moduł 3, Lekcja 24: Integracja Pydantic z LangChain
#
#
#
# Dotarliśmy do momentu, w którym łączymy dwie potężne koncepcje: walidację danych (Pydantic)
# i orkiestrację modeli językowych (LangChain). To połączenie rozwiązuje jeden
# z największych problemów w pracy z LLM-ami: ich tendencję do generowania
# nieustrukturyzowanego, "kreatywnego" tekstu.
#
# Co, jeśli moglibyśmy ZMUSIĆ model językowy, aby jego odpowiedź ZAWSZE miała
# formę idealnie pasującą do naszego modelu Pydantic?
#
# To właśnie umożliwia integracja Pydantic z LangChain.
#
# 1. Problem: Nieprzewidywalny output z LLM
#
# Załóżmy, że chcemy, aby model AI na podstawie recenzji produktu wyodrębnił
# główne zalety i wady. Bez żadnych "instrukcji formatowania", odpowiedź
# mogłaby wyglądać różnie za każdym razem.

def symuluj_odpowiedz_llm_bez_struktury(recenzja):
    """Symuluje odpowiedź LLM-a bez narzuconej struktury."""
    print(f"\nAnalizuję recenzję: '{recenzja}'")
    # Za każdym razem odpowiedź może mieć inny format
    return "Cóż, wydaje się, że główne plusy to: świetna bateria i dobry aparat. " \
    "Jeśli chodzi o wady, użytkownik wspomina o tym, że urządzenie jest trochę za ciężkie."

# Próba parsowania takiej odpowiedzi jest koszmarem – wymaga skomplikowanych
# wyrażeń regularnych i jest bardzo podatna na błędy.
recenzja_produktu = "Bateria trzyma wieki, aparat robi świetne zdjęcia, ale telefon jest ciężki " \
"jak cegła."
odpowiedz_llm = symuluj_odpowiedz_llm_bez_struktury(recenzja_produktu)

print("\n--- 1. Próba ręcznego parsowania niestrukturalnej odpowiedzi ---")
print(f"Odpowiedź LLM: {odpowiedz_llm}")
# ... tutaj byłby skomplikowany i zawodny kod do parsowania tego tekstu ...
print("Parsowanie tego ręcznie jest trudne i niepewne!")


# 2. Rozwiązanie: Pydantic jako "schemat odpowiedzi" dla LangChain
#
# LangChain posiada koncepcję "Parserów Wyjścia" (Output Parsers). Możemy dać
# LangChainowi nasz model Pydantic, a on zrobi dwie magiczne rzeczy:
#
#   1. Wygeneruje specjalne instrukcje formatowania, które dołączymy do naszego promptu,
#      mówiąc LLM-owi: "Twoja odpowiedź MUSI być w tym konkretnym formacie JSON".
#   2. Po otrzymaniu odpowiedzi od LLM-a, automatycznie spróbuje ją sparsować
#      i zwalidować za pomocą naszego modelu Pydantic.
#
# WAŻNE: Przed uruchomieniem, upewnij się, że masz zainstalowane potrzebne biblioteki.
# W terminalu/wierszu poleceń wpisz:
# pip install langchain pydantic
# (Dla realnych zastosowań potrzebne będzie też np. `langchain-openai`)

from pydantic import BaseModel, Field
from typing import List

# Krok 1: Definiujemy naszą pożądaną strukturę wyjściową za pomocą Pydantic
class AnalizaRecenzji(BaseModel):
    """Struktura danych zawierająca analizę recenzji produktu."""
    zalety: List[str] = Field(description="Lista kluczowych zalet wymienionych w recenzji.")
    wady: List[str] = Field(description="Lista kluczowych wad wymienionych w recenzji.")
    ogolny_sentyment: str = Field(description="Ogólny sentyment recenzji, np. 'pozytywny', 'negatywny', 'mieszany'.")


# 3. Budowanie łańcucha (Chain) z parserem Pydantic
#
# Zobaczmy, jak to działa w praktyce. Zbudujemy prosty łańcuch LangChain.

from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

print("\n--- 2. Użycie PydanticOutputParser ---")

# Krok 2: Tworzymy parser na podstawie naszego modelu Pydantic
parser = PydanticOutputParser(pydantic_object=AnalizaRecenzji)

# Krok 3: Pobieramy instrukcje formatowania
# To jest tekst, który LangChain wygenerował na podstawie naszego modelu.
# Dodamy go do promptu, aby "nauczyć" LLM-a, jak ma odpowiadać.
format_instructions = parser.get_format_instructions()
print("\nWygenerowane przez LangChain instrukcje formatowania dla LLM-a:")
print(format_instructions)

# Krok 4: Tworzymy szablon promptu, który zawiera te instrukcje
prompt_template_str = """
Przeanalizuj poniższą recenzję produktu.
Wyodrębnij z niej kluczowe zalety, wady oraz ogólny sentyment.

{format_instructions}

Recenzja:
{recenzja}
"""

prompt = PromptTemplate(
    template=prompt_template_str,
    input_variables=["recenzja"],
    partial_variables={"format_instructions": format_instructions}
)

# Krok 5: Symulujemy odpowiedź od LLM-a
# W prawdziwej aplikacji tutaj byłoby wywołanie modelu, np. `model.invoke(...)`
# Zauważ, że odpowiedź jest teraz idealnie sformatowanym stringiem JSON,
# bo LLM dostał nasze instrukcje!
symulowana_odpowiedz_llm_json = """
{
  "zalety": ["długi czas pracy na baterii", "świetna jakość aparatu"],
  "wady": ["duża waga urządzenia"],
  "ogolny_sentyment": "mieszany"
}
"""

print("\n--- 3. Parsowanie ustrukturyzowanej odpowiedzi ---")
# Krok 6: Używamy parsera, aby przekształcić odpowiedź LLM-a w obiekt Pydantic
try:
    sformatowana_analiza = parser.parse(symulowana_odpowiedz_llm_json)
    
    print("Sukces! Odpowiedź LLM została sparsowana i zwalidowana.")
    print("Typ obiektu:", type(sformatowana_analiza))
    print("Obiekt Pydantic:", sformatowana_analiza)
    
    # Teraz możemy bezpiecznie pracować z danymi
    print("\nZalety produktu:", sformatowana_analiza.zalety)
    if "duża waga urządzenia" in sformatowana_analiza.wady:
        print("Potwierdzono, że waga jest wadą.")

except Exception as e:
    print(f"Błąd podczas parsowania odpowiedzi LLM: {e}")

#
# 4. Podsumowanie – Dlaczego to jest rewolucyjne?
#
# Integracja Pydantic z LangChain zamienia model językowy z "kreatywnego pisarza"
# w niezawodne, programowalne narzędzie do ekstrakcji i generowania danych.
#
#     * Gwarancja struktury: Zmuszamy LLM do odpowiadania w przewidywalnym,
#       ustrukturyzowanym formacie (JSON), który zdefiniowaliśmy.
#
#     * Automatyczna walidacja: LangChain automatycznie sprawdza, czy odpowiedź LLM-a
#       jest zgodna z naszym modelem Pydantic. Jeśli nie, dostajemy błąd, a nie
#       "po cichu" zepsute dane.
#
#     * Niezawodność aplikacji: Zamiast pisać zawodne parsery tekstu, opieramy
#       naszą aplikację na solidnych, zwalidowanych obiektach Pydantic.
#
#     * Budowanie "agentów" i narzędzi: Ta technika jest fundamentem do tworzenia
#       agentów AI, które mogą wywoływać inne funkcje i narzędzia, ponieważ
#       potrafią generować poprawne, ustrukturyzowane argumenty dla tych narzędzi.
#
# Opanowanie tego wzorca jest kluczowe do budowania jakichkolwiek poważnych
# aplikacji opartych na LLM-ach. To most między światem języka naturalnego
# a światem uporządkowanego kodu.
#