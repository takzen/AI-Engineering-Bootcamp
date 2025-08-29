# --- Plik: data_processing.py ---
def wyczysc_tekst(tekst):
    """Usuwa białe znaki z początku i końca oraz zamienia tekst na małe litery."""
    if not isinstance(tekst, str):
        raise TypeError("Wejście musi być stringiem")
    return tekst.strip().lower()

def oblicz_srednia(lista_liczb):
    """Oblicza średnią arytmetyczną z listy liczb."""
    if not lista_liczb:
        return 0
    return sum(lista_liczb) / len(lista_liczb)