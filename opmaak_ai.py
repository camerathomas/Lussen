"""
DenkKrant — AI-opmaak
Stuurt ruwe analysetekst naar de AI en krijgt nette HTML terug.

Twee functies:
- maak_html():       één tekst → één HTML-blok (voor losse calls).
- maak_html_meerdere(): meerdere teksten → meerdere HTML-blokken (één call).
"""

import re


# ---------- Hulpfuncties ----------

def _schoon_html(html):
    """Verwijdert per ongeluk meegeleverde code-fences en rommel."""
    if not html:
        return ""

    html = re.sub(r"^```(?:html)?\s*", "", html.strip(), flags=re.IGNORECASE)
    html = re.sub(r"\s*```$", "", html.strip())

    match = re.search(
        r"<(h2|h3|h4|p|ul|ol|li|strong|em|table|thead|tbody|tr|th|td)\b",
        html,
        flags=re.IGNORECASE,
    )
    if match:
        html = html[match.start():]

    match = re.search(
        r"</(h2|h3|h4|p|ul|ol|li|strong|em|table|thead|tbody|tr|th|td)>\s*$",
        html,
        flags=re.IGNORECASE,
    )
    if match:
        html = html[:match.end()]

    return html.strip()


def _knip_secties(tekst, aantal):
    """
    Knipt de AI-output in N secties, op basis van markeringen
    zoals '=== SECTIE 1 ===' of '=== 1 ==='.
    Geeft een lijst van N strings terug (lege string als iets mist).
    """
    if not tekst:
        return [""] * aantal

    # Zoek alle markeringen
    patroon = re.compile(
        r"={2,}\s*(?:SECTIE\s*)?(\d+)\s*={2,}",
        flags=re.IGNORECASE,
    )
    matches = list(patroon.finditer(tekst))

    if not matches:
        # Geen markeringen: geef alles terug als eerste sectie
        return [tekst.strip()] + [""] * (aantal - 1)

    secties = []
    for i, match in enumerate(matches):
        start = match.end()
        einde = matches[i + 1].start() if i + 1 < len(matches) else len(tekst)
        secties.append(tekst[start:einde].strip())

    # Vul aan tot het juiste aantal
    while len(secties) < aantal:
        secties.append("")

    return secties[:aantal]


# ---------- Eén tekst → één HTML-blok ----------

def maak_html(client, vraag_ai, tekst, opmaak_sleutel):
    """
    Vraagt de AI om één tekst om te zetten naar nette HTML.
    Geeft de HTML terug (of None bij falen).
    """
    if not tekst or not tekst.strip():
        return None

    prompt = f"{opmaak_sleutel}\n\n--- RUWE TEKST ---\n\n{tekst}"

    try:
        antwoord, _ = vraag_ai(client, prompt)
        html = _schoon_html(antwoord)
        if html and "<" in html:
            return html
        return None
    except Exception:
        return None


# ---------- Meerdere teksten → meerdere HTML-blokken (één call) ----------

def maak_html_meerdere(client, vraag_ai, teksten, opmaak_sleutel):
    """
    Vraagt de AI om MEERDERE teksten in één keer om te zetten naar HTML.
    Geeft een lijst van HTML-blokken terug (één per tekst).

    teksten: lijst van strings, in de volgorde die je terug wilt.
    """
    if not teksten:
        return []

    aantal = len(teksten)

    # Bouw één gecombineerde prompt
    blokken = []
    for i, tekst in enumerate(teksten, start=1):
        if tekst and tekst.strip():
            blokken.append(
                f"=== SECTIE {i} ===\n{tekst.strip()}\n"
            )
        else:
            blokken.append(f"=== SECTIE {i} ===\n(niets)\n")

    gecombineerd = "\n\n".join(blokken)

    prompt = (
        f"{opmaak_sleutel}\n\n"
        f"--- RUWE TEKST, IN {aantal} SECTIES ---\n\n"
        f"{gecombineerd}\n\n"
        f"--- EINDE RUWE TEKST ---\n\n"
        f"BELANGRIJK: Zet elke sectie om naar HTML, en zet de markering "
        f"'=== SECTIE N ===' LETTERLIJK terug in je antwoord, zodat de "
        f"secties uit elkaar gehaald kunnen worden. "
        f"Begin elke sectie met '=== SECTIE N ===' op een eigen regel."
    )

    try:
        antwoord, _ = vraag_ai(client, prompt)
    except Exception:
        return [None] * aantal

    # Knip de secties uit elkaar
    ruwe_secties = _knip_secties(antwoord, aantal)

    # Schoon elke sectie op
    resultaat = []
    for sectie in ruwe_secties:
        html = _schoon_html(sectie)
        resultaat.append(html if html and "<" in html else None)

    return resultaat
