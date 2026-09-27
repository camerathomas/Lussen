"""
DenkKrant — AI-opmaak
Stuurt ruwe analysetekst naar de AI en krijgt nette HTML terug.
"""

import re


def _schoon_html(html):
    """Verwijdert per ongeluk meegeleverde code-fences en rommel."""
    if not html:
        return ""

    # Strip markdown code fences zoals ```html ... ```
    html = re.sub(r"^```(?:html)?\s*", "", html.strip(), flags=re.IGNORECASE)
    html = re.sub(r"\s*```$", "", html.strip())

    # Verwijder alles vóór de eerste toegestane tag
    match = re.search(
        r"<(h2|h3|h4|p|ul|ol|li|strong|em)\b",
        html,
        flags=re.IGNORECASE,
    )
    if match:
        html = html[match.start():]

    # Verwijder alles na de laatste toegestane sluittag
    match = re.search(
        r"</(h2|h3|h4|p|ul|ol|li|strong|em)>\s*$",
        html,
        flags=re.IGNORECASE,
    )
    if match:
        html = html[:match.end()]

    return html.strip()


def maak_html(client, vraag_ai, tekst, opmaak_sleutel):
    """
    Vraagt de AI om de tekst om te zetten naar nette HTML.
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
